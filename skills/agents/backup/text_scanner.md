# 目標

這是一份給 text_scanner agent 看的指引。

此 agent 做一件事：掃描整份論文，建立文件結構地圖（`text_plan.json`），讓下游 assembler workers 知道每一段文字在哪裡、屬於什麼角色、跨頁接續如何銜接。

- 輸入：paper directory（含 `shared/source.pdf`、`shared/previews/`）。
- 輸出：`<output_root>/text_plan.json`。
- 邊界：此 agent 負責版面理解和結構規劃。不做 word_id 對應、不組裝段落文字、不讀 `extracted.json`。

Scanner 和其他 lane 的 scanner（figure_scanner、table_scanner、equation_scanner）角色相同：產出輕量的 plan，讓 downstream worker 在已知結構中做精確工作。

# 流程

## Step 1: 掃描全部頁面

用 Read tool 讀 source.pdf（pages 參數，每次 ≤20 頁），逐段建立對整份文件的理解。Page preview 可輔助確認版面（欄位結構、圖表佔位），但文字內容以 source.pdf 為準。

對每頁記錄：
- **頁面角色**：`body`（有正文段落）、`table-dominant`（頁面主體是表格，正文只有零星幾行）、`figure-dominant`（頁面主體是圖片）、`references`（書目頁）、`mixed`（正文 + 大型圖表共存）。
- **欄位結構**：單欄或雙欄。
- **文字區域**：頁面上哪些 y 範圍有正文、哪些被圖表佔據。不需要精確到 pixel，用粗略描述即可（如「左欄 y=80-400 有正文，y=400-700 是 Table 3」）。

## Step 2: 識別段落區域

基於 Step 1 的頁面地圖，識別正文段落的粗略邊界。每個段落區域記錄：
- 所在頁面和欄位。
- 粗略起止位置（描述性，如「page 7 左欄上半」）。
- 推測的段落類型（heading / body / caption / reference）。

不需要逐段精確切割——assembler 會用 extracted.json 的座標做精確邊界。Scanner 的任務是提供「哪裡有什麼」的全局地圖。

## Step 3: 標記跨頁接續

這是 scanner 最重要的判斷。逐頁檢查：

- 頁面或欄位結尾處，句子是否在中途斷開（沒有句末標點、以連字號結尾、語法不完整）？
- 如果斷開，接續在哪裡？可能跨越多頁的純表格/圖片頁面。
- 讀 source.pdf 確認接續點的文字，確保前段結尾和後段開頭語意銜接。

每個跨頁接續記錄為一個 `continuation`：從哪頁哪欄的結尾，接到哪頁哪欄的開頭。

常見情境：
- 正文段落被整頁表格打斷（如 page 7 結尾 → pages 8-10 是 table → page 11 開頭接續）。
- 正文段落跨欄接續（左欄底部 → 右欄頂部）。
- Figure/table caption 插在正文段落中間，正文在 caption 之後繼續。

## Step 4: 確定章節結構

從 source.pdf 讀取所有 heading，建立文件大綱：
- 章節標題和編號（如「1. Introduction」「2.1 Potentiometric sensors」）。
- 每個章節的起始頁面和位置。
- 特殊區段：Abstract、Keywords、CRediT、References 的位置。

## Step 5: 分配 worker assignments

將段落區域分成 N 個 assignments（建議 2-4 個，依文件長度和複雜度決定）。分割原則：
- 在章節邊界切割，不在段落中間切。
- 把 references 獨立成一個 assignment（機械性高，不需讀 source.pdf）。
- 複雜區段（大量跨頁接續）不要拆得太碎——跨頁接續的兩端應在同一個 assignment 內。
- 每個 assignment 標註它包含的 continuations，讓 worker 知道要處理哪些跨頁銜接。

## Step 6: 寫出 text_plan.json 並自檢

寫出 `text_plan.json`（格式見 `# 格式`），然後自檢：
- JSON 可 parse。
- 每頁都有 `page_role` entry。
- 所有 `continuations` 的 `from` 和 `to` 頁面都存在於 `pages` 中。
- `assignments` 涵蓋所有段落區域，不遺漏。
- `outline` 的章節順序和 source.pdf 一致。

# 格式

`text_plan.json`。

## Example

```json
{
  "schema_version": "text_plan.v1",
  "total_pages": 24,
  "columns": "two-column",                         // 全文主要欄位結構
  "pages": [
    {
      "page": 1,
      "role": "body",
      "notes": "Title, authors, affiliations, abstract, keywords, intro start"
    },
    {
      "page": 8,
      "role": "table-dominant",
      "notes": "Table 1 occupies full page; no body text"
    },
    {
      "page": 20,
      "role": "mixed",
      "notes": "Left col: body text end + CRediT; right col: references start"
    }
  ],
  "outline": [
    {"heading": "1. Introduction", "page": 1, "position": "right column top"},
    {"heading": "2. Electrochemical sensors", "page": 2, "position": "left column middle"},
    {"heading": "2.1 Potentiometric sensors", "page": 2, "position": "right column top"},
    {"heading": "References", "page": 20, "position": "right column middle"}
  ],
  "continuations": [
    {
      "from": {"page": 7, "column": "right", "position": "bottom"},
      "to": {"page": 9, "column": "left", "position": "top"},
      "reason": "Pages 8-9 are Table 1-2; sentence continues after tables",
      "context": "...a gold screen-printed → ...electrode (SPE) and a coin-shaped"
    },
    {
      "from": {"page": 12, "column": "left", "position": "bottom"},
      "to": {"page": 15, "column": "left", "position": "top"},
      "reason": "Pages 13-14 are Tables 5-6; body resumes on page 15",
      "context": "...analyzed different ranges of → ...flow rates to deliver"
    }
  ],
  "assignments": [
    {
      "assignment_id": "worker_01",
      "description": "Front matter + Sections 1-3",
      "pages": [1, 2, 3, 4, 5, 6],
      "sections": ["front_matter", "1", "2", "3"],
      "continuations_included": []
    },
    {
      "assignment_id": "worker_02",
      "description": "Section 4 (vibration & flow) with cross-table continuations",
      "pages": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
      "sections": ["4"],
      "continuations_included": [0, 1]          // indices into top-level continuations[]
    },
    {
      "assignment_id": "worker_03",
      "description": "Sections 5-6 + back matter + references",
      "pages": [17, 18, 19, 20, 21, 22, 23, 24],
      "sections": ["5", "6", "back_matter", "references"],
      "continuations_included": []
    }
  ]
}
```

## 規則

- **`pages`**：每頁一個 entry。`role` 值：`body`、`table-dominant`、`figure-dominant`、`references`、`mixed`。`notes` 簡短描述該頁內容分佈。
- **`outline`**：依文件閱讀順序列出所有 heading。`position` 用自然語言描述（如 "left column top"），不需要精確座標。
- **`continuations`**：每個跨頁/跨欄接續一個 entry。`context` 欄位引用斷點前後各幾個字，讓 assembler 能定位 word_ids。`reason` 解釋為什麼會斷開（中間有什麼）。
- **`assignments`**：每個 assignment 分配給一個 assembler worker。`pages` 列出該 worker 負責的頁面。`continuations_included` 引用 `continuations[]` 的 index，告訴 worker 哪些跨頁接續在它的範圍內。
- Scanner 不決定段落精確邊界或 word_id 歸屬。這些由 assembler worker 在 extracted.json 中完成。
- 不確定某處是否為跨頁接續時，讀 source.pdf 確認。仍無法判定則記錄在 `continuations` 中並加上 `"uncertain": true`。
