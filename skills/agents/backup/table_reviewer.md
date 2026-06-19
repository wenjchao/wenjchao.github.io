# 目標

這是一份給 `table_reviewer` agent 看的指引。

Reviewer 讀取 extractor 建好的 canonical evidence，判斷每個表格的 crop 和結構化 JSON 能不能用。

Reviewer 同時檢查兩件事：
1. **Crop 邊界**：表格是否完整、邊緣是否乾淨（和 figure review 相同邏輯）。
2. **結構準確度**：結構化 JSON 是否準確反映來源表格的 header/body/footnote 結構和逐字內容（table 獨有）。

- 輸入：review_packet、canonical evidence 圖片。
- 輸出：`table_visual_review.json`（per-table pass/fail、edge_checks、structure checks、findings）。
- 輸出位置：`<paper_dir>/tables/reviewers/round_<N>/reviewer_<ID>/`

Reviewer 不修改 crop、不修改 `Table_<N>.json`、不修改 canonical。只要不確定，就標 `fail`。

# 流程

## Step 1: 準備審查資料

a) 確認 assignment 參數和 review_packet 路徑。

b) 讀取 review_packet。每個表格有 crop_preview、boundary_preview、edge strips、bottom band/micro、rendered_table_preview 等路徑。

c) Preflight：確認 evidence 檔案都存在。缺失 → `fail`，finding 用 `problem: "missing_evidence"`。

## Step 2: 觀看 evidence，建立 structural inventory

a) **[judgment]** 對每個表格，讀取 canonical evidence：
   - **Crop preview**：表格全貌。
   - **Boundary preview**：整體 framing。
   - **Edge strips / bottom band / bottom micro**：逐邊精確檢查。
   - **Rendered table preview**：結構化 JSON 渲染後的視覺結果。
   - **Source region preview**：來源頁面中的表格區域。

b) **[judgment]** 從**來源頁面 evidence** 建立 structural inventory：列數、欄數、標題層數、註腳數。再從**結構化 JSON / rendered table preview** 建立同樣的 inventory。兩份 inventory 必須一致，不一致 → `fail`。

## Step 3: 逐邊檢查（crop 邊界）

**[judgment]** 和 figure reviewer 相同的 cyan 線規則。

### 核心規則

Cyan 線切過的區域必須是一片空白。表格內容不可以穿過 cyan 線。周圍正文、page chrome 也不可以穿過 cyan 線。

### 整體 framing（boundary preview）

a) **[judgment]** 確認 cyan 矩形框住完整表格（標題到最後一個註腳）。特別注意：
   - **上邊**：表格標籤上方不能包含期刊頁首、running title、頁碼或分隔線。
   - **下邊**：最後一個註腳下方不能包含頁碼、正文、出版商頁尾或 logo。
   - **左/右邊**：不能包含頁邊註記、相鄰表格內容或欄位外溢。

### Top / left / right（edge strip）

b) **[judgment]** 逐一看 edge strip，記錄 `boundary_content`（`seg1` key）。

### Bottom（bottom band + microzoom）

c) **[judgment]** 逐一看底邊 microzoom，記錄 `boundary_content`（`micro_seg` key）。

### 記錄格式

每條邊必須記錄 `boundary_content`、`status`、`condition`、`notes`。

## Step 4: 結構檢查

**[judgment]** — Table 獨有的檢查。

a) **[judgment]** 逐項比對結構化 JSON 和來源：

   - 表號和表題完整且正確。
   - 標題分隔符（句點、破折號、冒號）與來源完全一致。
   - 所有標題層級、跨欄標題、列標籤、單位和註腳標記都已表示。
   - 列數和欄數符合來源。
   - 換行儲存格沒有被拆成假列。
   - 所有正文儲存格依來源順序出現。
   - **標題和儲存格文字逐字元符合來源**，包括原始錯字或拼字錯誤。不得通過已「修正」來源文字的表格。
   - 符號、不等式、上標/註腳標記和單位都已保留。
   - 註腳文字開頭的標記與儲存格/標題中的標記一致。
   - 所有表格註腳都已擷取。
   - 如果來源第一欄有「類別 + 具體項目」的雙層結構，確認擷取結果把兩部分分成不同欄。

b) **[judgment]** Rendered table preview 和 crop preview / source 的結構必須一致。

## Step 5: 判定

a) **[judgment]** 表格只有在下列全部成立時才 `pass`：
   - Structural inventory 一致（列/欄/標題層/註腳數）。
   - 四邊 edge_checks 全部 pass。
   - 結構化 JSON 逐字元準確。
   - Rendered preview 和來源結構一致。
   - 沒有未解決不確定性。

   不確定就是 `fail`。

b) **[judgment]** `fail` 時寫 `findings[]`。每個 finding 記錄：
   - `table_id`。
   - `problem`：crop 問題用 `content_cut`、`external_content_visible` 等。結構問題用 `header_level_error`、`false_row_split`、`wrapped_cell_split`、`cell_text_error`、`missing_footnote`、`footnote_marker_mismatch`、`title_separator_error`、`sub_column_error`。
   - `edge`（crop 問題）或 `null`（結構問題）。
   - `repair_hint`：crop 方向用 `expand_*`/`shrink_*`/`recrop`。結構修正用 `split_header_level`、`merge_wrapped_cell`、`split_false_row`、`correct_cell_text`、`add_missing_footnote`、`fix_title_separator`、`fix_sub_column`。
   - `notes`：具體說明。

c) **[judgment]** Reviewer 不提供修復座標，不提供修正後的 JSON。

d) Self-check：summary counts 正確、每個表格有 edge_checks 和 structure check、pass 表格沒有 failed edge 或結構錯誤、fail 表格至少一個 finding。

## Step 6: 輸出

a) 寫 `table_visual_review.json`（`schema_version: "table_review.v1"`）。

b) **[script]** 寫完後必須執行 mandatory 機械自檢：

   ```bash
   python3 agents/scripts/validate_table_review.py \
     "<output_root>/table_visual_review.json"
   ```

   若 validator 回傳 `status: "fail"`，修正欄位名、缺失區塊或 summary counts 後重寫重跑。Validator 通過前不得回報 review 完成。

   此 validator 檢查：schema_version、status/decision enum 值、每個 table 有 `reviewed_crop_units`/`structural_inventory`/`edge_checks`/`structure_check` 四個必填區塊、findings 有 `finding_id`/`table_id`/`problem`/`repair_hint`/`severity`/`notes`、summary counts 一致。不判斷邊界或結構是否正確。

### table_visual_review.json

#### Enums

- `decision`：`pass` | `fail`
- `status`：`pass`（全部通過）| `fail`（任一 fail）
- `condition`（建議值，可自訂 snake_case）：
  - `clean_margin`：crop edge 在表格內容之外，邊緣乾淨
  - `content_cut`：表格內容被切掉
  - `page_chrome_visible`：頁碼、頁眉等出現在 crop 內
  - `body_text_visible`：正文出現在 crop 內
  - `adjacent_content_visible`：相鄰表格或其他無關內容出現在 crop 內
  - `unknown`：evidence 不足
- `problem`（建議值，可自訂 snake_case）：
  - Crop 問題：
    - `content_cut`：表格內容被某條邊切掉
    - `external_content_visible`：正文或非表格內容被裁進 crop
    - `page_chrome_visible`：頁碼、頁眉等被裁進 crop
    - `missing_evidence`：必要 preview 缺失
  - 結構問題：
    - `header_level_error`：標題層級不正確（壓平或遺漏跨欄標題）
    - `false_row_split`：換行儲存格被拆成假列
    - `wrapped_cell_split`：同上（換行儲存格錯誤拆分）
    - `cell_text_error`：儲存格文字和來源不一致
    - `missing_footnote`：遺漏表格註腳
    - `footnote_marker_mismatch`：註腳文字開頭標記和儲存格中的標記不一致
    - `title_separator_error`：標題分隔符不正確
    - `sub_column_error`：子欄結構不正確
    - `row_count_mismatch`：列數和來源不一致
    - `column_count_mismatch`：欄數和來源不一致
- `repair_hint`：
  - Crop 方向：`expand_top` | `expand_bottom` | `expand_left` | `expand_right` | `shrink_top` | `shrink_bottom` | `shrink_left` | `shrink_right` | `recrop`
  - 結構修正：
    - `split_header_level`：把壓平的多層標題拆開
    - `merge_wrapped_cell`：把被錯誤拆成假列的換行儲存格合回
    - `split_false_row`：把被錯誤合併的列拆開
    - `correct_cell_text`：修正儲存格文字
    - `add_missing_footnote`：加入遺漏的註腳
    - `fix_title_separator`：修正標題分隔符
    - `fix_sub_column`：修正子欄結構
- `severity`：`required`（影響正確性）| `advisory`（不影響正確性的可選整理）

#### Fields

- `review_round`、`reviewer_id`
- `status`：`fail` if any table fails
- `tables[]`：
  - `table_id`、`table_label`、`decision`
  - `reviewed_crop_units[]`：`crop_id`、`crop_preview`、`boundary_preview`、`top_band`、`left_band`、`right_band`、`bottom_band`、`bottom_micro`、`rendered_table_preview`
  - `structural_inventory`：
    - `expected`：`rows`（int）、`columns`（int）、`header_levels`（int）、`footnotes`（int）— 從來源頁面計數
    - `observed`：同上 — 從結構化 JSON 計數
    - `match`：bool — 兩者是否一致
  - `edge_checks.crop_units[]`：
    - `crop_id`
    - `edges.{top,bottom,left,right}`：
      - `boundary_content`：structured observation。Bottom 用 `micro_seg1` 等做 key；top/left/right 用 `seg1`。
      - `status`：`pass` | `fail`
      - `condition`
      - `notes`：必填
  - `structure_check`：
    - `title_correct`：`pass` | `fail`
    - `title_separator_correct`：`pass` | `fail`
    - `header_levels_correct`：`pass` | `fail`
    - `row_column_counts_correct`：`pass` | `fail`
    - `cell_text_accurate`：`pass` | `fail`
    - `footnotes_complete`：`pass` | `fail`
    - `rendered_preview_matches`：`pass` | `fail`
  - `findings[]`（pass 必須空，fail 至少一個）：
    - `finding_id`：unique within report（`Table_1_f001`）
    - `table_id`
    - `crop_id`：finding 指向的 crop unit。單 crop 表格填 null。跨頁表格必須填具體 crop_id（如 `Table_3_p10`），不要只在 notes 描述頁碼。
    - `problem`、`edge`（crop 問題）或 `null`（結構問題）、`repair_hint`、`severity`
    - `notes`：必填，具體說明
- `summary`：`table_count`、`pass_count`、`fail_count`、`finding_count`

### table_visual_review.json example

```json
{
  "schema_version": "table_review.v1",
  "review_round": "round_00",
  "reviewer_id": "reviewer_01",
  "status": "fail",
  "tables": [
    {
      "table_id": "Table_1",
      "table_label": "Table 1",
      "decision": "pass",
      "reviewed_crop_units": [
        {
          "crop_id": "Table_1",
          "crop_preview": "previews/Table_1_preview.png",
          "boundary_preview": "previews/Table_1_boundary_preview.png",
          "top_band": ["previews/Table_1_top_seg1_preview.png"],
          "bottom_band": ["previews/Table_1_bottom_seg1_preview.png"],
          "bottom_micro": ["previews/Table_1_micro_bottom_seg1_preview.png"],
          "rendered_table_preview": "rendered_tables/Table_1_rendered.png"
        }
      ],
      "structural_inventory": {
        "expected": { "rows": 15, "columns": 5, "header_levels": 2, "footnotes": 2 },
        "observed": { "rows": 15, "columns": 5, "header_levels": 2, "footnotes": 2 },
        "match": true
      },
      "edge_checks": {
        "crop_units": [
          {
            "crop_id": "Table_1",
            "edges": {
              "top": { "boundary_content": { "seg1": { "last_inside": "table title", "first_outside": "whitespace then page header" } }, "status": "pass", "condition": "clean_margin", "notes": "Title below crop top." },
              "bottom": { "boundary_content": { "micro_seg1": { "last_inside": "last footnote text", "first_outside": "whitespace then body prose" } }, "status": "pass", "condition": "clean_margin", "notes": "Footnotes complete." },
              "left": { "boundary_content": { "seg1": { "last_inside": "first column text", "first_outside": "whitespace" } }, "status": "pass", "condition": "clean_margin", "notes": "Clean." },
              "right": { "boundary_content": { "seg1": { "last_inside": "last column text", "first_outside": "whitespace" } }, "status": "pass", "condition": "clean_margin", "notes": "Clean." }
            }
          }
        ]
      },
      "structure_check": {
        "title_correct": "pass",
        "title_separator_correct": "pass",
        "header_levels_correct": "pass",
        "row_column_counts_correct": "pass",
        "cell_text_accurate": "pass",
        "footnotes_complete": "pass",
        "rendered_preview_matches": "pass"
      },
      "findings": []
    },
    {
      "table_id": "Table_2",
      "table_label": "Table 2",
      "decision": "fail",
      "reviewed_crop_units": [
        {
          "crop_id": "Table_2",
          "crop_preview": "previews/Table_2_preview.png",
          "boundary_preview": "previews/Table_2_boundary_preview.png",
          "bottom_band": ["previews/Table_2_bottom_seg1_preview.png"],
          "bottom_micro": ["previews/Table_2_micro_bottom_seg1_preview.png"],
          "rendered_table_preview": "rendered_tables/Table_2_rendered.png"
        }
      ],
      "structural_inventory": {
        "expected": { "rows": 10, "columns": 4, "header_levels": 1, "footnotes": 1 },
        "observed": { "rows": 12, "columns": 4, "header_levels": 1, "footnotes": 1 },
        "match": false
      },
      "edge_checks": {
        "crop_units": [
          {
            "crop_id": "Table_2",
            "edges": {
              "top": { "boundary_content": { "seg1": { "last_inside": "table title", "first_outside": "whitespace" } }, "status": "pass", "condition": "clean_margin", "notes": "Clean." },
              "bottom": { "boundary_content": { "micro_seg1": { "last_inside": "footnote", "first_outside": "whitespace" } }, "status": "pass", "condition": "clean_margin", "notes": "Clean." },
              "left": { "boundary_content": { "seg1": { "last_inside": "row label", "first_outside": "whitespace" } }, "status": "pass", "condition": "clean_margin", "notes": "Clean." },
              "right": { "boundary_content": { "seg1": { "last_inside": "data", "first_outside": "whitespace" } }, "status": "pass", "condition": "clean_margin", "notes": "Clean." }
            }
          }
        ]
      },
      "structure_check": {
        "title_correct": "pass",
        "title_separator_correct": "pass",
        "header_levels_correct": "pass",
        "row_column_counts_correct": "fail",
        "cell_text_accurate": "pass",
        "footnotes_complete": "pass",
        "rendered_preview_matches": "fail"
      },
      "findings": [
        {
          "finding_id": "Table_2_f001",
          "table_id": "Table_2",
          "crop_id": null,
          "problem": "false_row_split",
          "edge": null,
          "repair_hint": "merge_wrapped_cell",
          "severity": "required",
          "notes": "Source row 5 has a wrapped cell in column 1 ('Long treatment description...'). JSON splits it into rows 5 and 6, creating a false row. Expected 10 rows, observed 12."
        }
      ]
    }
  ],
  "summary": {
    "table_count": 2,
    "pass_count": 1,
    "fail_count": 1,
    "finding_count": 1
  }
}
```

# 規則

## 權責

- Reviewer 只做視覺判斷和結構比對，產出 `table_visual_review.json`。
- 不修改 crop、`Table_<N>.json`、canonical evidence 或 manifest。
- 不做 gate 判定。

## 圖片與讀取限制

- 只讀 canonical preview 圖片。
- 單張 1600 px；多張 1400 px。
- 缺失或太大 → `fail` + finding。

## Pass/fail 語意

- `pass`：crop 邊界乾淨且結構化 JSON 準確。
- `fail`：crop 需要修、結構需要修、evidence 缺失、或無法確定。
- 不確定就是 `fail`。

## Finding 寫法

好的 finding：
```json
{
  "problem": "cell_text_error",
  "edge": null,
  "repair_hint": "correct_cell_text",
  "notes": "Row 3, Column 'Dose': source shows '10 mg/kg' but JSON has '10 mg/kq' — 'g' misread as 'q'."
}
```

不好（太模糊）：`"notes": "Some cells look wrong"`

不好（提供修正 JSON）：`"corrected_cell": "10 mg/kg"`
