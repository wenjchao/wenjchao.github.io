# Highlight Mapper Prompt 模板

## 目標

把一份中文摘要的每個 phrase，對應到原文 HTML 裡的英文片段，產出 `highlight_map.<key>.json`。

- 輸入：一份摘要（`summary.json` 中某個 `items[i]`）+ 一份乾淨原文 HTML（`/tmp/paper_clean.html`，已去掉 reader panel）
- 輸出：`highlight_map.<source_key>.json`，下游 apply 腳本會用此檔在原文裡標 `<mark>`、在摘要裡標 `<a>`

### 不做的事

- 不修改原文 HTML，也不修改摘要 JSON。
- 不在 mapping 裡放對應不到的 phrase（寧可漏掉純連接詞，也不要硬塞）。

## 流程

### Step 1：Decompose 摘要為 phrases

讀 assignment 指定的 `source_path` 和 `source_index`，取 `items[source_index]`。可用的位置：
- `main_line`：一段精煉主線
- `refined_final_output[i]`：第 i 個段落（i = 0..N-1）

把 `main_line` 與每個段落切成 phrase。規則：

1. **一個 phrase = 一個動作或一個因果**。例：
   - 「兒童心臟瓣膜置換的死結」（一個名詞性問題）
   - 「植入物無法跟著身體一起長大」（一個事實）
   - 「導致孩子必須反覆執行開胸手術換瓣膜」（一個因果結果）
2. 大約 **4–20 個中文字**。
3. 必須是 **原段落的連續 substring**（下游 `str.replace` 會用到）。
4. 同一段內的 phrases **不得彼此重疊**。
5. **覆蓋大部分內容**，但純連接詞（「為了解決這個問題」、「具體做法是」）可以略過。

### Step 2：對應原文 snippets

對每個 phrase，從 `/tmp/paper_clean.html` 找對應的英文片段。規則（嚴格）：

- (a) **優先 figure / table 為錨點的位置**：figure caption、table cell、正文中靠近 `Fig. N` / `Table N` 引用的句子。
- (b) **若同樣的事實在 figure/table/正文有錨點，跳過 abstract / discussion 的重複處**。
- (c) **abstract / discussion 只在沒有別處時 fallback 使用**。
- (d) **snippet 必須是 `/tmp/paper_clean.html` 的字元級 substring**（含大小寫、標點、連字號、數字）。下游會做 `str.replace(snippet, '<mark>' + snippet + '</mark>')`。
- (e) **snippet 不得跨 HTML tag**——必須是單一 tag（如某個 `<p>`、`<figcaption>`、`<td>`）內的連續文字。若關鍵段落橫跨 tag，取單一 tag 內最長片段。
- (f) **snippet 是 phrase 級而非單字級**——通常 5–25 個英文字、是有意義的子句。例：不要只取 `calcification`，要取 `leaflet calcification was 2.6-fold lower`。
- (g) 一個 phrase 符合 (a) 的多個位置都列出。
- (h) 跳過 `<script>` / `<style>` / MathJax 區塊 / HTML attribute 內的文字。

### Step 3：輸出 JSON

寫到 assignment 指定的 `output_path`，schema：

```json
{
  "schema_version": "highlight_map.v1",
  "source_summary_id": "summary_03",
  "source_key": "l1",
  "color_key": "summary",
  "phrases": [
    {
      "id": "h1-001",
      "summary_text": "原段落的精確 substring",
      "summary_location": "main_line",
      "paper_snippets": [
        {"snippet_id": "h1-001-a", "text": "原文精確 substring"}
      ]
    },
    {
      "id": "h1-002",
      "summary_text": "...",
      "summary_location": "refined_0",
      "paper_snippets": [
        {"snippet_id": "h1-002-a", "text": "..."},
        {"snippet_id": "h1-002-b", "text": "..."}
      ]
    }
  ]
}
```

- `source_key` 從 assignment 取（如 `l1`、`l2_m1`）；同時決定檔名（`highlight_map.<source_key>.json`）。
- `color_key` 對應 CSS 顏色：`l1` → `summary`（黃）、`l2_m1..m6` → `m1..m6`。若 assignment 沒給就依此慣例自己推。
- `id`：`h<short>-001`、`h<short>-002` ⋯ 依「main_line → refined_0 → refined_1 → ⋯」順序連號。`<short>` 對 L1 用 `1`，對 L2 用 `2m1` / `2m2` 等。
- `snippet_id`：`<phrase_id>-a` / `-b` ⋯

### Step 4：自檢（寫檔前必跑）

1. JSON 可 parse。
2. 每個 `summary_text` 是 source 段落的字面 substring（自己重讀 `summary.json` 比對）。
3. 每個 snippet `text` 是 `/tmp/paper_clean.html` 的字面 substring。
4. 沒有 snippet 內含 `<` 或 `>`。
5. 每個 phrase 至少 1 個 snippet。

任一項失敗 → 修正後重跑自檢，全部通過才寫檔。

### Step 5：回報

回覆（≤120 字）：
- 總 phrases / 總 snippets
- 每個 `summary_location` 的 phrase 數
- 標出使用 abstract/discussion fallback (rule c) 的 phrases
- 標出刻意略過的 phrases 和原因
