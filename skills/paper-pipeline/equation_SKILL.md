# 目標

這是一份給 pipeline orchestrator 看的指引。

此流程使用場景與目標：
- 輸入：一個 PDF 檔案。
- 輸出：後續可重組成 HTML / Markdown 的 lane artifacts。
- 目標：最大程度讓輸出的 HTML / Markdown 貼近原始 PDF，以利後續閱讀、分析與筆記。

本檔案描述 equation lane。

# 結構

## 目錄結構

```text
<paper_dir>/
  shared/
    source.pdf
    pages/              # 完整解析度頁面圖片
    previews/           # 受限尺寸 page previews
  equations/
    scanner/            # scanner 輸出（合併版）
      equation_plan.json
      scanner_01/       # 平行 scanner 時的個別輸出
      scanner_02/
    worker/             # worker 輸出
      round_00/
        worker_01/
          equations.json
          crops/
          previews/
      round_01/
        worker_01/
    reviewer/           # reviewer 輸出
      round_00/
        reviewer_01/
          visual_review.json
      round_01/
        reviewer_01/
    canonical/          # live state — 所有 downstream agent 的唯一讀取來源
      equation_plan.json
      equations.json
      visual_review.json
      crops/
      previews/
```

`canonical/` 是所有下游 agent 的唯一 handoff root。

### Round 命名

- `worker/round_00/` + `reviewer/round_00/`：initial extraction + 第一次 review。
- `worker/round_01/` + `reviewer/round_01/`：修 round_00 review 發現的問題 + re-review。
- 依此類推。不覆寫舊 round。

## 工具

所有 script 在 `skills/hand-written-pipeline/scripts/`。

| Script | 用途 |
|---|---|
| `render_pages.py` | PDF → 完整解析度頁面圖片 |
| `make_image_preview.py` | 頁面圖片 → 受限尺寸 page preview |
| `crop_and_preview.py` | equation 裁切 + evidence preview（`--boundary-only` mode，subagent 呼叫） |

不需要 promote、merge、divide 等 orchestration script。Parent 直接搬檔和組裝 JSON。

## Subagent prompts

| Prompt | 角色 |
|---|---|
| `subagent_prompts/equation_scanner.md` | 掃描 page previews，辨識所有數學表達式（displayed + inline），產出 equation_plan.json |
| `subagent_prompts/equation_worker.md` | 讀 equation_plan.json，裁切 + LaTeX 轉寫 + 驗證，產出 equations.json + crops/ + previews/。同時用於 initial extraction 和 repair。 |
| `subagent_prompts/equation_reviewer.md` | 讀 canonical equations.json，視覺審查指定的 equations（邊界 + LaTeX），產出 visual_review.json |

## 圖片路徑

Worker 產出的所有圖片路徑寫進 `equations.json` 的 `crop_units[].previews`（relative path）。搬進 canonical 後 relative path 不變。Reviewer 直接從 `equations.json` 讀取路徑，不需要推導或 glob。

`crop_and_preview.py` 遵循以下命名慣例產出檔案：

| 檔案 | 路徑 |
|---|---|
| Final crop | `crops/{crop_id}.png` |
| Crop preview | `previews/{crop_id}_preview.png` |
| Boundary preview | `previews/{crop_id}_boundary_preview.png` |

Equation lane 使用 `--boundary-only` mode：只產出 crop + crop preview + boundary preview，不產出 edge strips 和 microzoom。

# 流程

Pipeline 是 scan → crop → review → repair loop。

Parent 只做三種動作：
- **[script]** 跑 render/preview script（機械操作）
- **[spawn agent]** 啟動 subagent（委派視覺判斷）
- **[mechanical]** 搬檔或組裝 JSON（不需判斷）

所有 visual judgment 由 subagent 做。Parent 不看圖、不判斷 crop 品質、不發明座標。

Subagent 規則：
- 所有 scanner、worker、reviewer 都要啟動獨立 subagent。不得用 parent 的工作取代 subagent。
- Subagent prompt 必須使用指定的 prompt 檔案全文，不得摘要、改寫、截斷。Parent 唯一可以做的修改是在末尾附加 assignment block。
- Agent 啟動失敗 → 先修正 prompt/tool/context，重試。仍失敗 → 回報 blocked。

## Step 0: 前置工作

**[script]** 建立 paper directory，render pages，建立 page previews。

```bash
mkdir -p <paper_dir>/shared/pages <paper_dir>/shared/previews \
  <paper_dir>/equations/{scanner,worker,reviewer,canonical}

cp <source.pdf> <paper_dir>/shared/source.pdf

python3 skills/hand-written-pipeline/scripts/render_pages.py \
  "<paper_dir>/shared/source.pdf" "<paper_dir>/shared/pages" --dpi 300

# 為每頁建立 preview
for page in <paper_dir>/shared/pages/page_*.png; do
  base=$(basename "$page" .png)
  python3 skills/hand-written-pipeline/scripts/make_image_preview.py \
    "$page" "<paper_dir>/shared/previews/${base}_preview.png" --max-dim 1568
done
```

如果 shared/ 已由其他 lane（如 figure lane）建立，跳過 render，直接建立 `equations/` 目錄結構。

## Step 1: Scan

把頁面分成 N 組（建議每組 ≤10 頁；不分組時 N=1）。對每組啟動一個 scanner。

### 1a. [spawn agent] 啟動 equation_scanner（可平行）

Prompt = `equation_scanner.md` 全文 + assignment block：

```text
---
## Assignment
paper_dir: <paper_dir>
output_root: <paper_dir>/equations/scanner/scanner_01
pages: 1-10
```

每個 scanner 讀自己負責的 page previews，寫出 `<paper_dir>/equations/scanner/scanner_01/equation_plan.json`。多個 scanner 時 IN PARALLEL 執行。每個 scanner 各自從 `Equation_1` 開始編號。

單一 scanner 時 output_root 直接用 `<paper_dir>/equations/scanner`。

### 1b. [mechanical] 合併 scanner 輸出

多個 scanner 時，parent 合併所有 `equation_plan.json`：

1. 讀取所有 scanner 的 `equation_plan.json`，concat `equations` 陣列。
2. 按 `(page, y1)` 排序（`y1` 取自 `crop_units[0].crop_px[1]`）。
3. 重新指派全局 `equation_id`：`Equation_1`、`Equation_2`、...。`equation_number` 不變。
4. 寫入 `<paper_dir>/equations/scanner/equation_plan.json`（合併版）。
5. 複製到 `canonical/equation_plan.json`。

不得有重複的 `equation_number`（同頁同 seq 的合成編號視為重複）。

## Step 2: Crop + LaTeX

### 2a. [spawn agent] 啟動 equation_worker

把 equation_ids 分成 N 組（建議每組 ≤10 個；不分組時 N=1）。對每組啟動一個 worker：

```text
---
## Assignment
paper_dir: <paper_dir>
mode: initial
worker_id: worker_01
output_root: <paper_dir>/equations/worker/round_00/worker_01
equation_ids: [Equation_1, Equation_2, Equation_3]
```

每個 worker 讀 `canonical/equation_plan.json`，只處理自己的 `equation_ids`，裁切 + 轉寫 LaTeX + 驗證，寫出 `equations.json`、`crops/`、`previews/`。多個 worker 時 IN PARALLEL 執行。

### 2b. [mechanical] Promote to canonical

1. 把 `scanner/equation_plan.json` 複製到 `canonical/`（只在 round_00，且 Step 1b 未執行時）。
2. 把所有 worker 的 `crops/`、`previews/` 複製到 `canonical/`。
3. 讀取所有 worker 的 `equations.json`，concat `equations` 陣列，寫入 `canonical/equations.json`（多個 worker 時 `worker_id` 改為 `"merged"`）。

不得靜默覆蓋另一個 equation 或 crop id。

## Step 3: Review

### 3a. [spawn agent] 啟動 equation_reviewer

把 equation_ids 分成 N 組（建議每組 ≤10 個；不分組時 N=1）。對每組啟動一個 reviewer：

```text
---
## Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
output_root: <paper_dir>/equations/reviewer/round_00/reviewer_01
equation_ids: [Equation_1, Equation_2, Equation_3]
```

每個 reviewer 讀 `canonical/equations.json`，只審查自己的 `equation_ids`，用 previews 審查邊界品質，並讀 `shared/source.pdf` 確認精確符號和 LaTeX 正確性，寫出 `visual_review.json`。多個 reviewer 時 IN PARALLEL 執行。Repair 後的 re-review 只審查被修復的 equations——已 pass 的 equations 保持不動；`equation_ids` 就是 re-review 範圍。

### 3b. [mechanical] Promote review to canonical

1. 讀取所有 reviewer 的 `visual_review.json`，concat `equations` 陣列，寫入 `canonical/visual_review.json`（多個 reviewer 時 `reviewer_id` 改為 `"merged"`）。

## Step 4: Gate

**[mechanical]** Parent 讀 `canonical/visual_review.json`：

- 所有 equation 的 `findings` 都是空陣列 → equation lane close。
- 有 `severity: "required"` 的 findings → 進入 Step 5。
- Repair round limit 達到（預設 4 輪）→ 停止並回報 blocked。

Parent 不得自己做 visual judgment 來 override reviewer。Repair output 有 fail equation 時不得靜默 close。

## Step 5: Repair

Worker 直接從 canonical 讀取 `equations.json` + `visual_review.json`，不需要 parent 建立中間檔案。

### 5a. [spawn agent] 啟動 equation_worker（repair mode）

Parent 從 `canonical/visual_review.json` 取出有 `severity: "required"` finding 的 equation_ids，分成 N 組（建議每組 ≤3 個）。對每組啟動一個 worker：

```text
---
## Assignment
paper_dir: <paper_dir>
mode: repair
worker_id: worker_01
output_root: <paper_dir>/equations/worker/round_01/worker_01
equation_ids: [Equation_3, Equation_5]
```

每個 worker 讀 `canonical/equations.json` 取得 metadata + current crop_px + current latex，讀 `canonical/visual_review.json` 取得 findings 作為 defects（邊界問題或 LaTeX 問題），針對已知問題修正，驗證修復。多個 worker 時 IN PARALLEL 執行。

### 5b. [mechanical] Merge repair to canonical

只更新被修復的 equation，沒被修復的保持不動：

1. 對每個被修復的 crop_id，先刪除 `canonical/crops/{crop_id}*` 和 `canonical/previews/{crop_id}*`（清掉舊 segment 檔案，避免殘留）。
2. 把所有 worker 的 `crops/`、`previews/` 複製到 `canonical/`。
3. 讀取所有 worker 的 `equations.json`，把每個 equation entry 替換進 `canonical/equations.json` 對應的 `equation_id`。

### 5c. 回到 Step 3

回到 Step 3，只對被修復的 equation_ids 啟動 reviewer。已 pass 的 equations 不重新審查。下一輪 review 寫到 `<paper_dir>/equations/reviewer/round_01/`。
