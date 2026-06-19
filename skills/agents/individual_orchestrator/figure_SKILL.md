# 目標

這是一份給 pipeline orchestrator 看的指引。

此流程使用場景與目標：
- 輸入：一個 PDF 檔案。
- 輸出：後續可重組成 HTML / Markdown 的 lane artifacts。
- 目標：最大程度讓輸出的 HTML / Markdown 貼近原始 PDF，以利後續閱讀、分析與筆記。

目前只實作 figure lane。

# 結構

## 目錄結構

```text
<paper_dir>/
  shared/
    source.pdf
    pages/              # 完整解析度頁面圖片
    previews/           # 受限尺寸 page previews
  figures/
    scanner/            # scanner 輸出
      figure_plan.json
    worker/             # worker 輸出
      round_00/         # initial extraction
        worker_01/
          figures.json
          crops/
          previews/
        worker_02/      # 平行時
      round_01/         # 第一輪 repair
        worker_01/
    reviewer/           # reviewer 輸出
      round_00/
        reviewer_01/
          visual_review.json
      round_01/
        reviewer_01/
    canonical/          # live state — 所有 downstream agent 的唯一讀取來源
      figure_plan.json
      figures.json
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

所有 script 在 `agents/scripts/`。

| Script | 用途 |
|---|---|
| `render_pages.py` | PDF → 完整解析度頁面圖片 |
| `make_image_preview.py` | 頁面圖片 → 受限尺寸 page preview |
| `crop_and_preview.py` | figure 裁切 + 全套 evidence preview（subagent 呼叫） |

不需要 promote、merge、divide、build_review_packet、build_repair_request 等 orchestration script。Parent 直接搬檔和組裝 JSON。

## Subagent prompts

| Prompt | 角色 |
|---|---|
| `subagent_prompts/figure_scanner.md` | 掃描 page previews，辨識所有 figure，產出 figure_plan.json |
| `subagent_prompts/figure_worker.md` | 讀 figure_plan.json，裁切 + 驗證，產出 figures.json + crops/ + previews/。同時用於 initial extraction 和 repair。 |
| `subagent_prompts/figure_reviewer.md` | 讀 canonical figures.json，視覺審查指定的 figures，產出 visual_review.json |

## 圖片路徑

Worker 產出的所有圖片路徑寫進 `figures.json` 的 `crop_units[].previews`（relative path）。搬進 canonical 後 relative path 不變。Reviewer 直接從 `figures.json` 讀取路徑，不需要推導或 glob。

`crop_and_preview.py` 遵循以下命名慣例產出檔案：

| 檔案 | 路徑 |
|---|---|
| Final crop | `crops/{crop_id}.png` |
| Crop preview | `previews/{crop_id}_preview.png` |
| Boundary preview | `previews/{crop_id}_boundary_preview.png` |
| Edge band segments | `previews/{crop_id}_{top,bottom,left,right}_seg{N}_preview.png` |
| Bottom microzoom | `previews/{crop_id}_micro_bottom_seg{N}_preview.png` |

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
  <paper_dir>/figures/{scanner,worker,reviewer,canonical}

cp <source.pdf> <paper_dir>/shared/source.pdf

python3 agents/scripts/render_pages.py \
  "<paper_dir>/shared/source.pdf" "<paper_dir>/shared/pages" --dpi 300

# 為每頁建立 preview
for page in <paper_dir>/shared/pages/page_*.png; do
  base=$(basename "$page" .png)
  python3 agents/scripts/make_image_preview.py \
    "$page" "<paper_dir>/shared/previews/${base}_preview.png" --max-dim 1568
done
```

## Step 1: Scan

### 1a. [spawn agent] 啟動 figure_scanner

Prompt = `figure_scanner.md` 全文 + assignment block：

```text
---
## Assignment
paper_dir: <paper_dir>
output_root: <paper_dir>/figures/scanner
pages: 全部頁面
```

Scanner 讀 page previews，寫出 `<paper_dir>/figures/scanner/figure_plan.json`。

## Step 2: Crop

### 2a. [spawn agent] 啟動 figure_worker

把 figure_ids 分成 N 組（建議每組 ≤3 張；不分組時 N=1）。對每組啟動一個 worker：

```text
---
## Assignment
paper_dir: <paper_dir>
mode: initial
worker_id: worker_01
output_root: <paper_dir>/figures/worker/round_00/worker_01
figure_ids: [Figure_1, Figure_2, Figure_3]
```

每個 worker 讀 `canonical/figure_plan.json`，只處理自己的 `figure_ids`，寫出 `figures.json`、`crops/`、`previews/`。多個 worker 時 IN PARALLEL 執行。

### 2b. [mechanical] Promote to canonical

1. 把 `scanner/figure_plan.json` 複製到 `canonical/`（只在 round_00）。
2. 把所有 worker 的 `crops/`、`previews/` 複製到 `canonical/`。
3. 讀取所有 worker 的 `figures.json`，concat `figures` 陣列，寫入 `canonical/figures.json`（多個 worker 時 `worker_id` 改為 `"merged"`）。

不得靜默覆蓋另一個 figure 或 crop id。

## Step 3: Review

### 3a. [spawn agent] 啟動 figure_reviewer

把 figure_ids 分成 N 組（建議每組 ≤3 張；不分組時 N=1）。對每組啟動一個 reviewer：

```text
---
## Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
output_root: <paper_dir>/figures/reviewer/round_00/reviewer_01
figure_ids: [Figure_1, Figure_2, Figure_3]
```

每個 reviewer 讀 `canonical/figures.json`，只審查自己的 `figure_ids`，從 `crop_units[].previews` 取得 evidence 路徑，寫出 `visual_review.json`。多個 reviewer 時 IN PARALLEL 執行。Repair 後的 re-review 只審查被修復的 figures——已 pass 的 figures 保持不動。

### 3b. [mechanical] Promote review to canonical

1. 讀取所有 reviewer 的 `visual_review.json`，concat `figures` 陣列，寫入 `canonical/visual_review.json`（多個 reviewer 時 `reviewer_id` 改為 `"merged"`）。

## Step 4: Gate

**[mechanical]** Parent 讀 `canonical/visual_review.json`：

- 所有 figure 的 `findings` 都是空陣列 → figure lane close。
- 有 `severity: "required"` 的 findings → 進入 Step 5。
- Repair round limit 達到（預設 4 輪）→ 停止並回報 blocked。

Parent 不得自己做 visual judgment 來 override reviewer。Repair output 有 fail figure 時不得靜默 close。

## Step 5: Repair

Worker 直接從 canonical 讀取 `figures.json` + `visual_review.json`，不需要 parent 建立中間檔案。

### 5a. [spawn agent] 啟動 figure_worker（repair mode）

Parent 從 `canonical/visual_review.json` 取出有 `severity: "required"` finding 的 figure_ids，分成 N 組（建議每組 ≤3 張）。對每組啟動一個 worker：

```text
---
## Assignment
paper_dir: <paper_dir>
mode: repair
worker_id: worker_01
output_root: <paper_dir>/figures/worker/round_01/worker_01
figure_ids: [Figure_5, Figure_6, Figure_7]
```

每個 worker 讀 `canonical/figures.json` 取得 metadata + current crop_px，讀 `canonical/visual_review.json` 取得 findings 作為 defects，針對已知問題調整 crop_px，驗證修復。多個 worker 時 IN PARALLEL 執行。

### 5b. [mechanical] Merge repair to canonical

只更新被修復的 figure，沒被修復的保持不動：

1. 對每個被修復的 crop_id，先刪除 `canonical/crops/{crop_id}*` 和 `canonical/previews/{crop_id}*`（清掉舊 segment 檔案，避免殘留）。
2. 把所有 worker 的 `crops/`、`previews/` 複製到 `canonical/`。
3. 讀取所有 worker 的 `figures.json`，把每個 figure entry 替換進 `canonical/figures.json` 對應的 `figure_id`。

### 5c. 回到 Step 3

回到 Step 3，只對被修復的 figure_ids 啟動 reviewer。已 pass 的 figures 不重新審查。下一輪 review 寫到 `<paper_dir>/figures/reviewer/round_01/`。
