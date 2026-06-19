# review_packet.json

由 `build_review_packet.py` 從 `canonical/figures.json` 自動產生。不進 canonical。

`schema_version`: `"figure_review_packet.v1"`

## Fields

- `review_round`: string (e.g. `round_00`)
- `reviewer_id`: string (e.g. `reviewer_01`)
- `canonical_artifact_root`: string (e.g. `figures/canonical`)
- `figures[]`:
  - `figure_id`, `figure_label`
  - `crop_units[]`:
    - `crop_id`, `role`, `page`, `crop_px`
    - `source_page`: paper-dir-relative (e.g. `shared/pages/page_3.png`)
    - `crop_preview`, `boundary_preview`: canonical-artifact-root-relative
    - `top_band`, `left_band`, `right_band`: string array
    - `bottom_band`, `bottom_micro`: string array

## Example

```json
{
  "schema_version": "figure_review_packet.v1",
  "review_round": "round_00",
  "reviewer_id": "reviewer_01",
  "canonical_artifact_root": "figures/canonical",
  "figures": [
    {
      "figure_id": "Figure_1",
      "figure_label": "Fig. 1",
      "crop_units": [
        {
          "crop_id": "Figure_1",
          "role": "complete figure",
          "page": 3,
          "crop_px": [120, 300, 2380, 1850],
          "source_page": "shared/pages/page_3.png",
          "crop_preview": "previews/Figure_1_preview.png",
          "boundary_preview": "previews/Figure_1_boundary_preview.png",
          "top_band": ["previews/Figure_1_top_seg1_preview.png"],
          "left_band": ["previews/Figure_1_left_seg1_preview.png"],
          "right_band": ["previews/Figure_1_right_seg1_preview.png"],
          "bottom_band": ["previews/Figure_1_bottom_seg1_preview.png"],
          "bottom_micro": ["previews/Figure_1_micro_bottom_seg1_preview.png"]
        }
      ]
    }
  ]
}
```
