# 目標

這是一份給 `equation_reviewer` agent 看的指引。

Reviewer 的工作：讀取 worker 已經建好的 canonical evidence，判斷每個 crop unit 的邊界品質和 LaTeX 正確性；不能用時，回報哪個 crop 或 LaTeX 需要怎麼改。

- 輸入：一個 paper directory、review round / reviewer assignment、`output_root`，以及 assignment 指定的 `equation_ids`。
- 讀取位置：`<paper_dir>/equations/canonical/equations.json`——包含每個 equation 的 `crop_units`（含 `crop_px`、`crop_image`、`previews`）和 `latex`。Reviewer 根據 `equation_ids` 過濾要審查的 equations。所有 preview 路徑以 `<paper_dir>/equations/canonical/` 為 base 解析。
- 輸出位置：`<paper_dir>/equations/reviewer/round_<N>/reviewer_<ID>/`
- 輸出：`visual_review.json`——精簡審查結果。每個 equation 記錄 `visual_inventory`、逐邊 edge checks、LaTeX 審查，以及有問題時的 `findings[]`。

Reviewer 的工作是找缺陷，不是背書。Source.pdf（用 Read tool 的 `pages` 參數讀取，每次 ≤20 頁）和 preview 是共主來源：source.pdf 決定符號內容，preview 決定邊界和版面。Crop 和 LaTeX 要拿來對照這兩者。誤報比漏報傷害更大——會觸發不必要的修復循環。

核心判斷依據：
- **crop preview**：方程式內部內容是否完整——符號、上下標、上下限、對齊結構、編號。
- **boundary preview**：四邊整體 framing——cyan 矩形是否切到方程式內容，或混入外部正文、page chrome。
- **boundary preview**：四邊整體 framing（equation lane 不使用 edge strips 和 microzoom）。
- **latex vs crop preview**：LaTeX 是否準確反映 crop 中可見的數學結構。
- 誤報比漏報傷害更大——會觸發不必要的修復循環。不確定時讀 source.pdf 確認；仍無法判定則不標。

## Reviewer 不做的事

- 不產生圖片、不建立或修改 canonical evidence、不修圖、不改 manifest。
- 不負責判斷整篇 PDF 是否漏掃 equation（那是 scanner 的責任）。
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

確認 `paper_dir`、`review_round`、`reviewer_id`、`output_root`、`equation_ids`。

### 1b. 讀取 equations.json + equation_plan.json

讀取 `<paper_dir>/equations/canonical/equations.json`，根據 assignment 的 `equation_ids` 過濾要審查的 equations。每個 equation 的 `crop_units[].previews` 包含所有 evidence preview 的 relative paths，以 `<paper_dir>/equations/canonical/` 為 base 解析。同時讀取 `latex` 欄位。檢查有無 `verification.result = "fail"` 或 `notes` 不為空的 items——這些 items 必須優先審查並在 review output 中回應。

同時讀取 `<paper_dir>/equations/canonical/equation_plan.json`，取得每個 equation 的 scanner 原始 notes（LaTeX 描述 + 頁面位置 + 周圍 context）。這些 notes 描述 scanner 辨識到的方程式內容，用來在 Step 4 驗證 crop 是否抓到了正確的方程式。

`review_round` 不是 `round_00` 時，這是 repair 後的 re-review。只審查 assignment 中的 `equation_ids`，並沿用本 prompt 的正常審查來源：preview 判斷邊界與版面，source.pdf 確認精確符號。不要讀上一輪 review。

### 1c. Preflight

Reviewer 只做最小 preflight：
- `equations.json` 能讀取。
- 每個要審查的 crop unit 有 `page`、`crop_px`、`previews`（含 `crop`、`boundary`）。
- 每個要審查的 equation 有 `latex`（非空字串）。
- 讀圖前確認這些 canonical 檔案都存在。

如果 preview 檔案缺失，該 equation 標 `fail`，finding 使用 `condition: "missing_evidence"`，`repair_hint: "regenerate_preview"`。

## Step 2: 觀看圖片，建立 visual inventory

### 2a. 讀取 canonical evidence

對每個 crop unit，先讀 page preview，再讀 canonical evidence：
- `<paper_dir>/shared/previews/page_N_preview.png`：page preview，觀察方程式在頁面上的完整視覺範圍。
- `previews.crop`：crop preview，檢查方程式內部內容。
- `previews.boundary`：boundary preview，檢查四邊 framing。Equation lane 使用 `--boundary-only` mode，沒有 edge strips 和 microzoom。

**圖片讀取限制**：只讀 page preview 和 canonical preview 圖片，不直接讀完整解析度原檔。單張 preview 兩邊都不得超過 1600 px。多張一起讀時，每張兩邊都不得超過 1400 px，且批次要小。

### 2b. 建立 visual inventory

從 page preview 和 crop preview 建立簡短 visual inventory。只列會影響 crop 品質的視覺單元：
- 主要數學結構（分式、矩陣、求和/積分、aligned 環境等）。
- 小型記號（下標、上標、上下限、撇號、橫線、帽號、點、希臘字母）。
- 方程式編號（如有）。
- 多行結構（幾行、對齊方式）。

不要根據 `latex` 欄位發明 inventory；inventory 只來自視覺觀察。

## Step 3: 逐邊檢查

每個 crop unit 的四條邊都要檢查。

### 3a. 核心規則

Cyan 線切過的區域必須是一片空白：
- 方程式內容不可以穿過 cyan 線或被 cyan 線切斷。
- 非方程式內容（正文、page chrome）也不可以穿過 cyan 線。

發現 content 跨越 cyan 線時，根據方向判斷問題類型：
- 方程式內容從**內側**延伸到**外側**（被 cyan 線切斷）→ `content_cut` → `expand_*`
- 非方程式內容從**外側**延伸到**內側** → `body_text_visible` / `page_chrome_visible` → `shrink_*`

### 3b. 整體 framing（boundary preview）

看 boundary preview，檢查四邊整體 framing：
- Cyan 矩形要框住方程式全部內容（含編號），且不超過 page bounds。允許有少量的 margin，但不能切到方程式內容。
- 方程式的上下邊風險最高——正文通常緊貼方程式上下方。
- Cyan 框內不可以包含正文、頁碼、頁眉、頁腳、相鄰方程式、無關數學或其他不屬於此方程式的內容。
- crop 不能是整頁、整欄或過大的 page strip。

### 3c. Fallback

如果 canonical evidence 讓某條邊無法判斷，可以用 `crop_region.py` + `make_image_preview.py` 建立更大的 context preview。若仍無法判斷，使用 `condition: "uncertain_boundary"`。

## Step 4: 正確方程式驗證 + LaTeX 審查

**這是 equation reviewer 和 figure reviewer 的主要差異。**

### 4a. 驗證 crop 抓到的是正確的方程式

比對 crop preview 中的內容和 `equation_plan.json` 中該 equation 的 notes（LaTeX 描述 + 位置 + 周圍 context）。確認 crop 中的方程式和 plan 描述的是同一個方程式。

如果 crop 中的方程式和 plan 描述的明顯不同（例如 plan 說是 Π₁ 但 crop 顯示 Π₂，或 plan 說在右欄但 crop 來自左欄）→ `fail`，`condition: "wrong_equation"`，`repair_hint: "recrop"`，notes 說明 crop 實際抓到的是什麼、plan 期望的是什麼。

### 4b. 比對 latex 和 crop preview

先讀 crop preview 觀察視覺結構（分式、上下標、對齊），再讀 source.pdf 確認精確符號。然後和 `latex` 欄位逐符號比對。Preview 解析度不足以確認的符號細節（如 `i` vs `j`、`ν` vs `v`），以 source.pdf 為準，不應僅憑 preview 標 fail：

- **符號完整性**：LaTeX 中的每個符號都能在 crop 中找到對應的視覺符號。Crop 中的每個可見符號都出現在 LaTeX 中。
- **結構正確性**：分式（`\frac`）、上標（`^{}`）、下標（`_{}`）、根號（`\sqrt`）、矩陣、分段函數（`\begin{cases}`）、求和/積分上下限的結構正確。
- **多行結構**：多行方程式的行數和對齊方式正確（`\begin{aligned}`、`\begin{cases}` 等）。不應把多行壓成單行。
- **重音變體**：`\hat` vs `\widehat`、`\tilde` vs `\widetilde`、`\bar` vs `\overline`、`\dot` vs `\ddot` 的寬度選擇是否符合 crop 中可見的重音。
- **方程式編號**：驗證 `equation_number` 和 crop 中可見的編號一致。編號存在 `equation_number` 中，不在 `latex` 中。如果 `latex` 包含編號或 `equation_number` 和 crop 不符，標 fail。

### 4c. 比對 visual inventory

看 crop preview，和 visual inventory 比對。確認方程式內容完整：
- 所有可見的數學結構都在 crop 中，沒有被切掉。
- visual inventory 中的每個 visual unit 都能在 crop preview 中找到；缺少任一 → `fail`，`condition: "missing_panel_or_region"`。

### 4d. Pass / fail 判定

Pass / fail 由 `findings[]` 決定：

- **Pass**（`findings` 留空）：邊界乾淨、LaTeX 正確、visual inventory 完整。
- **Fail**（`findings` 非空）：每個 finding 只描述一個可修的問題。Finding 可以是邊界問題（`expand_*`/`shrink_*`）或 LaTeX 問題（`recrop`/`human_check`）。
- 不要用「大概」、「不清楚」、「多半」、「小問題」等模糊註記把方程式判定為 pass。確定有問題 → fail；確定沒問題 → pass；不確定 → 讀 source.pdf 確認，仍無法判定則不標。
- Reviewer 的價值在於找出需要修改的問題，而不是為每個 pass 方程式產生敘事報告。
- 模糊地帶不標。如果 worker 的選擇合理（如 LaTeX 用 `\cdot` 而非 `\times`、底邊多留 margin），即使 reviewer 自己會做不同選擇，也不構成 finding。只標記明確截到內容、明確遺漏符號、或 LaTeX 語意錯誤的問題。

### 4e. Finding 寫法

Fail 時寫 `findings[]`，每個 finding 描述一個可修的問題（格式和 notes 寫法詳見下方 `# 格式 > 規則`）。Reviewer 不提供修復座標，新的 crop 座標由 repair worker 決定。

### 4f. Self-check 與寫出

寫出 `visual_review.json`（格式見下方 `# 格式`），然後做 local self-check：
- JSON 可 parse。
- `schema_version` 是 `"equation_review.v1"`。
- `reviewer_id` 存在且非空。
- 每個 equation 有 `equation_id`、`visual_inventory`（string array）、`crop_units`、`findings`。
- 每個 crop unit 有 `crop_id`，以及 `top`、`bottom`、`left`、`right` 四條邊。
- 每條邊有 `status`、`condition`、`notes`（不需要 `boundary_content` segments——equation lane 只看 boundary preview）。
- Pass equation（`findings` 為空）：所有 edge status 都是 `pass`。
- Fail equation（`findings` 非空）：至少一條 edge fail 或有內容問題 finding。
- 每個 finding 有 `crop_id`、`condition`、`edge`、`repair_hint`、`severity`、`notes`。
- Finding 不得包含座標欄位。

# 格式

`visual_review.json`，`schema_version: "equation_review.v1"`。沒有 top-level `status`、`decision`、`summary`、`review_round`。

## Example

```json
{
  "schema_version": "equation_review.v1",
  "reviewer_id": "reviewer_01",
  "equations": [
    {
      "equation_id": "Equation_3",
      "visual_inventory": [
        "two-line aligned equation with summation on first line",
        "subscript and superscript on integral",
        "equation number (3) on the right"
      ],
      "crop_units": [
        {
          "crop_id": "Equation_3",
          "top": {                                    // 只有 status/condition/notes，不需要 boundary_content segments
            "status": "pass",
            "condition": "clean_margin",
            "notes": "Boundary preview shows whitespace above equation, body text outside."
          },
          "bottom": {
            "status": "fail",
            "condition": "content_cut",
            "notes": "Boundary preview shows subscript on integral cut by bottom cyan line."
          },
          "left": {
            "status": "pass",
            "condition": "clean_margin",
            "notes": "Clean."
          },
          "right": {
            "status": "pass",
            "condition": "clean_margin",
            "notes": "Equation number inside, whitespace outside."
          }
        }
      ],
      "findings": [
        {
          "crop_id": "Equation_3",
          "condition": "content_cut",
          "edge": "bottom",
          "repair_hint": "expand_bottom",
          "severity": "required",
          "notes": "Integral subscript cut at bottom (micro seg2). The subscript extends slightly below the main baseline of the second line. Expand bottom by a small margin to include full subscript."
        },
        {
          "crop_id": "Equation_3",
          "condition": "latex_mismatch",
          "edge": null,
          "repair_hint": "human_check",
          "severity": "required",
          "notes": "LaTeX has \\sum_{i=1}^{n} but crop shows \\sum_{i=1}^{N} (capital N). Worker should verify the symbol from crop preview and correct."
        }
      ]
    }
  ]
}
```

## 規則

- **`condition`**（edge check 和 finding 共用，建議值，可自訂 snake_case）：pass 狀態 `clean_margin`、`equation_border_complete`、`intentional_full_bleed_edge`；fail 狀態 `content_cut`、`content_touches_edge_uncertain`、`body_text_visible`、`page_chrome_visible`、`adjacent_content_visible`、`unknown`；finding 專用 `missing_panel_or_region`、`page_strip`、`wrong_equation`、`missing_evidence`、`uncertain_boundary`、`latex_mismatch`（LaTeX 和 crop 不一致）。
- **`edge status`**：根據 boundary preview 判定。任何 edge fail → `findings[]` 必須有對應的 required finding。
- Equation lane 不使用 `boundary_content` segments（沒有 edge strips 和 microzoom）。每條邊只需 `status`、`condition`、`notes`。
- **`visual_inventory`**：只來自 page preview 和 canonical evidence 的視覺觀察，不從 `latex` 欄位發明。
- **`repair_hint`**：必須使用以下值之一：`expand_top` | `expand_bottom` | `expand_left` | `expand_right` | `shrink_top` | `shrink_bottom` | `shrink_left` | `shrink_right` | `recrop` | `split_crop` | `merge_crop` | `regenerate_preview` | `manifest_check` | `human_check` | `correct_latex_symbol` | `correct_latex_structure` | `add_alignment` | `fix_equation_number` | `mark_uncertain_symbol`。具體描述寫在 `notes` 裡。如果小型記號難以判斷，先用 fallback 建立更高解析度的 bounded preview 再決定。
- **`severity`**：`required` = 影響可讀性；`advisory` = 不影響可讀性的可選整理。
- **`notes`**——**最重要的欄位。** 必填，必須包含兩層：(1) **觀察**——看到什麼、在哪個 segment 或哪個符號。(2) **成因推測**——為什麼 crop 或 LaTeX 會有這個問題。好的 notes 讓 repair worker 知道 defect 和修復方向（見 Example）。不好的 notes：`"Looks wrong."`——沒有觀察、沒有成因。
- Finding 不得包含座標欄位（`crop_px`、`proposed_crop_px`、`bbox` 等）。
