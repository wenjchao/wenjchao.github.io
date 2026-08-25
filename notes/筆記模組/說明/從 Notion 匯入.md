# 從 Notion 匯入

## 摘要
附的 `notion2modules.py` 可以把 Notion 匯出的 HTML 頁面轉成模組：頁面變總覽，**每一個 toggle——不論在第幾層、不論大小——都變成一個模組**，資料夾照 toggle 的巢狀；圖片一併複製並改成乾淨檔名。摘要不會自動產生（程式不猜），轉完自己補、再微調檔名。

## 內文
### 步驟

1. 在 Notion 裡對頁面選 **Export → HTML**，Include content 選 Everything，勾 **Include subpages** 與 **Create folders for subpages**。解壓後會得到 `頁名.html` 與同名的資料夾（放圖片）。
2. 第一次先裝兩個套件：`python3 -m pip install beautifulsoup4 lxml`。
3. 執行（輸出資料夾通常就是你的筆記資料夾）：

```bash
python3 notion2modules.py "CV new.html" ~/我的筆記
```

4. 得到 `我的筆記/CV new.md`（總覽）和 `我的筆記/CV new/…`（各主題、子題、子子題……與 `圖片/`）。打開檢視器就能看。
5. 程式最後會列出**沒有摘要的模組**——也就是全部，因為程式不會替你寫摘要：先用 overrides.json 的 `summaries` 填好再轉，或轉完直接在檢視器裡編輯。（舊版會把「主題：重點」的 toggle 拆成標題＋摘要；使用者覺得那是亂補，0.9 起預設關閉，真的想要可以加 `--split-title`。）

### 轉換規則

| Notion 裡的東西 | 變成 |
|---|---|
| 頁面本身 | `<頁名>.md`：摘要留給你寫，內文是一排 `[[<頁名>/<主題>\|摘要]]` 卡片 |
| 每一個 toggle（含 toggle heading），不論第幾層、不論大小 | 一個模組：`<頁名>/<主題>.md`、`<頁名>/<主題>/<子題>.md`、`<頁名>/<主題>/<子題>/<子子題>.md`……父模組在 toggle 原本的位置放一張 `[[相對路徑\|摘要]]` 卡片；toggle 在清單項目或引言裡面，卡片也跟著在那裡 |
| toggle 的前後鄰居是清單項目（例如 Heart Echo 的 EF 夾在 LVIDd、LA dimension 之間） | 併進同一個清單、用「扁平」外觀：`- [[<頁名>/<主題>\|扁平]]`（編號清單則接續編號），看起來和其他項目平行、標題後面多一個可展開的粗箭頭；連續幾個 toggle 一起併 |
| h3 標題後面的散落段落 | 以該標題為名的模組（例如「其他用藥」）；h3 後面直接接 toggle 時，h3 只當分組標題留在總覽 |
| 標題寫成「主題：重點」或「主題 ⇒ 重點」 | 整句都是標題、沒有摘要（預設）；加 `--split-title` 才拆成 標題＝主題、摘要＝重點。標題尾端的冒號不會進檔名 |
| blockquote 開頭是一行粗體 | 小節標題（Notion 裡常這樣當分段用） |
| Callout | `> 💡 …` 引言 |
| 表格、編號、核取方塊、程式碼、分隔線 | 對應的 Markdown |
| 粗體、斜體、底線、刪除線、螢光 | `**`、`*`、`<u>`、`~~`、`<mark>`（預設底色的螢光會拿掉） |
| 行內數學式（KaTeX） | `$…$`，檢視器會用 KaTeX 渲染 |
| 連到其他 Notion 頁面的連結 | 只留文字（那一頁不在匯出裡） |
| 圖片 | 複製到 `<頁名>/圖片/`，檔名去掉空白與 %XX 編碼；引用到別頁資料夾的圖會放進 `圖片/<那頁>/` |

### 微調：overrides.json

想改檔名、模組標題或預先填好摘要，寫一個 JSON 再用 `--overrides` 帶進去：

```json
{
  "summaries": { "CV new/Heart failure": "急性與慢性心衰竭的評估、分期、GDMT 與裝置。",
                 "CV new/Heart failure/Usage of Swan-Ganz/大圖": "Swan-Ganz 各項數值的大圖。" },
  "names":     { "High-Troponin rapid algorithm": "hs-Troponin 0-1-3 小時流程",
                 "CV new/Heart Echo/Diastolic dysfunction 的 echo 指標/圖示：": "Tissue Doppler 圖示" },
  "titles":    { "Non-cyanotic(Acyanotic) heart disease": "Non-cyanotic (acyanotic) heart disease" },
  "fixes":     [["Aortic aneuysm", "Aortic aneurysm"]]
}
```

`names`／`titles` 的 key 只要是原標題的**開頭**就會對到；寫成「`資料夾/原標題開頭`」就只對那個資料夾生效（兩個都叫「圖示」的 toggle 想分開命名時用得到）。`summaries` 的 key 是輸出的相對路徑（不含 .md），幾層都可以——這是唯一會產生摘要的地方。

其他選項：`--name 頁名`（不用 HTML 裡的標題）、`--no-images`（不複製圖片）、`--split-title`（「主題：重點」拆成標題＋摘要，預設不拆）。

### 轉完以後

- 總覽的摘要與沒有自動摘要的模組，花幾分鐘補一下——這是整套系統最有價值的部分。
- 檔名是從標題截出來的，太長的可以直接在檔案總管改名，再用左下角「壞連結」檢查有沒有要修的連結。
- Notion 裡「圖示」「大圖」這類只有圖的 toggle 也會各自成為模組（只有標題與圖、沒有摘要）：卡片顯示標題、按 ▸ 看圖，和 Notion 的收合行為一樣；嫌零碎可以手動合併回父模組。
- 想把某張卡片改成扁平（或反過來），直接把連結裡的 `摘要` 換成 `扁平`（或在直觀編輯裡點那個模組、改外觀）。
- 轉換是單向的：之後就在 .md 上編輯，不要再回 Notion 改。
