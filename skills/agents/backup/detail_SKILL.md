# Detail Pipeline

## 目標

這是一份給 detail lane orchestrator 看的指引。

把 `detail_scanner.md` 階段產出的 5–7 個模塊規劃，逐一展開成「迷你 summary pipeline」，產出每個模塊的最終解析。

- **輸入**：
  - `<paper_dir>/reassembly/canonical/paper.html`（論文原文，與 summary lane 同源）
  - `<paper_dir>/detail/detail_plan.md`（規劃階段輸出：模塊總覽 + Shared Utilities）
  - `<paper_dir>/summary/canonical/summary.json` 中指定一份 baseline summary（作為讀者已知共同語言）
- **輸出**：
  - N 份 per-module `<paper_dir>/detail/module_<N>_<slug>/canonical/module.json`（每份含 top-K 解析）
  - 1 份 top-level `<paper_dir>/detail/canonical/detail.json`（聚合全 N 個模塊，schema = `detail_final.v1`）

本檔案描述 detail lane，包含起頭的 Scanner 模塊拆解，到各模塊的 Detail 解析與最終聚合。

## 檔案生命週期與意涵 (File Lifecycle)

為避免混淆，以下是 Detail Pipeline 中各個 JSON 檔案的演進與其意涵：
1. **`output.json` (寫手草稿)**：由每個 `detail_worker` 獨立產生，存放在自己的工作區 (如 `worker/round_00/worker_01/output.json`)。
2. **`detail_XX.json` (候選名單)**：Orchestrator 收集所有草稿後，集中放置於 `canonical/candidate/` 並統一定名，供 Reviewer 評審。
3. **`module.json` (單一模塊得獎榜單)**：Reviewer 投票後，Orchestrator 將該模塊 Top-K 的 `detail_XX.json` 抽出聚合，成為代表**「該模塊最終成果」**的檔案 (`module_<N>_<slug>/canonical/module.json`)。
4. **`detail.json` (全篇模塊大集結)**：最後，Orchestrator 將所有模塊的 `module.json` 統整，產出代表**「整篇論文 Detail 總驗收」**的最終檔案 (`detail/canonical/detail.json`)。

## 參數

| 變數 | 預設 | 說明 |
|---|---|---|
| `MODULE_COUNT` | 3–7 | 由 `detail_scanner.md` 階段決定 |
| `WORKER_COUNT` | 8 | 全域啟動的 worker 總數（每個 worker 一次處理所有模塊） |
| `REVIEWER_COUNT_PER_MODULE` | 3 | 每個模塊啟動的 reviewer 數 |
| `VOTES_PER_BALLOT` | 7 | 每位 reviewer 在單一模塊中的總票數（採 4, 3, 0 票型，即第一名 4 票、第二名 3 票、第三名 0 票） |
| `TOP_K` | 3 | 每個模塊保留的最終解析數 |
| `BATCH_SIZE` | 2–3 | Reviewer 階段並行批次的模塊數（避免一次 spawn 過多） |
| `BASELINE_SUMMARY_INDEX` | 0 | `summary/canonical/summary.json` 中 `items[BASELINE_SUMMARY_INDEX]` 為讀者輪廓的 baseline（預設第 1 名） |

要調整數量，只改本表的預設值即可。下方流程文以 `WORKER_COUNT` 等變數引用，請勿在流程文中再寫死數字。

**TOP_K 耦合**：`TOP_K` 一處改動同步影響——
1. Reviewer Stage 1 淘汰後留下「語感前 TOP_K 名」進入 Stage 2 與 Stage 3。
2. Reviewer Stage 3 投票：選票上恰好 `TOP_K` 名候選人。
3. Step 4 Final Extraction：每個 module 的 `canonical/module.json` 的 `items` 長度 = `TOP_K`。

## 路徑慣例

`paper_dir = workspace/<paper_slug>`（沿用 SKILL.md）。Module 路徑慣例：`<paper_dir>/detail/module_<N>_<slug>/`，N = 1..MODULE_COUNT。

每個 `module_<N>_<slug>` 內部目錄結構與 summary lane 一致（見下節）。

## 使用的 subagent prompts

本 lane 使用專屬的模塊展開 prompts：

| 角色 | 沿用檔案 |
|---|---|
| Scanner | `subagent_prompts/detail_scanner.md` |
| Worker | `subagent_prompts/detail_worker.md` |
| Reviewer | `subagent_prompts/detail_reviewer.md` |
| Repair (optional) | `subagent_prompts/summary_repair.md` |

Schema：`detail.v1`（worker output / candidate）、`detail_module_final.v1`（module.json）、`detail_final.v1`（detail.json），HTML 骨架沿用 worker 規範。

## 目錄結構（每個 `module_<N>_<slug>` 都一致）

```text
<paper_dir>/
  detail/
    detail_plan.md                      # 規劃階段輸出（input）
    shuffles.json                       # Parent 產生：per-module per-reviewer 候選洗牌順序
    worker/
      round_00/                         # 全域 worker（每個 worker 一次處理所有模塊）
        worker_01/
          output.json
          output.html
        ...
        worker_<WORKER_COUNT>/
    module_<N>_<slug>/
      worker/
        round_01/                       # Repair（可選），只跑票數 top-K
          detail_XX/
            output.json
            output.html
      reviewer/
        round_00/                       # Per-module reviewer
          reviewer_A/
            visual_review.json
            review_report.md
          ...
          reviewer_<REVIEWER_COUNT_PER_MODULE>/
      canonical/                        # live state——所有下游 agent 唯一結構化資料來源
        candidate/                      # Worker detail
          detail_01.json
          ...
          detail_<WORKER_COUNT>.json
        voting/                         # Reviewer 投票結果
          review_A.json
          ...
        vote_tally.json                 # Parent 聚合票數
        module.json                     # Final delivery：top-K（schema = detail_module_final.v1）
```

> HTML 與 `review_report.md` 等人類視角衍生視圖**不進 canonical**，留在對應 work folder。

## Round 命名

- `detail/worker/round_00/`：全域 worker（每個 worker 一次處理所有模塊）。
- `module_<N>_<slug>/reviewer/round_00/`：per-module reviewer。
- `module_<N>_<slug>/worker/round_01/`：top-K repair only（可選；沒有 `reviewer/round_01/`）。
- 不覆寫舊 round 的 work folder；`canonical/` 視為 live state，新 round promote 會覆寫對應檔案。

## 流程

Parent 只做兩種動作（與 summary lane 一致）：
- **[spawn agent]** 啟動 subagent
- **[mechanical]** 搬檔或組裝 JSON（不需判斷）

所有內容撰寫和品質判斷由 subagent 做。Parent 不改寫文字。

### Step 0：Scanner (Planning)

[spawn agent] 啟動 1 個 `detail_scanner`：
讀取論文原文與 baseline summary，進行五軸掃描並決定模塊切分，產出 `<paper_dir>/detail/detail_plan.md`。

[mechanical] 讀 `<paper_dir>/detail/detail_plan.md`，取出 `MODULE_COUNT` 與每個模塊的下列欄位（皆來自模塊總覽表格那一行）：
- `slug`（kebab-case-ascii；orchestrator **不自行 invent**，一律以表格欄為準）
- `一句話 thesis`（表格欄那一欄、僅 1 句）

下游 worker / reviewer 路徑一律以 `module_<N>_<slug>/` 命名（N = 1..MODULE_COUNT，slug 從表格欄取）。

[mechanical] 確認 `<paper_dir>/summary/canonical/summary.json` 的 `items[BASELINE_SUMMARY_INDEX]` 存在。Parent 不抽詞清單；assignment 只傳 `baseline_summary_path` 與 `baseline_summary_index`，worker / reviewer 直接讀該摘要判讀哪些詞屬於 baseline 已涵蓋。

### Step 1：Work

直接全域 [spawn agent] `WORKER_COUNT` 個 `detail_worker`，每個 worker 一次處理所有模塊：

```text
Subagent prompt = <detail_worker.md 全文>

---
Assignment
paper_dir: <paper_dir>
paper_file: <paper_dir>/reassembly/canonical/paper.html
baseline_summary_path: <paper_dir>/summary/canonical/summary.json
baseline_summary_index: <BASELINE_SUMMARY_INDEX>
modules:
  - module_id: module_1_<slug1>
    thesis: <detail_plan.md 第一個模塊的一句話 thesis>
  - module_id: module_2_<slug2>
    thesis: <detail_plan.md 第二個模塊的一句話 thesis>
  ... (包含全部 MODULE_COUNT 個模塊)
mode: initial
worker_id: worker_<XX>   # XX = 01..WORKER_COUNT
output_root: <paper_dir>/detail/worker/round_00/worker_<XX>
```

每個 worker 獨立讀取論文與 baseline summary，按 assignment 產出包含多個模塊的 `output.json` + `output.html`。

[mechanical] **Promote**：
1. 收集 `WORKER_COUNT` 個 worker 的全域 `output.json`。
2. 將每個 worker 的 `output.json` 中 `modules` 陣列「拆散」到各個模塊目錄下。對於 `modules` 中的第 `i` 個元素：
   - 抽出該元素的內容，包裝成單模塊形式的 JSON：`{ "schema_version": "detail.v1", "worker_id": "worker_<XX>", "items": [ <抽出元素> ] }`。
   - 把抽出的元素中的 `item_id` 改為 `detail_<XX>`。
   - 寫入對應的 `<paper_dir>/detail/module_<N>_<slug>/canonical/candidate/detail_<XX>.json`。
3. HTML 留在全域 worker round folder，不進 canonical。

### Step 1.5：產生 Shuffle 計畫

[mechanical] Parent 產生 `<paper_dir>/detail/shuffles.json`，內容為每個模塊、每位 reviewer 各自獨立的候選順序：

```json
{
  "module_<N>_<slug>": {
    "reviewer_A": ["detail_03", "detail_07", "..."],
    "reviewer_B": ["..."],
    ...
    "reviewer_<最後一位>": ["..."]
  },
  ...
}
```

產法：對每個 `(module_id, reviewer_id)` 組合，把該模塊 `canonical/candidate/` 下的 `WORKER_COUNT` 個 `detail_XX` 獨立隨機洗牌一次，確保每位 reviewer 看到的 candidate 順序都不同，以消除 LLM 評審時的 Position Bias。

Reviewer 在 Step 2 會被傳入 `shuffles_path`，並以 `[module_id][reviewer_id]` 取得自己該讀的順序。

### Step 2：Review（per batch）

把 `MODULE_COUNT` 個模塊按 `BATCH_SIZE` 分批。每批同時 [spawn agent] `BATCH_SIZE × REVIEWER_COUNT_PER_MODULE` 個 `detail_reviewer`：

```text
Subagent prompt = <detail_reviewer.md 全文>

---
Assignment
paper_dir: <paper_dir>
baseline_summary_path: <paper_dir>/summary/canonical/summary.json
baseline_summary_index: <BASELINE_SUMMARY_INDEX>
module_id: module_<N>_<slug>
shuffles_path: <paper_dir>/detail/shuffles.json
review_round: round_00
reviewer_id: reviewer_<X>   # X = A..(A + REVIEWER_COUNT_PER_MODULE - 1)
output_root: <paper_dir>/detail/module_<N>_<slug>/reviewer/round_00/reviewer_<X>
```

每個 reviewer 讀 `shuffles.json` 中 `[module_id][reviewer_id]` 給定的順序，按該順序讀取 `<paper_dir>/detail/module_<N>_<slug>/canonical/candidate/<detail_XX>.json`，三階段評審後產出 `visual_review.json` + `review_report.md`。

[mechanical] **Promote**：
1. 把每個 reviewer 的 `visual_review.json` 複製到 `<paper_dir>/detail/module_<N>_<slug>/canonical/voting/review_<X>.json`。
2. `review_report.md` 留在 reviewer folder，不進 canonical。

### Step 3：Vote Tally（per module）

[mechanical] 對每個 module_<N>_<slug>：
1. 讀 `canonical/voting/review_*.json` 的 `global_evaluation.votes`。
2. 對每個 `detail_XX` 加總票數（未被投票者視為 0）。
3. 依總票數降序排序，取 top-`TOP_K`（票數相同並列；下游可由 sort 穩定性決定順序）。
4. 寫 `canonical/vote_tally.json`（含 `per_reviewer`、`totals`、`top_k`、`top`、`schema_version: "detail_vote_tally.v1"`）。

**Sanity check**：每模塊 `Σ votes = REVIEWER_COUNT_PER_MODULE × VOTES_PER_BALLOT`（採 4-3-0 票型時，第 3 名雖然 0 票仍需出現在 ballot 上）。

### Step 4：Final Extraction（per module）

[mechanical] 不 spawn agent。Parent 直接執行：

對每個 module_<N>_<slug>，從 `vote_tally.json` 的 `top` 抽 `TOP_K` 個 candidate，組 `<paper_dir>/detail/module_<N>_<slug>/canonical/module.json`：

```json
{
  "schema_version": "detail_module_final.v1",
  "items": [
    {
      "source_detail_id": "detail_XX",
      "rank": 1,
      "vote_total": <int>,
      "main_line": "<從 thinking_process 抽 step=1 tag=主線 卡片的 content>",
      "refined_final_output": ["第一段...", "..."],
      "baseline_known_terms": ["..."]
    },
    ...
  ]
}
```

抽取邏輯：
1. 對 `i in 0..TOP_K-1`，target = `top[i]`：
   - 讀 `canonical/candidate/<target>.json`。
   - `main_line`：找 `items[0].thinking_process` 中第一筆 `step == "1"` 且 `tag == "主線"` 的卡片，取其 `content`。
   - `refined_final_output`：把 `items[0].refined_final_output` 中每個物件的 `content` 抽出組陣列。
   - `baseline_known_terms`：直接複製 `items[0].baseline_known_terms` 整個陣列（worker 已產出此欄位，不重新計算）。
   - `vote_total`：從 `vote_tally.totals` 查 `item_id == target` 的 `votes`。
   - `rank = i + 1`。
2. 依 `rank` 升序組 `items`。

### Step 5：Top-level 聚合（detail.json）

[mechanical] 不 spawn agent。Parent 直接執行。

組合 `<paper_dir>/detail/canonical/detail.json`：

```json
{
  "schema_version": "detail_final.v1",
  "modules": [
    {
      "module_id": "module_<N>_<slug>",
      "thesis": "<detail_plan.md 表格欄一句話 thesis>",
      "items": [
        // TOP_K 個 item，shape 與 module_<N>_<slug>/canonical/module.json 的 items 完全相同：
        // { source_detail_id, rank, vote_total, main_line, refined_final_output, baseline_known_terms }
      ]
    }
    // ... MODULE_COUNT 個 module
  ]
}
```

抽取邏輯：
1. 依 `N = 1..MODULE_COUNT` 順序，對每個模塊：
   - `module_id`：取 `module_<N>_<slug>`，slug 從 detail_plan.md 表格欄。
   - `thesis`：從 detail_plan.md 表格欄抽（1 句）。
   - `items`：直接複製 `<paper_dir>/detail/module_<N>_<slug>/canonical/module.json` 的 `items` 陣列（已 top-K、已排序，原樣搬入）。
2. 寫入 `<paper_dir>/detail/canonical/detail.json`。

**Sanity check**：
- `modules` 長度 = `MODULE_COUNT`。
- 每個 module 的 `items` 長度 = `TOP_K`。
- 每個 module 的 `thesis` 是 1 句（含 0-1 個句號）。
- 所有 `module_id` 全域唯一。

### Step 6：Repair（可選，預設不跑）

本規範預設只跑 Step 1–5。若某 module 的 top-K 候選 reviewer findings 集中、修補確有價值，可額外 [spawn agent] `TOP_K` 個 `summary_repair`（沿用 summary lane 的 repair 約定），`target_detail_id` = `vote_tally.top[i]`，`output_root` = `<paper_dir>/detail/module_<N>_<slug>/worker/round_01/<target>`。Repair 完成後覆寫 `canonical/candidate/<target>.json`，重跑 Step 4 per-module 與 Step 5 top-level 聚合。

## 不在本規範範圍內

- Worker / Reviewer 的 schema、HTML 結構、詞彙精修協議等沿用 summary lane，本文件不重複。
- Layer-1 summary lane 本身的執行見 summary lane 相關指引。

## 驗證

完整跑完後 sanity check：

1. **目錄完整性**：每個 `<paper_dir>/detail/module_<N>_<slug>/canonical/` 應有：
   - `candidate/`（含 `WORKER_COUNT` 份 `detail_XX.json`）
   - `voting/`（含 `REVIEWER_COUNT_PER_MODULE` 份 `review_X.json`）
   - `vote_tally.json`
   - `module.json`（`items` 長度 = `TOP_K`，每個 item 含 `baseline_known_terms`）
   並且 `<paper_dir>/detail/shuffles.json` 存在，覆蓋全部 `MODULE_COUNT × REVIEWER_COUNT_PER_MODULE` 組合。

2. **票數一致性**：每個 module 的 `vote_tally.json` 中 `Σ totals[*].votes = REVIEWER_COUNT_PER_MODULE × VOTES_PER_BALLOT`。

3. **Thesis 完整性**：spot-check 任意 worker 的 assignment 應該含 `thesis` 欄位，且字字相同於 `detail_plan.md` 該模塊的表格欄 thesis。

4. **Top-level 聚合完整性**：`<paper_dir>/detail/canonical/detail.json` 存在；`modules` 長度 = `MODULE_COUNT`；每個 module 的 `items` 與對應 `module_<N>_<slug>/canonical/module.json` 的 `items` 完全相同。
