# 目標

這是一份給 `equation_repair` agent 看的指引。

Repair 讀取 assignment 指定的 repair request，修復被指派的方程式——可能是 crop 邊界問題，也可能是 LaTeX 問題。修復後的 artifacts 寫在本輪 repair 目錄。Repair 不直接寫 canonical，也不做最終接受判定——那是下一輪 reviewer 的工作。

- 輸入：repair request、canonical evidence 圖片、完整解析度頁面圖片、canonical `equations.json`。
- 輸出：修復後的 crops / previews / boundaries / rendered_latex、`decisions.json`、`equation_repair_report.json`。
- 輸出位置：`<paper_dir>/equations/repairs/round_<N>/repair_<ID>/`

# 流程

## 輔助工具

- `agents/scripts/crop_and_preview.py`：裁切 + 全套 edge evidence preview。recrop action 使用。
- `agents/scripts/render_latex_preview.py`：渲染修正後的 LaTeX。fix_latex action 使用。
- `agents/scripts/make_image_preview.py`：建立單張 preview。
- `agents/scripts/validate_figure_repair.py`：暫用 figure repair validator 做基本 contract check（equation-specific validator 尚未建立）。

不要直接呼叫 `skills/_shared/scripts/...`。Repair output 先寫在本輪 repair 目錄；不要直接更新 canonical。

## Step 1: 準備修復資料



a) 確認 assignment：`repair_round`、`repair_id`、`canonical_artifact_root`、`repair_artifact_root`、`request_file`。

b) 讀取 `request_file`。只處理分派給本 repair_id 的 requests。

c) 讀取 canonical `equations.json`，查看需要修復的方程式的 metadata（crop_px、page、latex、equation_number）。

d) **[judgment]** 對每個 request 做 preflight：只影響被指派的方程式 → 繼續。需要改相鄰方程式但不在 assignment → `blocked`。方程式不存在於 canonical → `unresolved`。

## Step 2: 讀取 canonical evidence



對每個要修復的方程式，讀取 canonical evidence：crop preview、boundary preview、edge strips、bottom band、bottom micro、rendered LaTeX preview。

## Step 3: 決定修復

**[judgment]**

Equation repair 有兩類 action：

### Crop 修復（和 figure repair 相同邏輯）

- `recrop`：調整 crop_px，重新裁切。
- 座標規則：所有 crop_px 用完整解析度頁面圖片 pixel coordinate。Final crop 永遠從 page image 裁出。
- 方程式邊界：方程式可見內容（數學符號、編號）保留在 crop 中。周圍正文排除。

### LaTeX 修復（equation 獨有）

- `fix_latex`：修正 LaTeX 字串中的符號、結構或對齊問題。
- 從 crop preview 和 source region preview 重新視覺轉寫有問題的部分。
- 修正後重新渲染 LaTeX preview，和 crop preview 比對確認。
- LaTeX 規則同 extractor：保留分式、上下標、根號、矩陣、分段函數、重音變體。

### 同時修復

同一方程式可能同時需要 recrop 和 fix_latex。先修 crop（因為 LaTeX 要從正確的 crop 轉寫），再修 LaTeX。

修復同一方程式的多個 crop units 時，只修改需要修復的 crop units。

## Step 4: 修復後視覺檢查

a) **[script]** Crop 修復後用 `crop_and_preview.py` 重建全套 evidence。LaTeX 修復後用 `render_latex_preview.py` 重新渲染。

b) **[judgment]** 讀取修復後 evidence，和 Step 2 的 canonical evidence 對照：
   - Reviewer finding 指出的 defect 已被處理。
   - Crop 邊界乾淨（同 figure 的 cyan 線規則）。
   - LaTeX 準確反映 crop 中可見的數學結構。
   - Rendered LaTeX preview 和 crop preview 視覺一致。

c) **[judgment]** 不正確 → 回到 Step 3 調整。不要直接修改 PNG。

d) **[judgment]** 版面限制導致無法乾淨分離 → 優先保留方程式全部內容，標 `unresolved`。

## Step 5: 寫出 repair report



a) 為每個處理過的 request 寫一筆 decision 到 `decisions.json`：

    ```json
    [
      {
        "request_id": "Equation_3_f001",
        "equation_id": "Equation_3",
        "result": "repaired",
        "action_taken": "recrop",
        "new_crop_px": [120, 450, 2380, 520],
        "notes": ["Expanded bottom to include subscript"]
      },
      {
        "request_id": "Equation_5_f002",
        "equation_id": "Equation_5",
        "result": "repaired",
        "action_taken": "fix_latex",
        "new_latex": "\\widehat{XY} = \\sum_{i=1}^{n} x_i",
        "notes": ["Changed \\hat{XY} to \\widehat{XY} — accent spans two characters"]
      }
    ]
    ```

    `new_crop_px` 用於 recrop action。`new_latex` 用於 fix_latex action。兩者可同時出現（同時修 crop 和 LaTeX）。`result: "unresolved"` / `"blocked"` 時不需要這些欄位。

b) 手動組裝 `equation_repair_report.json`（equation-specific repair report assembler 尚未建立）。包含 `repairs[]`、`merge.file_copies[]`、`merge.manifest_patches[]`（target `equations.json`）、`summary`。

c) Self-check：JSON 可 parse、修復後的 crop / preview / rendered LaTeX 存在、summary counts 正確。

d) 回報結果。

### decisions.json

#### Enums

- `result`：
  - `repaired`：crop 或 LaTeX 已修復
  - `unresolved`：無法修復（版面限制、evidence 不足等）
  - `blocked`：需要改相鄰方程式但不在 assignment
- `action_taken`：
  - `recrop`：調整 crop_px，重新裁切
  - `fix_latex`：修正 LaTeX 字串
  - `recrop_and_fix_latex`：同時修 crop 和 LaTeX

#### Fields

- `decisions[]`：
  - `request_id`：對應 repair request 的 finding_id
  - `equation_id`
  - `result`
  - `action_taken`
  - `new_crop_px`：[x1,y1,x2,y2]，recrop 時必填。完整解析度頁面圖片 pixel coordinate。
  - `new_latex`：string，fix_latex 時必填。不含方程式編號，不含 `$` 包裹。
  - `notes`：string array

### equation_repair_report.json

`schema_version: "equation_repair.v1"`

#### Enums

- `status`：`complete`（所有 request 完成）| `incomplete`（有 unresolved 或 blocked）
- `repairs[].result`：`repaired` | `unresolved` | `blocked`
- `merge.file_copies[].kind`：`crop` | `crop_preview` | `boundary_preview` | `top_band` | `left_band` | `right_band` | `bottom_band` | `bottom_micro` | `rendered_latex_preview`
- `merge.manifest_patches[].operation`：`replace` | `add_if_missing`
- `merge.manifest_patches[].target_file`：`equations.json`

#### Fields

- `repair_round`、`repair_id`、`status`、`source_request_file`
- `repairs[]`：
  - `request_id`、`equation_id`
  - `result`、`action_taken`
  - `updated_crop_units[]`：
    - `crop_id`、`page`、`old_crop_px`、`new_crop_px`、`role`
    - `repair_output`：map with `image_file`、`preview`、`boundary_preview`、`top_band`、`left_band`、`right_band`、`bottom_band`、`bottom_micro`（all repair-root-relative）
    - `canonical_target`：same structure（canonical-root-relative）
  - `updated_latex`：（fix_latex 時）`old_latex`、`new_latex`、`rendered_latex_preview`（repair-root-relative）
  - `requires_review`：bool（修改了 crop / LaTeX → must be `true`）
  - `notes`：string array
- `merge`：
  - `needs_parent_merge`：bool
  - `file_copies[]`：`kind`、`equation_id`、`crop_id`、`repair_output`（repair-root-relative）、`canonical_target`（canonical-root-relative）
  - `manifest_patches[]`：`target_file`、`operation`、`scope`、`selector`（{equation_id, crop_id}）、`path`、`old_value`、`new_value`
- `summary`：`request_count`、`repaired_count`、`unresolved_count`、`blocked_count`

# 格式

## Artifact root 相對路徑

- `canonical_artifact_root`：`<paper_dir>/equations/canonical/`
- `repair_artifact_root`：`<paper_dir>/equations/repairs/round_<N>/repair_<ID>/`
- `repair_output` 使用 repair artifact root 相對路徑。
- `canonical_target` 使用 canonical artifact root 相對路徑。
- 不要在路徑裡寫完整目錄前綴或絕對路徑。

# 規則

## 權責

- 只修復 assigned repair requests。
- 不重新執行 extraction，不重建方程式 inventory。
- 不直接覆蓋 canonical。
- 不修改來源 PDF、canonical review、canonical repair request。
- 任何 canonical artifact 被修改後，先前 review 失效，必須重新 review。

## 修復範圍

- 只處理分派給本 repair_id 的 requests。
- 相鄰方程式需要改但不在 assignment → `blocked`。
- 同方程式多個 crop units 時，只改需要修復的。
- LaTeX 修正只改有問題的部分，不重寫整個 LaTeX。

## 視覺檢查

- `repaired` 的方程式必須讀過 canonical evidence 和修復後 evidence。
- Crop 修復後確認邊緣乾淨。
- LaTeX 修復後確認 rendered preview 和 crop 視覺一致。
- 不確定 → `unresolved`。
