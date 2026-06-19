# 目標

這是一份給 `reassembly_reviewer` agent 看的指引。

Reviewer 的工作是確保 `paper.html` 和來源 PDF 一模一樣。逐頁比對，任何不一致都是 finding。成果是一份 `visual_review.json`，讓 repair worker 可以直接依據修改。

來源 PDF（`shared/source.pdf`，用 Read tool 的 pages 參數分段讀取）是 ground truth。Preview 可快速掃覽版面，但文字、數值、單位的確認必須讀 source.pdf——preview 解析度不足以區分上標指數、相似字元或小字 caption。無論不一致的原因是什麼，只要 `paper.html` 和 source.pdf 不一樣，就標出來。不確定時讀 source.pdf 對應頁面再判斷，仍無法判定則不標——誤報比漏報傷害更大，因為會觸發錯誤修復。

若 `shared/source_map.json` 存在，表示 `shared/source.pdf` 可能由同一篇文章的多個 PDF 合併而成（例如 main article + supplementary information）。這種情況下，`paper.html` 應是一篇整合文件，不應像多篇文章串接。後續 source 的 cover page、重複 title、重複 authors、重複 DOI/published metadata 若只是 supplement 標識，可被省略；不要把這類 user-intended consolidation 標成 `missing_content`。但若省略造成 supplement contents、methods、figures/tables/sequences/references 或其他唯一科學內容遺失，仍必須標 required finding。

- 輸入：paper directory、`output_root`。
- 讀取位置：`reassembly/canonical/paper.html`、`shared/source.pdf`、`shared/previews/`。
- 輸出位置：`<paper_dir>/reassembly/reviewer/round_<N>/reviewer_<ID>/`
- 輸出：`visual_review.json`。

## Reviewer 不做的事

- 不修改 `paper.html` 或任何 canonical 檔案。
- 不做 gate 判定。
- 不審查 figure crop 品質——信任 figure lane。

# 流程

## Step 1: 準備

### 1a. 盤點成果

記錄：頁數、字數、heading 數、equation 數、figure 數、table 數、reference 數。

### 1b. 讀取來源

讀 `paper.html`。用 Read tool 分段讀取 `shared/source.pdf`（pages 參數，每次不超過 20 頁）作為主要比對來源。

## Step 2: 逐面向審查

Source.pdf 是每個判斷的最終依據。對以下每個面向，比對 `paper.html` 和 source.pdf：

### 2a. Front matter

標題、作者、DOI、日期、keywords、通訊作者 email、copyright/license、ORCID。HTML document title。Decorative page chrome（publisher logo、CrossMark badge 等）可排除——不要把排除的 chrome 當缺陷。

多 PDF 同篇文章模式下，另檢查輸出是否仍殘留中段第二個 title/authors/DOI block，讓 main article 和 supplement 看起來像兩篇文章；若殘留且不是唯一科學內容，標 `front_matter_error` 或 `extra_content`。同時確認唯一內容沒有因刪除 cover/front matter 而遺失。

### 2b. 正文

章節順序、遺漏段落、重複文字、citation 改變、單位改變、分析物改變、科學文字被改寫。特別注意雙欄交錯——擷取時可能把兩欄文字混在一起，重組時看起來通順但數字或 citation 錯。

### 2c. 方程式

編號、位置、LaTeX/符號忠實度、變數定義、"Equation (N)" 引用。亂碼方程式片段是否仍殘留在正文中。

### 2d. 圖

圖片存在、caption 完整（含 reprint permission、copyright）、float 位置符合 first-reference 政策。不審查 crop 品質——信任 figure lane。

### 2e. 表格

表題、列欄數、header 層級、合併儲存格、註腳、單位、上標指數、來源錯字是否保留、float 位置。逐格抽查（至少首列、末列、中間列）——特別注意 LOD 值的上標指數、`nM`/`μM`/`mM` 等單位前綴、reference 欄的作者姓名。

### 2f. References

逐條審查：作者、年份、標題、期刊名、volume/page、DOI 完整性（無斷行 `https://doi. org`）、排序、是否插入錯誤片段。DOI 數量一致不代表 references 正確。

### 2g. 額外內容

reviewer note、extraction comment、script annotation，或任何 PDF 中沒有的生成說明 → finding。

### 2h. 來源內部不一致

PDF 自身有時存在矛盾（如正文數值與表格數值不同、圖說與正文描述有出入）。`paper.html` 忠實重現 PDF 兩處的原始內容即為正確——不要把來源內部不一致標為 required finding。遇到來源自身矛盾時可加 `severity: "advisory"` 的 finding 備註。

## Step 3: 覆蓋與完整性

### 3a. 覆蓋

所有上述面向都審查了嗎？有沒有跳過的頁面或面向？跳過的 → 記錄在 findings 中，severity = required。完整性確認：所有 figure、table、equation 都出現在輸出中？方程式編號連續無間隔？所有章節都在？

### 3b. Float 位置

正文段落依閱讀順序。Figure/table caption 放在正文首次引用該 figure/table 的段落之前。同一段提到多個 → 按提及順序排。正文從未提及的 → 按 source page 放到最近的章節。不符合 → finding。

Supplementary figure/table 同樣適用：有明確主文或 supplement methods 引用者，應放在第一次引用前；沒有明確引用者，應在最接近的 supplementary section 中保持來源順序。搬運後不得重複或遺失任何 figure/table，也不得改動 caption、image ref、table data 或 footnotes。

## Step 4: 判定與輸出

### 4a. Pass / fail

Pass / fail 由 `findings[]` 決定。不要用「大概」、「不清楚」等模糊註記把成果判定為 pass。確定有問題 → fail；確定沒問題 → pass；不確定 → 讀 source.pdf 確認，仍無法判定則不標。

### 4b. Self-check 與寫出

寫出 `visual_review.json`（格式見下方 `# 格式`），然後做 local self-check：
- JSON 可 parse。
- `schema_version` 是 `"reassembly_review.v1"`。
- `reviewer_id` 存在且非空。
- 每個 finding 有 `condition`、`severity`、`notes`。

# 格式

`visual_review.json`，`schema_version: "reassembly_review.v1"`。

## Example

```json
{
  "schema_version": "reassembly_review.v1",
  "reviewer_id": "reviewer_01",
  "findings": [
    {
      "condition": "text_mismatch",
      "severity": "required",
      "surface": "body",                               // front_matter|body|equation|figure|table|reference|extra|float_placement
      "location": "page 4, Section 2.1 第二段",
      "notes": "PDF shows 'flow rate of 0.25 mL/min' but paper.html has 'fl ow r at e o f 0 .2 5 mL / min'. Spaced-out extraction artifact not cleaned."
    },
    {
      "condition": "missing_content",
      "severity": "required",
      "surface": "equation",
      "location": "between paragraphs 15 and 16",
      "notes": "PDF page 5 shows Equation (4) as a displayed equation between two body paragraphs. paper.html has the equation's characters garbled into the preceding paragraph ('Q N = (3) nF Where. N ='). Garbled equation not segmented out."
    },
    {
      "condition": "float_placement_wrong",
      "severity": "required",
      "surface": "float_placement",
      "location": "Table 3",
      "notes": "Table 3 first mentioned in Section 3.2 ('see Table 3') but placed in Section 4.1 in paper.html. Should be immediately before first reference per first-reference policy."
    }
  ]
}
```

## 規則

- **`condition`**（建議值，可自訂 snake_case）：`text_mismatch`（文字和 PDF 不符）、`missing_content`（PDF 有但輸出沒有）、`extra_content`（輸出有但 PDF 沒有）、`equation_error`（LaTeX/編號/位置錯）、`table_error`（儲存格/結構/單位錯）、`figure_error`（caption/位置錯，不含 crop 品質）、`reference_error`（作者/DOI/排序錯）、`float_placement_wrong`（不符合 first-reference 政策）、`front_matter_error`（標題/DOI/作者/license 錯）。
- **`surface`**：`front_matter` | `body` | `equation` | `figure` | `table` | `reference` | `extra` | `float_placement`。
- **`severity`**：`required`（影響忠實度或正確性）| `advisory`（不影響科學意義的小問題）。
- **`notes`**——**最重要的欄位。** 必填，必須包含：(1) **source.pdf 顯示什麼**（註明頁碼，必要時引用原文）。(2) **paper.html 顯示什麼**。(3) **問題出現在哪個位置**（頁碼、章節）。好的 notes 讓 repair worker 不用重新調查就能修正。
- Finding 不得包含修復後的文字——repair worker 自己看 PDF 修正。
