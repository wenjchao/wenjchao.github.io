# repair_report.json

由 `build_repair_report.py` 從 `decisions.json` 自動組裝。Agent 不手寫此檔案。

`schema_version`: `"figure_repair.v3"`

## Enums

- `status`：`complete`（所有 request 完成）| `incomplete`（有 unresolved 或 blocked）
- `repairs[].result`：
  - `repaired`：crop / preview 已修復
  - `manifest_corrected`：只修正 manifest 欄位，不一定重裁
  - `preview_regenerated`：只重建缺失 preview，不改 crop_px
  - `unresolved`：無法修復（版面限制、缺少 evidence 等）
  - `blocked`：需要人工介入或相鄰 figure 未在 assignment 中
- `validation.repair_self_check_status`：`pass` | `fail`
- `merge.file_copies[].kind`：
  - `crop`：完整解析度 crop PNG
  - `crop_preview`：crop preview
  - `boundary_preview`：boundary preview（含 cyan 矩形）
  - `top_band` | `left_band` | `right_band`：上/左/右邊 edge strip
  - `bottom_band`：底邊 band segment
  - `bottom_micro`：底邊 microzoom segment
- `merge.manifest_patches[].operation`：`replace`（覆蓋現有值，需 old_value match）| `add_if_missing`（新增不存在的欄位）
- `merge.manifest_patches[].target_file`：`figures.json`（主 manifest）| `figure_index.json`（僅 manifest_correction action）

## Fields

- `repair_round`, `repair_id`, `status`, `source_request_file`
- `repairs[]`:
  - `request_id`, `figure_id`, `figure_label`
  - `result`, `action_taken`
  - `updated_crop_units[]`:
    - `crop_id`, `page`, `old_crop_px`, `new_crop_px`, `role`
    - `repair_output`: map with `image_file`, `preview`, `boundary_preview`, `top_band`, `left_band`, `right_band`, `bottom_band`, `bottom_micro` (all repair-root-relative)
    - `canonical_target`: same structure (canonical-root-relative)
  - `evidence_read`:
    - `source_boundary_previews`: string array (canonical-relative)
    - `repaired_crop_previews`, `repaired_boundary_previews`, `repaired_bottom_band_previews`, `repaired_bottom_micro_previews`: string arrays (repair-root-relative)
  - `requires_review`: boolean (true for any modified repair)
  - `notes`: string array
- `merge`:
  - `needs_parent_merge`: boolean
  - `file_copies[]`: `kind`, `figure_id`, `crop_id`, `repair_output`, `canonical_target`, `segment` (optional int)
  - `manifest_patches[]`: `target_file`, `operation`, `scope`, `selector` ({figure_id, crop_id}), `path`, `old_value`, `new_value`
  - `review_required_after_merge`: boolean
- `validation`: `repair_self_check_status`, `notes`
- `summary`: `request_count`, `repaired_count`, `preview_regenerated_count`, `unresolved_count`, `blocked_count`

## Example

```json
{
  "schema_version": "figure_repair.v3",
  "repair_round": "round_01",
  "repair_id": "repair_01",
  "status": "complete",
  "source_request_file": "repairs/round_01/repair_requests_merged.json",
  "repairs": [
    {
      "request_id": "Figure_1_f001",
      "figure_id": "Figure_1",
      "figure_label": "Fig. 1",
      "result": "repaired",
      "action_taken": "recrop",
      "updated_crop_units": [
        {
          "crop_id": "Figure_1",
          "page": 3,
          "old_crop_px": [120, 300, 2380, 1390],
          "new_crop_px": [120, 300, 2380, 1850],
          "role": "complete figure",
          "repair_output": {
            "image_file": "crops/Figure_1.png",
            "preview": "previews/Figure_1_preview.png",
            "boundary_preview": "previews/Figure_1_boundary_preview.png",
            "bottom_band": ["previews/Figure_1_bottom_seg1_preview.png"],
            "bottom_micro": ["previews/Figure_1_micro_bottom_seg1_preview.png"]
          },
          "canonical_target": {
            "image_file": "crops/Figure_1.png",
            "preview": "previews/Figure_1_preview.png",
            "boundary_preview": "previews/Figure_1_boundary_preview.png",
            "bottom_band": ["previews/Figure_1_bottom_seg1_preview.png"],
            "bottom_micro": ["previews/Figure_1_micro_bottom_seg1_preview.png"]
          }
        }
      ],
      "evidence_read": {
        "source_boundary_previews": ["previews/Figure_1_boundary_preview.png"],
        "repaired_crop_previews": ["previews/Figure_1_preview.png"],
        "repaired_boundary_previews": ["previews/Figure_1_boundary_preview.png"],
        "repaired_bottom_band_previews": ["previews/Figure_1_bottom_seg1_preview.png"],
        "repaired_bottom_micro_previews": ["previews/Figure_1_micro_bottom_seg1_preview.png"]
      },
      "requires_review": true,
      "notes": ["Expanded bottom to include missing panels."]
    }
  ],
  "merge": {
    "needs_parent_merge": true,
    "file_copies": [
      {
        "kind": "crop",
        "figure_id": "Figure_1",
        "crop_id": "Figure_1",
        "repair_output": "crops/Figure_1.png",
        "canonical_target": "crops/Figure_1.png"
      }
    ],
    "manifest_patches": [
      {
        "target_file": "figures.json",
        "operation": "replace",
        "scope": "crop_unit",
        "selector": {"figure_id": "Figure_1", "crop_id": "Figure_1"},
        "path": "crop_units[].crop_px",
        "old_value": [120, 300, 2380, 1390],
        "new_value": [120, 300, 2380, 1850]
      }
    ],
    "review_required_after_merge": true
  },
  "validation": {
    "repair_self_check_status": "pass",
    "notes": []
  },
  "summary": {
    "request_count": 1,
    "repaired_count": 1,
    "preview_regenerated_count": 0,
    "unresolved_count": 0,
    "blocked_count": 0
  }
}
```
