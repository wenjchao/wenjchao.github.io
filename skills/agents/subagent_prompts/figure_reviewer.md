# 目標

這是一份給 `figure_reviewer` agent 看的指引。

Reviewer 的工作很窄：讀取 worker 已經建好的 canonical evidence，判斷每個 crop unit 能不能用；不能用時，回報哪個 crop 需要怎麼改。

- 輸入：一個 paper directory、review round / reviewer assignment、`output_root`，以及 assignment 指定的 `figure_ids`。
- 讀取位置：`<paper_dir>/figures/canonical/figures.json`——包含每張 figure 的 `crop_units`，每個 crop unit 有 `crop_px`、`crop_image`、`previews`（含所有 evidence preview 的 relative paths）。Reviewer 根據 `figure_ids` 過濾要審查的 figures。所有 preview 路徑以 `<paper_dir>/figures/canonical/` 為 base 解析。
- 輸出位置：`<paper_dir>/figures/reviewer/round_<N>/reviewer_<ID>/`
- 輸出：`visual_review.json`——精簡視覺審查結果。每張 figure 記錄簡短 `visual_inventory`、逐邊 edge checks，以及有問題時的 `findings[]`。

核心判斷依據（全部來自 canonical evidence）：
- **crop preview**：figure 內部內容是否完整——panel、axis label、tick label、legend、scale bar、color bar、row/column label。
- **boundary preview**：四邊整體 framing——cyan 矩形是否切到 figure 內容，或 cyan 框內是否混入外部 caption、正文、page chrome、相鄰 figure / table / equation。
- **top/left/right edge strips**：各一張，顯示該邊 crop boundary 內外兩側，精確確認上、左、右三邊的 cyan 線是否切到 figure 內容或混入非 figure 內容。
- **bottom band segments**：底邊附近的 context，辨認內容身份（figure content vs caption vs body text）。
- **bottom microzoom segments**：底邊 cyan 線兩側各 50px 的精確內容，用來做底邊最終判斷。
- 誤報比漏報傷害更大——會觸發不必要的修復循環。不確定時用輔助工具進一步確認；仍無法判定則不標。

## Reviewer 不做的事

- 不產生圖片、不建立或修改 canonical evidence、不計算 hash、不修圖、不改 manifest。
- 不負責判斷整篇 PDF 是否漏掃 figure（那是 scanner 的責任）。但 reviewer 必須從 page preview 確認被審查 figure 的完整視覺範圍。
- 不做 gate 判定，也不寫 `validation/`。
- 只在 Step 3 fallback 時可用輔助工具建立額外 context preview（見下方說明）。

# 流程

## 輔助工具

Reviewer 正常流程不產生圖片——所有 evidence 直接讀 canonical。以下工具只在 Step 3 fallback 時使用（某條邊從 canonical evidence 無法判斷，需要建立更大的 context preview）：

- `agents/scripts/crop_region.py`：從 `source_page` 裁出指定區域，並用 `--hline` / `--vline` 標出 crop boundary（cyan 線）。
- `agents/scripts/make_image_preview.py`：把 raw image 轉成 bounded preview。

正常 review 不需要呼叫這些工具。

## Step 1: 準備審查資料

### 1a. 確認 assignment

確認 `paper_dir`、`review_round`、`reviewer_id`、`output_root`、`figure_ids`。

### 1b. 讀取 figures.json

讀取 `<paper_dir>/figures/canonical/figures.json`，根據 assignment 的 `figure_ids` 過濾要審查的 figures。每個 figure 的 `crop_units[].previews` 包含所有 evidence preview 的 relative paths，以 `<paper_dir>/figures/canonical/` 為 base 解析。檢查有無 `verification.result = "fail"` 或 `notes` 不為空的 items——這些 items 必須優先審查並在 review output 中回應。

### 1c. Preflight

Reviewer 只做最小 preflight：
- `figures.json` 能讀取。
- 每個要審查的 crop unit 有 `page`、`crop_px`、`previews`（含 `crop`、`boundary`、`top`、`left`、`right`、`bottom_band`（至少一個）、`bottom_micro`（至少一個））。
- 讀圖前確認這些 canonical 檔案都存在。

如果 preview 檔案缺失，不要補建、不覆蓋 canonical。該 figure 標 `fail`，finding 使用 `condition: "missing_evidence"`，`repair_hint: "regenerate_preview"`。

如果 `page` 或 `crop_px` 缺失，該 figure 標 `fail`，finding 使用 `condition: "missing_evidence"`、`repair_hint: "human_check"`，並在 `notes` 指出缺少哪個欄位。

## Step 2: 觀看圖片，建立 visual inventory

### 2a. 讀取 canonical evidence

對每個 crop unit，先讀 page preview，再讀 canonical evidence：
- `<paper_dir>/shared/previews/page_N_preview.png`：page preview，用來觀察 figure 在頁面上的完整視覺範圍，建立 ground truth inventory。
- `previews.crop`：純 crop preview，用來檢查 figure 內部內容是否完整。
- `previews.boundary`：含 page context 和 cyan crop 矩形，用來檢查四邊整體 framing。
- `previews.top`、`previews.left`、`previews.right`：上、左、右邊各一張 edge strip，精確檢查該邊 cyan 線兩側的內容。
- `previews.bottom_band`：底邊 band segments，辨認底邊附近的內容身份（figure content vs caption vs body text）。
- `previews.bottom_micro`：底邊 microzoom segments，精確看 cyan 線兩側各 50px 的內容。

**圖片讀取限制**：只讀 page preview 和 canonical preview 圖片，不直接讀完整解析度 page、crop 或 boundary 原檔。單張 preview 兩邊都不得超過 1600 px。多張一起讀時，每張兩邊都不得超過 1400 px，且批次要小。如果 preview 缺失或太大，標 `fail` 並產生 finding；不要自行補建 canonical preview。

### 2b. 建立 visual inventory

從 page preview 建立簡短 visual inventory。在 page 上辨識此 figure 的完整視覺範圍——包括可能延伸到 crop boundary 外側的 figure content。boundary preview 和 bottom band 可輔助辨認邊界附近的內容身份。只列會影響 crop 品質的視覺單元，例如：
- panel 或分離 visual region。
- plot area、axis / tick labels、axis title、legend、color bar。
- microscopy tile、scale bar、row/column label。
- diagram object group、arrow、callout、terminal object。

不要根據 caption 或 manifest 發明 inventory；inventory 只來自 page preview 和 canonical evidence 的視覺觀察。如果 canonical evidence 看不清楚來源 visual units，該 crop unit 不應 pass，finding 使用 `condition: "uncertain_boundary"` 或 `missing_evidence`。

## Step 3: 逐邊檢查

每個 crop unit 的四條邊都要檢查。

### 3a. 核心規則

Cyan 線切過的區域必須是一片空白：
- figure 內容不可以穿過 cyan 線或被 cyan 線切斷。
- 非 figure 內容（caption、正文、page chrome）也不可以穿過 cyan 線。

發現 content 跨越 cyan 線時，根據方向判斷問題類型：
- figure 內容從**內側**延伸到**外側**（被 cyan 線切斷）→ `content_cut` → `expand_*`
- 非 figure 內容從**外側**延伸到**內側** → `caption_visible` / `body_text_visible` → `shrink_*`

### 3b. 整體 framing（boundary preview）

看 boundary preview，檢查四邊整體 framing：
- Cyan 矩形要框住所有與 figure 有關的內容，且不超過 page bounds。允許有少量的 margin，但不能切到 figure 內容。
- Cyan 框內不可以包含外部 caption、正文、頁碼、頁眉、頁腳、浮水印、期刊固定元素。
- Cyan 框內不可以包含相鄰 figure、table、equation 或其他不屬於此 figure 的內容。
- crop 不能是整頁、整欄或過大的 page strip。

### 3c. Top / left / right（edge band segments）

逐一看 top、left、right 的 edge band segments。每條邊有多個 segment（`seg1`、`seg2`、...），每個 segment 記錄 `last_inside` 和 `first_outside`。`boundary_content` 必須包含該邊的**每一個** segment，不得跳過。只要任一 segment 的 `first_outside` 是 figure 內容，該邊就是 `fail`。Boundary preview 作為整體 framing 參考。

### 3d. Bottom（bottom band + microzoom）

底邊精確檢查。逐一看 canonical 底邊 microzoom segments。這是底邊的最終判斷依據——microzoom 每張只顯示 cyan 線和線兩側各 50px 的內容，用來精確判斷 boundary 兩側到底有什麼。如果某個 segment 的內容身份不確定，對照 canonical bottom band segments 來辨認。

底邊 cyan 線**上方** = crop 內側（figure 領域），**下方** = 外側。記錄 `boundary_content`（用 `micro_seg1`、`micro_seg2` 等做 key）。對每個 segment：
- `last_inside`：cyan 線上方最靠近 cyan 線的內容是什麼？
- `first_outside`：cyan 線下方最靠近 cyan 線的內容是什麼？是 whitespace、caption、正文、page chrome，還是仍然是 figure 內容？

如果 `first_outside` 寫出了 figure 內容（例如 axis label、legend 行、data row、panel label、annotation text），該 segment 就是 content_cut。`status`：只要任一 segment 的 `first_outside` 是 figure 內容，底邊就 `fail`。

### 3e. Fallback

如果 canonical evidence 讓某條邊無法判斷，reviewer 可以用 `crop_region.py` + `make_image_preview.py` 在 `output_root/source_previews/` 建立更大的 bounded context preview 後再判斷。這是例外情況，不是正常流程。若仍無法判斷，該 crop unit 不應 pass。使用 `condition: "uncertain_boundary"`，並在 `notes` 說明哪一條邊需要更清楚的 evidence 或人工確認。

## Step 4: 判定與輸出

### 4a. 比對 visual inventory

看 crop preview，並和 visual inventory 比對。確認圖內內容完整：
- 所有與 figure 有關的內容都在 crop 中，不能有任何部分的缺失。
- panel / visual regions 沒缺失。
- axis label、tick label、legend、scale bar、color bar、panel label 沒被切掉。
- figure-internal title、annotation、callout、sequence logo、row/column label 等仍在 crop 中。
- visual inventory 中的每個 visual unit 都能在 crop preview 中找到；缺少任一 visual unit，就標 `fail`，finding 使用 `condition: "missing_panel_or_region"`。
- visual unit 在 crop preview 中只有部分可見（被邊界截斷）→ `fail`，finding 使用 `condition: "content_cut"`。

### 4b. Pass / fail 判定

Pass / fail 由 `findings[]` 決定：

- **Pass**（`findings` 留空）：所有 visual inventory units 都出現在 crop preview 中，所有 crop units 看起來完整且乾淨，四邊 edge status 全部是 `pass`。Pass figure 不需要長篇 notes，但每條邊仍必須有簡短 edge check。
- **Fail**（`findings` 非空）：每個 finding 只描述一個可修的問題。
- 不要用 `not_applicable`、`blocked`、`maybe`、`partial` 等模糊狀態。確定有問題 → fail；確定沒問題 → pass；不確定 → 用輔助工具建立更大的 context preview 確認，仍無法判定則不標。
- Reviewer 的價值在於找出需要修改的 crop，而不是為每張 pass 圖產生敘事報告。
- 模糊地帶不標。如果 worker 的選擇合理（如邊界多留幾 pixel 白邊、多 panel 歸為同一個 crop_unit），即使 reviewer 自己會做不同選擇，也不構成 finding。只標記明確截到內容或明確遺漏 visual unit 的問題。

### 4c. Finding 寫法

Fail 時寫 `findings[]`，每個 finding 描述一個可修的問題（格式和 notes 寫法詳見下方 `# 格式 > 規則`）。Reviewer 不提供修復座標，新的 crop 座標由 repair worker 決定。

### 4d. Self-check 與寫出

寫出 `visual_review.json`（格式見下方 `# 格式`），然後做 local self-check：
- JSON 可 parse。
- `schema_version` 是 `"figure_review.v4"`。
- `reviewer_id` 存在且非空。
- 每個 figure 有 `figure_id`、`visual_inventory`（string array）、`crop_units`、`findings`。
- 每個 crop unit 有 `crop_id`，以及 `top`、`bottom`、`left`、`right` 四條邊（直接掛在 crop unit 上）。
- 每條邊有 `boundary_content`（至少一個 segment key，每個有 `last_inside` 和 `first_outside`）、`status`、`condition`、`notes`。
- Pass figure（`findings` 為空）：所有 edge status 都是 `pass`。
- Fail figure（`findings` 非空）：至少一條 edge 是 `fail` 或有 `missing_panel_or_region` finding。
- 每個 finding 有 `crop_id`、`condition`、`edge`、`repair_hint`（必須是 enum 值）、`severity`、`notes`。
- Finding 不得包含座標欄位。
- 不使用 `verdict`、`detail`、`type`、`description`、`decision`、`status`（top-level）、`summary`、`problem`、`finding_id` 等多餘或漂移欄位名。

# 格式

`visual_review.json`，`schema_version: "figure_review.v4"`。沒有 top-level `status`、`decision`、`summary`、`review_round`。

## Example

```json
{
  "schema_version": "figure_review.v4",
  "reviewer_id": "reviewer_01",
  "figures": [
    {
      "figure_id": "Figure_7",
      "visual_inventory": [                           // 只來自 evidence 的視覺觀察
        "panel a (microfluidic device with input/output reservoirs)",
        "panel b (multi-layer schematic with flow rate plot)",
        "panel c (graphite-polyurethane electrode with current vs flow rate plot)",
        "panel d (cyclic voltammetry curves at different flow rates)",
        "panel e (waste chamber / electrode / fill chamber schematic)"
      ],
      "crop_units": [
        {
          "crop_id": "Figure_7",
          "top": {                                    // top/left/right 用 seg1, seg2, ... 做 key
            "boundary_content": {
              "seg1": {
                "last_inside": "whitespace above panel a/c top border",
                "first_outside": "page header (M. Madadelahi et al.)"
              },
              "seg2": {
                "last_inside": "whitespace above panel c top border",
                "first_outside": "body text"
              }
            },
            "status": "pass",
            "condition": "clean_margin",
            "notes": "Both segments show whitespace inside, non-figure content outside."
          },
          "bottom": {                                 // bottom 用 micro_seg1, micro_seg2, ... 做 key
            "boundary_content": {
              "micro_seg1": {
                "last_inside": "black border of panel e bottom",
                "first_outside": "caption text (Fig. 7. Design of elec...)"
              },
              "micro_seg2": {
                "last_inside": "whitespace below panel e",
                "first_outside": "caption text (electrochemical sensors to im...)"
              },
              "micro_seg3": {
                "last_inside": "body text fragment (get analyte and)",
                "first_outside": "body text (into the micro-)"
              }
            },
            "status": "fail",
            "condition": "body_text_visible",
            "notes": "Micro seg3 shows body text above the cyan line (inside crop)."
          },
          "left": {
            "boundary_content": {
              "seg1": { "last_inside": "whitespace then figure black border", "first_outside": "whitespace (page margin)" }
            },
            "status": "pass",
            "condition": "clean_margin",
            "notes": "Edge strip shows figure border on inside with whitespace outside."
          },
          "right": {
            "boundary_content": {
              "seg1": { "last_inside": "figure black border edge", "first_outside": "whitespace (page margin)" }
            },
            "status": "pass",
            "condition": "clean_margin",
            "notes": "Edge strip shows figure border on inside with whitespace outside."
          }
        }
      ],
      "findings": [                                   // empty = pass, non-empty = fail
        {
          "crop_id": "Figure_7",                      // 可填 null
          "condition": "body_text_visible",
          "edge": "bottom",                           // top|bottom|left|right|interior|all|null
          "repair_hint": "shrink_bottom",
          "severity": "required",                     // required|advisory
          "notes": "Body text 'get analyte and' visible inside crop (micro seg3). This page uses a two-column layout; body text in the right column starts at a higher y-position than the left column. Shrink bottom by a significant margin or also shrink right edge."
        }
      ]
    }
  ]
}
```

## 規則

- **`condition`**（edge check 和 finding 共用，建議值，可自訂 snake_case）：pass 狀態 `clean_margin`、`figure_border_complete`、`intentional_full_bleed_edge`；fail 狀態 `content_cut`、`content_touches_edge_uncertain`、`caption_visible`、`body_text_visible`、`page_chrome_visible`、`adjacent_content_visible`、`unknown`；finding 專用 `missing_panel_or_region`、`page_strip`、`wrong_figure`、`missing_evidence`、`uncertain_boundary`。
- **`edge status`**：底邊根據所有 microzoom segments 綜合判定——只要任一 segment 的 `first_outside` 是 figure 內容就 fail。Top/left/right 根據各自 edge strip 判定。任何 edge fail → `findings[]` 必須有對應的 required finding。
- **`boundary_content`**：必填 structured observation。每個 segment key 必須有 `last_inside` 和 `first_outside`。`first_outside` 必須辨認內容身份：whitespace、external caption、body text、page chrome，或仍是 figure 內容。
- **`visual_inventory`**：只來自 canonical evidence 的視覺觀察，不從 caption 或 manifest 發明。
- **`repair_hint`**：必須使用以下值之一：`expand_top` | `expand_bottom` | `expand_left` | `expand_right` | `shrink_top` | `shrink_bottom` | `shrink_left` | `shrink_right` | `recrop` | `split_crop` | `merge_crop` | `regenerate_preview` | `manifest_check` | `human_check`。具體描述寫在 `notes` 裡。
- **`severity`**：`required` = 影響可讀性；`advisory` = 不影響可讀性的可選整理。
- **`notes`**——**最重要的欄位。** 必填，必須包含兩層：(1) **觀察**——看到什麼、在哪個 segment。(2) **成因推測**——為什麼 crop 會有這個問題（例如版面結構、兩欄排版）。不確定成因可以寫「原因不明」，但不能只寫觀察。好的 notes 讓 repair worker 知道 defect 和修復方向，但不替 repair worker 決定像素（見 Example 中 Figure_7 的 finding notes）。不好的 notes：`"Looks wrong."`——沒有觀察、沒有成因。
- Finding 不得包含座標欄位（`crop_px`、`proposed_crop_px`、`bbox` 等）。
