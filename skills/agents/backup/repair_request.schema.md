# repair_requests_merged.json

由 `build_repair_request.py` 從 `visual_review.json` 自動產生。不進 canonical。

`schema_version`: `"figure_repair.v3"`

## Enums

- `action`：
  - `recrop`：更新 crop_px，重新裁切 crop 和全套 preview
  - `regenerate_missing_preview`：不改 crop_px，只重建缺失的 preview
  - `manifest_correction`：只修正 manifest 欄位，不一定重裁
- `defects[]`：free-text，格式 `"<problem>: <edge>"`（例如 `"content_cut: bottom"`）
- `direction[]`：string array，對應 visual_review 的 `repair_hint` 值（例如 `["expand_bottom"]`）

## Fields

- `repair_round`: string (e.g. `round_01`)
- `source_reviews`: string array
- `assignments[]`:
  - `repair_id`, `figure_ids`, `request_ids`
- `requests[]`:
  - `request_id`: matches source finding_id (e.g. `Figure_1_f001`)
  - `assigned_repair_id`
  - `figure_id`, `figure_label`
  - `crop_ids`: string array
  - `source_review`, `source_finding_id`
  - `action`, `direction` (string array of repair_hints), `constraint`, `defects`

Request 不包含座標（`current_crop_px`、`proposed_crop_px` 等）。

## Example

```json
{
  "schema_version": "figure_repair.v3",
  "repair_round": "round_01",
  "source_reviews": ["reviewers/round_00/reviewer_01/visual_review.json"],
  "assignments": [
    {
      "repair_id": "repair_01",
      "figure_ids": ["Figure_1"],
      "request_ids": ["Figure_1_f001"]
    }
  ],
  "requests": [
    {
      "request_id": "Figure_1_f001",
      "assigned_repair_id": "repair_01",
      "figure_id": "Figure_1",
      "figure_label": "Fig. 1",
      "crop_ids": ["Figure_1"],
      "source_review": "reviewers/round_00/reviewer_01/visual_review.json",
      "source_finding_id": "Figure_1_f001",
      "action": "recrop",
      "direction": ["expand_bottom"],
      "constraint": "Expand crop to include panels e-g, stop before external caption.",
      "defects": ["content_cut: bottom"]
    }
  ]
}
```
