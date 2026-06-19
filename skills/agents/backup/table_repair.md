# 目標

這是一份給 `table_repair` agent 看的指引。

Repair 讀取 assignment 指定的 repair request，修復被指派的表格——可能是 crop 邊界問題，也可能是結構化 JSON 問題（儲存格文字、標題結構、註腳）。修復後的 artifacts 寫在本輪 repair 目錄。Repair 不直接寫 canonical，也不做最終接受判定。

- 輸入：repair request、canonical evidence 圖片、完整解析度頁面圖片、canonical `tables.json` 和 `Table_<N>.json`。
- 輸出：修復後的 crops / previews / boundaries / `Table_<N>.json` / rendered_tables、`decisions.json`、`table_repair_report.json`。
- 輸出位置：`<paper_dir>/tables/repairs/round_<N>/repair_<ID>/`

# 流程

## 輔助工具

- `agents/scripts/crop_and_preview.py`：裁切 + 全套 edge evidence preview。recrop action 使用。
- `agents/scripts/render_table_preview.py`：渲染修正後的結構化 JSON。fix_structure action 使用。
- `agents/scripts/make_image_preview.py`：建立單張 preview。

不要直接呼叫 `skills/_shared/scripts/...`。Repair output 先寫在本輪 repair 目錄；不要直接更新 canonical。

## Step 1: 準備修復資料

a) 確認 assignment 參數。

b) 讀取 `request_file`。只處理分派給本 repair_id 的 requests。

c) 讀取 canonical `tables.json` 和需要修復的表格的 `Table_<N>.json`。

d) **[judgment]** 對每個 request 做 preflight：只影響被指派的表格 → 繼續。需要改相鄰表格但不在 assignment → `blocked`。表格不存在於 canonical → `unresolved`。

## Step 2: 讀取 canonical evidence



對每個要修復的表格，讀取 canonical evidence：crop preview、boundary preview、edge strips、bottom band、bottom micro、rendered table preview、source region preview。

## Step 3: 決定修復

**[judgment]**

Table repair 有兩類 action：

### Crop 修復（和 figure repair 相同邏輯）

- `recrop`：調整 crop_px，重新裁切。
- 座標規則同 figure：完整解析度 pixel coordinate，從 page image 裁出。
- 表格邊界：表格可見內容（標籤、標題、欄標題、資料列、註腳）保留在 crop 中。周圍正文排除。

### 結構修復（table 獨有）

- `fix_structure`：修正結構化 JSON 中的問題。可能的修正包括：
  - `split_header_level`：把壓平的多層標題拆開。
  - `merge_wrapped_cell`：把被錯誤拆成假列的換行儲存格合回。
  - `split_false_row`：把被錯誤合併的列拆開。
  - `correct_cell_text`：修正儲存格文字（從 crop preview 重新讀取）。
  - `add_missing_footnote`：加入遺漏的註腳。
  - `fix_title_separator`：修正標題分隔符。
  - `fix_sub_column`：修正子欄結構。

- 從 crop preview 和 source region preview 重新視覺確認有問題的部分。
- 修正後重新渲染 table preview，和 crop preview / source 比對確認。
- **文字保留規則**：保留來源原文，包括錯字。不靜默修正。

### 同時修復

同一表格可能同時需要 recrop 和 fix_structure。先修 crop（因為結構要從正確的 crop 讀取），再修結構。

## Step 4: 修復後視覺檢查

a) **[script]** Crop 修復後用 `crop_and_preview.py` 重建全套 evidence。結構修復後用 `render_table_preview.py` 重新渲染。

b) **[judgment]** 讀取修復後 evidence，和 Step 2 的 canonical evidence 對照：
   - Reviewer finding 指出的 defect 已被處理。
   - Crop 邊界乾淨。
   - 結構化 JSON 準確反映表格結構和逐字內容。
   - Rendered table preview 和 crop / source 結構一致。

c) **[judgment]** 不正確 → 回到 Step 3 調整。

d) **[judgment]** 版面限制導致無法乾淨分離 → 優先保留表格全部內容，標 `unresolved`。

## Step 5: 寫出 repair report

a) 為每個處理過的 request 寫一筆 decision 到 `decisions.json`：

    ```json
    [
      {
        "request_id": "Table_2_f001",
        "table_id": "Table_2",
        "result": "repaired",
        "action_taken": "recrop",
        "new_crop_px": [55, 200, 2400, 1800],
        "notes": ["Expanded bottom to include last footnote row"]
      },
      {
        "request_id": "Table_2_f002",
        "table_id": "Table_2",
        "result": "repaired",
        "action_taken": "fix_structure",
        "structure_corrections": {
          "type": "correct_cell_text",
          "row": 3,
          "column": "Dose",
          "old_value": "10 mg/kq",
          "new_value": "10 mg/kg"
        },
        "notes": ["Fixed misread character: 'q' → 'g'"]
      }
    ]
    ```

    `new_crop_px` 用於 recrop action。`structure_corrections` 用於 fix_structure action。`result: "unresolved"` / `"blocked"` 時不需要這些欄位。

b) 手動組裝 `table_repair_report.json`（table-specific repair report assembler 尚未建立）。包含 `repairs[]`、`merge.file_copies[]`（crop + previews + `Table_<N>.json`）、`merge.manifest_patches[]`（target `tables.json`）、`summary`。

c) Self-check：JSON 可 parse、修復後的 crop / preview / rendered table / `Table_<N>.json` 存在、summary counts 正確。

d) 回報結果。

### decisions.json

#### Enums

- `result`：
  - `repaired`：crop 或結構已修復
  - `unresolved`：無法修復
  - `blocked`：需要改相鄰表格但不在 assignment
- `action_taken`：
  - `recrop`：調整 crop_px，重新裁切
  - `fix_structure`：修正結構化 JSON 中的問題
  - `recrop_and_fix_structure`：同時修 crop 和結構

#### Fields

- `decisions[]`：
  - `request_id`：對應 repair request 的 finding_id
  - `table_id`
  - `result`
  - `action_taken`
  - `new_crop_px`：[x1,y1,x2,y2]，recrop 時必填
  - `structure_corrections`：fix_structure 時必填。包含：
    - `type`：`correct_cell_text` | `split_header_level` | `merge_wrapped_cell` | `split_false_row` | `add_missing_footnote` | `fix_title_separator` | `fix_sub_column`
    - `row`：int（affected row index，如適用）
    - `column`：string（affected column name，如適用）
    - `old_value`：string（修正前的值）
    - `new_value`：string（修正後的值）
    - 或其他 type-specific 欄位（如 `header_level_index`、`footnote_text`）
  - `notes`：string array

### table_repair_report.json

`schema_version: "table_repair.v1"`

#### Enums

- `status`：`complete`（所有 request 完成）| `incomplete`（有 unresolved 或 blocked）
- `repairs[].result`：`repaired` | `unresolved` | `blocked`
- `merge.file_copies[].kind`：`crop` | `crop_preview` | `boundary_preview` | `top_band` | `left_band` | `right_band` | `bottom_band` | `bottom_micro` | `structured_json` | `rendered_table_preview`
- `merge.manifest_patches[].operation`：`replace` | `add_if_missing`
- `merge.manifest_patches[].target_file`：`tables.json`

#### Fields

- `repair_round`、`repair_id`、`status`、`source_request_file`
- `repairs[]`：
  - `request_id`、`table_id`
  - `result`、`action_taken`
  - `updated_crop_units[]`：
    - `crop_id`、`page`、`old_crop_px`、`new_crop_px`、`role`
    - `repair_output`：map with `image_file`、`preview`、`boundary_preview`、`top_band`、`left_band`、`right_band`、`bottom_band`、`bottom_micro`（all repair-root-relative）
    - `canonical_target`：same structure（canonical-root-relative）
  - `updated_structure`：（fix_structure 時）
    - `table_json_repair_output`：repair-root-relative path to modified `Table_N.json`
    - `table_json_canonical_target`：canonical-root-relative path
    - `rendered_table_preview`：repair-root-relative path to re-rendered preview
    - `corrections_applied`：array of `structure_corrections` from decisions
  - `requires_review`：bool（修改了 crop / structure → must be `true`）
  - `notes`：string array
- `merge`：
  - `needs_parent_merge`：bool
  - `file_copies[]`：`kind`、`table_id`、`crop_id`（crop kinds）或 `table_id`（structured_json kind）、`repair_output`、`canonical_target`
  - `manifest_patches[]`：`target_file`、`operation`、`scope`、`selector`、`path`、`old_value`、`new_value`
- `summary`：`request_count`、`repaired_count`、`unresolved_count`、`blocked_count`

# 格式

## Artifact root 相對路徑

- `canonical_artifact_root`：`<paper_dir>/tables/canonical/`
- `repair_artifact_root`：`<paper_dir>/tables/repairs/round_<N>/repair_<ID>/`
- `repair_output` 使用 repair artifact root 相對路徑。
- `canonical_target` 使用 canonical artifact root 相對路徑。
- 不要在路徑裡寫完整目錄前綴或絕對路徑。

# 規則

## 權責

- 只修復 assigned repair requests。
- 不重新執行 extraction，不重建表格 inventory。
- 不直接覆蓋 canonical。
- 不修改來源 PDF、canonical review、canonical repair request。
- 任何 canonical artifact 被修改後，先前 review 失效，必須重新 review。

## 修復範圍

- 只處理分派給本 repair_id 的 requests。
- 相鄰表格需要改但不在 assignment → `blocked`。
- 結構修正只改有問題的部分，不重寫整個 `Table_<N>.json`。
- **文字保留規則**：修正時仍保留來源原文（含錯字）。只修正擷取錯誤（misread），不修正來源錯誤。

## 視覺檢查

- `repaired` 的表格必須讀過 canonical evidence 和修復後 evidence。
- Crop 修復後確認邊緣乾淨。
- 結構修復後確認 rendered preview 和 crop / source 一致。
- 不確定 → `unresolved`。
