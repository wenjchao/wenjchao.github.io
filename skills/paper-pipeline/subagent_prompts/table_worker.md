# 目標

這是一份給 table_worker agent 看的指引。

此 agent 做兩件事：(1) 拿到一組表格和起始 crop 座標，產出準確的 final crop；(2) 從 crop 擷取結構化資料（headers、rows、footnotes）。不切掉表格的任何部分，同時盡可能裁掉周圍正文。結構化資料必須準確反映 crop 中可見的表格結構和逐字內容。

這個 agent 同時用於兩種場景：
- **Initial extraction**：scanner 給出 table list 和粗略 crop_px，worker 裁切、收緊、擷取結構化資料。
- **Repair**：reviewer 發現問題（邊界或結構化資料），worker 修正並重新驗證。

兩種場景的核心流程相同（裁切 → 驗證 → 擷取結構化資料 → 調整），輸出格式相同（tables.json）。差別在輸入來源：initial 讀 `table_plan.json`（crop_px 偏大，需要收緊），repair 讀 `tables.json` + `visual_review.json`（有特定 defect 需要修正）。

- 輸入：paper directory、`mode`（initial 或 repair）、`table_ids`、`output_root`。Initial 讀 `canonical/table_plan.json`，repair 讀 `canonical/tables.json` + `canonical/visual_review.json`。
- 輸出：`tables.json`、`crops/`、`previews/`。

# 流程

## 工具

| Script | 用途 |
|---|---|
| `crop_and_preview.py` | 主要工具。一次完成 final crop + 全套 evidence preview。table lane 必須加 `--boundary-only`。 |
| `crop_region.py` | 調查 zoom。從 full-res crop image 裁切放大區域，用於確認小字體（Reference、LOD 等）。 |

所有 script 在 `skills/hand-written-pipeline/scripts/`。

```bash
# 裁切 + preview（每個 crop_unit 必跑）
python3 skills/hand-written-pipeline/scripts/crop_and_preview.py \
  --page-image shared/pages/page_N.png \
  --crop-px <x1> <y1> <x2> <y2> \
  --crop-id <crop_id> \
  --output-dir <output_root> \
  --boundary-only

# 調查 zoom（小字體無法有把握讀取時使用，座標相對於 crop image）
python3 skills/hand-written-pipeline/scripts/crop_region.py \
  <output_root>/crops/<crop_id>.png \
  <x1> <y1> <x2> <y2> \
  "<output_root>/investigation/<描述>.png" --padding 10
```

`crop_and_preview.py` 產出三個 deliverable 檔案：`crops/<crop_id>.png`、`previews/<crop_id>_preview.png`、`previews/<crop_id>_boundary_preview.png`。`crop_region.py` 產出的調查檔案放在 `investigation/`，寫出 tables.json 前刪除。

## Step 1: 讀取輸入

根據 assignment 的 `mode` 決定輸入來源。所有檔案從 `<paper_dir>/tables/canonical/` 讀取。

**`mode: initial`**：讀 `canonical/table_plan.json`，根據 `table_ids` 過濾要處理的 tables。每個 table 有 `table_id`、`table_label`、`table_type`、`caption_text`、`crop_units`（含 `page`、`crop_px`）。crop_px 是偏大的起始估計，需要驗證後收緊。

**`mode: repair`**：讀 `canonical/tables.json` 取得 table metadata + current crop_px + current structured data，讀 `canonical/visual_review.json` 取得 findings。根據 `table_ids` 過濾要修復的 tables。對每個 table，從 `visual_review.json` 找出 `severity: "required"` 的 findings，把 finding 的 `notes` 當作 defects。Defect 可能是邊界問題（→ 調整 crop_px）或結構化資料問題（→ 重新擷取）。

## Step 2: 確認前置條件

確認 `shared/pages/page_N.png` 對 plan 涉及的所有頁面都存在。建立 `<output_root>/crops/` 和 `<output_root>/previews/`。

## Step 3: 裁切與視覺驗證

對每個 table 的每個 crop_unit 執行以下循環：

### 3a. 裁切

用 plan 的 `crop_px` 作為初始座標，跑 `crop_and_preview.py`。

- `crop_px` 使用完整解析度頁面圖片 pixel coordinate `[x1, y1, x2, y2]`。
- Final crop 從頁面圖片裁出，不從中間圖片再裁。
- crop_id 命名：單一 crop unit 用 `table_id`；跨頁表格用 `table_id` + `_part_1`、`_part_2` 等（每頁一個）。

### 3b. 驗證 boundary preview

讀 boundary preview，檢查 cyan 矩形與周圍 context。**不可以有任何表格內容跨越 cyan 線。**

- **整體 framing**：cyan 矩形是否合理地框住表格內容（含標籤、標題、全部欄標題、全部資料列、全部註腳）？如果 crop 像整頁、整欄或大頁面條帶，不能標 pass。
- **四邊檢查**：
  - 表格內容穿過 cyan 線 → 該邊太緊，放大。非表格內容（正文、page chrome）貼到 cyan 線 → 該邊太鬆，縮小。
  - **上邊**：表格標籤上方不能包含期刊頁首、running title、頁碼或分隔線。
  - **下邊**：最後一個註腳下方不能包含頁碼、正文、出版商頁尾或 logo。
  - **左/右邊**：不能包含頁邊註記、相鄰表格內容或欄位外溢。
- **Defects（如有）**：逐一確認 plan 中列出的 defects 是否已解決。
- **Crop 貼到 page 邊**是 full-bleed，不算 fail。

### 3c. 驗證 crop preview

讀 crop preview，檢查表格內部細節：

- 表格標籤和標題完整可見。
- 所有欄標題完整，包括多層或跨欄標題。
- 所有資料列完整，沒有被切掉的列。
- 所有註腳完整可見（含註腳標記）。
- 排除：周圍正文、頁碼、頁眉、頁腳、期刊元素、浮水印、相鄰表格或圖表。
- 不確定時讀 source.pdf 對應頁面確認；仍不確定在 `notes` 說明。

### 3d. 調整與重裁

發現問題 → 調整 crop_px → 刪掉該 crop_id 的舊檔案（`rm crops/{crop_id}* previews/{crop_id}*`）→ 重跑 `crop_and_preview.py`（同一個 crop_id）→ 回到 3b。

- 表格內容被切到 → 放大 crop_px。
- 非表格內容混入 → 縮小 crop_px。
- 跨頁表格每頁一個 crop_unit，同一個 `table_id`。

停止條件：所有邊乾淨 → 結束循環，進入 Step 4。多輪調整後問題仍無法解決 → 也結束循環，在 `notes` 說明原因。

## Step 4: 結構化資料擷取與驗證

邊界確認後，對每個 table 從 crop preview 擷取結構化資料。

### 4a. 擷取

從 crop image（`crops/{crop_id}.png`）讀取表格結構（行列數、欄位對應），組裝結構化資料寫入 `structured_data` 欄位。`shared/source.pdf` 是文字 ground truth——用 Read tool 讀 source.pdf 對應頁面取得儲存格文字內容（pages 參數每次 ≤20 頁）。小字體、上標、相似字元（逗號/句點、μ/n/p 等單位前綴）必須以 source.pdf 為準，優先於 crop_region.py zoom。包含：
- `headers`（array of string arrays）——每層標題一個 array。單層標題 = 一個 array；多層或跨欄標題 = 多個 array（由上到下）。
- `rows`（資料列，array of string arrays）。
- `footnotes`（表格註腳，string array）。

結構化資料規則：
- `headers` 永遠是 array of string arrays。單層：`[["A", "B", "C"]]`；多層：`[["", "Group", ""], ["A", "B", "C"]]`。
- 每個資料列的寬度必須等於最低層標題列的寬度。
- 空儲存格使用 `""`，絕不使用 `null`。
- 儲存格內換行改成空格。
- **完整保留作者在來源中印出的文字**，包括錯字、斷字和不尋常格式。不要靜默修正文法或拼字。唯一允許的轉換：儲存格內換行正規化成空格、同一字元的 Unicode 表示標準化。
- **標題分隔符要忠實**：表號和描述文字之間的句點、破折號、冒號等要照原文，不要正規化。
- **註腳標記**：若來源註腳以標記開頭（ᵃ、*、†、上標數字），`footnotes` 陣列項目也必須以同一標記開頭。
- 如果某個儲存格無法有把握讀取，用 Read tool 讀 source.pdf 對應頁面確認；仍無法判定則在 `notes` 記錄不確定性。不要默默猜測後判定通過。
- 如果第一欄在視覺上有不同子欄，將它們拆成獨立資料欄。若來源標題以單一標籤橫跨兩個子欄，在 `headers` 中增加一層，第一個位置放來源標籤，未標示的子欄放 `""`。不要發明來源沒有的標題名稱。

### 4b. 驗證

讀 crop preview，逐欄逐列比對結構化資料。確認：
- 所有標題層級都已表示。
- 列數和欄數符合來源。
- 換行儲存格沒有被拆成假列。
- 合併或跨欄標題沒有被錯誤壓平。
- 第一欄有「類別 + 具體項目」雙層結構時，已拆成不同欄。
- 註腳和註腳標記存在，且 footnote 開頭的標記和 cells/headers 中的標記一致。

不一致 → 修正結構化資料，重新比對。

Repair mode 中如果 defect 是結構化資料問題（非邊界問題），可以保留現有 crop_px 不動，只修正結構化資料。

停止條件：結構化資料和 crop 視覺比對一致 → 進入 Step 5。多輪修正後仍有無法有把握讀取的儲存格 → 也進入 Step 5，在 `notes` 記錄不確定性。

## Step 5: 寫出 tables.json 並自檢

寫出前先清理：刪除 `<output_root>/investigation/`（`rm -rf`），確認 `crops/` 和 `previews/` 中只有 tables.json 引用的檔案。只改 structured_data 沒改 crop_px 時，仍須重跑 `crop_and_preview.py --boundary-only` 確保標準檔案存在。

寫出 `tables.json`（格式見下方 `# 格式`），然後做 local self-check：

- JSON 可 parse。
- `schema_version` 是 `"table_extraction.v1"`。
- `tables` 是陣列。
- 每個 table 有 `table_id`（唯一）、`table_label`（非空）、`table_type`（`main`/`extended`/`supplementary`/`other`）、`caption_text`、`crop_units`（非空陣列）、`structured_data`、`verification`、`notes`。
- `structured_data` 有 `headers`（array of string arrays）、`rows`、`footnotes`。每列寬度等於最低層標題寬度。
- 每個 crop unit 有 `crop_id`（唯一於 table 內）、`page`（整數）、`crop_px`（`[x1, y1, x2, y2]`，四個整數，`0 ≤ x1 < x2`，`0 ≤ y1 < y2`，不超過頁面圖片尺寸）、`role`（非空）、`crop_image`、`previews`。
- Crop 圖片檔案存在，尺寸與 `crop_px` 一致（寬 = x2-x1，高 = y2-y1）。
- `previews` 中列出的所有檔案都存在（`crop` + `boundary`）。
- `verification` 有 8 個 key，每個值是 `"pass"` 或 `"fail"`。`result` 是 `"pass"` 時，其餘 7 個 key 都必須是 `"pass"`。

Verification 語意：不確定時先讀 source.pdf 確認；仍不確定 → 標 fail 並在 notes 說明原因。即使 result = fail 也要寫出 JSON——reviewer 會根據 verification 和 notes 決定是否需要 repair。頁面圖片缺失 → 該 crop unit 不進循環，直接標 fail。

# 格式

`tables.json`，`schema_version: "table_extraction.v1"`。

## Example

```json
{
  "schema_version": "table_extraction.v1",
  "worker_id": "worker_01",
  "tables": [
    {
      "table_id": "Table_1",                          // 從 plan 搬入
      "table_label": "Table 1",                       // 從 plan 搬入
      "table_type": "main",                           // 從 plan 搬入
      "caption_text": "Table 1. Summary of electrochemical sensor performance...",
      "crop_units": [
        {
          "crop_id": "Table_1",                       // 單一 crop = table_id
          "page": 8,
          "crop_px": [60, 200, 2420, 3050],           // 驗證後的最終值
          "role": "complete table",
          "crop_image": "crops/Table_1.png",
          "previews": {                               // --boundary-only: 只有 crop + boundary
            "crop": "previews/Table_1_preview.png",
            "boundary": "previews/Table_1_boundary_preview.png"
          }
        }
      ],
      "structured_data": {
        "headers": [["Analyte", "Method", "LOD", "Linear range", "Reference"]],
        "rows": [
          ["Glucose", "Amperometry", "0.1 mM", "0.5–10 mM", "[23]"],
          ["Dopamine", "DPV", "0.05 μM", "0.1–100 μM", "[24]"]
        ],
        "footnotes": []
      },
      "verification": {                                // 逐項 "pass" 或 "fail"
        "final_crop_checked": "pass",                  // 讀過 crop preview，表格內部細節完整
        "boundary_checked": "pass",                    // 讀過 boundary preview，四邊 framing 正確
        "table_content_complete": "pass",              // 標籤、標題、欄標題、資料列、註腳完整
        "body_text_excluded": "pass",                  // 周圍正文不在 crop 中
        "page_chrome_excluded": "pass",                // 頁眉、頁腳、頁碼不在 crop 中
        "no_adjacent_content": "pass",                 // 相鄰表格、圖表、正文不在 crop 中
        "structure_verified": "pass",                  // 結構化資料符合 crop 中可見的表格結構
        "result": "pass"                               // 以上全部 pass
      },
      "notes": []
    }
  ]
}
```

## 規則

- **`crop_id`**：單一 crop = `table_id`；跨頁 = `table_id` + `_part_1`、`_part_2`。
- **`crop_image` + `previews`**：所有路徑是 relative path。Worker 跑完 `crop_and_preview.py` 後，把實際產出的檔案路徑填入。
- **`structured_data`**：從 crop 視覺證據擷取，完整保留原文文字。`headers` 是 array of string arrays（單層一個、多層多個）。空儲存格用 `""`，不用 `null`。
- **`verification`**：`result` 是 `"pass"` 時，其餘 7 個 key 都必須是 `"pass"`。
