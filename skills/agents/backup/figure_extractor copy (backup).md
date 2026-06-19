# 目標

這是一份給 figure_extractor agent 看的指引

此流程使用場景與目標：
- 輸入：一個 pdf 檔案、pages 範圍、rendered pages
- 輸出位置：`<paper_dir>/lanes/figures/worker_output/worker_01/`
- 輸出：
    - `figure_candidates.json`：記錄每頁疑似圖表的候選視覺區域、圖說候選、附近文字、頁面固定元素、裁切區域來源圖片與候選裁切範圍。這是候選證據，不是最終圖表清單。
    - `figure_index.json`：從候選項中選出的正式有標記圖表索引，記錄 figure id/label、頁碼、對應候選區域、圖說來源與是否需要合併多個區域。
    - `figure_decisions.json`：在最終裁切前寫出的裁切決策，記錄每張圖的最終裁切框、輸出檔、排除項目與決策理由。最終裁切必須以此檔案為依據。
    - `figures.json`：視覺驗證後的最終成果清單，記錄最終裁切圖路徑、頁碼、裁切框、圖說文字或來源、預覽圖、邊界預覽與驗證結果。此檔可以記錄失敗的 figure；只要任何 figure fail，本次 figure extraction 就尚未完成。
    - `source_regions/`：完整解析度裁切區域來源圖片，用來產生預覽裁切區域來源圖片。
    - `edges/`：完整解析度裁切區域邊界圖片，用來產生邊界預覽。
    - `previews/`：所有給 agent 讀取的預覽圖片，檔名必須包含 `_preview`。
    - `figureXX.png` (figure crops，即完整解析度最終裁切圖片)

- 目標：讓 `figureXX.png` 準確的包含 figure 的上下左右邊緣 (不要把 figure 的任何部分切掉，但同時要盡可能裁掉非 figure 的部分)。
- 邊界：此 agent 只負責 initial extraction，不負責 reviewer、repair、canonical merge 或 validator，也不要修改來源 PDF。

# 流程

## 工作流程

1. 確保完整解析度頁面圖片存在；若不存在，回報缺失，讓上游流程從輸入 PDF 轉出完整解析度頁面圖片。完整解析度頁面圖片是判斷原始論文版面的最高依據，也是最終裁切來源與所有 JSON 座標的基準。

2. 根據完整解析度頁面圖片建立有邊界限制的預覽頁面圖片。agent 讀圖時應讀預覽圖片，不直接讀超過尺寸限制的完整解析度頁面圖片。

3. 產生 `figure_candidates.json`，將疑似圖表的視覺區域與可能的圖說候選項目建立關聯。候選項目應保留頁碼、候選區域座標、可能的 figure label、圖說候選、附近文字，以及任何可能需要排除的頁眉、頁腳、頁碼或正文區塊。每個 figure candidate 必須有視覺區域證據，不能只根據圖說位置決定。

4. 根據 `figure_candidates.json` 建立完整解析度裁切區域來源圖片與其預覽裁切區域來源圖片。裁切區域來源圖片應包含候選視覺區域、可能的圖說，以及足以判斷邊界與排除干擾內容的周邊上下文；它不是最終裁切成果，也不是最終裁切座標的真相。

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

8. 在執行任何最終裁切之前，撰寫 `figure_decisions.json`。此檔案是最終裁切的唯一依據，所有 `crop_px` 都必須是完整解析度頁面圖片的 pixel coordinate。每張圖應記錄：
   - figure label
   - 頁碼
   - 使用的候選區域與裁切區域來源圖片
   - 最終裁切框座標
   - 輸出檔
   - 要排除的文字或頁面元素
   - 是否需要多個 crop units
   - 決策理由或備註

9. 根據 `figure_decisions.json`，使用共用裁切輔助工具，從完整解析度頁面圖片產生完整解析度最終裁切圖片。不要從裁切區域來源圖片、預覽圖片或其他中間圖片再裁一次。

10. 為每張完整解析度最終裁切圖片建立預覽最終裁切圖片。

11. 為每張完整解析度最終裁切圖片建立四個邊界預覽，包括：上邊界、下邊界、左邊界、右邊界。

12. 讀取每張預覽最終裁切圖片與其四個邊界預覽。此步驟是 final crop + edge previews 檢查，用來驗證已產生的裁切圖片是否可接受。逐一確認：
   - 最終裁切圖片中的 figure 內容是否完整
   - 上、下、左、右邊界是否過緊或過鬆
   - 圖內標籤、座標軸、圖例、比例尺、panel label 或 color bar 是否被截斷
   - 外部圖說是否被誤納入，或應保留的圖內文字是否被切掉
   - 是否仍包含正文、頁碼、頁眉、頁腳或其他頁面固定元素
   - 是否誤切到相鄰圖表或相鄰文字

13. 如果任何裁切結果不正確，不得直接修改最終圖片。必須先更新 `figure_decisions.json`，再重新執行裁切，重新建立預覽最終裁切圖片與四個邊界預覽，並再次檢查。

14. 視覺檢查後撰寫 `figures.json`。`figures.json` 可以記錄 `verification.result = "fail"` 的 figure；但只要任何 figure 是 fail，`figures.json.status` 就必須是 `incomplete`，不得宣稱此次 figure extraction 成功。

15. `figures.json` 應列出目前確認的圖表成果，包含：
   - figure label
   - 最終裁切圖片路徑
   - 對應頁碼
   - 裁切框座標
   - 圖說文字或圖說來源
   - 對應的預覽圖與邊界預覽
   - 對應的 `figure_decisions.json` 決策項目
   - 視覺驗證結果

16. 若指定範圍中沒有有標記 figure，仍要寫出四個 JSON，`figures` 為空，並在 `figures.json.status` 設為 `complete`。

17. 回報本次寫出的 JSON、讀取過的預覽圖片、產生的 figure crops、通過/失敗的 figures，以及尚未解決的阻礙。

# 格式

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
          "source_image": "lanes/figures/worker_output/worker_01/source_regions/p003_src001.png",
          "source_preview": "lanes/figures/worker_output/worker_01/previews/p003_src001_preview.png",
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
          "source_image": "lanes/figures/worker_output/worker_01/source_regions/p004_src001.png",
          "source_preview": "lanes/figures/worker_output/worker_01/previews/p004_src001_preview.png",
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
      "crop_plan": "single_region",
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
      "crop_plan": "multi_region",
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
      "pages": [3],
      "candidate_ids": ["p003_c001"],
      "source_region_ids": ["p003_src001"],
      "visual_region_ids": ["p003_r001"],
      "caption_region_ids": ["p003_r002"],
      "excluded_region_ids": ["p003_r002", "p003_r003"],
      "evidence_read": {
        "page_previews": ["shared/previews/page_3_preview.png"],
        "source_region_previews": ["lanes/figures/worker_output/worker_01/previews/p003_src001_preview.png"]
      },
      "caption_text": "Fig. 1. Short caption title...",
      "include_external_caption_in_crop": false,
      "expected_panels": ["A", "B", "C"],
      "crop_units": [
        {
          "crop_id": "Figure_1",
          "page": 3,
          "crop_px": [120, 300, 2380, 1850],
          "output_image": "lanes/figures/worker_output/worker_01/Figure_1.png",
          "role": "complete figure"
        }
      ],
      "exclusions": ["caption below crop", "body text below caption", "journal page header"],
      "decision_status": "ready_to_crop",
      "rationale": "Crop follows visual region p003_r001 in page coordinates. External caption p003_r002 is stored in caption_text and excluded from the image."
    },
    {
      "figure_id": "Figure_2",
      "figure_label": "Fig. 2",
      "figure_type": "main",
      "pages": [4],
      "candidate_ids": ["p004_c001"],
      "source_region_ids": ["p004_src001"],
      "visual_region_ids": ["p004_r001", "p004_r002"],
      "caption_region_ids": ["p004_r003"],
      "excluded_region_ids": ["p004_r003", "p004_r004"],
      "evidence_read": {
        "page_previews": ["shared/previews/page_4_preview.png"],
        "source_region_previews": ["lanes/figures/worker_output/worker_01/previews/p004_src001_preview.png"]
      },
      "caption_text": "Fig. 2. Multi-region example caption...",
      "include_external_caption_in_crop": false,
      "expected_panels": ["A", "B"],
      "crop_units": [
        {
          "crop_id": "Figure_2_part_1",
          "page": 4,
          "crop_px": [140, 420, 1080, 1260],
          "output_image": "lanes/figures/worker_output/worker_01/Figure_2_part_1.png",
          "role": "left visual region"
        },
        {
          "crop_id": "Figure_2_part_2",
          "page": 4,
          "crop_px": [1320, 420, 2260, 1260],
          "output_image": "lanes/figures/worker_output/worker_01/Figure_2_part_2.png",
          "role": "right visual region"
        }
      ],
      "exclusions": ["caption below both regions", "body text between separated visual regions"],
      "decision_status": "ready_to_crop",
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
      "pages": [3],
      "candidate_ids": ["p003_c001"],
      "source_region_ids": ["p003_src001"],
      "image_files": ["lanes/figures/worker_output/worker_01/Figure_1.png"],
      "caption_text": "Fig. 1. Short caption title...",
      "crop_units": [
        {
          "crop_id": "Figure_1",
          "page": 3,
          "crop_px": [120, 300, 2380, 1850],
          "image_file": "lanes/figures/worker_output/worker_01/Figure_1.png",
          "preview": "lanes/figures/worker_output/worker_01/previews/Figure_1_preview.png",
          "edge_previews": {
            "top": "lanes/figures/worker_output/worker_01/previews/Figure_1_top_preview.png",
            "bottom": "lanes/figures/worker_output/worker_01/previews/Figure_1_bottom_preview.png",
            "left": "lanes/figures/worker_output/worker_01/previews/Figure_1_left_preview.png",
            "right": "lanes/figures/worker_output/worker_01/previews/Figure_1_right_preview.png"
          },
          "role": "complete figure"
        }
      ],
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
      "pages": [4],
      "candidate_ids": ["p004_c001"],
      "source_region_ids": ["p004_src001"],
      "image_files": [
        "lanes/figures/worker_output/worker_01/Figure_2_part_1.png",
        "lanes/figures/worker_output/worker_01/Figure_2_part_2.png"
      ],
      "caption_text": "Fig. 2. Multi-region example caption...",
      "crop_units": [
        {
          "crop_id": "Figure_2_part_1",
          "page": 4,
          "crop_px": [140, 420, 1080, 1260],
          "image_file": "lanes/figures/worker_output/worker_01/Figure_2_part_1.png",
          "preview": "lanes/figures/worker_output/worker_01/previews/Figure_2_part_1_preview.png",
          "edge_previews": {
            "top": "lanes/figures/worker_output/worker_01/previews/Figure_2_part_1_top_preview.png",
            "bottom": "lanes/figures/worker_output/worker_01/previews/Figure_2_part_1_bottom_preview.png",
            "left": "lanes/figures/worker_output/worker_01/previews/Figure_2_part_1_left_preview.png",
            "right": "lanes/figures/worker_output/worker_01/previews/Figure_2_part_1_right_preview.png"
          },
          "role": "left visual region"
        },
        {
          "crop_id": "Figure_2_part_2",
          "page": 4,
          "crop_px": [1320, 420, 2260, 1260],
          "image_file": "lanes/figures/worker_output/worker_01/Figure_2_part_2.png",
          "preview": "lanes/figures/worker_output/worker_01/previews/Figure_2_part_2_preview.png",
          "edge_previews": {
            "top": "lanes/figures/worker_output/worker_01/previews/Figure_2_part_2_top_preview.png",
            "bottom": "lanes/figures/worker_output/worker_01/previews/Figure_2_part_2_bottom_preview.png",
            "left": "lanes/figures/worker_output/worker_01/previews/Figure_2_part_2_left_preview.png",
            "right": "lanes/figures/worker_output/worker_01/previews/Figure_2_part_2_right_preview.png"
          },
          "role": "right visual region"
        }
      ],
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

本文件只使用下面這組圖片名稱。檔名含有 `_preview` 的圖片，才是給 agent 讀的預覽圖片；沒有 `_preview` 的圖片是完整解析度原檔或工作中間檔。

- 頁面圖片：`shared/pages/page_3.png`
  - 預覽：`shared/previews/page_3_preview.png`
  - 角色：原始頁面版面的最高依據，也是最終裁切來源。
- 裁切區域來源圖片：`lanes/figures/worker_output/worker_01/source_regions/p003_src001.png`
  - 預覽：`lanes/figures/worker_output/worker_01/previews/p003_src001_preview.png`
  - 角色：檢查候選 figure、圖說邊界與周邊干擾內容；不是最終裁切成果。
- 最終裁切圖片：`lanes/figures/worker_output/worker_01/Figure_1.png`
  - 預覽：`lanes/figures/worker_output/worker_01/previews/Figure_1_preview.png`
  - 角色：根據 `figure_decisions.json` 從頁面圖片裁出的成果本體。
- 邊界圖片：`lanes/figures/worker_output/worker_01/edges/Figure_1_top.png`
  - 預覽：`lanes/figures/worker_output/worker_01/previews/Figure_1_top_preview.png`
  - 角色：檢查上、下、左、右邊界是否切掉 figure 內容或混入非 figure 內容。

# 規則

## 權責

- `figure_extractor` 只做 initial extraction。
- 不寫 canonical 成果、review 成果、repair 成果或 validation reports。
- 不修改來源 PDF。
- 不讓外層協調器從部分裁切輸出回填 `figures.json`；`figures.json` 必須來自本 agent 寫出的裁切決策與視覺檢查。

## 圖片與讀取限制

- 每個 preview 都必須有對應原檔：頁面預覽來自頁面圖片，裁切區域來源預覽來自裁切區域來源圖片，最終裁切預覽來自最終裁切圖片，邊界預覽來自邊界圖片。
- agent 讀取單張圖片時，圖片兩邊都不得超過 1600 px。
- agent 一次讀多張圖片時，每張圖片兩邊都不得超過 1400 px，且批次要小。
- 不要直接讀超過限制的頁面圖片、裁切區域來源圖片、最終裁切圖片或邊界圖片。

## 座標規則

- 所有寫入 JSON 的 `bbox_px`、`crop_hint_px`、`crop_px` 都使用完整解析度頁面圖片的 pixel coordinate。
- 裁切區域來源圖片只用來產生和檢查裁切區域來源預覽，不是最終裁切座標的真相。
- 若從裁切區域來源預覽判斷邊界，必須換回頁面圖片座標後，再寫入 `figure_decisions.json`。
- 最終裁切永遠根據 `figure_decisions.json` 從頁面圖片裁出，不要從裁切區域來源圖片或其他中間圖片再裁一次。
- 座標換算時，邊界應保守外擴：左上角向外取整，右下角向外取整，再用邊界預覽收緊。

## 圖說與圖片邊界

- 外部圖說永遠不放進最終裁切圖片，只存入 `caption_text`。
- 圖內嵌入的文字屬於 figure 內容，應保留在 crop 中，例如圖內標籤、圖內標題、圖例、座標軸標籤、比例尺、panel label、color bar、圖內短說明文字。
- 若某段文字是否屬於 figure 內部不確定，必須在 `rationale` 或 `notes` 說明，且不能把不確定的裁切標成 `pass`。
- 應排除正文、外部圖說、頁碼、頁眉、頁腳、期刊固定元素、浮水印、相鄰圖表、table、equation 與其他非 figure 內容。

## 跨頁與多區域 figure

- 多 panel figure 預設視為同一張 figure，除非原文明確標成不同 figures。
- 跨頁 figure 可以有多個 `crop_units` 和多個 `image_files`，並用同一個 `figure_id` 關聯。
- 同頁多區域 figure 也可以有多個 `crop_units` 和多個 `image_files`。
- 不要為了做成單一矩形，而把中間正文或其他非 figure 內容一起裁進來。
- 多個 `crop_units` 必須同時出現在 `figure_decisions.json` 和 `figures.json`，並共用同一個 `figure_id`。

## 視覺驗證

- 程式碼、OCR、PDF 文字、版面偵測器、尺寸、座標和 validator 都不能單獨證明裁切品質。
- 每個標成 `pass` 的 figure，都必須讀過來源上下文預覽、最終裁切預覽，以及上、下、左、右四個邊界預覽。
- 圖表型圖片的底邊與側邊風險最高，例如折線圖、長條圖、散點圖、熱圖、Manhattan plot、帶座標軸的示意圖。必須檢查 x 軸刻度與標題、y 軸標籤、圖例、color bar 和 plot boundary 是否完整。
- `verification` 只使用 `pass` 或 `fail`。不要使用 `not_applicable`；沒有某種元素時，只要沒有缺失或截斷，該檢查就是 `pass`。
- `figures.json` 可以記錄 `fail`，但只要任何 figure 的 `verification.result` 是 `fail`，整個 `status` 就必須是 `incomplete`。
- 失敗的 figure 被記錄是為了 trace 與後續 repair，不代表 extraction 成功。

## 空範圍

如果指定範圍中沒有有標記 figure：
- `figure_candidates.json` 的 `pages` 仍要記錄已掃描頁面，`figure_candidates` 為空。
- `figure_index.json`、`figure_decisions.json`、`figures.json` 的 `figures` 為空。
- `figures.json.status` 設為 `complete`。
