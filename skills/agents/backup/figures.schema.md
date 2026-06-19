# figures.json

唯一的 extraction output manifest。進 canonical，是 repair 的 patch 對象。

`schema_version`: `"figure_extraction.v3"`

## Enums

- `figure_type`：`main`（主文）| `extended`（Extended Data）| `supplementary`（Supplementary）| `other`（其他）
- `status`：`complete`（所有 figure pass）| `incomplete`（任何 figure fail）
- `verification.*`：`pass` | `fail`。不使用 `not_applicable`。
- `verification` 欄位：
  - `source_context_checked`：agent 已讀過 source context preview
  - `final_crop_checked`：agent 已讀過 final crop preview，檢查內部細節
  - `boundary_preview_checked`：agent 已讀過 boundary preview 和 edge strips，檢查四邊 framing
  - `figure_content_complete`：figure 內部內容完整（axis、legend、panel 等）
  - `external_caption_excluded`：外部 caption 不在 crop 中
  - `page_chrome_excluded`：頁眉、頁腳、頁碼等不在 crop 中
  - `no_adjacent_content`：相鄰 figure、table、正文等不在 crop 中
  - `result`：綜合判定

## Fields

- `status`: `complete` 或 `incomplete`
- `figures[]`:
  - `figure_id`, `figure_label`, `figure_type`
  - `candidate_ids`, `source_region_ids`
  - `caption_text`
  - `crop_units[]`:
    - `crop_id`: filename-safe, unique within figure
    - `page`: int
    - `crop_px`: [x1, y1, x2, y2] in full-res page pixels
    - `image_file`: artifact-root-relative (e.g. `crops/Figure_1.png`)
    - `preview`: artifact-root-relative (e.g. `previews/Figure_1_preview.png`)
    - `boundary_preview`: artifact-root-relative
    - `top_band`: string array (artifact-root-relative)
    - `left_band`: string array
    - `right_band`: string array
    - `bottom_band`: string array
    - `bottom_micro`: string array
    - `role`: free-text short description (e.g. `complete figure`, `left visual region`)
  - `evidence_read`:
    - `final_crop_previews`: string array
    - `boundary_previews`: string array
    - `bottom_band_previews`: string array
    - `bottom_micro_previews`: string array
  - `verification`:
    - `source_context_checked`: `pass` | `fail`
    - `final_crop_checked`: `pass` | `fail`
    - `boundary_preview_checked`: `pass` | `fail`
    - `figure_content_complete`: `pass` | `fail`
    - `external_caption_excluded`: `pass` | `fail`
    - `page_chrome_excluded`: `pass` | `fail`
    - `no_adjacent_content`: `pass` | `fail`
    - `result`: `pass` | `fail`
  - `notes`

## Naming

- `figure_id`: filename-safe, e.g. `Figure_1`, `Extended_Data_Figure_1`
- Single crop: `crops/<figure_id>.png`; multi crop: `crops/<figure_id>_part_<N>.png`
- 所有 artifact path 使用 artifact-root-relative（不含 `figures/canonical/`）
- Shared page paths 使用 paper-dir-relative（`shared/pages/page_3.png`）
- Figure 層不寫 derived 欄位（`pages`、`image_files`、`crop_count`）

## Example

```json
{
  "schema_version": "figure_extraction.v3",
  "worker_id": "worker_01",
  "status": "complete",
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
          "boundary_preview": "previews/Figure_1_boundary_preview.png",
          "top_band": ["previews/Figure_1_top_seg1_preview.png"],
          "left_band": ["previews/Figure_1_left_seg1_preview.png"],
          "right_band": ["previews/Figure_1_right_seg1_preview.png"],
          "bottom_band": ["previews/Figure_1_bottom_seg1_preview.png"],
          "bottom_micro": ["previews/Figure_1_micro_bottom_seg1_preview.png"],
          "role": "complete figure"
        }
      ],
      "evidence_read": {
        "final_crop_previews": ["previews/Figure_1_preview.png"],
        "boundary_previews": ["previews/Figure_1_boundary_preview.png"],
        "bottom_band_previews": ["previews/Figure_1_bottom_seg1_preview.png"],
        "bottom_micro_previews": ["previews/Figure_1_micro_bottom_seg1_preview.png"]
      },
      "verification": {
        "source_context_checked": "pass",
        "final_crop_checked": "pass",
        "boundary_preview_checked": "pass",
        "figure_content_complete": "pass",
        "external_caption_excluded": "pass",
        "page_chrome_excluded": "pass",
        "no_adjacent_content": "pass",
        "result": "pass"
      },
      "notes": []
    }
  ],
  "notes": []
}
```
