# Phase 2 Pipeline: Summary, Method, Mapping

## 目標

這是一份給 pipeline orchestrator 看的指引，定義了 Phase 2（Summary, Method, Mapping）三條 Lane 的運行架構。
- **Summary Lane**：將科學論文轉譯為外行人能懂的結構化摘要，並透過多 worker 與 reviewer 機制篩選出最高品質結果。
- **Method Lane**：把方法論與工具箱藍圖，逐一展開成「迷你 summary pipeline」，產出每個技術模塊的最終白話解析與工具清單。
- **Mapping Lane**：把指定摘要的每個 phrase，對應到原文 HTML 裡的英文片段，產出多份結構化 mapping JSON 並注入最終 HTML。

這份文件是 100% 獨立的架構指南，包含所有的底層邏輯與共通合約。

## 參數與變數

以下是全域參數，要調整數量，只改本表的預設值即可。下方流程文以變數名稱引用，請勿在流程文中寫死數字。

| 變數 | 預設 | 說明 |
|---|---|---|
| `{{SUMMARY_WORKER_COUNT}}` | 12 | 啟動的 summary_worker 數量。 |
| `{{SUMMARY_REVIEWER_COUNT}}` | 5 | 啟動的 summary_reviewer 數量。 |
| `{{SUMMARY_VOTES_PER_BALLOT}}` | 7 | 每位 summary reviewer 一張選票的總票數。 |
| `{{SUMMARY_TOP_K}}` | 3 | Summary 選票候選人數 = repair 數 = final 收件數。 |
| `{{METHOD_MODULE_COUNT}}` | - | 由 `methodology_and_toolchain.md` 解析出的子項總數。 |
| `{{METHOD_WORKER_COUNT}}` | 2 | Method 每個 batch 啟動的 worker 總數。 |
| `{{METHOD_MODULES_PER_BATCH}}` | 6 | Method 每個 worker 一次最多處理的模塊數量限制。 |
| `{{METHOD_REVIEWER_COUNT}}` | 1 | Method 每個模塊啟動的 reviewer 數。 |
| `{{METHOD_VOTES_PER_BALLOT}}`| 1 | 每位 method reviewer 在單一模塊中的總票數。 |
| `{{METHOD_TOP_K}}` | 1 | Method 每個模塊保留的最終解析數。 |
| `{{BASELINE_SUMMARY_INDEX}}` | 0 | `summary/canonical/summary.json` 中對應的 baseline 摘要索引。 |
| `{{PAPER_DIR}}` | - | paper 目錄（`<paper_dir>`），由使用者直接提供，例如 `workspace/<paper_slug>`。 |
| `{{PAPER_SLUG}}` | basename(`paper_dir`) | paper_dir 的最後一層名稱，用作目的端資料夾與部分檔名前綴。 |
| `{{SOURCE_KEYS}}` | 自動偵測 | Mapping lane 的識別碼列表，決定來源與輸出檔名（例：`l1`, `method_m1`, `method_m2`）。 |
| `{{GITHUB_IO_ROOT}}` | `/Users/wenj/Courses/wenjchao.github.io` | GitHub Pages repo 本地路徑。 |

## 共通機制與 Contract

### 1. Parent 與 Subagent 權責界線

- Parent 只做兩種動作：
  - **`[spawn agent]`**：啟動 subagent（將所有內容判斷、撰寫與品質審查委派給 subagent）。
  - **`[mechanical]`**：搬檔或組裝/解析 JSON（純機械操作，不需判斷）。
- 所有 worker、reviewer 都要啟動獨立 subagent。不得用 parent 的工作取代 subagent。Parent 不改寫文字、不判斷品質。
- Subagent prompt 必須使用指定的 prompt 檔案全文，不得摘要、改寫、截斷。Parent 唯一可以做的修改是在末尾附加 assignment block。
- Agent 啟動失敗時，先修正 prompt/tool/context 後重試。若持續失敗則回報 blocked。

### 2. Candidate 與洗牌 (Shuffle) 機制 (Evaluation Pipelines)

Summary 與 Method 都是多重生成與投票評選系統，需將草稿轉換為匿名候選名單，並消除 LLM 評審的 Position Bias。
- **Candidate Promote**：Worker 獨立產出的 `output.json` 必須由 Parent 取出，將內部的 `item_id` 改名為目標 ID（如 `summary_XX` 或 `method_XX`），並放入 `canonical/candidate/` 目錄。
- **Shuffle**：在傳遞給 Reviewer 讀取前，Parent 必須對所有的候選名單順序進行**獨立的隨機洗牌 (Shuffle)**，產生洗牌對應關係（例如 `shuffles.json`）。每位 Reviewer 看到的順序都必須不同。

### 3. 投票與計票 (Voting & Tally) 機制 (Evaluation Pipelines)

- Reviewer 讀取洗牌後的所有候選 JSON，進行淘汰與比對，最後產出 `visual_review.json`（包含 `global_evaluation.votes`）與一份人類可讀的 `review_report.md`。
- **Aggregate Votes (機械計票)**：
  1. 讀取所有 reviewer 的 `visual_review.json` 中的 `votes`。
  2. 對每個候選項目（如 `summary_XX`）加總所有得票（未被投票者視為 0 票）。
  3. 依總票數降序排序，取總票數最多的前 `{{TOP_K}}` 名（票數相同時並列）。
  4. 寫入完整票數表 `canonical/vote_tally.json`。

### 4. Markdown 最終交付 Contract

Pipeline 的最終目的包含產出供人類閱讀的 Markdown 並發布至 `final/` 目錄：
- 從 `canonical/vote_tally.json` 取出排名第一（Rank 1）的資料。
- Parent 直接（Inline LLM Task 或腳本）將其組裝為特定格式的 Markdown 檔案。
- 將生成的 Markdown 無損複製至 `<paper_dir>/final/` 對應路徑，作為最終交付。

### 5. Gate 與 Repair 機制 (比對修復系統)

如 Mapping 等流程需要精確比對，採用 Gate 與 Repair 迴圈確保品質：
- **Gate 審查**：Parent 讀取 canonical 中的 review JSON：
  - 若所有項目的 `findings` 皆為空陣列 -> 品質過關，Lane close 或進入合併階段。
  - 若出現 `severity: "required"` 的 findings -> 該項目進入 Repair。
  - 若達到 Repair round limit（預設 4 輪）-> 回報 Blocked。
  - Parent 不得 override reviewer，有 fail 項目時不得靜默 close。
- **Repair 修復**：
  - 針對有 `required` findings 的項目啟動 Repair Worker，讀取當前成果與 review 意見進行局部修正。
  - Repair Promote 後，Re-review 只針對「被修復的項目」進行審查，已通過的項目不重新審查。
  - 不覆寫舊 round 的 work folder；`canonical/` 視為 Live State，直接覆寫更新檔。

## 全域目錄結構與 Prompts 總表

### Subagent Prompts 總表

| 角色 | Lane | 沿用檔案 | 職責簡述 |
|---|---|---|---|
| Worker | Summary | `subagent_prompts/summary_worker.md` | 將科學論文轉譯為外行人能懂的結構化摘要。 |
| Reviewer | Summary | `subagent_prompts/summary_reviewer.md` | 語感淘汰、比對並投票，給出評審結果。 |
| Repair | Summary | `subagent_prompts/summary_repair.md` | 對票數前 K 名的摘要進行最小修補。 |
| Scanner | Method | `subagent_prompts/method_scanner.md` | 從原文產出方法論與工具箱藍圖。 |
| Worker | Method | `subagent_prompts/method_worker.md` | 展開各技術模塊的白話解析與工具清單。 |
| Reviewer | Method | `subagent_prompts/method_reviewer.md` | 針對單一模塊的候選項目進行審查與投票。 |
| Worker | Mapping | `subagent_prompts/mapping_worker.md` | 把 phrase 對應到原文 HTML 的英文片段 (含 repair)。 |
| Reviewer | Mapping | `subagent_prompts/mapping_reviewer.md` | 審查 mapping 是否違反擷取或 overlap 等規則。 |
| Merger | Mapping | `scripts/mapping_merger_script.py` | (Script) Deterministic 將 mapping 套用到 paper.html。 |

*(註：路徑慣例中，原始論文一律讀取 `<paper_dir>/reassembly/canonical/paper.html`)*

### 全域目錄結構大樹狀圖

這是一份合併後的典型檔案分布，展示了 `summary/`, `method/`, `mapping/` 三條 Lane 以及最終 `final/` 目錄之間的關係。

```text
<paper_dir>/
  reassembly/
    canonical/
      paper.html                     # 所有 Lane 共用的原始輸入來源
  summary/
    worker/
      round_00/
        worker_01/
          output.json                # Worker 草稿
          output.html
      round_01/
        summary_XX/                  # Repair worker (只跑 top-K)
    reviewer/
      round_00/
        reviewer_A/
          visual_review.json
          review_report.md
    canonical/                       # Summary Live State
      candidate/
        summary_01.json              # 重新命名的候選項目
      voting/
        review_A.json
      vote_tally.json                # Parent 聚合票數
      summary.json                   # 抽取出的 Final 摘要列表
      <paper_id>_summary.md

  method/
    methodology_and_toolchain.md     # Scanner 規劃的各模塊藍圖
    shuffles.json                    # Parent 產生的洗牌順序
    worker/
      batch_01/
        round_00/
          worker_01/
            output.json
    module_<N>_<slug>/               # (每個模塊都有自己的 canonical 與 reviewer)
      reviewer/
        round_00/
          reviewer_A/
      canonical/
        candidate/
          method_01.json
        voting/
          review_A.json
        vote_tally.json
        module.json                  # 該模塊 Final 摘要
    canonical/
      method.json                    # 聚合全 N 個模塊的大清單
      <slug>.md

  mapping/
    worker/
      round_00/
        l1/
          output.json
        method_m1/
      round_01/                      # Repair
    reviewer/
      round_00/
        l1/
          visual_review.json
    canonical/
      mapping.l1.json
      visual_review.l1.json
      mapping.method_m1.json
      paper.html                     # 經過 Merger 腳本處理的最終 HTML

  final/                             # Pipeline 最終交付同捆包
    <paper_id>_summary.md            # 從 summary/ 複製而來
    method/
      <slug>.md                      # 從各 method module 複製而來
    <paper_id>.html                  # 從 mapping/ 複製而來，含有完整螢光筆標註

wenjchao.github.io/                  # (Moving Lane 目的地)
  workspace/
    <paper_slug>/                    # 對應並同步自 final/ 的所有內容
      <paper_id>_summary.md
      method/
      <paper_id>.html
```

---

## Summary Lane 專屬流程

1. **Work (Summary Generation)**
   - 平行啟動 `{{SUMMARY_WORKER_COUNT}}` 個 `summary_worker` (`worker_01` 到 `worker_N`)。
   - `[mechanical]` 收集 `output.json`，改 `item_id` 為 `summary_01` 至 `summary_N`，放入 `canonical/candidate/`。
2. **Review (Summary Evaluation)**
   - `[mechanical]` 對 `canonical/candidate/` 執行獨立的隨機洗牌。
   - 平行啟動 `{{SUMMARY_REVIEWER_COUNT}}` 個 `summary_reviewer`，各別讀取洗牌後的 JSON。
   - `[mechanical]` 複製 `visual_review.json` 到 `canonical/voting/`。
   - `[mechanical]` 執行計票邏輯，寫入 `vote_tally.json`。
3. **Repair (Top-K Refinement)**
   - 針對總票數前 `{{SUMMARY_TOP_K}}` 名，平行啟動對應數量的 `summary_repair` 進行最小修補（不改動 `thinking_process` 等原始資訊，只改 `refined_final_output`）。
   - 修補後的檔案直接覆寫回 `canonical/candidate/<target>.json`。
4. **Final Extraction**
   - 從修補後的 `candidate` 目錄中，依照 `vote_tally.json` 的前 `{{SUMMARY_TOP_K}}` 名順序，抽取出 `main_line`、`refined_final_output` 等必要欄位，組裝成 schema 為 `summary_final.v1` 的單一精簡檔案 `canonical/summary.json`。
5. **Markdown Generation**
   - 讀取 `summary.json` 第一名（Rank 1）資料，由 Parent（Inline LLM Task）構思短標題（上限 15 字）、取出作者資訊，並組裝為 Markdown。
   - 寫入 `canonical/<paper_id>_summary.md` 並無損複製至 `final/<paper_id>_summary.md`。

---

## Method Lane 專屬流程

1. **Scanner (Planning)**
   - 啟動 1 個 `method_scanner`，產出 `methodology_and_toolchain.md`。
   - `[mechanical]` 解析該檔案第 2 節與第 3 節，找出所有模塊（`{{METHOD_MODULE_COUNT}}` 個），提取 `subitem_id`、`short_label`、`slug` 等。
2. **Work (Batched)**
   - 以 `{{METHOD_MODULES_PER_BATCH}}` 為單位切分為多個 Batch。
   - 對每個 Batch，啟動 `{{METHOD_WORKER_COUNT}}` 個 `method_worker`，每個 Worker 一次處理被分配到的多個模塊。
   - `[mechanical]` 收集 `output.json` 後，將內部的 `modules` 陣列拆散。把對應的內容包裝成獨立的 `method_XX.json` 放入各個模塊的 `module_<N>_<slug>/canonical/candidate/` 中。
3. **Review & Vote Tally (per module)**
   - `[mechanical]` 產生 `shuffles.json` 消除位置偏見。
   - 對每個模塊，平行啟動 `{{METHOD_REVIEWER_COUNT}}` 個 `method_reviewer`。
   - 收集 `visual_review.json` 至對應模塊的 `canonical/voting/`，執行計票並產生該模塊的 `vote_tally.json`。
4. **Final Extraction & Markdown (per module)**
   - 從該模塊的 `vote_tally.json` 取前 `{{METHOD_TOP_K}}` 名，組裝成 `canonical/module.json`。
   - 將第 1 名資料組裝成 Markdown (`<slug>.md`)，寫入 `method/canonical/<slug>.md` 並複製至 `final/method/<slug>.md`。
5. **Top-level 聚合**
   - `[mechanical]` 組合所有模塊的 `module.json`，產出代表整篇論文 Method 總驗收的 `<paper_dir>/method/canonical/method.json`。
   *(註：本 pipeline 依需求暫不設立 Method Repair 階段。)*

---

## Mapping Lane (v2) 專屬流程

1. **自動偵測目標**
   - 若未提供 `{{SOURCE_KEYS}}`，Parent 自動掃描 `summary.json`（對應 key: `l1`）與 `method.json`（對應 keys: `method_m1` 到 `method_mN`，依據 `modules[]` 數量）。
2. **Work**
   - 針對所有 source_key，平行啟動 `mapping_worker`。
   - Worker 讀取目標摘要的 phrase 並對應原文 HTML，寫出 `output.json`。
   - `[mechanical]` 改名並放入 `canonical/mapping.<source_key>.json`。
3. **Review & Gate**
   - 針對所有 source_key，平行啟動 `mapping_reviewer` 找尋違反規則或重疊的 defect，產出 `visual_review.json`。
   - 執行 **Gate 機制**：有 `required` findings 進入下一步 Repair，全空則直接進入 Merge。
4. **Repair**
   - 針對有問題的 `source_key` 啟動 `mapping_worker`（repair mode），修正後覆蓋 `canonical/` 原檔。
   - Re-review 僅對被修復的 `source_key` 進行重新審查。
5. **Merge (Deterministic Script)**
   - `[mechanical]` 所有 mapping 皆通過 Gate 後，直接執行 Python 腳本：
     ```bash
     python3 agents/scripts/mapping_merger_script.py <paper_dir>
     ```
   - 該腳本負責讀取所有通過審查的 `mapping.*.json`，注入 HTML 結構、Reader Panel、Margin Rail 等，最終寫到 `mapping/canonical/paper.html`。
   - stdout 必須印出 `Step 9 self-check: 11/11 PASS` 否則回報錯誤。
6. **Finalize**
   - 將 `mapping/canonical/paper.html` 無損複製覆寫到 `final/<paper_id>.html`，完成含有完整 mapping 標註的論文交付。

---

## Moving Lane (Publish) 專屬流程

這是 mapping pipeline 之後、發布前的最後一步（mechanical），將已 finalize 的 paper 複製到個人 GitHub Pages 倉庫使其成為可訪問的網頁。

1. **前置驗證**
   - 確認 `<paper_dir>/final/` 存在。
   - 確認 `<paper_dir>/final/<paper_slug>.html` 存在（若無代表 mapping pipeline 未成功或 merger 發生錯誤）。
   - 確認目的端 root `{{GITHUB_IO_ROOT}}/workspace/` 存在（如不存在則 abort 並要求 user 確認路徑）。
2. **同步 (Rsync)**
   - `[mechanical]` 對每篇 paper 跑一次 `rsync`：
     ```bash
     mkdir -p {{GITHUB_IO_ROOT}}/workspace/{{PAPER_SLUG}}
     rsync -a <paper_dir>/final/ {{GITHUB_IO_ROOT}}/workspace/{{PAPER_SLUG}}/
     ```
   - **注意**：末尾 `/` 在 `rsync` 是必要的。必須加上 `-a` 以保留權限等屬性。
   - **禁止**加 `--delete`，以免誤刪目的端 user 自行添加的舊檔備份。同名檔案會預期地被 `final/` 覆蓋。
3. **批次處理 (若需要)**
   - 一次處理多篇 paper 時，直接 loop 所有 `{{PAPER_SLUG}}` 執行上述邏輯。
4. **交還給 User**
   - 複製完成後，**不要**自動 `git add / commit / push`，因為部署是 user 的最終決策。
   - 僅回報：各 paper 複製後的 item count 與 total size、哪些是新增/覆蓋、以及任何 `rsync` 警告。
   - （SKILL 不負責 site-level 的 `index.html` 或 theme，只負責將內容就緒）。
