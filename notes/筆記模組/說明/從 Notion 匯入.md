# 從 Notion 匯入

## 摘要
1. `notion2modules.py` 把 Notion 匯出的 HTML 轉成模組：每個 toggle＝一個模組，資料夾照巢狀，圖片一併搬。
2. 重點是**原樣搬運**：不補摘要、不亂補任何內容。
3. 轉換是單向的：轉完就在 .md 上編輯，不回 Notion。

## 內文
### 步驟

1. Notion：頁面 → **Export → HTML**，Everything＋**Include subpages**＋**Create folders for subpages**。解壓得 `頁名.html`＋同名圖片資料夾。
2. `python3 -m pip install beautifulsoup4 lxml`（一次）。
3. `python3 notion2modules.py "CV new.html" ~/我的筆記` → `我的筆記/CV new.md`（總覽）＋ `我的筆記/CV new/…`（各層模組與 `圖片/`）。

### 原樣搬運

- 程式只搬運、只改格式，不產生內容：沒有摘要就留空，**轉完也不要補**。
- 標題一字不動；舊版會把「主題：重點」拆成標題＋摘要，已預設關閉（要開加 `--split-title`）。
- 轉完的整理只做三件不動內容的事：檔名太長就改名（再用「壞連結」修連結）、卡片改外觀（連結裡 `摘要` 換 `扁平`）、太零碎的小模組用併回鈕併回上層。

### 匯入之後：改寫

匯入只搬運；把筆記變好是之後手動改寫的事（見 [[如何編輯內容/怎麼寫出好筆記]]）。改寫時常見的 Notion 殘留：

- 💡 callout 和 blockquote：只是包裝，拆掉，內容用一般清單寫。
- 為了在兩處顯示而複製的頁面：刪掉複本，兩處引用同一個模組。
- 用 `###` 假裝的分節：夠格的（會被引用、夠長、夠獨立）切成子模組，其餘留著。
- 複述內文的摘要：整段刪，或重寫成架構與結論。

### 轉換規則

| Notion 裡的東西 | 變成 |
|---|---|
| 頁面本身 | `<頁名>.md`：摘要留空，內文是一排 `[[<頁名>/<主題>\|摘要]]` 卡片 |
| 每一個 toggle（含 toggle heading），不論第幾層、不論大小 | 一個模組：`<頁名>/<主題>.md`、`<頁名>/<主題>/<子題>.md`……父模組在 toggle 原位放 `[[相對路徑\|摘要]]` 卡片；toggle 在清單或引言裡，卡片也跟著在那裡 |
| toggle 的前後鄰居是清單項目（如 Heart Echo 的 EF 夾在 LVIDd、LA dimension 之間） | 併進同一個清單、用「扁平」外觀：`- [[<頁名>/<主題>\|扁平]]`（編號清單接續編號）；連續幾個 toggle 一起併 |
| h3 後面的散落段落 | 以該 h3 為名的模組；h3 後直接接 toggle 時，h3 只當分組標題留在總覽 |
| 標題「主題：重點」「主題 ⇒ 重點」 | 整句都是標題、沒有摘要（預設）；`--split-title` 才拆。標題尾端冒號不進檔名 |
| blockquote 開頭一行粗體 | 小節標題 |
| Callout | `> 💡 …` 引言 |
| 一般引言（無粗體標題的 blockquote） | 單行 → `###` 小節標題；多行 → 獨立子模組、原位 `[[子模組\|全文]]`（粗體或 ≤40 字的第一行當標題；取不出標題的保留 `>` 並在結尾警告） |
| 表格、編號、核取方塊、程式碼、分隔線 | 對應 Markdown |
| 粗體、斜體、底線、刪除線、螢光 | `**`、`*`、`<u>`、`~~`、`<mark>`（預設底色的螢光拿掉） |
| 行內數學式 | `$…$`（KaTeX） |
| 連到其他 Notion 頁的連結 | 只留文字（那頁不在匯出裡） |
| 圖片 | 複製到 `<頁名>/圖片/`，檔名去空白與 %XX；引用別頁資料夾的圖放 `圖片/<那頁>/` |

### 微調：overrides.json

改檔名或標題用 `--overrides overrides.json`：

```json
{
  "names":  { "High-Troponin rapid algorithm": "hs-Troponin 0-1-3 小時流程",
              "CV new/Heart Echo/Diastolic dysfunction 的 echo 指標/圖示：": "Tissue Doppler 圖示" },
  "titles": { "Non-cyanotic(Acyanotic) heart disease": "Non-cyanotic (acyanotic) heart disease" },
  "fixes":  [["Aortic aneuysm", "Aortic aneurysm"]]
}
```

- `names`／`titles` 的 key 是原標題的**開頭**；寫「`資料夾/開頭`」只對那個資料夾生效（兩個同名 toggle 分開命名用）。
- 另有 `summaries`（key＝輸出相對路徑，預先填自己寫的摘要）——原樣搬運原則下通常不用。
- 其他選項：`--name 頁名`（不用 HTML 標題）、`--no-images`。
