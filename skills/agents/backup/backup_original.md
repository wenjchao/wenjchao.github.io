# 目標
這是一份給 figure_extractor agent 看的指引

此流程使用場景與目標：
- 輸入：一個 pdf 檔案、pages 範圍、rendered pages
- 輸出：
    - `figure_candidates.json`：記錄每頁疑似圖表的候選視覺區域、圖說候選、附近文字、頁面固定元素與候選裁切範圍。這是候選證據，不是最終圖表清單。
    - `figure_index.json`：從候選項中選出的正式有標記圖表索引，記錄 figure id/label、頁碼、對應候選區域、圖說來源與是否需要合併多個區域。
    - `figure_decisions.json`：在最終裁切前寫出的裁切決策，記錄每張圖的最終裁切框、輸出檔、排除項目與決策理由。最終裁切必須以此檔案為依據。
    - `figures.json`：通過視覺驗證後的最終成果清單，記錄最終裁切圖路徑、頁碼、裁切框、圖說文字或來源、預覽圖、邊界預覽與驗證結果。
    - `figureXX.png` (figure crops，即完整解析度最終裁切圖片)
    - `figureXX_top.png, figureXX_bottom.png, figureXX_left.png, figureXX_right.png` (edge previews，即最終裁切圖片的邊界預覽)

- 目標：讓 `figureXX.png` 準確的包含 figure 的上下左右邊緣 (不要把 figure 的任何部分切掉，但同時要盡可能裁掉非 figure 的部分)。

# 流程

## 工作流程

1. 確保完整解析度頁面圖片存在；若不存在，必須先從輸入 PDF 轉出完整解析度頁面圖片。完整解析度頁面圖片是判斷原始論文版面的最高依據。

2. 根據完整解析度頁面圖片建立有邊界限制的預覽頁面圖片。

3. 產生 `figure_candidates.json`，將疑似圖表的視覺區域與可能的圖說候選項目建立關聯。候選項目應保留頁碼、候選區域座標、可能的 figure label、圖說候選、附近文字，以及任何可能需要排除的頁眉、頁腳、頁碼或正文區塊。

4. 根據 `figure_candidates.json` 建立完整解析度裁切區域來源圖片與其預覽裁切區域來源圖片。裁切區域來源圖片應包含候選視覺區域、可能的圖說，以及足以判斷邊界與排除干擾內容的周邊上下文；它不是最終裁切成果。

5. 讀取 `figure_candidates.json`、預覽頁面圖片，以及預覽裁切區域來源圖片，用來判斷哪些候選區域應被選為正式圖表，並為後續撰寫 `figure_index.json` 做準備。

6. 根據候選結果撰寫 `figure_index.json`，列出本次要擷取的所有已標記圖表。每個項目應至少包含：
   - figure label，例如 `Figure 1`、`Fig. 2`、`Extended Data Fig. 1`
   - 所在頁碼
   - 對應的候選區域 id
   - 圖說候選 id
   - 是否需要合併多個視覺區域
   - 是否需要排除頁眉、頁腳、欄位文字、頁碼或其他頁面固定元素

7. 針對 `figure_index.json` 中的每一張圖，檢查預覽頁面圖片與預覽裁切區域來源圖片。此步驟是候選/source context 檢查，用來決定圖表成員與裁切決策，不是驗證最終裁切成果。確認：
   - 候選視覺區域確實屬於該 figure label
   - 圖的主要視覺內容、圖說候選、附近正文與頁面固定元素都在可判斷的上下文中
   - 圖說邊界與外部正文邊界可被辨識
   - 後續裁切應排除的正文、頁碼、頁眉、頁腳、欄線、其他圖表或頁面邊界已被標記
   - 若圖跨欄、跨頁或由多個 panel 組成，所有必要候選區域都有被納入裁切決策

8. 在執行任何最終裁切之前，撰寫 `figure_decisions.json`。此檔案是最終裁切的唯一依據，應記錄每張圖的：
   - figure label
   - 頁碼
   - 使用的裁切區域來源圖片
   - 最終裁切框座標
   - 圖說是否納入裁切
   - 要排除的文字或頁面元素
   - 是否需要合併多個區域
   - 決策理由或備註

9. 根據 `figure_decisions.json`，使用共用裁切輔助工具產生完整解析度最終裁切圖片。

10. 為每張完整解析度最終裁切圖片建立預覽最終裁切圖片。

11. 為每張完整解析度最終裁切圖片建立四個預覽裁切區域邊界圖片，包括：
   - 上邊界
   - 下邊界
   - 左邊界
   - 右邊界

12. 讀取每張預覽最終裁切圖片與其四個邊界預覽。此步驟是 final crop + edge previews 檢查，用來驗證已產生的裁切圖片是否可接受。逐一確認：
   - 最終裁切圖片中的 figure 內容是否完整
   - 上、下、左、右邊界是否過緊或過鬆
   - 圖內標籤、座標軸、圖例、比例尺、panel label 或 color bar 是否被截斷
   - 外部圖說是否被誤納入，或應保留的圖內文字是否被切掉
   - 是否仍包含正文、頁碼、頁眉、頁腳或其他頁面固定元素
   - 是否誤切到相鄰圖表或相鄰文字

13. 如果任何裁切結果不正確，不得直接修改最終圖片。必須先更新 `figure_decisions.json`，再重新執行裁切，重新建立預覽最終裁切圖片與四個邊界預覽，並再次檢查。

14. 只有在所有裁切都已通過視覺驗證，且每個裁切框都與目前的 `figure_decisions.json` 完全一致後，才撰寫 `figures.json`。

15. `figures.json` 應列出最終確認的圖表成果，包含：
   - figure label
   - 最終裁切圖片路徑
   - 對應頁碼
   - 裁切框座標
   - 圖說文字或圖說來源
   - 是否包含圖說
   - 對應的 `figure_decisions.json` 決策項目

16. 執行機械式驗證，確認：
   - `figures.json` 中列出的每張圖都存在
   - 每張最終裁切圖片都有對應的裁切決策
   - 裁切框座標與 `figure_decisions.json` 一致
   - 所有必要的預覽圖與邊界預覽都已建立
   - 沒有未驗證的裁切圖片被寫入 `figures.json`

17. 如果機械式驗證失敗，必須修正對應的 artifact，重新驗證；若無法修正，則回報此次 figure extraction 尚未完成，不得宣稱擷取成功。


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
          "notes": ["Contains Fig. 1 visual region, caption boundary, and nearby body text."]
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
          "notes": ["Left panel group found from bounded page preview."]
        },
        {
          "region_id": "p004_r002",
          "region_type": "figure_visual",
          "bbox_px": [1320, 420, 2260, 1260],
          "source": "model_visual",
          "confidence": 0.72,
          "text": null,
          "notes": ["Right panel group found from bounded page preview."]
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
          "notes": ["Shows both visual regions, intervening body text, and caption boundary."]
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
  "notes": ["Any figure with verification.result = fail means this worker output is not successful, even though the failed figure is recorded for traceability."]
}
```

## 圖片檔案

# 規則

## 圖片分類

完整解析度圖片：檔案尺寸接近原始解析度（約 300 dpi 或更高）

- 完整解析度頁面圖片：輸入的 pdf 轉出來的整頁圖片，這是判斷原始論文長什麼樣子的最高依據
- 完整解析度裁切區域來源圖片：根據 `figure_candidates.json`、`figure_index.json` 或 `figure_decisions.json`，從完整解析度頁面圖片裁切出來的工作區域來源圖片。它用來檢查候選圖表、圖說邊界與周邊干擾內容；它不是最終裁切成果，也不代表該區域一定會進入 `figures.json`。
- 完整解析度裁切區域邊界圖片：裁切區域來源圖片或最終裁切圖片的四個邊界，用來檢查邊界附近是否有內容被切掉或混入非 figure 內容
- 完整解析度最終裁切圖片：根據 `figure_decisions.json` 從完整解析度頁面圖片裁切出的圖片，這是被審查的成果本體

預覽圖片：上述四種圖片的縮小版，單一圖片兩邊都不得超過 1600 px。多圖讀取時，每張兩邊不得超過 1400 px，且批次要小。

- 預覽頁面圖片：從完整解析度頁面圖片縮小得到
- 預覽裁切區域來源圖片：從完整解析度裁切區域來源圖片縮小得到，用於審查候選區域、圖說邊界、周邊上下文與需要排除的干擾內容。
- 預覽裁切區域邊界圖片：從完整解析度裁切區域邊界圖片縮小得到
- 預覽最終裁切圖片：從完整解析度最終裁切圖片縮小得到

## 座標規則

- 所有寫入 JSON 的座標，一律使用完整解析度頁面圖片的 pixel coordinate。
- 裁切區域來源圖片只用來視覺檢查，不作為最終裁切座標的真相。
- 若從裁切區域或其 preview 判斷邊界，必須換回頁面圖片座標後再寫入 `figure_decisions.json`。
- 最終裁切永遠根據 `figure_decisions.json`，從完整解析度頁面圖片裁出，不要從中間裁切圖再裁一次。
- 座標換算時，邊界應保守外擴：左上角向外取整，右下角向外取整，再用 final crop edge previews 收緊。