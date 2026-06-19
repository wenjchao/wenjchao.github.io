# Highlight Map Pipeline

## 目標

把指定摘要（L1 best、或 L2 某個 module top）的每個 phrase，對應到原文 HTML 裡的英文片段，產出 `highlight_map.<source_key>.json`，供 [highlight_apply_SKILL.md](highlight_apply_SKILL.md) 套用螢光筆。

- 輸入：
  - `<paper_dir>/<basename>.html`（論文原文）
  - `<paper_dir>/summary/canonical/summary.json` 或 `<paper_dir>/detail/module_<N>_<slug>/canonical/summary.json`
- 輸出：`highlight_map.<source_key>.json`，放在對應的 `canonical/` 目錄下

## 參數

| 變數 | 預設 | 說明 |
|---|---|---|
| `paper_dir` | （必填） | paper 目錄 |
| `source_key` | `l1` | 識別碼，決定螢光筆顏色與輸出檔名 |

### 對應慣例（`source_key` → 來源/輸出/顏色）

| `source_key` | 摘要來源 | mapping 輸出路徑 | `color_key` |
|---|---|---|---|
| `l1` | `summary/canonical/summary.json` items[0] | `summary/canonical/highlight_map.l1.json` | `summary`（黃）|
| `l2_m1` | `detail/module_1_<slug>/canonical/summary.json` items[0] | `detail/module_1_<slug>/canonical/highlight_map.l2_m1.json` | `m1`（粉）|
| `l2_m2` | `detail/module_2_<slug>/canonical/summary.json` items[0] | `detail/module_2_<slug>/canonical/highlight_map.l2_m2.json` | `m2`（綠）|
| ⋯ | 依此類推（m3 藍 / m4 桃 / m5 紫 / m6 青）|

Parent 從 `source_key` 推出 `source_path`、`output_path`、`color_key` 三個欄位，傳給 subagent。

## 路徑慣例

`basename` 為 `paper_dir` 最後一段（與其他 lane 相同）。`paper_file = <paper_dir>/<basename>.html`。

## 流程

Parent 只做兩種動作：
- **[spawn agent]** 啟動 `highlight_mapper`
- **[mechanical]** 跑簡單 script（去掉舊 panel、驗 mapping）

### Step 1：準備 clean paper

[mechanical] 把先前注入的 reader panel 暫時去掉，存到 `/tmp/paper_clean.html`，讓 subagent 看到的是原始論文文字：

```bash
python3 - <<'PY'
import re
from pathlib import Path
src = Path("<paper_dir>/<basename>.html").read_text(encoding="utf-8")
clean = re.sub(
    r'<style id="reader-panel-style">.*?</style>\s*<aside class="reader-panel">.*?</aside>\s*',
    "", src, flags=re.S,
)
# 也把 apply 注入的 <script id="reader-panel-js"> 去掉
clean = re.sub(r'<script id="reader-panel-js">.*?</script>\s*', "", clean, flags=re.S)
Path("/tmp/paper_clean.html").write_text(clean, encoding="utf-8")
print(f"clean paper: {len(clean)} bytes")
PY
```

### Step 2：Spawn mapper subagent

[spawn agent] 啟動一個 `highlight_mapper`：

```text
Subagent prompt = <agents/subagent_prompts/highlight_mapper.md 全文>

---
Assignment
paper_dir: <paper_dir>
source_path: <source_path 依 source_key 推得>
source_index: 0
clean_paper: /tmp/paper_clean.html
source_key: <source_key>
color_key: <color_key 依 source_key 推得>
output_path: <output_path 依 source_key 推得>
```

例：`source_key = l1` 時——
- `source_path = <paper_dir>/summary/canonical/summary.json`
- `output_path = <paper_dir>/summary/canonical/highlight_map.l1.json`
- `color_key = summary`

### Step 3：驗證 mapping

[mechanical] 跑檢查：

```bash
python3 - <<'PY'
import json
from pathlib import Path
hm = json.load(open("<output_path>"))
src = json.load(open("<source_path>"))["items"][<source_index>]
clean = Path("/tmp/paper_clean.html").read_text()
loc_text = {"main_line": src["main_line"]}
for i, p in enumerate(src["refined_final_output"]):
    loc_text[f"refined_{i}"] = p
errors = []
for p in hm["phrases"]:
    if p["summary_location"] not in loc_text:
        errors.append(f"{p['id']}: 未知 location {p['summary_location']}")
        continue
    if p["summary_text"] not in loc_text[p["summary_location"]]:
        errors.append(f"{p['id']}: summary_text 不在 {p['summary_location']}")
    for sn in p["paper_snippets"]:
        if sn["text"] not in clean:
            errors.append(f"{p['id']}/{sn['snippet_id']}: snippet 不在原文")
        if "<" in sn["text"] or ">" in sn["text"]:
            errors.append(f"{sn['snippet_id']}: snippet 含 <>")
phrases = len(hm["phrases"])
snippets = sum(len(p["paper_snippets"]) for p in hm["phrases"])
print(f"phrases={phrases}, snippets={snippets}, errors={len(errors)}")
for e in errors[:20]:
    print(" -", e)
assert not errors, f"{len(errors)} 個錯誤"
PY
```

任何錯誤 → 修正 prompt / 補充 context 後重跑 Step 2。

## 完成判定

- `highlight_map.<source_key>.json` 存在且通過 Step 3 sanity check。
- mapping 對應的摘要 / 原文沒有被改動（subagent 只寫 mapping JSON，不該動其他檔）。

## 後續

mapping JSON 完成後，跑 [highlight_apply_SKILL.md](highlight_apply_SKILL.md) 把螢光筆真的標到 paper HTML。多個 mapping（L1 + L2_m1 + L2_m2…）可以累積後一次套用。
