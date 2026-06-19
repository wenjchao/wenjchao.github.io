# figure_extractor.md 寫作風格遺留問題

這份文件列出新版 `figure_extractor.md`（已套用 `figure_extractor_revision_plan.md` 所有決策）後仍存在的 5 個寫作風格問題，並提供改寫方法。

問題按影響可讀性的程度排序：A 影響最大，E 最小。

每條問題附：
- **現況**：plan 中目前的樣子
- **為什麼有問題**：對照 `rewrite_goals.md` 規範
- **改寫方法**：具體的修法（含範例）

---

## 抽取原則：規則放在流程段還是規則段？

5 個問題的處理方向會被一個前提決定：哪些規則應該 inline 在流程段、哪些應該抽到規則段。先把判準講清楚。

### 預設方向

**規則跟著它執行的 step 放在流程段（inline）**。流程段不只是「做事順序」的索引，也包含當下執行該 step 必須知道的規則。讓 agent 順著流程讀下去，不必反覆跳到後段查基本判斷。

### 抽到規則段的三個條件

滿足下列**任一**條件才抽到規則段：

1. **跨多個 step 適用**（cross-cutting）——例如 `_preview` 限制、JSON 座標規則、enum 列表，這些不屬於任何單一 step。
2. **太長到 inline 會壓垮 step 可讀性**——例如 6 條以上的細項清單，硬塞進一個 step 會打斷流程閱讀。
3. **有獨立 concept-identity，agent 或 reviewer 會回頭 reference**——例如「視覺驗證契約」「機械自檢」這類有名稱、會被指涉的概念。

不滿足任何條件就 inline。**一個規則只放一個位置，不要兩處重複**。

### 套用到 `figure_extractor.md` 現有規則

| 規則 | 屬性 | 結論 |
|---|---|---|
| 邊界決策樹 | 只在 step 13-14 用、是該 step 的主要操作邏輯、agent 不會回頭 reference | **只 inline 在 step 13-14**；規則段不放 |
| Mechanical self-check | step 17 唯一觸發，但 6 條 inline 會壓垮（條件 2），且有 concept-identity（條件 3） | **抽到規則段**；step 17 簡述並指針 |
| `_preview` 限制 | 跨所有讀圖 step（條件 1） | **抽到規則段** |
| 座標規則 | 所有寫 JSON 座標時都適用（條件 1） | **抽到規則段** |
| JSON 命名與 enum | 所有 JSON 都適用（條件 1） | **抽到規則段** |
| `expected_panels` 填寫 | 寫 JSON 時用，跨多個 step（條件 1） | **抽到「JSON 命名與 enum」段** |
| 視覺驗證契約（工具能力、verification subfield、失敗模式） | 多個 step 都會回頭參照（條件 3） | **抽到規則段「視覺驗證」** |
| `source_regions` 何時建立 | 只在 step 4 觸發、是該 step 的主要邏輯 | **inline 在 step 4**（已經是現況） |

後面 5 個問題的處理方向會反映這條判準。

---

## A. 「視覺驗證」段 26 條 bullets 沒分組（影響最大）

### 現況

`figure_extractor.md` 規則段「## 視覺驗證」(line 604-629) 一個 section 塞了約 26 條 bullets，混合五件事：

| 內容類別 | 條數 |
|---|---|
| 輔助工具能/不能（B1） | 4 條 |
| verification 三個 subfield（D3） | 4 條 |
| `expected_panels`（A3） | 1 條 |
| 邊界決策樹（A5/A6） | 4 條 |
| 圖表型圖片風險、verification pass/fail 等（原版保留） | 約 8 條 |
| 高頻失敗模式（B2） | 5 條 |

26 條全部平鋪在同一個 `## 視覺驗證` 標題下，沒有 sub-section 分組。

### 為什麼有問題

對照 `rewrite_goals.md`：

- 「**按讀者真正會卡住的點分組，不要按抽象概念分組**」——目前一節塞五件事，讀者讀完無法建立分類認知。
- 「**一條 bullet 一個概念**」雖然單條 bullet 內容簡潔，但 26 條混在一個 section 仍然會壓垮 novice 讀者。
- 「**讓人和 agent 都能快速、流暢、準確地理解流程**」——這節「快速」做不到。

對 novice 讀者來說，最致命的是**找不到 mental anchor**：26 條沒有任何分組標題，讀完只會記得「視覺驗證好像很多規則」而不知道規則之間的層次。

### 改寫方法

按抽取原則，「視覺驗證」整段保留在規則段（多 step 會回頭參照）。但內部用 `###` 分四個 sub-section。

**注意**：邊界決策樹**不**放在這節（按抽取原則只 inline 在 step 13-14），所以 sub-section 從 5 個減為 4 個。

`expected_panels` 也**不**放在這節（按抽取原則搬到「JSON 命名與 enum」段，見問題 E）。

```markdown
## 視覺驗證

### 輔助工具的能力邊界
- 這裡的輔助工具，指 render、preview、layout detection、OCR、crop、file check、coordinate check 等 script 或 detector。
- 輔助工具可以產生候選證據、建立預覽圖片、執行裁切、檢查檔案是否存在、檢查座標是否在頁面範圍內。
- 輔助工具不能判斷 figure 是否完整、caption 是否外漏、座標軸或圖例是否被切掉，也不能判斷 crop 是否只是 page strip。
- 所以輔助工具輸出只能當作 candidate evidence，不是 final truth。`pass` 必須由 agent 讀過 source context、final crop preview 和 edge previews 後判斷。

### Verification 三個 subfield
- `verification.source_context_checked`、`final_crop_checked`、`edge_previews_checked` 都寫在 `figures.json.verification` 物件內。
- `source_context_checked` 代表 agent 已讀過預覽頁面圖片或預覽裁切區域來源圖片。
- `final_crop_checked` 代表 agent 已讀過預覽最終裁切圖片。
- `edge_previews_checked` 代表 agent 已讀過四個邊界預覽。
- 每個標成 `pass` 的 figure，都必須讀過來源上下文預覽、最終裁切預覽，以及上、下、左、右四個邊界預覽。

### Pass/fail 語意
- `verification` 只使用 `pass` 或 `fail`。不要使用 `not_applicable`；沒有某種元素時，只要沒有缺失或截斷，該檢查就是 `pass`。
- `figures.json` 可以記錄 `fail`，但只要任何 figure 的 `verification.result` 是 `fail`，整個 `status` 就必須是 `incomplete`。
- 失敗的 figure 被記錄是為了 trace 與後續 repair，不代表 extraction 成功。

### 高頻失敗模式
- 不要把整頁、整欄或大頁面條帶當成 figure crop。
- 不要把外部 caption、頁眉、頁腳、頁碼、浮水印或其他 page chrome 裁進 figure。
- 不要切掉座標軸、圖例、比例尺、panel label、color bar 或其他 figure 內容。
- 不要把輔助工具產生的 bbox 當成最終裁切真相。
- 不要在沒有讀 source context preview、final crop preview 和四個 edge previews 的情況下標 `pass`。
- 圖表型圖片（折線圖、長條圖、散點圖、熱圖、Manhattan plot、帶座標軸的示意圖）的底邊與側邊風險最高，必須檢查 x 軸刻度與標題、y 軸標籤、圖例、color bar 和 plot boundary 是否完整。
```

四個 sub-sections：輔助工具能力邊界、Verification 三個 subfield、Pass/fail 語意、高頻失敗模式（含圖表型圖片風險）。

---

## B. 流程段與規則段內容重複

### 現況

四處重複：

| 內容 | 流程段位置 | 規則段位置 |
|---|---|---|
| 邊界決策樹 | step 13-14 (line 76-78) | 視覺驗證 line 617-620 |
| self-check | step 17 (line 90) | 規則段「Mechanical self-check」 |
| `_preview` 限制 | step 2 隱含 | 規則段「圖片與讀取限制」 |
| pages、image_files 不在 figure 層 | （未提）| JSON 命名 line 104 + Mechanical self-check line 649 |

舉例對照（邊界決策樹）：

**流程 step 13-14**：
> 13. 邊界檢查先看 crop 形態，再讀四個邊界預覽。若 crop 像整頁、整欄或大頁面條帶，不能直接標 `pass`。大幅寬圖可以接近整頁寬度，但垂直方向仍必須緊貼 figure，且不得混入正文、外部圖說、頁碼、頁眉、頁腳或其他 page chrome。
> 14. 四邊檢查時，非 figure 內容碰邊就縮小 crop，figure 內容碰邊就放大 crop。調整後必須更新 `figure_decisions.json`、重裁、重建預覽最終裁切圖片與四個邊界預覽，並再次檢查。若 figure 內容和非 figure 內容因版面交錯而無法乾淨分離，優先保留 figure 的全部內容，將該 figure 標 `fail`，並在 `notes` 說明原因。

**規則段視覺驗證 line 617-620**：
> - 邊界檢查先看 crop 形態，再讀四個邊界預覽。若 crop 像整頁、整欄或大頁面條帶，不能直接標 `pass`。
> - 大幅寬圖可以接近整頁寬度，但垂直方向仍必須緊貼 figure，且不得混入正文、外部圖說、頁碼、頁眉、頁腳或其他 page chrome。
> - 四邊檢查時，非 figure 內容碰邊就縮小 crop，figure 內容碰邊就放大 crop。調整後必須更新 `figure_decisions.json`、重裁、重建 preview，並重新檢查。
> - 若 figure 內容和非 figure 內容因版面交錯而無法乾淨分離，優先保留 figure 的全部內容，將該 figure 標 `fail`，並在 `notes` 說明原因。

幾乎逐字重複。

### 為什麼有問題

對照 `rewrite_goals.md`：「**每個重要 contract 都明確存在，但同一件事不要重複講**」。

重複造成：
- 讀者讀到相同規則兩次，浪費 attention
- 規則更新時兩處都要改，容易 drift（兩處用詞不完全一致就會混淆）
- 文件膨脹，影響「快速理解流程」

### 改寫方法

按抽取原則，**每條規則只放一個位置**。逐項處理：

#### 邊界決策樹 → **只 inline 在 step 13-14，規則段刪除**

理由：邊界決策只在 step 13-14 觸發、是該 step 的**主要操作邏輯**、agent 不會跨 step 回頭 reference。完整保留在 step 中最直接。

**操作**：
- step 13-14 保留現狀（完整的決策樹規則）
- 規則段「## 視覺驗證」**刪除**「邊界檢查先看 crop 形態⋯⋯」「大幅寬圖⋯⋯」「四邊檢查時⋯⋯」「若 figure 內容和非 figure 內容因版面交錯⋯⋯」這四條 bullets

#### Mechanical self-check → **規則段保留完整，step 17 簡述並指針**

理由：self-check 6 條項目 inline 在 step 17 會壓垮（條件 2）；且 self-check 有 concept-identity，agent 可能回頭想「我要 check 哪些？」（條件 3）。

**操作**：
- 規則段「## 機械自檢」保留完整 6 條項目
- step 17 改成：

```
17. 寫出 `figures.json` 前，執行 mechanical self-check（檢查項目見規則段「機械自檢」）。
    self-check 失敗時，必須修正 artifact 後重檢；self-check 通過不代表視覺驗證通過。
```

#### `_preview` 限制 → **規則段保留，step 2 不重複**

理由：`_preview` 限制是跨所有讀圖 step 的 cross-cutting 規則（條件 1）。

**操作**：
- 規則段「## 圖片與讀取限制」保留完整
- step 2 不再重述「agent 讀圖時應讀預覽圖片，不直接讀超過尺寸限制的完整解析度頁面圖片」

#### pages / image_files 不在 figure 層 → **JSON 命名段為主，規則段 reference**

理由：這是 JSON schema 規則，cross-cutting 適用所有寫 JSON 場合（條件 1）。

**操作**：
- 「## JSON 命名與 enum」保留主規則（line 104）
- 「## 機械自檢」第 6 條改成「figure 層 derived field 檢查（規則見『JSON 命名與 enum』）」，不重述細節

---

## C. 三個英文 section title 跟其他中文 title 不一致

### 現況

規則段 11 個 sub-sections，其中 3 個用英文 title：

```markdown
## 權責              ✓ 中文
## 圖片與讀取限制     ✓ 中文
## 座標規則           ✓ 中文
## Source regions     ✗ 英文
## 圖說與圖片邊界     ✓ 中文
## 跨頁與多區域 figure ✓ 中文（混排）
## 視覺驗證           ✓ 中文
## Evidence read      ✗ 英文
## Mechanical self-check ✗ 英文
## 空範圍             ✓ 中文
```

### 為什麼有問題

對照 `rewrite_goals.md`「**保留自然的中文節奏**」：

> 可以保留必要的英文術語，例如 `figure_extractor agent`、`figure`、`crop`、`preview`、`final crop + edge previews`、`worker_output/worker_01/`。**不要硬翻成讀起來不自然的中文**。

但 **section title 是文件結構**，不是 inline 術語。中英混排在 title 層級會破壞文件 navigation 一致性。讀者瀏覽目錄時看到「權責 / Source regions / 圖說與圖片邊界 / Evidence read」會以為這是兩個不同來源拼起來的文件。

### 改寫方法

三個 title 改成中文（必要時括弧附英文）：

```markdown
## Source regions       → ## 來源區域（source_regions）
## Evidence read        → ## 閱讀證據紀錄（evidence_read）
## Mechanical self-check → ## 機械自檢
```

加括弧的好處是讀者搜尋英文關鍵字仍找得到；不加括弧的好處是 title 純粹中文一致。建議至少前兩個加括弧（因為對應到 JSON 欄位名），第三個不需要（「機械自檢」已經夠清楚）。

最終建議：

```markdown
## 來源區域（source_regions）
## 閱讀證據紀錄（evidence_read）
## 機械自檢
```

---

## D. step 1 / 2 / 4 句子塞太多概念

### 現況

step 1（line 25）：

> 1. 確保完整解析度頁面圖片存在。若 `shared/pages/page_N.png` 不存在，呼叫指定 render helper 從輸入 PDF 產生缺失的 page image；helper 失敗才回報缺失並停下。agent 只檢查檔案是否存在，不自行判斷「該不該 render」。完整解析度頁面圖片是判斷原始論文版面的最高依據，也是最終裁切來源與所有 JSON 座標的基準。

step 2（line 27）：

> 2. 確保預覽頁面圖片存在。若 `shared/previews/page_N_preview.png` 不存在，呼叫指定 preview helper 從對應 page image 產生缺失的 page preview。補齊後仍使用約定路徑，不把臨時輸出路徑寫進 JSON。agent 讀圖時應讀預覽圖片，不直接讀超過尺寸限制的完整解析度頁面圖片。

step 4（line 31）：

> 4. 依需要建立完整解析度裁切區域來源圖片與其預覽裁切區域來源圖片。不是所有 candidates 都必須有裁切區域來源圖片；但只要 agent 要讀 source context，或該 candidate 會進入 `figure_index.json`，就必須先建立裁切區域來源預覽與其完整解析度原檔。沒被讀也沒進入 index 的 candidate，`source_region_ids` 寫空陣列，不要省略欄位。

三個 step 各自塞了 3-4 個資訊塊：（a）操作條件、（b）helper 動作、（c）判斷邏輯注釋、（d）角色 / 為什麼說明 / 例外處理。

### 為什麼有問題

對照 `rewrite_goals.md`：

- 「**一條 bullet 只處理一個概念**」
- 「**好的流程步驟應該包含：這一步讀什麼。這一步寫什麼。這一步的 artifact 是什麼角色。這一步不是什麼。這一步如果失敗，應該怎麼處理。**」——這個建議是說「step 的內容應該交代這些」，不是「每個 step 都把這 5 件事擠成一段」。

對 novice 讀者最有殺傷力的是 step 1。流程第一步就要 parse「條件式 + helper 呼叫 + 注釋 + 角色說明」，會立刻感到資訊密度過高。step 4 同樣塞了「建立動作 + 何時必填 + 何時可空 + 空陣列規則」四個概念。

### 改寫方法

把「操作步驟」和「概念說明」分開：
- 操作放 step
- 角色/為什麼的說明挪到「## 圖片檔案」段或文件開頭「# 目標」段
- agent 讀圖規則屬於 cross-cutting（已在「## 圖片與讀取限制」），step 不重述（呼應問題 B 的 `_preview` 限制處理）
- 多概念條件式可用 sub-bullets 拆解，讓單一概念占一條

**範例**：

step 1 / step 2 改成：

```
1. 若 `shared/pages/page_N.png` 不存在，呼叫 render helper 從 PDF 產生；helper 失敗才回報並停。agent 只檢查檔案是否存在，不自行判斷「該不該 render」。

2. 若 `shared/previews/page_N_preview.png` 不存在，呼叫 preview helper 由 `page_N.png` 產生。補齊後仍使用約定路徑，不把臨時輸出路徑寫進 JSON。
```

step 4 改成 sub-bullet 結構：

```
4. 依需要建立 source region（按需產生）：
   - 必填情況：agent 要讀 source context、或 candidate 會進入 `figure_index.json` → 必須先建立 source region preview 與完整解析度原檔。
   - 可空情況：candidate 沒被讀也沒進入 index → 不必建立；其 `source_region_ids` 寫空陣列，不省略欄位。
```

「完整解析度頁面圖片是判斷原始論文版面的最高依據，也是最終裁切來源與所有 JSON 座標的基準」這句**挪到「## 圖片檔案」段**，因為那節就是介紹每張圖片的角色：

```markdown
## 圖片檔案

- 頁面圖片：`shared/pages/page_3.png`
  - 預覽：`shared/previews/page_3_preview.png`
  - 角色：原始頁面版面的最高依據；最終裁切來源；所有 JSON 座標的基準。
  ...
```

「agent 讀圖時應讀預覽圖片，不直接讀超過尺寸限制的完整解析度頁面圖片」這句**已經在規則段「圖片與讀取限制」**寫過，不必在 step 2 重複（呼應問題 B）。

---

## E. `expected_panels` 規則重複出現

### 現況

- `expected_panels` 出現在 `figure_decisions.json` example（line 338、372）
- 「## JSON 命名與 enum」段已經有 `expected_panels` 填寫規則
- 「## 視覺驗證」段又重複寫了一次相同規則

### 為什麼有問題

對照 `rewrite_goals.md`「**規則要回答讀者真正會卡住的問題**」：

讀者看 JSON example 卡住的時候會問「我看到 `expected_panels` 這個欄位，該怎麼填？」。這個答案現在已經在「JSON 命名與 enum」段；但「視覺驗證」段又重複了一次，會讓讀者以為這條規則同時屬於兩個地方。

這違反「同一件事不要重複講」的原則，也增加後續 drift 風險：若之後只改其中一處，兩段規則可能變得不一致。

對照其他欄位的處理：
- `crop_hint_px` / `crop_px`：規則在 JSON 命名段 ✓
- `role`：規則在 JSON 命名段 ✓
- `expected_panels`：規則也應只保留在 JSON 命名段 ✓

### 改寫方法

按抽取原則，`expected_panels` 是寫 JSON 時用、跨 step 適用（條件 1），應該只保留在「JSON 命名與 enum」段。

**操作**：
1. 從「## 視覺驗證」段刪除這條：
   > `expected_panels` 只能根據圖中實際可見的 panel label 或明確視覺結構填寫。不要因為 caption、cross-reference 或正文提到 `Panels A-D` 就自動發明 panel；如果 panel label 不清楚，應在 `notes` 或 `rationale` 說明。

2. 保留「## JSON 命名與 enum」段裡既有的 `expected_panels` 規則；如果需要微調用詞，只改這一處。

一處單一 source of truth。

---

## 修改順序建議

按「影響可讀性大小」+「相互依賴」排序：

1. **先做 A**（拆視覺驗證段）——影響最大、最大段重組。順帶處理「邊界決策樹從規則段移除」（呼應問題 B 第一項）。
2. **同時做 E**（刪除視覺驗證段重複的 `expected_panels` 規則）——A 拆分時順手做。
3. **接著做 B**（消除流程/規則重複）——A 完成後，邊界決策樹的處理也順帶完成；剩下 self-check、`_preview`、derived field 三項各自獨立修。
4. **再做 C**（中文化 section title）——獨立小修。
5. **最後做 D**（拆 step 1/2）——獨立小修。

A、E、B 的「邊界決策樹處理」可以一起做。B 的其餘三項、C、D 都是獨立小型修改。

---

## 整體預期效果

修完這 5 項後：

- 視覺驗證段從「26 條 bullets 一團」變成「4 個 sub-section 各 3-6 條 bullets」，novice 讀者能建立 mental model
- 流程段保留**操作 + 該 step 局部規則**的敘事節奏，規則段保留**跨 step / 太長 / 有 concept-identity 的 contract**——職責分明
- 邊界決策樹只在 step 13-14、self-check 只在規則段、各得其所
- 文件 navigation 純中文一致，目錄可讀
- step 1/2 從「資訊塊堆疊」變成「操作 + helper + 注釋」單一概念
- `expected_panels` 規則只保留在讀者預期的位置，不在視覺驗證段重複

文件總長度會略減（消除真重複），但結構更清楚——對 novice 讀者的「一讀就懂」標準幫助最大。

---

# 補充問題：目前 style issues 還漏掉的幾處

前面 A-E 已經抓到主要結構問題，但還有幾個會影響「新版 schema 語意一致性」和「novice 讀者理解速度」的地方。這些問題不一定比 A-E 嚴重，但如果要做整體整理，應該一起處理。

---

## F. 開頭 `# 目標` 還有舊版命名與舊 schema 語意

### 現況

開頭輸出段仍使用：

```markdown
- `figureXX.png` (figure crops，即完整解析度最終裁切圖片)

- 目標：讓 `figureXX.png` 準確的包含 figure 的上下左右邊緣
```

同一段也說：

```markdown
`figures.json`：視覺驗證後的最終成果清單，記錄最終裁切圖路徑、頁碼、裁切框、圖說文字或來源、預覽圖、邊界預覽與驗證結果。
```

### 為什麼有問題

新版已經決定：

- 單一 crop 圖片使用 `<figure_id>.png`。
- 多個 crop 使用 `<figure_id>_part_<N>.png`。
- 頁碼、圖檔路徑、裁切框都以 `crop_units[]` 為準。

所以 `figureXX.png` 是舊版直覺命名，不再精準。`figures.json` 的描述也容易讓讀者以為頁碼、路徑、裁切框是 figure 層欄位，而不是 `crop_units[]` 裡的欄位。

這違反 `rewrite_goals.md` 的兩個原則：

- 名詞穩定，同一個 artifact 不要在不同段落換不同名字。
- 規則要直接回答讀者實際要寫哪個欄位、檔名、路徑。

### 改寫方法

把開頭改成新版命名：

```markdown
- `<figure_id>.png`：單一 crop figure 的完整解析度最終裁切圖片。
- `<figure_id>_part_<N>.png`：同一 figure 有多個 crop units 時的完整解析度最終裁切圖片。
```

目標句改成：

```markdown
- 目標：讓每個 final crop 準確包含 figure 的上下左右邊緣；不要切掉 figure 內容，也盡可能裁掉非 figure 內容。
```

`figures.json` 描述改成：

```markdown
- `figures.json`：視覺驗證後的最終成果清單。每個 figure 透過 `crop_units[]` 記錄 final crop 圖片路徑、頁碼、裁切框、預覽圖、邊界預覽與 crop 角色，並記錄 `caption_text` 與驗證結果。
```

這樣開頭就和 `crop_units` 的新版語意一致。

---

## G. workflow step 8 仍使用舊式欄位說法

### 現況

step 8 寫：

```markdown
每張圖應記錄：
- figure label
- 頁碼
- 使用的候選區域與裁切區域來源圖片
- 最終裁切框座標
- 輸出檔
- 要排除的文字或頁面元素
- 是否需要多個 crop units
- 決策理由或備註
```

### 為什麼有問題

新版 `figure_decisions.json` 的重點是 `crop_units[]`。頁碼、最終裁切框座標、輸出檔都不應被讀成 figure 層欄位，而應該明確寫在 `crop_units[]` 裡：

- `crop_units[].page`
- `crop_units[].crop_px`
- `crop_units[].image_file`

目前 step 8 的列法容易讓 novice 讀者以為 decision figure object 直接有 `pages`、`crop_px` 或 `output_file`。

### 改寫方法

把 step 8 的列點改成以 `crop_units[]` 為中心：

```markdown
每張圖應記錄：
- figure label
- 使用的候選區域、視覺區域、圖說區域與 source region
- `caption_text`
- `crop_units[]`：每個 crop unit 記錄 `crop_id`、`page`、`crop_px`、`image_file`、預期 preview / edge preview 路徑與 `role`
- 要排除的文字或頁面元素
- 決策理由或備註
```

「是否需要多個 crop units」可以不用獨立列，因為是否多個 crop 直接由 `crop_units[]` 的數量表達。

---

## H. `JSON 命名與 enum` 段內容過密

### 現況

`## JSON 命名與 enum` 目前同時包含：

- `schema_version`
- 欄位命名 / anti-drift 規則
- `region_type`、`source`、`figure_type` enum
- `unexpected_labeled_figures` / `omitted_candidates`
- `crop_hint_px` / `crop_px`
- `expected_panels`
- `role`

內容都重要，但都塞在同一節，讀者不容易掃描。

### 為什麼有問題

這一節目前有類似「視覺驗證段」的問題，只是程度較輕：不是規則錯，而是不同類型的規則放在同一串 bullets 裡。

對 novice 讀者來說，看到 JSON example 卡住時，會想快速找：

- 欄位名稱怎麼寫？
- enum 有哪些值？
- batch 對帳欄位怎麼填？
- 某個特殊欄位如 `expected_panels` / `role` 怎麼用？

如果全部混在一節，定位成本會變高。

### 改寫方法

保留 `## JSON 命名與 enum` 作為總章，但在內部拆成小段：

```markdown
## JSON 命名與 enum

### 版本與欄位命名
...

### 可用 enum
...

### Batch / assignment 對帳欄位
...

### 其他欄位規則
...
```

拆小段即可，不需要增加內容。重點是讓讀者能快速定位規則類型。

---

## I. `source_context_checked` 與 `evidence_read` 的關係不夠直覺

### 現況

`figures.json.verification.source_context_checked` 寫在 final manifest 裡，但對應 evidence 卻在 `figure_decisions.json.evidence_read.page_previews` 或 `source_region_previews` 裡。

規則段有寫：

```markdown
`source_context_checked = "pass"` 時，必須能在 `figure_decisions.json.evidence_read.page_previews` 或 `source_region_previews` 找到對應條目。
```

### 為什麼有問題

這個設計是合理的：source context 是 decision 階段讀的 evidence，final manifest 只記錄最後驗證結果。但對第一次讀的人來說會有一點不直覺：

- 為什麼 `figures.json` 的 verification 要看 `figure_decisions.json` 的 evidence？
- 為什麼 `figures.json.evidence_read` 不記錄 source context preview？

如果不補一句語意說明，讀者可能以為這是 schema 漏欄位。

### 改寫方法

在「閱讀證據紀錄（evidence_read）」段補一句：

```markdown
source context 是裁切決策前讀取的 evidence，所以記在 `figure_decisions.json.evidence_read`；final crop 與 edge preview 是裁切後讀取的 evidence，所以記在 `figures.json.evidence_read`。
```

這句可以放在該段第一句，先解釋分工，再列欄位。

---

## J. `figure_decisions.json` 裡的 preview / edge_previews 需要說明是預期路徑

### 現況

`figure_decisions.json` 的 `crop_units[]` 範例已經包含：

```json
"preview": "lanes/figures/worker_output/worker_01/previews/Figure_1_preview.png",
"edge_previews": {
  "top": "...",
  "bottom": "...",
  "left": "...",
  "right": "..."
}
```

但 decision manifest 是「最終裁切前」寫出的裁切決策。這時 preview / edge preview 通常還沒產生，或至少還沒被驗證。

### 為什麼有問題

如果不說明，讀者可能誤會：

- `figure_decisions.json` 已經代表 preview 存在。
- `figure_decisions.json` 裡的 edge previews 已經被檢查過。
- decision manifest 同時承擔裁切決策和驗證結果。

這會模糊 candidate / decision / final manifest 的角色。

### 改寫方法

在 step 8 或 JSON 命名段補一句：

```markdown
`figure_decisions.json` 中的 `preview` 與 `edge_previews` 是預期輸出路徑，用來讓後續裁切與預覽建立有固定目標；它們不代表圖片已通過視覺驗證。
```

在 `figures.json` 裡，這些同名路徑才代表已產生並被納入 final verification 的成果。

---

## K. 邊界決策樹只放 workflow 時，標題感要更明確

### 現況

style issues 目前建議：邊界決策樹只 inline 在 step 13-14，規則段刪除重複內容。這方向合理，但 step 13 / 14 如果只是一般流程編號，讀者回頭找「邊界決策」時可能不夠快。

### 為什麼有問題

邊界決策樹雖然只在 step 13-14 執行，但它仍有獨立 concept-identity。讀者和 agent 之後很可能會說「回去看邊界決策那段」。

如果完全沒有固定詞，step 13-14 會被淹沒在 workflow 裡。

### 改寫方法

在 step 13 開頭保留固定詞：

```markdown
13. 執行邊界決策。先看 crop 形態，再讀四個邊界預覽。...
```

或在 step 12-14 之前加一個輕量小標：

```markdown
裁切驗證與邊界決策：
12. ...
13. ...
14. ...
```

不一定要把它升格成規則段；只要讓「邊界決策」這個概念在流程段裡容易被找到即可。

---

## L. 流程 19 步沒分階段，novice 讀者沒有 mental anchor

### 現況

整份 `figure_extractor.md` 流程從 step 1 到 step 19，平鋪在一個 `## 工作流程` 標題下，沒有 sub-heading 分段。

```markdown
## 工作流程

1. ...（page image render）
2. ...（page preview render）
3. ...（產 figure_candidates.json）
4. ...（產 source_regions）
...
19. ...（worker 回報）
```

### 為什麼有問題

19 個 step 一氣讀下來，novice 讀者沒辦法在腦中建立「我現在大概在哪個階段」的感覺。讀完只會記得「好像有很多步驟」，但答不出「裁切是 step 幾、驗證是 step 幾」。

對照 `rewrite_goals.md`：

- 「**人可以順著讀，不需要在腦中重新整理流程**」——19 步無分組需要讀者自己整理。
- 「**流程步驟具體，但不要把固定短枚舉拆成過長的 checklist**」——19 步單純編號就是一個沒分組的 checklist。

K 問題（邊界決策的標題感）其實是這個問題的局部表現：邊界決策只是其中一個 phase，整份流程的所有 phase 都需要標題。

### 改寫方法

用 `###` 把 19 步分成 4-5 個 phase。範例分組：

```markdown
## 工作流程

### 準備頁面圖片
1. 若 `shared/pages/page_N.png` 不存在，呼叫 render helper⋯⋯
2. 若 `shared/previews/page_N_preview.png` 不存在，呼叫 preview helper⋯⋯

### 候選偵測與索引
3. 產生 `figure_candidates.json`⋯⋯
4. 依需要建立 source region⋯⋯
5. 讀取候選與 preview，判斷哪些進入 index⋯⋯
6. 撰寫 `figure_index.json`⋯⋯
7. 對 indexed figures 做 source context 檢查⋯⋯

### 裁切決策與執行
8. 撰寫 `figure_decisions.json`⋯⋯
9. 從頁面圖片產生最終裁切圖片⋯⋯
10. 為每張裁切圖片建立預覽⋯⋯
11. 建立四個邊界預覽⋯⋯

### 視覺驗證與邊界決策
12. 讀取每張預覽最終裁切圖片與其四個邊界預覽⋯⋯
13. 執行邊界決策⋯⋯
14. ⋯⋯

### 最終 manifest 與 self-check
15. 撰寫 `figures.json`⋯⋯
16. ⋯⋯
17. 執行 mechanical self-check⋯⋯
18. 空範圍處理⋯⋯
19. 回報 worker 結果⋯⋯
```

5 個 phase 標題讓讀者一眼看到「啊，這份 pipeline 大致分這幾個階段」，每階段內部仍是線性編號。這同時解決了 K 問題（邊界決策有了「視覺驗證與邊界決策」這個 phase 名稱）。

---

## M. `figure_index.json` 還有 figure 層 `pages` 沒被解釋

### 現況

JSON example 中：
- `figure_candidates.json` 每 page object 有 `page` 欄位（line 147、207）
- `figure_index.json` 每個 figure 有 `pages` 欄位（line 295、305）
- `figure_decisions.json` 和 `figures.json` 的 figure 層**沒有** `pages` 欄位（按 A1 plan 已移除）

讀者看 4 個 JSON 對照時會困惑：「為什麼 `figure_index.json` 還有 `pages`，但 `figure_decisions.json` 沒有？」

「## JSON 命名與 enum」line 103 有解釋：

> `figure_index.json` 可以保留 `pages`，因為它只是先列出有哪些正式 figure，還沒有 `crop_units`。

但這條規則放在「替代鍵黑名單」附近的位置，讀者看 JSON example 卡住時不一定會翻到 line 103。

### 為什麼有問題

對照 `rewrite_goals.md`「**規則要回答讀者真正會卡住的問題**」：

讀者最會卡住的時刻是看 JSON example、發現命名不一致的當下。規則在 line 103 雖然存在，但**讀者預期會在 example 旁邊找說明**。

### 改寫方法

兩個選項：

**選項 A（簡單）**：在 `figure_index.json` example 上方加一行註解：

```markdown
### figure_index.json

> 註：`figure_index.json` 的 figure 層保留 `pages` 欄位，因為這個階段還沒有 `crop_units`。到了 `figure_decisions.json` 和 `figures.json`，頁碼改由 `crop_units[].page` 表達。

```json
{
  ...
}
```
```

**選項 B（更完整）**：把這條規則放進 H 問題建議的「### 版本與欄位命名」sub-section 開頭，明示「pages 在不同階段的處理不同」。

建議 A——讀者卡住的點就在 example 旁邊，註解在最近的位置最好。

---

## N. 開頭「目標」段提到 mode 但沒解釋

### 現況

line 19：

> 邊界：此 agent 只負責 initial extraction，不負責 reviewer、repair、canonical merge、validator，**也不處理 repair / continue / batch mode**，不修改來源 PDF。

連續列了七個 agent 不做的事，包括「repair / continue / batch mode」這三個 mode。novice 讀者第一次看到這份文件，會困惑這三個 mode 是什麼概念。

### 為什麼有問題

對照 `rewrite_goals.md`「**完全沒看過這個 project 的朋友讀完規則就知道怎麼寫**」：

「不處理 X」這種否定式邊界宣告，**只有讀者知道 X 是什麼**才有意義。novice 讀者連 mode 是什麼概念都不知道，看到「不處理 repair mode」反而會被新名詞干擾。

### 改寫方法

兩個選項：

**選項 A（簡短括弧）**：直接補一句 navigation：

```markdown
邊界：此 agent 只負責 initial extraction，不負責 reviewer、repair、canonical merge、validator，也不處理 repair / continue / batch mode（這些 mode 由其他 agent 或 orchestrator 處理），不修改來源 PDF。
```

**選項 B（拆兩條 bullets）**：把責任邊界和 mode 拆開：

```markdown
邊界：
- 此 agent 只負責 initial extraction，不負責 reviewer、repair、canonical merge、validator，也不修改來源 PDF。
- 不處理 repair / continue / batch mode；這些 mode 由其他 agent 或 orchestrator 觸發新的 extraction run，本 agent 不需要感知。
```

建議 B——既解釋了 mode，也順帶說明「為什麼 extractor 不感知這些 mode」（呼應 E3 plan 的決策）。

---

## O. 「跨頁與多區域 figure」段混雜多概念，部分內容該搬出去

### 現況

「## 跨頁與多區域 figure」段（line 592-602）9 條 bullets 混了三類概念：

| 內容 | 屬於什麼類別 |
|---|---|
| 多 panel figure 視為同一張 figure | 概念規則（本段核心） |
| 跨頁 figure / 同頁多區域處理 | 概念規則（本段核心） |
| 「不要為單一矩形而切非 figure」反例 | 概念規則（本段核心） |
| `crop_units[]` 結構與必填欄位 | JSON schema（屬於 JSON 命名段） |
| `crop_units` 必須同時在 decisions 和 figures、共用 `figure_id` | D1 一致性規則（cross-cutting） |
| 不一致時的修正流程 | D1 一致性規則（cross-cutting） |
| `figure_id` filename-safe + 不含空格 | JSON 命名規則（cross-cutting） |
| `<figure_id>.png` / `<figure_id>_part_<N>.png` 命名 | JSON 命名規則（cross-cutting） |

後三類（共 5 條 bullets）其實**所有 figure 都適用**，不是「跨頁與多區域」獨有。

### 為什麼有問題

對照 `rewrite_goals.md`：

- 「**按讀者真正會卡住的點分組**」——目前一節塞三類概念，讀者讀完不清楚這節在管什麼。
- 「**名詞穩定，同一個 artifact 不要在不同段落換不同名字**」——`figure_id` 命名規則出現在這節，但 JSON 命名段沒對應條目，schema 規則被分散在兩處。
- 「**一個規則只放一個位置**」（抽取原則）——`crop_units` 一致性規則跟 D1 重疊。

按抽取原則：
- `figure_id` 命名規則 → cross-cutting（條件 1）→ JSON 命名段
- `crop_units` 一致性 → cross-cutting（條件 1）→ 已在 JSON 命名段（line 104 等）
- 多 panel / 跨頁 / 多區域處理 → 概念規則，保留本段

### 改寫方法

把「跨頁與多區域 figure」段**精簡為純概念規則**，schema / 命名規則搬到該屬於的位置：

**保留在本段的內容**：

```markdown
## 跨頁與多區域 figure

- 多 panel figure 預設視為同一張 figure，除非原文明確標成不同 figures。
- 跨頁 figure 可以有多個 `crop_units`，並用同一個 `figure_id` 關聯。
- 同頁多區域 figure 也可以有多個 `crop_units`。
- 不要為了做成單一矩形，而把中間正文或其他非 figure 內容一起裁進來。
```

精簡後本段只剩 4 條 bullets，純粹講「同一 figure 怎麼用多個 crop」的概念。

**搬到「## JSON 命名與 enum」段**（按 H 問題建議的 sub-section 分組，放在「### 版本與欄位命名」）：

- `figure_id` 必須 filename-safe，不含空格，例如 `Figure_1`、`Figure_2`、`Extended_Data_Figure_1`。
- 單一 crop 圖片使用 `<figure_id>.png`；多個 crop 統一使用 `<figure_id>_part_<N>.png`。頁碼與位置由 `crop_units[].page` 和 `crop_units[].role` 表達，不塞進檔名。

**刪除（D1 已涵蓋）**：

- 「每個 final crop 都寫成 `crop_units[]` 裡的一個 object⋯⋯」——這條已經由 step 8（撰寫 `figure_decisions.json`）和 JSON 命名段共同涵蓋。
- 「`crop_units` 必須同時出現在 decisions 和 figures、共用 `figure_id`」+「不一致時回 decisions 修」——這是 D1 的核心，inline 在 step 8 / step 15 附近，本段不重述。

---

## P. 章節間 cross-reference 與輕度重疊

### 現況

四處跨節 cross-reference 缺失或概念重疊：

1. **「# 目標」段輸出列表 vs 「## 圖片檔案」段角色介紹**——line 7-16 列了輸出 artifacts，line 533-548 又介紹圖片角色。兩處概念部分重疊（都列 source_regions、edges、previews、final crop），角度不同（manifest 列表 vs 角色說明），但沒 cross-ref 連結。
2. **「## 圖片檔案」段 vs 「## 來源區域（source_regions）」段**——前者談圖片實體角色、後者談 JSON schema，但都會提到「裁切區域來源圖片」，讀者可能困惑兩段是不是同一回事。
3. **E + H 沒明示 cross-ref**——E 說「`expected_panels` 搬到 JSON 命名段」、H 說「JSON 命名段拆 sub-sections」，但沒說 `expected_panels` 該放在 H 拆出來的哪個 sub-section。
4. **M 選項 B 沒展開**——M 提到「把 `figure_index.json` 的 `pages` 規則放進 H 的「### 版本與欄位命名」sub-section 開頭」，但沒給具體範例。

### 為什麼有問題

對照 `rewrite_goals.md`：

- 「**人可以順著讀，不需要在腦中重新整理流程**」——cross-ref 缺失時，讀者卡在「我是不是漏看了什麼？」。
- 「**名詞穩定，同一個 artifact 不要在不同段落換不同名字**」——重疊概念若沒明示分工，會造成「這兩處是同一回事還是不同？」的困惑。
- 實作 B、E、H、M 時，這些 cross-ref 缺失會導致實作者重新猜測歸屬，浪費精力或踩雷。

### 改寫方法

#### 1. 「# 目標」輸出列表 → 加 navigation 指針

在輸出列表結尾加一句：

```markdown
- 目標：⋯⋯
- 邊界：⋯⋯

每個圖片 artifact 的角色與生成關係見「## 圖片檔案」。
```

讓讀者知道後面有更詳細的章節，不是重複。

#### 2. 圖片檔案 vs 來源區域 → 兩段互相 cross-ref

「## 圖片檔案」開頭加一句：

```markdown
本節介紹每種圖片的角色；對應的 JSON schema 欄位見「## 來源區域」（`source_regions`）與其他規則段。
```

「## 來源區域（source_regions）」開頭加一句：

```markdown
本節定義 `source_regions` 在 `figure_candidates.json` 的 schema；對應的圖片實體角色見「## 圖片檔案」。
```

#### 3. E + H 歸屬 → 明示 `expected_panels` 的 sub-section 位置

實作 H 時，在「### 其他欄位規則」sub-section 內包含 `expected_panels`（跟 `crop_hint_px` / `crop_px` / `role` 一起列）。建議在 E 問題或 H 問題的改寫範例補一行確認這點。

#### 4. M 選項 B 具體範例

如果採選項 B（不在 example 上方加註解、改在 JSON 命名段強化說明），具體範例：

```markdown
### 版本與欄位命名

⋯（既有內容）⋯

`pages` 欄位在不同階段的處理不同：
- `figure_candidates.json`：每個 page object 有 `page`（單數）。
- `figure_index.json`：figure 物件可以有 `pages: [...]`，因為此階段還沒有 `crop_units`。
- `figure_decisions.json` 和 `figures.json`：figure 物件**不寫** `pages`，頁碼由 `crop_units[].page` 表達。
```

這條規則放在「版本與欄位命名」最合適，讓讀者看 JSON example 卡住時能快速找到完整解釋。

---

## 修改順序建議的補強

A-N 原本的修改順序在 D 後面已經給出，O 和 P 屬於後期整理：

- **O**（跨頁與多區域 figure 段精簡）：在做完 H（JSON 命名段拆 sub-sections）之後做，因為 O 的部分內容要搬進 H 拆出來的 sub-section。
- **P**（cross-reference 補強）：放在最後做，作為文件清整的收尾。前面 A-O 的修改完成後，cross-ref 缺失的位置會更明顯，這時候補最有效。

A-P 完整順序建議：

1. A（拆視覺驗證段）+ E（搬 `expected_panels`）+ B（消除流程/規則重複）的「邊界決策樹」項
2. C（中文化 section title）
3. D（拆 step 1/2/4）
4. F（開頭命名舊版）+ G（step 8 改寫）+ N（mode 解釋）
5. L（流程分階段）+ K（邊界決策標題感被 L 吸收）
6. M（figure_index.json pages 不一致）
7. H（JSON 命名段拆 sub-sections）
8. O（跨頁與多區域 figure 段精簡，內容搬進 H 拆出來的 sub-section）
9. I（evidence_read 跨階段關係說明）+ J（decision preview 是預期路徑說明）
10. B 剩餘三項（self-check、`_preview`、derived field）
11. P（cross-reference 補強，全文清整）
