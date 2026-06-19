# Method Pipeline

## 目標

這是一份給 Method Lane Orchestrator 看的指引。

把 `method_scanner.md` 產出的方法論與工具箱藍圖，逐一展開成「迷你 summary pipeline」，產出每個技術模塊的最終白話解析與工具清單。

- **輸入**：
  - `<paper_dir>/reassembly/canonical/paper.html`（論文原文）
  - `<paper_dir>/method/methodology_and_toolchain.md`（規劃階段輸出：各技術模塊總覽）
  - `<paper_dir>/summary/canonical/summary.json` 中指定一份 baseline summary（作為讀者已知共同語言）
- **輸出**：
  - N 份 per-module `<paper_dir>/method/module_<N>_<slug>/canonical/module.json`（每份含 top-K 解析與工具清單）
  - 1 份 top-level `<paper_dir>/method/canonical/method.json`（聚合全 N 個模塊，代表整篇論文 Method 總驗收）

## 檔案生命週期與意涵 (File Lifecycle)

為避免混淆，以下是 Method Pipeline 中各個 JSON 檔案的演進與其意涵：
1. **`output.json` (寫手草稿)**：由每個 `method_worker` 獨立產生，存放在自己的工作區 (如 `worker/batch_01/round_00/worker_01/output.json`)。
2. **`method_XX.json` (候選名單)**：Orchestrator 收集所有草稿後，將各模塊獨立切開，集中放置於各模塊下的 `canonical/candidate/` 並統一定名，供 Reviewer 評審。
3. **`module.json` (單一模塊得獎榜單)**：Reviewer 投票後，Orchestrator 將該模塊 Top-K 的 `method_XX.json` 抽出聚合，成為代表**「該模塊最終成果」**的檔案。
4. **`method.json` (全篇模塊大集結)**：最後，Orchestrator 將所有模塊的 `module.json` 統整，產出代表整篇論文 Method 的最終檔案。

## 參數

| 變數 | 預設 | 說明 |
|---|---|---|
| `MODULE_COUNT` | - | 由 `methodology_and_toolchain.md` 解析出的子項總數 |
| `WORKER_COUNT` | 2 | 每個 batch 啟動的 worker 總數 |
| `MODULES_PER_BATCH` | 6 | 每個 worker 一次最多處理的模塊數量限制 |
| `REVIEWER_COUNT_PER_MODULE` | 1 | 每個模塊啟動的 reviewer 數 |
| `VOTES_PER_BALLOT` | 1 | 每位 reviewer 在單一模塊中的總票數 |
| `TOP_K` | 1 | 每個模塊保留的最終解析數 |
| `BASELINE_SUMMARY_INDEX` | 0 | `summary/canonical/summary.json` 中對應的 baseline 摘要索引 |

## 路徑慣例

`paper_dir = workspace/<paper_slug>`。Module 路徑慣例：`<paper_dir>/method/module_<N>_<slug>/`，N = 1..MODULE_COUNT。

## 使用的 subagent prompts

| 角色 | 沿用檔案 |
|---|---|
| Scanner | `subagent_prompts/method_scanner.md` |
| Worker | `subagent_prompts/method_worker.md` |
| Reviewer | `subagent_prompts/method_reviewer.md` |

Schema：`method_multi.v1`（worker output）、`method_review.v1`（reviewer output）、`method_module_final.v1`（module.json）、`method_final.v1`（method.json）。

## 目錄結構

```text
<paper_dir>/
  method/
    methodology_and_toolchain.md        # 規劃階段輸出（input）
    shuffles.json                       # Parent 產生：per-module per-reviewer 候選洗牌順序
    worker/
      batch_01/
        round_00/                       
          worker_01/
            output.json
            output.html
          ...
      batch_02/ ...
    module_<N>_<slug>/
      reviewer/
        round_00/                       # Per-module reviewer
          reviewer_A/
            visual_review.json
            review_report.md
          ...
      canonical/                        # live state
        candidate/                      # Worker 拆解後的結果
          method_01.json
          ...
        voting/                         # Reviewer 投票結果
          review_A.json
          ...
        vote_tally.json                 # Parent 聚合票數
        module.json                     # Final delivery
```

## 流程

Parent 只做兩種動作：**[spawn agent]** 啟動 subagent，以及 **[mechanical]** 搬檔或組裝 JSON。所有內容判斷由 subagent 執行。

### Step 0：Scanner (Planning)

[spawn agent] 啟動 1 個 `method_scanner`：
讀取論文原文，產出 `<paper_dir>/method/methodology_and_toolchain.md`。

[mechanical] 讀 `methodology_and_toolchain.md` 的第 2 節與第 3 節，解析出所有子項（例如 2-A, 2-B, 3-A）。每個子項成為一個模塊：
- `subitem_id`（如 2-A）
- `subitem_heading`（如 Inverse PCR 定位法）
- `short_label`（2-4 字的核心關鍵詞，**上限 5 字**；用於 reader-panel 右上角 toggle widget。例：subitem_heading「Pulse Duplicator 水力性能測試」→ short_label「水力性能」）
- `thesis`（取自該項目的「目標」描述，一句話）
- `slug`（從 heading 轉成 kebab-case-ascii）

總模塊數為 `MODULE_COUNT`。

### Step 1：Work (Batched)

因為一個 worker 處理過多模塊會導致品質下降或超過 token 限制，所以將 `MODULE_COUNT` 個模塊以 `MODULES_PER_BATCH` (= 6) 為單位切分成多個 Batch。

對於每個 Batch：
[spawn agent] 啟動 `WORKER_COUNT` 個 `method_worker`，每個 worker 處理該 Batch 分配到的模塊：

```text
Subagent prompt = <method_worker.md 全文>

---
Assignment
paper_dir: <paper_dir>
paper_file: <paper_dir>/reassembly/canonical/paper.html
baseline_summary_path: <paper_dir>/summary/canonical/summary.json
baseline_summary_index: <BASELINE_SUMMARY_INDEX>
modules:
  - module_id: module_<N>_<slug>
    subitem_id: <2-A>
    subitem_heading: <Heading>
    short_label: <2-4 字關鍵詞>
    thesis: <目標>
  ... (該 Batch 的所有模塊，最多 6 個)
mode: initial
worker_id: worker_<XX>   # XX = 01..WORKER_COUNT
output_root: <paper_dir>/method/worker/batch_<Y>/round_00/worker_<XX>
```

[mechanical] **Promote**：
對所有 Batch 收集 `output.json`：
1. 將每個 worker 的 `output.json` 中 `modules` 陣列「拆散」到各個模塊目錄下。
2. 抽出每個模塊的內容，包裝成：`{ "schema_version": "method_multi.v1", "worker_id": "worker_<XX>", "items": [ <抽出元素> ] }`。
3. 把抽出元素中的 `item_id` 改為 `method_<XX>`。
4. 寫入對應的 `<paper_dir>/method/module_<N>_<slug>/canonical/candidate/method_<XX>.json`。
5. HTML 留在 worker folder，不進 canonical。

### Step 1.5：產生 Shuffle 計畫

[mechanical] Parent 產生 `<paper_dir>/method/shuffles.json`，對每個 `(module_id, reviewer_id)` 組合獨立洗牌，消除 Position Bias，格式與 Detail Lane 相同。

### Step 2：Review（per module）

每個模塊獨立 [spawn agent] `REVIEWER_COUNT_PER_MODULE` 個 `method_reviewer`：

```text
Subagent prompt = <method_reviewer.md 全文>

---
Assignment
paper_dir: <paper_dir>
module_id: module_<N>_<slug>
shuffles_path: <paper_dir>/method/shuffles.json
review_round: round_00
reviewer_id: reviewer_<X>
output_root: <paper_dir>/method/module_<N>_<slug>/reviewer/round_00/reviewer_<X>
```

[mechanical] **Promote**：
把每個 reviewer 的 `visual_review.json` 複製到 `<paper_dir>/method/module_<N>_<slug>/canonical/voting/review_<X>.json`。

### Step 3：Vote Tally（per module）

[mechanical] 對每個 module：
1. 讀 `canonical/voting/review_*.json` 的 `global_evaluation.votes`。
2. 加總每個 `method_XX` 票數，依降序排序取 top-`TOP_K`。
3. 寫 `canonical/vote_tally.json`。

### Step 4：Final Extraction（per module）

[mechanical] 不 spawn agent。Parent 對每個 module：
從 `vote_tally.json` 取前 `TOP_K` 名，組 `<paper_dir>/method/module_<N>_<slug>/canonical/module.json`：

```json
{
  "schema_version": "method_module_final.v1",
  "items": [
    {
      "source_method_id": "method_XX",
      "rank": 1,
      "vote_total": <int>,
      "outline": "<從 subitem_heading 取得，移除 #### A. 等前綴與多餘標點>",
      "main_line": "<從 thinking_process 抽 step=1 tag=主線 的 content>",
      "refined_final_output": ["第一段...", "..."],
      "toolchain_terms": [{"term": "...", "description": "..."}],
      "context_and_significance": "...",
      "baseline_known_terms": ["..."]
    }
  ]
}
```

### Step 4.5：Markdown 產出（per module）

[mechanical] 不 spawn agent。Parent 對每個 module：
取 `vote_tally.json` 中的**第 1 名**（Voting 勝利者）資料，組裝成獨立的 Markdown 檔案，檔名為 `<slug>.md`（取自 `module_<N>_<slug>` 中的 slug）。
必須將此檔案存放到以下兩個路徑：
1. `<paper_dir>/method/canonical/<slug>.md`
2. `<paper_dir>/final/method/<slug>.md`

Markdown 內容結構必須如下：

```markdown
# [outline]

1. 引用自哪篇 paper: [paper_slug]
2. Outline (任務主線): [outline]
3. Method: 
   [refined_final_output 的所有段落合併，以換行分隔]
4. 工具與材料: 
   [toolchain_terms 以列點呈現，例如：- **Lentivirus**: 一種能...]
5. 與此篇文章的關係: 
   [context_and_significance]
```

### Step 5：Top-level 聚合（method.json）

[mechanical] 不 spawn agent。組合 `<paper_dir>/method/canonical/method.json`：

```json
{
  "schema_version": "method_final.v1",
  "modules": [
    {
      "module_id": "module_<N>_<slug>",
      "subitem_id": "2-A",
      "subitem_heading": "Inverse PCR 定位法",
      "short_label": "插入定位",
      "thesis": "在細胞基因組中隨機且單一地插入帶有條碼的插槽。",
      "items": [
        // 該模塊的 TOP_K 個結果
      ]
    }
  ]
}
```

*(註：本 pipeline 依需求暫不設立 Repair 階段。)*
