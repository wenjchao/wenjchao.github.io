# Mapping Pipeline (v2)

## 目標

這是一份給 pipeline orchestrator 看的指引。

此流程使用場景與目標：
- 輸入：
  - `<paper_dir>/reassembly/canonical/paper.html`
  - `<paper_dir>/summary/canonical/summary.json` 與 `<paper_dir>/method/canonical/method.json`
- 輸出：把指定摘要（L1 best、或 method 某個 module top）的每個 phrase，對應到原文 HTML 裡的英文片段，產出多份結構化 mapping JSON (`mapping.<source_key>.json`)。

本檔案描述 mapping lane。

## 參數

| 變數 | 預設 | 說明 |
|---|---|---|
| `paper_dir` | （必填） | paper 目錄，由使用者直接提供 |
| `source_keys` | 自動偵測所有可用模組 | 識別碼列表，決定來源、螢光筆顏色與輸出檔名（例：`l1`, `method_m1`, `method_m2`） |

使用者會在任務中給你 `paper_dir`。如果沒有特別指定 `source_keys`，你必須自動掃描 `<paper_dir>/summary/canonical/summary.json` 與 `<paper_dir>/method/canonical/method.json`，讀後者的 `modules[]` 長度 N，推導出 `source_keys` 列表 = `l1` + `method_m1`..`method_mN`。

## 路徑慣例

| `source_key` | 摘要來源 |
|---|---|
| `l1` | `summary/canonical/summary.json` → `items[0]` |
| `method_mN` | `method/canonical/method.json` → `modules[N-1].items[0]`（`module_index = N-1`，0-based） |

## 結構

### Subagent prompts

| Prompt | 角色 |
|---|---|
| `subagent_prompts/mapping_worker.md` | 把指定摘要的每個 phrase 對應到原文 HTML 裡的英文片段，產出 mapping JSON。 |
| `subagent_prompts/mapping_reviewer.md` | 找缺陷：審查 mapping JSON 是否違反擷取或 overlap 等規則，產出 `visual_review.json`。 |
| `subagent_prompts/mapping_merger.md` | （Reference only）Step 1-9 規範。實際執行請用 `python3 agents/scripts/mapping_merger_script.py <paper_dir>`，這支 script 就是這份 spec 的 deterministic 實作。 |
| `subagent_prompts/mapping_merger_reviewer.md` | 對 merger 寫出的 `paper.html` 做外部審查；產出 `mapping_merger_review.v1` JSON，內含 `findings[]`（paper.html 必修的 rendering bug）與 `merger_bugs[]`（merger script 的誤判 / 待改項目）。 |
| `subagent_prompts/mapping_merger_repair.md` | 依 reviewer 的 `required` findings 直接 patch `paper.html`（in-place）；不碰源檔、不碰 merger script、不重跑 merger。 |

### 目錄結構

```text
<paper_dir>/
  mapping/
    worker/
      round_00/
        l1/
          output.json
        l2_m1/
          output.json
      round_01/                    # repair 時
    reviewer/
      round_00/
        l1/
          visual_review.json
      round_01/                    # re-review 時
    merger_reviewer/               # merger 寫完 paper.html 後的外部審查
      round_00/
        reviewer_01/
          visual_review.json       # schema mapping_merger_review.v1
      round_01/                    # patch 後 re-review
    merger_repair/                 # merger reviewer 標 required 後的 in-place patch
      round_00/
        worker_01/
          repair_log.json          # schema mapping_merger_repair.v1
      round_01/
    canonical/                     # canonical 輸出 (由 parent 從 worker promote)
      mapping.l1.json
      visual_review.l1.json
      mapping.l2_m1.json
      merger_review.json           # 最終一輪的 merger reviewer visual_review.json
      paper.html                   # merger 寫出 → repair worker 可能 in-place patch
```

`round_00` = initial + 第一次 review。`round_01` = 修 round_00 問題 + re-review。依此類推，不覆寫舊 round。

## 流程

Parent 只做兩種動作：
- **[spawn agent]** 啟動 subagent（委派判斷）
- **[mechanical]** 搬檔或組裝 JSON（不需判斷）

所有內容撰寫和品質判斷由 subagent 做。Parent 不改寫文字。

### Step 1: Work

**[mechanical]** 自動偵測目標：
如果使用者未提供 `source_keys`，請：
1. 確認 `<paper_dir>/summary/canonical/summary.json` 存在 → 加入 `l1`。
2. 讀 `<paper_dir>/method/canonical/method.json`，取 `modules[]` 長度 N → 加入 `method_m1`..`method_mN`。

**[spawn agent]** 針對 `source_keys` 列表中的每一個 key，解析其對應的 source 實際路徑，然後平行啟動 `mapping_worker`：

```text
---
Assignment
paper_dir: <paper_dir>
summary_path: <對應的 source JSON 實際路徑>
mode: initial
source_key: <source_key>
module_index: <method_mN 才需要；0-based index 到 modules[]>
output_root: <paper_dir>/mapping/worker/round_00/<source_key>
```

- `l1`：`summary_path` 指向 `summary/canonical/summary.json`；不需 `module_index`。
- `method_mN`：`summary_path` 指向 `method/canonical/method.json`；`module_index` = N - 1。

每個 Worker 獨立讀取 source、`paper.html`，找出 mapping 並寫出 `output.json` 到指定的 `output_root` 內。

### Step 2: Promote

**[mechanical]** Promote：
1. 等待所有 worker 完成任務。
2. 收集所有 worker 的 `output.json`。
3. 重新命名檔案並複製到 `<paper_dir>/mapping/canonical/mapping.<source_key>.json`。

### Step 3: Review

**[spawn agent]** 針對 `source_keys` 列表中的每一個 key，平行啟動 `mapping_reviewer`：

```text
---
Assignment
paper_dir: <paper_dir>
summary_path: <對應的 source JSON 實際路徑>
module_index: <method_mN 才需要；0-based index 到 modules[]>
review_round: round_00
source_key: <source_key>
output_root: <paper_dir>/mapping/reviewer/round_00/<source_key>
```

`summary_path` 與 `module_index` 規則同 Step 1。Reviewer 將讀取 source、`paper.html` 以及 mapping JSON，審查字串是否精確相符並產出 review 結果。Re-review 時只把 `review_round` 和 `output_root` 換到下一輪（例如 `round_01`）。

**[mechanical]** Promote：把所有 reviewer 的 `visual_review.json` 重新命名並複製到 `canonical/visual_review.<source_key>.json`。

### Step 4: Gate

讀取所有的 `canonical/visual_review.<source_key>.json`：
- 若所有 key 的 `findings` 都是空陣列 → 品質過關，進入 Step 6: Merge。
- 有 `severity: "required"` 的 findings → 針對該 key 進入 Step 5: Repair。
- Round limit 達到（預設 4 輪）→ blocked。

Parent 不得自己做品質判斷來 override reviewer。有 fail 的 key 時不得靜默 close。

### Step 5: Repair

**[spawn agent]** 針對有 required findings 的 `source_key`，啟動 `mapping_worker`（repair mode）：

```text
---
Assignment
paper_dir: <paper_dir>
summary_path: <對應的 source JSON 實際路徑>
module_index: <method_mN 才需要；0-based index 到 modules[]>
mode: repair
source_key: <source_key>
output_root: <paper_dir>/mapping/worker/round_01/<source_key>
```

Worker 讀取 `summary_path`、`paper.html`、`canonical/mapping.<source_key>.json`（目前成果）與 `canonical/visual_review.<source_key>.json`（findings），針對有問題的物件進行修正並輸出 `output.json`。

**[mechanical]** Promote：
1. 複製新檔案並覆蓋 `canonical/mapping.<source_key>.json`。
2. 回到 Step 3，只對被修復的 `source_key` 啟動 reviewer 進行 re-review。已 pass 的 key 不重新審查。下一輪寫到 `reviewer/round_01/`。

### Step 6: Merge

**[mechanical]** 直接執行確定性 Python 組合器（取代舊版 LLM `mapping_merger` agent）：

```bash
python3 agents/scripts/mapping_merger_script.py <paper_dir>
```

腳本讀取 `<paper_dir>/mapping/canonical/` 內所有 `mapping.*.json`，套用到 `<paper_dir>/reassembly/canonical/paper.html`，注入 reader panel + margin rail + color toggle，最終寫到 `<paper_dir>/mapping/canonical/paper.html`。實作就是 `subagent_prompts/mapping_merger.md` 的 Step 1-9 規範，含 11 條 self-check。

**self-check 不再是 hard gate**：不論 11/11 PASS 或部分 fail，腳本都會寫出 paper.html，由下一步 Merger Reviewer 做外部審查決定是否需要修。**Parent 必須抓 stdout** 並轉交給 reviewer。

如果未來要進一步修補規則，編輯 `subagent_prompts/mapping_merger.md`（spec）+ 同步改 `scripts/mapping_merger_script.py`（實作）。LLM agent 版本已退役，不再使用。

### Step 7: Merger Review

**[spawn agent]** 啟動 1 個 `mapping_merger_reviewer`：

```text
---
Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
output_root: <paper_dir>/mapping/merger_reviewer/round_00/reviewer_01
self_check_stdout: |
  <Step 6 印出的完整 stdout，包含每條 [Step 9] check N PASS/FAIL>
```

Reviewer 讀 `mapping/canonical/paper.html`、所有 `mapping.*.json`、`method.json`、`summary.json`、`mapping_merger.md` spec，產出 `visual_review.json`（schema `mapping_merger_review.v1`），含：

- `findings[]`：reader-visible rendering bug。`severity: required` 觸發 repair；`severity: advisory` 僅記錄不卡 gate。
- `merger_bugs[]`：reviewer 判定為 merger script bug 或 self-check 誤判的條目。**不影響 gate**，會在最後一輪 close 時呈給 user。

Re-review 時把 `review_round` 換到 `round_01` 等，並只審被 patch 過的範圍。

**[mechanical]** Promote：把 reviewer 的 `visual_review.json` 複製成 `<paper_dir>/mapping/canonical/merger_review.json`。

### Step 8: Merger Repair Gate

讀 `mapping/canonical/merger_review.json`：

- 沒有 `required` finding → 進入 Step 10 Finalize。
- 有 `required` finding 且 round < 4 → 進入 Step 9 Repair。
- Round limit（預設 4 輪）達到 → 回報 Blocked。

Parent 不得 override reviewer。Repair 完成後 re-review 不允許靜默 close。

### Step 9: Merger Repair

**[spawn agent]** 啟動 1 個 `mapping_merger_repair`：

```text
---
Assignment
paper_dir: <paper_dir>
review_path: <paper_dir>/mapping/canonical/merger_review.json
repair_round: round_00
worker_id: worker_01
output_root: <paper_dir>/mapping/merger_repair/round_00/worker_01
```

Repair worker **直接 in-place patch `mapping/canonical/paper.html`**，並寫 `<output_root>/repair_log.json`（schema `mapping_merger_repair.v1`），裡面分 `patches[]`（已修）與 `skipped[]`（無法在 HTML 層修，附 reason）。

**禁止**：
- 改任何源檔（`mapping.*.json`、`method.json`、`summary.json`）——這是上游 lane 的責任，且改了會被下次 merger 重跑蓋掉。
- 改 `mapping_merger_script.py` 或 `mapping_merger.md` spec——這由 user 在收到 `merger_bugs` 報告後決定。
- 重跑 `mapping_merger_script.py`——會把這次 patch 蓋掉。

Repair 完成後回到 Step 7 做 re-review（下一個 round）。

### Step 10: Finalize

**[mechanical]** Promote to final:
將 `<paper_dir>/mapping/canonical/paper.html` 複製並覆寫到 `<paper_dir>/final/<paper_id>.html`（其中 `<paper_id>` 為 `paper_dir` 的目錄名稱）。

### Step 11: Surface merger_bug_report

**[mechanical]** Gate close 後一律執行：

1. 讀最終一輪的 `mapping/canonical/merger_review.json` 取 `merger_bugs[]`。
2. 讀最終一輪的 `mapping/merger_repair/round_<N>/worker_<X>/repair_log.json` 取 `skipped[].reason`。
3. 把兩份合併呈給 user，每條包含 `kind`、`evidence`、`suggested_fix`，並標出「paper.html 已 patch 但根本問題仍在源檔／merger」。
4. **詢問 user 是否要修 merger script 或源檔**；user 決定，Parent 不主動改 merger 或源檔。

這一步是「下一篇 paper 跑同樣 merger 不再踩同樣雷」的入口；不做這步等於 paper.html patch 是暫時的、下次 merger 重跑會回到壞狀態。
