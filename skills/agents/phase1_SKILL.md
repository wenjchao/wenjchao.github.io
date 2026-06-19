# Phase 1 Pipeline

## 目標

輸入：`source.pdf`；或同一篇文章的多個 PDF（例如 main article + supplementary information）。輸出：`workspace/<paper_slug>/final/`（含 `<paper_slug>.html`、`figures/`、`<paper_slug>.md`）。

這是一條由 parent orchestrator 跑完的 paper reassembly pipeline。Parent 先根據論文內容命名 paper directory，建立 shared page assets，接著啟動四條 extraction lanes（figure / equation / table / text），四條 lane 全部 close 後，才啟動 reassembly lane。`reassembly/canonical/paper.html` 是 reviewed canonical working output；pipeline close 後，parent 另外在 `<paper_dir>/final/` 建立同捆包作為最終交付。

Parent 的責任邊界很窄：
- Parent 只做三種動作：`[script]` 跑固定 script、`[spawn agent]` 啟動 subagent、`[mechanical]` 搬檔或合併 JSON。
- 所有 scanner、worker、reviewer、merger 都必須由獨立 subagent 執行。Parent 不得取代。
- 所有 visual judgment 和內容判斷都由 subagent 做。Parent 不看圖、不判斷品質、不發明座標、不組裝段落、不清理文字、不決定 float 位置、不判斷忠實度。
- Parent 不得 override reviewer。只要 canonical review 有 `severity: "required"` finding，該 lane 就不能 close。

# 全域結構

## Paper Directory

每篇 paper 都有自己的 `<paper_dir>`，而且必須放在 `workspace/` 底下：`<paper_dir> = workspace/<paper_slug>`。所有 pipeline artifact、intermediate output、review output 和 final deliverables 都留在這個 directory 裡，不要散到 repo 其他位置。

Parent 先讀論文內容，取一個最多 5 個 English words 的簡潔 title，能概括整篇 paper。把這個 title 轉成 lowercase hyphenated `paper_slug`，只使用 `a-z`、`0-9` 和 `-`。例如 title `Electrochemical Sensor Review` 對應 `paper_slug = electrochemical-sensor-review`，`<paper_dir> = workspace/electrochemical-sensor-review`。

`canonical/` 是所有下游 agent 的唯一讀取來源；`round_00` 是 initial，`round_01` 是第一輪 repair，依此類推。舊 round 不覆寫。`<paper_dir>/final/` 同捆包只在 reassembly lane close 後建立，是最終交付，不是任何 reviewer 的輸入。

```text
workspace/
  <paper_slug>/
    final/                # 最終交付同捆包，reassembly close 後建立
      <paper_slug>.html   # copied from reassembly/canonical/paper.html, renamed
      figures/            # copied from reassembly/canonical/figures/
      <paper_slug>.md     # derived from the reviewed canonical HTML
    shared/
      source.pdf           # downstream 唯一來源；多 PDF 時是合併後的 PDF
      source_1.pdf         # optional, 原始輸入 1
      source_2.pdf         # optional, 原始輸入 2
      source_map.json      # optional, 記錄 source_N.pdf 對應到 source.pdf 的頁面範圍
      pages/              # 完整解析度頁面圖片
      previews/           # 受限尺寸 page previews
    figures/
      scanner/
        figure_plan.json
      worker/
        round_00/
          worker_01/
            figures.json
            crops/
            previews/
        round_01/
          worker_01/
      reviewer/
        round_00/
          reviewer_01/
            visual_review.json
        round_01/
          reviewer_01/
      canonical/
        figure_plan.json
        figures.json
        visual_review.json
        crops/
        previews/
    equations/
      scanner/
        equation_plan.json
        scanner_01/       # 平行 scanner 時的個別輸出
        scanner_02/
      worker/
        round_00/
          worker_01/
            equations.json
            crops/
            previews/
        round_01/
          worker_01/
      reviewer/
        round_00/
          reviewer_01/
            visual_review.json
        round_01/
          reviewer_01/
      canonical/
        equation_plan.json
        equations.json
        visual_review.json
        crops/
        previews/
    tables/
      scanner/
        table_plan.json
      worker/
        round_00/
          worker_01/
            tables.json
            crops/
            previews/
        round_01/
          worker_01/
      reviewer/
        round_00/
          reviewer_01/
            visual_review.json
        round_01/
          reviewer_01/
      canonical/
        table_plan.json
        tables.json
        visual_review.json
        crops/
        previews/
    text/
      scanner/
        extracted.json
      worker/
        round_00/
          worker_01/
            paragraphs.json
          worker_02/
            paragraphs.json
          worker_03/
            paragraphs.json
          merged/
            paragraphs.json
        round_01/
          worker_01/
      reviewer/
        round_00/
          reviewer_01/
            visual_review.json
          reviewer_02/
            visual_review.json
        round_01/
          reviewer_01/
      canonical/
        extracted.json
        paragraphs.json
        visual_review.json
    reassembly/
      worker/
        round_00/
          worker_01/
            paper.html
            figures/
        round_01/
          worker_01/
      reviewer/
        round_00/
          reviewer_01/
            visual_review.json
        round_01/
          reviewer_01/
      canonical/
        paper.html
        visual_review.json
        figures/
```

## Scripts

所有 script 都在 `agents/scripts/`。

| Script | 用途 | Lane |
|---|---|---|
| `render_pages.py` | PDF -> 完整解析度頁面圖片 | 全部 |
| `make_image_preview.py` | 頁面圖片 -> 受限尺寸 page preview | 全部 |
| `crop_and_preview.py` | 裁切 + evidence preview；subagent 呼叫 | figure, equation, table |
| `extract.py` | PDF -> 字詞層級文字 + 座標 | text |

## Subagent Prompt Contract

每個 scanner、worker、reviewer、merger 都用對應的 prompt file 啟動：
- Prompt = 指定 prompt 檔案全文 + 末尾附加 assignment block。
- Prompt 不得摘要、改寫、截斷。
- 啟動失敗時，parent 修正後重試。仍失敗則回報 blocked。

## Shared Setup

第一次處理 paper 時，parent 先決定 `paper_title` 和 `paper_slug`，再設定 `<paper_dir> = workspace/<paper_slug>`。不要在 `workspace/` 以外建立任何 paper artifact。若 `shared/pages/` 和 `shared/previews/` 已存在，可跳過 render/preview，只建立 lane 自己的目錄結構。

```bash
# <paper_dir> is workspace/<paper_slug>
mkdir -p <paper_dir>/shared/{pages,previews} \
  <paper_dir>/figures/{scanner,worker,reviewer,canonical} \
  <paper_dir>/equations/{scanner,worker,reviewer,canonical} \
  <paper_dir>/tables/{scanner,worker,reviewer,canonical} \
  <paper_dir>/text/{scanner,worker,reviewer,canonical} \
  <paper_dir>/reassembly/{worker,reviewer,canonical}

cp <source.pdf> <paper_dir>/shared/source.pdf

python3 agents/scripts/render_pages.py \
  "<paper_dir>/shared/source.pdf" "<paper_dir>/shared/pages" --dpi 300

for page in <paper_dir>/shared/pages/page_*.png; do
  base=$(basename "$page" .png)
  python3 agents/scripts/make_image_preview.py \
    "$page" "<paper_dir>/shared/previews/${base}_preview.png" --max-dim 1568
done
```

若使用者提供多個 PDF，且說明它們是同一篇文章（常見為 main article + supplementary information），parent 仍只建立一個 `<paper_dir>` 和一個最終輸出。做法是把原始檔保存在 `shared/source_1.pdf`、`shared/source_2.pdf`...，再機械合併為 downstream 唯一讀取的 `shared/source.pdf`，並寫出 `shared/source_map.json` 記錄每個 source 在合併 PDF 中的頁面範圍。後續 scanner/worker/reviewer assignment 都應附上 source_map 摘要。不要為 main article 和 supplement 分別建立 paper directory，也不要建立兩份 final HTML/Markdown。

## Gate 和 Repair Contract

每條 lane 的 gate 都只讀該 lane 的 `canonical/visual_review.json`。

- Close：所有 item 的 `findings` 都是空陣列。
- Repair：任何 item 有 `severity: "required"` finding。
- Blocked：repair round limit 達到，預設 4 輪。

Parent 不得用自己的判斷覆蓋 reviewer。Repair output 中仍有 fail item 時不得靜默 close。

Repair 只處理 required findings 對應的 item：
- figure / equation / table：只替換被修復的 item；沒被修復的 item 保持不動。
- text：repair worker 輸出完整 `paragraphs.json`，直接取代 canonical。
- reassembly：repair worker 輸出完整 `paper.html` 和 `figures/`，直接取代 canonical。

# Item Lanes：Figure / Equation / Table

Figure、equation、table 三條 lane 都是 item extraction lane：scanner 先產生 plan，worker 根據 plan 產生 extraction JSON 和 evidence，reviewer 審查 canonical evidence，gate 決定 close 或 repair。

## Lane 差異

| Lane | item id | Plan | Worker JSON | Review JSON | Scanner prompt | Worker prompt | Reviewer prompt |
|---|---|---|---|---|---|---|---|
| figure | `figure_id` | `figure_plan.json` | `figures.json` | `visual_review.json` | `subagent_prompts/figure_scanner.md` | `subagent_prompts/figure_worker.md` | `subagent_prompts/figure_reviewer.md` |
| equation | `equation_id` | `equation_plan.json` | `equations.json` | `visual_review.json` | `subagent_prompts/equation_scanner.md` | `subagent_prompts/equation_worker.md` | `subagent_prompts/equation_reviewer.md` |
| table | `table_id` | `table_plan.json` | `tables.json` | `visual_review.json` | `subagent_prompts/table_scanner.md` | `subagent_prompts/table_worker.md` | `subagent_prompts/table_reviewer.md` |

| Lane | Scan 範圍 | Worker 分組 | Reviewer 分組 | Crop mode | Promote 檔案規則 | Repair 刪除規則 |
|---|---|---|---|---|---|---|
| figure | 全部頁面，一個 scanner | 建議每組 <=3 張；不分組可 N=1 | 建議每組 <=3 張；不分組可 N=1 | full evidence | worker 的 `crops/`、`previews/` 可複製到 canonical | 對被修復的 `crop_id` 刪 `canonical/crops/{crop_id}*` 和 `canonical/previews/{crop_id}*` |
| equation | 建議每組 <=10 頁；可平行 scanner | 建議每組 <=10 個；不分組可 N=1 | 建議每組 <=10 個；不分組可 N=1 | `--boundary-only` | worker 的 `crops/`、`previews/` 可複製到 canonical | 對被修復的 `crop_id` 刪 `canonical/crops/{crop_id}*` 和 `canonical/previews/{crop_id}*` |
| table | 全部頁面，一個 scanner | 建議每組 <=3 張；不分組可 N=1 | 建議每組 <=3 張；不分組可 N=1 | `--boundary-only` | 只複製 `tables.json` 中 `crop_image` 和 `previews` 記錄的檔案，不整目錄複製，不用 glob | 只刪 `canonical/crops/{crop_id}.png`、`canonical/previews/{crop_id}_preview.png`、`canonical/previews/{crop_id}_boundary_preview.png`，不用 glob |

## Evidence Naming

Worker 必須把圖片路徑寫進主 JSON 的 `crop_units[].previews`，所有路徑都是 relative path。搬進 canonical 後 relative path 不變。Reviewer 直接從主 JSON 讀 evidence 路徑，不用推導或 glob。

`crop_and_preview.py` 的輸出命名：

| Lane | 檔案 | 路徑 |
|---|---|---|
| figure / equation / table | Final crop | `crops/{crop_id}.png` |
| figure / equation / table | Crop preview | `previews/{crop_id}_preview.png` |
| figure / equation / table | Boundary preview | `previews/{crop_id}_boundary_preview.png` |
| figure only | Edge band segments | `previews/{crop_id}_{top,bottom,left,right}_seg{N}_preview.png` |
| figure only | Bottom microzoom | `previews/{crop_id}_micro_bottom_seg{N}_preview.png` |

Equation 和 table 使用 `--boundary-only`，只產出 crop、crop preview、boundary preview，不產出 edge strips 和 microzoom。

## Step 1: Scan

Scanner 只產生 plan，不裁切、不產生 worker JSON。

### Figure scan

```text
---
## Assignment
paper_dir: <paper_dir>
output_root: <paper_dir>/figures/scanner
pages: 全部頁面
```

輸出：`<paper_dir>/figures/scanner/figure_plan.json`。

### Equation scan

把頁面分成 N 組，建議每組 <=10 頁。每個 scanner 各自從 `Equation_1` 開始編號。單一 scanner 時 `output_root` 直接用 `<paper_dir>/equations/scanner`；多 scanner 時使用 `scanner_01`、`scanner_02`。

```text
---
## Assignment
paper_dir: <paper_dir>
output_root: <paper_dir>/equations/scanner/scanner_01
pages: 1-10
```

多 scanner 完成後，parent 機械合併：
1. 讀取所有 `scanner_*/equation_plan.json`，concat `equations` 陣列。
2. 按 `(page, y1)` 排序，`y1` 取自 `crop_units[0].crop_px[1]`。
3. 重新指派全局 `equation_id`：`Equation_1`、`Equation_2`、...
4. `equation_number` 不變。
5. 寫入 `<paper_dir>/equations/scanner/equation_plan.json`，再複製到 `canonical/equation_plan.json`。
6. 不得有重複的 `equation_number`；同頁同 seq 的合成編號視為重複。

### Table scan

```text
---
## Assignment
paper_dir: <paper_dir>
output_root: <paper_dir>/tables/scanner
pages: 全部頁面
```

輸出：`<paper_dir>/tables/scanner/table_plan.json`。

## Step 2: Promote Plan

Scan 完成後，parent 把 plan 複製到 canonical，供 worker 讀取：

```text
figures/scanner/figure_plan.json     -> figures/canonical/figure_plan.json
equations/scanner/equation_plan.json -> equations/canonical/equation_plan.json
tables/scanner/table_plan.json       -> tables/canonical/table_plan.json
```

Equation lane 若已執行多 scanner 合併，Step 1 的合併結果已經複製到 canonical，不重複覆寫也可以。

## Step 3: Extract

Worker 讀 canonical plan，只處理 assignment 指定的 item ids。

### Figure worker

```text
---
## Assignment
paper_dir: <paper_dir>
mode: initial
worker_id: worker_01
output_root: <paper_dir>/figures/worker/round_00/worker_01
figure_ids: [Figure_1, Figure_2, Figure_3]
```

輸出：`figures.json`、`crops/`、`previews/`。

### Equation worker

```text
---
## Assignment
paper_dir: <paper_dir>
mode: initial
worker_id: worker_01
output_root: <paper_dir>/equations/worker/round_00/worker_01
equation_ids: [Equation_1, Equation_2, Equation_3]
```

輸出：`equations.json`、`crops/`、`previews/`。

### Table worker

```text
---
## Assignment
paper_dir: <paper_dir>
mode: initial
worker_id: worker_01
output_root: <paper_dir>/tables/worker/round_00/worker_01
table_ids: [Table_1, Table_2, Table_3]
```

輸出：`tables.json`、`crops/`、`previews/`。

## Step 4: Promote Extraction

Parent 機械 promote worker output：

1. 讀取所有 worker 主 JSON。
2. Concat item array（`figures` / `equations` / `tables`）。
3. 多 worker 時把頂層 `worker_id` 改成 `"merged"`。
4. 寫入 lane 的 canonical 主 JSON。
5. 不得靜默覆蓋另一個 item 或 crop id。

Figure / equation 的 crop promote：
- 把所有 worker 的 `crops/` 和 `previews/` 複製到 canonical。

Table 的 crop promote：
- 對每個 worker 的 `tables.json`，逐個讀 `crop_units[]`。
- 只複製 `crop_image` 和 `previews` 中記錄的檔案到 canonical。
- 不得整目錄複製，不得使用 glob。

## Step 5: Review

Reviewer 讀 canonical 主 JSON，並依各 lane prompt 使用對應 evidence：figure 主要看 page preview 和 canonical previews；equation / table 用 previews 判斷邊界與版面，並在精確符號、文字或數值判斷時讀 `shared/source.pdf`。Reviewer 輸出自己的 `visual_review.json`。多 reviewer 可以平行；repair 後只 re-review 被修復的 items，已 pass 的 items 保持不動。

三條 item lane 的 re-review 節奏一致：只把 `review_round` 和 `output_root` 換到下一輪，並把 ids 限縮到修復過的 items。Reviewer 不需要上一輪 review；item ids 就是 re-review 的範圍，evidence 來源仍沿用各 lane 的正常審查規則。

### Figure reviewer

```text
---
## Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
output_root: <paper_dir>/figures/reviewer/round_00/reviewer_01
figure_ids: [Figure_1, Figure_2, Figure_3]
```

### Equation reviewer

```text
---
## Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
output_root: <paper_dir>/equations/reviewer/round_00/reviewer_01
equation_ids: [Equation_1, Equation_2, Equation_3]
```

### Table reviewer

```text
---
## Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
output_root: <paper_dir>/tables/reviewer/round_00/reviewer_01
table_ids: [Table_1, Table_2, Table_3]
```

## Step 6: Promote Review

Parent 機械 promote review：

- 單一 reviewer：複製 reviewer 的 `visual_review.json` 到 canonical。
- 多 reviewer：concat item array（`figures` / `equations` / `tables`），頂層 `reviewer_id` 改成 `"merged"`，寫入 canonical。

Re-review 時只替換被修復 item 的 review entry；已 pass item 的 review entry 保持不動。

## Step 7: Gate

Parent 讀 canonical review：
- 所有 item 的 `findings` 都是空陣列 -> lane close。
- 有 `severity: "required"` finding -> 進入 repair。
- repair round limit 達到 -> blocked。

## Step 8: Repair

Repair worker 直接讀 canonical 主 JSON + canonical `visual_review.json`。Parent 不建立中間檔。

### Figure repair

```text
---
## Assignment
paper_dir: <paper_dir>
mode: repair
worker_id: worker_01
output_root: <paper_dir>/figures/worker/round_01/worker_01
figure_ids: [Figure_5, Figure_6, Figure_7]
```

Merge repair：
1. 對每個被修復的 `crop_id`，刪除 `canonical/crops/{crop_id}*` 和 `canonical/previews/{crop_id}*`。
2. 把 worker 新的 `crops/`、`previews/` 複製到 canonical。
3. 讀 worker `figures.json`，把對應 `figure_id` 的 entry 替換進 canonical `figures.json`。
4. 回到 review，只審查被修復的 figure ids。

### Equation repair

```text
---
## Assignment
paper_dir: <paper_dir>
mode: repair
worker_id: worker_01
output_root: <paper_dir>/equations/worker/round_01/worker_01
equation_ids: [Equation_3, Equation_5]
```

Merge repair：
1. 對每個被修復的 `crop_id`，刪除 `canonical/crops/{crop_id}*` 和 `canonical/previews/{crop_id}*`。
2. 把 worker 新的 `crops/`、`previews/` 複製到 canonical。
3. 讀 worker `equations.json`，把對應 `equation_id` 的 entry 替換進 canonical `equations.json`。
4. 回到 review，只審查被修復的 equation ids。

### Table repair

```text
---
## Assignment
paper_dir: <paper_dir>
mode: repair
worker_id: worker_01
output_root: <paper_dir>/tables/worker/round_01/worker_01
table_ids: [Table_3, Table_5]
```

Merge repair：
1. 對每個被修復的 `crop_id`，刪除 `canonical/crops/{crop_id}.png`、`canonical/previews/{crop_id}_preview.png`、`canonical/previews/{crop_id}_boundary_preview.png`。不要使用 `{crop_id}*` glob。
2. 對每個 worker 的 `tables.json`，只複製 `crop_image` 和 `previews` 中記錄的檔案到 canonical。不得整目錄複製或使用 glob。
3. 讀 worker `tables.json`，把對應 `table_id` 的 entry 替換進 canonical `tables.json`。
4. 回到 review，只審查被修復的 table ids。

# Text Lane

Text lane 從 PDF 擷取 word-level text，再由多個 workers 組裝段落，最後由唯一的 merger 合併。它是唯一有 merger 的 extraction lane。

## Prompts

| Prompt | 角色 |
|---|---|
| `subagent_prompts/text_scanner.md` | 從 PDF 擷取字詞層級文字 + 座標，產出 `extracted.json` |
| `subagent_prompts/text_worker.md` | 讀 `extracted.json` + source.pdf + page previews，組裝段落；同時用於 initial 和 repair |
| `subagent_prompts/text_merger.md` | 合併多個 worker 的 `paragraphs.json`，reconcile overlap 區域 |
| `subagent_prompts/text_reviewer.md` | 審查段落品質，產出 `visual_review.json` |

## Step 1: Scan

Text scanner 跑 `extract.py`，逐頁 QC，去除 `blocks` 後寫出 scanner output。

```text
---
## Assignment
paper_dir: <paper_dir>
output_root: <paper_dir>/text/scanner
```

輸出：`<paper_dir>/text/scanner/extracted.json`。

Promote：parent 把 `text/scanner/extracted.json` 複製到 `text/canonical/extracted.json`。

## Step 2: Assemble

Parent 決定 worker 分配。這是機械分配，不做段落組裝判斷。原則：
- 按 section 邊界切割；可讀 source.pdf 前幾頁確認章節結構。
- 每個 worker 分配 6-12 頁。
- 相鄰 worker 之間有 2-3 頁 overlap。
- References 頁面獨立成一個 worker。
- 每個 assignment 標明 `owned_pages` 和 `overlap_pages`。

典型 24 頁論文：
- `worker_01`: pages 1-8（owned: 1-6, overlap: 7-8）
- `worker_02`: pages 7-18（overlap: 7-8, owned: 9-16, overlap: 17-18）
- `worker_03`: pages 17-20（overlap: 17-18, 20; owned: 19）
- `worker_04`: pages 20-24（overlap: 20; owned: 21-24，references 專用）

Worker assignment：

```text
---
## Assignment
paper_dir: <paper_dir>
mode: initial
worker_id: worker_01
output_root: <paper_dir>/text/worker/round_00/worker_01
pages: [1, 2, 3, 4, 5, 6, 7, 8]
owned_pages: [1, 2, 3, 4, 5, 6]
overlap_pages: [7, 8]
```

每個 worker 組裝自己 `pages` 範圍內的所有段落，包含 overlap pages。Worker 不需要知道其他 worker 的存在。

## Step 3: Merge

所有 text workers 完成後，啟動 `text_merger`。

```text
---
## Assignment
paper_dir: <paper_dir>
output_root: <paper_dir>/text/worker/round_00/merged

workers:
  - worker_id: worker_01
    path: <paper_dir>/text/worker/round_00/worker_01/paragraphs.json
    pages: [1, 2, 3, 4, 5, 6, 7, 8]
    owned_pages: [1, 2, 3, 4, 5, 6]
    overlap_pages: [7, 8]
  - worker_id: worker_02
    path: <paper_dir>/text/worker/round_00/worker_02/paragraphs.json
    pages: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    owned_pages: [9, 10, 11, 12, 13, 14, 15, 16]
    overlap_pages: [7, 8, 17, 18]
  - worker_id: worker_03
    path: <paper_dir>/text/worker/round_00/worker_03/paragraphs.json
    pages: [17, 18, 19, 20]
    owned_pages: [19]
    overlap_pages: [17, 18, 20]
  - worker_id: worker_04
    path: <paper_dir>/text/worker/round_00/worker_04/paragraphs.json
    pages: [20, 21, 22, 23, 24]
    owned_pages: [21, 22, 23, 24]
    overlap_pages: [20]
```

Merger 在 overlap 區域選擇最佳版本，reconcile 邊界，重新編號，寫出 `<paper_dir>/text/worker/round_00/merged/paragraphs.json`。

Promote：parent 把 merger 的 `paragraphs.json` 複製到 `text/canonical/paragraphs.json`。

## Step 4: Review

Text review 可以多 reviewer 平行。每個 reviewer 審查「段落所在頁面落在其範圍內」的段落，coverage 檢查也按同樣頁面範圍。

```text
---
## Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
output_root: <paper_dir>/text/reviewer/round_00/reviewer_01
paragraph_ids: [1, 2, ..., 80]
```

也可用 `paragraph_ids: all` 審查全部段落。

Promote review：
- 單一 reviewer：複製到 `text/canonical/visual_review.json`。
- 多 reviewer：對每個段落取所有 reviewer findings 的 union；overlap 段落同一 condition + severity 的 finding 去重。
- 合併後的 `visual_review.json` 必須涵蓋所有段落（1 到 N）。

## Step 5: Gate

Parent 讀 `text/canonical/visual_review.json`：
- 所有段落 `findings` 都是空陣列 -> text lane close。
- 有 `severity: "required"` finding -> repair。
- round limit 達到 -> blocked。

## Step 6: Repair

Text repair worker 直接讀 canonical `paragraphs.json`、`extracted.json`、`visual_review.json`。`paragraph_ids` 來自 required findings；`null` 表示不屬於特定段落的問題，例如 missing_content。

```text
---
## Assignment
paper_dir: <paper_dir>
mode: repair
worker_id: worker_01
output_root: <paper_dir>/text/worker/round_01/worker_01
paragraph_ids: [28, 29, null]
```

Repair worker 輸出完整 `paragraphs.json`，不只修復段落，並在頂層包含 `modified_paragraphs`（新編號 list）。

Promote repair：parent 直接複製 repair worker 的 `paragraphs.json` 到 `text/canonical/paragraphs.json`，取代舊檔。

Re-review：只對 `modified_paragraphs` 做完整審查。Reviewer 輸出仍必須涵蓋 canonical 中所有段落；parent promote 後再 gate。

# Reassembly Lane

Reassembly lane 沒有 scanner。四條 extraction lanes 全部 close 後才啟動。四條 lane 的 canonical 對 reassembly 是只讀輸入。

Parent 在 reassembly lane 只做：
- `[spawn agent]` 啟動 worker / reviewer。
- `[mechanical]` promote `paper.html`、`figures/`、`visual_review.json`。

Parent 不清理文字、不決定 float 位置、不判斷忠實度。

## Prompts

| Prompt | 角色 |
|---|---|
| `subagent_prompts/reassembly_worker.md` | 讀四條 lane 的 canonical + source.pdf，組出 `paper.html` |
| `subagent_prompts/reassembly_reviewer.md` | 審查 `paper.html` 是否忠實於 PDF，產出 `visual_review.json` |

## Step 0: Prerequisite

確認四條 extraction lanes 都已 close：各自 `canonical/visual_review.json` 中沒有 `severity: "required"` findings。建立 `reassembly/{worker,reviewer,canonical}` 目錄。

## Step 1: Reassemble

```text
---
## Assignment
paper_dir: <paper_dir>
mode: initial
worker_id: worker_01
output_root: <paper_dir>/reassembly/worker/round_00/worker_01
```

Worker 讀四條 lane 的 canonical + source.pdf，寫出 `paper.html` 和 `figures/`。

Promote：parent 把 worker 的 `paper.html` 和 `figures/` 複製到 `reassembly/canonical/`。

## Step 2: Review

```text
---
## Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
output_root: <paper_dir>/reassembly/reviewer/round_00/reviewer_01
```

Reviewer 讀 `reassembly/canonical/paper.html`，對照 source.pdf，寫出 `visual_review.json`。

Promote：parent 把 reviewer 的 `visual_review.json` 複製到 `reassembly/canonical/visual_review.json`。

## Step 3: Gate

Parent 讀 `reassembly/canonical/visual_review.json`：
- `findings` 為空 -> reassembly lane close，進入 final package。
- 有 `severity: "required"` finding -> repair。
- round limit 達到 -> blocked。

## Step 4: Final Package

只有 reassembly lane close 後，parent 才建立 `<paper_dir>/final/` 同捆包。HTML 和 `figures/` 是一組，必須一起搬移：
- 複製 `reassembly/canonical/paper.html` 到 `<paper_dir>/final/<paper_slug>.html`。檔名改成 `<paper_slug>` 讓交付檔自我識別；內容不動，`figures/` 相對路徑仍指向同層。
- 複製 `reassembly/canonical/figures/` 到 `<paper_dir>/final/figures/`。
- 從 reviewed canonical HTML 建立 `<paper_dir>/final/<paper_slug>.md`，保留原文順序、標題、段落、方程式、表格和圖片引用；不得趁轉換時修文、補內容或重新審查。

`reassembly/canonical/` 保持原狀。`final/` 不是任何 reviewer 的輸入。若無法可靠建立同捆包，pipeline 不算 Done，必須回報 blocked。Repair 後再次 close 必須重新產生 `final/`，避免交付落後於 canonical。

## Step 5: Repair

```text
---
## Assignment
paper_dir: <paper_dir>
mode: repair
worker_id: worker_01
output_root: <paper_dir>/reassembly/worker/round_01/worker_01
```

Repair worker 讀 `reassembly/canonical/paper.html` + `reassembly/canonical/visual_review.json`，根據 findings 修正 `paper.html`。

Promote repair：parent 把 worker 的 `paper.html` 和 `figures/` 覆蓋 `reassembly/canonical/`。

回到 Step 2 做 re-review。

# 整體流程

1. **Setup**：根據 paper 內容取最多 5 個 English words 的 title，轉成 `paper_slug`，建立 `workspace/<paper_slug>`，複製 `source.pdf`、render pages、建立 page previews。
2. **Extraction lanes**：figure、equation、table、text 可平行啟動。每條 lane 自己跑 scan -> extract/assemble -> review -> gate -> repair loop。
3. **Extraction close**：四條 extraction lanes 的 canonical reviews 都沒有 required findings。
4. **Reassembly lane**：worker -> review -> gate -> repair loop。
5. **Final package**：建立 `<paper_dir>/final/` 同捆包（`<paper_slug>.html` + `figures/` + `<paper_slug>.md`）。
6. **Done**：`<paper_dir>/final/` 是最終交付；`<paper_dir>/reassembly/canonical/` 是保留的 canonical working output。

`canonical/` 是每個 downstream agent 的唯一讀取來源。任何 round output 必須先通過 parent 的 mechanical promote，才會成為下一步可讀狀態。
