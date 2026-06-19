# Summary Pipeline

## 目標

這是一份給 pipeline orchestrator 看的指引。

此流程使用場景與目標：
- 輸入：一篇已準備好的科學論文（包含原始文件或已初步萃取的內容）。
- 輸出：多份結構化摘要及其雙盲審查報告（JSON, HTML, Markdown）。
- 目標：將科學論文轉譯為外行人能懂的結構化摘要，並透過多 worker 與 reviewer 機制篩選出最高品質結果。

本檔案描述 summary lane。

## 參數

| 變數 | 預設 | 說明 |
|---|---|---|
| `{{WORKER_COUNT}}` | 12 | 啟動的 summary_worker 數量。 |
| `{{REVIEWER_COUNT}}` | 5 | 啟動的 summary_reviewer 數量。 |
| `{{VOTES_PER_BALLOT}}` | 7 | 每位 reviewer 一張選票的總票數。 |
| `{{TOP_K}}` | 3 | 選票候選人數 = repair 數 = final 收件數。 |

要調整數量，只改本表的預設值即可。下方流程文以 `{{WORKER_COUNT}}` / `{{REVIEWER_COUNT}}` / `{{VOTES_PER_BALLOT}}` / `{{TOP_K}}` 引用，請勿在流程文中再寫死數字。

**TOP_K 耦合**：`{{TOP_K}}` 一處改動會同步影響——
1. Reviewer Stage 1 淘汰後留下的「語感前 K 名」進入 Stage 2 與 Stage 3。
2. Reviewer Stage 3 投票：選票上恰好 `{{TOP_K}}` 名候選人。
3. Step 3 Repair：對 vote_tally `top_K` 平行 spawn `{{TOP_K}}` 個 repair agent。
4. Step 4 Final Extraction：`canonical/summary.json` 的 `items` 長度 = `{{TOP_K}}`。

## 路徑慣例

`paper_file = <paper_dir>/reassembly/canonical/paper.html`。

## 結構

### Subagent prompts

| Prompt | 角色 |
|---|---|
| `subagent_prompts/summary_worker.md` | 將科學論文轉譯為外行人能懂的結構化摘要（JSON + HTML）。 |
| `subagent_prompts/summary_reviewer.md` | 從多篇候選摘要中，進行嚴格的語感淘汰、內容比對與投票，給出評審結果（JSON + Markdown）。 |
| `subagent_prompts/summary_repair.md` | 依 reviewer 的改進建議，對票數前 `{{TOP_K}}` 名的摘要進行最小修補（JSON + HTML）。 |

### 目錄結構

```text
<paper_dir>/
  summary/
    worker/
      round_00/
        worker_01/
          output.json
          output.html
        ...
        worker_N/
          output.json
          output.html
      round_01/                # Repair：只跑票數前 {{TOP_K}} 名
        summary_XX/            # 命名直接用目標 summary_id
          output.json
          output.html
        ...
    reviewer/
      round_00/
        reviewer_A/
          visual_review.json
          review_report.md
        reviewer_B/
          visual_review.json
          review_report.md
    canonical/               # live state——所有下游 agent 的唯一結構化資料來源
      candidate/             # Worker summary；top-3 在 Step 3 後為修補版
        summary_01.json
        ...
        summary_N.json
      voting/                # Reviewer 投票結果
        review_A.json
        ...
        review_E.json
      vote_tally.json        # Parent 聚合的票數表
      summary.json           # Final delivery：top-3 精簡呈現（main_line + refined_final_output 純字串陣列）
```

> HTML 與 review_report.md 等人類視角的衍生視圖**不進 canonical**，留在對應的 work folder（`worker/round_XX/...`、`reviewer/round_00/...`）。

### Round 命名

- `worker/round_00/` + `reviewer/round_00/`：initial worker assembly + initial review。
- `worker/round_01/`：top-3 repair only（沒有對應的 `reviewer/round_01/`，因為這一輪不再做 review）。
- 不覆寫 work folder 的舊 round；`canonical/` 則視為 live state，新 round 的 promote 會覆寫對應檔案。

## 流程

Parent 只做兩種動作：
- **[spawn agent]** 啟動 subagent（委派判斷）
- **[mechanical]** 搬檔或組裝 JSON（不需判斷）

所有內容撰寫和品質判斷由 subagent 做。Parent 不改寫文字。

Subagent 規則：
- 所有 worker、reviewer 都要啟動獨立 subagent。不得用 parent 的工作取代 subagent。
- Subagent prompt 必須使用指定的 prompt 檔案全文，不得摘要、改寫、截斷。Parent 唯一可以做的修改是在末尾附加 assignment block。
- Agent 啟動失敗 → 先修正 prompt/tool/context，重試。仍失敗 → 回報 blocked。

### Step 1: Work (Summary Generation)

**[spawn agent]** 平行啟動 `{{WORKER_COUNT}}` 個 `summary_worker` (`worker_01` 到 `worker_N`)

```text
---
Assignment
paper_dir: <paper_dir>
paper_file: <paper_dir>/reassembly/canonical/paper.html
mode: initial
worker_id: worker_01  # 至 worker_N
output_root: <paper_dir>/summary/worker/round_00/worker_01
```

這些 Worker 獨立讀取論文來源，進行迭代詰問與精修，各自寫出 `output.json` 與 `output.html`。藉此獲得 `{{WORKER_COUNT}}` 份具備多樣性的摘要以供後續評選。

**[mechanical]** Promote：
1. 收集所有 worker 的 `output.json`。
2. 將每一份 JSON 中的 `item_id` 依序改為 `summary_01` 到 `summary_N`。
3. 重新命名檔案並複製到 `canonical/candidate/summary_01.json` ~ `canonical/candidate/summary_N.json`。
4. HTML 留在 `worker/round_00/worker_XX/output.html`，不進 canonical。

### Step 2: Review (Summary Evaluation)

**[spawn agent]** 平行啟動 `{{REVIEWER_COUNT}}` 個 `summary_reviewer` (`reviewer_A`, `reviewer_B`, 以此類推)

```text
---
Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_A  # 與 reviewer_B
output_root: <paper_dir>/summary/reviewer/round_00/reviewer_A
```

**[mechanical] 洗牌 (Shuffle) 規則**：Orchestrator 在傳遞 `canonical/candidate/` 下的 `summary_01.json ~ summary_N.json` 給 Reviewer 進行讀取前，必須對這 `{{WORKER_COUNT}}` 份 candidate 的順序進行**獨立的隨機洗牌 (Shuffle)**，確保每一位 reviewer 看到的 candidate 順序都不同，以此消除 LLM 評審時的 Position Bias。

`{{REVIEWER_COUNT}}` 位 Reviewer 獨立讀取洗牌後的所有候選 JSON，進行三階段評審：語感淘汰、內容比對與投票。各自寫出 `visual_review.json` 與 `review_report.md`。這種雙盲加洗牌機制可確保結果客觀與公平。

**[mechanical]** Promote：
1. 把所有 reviewer 的 `visual_review.json` 依序複製到 `canonical/voting/review_A.json`、`canonical/voting/review_B.json`…（共 `{{REVIEWER_COUNT}}` 份）。
2. `review_report.md` 留在 `reviewer/round_00/reviewer_X/`，不進 canonical。

**[mechanical]** Aggregate votes：
1. 讀取 `canonical/voting/review_*.json` 的 `global_evaluation.votes`。
2. 對每個 `summary_XX` 加總所有 reviewer 投給它的票數（未被任何 reviewer 投票者視為 0 票）。
3. 依總票數降序排序，取總票數最多的前 `{{TOP_K}}` 名（票數相同時並列）。
4. 寫入 `canonical/vote_tally.json`（完整票數表，含每位 reviewer 的明細與總和）。
5. 票數第一名即最終採用的摘要 id。

加總正確性的快速 sanity check：所有 `summary_XX` 的票數總和應等於 `{{REVIEWER_COUNT}} * {{VOTES_PER_BALLOT}}`。

### Step 3: Repair (Top-3 Refinement)

**[mechanical]** 從 `canonical/vote_tally.json` 讀出 `top_3` 列表（其長度為 `{{TOP_K}}`，依總票數排序）。

**[spawn agent]** 平行啟動 `{{TOP_K}}` 個 `summary_repair`，每個負責修補 `top_3` 中的一篇：

```text
---
Assignment
paper_dir: <paper_dir>
target_summary_id: <top_3[i]>          # i = 0, 1, ..., {{TOP_K}}-1
output_root: <paper_dir>/summary/worker/round_01/<top_3[i]>
```

每個 repair agent 獨立讀取 `canonical/candidate/<target>.json` 與所有 `canonical/voting/review_*.json`，依 reviewer 的 `findings` 與 `improvement_suggestions` 做最小修補，寫出 `output.json` 與 `output.html`。修補不動 `thinking_process`、`final_output`、`item_id`、`worker_id`，只改 `refined_final_output` 並在 `self_check` 中追加修補紀錄。

**[mechanical]** Promote repaired：
1. 把 `worker/round_01/<target>/output.json` 覆寫至 `canonical/candidate/<target>.json`。
2. HTML 留在 `worker/round_01/<target>/output.html`，不進 canonical。
3. 未進入 top `{{TOP_K}}` 的摘要在 `canonical/candidate/` 中維持 round_00 原版。

Repair 完成後，`canonical/candidate/` 中 top `{{TOP_K}}` 摘要為修補版；原始 round_00 版本仍保留在 `summary/worker/round_00/worker_XX/`，可隨時對照差異。

### Step 4: Final Extraction

**[mechanical]** 把票數前 `{{TOP_K}}` 名抽成單一精簡檔案 `canonical/summary.json`，schema 為 `summary_final.v1`：

```json
{
  "schema_version": "summary_final.v1",
  "items": [
    {
      "source_summary_id": "summary_XX",
      "rank": 1,
      "vote_total": <int>,
      "main_line": "<主線句>",
      "refined_final_output": ["第一段...", "第二段...", "..."]
    },
    ...
  ]
}
```

抽取邏輯：
1. 從 `canonical/vote_tally.json` 讀 `top_3` 與 `totals`。
2. 對 `i in 0..{{TOP_K}}-1`，target = `top_3[i]`：
   - 讀 `canonical/candidate/<target>.json`。
   - `main_line`：從 `items[0].thinking_process` 找第一筆 `step == "1"` 且 `tag == "主線"` 的卡片，取其 `content`（純字串）。
   - `refined_final_output`：把 `items[0].refined_final_output` 中每個物件的 `content` 抽出，組成字串陣列（丟掉 `sources` 欄位）。
   - `vote_total`：從 `vote_tally.totals` 查 `item_id == target` 的 `votes`。
   - rank = i + 1。
3. 依 rank 升序組成 `items`，寫入 `canonical/summary.json`。

不 spawn agent。Parent 直接執行。

### Step 5: Markdown Generation

**[inline LLM task]** Parent 直接產出給最終發布用的 Markdown。

請讀取剛生成的 `canonical/summary.json`，取用其中排名第一名（`rank: 1`）的摘要內容，並直接負責撰寫：
1. **構思短標題**：為該論文寫一個中文主題，光看標題就能知道研究的對象與核心發現，而且要流暢、一眼好懂。
   - 必須點名研究對象的實質名詞（如「DNA 開關」「染色質位置」），不能只用比喻包裝（如「音量旋鈕」這種純隱喻就不行）。
   - 盡量同時帶出核心結論或研究問題，用白話動詞描述（如「只放大縮小、不挑」），避免「XX 的效應 / 機制」這類術語空殼。
   - 十五個字為上限，但仍是「標題」而非整句話，約 10–15 字為宜——流暢、好懂優先於簡短。
   - 不能有錯誤。例如原文為靜電力，不能為了好懂而改用「磁力」
2. **取出作者資訊**：從原始論文中取出所有作者的名字。
3. **組合 Markdown**：將該短標題、作者列表、`main_line` 以及 `refined_final_output` 合併成一份 Markdown 檔案，格式如下：

```markdown
---
title: "<你構思的十五個字以內中文主題>"
author: "<作者一, 作者二...>"
---

# 主線
<main_line 的內容>

# 摘要
<refined_final_output 的所有段落，請使用適當的段落分隔>
```

4. **存檔**：將結果寫入 `<paper_dir>/summary/canonical/<paper_id>_summary.md`（其中 `<paper_id>` 為 `paper_dir` 的最後一層目錄名稱）。此步驟由 Parent 直接執行即可，不用額外 spawn subagent。
5. **[mechanical] 複製至 final**：將上述產出的 `<paper_dir>/summary/canonical/<paper_id>_summary.md` 複製一份到 `<paper_dir>/final/<paper_id>_summary.md`。
