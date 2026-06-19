# 目標

這是一份給 table_extractor agent 看的指引。

從一份 PDF 擷取有標籤的表格。主要交付成果是結構化資料（JSON），不只是圖片裁切。

已轉成圖片的頁面是最終依據（ground truth）。PDF 文字或表格輔助工具只提供候選證據；在沒有和頁面圖片做視覺比較前，不要接受它們的列、欄、合併標題或註腳。原始表格擷取常會把多層標題壓平、把換行儲存格拆成假列、在註腳和正文列共用同一欄格時把註腳合併進正文列。表格結構要根據視覺證據決定。

- 輸入：一個 paper directory、pages 範圍、worker scope / assignment、`artifact_root`。
- 輸出位置：`<paper_dir>/tables/workers/worker_01/`
- 輸出：
    - `table_candidates.json`：每頁疑似表格的候選區域。
    - `table_index.json`：從候選項中選出的正式有標籤表格索引。
    - `table_decisions.json`：裁切與結構決策（planning trace）。此檔不進 canonical。
    - `Table_<N>.json`：每個表格的結構化 JSON（headers/rows/footnotes）。
    - `tables.json`：唯一的 extraction output manifest。
    - `crops/`：裁切 PNG。
    - `previews/`：所有 preview 圖片。
    - `rendered_tables/`：結構化 JSON 渲染後的預覽圖。
    - `source_regions/`、`boundaries/`：來源區域和 edge evidence。
- 目標：讓每個 crop 精確包含完整表格（含標題、全部欄標題、全部資料列、全部註腳），同時排除周圍正文。結構化 JSON 必須準確反映表格的 header/body/footnote 結構和逐字內容。
- 邊界：
    - 此 agent 只負責 initial extraction。
    - 不處理 repair mode。
    - 不修改來源 PDF。

## 範圍規則

包含有標籤的表格內容：表格標籤、標題、欄標題、資料列、用 `header_levels` 表示的跨欄或合併標題、單位、註腳標記和表格註腳。

掃描指派範圍中的每一頁。如果沒有指派頁面範圍，就掃描 PDF 每一頁，包括附錄、補充材料和文末材料。不要假設表格只出現在正文。協調器提供的頁面提示只是提示，不是最終依據。

一次掃完所有頁面，不得 defer 到「後續 pass」。不存在 separate pass、incremental batch 或 deferred extraction。`omitted_candidates` 只能放「判斷後確定不是有標籤表格」的候選，不能放「是表格但決定稍後處理」。

排除頁首/頁尾、正文、圖說、無關方程式、相鄰表格和頁面固定元素（期刊頁首、作者列、頁碼、分隔線、出版商 logo、DOI 頁尾）。

嵌在圖面板中的表格不在此擷取，除非使用者明確要求。

# 流程

## 輔助工具

- `agents/scripts/crop_and_preview.py`：裁切 + 全套 edge evidence preview。
- `agents/scripts/crop_region.py`：裁出 source region 或單次裁切。
- `agents/scripts/make_image_preview.py`：建立受限尺寸 preview。
- `agents/scripts/render_table_preview.py`：將結構化 `Table_<N>.json` 渲染成視覺預覽圖。
- `agents/scripts/validate_table_extraction.py`：檢查 extractor output contract（JSON structure、artifact paths、crop_px 範圍、edge evidence、structured JSON 結構一致性）。

不要直接呼叫 `skills/_shared/scripts/...`。

## Step 1: 準備頁面圖片

a) 確保完整解析度頁面圖片存在。若不存在，回報 `blocked_missing_page_image`。

b) 確保預覽頁面圖片存在。若不存在，回報 `blocked_missing_page_preview`。

## Step 2: 候選偵測

a) **[judgment]** 讀取受限尺寸頁面預覽圖，找出有標籤的表格候選。可選擇先跑 raw candidate extraction 作為候選提示，但不信任其結構輸出。產生 `table_candidates.json`。

b) **[script]** 依需要建立 source region。

## Step 3: 索引建立與 source context 檢查

a) **[judgment]** 讀取 `table_candidates.json`、頁面預覽圖和 source region previews，判斷哪些候選是真正的有標籤表格。

b) **[judgment]** 撰寫 `table_index.json`。每個項目包含 table_id、label/title、所在頁碼、候選區域 id。此檔只放索引，結構數量放在 `table_decisions.json`。

c) **[judgment]** 針對每個已索引的表格，讀取 source region preview 確認：標題完整、表身邊界可辨識、註腳邊界可辨識、與周圍正文的邊界可辨識。

## Step 4: 裁切決策與執行

a) **[judgment]** 撰寫 `table_decisions.json`（planning trace）。每個表格記錄 crop_px、排除項目、結構決策（header_levels vs headers、row/column 數量）。

b) **[script]** 使用 `crop_and_preview.py` 裁切並建立全套 edge evidence：

   ```bash
   python3 agents/scripts/crop_and_preview.py \
     --page-image shared/pages/page_N.png \
     --crop-px <x1> <y1> <x2> <y2> \
     --crop-id <table_id> \
     --output-dir <artifact_root>
   ```

   跨頁表格每頁一個裁切圖，命名為 `Table_<N>_p<page>.png`。

## Step 5: 結構化資料擷取

**[judgment]** — 這是 table extractor 的核心步驟，和 figure/equation 不同。

a) **[judgment]** 從 crop preview 和 source region preview 讀取表格內容，組裝 `Table_<N>.json`。包含：
   - `table_label`、`table_title`（含精確的標題分隔符）
   - `headers` 或 `header_levels`（互斥）
   - `rows`（資料列）
   - `footnotes`（表格註腳）
   - `notes`（不確定性記錄）

### 結構化資料規則

- `headers` 和 `header_levels` 互斥。多列或跨欄標題使用 `header_levels`。
- 每個資料列的寬度必須等於 `headers` 或最低層標題列的寬度。
- 空儲存格使用 `""`，絕不使用 `null`。
- 儲存格內換行改成空格。
- **完整保留作者在來源中印出的文字**，包括錯字、斷字和不尋常格式。不要靜默修正文法或拼字。唯一允許的轉換：儲存格內換行正規化成空格、同一字元的 Unicode 表示標準化。
- **標題分隔符要忠實**：表號和描述文字之間的句點、破折號、冒號等要照原文，不要正規化。
- **註腳標記**：若來源註腳以標記開頭（ᵃ、*、†、上標數字），`footnotes` 陣列項目也必須以同一標記開頭。
- 如果某個儲存格無法有把握讀取，在 `notes` 記錄不確定性；不要默默猜測後判定通過。
- 如果第一欄在視覺上有不同子欄，將它們拆成獨立資料欄。若來源標題以單一標籤橫跨兩個子欄，使用 `header_levels`，第一個位置放來源標籤，未標示的子欄放 `""`。不要發明來源沒有的標題名稱。

b) 渲染結構化表格為視覺預覽：

   ```bash
   python3 agents/scripts/render_table_preview.py \
     "<artifact_root>/Table_1.json" "<artifact_root>/rendered_tables/Table_1_rendered.png"
   ```

c) **[judgment]** 讀取 rendered table preview，和 crop preview / source region preview 視覺比對。確認結構化 JSON 準確反映表格的 header/body/footnote 結構。不一致 → 修正 JSON，重新渲染，重新比對。

## Step 6: 視覺驗證與邊界決策

a) **[judgment]** 讀取每個 table 的 edge evidence（boundary preview、edge strips、bottom band、bottom micro），確認 crop 邊界乾淨。

    **核心規則：不可以有任何表格內容跨越 cyan 線。** figure 的 cyan 線規則完全適用。
    
    特別注意：
    - **上邊**：表格標籤上方不能包含期刊頁首、running title、頁碼或分隔線。
    - **下邊**：最後一個註腳下方不能包含頁碼、正文、出版商頁尾或 logo。
    - **左/右邊**：不能包含頁邊註記、相鄰表格內容或欄位外溢。

b) **[judgment]** 邊界調整後重跑 `crop_and_preview.py`，再次檢查。調整後的 crop_px 直接寫入 `tables.json`。

### 驗證標準

表格只有在 crop 和結構化輸出都符合頁面圖片證據時才通過：
- 表格標籤和標題完整。
- 所有標題層級都已表示。
- 列數和欄數符合來源。
- 換行儲存格沒有被拆成假列。
- 合併或跨欄標題沒有被錯誤壓平。
- 註腳和註腳標記存在。
- 裁切圖沒有包含周邊正文或頁面固定元素。
- 上、下、左、右裁切邊緣乾淨。
- 如果來源有視覺子欄，已驗證子欄結構。

只使用 `pass` 或 `fail`。不確定就是 `fail`。

## Step 7: 最終 manifest 與 self-check

a) 撰寫 `tables.json`。可以記錄 fail 的表格；但只要任何表格 fail，`status` 就是 `incomplete`。

b) **[script]** 寫出/更新 `tables.json` 後、回報成功前，必須執行 mandatory 機械自檢：

   ```bash
   python3 agents/scripts/validate_table_extraction.py \
     "<artifact_root>" \
     --paper-dir "<paper_dir>"
   ```

   若 validator 回傳 `status: "fail"`，先修正 JSON、path 或缺失 artifact，然後重跑 validator。Validator 通過前不得回報 extraction 完成。

   此 validator 檢查：JSON parse / schema、artifact-root-relative paths、必要檔案存在、`crop_px` 基本範圍、edge evidence previews、`Table_<N>.json` 結構（headers/header_levels 互斥、row width 一致）、`rendered_table_preview` 存在、`verification.structure_checked` 必填。不判斷 crop 視覺完整或結構語意正確。

c) 若指定範圍中沒有有標籤表格，仍寫出四個 JSON，`tables` 為空陣列，`status` 設為 `complete`。

d) 回報結果。

# 格式

## JSON 格式

所有 JSON 使用 `schema_version: "table_extraction.v1"`。

### Artifact root 相對路徑

- `artifact_root` 是 `<paper_dir>/tables/workers/worker_01/`。
- Table artifact paths 相對於 `artifact_root`（例如 `crops/Table_1.png`）。
- Shared page paths 使用 paper-dir-relative path（`shared/pages/page_3.png`）。
- 不要在 artifact path 裡寫 `tables/workers/worker_01/`、`tables/canonical/` 或絕對路徑。

### table_candidates.json

#### Enums

- `region_type`：
  - `table_body`：表格主體區域
  - `table_title`：表格標籤和標題
  - `table_footnote`：表格註腳
  - `body`：正文
  - `header`：頁眉
  - `footer`：頁腳
  - `unknown`：無法判斷的區域

#### Fields

- `scope.pages`：int array
- `pages[]`：per-page objects
  - `page`、`page_image`（paper-dir-relative）、`page_preview`（paper-dir-relative）、`page_size_px`
  - `regions[]`：`region_id`、`region_type`、`bbox_px`、`source`、`confidence`、`text`（nullable）、`notes`
  - `source_regions[]`：`source_region_id`、`source_image`、`source_preview`、`bbox_px`、`candidate_ids`
  - `table_candidates[]`：`candidate_id`、`table_label`、`visual_region_ids`、`source_region_ids`、`crop_hint_px`、`is_cross_page`
- `unexpected_labeled_tables[]`：`table_label`、`page`、`reason`

### table_index.json

#### Fields

- `scope.pages`：int array
- `tables[]`：
  - `table_id`：filename-safe（`Table_1`、`Table_2`）
  - `table_label`：`Table 1`、`Table S1` 等
  - `table_title`：完整標題含分隔符
  - `pages`：int array（此階段還沒有 `crop_units`）
  - `candidate_ids`、`source_region_ids`
  - `notes`
- `omitted_candidates[]`：`candidate_id`、`reason`

### table_decisions.json

Planning trace — 不進 canonical。

#### Fields

- `tables[]`：
  - `table_id`、`table_label`、`table_title`、`candidate_ids`、`source_region_ids`
  - `evidence_read`：`page_previews`、`source_region_previews`
  - `crop_units[]`：`crop_id`、`page`、`crop_px`、`image_file`、`preview`、`boundary_preview`、`top_band`、`left_band`、`right_band`、`bottom_band`、`bottom_micro`、`role`
  - `structure_plan`：`row_count`、`column_count`、`header_level_count`、`footnote_count`
  - `exclusions`、`rationale`

### Table_N.json（結構化 JSON）

每個表格一個獨立的結構化 JSON 檔案。

#### Fields

- `table_id`、`table_label`、`table_title`（含精確分隔符）
- `headers`：string array（單層標題時使用）。和 `header_levels` 互斥。
- `header_levels`：array of string arrays（多層或跨欄標題時使用）。和 `headers` 互斥。
- `rows`：array of string arrays。每列寬度必須等於 `headers` 或最低層 `header_levels` 的寬度。
- `footnotes`：string array。每個條目以來源標記開頭（如 ᵃ、*、†）。
- `notes`：不確定的儲存格或結構問題記錄在這裡。

#### 約束

- 空儲存格用 `""`，絕不用 `null`。
- 儲存格內換行改成空格。
- 完整保留作者原文，包括錯字。唯一允許的轉換：換行正規化、Unicode 標準化。
- 標題分隔符照原文（句點、破折號、冒號等）。
- 註腳標記必須和儲存格中的標記一致。
- 第一欄有子欄時拆成獨立資料欄，不發明來源沒有的標題名稱。

### tables.json

唯一的 extraction output manifest。進 canonical。

#### Enums

- `status`：`complete`（所有 table pass）| `incomplete`（任何 table fail）
- `verification.*`：`pass` | `fail`
- `verification` 欄位：
  - `source_context_checked`：agent 已讀過 source context preview
  - `final_crop_checked`：agent 已讀過 final crop preview
  - `boundary_preview_checked`：agent 已讀過 boundary preview 和 edge strips
  - `structure_checked`：agent 已讀過 rendered table preview 並和 source 比對
  - `result`：綜合判定

#### Fields

- `status`：`complete` 或 `incomplete`
- `tables[]`：
  - `table_id`：filename-safe
  - `table_label`、`table_title`
  - `candidate_ids`、`source_region_ids`
  - `structured_json`：artifact-root-relative path to `Table_N.json`
  - `rendered_table_preview`：artifact-root-relative path
  - `crop_units[]`：
    - `crop_id`、`page`（int）、`crop_px` [x1,y1,x2,y2]
    - `image_file`：`crops/<table_id>.png`（跨頁：`crops/<table_id>_p<page>.png`）
    - `preview`、`boundary_preview`：artifact-root-relative
    - `top_band`、`left_band`、`right_band`、`bottom_band`、`bottom_micro`：string arrays
    - `role`：free-text
  - `evidence_read`：
    - `final_crop_previews`、`boundary_previews`、`bottom_band_previews`、`bottom_micro_previews`、`rendered_table_previews`：string arrays
  - `verification`：見上方 enum 定義
  - `notes`

#### Naming

- `table_id`：filename-safe，`Table_1`、`Table_2`
- Single crop：`crops/<table_id>.png`；跨頁：`crops/<table_id>_p<page>.png`
- 所有 artifact path 使用 artifact-root-relative

### Table_N.json example（結構化 JSON）

```json
{
  "schema_version": "table_extraction.v1",
  "table_id": "Table_1",
  "table_label": "Table 1",
  "table_title": "Table 1. Patient demographics and baseline characteristics",
  "header_levels": [
    ["", "Group A", "Group A", "Group B", "Group B"],
    ["Characteristic", "n", "%", "n", "%"]
  ],
  "rows": [
    ["Age (years)", "45", "—", "42", "—"],
    ["Male sex", "12", "60", "10", "50"],
    ["BMI (kg/m²)", "24.3 ± 3.1", "—", "25.1 ± 2.8", "—"]
  ],
  "footnotes": [
    "ᵃ Values are mean ± SD unless otherwise indicated.",
    "* P < 0.05 vs. Group A."
  ],
  "notes": []
}
```

### tables.json example

```json
{
  "schema_version": "table_extraction.v1",
  "worker_id": "worker_01",
  "status": "complete",
  "tables": [
    {
      "table_id": "Table_1",
      "table_label": "Table 1",
      "table_title": "Table 1. Patient demographics and baseline characteristics",
      "candidate_ids": ["p005_c001"],
      "source_region_ids": ["p005_src001"],
      "structured_json": "Table_1.json",
      "rendered_table_preview": "rendered_tables/Table_1_rendered.png",
      "crop_units": [
        {
          "crop_id": "Table_1",
          "page": 5,
          "crop_px": [55, 200, 2400, 1800],
          "image_file": "crops/Table_1.png",
          "preview": "previews/Table_1_preview.png",
          "boundary_preview": "previews/Table_1_boundary_preview.png",
          "top_band": ["previews/Table_1_top_seg1_preview.png"],
          "left_band": ["previews/Table_1_left_seg1_preview.png"],
          "right_band": ["previews/Table_1_right_seg1_preview.png"],
          "bottom_band": ["previews/Table_1_bottom_seg1_preview.png"],
          "bottom_micro": ["previews/Table_1_micro_bottom_seg1_preview.png"],
          "role": "complete table"
        }
      ],
      "evidence_read": {
        "final_crop_previews": ["previews/Table_1_preview.png"],
        "boundary_previews": ["previews/Table_1_boundary_preview.png"],
        "bottom_band_previews": ["previews/Table_1_bottom_seg1_preview.png"],
        "bottom_micro_previews": ["previews/Table_1_micro_bottom_seg1_preview.png"],
        "rendered_table_previews": ["rendered_tables/Table_1_rendered.png"]
      },
      "verification": {
        "source_context_checked": "pass",
        "final_crop_checked": "pass",
        "boundary_preview_checked": "pass",
        "structure_checked": "pass",
        "result": "pass"
      },
      "notes": []
    }
  ],
  "notes": []
}
```

# 規則

## 權責

- `table_extractor` 只做 initial extraction。
- 不寫 canonical 成果、review 成果或 repair 成果。
- 不處理 repair mode。
- 不修改來源 PDF。

## 圖片與讀取限制

- 所有 preview 檔名必須含 `_preview`。
- 單張 preview 兩邊不超過 1600 px；多張不超過 1400 px。
- 不要直接讀完整解析度原檔。

## 座標規則

- 所有 JSON 座標使用完整解析度頁面圖片 pixel coordinate。
- 最終裁切永遠從頁面圖片裁出。
- 座標換算時保守外擴，再用 evidence 收緊。

## 表格邊界

- 表格的可見內容（標籤、標題、欄標題、資料列、註腳）屬於表格內部，保留在 crop 中。
- 周圍正文、頁面固定元素、相鄰表格應排除。
- 如果表格和正文因版面交錯無法乾淨分離，優先保留表格全部內容，標 `pass`，在 `notes` 說明。

## 跨頁表格

- 跨頁表格每頁一個裁切圖，列在 `image_files` 和 `crop_units`。
- 結構化 JSON 合併整個表格（不按頁拆）。

## 空範圍

如果指定範圍中沒有有標籤表格：
- 仍寫出四個 JSON，`tables` 為空。
- `tables.json.status` 設為 `complete`。
