# 通用 Pipeline 模板

這份模板定義一個通用 pattern：scanner → worker → reviewer，搭配 canonical promote 和 findings-based repair loop。可以套用在任何需要「辨識 → 處理 → 審查」的任務上。

不是每條 lane 都需要全部角色。沒有 scanner 時 worker 直接從輸入開始；沒有 reviewer 時 worker 自檢就是品質關卡；沒有 repair loop 時 one-shot 執行；一條 lane 可以有多種 worker（如 worker + merger）。根據需要裁剪。

寫作指南和設計原則詳見 `rewrite_goals.md`。

以下四段是四個獨立模板。複製你需要的段落到新檔案，把 `{{placeholder}}` 替換成你的內容。`{{...}}` 是需要填寫的空格；其餘文字是固定骨架，直接保留。

---

# Scanner Prompt 模板

> 複製到 `subagent_prompts/{{lane}}_scanner.md`

## 目標

這是一份給 {{LANE}}_scanner agent 看的指引。

此流程使用場景與目標：
- 輸入：{{scanner 讀什麼（paper directory、HTML 檔案、API 回應…）}}。
- 輸出：`<output_root>/{{plan_json}}`
- 目標：{{辨識什麼目標物件、產出什麼清單、給誰用}}。
- 邊界：此 agent 只負責辨識。{{列出不做的事——不執行核心任務、不產生最終成果}}。

## 流程

### Step 1: 確認前置條件

{{需要什麼輸入存在？缺少時怎麼處理（回報 blocked？部分執行？）}}

### Step 2: 掃描並辨識

{{核心辨識工作：
- 看什麼來源（逐頁？逐段？逐 API call？）
- 用什麼線索辨識目標物件
- 每個物件記錄什麼資訊（ID、位置、描述、初始參數…）
如果辨識邏輯有分支，在這裡展開。}}

### Step 3: 填寫 notes

每個物件的 `notes` 是**必填**欄位，是下游 worker 定位和理解物件的主要依據。`notes` 必須包含：

{{必填內容因 lane 而異，但通常包含：
1. 物件的描述（讓 worker 能辨識「這是哪個物件」）
2. 位置資訊（讓 worker 能找到物件）
3. 周圍 context（讓 worker 理解物件的環境）}}

Scanner 的初始參數可能不準確——notes 是 worker 的 fallback 定位依據。

### Step 4: 寫出 plan 並自檢

寫出 `{{plan_json}}`（格式見下方 `## 格式`），然後自檢：
- JSON 可 parse。
- `schema_version` 正確。
- 每個物件有 ID、notes（非空）。
- {{lane-specific 自檢——如 ID 連續、沒有重複、覆蓋所有來源等}}

## 格式

`{{plan_json}}`，`schema_version: "{{lane}}_plan.v1"`。

### Example

```json
{
  "schema_version": "{{lane}}_plan.v1",
  "items": [
    {
      "item_id": "Item_1",
      "page": 2,
      "initial_params": {},
      "notes": "第一段落描述了... 位於左欄中段..."
    },
    {
      "item_id": "Item_2",
      "page": 5,
      "initial_params": {},
      "notes": "..."
    }
  ]
}
```

### 規則

- **`item_id`**：`{{ID_PREFIX}}_N`，從 1 開始連續編號。{{平行 scanner 時合併後重新編號。}}
- **`initial_params`**：{{估算策略——寧可大不要小？精確優先？}}
- **`notes`**：必填。{{重複 Step 3 的必填內容摘要}}。

---

# Worker Prompt 模板

> 複製到 `subagent_prompts/{{lane}}_worker.md`

## 目標

這是一份給 {{LANE}}_worker agent 看的指引。

此 agent 做一件事：{{一句話描述核心任務和品質目標}}。

這個 agent 同時用於兩種場景：
- **Initial {{動作名}}**：scanner 給出{{什麼}}，worker {{做什麼}}。
- **Repair**：reviewer 發現問題，worker {{根據 findings 做什麼修正}}。

兩種場景的核心流程相同（{{流程摘要}}），輸出格式相同（`{{output_json}}`）。差別在輸入來源：initial 讀 `canonical/{{plan_json}}`，repair 讀 `canonical/{{output_json}}` + `canonical/visual_review.json`。

- 輸入：`<paper_dir>`、`mode`（initial / repair）、`item_ids`、`output_root`。
- 輸出：`{{output_json}}`{{、其他產出檔案（如果有）}}。

### Worker 不做的事

- 不修改 canonical 或上游檔案。
- 不發明輸入中沒有的內容。
- 不做 gate 判定。
{{其他權責邊界。每條都具體。}}

{{（選填）為什麼這件事不容易：

### 為什麼這件事不容易

（2-3 個讓這個任務需要判斷而非機械操作的機制）
}}

## 流程

{{（選填）工具表：

### 工具

| Tool | 用途 |
|---|---|
| `script_name.py` | 一句話說明 |
}}

本指引中列出的檢查項目和 pattern 是常見失敗機制的例子，不是完整清單。如果成果看起來不對，即使不符合任何列出的 pattern，也要調查。

### Step 1: 讀取輸入

**`mode: initial`**：讀 `canonical/{{plan_json}}`，根據 assignment 的 `item_ids` 過濾。{{說明注意什麼——如可疑區域、qc_notes}}

**`mode: repair`**：讀 `canonical/{{output_json}}`（目前成果）+ `canonical/visual_review.json`（findings）。Finding 的 notes 包含觀察和成因——worker 據此修正，不需重新調查。

### Step 2: {{核心工作步驟名稱}}

{{展開核心工作流程。用 #### 2a、2b、2c 分段。
每個 sub-step 描述「看什麼 → 做什麼 → 產出什麼」。
標出 initial 和 repair 的差異點。}}

#### 常見失敗

{{這個任務常在哪裡出錯：
- 失敗模式 1
- 失敗模式 2
- ...
這些是失敗機制，不是檢查清單。如果成果看起來不對，即使不符合上面任何 pattern，也要調查。}}

### Step 3: 驗證

{{完成後的驗證：
- 回頭對照 ground truth 確認成果正確
- 覆蓋檢查（所有 item_ids 都處理了嗎？）
- 一致性檢查（物件之間沒有矛盾嗎？）
不確定時先讀 source 確認；仍不確定在 notes 記錄——reviewer 會決定是否需要 repair。}}

### Step 4: 寫出成果並自檢

寫出 `{{output_json}}`（格式見下方 `## 格式`），然後自檢：
- JSON 可 parse。
- `schema_version` 正確。
- `worker_id` 存在且非空。
- 每個物件有完整的必填欄位。
- {{lane-specific 自檢}}

## 格式

`{{output_json}}`，`schema_version: "{{lane}}.v1"`。

### Example

```json
{
  "schema_version": "{{lane}}.v1",
  "worker_id": "worker_01",
  "items": [
    {
      "item_id": "Item_1",
      "...": "{{lane-specific 欄位}}",
      "notes": []
    }
  ]
}
```

### 規則

{{用 flat bullet list。每條規則一個概念：
- **`欄位名`**：說明。先給正確寫法，再給禁止寫法。
}}

---

# Reviewer Prompt 模板

> 複製到 `subagent_prompts/{{lane}}_reviewer.md`

## 目標

這是一份給 `{{LANE}}_reviewer` agent 看的指引。

Reviewer 的工作是找缺陷，不是背書。{{一句話描述審查什麼成果、對照什麼 ground truth}}。

- 輸入：`<paper_dir>`、`review_round`、`reviewer_id`、`output_root`、`item_ids`（或 `all`）。
- 讀取位置：`<paper_dir>/{{lane}}/canonical/{{output_json}}`。{{其他需要讀的檔案}}。
- 輸出位置：`<paper_dir>/{{lane}}/reviewer/round_<N>/reviewer_<ID>/`
- 輸出：`visual_review.json`。

核心判斷依據：
{{用什麼 evidence 做什麼判斷：
- **evidence A**：用來判斷什麼。
- **evidence B**：用來判斷什麼。
- **ground truth**：最終依據。和其他 evidence 有衝突時以此為準。}}

- 誤報比漏報傷害更大——false positive 觸發錯誤修復。不確定時進一步確認；仍無法判定則不標。

### Reviewer 不做的事

- 不修改 `{{output_json}}` 或任何 canonical 檔案。
- 不改寫內容、不猜缺失內容。
- 不做 gate 判定。
{{其他權責邊界}}

## 流程

本指引中列出的檢查項目和 pattern 是常見失敗機制的例子，不是完整清單。如果成果看起來不對，即使不符合任何列出的 pattern，也要調查。

### Step 1: 準備審查資料

#### 1a. 確認 assignment

確認 `paper_dir`、`review_round`、`reviewer_id`、`output_root`、`item_ids`。

#### 1b. 讀取成果

讀取 `canonical/{{output_json}}`。根據 assignment 的 `item_ids` 過濾要審查的物件。

{{如果成果中有 worker 自檢結果（如 verification.result = "fail"），說明優先審查這些。}}

`review_round` 不是 `round_00` 時，這是 repair 後的 re-review。只審查 assignment 中的 `item_ids`，並沿用本 prompt 的正常審查來源判斷是否通過；不要讀上一輪 review。

### Step 2: {{核心審查步驟名稱}}

{{展開審查流程。用 #### sub-step 分段。
描述「看什麼 → 和什麼比對 → 什麼算問題」。

常見的審查結構（選一個或組合）：
- 建立獨立 baseline（如 inventory）→ 和成果比對。
- 逐物件審查 → 覆蓋與一致性檢查。
- 逐面向審查（適用於 final output review）。

用「常見但非全部的問題 pattern」framing：
- pattern 1
- pattern 2
- ...
如果看起來不對，即使不符合上面任何 pattern，也要調查。}}

### Step 3: 判定與輸出

#### Pass / fail 判定

Pass / fail 由 `findings[]` 決定：
- **Pass**（`findings` 留空）：{{列出 pass 條件}}。
- **Fail**（`findings` 非空）：每個 finding 只描述一個可修的問題。
- 不要用「大概」、「不清楚」等模糊註記把物件判定為 pass。確定有問題 → fail；確定沒問題 → pass；不確定 → 進一步確認（讀 source 或用輔助工具），仍無法判定則不標。
- 對過短的問題清單保持懷疑，尤其是第一次 review。宣稱全部 pass 前，確認所有檢查都已完成。
- 模糊地帶不標。如果 worker 的選擇合理（{{列出 2-3 個灰色地帶例子}}），即使 reviewer 自己會做不同選擇，也不構成 finding。只標記{{什麼算明確問題}}。

#### Self-check 與寫出

寫出 `visual_review.json`（格式見下方 `## 格式`），然後做 local self-check：
- JSON 可 parse。
- `schema_version` 正確。
- `reviewer_id` 存在且非空。
- 每個 assignment 中的物件都有 entry（即使 findings 為空）。少於應審查數 = 審查未完成。
- 每個 finding 有 `condition`、`severity`、`notes`。
- 不使用 Example 中不存在的頂層欄位。

## 格式

`visual_review.json`，`schema_version: "{{lane}}_review.v1"`。沒有 top-level `status`、`decision`、`summary`、`review_round`。

### Example

```json
{
  "schema_version": "{{lane}}_review.v1",
  "reviewer_id": "reviewer_01",
  "items": [
    {
      "item_id": "Item_1",
      "findings": []
    },
    {
      "item_id": "Item_2",
      "findings": [
        {
          "condition": "{{example_condition}}",
          "severity": "required",
          "notes": "Item_2 的 X 部分顯示 A，但 ground truth 顯示 B。可能原因是 C。Worker 應從 ground truth 重新 D。"
        }
      ]
    },
    {
      "item_id": null,
      "findings": [
        {
          "condition": "missing_content",
          "severity": "required",
          "notes": "{{描述遺漏了什麼、在哪裡應該有、為什麼被遺漏}}"
        }
      ]
    }
  ]
}
```

### 規則

- **`condition`**（建議值，可自訂 snake_case）：{{列出此 lane 常見的 condition 和說明}}。
- **`severity`**：`required`（影響品質標準）| `advisory`（不影響品質標準的小問題）。
- **`notes`**——**最重要的欄位。** 必填，必須包含：(1) **觀察**——具體看到什麼（哪個物件、哪個位置、什麼內容）。(2) **成因推測**——為什麼會有這個問題。好的 notes 讓 repair worker 不用重新調查就能修正。不好的 notes：`"Looks wrong."`
- **`item_id`**：可填 `null`（不屬於特定物件的全域問題，如 missing_content）。
- Finding 不得包含修復後的內容——repair worker 自己重做。

---

# SKILL Section 模板

> 複製到 `SKILL.md` 中作為一條 lane 的段落

## {{LANE_NAME}} Lane

Prompt：`{{lane}}_scanner.md`、`{{lane}}_worker.md`、`{{lane}}_reviewer.md`

### Subagent prompts

| Prompt | 角色 |
|---|---|
| `subagent_prompts/{{lane}}_scanner.md` | {{scanner 一句話角色描述}} |
| `subagent_prompts/{{lane}}_worker.md` | {{worker 一句話角色描述}} |
| `subagent_prompts/{{lane}}_reviewer.md` | {{reviewer 一句話角色描述}} |

### 目錄結構

```text
<paper_dir>/
  {{lane}}/
    scanner/
      {{plan_json}}
    worker/
      round_00/
        worker_01/
          {{output_json}}
          {{其他輸出}}
        worker_02/           # 平行時
      round_01/
        worker_01/           # repair
    reviewer/
      round_00/
        reviewer_01/
          visual_review.json
        reviewer_02/         # 平行時
      round_01/
        reviewer_01/
    canonical/               # live state——所有下游 agent 的唯一讀取來源
      {{plan_json}}
      {{output_json}}
      visual_review.json
      {{其他 canonical 內容}}
```

`round_00` = initial + 第一次 review。`round_01` = 修 round_00 問題 + re-review。依此類推，不覆寫舊 round。

### Step 1: Scan

**[spawn agent]** 啟動 {{lane}}_scanner

```text
---
Assignment
paper_dir: <paper_dir>
output_root: <paper_dir>/{{lane}}/scanner
{{其他 scanner 欄位}}
```

Scanner {{做什麼}} → `{{plan_json}}`。

**[mechanical]** Promote：把 `scanner/{{plan_json}}` 複製到 `canonical/`。

{{（選填）平行 scanner 合併：
1. Concat 所有 scanner 的 items array。
2. 按 {{sort_key}} 排序。
3. 重新指派全局 item_id（從 1 開始）。不得有重複 ID。
4. 寫 `scanner/{{plan_json}}`。
5. 複製到 `canonical/`。}}

### Step 2: Work

**[spawn agent]** 啟動 {{lane}}_worker

把 item_ids 分成 N 組（建議每組 ≤{{建議數量}}；不分組時 N=1）。

```text
---
Assignment
paper_dir: <paper_dir>
mode: initial
worker_id: worker_01
output_root: <paper_dir>/{{lane}}/worker/round_00/worker_01
item_ids: [Item_1, Item_2, Item_3]
```

Worker 讀 `canonical/{{plan_json}}`，只處理自己的 `item_ids`，{{做什麼}}，寫出 `{{output_json}}`{{和其他輸出}}。多個 worker 時 IN PARALLEL 執行。

**[mechanical]** Promote：

多 worker 時先合併：
1. Concat 所有 worker 的 items array → `worker_id` 改為 `"merged"`。
2. {{複製成果檔案——用什麼方式、複製什麼}}。
3. 寫合併後的 `{{output_json}}` 到 `canonical/`。

單 worker 時直接複製。round_00 時也複製 `{{plan_json}}`。

### Step 3: Review

**[spawn agent]** 啟動 {{lane}}_reviewer

分組（建議每組 ≤{{建議數量}}，可以和 worker 不同分法）：

```text
---
Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
output_root: <paper_dir>/{{lane}}/reviewer/round_00/reviewer_01
item_ids: [Item_1, Item_2, Item_3]
```

Re-review 時只把 `review_round` 和 `output_root` 換到下一輪，並把 `item_ids` 限縮到修復過的物件。

**[mechanical]** Promote：把 reviewer 的 `visual_review.json` 複製到 `canonical/`。

多 reviewer 時合併：Concat items array，`reviewer_id` → `"merged"`。Overlap 物件的 findings 去重（same condition + severity）。合併後必須覆蓋所有物件。

### Step 4: Gate

讀 `canonical/visual_review.json`：
- 所有物件的 `findings` 都是空陣列 → lane close。
- 有 `severity: "required"` 的 findings → Step 5。
- Round limit 達到（預設 4 輪）→ blocked。

Parent 不得自己做品質判斷來 override reviewer。有 fail 物件時不得靜默 close。

### Step 5: Repair

**[spawn agent]** 啟動 {{lane}}_worker（repair mode）

Parent 從 `canonical/visual_review.json` 取出有 required findings 的 item_ids。分組（建議每組 ≤{{repair 建議數量}}）：

```text
---
Assignment
paper_dir: <paper_dir>
mode: repair
worker_id: worker_01
output_root: <paper_dir>/{{lane}}/worker/round_01/worker_01
item_ids: [Item_2]
```

Worker 讀 `canonical/{{output_json}}`（目前成果）+ `canonical/visual_review.json`（findings），修正有問題的物件。

**[mechanical]** Promote：

{{Promote 步驟：
1. 刪舊檔（如果適用）：{{用 glob 還是確切檔名？}}
2. 複製新檔案。
3. 在 canonical {{output_json}} 中替換被修復的 entries（by item_id）。}}

回到 Step 3，只對被修復的 item_ids 啟動 reviewer re-review。已 pass 的物件不重新審查。下一輪寫到 `reviewer/round_01/`。

---

# 設計決策

填寫模板前先回答這些問題。不是每個都適用——根據需要選擇。

**Scanner**：辨識什麼、用什麼線索？Notes 必填什麼？初始參數估算策略？是否平行、合併排序 key？

**Worker**：核心任務和品質目標？用什麼工具？Initial vs repair 差異？是否平行、怎麼分組？是否需要 merger？輸出有什麼檔案？Ground truth 是什麼？「為什麼不容易」值得寫嗎？常見失敗模式？

**Reviewer**：對照什麼 ground truth？需要什麼 evidence？什麼算 pass / fail？灰色地帶例子？常見 condition 值？Notes 必填什麼？

**SKILL Section**：Promote 複製什麼、用什麼方式？合併規則？Repair 刪舊檔方式？分組大小（initial vs repair）？Round limit？
