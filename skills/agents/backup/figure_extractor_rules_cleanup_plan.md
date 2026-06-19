# figure_extractor 規則區去重計畫

這份計畫只討論 `figure_extractor.md` 的 `# 規則` 區域。目標是減少重複、保留必要 contract，並讓讀者能快速知道每條規則應該去哪裡看。

本計畫不直接修改 `figure_extractor.md`。每一項都先列出想改什麼、想怎麼改，以及需要動到的位置。

# 整體方向

- 流程段保留「做到這一步時要注意什麼」。
- 規則段保留「完整判準與跨流程 contract」。
- 同一條規則只保留一個完整版本；其他地方若需要提醒，只放短指針。
- 不刪掉重要 contract，只刪掉同一內容的重複展開。

# 可選結構重整方案

下面是較大幅的 `# 規則` 區重整方案。它不是第一輪必做項目，但應該保留在計畫裡，方便討論是否要在去重後套用。

```md
# 規則

## 權責

## 圖片與座標
### 圖片與讀取限制
### 座標規則

## 候選與 source context
### 來源區域（source_regions）
### 閱讀證據紀錄（evidence_read）中的 source context

## 裁切內容
### 圖說與圖片邊界
### 跨頁與多區域 figure

## 視覺驗證
### 輔助工具的能力邊界
### verification 欄位
### evidence_read 與 pass 的對應
### 邊界檢查與高頻失敗模式

## 機械自檢

## 空範圍
```

這個結構的優點是把相近概念放在一起：
- 圖片讀取限制與座標規則同屬「圖片與座標」。
- `source_regions` 與 decision 階段的 `evidence_read` 同屬「候選與 source context」。
- 圖說邊界與跨頁/多區域同屬「裁切內容」。
- `verification`、final 階段的 `evidence_read`、高頻失敗模式同屬「視覺驗證」。

這個結構的風險是改動較大，容易牽動已經寫順的段落。因此建議先做去重；去重後如果 `evidence_read` 與 `視覺驗證` 仍然顯得分散，再考慮套用這個重整方案。

# 本計畫已涵蓋的具體改動

以下六項是本計畫會處理的重點：

- `輔助工具的能力邊界`：刪掉完整 preview 清單，保留工具能力邊界；工具輸出不能取代 agent 的讀圖判斷。
- `verification 三個欄位`：保留 `pass` 的視覺前提，說明 source context、final crop preview、四個 edge previews 都讀過且可接受後，才可以標 `pass`。
- `閱讀證據紀錄（evidence_read）`：保留 `pass` 與 preview 紀錄的對應規則，作為 audit trail。
- `高頻失敗模式`：改成失敗類型清單，不再重列完整的保留/排除細項。
- `圖說與圖片邊界`：保留完整的保留/排除清單，作為 figure boundary 的主規則。
- 流程 step 12/13：保留流程檢查提醒，但用短句，不展開成另一份完整規則清單。

# A. `pass` 的讀圖前提與 `evidence_read`

## 問題

目前「標成 `pass` 前必須讀過哪些 preview」散在多個地方：
- `### 輔助工具的能力邊界`
- `### verification 三個欄位`
- `## 閱讀證據紀錄（evidence_read）`

這四處不是完全等價。`evidence_read` 能檢查 manifest 裡有沒有紀錄，但不能取代「agent 必須真的讀圖後才能標 `pass`」這條視覺前提。

## 決策

保留兩層規則：
- `verification` 段說明：什麼情況可以把視覺檢查標成 `pass`。
- `evidence_read` 段說明：標成 `pass` 後，JSON 裡必須能找到對應的讀圖紀錄。

其他段落不再重複列出完整 preview 清單。

## 建議改法

### `### verification 三個欄位`

在這裡保留主規則，寫清楚 `pass` 的視覺前提：

```md
- 一個 figure 只有在 source context、final crop preview、四個 edge previews 都已讀過，且三項檢查都可接受時，才能把相關 `verification` 欄位與 `result` 標成 `pass`。
```

這條是人類與 agent 的判斷規則，不是機械自檢規則。

### `## 閱讀證據紀錄（evidence_read）`

保留目前較細的對應規則：
- `source_context_checked = "pass"` 對應 `page_previews` 或 `source_region_previews`
- `final_crop_checked = "pass"` 對應 `final_crop_previews`
- `edge_previews_checked = "pass"` 對應 `edge_previews`

這段負責 audit trail，不負責取代視覺判斷。

### 其他段落怎麼處理

- `輔助工具的能力邊界`：把末條改成「輔助工具輸出只能當作 candidate evidence，不是 final truth；工具輸出不能取代 agent 的讀圖判斷。」
- `高頻失敗模式`：刪掉「沒有讀 source context preview、final crop preview 和四個 edge previews 就標 `pass`」這條；這是一般 pass gate，不是 crop 品質的失敗類型。
- 完整 `pass` 條件只在 `verification` 與 `evidence_read` 展開。

# B. 該保留什麼、該排除什麼

## 問題

「figure 內容要保留」和「非 figure 內容要排除」同時出現在：
- `## 圖說與圖片邊界`
- `### 高頻失敗模式`
- 流程 step 12 的檢查清單

這些內容都在講 figure boundary，但目前分散後會讓讀者覺得清單一直重來。

## 決策

完整保留/排除清單放在 `## 圖說與圖片邊界`。  
流程段保留檢查提醒。  
`高頻失敗模式` 只列失敗類型，不再重列完整清單。

## 建議改法

### `## 圖說與圖片邊界`

保留完整規則：
- 外部圖說只存 `caption_text`，不放進 crop。
- 圖內文字屬於 figure 內容，應保留。
- 不確定文字歸屬時，要寫 `rationale` 或 `notes`，不能標 `pass`。
- 正文、外部圖說、頁碼、頁眉、頁腳、期刊固定元素、浮水印、相鄰圖表、table、equation 與其他非 figure 內容應排除。

這段是 figure boundary 的主規則。

### `### 高頻失敗模式`

把原本的長清單改成較短的失敗類型：

```md
- caption / page chrome leakage。
- figure content truncation。
```

不要在這裡再展開所有 caption、頁眉、頁腳、座標軸、圖例、比例尺等細項。細項已經由 `圖說與圖片邊界` 和流程 step 12 承擔。

### 流程 step 12

可以保留具體檢查清單，因為流程段需要提醒 agent 在 final crop + edge previews 檢查時逐項看圖。  
但如果 step 12 已經太長，可以把細項濃縮成：

```md
- figure 內容是否完整；非 figure 內容是否被排除。完整邊界規則見「## 圖說與圖片邊界」。
```

這項是否要濃縮，需另行決定。

# C. page-strip / full-column crop

## 問題

`page-strip` 失敗模式同時出現在：
- 流程 step 13
- `### 高頻失敗模式`

這是重複，但它也是高頻錯誤。完全刪掉流程段提醒，可能會讓 agent 在邊界決策時忘記先檢查 crop 形態。

## 決策

兩邊都保留，但功能不同：
- 流程 step 13 保留短提醒，因為這是邊界決策當下要做的事。
- `高頻失敗模式` 保留概念宣告，說 page-strip 本身是常見失敗類型。

## 建議改法

### 流程 step 13

保留 inline 規則，但不要展開：

```md
先檢查 crop 是否像整頁、整欄或大頁面條帶；這類 page-strip 失敗模式不得直接標 `pass`。
```

### `### 高頻失敗模式`

保留：

```md
- page-strip / full-column crop。
```

這裡只列失敗類型，不重複操作規則。

# D. preview 對應原檔與 `source_regions`

## 問題

preview 對應原檔的規則出現在：
- `## 圖片與讀取限制`
- `## 來源區域（source_regions）`

這兩處有交集，但角度不同。

## 決策

保留兩段：
- `圖片與讀取限制` 講所有 preview 的全域規則。
- `source_regions` 講 source region 何時必須建立。

## 建議改法

### `## 圖片與讀取限制`

可以把「每個 preview 都必須有對應原檔」寫短一點：

```md
- 每個 preview 都必須來自對應原檔或工作中間檔，不得憑空產生。
```

### `## 來源區域（source_regions）`

保留現在的 lifecycle 規則：
- agent 要讀 source context 前，必須先建立 source region preview 與完整解析度原檔。
- candidate 進入 `figure_index.json` 時，也必須有 source region preview 與完整解析度原檔。

這裡不只是圖片命名，而是 source context 的建立時機。

# E. `evidence_read` 是否併入 `視覺驗證`

## 問題

`evidence_read` 和 `verification` 高度相關。讀者可能會希望兩者放在一起。

## 決策

先不搬章節。先完成去重，再看 `evidence_read` 是否還需要獨立。

## 理由

如果現在直接把 `evidence_read` 併入 `## 視覺驗證`，`視覺驗證` 會變成很大的 section。  
先去重後，`evidence_read` 段可能會自然變短，到時再決定是否降成 `視覺驗證` 底下的 `### evidence_read 紀錄`。

# F. 建議修改順序

1. 先整理 `pass` 規則：
   - `verification` 保留主規則。
   - `evidence_read` 保留對應紀錄規則。
   - `輔助工具的能力邊界` 和 `高頻失敗模式` 改成短提醒。

2. 再整理 figure boundary：
   - 完整保留/排除清單留在 `圖說與圖片邊界`。
   - `高頻失敗模式` 改成失敗類型，不重列細項。

3. 接著整理 page-strip：
   - 流程段保留短提醒。
   - `高頻失敗模式` 保留類型名稱。

4. 最後整理 preview 對應原檔：
   - `圖片與讀取限制` 改短。
   - `source_regions` 保留建立時機。

5. 完成後再評估是否需要把 `evidence_read` 併入 `視覺驗證`。

# G. 暫時不做的事

- 不大幅重排整個 `# 規則` 區。
- 不刪掉 `source_regions`、`evidence_read` 或 `verification` 的 contract。
- 不把 `evidence_read` 當成唯一 pass 條件。
- 不把流程段改成只剩步驟名稱；流程段仍應保留該步驟必要的短規則。
