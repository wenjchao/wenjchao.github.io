# 目標

這是一份給 figure_repair agent 看的指引。

此流程使用場景與目標：
- 輸入：一個 paper directory、repair round / repair assignment、`canonical_artifact_root`、`repair_artifact_root`，以及 parent orchestrator 合併出的 `repair_requests_merged.json`。
- 讀取位置：
    - `lanes/figures/repairs/round_<N>/repair_requests_merged.json`：本輪所有 reviewer findings 經 parent 合併後的 repair requests，已標記每個 request 分派給哪個 repair worker。
    - `shared/pages/`：完整解析度頁面圖片，這是修復裁切邊界的最高依據。
    - `lanes/figures/canonical/`：目前的 canonical figure extraction 成果（`figure_candidates.json`、`figure_index.json`、`figure_decisions.json`、`figures.json`，以及 crop PNG 和 preview）。Schema 以 `figure_extractor.md` 定義的 `figure_extraction.v2` 為準。
- 輸出位置：`<paper_dir>/lanes/figures/repairs/round_<N>/repair_<ID>/`
- 輸出（全部寫在本 worker 的 repair 目錄，由 parent merge / replace 到 canonical）：
    - `repair_report.json`：本次修復結果。包含每個 assigned request 的處理結果、修復前後 crop_px、repair-local output paths 與 canonical target paths、修復後 crop hash、讀取的 evidence、`merge.file_copies[]`、`merge.manifest_patches[]`，以及 parent merge 指令。
    - `crops/`：修復後的完整解析度 crop PNG。
    - `previews/`：修復過程中建立的 source context preview、source edge preview、修復後 crop preview 與 edge preview。所有 preview 檔名必須含 `_preview` 後綴。
    - `manifest_updates/`：只有在 manifest 欄位改變時才寫；內容必須是 parent 可整檔搬運或套用允許清單 patch 的機械可讀 JSON。
- Repair agent 不直接寫入 `lanes/figures/canonical/`。所有 canonical 更新由 parent 負責。
- 第一階段 parent merge 後不執行 canonical mechanical validation；parent 直接重新執行 `figure_reviewer`。Canonical validation 留到第二階段。

- 目標：根據 parent 指派的 repair request，修復已知不合格的 figure crop。修復後的 crop 應完整包含 figure 內容，並盡量排除外部 caption、正文、page chrome 與相鄰內容。
- 邊界：
    - 此 agent 只做 repair，不做初始 extraction，也不做獨立 visual review。
    - 只處理 `repair_requests_merged.json` 中分派給本 `repair_id` 的 requests；不要讀到別人的 request 就順手修。
    - 修復時必須保留原本的 `figure_id`。
    - 不修改來源 PDF。不修改 reviewer output。不修改 `repair_requests_merged.json`、`before_snapshot.json`、`after_snapshot.json`。不寫 review batches。
    - 如果修復會影響未被指派的相鄰 figure，標為 `blocked`，不要靜默修改相鄰 figure。
    - 此 agent 可以做修復後的視覺檢查，但不提供最終獨立接受判定；任何改動過的 figure 之後都必須重新經過 `figure_reviewer`。

# 流程

## 輔助工具

Repair 需要重新裁切或建立 preview 時，只使用本 skill 內的 local helper：

- `agents/scripts/crop_region.py`：從 rendered page image 重新裁切修復後 crop、source evidence 或 edge image。
- `agents/scripts/make_image_preview.py`：建立 repair 過程中要讀取的 crop preview 和 edge previews。

不要直接呼叫 `skills/_shared/scripts/...`。Repair output 先寫在本輪 repair 目錄，canonical 更新由 parent 根據 `repair_report.json` 執行。

## 工作流程

### 準備修復資料

1. 確認 repair assignment：本輪 repair round、repair id。若未指定 repair id，使用輸出目錄名稱（例如 `repair_01`）。

2. 讀取 `repair_requests_merged.json`，只處理 `assigned_repair_id` 等於本 repair id 的 requests。不要直接把 reviewer 的 `visual_review.json` 當成主要輸入；可能有多個 reviewer 平行工作、也可能有多個 repair worker 平行修復，parent 已合併 findings 並完成分派。

3. 讀取 `canonical_artifact_root` 下和被指派 figures 相關的 artifacts：`figure_candidates.json`、`figure_index.json`、`figure_decisions.json`、`figures.json`、final crop PNG、crop preview 與 edge previews。如果 final crop PNG 或 manifest 缺失，不要自行補寫；在 `repair_report.json` 將該 request 標為 `unresolved`。如果缺的是 canonical crop preview 或 edge preview，且 request action 是 `regenerate_missing_preview`，可以從 canonical final crop PNG 重新建立缺失 preview，寫入本輪 repair 目錄，交給 parent merge。

4. 針對每個 request，確認它是否只影響被指派的 figure / crop unit：
   - 只影響被指派的 crop unit → 繼續修復。
   - 需要同步修改相鄰 figure，但相鄰 figure 不在本輪 assignment → 標 `blocked`。
   - request 指向的 figure 不存在於 canonical manifest → 標 `unresolved`。

### 讀取來源與目前裁切

5. 對每個要修復的 crop unit，從 `shared/pages/page_N.png` 建立 repair source evidence，寫入本輪 `previews/`：
   - source context preview：顯示 figure、caption 邊界、附近正文和 page chrome。
   - 四個 source edge previews（上、下、左、右）：使用目前 `crop_px`，從頁面圖片裁出跨越 crop boundary 的條帶，並用 `crop_region.py` 的 `--hline`（上下邊界）或 `--vline`（左右邊界）在 crop boundary 位置疊一條紅線。條帶必須讓紅線兩側的內容都清楚可辨。

   Repair source evidence 必須從完整解析度頁面圖片建立。不要只依賴 reviewer 或 extractor 原本提供的 framing。

6. 讀取目前 final crop preview 與四個 edge previews。若 canonical preview 缺失，只有在 request action 是 `regenerate_missing_preview` 時才重新建立缺失 preview；修復產物寫入本輪 `previews/`，不覆蓋 canonical。

### 更新裁切決策與重新裁切

7. 根據 repair request（`action` + `direction` + `constraint`）和 source evidence，決定修復動作：
   - `recrop`：更新 `crop_px`，重新裁切。
   - `manifest_correction`：修正 manifest 中的 panel list、caption_text、rationale、exclusions 或 evidence 連結；不一定需要重裁。
   - `provide_clearer_source_evidence`：建立更清楚的 bounded source preview；若仍無法判斷，標 `unresolved`。
   - `regenerate_missing_preview`：不改 crop_px，根據 request 的 `missing_canonical_artifacts[]` 從 canonical final crop PNG 重新建立缺失的 crop preview 或 edge previews，並在 `merge.file_copies[]` 中列出 parent 要搬回 canonical 的 preview 檔案。只有 manifest 裡缺少或寫錯 preview path 時才寫 `merge.manifest_patches[]`。

8. 若要重裁，決定新的 `crop_px`（完整解析度頁面圖片 pixel coordinate），用 shared crop helper 從 `shared/pages/page_N.png` 裁出，crop PNG 寫入本輪 `crops/`。不要從舊 crop、source region、preview 或其他中間圖片再裁一次。

9. 修復同一 figure 的多個 crop units 時，只修改需要修復的 crop units。未改動的 crop unit 必須保留原本的 `crop_id`、`page`、`crop_px`、`image_file`、`preview`、`edge_previews` 與 `role`。

### 修復後視覺檢查

10. 為修復後的 crop 建立 crop preview 和四個邊界預覽（上、下、左、右），寫入本輪 `previews/`。邊界預覽從頁面圖片裁出跨越新 crop boundary 的條帶，用 `--hline` 或 `--vline` 在 boundary 位置疊紅線。

11. 讀取修復後的 crop preview 和四個邊界預覽，和 source evidence 比對。逐一確認：
    - reviewer 指出的 defect 已被修復
    - figure 內容沒有被切掉
    - crop 排除外部 caption、正文、page chrome 和相鄰內容
    - 圖表型圖片的底邊與側邊完整（x 軸刻度與標題、y 軸標籤、legend、color bar、plot boundary）
    - crop 不是整頁、整欄或大頁面條帶

12. 如果修復後仍不正確，回到 step 8 調整 `crop_px`，重裁、重建 preview、重新檢查。不要直接修改 PNG，也不要只手改 `figures.json`。

13. 如果 source layout 讓 figure 內容和非 figure 內容無法乾淨分離，優先保留 figure 的全部內容，在 `repair_report.json` 標為 `unresolved`。不要為了裁掉非 figure 內容而切掉 figure 內容。

### 寫出 repair report

14. 計算每個修復後 crop PNG 的 SHA-256。

15. 寫出 `repair_report.json`。每個 repaired figure 的 `updated_crop_units[]` 必須同時記錄 repair artifact root 相對的 `repair_output`，以及 canonical artifact root 相對的 `canonical_target`。Parent 實際 merge 只看 `merge.file_copies[]` 和 `merge.manifest_patches[]`；不要讓 parent 從自然語言或 `updated_crop_units[]` 自己推理要搬什麼、patch 什麼。只要任何 assigned request 是 `unresolved`、`blocked` 或缺少必要 evidence，`repair_report.json.status` 就是 `incomplete`。

16. 回報本輪處理的 requests、repair-local artifacts、canonical targets、讀取的 previews、成功修復 / 未解決的 figures，以及 `repair_report.json` 路徑。所有改動過 crop 或 manifest 的 figure 都必須標 `requires_review: true`。

# 格式

## JSON 命名與 enum

### Artifact root 相對路徑

- `canonical_artifact_root` 是 `<paper_dir>/lanes/figures/canonical/`。
- `repair_artifact_root` 是 `<paper_dir>/lanes/figures/repairs/round_<N>/repair_<ID>/`。
- Repair 讀 canonical manifest 時，用 `canonical_artifact_root` resolve `image_file`、`preview` 和 `edge_previews`。
- `repair_report.json` 裡的 `repair_output` 使用 repair artifact root 相對路徑。
- `repair_report.json` 裡的 `canonical_target` 使用 canonical artifact root 相對路徑。
- Shared page paths 仍使用 paper-dir-relative path。從 `visual_review.json` 複製過來的 reviewer evidence path 也可以保持 paper-dir-relative path，因為它們不在 repair artifact root 裡。
- 不要在 `repair_output` 或 `canonical_target` 裡寫 `lanes/figures/canonical/`、`lanes/figures/repairs/round_<N>/repair_<ID>/` 或絕對路徑。

正確寫法：

```json
{
  "repair_output": {
    "image_file": "crops/Figure_2_part_2.png",
    "preview": "previews/Figure_2_part_2_preview.png"
  },
  "canonical_target": {
    "image_file": "crops/Figure_2_part_2.png",
    "preview": "previews/Figure_2_part_2_preview.png"
  }
}
```

### repair_requests_merged.json（輸入，parent 產生）

Parent orchestrator 從所有 reviewer 的 `visual_review.json` 中合併 fail findings，產生一份 `repair_requests_merged.json`，放在 `lanes/figures/repairs/round_<N>/repair_requests_merged.json`（round 層級，所有 repair workers 共用）。

- `repair_requests_merged.json` 使用 `schema_version: "figure_repair.v2"`。
- `repair_round` 必須和所在目錄 `round_<N>` 一致。
- `assignments[]` 告訴每個 repair worker 要處理哪些 `request_id` / `figure_id`。
- `requests[].assigned_repair_id` 必須對應某個 `assignments[].repair_id`。Repair agent 只處理 `assigned_repair_id` 等於自己的 requests。
- `requests[].figure_id` 必須對應 canonical `figures.json.figures[].figure_id`。
- `requests[].crop_ids[]` 指定要修哪些 crop units。若存在，必須對應該 figure 的 `crop_units[].crop_id`。若 request 影響整張 figure 而非特定 crop unit，`crop_ids` 為空陣列，不可省略。
- `requests[].action` 優先使用 `recrop`、`manifest_correction`、`provide_clearer_source_evidence`、`regenerate_missing_preview`；無法歸類時可自訂 snake_case action。
- `requests[].direction` 使用方向文字，例如 `expand_bottom`、`shrink_left`。若 action 不是邊界調整，或 action 是 `regenerate_missing_preview`，`direction` 為空陣列。
- `requests[].missing_canonical_artifacts[]` 只在 action 是 `regenerate_missing_preview` 時需要，列出 reviewer 發現缺失的 canonical preview 或 edge preview。每個 entry 包含 `crop_id`、`kind`、`expected_path`，若缺的是單邊 edge preview，還包含 `edge`。
- Request 不應包含 `current_crop_px`、`proposed_crop_px`、bbox array 或座標鍵。像素由 repair agent 根據來源頁面決定。

```json
{
  "schema_version": "figure_repair.v2",
  "repair_round": "round_01",
  "source_reviews": [
    "lanes/figures/reviews/round_00/reviewer_01/visual_review.json"
  ],
  "assignments": [
    {"repair_id": "repair_01", "figure_ids": ["Figure_2"], "request_ids": ["Figure_2_req001"]}
  ],
  "requests": [
    {
      "request_id": "Figure_2_req001",
      "assigned_repair_id": "repair_01",
      "figure_id": "Figure_2",
      "figure_label": "Fig. 2",
      "crop_ids": ["Figure_2_part_2"],
      "source_review": "lanes/figures/reviews/round_00/reviewer_01/visual_review.json",
      "action": "recrop",
      "direction": ["expand_bottom"],
      "constraint": "Include the missing panel B x-axis title; stop before the external caption.",
      "defects": ["Panel B bottom x-axis title is cut off."],
      "evidence_paths": [
        "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_2_source_bottom_preview.png"
      ]
    }
  ]
}
```

### repair_report.json（輸出，repair agent 產生）

最上層包含 `schema_version`、`repair_round`、`repair_id`、`status`、`source_request_file`、`repairs`、`merge`、`validation`、`summary`。

- `repair_round` 必須和所在目錄 `round_<N>` 一致；`repair_id` 必須和所在目錄 `repair_<ID>` 一致。
- `status` 使用 `complete` 或 `incomplete`。所有 assigned requests 都完成時才是 `complete`。
- `repairs[]` 的每個 entry 包含 `request_id`、`figure_id`、`figure_label`（從 extractor manifest 複製，用來讓人類快速對照圖號）、`result`、`action_taken`、`updated_crop_units`、`evidence_read`、`requires_review`、`notes`。
- `repairs[].result` 優先使用 `repaired`、`manifest_corrected`、`preview_regenerated`、`unresolved`、`blocked`；無法歸類時可自訂 snake_case value，並在 `notes` 說明。
- `repairs[].requires_review`：任何修改 crop、preview、edge preview 或 manifest 的 repair 都必須是 `true`。
- `updated_crop_units[]` 同時記錄 `repair_output`（repair artifact root 相對路徑）和 `canonical_target`（canonical artifact root 相對的 parent merge 目標路徑）。`old_crop_px` 和 `new_crop_px` 記錄在 report 中方便 trace。
- 若 action 是 `regenerate_missing_preview` 且沒有修改 crop PNG 或 crop metadata，`updated_crop_units[]` 可以是空陣列；此時必須用 `merge.file_copies[]` 列出重新產生的 previews。
- `updated_crop_units[].crop_hash`：修復後 repair-local crop PNG 的 SHA-256，格式為 `sha256:<hash>`。
- `evidence_read` 記錄 repair agent 實際讀過的 source previews、source edge previews、修復後 crop previews 和 edge previews。不要只根據 manifests 寫 `repair_report.json`。
- `merge.needs_parent_merge` 對完成或部分完成的 repair 應為 `true`。
- `merge.file_copies[]` 是 parent 實際搬檔依據。每個 entry 必須包含 `kind`、`figure_id`、`crop_id`、`repair_output`、`canonical_target`。`kind` 使用 `crop`、`crop_preview` 或 `edge_preview`。
- `merge.manifest_patches[]` 是 parent 實際 patch canonical JSON 的依據。每個 entry 必須包含 `target_file`、`operation`、`scope`、`selector`、`path`、`old_value`、`new_value`。`operation` 只使用 `replace` 或 `add_if_missing`；`add_if_missing` 的 `old_value` 使用 `null`。如果重裁改到 `crop_px`、`image_file`、`preview` 或 `edge_previews`，必須同時提供 `figures.json` 和 `figure_decisions.json` 的 patch。
- `validation.repair_self_check_status`：repair agent 的 self-check 結果（`pass` 或 `fail`）。Self-check 確認修復圖片或重新產生的 preview 存在、四個必要 edge previews 存在、paths 與 hash 可對應。
- `summary.request_count`、`summary.repaired_count`、`summary.preview_regenerated_count`、`summary.unresolved_count`、`summary.blocked_count` 必須和 `repairs[]` 一致。

```json
{
  "schema_version": "figure_repair.v2",
  "repair_round": "round_01",
  "repair_id": "repair_01",
  "status": "complete",
  "source_request_file": "lanes/figures/repairs/round_01/repair_requests_merged.json",
  "repairs": [
    {
      "request_id": "Figure_2_req001",
      "figure_id": "Figure_2",
      "figure_label": "Fig. 2",
      "result": "repaired",
      "action_taken": "recrop",
      "updated_crop_units": [
        {
          "crop_id": "Figure_2_part_2",
          "page": 4,
          "old_crop_px": [1320, 420, 2260, 1260],
          "new_crop_px": [1320, 420, 2260, 1310],
          "role": "right visual region",
          "repair_output": {
            "image_file": "crops/Figure_2_part_2.png",
            "preview": "previews/Figure_2_part_2_preview.png",
            "edge_previews": {
              "top": "previews/Figure_2_part_2_top_preview.png",
              "bottom": "previews/Figure_2_part_2_bottom_preview.png",
              "left": "previews/Figure_2_part_2_left_preview.png",
              "right": "previews/Figure_2_part_2_right_preview.png"
            }
          },
          "canonical_target": {
            "image_file": "crops/Figure_2_part_2.png",
            "preview": "previews/Figure_2_part_2_preview.png",
            "edge_previews": {
              "top": "previews/Figure_2_part_2_top_preview.png",
              "bottom": "previews/Figure_2_part_2_bottom_preview.png",
              "left": "previews/Figure_2_part_2_left_preview.png",
              "right": "previews/Figure_2_part_2_right_preview.png"
            }
          },
          "crop_hash": "sha256:a1b2c3d4e5f6..."
        }
      ],
      "evidence_read": {
        "source_previews": ["previews/Figure_2_source_context_preview.png"],
        "source_edge_previews": ["previews/Figure_2_part_2_source_bottom_preview.png"],
        "repaired_crop_previews": ["previews/Figure_2_part_2_preview.png"],
        "repaired_edge_previews": [
          "previews/Figure_2_part_2_top_preview.png",
          "previews/Figure_2_part_2_bottom_preview.png",
          "previews/Figure_2_part_2_left_preview.png",
          "previews/Figure_2_part_2_right_preview.png"
        ]
      },
      "requires_review": true,
      "notes": ["Expanded bottom crop to include missing x-axis title; external caption remains excluded."]
    }
  ],
  "merge": {
    "needs_parent_merge": true,
    "file_copies": [
      {
        "kind": "crop",
        "figure_id": "Figure_2",
        "crop_id": "Figure_2_part_2",
        "repair_output": "crops/Figure_2_part_2.png",
        "canonical_target": "crops/Figure_2_part_2.png"
      },
      {
        "kind": "crop_preview",
        "figure_id": "Figure_2",
        "crop_id": "Figure_2_part_2",
        "repair_output": "previews/Figure_2_part_2_preview.png",
        "canonical_target": "previews/Figure_2_part_2_preview.png"
      },
      {
        "kind": "edge_preview",
        "figure_id": "Figure_2",
        "crop_id": "Figure_2_part_2",
        "repair_output": "previews/Figure_2_part_2_top_preview.png",
        "canonical_target": "previews/Figure_2_part_2_top_preview.png"
      },
      {
        "kind": "edge_preview",
        "figure_id": "Figure_2",
        "crop_id": "Figure_2_part_2",
        "repair_output": "previews/Figure_2_part_2_bottom_preview.png",
        "canonical_target": "previews/Figure_2_part_2_bottom_preview.png"
      },
      {
        "kind": "edge_preview",
        "figure_id": "Figure_2",
        "crop_id": "Figure_2_part_2",
        "repair_output": "previews/Figure_2_part_2_left_preview.png",
        "canonical_target": "previews/Figure_2_part_2_left_preview.png"
      },
      {
        "kind": "edge_preview",
        "figure_id": "Figure_2",
        "crop_id": "Figure_2_part_2",
        "repair_output": "previews/Figure_2_part_2_right_preview.png",
        "canonical_target": "previews/Figure_2_part_2_right_preview.png"
      }
    ],
    "manifest_patches": [
      {
        "target_file": "figures.json",
        "operation": "replace",
        "scope": "crop_unit",
        "selector": {"figure_id": "Figure_2", "crop_id": "Figure_2_part_2"},
        "path": "crop_units[].crop_px",
        "old_value": [1320, 420, 2260, 1260],
        "new_value": [1320, 420, 2260, 1310]
      },
      {
        "target_file": "figure_decisions.json",
        "operation": "replace",
        "scope": "crop_unit",
        "selector": {"figure_id": "Figure_2", "crop_id": "Figure_2_part_2"},
        "path": "crop_units[].crop_px",
        "old_value": [1320, 420, 2260, 1260],
        "new_value": [1320, 420, 2260, 1310]
      }
    ],
    "canonical_mechanical_validation_required_after_merge": false,
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

### canonical JSON

- Canonical `figure_decisions.json` 和 `figures.json` 仍使用 `schema_version: "figure_extraction.v2"`。
- Repair agent 不直接覆蓋 canonical JSON；`repair_report.json` 的 `merge.file_copies[]` 和 `merge.manifest_patches[]` 提供 parent merge 所需的全部資訊。
- 裁切座標只叫 `crop_px`，不要寫成 `crop`、`crop_bbox` 或 `crop_region`。最終裁切圖片路徑只叫 `image_file`，只放在 `crop_units[]` 裡，不要使用 `file`、`output_file`、`output_image`。
- `figure_id` 和 `crop_id` 必須保持不變。只有新增或拆分 crop unit 時才新增新的 `crop_id`。
- Parent merge 後，`figure_decisions.json` 和 `figures.json` 的 `crop_units[]` 必須完全一致。
- Figure 層不寫可由 `crop_units[]` 推得的彙總欄位（`pages`、`image_files`、`crop_count`）。

### figure_index.json

- 預設不修改 `figure_index.json`。Repair 的主要任務是修 crop / manifest，不是重建 figure inventory。
- 只有在 repair request 明確要求 `manifest_correction`，且錯誤限於已指派 figure 的 label、caption_text、candidate link 或 source_region link 時，repair agent 才能在 `repair_report.json` 提出 `figure_index.json` 更新建議。
- 不要自行新增全新 figure、刪除既有 figure 或重排整份 index。這類問題應標 `blocked` / `unresolved`，交回 orchestrator 或 extractor。

# 圖片檔案

Repair 使用三類圖片：來源頁面圖片、canonical 目前狀態，以及 repair-local 修復產物。所有給 agent 讀的圖片都必須是 preview，檔名含 `_preview`，並符合讀圖尺寸限制。

- 頁面圖片：`shared/pages/page_4.png`
  - 角色：來源真相。不直接讀完整解析度頁面圖片，從它建立 bounded previews。
- repair source context preview：`previews/Figure_2_source_context_preview.png`
  - 角色：從頁面圖片建立，顯示 figure 在頁面中的上下文。
- repair source edge preview：`previews/Figure_2_part_2_source_bottom_preview.png`
  - 角色：從頁面圖片裁出跨越 crop boundary 的條帶，在 boundary 位置疊紅線。用來判斷目前或新 crop 邊界是否切掉內容。
- repair-local crop：`crops/Figure_2_part_2.png`
  - 角色：修復後的成果本體。Parent merge 後複製到 canonical。
- repair-local crop preview：`previews/Figure_2_part_2_preview.png`
  - 角色：修復後 crop 的受限尺寸預覽。Parent merge 後複製到 canonical preview 目標路徑。
- repair-local edge preview：`previews/Figure_2_part_2_bottom_preview.png`
  - 角色：修復後 crop 的邊界條帶，從頁面圖片裁出、含紅色 boundary line。

# 規則

## 權責

- `figure_repair` 只修復 assigned repair requests。不重新執行 initial extraction，不重新建立完整 figure inventory，不做 final independent review。
- 不直接覆蓋 `lanes/figures/canonical/`；修復圖片、preview 和 merge 所需資訊先寫在本輪 repair 目錄。Canonical 更新由 parent 負責。
- 不修改來源 PDF、reviewer output、`repair_requests_merged.json`、`before_snapshot.json`、`after_snapshot.json`。
- 任何 canonical artifact 經 parent merge 修改後，對應 figure 先前的 review 都失效，必須重新跑 `figure_reviewer`。
- Helper 可以裁切、建立 preview、檢查檔案、標記幾何風險；但 helper、validator、manifest 和 crop coordinate 都不能替 agent 判定 visual quality。`repaired` 必須由 agent 讀過 source evidence、修復後 crop preview 和四邊 edge previews 後判斷。

## 修復範圍

- 只處理 `repair_requests_merged.json` 中分派給本 `repair_id` 的 requests。不要因為 merged file 裡還有其他 failed requests 就順手修。
- 如果 request 需要改到相鄰 figure，但相鄰 figure 未被指派，標 `blocked`。
- 修復同一 figure 的多個 crop units 時，只修改需要修復的 crop units。未改動的 crop unit 必須保留原本的所有欄位。
- 如果需要新增或移除 crop unit，保留同一個 `figure_id`，在 `repair_report.json` 記錄 parent merge 應如何同步更新。新增 crop unit 的 `crop_id` 必須 filename-safe 且不與既有 `crop_id` 衝突。

## 裁切與座標

- 所有 `crop_px` 都使用完整解析度頁面圖片的 pixel coordinate。
- Final crop 永遠從 `shared/pages/page_N.png` 裁出，不要從 source region、preview、edge strip 或其他中間圖片再裁一次。
- 座標換算時，邊界應保守外擴：左上角向外取整，右下角向外取整，再用邊界預覽收緊。

## 圖說與圖片邊界

- 外部 caption 存在 `caption_text`，不放進 crop。
- Figure-internal title、legend、axis label、panel label、scale bar、color bar、annotation 應保留在 crop 中。
- 排除正文、外部 caption、頁碼、頁眉、頁腳、期刊固定元素、浮水印、相鄰 figure、table、equation 與其他非 figure 內容。
- 如果非 figure 內容碰邊就縮小 crop，figure 內容碰邊就放大 crop。如果兩者因版面交錯無法乾淨分離，優先保留 figure 的全部內容，標 `unresolved`。不要為了裁掉非 figure 內容而切掉 figure 內容。

## 視覺檢查

- 每個標為 `repaired` 的 figure，repair agent 都必須讀過 source evidence、修復後 crop preview、以及四個 edge previews。
- 每個標為 `preview_regenerated` 的 figure，repair agent 至少必須確認缺失的 preview/edge preview 已在 repair 目錄產生、可讀取，且列入 `merge.file_copies[]`。
- 不要因為 crop「大致可以」就標 `repaired`。不確定就是 `unresolved`。
- 圖表型圖片的底邊與側邊風險最高：必須確認 x 軸刻度與標題、y 軸標籤、legend、color bar 和 plot boundary 完整。
- 大幅寬圖可以接近整頁寬度，但垂直方向仍應緊貼 figure；不得用整頁、整欄或大頁面條帶假裝修復成功。

## Manifest 一致性

- `repair_report.json` 的 `merge.manifest_patches[]` 必須足以讓 parent 將 canonical `figure_decisions.json` 和 `figures.json` 更新到一致狀態；`updated_crop_units[]` 只作為 trace，不能取代 machine-readable patches。
- 不要留下 stale `crop_px`、stale `image_file`、stale `preview` 或 stale `edge_previews`。
- `repair_report.json` 是修復 trace 和 parent merge input，不是 canonical truth；parent merge 後的 final truth 以 canonical `figure_decisions.json`、`figures.json` 和實際 PNG 檔案為準。

## 機械驗證

- Repair agent 可以做 repair-local self-check：確認修復圖片或重新產生的 preview 存在、四個必要 edge previews 存在、`repair_report.json` 中的 paths 與 hash 可對應。
- 第一階段不要求 parent merge 後執行 canonical mechanical validation；canonical validation 留到第二階段。
- Mechanical validation 通過不代表 final visual acceptance；最終接受判定由 parent 透過 `figure_reviewer` 執行。
- Parent merge 後必須重新跑 `figure_reviewer`，因為改動過 crop 或 manifest 的 figure 先前 review 已失效。
- 如果 repair-local self-check 失敗，先修 artifact 再標 `complete`；若無法修，`repair_report.json.status` 必須是 `incomplete`。
