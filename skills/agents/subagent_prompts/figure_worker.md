# 目標

這是一份給 figure_worker agent 看的指引。

此 agent 做一件事：拿到一組 figure 和起始 crop 座標，產出準確的 final crop。不切掉 figure 的任何部分，同時盡可能裁掉非 figure 的部分。

這個 agent 同時用於兩種場景：
- **Initial extraction**：scanner 給出 figure list 和粗略 crop_px，worker 裁切並收緊。
- **Repair**：reviewer 發現問題，orchestrator 給出現有 crop_px 和 defects 描述，worker 修正並重新驗證。

兩種場景的核心流程相同（裁切 → 驗證 → 調整），輸出格式相同（figures.json）。差別在輸入來源：initial 讀 `figure_plan.json`（crop_px 偏大，需要收緊），repair 讀 `figures.json` + `visual_review.json`（crop_px 已接近正確，有特定 defect 需要修正）。


- 輸入：paper directory、`mode`（initial 或 repair）、`figure_ids`、`output_root`。Initial 讀 `canonical/figure_plan.json`，repair 讀 `canonical/figures.json` + `canonical/visual_review.json`。
- 輸出：`figures.json`、`crops/`、`previews/`。

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
  --output-dir <output_root>
```

產出：`crops/<crop_id>.png`（final crop）、`previews/<crop_id>_preview.png`（crop preview）、`previews/<crop_id>_boundary_preview.png`（boundary preview，含 cyan 矩形）、三邊 edge strips、bottom band segments、bottom microzoom segments。重跑同一個 crop_id 會覆寫全部檔案。

## Step 1: 讀取輸入

根據 assignment 的 `mode` 決定輸入來源。所有檔案從 `<paper_dir>/figures/canonical/` 讀取。

**`mode: initial`**：讀 `canonical/figure_plan.json`，根據 `figure_ids` 過濾要處理的 figures。每張 figure 有 `figure_id`、`figure_label`、`figure_type`、`caption_text`、`crop_units`（含 `page`、`crop_px`）。crop_px 是偏大的起始估計，需要驗證後收緊。

**`mode: repair`**：讀 `canonical/figures.json` 取得 figure metadata + current crop_px，讀 `canonical/visual_review.json` 取得 findings。根據 `figure_ids` 過濾要修復的 figures。對每個 figure，從 `visual_review.json` 找出 `severity: "required"` 的 findings，把 finding 的 `notes` 當作 defects。裁切時優先處理這些已知問題。

## Step 2: 確認前置條件

確認 `shared/pages/page_N.png` 對 plan 涉及的所有頁面都存在。建立 `<output_root>/crops/` 和 `<output_root>/previews/`。

## Step 3: 裁切與視覺驗證

對每張 figure 的每個 crop_unit 執行以下循環：

### 3a. 裁切

用 plan 的 `crop_px` 作為初始座標，跑 `crop_and_preview.py`。

- `crop_px` 使用完整解析度頁面圖片 pixel coordinate `[x1, y1, x2, y2]`。
- Final crop 從頁面圖片裁出，不從中間圖片再裁。
- crop_id 命名：單一 crop unit 用 `figure_id`；多個 crop units 用 `figure_id` + `_part_1`、`_part_2` 等。

### 3b. 驗證 boundary preview

讀 boundary preview，檢查 cyan 矩形與周圍 context。**不可以有任何圖片物體跨越 cyan 線。**

- **整體 framing**：cyan 矩形是否合理地框住 figure 內容？如果 crop 像整頁、整欄或大頁面條帶，不能標 pass。
- **四邊檢查**：figure 內容穿過 cyan 線 → 該邊太緊，放大。非 figure 內容（caption、正文、page chrome）貼到 cyan 線 → 該邊太鬆，縮小。也檢查 cyan 矩形**外側**是否有屬於此 figure 的 content（如 radiating labels、detached legend）。外側有 figure content → 該邊太緊，放大。
- **Defects（如有）**：逐一確認 plan 中列出的 defects 是否已解決。
- **Crop 貼到 page 邊**是 full-bleed，不算 fail。

### 3c. 驗證 crop preview

讀 crop preview，列出此 figure 的 visual units（panels、axis labels、tick labels、legend、color bar、比例尺等），逐一確認每個 unit 都在 crop 中且完整。

排除規則：
- 外部圖說不放進 crop，只存 `caption_text`。
- 圖內嵌入文字（圖例、座標軸標籤、panel label、color bar、比例尺）保留在 crop。
- 排除：正文、外部圖說、頁碼、頁眉、頁腳、期刊元素、浮水印、相鄰圖表。
- 不確定時讀 source.pdf 對應頁面確認；仍不確定在 `notes` 說明。

### 3d. 逐邊精準檢查（按需）

Boundary preview 中某邊看起來緊或不確定時，讀該邊的 edge band segments 逐 segment 確認 cyan 線兩側的內容。四邊都有 segmented edge strips 可用。底邊額外有 bottom microzoom segments（各 50px），用於圖表型圖片（折線圖、長條圖、散點圖、熱圖）的底邊精準確認。

### 3e. 調整與重裁

發現問題 → 調整 crop_px → 刪掉該 crop_id 的舊檔案（`rm crops/{crop_id}* previews/{crop_id}*`）→ 重跑 `crop_and_preview.py`（同一個 crop_id）→ 回到 3b。

- Figure 內容被切到 → 放大 crop_px。
- 非 figure 內容混入 → 縮小 crop_px。
- 版面交錯無法乾淨分離 → 優先保留 figure 全部內容，在 `notes` 說明。
- 多 panel figure 預設同一張。跨頁或多區域用多個 `crop_units`，同一 `figure_id`。不為單一矩形裁入中間正文。

停止條件：所有邊乾淨 → 結束循環，進入下一步。多輪調整後問題仍無法解決（例如版面交錯無法乾淨分離）→ 也結束循環，在 `notes` 說明原因。

## Step 4: 寫出 figures.json 並自檢

寫出 `figures.json`（格式見下方 `# 格式`），然後做 local self-check：

- JSON 可 parse。
- `schema_version` 是 `"figure_extraction.v4"`。
- `figures` 是陣列。
- 每個 figure 有 `figure_id`（唯一）、`figure_label`（非空）、`figure_type`（`main`/`extended`/`supplementary`/`other`）、`caption_text`、`crop_units`（非空陣列）、`verification`、`notes`。
- 不得包含 `pages`、`image_files`、`crop_count` 等衍生欄位。
- 每個 crop unit 有 `crop_id`（唯一於 figure 內）、`page`（整數）、`crop_px`（`[x1, y1, x2, y2]`，四個整數，`0 ≤ x1 < x2`，`0 ≤ y1 < y2`，不超過頁面圖片尺寸）、`role`（非空）、`crop_image`、`previews`。
- Crop 圖片檔案存在，尺寸與 `crop_px` 一致（寬 = x2-x1，高 = y2-y1）。
- `previews` 中列出的所有檔案都存在：`crop`、`boundary`、`top`（≥1）、`left`（≥1）、`right`（≥1）、`bottom_band`（≥1）、`bottom_micro`（≥1）。
- `verification` 有 7 個 key（`final_crop_checked`、`boundary_checked`、`figure_content_complete`、`caption_excluded`、`page_chrome_excluded`、`no_adjacent_content`、`result`），每個值是 `"pass"` 或 `"fail"`。
- `result` 是 `"pass"` 時，其餘 6 個 key 都必須是 `"pass"`。

Verification 語意：不確定時先讀 source.pdf 確認；仍不確定 → 標 fail 並在 notes 說明原因。即使 result = fail 也要寫出 JSON——reviewer 會根據 verification 和 notes 決定是否需要 repair。頁面圖片缺失 → 該 crop unit 不進循環，直接標 fail。

# 格式

`figures.json`，`schema_version: "figure_extraction.v4"`。

## Example

```json
{
  "schema_version": "figure_extraction.v4",
  "worker_id": "worker_01",
  "figures": [
    {
      "figure_id": "Figure_1",                       // 從 plan 搬入
      "figure_label": "Fig. 1",                      // 從 plan 搬入
      "figure_type": "main",                         // 從 plan 搬入
      "caption_text": "Fig. 1 | Generation of idealized scaffolds...",
      "crop_units": [
        {
          "crop_id": "Figure_1",                     // 單一 crop = figure_id；多 crop = figure_id + _part_1, _part_2
          "page": 2,
          "crop_px": [88, 90, 2395, 1840],           // 驗證後的最終值
          "role": "complete figure",                  // 短描述
          "crop_image": "crops/Figure_1.png",         // relative path
          "previews": {                               // crop_and_preview.py 產出的實際檔案路徑
            "crop": "previews/Figure_1_preview.png",
            "boundary": "previews/Figure_1_boundary_preview.png",
            "top": ["previews/Figure_1_top_seg1_preview.png", "previews/Figure_1_top_seg2_preview.png"],
            "left": ["previews/Figure_1_left_seg1_preview.png"],
            "right": ["previews/Figure_1_right_seg1_preview.png"],
            "bottom_band": ["previews/Figure_1_bottom_seg1_preview.png", "previews/Figure_1_bottom_seg2_preview.png"],
            "bottom_micro": ["previews/Figure_1_micro_bottom_seg1_preview.png", "previews/Figure_1_micro_bottom_seg2_preview.png"]
          }
        }
      ],
      "verification": {                              // 逐項 "pass" 或 "fail"
        "final_crop_checked": "pass",                // 讀過 crop preview，figure 內部細節完整
        "boundary_checked": "pass",                  // 讀過 boundary preview，四邊 framing 正確
        "figure_content_complete": "pass",           // 沒有被切掉的 panel、axis、legend
        "caption_excluded": "pass",                  // 外部 caption 不在 crop 中
        "page_chrome_excluded": "pass",              // 頁眉、頁腳、頁碼不在 crop 中
        "no_adjacent_content": "pass",               // 相鄰 figure、table、正文不在 crop 中
        "result": "pass"                             // 以上全部 pass
      },
      "notes": []
    }
  ]
}
```

## 規則

- **`crop_id`**：單一 crop = `figure_id`；多 crop = `figure_id` + `_part_1`、`_part_2`。
- **`crop_image` + `previews`**：所有路徑是 relative path。Worker 跑完 `crop_and_preview.py` 後，把實際產出的檔案路徑填入。
- **`verification`**：`result` 是 `"pass"` 時，其餘 6 個 key 都必須是 `"pass"`。
- 不得包含 `pages`、`image_files`、`crop_count` 等衍生欄位。
