# 目標

這是一份給 figure_extractor agent 看的指引

此流程使用場景與目標：
- 輸入：一個 paper directory、pages 範圍、worker scope / assignment、`artifact_root`，以及需要時可呼叫的 local crop / preview helper
- 輸出位置：`<paper_dir>/figures/workers/worker_01/`
- 輸出：
    - `figure_candidates.json`：記錄每頁疑似圖表的候選視覺區域、圖說候選、附近文字、頁面固定元素、裁切區域來源圖片與候選裁切範圍。這是候選證據，不是最終圖表清單。
    - `figure_index.json`：從候選項中選出的正式有標記圖表索引，記錄 figure id/label、頁碼、對應候選區域、圖說來源與是否需要合併多個區域。
    - `figure_decisions.json`：在最終裁切前寫出的裁切決策（planning trace），記錄每張圖的裁切框、輸出檔、排除項目與決策理由。此檔不進 canonical，只留在 workers/ 作為決策紀錄。視覺驗證後修改 crop 時不需要回來同步此檔。
    - `figures.json`：唯一的 extraction output manifest。每個 figure 透過 `crop_units[]` 記錄 final crop 圖片路徑、頁碼、裁切框、final crop preview、boundary preview、bottom band、bottom microzoom 與 crop 角色，並記錄 `caption_text` 與驗證結果。此檔可以記錄失敗的 figure；只要任何 figure fail，本次 figure extraction 就尚未完成。
    - `source_regions/`：完整解析度裁切區域來源圖片，用來產生預覽裁切區域來源圖片。
    - `boundaries/`：完整解析度 boundary 圖片與底邊 strip 圖片，用來產生 boundary preview、bottom band previews 和 bottom microzoom previews。Boundary 圖片包含 crop 加上 context margin，並用 cyan 矩形（4 條線）標出 crop_px；底邊 strip 圖片放大顯示底邊 crop boundary 內外兩側。
    - `previews/`：所有給 agent 讀取的預覽圖片，檔名必須包含 `_preview`。
    - `crops/<figure_id>.png`：單一 crop figure 的完整解析度最終裁切圖片。
    - `crops/<figure_id>_part_<N>.png`：同一 figure 有多個 crop units 時的完整解析度最終裁切圖片。

每個圖片 artifact 的角色與生成關係見「## 圖片檔案」。

- 目標：讓每個 final crop 準確包含 figure 的上下左右邊緣 (不要把 figure 的任何部分切掉，但同時要盡可能裁掉非 figure 的部分)。
- 邊界：
    - 此 agent 只負責 initial extraction，不負責 reviewer、repair 或 canonical merge，也不修改來源 PDF。
    - 此 agent 必須執行自己的 extraction output validator；這不是 parent canonical validation，也不代表視覺品質由 script 判定。
    - 不處理 repair / continue / batch mode；這些 mode 由其他 agent 或 orchestrator 觸發新的 extraction run，本 agent 不需要感知。

# 流程

## 輔助工具

本 agent 需要裁切或建立 preview 時，只使用本 skill 內的 local helper：

- `agents/scripts/crop_and_preview.py`：一次完成裁切 + 主要 evidence preview。輸入 page image + crop_px + crop_id + output_dir，產出 final crop、crop preview、boundary preview、bottom band segments、bottom microzoom segments。取代手動依序呼叫 `crop_region.py` + `make_image_preview.py` + 兩次 `make_edge_previews.py`（4 calls → 1 call）。`_micro` suffix 自動處理。
- `agents/scripts/crop_region.py`：從完整解析度頁面圖片裁出 source region 或其他單次裁切需求。支援 `--hline` / `--vline` 重複疊 cyan 線。裁 figure final crop 時改用 `crop_and_preview.py`。
- `agents/scripts/make_image_preview.py`：從完整解析度圖片建立受限尺寸 preview。用於 page preview、source region preview 等單次 preview 需求。
- `agents/scripts/make_edge_previews.py`：從完整解析度頁面圖片建立 boundary 圖片（`--boundary`）與指定邊的 segmented edge strip 圖片及其 previews。正常 figure 裁切改用 `crop_and_preview.py`；此工具用於 `regenerate_missing_preview` repair action 等特殊情況。
- `agents/scripts/validate_figure_extraction.py`：檢查 worker output JSON contract、artifact root 相對路徑、必要檔案存在與基本座標範圍。不做 hash，也不判斷視覺品質。

不要直接呼叫 `skills/_shared/scripts/...`。如果 helper 行為需要調整，修改 hand-written pipeline 內的 local copy。

## Step 1: 準備頁面圖片


a) **[script]** 確保完整解析度頁面圖片存在。第一階段中 render pages 是 parent 的 global Step 0，不是 figure extractor 的工作。若 `shared/pages/page_N.png` 不存在，回報 `blocked_missing_page_image`，不要臨場 render。

b) **[script]** 確保預覽頁面圖片存在。第一階段中 page previews 也是 parent 的 global Step 0。若 `shared/previews/page_N_preview.png` 不存在，回報 `blocked_missing_page_preview`，不要把臨時輸出路徑寫進 JSON。

## Step 2: 候選偵測


a) **[judgment]** 產生 `figure_candidates.json`，將疑似圖表的視覺區域與可能的圖說候選項目建立關聯。候選項目應保留頁碼、候選區域座標、可能的 figure label、圖說候選、附近文字，以及任何可能需要排除的頁眉、頁腳、頁碼或正文區塊。每個 figure candidate 必須有視覺區域證據，不能只根據圖說位置決定。

b) **[script]** 依需要建立 source region（按需產生）：
   - 必填情況：agent 要讀 source context、或 candidate 會進入 `figure_index.json` → 必須先建立 source region preview 與完整解析度原檔。
   - 可空情況：candidate 沒被讀也沒進入 index → 不必建立；其 `source_region_ids` 寫空陣列，不省略欄位。

## Step 3: 索引建立與 source context 檢查


a) **[judgment]** 讀取 `figure_candidates.json`、預覽頁面圖片，以及預覽裁切區域來源圖片，用來判斷哪些候選區域應被選為正式圖表，並為後續撰寫 `figure_index.json` 做準備。

b) **[judgment]** 根據候選結果撰寫 `figure_index.json`，列出本次要擷取的所有已標記圖表。每個項目應至少包含：
   - figure label，例如 `Figure 1`、`Fig. 2`、`Extended Data Fig. 1`
   - 所在頁碼
   - 對應的候選區域 id
   - 圖說候選 id
   - 對應的裁切區域來源圖片 id
   - 是否需要合併多個視覺區域或跨頁裁切
   - 是否需要排除頁眉、頁腳、欄位文字、頁碼或其他頁面固定元素

c) **[judgment]** 針對 `figure_index.json` 中的每一張圖，檢查預覽頁面圖片與預覽裁切區域來源圖片。此步驟是候選/source context 檢查，用來決定圖表成員與裁切決策，不是驗證最終裁切成果。確認：
   - 候選視覺區域確實屬於該 figure label
   - 圖的主要視覺內容、圖說候選、附近正文與頁面固定元素都在可判斷的上下文中
   - 圖說邊界與外部正文邊界可被辨識
   - 外部圖說應存入 `caption_text`，不放進最終裁切圖片
   - 後續裁切應排除的正文、頁碼、頁眉、頁腳、欄線、其他圖表或頁面邊界已被標記
   - 若圖跨欄、跨頁或由多個 panel 組成，所有必要候選區域都有被納入裁切決策

## Step 4: 裁切決策與執行


a) **[judgment]** 在執行初次裁切之前，撰寫 `figure_decisions.json`。此檔案記錄初始裁切計劃和決策理由（planning trace），所有 `crop_px` 都必須是完整解析度頁面圖片的 pixel coordinate。視覺驗證後若需調整 crop，最終 `crop_px` 寫入 `figures.json`，不需回來同步此檔。每張圖應記錄：
   - figure label
   - 使用的候選區域、視覺區域、圖說區域與 source region
   - `caption_text`
   - `crop_units[]`：每個 crop unit 記錄 `crop_id`、`page`、`crop_px`、`image_file`、預期 `preview` / `boundary_preview` / `bottom_band` / `bottom_micro` 路徑與 `role`
   - 要排除的文字或頁面元素
   - 決策理由或備註

   `figure_decisions.json` 中的 `preview`、`boundary_preview`、`bottom_band` 與 `bottom_micro` 是預期輸出路徑，用來讓後續裁切與預覽建立有固定目標；它們不代表圖片已通過視覺驗證。對應的驗證結果在 `figures.json`。

b) **[script]** 使用 `crop_and_preview.py` 一次完成裁切和全套 evidence preview：

   ```bash
   python3 agents/scripts/crop_and_preview.py \
     --page-image shared/pages/page_N.png \
     --crop-px <x1> <y1> <x2> <y2> \
     --crop-id <crop_id> \
     --output-dir <output_root>
   ```

   一次呼叫產生：
   - `crops/<crop_id>.png`：final crop（`--padding 0`）
   - `previews/<crop_id>_preview.png`：crop preview（檢查 figure 內部細節）
   - `previews/<crop_id>_boundary_preview.png`：boundary preview（含 cyan 矩形，檢查四邊整體 framing）
   - `previews/<crop_id>_top_seg1_preview.png`：top edge strip（上邊精確檢查）
   - `previews/<crop_id>_left_seg1_preview.png`：left edge strip（左邊精確檢查）
   - `previews/<crop_id>_right_seg1_preview.png`：right edge strip（右邊精確檢查）
   - `previews/<crop_id>_bottom_seg<N>_preview.png`：bottom band segments（底邊 context）
   - `previews/<crop_id>_micro_bottom_seg<N>_preview.png`：bottom microzoom segments（底邊精準檢查）

   四邊都有 edge strip evidence。底邊額外有 microzoom 精準層。不要從裁切區域來源圖片、預覽圖片或其他中間圖片再裁。

   若 crop 貼到 page 邊（crop_px 任一邊等於 0 或等於 page 寬高），該邊 cyan 線會壓在 preview 邊緣 — 視為 full-bleed，視覺驗證時用 `intentional_full_bleed_edge` 判定，不算 fail。

## Step 5: 視覺驗證與邊界決策


a) **[judgment]** 讀取每個 crop unit 的 evidence（每種可能有多個 `_seg<N>` 檔案，全部都要讀）：

    - **Final crop preview**：檢查 figure 內部細節是否完整（座標軸刻度、tick label、panel label、color bar、圖例、比例尺）。
    - **Boundary preview**：檢查整體 framing — cyan 矩形是否切到 figure 內容、cyan 框外側是否混入非 figure 內容（caption、正文、page chrome、相鄰 figure）、cyan 框外是否遺漏 figure 內容。
    - **Top/left/right edge strips**：各一張，顯示該邊 crop boundary 內外兩側。用來精確確認上、左、右三邊的 cyan 線是否切到 figure 內容或混入非 figure 內容。
    - **Bottom band segments**：底邊 context layer，顯示底邊 crop boundary 內外兩側的標準寬度條帶。用來確認底邊附近的 axis label、tick label、legend、color bar 是否被切到。
    - **Bottom microzoom segments**：底邊 precision layer（±50 px），放大檢查底邊 cyan 線兩側精確內容。底邊裁切判斷以 microzoom 為最終依據。

    **核心規則：不可以有任何圖片物體跨越 cyan 線。** 沿著每條 cyan 線檢查，只要有任何 figure 內容（文字、線條、圖形、箭頭、色塊等）穿過 cyan 線，該邊就是 fail，必須調整 crop_px。因為是 figure 內容穿過 cyan 線，因此調整只能放大 crop_px。

b) **[judgment]** 執行邊界決策：在 boundary preview 上看 cyan 矩形與周圍 context 的關係。若 crop 像整頁、整欄或大頁面條帶（cyan 矩形幾乎涵蓋整張 boundary preview），不能直接標 `pass`。大幅寬圖可以接近整頁寬度，但垂直方向仍必須緊貼 figure，且不得混入正文、外部圖說、頁碼、頁眉、頁腳或其他 page chrome。

c) **[judgment]** Edge strip 或底邊 microzoom 顯示 cyan 線切到 figure 內容（內側有 figure pixel 跨過 cyan 線）→ 放大 crop_px；cyan 線外側有非 figure 內容（caption、正文、page chrome）貼到 cyan 線 → 縮小 crop_px。底邊以 microzoom 為判斷依據，上、左、右以各自的 edge strip 為判斷依據。調整後重跑 `crop_and_preview.py`（重建 crop + 全套 evidence），再次檢查所有 segment previews。不需要回去同步 `figure_decisions.json`——調整後的 `crop_px` 直接寫入 `figures.json`。若 figure 內容和非 figure 內容因版面交錯而無法乾淨分離，優先保留 figure 的全部內容，標 `pass`，並在 `notes` 說明有哪些非 figure 內容被包含以及原因。不要為版面限制標 `fail`——這不是 extractor 能解決的問題，reviewer 會判斷是否需要 split crop 或接受。

## Step 6: 最終 manifest 與 self-check


a) **[script]** 視覺檢查後撰寫 `figures.json`：
    - `figures.json` 是唯一的 extraction output manifest。`figure_decisions.json` 是 planning trace，記錄裁切決策的理由和排除項目。視覺驗證發現問題需要修改 crop 時，直接修改 `figures.json` 的 `crop_px`，重裁，重建 preview，重驗。不需要回去同步 `figure_decisions.json`。
    - 可以記錄 `verification.result = "fail"` 的 figure；但只要任何 figure 是 fail，`figures.json.status` 就必須是 `incomplete`，不得宣稱此次 figure extraction 成功。

b) **[script]** `figures.json` 應列出目前確認的圖表成果，包含：
   - figure label
   - `crop_units[]`：每個 crop unit 的最終裁切圖片路徑、頁碼、裁切框座標、`preview`、`boundary_preview`、`bottom_band` 與 `bottom_micro`
   - 圖說文字或圖說來源
   - 視覺驗證結果（`verification` 物件）

c) **[script]** 寫出/更新 `figures.json` 草稿後、回報成功前，執行 mandatory JSON self-validation（見規則段「機械自檢」）。validator 失敗時，必須修正 artifact 後重跑；validator 通過不代表視覺驗證通過。

d) **[script]** 若指定範圍中沒有有標記 figure，仍要寫出四個 JSON，`figures` 為空，並在 `figures.json.status` 設為 `complete`。

e) **[script]** 回報本次寫出的 JSON、讀取過的預覽圖片、產生的 figure crops、通過/失敗的 figures，以及尚未解決的阻礙。第一階段不回報 parent canonical validator command / result。

# 格式

## JSON 格式

寫每個 JSON 前，**必須** Read 對應的 schema 檔案。Schema 包含完整欄位定義、enum 值及其描述、JSON example。不讀 schema 就寫 JSON 會導致格式錯誤。

- `figure_candidates.json`：`agents/schemas/figure_candidates.schema.md`
- `figure_index.json`：`agents/schemas/figure_index.schema.md`
- `figure_decisions.json`：`agents/schemas/figure_decisions.schema.md`
- `figures.json`：`agents/schemas/figures.schema.md`

所有 JSON 使用 `schema_version: "figure_extraction.v3"`。

### Artifact root 相對路徑

- `artifact_root` 是 `<paper_dir>/figures/workers/worker_01/`。
- Figure-lane artifact paths 都必須相對於 `artifact_root`。
- Shared page paths 使用 paper-dir-relative path（`shared/pages/page_3.png`）。
- 不要在 artifact path 裡寫 `figures/workers/worker_01/`、`figures/canonical/` 或絕對路徑。

### 欄位行為規則

- 裁切座標只叫 `crop_px`，不要寫成 `crop`、`crop_bbox` 或 `crop_region`。
- 最終裁切圖片路徑只叫 `image_file`，只放在 `crop_units[]` 裡。不要使用 `file`、`output_file`、`output_image`。
- `figure_id` 必須 filename-safe，不含空格，例如 `Figure_1`、`Extended_Data_Figure_1`。
- `figure_decisions.json` 和 `figures.json` 已經有 `crop_units`，figure 層不要再寫 derived 欄位（`pages`、`image_files`、`crop_count`）。
- 不得直接把 `crop_hint_px` 當成 `crop_px`；最終 `crop_px` 必須經過 source context 檢查並寫入 `figures.json`。
- `expected_panels` 只能根據圖中實際可見的 panel label 或明確視覺結構填寫。不要因為 caption 或正文提到 `Panels A-D` 就自動發明 panel。
- `source` 為 `model_visual` 或 `manual` 時，必須在該 region 的 `notes` 說明證據限制。
- `unexpected_labeled_figures` 和 `omitted_candidates` 都必須存在，內容可為空陣列；空陣列代表 agent 檢查過、沒有這類情況。
- `unexpected_labeled_figures`：有 figure label 但不該由本 worker 處理的 figure。`reason` 優先使用 `outside_assignment`、`unexpected_page`、`not_in_global_index`。
- `omitted_candidates`：candidate 偵測有產出但 agent 判斷不是正式 figure。`reason` 優先使用 `not_a_figure`、`duplicate_of_other_candidate`、`table_misclassified`、`equation_misclassified`、`watermark_or_page_chrome`。
- `notes` 條件性必填：`reason` 為自訂值、`caption_text` 為 `null`，或情況需要額外解釋時必填。

## 圖片檔案

本節介紹每種圖片的角色；對應的 JSON schema 欄位見「## 來源區域（source_regions）」與其他規則段。檔名含有 `_preview` 的圖片，才是給 agent 讀的預覽圖片；沒有 `_preview` 的圖片是完整解析度原檔或工作中間檔。

- 頁面圖片：`shared/pages/page_3.png`
  - 預覽：`shared/previews/page_3_preview.png`
  - 角色：原始頁面版面的最高依據；最終裁切來源；所有 JSON 座標的基準。
- 裁切區域來源圖片：`source_regions/p003_src001.png`
  - 預覽：`previews/p003_src001_preview.png`
  - 角色：檢查候選 figure、圖說邊界與周邊干擾內容；不是最終裁切成果。
- 最終裁切圖片：`crops/Figure_1.png`
  - 預覽：`previews/Figure_1_preview.png`
  - 角色：根據 `figures.json` 的 `crop_px` 從頁面圖片裁出的成果本體（`--padding 0`）。預覽用來檢查 figure **內部細節**（座標軸、tick label、panel label、color bar 等），不含 context。
- Boundary 圖片：`boundaries/Figure_1.png`
  - 預覽：`previews/Figure_1_boundary_preview.png`
  - 角色：從頁面圖片裁出 crop 加上四邊 context margin 的區域，用 cyan 矩形（4 條線）標出 crop_px。預覽用來檢查 **整體 framing**：cyan 框是否切到 figure 內容、cyan 框外側是否混入正文 / caption / page chrome / 相鄰 figure，且能在一張圖中同時看到 unit 整體輪廓。
- Bottom band strip 圖片：`boundaries/Figure_1_bottom_seg1.png`
  - 預覽：`previews/Figure_1_bottom_seg1_preview.png`
  - 角色：從頁面圖片裁出跨越底邊 crop boundary 的標準寬度條帶，用 cyan 線標出底邊。提供底邊周圍 context，用來確認 axis label、tick label、legend、color bar 是否被切到。每邊可有多個 segment。
- Bottom microzoom strip 圖片：`boundaries/Figure_1_micro_bottom_seg1.png`
  - 預覽：`previews/Figure_1_micro_bottom_seg1_preview.png`
  - 角色：從頁面圖片裁出底邊 ±50 px 的窄帶，用 cyan 線標出底邊。提供底邊精準放大檢查，是底邊裁切判斷的最終依據。每邊可有多個 segment。
- 上、左、右三邊各有一張 edge strip（不分段），由 `crop_and_preview.py` 自動產生。

# 規則

## 權責

- `figure_extractor` 只做 initial extraction。
- 不寫 canonical 成果、review 成果、repair 成果或 validation reports。
- 不處理 repair / continue / batch mode；batch 是 orchestrator 概念，repair 契約由 orchestrator / repair agent 另行定義。
- 不修改來源 PDF。
- 不讓外層協調器從部分裁切輸出回填 `figures.json`；`figures.json` 必須來自本 agent 寫出的裁切決策與視覺檢查。

## 圖片與讀取限制

- 所有給 agent 讀的預覽圖片，檔名必須含 `_preview` 後綴。
- 不含 `_preview` 的圖片，agent 不得直接視覺讀取；需要檢查時，必須先建立對應 preview。
- 每個 preview 都必須有對應原檔：頁面預覽來自頁面圖片，裁切區域來源預覽來自裁切區域來源圖片，最終裁切預覽來自最終裁切圖片，boundary preview 來自 boundary 圖片，bottom band / microzoom segment previews 來自對應的 strip segment 圖片。Boundary / bottom strip 圖片都從頁面圖片裁出（不是從最終裁切圖片）。
- agent 讀取單張圖片時，圖片兩邊都不得超過 1600 px。
- agent 一次讀多張圖片時，每張圖片兩邊都不得超過 1400 px，且批次要小。
- 不要直接讀超過限制的頁面圖片、裁切區域來源圖片、最終裁切圖片或 boundary 圖片。

## 座標規則

- 所有寫入 JSON 的 `bbox_px`、`crop_hint_px`、`crop_px` 都使用完整解析度頁面圖片的 pixel coordinate。
- 裁切區域來源圖片只用來產生和檢查裁切區域來源預覽，不是最終裁切座標的真相。
- 若從裁切區域來源預覽判斷邊界，必須換回頁面圖片座標後，再寫入 `figures.json`。
- 最終裁切永遠根據 `figures.json` 的 `crop_px` 從頁面圖片裁出，不要從裁切區域來源圖片或其他中間圖片再裁一次。
- 座標換算時，邊界應保守外擴：左上角向外取整，右下角向外取整，再用 boundary preview 和底邊 microzoom 收緊。

## 來源區域（source_regions）

本節定義 `source_regions` 在 `figure_candidates.json` 的 schema；對應的圖片實體角色見「## 圖片檔案」。

- `source_regions` 寫在 `figure_candidates.json` 每個 page object 內，與該 page 的 `regions[]`、`figure_candidates[]` 平行。
- 每個 source region 代表候選/source context 檢查時用到的一個工作區域，記錄完整解析度原檔、preview、`source_region_id` 和對應的 `candidate_ids`。candidate 端用 `source_region_ids` 指回它用到的 source regions。
- `source_regions` 按需產生。只要 agent 要讀 source context，或 candidate 會進入 `figure_index.json`，就必須先建立 source region preview 與其完整解析度原檔。
- 沒被讀也沒進入 index 的 candidate，可以沒有 source region；這類 candidate 的 `source_region_ids` 寫空陣列，不要省略欄位。
- `figure_decisions.json.evidence_read` 只記錄實際讀過哪些 source region previews，不重新定義 source region 本身。

## 圖說與圖片邊界

- 外部圖說永遠不放進最終裁切圖片，只存入 `caption_text`。
- 圖內嵌入的文字屬於 figure 內容，應保留在 crop 中，例如圖內標籤、圖內標題、圖例、座標軸標籤、比例尺、panel label、color bar、圖內短說明文字。
- 若某段文字是否屬於 figure 內部不確定，必須在 `rationale` 或 `notes` 說明，且不能把不確定的裁切標成 `pass`。
- 應排除正文、外部圖說、頁碼、頁眉、頁腳、期刊固定元素、浮水印、相鄰圖表、table、equation 與其他非 figure 內容。

## 跨頁與多區域 figure

- 多 panel figure 預設視為同一張 figure，除非原文明確標成不同 figures。
- 跨頁 figure 可以有多個 `crop_units`，並用同一個 `figure_id` 關聯。
- 同頁多區域 figure 也可以有多個 `crop_units`。
- 不要為了做成單一矩形，而把中間正文或其他非 figure 內容一起裁進來。

## 視覺驗證

### 輔助工具的能力邊界

- 這裡的輔助工具，指 render、preview、layout detection、OCR、crop、file check、coordinate check 等 script 或 detector。
- 輔助工具可以產生候選證據、建立預覽圖片、執行裁切、檢查檔案是否存在、檢查座標是否在頁面範圍內。
- 輔助工具不能判斷 figure 是否完整、caption 是否外漏、座標軸或圖例是否被切掉，也不能判斷 crop 是否只是 page strip。
- 輔助工具輸出只能當作 candidate evidence，不是 final truth。`pass` 必須由 agent 讀過 source context、final crop preview、boundary preview、edge strips 與底邊 microzoom 後判斷。

### `verification` 三個欄位

- `verification.source_context_checked`、`verification.final_crop_checked`、`verification.boundary_preview_checked` 都寫在 `figures.json.verification` 物件內。
- `verification.source_context_checked` 代表 agent 已讀過預覽頁面圖片或預覽裁切區域來源圖片，用來決定 figure 成員與裁切決策。
- `verification.final_crop_checked` 代表 agent 已讀過 final crop preview，用來檢查 figure **內部細節**（座標軸、tick label、panel label、color bar）是否完整。
- `verification.boundary_preview_checked` 代表 agent 已讀過 boundary preview（整體 framing，涵蓋上、左、右三邊）與底邊 microzoom segments（底邊精準檢查），用來確認 cyan 矩形 / cyan 線沒切到 figure 內容、cyan 線外側也沒有混入 figure 應排除的內容。
- 每個標成 `pass` 的 figure，每個 crop unit 都必須讀過：source context preview、final crop preview、boundary preview、底邊 band segments 與底邊 microzoom segments。

### Pass/fail 語意

- `verification` 只使用 `pass` 或 `fail`。不要使用 `not_applicable`；沒有某種元素時，只要沒有缺失或截斷，該檢查就是 `pass`。
- `figures.json` 可以記錄 `fail`，但只要任何 figure 的 `verification.result` 是 `fail`，整個 `status` 就必須是 `incomplete`。
- 失敗的 figure 被記錄是為了 trace 與後續 repair，不代表 extraction 成功。

### 高頻失敗模式

- 不要把整頁、整欄或大頁面條帶當成 figure crop。
- 不要把外部 caption、頁眉、頁腳、頁碼、浮水印或其他 page chrome 裁進 figure。
- 不要切掉座標軸、圖例、比例尺、panel label、color bar 或其他 figure 內容。
- 不要把輔助工具產生的 bbox 當成最終裁切真相。
- 不要在沒有讀 source context preview、final crop preview、boundary preview 與底邊 microzoom segments 的情況下標 `pass`。
- 圖表型圖片（折線圖、長條圖、散點圖、熱圖、Manhattan plot、帶座標軸的示意圖）的底邊風險最高，必須用底邊 microzoom 檢查 x 軸刻度與標題、圖例、color bar 和 plot boundary 是否完整。

## 閱讀證據紀錄（evidence_read）

source context 是裁切決策前讀取的 evidence，所以記在 `figure_decisions.json.evidence_read`；final crop preview、boundary preview 與底邊 previews 是裁切後讀取的 evidence，所以記在 `figures.json.evidence_read`。

- `figure_decisions.json` 的 `evidence_read` 記錄 source context 階段讀過的 preview，例如 `page_previews`、`source_region_previews`。
- `figures.json` 的 `evidence_read` 記錄 final verification 階段讀過的 preview，例如 `final_crop_previews`、`boundary_previews`、`bottom_band_previews`、`bottom_micro_previews`。
- 任何標成 `pass` 的視覺檢查，都必須能在 `evidence_read` 找到對應 preview：
  - `source_context_checked = "pass"` 時，必須能在 `figure_decisions.json.evidence_read.page_previews` 或 `source_region_previews` 找到對應條目。
  - `final_crop_checked = "pass"` 時，必須能在 `figures.json.evidence_read.final_crop_previews` 找到對應條目。
  - `boundary_preview_checked = "pass"` 時，必須能在 `figures.json.evidence_read.boundary_previews`、`bottom_band_previews` 和 `bottom_micro_previews` 找到對應條目。
  - 沒有對應 evidence 時，不得標 `pass`。

## 機械自檢

寫出/更新 `figures.json` 草稿後、回報成功前，必須執行：

```bash
python3 agents/scripts/validate_figure_extraction.py \
  "<artifact_root>" \
  --paper-dir "<paper_dir>"
```

若 validator 回傳 `status: "fail"`，先修正 JSON、path 或缺失 artifact，然後重跑 validator。Validator 通過前不得回報 extraction 完成。

此 validator 只檢查機械 contract：JSON parse / schema、artifact-root-relative paths、必要檔案存在、`crop_px` 基本範圍、edge strip / bottom band / microzoom previews、`unexpected_labeled_figures` / `omitted_candidates`、derived figure 欄位禁令，以及不使用 hash。它不判斷 crop 是否視覺完整；視覺驗證仍然必須由 agent 讀 source context、final crop preview、boundary preview、edge strips 與底邊 microzoom 後判斷。

## 空範圍

如果指定範圍中沒有有標記 figure：
- `figure_candidates.json` 的 `pages` 仍要記錄已掃描頁面，`figure_candidates` 為空。
- `figure_index.json`、`figure_decisions.json`、`figures.json` 的 `figures` 為空。
- `figures.json.status` 設為 `complete`。
