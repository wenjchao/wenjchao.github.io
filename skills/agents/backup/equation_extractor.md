# 目標

這是一份給 equation_extractor agent 看的指引。

從一份 PDF 擷取顯示方程式（displayed equations），輸出裁切 PNG 和 LaTeX 中繼資料。

已轉成圖片的頁面是最終依據（ground truth）。PDF 文字擷取可以協助定位候選項，但方程式範圍和 LaTeX 必須根據視覺證據決定。PDF 文字擷取會失去符號之間的空間關係，因此下標、上標、分式版面、上下限和對齊不能從文字流推斷——LaTeX 一律要從頁面圖片證據轉寫。

- 輸入：一個 paper directory、pages 範圍、worker scope / assignment、`artifact_root`。
- 輸出位置：`<paper_dir>/equations/workers/worker_01/`
- 輸出：
    - `equation_candidates.json`：每頁疑似顯示方程式的候選視覺區域、編號候選、附近文字。
    - `equation_index.json`：從候選項中選出的正式顯示方程式索引。
    - `equation_decisions.json`：裁切決策（planning trace）。此檔不進 canonical。
    - `equations.json`：唯一的 extraction output manifest。每個方程式記錄 crop、LaTeX、verification。
    - `crops/`：裁切 PNG。
    - `previews/`：所有 preview 圖片。
    - `rendered_latex/`：LaTeX 渲染後的預覽圖。
    - `source_regions/`：來源區域裁切。
    - `boundaries/`：boundary 和 edge strip 原檔。
- 目標：讓每個 crop 精確包含完整方程式（含編號），不切掉任何部分，同時排除周圍正文。LaTeX 必須準確反映 crop 中可見的數學結構。
- 邊界：
    - 此 agent 只負責 initial extraction，不負責 reviewer、repair 或 canonical merge。
    - 此 agent 必須執行自己的 self-check；這不是 parent canonical validation。
    - 不處理 repair mode；repair 由獨立的 repair agent 執行。

## 範圍規則

預設範圍是 `all_displayed`：擷取所有顯示方程式（置中或獨立成行），無論是否編號。包含命題、引理、推論和附錄證明中的方程式區塊。

對未編號方程式，使用頁面錨定的合成 `equation_number`，格式為 `unnumbered_p<page>_<seq>`（例如 `unnumbered_p7_1`）。無論是否編號，`equation_id` 都使用正常連續格式（`Equation_1`、`Equation_2`）。

如果協調器指定 `scope: numbered_only`，只擷取明確可見編號的方程式（例如 `(1)`、`(2)`、`Eq. 1`）。重要的未編號顯示方程式可在 `notes` 提到，但不要擷取。

掃描指派範圍中的每一頁。如果沒有指派頁面範圍，就掃描 PDF 每一頁，包括附錄、補充證明和文末材料。不要假設方程式只出現在正文。協調器提供的頁面提示只是提示，不是最終依據。

一次掃完所有頁面，不得 defer 到「後續 pass」。不存在 separate pass、incremental batch 或 deferred extraction。`omitted_candidates` 只能放「判斷後確定不是顯示方程式」的候選，不能放「是顯示方程式但決定稍後處理」。

排除行內數學、正文中的普通變數定義、化學結構圖，以及圖面板中的數學。

# 流程

## 輔助工具

本 agent 需要裁切或建立 preview 時，只使用本 skill 內的 local helper：

- `agents/scripts/crop_and_preview.py`：一次完成裁切 + 全套 edge evidence preview（crop、boundary、top/left/right edge strips、bottom band、bottom micro）。
- `agents/scripts/crop_region.py`：裁出 source region 或其他單次裁切需求。
- `agents/scripts/make_image_preview.py`：建立受限尺寸 preview。
- `agents/scripts/render_latex_preview.py`：渲染 LaTeX 為預覽圖（pdflatex → matplotlib → text fallback）。
- `agents/scripts/validate_equation_extraction.py`：檢查 extractor output contract（JSON structure、artifact paths、crop_px 範圍、LaTeX 非空、braces balanced、edge evidence 存在）。

不要直接呼叫 `skills/_shared/scripts/...`。

## Step 1: 準備頁面圖片



a) 確保完整解析度頁面圖片存在（`shared/pages/page_N.png`）。若不存在，回報 `blocked_missing_page_image`。

b) 確保預覽頁面圖片存在（`shared/previews/page_N_preview.png`）。若不存在，回報 `blocked_missing_page_preview`。

## Step 2: 候選偵測

**[judgment]**

a) **[judgment]** 讀取受限尺寸頁面預覽圖，找出顯示方程式候選。產生 `equation_candidates.json`。每個候選應記錄頁碼、候選區域座標、可能的方程式編號、附近文字、是否跨行或跨頁。每個候選必須有視覺區域證據。

b) **[script]** 依需要建立 source region（按需產生）。要讀 source context 或候選會進入 index → 必須先建立 source region preview。

## Step 3: 索引建立與 source context 檢查

**[judgment]**

a) **[judgment]** 讀取 `equation_candidates.json`、預覽頁面圖片和 source region previews，判斷哪些候選是真正的顯示方程式。

b) **[judgment]** 撰寫 `equation_index.json`，列出本次要擷取的所有方程式。每個項目包含 equation_id、equation_number（含合成編號）、所在頁碼、候選區域 id、是否多行或跨頁。

c) **[judgment]** 針對每個已索引的方程式，讀取 source region preview 確認：方程式範圍完整、編號位置正確、與周圍正文的邊界可辨識。

## Step 4: 裁切決策與執行

a) **[judgment]** 撰寫 `equation_decisions.json`（planning trace）。每個方程式記錄 crop_px、image_file、排除項目、決策理由。所有 crop_px 使用完整解析度頁面圖片 pixel coordinate。

b) **[script]** 使用 `crop_and_preview.py` 一次完成裁切和全套 evidence preview：

   ```bash
   python3 agents/scripts/crop_and_preview.py \
     --page-image shared/pages/page_N.png \
     --crop-px <x1> <y1> <x2> <y2> \
     --crop-id <equation_id> \
     --output-dir <artifact_root>
   ```

   不要從 source region 或其他中間圖片再裁。多行方程式作為單一區塊裁切，不拆開。跨頁方程式分別裁切每頁部分。

## Step 5: LaTeX 轉寫

**[judgment]**

a) **[judgment]** 對每個方程式，從 crop preview 和 source region preview 轉寫 LaTeX。LaTeX 必須從視覺證據轉寫，不從 PDF text extraction 複製。

b) 渲染 LaTeX 預覽：

   ```bash
   python3 agents/scripts/render_latex_preview.py \
     "<artifact_root>/equations.json" "<artifact_root>/rendered_latex" --batch
   ```

c) **[judgment]** 讀取 rendered LaTeX preview，和 crop preview 視覺比對。確認 LaTeX 準確反映 crop 中可見的數學結構。不一致 → 修正 LaTeX，重新渲染，重新比對。

### LaTeX 規則

- 保留分式（`\frac`）、上標（`^{}`）、下標（`_{}`）、根號（`\sqrt`）、矩陣、分段函數（`\begin{cases}`）、求和/積分上下限、希臘字母、運算子和有意義的對齊。
- 多行環境：保留 `\begin{aligned}`、`\begin{cases}`、`\begin{pmatrix}` 等結構。不要把多行方程式壓成單行。
- 重音變體：單字元用 `\hat{x}`，多字元用 `\widehat{XY}`。`\tilde`/`\widetilde`、`\bar`/`\overline`、`\dot`/`\ddot` 同理。比較來源圖片中的重音寬度來選擇。
- 方程式編號存在 metadata 中，不放進 `latex` 欄位。
- 未解決的符號歧義記錄在 `uncertainties`；通過的擷取不得有未解決不確定性。

## Step 6: 視覺驗證與邊界決策

**[judgment]**

a) **[judgment]** 讀取每個 equation 的 evidence：
    - **Crop preview**：方程式內部細節（符號、上下標、對齊）。
    - **Boundary preview**：整體 framing — cyan 矩形是否切到方程式或混入正文。
    - **Edge strips / bottom band / bottom microzoom**：逐邊精確檢查。

    **核心規則：不可以有任何方程式內容跨越 cyan 線。** figure 的 cyan 線規則完全適用於 equation。

b) **[judgment]** 邊界調整後重跑 `crop_and_preview.py`，再次檢查。調整後的 crop_px 直接寫入 `equations.json`，不需回去同步 `equation_decisions.json`。

### 驗證標準

方程式只有在下列條件全部成立時才通過：
- crop 包含完整顯示方程式和編號。
- 不包含周圍正文或頁面固定元素。
- 上、下、左、右 crop 邊緣乾淨。
- LaTeX 符合可見方程式結構。
- 小型記號完整：下標、上標、上下限、撇號、橫線、帽號、點和希臘字母。
- 多行對齊、分段函數、矩陣或括號結構已保留。

只使用 `pass` 或 `fail`。不確定就是 `fail`。

## Step 7: 最終 manifest 與 self-check



a) 撰寫 `equations.json`。`equations.json` 是唯一的 extraction output manifest。可以記錄 `verification.result = "fail"` 的方程式；但只要任何方程式 fail，`status` 就是 `incomplete`。

b) **[script]** 寫出/更新 `equations.json` 後、回報成功前，必須執行 mandatory 機械自檢：

   ```bash
   python3 agents/scripts/validate_equation_extraction.py \
     "<artifact_root>" \
     --paper-dir "<paper_dir>"
   ```

   若 validator 回傳 `status: "fail"`，先修正 JSON、path 或缺失 artifact，然後重跑 validator。Validator 通過前不得回報 extraction 完成。

   此 validator 只檢查機械 contract：JSON parse / schema、artifact-root-relative paths、必要檔案存在、`crop_px` 基本範圍、edge strip / bottom band / microzoom previews、LaTeX 非空且 braces balanced、`rendered_latex_preview` 存在、`verification.latex_checked` 必填。它不判斷 crop 是否視覺完整或 LaTeX 是否語意正確。

c) 若指定範圍中沒有顯示方程式，仍寫出四個 JSON，`equations` 為空陣列，`status` 設為 `complete`。

d) 回報結果。

# 格式

## JSON 格式

所有 JSON 使用 `schema_version: "equation_extraction.v1"`。

### Artifact root 相對路徑

- `artifact_root` 是 `<paper_dir>/equations/workers/worker_01/`。
- Equation artifact paths 相對於 `artifact_root`（例如 `crops/Equation_1.png`）。
- Shared page paths 使用 paper-dir-relative path（`shared/pages/page_3.png`）。
- 不要在 artifact path 裡寫 `equations/workers/worker_01/`、`equations/canonical/` 或絕對路徑。

### equation_candidates.json

#### Enums

- `region_type`：
  - `equation_display`：置中或獨立成行的顯示方程式區域
  - `equation_number`：方程式編號（如 `(1)`、`(A.3)`）
  - `body`：正文
  - `header`：頁眉
  - `footer`：頁腳
  - `unknown`：無法判斷的區域
- `source`：
  - `model_visual`：從受限尺寸頁面預覽圖片目視判斷。必須在 `notes` 說明證據限制。
  - `pdf_text`：PDF 文字層
  - `geometry`：幾何分析（置中偵測等）
  - `manual`：手動標記。必須在 `notes` 說明證據限制。

#### Fields

- `scope.pages`：int array，worker 掃描的頁碼
- `pages[]`：per-page objects
  - `page`：int
  - `page_image`：paper-dir-relative path
  - `page_preview`：paper-dir-relative path
  - `page_size_px`：[width, height]
  - `regions[]`：
    - `region_id`、`region_type`、`bbox_px` [x1,y1,x2,y2]、`source`、`confidence`（float）、`text`（nullable）、`notes`
  - `source_regions[]`：
    - `source_region_id`、`source_image`（artifact-root-relative）、`source_preview`（artifact-root-relative）、`bbox_px`、`candidate_ids`
  - `equation_candidates[]`：
    - `candidate_id`、`equation_number`（nullable for unnumbered）、`visual_region_ids`、`source_region_ids`、`crop_hint_px` [x1,y1,x2,y2]、`is_multiline`（bool）、`is_cross_page`（bool）
- `unexpected_labeled_equations[]`：有方程式編號但不在 assignment 的。必填 `equation_number`、`page`、`reason`。

### equation_index.json

#### Fields

- `scope.pages`：int array
- `equations[]`：
  - `equation_id`：filename-safe（`Equation_1`、`Equation_2`）
  - `equation_number`：可見編號原樣（`(1)`、`(A.3)`）或合成（`unnumbered_p<page>_<seq>`）
  - `pages`：int array（此階段還沒有 `crop_units`，所以保留 `pages`）
  - `candidate_ids`、`source_region_ids`
  - `is_multiline`：bool
  - `is_cross_page`：bool
  - `notes`
- `omitted_candidates[]`：`candidate_id`、`reason`

### equation_decisions.json

Planning trace — 不進 canonical。

#### Fields

- `equations[]`：
  - `equation_id`、`equation_number`、`candidate_ids`、`source_region_ids`
  - `evidence_read`：`page_previews`（paper-dir-relative）、`source_region_previews`（artifact-root-relative）
  - `crop_units[]`：
    - `crop_id`、`page`（int）、`crop_px` [x1,y1,x2,y2]、`image_file`、`preview`、`boundary_preview`、`top_band`、`left_band`、`right_band`、`bottom_band`、`bottom_micro`、`role`
  - `exclusions`、`rationale`

### equations.json

唯一的 extraction output manifest。進 canonical。

#### Enums

- `status`：`complete`（所有 equation pass）| `incomplete`（任何 equation fail）
- `verification.*`：`pass` | `fail`
- `verification` 欄位：
  - `source_context_checked`：agent 已讀過 source context preview
  - `final_crop_checked`：agent 已讀過 final crop preview
  - `boundary_preview_checked`：agent 已讀過 boundary preview 和 edge strips
  - `latex_checked`：agent 已讀過 rendered LaTeX preview 並和 crop 比對
  - `result`：綜合判定

#### Fields

- `status`：`complete` 或 `incomplete`
- `equations[]`：
  - `equation_id`：filename-safe
  - `equation_number`：可見編號原樣或合成
  - `candidate_ids`、`source_region_ids`
  - `latex`：不含方程式編號，不含 `$` 或 `$$` 包裹
  - `rendered_latex_renderer`：`pdflatex` | `matplotlib` | `text_fallback`
  - `rendered_latex_preview`：artifact-root-relative path
  - `uncertainties`：string array（通過的方程式必須為空陣列）
  - `crop_units[]`：
    - `crop_id`、`page`（int）、`crop_px` [x1,y1,x2,y2]
    - `image_file`：`crops/<equation_id>.png`（跨頁：`crops/<equation_id>_p<page>.png`）
    - `preview`、`boundary_preview`：artifact-root-relative
    - `top_band`、`left_band`、`right_band`：string array
    - `bottom_band`、`bottom_micro`：string array
    - `role`：free-text（`complete equation`、`page 3 portion` 等）
  - `evidence_read`：
    - `final_crop_previews`、`boundary_previews`、`bottom_band_previews`、`bottom_micro_previews`、`rendered_latex_previews`：string arrays
  - `verification`：見上方 enum 定義
  - `notes`

#### Naming

- `equation_id`：filename-safe，`Equation_1`、`Equation_2`（不論是否編號都連續）
- Single crop：`crops/<equation_id>.png`；跨頁：`crops/<equation_id>_p<page>.png`
- 所有 artifact path 使用 artifact-root-relative
- `crop_px`：完整解析度頁面圖片 pixel coordinate

### equation_candidates.json example

```json
{
  "schema_version": "equation_extraction.v1",
  "worker_id": "worker_01",
  "scope": { "pages": [3, 4] },
  "pages": [
    {
      "page": 3,
      "page_image": "shared/pages/page_3.png",
      "page_preview": "shared/previews/page_3_preview.png",
      "page_size_px": [2481, 3296],
      "regions": [
        {
          "region_id": "p003_r001",
          "region_type": "equation_display",
          "bbox_px": [200, 1400, 2200, 1500],
          "source": "model_visual",
          "confidence": 0.85,
          "text": null,
          "notes": ["從頁面預覽圖片識別的置中顯示方程式"]
        }
      ],
      "source_regions": [
        {
          "source_region_id": "p003_src001",
          "source_image": "source_regions/p003_src001.png",
          "source_preview": "previews/p003_src001_preview.png",
          "bbox_px": [150, 1300, 2300, 1600],
          "candidate_ids": ["p003_c001"]
        }
      ],
      "equation_candidates": [
        {
          "candidate_id": "p003_c001",
          "equation_number": "(1)",
          "visual_region_ids": ["p003_r001"],
          "source_region_ids": ["p003_src001"],
          "crop_hint_px": [200, 1400, 2200, 1500],
          "is_multiline": false,
          "is_cross_page": false
        }
      ]
    }
  ],
  "unexpected_labeled_equations": [],
  "notes": []
}
```

### equation_index.json example

```json
{
  "schema_version": "equation_extraction.v1",
  "worker_id": "worker_01",
  "scope": { "pages": [3, 4] },
  "equations": [
    {
      "equation_id": "Equation_1",
      "equation_number": "(1)",
      "pages": [3],
      "candidate_ids": ["p003_c001"],
      "source_region_ids": ["p003_src001"],
      "is_multiline": false,
      "is_cross_page": false,
      "notes": []
    },
    {
      "equation_id": "Equation_2",
      "equation_number": "unnumbered_p4_1",
      "pages": [4],
      "candidate_ids": ["p004_c001"],
      "source_region_ids": ["p004_src001"],
      "is_multiline": true,
      "is_cross_page": false,
      "notes": ["未編號的 aligned 方程式"]
    }
  ],
  "omitted_candidates": [],
  "notes": []
}
```

### equation_decisions.json example

```json
{
  "schema_version": "equation_extraction.v1",
  "worker_id": "worker_01",
  "equations": [
    {
      "equation_id": "Equation_1",
      "equation_number": "(1)",
      "candidate_ids": ["p003_c001"],
      "source_region_ids": ["p003_src001"],
      "evidence_read": {
        "page_previews": ["shared/previews/page_3_preview.png"],
        "source_region_previews": ["previews/p003_src001_preview.png"]
      },
      "crop_units": [
        {
          "crop_id": "Equation_1",
          "page": 3,
          "crop_px": [200, 1405, 2200, 1495],
          "image_file": "crops/Equation_1.png",
          "preview": "previews/Equation_1_preview.png",
          "boundary_preview": "previews/Equation_1_boundary_preview.png",
          "top_band": ["previews/Equation_1_top_seg1_preview.png"],
          "left_band": ["previews/Equation_1_left_seg1_preview.png"],
          "right_band": ["previews/Equation_1_right_seg1_preview.png"],
          "bottom_band": ["previews/Equation_1_bottom_seg1_preview.png"],
          "bottom_micro": ["previews/Equation_1_micro_bottom_seg1_preview.png"],
          "role": "complete equation"
        }
      ],
      "exclusions": ["surrounding prose above and below"],
      "rationale": "Single-line numbered equation centered on page 3."
    }
  ],
  "notes": []
}
```

### equations.json example

```json
{
  "schema_version": "equation_extraction.v1",
  "worker_id": "worker_01",
  "status": "complete",
  "equations": [
    {
      "equation_id": "Equation_1",
      "equation_number": "(1)",
      "candidate_ids": ["p003_c001"],
      "source_region_ids": ["p003_src001"],
      "latex": "E = mc^{2}",
      "rendered_latex_renderer": "pdflatex",
      "rendered_latex_preview": "rendered_latex/Equation_1_preview.png",
      "uncertainties": [],
      "crop_units": [
        {
          "crop_id": "Equation_1",
          "page": 3,
          "crop_px": [200, 1405, 2200, 1495],
          "image_file": "crops/Equation_1.png",
          "preview": "previews/Equation_1_preview.png",
          "boundary_preview": "previews/Equation_1_boundary_preview.png",
          "top_band": ["previews/Equation_1_top_seg1_preview.png"],
          "left_band": ["previews/Equation_1_left_seg1_preview.png"],
          "right_band": ["previews/Equation_1_right_seg1_preview.png"],
          "bottom_band": ["previews/Equation_1_bottom_seg1_preview.png"],
          "bottom_micro": ["previews/Equation_1_micro_bottom_seg1_preview.png"],
          "role": "complete equation"
        }
      ],
      "evidence_read": {
        "final_crop_previews": ["previews/Equation_1_preview.png"],
        "boundary_previews": ["previews/Equation_1_boundary_preview.png"],
        "bottom_band_previews": ["previews/Equation_1_bottom_seg1_preview.png"],
        "bottom_micro_previews": ["previews/Equation_1_micro_bottom_seg1_preview.png"],
        "rendered_latex_previews": ["rendered_latex/Equation_1_preview.png"]
      },
      "verification": {
        "source_context_checked": "pass",
        "final_crop_checked": "pass",
        "boundary_preview_checked": "pass",
        "latex_checked": "pass",
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

- `equation_extractor` 只做 initial extraction。
- 不寫 canonical 成果、review 成果或 repair 成果。
- 不處理 repair mode。
- 不修改來源 PDF。

## 圖片與讀取限制

- 所有 preview 檔名必須含 `_preview`。
- 不含 `_preview` 的圖片不得直接讀取。
- 單張 preview 兩邊不超過 1600 px；多張一起讀時每張不超過 1400 px。

## 座標規則

- 所有 JSON 座標使用完整解析度頁面圖片 pixel coordinate。
- 最終裁切永遠從頁面圖片裁出，不從 source region 或中間圖片再裁。
- 座標換算時保守外擴，再用 evidence 收緊。

## 方程式邊界

- 方程式的可見內容（數學符號、編號、對齊標記）屬於方程式內部，保留在 crop 中。
- 周圍正文、頁面固定元素、相鄰方程式應排除。
- 如果方程式和正文因版面交錯無法乾淨分離，優先保留方程式的全部內容，標 `pass`，在 `notes` 說明。

## 跨頁方程式

- 跨頁方程式分別裁切每頁部分，列在 `image_files` 和 `crop_units`，用同一個 `equation_id` 關聯。
- 在 `notes` 說明跨頁分割。

## 空範圍

如果指定範圍中沒有顯示方程式：
- 仍寫出四個 JSON，`equations` 為空。
- `equations.json.status` 設為 `complete`。
