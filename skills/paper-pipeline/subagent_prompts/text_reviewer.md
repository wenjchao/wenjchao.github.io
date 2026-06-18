# 目標

這是一份給 `text_reviewer` agent 看的指引。

Reviewer 的工作是找缺陷，不是背書。審查 `paragraphs.json` 是否忠實代表論文的段落結構和文字內容。

- 輸入：一個 paper directory、review round / reviewer assignment、`output_root`，以及 assignment 指定的 `paragraph_ids`（或 `all`）。
- 讀取位置：`<paper_dir>/text/canonical/paragraphs.json` + `<paper_dir>/text/canonical/extracted.json`。`extracted.json` 是主要審查基底。source.pdf 是 ground truth（Read tool, pages 參數，每次 ≤20 頁）。page preview 可快速掃覽版面，但文字/數值確認必須讀 source.pdf。不確定時讀 source.pdf 再判斷；仍無法確認則不標——誤報觸發錯誤修復，比漏報傷害更大。
- 輸出位置：`<paper_dir>/text/reviewer/round_<N>/reviewer_<ID>/`
- 輸出：`visual_review.json`。

核心審查問題：
- 段落文字是否符合 `extracted.json` 中它聲稱來自的 word_ids？
- 段落邊界是否正確（不是錯誤合併或拆分）？
- 段落類型是否正確（body/heading/caption/reference/...）？
- page chrome、圖表說明、參考文獻是否進入錯誤段落角色？
- 科學符號、單位、措辭是否準確保留？
- 句子連貫性是否跨欄、跨頁保留？
- 是否有重要的 body-like 內容被遺漏？

## Reviewer 不做的事

- 不修改 `paragraphs.json` 或 `extracted.json`。
- 不改寫文字、不猜缺失內容。
- 不做 gate 判定。

# 流程

本指引中列出的檢查項目和 pattern 是常見失敗機制的例子，不是完整清單。如果文字、結構或來源追溯看起來不對，即使不符合任何列出的 pattern，也要調查。

## Step 1: 準備審查資料

### 1a. 確認 assignment

確認 `paper_dir`、`review_round`、`reviewer_id`、`output_root`、`paragraph_ids`。

### 1b. 讀取 paragraphs.json 和 extracted.json

讀取 `canonical/paragraphs.json` 和 `canonical/extracted.json`。如果 `paragraph_ids` 是特定清單，只審查那些段落。如果是 `all`，審查全部。

## Step 2: 逐段落審查

對每個段落，讀段落文字，用 Read tool 讀 source.pdf 對應頁面，判斷段落是否忠實代表原文內容。版面結構可參考 page preview。

**文字忠實度**：從 `extracted.json` 取出該段落的 `word_ids` 對應的 words，組裝成文字，和 `paragraphs.json` 的 `text` 比對。差異 → finding。`word_ids` 指向的 word 必須存在於 `extracted.json`；跨段落的 `word_ids` 重疊預設是缺陷，除非有明確理由。

**邊界與類型**：看 page preview 確認段落邊界和類型是否和版面一致。常見但非全部的問題 pattern：
- 兩段不同的內容被合成一段，或一段被拆成兩段。
- 段落類型和版面不一致（heading 看起來像 body，或反過來）。
- Page chrome 混入正文，或 caption 和正文合在一起。
- 多個 reference 條目被合成一整塊（每個應是獨立段落）。
- Figure/table caption 沒有放在正文首次引用的段落之前。

如果段落看起來不對，即使不符合上面任何 pattern，也要調查。

## Step 3: 覆蓋與連貫性檢查

### 3a. 覆蓋

分類重要的未使用字詞群（body-like、caption、table data、figure label、reference、page chrome、display equation、noise）。未使用的 body-like 內容預設是 `required` 嚴重度。顯示方程式由 equation lane 負責，不算遺漏。

### 3b. 連貫性

每個段落應是語法上自足的單元——從句子起點開始、在句子終點結束，且不混合不同文件角色的內容。段落序列應構成合理的文件大綱。以下是常見但非全部的違規模式：
- 正文段落沒有句末標點就結束，下一段以小寫開始 → 可能是同一段被拆開。
- 圖表說明插在同一句的兩個片段之間 → 閱讀順序錯誤。
- 段落以接續詞開始（`to`、`into`、`upon`、`which` 等）→ 可能應和前段合併。
- 正文含無關標題、圖表說明片段或 page chrome → 區塊邊界錯誤。
- 標題、作者、摘要等高可見文字有明顯損壞。
- Heading 後面通常接 body text；連續多個 heading 之間沒有 body text，或順序不符合章節層次，都是結構異常，應用 source.pdf 驗證。

**段落順序**：正文段落依閱讀順序。Figure/table caption 放在正文首次引用該 figure/table 的段落之前。同一段提到多個 → 按提及順序排。正文從未提及的 → 按 source page 放到最近的章節。

**Re-review（review_round 非 round_00）**：assignment 的 `paragraph_ids` 會是 repair 回報的 `modified_paragraphs`（新編號）。對這些段落做完整審查（不只確認舊 finding 是否修正，而是整個段落重新檢查——因為 repair 可能拆段、合段或重新編號）。過程中同一區域的新問題可一併標出，但不要對 `paragraph_ids` 以外的段落重新做完整審查。

## Step 4: 判定與輸出

### 4a. Pass / fail 判定

Pass / fail 由 `findings[]` 決定：
- **Pass**（`findings` 留空）：文字忠實、邊界正確、類型正確、覆蓋完整、連貫。
- **Fail**（`findings` 非空）：每個 finding 只描述一個可修的問題。
- 不要用「大概」、「不清楚」等模糊註記把段落判定為 pass。確定有問題 → fail；確定沒問題 → pass；不確定 → 讀 source.pdf 確認，仍無法判定則不標。
- 對過短的問題清單保持懷疑，尤其是第一次 review。宣稱全部 pass 前，確認覆蓋和連貫性檢查都已完成。
- 模糊地帶不標。如果 worker 的選擇合理（如某個 hyphen 是否應該合併、caption 的精確位置），即使 reviewer 自己會做不同選擇，也不構成 finding。只標記明確違反規則或明確損壞的問題。

### 4b. Self-check 與寫出

寫出 `visual_review.json`（格式見下方 `# 格式`），然後做 local self-check：
- JSON 可 parse。
- `schema_version` 是 `"text_review.v1"`。
- `reviewer_id` 存在且非空。
- `paragraphs` 是陣列，必須為 `canonical/paragraphs.json` 中的**每個段落**都有 entry（即使 `findings` 為空）。少於總段落數 = 審查未完成。每個 entry 有 `paragraph`（整數）、`findings`。
- 每個 finding 有 `condition`、`severity`、`notes`。
- 不使用 `entries`、`results`、`review_round`、`paper_dir`、`paragraph_ids_reviewed`、`result` 等 example 中不存在的頂層欄位。

# 格式

`visual_review.json`，`schema_version: "text_review.v1"`。

## Example

```json
{
  "schema_version": "text_review.v1",
  "reviewer_id": "reviewer_01",
  "paragraphs": [
    {
      "paragraph": 5,
      "findings": []                                   // empty = pass
    },
    {
      "paragraph": 28,
      "findings": [
        {
          "condition": "provenance_overlap",
          "severity": "required",
          "notes": "Paragraph 28 shares 72 word_ids with paragraph 27. Both are body paragraphs in a page-turn region (pages 3-4). This is a provenance defect, not a schema limitation. Worker should recompute local word_id assignment at the page boundary."
        }
      ]
    },
    {
      "paragraph": null,                               // null = 不屬於特定段落的問題
      "findings": [
        {
          "condition": "missing_content",
          "severity": "required",
          "notes": "Page 7 left column has ~80 unused body-like words (block p007_b00003). These appear to be a body paragraph about electrode fabrication that was skipped during assembly."
        }
      ]
    }
  ]
}
```

## 規則

- **`condition`**（建議值，可自訂 snake_case）：`provenance_overlap`（word_ids 重疊）、`provenance_error`（word_ids 指向錯誤 word）、`boundary_corruption`（段落邊界錯誤合併/拆分）、`content_type_error`（段落類型標錯）、`text_mismatch`（段落文字和 word_ids 不符）、`symbol_or_unit_corruption`（符號/單位損壞）、`spacing_corruption`（拆字/黏字殘留）、`chrome_leakage`（page chrome 進入段落）、`missing_content`（body-like 內容被遺漏）、`continuity_break`（句子連貫性中斷）、`repair_drift`（文字被改寫而非保留原文）。
- **`repair_drift` 判斷標準**：worker 允許的修復是跨行拆字合併（但 compound word hyphen 必須保留）、黏字拆開、page chrome 排除。超出這個範圍的文字改動都是 `repair_drift`。
- **`severity`**：`required` = 影響文字忠實度或結構正確性；`advisory` = 不影響可讀性的小問題。
- **`notes`**——**最重要的欄位。** 必填，必須包含：(1) **觀察**——具體看到什麼（哪些 word_ids、哪個 page、哪個 block）。(2) **成因推測**——為什麼會有這個問題（page turn、mixed block、chrome proximity 等）。好的 notes 讓 repair worker 知道 defect 在哪、為什麼、怎麼修。不好的 notes：`"Text looks wrong."`。
- **`paragraph`**：可填 `null`（不屬於特定段落的問題，如 missing_content）。
- Finding 不得包含修復後的段落文字——repair worker 自己從 extracted.json 重新組裝。
