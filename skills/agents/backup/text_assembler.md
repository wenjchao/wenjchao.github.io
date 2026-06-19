# 目標

這是一份給 text_assembler agent 看的指引。

此 agent 做一件事：從 `extracted.json` 的字詞層級資料組裝最終段落序列。模型決定段落邊界、類型和順序。

這個 agent 同時用於兩種場景：
- **Initial assembly**：從 extractor 的 `extracted.json` 組裝全部段落。
- **Repair**：reviewer 發現問題，assembler 以 review findings 為指引重新組裝完整段落序列。

- 輸入：paper directory、`mode`（initial 或 repair）、`output_root`。Initial 讀 `canonical/extracted.json`，repair 額外讀 `canonical/paragraphs.json` + `canonical/visual_review.json`。
- 輸出：`paragraphs.json`。不論 initial 或 repair mode，輸出都是完整的段落序列，包含所有段落。

## Assembler 不做的事

- 不修改 `extracted.json`。
- 不發明缺失文字、不猜截斷的引用或符號。
- 不為了流暢改寫措辭、不現代化表述、不靜默改變科學意義。

# 流程

本指引中列出的檢查項目和 pattern 是常見失敗機制的例子，不是完整清單。如果結構、文字或來源追溯看起來不對，即使不符合任何列出的 pattern，也要調查。

## Step 1: 讀取輸入

根據 assignment 的 `mode` 決定輸入來源。所有檔案從 `<paper_dir>/text/canonical/` 讀取。

**`mode: initial`**：讀 `canonical/extracted.json`。掃描 `qc_notes` 和 `artifact_regions` 識別可疑區域。

**`mode: repair`**：讀 `canonical/paragraphs.json` 取得目前段落 + `canonical/visual_review.json` 取得 findings。`paragraph_ids` 標示哪些段落有問題，finding 的 `notes` 包含具體的修復指引。以這些 findings 為指引重新組裝，確保段落邊界、順序和 word_ids 全局一致。

## Step 2: 逐頁組裝段落

依頁面或短頁面範圍局部工作。對每個區域：

### 2a. 建立版面結構

從 word 座標建立版面理解，page preview 是驗證來源：

1. **分行**：判斷哪些 words 屬同一行。上標、下標也屬同一行，不因 y 偏移分開。
2. **偵測欄位**：判斷是單欄還是多欄版面。
3. **決定 reading order**：決定欄位內和欄位間的閱讀順序。
4. **讀 page preview** 建立版面理解。Page preview 是版面判斷的主要依據——欄位結構、段落分隔、圖表位置都在圖上一目了然。座標是輔助證據，不是主要來源。
5. **跨欄元素**：圖、表格、caption 可能橫跨 gutter 佔據兩欄。用 page preview 辨識這些元素後，將它們作為整體處理，不要按欄拆開。

### 2b. 偵測段落邊界

在每欄內，用以下信號偵測段落起點：

- **Indentation**：行首 word 的 x 座標明顯偏離該欄慣常的左邊界 → 新段落。
- **Font 變化**：`font_name` 或 `font_size` 改變 → 可能是新段落。此規則適用於所有段落類型之間的轉換，包括 heading 與 heading 之間。同一段落內的 words 應有一致的視覺格式。
- **Vertical gap**：連續行的 y 間距顯著大於正常行距 → 可能是段落分隔。
- **內容信號**：重複出現的格式化模式（如編號項目 `"1."`），每個實例通常是獨立段落。每個 reference 條目是獨立段落，不要合成一整塊。

在決定如何分段時，看 page preview——行距間隙和縮排在圖上一目了然。

### 2c. 偵測跨頁接續

兩個相鄰欄或頁的段落可能是同一段。判斷標準：

- 前段結尾**沒有句末標點**（`.?!)"` 以外的字元結尾）→ 高度可能接續。
- 下一欄/頁開頭的行**沒有 indentation 且以小寫開頭** → 幾乎確定是接續。
- 若不確定，讀 page preview 確認。

跨頁段落的 `pages` 列出所有出現頁面，`word_ids` 包含所有頁面的 word。

### 2d. 決定段落

對每個段落決定：
- 段落邊界（哪些 words 屬於同一段）。
- 段落類型（`title`、`authors`、`affiliation`、`abstract`、`heading`、`body`、`caption`、`reference`、`other`）。
- 段落順序（依 reading order）。Figure/table caption 放在正文首次引用該 figure/table 的段落之前。同一段提到多個 → 按提及順序排。正文從未提及的 → 按 source page 放到最近的章節。
- 忠實的段落文字（從 `words` 組裝，修復拆字和黏字，但不改寫內容）。跨行拆字可以合併，但 compound word 的 hyphen 必須保留。不確定時保留 hyphen。
- 來源追溯（`word_ids`）。

每個段落在產出前，必須親自讀過 page preview 確認邊界和文字正確。

### 2e. 風險區域

以下情況必須看 page preview 再決定，不能只靠座標：
- 圖、表格或圖表說明附近的段落（figure label 和 caption 文字容易混在一起）。
- 文末區域（致謝、參考文獻、出版資訊常擠在一起，需視覺確認邊界）。
- 符號恢復在科學意義上不清楚。
- 多欄轉換處（不同欄的 heading、body、caption 可能被混合排序）。

## Step 3: 完整性與連貫性檢查

組裝完成後，檢查段落序列：

**覆蓋檢查**：分類重要的未使用字詞群（body-like、caption、table data、figure label、reference、page chrome、extraction noise）。未使用的 body-like 內容必須解決或記錄為不確定性。

**連貫性檢查**：每個段落應是語法上自足的單元——從句子起點開始、在句子終點結束，且不混合不同文件角色的內容。以下是常見但非全部的違規模式：
- 正文段落沒有句末標點就結束，下一個正文段落以小寫開始 → 可能是同一段被拆開。
- 圖表說明插在同一句的兩個片段之間 → 閱讀順序錯誤。
- 段落以接續詞開始（`to`、`into`、`upon`、`which` 等）→ 可能和前一段應該合併。
- 正文段落包含無關標題、圖表說明片段或 page chrome → 邊界錯誤。
- Heading 後面通常接 body text；連續多個 heading 之間沒有 body text，或順序不符合章節層次 → 結構異常，用 page preview 驗證。
- 標題、作者、摘要等高可見文字有明顯損壞 → 優先修復。

**修復邊界**：修復損壞（恢復字詞邊界、段落邊界、正確類型標記），但不改寫內容。無法有把握重建的部分，保留最合理的讀法，在 `notes` 記錄。

## Step 4: 寫出 paragraphs.json 並自檢

寫出 `paragraphs.json`（格式見下方 `# 格式`），然後做 local self-check：
- JSON 可 parse。
- `paragraphs` 是陣列，`paragraph` 連續編號。
- 每個 paragraph 有 `paragraph`（整數）、`pages`（整數陣列）、`type`（enum）、`text`（非空）、`word_ids`（非空，指向 `extracted.json` 中真實 word）。
- `word_ids` 沒有跨段落重複（除非在 `notes` 明確說明理由）。
- Page chrome 不在段落文字中。
- 預設範圍的 caption 有出現。
- 異常長的 body 段落可能是多段被錯誤合併，應用 page preview 確認段落邊界。

Verification 語意：不確定某段的邊界或文字 → 在 `notes` 記錄，不要猜。即使有 notes 也要寫出段落——reviewer 會決定是否需要 repair。

# 格式

`paragraphs.json`。

## Example

```json
{
  "schema_version": "paragraphs.v1",
  "worker_id": "worker_01",
  "paragraphs": [
    {
      "paragraph": 1,
      "pages": [1],
      "type": "title",
      "text": "Electrochemical sensors: Types, applications, and the novel impacts...",
      "word_ids": ["p001_w000001", "p001_w000002"],
      "notes": []
    },
    {
      "paragraph": 5,
      "pages": [1, 2],
      "type": "body",
      "text": "The development of electrochemical sensors has seen significant growth...",
      "word_ids": ["p001_w000145", "p002_w000001"],
      "notes": ["Cross-page continuation verified against page previews"]
    }
  ]
}
```

## 規則

- **`word_ids`**：真正的來源追溯，不是裝飾。段落成果必須能從 `word_ids` 回溯到 `extracted.json` 中的字詞，重建頁面座標。
- **`type`**：`title`、`authors`、`affiliation`、`abstract`、`heading`、`body`、`caption`、`reference`、`other`。
- **`text`**：從 `extracted.json` 的 `words` 忠實組裝。完整保留原文（含錯字）。允許的修復：跨行拆字合併（見 Step 2d）、黏字拆開、page chrome 排除。
- **預設範圍**：包含文章文字、圖說、表格說明。排除表格儲存格資料、page chrome、出版權限文字。顯示方程式由 equation lane 負責，text lane 直接跳過——包括有編號的（如 "(1)"、"(2a)"）、置中或獨立成行的、以及定理或證明中的方程式區塊。方程式後的變數定義（如 "Where: N = ..."）是正文，照常收錄。未使用的方程式字詞不算遺漏。
- **跨頁段落**：`pages` 列出所有出現頁面，`word_ids` 包含所有頁面的 word。
