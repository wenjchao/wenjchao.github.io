# figure_decisions.json

Planning trace — 記錄裁切決策的理由和排除項目。不進 canonical。

`schema_version`: `"figure_extraction.v3"`

## Enums

- `figure_type`：`main`（主文）| `extended`（Extended Data）| `supplementary`（Supplementary）| `other`（其他）

## Fields

- `figures[]`:
  - `figure_id`, `figure_label`, `figure_type`
  - `candidate_ids`, `source_region_ids`, `visual_region_ids`, `caption_region_ids`, `excluded_region_ids`
  - `evidence_read`: `page_previews` (paper-dir-relative), `source_region_previews` (artifact-root-relative)
  - `caption_text`, `expected_panels`, `exclusions`, `rationale`
  - `crop_units[]`: 初始裁切計劃
    - `crop_id`, `page`, `crop_px` [x1,y1,x2,y2], `image_file`, `preview`, `boundary_preview`, `bottom_band`, `bottom_micro`, `role`

## Naming

- `figure_id` 必須 filename-safe：`Figure_1`、`Extended_Data_Figure_1`
- `crop_px`: 完整解析度頁面圖片的 pixel coordinate [x1, y1, x2, y2]
- `image_file`: `crops/<figure_id>.png`（single crop）或 `crops/<figure_id>_part_<N>.png`（multi crop）
- 所有 artifact path 使用 artifact-root-relative（不含 `figures/workers/...`）
- `figure_decisions.json` 和 `figures.json` 有 `crop_units` 時，figure 層不寫 derived 欄位（`pages`、`image_files`、`crop_count`）

## Example

```json
{
  "schema_version": "figure_extraction.v3",
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
          "boundary_preview": "previews/Figure_1_boundary_preview.png",
          "bottom_band": ["previews/Figure_1_bottom_seg1_preview.png"],
          "bottom_micro": ["previews/Figure_1_micro_bottom_seg1_preview.png"],
          "role": "complete figure"
        }
      ],
      "exclusions": ["caption below crop", "body text below caption"],
      "rationale": "Crop follows visual region p003_r001. External caption stored in caption_text."
    }
  ],
  "notes": []
}
```
