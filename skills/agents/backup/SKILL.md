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
    pages/              # 完整解析度頁面圖片（render_pages.py 產生）
    previews/           # 受限尺寸 page previews（make_image_preview.py 產生）
  figures/              # figure lane
    workers/worker_01/
    canonical/
    reviewers/
    repairs/
  equations/            # equation lane
    workers/worker_01/
    canonical/
    reviewers/
    repairs/
  tables/               # table lane
    workers/worker_01/
    canonical/
    reviewers/
    repairs/
```

每個 lane 的內部結構相同：`workers/` 放 extractor 輸出，`canonical/` 放 live state，`reviewers/` 和 `repairs/` 放 per-round trace。

### Canonical 只放 live state

`canonical/` 是所有下游 agent 的唯一 handoff root。裡面只有：

- `figures.json`：唯一的 extraction manifest。Repair 的唯一 patch 對象。
- `visual_review.json`：最新一輪 review（每輪覆寫）。Gate 和 build_repair_request 讀這個。
- `crops/`：final crop 圖片。
- `previews/`：所有 evidence previews（crop preview、boundary preview、edge strips、bottom band、bottom micro）。

不進 canonical 的東西：`figure_decisions.json`（planning trace，留在 workers）、`review_packet.json`（留在 reviewers/）、`repair_requests_merged.json`（留在 repairs/）。

### Round 命名

- `reviewers/round_00/`：審 extraction promote 後的 canonical。
- `repairs/round_01/`：修 round_00 review 發現的問題。
- `reviewers/round_01/`：審 round_01 repair merge 後的 canonical。
- 依此類推。不覆寫舊的 review 或 repair 工作目錄。

### Artifact root 相對路徑

Figure lane JSON 裡的 artifact path 都使用 artifact root 相對路徑：

- Extractor / validator：artifact root 是 `workers/worker_01/`
- Reviewer / repair：artifact root 是 `canonical/`
- Repair output：`repair_output` 以 `repairs/round_N/repair_ID/` 為 root；`canonical_target` 以 `canonical/` 為 root

不要在 artifact path 裡寫完整的 `figures/canonical/` 或絕對路徑。Shared page paths（`shared/pages/page_3.png`）使用 paper-dir-relative path。

## 工具

所有 script 放在 `agents/scripts/`。

### Subagent 工具（extractor / reviewer / repair 呼叫）

| Script | 使用者 | 用途 |
|---|---|---|
| `crop_and_preview.py` | extractor, repair | 一次完成 figure 裁切 + 全套 evidence preview |
| `crop_region.py` | extractor, reviewer (fallback) | 單次裁切（source region、reviewer fallback context） |
| `make_image_preview.py` | extractor | 單張 preview（source region preview） |
| `make_edge_previews.py` | repair | 單邊 edge strip（regenerate_missing_preview action） |
| `build_repair_report.py` | repair | 從 decisions.json 自動組裝 repair_report.json |
| `build_manifest_patches.py` | repair (via build_repair_report) | 從 canonical 讀 old_value 產生 manifest patches |
| `validate_figure_extraction.py` | extractor | 檢查 extractor output contract |
| `validate_figure_review.py` | reviewer | 檢查 reviewer output contract |
| `validate_figure_repair.py` | repair | 檢查 repair output contract |

### Orchestration 工具（parent 呼叫）

| Script | 用途 |
|---|---|
| `render_pages.py` | PDF → 完整解析度頁面圖片 |
| `make_image_preview.py` | 頁面圖片 → 受限尺寸 page preview |
| `promote_to_canonical.py` | 搬檔到 canonical |
| `build_review_packet.py` | 從 canonical figures.json 產生 review packet |
| `check_review_gate.py` | 讀 visual_review.json，回傳 exit code |
| `build_repair_request.py` | 從 visual_review.json 產生 repair requests |
| `merge_repair.py` | 套用 repair report 的 file_copies + manifest_patches 到 canonical |
| `divide_review_packet.py` | 分割 review packet 給 N 個 reviewer（parallel） |
| `merge_reviews.py` | 合併 N 份 visual_review.json |
| `divide_repair_requests.py` | 分割 repair requests 給 N 個 repair worker（parallel） |
| `merge_repair_reports.py` | 合併 N 份 repair_report.json（含 path rewriting） |

## JSON Schema

所有 JSON 格式定義在 `agents/schemas/`：

| Schema | 產生者 | 消費者 |
|---|---|---|
| `figure_candidates.schema.md` | extractor | extractor（self-reference） |
| `figure_index.schema.md` | extractor | extractor |
| `figure_decisions.schema.md` | extractor | —（planning trace） |
| `figures.schema.md` | extractor, repair (via merge) | reviewer, repair, build_review_packet |
| `review_packet.schema.md` | build_review_packet.py | reviewer |
| `visual_review.schema.md` | reviewer | check_review_gate, build_repair_request |
| `repair_request.schema.md` | build_repair_request.py | repair |
| `repair_report.schema.md` | build_repair_report.py | merge_repair |

# 流程

Pipeline 是一個 extract → review → repair loop。

Parent 只做三種動作：
- **[script]** 跑 orchestration script（機械操作，不需判斷）
- **[spawn agent]** 啟動 subagent（委派視覺判斷）
- **[judgment]** 讀 exit code 決定下一步（簡單分支邏輯）

所有 visual judgment 由 subagent 做。Parent 不看圖、不判斷 crop 品質、不發明座標。

## Step 0: 前置工作

**[script]** 建立 paper directory，render pages，建立 page previews。

```bash
# 建立目錄結構
mkdir -p <paper_dir>/shared/pages <paper_dir>/shared/previews \
  <paper_dir>/figures/{workers,canonical,reviewers,repairs}

# 複製 PDF
cp <source.pdf> <paper_dir>/shared/source.pdf

# Render 完整解析度頁面圖片
python3 agents/scripts/render_pages.py \
  "<paper_dir>/shared/source.pdf" "<paper_dir>/shared/pages" --dpi 300

# 為每頁建立 preview
python3 agents/scripts/make_image_preview.py \
  "<paper_dir>/shared/pages/page_N.png" "<paper_dir>/shared/previews/page_N_preview.png" \
  --max-dim 1568
```

這是所有 lane 共用的前置工作，不屬於 figure lane。

## Step 1: Extraction

### 1a. [spawn agent] 啟動 figure_extractor

Prompt = `agents/subagent_prompts/figure_extractor.md` 全文 + assignment block：

```text
---
## Assignment
paper_dir: <paper_dir>
worker_id: worker_01
output_root: <paper_dir>/figures/workers/worker_01
artifact_root: <paper_dir>/figures/workers/worker_01
pages: 全部頁面
```

Extractor 寫出 `workers/worker_01/`（含 figure_candidates.json、figure_index.json、figure_decisions.json、figures.json、crops/、previews/、source_regions/、boundaries/）。

Extractor 在完成前會自己跑 `validate_figure_extraction.py`。

### 1b. [script] Promote to canonical

```bash
python3 agents/scripts/promote_to_canonical.py \
  --source <paper_dir>/figures/workers/worker_01 \
  --canonical <paper_dir>/figures/canonical \
  --mode extraction
```

搬 `figures.json`、`crops/`、`previews/`。不搬 `figure_decisions.json`（planning trace）、`figure_candidates.json`、`figure_index.json`、`source_regions/`、`boundaries/`。

## Step 2: Review

### 2a. [script] 建立 review packet

```bash
python3 agents/scripts/build_review_packet.py \
  "<paper_dir>/figures/canonical/figures.json" \
  --review-round round_00 \
  --output "<paper_dir>/figures/reviewers/round_00/reviewer_01/review_packet.json"
```

格式見 `schemas/review_packet.schema.md`。不進 canonical。

### 2b. [spawn agent] 啟動 figure_reviewer

Prompt = `agents/subagent_prompts/figure_reviewer.md` 全文 + assignment block：

```text
---
## Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
canonical_artifact_root: <paper_dir>/figures/canonical
output_root: <paper_dir>/figures/reviewers/round_00/reviewer_01
review_packet: <paper_dir>/figures/reviewers/round_00/reviewer_01/review_packet.json
scope: review_packet.json 中的全部 figures
```

Reviewer 讀 canonical evidence，寫出 `visual_review.json`。Reviewer 在完成前會自己跑 `validate_figure_review.py`。

#### Parallel review（可選）

建議每個 reviewer 負責 3 個 figures 左右。

```bash
# 分割
python3 agents/scripts/divide_review_packet.py \
  <full_review_packet.json> --workers N --output-dir reviewers/round_00

# 啟動 N 個 reviewer subagents IN PARALLEL（每個用不同的 reviewer_id 和 review_packet）

# 合併
python3 agents/scripts/merge_reviews.py \
  reviewer_01/visual_review.json reviewer_02/visual_review.json ... \
  --review-round round_00 --output reviewers/round_00/merged/visual_review.json
```

任何一個 reviewer 失敗 → 不 merge，回報 blocked。不嘗試 partial merge。

### 2c. [script] Promote review to canonical

```bash
python3 agents/scripts/promote_to_canonical.py \
  --source <paper_dir>/figures/reviewers/round_00/reviewer_01 \
  --canonical <paper_dir>/figures/canonical \
  --mode review
```

Parallel mode 時 source 改為 `reviewers/round_00/merged`。覆寫 `canonical/visual_review.json`。

## Step 3: Gate

### 3a. [script] 讀 gate

```bash
python3 agents/scripts/check_review_gate.py \
  "<paper_dir>/figures/canonical/visual_review.json"
```

### 3b. [judgment] 決定下一步

| Exit code | 意義 | 動作 |
|---|---|---|
| 0 | pass | Figure lane close。 |
| 1 | needs_repair | 進入 Step 4。 |
| 2 | blocked | 停止並回報（repair round limit、human_check、異常）。 |

預設最多 4 個 repair rounds。Parent 不得自己做 visual judgment 來 override reviewer。

## Step 4: Repair

### 4a. [script] 建立 repair request

```bash
python3 agents/scripts/build_repair_request.py \
  "<paper_dir>/figures/canonical/visual_review.json" \
  --repair-round round_01 \
  --output "<paper_dir>/figures/repairs/round_01/repair_requests_merged.json"
```

機械轉換 required findings → repair requests（只轉換 `severity == "required"` 的 findings）。轉換規則：

- `repair_hint` → `action`：`expand_*`/`shrink_*`/`recrop`/`split_crop`/`merge_crop` → `recrop`；`regenerate_preview` → `regenerate_missing_preview`；`manifest_check` → `manifest_correction`；`human_check` → block
- `finding_id` → `request_id`，`notes` → `constraint`，`problem` + `edge` → `defects`
- Request 不包含座標

格式見 `schemas/repair_request.schema.md`。不進 canonical。若腳本回傳 `blocked`（例如 `human_check`），停止回報。

### 4b. [script] 保存 canonical snapshot

```bash
cp -R <paper_dir>/figures/canonical/* \
  <paper_dir>/figures/repairs/round_01/before_snapshot/
```

### 4c. [spawn agent] 啟動 figure_repair

Prompt = `agents/subagent_prompts/figure_repair.md` 全文 + assignment block：

```text
---
## Assignment
paper_dir: <paper_dir>
repair_round: round_01
repair_id: repair_01
canonical_artifact_root: <paper_dir>/figures/canonical
repair_artifact_root: <paper_dir>/figures/repairs/round_01/repair_01
request_file: <paper_dir>/figures/repairs/round_01/repair_requests_merged.json
source_review: <paper_dir>/figures/canonical/visual_review.json
```

Repair worker 讀 canonical + repair request，裁切修復後的 crop 和 previews，寫 `decisions.json`，呼叫 `build_repair_report.py` 組裝 `repair_report.json`，跑 `validate_figure_repair.py`。

#### Parallel repair（可選）

建議每個 repair worker 負責 3 個 figures 左右。

```bash
# 分割（greedy balancing by request count）
python3 agents/scripts/divide_repair_requests.py \
  <repair_requests_merged.json> --workers M --output-dir repairs/round_01

# 啟動 M 個 repair subagents IN PARALLEL（每個用不同的 repair_id 和 repair_requests_assigned.json）

# 合併（含 repair_output path rewriting）
python3 agents/scripts/merge_repair_reports.py \
  repair_01/repair_report.json repair_02/repair_report.json ... \
  --repair-round round_01 --output repairs/round_01/merged_repair_report.json
```

任何一個 repair agent 失敗 → 不 merge，回報 blocked。

### 4d. [script] Merge repair to canonical

```bash
python3 agents/scripts/merge_repair.py \
  "<repair_report.json>" \
  --repair-root "<repair_artifact_root>" \
  --canonical "<paper_dir>/figures/canonical"
```

Parallel mode 時用 merged report，`--repair-root` 指向 `repairs/round_01/`。

腳本先 validate（dry-run），全部通過才 execute。有 old_value mismatch → 報錯停止，canonical 不被動到。

`merge_repair.py` 的行為：
- `repair_report.json` 的 `status` 是 `incomplete` → exit code 2，parent 必須 block 或重新分派，不得靜默 close。
- `merge.needs_parent_merge` 為 `false` → 不需要 merge，跳過。
- `repair_round`、`repair_id` 必須和 assignment 一致（由 `build_repair_report.py` 自動帶入）。

格式細節（`file_copies[]`、`manifest_patches[]` 的結構）見 `schemas/repair_report.schema.md`。

### 4e. [judgment] 回到 Step 2

Repair merge 後，先前 review 全部失效。下一輪 review 寫到 `reviewers/round_01/`，promote 後覆寫 `canonical/visual_review.json`。

# 規則

## Subagent 規則

- 所有 worker、reviewer、repair 都要啟動獨立 subagent。不得用 parent 的工作取代 subagent。
- Subagent prompt 必須使用指定的 prompt 檔案全文，不得摘要、改寫、截斷。Parent 唯一可以做的修改是在末尾附加 assignment block。
- Agent 啟動失敗 → 先修正 prompt/tool/context，重試。仍失敗 → 回報 blocked。

## Parent 不得做的事

- 代替 reviewer 或 repair worker 做 visual judgment。
- 自己發明新的 crop coordinate。
- 靜默覆蓋另一個 figure 或 crop id。
- repair_report 的 status 是 `incomplete` 時靜默 close。
- 跳過 review 直接 close（repair merge 後一定要 re-review）。

## Review & repair 規則

- 預設最多 4 個 repair rounds，除非使用者明確改變。
- 任何改動 crop、preview 或 manifest 的 repair 都讓先前 review 失效，必須重新完整 review。
- 每輪 review 都審查當前 canonical 的全部 figures（不做 partial review reuse）。
- 不使用 hash；round numbering + 不覆寫舊目錄 + stage barrier 就是 stale review 防線。

## 輸出格式

- Agent primary reports 和 decisions 只能是 JSON。
- Parent 可以做機械式 JSON cleanup 或允許清單內的 patch，但不能編造 verdicts、findings、coverage、source evidence、crop coordinate 或 scientific values。
