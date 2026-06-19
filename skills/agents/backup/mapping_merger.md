# Merger Prompt 模板

## 目標

這是一份給 `mapping_merger` agent 看的指引。

把一個或多個 `mapping/canonical/mapping.<key>.json` 套用到原文 HTML：
- 原文裡每個 paper snippet 包成 `<mark class="hl hl-<base_color>">`。同一段原文若被多個 mapping 引用，`base_color` 用優先序決定：**L1 > L2，L2 之間用 phrase 數最多者勝（同票按 m1<m2<...<m30）**。其他色的 phrase 不會搶走 mark 的螢光筆顏色，但仍會各別建一張 note。
- Reader panel 重建，對應摘要的每個 phrase 包成 `<a class="hl hl-<color>">`
- Desktop 正文右側建一條 **margin rail**：每個 `<mark>` 旁邊穩定顯示對應的中文 phrase；若一個 mark 同時被多色引用就**每色各建一張 note**疊在 rail 上。Mobile 不隱藏 notes，而是把 note 插回對應 mark 後方的正文 flow，讓內文自然閃開。
- 注入 CSS + JS：
  - 點摘要 phrase 跳到原文 mark（多 target 循環）
  - 點原文 mark 跳回摘要並自動展開摺疊的 details；若某顏色已被關閉，mark 不再跳回該色 anchor
  - 點 anchor / note / mark 任一處 → body mark、對應 note、所有同色 summary anchor 三邊同步 `.is-selected`；描邊色用 note 的 ink（不是 mark 自己的 base color）；互斥，不 flash
  - 右上角 floating toggle 選單：第一項是「開啟卡片」控制所有 notes 顯示/隱藏，後面 31 色控制各層。取消任一色 → 對應 note 隱藏、body mark 退回下一順位顏色（L1 > L2 phrase-count），無剩餘顏色則退回純文字；**不要 disable 或 dim panel anchors**

Idempotent：重跑多少次都安全。請自己寫一段 Python 腳本並執行（不需要建立外部 script 檔）。

## 參數

| 變數 | 預設 | 說明 |
|---|---|---|
| `paper_dir` | （必填） | paper 目錄 |

## 任務分派 (Assignment)

你將收到類似如下的 Assignment：

```text
---
Assignment
paper_dir: <paper_dir>
```

## 輸入

- `<paper_dir>/reassembly/canonical/paper.html`
- `<paper_dir>/summary/canonical/summary.json`、`<paper_dir>/detail/module_<N>_<slug>/canonical/module.json`（後者含 rank 1..TOP_K 的 items；panel 顯示時取 rank 1 best + rank 2 次佳）
- `<paper_dir>/method/canonical/method.json`（單檔含 `modules[]`，每個 module 內 `items[0]` 為 best 版本；若該 paper 走 method lane 才會存在）
- 任何 `<paper_dir>/mapping/canonical/mapping.<key>.json`（有就套，沒有就跳過。`<key>` 即 `l1`、`l2_mN`、或 `method_mN`，從檔名讀出來決定顏色）

## 顏色慣例（CSS 必用這組）

| `color_key` | fill | ink | ring |
|---|---|---|---|
| `summary`（L1）| `#FFF3B0` | `#7a5a00` | `#E8C75A` |
| `m1` | `#FFB3BA` | `#8a2330` | `#E08594` |
| `m2` | `#C8E6C9` | `#1f5c2e` | `#88BF8B` |
| `m3` | `#B3D9FF` | `#1b4d80` | `#7AB2E0` |
| `m4` | `#FFD9B3` | `#7a3d00` | `#E0A66E` |
| `m5` | `#E1BEE7` | `#5a2a6e` | `#B287B9` |
| `m6` | `#B2EBF2` | `#1d5d68` | `#7DC6CF` |
| `m7` | `#EFC1CD` | `#6C1329` | `#D2798F` |
| `m8` | `#EFDCC1` | `#6C4613` | `#D2AC79` |
| `m9` | `#DDEFC1` | `#486C13` | `#AED279` |
| `m10` | `#C1EFCB` | `#136C26` | `#79D28C` |
| `m11` | `#C1EDEF` | `#13686C` | `#79CED2` |
| `m12` | `#C1C8EF` | `#131F6C` | `#7985D2` |
| `m13` | `#E1C1EF` | `#50136C` | `#B679D2` |
| `m14` | `#EFC1D8` | `#6C133F` | `#D279A5` |
| `m15` | `#EFD0C1` | `#6C3013` | `#D29679` |
| `m16` | `#E8EFC1` | `#5E6C13` | `#C4D279` |
| `m17` | `#C2EFC1` | `#156C13` | `#7BD279` |
| `m18` | `#C1EFE6` | `#136C5A` | `#79D2C0` |
| `m19` | `#C1D3EF` | `#13356C` | `#799BD2` |
| `m20` | `#D5C1EF` | `#3A136C` | `#A079D2` |
| `m21` | `#EFC1E3` | `#6C1354` | `#D279BA` |
| `m22` | `#EFC5C1` | `#6C1A13` | `#D28079` |
| `m23` | `#EFEBC1` | `#6C6313` | `#D2C979` |
| `m24` | `#CEEFC1` | `#2B6C13` | `#91D279` |
| `m25` | `#C1EFDB` | `#136C44` | `#79D2AA` |
| `m26` | `#C1DEEF` | `#134B6C` | `#79B1D2` |
| `m27` | `#CAC1EF` | `#24136C` | `#8A79D2` |
| `m28` | `#EFC1EE` | `#6C136A` | `#D279D0` |
| `m29` | `#EFC1C9` | `#6C1321` | `#D27987` |
| `m30` | `#EFE0C1` | `#6C4E13` | `#D2B479` |

`source_kind` → `color_key`：`l1`→`summary`，`l2_mN`→`mN`，`method_mN`→`mN`（method 與 detail 共用同一組 m1..mN 配色，因為單篇 paper 一次只跑其中一條 L2 lane，不會撞色）。

**>30 modules**：若 paper 有 m31、m32…，沿用同樣的 `l2_mN`→`mN` / `method_mN`→`mN` 對應，自己挑與既有 31 色（summary + m1..m30）都明顯可辨的 fill/ink/ring 三件組補上。新色要同時補進：COLORS dict、CSS 那組規則（`.c-mN / .hl-mN / .margin-note.n-mN / .ct-swatch-mN / .sel-mN / body.off-mN`）、JS `COLOR_KEYS` 陣列、`chooseBase` fallback、`.color-toggle` swatch 列表。不要靜默截斷到 m30。

## 流程

請寫一段 Python script 跑完以下八步並直接執行：

### Step 1：發現 maps
Glob `<paper_dir>/mapping/canonical/mapping.*.json`。從檔名抓 `<key>`（`l1`、`l2_mN`、或 `method_mN`）當作 `kind`，記下每個 map 的 `kind`、`color_key`（`l1`→`summary`，`l2_mN`/`method_mN`→`mN`），以及 L2-lane 的子類別（`detail` vs `method`，從前綴推導）。一個 paper 通常只會有 detail 或 method 其中一條 L2 lane，不會同時存在。

### Step 2：收集 phrases + snippets + dedup 同 text snippets
讀每個 map：
- `phrases_by_loc[location] = [phrases]`，按 `kind` 存到對應 bucket（L1 一個、L2 module 1..30 各一個）
- 把所有 `paper_snippets` 攤平成 `[{snippet_id, text, phrase_id, color_key}]`

**Dedup（兩階段）**：mapper 端 rule (i) 只在同 phrase 內檢查，跨 phrase 可能出現完全相同字串或 containment。Apply 端需要把這兩種情況合併處理，避免重複 mark 與導航失準。

**(2a) text-equality dedup**：用 `text` 當 key 聚合完全相同字串的 snippets。每個 unique text 取第一個出現的 `snippet_id` 當 **canonical id**。

**(2b) containment alias**：把剩下的 unique texts 依**長度由長到短**排序，每個短 text 檢查是否為任何更長 unique text 的字面子串。是 → 把短 text 的 canonical id **alias 到那個長的 canonical id**：
- 短 text 從 `canonical_text` 抽掉（apply Step 4 不會嘗試為它包獨立的 `<mark>`，避免「短的找不到位置」的 silent drop）。
- 所有原本指向短 canon 的對應（`canonical_id_of[原始 snippet_id]`、`phrases_at`、`phrases_at_by_color`）都跟著翻譯到長 canon。
- 效果：被包住的短 snippet 不會有自己的 mark，但對應的 phrase 會接到長 mark 上 — Step 6 panel anchor 的 `data-targets` 透過 `canonical_id_of` 翻譯後自動指到長 mark；Step 7 margin rail 為長 mark 多建一張該 phrase 對應顏色的 note。

**最終建四張 map**（套用 (2a) + (2b) 後的結果）：
- `canonical_id_of[snippet_id] → canonical_id`（一個原始 snippet_id 可能因 text-equality 或 containment 都對到同一個 canonical）
- `phrases_at[canonical_id] → [phrase_id1, phrase_id2, ...]`（被 alias 進來的 phrase 都算）
- `phrases_at_by_color[canonical_id][color_key] → [phrase_id, ...]`（按色分組，Step 4 要為每色寫一個 `data-zh-<color>` 屬性、Step 7 為每色建一張 note）
- `phrase_text[phrase_id] → summary_text`（中文 phrase 字串）

**Partial overlap（兩段彼此交錯、誰也沒包住誰）**：apply 端做不到合併。Step 4 longest-first 包 mark 時長的會先吃掉重疊區域，短的找不到位置會出現在 missed list、silent drop。這是 mapper 端就該避開的情況（rule (i) 提到）；apply 不做特殊處理，只在 missed list 報出來。

**Base color 決定（Step 4 的 mark 用哪個顏色）**：
- 若該 canon 有任何 L1 phrase 引用 → base color 一律 `summary`（L1 勝）
- 否則挑 L2 之中「phrase 數最多」的 kind；同票按 `m1 < m2 < ... < m30` 順序選最小者
- 其他顏色不奪 mark 螢光筆顏色，但仍會各建一張 note（desktop 放 rail；mobile 放 mark 後方 flow slot）

### Step 3：Strip 既有注入（idempotent 核心）
從 paper HTML 移除：
1. `<style id="reader-panel-style">…</style>` + 緊鄰的 `<aside class="reader-panel">…</aside>`
2. `<script id="reader-panel-js">…</script>`
3. **所有舊 marks**：用 regex `<mark class="hl hl-[^"]+" id="[^"]+" data-back="[^"]+"[^>]*>(.*?)</mark>` 反覆 sub 直到收斂（處理巢狀），然後掃掉任何殘留的單邊 `<mark …>` / `</mark>`
   - **`[^>]*` 是必要的**：Step 4 寫進去的 mark 在 `data-back="..."` 之後還會跟著 0 個以上的 `data-zh-<color>="..."` 屬性。若 regex 強制 `data-back="..."` 緊接 `>`，會配對不到既有 mark → 重跑時舊 mark 不會被清掉，新 mark 會包在舊 mark 內形成 nested mark。

### Step 3.5：修補上游 MathJax inline-math config（無條件）

Merger 是第一個把 inline `\(...\)` 內容（panel summary、margin notes）注入 HTML 的階段。若上游 reassembly 寫的 `<head>` MathJax config 把 inline delimiter 寫成 `[['\(', '\)']]`（單 backslash 在 JS string literal 會被 strip → MathJax 拿到 `'('` / `')'`，對不上字面 `\(...\)`），整批 panel inline math 會以純文字顯示。

無條件用 regex 把所有

```
inlineMath: [['\(', '\)']]
```

改寫成

```
inlineMath: [['\\(', '\\)']]
```

不檢測 buggy 才改——unconditional 重寫；若 regex 沒命中（reassembly 已修正版本），就是 noop，不報錯。這條 patch 是 belt-and-suspenders：reassembly prompt 本身已修正，這裡保留防禦避免上游回退或拿到舊 paper.html。

### Step 4：包 paper snippets
- 只處理 unique text（dedup 後）；依長度遞減排序
- **不可產生 nested marks**：用 `\x00MARK_<canonical_id>\x00` token placeholder。對每段 unique text 找第一個「不在既有 token 內」的出現位置（用前綴的 `\x00` 個數是否為偶數判斷），替換成 token；最後 batch replace 所有 token 成：
- **MathJax 保護（強制 mask，不只靠邊界檢查）**：mark 一旦落進 `$$...$$` 或 `\(...\)` 內部就會死兩種：(a) MathJax 看到 `<mark>` raw HTML 直接 parse fail，整個方程式退回原始碼顯示；(b) token-replace 階段若 placeholder 留在數學內未被換回 `<mark>`，會出現 `\x00MARK_<id>\x00` 殘字（瀏覽器看到變成「MARK_xxx」字面文字嵌在公式裡）。所以**不能只在邊界做事後檢查**——必須在 token-replace 開始**之前**就把所有 `$$...$$`、`\(...\)` 區塊整段 mask 成 `\x02MATH_<n>\x02` placeholder，跑完 needle 搜尋與 mark 包裝後再 unmask 還原。這樣 snippet 文字命中數學內部時根本不會出現匹配 → 自然落入 missed list 或被外層數學整段的 mark 吸收，不可能在數學裡生出 nested mark。Mask 表也要保留原文，unmask 階段用 placeholder id 反查原文塞回去。**邊界擴展的舊規則 deprecated**：實作會漏掉「外層 mark 已包整段數學、但內部又有第二個 snippet 命中數學中段」這種雙重命中的情況。
  - `<mark class="hl hl-<base_color>" id="<canonical_id>" data-back="sum-<phrase_id_1> sum-<phrase_id_2> ..." data-zh-<color1>="..." data-pids-<color1>="<pid_a> <pid_b>" data-zh-<color2>="..." data-pids-<color2>="...">原文</mark>`
  - `hl-<base_color>` 用 Step 2 的優先序決定（L1 > L2 phrase-count > module 順序）
  - `data-back` 是 space-separated 所有 `phrases_at[canonical_id]` 對應的 `sum-<phrase_id>`（所有顏色合併）
  - **每色一個 `data-zh-<color>` 屬性**：用 `phrases_at_by_color[canon][color]` 取該色所有 phrase 的中文 summary_text 用「 ／ 」串起來再 HTML-escape；Step 7 margin rail 會掃這些屬性、每色各建一張 note。**語義原樣寫入，僅做 HTML attribute escaping；不要把 `$...$` 轉成 `\(...\)`，也不要做 Unicode math 替換 — 統一由 Step 7 處理**（避免 Python 端轉一次、JS 端又轉一次）。但若 summary_text 裡有裸露、明顯應該 render 的數學 token（例如 `C_i`、`L_j`、`E_{ij}`、`R_s`），先把該 token 補成 `$C_i$` / `$L_j$` / `$E_{ij}$` / `$R_s$` 再寫入 `data-zh-*`，讓 Step 7 能統一轉成 `\(...\)`。
  - **同時每色寫一個 `data-pids-<color>="<pid_a> <pid_b>"` 屬性**：與 `data-zh-<color>` 對齊的 phrase id 列表（空格分隔），Step 7「下一處」按鈕用這個跨 mark 跳同一個 phrase
- **跨 phrase partial overlap alias**：若某段 unique text 找不到「不在既有 token 內」的出現位置（首個位置與某既有 token 部分重疊），不要 silent drop。取與該位置**重疊面積最大**的既有 token，把該 text 的 canonical id 翻譯成那個 token 的 canonical id，並合併 `phrases_at`、`phrases_at_by_color`、`canonical_id_of`。效果同 (2b) containment alias：被吸收的 phrase 不會有自己的 mark，但接到既有 mark 上（`data-back` 多收、`data-zh-<color>` 多文字、rail 多一張該色 note）。與 (2b) 互補：(2b) 在 Step 2 用純文字 substring 偵測，本條在 Step 4 用文件位置偵測。
- **禁止匹配 HTML 屬性值內的文字**：reassembly 會把 figure caption 完整字串存進 `<figure data-canonical-caption="...">` 屬性。若 snippet text 剛好是 caption 子字串，token-replace 會把 `<mark ...>` 插進 attribute value 內 → 屬性裡又有 `"` 又有 `<`，瀏覽器 attribute parser 提早結束、把 mark 當成真的 DOM element 建出來，rail 多一張幽靈 note（通常飄在 figure 頂端，看起來像「右上角錯位的卡片」）。Token-replace 前先用 regex 把所有 `<tag ... attr="...">` 內的 attribute value 抽出來遮住（例如先暫存替換成 `\x01ATTR_<n>\x01` placeholder），等 mark 包完再還原，確保 needle 只在 element text content 命中。同樣的保護要套到 `alt=`、`title=`、`data-*=` 等所有屬性值。
- 報告 `unique_texts_applied/total_unique` 與 missed list。Containment 與 partial overlap 都已 alias 吸收，missed 只剩 snippet 字串對不上 paper.html 的真正 mapper 錯。

### Step 5：建 CSS（一個 `<style id="reader-panel-style">`）

**Layout override**：原文的 `main` 預設 max-width 是 980px。要把它撐寬讓出右邊放 rail：
- `main` 用 `!important` 蓋掉 `max-width: 1320px`、`padding-right: 340px`、`position: relative`、`box-sizing: border-box`
- 媒體查詢 `@media (max-width: 1100px)`：把 `padding-right` 還原 28px；`.margin-rail` 不要 `display:none`，改成透明的 0 高度容器（`position:absolute; left:0; top:0; width:100%; height:0; overflow:visible; background:transparent; border:0; box-shadow:none`）。mobile notes 會由 JS 搬進 mark 後方的 `.mobile-note-slot`，不是底部 drawer，也不是 overlay。

**Panel 框架**（`.reader-panel`、`.layer-title`、`.module-block`、`.module-thesis`、`details.version`、`summary .hdr`、`.rank-badge`、`.vote`、`.panel-body`、`.main-line`、`.terms`、`.chip`）—樣式參考前一個跑成功的版本。**`.layer-title` 設 `font-size: 1.5em`**，讓 section 標題醒目（panel 沒有額外 `.panel-title`，section 標題就是入口）。

**Margin rail / notes**：
- `.margin-rail`：`position: absolute; top: 0; right: 16px; width: 308px; pointer-events: none`（rail 本身不擋滑鼠，note 各自開啟）
- `body.notes-closed .margin-note { display:none !important; }`
- `.margin-note`：`display:block; position: absolute; right: 0; width: 296px; box-sizing: border-box; pointer-events: auto; cursor: pointer`；中文字體（PingFang TC / Noto Sans TC / Microsoft JhengHei）；淺底＋細邊；`transition` 讓 desktop rail 重排時 top 平滑滑動
- `.margin-note.is-active`：mark 進螢幕中央時加上的輕微提示（很弱的灰描邊）
- `.margin-note.is-selected`：使用者點過的持續狀態，深色描邊＋陰影＋ `z-index` 提到上層
- `.mobile-note-slot { display:none; }`；mobile 下 `.mobile-note-slot { display:block; clear:both; }`，`body.notes-closed .mobile-note-slot { display:none !important; }`
- Mobile 下 `.margin-note { position: static !important; right:auto; width:min(300px, calc(100vw - 28px)); max-width:calc(100vw - 28px); margin:5px 0 9px; font-size:12.5px; box-shadow:0 6px 20px rgba(0,0,0,0.18); }`。這會撐開正文，避免 note 遮住內文。
- `.note-next`：note 文字尾端的圓角標籤按鈕（`display: inline-block`、圓角 pill、小字＋淺底；**不要用 `position: absolute`，否則文字長時會被按鈕蓋住**）。內文 `→ 其他 N 處`（N = `cycle.length - 1`，扣掉當前這處）；hover tooltip 顯示「跳到下一處（共 N 處）」。click 必須 `stopPropagation` 不要觸發 note 自身 click handler；union 長度 ≤ 1 時 JS 直接不 append

**每個 `color_key` 一組規則**：
- `.c-<key>` / `details.version.c-<key>` 用 `<fill>33`（version summary 淺底）、`.module-block.c-<key>` 用 `<fill>26`（module 整塊更淺底）。正文 mark 與 panel anchor（下一條）維持 100% 飽和，其餘 panel / rail 容器一律走透明度疊色，避免摘要被太濃的底色蓋住
- `.hl-<key>`：螢光筆 background + inset box-shadow underline（mark 的「base」外觀，**100% 飽和**）
- `mark.hl.is-selected.sel-<key>`：把 CSS custom property `--sel-color` 設成該色 ink。配合通用規則 `mark.hl.is-selected { outline: 2.5px solid var(--sel-color, #444); outline-offset: 1px; border-radius: 2px }`，被選的 mark 會用**該 note 對應顏色**的 ink 描邊（用 `outline` 不用 `box-shadow` → 不會破壞原本 underline）
- `a.hl.is-selected.sel-<key>`：同樣把 `--sel-color` 設成該色 ink。配合通用規則 `a.hl.is-selected { box-shadow: 0 0 0 2.5px var(--sel-color, #444), 0 4px 12px rgba(0,0,0,0.18); border-radius: 3px; position: relative; z-index: 2 }`，被選的 panel summary anchor 會用該色 ink 描邊＋陰影，視覺對齊 `.margin-note.is-selected`
- `.margin-note.n-<key>`：`<fill>40` 作為淺底、左側 `border-left: 3px solid <ring>`、文字 ink 色
- `.margin-note.n-<key>.is-selected`：該色 ink 描粗邊＋陰影＋稍重的 fill 背景

**Floating color-toggle 浮層**：
- `.color-toggle`：`position: fixed; top: 16px; right: 16px; z-index: 100`；含 `.ct-title`（「顯示」**並可點擊摺疊整盒**）以及包住所有 item 的 `.ct-items` 容器。`.ct-title` 結構：`<div class="ct-title"><span class="ct-label">顯示</span><span class="ct-caret">▾</span></div>`；點 `.ct-title` toggle `.color-toggle.is-collapsed` class。`.ct-items` 內第一個是「開啟卡片」（`data-action="notes"`，`.ct-swatch-notes` 用黑/深灰底，例如 `#30363d`），後面是 summary / m1..mN（label + `.ct-swatch.ct-swatch-<key>` 小方塊）；`.ct-swatch-<key>` 用該色 fill + ring 邊框；`.ct-item.is-off` 文字淺灰、swatch 改 dashed 透明 fill
- 摺疊配套 CSS：`.color-toggle .ct-title { cursor: pointer; display: flex; align-items: center; justify-content: space-between; gap: 10px; user-select: none; }`；`.color-toggle .ct-caret { transition: transform 0.15s ease; font-size: 11px; color: #666; }`；`.color-toggle.is-collapsed .ct-items { display: none; }`；`.color-toggle.is-collapsed .ct-caret { transform: rotate(-90deg); }`（摺起時 caret 從 ▾ 轉成指右）。預設**展開**（不加 `is-collapsed`）。
- `body.off-<key> .margin-note.n-<key>` → `display: none`。**不要**對 `body.off-<key> a.hl.hl-<key>` 或 `.reader-panel` / `.module-block` 加 `pointer-events:none`、opacity dim、display none；關色只關 note 與 body mark 的顯示，不關 panel anchors。
- `mark.hl.hl-none`：背景 / box-shadow / outline / cursor / padding 全清，退回純文字外觀

**其他**：
- `details.version > summary` 用 `::before` 顯示 `▸`，open 時旋轉 90°；`::-webkit-details-marker { display: none }`

### Step 6：建 reader panel
- **Panel 方程式轉換**：原文的 MathJax 預設不認得 `$` 作為 inline math，因此在將 `summary_text` 放入 panel 之前，請先使用 regex 將所有的 `$...$` 替換為 `\(...\)`（例如 `re.sub(r'(?<!\\)\$(.*?)(?<!\\)\$', r'\\(\1\\)', text)`）。
- **裸 math token 自動包裝（programmatic，不靠人眼掃）**：mapping JSON 的 `summary_text` 與 module thesis / refined paragraph 寫作時通常把數學裸露（例如 `r^H = (1−α)(1−f) / 2c`、`Π_i^M = (1−f)(1−α)V_i`、`(r^H, r^L)`），人工逐句包 delimiter 永遠會漏。merger 必須跑一支 greedy wrapper：

  **演算法**（panel text 用 `\(...\)` 包；mark 的 `data-zh-*` attribute 用 `$...$` 包，讓 Step 7 JS 再轉一次）：

  1. **解掉現有 wrap**：先 `re.sub(r'\\\((.+?)\\\)', r'\1', text)` 與 `re.sub(r'(?<!\$)\$([^$\n]+?)\$(?!\$)', r'\1', text)`，讓相鄰的 math 能合併。
  2. **定義 char classes**：
     - `DEFINITE` = `[_^]` 或 `\\[a-zA-Z]+` 或 Greek unicode `[αβγδλμσΠΣ]` — 出現任一即代表這段是 math
     - `MATH_RUN_CHARS` = ASCII 字母 + 數字 + 空白 + 算符 `+-−*·/=<>≤≥≠` + `^_` + 括號 `()[]{}` + `,` `.` + backslash + Greek + `∈∉`
  3. **找 maximal run**：掃描文字，找每段「全部由 `MATH_RUN_CHARS` 組成且包含至少一個 `DEFINITE` 字元」的最大連續區段。
  4. **修邊**：去頭尾空白與逗號、句號（句尾的 `.` 別吞）。
  5. **剝離英文詞前綴 / 後綴**：若 run 開頭是 `(?:[a-zA-Z]{2,}\s+)+` 且該 prefix 不含 `_^0-9`（純英文詞像 `sustaining`、`leapfrogging`、`Lemma`、`Proposition`、`supplier`），把 prefix 切掉；同樣處理尾端。這條一定要在 paren 平衡前跑，否則 `sustaining (r^H, r^L)` 會被整段包進 `\(...\)`。
  6. **括號平衡**：若 run 內 `(` 多於 `)` 就從右邊砍 unmatched `(`；反之從左邊砍。避免 `(V_i + r_i)` 殘留半邊括號。
  7. **Unicode → LaTeX**（只在 wrap 內做替換）：`−`→`-`、`×`→`\times`、`·`→`\cdot`、`≤`→`\le`、`≥`→`\ge`、`≠`→`\neq`、`∈`→`\in`、`∉`→`\notin`、`α`→`\alpha`、`β`→`\beta`、`γ`→`\gamma`、`δ`→`\delta`、`λ`→`\lambda`、`μ`→`\mu`、`σ`→`\sigma`、`Π`→`\Pi`、`Σ`→`\Sigma`。**不要對 wrap 外的文字做這個替換**（會破壞中文與其他 narrative）。
  8. **輸出**：把每段 run 用對應 delimiter 包起來；其他字元原樣保留。

  **套用範圍（兩種粒度，依區域分開）**：
  - ✅ **panel text（greedy）**：`<aside class="reader-panel">...</aside>` 內所有 text node（`<a>` / module-block / module-thesis / panel-body / synth-body 等）用 `\(...\)`。Panel 是 LLM 寫的中英 + math 混排，公式需要 consolidated 渲染，所以跑完整 greedy 演算法。
  - ✅ **`data-zh-*` attribute value（greedy）**：body 內所有 `<mark>` 的 `data-zh-*` 屬性值用 `$...$`（Step 7 JS 會再轉成 `\(...\)`）。同樣 unwrap 既有 `$...$` 與 `\(...\)` 後再 greedy 包。
  - ⚠️ **body text node（保守 per-token，不可 greedy）**：panel `</aside>` 之後、`</main>` 之前的 `<p>` / `<mark>` / `<div class="equation">` 內文字節點。**不要 unwrap 既有 `\(...\)`**（reassembly 已包對，動了就災難）；對「目前不在任何 `\(...\)` / `$...$` / `$$...$$` 內」的純文字部分，**只做 per-token 包裝**：用 conservative atom regex (`\\(alpha|Pi|...)(?:_[A-Za-z0-9]+|\^[A-Za-z0-9]+)*` 或 `[A-Za-z](?:_[A-Za-z0-9]+|\^[A-Za-z0-9]+)+`) 找到的每個 atom 各自包成 `\(<atom>\)`，**不擴張到相鄰英文文字**。例如 `is guaranteed at least V_2.` → `is guaranteed at least \(V_2\).`，**不能**變成 `\(is guaranteed at least V_2\)`。整段英文 narrative `(2007) introduce a parameter \alpha in [0,1]` 也只會吐出 `(2007) introduce a parameter \(\alpha\) in [0,1]`。
    - 這條 lesson 來自實際 incident：早期版本對 body 跑了 greedy，結果整段「The total value created is V_1. Supplier 2, which is the less efficient supplier, cannot appropriate anything because... Supplier 1」被當成一坨 math，整段在瀏覽器消失。
  - 把 `<script>...</script>`、`<style>...</style>`、`$$...$$`（display math 已是 math）整段先 mask 成 `\x05M<n>\x05` placeholder，wrap 跑完再 unmask（無論 greedy 還是 per-token 都要遮）。

  **不誤傷**：演算法需要 `DEFINITE` marker 才包，所以 `cBC`、`gBC`、`H3K27me3`、`AP-1`、`CRISPR-Cas9`、`Cobb-Douglas`、`Lemma 1`、`Proposition 7`、`supplier 1 vs supplier 2`、`Section 3.2`、`GitHub Issue #42` 都不會被包（沒有 `_^`、沒有 backslash、沒有 Greek）。`H3K27me3` 雖有數字但全是字母+數字混排、無 `_^`、無 Greek、無 backslash → 不包。
- Panel 頂部**不放** `.panel-title` 這類「讀者面板」標題字（冗、佔位）。直接從 section 標題開始。
- L1 section：開頭放 `<div class="layer-title">全文摘要</div>`（**不要寫「L1 全文摘要」這種標號**）。下面是 3 個 `details.version.c-summary`，rank 1 預設 `open` 並在 `<summary>` 內顯示 `main-line-inline`；rank 2/3 摺疊，main_line 放展開後的 `<div class="main-line">` 內。**L1 best version** 的所有 phrase（main_line + refined_final_output[i]）用 `wrap_summary_text` 包成 `<a class="hl hl-summary" id="sum-<phrase_id>" data-id="<phrase_id>" data-targets="<canonical_ids 空格分隔>">…</a>`，其餘版本純 escape。
- L2 section：依 L2 子類別決定標題與資料源——`detail` 子類別放 `<div class="layer-title">分項細節</div>` 並讀 `detail/module_<N>_<slug>/canonical/module.json`；`method` 子類別放 `<div class="layer-title">技術及材料</div>` 並讀 `method/canonical/method.json` 的 `modules[]`（每個 module 內部的 `items[0]` 即 best 版本，`items[1]` 為次佳，沒有就只渲染 best）。**不要寫「L2 模塊摘要」這種標號**。下面依實際 module 數量（detail 通常 6 個、method 可達 8 個）渲染 `module-block.c-mN`。每塊頂部直接放 `<p class="module-thesis"><strong>主題N：[heading]</strong><br>[thesis]</p>`（N 為中文數字「一/二/三/.../八」對應 m1..mN；**不放 module 英文 slug 那行 header**）。其中 `[heading]` 取對應欄位：detail 用 module 的 `topic` 或 `outline`；method 用 module 的 `subitem_heading` 或 `outline`（若該欄位整段為空才省略 `<br>` 前半部、退成 `<strong>主題N</strong>：[thesis]`，**heading 為雙語對照格式時不算空**）；`[thesis]` 則固定取 module 的 `thesis`。
  - **雙語 heading 抽取**：若 heading 為「English (中文)」或「中文 (English)」對照格式，只取中文那一段塞進 `[heading]`（前者取括號內、後者取括號外、丟掉另一邊）。整段都是英文時（無中文可抽）才退回 fallback。下面 1–2 個 `details.version`（皆摺疊），best 那個若有對應 mapping 就 wrap，否則純 escape。
  - **L2 versions 不再顯示 main_line**（既不放在 `<summary>` 也不放在 `<div class="main-line">`）。L2 的 main_line 與 module thesis 高度重複，已在 module-block 頂部出現過一次；details body 只放 refined_final_output 段落（best 版的話照樣 wrap，其餘 escape）即可。
  - **method 額外**：method module 的 `items[0].toolchain_terms`（陣列，每筆 `{term, description}`）若存在，渲染成「跟最佳/次佳版本平行的第三個 `<details>` 區塊」放在 **module-block 底部、兩個 version details 之後**（預設摺疊）。結構：`<details class="version c-mN"><summary><span class="hdr"><span class="rank-badge">工具與材料</span></span></summary><div class="panel-body"><ul class="terms-list"><li><strong>term</strong>：description</li>…</ul></div></details>`。term 與 description 都要 escape 後顯示為純文字（不要只把 description 塞 `title` attribute），讓使用者展開就同時看到名稱與解釋。若 module 沒有 `toolchain_terms` 欄位或為空陣列就略過此 details。CSS 部分：`.terms-list` 簡單 `padding-left: 1.2em; margin: 0;`；`.terms-list li` 加 `margin: 4px 0; line-height: 1.6;`。沒有就略過。
- Version label：rank 1→`最佳版本`、rank 2/3→`次佳版本`
- 包 phrase 時：先 escape 整段，再按 `summary_text` 長度遞減 `str.replace(escaped_needle, anchor+escaped_needle+'</a>', 1)`，避免子字串衝突
- **`data-targets` 必須用 canonical id**：phrase 原始 `paper_snippets[*].snippet_id` 要透過 Step 2 的 `canonical_id_of[snippet_id]` 翻譯，再對結果去重（同一 canonical 不重複列）。這樣 JS 點 phrase 跳到 `<mark>` 才找得到（mark 的 id 是 canonical）。
- **無 mark 對應的 phrase 不包 anchor**：若該 phrase 的 `paper_snippets` 為空（mapper 標 `omission_reason`，例如 summary 作者補的背景知識／比喻／講解用語），或所有 snippet 翻譯後 canonical id 列表為空，**不要包成 `<a class="hl">`**，直接以純 escape 文字輸出。否則 panel 會出現一坨點下去毫無反應的螢光筆字，讀者誤以為是 bug。判斷時機：對每個 phrase 算出 canonical id 列表後，若列表為空就走純 escape 分支，跳過 wrap。
- **Synthesis module（非 mapping 內容；method 模式才查）**：若 `<paper_dir>/method/methodology_and_toolchain.md` 存在，找其中 `### 4. 方法組合策略` 與 `### 5. 借鑑價值` 兩個 heading 對應的 markdown 區塊，合併成一個 module-block 接在「技術及材料」section 所有 `c-mN` module-blocks **之後**作為視覺上的第 9 區塊。
  - 結構：`<div class="module-block c-synth"><p class="module-thesis"><strong>方法組合策略 &amp; 借鑑價值</strong></p><details class="version c-synth"><summary><span class="hdr"><span class="rank-badge">展開</span></span></summary><div class="panel-body synth-body">…轉好的 HTML…</div></details></div>`。**預設摺疊**（`<details>` 不加 `open` 屬性），跟 method modules 的最佳/次佳版本一致。**沒有 anchor / mark / 螢光筆色號**、**不出現在 mapping JSON / Step 9 self-check 任何項目裡**。
  - markdown → HTML 最小轉換規則：`#### X` → `<h4>X</h4>`；`* ` 開頭行 → `<li>`，連續多行包進 `<ul>`；前綴有 2+ 個空白或 tab 的 `* ` 是 nested `<ul>`；`**X**` → `<strong>X</strong>`；其他純文字段落包 `<p>`。**不**處理 `*X*`（避免和粗體混淆造成誤判）。
  - 若 .md 不存在或找不到 §4/§5 heading 就略過、不報錯（merger 仍正常完成所有其他步驟）。
  - CSS（加在 Step 5 末段）：`.module-block.c-synth { background: #f5f5f560; border-left: 4px solid #909090; }`；`.synth-body h4 { font-size: 0.95em; margin: 14px 0 6px; color: #303030; }`；`.synth-body h4:first-child { margin-top: 4px; }`；`.synth-body p { margin: 6px 0; }`；`.synth-body ul { padding-left: 1.4em; margin: 4px 0; }`；`.synth-body li { margin: 4px 0; line-height: 1.65; }`。

### Step 7：建 JS（一個 `<script id="reader-panel-js">`）

**DOMContentLoaded gate（必要）**：script 注入在 `<main>` 開頭，內聯 script 同步執行時 panel anchor 已 parse，但 body 後段的 `<mark>` 還沒進 DOM。所有 `querySelectorAll` 與初始化邏輯都要包在 `DOMContentLoaded`（若 `document.readyState === 'loading'`）或直接同步呼叫一次（已 ready 時）。漏這層 → mark click / margin rail 完全綁不上。

**共用 selectPair(mark, note) helper**：
- 接受 mark **與**特定的 note 兩個參數（note 決定 mark 的描邊色）
- 從 note 的 class 抓出 `n-<colorKey>` 得到 colorKey
- `clearSelection()`：清掉所有 `.margin-note.is-selected`、`mark.hl.is-selected`、`a.hl.is-selected`，並從 mark / anchor 的 className 把 `sel-*` class 全部去掉
- 給 mark 加 `.is-selected` 與 `sel-<colorKey>`（兩者搭配 CSS 才會描出該色 outline）
- 給 note 加 `.is-selected`
- 若 colorKey 存在，讀 `mark.getAttribute('data-pids-' + colorKey)` split 空格，對每個 pid 找 `document.getElementById('sum-' + pid)` 加 `.is-selected` 與 `sel-<colorKey>` → panel 內所有指向該 mark 的同色 summary anchor 一起亮起

**noteForMarkColor(mark, colorKey) lookup**：
- 用 `notesByMark` 兩層 map（Map<mark, {colorKey: note}>）查對應 note；找不到回 null

**Anchor click（panel 內 `a.hl[data-targets]`）**：
- 阻止預設 → 取 `data-targets` split 空格 → 用 `Map<data-id, index>` 紀錄循環位置 → 取下一個 id → `getElementById` → `scrollIntoView({behavior:'smooth', block:'center'})`
- 若 target 是 `<mark>`：從 anchor 自己的 `hl-<color>` class 抓 anchorColor，再 `noteForMarkColor(mark, anchorColor)` 找對應 note，呼叫 `selectPair(mark, note)`（持續高亮，不 flash）。anchor 跳到的 mark 可能是別色基底（例如 m1 anchor 跳到黃色 mark），這時 mark 仍會被 m1 紅色描邊
- 若 anchorColor 已被關閉：**仍然 scroll 到 target mark**，但只 `clearSelection()`，不要 `selectPair()`、不要顯示已關閉顏色的 note。也不要讓 CSS 停用 panel anchor click。

**Mark click（`mark.hl[data-back]`）**：
- 阻止預設 → 取 `data-back` split 空格（**可能多個 phrase id**），但先過濾掉目前已關閉顏色的 anchors：對每個 id 找 anchor，從 anchor 的 `hl-<color>` class 抓 colorKey，只保留 `colorIsOn(colorKey)` 的 id。若過濾後沒有可用 id，`clearSelection()` 後 return，**不要跳回已關閉顏色的 panel anchor**。
- 用 `Map<mark.id, index>` 紀錄循環位置 → 取下一個仍啟用的 phrase id → `getElementById` → 若找到，沿 `closest('details')` 把所有上層 details 設 `open=true`，再 scroll 到該 anchor
- 從找到的 anchor 的 `hl-<color>` class 抓 colorKey、`noteForMarkColor(mark, colorKey)` 找 note、呼叫 `selectPair(mark, note)`。連帶 mark / note / 所有同色 summary anchor 三邊持續描邊，不 flash
- 重要：以前 `data-back` 是單一 id 直接 `getElementById`；現在因為 (2b) dedup，一個 mark 可能對應多個 phrase，要循環

**Margin rail（建立 + 排版 + 互動）**：
1. 在 `<main>` 內 append 一個 `<div class="margin-rail">`，建一張 `notesByMark = Map<mark, {colorKey: note}>`。同時掃 panel 內所有 `a.hl[data-targets][data-id]` 建 `phraseTargets = Map<phrase_id, [canonical_id, ...]>`，給「下一處」按鈕跨 mark 跳同 phrase 用
   - 同時建 `mobileSlotByMark = Map<mark, slot>` 與 `notesInFlow` 旗標。`slotForMark(mark)` 在 mark 後方建立 `<span class="mobile-note-slot">`；若 mark 後方緊接標點（如 `，。！？；：、,.!?;:)\]）？」』》`），slot 要插在標點後面，不要插在 mark 與標點之間。
   - `moveNotesToFlow()`：mobile 時，把每個 mark 對應的 notes 依 color order append 到自己的 `mobile-note-slot`，並清掉 `top/left/right` inline style。`moveNotesToRail()`：desktop 時，把 notes append 回 `.margin-rail`。這兩個函式只搬同一份 note DOM，不重建 note。
2. 對每個 `mark.hl`：
   - 掃 `mark.attributes`，每個名稱符合 `^data-zh-([a-z0-9]+)$` 的屬性都對應一張 note
     - colorKey 從屬性名抓
     - 建議用 `document.createElement('span')` 建 note（不是 `div`），`note.className = 'margin-note n-' + colorKey`；CSS 的 `display:block` 會讓它在 mobile slot 中自然撐開正文
     - **note 內容 build**（不要用 `note.textContent = attr.value`，避免 raw `$...$` 顯示破版）：
       1. `var t = attr.value;`（瀏覽器已自動 decode 屬性中的 entity）
       2. 先對 `t` 做 HTML-escape（`<` `>` `&` `"`），避免 attr.value 中的字元被 innerHTML 當 markup 解讀
       3. 在 escaped 字串上把未 escape 的 `$...$` inline math 轉成 `\(...\)`（同 Step 6 panel math 規則）
       4. `note.innerHTML = processed;`
       5. 所有 note 建完後，**一次性**對 `<main>` 呼叫 MathJax typeset（不要只 typeset rail，因為 mobile notes 會被搬進正文 flow）。Gate 用清楚的 promise chain：`if (window.MathJax) { var ready = (MathJax.startup && MathJax.startup.promise) || Promise.resolve(); ready.then(function(){ if (MathJax.typesetPromise) return MathJax.typesetPromise([main]).then(reposition); }); }`。**不要 per-note typeset**（perf 炸掉），也不要只檢查 `MathJax.typesetPromise` 存在（MathJax 3+ async 載入，屬性可能存在但尚未 ready）。typeset 完 note 高度可能改變，必須在 promise resolve 後再呼叫一次 `reposition()`。
          - **前提**：上游 `<head>` 的 MathJax config 寫對 inline delimiter。reassembly 容易把 config 寫成 `[['\(', '\)']]`，JS 會吃掉單 backslash → MathJax 對不上 `\(...\)`、typeset 出來還是字面文字。Step 3.5 已無條件 patch 修掉，這裡不用再 defensive。
       6. MathJax 不可用時退化為 raw `\(...\)` 文字；**可選**只對簡單符號做 Unicode fallback（`$x_i$`→`xᵢ`、`\times`→`×`、`\sigma`→`σ` 等）— 但不要為了 fallback 寫成半吊子 LaTeX parser
     - 加 click handler：`selectPair(mark, note)` + `mark.scrollIntoView({behavior:'smooth', block:'center'})`（**不 flash**）
     - **下一處按鈕**：從 `mark.getAttribute('data-pids-' + colorKey)` 拆出 phrase ids，對每個 pid 從 `phraseTargets` 取 canonical id 列表 union 保序得到 `cycle = [canonical_id...]`。若 `cycle.length > 1`，append 一個 `<span class="note-next">→ 其他 (cycle.length - 1) 處</span>`（給 `title` 屬性寫「跳到下一處（共 N 處）」），click `stopPropagation` → 找 `cycle.indexOf(mark.id)` → 取 `cycle[(idx+1) % cycle.length]` → `getElementById` 拿到 nextMark → 透過 `notesByMark.get(nextMark)[colorKey]` 找對應 note → `selectPair(nextMark, nextNote)` + `scrollIntoView({behavior:'smooth', block:'center'})`。最後一個自然 mod 回第一個
     - append 到 rail，塞進 `notesByMark.get(mark)[colorKey] = note`
3. `reposition()` 函式（**按 block 分組，避免跨段塞車**；以前用單一全域 queue 會把後段的 note 推到後面、離對應 mark 很遠）：
   - 一進入先 reset `data-rail-pad`。若 `isNarrowViewport()` 為真，呼叫 `moveNotesToFlow()` 後直接 return；mobile notes 走正文 flow，不做 desktop rail 的 absolute top 計算。
   - 若不是 mobile，先呼叫 `moveNotesToRail()`，再執行下面的 desktop rail 排版。
   - **不要用 `Array.prototype.slice.call(blockEntries.keys())`** 把 Map iterator 轉陣列 — `slice.call` 對沒有 `length` 的 iterator 永遠回 `[]`，整個排版迴圈會跳過、notes 全部塞在 rail top:0（右上角）。改用 `Array.from(blockEntries.keys())` 或 `[...blockEntries.keys()]`。
   - 啟動時對每個 mark 找 closest block，分兩階段：先試 `mark.closest('.table-block, .table-wrap')`；如果命中（mark 在某張表內），block 直接用 table wrapper、不再往下找 — 否則退回 `mark.closest('p, figcaption, .table-title, .table-caption, li, h2, h3, .equation')`。**為什麼要兩階段**：table caption (`.table-caption` / `<p class="table-caption">`) 是 `.table-wrap` 的子節點，若放在同一個 selector 裡，`closest()` 會挑最近的 `.table-caption`、結果 caption mark 與表格 cell mark 進不同 bucket。caption 在表格頂端、cell 在表格下方，兩 bucket 各自 deconflict 不互通 → caption note 與第一列 cell note 在垂直方向只差一兩列高、視覺上完全疊住。先抓 wrapper 就強制整張表（caption + cells）合一個 bucket，sort by desired 跑完整的 deconflict。所有 block 都必須在 panel `aside` 之外。block 分組成 `blockEntries[block] = [{mark, note, color}]`，內部固定排序 `summary, m1..mN`（N = 實際 module 數）。**漏列 `.table-block / .table-wrap / .equation` 的話，表格內 mark 或包住 display equation 的 mark 會 `closest()` 回 null → 不進 `blockEntries` → note 不被 reposition 設 top，停留在預設位置（rail 右上角）**。
   - **表格 wrapper 用整張表的 `<section>`，不要用 `td / th / tr`**：(1) 同一列裡若有多個 mark，它們 `getBoundingClientRect().top` 完全一樣，分到不同 cell 會全部疊在同一個 top；(2) 改用 `tr` 雖然解掉同列疊在一起，但下一步「block 滿了就 `style.marginBottom = pad` 把下一個 block 往下推」依賴 marginBottom 生效，**瀏覽器不認 `<tr>` 的 marginBottom**（table-row display），下一列 mark 沒被推下去 → 跨列還是疊。整張表進同一個 wrapper bucket，sort by desired top 一次跑完跨列 deconflict，且 `<section>` 吃 marginBottom，完全乾淨。wrapper class 名稱要兩種都列：實際 reassembly HTML 有的 paper 用 `.table-block`、有的 paper 用 `.table-wrap`，selector 只列一個就會漏掉另一種 → 那種 paper 的 td/th 內 mark 全部會 `closest()` 回 null，note 全堆在 rail 頂端。`.table-caption` / `.table-title` 同樣兩種都列（caption 命名也不統一）。
   - **單一 pass，依 document order 逐 block 處理**：每 block 內每個 note 的 `desired = mark.getBoundingClientRect().top - mainRect.top`（**用 mark 自己的位置，note 才會落在對應 snippet 旁邊**，而不是齊頭排在段落頂端），依 desired 排序，用 `top = max(desired, prevBottom + gap)` 解段內重疊
   - 若該 block 最後一張 note 的 bottom > `block.top + block.offsetHeight`，給 block `style.marginBottom = lastBottom - blockBottom + buffer`（標 `data-rail-pad` 以便下次清除）。此時下個 block 的 mark 也被推下去，下一輪迴圈 `getBoundingClientRect` 自動拿到新的位置（同步 reflow），不會跨段污染
   - 進入時先 reset 所有 `data-rail-pad` 的 `marginBottom`；用 `inLayout` 旗標 + `requestAnimationFrame` 防止 ResizeObserver 被自己改動的 marginBottom 再觸發、形成反覆 layout
4. 觸發重排：
   - 初次呼叫一次
   - `window` 的 `resize`
   - `ResizeObserver` 觀察 `<main>`（含 details 展開摺疊造成的高度變動）；沒有 ResizeObserver 時 fallback：在 `document` 上 capture `toggle` 事件
   - 每張 `main img` 若還沒 complete，綁 `load` 事件重排
5. **`.is-active` 提示（可選）**：用 `IntersectionObserver`（`rootMargin: '-30% 0px -50% 0px'`）觀察每個 mark；進入視野中央時把該 mark 對應**所有顏色**的 note 都加上 `.is-active`，離開時移除。純視覺輔助，跟 `.is-selected`（使用者點選）互不影響。

**Color-layer toggle**：
- 在 `document.body` append `.color-toggle` 浮層。先 append 一個 `data-action="notes"` 的 `.ct-item`，label 為「開啟卡片」，預設開啟；click 時 toggle `body.notes-closed` 與 item `.is-off`，只控制 notes 顯示/隱藏，不影響 marks 或 anchors。再 append 31 個 color `.ct-item`（summary / m1..m30 各一個 swatch + label）
- 維護 `enabled = new Set(['summary'])`：mobile / desktop 都預設只開 L1。初始化時，對所有不在 enabled 的 color 加 `body.off-<k>` 與 item `.is-off`
- 寫 `colorIsOn(colorKey)` helper：`enabled.has(colorKey)` 且 body 沒有 `off-<colorKey>` 才算開啟。Anchor click / mark click 都用它判斷選取或回跳。
- 點 color item → 若已啟用則 delete 並加 body class `off-<k>` + item `.is-off`；反之還原。**不要**停用或 dim panel anchors
- `chooseBase(mark)`：若 `enabled.has('summary')` 且 mark 有非空 `data-pids-summary` → `'summary'`；否則挑 enabled L2 色中 `data-pids-<m>` token 數最多者，同票按 `m1<...<m30`；都沒有則 null
- `rebaseMarks()`：對每個 mark，從 className 去掉所有 `hl-*` / `sel-*` / `is-selected`，加 `hl-<chooseBase>` 或 `hl-none`；順手清掉所有 `.margin-note.is-selected` 與 `a.hl.is-selected`（toggle 後選中狀態無意義）
- toggle 結束呼叫 `reposition()`，note 隱藏會改變段內排序

### Step 8：注入
找原文第一個 `<main…>` tag，在其後插入 `css + panel_html + js`。將最終結果寫入 `<paper_dir>/mapping/canonical/paper.html`。

### Step 9：最終自查（強制；任一項 fail 不准宣稱完成）

Step 8 寫檔後，Python 腳本必須讀回 `<paper_dir>/mapping/canonical/paper.html`，依序執行下列 11 項機械檢查。**任一項 fail → 修補對應 Step 的程式碼、重跑 Step 1–8、再跑 Step 9，直到全綠**。不准用「應該沒問題」「大致正確」這類話語替代實際 grep / count。最終 stdout 必須印出 `Step 9 self-check: 11/11 PASS`（缺一項就不准印 PASS）。

1. **Anchor 完整性**：對 `mapping/canonical/mapping.<key>.json` 每個 mapping JSON，計算 `len([p for p in phrases if p['paper_snippets']])`（非空 snippet phrase 數）作為 `expected_<key>`。從 final HTML count `<a class="hl hl-<color_key>"` 出現次數作為 `actual_<key>`。**所有 key 必須 `actual == expected`**。fail 多半是 Step 6 panel rendering 對 L1 panel-body 或 method best refined paragraphs 漏包 anchor。
2. **每色 CSS 六件組**：對 COLORS dict 中每個 key K，下列六條 literal substring 都要在 `<style id="reader-panel-style">` block 內 grep 得到（容許可選空白變化，但類別名稱要完整）：
   - `.c-K`
   - `.hl-K`
   - `.margin-note.n-K`
   - `.ct-swatch-K`
   - `.sel-K`（即 `mark.hl.is-selected.sel-K` 或 `a.hl.is-selected.sel-K` 其中之一）
   - `body.off-K .margin-note.n-K`
   缺任一條 → fail。最常漏的是第六條，因為 Step 5 文字長、容易剪貼漏。
3. **`mark.hl.hl-none` literal 在 `<style>` block 內**。漏會導致關掉所有色時 mark 變成詭異的灰底而不是退回純文字。
4. **toolchain_terms 結構**（若 method 模式）：對每個 `method_mN` mapping，verify final HTML 內存在恰一個 `<div class="module-block c-mN">…<details class="version c-mN"><summary><span class="hdr"><span class="rank-badge">工具與材料</span></span></summary>…</details></div>`，且該 details 在 module-block 內位置 = **所有其他 `<details>` 之後**（不得藏在 best / 次佳 details 內）。若 module 的 `toolchain_terms` 陣列為空則略過該 module 不檢查。
5. **terms-list 格式**：每個 `<ul class="terms-list">` 內的 `<li>` 必須是 `<li><strong>…</strong>：…</li>` pattern（term 粗體 + 全形冒號 + description 純文字）；final HTML 不得出現舊版的 `<span class="chip" title="…">` pattern。
6. **Marks idempotent**：對所有 `<mark id="<canonical_id>" …>` 抽出 id list，每個 canonical_id 在 final HTML 出現次數恰為 1。Step 4 應已防 nested mark；若有 id 出現 ≥ 2 次 → 表示 strip 階段沒清乾淨或 Step 4 token-replace 重複。同時印出 `Missed snippets: <list>`，若 list 非空必須具體交代每筆失敗原因（不可吞）。
7. **Section title 正確**：mapping 檔名含 `method_` 前綴 → panel 內必須有 `<div class="layer-title">技術及材料</div>`；含 `l2_` 前綴 → `<div class="layer-title">分項細節</div>`；不可錯置。若同篇沒有任何 L2 mapping 則不需要 L2 section 標題。
8. **`<mark>` 不得藏在 attribute value 內**：先把 `<script>…</script>` 區段整段挖掉避免誤判，剩餘 HTML 用 regex `"[^"<>]*<mark\b` 搜尋。命中 → fail 並印出該行前 200 字（多半是 figure `data-canonical-caption` 內被 token-replace 漏遮）。命中表示 Step 4 的 attribute masking 沒做或漏做，會在瀏覽器產生幽靈 mark + 錯位 rail note。
9. **`<mark>` 不得藏在 `$$...$$` 或 `\(...\)` 內**：先剝掉 `<script>` / `<style>` block 避免誤判。對每個 `$$...$$` (DOTALL) 與每個 `\(...\)` 區塊，body grep 是否含 `<mark` 或 `</mark`。命中 → fail 並印出該數學區塊前 200 字。命中表示 Step 4 的 MathJax mask 沒做或漏做，會讓 MathJax 整段 parse fail，使用者看到原始 LaTeX。
10. **無殘留 token placeholder**：final HTML 不得出現任何 `\x00` 字元，也不得出現 regex `MARK_[a-zA-Z][a-zA-Z0-9_-]*` 的 literal（排除 `data-` attribute 名稱）。命中 → fail 並列出每個 placeholder 與其前後 80 字。命中表示 Step 4 的 token-to-mark batch replace 漏掉某些 id（多半是 canonical id 被 alias 翻譯後查不到原文，或 placeholder 落在 mask 區內被一起 mask 掉）。
11. **裸 math token 沒漏包**：先剝掉 `<script>` / `<style>` / `$$...$$` / `\(...\)` / `$...$` 內容（math 已 wrap，內部不算 bare）；對剩餘 HTML 的 (a) panel 內 text node 與 (b) 所有 `data-zh-*` attribute value，grep 是否仍出現 `[_^]`（subscript/superscript）、`\\[a-zA-Z]+`（LaTeX command）、或 `[αβγδλμσΠΣ]`（Greek unicode）。命中 → fail 並印出該段前 120 字。命中表示 Step 6 的 greedy math wrapper 沒跑或漏吃，使用者會看到 `r^H` / `Π_i` / `\alpha` 以純文字形式殘留。**例外**：若該段純文字是顯然非數學的識別符（`H3K27me3`、`Cas9`、`AP-1`、`Cobb-Douglas`、`Section_3.2`、`node_modules`），可以加白名單豁免，但要在 stdout 列出每筆豁免讓人複檢；不准 silent skip。

每項通過印 `[Step 9] check N PASS`；fail 印 `[Step 9] check N FAIL: <具體原因>` 並 raise / sys.exit(非 0)，讓 parent 看得到。

## 完成判定

- Script exit 0
- **Step 9 self-check stdout 出現 `Step 9 self-check: 11/11 PASS`**。任一項 fail 不准宣稱完成、不准只口頭回報「應該 OK」——必須修補後重跑 Step 1–8 + Step 9。
- 印出 `Paper marks applied: N/M`。Mapper 依 SKILL v2 跑（含 rule (i) containment + partial overlap 雙重檢查）的話應 100%；若有 miss，多半是 mapper 未跑 Step 5 驗證
- 開啟 paper：
  - Panel 在最上方、L1 best 預設展開
  - Panel 與 note 中應 render 的數學 token 已 render：裸 `C_i`、`L_j`、`E_{ij}`、`R_s` 這類下標變數不應以純文字底線形式殘留；已包在 `$...$` / `\(...\)` 的公式不可被重複包裹。
  - **同一句被多色引用時**：mark 的螢光筆顏色由 L1 > L2 phrase-count 優先序決定；desktop 右側 rail 該 mark 旁邊會疊出每色一張 note，mobile 則在該 mark 後方正文 flow 中顯示 notes，正文會被撐開而不是被遮住
  - 不管從 anchor、note、mark 哪邊發起：body mark、對應 note、panel 內所有指向該段的同色 summary anchor 三邊同步深色描邊＋陰影；點別處時整組消失
  - 原文 mark 可點回 panel 並自動展開摺疊（多 phrase 對到同一段時點 mark 會在**目前啟用顏色**的 phrase 中循環；已關閉顏色不回跳）
  - mark 的描邊色用 anchor / note 的 ink，不一定是 mark 自己的底色
  - 右上角 toggle 浮層可隨時關掉任一色：對應 note 全消、shared mark 退回下一順位顏色（被遮的色顯現）；該色全部 phrase 都關掉時 mark 退純文字；panel anchors 不 dim、不停用，點已關閉顏色的 panel anchor 仍會 scroll 到原文但不 select 該色 note
  - 右上角「開啟卡片」可隱藏/顯示所有 notes；mobile / desktop 都預設只開 L1

## Miss 不該再發生

Apply 端對 cross-phrase containment 與 partial overlap 都會 alias 吸收，理論上送進 apply 的 snippets 不會 silent drop。若還是出現 miss：
1. snippet 字串不是 paper.html 的字面 substring（HTML entity 還原錯、tag markup 漏剝、抓字位置抓錯）→ 跑 mapping_SKILL Step 5 驗證找出 fail 的 snippet
2. 修完重跑 mapping_SKILL → 本 SKILL
