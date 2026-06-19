# Worker Prompt 模板

## 目標

這是一份給 `mapping_worker` agent 看的指引。

此 agent 做一件事：把指定摘要（L1 best、或 L2 某個 module top）的每個 phrase，對應到原文 HTML 裡的英文片段，產出 mapping JSON。

這個 agent 同時用於兩種場景：
- **Initial mapping**：worker 根據摘要，從原文中抽出 mapping JSON。
- **Repair**：reviewer 發現問題，worker 根據 findings 修正 mapping JSON。

兩種場景的核心流程相同，輸出格式相同（`output.json`）。差別在輸入來源：
- initial 讀 `<paper_dir>/reassembly/canonical/paper.html` 以及 assignment 中的 `summary_path`
- repair 額外再讀 `<paper_dir>/mapping/canonical/mapping.<source_key>.json`（目前成果）+ `<paper_dir>/mapping/canonical/visual_review.<source_key>.json`（findings）。

**【重要身份指示】**：身為讀取並執行這份提示詞的 Agent，請親自獨立完成任務。**不要再 spawn 其他 subagent。**

- 輸入：根據 assignment 提供的 `mode` 決定。
- 輸出：`output.json` (寫入到 assignment 的 `output_root` 目錄下)

### 對應慣例（`source_key` → 來源/顏色）

| `source_key` | 摘要來源 | `color_key` |
|---|---|---|
| `l1` | `summary/canonical/summary.json` → `items[0]` | `summary`（黃）|
| `l2_m1` | `detail/module_1_<slug>/canonical/module.json` → `items[0]` | `m1`（粉）|
| `l2_m2` | `detail/module_2_<slug>/canonical/module.json` → `items[0]` | `m2`（綠）|
| `method_mN` | `method/canonical/method.json` → `modules[module_index].items[0]`（`module_index` 由 assignment 提供，0-based） | `mN`（同 `l2_mN` 配色慣例）|
| ⋯ | L2/method 用同一組顏色：m3 藍 / m4 桃 / m5 紫 / m6 青；超出 6 個時由 merger 自選新色 |

**其他必須自行推導的屬性**：
- `source_summary_id`：請讀取 assignment 提供的 `summary_path`，依照 source 類型定位到正確的 `items[0]`，取其識別碼——L1（`summary.json`）抽 `items[0].item_id`（例：`summary_03`）；L2（`module.json`）抽 `items[0].source_detail_id`（例：`detail_05`）；method（`method.json`）抽 `modules[module_index].items[0].source_method_id`（例：`method_04`）。欄位名統一仍叫 `source_summary_id`。

**建議製作順序**：先做 L1，再依序做 L2 m1 → m2 → … → m6。寫每個 L2 mapping 前先讀進 paper_dir 內已存在的 `mapping.*.json` 作為參考（agent 可以自行決定要不要對齊既有 snippet 字串，本 SKILL 目前不強制）。

---

## 執行流程

### Step 1：讀取輸入

**`mode: initial`**：讀取 assignment 提供的 `summary_path`，進入 Step 2 (Decompose)。

**`mode: repair`**：讀取 assignment 提供的 `summary_path`、`canonical/mapping.<source_key>.json`（目前成果）以及 `canonical/visual_review.<source_key>.json`（findings）。Finding 的 notes 包含觀察和成因，你只需要針對有 finding 的 `phrase` 進行修正（例如重新找對應的 snippet、調整 text-equality 等），修正後跳至 Step 4 自檢。不需重新分解整個摘要。

### Step 2：Decompose 摘要為 phrases (initial mode)

（若為 repair mode 則跳過此步，直接處理 findings）

依 source 類型定位 `items[0]`（L1/L2 在頂層；method 在 `modules[module_index]` 之下）。可用的位置包含：
- `main_line`：一段精煉主線
- `refined_final_output[i]`：第 i 個段落（i = 0..N-1）

把 `main_line` 與每個段落切成 phrase。規則：
1. **一個 phrase = 一個動作或一個因果**。例：
   - 「兒童心臟瓣膜置換的死結」（一個名詞性問題）
   - 「植入物無法跟著身體一起長大」（一個事實）
   - 「導致孩子必須反覆執行開胸手術換瓣膜」（一個因果結果）
2. 大約 **4–20 個中文字**。
3. 必須是 **原段落的連續 substring**（下游做標記時會用到）。
4. 同一段內的 phrases **不得彼此重疊**。
5. **整段每個獨立的事實／動作／因果都列一個 phrase**，只有純連接詞（「為了解決這個問題」、「具體做法是」）才略過。
6. 如果夾帶數據或細節，一定要成為 phrase 或是 phrase 的一部分。例：「瓣膜從原本的 19 mm 長到大約 25 mm」，這種事情很重要，一定要找到資料來源。
7. **無法標記的內容也要列為 phrase**：對於某些 summary 裡的內容，如果因為某些原因找不到對應原文，你仍然必須將它切成 phrase 納入，但將 `paper_snippets` 設為空陣列 `[]`，並新增一個 `omission_reason` 欄位填寫原因（例如「沒有對應的內文可以對照」、「屬於從 summary 其他部分推論出來的詞句」或「為了講解方便額外創造但是沒有寫在內文的詞句」）。

### Step 3：對應原文 snippets

對每個 phrase，從 `<paper_dir>/reassembly/canonical/paper.html` 找對應的英文片段。規則（嚴格）：
- (a) **對於數據或細節，一定要找到該數據或細節的確實出處**。諸如「（請看 Fig. 1D）」這樣的文字一定要連到相關的 figure caption。
- (b) **優先 figure / table 為錨點的位置**：figure caption、table cell、正文中靠近 `Fig. N` / `Table N` 引用的句子。
- (c) **若同樣的事實在 figure/table/正文有錨點，跳過 abstract / discussion 的重複處**。
- (c.1) **abstract / discussion 只在沒有別處時 fallback 使用**。
- (d) **snippet 必須是 `<paper_dir>/reassembly/canonical/paper.html` 的字元級 substring**（含大小寫、標點、連字號、數字）。下游會用字面精確比對來找 snippet 的位置並包裝標籤。
- (e) **snippet 不得跨 HTML tag**——必須是單一 tag（如某個 `<p>`、`<figcaption>`、`<td>`）內的連續文字。若關鍵段落橫跨 tag，取單一 tag 內最長片段。
- (f) **snippet 是 phrase 級而非單字級**——通常 5–25 個英文字、是有意義的子句。例：不要只取 `calcification`，要取 `leaflet calcification was 2.6-fold lower`。
- (g) 一個 phrase 若在多個 **不同錨點**（不同 figure caption / 不同 `<p>` / 不同 `<td>`）都被佐證，全部列為 snippets。同一錨點內只截一次（最完整的那段）。abstract / discussion 仍受 (c) 規範——body / figure / table 已有對應時，不要再加 abstract / discussion 當作「多錨點之一」。
- (h) 跳過 `<script>` / `<style>` / MathJax 區塊 / HTML attribute 內的文字。
- (h.1) **HTML entity 必須原樣保留**：paper HTML 用 `>`、`<`、`&` 等 entity 編碼數學不等式（例如 `P > 0.05`、`<5 mmHg mean systolic pressure gradient`）。snippet 字串要**完整含 entity**，不可改寫成 `>` 或 `<`，否則字面 substring 比對會找不到。
- (i) **防止同一個 phrase 反覆引用同一段原文**：同一個 phrase 自己的 `paper_snippets` list 內不得 substring-containment 或 partial overlap。**跨 phrase 引用不歸 rule (i) 管**。
  - **跨 phrase / 跨 module / 跨 mapping 完全不限制**：containment、partial overlap、完全相同字串都自由。
  - 跨 phrase 出現 **containment** 時（短 B 完全是長 A 的子串），apply 端會**隱式合併**：短 B 沒有自己的 `<mark>`，但 B 對應的 phrase 會被接到 A 的 mark 上（`data-back` 多收 B 的 phrase id、Y 的 panel anchor 仍會跳到 A 的 mark、右側 rail 該 mark 旁多一張 B 對應顏色的 note）。寫的時候**不需要刻意避免** containment，apply 會自動處理。
  - 跨 phrase 出現 **partial overlap**（兩段彼此交錯、誰也沒包住誰）時，apply 端同樣 alias 吸收：長的先被包成 mark，短的字面位置已被佔用 → 短的 canonical id 翻譯到長的 mark 上（行為同 containment）。短 snippet 沒有自己的 `<mark>`，但對應的 phrase 仍接得回去。

  實務做法：
  - 對每個 phrase 盡量列出所有合 (a)–(g) 規則的 snippet。
  - 寫完後**只在同一個 phrase 自己的 paper_snippets list 內**做兩兩 containment + partial overlap 檢查；發現衝突 → 刪短的、或把長的切短到不包含。跨 phrase 不必管。

### Step 4：輸出 JSON

**你必須使用寫檔工具 (如 `write_to_file` 或透過 Python / bash 腳本) 確實在對應的 `output_path` 建立實體檔案，不要只在對話中印出內容。**

JSON schema 範例如下：

```json
{
  "schema_version": "mapping.v1",
  "source_summary_id": "summary_03",
  "source_key": "l1",
  "color_key": "summary",
  "phrases": [
    {
      "id": "h-l1-001",
      "summary_text": "原段落的精確 substring",
      "summary_location": "main_line",
      "paper_snippets": [
        {"snippet_id": "h-l1-001-a", "text": "原文精確 substring"}
      ]
    },
    {
      "id": "h-l1-002",
      "summary_text": "...",
      "summary_location": "refined_0",
      "paper_snippets": [],
      "omission_reason": "屬於為了講解方便額外創造的比喻，原文沒有對應內文"
    }
  ]
}
```

- `source_summary_id`：L1 從 `items[0].item_id`、L2 從 `items[0].source_detail_id` 取得（依 `source_key` 決定）。
- `id`：使用 `h-<source_key>-<序號>` 的格式。例如 `h-l1-001`、`h-l1-002` ⋯ 依「main_line → refined_0 → refined_1 → ⋯」順序連號。若為 L2 則是 `h-l2_m1-001`。
- `snippet_id`：`<phrase_id>-a` / `-b` ⋯

### Step 5：自檢

寫完 JSON 後，逐項對照下列檢查自我驗證。任何一項不通過就回去修，直到全部通過再進 Step 5。

**Metadata**
- JSON 可 parse。
- `schema_version` = `mapping.v1`、`source_key` = 你被指定的 key、`color_key` 對應慣例表（`l1`→`summary`，`l2_mN`→`mN`）。
- `source_summary_id` = 來源檔 `items[0]` 的識別碼（L1: `item_id`；L2: `source_detail_id`）。

**Phrase**
- 每個 `phrase.id` 唯一，格式 `h-<source_key>-NNN`，依「main_line → refined_0 → refined_1 → ⋯」順序連號無跳號。
- 每個 `summary_text` 是該 `summary_location` 原段落的字面 substring（重讀 `summary_path` 來源檔比對）。
- 同一 `summary_location` 內的 phrases 不彼此重疊（位置不交錯）。
- 整段每個獨立事實／動作／因果都有對應 phrase；只有純連接詞略過。
- 無法標記的 phrase 必須要有 `omission_reason` 且 `paper_snippets` 為空。

**Snippet**
- 每個 `snippet.text` 是 `<paper_dir>/reassembly/canonical/paper.html` 的字面 substring（精確到大小寫、標點、連字號、數字）。
- snippet **不可含 HTML tag markup**（例如 `<p>`、`</mark>`、`<br/>` 這種「尖括號＋tag 名」pattern）。但 HTML entity（`>`、`<`、`&` 等）是合法的、必須原樣保留。檢查時建議先剝除 `&[a-z]+;` 與 `&#\d+;` 兩種 entity，再看剩下的字串是否還有 `<` 或 `>`；**只有後者算違規**。
- 若有對應原文，每個 phrase 至少 1 個 snippet；同事實若在多錨點佐證則列多個。若無，必須要有 `omission_reason`。
- 每個 snippet 來自單一 tag（`<p>` / `<figcaption>` / `<td>`）內的連續文字。
- snippet 長度通常 5–25 個英文字、是有意義的子句，不是單字。
- 沒有 snippet 取自 `<script>` / `<style>` / MathJax 區塊 / HTML attribute。

**Rule (a)–(c) 優先序**
- 凡有 figure caption / table / body 錨點的 fact，沒去抓 abstract / discussion 當「額外一條」。
- 純 abstract / discussion 來源的 snippet 僅出現在「其他位置完全沒提到」的 fact。

**Rule (g) 多錨點**
- 同一事實若在不同錨點（不同 figure caption / 不同 `<p>` / 不同 `<td>`）出現都列為 snippet。
- 同一錨點內只截一次（最完整那段）。

**Rule (i) 同 phrase 內不得 substring-containment 或 partial overlap**
- 範圍：**只在同一個 phrase 自己的 paper_snippets list 內**兩兩比對：
  - 沒有同 phrase 內 snippet A 完全包含同 phrase 內 snippet B（substring containment）。
  - 沒有同 phrase 內 snippet A 的尾巴與同 phrase 內 snippet B 的開頭重疊 ≥ 15 個英文字（partial overlap）。
- **跨 phrase（不管同 module 或跨 mapping）不檢查**：containment / overlap / 完全相同字串都允許。
  - 跨 phrase containment 由 apply 端隱式合併處理（短 snippet 對應的 phrase 接到長的 mark 上）。
  - 跨 phrase partial overlap 由 apply 端用位置 alias 吸收（行為同 containment：短 snippet 對應的 phrase 接到長的 mark 上）。

### Step 6：回報

在 Step 5 自檢全部通過後，請在給使用者的最終回應中，整理一份約 120 字內的簡短回報：
- 總 phrases 數量 / 總 snippets 數量
- 每個 `summary_location` 的 phrase 分布（例如：main_line: 1, refined_0: 3...）
- 標出使用了 abstract / discussion 做為 fallback 的 phrases
- 標出刻意略過的 phrases 與原因

## 完成判定

- 確實存在並寫入磁碟到指定的 `output_path`，且 Step 5 所有自檢項目都通過。
- 提供了 Step 6 的回報訊息。
- mapping 對應的摘要 / 原文沒有被改動。