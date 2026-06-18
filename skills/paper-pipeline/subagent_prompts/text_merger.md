# 目標

這是一份給 text_merger agent 看的指引。

此 agent 做一件事：把多個 worker 的 paragraphs 輸出合併成一份完整的 `paragraphs.json`。每個 worker 處理一段重疊的頁面範圍，overlap 區域會有重複或衝突的段落——merger 決定保留哪個版本、如何銜接。

- 輸入：N 份 worker 的 `paragraphs.json`（各自包含 worker_id 和負責的頁面範圍）+ `canonical/extracted.json` + source.pdf。
- 輸出：`<output_root>/paragraphs.json`——合併後的完整段落序列。
- 邊界：此 agent 只做合併判斷。不重新組裝段落文字、不修改 word_ids、不發明內容。

## 不做的事

- 不重新組裝段落（保留 worker 的 text 和 word_ids 原文）。
- 不修正 worker 的 hyphen 或 spacing 問題（留給 reviewer）。
- 不補充 worker 遺漏的內容（留給 reviewer → repair）。

# 流程

## Step 1: 讀取所有 worker 輸出

讀取 assignment 中列出的所有 worker paragraphs JSON。記錄每個 worker 的：
- `worker_id`
- `owned_pages`：該 worker 專屬負責的頁面（非 overlap）
- `overlap_pages`：和相鄰 worker 重疊的頁面

這些資訊從 assignment block 取得。

## Step 2: 非 overlap 區域——直接採用

對每個 worker 的 `owned_pages` 範圍內的段落，直接納入最終輸出，不做修改。這是整個合併最簡單的部分——大部分段落走這條路。

## Step 3: Overlap 區域——判斷與合併

Overlap 區域的段落會被兩個相鄰 worker 處理。Merger 需要決定：

### 3a. 辨識重複段落

兩個 worker 產出的段落如果 word_ids 高度重疊（>50% 共同 word_ids），視為同一段落的兩個版本。

### 3b. 選擇最佳版本

對每對重複段落，選擇較好的版本。判斷依據：

- **完整性**：跨頁段落哪個版本包含更多 word_ids？覆蓋更完整的那個版本更好。
- **邊界正確性**：哪個版本的段落邊界更合理（句首開始、句末結束、沒有混入無關內容）？
- **上下文連貫**：哪個版本在其 worker 的段落序列中和前後段落銜接更流暢？

通常規則是：**跨頁段落選看到更多頁面的那個 worker 的版本。** 例如頁面 7 的段落跨到頁面 11——如果 worker_01（pages 1-8）和 worker_02（pages 7-16）都組裝了它，worker_02 的版本幾乎一定更完整，因為它能看到 page 11。

### 3c. 處理邊界段落

有些段落只存在於一個 worker 的 overlap 區域，另一個 worker 沒有組裝。判斷：
- 如果它的 word_ids 全在 overlap 區域，且另一個 worker 已經涵蓋了那些 words → 丟棄（是重複片段）。
- 如果它包含另一個 worker 完全沒碰的 word_ids → 保留。

### 3d. 不確定時讀 source.pdf

如果兩個版本品質相當、或無法從 word_ids 判斷哪個更好，用 Read tool 讀 source.pdf 對應頁面確認原文結構。

## Step 4: 組裝最終序列

按照閱讀順序排列所有保留的段落：
1. Worker_01 的 owned_pages 段落
2. Overlap 12 區域選出的段落
3. Worker_02 的 owned_pages 段落
4. Overlap 23 區域選出的段落
5. Worker_03 的 owned_pages 段落
6. ...依此類推

排序後重新指派連續的 `paragraph` 編號（從 1 開始）。

## Step 5: 銜接檢查

合併後的段落序列在 worker 邊界處可能有連貫性問題。快速檢查：
- 相鄰 worker 交界處的段落是否語法連貫（前段有句末標點、後段不以小寫接續詞開始）。
- 如果交界處有斷裂跡象（看起來應該是同一段），merge 成一段。只在這種情況下 merger 可以合併段落。
- Captions 的位置：如果 caption 被分到了引用它的正文之後，重新排列到正文之前。

## Step 6: 寫出 paragraphs.json 並自檢

寫出合併後的 `paragraphs.json`（格式同 `text_worker.md` 的輸出），然後自檢：
- JSON 可 parse，`paragraph` 連續編號。
- 每個 paragraph 有 `paragraph`、`pages`、`type`、`text`（非空）、`word_ids`（非空）。
- `word_ids` 沒有跨段落重複。
- 合併沒有遺失段落——每個 worker owned_pages 範圍的段落都在。
- 段落 `pages` 欄位和 `word_ids` 一致（word_ids 來自的頁面都列在 pages 中）。

# 格式

輸出格式和 `text_worker.md` 的 `paragraphs.json` 完全相同（`schema_version: "paragraphs.v1"`）。Merger 不引入新欄位。

## 規則

- **選版本的預設策略**：跨頁段落選「能看到更多相關頁面」的 worker 版本。同頁段落如果兩版相同，選前一個 worker 的版本。
- **合併段落的唯一時機**：worker 交界處兩段明顯是同一句的前後半段（前段無句末標點 + 後段以小寫開始 + 兩段 word_ids 不重疊）。除此之外不合併、不拆分、不改寫。
- **word_ids 是硬約束**：merger 不得修改任何段落的 word_ids 或 text。如果有問題，原樣保留，reviewer 會標記。
- **不確定就保留**：如果不確定某段該丟棄還是保留，保留。多一段比少一段安全——reviewer 可以標 boundary_corruption，但 missing_content 更難修。
