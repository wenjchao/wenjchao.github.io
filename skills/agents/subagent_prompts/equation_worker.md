# 目標

這是一份給 equation_worker agent 看的指引。

此 agent 做兩件事：(1) 拿到一組方程式和起始 crop 座標，產出準確的 final crop；(2) 從 crop 轉寫 LaTeX。不切掉方程式的任何部分，同時盡可能裁掉周圍正文。LaTeX 必須準確反映 crop 中可見的數學結構。

這個 agent 同時用於兩種場景：
- **Initial extraction**：scanner 給出 equation list 和粗略 crop_px，worker 裁切、收緊、轉寫 LaTeX。
- **Repair**：reviewer 發現問題（邊界或 LaTeX），worker 修正並重新驗證。

兩種場景的核心流程相同（裁切 → 驗證 → LaTeX → 調整），輸出格式相同（equations.json）。差別在輸入來源：initial 讀 `equation_plan.json`（crop_px 偏大，需要收緊），repair 讀 `equations.json` + `visual_review.json`（有特定 defect 需要修正）。

- 輸入：paper directory、`mode`（initial 或 repair）、`equation_ids`、`output_root`。Initial 讀 `canonical/equation_plan.json`，repair 讀 `canonical/equations.json` + `canonical/visual_review.json`。
- 輸出：`equations.json`、`crops/`、`previews/`。

# 流程

## 工具

| Script | 用途 |
|---|---|
| `crop_and_preview.py` | 主要工具。一次完成 final crop + 全套 evidence preview。 |

所有 script 在 `agents/scripts/`。

```bash
python3 agents/scripts/crop_and_preview.py \
  --page-image shared/pages/page_N.png \
  --crop-px <x1> <y1> <x2> <y2> \
  --crop-id <crop_id> \
  --output-dir <output_root> \
  --boundary-only
```

產出：`crops/<crop_id>.png`（final crop）、`previews/<crop_id>_preview.png`（crop preview）、`previews/<crop_id>_boundary_preview.png`（boundary preview，含 cyan 矩形）。`--boundary-only` 跳過 edge strips 和 microzoom（equation crop 是中間證據，不需要像素級邊界精確度，但是不能漏掉、切掉重要資訊）。

## Step 1: 讀取輸入

根據 assignment 的 `mode` 決定輸入來源。所有檔案從 `<paper_dir>/equations/canonical/` 讀取。

**`mode: initial`**：讀 `canonical/equation_plan.json`，根據 `equation_ids` 過濾要處理的 equations。每個 equation 有 `equation_id`、`equation_number`、`equation_type`、`crop_units`（含 `page`、`crop_px`）、`notes`。

- `notes` 包含 scanner 對方程式的描述：LaTeX 轉寫、頁面位置、周圍 context。用這些資訊在頁面上定位方程式。
- `crop_px` 是從低解析度 preview 估算的粗略 hint，**經常不準確**——可能偏移數百 pixel 甚至指向錯誤區域。不要盲信 crop_px，以 notes 中的內容描述為主要定位依據。
- **重要**：notes 中的 LaTeX 是 scanner 從 preview 快速轉寫的，可能有錯。Worker 必須自己看 page preview / crop preview 來確認方程式內容，自己寫最終的 LaTeX。不得直接複製 scanner notes 中的 LaTeX 到輸出。

**`mode: repair`**：讀三份檔案：

1. `canonical/equations.json`：取得 equation metadata + current crop_px + current latex。
2. `canonical/visual_review.json`：取得 findings。根據 `equation_ids` 過濾要修復的 equations。對每個 equation，找出 `severity: "required"` 的 findings。**仔細讀每個 finding 的 `notes`**——notes 包含 reviewer 的具體觀察（看到什麼、在哪個 segment）和成因推測（為什麼 crop 有問題）。這是 repair 的直接指引，告訴你該往哪個方向修、問題的根源是什麼。不讀 notes 就動手修等於盲修。
3. `canonical/equation_plan.json`：取得 scanner 原始 notes（LaTeX 描述 + 位置 + 周圍 context）。用 plan 的 notes 確認自己要修的是哪個方程式——尤其在密集頁面上，多個方程式結構相似，不看 plan 很容易修錯目標。

## Step 2: 確認前置條件

確認 `shared/pages/page_N.png` 對 plan 涉及的所有頁面都存在。建立 `<output_root>/crops/` 和 `<output_root>/previews/`。

## Step 3: 裁切與視覺驗證

對每個 equation 的每個 crop_unit 執行以下循環：

### 3a. 定位與裁切

先讀 page preview 確認方程式位置，再裁切。

1. **讀 page preview + notes 定位**：讀取該 equation 所在頁面的 page preview（`shared/previews/page_N_preview.png`）。根據 notes 中的 LaTeX、位置描述和周圍 context，在頁面上找到目標方程式。密集頁面（如 proof appendix）可能有多個結構相似的方程式（如多個 Π 展開式），用 notes 中的**周圍 context**（"在 But, 開頭的結論之後"、"在 Supplier 1's profits 段落中"）來區分，不要只靠數學內容識別。
2. **自己估算 crop_px**：根據自己在 page preview 上看到的位置估算 crop_px（從 preview 座標乘以 scale factor 換算到完整解析度）。**完全忽略 plan/equations.json 中的 crop_px**——scanner 的 crop_px 從未準確過，試圖使用它只會浪費一次 crop 循環。多行方程式（≥3 行）底部多留 150px margin，寧可第一刀切太大再收緊，也不要太小再擴展（底部 clipping 是最常見的 failure，擴展需要重跑整個 crop+preview 流程）。
3. **裁切**：用自己估算的 crop_px 跑 `crop_and_preview.py`。

- `crop_px` 使用完整解析度頁面圖片 pixel coordinate `[x1, y1, x2, y2]`。
- Final crop 從頁面圖片裁出，不從中間圖片再裁。
- crop_id 命名：單一 crop unit 用 `equation_id`；跨頁方程式用 `equation_id` + `_part_1`、`_part_2` 等。
- 多行方程式（aligned、cases、matrix 等）作為單一區塊裁切，不拆開。

### 3b. 驗證 boundary preview

讀 boundary preview，檢查 cyan 矩形與周圍 context。**不可以有任何方程式內容跨越 cyan 線。**

- **整體 framing**：cyan 矩形是否合理地框住方程式內容（含編號）？如果 crop 像整頁、整欄或大頁面條帶，不能標 pass。
- **四邊檢查**：方程式內容穿過 cyan 線 → 該邊太緊，放大。非方程式內容（正文、page chrome）貼到 cyan 線 → 該邊太鬆，縮小。也檢查 cyan 矩形外側是否有屬於此方程式的內容（如方程式編號、大型括號的尖端）。外側有方程式 content → 該邊太緊，放大。
- **Defects（如有）**：逐一確認 plan 中列出的 defects 是否已解決。
- **Crop 貼到 page 邊**是 full-bleed，不算 fail。

### 3c. 驗證 crop preview

讀 crop preview，檢查方程式內部細節：

- 小型記號完整：下標、上標、上下限、撇號、橫線、帽號、點、希臘字母。
- 多行對齊、分段函數、矩陣、括號結構完整。
- 方程式編號完整可見（如有）。
- 排除：周圍正文、頁碼、頁眉、頁腳、期刊元素、浮水印、相鄰方程式或圖表。
- 不確定時讀 source.pdf 對應頁面確認；仍不確定在 `notes` 說明。

### 3d. 調整與重裁

發現問題 → 調整 crop_px → 刪掉該 crop_id 的舊檔案（`rm crops/{crop_id}* previews/{crop_id}*`）→ 重跑 `crop_and_preview.py`（同一個 crop_id）→ 回到 3b。

- 方程式內容被切到 → 放大 crop_px。
- 非方程式內容混入 → 縮小 crop_px。
- 跨頁方程式每頁一個 crop_unit，同一個 `equation_id`。

停止條件：所有邊乾淨 → 結束循環，進入 Step 4。多輪調整後問題仍無法解決 → 也結束循環，在 `notes` 說明原因。

## Step 4: LaTeX 轉寫與驗證

邊界確認後，對每個 equation 從 crop preview 轉寫 LaTeX。

### 4a. 轉寫

結合 crop preview（視覺結構）和 source.pdf（精確符號，用 Read tool 的 `pages` 參數讀取）轉寫 LaTeX。Preview 確認結構和排版，source.pdf 確認每個符號。**不得從 scanner notes 中的 LaTeX 複製。**

LaTeX 規則：
- 保留分式（`\frac`）、上標（`^{}`）、下標（`_{}`）、根號（`\sqrt`）、矩陣、分段函數（`\begin{cases}`）、求和/積分上下限、希臘字母、運算子和有意義的對齊。
- 多行環境：保留 `\begin{aligned}`、`\begin{cases}`、`\begin{pmatrix}` 等結構。不要把多行方程式壓成單行。
- 重音變體：單字元用 `\hat{x}`，多字元用 `\widehat{XY}`。`\tilde`/`\widetilde`、`\bar`/`\overline`、`\dot`/`\ddot` 同理。比較 crop 中的重音寬度來選擇。
- 方程式編號存在 `equation_number` 欄位中，不放進 `latex` 欄位。
- 符號歧義先比對 source.pdf；仍無法判定則記錄在 `notes`。

### 4b. 驗證

讀 crop preview，確認：
- Crop 中的方程式和 plan notes 描述的是同一個方程式（內容、位置、周圍 context 一致）。不是同一個 → 重新定位裁切。
- `equation_number` 和 crop 中可見的編號一致。`latex` 中不含編號。
- 逐一比對 LaTeX 中的每個符號、結構和對齊，確認 LaTeX 準確反映 crop 中可見的數學結構。不一致 → 修正 LaTeX，重新比對。

Repair mode 中如果 defect 是 LaTeX 問題（非邊界問題），可以保留現有 crop_px 不動，只修正 LaTeX。

停止條件：LaTeX 和 crop 視覺比對一致 → 進入 Step 5。多輪修正後仍有無法解決的符號歧義 → 也進入 Step 5，在 `notes` 記錄不確定性。

## Step 5: 寫出 equations.json 並自檢

寫出 `equations.json`（格式見下方 `# 格式`），然後做 local self-check：

- JSON 可 parse。
- `schema_version` 是 `"equation_extraction.v1"`。
- `equations` 是陣列。
- 每個 equation 有 `equation_id`（唯一）、`equation_number`（非空）、`equation_type`（`displayed`/`inline`）、`crop_units`（非空陣列）、`latex`（非空字串）、`verification`、`notes`。
- 每個 crop unit 有 `crop_id`（唯一於 equation 內）、`page`（整數）、`crop_px`（`[x1, y1, x2, y2]`，四個整數，`0 ≤ x1 < x2`，`0 ≤ y1 < y2`，不超過頁面圖片尺寸）、`role`（非空）、`crop_image`、`previews`。
- Crop 圖片檔案存在，尺寸與 `crop_px` 一致（寬 = x2-x1，高 = y2-y1）。
- `previews` 中列出的所有檔案都存在（`crop` + `boundary`）。
- `verification` 有 8 個 key，每個值是 `"pass"` 或 `"fail"`。`result` 是 `"pass"` 時，其餘 7 個 key 都必須是 `"pass"`。

Verification 語意：不確定時先讀 source.pdf 確認；仍不確定 → 標 fail 並在 notes 說明原因。即使 result = fail 也要寫出 JSON——reviewer 會根據 verification 和 notes 決定是否需要 repair。頁面圖片缺失 → 該 crop unit 不進循環，直接標 fail。

# 格式

`equations.json`，`schema_version: "equation_extraction.v1"`。

## Example

```json
{
  "schema_version": "equation_extraction.v1",
  "worker_id": "worker_01",
  "equations": [
    {
      "equation_id": "Equation_1",                     // 從 plan 搬入
      "equation_number": "(1)",                        // 從 plan 搬入
      "equation_type": "displayed",                     // 從 plan 搬入；displayed|inline
      "latex": "E = \\frac{1}{2} m v^2",              // 從 crop 視覺證據轉寫，不含編號
      "crop_units": [
        {
          "crop_id": "Equation_1",                     // 單一 crop = equation_id
          "page": 3,
          "crop_px": [150, 1200, 2350, 1310],          // 驗證後的最終值
          "role": "complete equation",
          "crop_image": "crops/Equation_1.png",
          "previews": {                               // --boundary-only: 只有 crop + boundary
            "crop": "previews/Equation_1_preview.png",
            "boundary": "previews/Equation_1_boundary_preview.png"
          }
        }
      ],
      "verification": {                                // 逐項 "pass" 或 "fail"
        "final_crop_checked": "pass",                  // 讀過 crop preview，方程式內部細節完整
        "boundary_checked": "pass",                    // 讀過 boundary preview，四邊 framing 正確
        "equation_content_complete": "pass",           // 沒有被切掉的符號、編號、結構
        "body_text_excluded": "pass",                  // 周圍正文不在 crop 中（inline 類型：周圍正文在預期範圍內即 pass）
        "page_chrome_excluded": "pass",                // 頁眉、頁腳、頁碼不在 crop 中
        "no_adjacent_content": "pass",                 // 相鄰方程式、圖表不在 crop 中（inline 類型：同句正文在預期範圍內即 pass）
        "latex_verified": "pass",                      // LaTeX 符合 crop 中可見的數學結構
        "result": "pass"                               // 以上全部 pass
      },
      "notes": []
    }
  ]
}
```

## 規則

- **`crop_id`**：單一 crop = `equation_id`；跨頁 = `equation_id` + `_part_1`、`_part_2`。
- **`crop_image` + `previews`**：所有路徑是 relative path。Worker 跑完 `crop_and_preview.py` 後，把實際產出的檔案路徑填入。
- **`latex`**：從 crop preview 視覺證據獨立轉寫，不從 PDF text extraction 或 scanner notes 複製。方程式編號不放進 `latex`（存在 `equation_number`）。
- **`verification`**：`result` 是 `"pass"` 時，其餘 7 個 key 都必須是 `"pass"`。
