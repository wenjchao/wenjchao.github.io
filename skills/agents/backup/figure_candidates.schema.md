# figure_candidates.json

`schema_version`: `"figure_extraction.v3"`

## Enums

- `region_type`：
  - `figure_visual`：圖表的視覺內容區域
  - `caption`：圖說文字
  - `body`：正文
  - `header`：頁眉
  - `footer`：頁腳
  - `table`：表格
  - `equation`：方程式
  - `separator`：分隔線
  - `unknown`：無法判斷的區域
- `source`：
  - `layout_detector`：版面偵測器
  - `object_detector`：物件偵測器
  - `pdf_text`：PDF 文字層
  - `ocr`：OCR
  - `geometry`：幾何分析
  - `model_visual`：從受限尺寸頁面預覽圖片目視判斷。必須在 `notes` 說明證據限制。
  - `manual`：手動標記。必須在 `notes` 說明證據限制。
- `unexpected_labeled_figures[].reason`（建議值，可自訂 snake_case）：
  - `outside_assignment`：不在本 worker 的 assignment 範圍
  - `unexpected_page`：出現在非預期頁碼
  - `not_in_global_index`：不在 global index 或 assignment list 中（僅在可讀到 global index 時使用）

## Fields

- `scope.pages`: int array, worker 掃描的頁碼
- `pages[]`: per-page objects
  - `page`: int
  - `page_image`: paper-dir-relative path (e.g. `shared/pages/page_3.png`)
  - `page_preview`: paper-dir-relative path
  - `page_size_px`: [width, height]
  - `regions[]`: detected regions
    - `region_id`, `region_type`, `bbox_px` [x1,y1,x2,y2], `source`, `confidence`, `text` (nullable), `notes`
  - `source_regions[]`: cropped context areas for candidate inspection
    - `source_region_id`, `source_image` (artifact-root-relative), `source_preview` (artifact-root-relative), `bbox_px`, `candidate_ids`, `notes`
  - `figure_candidates[]`: candidate figures
    - `candidate_id`, `figure_label`, `visual_region_ids`, `caption_region_ids`, `excluded_region_ids`, `source_region_ids`, `crop_hint_px` (dict keyed by `page_N`), `confidence`, `risks`
- `unexpected_labeled_figures[]`: `figure_label`, `page`, `reason`, `caption_text` (nullable), `notes` (conditional)
- `crop_hint_px` 只出現在 candidate 層，表示候選階段的裁切提示，不是 final crop。

## Example

```json
{
  "schema_version": "figure_extraction.v3",
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
        }
      ],
      "source_regions": [
        {
          "source_region_id": "p003_src001",
          "source_image": "source_regions/p003_src001.png",
          "source_preview": "previews/p003_src001_preview.png",
          "bbox_px": [90, 260, 2410, 2080],
          "candidate_ids": ["p003_c001"],
          "notes": []
        }
      ],
      "figure_candidates": [
        {
          "candidate_id": "p003_c001",
          "figure_label": "Fig. 1",
          "visual_region_ids": ["p003_r001"],
          "caption_region_ids": ["p003_r002"],
          "excluded_region_ids": ["p003_r002"],
          "source_region_ids": ["p003_src001"],
          "crop_hint_px": {
            "page_3": [120, 300, 2380, 1850]
          },
          "confidence": 0.82,
          "risks": ["Large chart-like figure; verify bottom axis labels."]
        }
      ]
    }
  ],
  "unexpected_labeled_figures": [],
  "notes": []
}
```
