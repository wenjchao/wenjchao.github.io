# 目標

這是一份給 equation_scanner agent 看的指引。

此流程使用場景與目標：
- 輸入：一個 paper directory（含 `shared/pages/`、`shared/previews/`）、pages 範圍。
- 輸出：`<output_root>/equation_plan.json`
- 目標：辨識 paper 中所有數學表達式（displayed equations 和 inline math），產出一份方程式清單給下游 worker agent 使用。最終目的是將 paper 組裝回 HTML/Markdown，因此所有數學內容都需要被標記。
- 邊界：此 agent 只負責辨識。不裁切方程式、不轉寫 LaTeX、不寫 equations.json。

# 流程

## Step 1: 確認前置條件

確認 `shared/pages/page_N.png` 和 `shared/previews/page_N_preview.png` 對所有 assignment 頁面都存在。若缺少，回報 blocked。

## Step 2: 掃描頁面並辨識顯示方程式

逐頁讀 page preview 辨識數學表達式的位置和範圍。同時用 Read tool 讀 `shared/source.pdf`（`pages` 參數，每次 ≤20 頁）確認方程式內容。Preview 決定空間位置，source.pdf 決定符號內容——兩者互補，衝突時符號信 source.pdf。

### 收錄範圍

收錄所有數學表達式，包括：
- 有編號的顯示方程式（"(1)"、"(2a)"、"Eq. 1" 等）。
- 未編號的顯示方程式（置中或獨立成行）。
- 命題、引理、推論和附錄證明中的方程式區塊。
- **正文中的 inline math**——僅限 plain text（含 Unicode 符號如 α、κ、₁）無法充分表達、需要 LaTeX 渲染的表達式（如含 `\frac`、`\sqrt`、`\sum`、`\int`、多層上下標）。Plain text 可表達的 inline math（如 `κ = L/A·R`、`V₁ - V₂`）不收錄。
- 證明段落中與正文交錯的半顯示（semi-displayed）公式。

不收錄：
- Plain text 可充分表達的 inline math。
- 單純的變數名稱或符號定義（如 "let x denote..."）。
- 化學結構圖、圖面板中的數學。

### equation_type 分類

- `displayed`：置中或獨立成行的方程式（有無編號皆可）。
- `inline`：嵌在正文段落中的數學表達式。

### 拆分粒度

每個獨立的數學表達式都是一個獨立的 equation entry。不要把多個表達式合併成一個 entry。

- 一段推導中如果有多個獨立的等式/不等式，每個都是獨立的 equation。例如：一段 proof 先寫 `Π₁(r^L, r^H) = f(1-f)(1-α)(V₁+r^L) - c(r^L)²`，再展開成 `= f(1-f)(1-α)(V₁ + f(1-f)(1-α)/2c) - c(f(1-f)(1-α)/2c)²`，這是**兩個** equation（初始定義和展開式），不是一個。
- 多行方程式（aligned、cases、matrix 等）如果是同一個表達式的多行排版，作為**單一** equation 記錄。
- 跨頁方程式記錄到同一個 equation 的多個 crop_units 裡。
- 判斷標準：如果兩行數學之間有正文（"that is:"、"Deviating would give:"等），它們是不同的 equation。如果兩行數學之間只有對齊符號（`=`、`&=`），它們是同一個 equation 的多行排版。

### 掃描要求

- 掃描所有頁面，包括附錄、補充證明和文末材料。不要假設方程式只出現在正文。
- 一次掃完所有頁面，不得 defer 到「後續 pass」。
- 看到疑似數學表達式但不列入的項目，記錄到 `excluded`。
- 如果 assignment 指定 `scope: numbered_only`，只辨識有明確可見編號的方程式。其他方程式可在 `notes` 提到，但不列入 `equations`。
- 如果 assignment 指定 `scope: displayed_only`，只辨識顯示方程式，排除 inline math。

### Notes 撰寫要求

每個 equation 的 `notes` 是**必填**欄位，用來幫助下游 worker 辨識這個方程式。`notes` 必須包含：

1. **完整 LaTeX 轉寫**：結合 page preview（視覺結構）和 source.pdf（精確符號）轉寫 LaTeX。多行方程式保留結構（`\begin{aligned}` 等）。這是 scanner 對方程式內容的最佳辨識，幫助 worker 在頁面上找到正確的方程式。
2. **位置描述**：方程式在頁面上的位置（如「左欄中段」、「右欄底部」、「跨雙欄置中」）。
3. **周圍 context**：方程式上下文的簡短描述（如「在 Proposition 2 的證明中」、「緊接在 'The expected payoff is' 之後」）。

Scanner 的 crop_px 是從低解析度 preview 估算的，可能不準確。Notes 中的 LaTeX 和位置描述是 worker 定位方程式的重要依據——當 crop_px 偏離時，worker 靠 notes 在頁面上找到正確的方程式。

## Step 3: 寫出 equation_plan.json 並自檢

寫出 `equation_plan.json`（格式見下方 `# 格式`），然後做 local self-check：
- JSON 可 parse。
- `schema_version` 是 `"equation_plan.v1"`。
- `equations` 是陣列。
- 每個 equation 有 `equation_id`（唯一、filename-safe）、`equation_number`（非空）、`equation_type`（`displayed`/`inline`）、`crop_units`（非空陣列）、`notes`（非空字串）。
- 每個 crop unit 有 `page`（整數）和 `crop_px`（`[x1, y1, x2, y2]`，四個整數，`0 ≤ x1 < x2`，`0 ≤ y1 < y2`）。
- `excluded` 是陣列（可為空）。

## Step 4: 完整性自檢

寫完 plan 後，逐頁重新讀 page preview，比對已記錄的 equations 是否覆蓋了該頁所有數學內容。

對每一頁：
1. 重讀該頁 preview。
2. 檢查頁面上的每個數學表達式是否已出現在 plan 中（透過 page number + notes 中的 LaTeX 比對）。
3. 特別注意頁面底部、欄位底部、proof 段落末尾——這些位置最容易遺漏。
4. 發現遺漏 → 補入 plan，更新 equation_id 編號。

完整性自檢後再寫出最終版 `equation_plan.json`。

# 格式

`equation_plan.json`，`schema_version: "equation_plan.v1"`。

## Example

```json
{
  "schema_version": "equation_plan.v1",
  "equations": [
    {
      "equation_id": "Equation_1",                     // filename-safe，不含空格，連續編號
      "equation_number": "(1)",                        // 照 paper 原文的編號；未編號用 unnumbered_p<page>_<seq>
      "equation_type": "displayed",                    // displayed|inline
      "crop_units": [
        {"page": 3, "crop_px": [100, 1200, 2400, 1350]}
      ],
      "notes": "LaTeX: `E = \\frac{1}{2} m v^2`. 左欄中段，在 'The kinetic energy is given by' 之後。"
    },
    {
      "equation_id": "Equation_2",
      "equation_number": "unnumbered_p5_1",            // 未編號方程式的合成編號
      "equation_type": "displayed",                    // 未編號但仍是 displayed
      "crop_units": [
        {"page": 5, "crop_px": [200, 800, 2300, 1050]}
      ],
      "notes": "LaTeX: `\\Pi_1 = (1-\\alpha)(V_1 - V_2)`, `\\Pi_2 = 0`. 兩行顯示方程式，右欄上方，Proposition 1 證明的第一步。"
    },
    {
      "equation_id": "Equation_3",
      "equation_number": "unnumbered_p7_1",
      "equation_type": "inline",                       // 嵌在正文中的數學表達式
      "crop_units": [
        {"page": 7, "crop_px": [60, 1500, 1140, 1580]}
      ],
      "notes": "LaTeX: `\\Pi_1 = (1-\\alpha)(V_1 - V_2)`. 左欄中段，嵌在 'The expected value capture is' 句子中。"
    }
  ],
  "excluded": [],                                      // 不列入 equations 的項目，陣列必須存在
  "notes": []                                       // 全局 notes（非 equation-level）
}
```

## 規則

- **`equation_id`**：連續編號（`Equation_1`、`Equation_2`、...），不管是否有原文編號。
- **`equation_number`**：有編號的方程式照 paper 原文（`"(1)"`、`"(2a)"`）。未編號的方程式（displayed 或 inline）使用合成編號 `unnumbered_p<page>_<seq>`（例如 `unnumbered_p7_1`）。
- **`equation_type`**：`displayed`（置中或獨立成行）或 `inline`（嵌在正文段落中）。
- **`crop_units`**：每個 entry 有 `page`（int）和 `crop_px`（`[x1, y1, x2, y2]`，完整解析度頁面圖片 pixel 座標，從 page preview 用 scale factor 換算）。單頁方程式一個 entry；跨頁方程式多個 entry。多行方程式作為單一區塊，不拆開。
- **`crop_px`**：**寧可大不要小**——涵蓋方程式可能佔據的最大範圍（含編號）。Worker 會用 boundary preview 收緊，hint 太小則 worker 要多輪擴展。排除周圍正文和明顯的 page chrome（頁眉、頁碼）。注意：從 preview 換算的座標可能不精確，這是預期行為——worker 會結合 `notes` 中的 LaTeX 和位置描述來定位。
- **`notes`**：**必填**。包含完整 LaTeX 轉寫、頁面位置描述、周圍 context（詳見 Step 2 的 Notes 撰寫要求）。
- **`excluded`**：不列入 equations 的項目。每項：`label`（nullable）、`page`、`reason`、`notes`。`reason` 建議值：`outside_assignment`、`variable_name_only`、`chemical_structure`、`math_in_figure`、`not_an_equation`。
