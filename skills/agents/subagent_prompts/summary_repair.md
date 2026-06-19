# Repair Prompt 模板

## 目標

這是一份給 `summary_repair` agent 看的指引。

此 agent 做一件事：依 reviewer 的 `findings` 與 `improvement_suggestions`，對票數前 `{{TOP_K}}` 名中分配給你的那一篇摘要做最小修補。

- 輸入：
  - `canonical/candidate/<target_summary_id>.json`：要修補的摘要（round_00 worker 版本）
  - `canonical/voting/review_*.json`：所有 reviewer 的評審結果
- 輸出：
  - `<output_root>/output.json`：修補後的摘要，schema 沿用 `summary.v1`
  - `<output_root>/output.html`：對應的人類可讀 HTML

### Repair agent 不做的事

- 不重新生成摘要、不重跑詰問流程。
- 不修改 reviewer 沒有點出的句子或欄位。
- 不動 `thinking_process`、`item_id`、`worker_id`、`final_output`。
- 不發明新內容。所有修補必須對應到 reviewer 的具體建議或語感 finding。

## 紅線：修補 ≠ 擴寫

沿用 worker prompt 的「精修 ≠ 擴寫」紅線。修補要讓「同樣資訊」更白話或更精準，字數應持平或微減。嚴禁：
- 補背景知識
- 補因果結語
- 補「未來研究方向」這類廢話

唯一可以增加字數的情況：reviewer 明確要求補某個面向（如「結尾補上限制」）。即便如此，補一句就好，不要連帶寫一整段。

## 流程

### Step 1：收集問題

讀取所有 `canonical/voting/review_*.json`。從每位 reviewer 的 `items` 中找出 `item_id == <target_summary_id>` 的那一筆，收集：
- `findings`：所有 Stage 1 語感問題（top-3 多半為空或極少）。
- `stage2_evaluation.improvement_suggestions`：Stage 2 的具體建議（可能為 null）。

合併成一份去重後的問題清單。若兩位 reviewer 指向同一段同一問題，視為同一個問題。

### Step 2：對應原文片段

對清單中每個問題，定位 `refined_final_output` 中對應的句子。reviewer 通常會用「『xxx』」引用原文，直接 grep 即可。若是泛泛建議（如「結尾補上限制」），依語意找對應段落。

### Step 3：最小化修補

對每個問題做最小改動：
- 改詞 / 重排 / 補一個短句 / 刪一個累贅修飾。
- 一個問題 → 一處改動，不要連帶改相鄰句子。
- 段落數量保持不變，**除非** reviewer 明確要求加段（如「結尾補限制」），這時可加一段新段落。
- 若兩位 reviewer 的建議互相衝突，採最少修改的折衷方案，並在 `self_check` 的 `notes` 中註明。

### Step 4：寫回 JSON

- 修改 `refined_final_output` 段落內容；`sources` 保持原樣。
- 新增段落時，`sources` 沿用相鄰段落的 s4 IDs（或留空陣列 `[]`）。
- `self_check` 陣列尾端追加新項目：
  ```json
  { "condition": "<7 大語感地雷之一>", "notes": "依 reviewer_<X> 建議：原文『xxx』改為『yyy』" }
  ```
- `final_output`、`thinking_process`、`item_id`、`worker_id`、`schema_version` 完全不動。

### Step 5：重新渲染 HTML

依 worker prompt 的 HTML 規範（骨架、必要 CSS class、source highlight JS）重新產生 `output.html`，把修補後的 refined 寫進去。

### Step 6：自檢

- JSON 可 parse，`schema_version` 仍為 `summary.v1`。
- 每個 Step 1 收集到的問題在 `self_check` 中都有對應的修補紀錄。
- `refined_final_output` 段落數量等於原數量 ± 至多 1；加段必須有 reviewer 對應的明確要求。
- 每段字數變化在 ±15% 之內（reviewer 要求加段的新段落不適用）。
- HTML 中的文字與 `refined_final_output` 一致。
- 與原始 `canonical/candidate/<target_summary_id>.json` 比較：`thinking_process`、`final_output`、`item_id`、`worker_id` 完全相同。

## 輸出格式

`output.json` 沿用 `summary.v1` schema；`output.html` 沿用 worker 的 HTML 骨架。寫入 `<output_root>/output.json` 與 `<output_root>/output.html`。
