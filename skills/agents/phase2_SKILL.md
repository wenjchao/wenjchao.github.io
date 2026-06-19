# Phase 2 Pipeline: Summary, Method, Mapping

## 目標

這是一份給 pipeline orchestrator 看的指引，定義了 Phase 2（Summary, Method, Mapping, Moving）四條 Lane 的運行架構。預設下，Phase 2 會按順序跑完全部四條 Lane；user 若想中止在某條 Lane，需明確指示。
- **Summary Lane**：將科學論文轉譯為外行人能懂的結構化摘要，並透過多 worker 與 reviewer 機制篩選出最高品質結果。
- **Method Lane**：把方法論與工具箱藍圖，逐一展開成「迷你 summary pipeline」，產出每個技術模塊的最終白話解析與工具清單。
- **Mapping Lane**：把指定摘要的每個 phrase，對應到原文 HTML 裡的英文片段，產出多份結構化 mapping JSON 並注入最終 HTML。
- **Moving Lane**（預設開啟）：把 `final/` 同步到本機 GitHub Pages repo，並自動 `git add` + `git commit`（不 push）。

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
- **Assignment block 完整範本**：本檔案各 Lane 流程只給高層步驟，每個 spawn 步驟的 assignment block 完整欄位範本見 `agents/individual_orchestrator/<lane>_SKILL.md` 對應 step。例如 mapping worker 的 `summary_path` / `mode` / `module_index` 欄位範本見 `mapping_SKILL.md` Step 1。每次 spawn agent 之前**必須**對照 individual orchestrator 的範本組 assignment，phase2 沒寫的欄位不代表可以省略。

### 2. Candidate 與洗牌 (Shuffle) 機制 (Evaluation Pipelines)

Summary 與 Method 都是多重生成與投票評選系統，需將草稿轉換為匿名候選名單，並消除 LLM 評審的 Position Bias。
- **Candidate Promote**：Worker 獨立產出的 `output.json` 必須由 Parent 取出，將內部的 `item_id` 改名為目標 ID（如 `summary_XX` 或 `method_XX`），並放入 `canonical/candidate/` 目錄。
- **Shuffle**：在傳遞給 Reviewer 讀取前，Parent 必須對所有的候選名單順序進行**獨立的隨機洗牌 (Shuffle)**，產生洗牌對應關係（例如 `shuffles.json`）。每位 Reviewer 看到的順序都必須不同。
- **Round 命名約定**：
  - `round_00` = initial worker assembly + 第一次 review。
  - `round_01` = repair only（Summary repair 或 Mapping repair）；**Summary repair 沒有對應的 `reviewer/round_01/`**，因為這一輪不再做 review；Mapping 才會有 `reviewer/round_01/`（只對被修復的 key 重審）。
  - 不覆寫舊 round 的 work folder；`canonical/` 視為 Live State，新 round 的 promote 會覆寫對應檔案。
- **canonical/ 內容範圍**：只放結構化的 JSON（candidate、voting、vote_tally、最終匯總）。**HTML 與 `review_report.md` 等人類視角衍生視圖不進 canonical**，留在對應的 work folder（`worker/round_XX/...`、`reviewer/round_XX/...`）。

### 3. 投票與計票 (Voting & Tally) 機制 (Evaluation Pipelines)

- Reviewer 讀取洗牌後的所有候選 JSON，進行淘汰與比對，最後產出 `visual_review.json`（包含 `global_evaluation.votes`）與一份人類可讀的 `review_report.md`。
- **Aggregate Votes (機械計票)**：
  1. 讀取所有 reviewer 的 `visual_review.json` 中的 `votes`。
  2. 對每個候選項目（如 `summary_XX`）加總所有得票（未被投票者視為 0 票）。
  3. 依總票數降序排序，取總票數最多的前 `{{TOP_K}}` 名（票數相同時並列）。
  4. 寫入完整票數表 `canonical/vote_tally.json`。
- **Sanity check**：所有候選的總票數和應等於 `REVIEWER_COUNT × VOTES_PER_BALLOT`。對不上代表有 reviewer 沒投足票數或寫錯欄位，應該回頭檢查 reviewer JSON 而不是繼續往下跑。

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

### 6. TOP_K 耦合

`{{SUMMARY_TOP_K}}` / `{{METHOD_TOP_K}}` 一處改動會同步影響多個下游步驟，改參數時必須一起檢查：
1. Reviewer Stage 1 淘汰後留下的「語感前 K 名」進入 Stage 2 與 Stage 3。
2. Reviewer Stage 3 投票：選票上恰好 K 名候選人，總票數 = `VOTES_PER_BALLOT`。
3. Parent 的 Repair 階段：對 vote_tally 前 K 名平行 spawn K 個 repair agent（Summary）。
4. Final Extraction：`canonical/summary.json` / `module.json` 的 `items` 長度 = K。

### 7. 檔案生命週期 (Evaluation Pipelines)

為避免混淆，以下是同一份內容沿 pipeline 演進的命名與意涵（以 Method 為例，Summary 同理）：
1. **`output.json`（寫手草稿）**：由每個 worker 獨立產生，存放在自己的工作區（如 `worker/batch_01/round_00/worker_01/output.json`）。
2. **`method_XX.json` / `summary_XX.json`（候選名單）**：Parent 收集所有草稿後，將內容拆開、改 `item_id`、集中放在 `canonical/candidate/`，供 Reviewer 評審。
3. **`module.json`（單模塊得獎榜單）/ `summary.json`（全文摘要榜單）**：Reviewer 投票後，Parent 把該模塊（或全文）的 Top-K `XX.json` 抽出聚合，成為代表「該模塊／該全文最終成果」的檔案。
4. **`method.json`（全篇模塊大集結）**：最後 Parent 將所有模塊的 `module.json` 統整成代表整篇論文 Method 的最終檔案。

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
| Merger Reviewer | Mapping | `subagent_prompts/mapping_merger_reviewer.md` | 對 merger 寫出的 paper.html 做外部審查；區分 paper.html 必修 `required` finding 與 merger script 的 `merger_bug`。 |
| Merger Repair | Mapping | `subagent_prompts/mapping_merger_repair.md` | 依 reviewer 的 `required` findings 直接 patch paper.html；不碰源檔，不碰 merger script。 |

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
   - 從修補後的 `candidate` 目錄中，依照 `vote_tally.json` 的前 `{{SUMMARY_TOP_K}}` 名順序抽取，組裝成 schema 為 `summary_final.v1` 的單一精簡檔案 `canonical/summary.json`。具體抽取規則：
     - `main_line`：從 `items[0].thinking_process` 找第一筆 `step == "1"` 且 `tag == "主線"` 的卡片，取其 `content`（純字串）。
     - `refined_final_output`：把 `items[0].refined_final_output` 中每段物件的 `content` 抽出，組成**純字串陣列**（**必須丟掉 `sources` 欄位**——下游 merger 與 markdown 都假設這是 string[]，留著 dict 會破壞渲染）。
     - `vote_total`：從 `vote_tally` 查該 `item_id` 的總票數。
     - `rank`：依 vote 排序產生（1-based）。
5. **Markdown Generation**
   - 讀取 `summary.json` 第一名（Rank 1）資料，由 Parent（Inline LLM Task）構思短標題、取出作者資訊，並組裝為 Markdown。
   - **短標題實質約束（不只是字數）**：
     - 上限 15 字，約 10–15 字為宜——流暢、好懂優先於簡短。
     - **必須點名研究對象的實質名詞**（如「DNA 開關」「染色質位置」），不能只用比喻包裝（如純隱喻「音量旋鈕」不行）。
     - **同時帶出核心結論或研究問題**，用白話動詞描述（如「只放大縮小、不挑」），避免「XX 的效應 / 機制」這類術語空殼。
     - **不能有事實錯誤**。例如原文為靜電力，不能為了好懂而改用「磁力」。
   - 寫入 `canonical/<paper_id>_summary.md`，然後 `[mechanical]` 無損複製到 `final/<paper_id>_summary.md`。

---

## Method Lane 專屬流程

1. **Scanner (Planning)**
   - 啟動 1 個 `method_scanner`，產出 `methodology_and_toolchain.md`。
   - `[mechanical]` 解析該檔案第 2 節與第 3 節，找出所有模塊（`{{METHOD_MODULE_COUNT}}` 個），對每個模塊提取下列欄位：
     - `subitem_id`：如 `2-A`、`3-B`。
     - `subitem_heading`：取該子項的標題文字。
     - `short_label`：**2–4 字的核心關鍵詞，上限 5 字**。用於 reader-panel 右上角顏色切換 chip 的標籤；太長會撐爆 UI，下游 merger 直接吃這個欄位。範例：subitem_heading「Pulse Duplicator 水力性能測試」→ short_label「水力性能」。
     - `thesis`：取該子項「目標：」line 的一句話。
     - `slug`：從 heading 轉成 kebab-case ASCII（用作目錄名 `module_<N>_<slug>` 與 markdown 檔名 `<slug>.md`）。
2. **Work (Batched)**
   - 以 `{{METHOD_MODULES_PER_BATCH}}` 為單位切分為多個 Batch。
   - 對每個 Batch，啟動 `{{METHOD_WORKER_COUNT}}` 個 `method_worker`，每個 Worker 一次處理被分配到的多個模塊。
   - `[mechanical]` 收集 `output.json` 後，將內部的 `modules` 陣列拆散。把對應的內容包裝成獨立的 `method_XX.json` 放入各個模塊的 `module_<N>_<slug>/canonical/candidate/` 中。
3. **Review & Vote Tally (per module)**
   - `[mechanical]` 產生 `shuffles.json` 消除位置偏見。
   - 對每個模塊，平行啟動 `{{METHOD_REVIEWER_COUNT}}` 個 `method_reviewer`。
   - 收集 `visual_review.json` 至對應模塊的 `canonical/voting/`，執行計票並產生該模塊的 `vote_tally.json`。
4. **Final Extraction & Markdown (per module)**
   - 從該模塊的 `vote_tally.json` 取前 `{{METHOD_TOP_K}}` 名，組裝成 `canonical/module.json`，schema 為 `method_module_final.v1`：
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
   - 將第 1 名資料組裝成 Markdown (`<slug>.md`)，寫入 `method/canonical/<slug>.md` 並複製至 `final/method/<slug>.md`。Markdown 結構：
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
5. **Top-level 聚合**
   - `[mechanical]` 組合所有模塊的 `module.json`，產出代表整篇論文 Method 總驗收的 `<paper_dir>/method/canonical/method.json`，schema 為 `method_final.v1`：
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
             // 該模塊的 TOP_K 個結果（schema 同 module.json 的 items）
           ]
         }
       ]
     }
     ```
   - **Schema 名稱速查**：`method_multi.v1`（worker output）、`method_review.v1`（reviewer output）、`method_module_final.v1`（單模塊 module.json）、`method_final.v1`（聚合 method.json）。
   *(註：本 pipeline 依需求暫不設立 Method Repair 階段。)*

---

## Mapping Lane (v2) 專屬流程

1. **自動偵測目標**
   - 若未提供 `{{SOURCE_KEYS}}`，Parent 自動掃描 `summary.json`（對應 key: `l1`）與 `method.json`（對應 keys: `method_m1` 到 `method_mN`，依據 `modules[]` 數量）。
   - **source_key → assignment 對應表**（worker 與 reviewer 都要照這張表組 assignment）：

     | `source_key` | `summary_path` | `module_index` | `color_key` |
     |---|---|---|---|
     | `l1` | `<paper_dir>/summary/canonical/summary.json` | （不需要） | `summary` |
     | `method_mN` | `<paper_dir>/method/canonical/method.json` | `N − 1`（0-based） | `mN` |
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
   - 腳本內含 11 條 self-check（同 `mapping_merger.md` Step 9）。**self-check 不是 gate**：不論 11/11 PASS 或部分 fail，Merger 都會寫出 paper.html，由下一步的 Merger Reviewer 做外部審查。Parent **必須抓 stdout** 傳給 reviewer。
   - **雙來源規則**：merger 的 spec 在 `subagent_prompts/mapping_merger.md`（Step 1-9 規範），實作在 `agents/scripts/mapping_merger_script.py`。未來要修補 merger 規則必須**同步改兩處**，否則 spec 與實作會漂移。LLM agent 版本已退役。
6. **Merger Review**
   - `[spawn agent]` 啟動 1 個 `mapping_merger_reviewer`，assignment 帶上 Step 5 抓到的 self-check stdout：
     ```text
     paper_dir: <paper_dir>
     review_round: round_00
     reviewer_id: reviewer_01
     output_root: <paper_dir>/mapping/merger_reviewer/round_00/reviewer_01
     self_check_stdout: |
       <Step 5 印出的完整 stdout>
     ```
   - Reviewer 讀 `mapping/canonical/paper.html`、所有 `mapping.*.json`、`method.json`、`summary.json`、`mapping_merger.md` spec，產出 `visual_review.json`（schema `mapping_merger_review.v1`）：
     - `findings[]`：reader-visible 的 rendering bug，分 `required` / `advisory`。
     - `merger_bugs[]`：reviewer 認為是 merger script bug 或誤判的 entry（false positive in self-check、wrap rule too strict 等）。**不影響 gate**。
   - `[mechanical]` Promote：複製 `visual_review.json` 到 `mapping/canonical/merger_review.json`。
7. **Merger Repair (Gate-driven)**
   - **Gate**：讀 `mapping/canonical/merger_review.json`。
     - 沒有 `required` findings → 進入 Step 8 Finalize。
     - 有 `required` findings 且 round < 4 → 進入 Repair。
     - Round limit 達到（預設 4 輪）→ 回報 Blocked。
   - `[spawn agent]` 啟動 1 個 `mapping_merger_repair`，assignment：
     ```text
     paper_dir: <paper_dir>
     review_path: <paper_dir>/mapping/canonical/merger_review.json
     output_root: <paper_dir>/mapping/merger_repair/round_<N>/worker_01
     ```
   - Repair worker **直接 patch `mapping/canonical/paper.html`**（in-place），同時寫 `<output_root>/repair_log.json`。**不得**改源檔 (mapping/method/summary)、不得改 merger script、不得重跑 merger script——重跑會把 patch 蓋掉。
   - 完成後回到 Step 6 Merger Review 做 re-review（round_01）；reviewer 看的是 patch 後的 paper.html。已通過的 finding 不重審。
8. **Finalize**
   - 將 `mapping/canonical/paper.html` 無損複製覆寫到 `final/<paper_id>.html`，完成含有完整 mapping 標註的論文交付。
9. **Surface merger_bug_report**（gate close 後一律執行）
   - `[mechanical]` 從 `mapping/canonical/merger_review.json`（最終一輪）讀 `merger_bugs[]`，與 repair_log 中的 `skipped[].reason` 合併，呈給 user。
   - 訊息結構：每筆 `kind`、`evidence`、`suggested_fix`，並標出 paper.html 已被 patch 但根本問題仍在源檔／merger 內。
   - **詢問 user 是否要修 merger / 源檔**；user 決定，Parent 不主動改 merger script 或源檔。

---

## Moving Lane (Publish) 專屬流程

**預設開啟**：Mapping Lane 完成後自動執行，不需 user 額外指示；只有當 user 明確說「不要 publish / 跳過 moving lane」才略過。

這是 mapping pipeline 之後、發布前的最後一步（mechanical），將已 finalize 的 paper 複製到個人 GitHub Pages 倉庫使其成為可訪問的網頁。

1. **前置驗證**
   - 確認 `<paper_dir>/final/` 存在。
   - 確認 `<paper_dir>/final/<paper_slug>.html` 存在（若無代表 mapping pipeline 未成功或 merger 發生錯誤）。
   - 確認該 HTML 是 mapping_merger 在 **Step 9 self-check 11/11 PASS** 之後寫出來的；若 self-check 沒過就跑 Moving，等於把半成品上架。**沒過 11/11 → 回頭修 mapping，不要 publish**。
   - 確認目的端 root `{{GITHUB_IO_ROOT}}/papers/` 存在（如不存在則 abort 並要求 user 確認路徑）。
2. **同步 (Rsync)**
   - `[mechanical]` 對每篇 paper 跑一次 `rsync`：
     ```bash
     mkdir -p {{GITHUB_IO_ROOT}}/papers/{{PAPER_SLUG}}
     rsync -a <paper_dir>/final/ {{GITHUB_IO_ROOT}}/papers/{{PAPER_SLUG}}/
     ```
   - **注意**：末尾 `/` 在 `rsync` 是必要的。必須加上 `-a` 以保留權限等屬性。
   - **禁止**加 `--delete`，以免誤刪目的端 user 自行添加的舊檔備份。同名檔案會預期地被 `final/` 覆蓋。
3. **批次處理 (若需要)**
   - 一次處理多篇 paper 時，直接 loop 所有 `{{PAPER_SLUG}}` 執行上述邏輯。
4. **Git commit（不 push）**
   - **前提**：Step 2 的 `rsync` 必須先成功完成；本步只負責把 rsync 帶進去的檔案 commit 起來，本身不複製任何檔案。
   - `[mechanical]` 在 `{{GITHUB_IO_ROOT}}` 對剛同步進來的 paper 目錄做 `git add` 與 `git commit`：
     ```bash
     cd {{GITHUB_IO_ROOT}}
     git add papers/{{PAPER_SLUG}}/
     git commit -m "Add paper: {{PAPER_SLUG}}"   # 或 "Update paper: {{PAPER_SLUG}}"
     ```
   - 只 stage `papers/{{PAPER_SLUG}}/`，避免誤加目的端 user 自己改的其他檔案。
   - commit message 依目的端原本是否已存在同名 paper 目錄判斷：新增用 `Add paper: ...`、覆寫既有用 `Update paper: ...`。
   - **禁止**自動 `git push`，推送由 user 作最終決策。
5. **回報**
   - 回報：各 paper 複製後的 item count 與 total size、哪些是新增/覆蓋、`rsync` 警告、以及剛產生的 commit SHA 與 message，讓 user 確認後再 push。
   - （SKILL 不負責 site-level 的 `index.html` 或 theme，只負責將內容就緒）。
