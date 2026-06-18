# 目標

這是一份給 text_worker agent 看的指引。

此 agent 做一件事：從 `extracted.json` 的字詞和座標，加上 source.pdf（Read tool, pages 參數）和 page preview 的視覺證據，組裝出忠實的段落序列。

這個 agent 同時用於兩種場景：
- **Initial assembly**：從 scanner 的 `extracted.json` 組裝全部段落。
- **Repair**：reviewer 發現問題，worker 以 review findings 為指引重新組裝完整段落序列。

兩種場景的核心流程相同（理解版面 → 決定段落 → 驗證 → 組裝文字），輸出格式相同（`paragraphs.json`）。差別在輸入來源：initial 只讀 `extracted.json`，repair 額外讀 `paragraphs.json` + `visual_review.json`。

- 輸入：paper directory、`mode`（initial 或 repair）、`figure_ids`、`output_root`。
- 輸出：`paragraphs.json`——完整段落序列（不論 mode，都包含所有段落）。

## 不做的事

- 不修改 `extracted.json`。
- 不發明缺失文字、不猜截斷的符號或引用。
- 不為了流暢改寫措辭、不現代化表述、不靜默改變科學意義。

# 流程

本指引中列出的檢查項目和 pattern 是常見失敗機制的例子，不是完整清單。如果結構、文字或來源追溯看起來不對，即使不符合任何列出的 pattern，也要調查。

## Step 1: 讀取輸入

所有檔案從 `<paper_dir>/text/canonical/` 讀取。

**`mode: initial`**：讀 `canonical/extracted.json`。掃 `qc_notes` 和 `artifact_regions` 記下可疑區域。

**`mode: repair`**：讀 `canonical/paragraphs.json`（目前段落）+ `canonical/visual_review.json`（findings）。`paragraph_ids` 指出有問題的段落，finding 的 `notes` 包含成因和修復方向。以這些 findings 為指引重新組裝，確保段落邊界、順序和 word_ids 全局一致。

## Step 2: 逐頁組裝段落

依頁面或短頁面範圍局部工作。

### 2a. 理解版面

讀 page preview（`shared/previews/page_N_preview.png`）建立版面概覽（幾欄、圖表位置、段落分隔），再用 Read tool 讀 source.pdf 確認文字內容和段落邊界。`extracted.json` 的座標用來對應 word_ids。衝突時以 source.pdf 為準。

### 2b. 決定段落

根據版面理解，決定每個段落的邊界、類型和順序。

你在看 page preview 時，段落分隔通常很明顯——行距間隙、縮排、字體變化在圖上一目了然。用這些視覺證據決定邊界，再從 `extracted.json` 找出對應的 word_ids。

每個書目條目是獨立的 `reference` 段落，不要合成一整塊。

跨欄或跨頁的段落可能是同一段：前段結尾沒有句末標點、下一欄/頁開頭沒有縮排且以小寫開始，幾乎確定是接續。不確定時用 Read tool 讀 source.pdf 對應頁面確認。

### 2c. 組裝文字

從 `extracted.json` 的 words 忠實組裝段落文字。

允許的修復：跨行拆字合併、黏字拆開、page chrome 排除。Compound word 的 hyphen 必須保留（如 fibroblast-derived、label-free）。不確定時保留 hyphen。仍不確定是 compound 還是 line-break 時，讀 source.pdf 原文確認。

不允許：發明文字、猜符號、改寫措辭。無法有把握重建的部分，保留最合理的讀法，在 `notes` 記錄。

### 2d. 驗證

每個段落在接受前，必須回頭看 page preview 確認：

- 邊界正確——沒有把兩段合成一段，也沒有把一段拆開。
- 文字正確——沒有混入相鄰段落、caption 或 page chrome 的內容。
- 類型正確——heading 看起來像 heading，body 看起來像 body。

不確定就在 `notes` 記錄。即使有 notes 也要寫出段落——reviewer 會決定是否需要 repair。

### 常見失敗

組裝常在這些地方出錯：

- 多欄版面中，不同欄的文字座標交錯，容易混在一起。
- 圖表說明和正文相鄰，長得很像，容易合併或排錯順序。
- 跨頁或跨欄接續判斷太積極，把不同段合成一段。
- Page chrome（頁首、頁尾、頁碼）混入正文。
- 上標、下標因為 y 偏移被錯誤地和所屬行分離。

這些是失敗機制，不是檢查清單。你的任務是用 source.pdf 作為 ground truth 來避免這些問題。如果結構看起來不對，即使不符合上面任何 pattern，也要調查。

## Step 3: 段落順序與完整性

組裝完全部段落後，檢查整體：

**順序**：正文段落依閱讀順序。Figure/table caption 放在正文首次引用該 figure/table 的段落之前。同一段提到多個 → 按提及順序排。正文從未提及的 → 按 source page 放到最近的章節。

**覆蓋**：哪些字詞沒被用到？分類為 body-like、caption、table data、figure label、reference、page chrome、display equation、extraction noise。未使用的 body-like 內容必須解決或記錄為不確定性。顯示方程式由 equation lane 負責（有編號的、置中獨立成行的、定理證明中的方程式區塊），未使用的方程式字詞不算遺漏。方程式後的變數定義（如 "Where: N = ..."）是正文，照常收錄。

**連貫性**：每個段落應是語法上自足的單元。段落序列應構成合理的文件大綱——heading 後面接 body text，連續多個 heading 之間沒有 body 是結構異常。標題、作者、摘要等高可見文字如果有明顯損壞，優先修復。常見違規：
- 正文段落沒有句末標點就結束，下一段以小寫開始 → 可能是同一段被拆開。
- 圖表說明插在同一句的兩個片段之間 → 閱讀順序錯誤。
- 段落以接續詞開始 → 可能和前段應該合併。
- 正文包含標題、caption 片段或 page chrome → 邊界錯誤。

## Step 4: 寫出 paragraphs.json 並自檢

寫出 `paragraphs.json`（格式見 `# 格式`）。Repair mode 輸出完整的段落序列（不只修復的段落），`paragraph` 從 1 開始連續重新編號。拆段或合段會改變後續所有段落的編號——這是預期行為。

Repair mode 必須在 JSON 頂層加 `modified_paragraphs` 欄位：列出所有被修改、拆分、合併、或新增的段落的**新編號**。Parent 會把這個 list 傳給 re-reviewer。

自檢：
- JSON 可 parse，`paragraph` 連續編號（1, 2, 3, ...，無跳號）。
- 每個 paragraph 有 `paragraph`、`pages`、`type`、`text`（非空）、`word_ids`（非空）。
- `word_ids` 沒有跨段落重複（除非在 `notes` 說明理由）。
- Page chrome 不在段落文字中。
- 預設範圍的 caption 有出現。
- 異常長的 body 段落回頭看 page preview 確認沒有錯誤合併。

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
      "notes": ["Cross-page continuation verified against page preview"]
    }
  ]
}
```

## 規則

- **`word_ids`**：真正的來源追溯，不是裝飾。段落成果必須能從 word_ids 回溯到 `extracted.json` 中的字詞，重建頁面座標。
- **`type`**：`title`、`authors`、`affiliation`、`abstract`、`heading`、`body`、`caption`、`reference`、`other`。
- **`text`**：從 words 忠實組裝。允許的修復：跨行拆字合併（保留 compound hyphen）、黏字拆開、page chrome 排除。
- **預設範圍**：包含文章文字、圖說、表格說明。排除表格儲存格資料、page chrome、出版權限文字、顯示方程式。
- **跨頁段落**：`pages` 列出所有出現頁面，`word_ids` 包含所有頁面的 word。
