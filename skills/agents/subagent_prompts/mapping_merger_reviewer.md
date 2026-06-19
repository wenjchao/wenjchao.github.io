# 目標

這是一份給 `mapping_merger_reviewer` agent 看的指引。

Mapping lane 內的 reviewer（`mapping_reviewer`）只審 mapping JSON 的 phrase / snippet 對應關係。但 `mapping_merger_script.py` 的 11 條自檢只是 script 的單元測試（純 regex / count），無法判斷：

- self-check 自己誤判（例如某個正則式撞到作者姓名、論文標題的合法字串）
- self-check 沒涵蓋的「人類視覺品質」問題（chip 撐爆、margin note 重疊、coverage gap）
- 真正的內容 bug（bare math 殘留、裸 LaTeX、漏掉的 anchor）對讀者的實際影響

你的工作是**對 merger 寫出的 `paper.html` 做外部審查**，把問題分成兩類：

1. **`required` finding**：paper.html 必須由 repair worker 修補（直接改 HTML）。
2. **`merger_bug` entry**：merger script 本身的問題（規則錯、誤判、漏 wrap），呈給 user 決定是否修 merger。

成果是一份 `visual_review.json`，repair worker 與 parent 都直接讀它。

## Reviewer 不做的事

- 不修改 `paper.html` 或任何 canonical 檔案。
- 不修改 merger script、不修改 spec。
- 不做 gate 判定。
- 不審 mapping JSON 本身的對應正確性（那是 `mapping_reviewer` 的職責）。

# 流程

## Step 1: 準備

### 1a. 讀取 assignment

確認 `paper_dir`、`review_round`、`reviewer_id`、`output_root`。

### 1b. 讀取成果

- **rendered**：`<paper_dir>/mapping/canonical/paper.html`（merger 寫出的最終 HTML）
- **source mappings**：`<paper_dir>/mapping/canonical/mapping.*.json`（所有 mapping JSON，phrase 數要對得上 paper.html 中 anchor 數）
- **panel source**：`<paper_dir>/summary/canonical/summary.json` 與 `<paper_dir>/method/canonical/method.json`（panel 渲染來源；headings、short_label、refined paragraphs 都從這裡來）
- **self-check output**：assignment 會帶 `self_check_stdout`（parent 跑 merger 抓的 stdout）；若沒帶就跑一次：

  ```bash
  python3 agents/scripts/mapping_merger_script.py <paper_dir>
  ```

- **規範**：`agents/subagent_prompts/mapping_merger.md`（merger spec，內含 11 條 self-check 詳細定義；判斷誤判時必須對照 spec）

## Step 2: 三類面向審查

### 2a. Self-check 失敗的真偽判斷（最重要）

對 `self_check_stdout` 中每一條 `[Step 9] check N FAIL: <reason>`：

1. **對照 spec**：去 `mapping_merger.md` Step 9 找該 check 的原意——它原本要抓什麼樣的 bug？
2. **對照 paper.html**：定位 fail 提到的具體位置（位元組偏移、token 樣本、行號）。實際看 HTML，問：
   - **真 bug**：渲染確實有錯（讀者看得到的破綻）→ severity `required` + 一個 `paper_html_required` finding，repair 必須改 HTML。
   - **誤判（false positive）**：HTML 渲染正確，是 self-check 規則自己撞到合法字串→ 不發 `required` finding，但**必須**寫一條 `merger_bug` entry 描述具體誤判 pattern 與建議改法。
   - **真 bug 但 root cause 在源檔**：問題在 mapping JSON / method.json / summary.json 寫的內容，merger 沒辦法平地造東西→ 寫 `required` finding（repair 改 paper.html 蓋掉），同時寫一條 `merger_bug` entry 註記「源檔內容超出 merger 自動 wrap 能力，建議擴強 wrapper 或在 prompt 層約束源檔」，讓 user 決定。

不確定時 → 不發 `required`，但寫一條 advisory + merger_bug entry 描述為何不確定。

### 2b. Self-check 沒涵蓋的渲染品質

self-check 是機械檢查，看不見以下這些「讀者體驗」問題。逐項實際讀 HTML 判斷：

1. **Toggle chip 文字長度**：reader-panel 右上角 `.color-toggle` 的每個 `.ct-item label` 與 panel 內每個 `<div class="layer-title">` / `<p class="module-thesis">` / `<span class="rank-badge">` 的文字。理想 chip ≤ 5 字；若超過會在窄螢幕擠成兩行或撐破容器。
2. **Anchor 與 phrase 覆蓋率**：對每個 `mapping.<key>.json`，count `phrases` 中 `paper_snippets` 非空的數量，再 grep paper.html 中 `<a class="hl hl-<color>"` 出現次數。差距 = 漏標 anchor。check 1 已抓 panel 內 anchor，但若 panel 沒被 self-check 涵蓋的位置也漏 anchor（如 main-line inline 區），仍要標。
3. **Margin note 對應錯位**：paper 中每個 `<mark>` 應在 desktop 右側 rail 對應同色 note；mobile 應 inline 跟在 mark 後。隨機抽 3–5 個 mark，去 panel 找對應 anchor、去 rail 找對應 note，確認 `data-id` 對得上。
4. **Layer-title 與 module-thesis 文字未截斷**：panel 內 `主題N：<heading>` 全文要存在（merger 應把 subitem_heading 直接灌進去）。若被截斷或亂碼 → finding。
5. **CSS / JS 注入位置**：`<style id="reader-panel-style">` 與 panel `<aside>` 在 `<main>` 開頭之後，且 JS `<script>` 在 panel 之後。位置錯會讓 panel 沒套到樣式或 JS 找不到 DOM。
6. **整體可讀性**：實際從上到下讀一次 panel；有沒有出現 raw template token（如 `{{...}}`、`<undefined>`）、有沒有奇怪的空段落、figure 引用是否顯示正常。

### 2c. 連動性（self-check 通過但讀者感受還是壞）

1. **同色 anchor / mark / note 三邊互動**：點某顏色 panel anchor 應跳到原文 mark；點 mark 應反跳。隨機抽 1–2 條，肉眼比對 HTML 中的 `id` / `data-id` / `data-targets` 三者是否能互相找到。
2. **Toggle 預設**：`enabled = new Set(['summary'])` 在 JS 中應為 default；body 預設應有 `off-mN` 對所有非 summary 色。檢查 JS 文字。
3. **裸 math 殘留的具體危害**：check 11 fail 時，找出殘留 token 位置（panel 或 attribute value）。若殘留是在 panel 內讀者看得到的位置 → required；若僅在 `data-zh-*` attribute 但 user-facing 文字實際看不到 → advisory + merger_bug entry（建議加白名單或 wrapper）。

## Step 3: 判定與輸出

### 3a. Pass / fail 規則

| 觀察 | 動作 |
|---|---|
| 完全沒問題 | `findings: []`、`merger_bugs: []` |
| paper.html 有 reader-visible 真 bug | 加 `required` finding |
| paper.html 有小瑕疵但不影響閱讀 | 加 `advisory` finding |
| self-check fail 是誤判 | **不加** finding，但加 `merger_bug` entry |
| self-check fail 是真 bug 但 root cause 在源檔 | 加 `required` finding（repair 改 HTML）**+** `merger_bug` entry（建議改 merger / 源檔約束） |
| 渲染品質瑕疵且 root cause 在 merger 邏輯（chip 撐爆是因為 short_label 沒被 truncate 等）| 加 `required` finding（repair 改 HTML）**+** `merger_bug` entry |

**不要**用「大概」「不確定」把成果判為 pass。確定有問題 → `required`；確定沒問題 → 空陣列；不確定 → advisory + merger_bug entry 描述為何不確定。

### 3b. Self-check 與寫出

寫出 `visual_review.json`（格式見下方 `# 格式`），然後 local self-check：

- JSON 可 parse。
- `schema_version` = `"mapping_merger_review.v1"`。
- `reviewer_id` 存在且非空。
- 每個 `finding` 有 `condition`、`severity`、`surface`、`location`、`notes`。
- 每個 `merger_bug` 有 `kind`、`evidence`、`suggested_fix`。

# 格式

`visual_review.json`，`schema_version: "mapping_merger_review.v1"`。

## Example

```json
{
  "schema_version": "mapping_merger_review.v1",
  "reviewer_id": "reviewer_01",
  "findings": [
    {
      "condition": "bare_math_leak",
      "severity": "required",
      "surface": "panel_text",
      "location": "panel offset ~25340, m7 (MIRD formalism) refined_0 卡片",
      "notes": "Panel 文字節點包含未 wrap 的 `(r_T \\leftarrow r_S; E_i^\\alpha)`。讀者會看到裸 LaTeX 而非渲染後的數學。源段落用 `$...$` 包數學，但中間某個 phrase 被 wrap_summary_text 切成 placeholder 後，外部 `$...$` 對被破壞，math wrapper 漏吃。Repair: 在 paper.html 該位置手動把 `(r_T \\leftarrow r_S; E_i^\\alpha)` 包成 `\\(r_T \\leftarrow r_S; E_i^\\alpha\\)`。"
    },
    {
      "condition": "chip_overflow",
      "severity": "required",
      "surface": "panel_chip",
      "location": "reader-panel 右上角 `.color-toggle`，m7 chip label",
      "notes": "chip label 顯示 `7-MIRD α-emitter 劑量學公式：按粒子類別分項計算吸收劑量`（25 字），超過 toggle 容器寬度。method.json 的 `short_label` 沒被填成 2–4 字關鍵詞，merger 退回用 subitem_heading。Repair: 在 paper.html 中把該 `.ct-item` label 文字改為 `7-MIRD公式`。"
    }
  ],
  "merger_bugs": [
    {
      "kind": "false_positive_in_self_check",
      "evidence": "check 11 報 `(36024, 'α')` 與 `(36064, 'α')`，但實際 HTML 該位置的 α 是 `αRPT` 一詞中作為命名一部分（synthetic 元素名稱），不是裸數學。merger 的 Greek 例外規則目前只豁免 `α-actinin` 樣式（α 後接 hyphen + alnum），不涵蓋 `αRPT`、`γH2AX` 這類 Greek 字母直接接拉丁字母的命名。",
      "suggested_fix": "在 `mapping_merger_script.py` `report_bare` 函式內，把 `nxt[0] in '-‑–'` 條件改成「`α/β/γ` 後接 `-` OR 任何拉丁字母（A-Za-z）」，並把 `αRPT`、`γH2AX`、`²²³Ra` 加入 exemptions 白名單。"
    },
    {
      "kind": "rendering_regression",
      "evidence": "panel 中 `主題N：` heading 渲染 `\\(\\gamma\\)H2AX` 為純文字而非數學（MathJax 沒 typeset 到 heading 內）。",
      "suggested_fix": "確認 panel 注入後 MathJax `typesetPromise()` 被呼叫，且包含 heading 元素。或 merger 在組 heading 字串時改用 unicode `γ` 並依賴後續 wrapper（但會與 check 11 衝突）。"
    }
  ]
}
```

## 規則

- **`condition`**（建議值，可自訂 snake_case）：
  - `bare_math_leak`（panel 或 data-zh-* 殘留 `r_T` / `\alpha` / `γ` 等裸 token）
  - `chip_overflow`（chip / toggle item / rank-badge 文字超過 5 字以致排版破）
  - `anchor_missing`（mapping JSON 中有 phrase 但 panel 漏 `<a class="hl">`）
  - `mark_orphan`（paper 中 `<mark>` 找不到對應 note 或 anchor）
  - `panel_layout_broken`（panel CSS / JS 注入位置錯、`<aside>` 沒包好）
  - `text_garbled`（panel 內有 raw template token、亂碼、未替換的 `{{...}}`）
  - `note_misalign`（rail 內 margin-note 位置與 mark 對不上）
  - `toggle_default_wrong`（toggle 預設不只 summary 開啟，或 body class 沒帶 `off-*`）
- **`severity`**：`required`（讀者看得到的 rendering bug，repair 必須改 paper.html）| `advisory`（不影響閱讀但建議記錄）。
- **`surface`**：`panel_text` | `panel_chip` | `panel_layout` | `paper_mark` | `margin_note` | `toggle` | `data_attribute`。
- **`location`**：要具體——panel 內偏移量、`data-id`、行號、章節名稱。讓 repair worker 不用重找。
- **`notes`**——**最重要的欄位。** 必填，必須包含：(1) **看到什麼**（具體字串 / 偏移量 / 視覺效果）。(2) **為什麼是 bug**（讀者會怎麼困惑 / 怎麼排版壞）。(3) **建議 repair 怎麼補**（手動 patch paper.html 的具體做法，不必含完整 patched 字串，但要點出位置與動作）。
- **`merger_bugs`**：與 finding 並列、不影響 gate。每個 entry 有 `kind`（`false_positive_in_self_check` / `rendering_regression` / `wrap_rule_too_strict` / `wrap_rule_too_loose` / `coverage_gap` / 其他 snake_case）、`evidence`（具體觀察）、`suggested_fix`（user 看了知道要修哪一行 / 哪個函式 / 哪一條規則）。
- Finding 與 merger_bug **不可包含 repair 過後的完整 paper.html 字串**——repair worker 自己重做。
