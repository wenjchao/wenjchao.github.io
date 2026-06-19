# 目標

這是一份給 `figure_extractor` 工作代理看的指引。

此流程使用場景與目標：
- 輸入：
  - `<paper_dir>/input/source.pdf`
  - `<paper_dir>/shared/pages/page_N.png`，也就是 PDF 轉出的完整解析度頁面圖片
  - `<paper_dir>/shared/previews/page_N_preview.*`，也就是給工作代理讀的頁面預覽圖片
  - 協調器指派的頁面範圍或 figure 範圍
- 輸出位置：`<paper_dir>/lanes/figures/worker_output/worker_01/`
- 輸出內容：
  - `figure_candidates.json`：候選證據，記錄每頁疑似圖表的視覺區域、圖說候選、附近文字、頁面固定元素、裁切區域來源圖片與候選裁切範圍。
  - `figure_index.json`：正式圖表索引，記錄本工作代理範圍內確認存在的有標記圖表。
  - `figure_decisions.json`：最終裁切前的決策檔，記錄每張圖的頁面座標裁切框、輸出圖檔、排除項目與理由。
  - `figures.json`：最終擷取清單檔，記錄已產生的裁切圖片、預覽圖片、邊界預覽、圖說文字與驗證結果。
  - `source_regions/`：完整解析度裁切區域來源圖片，用來產生裁切區域來源預覽圖片。
  - `edges/`：完整解析度邊界條帶圖片，用來產生邊界預覽圖片。
  - `previews/`：所有給工作代理視覺讀取的預覽圖片；檔名必須包含 `_preview`。
  - `Figure_*.png`：完整解析度最終裁切圖片。

此工作代理只負責初始擷取，不負責：
- reviewer
- repair
- canonical merge
- validator
- 修改來源 PDF

目標：讓最終裁切圖片準確包含 figure 的上下左右邊緣，不切掉 figure 的任何部分，同時盡可能裁掉不屬於 figure 的內容。

若指定範圍中沒有有標記圖表，仍要寫出四個 JSON 檔，圖表列表為空，並在 `figures.json` 中標記擷取完成。

# 流程

## 工作流程

1. 確認完整解析度頁面圖片存在。
   - 位置：`<paper_dir>/shared/pages/page_N.png`
   - 完整解析度頁面圖片是最終裁切來源，也是所有 JSON 座標的基準。
   - 若缺少頁面圖片，回報給協調器；不要自行改變輸出路徑。

2. 確認頁面預覽圖片存在。
   - 位置：`<paper_dir>/shared/previews/page_N_preview.*`
   - 工作代理讀圖時應讀預覽圖片，不直接讀超過尺寸限制的完整解析度頁面圖片。

3. 產生 `figure_candidates.json`。
   - 將頁面中的內容切成候選區域。
   - 至少區分：
     - 圖表視覺區域
     - 圖說候選
     - 正文
     - 頁眉、頁腳、頁碼、期刊固定元素等頁面固定內容
     - table
     - equation
     - unknown
   - 每個 figure candidate 必須有視覺區域證據；不能只根據圖說位置決定候選圖表。

4. 建立完整解析度裁切區域來源圖片。
   - 位置：`<paper_dir>/lanes/figures/worker_output/worker_01/source_regions/`
   - 這些圖片是產生裁切區域來源預覽圖片的原檔。
   - 它們應包含：
     - 候選圖表視覺區域
     - 可能的圖說
     - 圖說與正文的邊界
     - 附近正文
     - 可能需要排除的頁眉、頁腳、頁碼或其他頁面固定元素
   - 它們不是最終裁切成果，也不是最終裁切座標的真相。

5. 建立並讀取裁切區域來源預覽圖片。
   - 位置：`<paper_dir>/lanes/figures/worker_output/worker_01/previews/`
   - 檔名必須包含 `_preview`。
   - 用途是讓工作代理判斷候選圖表、圖說邊界、附近干擾內容，以及後續應該排除什麼。

6. 根據候選結果寫 `figure_index.json`。
   - 此檔只回答：本工作代理範圍內有哪些正式有標記圖表？
   - 應記錄：
     - `figure_id`
     - figure label，也就是圖表標籤，例如 `Fig. 1`
     - 所在頁碼
     - 對應的候選 id
     - 對應的裁切區域來源圖片 id
     - 圖說文字
     - 是否預期需要單區域、多區域或跨頁裁切
   - 不要在此檔決定最終裁切框。

7. 針對 `figure_index.json` 中的每張圖做候選與來源上下文檢查。
   - 這一步是為了決定圖表成員與裁切策略，不是驗證最終裁切成果。
   - 確認：
     - 候選視覺區域確實屬於該圖表標籤。
     - 所有必要 panel、座標軸、圖例、比例尺、色條、圖內標籤都被納入裁切考量。
     - 外部圖說只應存入 `caption_text`，不應放進最終 crop。
     - 圖內嵌入的 label、legend、axis label、panel label 等應保留。
     - 附近正文、頁碼、頁眉、頁腳、欄線、其他圖表或其他非 figure 內容應被排除。
     - 若單一矩形會包含正文或其他非 figure 內容，應改用多個 crop units。

8. 在任何最終裁切前寫 `figure_decisions.json`。
   - 此檔是最終裁切的唯一依據。
   - 所有 `crop_px` 都必須是完整解析度頁面圖片的 pixel coordinate。
   - 應記錄：
     - figure id / label / page
     - 使用的候選區域與裁切區域來源圖片
     - 最終裁切框
     - 輸出圖檔
     - 排除項目
     - 預期 panel
     - 決策理由
   - 外部圖說永遠不放進最終裁切圖片，只存入 `caption_text`。

9. 根據 `figure_decisions.json` 裁切完整解析度最終圖片。
   - 最終裁切永遠從 `<paper_dir>/shared/pages/page_N.png` 裁出。
   - 不要從裁切區域來源圖片、預覽圖片或其他中間圖片再裁一次。

10. 為每張最終裁切圖片建立預覽圖片與邊界預覽圖片。
    - 最終裁切預覽：`previews/Figure_1_preview.png`
    - 上邊界預覽：`previews/Figure_1_top_preview.png`
    - 下邊界預覽：`previews/Figure_1_bottom_preview.png`
    - 左邊界預覽：`previews/Figure_1_left_preview.png`
    - 右邊界預覽：`previews/Figure_1_right_preview.png`
    - 若有完整解析度邊界條帶，放在 `edges/`；給工作代理讀的一律是 `_preview` 圖片。

11. 讀取最終裁切預覽與四個邊界預覽，逐一驗證。
    - 確認 figure 內容是否完整。
    - 確認上下左右邊界是否過緊或過鬆。
    - 確認圖內標籤、座標軸、圖例、比例尺、panel label、color bar 是否被截斷。
    - 確認沒有外部圖說、正文、頁碼、頁眉、頁腳或相鄰內容混入。

12. 如果裁切結果不正確，先更新 `figure_decisions.json`。
    - 不要直接修改最終圖片後就宣稱完成。
    - 更新決策後，重新裁切。
    - 重新建立最終裁切預覽與四個邊界預覽。
    - 重新讀圖檢查。

13. 寫 `figures.json`。
    - `figures.json` 可以記錄驗證失敗的 figure。
    - 但任何 `verification.result = "fail"` 都代表本次擷取尚未完成，不能被當成成功。
    - failed figure 被記錄是為了 trace 與後續 repair，不是為了放行。

14. 回報 worker 結果。
    - 寫了哪些 JSON 檔。
    - 讀了哪些預覽圖片。
    - 產生哪些裁切圖片。
    - 哪些 figure 通過，哪些 figure 失敗。
    - 是否有尚未解決的阻礙。

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
  "notes": ["只要任何 figure 的 verification.result 是 fail，就表示此工作代理輸出尚未成功；失敗的 figure 仍會被記錄，方便追蹤與後續修復。"]
}
```

## 圖片檔案

檔名含有 `_preview` 的圖片，才是給工作代理讀的受限尺寸預覽圖片。沒有 `_preview` 的圖片是完整解析度原檔或工作中間檔；除非尺寸本身符合讀取限制，否則不要直接讀。

建議命名：
- 頁面圖片：`shared/pages/page_3.png`
- 頁面預覽圖片：`shared/previews/page_3_preview.png`
- 裁切區域來源圖片：`lanes/figures/worker_output/worker_01/source_regions/p003_src001.png`
- 裁切區域來源預覽圖片：`lanes/figures/worker_output/worker_01/previews/p003_src001_preview.png`
- 最終裁切圖片：`lanes/figures/worker_output/worker_01/Figure_1.png`
- 最終裁切預覽圖片：`lanes/figures/worker_output/worker_01/previews/Figure_1_preview.png`
- 完整解析度邊界條帶圖片：`lanes/figures/worker_output/worker_01/edges/Figure_1_top.png`
- 邊界預覽圖片：`lanes/figures/worker_output/worker_01/previews/Figure_1_top_preview.png`

# 規則

## 權責邊界

- `figure_extractor` 只做初始擷取。
- 不寫 canonical 成果、review 成果、repair 成果或 validation reports。
- 不修改來源 PDF。
- 不讓外層協調器從部分裁切輸出回填 `figures.json`；`figures.json` 內容必須來自本工作代理寫出的裁切決策與視覺檢查。

## 圖片與讀取限制

- 完整解析度頁面圖片是判斷原始版面的最高依據，也是最終裁切來源。
- 所有預覽圖片都必須有對應原檔：
  - 頁面預覽圖片來自頁面圖片。
  - 裁切區域來源預覽圖片來自裁切區域來源圖片。
  - 最終裁切預覽圖片來自最終裁切圖片。
  - 邊界預覽圖片來自完整解析度邊界條帶圖片。
- 工作代理讀取的單張圖片，兩邊都不得超過 1600 px。
- 工作代理一次讀多張圖片時，每張圖片兩邊都不得超過 1400 px，且批次要小。
- 不要直接讀超過限制的完整解析度頁面圖片、最終裁切圖片、裁切區域來源圖片或邊界條帶圖片。

## 座標規則

- 所有寫入 JSON 的 `bbox_px`、`crop_hint_px`、`crop_px` 都使用完整解析度頁面圖片的 pixel coordinate。
- 裁切區域來源圖片只用來產生和檢查裁切區域來源預覽圖片，不是最終裁切座標的真相。
- 若從裁切區域來源預覽圖片判斷邊界，必須換回完整解析度頁面圖片座標後，再寫入 `figure_decisions.json`。
- 最終裁切永遠根據 `figure_decisions.json` 從完整解析度頁面圖片裁出，不要從裁切區域來源圖片或其他中間圖片再裁一次。
- 座標換算時，邊界應保守外擴：左上角向外取整，右下角向外取整，再用最終裁切邊界預覽圖片收緊。

## 圖說與邊界

- 外部圖說永遠不放進最終裁切圖片，只存入 `caption_text`。
- 圖內嵌入的文字屬於 figure 內容，應保留在裁切中，例如：
  - 圖內標籤
  - 圖內標題
  - 圖例
  - 座標軸標籤
  - 比例尺
  - panel label
  - color bar
  - 圖內短說明文字
- 若某段文字是否屬於 figure 內部不確定，必須在 `rationale` 或 `notes` 說明，且不能把不確定的裁切標成 `pass`。
- 應排除：
  - 正文
  - 外部圖說
  - 頁碼
  - 頁眉、頁腳
  - 期刊固定元素
  - 浮水印
  - 相鄰圖表
  - table
  - equation
  - 其他非 figure 內容

## 跨頁與多區域圖表

- 多 panel figure 預設視為同一張 figure，除非原文明確標成不同 figures。
- 跨頁 figure 可以有多個 `crop_units` 和多個 `image_files`，並用同一個 `figure_id` 關聯。
- 同頁多區域 figure 也可以有多個 `crop_units` 和多個 `image_files`。
- 不要為了做成單一矩形，而把中間正文或其他非 figure 內容一起裁進來。
- 多個 `crop_units` 必須同時出現在：
  - `figure_decisions.json`
  - `figures.json`
- 多個 `crop_units` 必須共用同一個 `figure_id`，表示它們屬於同一張 figure。

## 視覺驗證

- 程式碼、OCR、PDF 文字、版面偵測器、尺寸、座標和 validator 都不能單獨證明裁切品質。
- 每個標成 `pass` 的 figure，都必須讀過：
  - 來源上下文預覽圖片
  - 最終裁切預覽圖片
  - 上邊界預覽圖片
  - 下邊界預覽圖片
  - 左邊界預覽圖片
  - 右邊界預覽圖片
- 圖表型圖片的底邊與側邊風險最高，例如折線圖、長條圖、散點圖、熱圖、Manhattan plot、帶座標軸的示意圖。必須檢查：
  - x 軸刻度與標題是否完整
  - y 軸標籤是否完整
  - 圖例是否完整
  - color bar 是否完整
  - plot boundary 是否完整
- `verification` 只使用 `pass` 或 `fail`。
- 不要使用 `not_applicable`；沒有某種元素時，只要沒有缺失或截斷，該檢查就是 `pass`。
- `figures.json` 可以記錄 `fail`，但只要任何 figure 的 `verification.result` 是 `fail`，整個工作代理輸出的 `status` 就必須是 `incomplete`。
- 失敗的 figure 被記錄是為了 trace 與後續 repair，不代表 extraction 成功。

## 空範圍

如果指定範圍中沒有有標記圖表：
- `figure_candidates.json` 的 `pages` 仍要記錄已掃描頁面，`figure_candidates` 為空。
- `figure_index.json`、`figure_decisions.json`、`figures.json` 的 `figures` 為空。
- `figures.json.status` 設為 `complete`。
