# 目標

這是一份給 `equation_reviewer` agent 看的指引。

Reviewer 讀取 extractor 建好的 canonical evidence，判斷每個方程式的 crop 和 LaTeX 能不能用。能用就標 `pass`；不能用就標 `fail` 並寫出可執行的 finding。

Reviewer 同時檢查兩件事：
1. **Crop 邊界**：方程式是否完整、邊緣是否乾淨（和 figure review 相同邏輯）。
2. **LaTeX 準確度**：LaTeX 是否準確反映 crop 中可見的數學結構（equation 獨有）。

- 輸入：review_packet（列出要審查的 equations 和 evidence 路徑）、canonical evidence 圖片。
- 輸出：`equation_visual_review.json`（per-equation pass/fail、edge_checks、LaTeX checks、findings）。
- 輸出位置：`<paper_dir>/equations/reviewers/round_<N>/reviewer_<ID>/`

Reviewer 不修改 crop、不修改 LaTeX、不修改 canonical。只要不確定，就標 `fail`。

# 流程

## Step 1: 準備審查資料



a) 確認 assignment：`paper_dir`、`review_round`、`reviewer_id`、`canonical_artifact_root`、`output_root`、review_packet 路徑。

b) 讀取 review_packet。每個方程式有 `crop_preview`、`boundary_preview`、`top_band`、`left_band`、`right_band`、`bottom_band`、`bottom_micro`、`rendered_latex_preview`、`latex` 等欄位。

c) Preflight：確認每個方程式的 evidence 檔案都存在。缺失 → `fail`，finding 用 `problem: "missing_evidence"`。

## Step 2: 觀看 evidence

**[judgment]**

a) **[judgment]** 對每個方程式，讀取 canonical evidence：
   - **Crop preview**：方程式內部細節（符號、上下標、對齊、編號）。
   - **Boundary preview**：整體 framing — cyan 矩形是否切到方程式或混入正文。
   - **Edge strips / bottom band / bottom micro**：逐邊精確檢查。
   - **Rendered LaTeX preview**：LaTeX 渲染後的視覺結果。
   - **LaTeX 字串**：`equations.json` 中的 `latex` 欄位。

b) **[judgment]** 建立簡短 visual inventory：方程式包含哪些視覺元素（分式、矩陣、求和、積分、上下標、希臘字母、對齊結構、編號）。

## Step 3: 逐邊檢查（crop 邊界）

**[judgment]** 和 figure reviewer 相同的 cyan 線規則。

### 核心規則

Cyan 線切過的區域必須是一片空白：
- 方程式內容不可以穿過 cyan 線或被 cyan 線切斷。
- 周圍正文、頁面固定元素不可以穿過 cyan 線。

### 整體 framing（boundary preview）

a) **[judgment]** 看 boundary preview 確認 cyan 矩形框住完整方程式（含編號），不混入正文或 page chrome。

### Top / left / right（edge strip）

b) **[judgment]** 逐一看 top、left、right 的 edge strip，記錄 `boundary_content`（`seg1` key，`last_inside` + `first_outside`）。

### Bottom（bottom band + microzoom）

c) **[judgment]** 逐一看底邊 microzoom segments，記錄 `boundary_content`（`micro_seg1` key）。不確定時對照 bottom band。

### 記錄格式

每條邊必須記錄 `boundary_content`、`status`（pass/fail）、`condition`、`notes`。

## Step 4: LaTeX 檢查

**[judgment]** Equation 獨有的檢查。

a) **[judgment]** 讀取 rendered LaTeX preview，和 crop preview 並排比對：
   - LaTeX 是否完整反映 crop 中可見的數學結構？
   - 分式、上下標、根號、矩陣、分段函數、求和/積分上下限是否正確？
   - 希臘字母、運算子、重音（hat/tilde/bar/dot）是否正確？
   - 多行對齊是否保留？
   - 方程式編號是否在 metadata 中正確記錄（不在 latex 欄位內）？

b) **[judgment]** 如果 rendered LaTeX preview 是 text fallback（沒有 pdflatex），記錄限制但不只因為 renderer fallback 就判定 fail。仍需目視比對 LaTeX 字串和 crop。

## Step 5: 判定

**[judgment]**

a) **[judgment]** 方程式只有在下列全部成立時才 `pass`：
   - 方程式編號正確。
   - crop 包含完整方程式和編號。
   - 周圍正文、page chrome 排除。
   - 四邊 edge_checks 全部 pass。
   - LaTeX 符合可見數學結構。
   - 小型記號完整（下標、上標、撇號、橫線、帽號、點、希臘字母）。
   - 多行對齊和括號結構已保留。
   - 沒有未解決不確定性。

   不確定就是 `fail`。不要用「大概」、「不清楚」、「多半」把方程式判定為 pass。

b) **[judgment]** `fail` 時寫 `findings[]`。每個 finding 記錄：
   - `equation_id`。
   - `problem`：crop 問題用 `content_cut`、`external_content_visible` 等（同 figure）。LaTeX 問題用 `latex_symbol_error`、`latex_structure_error`、`latex_alignment_missing`、`equation_number_error`。
   - `edge`（crop 問題）或 `null`（LaTeX 問題）。
   - `repair_hint`：crop 方向用 `expand_*`/`shrink_*`/`recrop`。LaTeX 修正用 `correct_latex_symbol`、`correct_latex_structure`、`add_alignment`、`fix_equation_number`、`mark_uncertain_symbol`。
   - `notes`：具體說明看到什麼。

c) **[judgment]** Reviewer 不提供修復座標，也不提供修正後的 LaTeX。

d) Self-check：JSON 可 parse、summary counts 正確、每個方程式有 edge_checks（top/bottom/left/right）和 LaTeX check、pass 方程式沒有 failed edge 或 LaTeX error、fail 方程式至少一個 finding。

## Step 6: 輸出



a) 寫 `equation_visual_review.json`（`schema_version: "equation_review.v1"`）。

b) 跑 self-check（同 Step 5d）。若 fail 修正後重寫。

### equation_visual_review.json

#### Enums

- `decision`：`pass` | `fail`
- `status`：`pass`（全部通過）| `fail`（任一 fail）
- `condition`（建議值，可自訂 snake_case）：
  - `clean_margin`：crop edge 在方程式內容之外，邊緣乾淨
  - `figure_border_complete`：crop edge 貼齊方程式邊框
  - `intentional_full_bleed_edge`：方程式本來就貼到頁面邊，且沒有內容被切掉
  - `content_cut`：方程式內容被切掉
  - `caption_visible`：正文出現在 crop 內
  - `body_text_visible`：正文出現在 crop 內
  - `page_chrome_visible`：頁碼、頁眉等出現在 crop 內
  - `unknown`：evidence 不足
- `problem`（建議值，可自訂 snake_case）：
  - Crop 問題：
    - `content_cut`：方程式內容被某條邊切掉
    - `external_content_visible`：正文或其他非方程式內容被裁進 crop
    - `page_chrome_visible`：頁碼、頁眉等被裁進 crop
    - `missing_evidence`：必要 preview 缺失
    - `uncertain_boundary`：evidence 不足以做出 pass 判斷
  - LaTeX 問題：
    - `latex_symbol_error`：LaTeX 中某個符號不正確（例如 `\hat` 應為 `\widehat`）
    - `latex_structure_error`：LaTeX 結構不正確（例如 aligned 環境遺漏）
    - `latex_alignment_missing`：多行方程式的對齊未保留
    - `equation_number_error`：方程式編號記錄錯誤
- `repair_hint`：
  - Crop 方向：`expand_top` | `expand_bottom` | `expand_left` | `expand_right` | `shrink_top` | `shrink_bottom` | `shrink_left` | `shrink_right` | `recrop`
  - LaTeX 修正：
    - `correct_latex_symbol`：修正特定符號
    - `correct_latex_structure`：修正結構（分式、矩陣等）
    - `add_alignment`：加入多行對齊
    - `fix_equation_number`：修正方程式編號
    - `mark_uncertain_symbol`：標記無法確定的符號
- `severity`：`required`（影響正確性）| `advisory`（不影響正確性的可選整理）

#### Fields

- `review_round`、`reviewer_id`
- `status`：`fail` if any equation fails
- `equations[]`：
  - `equation_id`、`equation_number`、`decision`
  - `reviewed_crop_units[]`：`crop_id`、`crop_preview`、`boundary_preview`、`top_band`、`left_band`、`right_band`、`bottom_band`、`bottom_micro`、`rendered_latex_preview`
  - `visual_inventory`：`source_units`（string array）、`missing_from_crop`（string array，pass 必須空）
  - `edge_checks.crop_units[]`：
    - `crop_id`
    - `edges.{top,bottom,left,right}`：
      - `boundary_content`：structured observation。Bottom 用 `micro_seg1` 等做 key；top/left/right 用 `seg1`。每個 key 有 `last_inside` 和 `first_outside`。
      - `status`：`pass` | `fail`
      - `condition`
      - `notes`：必填
  - `latex_check`：
    - `latex_matches_crop`：`pass` | `fail`
    - `rendered_preview_compared`：bool
    - `notes`：說明 LaTeX 和 crop 的比對結果
  - `findings[]`（pass 必須空，fail 至少一個）：
    - `finding_id`：unique within report（`Equation_1_f001`）
    - `equation_id`
    - `problem`、`edge`（crop 問題）或 `null`（LaTeX 問題）、`repair_hint`、`severity`
    - `notes`：必填，具體說明
- `summary`：`equation_count`、`pass_count`、`fail_count`、`finding_count`

### equation_visual_review.json example

```json
{
  "schema_version": "equation_review.v1",
  "review_round": "round_00",
  "reviewer_id": "reviewer_01",
  "status": "fail",
  "equations": [
    {
      "equation_id": "Equation_1",
      "equation_number": "(1)",
      "decision": "pass",
      "reviewed_crop_units": [
        {
          "crop_id": "Equation_1",
          "crop_preview": "previews/Equation_1_preview.png",
          "boundary_preview": "previews/Equation_1_boundary_preview.png",
          "top_band": ["previews/Equation_1_top_seg1_preview.png"],
          "left_band": ["previews/Equation_1_left_seg1_preview.png"],
          "right_band": ["previews/Equation_1_right_seg1_preview.png"],
          "bottom_band": ["previews/Equation_1_bottom_seg1_preview.png"],
          "bottom_micro": ["previews/Equation_1_micro_bottom_seg1_preview.png"],
          "rendered_latex_preview": "rendered_latex/Equation_1_preview.png"
        }
      ],
      "visual_inventory": {
        "source_units": ["fraction", "subscript i", "summation with limits"],
        "missing_from_crop": []
      },
      "edge_checks": {
        "crop_units": [
          {
            "crop_id": "Equation_1",
            "edges": {
              "top": {
                "boundary_content": { "seg1": { "last_inside": "top of fraction bar", "first_outside": "whitespace then prose" } },
                "status": "pass", "condition": "clean_margin", "notes": "Clean whitespace above."
              },
              "bottom": {
                "boundary_content": { "micro_seg1": { "last_inside": "subscript i baseline", "first_outside": "whitespace then prose" } },
                "status": "pass", "condition": "clean_margin", "notes": "Subscript fully inside."
              },
              "left": {
                "boundary_content": { "seg1": { "last_inside": "equation content", "first_outside": "whitespace" } },
                "status": "pass", "condition": "clean_margin", "notes": "Clean."
              },
              "right": {
                "boundary_content": { "seg1": { "last_inside": "equation number (1)", "first_outside": "whitespace" } },
                "status": "pass", "condition": "clean_margin", "notes": "Number included."
              }
            }
          }
        ]
      },
      "latex_check": {
        "latex_matches_crop": "pass",
        "rendered_preview_compared": true,
        "notes": "LaTeX accurately reflects visible math."
      },
      "findings": []
    },
    {
      "equation_id": "Equation_3",
      "equation_number": "(3)",
      "decision": "fail",
      "reviewed_crop_units": [
        {
          "crop_id": "Equation_3",
          "crop_preview": "previews/Equation_3_preview.png",
          "boundary_preview": "previews/Equation_3_boundary_preview.png",
          "bottom_band": ["previews/Equation_3_bottom_seg1_preview.png"],
          "bottom_micro": ["previews/Equation_3_micro_bottom_seg1_preview.png"],
          "rendered_latex_preview": "rendered_latex/Equation_3_preview.png"
        }
      ],
      "visual_inventory": {
        "source_units": ["widehat accent over XY", "summation"],
        "missing_from_crop": []
      },
      "edge_checks": {
        "crop_units": [
          {
            "crop_id": "Equation_3",
            "edges": {
              "top": { "boundary_content": { "seg1": { "last_inside": "widehat top", "first_outside": "whitespace" } }, "status": "pass", "condition": "clean_margin", "notes": "Clean." },
              "bottom": { "boundary_content": { "micro_seg1": { "last_inside": "subscript", "first_outside": "whitespace" } }, "status": "pass", "condition": "clean_margin", "notes": "Clean." },
              "left": { "boundary_content": { "seg1": { "last_inside": "equation content", "first_outside": "whitespace" } }, "status": "pass", "condition": "clean_margin", "notes": "Clean." },
              "right": { "boundary_content": { "seg1": { "last_inside": "number (3)", "first_outside": "whitespace" } }, "status": "pass", "condition": "clean_margin", "notes": "Clean." }
            }
          }
        ]
      },
      "latex_check": {
        "latex_matches_crop": "fail",
        "rendered_preview_compared": true,
        "notes": "Source shows \\widehat{XY} but LaTeX has \\hat{XY}. Accent spans two characters."
      },
      "findings": [
        {
          "finding_id": "Equation_3_f001",
          "equation_id": "Equation_3",
          "problem": "latex_symbol_error",
          "edge": null,
          "repair_hint": "correct_latex_symbol",
          "severity": "required",
          "notes": "Source shows \\widehat{XY} but LaTeX has \\hat{XY}. The accent spans two characters in the source."
        }
      ]
    }
  ],
  "summary": {
    "equation_count": 2,
    "pass_count": 1,
    "fail_count": 1,
    "finding_count": 1
  }
}
```

# 規則

## 權責

- Reviewer 只做視覺判斷和 LaTeX 比對，產出 `equation_visual_review.json`。
- 不修改 crop、LaTeX、canonical evidence 或 manifest。
- 不做 gate 判定。

## 圖片與讀取限制

- 只讀 canonical preview 圖片，不直接讀完整解析度原檔。
- 單張 preview 兩邊不超過 1600 px；多張不超過 1400 px。
- 缺失 → `fail` + finding，`problem: "missing_evidence"`。
- 如果小型記號（下標、上標、重音、根號尾端）或 crop 邊界在既有 evidence 中難以判斷，可使用 `agents/scripts/crop_region.py` + `agents/scripts/make_image_preview.py` 建立更高解析度但仍受限尺寸的目標 edge preview，再做決定。這是唯一允許 reviewer 建立新 evidence 的情況。

## Pass/fail 語意

- `pass`：crop 邊界乾淨且 LaTeX 準確。
- `fail`：crop 需要修、LaTeX 需要修、evidence 缺失、或無法確定。
- 不確定就是 `fail`。

## Finding 寫法

好的 finding：
```json
{
  "problem": "latex_symbol_error",
  "edge": null,
  "repair_hint": "correct_latex_symbol",
  "notes": "Source shows \\widehat{XY} but LaTeX has \\hat{XY}. The accent spans two characters in the source."
}
```

不好（太模糊）：`"notes": "LaTeX looks off"`

不好（提供修正 LaTeX）：`"corrected_latex": "\\widehat{XY}"`
