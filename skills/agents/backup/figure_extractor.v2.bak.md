# 目標

這是一份給 figure_extractor agent 看的指引

此流程使用場景與目標：
- 輸入：一個 paper directory、pages 範圍、worker scope / assignment、`artifact_root`，以及需要時可呼叫的 local crop / preview helper
- 輸出位置：`<paper_dir>/lanes/figures/worker_output/worker_01/`
- 輸出：
    - `figure_candidates.json`：記錄每頁疑似圖表的候選視覺區域、圖說候選、附近文字、頁面固定元素、裁切區域來源圖片與候選裁切範圍。這是候選證據，不是最終圖表清單。
    - `figure_index.json`：從候選項中選出的正式有標記圖表索引，記錄 figure id/label、頁碼、對應候選區域、圖說來源與是否需要合併多個區域。
    - `figure_decisions.json`：在最終裁切前寫出的裁切決策，記錄每張圖的最終裁切框、輸出檔、排除項目與決策理由。最終裁切必須以此檔案為依據。
    - `figures.json`：視覺驗證後的最終成果清單。每個 figure 透過 `crop_units[]` 記錄 final crop 圖片路徑、頁碼、裁切框、預覽圖、邊界預覽與 crop 角色，並記錄 `caption_text` 與驗證結果。此檔可以記錄失敗的 figure；只要任何 figure fail，本次 figure extraction 就尚未完成。
    - `source_regions/`：完整解析度裁切區域來源圖片，用來產生預覽裁切區域來源圖片。
    - `edges/`：完整解析度裁切區域邊界圖片，用來產生邊界預覽。
    - `previews/`：所有給 agent 讀取的預覽圖片，檔名必須包含 `_preview`。
    - `crops/<figure_id>.png`：單一 crop figure 的完整解析度最終裁切圖片。
    - `crops/<figure_id>_part_<N>.png`：同一 figure 有多個 crop units 時的完整解析度最終裁切圖片。

每個圖片 artifact 的角色與生成關係見「## 圖片檔案」。

- 目標：讓每個 final crop 準確包含 figure 的上下左右邊緣 (不要把 figure 的任何部分切掉，但同時要盡可能裁掉非 figure 的部分)。
- 邊界：
    - 此 agent 只負責 initial extraction，不負責 reviewer、repair、canonical merge、validator，也不修改來源 PDF。
    - 不處理 repair / continue / batch mode；這些 mode 由其他 agent 或 orchestrator 觸發新的 extraction run，本 agent 不需要感知。

# 流程

## 輔助工具

本 agent 需要裁切或建立 preview 時，只使用本 skill 內的 local helper：

- `agents/scripts/crop_region.py`：從完整解析度頁面圖片裁出 source region、final crop 或 edge image。
- `agents/scripts/make_image_preview.py`：從完整解析度圖片建立受限尺寸 preview。

不要直接呼叫 `skills/_shared/scripts/...`。如果 helper 行為需要調整，修改 hand-written pipeline 內的 local copy。

## 工作流程

### 準備頁面圖片

1. 確保完整解析度頁面圖片存在。第一階段中 render pages 是 parent 的 global Step 0，不是 figure extractor 的工作。若 `shared/pages/page_N.png` 不存在，回報 `blocked_missing_page_image`，不要臨場 render。

2. 確保預覽頁面圖片存在。第一階段中 page previews 也是 parent 的 global Step 0。若 `shared/previews/page_N_preview.png` 不存在，回報 `blocked_missing_page_preview`，不要把臨時輸出路徑寫進 JSON。

### 候選偵測與索引

3. 產生 `figure_candidates.json`，將疑似圖表的視覺區域與可能的圖說候選項目建立關聯。候選項目應保留頁碼、候選區域座標、可能的 figure label、圖說候選、附近文字，以及任何可能需要排除的頁眉、頁腳、頁碼或正文區塊。每個 figure candidate 必須有視覺區域證據，不能只根據圖說位置決定。

4. 依需要建立 source region（按需產生）：
   - 必填情況：agent 要讀 source context、或 candidate 會進入 `figure_index.json` → 必須先建立 source region preview 與完整解析度原檔。
   - 可空情況：candidate 沒被讀也沒進入 index → 不必建立；其 `source_region_ids` 寫空陣列，不省略欄位。

5. 讀取 `figure_candidates.json`、預覽頁面圖片，以及預覽裁切區域來源圖片，用來判斷哪些候選區域應被選為正式圖表，並為後續撰寫 `figure_index.json` 做準備。

6. 根據候選結果撰寫 `figure_index.json`，列出本次要擷取的所有已標記圖表。每個項目應至少包含：
   - figure label，例如 `Figure 1`、`Fig. 2`、`Extended Data Fig. 1`
   - 所在頁碼
   - 對應的候選區域 id
   - 圖說候選 id
   - 對應的裁切區域來源圖片 id
   - 是否需要合併多個視覺區域或跨頁裁切
   - 是否需要排除頁眉、頁腳、欄位文字、頁碼或其他頁面固定元素

7. 針對 `figure_index.json` 中的每一張圖，檢查預覽頁面圖片與預覽裁切區域來源圖片。此步驟是候選/source context 檢查，用來決定圖表成員與裁切決策，不是驗證最終裁切成果。確認：
   - 候選視覺區域確實屬於該 figure label
   - 圖的主要視覺內容、圖說候選、附近正文與頁面固定元素都在可判斷的上下文中
   - 圖說邊界與外部正文邊界可被辨識
   - 外部圖說應存入 `caption_text`，不放進最終裁切圖片
   - 後續裁切應排除的正文、頁碼、頁眉、頁腳、欄線、其他圖表或頁面邊界已被標記
   - 若圖跨欄、跨頁或由多個 panel 組成，所有必要候選區域都有被納入裁切決策

### 裁切決策與執行

8. 在執行任何最終裁切之前，撰寫 `figure_decisions.json`。此檔案是最終裁切的唯一依據，所有 `crop_px` 都必須是完整解析度頁面圖片的 pixel coordinate。每張圖應記錄：
   - figure label
   - 使用的候選區域、視覺區域、圖說區域與 source region
   - `caption_text`
   - `crop_units[]`：每個 crop unit 記錄 `crop_id`、`page`、`crop_px`、`image_file`、預期 preview / edge preview 路徑與 `role`
   - 要排除的文字或頁面元素
   - 決策理由或備註

   `figure_decisions.json` 中的 `preview` 與 `edge_previews` 是預期輸出路徑，用來讓後續裁切與預覽建立有固定目標；它們不代表圖片已通過視覺驗證。對應的驗證結果在 `figures.json`。

9. 根據 `figure_decisions.json`，使用共用裁切輔助工具，從完整解析度頁面圖片產生完整解析度最終裁切圖片。不要從裁切區域來源圖片、預覽圖片或其他中間圖片再裁一次。

10. 為每張完整解析度最終裁切圖片建立預覽最終裁切圖片。

11. 為每個 crop unit 從頁面圖片建立四個邊界圖片（上、下、左、右）與其預覽。每張邊界圖片是一個跨越 crop boundary 的條帶，同時顯示 crop 內側和外側的內容，並用 `crop_region.py` 的 `--hline`（上下邊界）或 `--vline`（左右邊界）在 crop boundary 位置疊一條紅線。例如 `crop_px = [x1, y1, x2, y2]` 的底邊界：從頁面圖片裁出 `[x1, y2-100, x2, y2+100]` 左右的條帶，`--hline y2`。條帶寬度可依版面調整，但必須讓紅線兩側的內容都清楚可辨。

### 視覺驗證與邊界決策

12. 讀取每張預覽最終裁切圖片與其四個邊界預覽。此步驟是 final crop + edge previews 檢查，用來驗證已產生的裁切圖片是否可接受。逐一確認：
   - 最終裁切圖片中的 figure 內容是否完整
   - 上、下、左、右邊界是否過緊或過鬆
   - 圖內標籤、座標軸、圖例、比例尺、panel label 或 color bar 是否被截斷
   - 外部圖說是否被誤納入，或應保留的圖內文字是否被切掉
   - 是否仍包含正文、頁碼、頁眉、頁腳或其他頁面固定元素
   - 是否誤切到相鄰圖表或相鄰文字

13. 執行邊界決策：先看 crop 形態，再讀四個邊界預覽。若 crop 像整頁、整欄或大頁面條帶，不能直接標 `pass`。大幅寬圖可以接近整頁寬度，但垂直方向仍必須緊貼 figure，且不得混入正文、外部圖說、頁碼、頁眉、頁腳或其他 page chrome。

14. 四邊檢查時，非 figure 內容碰邊就縮小 crop，figure 內容碰邊就放大 crop。調整後必須更新 `figure_decisions.json`、重裁、重建預覽最終裁切圖片與四個邊界預覽，並再次檢查。若 figure 內容和非 figure 內容因版面交錯而無法乾淨分離，優先保留 figure 的全部內容，將該 figure 標 `fail`，並在 `notes` 說明原因。

### 最終 manifest 與 self-check

15. 視覺檢查後撰寫 `figures.json`：
    - 每個 figure 的 `crop_units` 必須與 `figure_decisions.json` 對應 figure 的 `crop_units` 完全一致；不一致時回到 `figure_decisions.json` 修正並重生 final manifest，不要直接手改 `figures.json`。
    - 可以記錄 `verification.result = "fail"` 的 figure；但只要任何 figure 是 fail，`figures.json.status` 就必須是 `incomplete`，不得宣稱此次 figure extraction 成功。

16. `figures.json` 應列出目前確認的圖表成果，包含：
   - figure label
   - `crop_units[]`：每個 crop unit 的最終裁切圖片路徑、頁碼、裁切框座標、preview 與 edge previews
   - 圖說文字或圖說來源
   - 對應的 `figure_decisions.json` 決策項目
   - 視覺驗證結果（`verification` 物件）

17. 寫出/更新 `figures.json` 草稿後、回報成功前，執行 mechanical self-check（檢查項目見規則段「機械自檢」）。self-check 失敗時，必須修正 artifact 後重檢；self-check 通過不代表視覺驗證通過。

18. 若指定範圍中沒有有標記 figure，仍要寫出四個 JSON，`figures` 為空，並在 `figures.json.status` 設為 `complete`。

19. 回報本次寫出的 JSON、讀取過的預覽圖片、產生的 figure crops、通過/失敗的 figures，以及尚未解決的阻礙。第一階段不回報 parent canonical validator command / result。

# 格式

## JSON 命名與 enum

### Artifact root 相對路徑

- `artifact_root` 是 `<paper_dir>/lanes/figures/worker_output/worker_01/`。
- Figure-lane artifact paths 都必須相對於 `artifact_root`，不要把 worker output 目錄本身寫進 JSON。
- 適用欄位包含：`source_regions[].source_image`、`source_regions[].source_preview`、`crop_units[].image_file`、`crop_units[].preview`、`crop_units[].edge_previews.*`、`figure_decisions.json.evidence_read.source_region_previews`、`figures.json.evidence_read.final_crop_previews` 和 `figures.json.evidence_read.edge_previews`。
- Shared page paths 不屬於 figure-lane artifact，仍使用 paper-dir-relative path，例如 `shared/pages/page_3.png` 和 `shared/previews/page_3_preview.png`。
- 不要在 figure artifact path 裡寫 `lanes/figures/worker_output/worker_01/`、`lanes/figures/canonical/` 或絕對路徑。

正確寫法：

```json
{
  "source_image": "source_regions/p003_src001.png",
  "source_preview": "previews/p003_src001_preview.png",
  "image_file": "crops/Figure_1.png",
  "preview": "previews/Figure_1_preview.png"
}
```

### 版本與欄位命名

- 所有 JSON 都使用 `schema_version: "figure_extraction.v2"`。v2 schema 以本文件內的 JSON examples 與規則為準，不再引用舊版 `figure_schemas.md`。
- 裁切座標只叫 `crop_px`，不要寫成 `crop`、`crop_bbox` 或 `crop_region`。
- 最終裁切圖片路徑只叫 `image_file`，而且只放在 `crop_units[]` 裡。不要使用 `file`、`output_file`、`output_image`。
- `figure_id` 必須 filename-safe，不含空格，例如 `Figure_1`、`Figure_2`、`Extended_Data_Figure_1`。
- 單一 crop 圖片使用 `crops/<figure_id>.png`；多個 crop 統一使用 `crops/<figure_id>_part_<N>.png`。頁碼與位置由 `crop_units[].page` 和 `crop_units[].role` 表達，不塞進檔名。
- `pages` 欄位在不同階段的處理不同：
  - `figure_candidates.json`：每個 page object 有 `page`（單數）。
  - `figure_index.json`：figure 物件可以有 `pages: [...]`，因為此階段還沒有 `crop_units`。
  - `figure_decisions.json` 和 `figures.json`：頁碼由 `crop_units[].page` 表達（見下一條 derived field 禁令）。
- `figure_decisions.json` 和 `figures.json` 已經有 `crop_units`，figure 層不要再寫可由 `crop_units` 推得的彙總欄位，例如 `pages`、`image_files`、`crop_count`。
  - 頁碼讀 `crop_units[].page`
  - 圖檔路徑讀 `crop_units[].image_file`

### 可用 enum

- `region_type` 用於 `figure_candidates.json` 的 `regions[]`：`figure_visual`、`caption`、`body`、`header`、`footer`、`table`、`equation`、`separator`、`unknown`。
- `source` 用於 `figure_candidates.json` 的 `regions[].source`：`layout_detector`、`object_detector`、`pdf_text`、`ocr`、`geometry`、`model_visual`、`manual`。`source` 為 `model_visual` 或 `manual` 時，必須在該 region 的 `notes` 說明證據限制。
- `figure_type` 用於 `figure_index.json`、`figure_decisions.json`、`figures.json` 的 figure object：`main`、`extended`、`supplementary`、`other`。

### batch / assignment 對帳欄位

- `unexpected_labeled_figures` 寫在 `figure_candidates.json` 最外層，用來記錄有 figure label、但不該由本 worker 處理的 figure。
- `omitted_candidates` 寫在 `figure_index.json` 最外層，用來記錄已產生 candidate evidence、但最後不收進正式 figure index 的候選。
- 「有 label 但不該由本 worker 處理」進 `unexpected_labeled_figures`；「candidate 偵測有產出但 agent 判斷不是正式 figure」進 `omitted_candidates`。
- `unexpected_labeled_figures[]` 必填 `figure_label`、`page`、`reason`；`caption_text` 讀得到時必填，讀不到填 `null`。
- `omitted_candidates[]` 必填 `candidate_id`、`reason`。
- `notes` 條件性必填：`reason` 為自訂值、`caption_text` 為 `null`，或情況需要額外解釋時必填；其餘可省略。
- `reason` 採半開放：能歸類時優先用下面的建議值，否則自訂 snake_case。
  - `unexpected_labeled_figures.reason` 優先使用：`outside_assignment`、`unexpected_page`、`not_in_global_index`。`not_in_global_index` 只在本 worker 能讀到 global index 或 assignment list 時使用。
  - `omitted_candidates.reason` 優先使用：`not_a_figure`、`duplicate_of_other_candidate`、`table_misclassified`、`equation_misclassified`、`watermark_or_page_chrome`。
- 兩個欄位都必須存在，內容可為空陣列；空陣列代表 agent 檢查過、沒有這類情況。

### 其他欄位規則

- `crop_hint_px` 只出現在 `figure_candidates.json` 的 candidate 層，表示候選階段的裁切提示。
- `crop_px` 只出現在 `figure_decisions.json` 和 `figures.json` 的 `crop_units[]` 裡，表示已決定的最終裁切框。
- single-region 時，`crop_hint_px` 通常等於該 visual region 的 `bbox_px`；multi-region 時，`crop_hint_px` 可以是包住多個 visual regions 的 union 提示框。兩種情況下都不是 final crop。
- 不得直接把 `crop_hint_px` 當成 `crop_px`；最終 `crop_px` 必須經過 source context 檢查並寫入 `figure_decisions.json`。
- `expected_panels` 只能根據圖中實際可見的 panel label 或明確視覺結構填寫。不要因為 caption、cross-reference 或正文提到 `Panels A-D` 就自動發明 panel；如果 panel label 不清楚，應在 `notes` 或 `rationale` 說明。
- `role` 放在 `crop_units[]` 裡，用簡短文字說明該 crop 的角色，例如 `complete figure`、`left visual region`、`page 6 portion`。上述為範例，不是 enum；agent 可依實際結構自訂簡短描述。`role` 不表示 pass/fail，也不取代 `notes` 或 `rationale`。

## json 檔案 example

### figure_candidates.json

```json
{
  "schema_version": "figure_extraction.v2",
  "worker_id": "worker_01",
  "scope": {
    "pages": [3, 4],
    "notes": []
  },
  "pages": [
    {
      "page": 3,
      "page_image": "shared/pages/page_3.png",
      "page_preview": "shared/previews/page_3_preview.png",
      "page_size_px": [2475, 3150],
      "regions": [
        {
          "region_id": "p003_r001",
          "region_type": "figure_visual",
          "bbox_px": [120, 300, 2380, 1850],
          "source": "layout_detector",
          "confidence": 0.86,
          "text": null,
          "notes": []
        },
        {
          "region_id": "p003_r002",
          "region_type": "caption",
          "bbox_px": [120, 1880, 2380, 2050],
          "source": "pdf_text",
          "confidence": 0.94,
          "text": "Fig. 1. Short caption title...",
          "notes": []
        },
        {
          "region_id": "p003_r003",
          "region_type": "body",
          "bbox_px": [120, 2080, 2380, 2600],
          "source": "pdf_text",
          "confidence": 0.91,
          "text": "The results in Fig. 1 show...",
          "notes": []
        }
      ],
      "source_regions": [
        {
          "source_region_id": "p003_src001",
          "source_image": "source_regions/p003_src001.png",
          "source_preview": "previews/p003_src001_preview.png",
          "bbox_px": [90, 260, 2410, 2080],
          "candidate_ids": ["p003_c001"],
          "notes": ["包含 Fig. 1 的視覺區域、圖說邊界與附近正文。"]
        }
      ],
      "figure_candidates": [
        {
          "candidate_id": "p003_c001",
          "figure_label": "Fig. 1",
          "visual_region_ids": ["p003_r001"],
          "caption_region_ids": ["p003_r002"],
          "excluded_region_ids": ["p003_r002", "p003_r003"],
          "source_region_ids": ["p003_src001"],
          "crop_hint_px": {
            "page_3": [120, 300, 2380, 1850]
          },
          "confidence": 0.82,
          "risks": ["Large chart-like figure; verify bottom axis labels and side legend edges."]
        }
      ]
    },
    {
      "page": 4,
      "page_image": "shared/pages/page_4.png",
      "page_preview": "shared/previews/page_4_preview.png",
      "page_size_px": [2475, 3150],
      "regions": [
        {
          "region_id": "p004_r001",
          "region_type": "figure_visual",
          "bbox_px": [140, 420, 1080, 1260],
          "source": "model_visual",
          "confidence": 0.72,
          "text": null,
          "notes": ["從受限尺寸頁面預覽圖片找到的左側 panel 群。"]
        },
        {
          "region_id": "p004_r002",
          "region_type": "figure_visual",
          "bbox_px": [1320, 420, 2260, 1260],
          "source": "model_visual",
          "confidence": 0.72,
          "text": null,
          "notes": ["從受限尺寸頁面預覽圖片找到的右側 panel 群。"]
        },
        {
          "region_id": "p004_r003",
          "region_type": "caption",
          "bbox_px": [140, 1320, 2260, 1510],
          "source": "pdf_text",
          "confidence": 0.93,
          "text": "Fig. 2. Multi-region example caption...",
          "notes": []
        },
        {
          "region_id": "p004_r004",
          "region_type": "body",
          "bbox_px": [1090, 420, 1310, 1260],
          "source": "pdf_text",
          "confidence": 0.87,
          "text": "Body text between panel groups...",
          "notes": []
        }
      ],
      "source_regions": [
        {
          "source_region_id": "p004_src001",
          "source_image": "source_regions/p004_src001.png",
          "source_preview": "previews/p004_src001_preview.png",
          "bbox_px": [110, 380, 2290, 1530],
          "candidate_ids": ["p004_c001"],
          "notes": ["顯示兩個視覺區域、中間正文與圖說邊界。"]
        }
      ],
      "figure_candidates": [
        {
          "candidate_id": "p004_c001",
          "figure_label": "Fig. 2",
          "visual_region_ids": ["p004_r001", "p004_r002"],
          "caption_region_ids": ["p004_r003"],
          "excluded_region_ids": ["p004_r003", "p004_r004"],
          "source_region_ids": ["p004_src001"],
          "crop_hint_px": {
            "page_4": [140, 420, 2260, 1260]
          },
          "confidence": 0.68,
          "risks": ["A single rectangle would include body text between the two visual regions."]
        }
      ]
    }
  ],
  "unexpected_labeled_figures": [],
  "notes": []
}
```

### figure_index.json

> 註：`figure_index.json` 的 figure 層保留 `pages` 欄位，因為這個階段還沒有 `crop_units`。到了 `figure_decisions.json` 和 `figures.json`，頁碼改由 `crop_units[].page` 表達。

```json
{
  "schema_version": "figure_extraction.v2",
  "worker_id": "worker_01",
  "scope": {
    "pages": [3, 4]
  },
  "figures": [
    {
      "figure_id": "Figure_1",
      "figure_label": "Fig. 1",
      "figure_type": "main",
      "pages": [3],
      "candidate_ids": ["p003_c001"],
      "source_region_ids": ["p003_src001"],
      "caption_text": "Fig. 1. Short caption title...",
      "notes": []
    },
    {
      "figure_id": "Figure_2",
      "figure_label": "Fig. 2",
      "figure_type": "main",
      "pages": [4],
      "candidate_ids": ["p004_c001"],
      "source_region_ids": ["p004_src001"],
      "caption_text": "Fig. 2. Multi-region example caption...",
      "notes": ["The figure has two separated visual regions with body text between them."]
    }
  ],
  "omitted_candidates": [],
  "notes": []
}
```

### figure_decisions.json

```json
{
  "schema_version": "figure_extraction.v2",
  "worker_id": "worker_01",
  "figures": [
    {
      "figure_id": "Figure_1",
      "figure_label": "Fig. 1",
      "figure_type": "main",
      "candidate_ids": ["p003_c001"],
      "source_region_ids": ["p003_src001"],
      "visual_region_ids": ["p003_r001"],
      "caption_region_ids": ["p003_r002"],
      "excluded_region_ids": ["p003_r002", "p003_r003"],
      "evidence_read": {
        "page_previews": ["shared/previews/page_3_preview.png"],
        "source_region_previews": ["previews/p003_src001_preview.png"]
      },
      "caption_text": "Fig. 1. Short caption title...",
      "expected_panels": ["A", "B", "C"],
      "crop_units": [
        {
          "crop_id": "Figure_1",
          "page": 3,
          "crop_px": [120, 300, 2380, 1850],
          "image_file": "crops/Figure_1.png",
          "preview": "previews/Figure_1_preview.png",
          "edge_previews": {
            "top": "previews/Figure_1_top_preview.png",
            "bottom": "previews/Figure_1_bottom_preview.png",
            "left": "previews/Figure_1_left_preview.png",
            "right": "previews/Figure_1_right_preview.png"
          },
          "role": "complete figure"
        }
      ],
      "exclusions": ["caption below crop", "body text below caption", "journal page header"],
      "rationale": "Crop follows visual region p003_r001 in page coordinates. External caption p003_r002 is stored in caption_text and excluded from the image."
    },
    {
      "figure_id": "Figure_2",
      "figure_label": "Fig. 2",
      "figure_type": "main",
      "candidate_ids": ["p004_c001"],
      "source_region_ids": ["p004_src001"],
      "visual_region_ids": ["p004_r001", "p004_r002"],
      "caption_region_ids": ["p004_r003"],
      "excluded_region_ids": ["p004_r003", "p004_r004"],
      "evidence_read": {
        "page_previews": ["shared/previews/page_4_preview.png"],
        "source_region_previews": ["previews/p004_src001_preview.png"]
      },
      "caption_text": "Fig. 2. Multi-region example caption...",
      "expected_panels": ["A", "B"],
      "crop_units": [
        {
          "crop_id": "Figure_2_part_1",
          "page": 4,
          "crop_px": [140, 420, 1080, 1260],
          "image_file": "crops/Figure_2_part_1.png",
          "preview": "previews/Figure_2_part_1_preview.png",
          "edge_previews": {
            "top": "previews/Figure_2_part_1_top_preview.png",
            "bottom": "previews/Figure_2_part_1_bottom_preview.png",
            "left": "previews/Figure_2_part_1_left_preview.png",
            "right": "previews/Figure_2_part_1_right_preview.png"
          },
          "role": "left visual region"
        },
        {
          "crop_id": "Figure_2_part_2",
          "page": 4,
          "crop_px": [1320, 420, 2260, 1260],
          "image_file": "crops/Figure_2_part_2.png",
          "preview": "previews/Figure_2_part_2_preview.png",
          "edge_previews": {
            "top": "previews/Figure_2_part_2_top_preview.png",
            "bottom": "previews/Figure_2_part_2_bottom_preview.png",
            "left": "previews/Figure_2_part_2_left_preview.png",
            "right": "previews/Figure_2_part_2_right_preview.png"
          },
          "role": "right visual region"
        }
      ],
      "exclusions": ["caption below both regions", "body text between separated visual regions"],
      "rationale": "A single rectangle would include non-figure body text p004_r004, so Fig. 2 is represented by two crop units that share one figure_id."
    }
  ],
  "notes": []
}
```

### figures.json

```json
{
  "schema_version": "figure_extraction.v2",
  "worker_id": "worker_01",
  "status": "incomplete",
  "figures": [
    {
      "figure_id": "Figure_1",
      "figure_label": "Fig. 1",
      "figure_type": "main",
      "candidate_ids": ["p003_c001"],
      "source_region_ids": ["p003_src001"],
      "caption_text": "Fig. 1. Short caption title...",
      "crop_units": [
        {
          "crop_id": "Figure_1",
          "page": 3,
          "crop_px": [120, 300, 2380, 1850],
          "image_file": "crops/Figure_1.png",
          "preview": "previews/Figure_1_preview.png",
          "edge_previews": {
            "top": "previews/Figure_1_top_preview.png",
            "bottom": "previews/Figure_1_bottom_preview.png",
            "left": "previews/Figure_1_left_preview.png",
            "right": "previews/Figure_1_right_preview.png"
          },
          "role": "complete figure"
        }
      ],
      "evidence_read": {
        "final_crop_previews": ["previews/Figure_1_preview.png"],
        "edge_previews": [
          "previews/Figure_1_top_preview.png",
          "previews/Figure_1_bottom_preview.png",
          "previews/Figure_1_left_preview.png",
          "previews/Figure_1_right_preview.png"
        ]
      },
      "verification": {
        "source_context_checked": "pass",
        "final_crop_checked": "pass",
        "edge_previews_checked": "pass",
        "figure_content_complete": "pass",
        "external_caption_excluded": "pass",
        "page_chrome_excluded": "pass",
        "no_adjacent_content": "pass",
        "result": "pass"
      },
      "notes": []
    },
    {
      "figure_id": "Figure_2",
      "figure_label": "Fig. 2",
      "figure_type": "main",
      "candidate_ids": ["p004_c001"],
      "source_region_ids": ["p004_src001"],
      "caption_text": "Fig. 2. Multi-region example caption...",
      "crop_units": [
        {
          "crop_id": "Figure_2_part_1",
          "page": 4,
          "crop_px": [140, 420, 1080, 1260],
          "image_file": "crops/Figure_2_part_1.png",
          "preview": "previews/Figure_2_part_1_preview.png",
          "edge_previews": {
            "top": "previews/Figure_2_part_1_top_preview.png",
            "bottom": "previews/Figure_2_part_1_bottom_preview.png",
            "left": "previews/Figure_2_part_1_left_preview.png",
            "right": "previews/Figure_2_part_1_right_preview.png"
          },
          "role": "left visual region"
        },
        {
          "crop_id": "Figure_2_part_2",
          "page": 4,
          "crop_px": [1320, 420, 2260, 1260],
          "image_file": "crops/Figure_2_part_2.png",
          "preview": "previews/Figure_2_part_2_preview.png",
          "edge_previews": {
            "top": "previews/Figure_2_part_2_top_preview.png",
            "bottom": "previews/Figure_2_part_2_bottom_preview.png",
            "left": "previews/Figure_2_part_2_left_preview.png",
            "right": "previews/Figure_2_part_2_right_preview.png"
          },
          "role": "right visual region"
        }
      ],
      "evidence_read": {
        "final_crop_previews": [
          "previews/Figure_2_part_1_preview.png",
          "previews/Figure_2_part_2_preview.png"
        ],
        "edge_previews": [
          "previews/Figure_2_part_1_top_preview.png",
          "previews/Figure_2_part_1_bottom_preview.png",
          "previews/Figure_2_part_1_left_preview.png",
          "previews/Figure_2_part_1_right_preview.png",
          "previews/Figure_2_part_2_top_preview.png",
          "previews/Figure_2_part_2_bottom_preview.png",
          "previews/Figure_2_part_2_left_preview.png",
          "previews/Figure_2_part_2_right_preview.png"
        ]
      },
      "verification": {
        "source_context_checked": "pass",
        "final_crop_checked": "fail",
        "edge_previews_checked": "pass",
        "figure_content_complete": "fail",
        "external_caption_excluded": "pass",
        "page_chrome_excluded": "pass",
        "no_adjacent_content": "pass",
        "result": "fail"
      },
      "notes": ["Right visual region crop appears to cut off the panel B x-axis label; extraction is incomplete until repaired."]
    }
  ],
  "notes": ["只要任何 figure 的 verification.result 是 fail，就表示本次輸出尚未成功；失敗的 figure 仍會被記錄，方便追蹤與後續 repair。"]
}
```

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
  - 角色：根據 `figure_decisions.json` 從頁面圖片裁出的成果本體。
- 邊界圖片：`edges/Figure_1_top.png`
  - 預覽：`previews/Figure_1_top_preview.png`
  - 角色：從頁面圖片裁出跨越 crop boundary 的條帶，同時顯示 crop 內側和外側，並在 boundary 位置疊一條紅線。用來檢查邊界是否切掉 figure 內容或混入非 figure 內容。紅線讓 agent 一眼看出 figure content 是否跨越 crop boundary。

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
- 每個 preview 都必須有對應原檔：頁面預覽來自頁面圖片，裁切區域來源預覽來自裁切區域來源圖片，最終裁切預覽來自最終裁切圖片，邊界預覽來自邊界圖片。邊界圖片從頁面圖片裁出（不是從最終裁切圖片）。
- agent 讀取單張圖片時，圖片兩邊都不得超過 1600 px。
- agent 一次讀多張圖片時，每張圖片兩邊都不得超過 1400 px，且批次要小。
- 不要直接讀超過限制的頁面圖片、裁切區域來源圖片、最終裁切圖片或邊界圖片。

## 座標規則

- 所有寫入 JSON 的 `bbox_px`、`crop_hint_px`、`crop_px` 都使用完整解析度頁面圖片的 pixel coordinate。
- 裁切區域來源圖片只用來產生和檢查裁切區域來源預覽，不是最終裁切座標的真相。
- 若從裁切區域來源預覽判斷邊界，必須換回頁面圖片座標後，再寫入 `figure_decisions.json`。
- 最終裁切永遠根據 `figure_decisions.json` 從頁面圖片裁出，不要從裁切區域來源圖片或其他中間圖片再裁一次。
- 座標換算時，邊界應保守外擴：左上角向外取整，右下角向外取整，再用邊界預覽收緊。

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
- 輔助工具輸出只能當作 candidate evidence，不是 final truth。`pass` 必須由 agent 讀過 source context、final crop preview 和 edge previews 後判斷。

### `verification` 三個欄位

- `verification.source_context_checked`、`verification.final_crop_checked`、`verification.edge_previews_checked` 都寫在 `figures.json.verification` 物件內。
- `verification.source_context_checked` 代表 agent 已讀過預覽頁面圖片或預覽裁切區域來源圖片，用來決定 figure 成員與裁切決策。
- `verification.final_crop_checked` 代表 agent 已讀過預覽最終裁切圖片，用來檢查裁切成果本體。
- `verification.edge_previews_checked` 代表 agent 已讀過四個邊界預覽，用來檢查邊界是否過緊、過鬆或混入非 figure 內容。
- 每個標成 `pass` 的 figure，都必須讀過來源上下文預覽、最終裁切預覽，以及上、下、左、右四個邊界預覽。

### Pass/fail 語意

- `verification` 只使用 `pass` 或 `fail`。不要使用 `not_applicable`；沒有某種元素時，只要沒有缺失或截斷，該檢查就是 `pass`。
- `figures.json` 可以記錄 `fail`，但只要任何 figure 的 `verification.result` 是 `fail`，整個 `status` 就必須是 `incomplete`。
- 失敗的 figure 被記錄是為了 trace 與後續 repair，不代表 extraction 成功。

### 高頻失敗模式

- 不要把整頁、整欄或大頁面條帶當成 figure crop。
- 不要把外部 caption、頁眉、頁腳、頁碼、浮水印或其他 page chrome 裁進 figure。
- 不要切掉座標軸、圖例、比例尺、panel label、color bar 或其他 figure 內容。
- 不要把輔助工具產生的 bbox 當成最終裁切真相。
- 不要在沒有讀 source context preview、final crop preview 和四個 edge previews 的情況下標 `pass`。
- 圖表型圖片（折線圖、長條圖、散點圖、熱圖、Manhattan plot、帶座標軸的示意圖）的底邊與側邊風險最高，必須檢查 x 軸刻度與標題、y 軸標籤、圖例、color bar 和 plot boundary 是否完整。

## 閱讀證據紀錄（evidence_read）

source context 是裁切決策前讀取的 evidence，所以記在 `figure_decisions.json.evidence_read`；final crop 與 edge preview 是裁切後讀取的 evidence，所以記在 `figures.json.evidence_read`。

- `figure_decisions.json` 的 `evidence_read` 記錄 source context 階段讀過的 preview，例如 `page_previews`、`source_region_previews`。
- `figures.json` 的 `evidence_read` 記錄 final verification 階段讀過的 preview，例如 `final_crop_previews`、`edge_previews`。
- 任何標成 `pass` 的視覺檢查，都必須能在 `evidence_read` 找到對應 preview：
  - `source_context_checked = "pass"` 時，必須能在 `figure_decisions.json.evidence_read.page_previews` 或 `source_region_previews` 找到對應條目。
  - `final_crop_checked = "pass"` 時，必須能在 `figures.json.evidence_read.final_crop_previews` 找到對應條目。
  - `edge_previews_checked = "pass"` 時，必須能在 `figures.json.evidence_read.edge_previews` 找到對應條目。
  - 沒有對應 evidence 時，不得標 `pass`。

## 機械自檢

寫出/更新 `figures.json` 草稿後、回報成功前，先做 mechanical self-check。self-check 至少確認：
- 每個 figure-lane artifact path 都是 artifact root 相對路徑，不含 `worker_output/`、`canonical/` 或 absolute path。
- 以 `artifact_root` resolve 後，每個 `crop_units[].image_file` 實際存在。
- 每個 `crop_px` 都在對應頁面尺寸範圍內。
- `figures.json` 的 `crop_units` 和 `figure_decisions.json` 對應 figure 的 `crop_units` 完全一致。
- 每張 final crop 都有 final crop preview 和四個 edge previews。
- `figure_candidates.json` 最外層必須有 `unexpected_labeled_figures`，`figure_index.json` 最外層必須有 `omitted_candidates`；兩者都可以是空陣列。
- figure 層不出現可由 `crop_units` 推得的彙總欄位（規則見「JSON 命名與 enum」段的「版本與欄位命名」）。
- self-check 失敗時，必須修正 artifact 後重檢；不能把壞 manifest 寫成成功。
- self-check 通過不代表視覺驗證通過。視覺驗證仍然必須讀圖判斷。

## 空範圍

如果指定範圍中沒有有標記 figure：
- `figure_candidates.json` 的 `pages` 仍要記錄已掃描頁面，`figure_candidates` 為空。
- `figure_index.json`、`figure_decisions.json`、`figures.json` 的 `figures` 為空。
- `figures.json.status` 設為 `complete`。
