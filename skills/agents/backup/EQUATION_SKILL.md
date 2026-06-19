# 目標

這是一份給 equation lane orchestrator 看的指引。

Equation lane 從 PDF 擷取顯示方程式（displayed equations），輸出裁切 PNG 和 LaTeX 中繼資料。

# 結構

Equation lane 使用 `<paper_dir>/equations/`：

```text
<paper_dir>/
  shared/
    source.pdf
    pages/              # 完整解析度頁面圖片（render_pages.py 產生）
    previews/           # 受限尺寸 page previews（make_image_preview.py 產生）
  equations/
    workers/
      worker_01/          # extractor 寫入：equation_candidates/index/decisions/equations.json、crops/、previews/、rendered_latex/、source_regions/、boundaries/
    canonical/            # live state：equations.json、visual_review.json、crops/、previews/、rendered_latex/
    reviewers/            # per-round、per-reviewer trace
    repairs/              # per-round repair trace
```

### Canonical 只放 live state

- `equations.json`：唯一的 extraction manifest。Repair 的唯一 patch 對象。
- `visual_review.json`：最新一輪 review（每輪覆寫）。Gate 和 build_repair_request 讀這個。
- `crops/`：final crop 圖片。
- `previews/`：所有 evidence previews（crop preview、boundary preview、edge strips、bottom band、bottom micro）。
- `rendered_latex/`：LaTeX 渲染預覽圖。

不進 canonical：`equation_decisions.json`（planning trace，留在 workers/）、`review_packet.json`（留在 reviewers/）、`repair_requests_merged.json`（留在 repairs/）。

### Round 命名

- `reviewers/round_00/`：審 extraction promote 後的 canonical。
- `repairs/round_01/`：修 round_00 review 發現的問題。
- `reviewers/round_01/`：審 round_01 repair merge 後的 canonical。
- 依此類推。不覆寫舊的 review 或 repair 工作目錄。

### Artifact root 相對路徑

Equation lane JSON 裡的 artifact path 都使用 artifact root 相對路徑：

- Extractor / validator：artifact root 是 `workers/worker_01/`
- Reviewer / repair：artifact root 是 `canonical/`
- Repair output：`repair_output` 以 `repairs/round_N/repair_ID/` 為 root；`canonical_target` 以 `canonical/` 為 root

不要在 artifact path 裡寫完整的 `equations/canonical/` 或絕對路徑。Shared page paths（`shared/pages/page_3.png`）使用 paper-dir-relative path。

## 工具

所有 script 放在 `agents/scripts/`。

### Subagent 工具（extractor / reviewer / repair 呼叫）

| Script | 使用者 | 用途 |
|---|---|---|
| `crop_and_preview.py` | extractor, repair | 一次完成裁切 + 全套 edge evidence preview |
| `crop_region.py` | extractor, reviewer (fallback) | 單次裁切（source region、reviewer fallback context） |
| `make_image_preview.py` | extractor, reviewer (fallback) | 單張 preview（source region preview、reviewer higher-res fallback） |
| `make_edge_previews.py` | repair | 單邊 edge strip（regenerate_missing_preview action） |
| `render_latex_preview.py` | extractor, repair | 渲染 LaTeX 為預覽圖（pdflatex → matplotlib → text fallback） |
| `validate_equation_extraction.py` | extractor | 檢查 extractor output contract |

Equation lane 目前沒有專用的 `equation_build_repair_report.py`，repair agent 手動組裝 repair report。

### Orchestration 工具（parent 呼叫）

| Script | 用途 |
|---|---|
| `render_pages.py` | PDF → 完整解析度頁面圖片 |
| `make_image_preview.py` | 頁面圖片 → 受限尺寸 page preview |
| `equation_promote_to_canonical.py` | 搬檔到 canonical |
| `equation_build_review_packet.py` | 從 canonical equations.json 產生 review packet |
| `equation_check_review_gate.py` | 讀 visual_review.json，回傳 exit code |
| `equation_build_repair_request.py` | 從 visual_review.json 產生 repair requests |
| `equation_merge_repair.py` | 套用 repair report 的 file_copies + manifest_patches 到 canonical |
| `equation_divide_review_packet.py` | 分割 review packet 給 N 個 reviewer（parallel） |
| `equation_merge_reviews.py` | 合併 N 份 visual_review.json |
| `equation_divide_repair_requests.py` | 分割 repair requests 給 N 個 repair worker（parallel） |
| `equation_merge_repair_reports.py` | 合併 N 份 repair_report.json（含 path rewriting） |

# 流程

Pipeline 是一個 extract → review → repair loop。

Parent 只做三種動作：
- **[script]** 跑 orchestration script（機械操作，不需判斷）
- **[spawn agent]** 啟動 subagent（委派視覺判斷）
- **[judgment]** 讀 exit code 決定下一步（簡單分支邏輯）

所有 visual judgment 由 subagent 做。Parent 不看圖、不判斷 crop 品質、不發明座標。

## Step 0: 前置工作

**[script]** 建立 paper directory，render pages，建立 page previews。若已在其他 lane 完成，不需重複 shared/ 的部分。

```bash
# 建立目錄結構
mkdir -p <paper_dir>/shared/pages <paper_dir>/shared/previews \
  <paper_dir>/equations/{workers,canonical,reviewers,repairs}

# 複製 PDF（若 shared/ 尚未建立）
cp <source.pdf> <paper_dir>/shared/source.pdf

# Render 完整解析度頁面圖片（若 shared/pages/ 尚未建立）
python3 agents/scripts/render_pages.py \
  "<paper_dir>/shared/source.pdf" "<paper_dir>/shared/pages" --dpi 300

# 為每頁建立 preview（若 shared/previews/ 尚未建立）
python3 agents/scripts/make_image_preview.py \
  "<paper_dir>/shared/pages/page_N.png" "<paper_dir>/shared/previews/page_N_preview.png" \
  --max-dim 1568
```

## Step 1: Extraction

### 1a. [spawn agent] 啟動 equation_extractor

Prompt = `agents/subagent_prompts/equation_extractor.md` 全文 + assignment block：

```text
---
## Assignment
paper_dir: <paper_dir>
worker_id: worker_01
output_root: <paper_dir>/equations/workers/worker_01
artifact_root: <paper_dir>/equations/workers/worker_01
pages: 全部頁面
```

Extractor 寫出 `workers/worker_01/`（含 equation_candidates.json、equation_index.json、equation_decisions.json、equations.json、crops/、previews/、rendered_latex/、source_regions/、boundaries/）。

Extractor 在完成前會自己做 self-check。

### 1b. [script] Promote to canonical

```bash
python3 agents/scripts/equation_promote_to_canonical.py \
  --source <paper_dir>/equations/workers/worker_01 \
  --canonical <paper_dir>/equations/canonical \
  --mode extraction
```

搬 `equations.json`、`crops/`、`previews/`、`rendered_latex/`。不搬 `equation_decisions.json`（planning trace）、`equation_candidates.json`、`equation_index.json`、`source_regions/`、`boundaries/`。

## Step 2: Review

### 2a. [script] 建立 review packet

```bash
python3 agents/scripts/equation_build_review_packet.py \
  "<paper_dir>/equations/canonical/equations.json" \
  --review-round round_00 \
  --output "<paper_dir>/equations/reviewers/round_00/reviewer_01/review_packet.json"
```

### 2b. [spawn agent] 啟動 equation_reviewer

Prompt = `agents/subagent_prompts/equation_reviewer.md` 全文 + assignment block：

```text
---
## Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
canonical_artifact_root: <paper_dir>/equations/canonical
output_root: <paper_dir>/equations/reviewers/round_00/reviewer_01
review_packet: <paper_dir>/equations/reviewers/round_00/reviewer_01/review_packet.json
scope: review_packet.json 中的全部 equations
```

Reviewer 讀 canonical evidence（crop preview + boundary/edge evidence + rendered LaTeX preview），寫出 `equation_visual_review.json`。Reviewer 同時檢查 crop 邊界和 LaTeX 準確度。

#### Parallel review（可選）

建議每個 reviewer 負責 5-8 個 equations。

```bash
# 分割
python3 agents/scripts/equation_divide_review_packet.py \
  <full_review_packet.json> --workers N --output-dir reviewers/round_00

# 啟動 N 個 reviewer subagents IN PARALLEL（每個用不同的 reviewer_id 和 review_packet）

# 合併
python3 agents/scripts/equation_merge_reviews.py \
  reviewer_01/visual_review.json reviewer_02/visual_review.json ... \
  --review-round round_00 --output reviewers/round_00/merged/visual_review.json
```

任何一個 reviewer 失敗 → 不 merge，回報 blocked。不嘗試 partial merge。

### 2c. [script] Promote review to canonical

```bash
python3 agents/scripts/equation_promote_to_canonical.py \
  --source <paper_dir>/equations/reviewers/round_00/reviewer_01 \
  --canonical <paper_dir>/equations/canonical \
  --mode review
```

Parallel mode 時 source 改為 `reviewers/round_00/merged`。覆寫 `canonical/visual_review.json`。

## Step 3: Gate

### 3a. [script] 讀 gate

```bash
python3 agents/scripts/equation_check_review_gate.py \
  "<paper_dir>/equations/canonical/visual_review.json"
```

### 3b. [judgment] 決定下一步

| Exit code | 意義 | 動作 |
|---|---|---|
| 0 | pass | Equation lane close。 |
| 1 | needs_repair | 進入 Step 4。 |
| 2 | blocked | 停止並回報（repair round limit、human_check、異常）。 |

預設最多 4 個 repair rounds。Parent 不得自己做 visual judgment 來 override reviewer。

## Step 4: Repair

### 4a. [script] 建立 repair request

```bash
python3 agents/scripts/equation_build_repair_request.py \
  "<paper_dir>/equations/canonical/visual_review.json" \
  --repair-round round_01 \
  --output "<paper_dir>/equations/repairs/round_01/repair_requests_merged.json"
```

Equation repair request 可能包含 crop 修復方向（`expand_*`/`shrink_*`/`recrop`）和 LaTeX 修復方向（`correct_latex_symbol`/`correct_latex_structure`/`add_alignment`/`fix_equation_number`）。

### 4b. [script] 保存 canonical snapshot

```bash
cp -R <paper_dir>/equations/canonical/* \
  <paper_dir>/equations/repairs/round_01/before_snapshot/
```

### 4c. [spawn agent] 啟動 equation_repair

Prompt = `agents/subagent_prompts/equation_repair.md` 全文 + assignment block：

```text
---
## Assignment
paper_dir: <paper_dir>
repair_round: round_01
repair_id: repair_01
canonical_artifact_root: <paper_dir>/equations/canonical
repair_artifact_root: <paper_dir>/equations/repairs/round_01/repair_01
request_file: <paper_dir>/equations/repairs/round_01/repair_requests_merged.json
source_review: <paper_dir>/equations/canonical/visual_review.json
```

Equation repair 有兩類 action：`recrop` 和 `fix_latex`（equation 獨有）。Repair agent 寫 `decisions.json`（含 `new_crop_px` 和/或 `new_latex`），手動組裝 `equation_repair_report.json`。

#### Parallel repair（可選）

建議每個 repair worker 負責 5-8 個 equations。

```bash
# 分割（greedy balancing by request count）
python3 agents/scripts/equation_divide_repair_requests.py \
  <repair_requests_merged.json> --workers M --output-dir repairs/round_01

# 啟動 M 個 repair subagents IN PARALLEL（每個用不同的 repair_id 和 repair_requests_assigned.json）

# 合併（含 repair_output path rewriting）
python3 agents/scripts/equation_merge_repair_reports.py \
  repair_01/repair_report.json repair_02/repair_report.json ... \
  --repair-round round_01 --output repairs/round_01/merged_repair_report.json
```

任何一個 repair agent 失敗 → 不 merge，回報 blocked。

### 4d. [script] Merge repair to canonical

```bash
python3 agents/scripts/equation_merge_repair.py \
  "<repair_report.json>" \
  --repair-root "<repair_artifact_root>" \
  --canonical "<paper_dir>/equations/canonical"
```

Parallel mode 時用 merged report，`--repair-root` 指向 `repairs/round_01/`。

腳本先 validate（dry-run），全部通過才 execute。有 old_value mismatch → 報錯停止，canonical 不被動到。

`equation_merge_repair.py` 的行為：
- `repair_report.json` 的 `status` 是 `incomplete` → exit code 2，parent 必須 block 或重新分派，不得靜默 close。
- `merge.needs_parent_merge` 為 `false` → 不需要 merge，跳過。
- `repair_round`、`repair_id` 必須和 assignment 一致。

### 4e. [judgment] 回到 Step 2

Repair merge 後，先前 review 全部失效。下一輪 review 寫到 `reviewers/round_01/`，promote 後覆寫 `canonical/visual_review.json`。

# 規則

## Subagent 規則

- 所有 extractor、reviewer、repair 都要啟動獨立 subagent。不得用 parent 的工作取代 subagent。
- Subagent prompt 必須使用指定的 prompt 檔案全文，不得摘要、改寫、截斷。Parent 唯一可以做的修改是在末尾附加 assignment block。
- Agent 啟動失敗 → 先修正 prompt/tool/context，重試。仍失敗 → 回報 blocked。

## Parent 不得做的事

- 代替 reviewer 或 repair worker 做 visual judgment。
- 自己發明新的 crop coordinate。
- 靜默覆蓋另一個 equation 或 crop id。
- repair_report 的 status 是 `incomplete` 時靜默 close。
- 跳過 review 直接 close（repair merge 後一定要 re-review）。

## Review & repair 規則

- 預設最多 4 個 repair rounds，除非使用者明確改變。
- 任何改動 crop、preview、manifest 或 rendered LaTeX 的 repair 都讓先前 review 失效，必須重新完整 review。
- 每輪 review 都審查當前 canonical 的全部 equations（不做 partial review reuse）。
- 不使用 hash；round numbering + 不覆寫舊目錄 + stage barrier 就是 stale review 防線。
- Reviewer 同時檢查 crop 邊界和 LaTeX 準確度。一個方程式可能 crop 通過但 LaTeX 不通過（或反之）。
- Repair request 可能同時包含 crop 和 LaTeX 修復方向。先修 crop，再修 LaTeX。
- rendered LaTeX preview 也要 promote 到 canonical。

## 輸出格式

- Agent primary reports 和 decisions 只能是 JSON。
- Parent 可以做機械式 JSON cleanup 或允許清單內的 patch，但不能編造 verdicts、findings、coverage、source evidence、crop coordinate、LaTeX 或 scientific values。
