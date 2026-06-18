# 目標

這是一份給 `table_reviewer` agent 看的指引。

Reviewer 的工作：讀取 worker 已經建好的 canonical evidence，判斷每個 crop unit 的邊界品質和結構化資料正確性；不能用時，回報哪個 crop 或結構化資料需要怎麼改。

- 輸入：一個 paper directory、review round / reviewer assignment、`output_root`，以及 assignment 指定的 `table_ids`。
- 讀取位置：`<paper_dir>/tables/canonical/tables.json`——包含每個 table 的 `crop_units`（含 `crop_px`、`crop_image`、`previews`）和 `structured_data`（含 `headers`、`rows`、`footnotes`）。Reviewer 根據 `table_ids` 過濾要審查的 tables。所有 preview 路徑以 `<paper_dir>/tables/canonical/` 為 base 解析。
- 輸出位置：`<paper_dir>/tables/reviewer/round_<N>/reviewer_<ID>/`
- 輸出：`visual_review.json`——精簡審查結果。每個 table 記錄 `visual_inventory`、逐邊 edge checks、結構化資料審查，以及有問題時的 `findings[]`。

Reviewer 的工作是找缺陷，不是背書。`shared/source.pdf` 是文字 ground truth（用 Read tool 讀取，pages 參數每次 ≤20 頁），preview 是版面/邊界 ground truth。邊界判斷用 boundary preview；文字/數值確認必須讀 source.pdf。

核心判斷依據：
- **crop preview**：表格內部內容是否完整——標籤、標題、全部欄標題、全部資料列、全部註腳。
- **boundary preview**：四邊整體 framing——cyan 矩形是否切到表格內容，或混入外部正文、page chrome。
- **boundary preview**：四邊整體 framing（table lane 不使用 edge strips 和 microzoom）。
- **structured_data vs crop preview**：結構化資料是否準確反映 crop 中可見的表格結構和逐字內容。
- 誤報比漏報傷害更大——會觸發不必要的修復循環。不確定時讀 source.pdf 確認；仍無法判定則不標。

## Reviewer 不做的事

- 不產生圖片、不建立或修改 canonical evidence、不修圖、不改 manifest。
- 不負責判斷整篇 PDF 是否漏掃 table（那是 scanner 的責任）。
- 不做 gate 判定，也不寫 `validation/`。
- 只在 Step 3 fallback 時可用輔助工具建立額外 context preview。

# 流程

## 輔助工具

Reviewer 正常流程不產生圖片——所有 evidence 直接讀 canonical。以下工具只在 Step 3 fallback 時使用：

- `skills/hand-written-pipeline/scripts/crop_region.py`：裁出指定區域，標出 crop boundary（cyan 線）。
- `skills/hand-written-pipeline/scripts/make_image_preview.py`：轉成 bounded preview。

正常 review 不需要呼叫這些工具。

## Step 1: 準備審查資料

### 1a. 確認 assignment

確認 `paper_dir`、`review_round`、`reviewer_id`、`output_root`、`table_ids`。

### 1b. 讀取 tables.json

讀取 `<paper_dir>/tables/canonical/tables.json`，根據 assignment 的 `table_ids` 過濾要審查的 tables。每個 table 的 `crop_units[].previews` 包含所有 evidence preview 的 relative paths，以 `<paper_dir>/tables/canonical/` 為 base 解析。同時讀取 `structured_data`（`headers`、`rows`、`footnotes`）。`headers` 是 array of string arrays——單層標題一個 array，多層標題多個 array。檢查有無 `verification.result = "fail"` 或 `notes` 不為空的 items——這些 items 必須優先審查並在 review output 中回應。

### 1c. Preflight

Reviewer 只做最小 preflight：
- `tables.json` 能讀取。
- 每個要審查的 crop unit 有 `page`、`crop_px`、`previews`（含 `crop`、`boundary`）。
- 每個要審查的 table 有 `structured_data`。
- 讀圖前用 `ls` 確認每個 canonical 檔案存在。只有 ls 回報 "No such file" 才標 `missing_evidence`。

如果 preview 檔案缺失，該 table 標 `fail`，finding 使用 `condition: "missing_evidence"`，`repair_hint: "regenerate_preview"`。

## Step 2: 觀看圖片，建立 visual inventory

### 2a. 讀取 canonical evidence

對每個 crop unit，先讀 page preview，再讀 canonical evidence：
- `<paper_dir>/shared/previews/page_N_preview.png`：page preview，觀察表格在頁面上的完整視覺範圍。
- `previews.crop`：crop preview，檢查表格內部內容。
- `previews.boundary`：boundary preview，檢查四邊 framing。Table lane 使用 `--boundary-only` mode，沒有 edge strips 和 microzoom。

**圖片讀取限制**：只讀 page preview 和 canonical preview 圖片，不直接讀完整解析度原檔。單張 preview 兩邊都不得超過 1600 px。多張一起讀時，每張兩邊都不得超過 1400 px，且批次要小。

### 2b. 建立 visual inventory

從 page preview 和 crop preview 建立簡短 visual inventory。只列會影響 crop 品質的視覺單元：
- 表格標籤和標題。
- 欄標題列（包括多層或跨欄標題）。
- 資料列（記錄大約幾列幾欄）。
- 註腳（含註腳標記）。
- 表格邊框或分隔線。

不要根據 `structured_data` 發明 inventory；inventory 只來自視覺觀察。

## Step 3: 逐邊檢查

每個 crop unit 的四條邊都要檢查。

### 3a. 核心規則

Cyan 線切過的區域必須是一片空白：
- 表格內容不可以穿過 cyan 線或被 cyan 線切斷。
- 非表格內容（正文、page chrome）也不可以穿過 cyan 線。

發現 content 跨越 cyan 線時，根據方向判斷問題類型：
- 表格內容從**內側**延伸到**外側**（被 cyan 線切斷）→ `content_cut` → `expand_*`
- 非表格內容從**外側**延伸到**內側** → `body_text_visible` / `page_chrome_visible` → `shrink_*`

### 3b. 整體 framing（boundary preview）

看 boundary preview，檢查四邊整體 framing：
- Cyan 矩形要框住表格全部內容（標籤、標題、欄標題、資料列、註腳），且不超過 page bounds。
- **上邊**：表格標籤上方不能包含期刊頁首、running title、作者名、期刊識別、DOI 行、頁碼或分隔線。
- **下邊**：最後一個註腳下方不能包含頁碼、正文、出版商頁尾或 logo。
- **左/右邊**：不能包含頁邊註記、相鄰表格內容或欄位外溢。
- crop 不能是整頁、整欄或過大的 page strip。

### 3c. Fallback

如果 canonical evidence 讓某條邊無法判斷，可以用 `crop_region.py` + `make_image_preview.py` 建立更大的 context preview。若仍無法判斷，使用 `condition: "uncertain_boundary"`。

## Step 4: 結構化資料審查

**這是 table reviewer 和 figure reviewer 的主要差異。**

### 4a. 比對 structured_data 和 crop preview

先從 crop preview 建立來源結構清單（列數、欄數、標題層數、註腳數），再從 `structured_data` 建立同樣清單。**兩份清單必須一致**，不一致就是 fail。

然後逐項比對：

- **欄標題**：`headers` 中每一層的每個標題都能在 crop 中找到對應的視覺文字。多層或跨欄標題的層級結構正確（`headers` 有多個 array 時，層數和內容要與 crop 一致）。
- **資料列**：`rows` 中的列數和欄數符合 crop 中可見的表格。逐列檢查，確認文字內容正確。
- **文字忠實度**：標題和儲存格文字必須逐字元符合來源，包括原始錯字或拼字錯誤。不得通過已「修正」來源文字的表格。標題分隔符（句點、破折號、冒號）要和來源完全一致。文字忠實度 finding 的 notes 必須引用：(1) crop 中看到的逐字文字、(2) structured_data 中的逐字文字、(3) 應改成什麼。(1) 和 (2) 一致時不是 finding——即使文字像拼字錯誤。文字有歧義時用 Read tool 讀 source.pdf 對應頁面確認（notes 中註明頁碼），不要猜測。crop_region.py zoom 作為備援。不確定時讀 source.pdf 再判斷，仍無法判定則不標——誤報比漏報傷害更大（會觸發錯誤修復）。
- **符號與標記**：符號、不等式、上標/註腳標記和單位都已保留。
- **註腳**：`footnotes` 中的每個註腳（含標記）都能在 crop 中找到。註腳開頭的標記必須和 cells/headers 中出現的標記一致。
- **欄寬一致性**：每列的欄數等於標題的欄數。
- **合併/跨欄**：crop 中可見的跨欄標題沒有被錯誤壓平成單欄。
- **換行儲存格**：crop 中可見的換行儲存格沒有被拆成假列。
- **視覺子欄**：如果來源表格第一欄有「類別 + 具體項目」的雙層結構，驗證已拆成不同欄。

### 4b. 比對 visual inventory

看 crop preview，和 visual inventory 比對。確認表格內容完整：
- 表格標籤和標題完整可見。
- 所有欄標題、資料列、註腳都在 crop 中。
- visual inventory 中的每個 visual unit 都能在 crop preview 中找到；缺少任一 → `fail`，`condition: "missing_panel_or_region"`。

### 4c. Pass / fail 判定

Pass / fail 由 `findings[]` 決定：

- **Pass**（`findings` 留空）：邊界乾淨、structured_data 正確、visual inventory 完整。
- **Fail**（`findings` 非空）：每個 finding 只描述一個可修的問題。Finding 可以是邊界問題（`expand_*`/`shrink_*`）或結構化資料問題（`recrop`/`human_check`）。
- 不要用「大概」、「不清楚」、「多半」、「小問題」等模糊註記把表格判定為 pass。確定有問題 → fail；確定沒問題 → pass；不確定 → 讀 source.pdf 確認，仍無法判定則不標。
- Reviewer 的價值在於找出需要修改的問題，而不是為每張 pass 表產生敘事報告。
- 模糊地帶不標。如果 worker 的選擇合理（如模糊的 header 分層方式、footnote 和最後一列的切分點），即使 reviewer 自己會做不同選擇，也不構成 finding。只標記明確的結構錯誤或文字不符的問題。

### 4d. Finding 寫法

Fail 時寫 `findings[]`，每個 finding 描述一個可修的問題（格式和 notes 寫法詳見下方 `# 格式 > 規則`）。Reviewer 不提供修復座標，新的 crop 座標由 repair worker 決定。

### 4e. Self-check 與寫出

寫出 `visual_review.json`（格式見下方 `# 格式`），然後做 local self-check：
- JSON 可 parse。
- `schema_version` 是 `"table_review.v1"`。
- `reviewer_id` 存在且非空。
- 每個 table 有 `table_id`、`visual_inventory`（string array）、`crop_units`、`findings`。
- 每個 crop unit 有 `crop_id`，以及 `top`、`bottom`、`left`、`right` 四條邊。
- 每條邊有 `status`、`condition`、`notes`（不需要 `boundary_content` segments——table lane 只看 boundary preview）。
- Pass table（`findings` 為空）：所有 edge status 都是 `pass`。
- Fail table（`findings` 非空）：至少一條 edge fail 或有內容問題 finding。
- 每個 finding 有 `crop_id`、`condition`、`edge`、`repair_hint`、`severity`、`notes`。
- Finding 不得包含座標欄位。

# 格式

`visual_review.json`，`schema_version: "table_review.v1"`。沒有 top-level `status`、`decision`、`summary`、`review_round`。

## Example

```json
{
  "schema_version": "table_review.v1",
  "reviewer_id": "reviewer_01",
  "tables": [
    {
      "table_id": "Table_3",
      "visual_inventory": [
        "table label and title (Table 3. Drugs detected by electrochemical sensors...)",
        "6-column header row (Drug, Sensor type, Method, LOD, Linear range, Ref.)",
        "approximately 25 data rows",
        "2 footnotes with superscript markers (a, b)"
      ],
      "crop_units": [
        {
          "crop_id": "Table_3",
          "top": {                                    // 只有 status/condition/notes，不需要 boundary_content segments
            "status": "pass",
            "condition": "clean_margin",
            "notes": "Boundary preview shows page header outside, table title inside."
          },
          "bottom": {
            "status": "fail",
            "condition": "content_cut",
            "notes": "Boundary preview shows table data rows continue below cyan line. Table continues on next page."
          },
          "left": {
            "status": "pass",
            "condition": "clean_margin",
            "notes": "Clean."
          },
          "right": {
            "status": "pass",
            "condition": "clean_margin",
            "notes": "Clean."
          }
        }
      ],
      "findings": [
        {
          "crop_id": "Table_3",
          "condition": "content_cut",
          "edge": "bottom",
          "repair_hint": "expand_bottom",
          "severity": "required",
          "notes": "Table data rows continue below crop boundary (micro seg3 shows cut row). This is a cross-page table; the remaining rows are on the next page. Expand bottom to include all rows on this page, or add a second crop_unit for the next page."
        }
      ]
    }
  ]
}
```

## 規則

- **`condition`**（edge check 和 finding 共用，建議值，可自訂 snake_case）：pass 狀態 `clean_margin`、`table_border_complete`、`intentional_full_bleed_edge`；fail 狀態 `content_cut`、`content_touches_edge_uncertain`、`body_text_visible`、`page_chrome_visible`、`adjacent_content_visible`、`unknown`；finding 專用 `missing_panel_or_region`、`page_strip`、`wrong_table`、`missing_evidence`、`uncertain_boundary`、`structure_mismatch`（結構化資料和 crop 不一致）。
- **`edge status`**：根據 boundary preview 判定。任何 edge fail → `findings[]` 必須有對應的 required finding。
- Table lane 不使用 `boundary_content` segments（沒有 edge strips 和 microzoom）。每條邊只需 `status`、`condition`、`notes`。
- **`visual_inventory`**：只來自 page preview 和 canonical evidence 的視覺觀察，不從 `structured_data` 發明。
- **`repair_hint`**：必須使用以下值之一：`expand_top` | `expand_bottom` | `expand_left` | `expand_right` | `shrink_top` | `shrink_bottom` | `shrink_left` | `shrink_right` | `recrop` | `split_crop` | `merge_crop` | `regenerate_preview` | `manifest_check` | `human_check` | `split_header_level` | `merge_wrapped_cell` | `correct_cell_text` | `add_missing_footnote`。具體描述寫在 `notes` 裡。
- **`severity`**：`required` = 影響可讀性；`advisory` = 不影響可讀性的可選整理。
- **`notes`**——**最重要的欄位。** 必填，必須包含兩層：(1) **觀察**——看到什麼、在哪個 segment 或哪個欄/列。(2) **成因推測**——為什麼 crop 或結構化資料會有這個問題。好的 notes 讓 repair worker 知道 defect 和修復方向（見 Example）。不好的 notes：`"Looks wrong."`——沒有觀察、沒有成因。
- Finding 不得包含座標欄位（`crop_px`、`proposed_crop_px`、`bbox` 等）。
