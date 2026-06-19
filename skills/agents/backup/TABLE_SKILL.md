# 目標

這是一份給 table lane orchestrator 看的指引。

Table lane 從 PDF 擷取有標籤的表格，輸出裁切 PNG 和結構化 JSON（headers、rows、footnotes）。

Table lane 的核心差異：主要交付成果是結構化資料，不只是圖片裁切。

# 結構

Table lane 使用 `<paper_dir>/tables/`：

```text
<paper_dir>/
  shared/
    source.pdf
    pages/              # 完整解析度頁面圖片（render_pages.py 產生）
    previews/           # 受限尺寸 page previews（make_image_preview.py 產生）
  tables/
    workers/
      worker_01/          # extractor 寫入：table_candidates/index/decisions/tables.json、Table_N.json、crops/、previews/、rendered_tables/、source_regions/、boundaries/
    canonical/            # live state：tables.json、Table_N.json、visual_review.json、crops/、previews/、rendered_tables/
    reviewers/            # per-round、per-reviewer trace
    repairs/              # per-round repair trace
```

### Canonical 只放 live state

- `tables.json`：唯一的 extraction manifest。Repair 的唯一 patch 對象。
- `Table_N.json`：每個表格的結構化 JSON（headers/rows/footnotes）。
- `visual_review.json`：最新一輪 review（每輪覆寫）。Gate 和 build_repair_request 讀這個。
- `crops/`：final crop 圖片。
- `previews/`：所有 evidence previews（crop preview、boundary preview、edge strips、bottom band、bottom micro）。
- `rendered_tables/`：結構化 JSON 渲染後的預覽圖。

不進 canonical：`table_decisions.json`（planning trace，留在 workers/）、`review_packet.json`（留在 reviewers/）、`repair_requests_merged.json`（留在 repairs/）。

### Round 命名

- `reviewers/round_00/`：審 extraction promote 後的 canonical。
- `repairs/round_01/`：修 round_00 review 發現的問題。
- `reviewers/round_01/`：審 round_01 repair merge 後的 canonical。
- 依此類推。不覆寫舊的 review 或 repair 工作目錄。

### Artifact root 相對路徑

Table lane JSON 裡的 artifact path 都使用 artifact root 相對路徑：

- Extractor / validator：artifact root 是 `workers/worker_01/`
- Reviewer / repair：artifact root 是 `canonical/`
- Repair output：`repair_output` 以 `repairs/round_N/repair_ID/` 為 root；`canonical_target` 以 `canonical/` 為 root

不要在 artifact path 裡寫完整的 `tables/canonical/` 或絕對路徑。Shared page paths（`shared/pages/page_3.png`）使用 paper-dir-relative path。

## 工具

所有 script 放在 `agents/scripts/`。

### Subagent 工具（extractor / reviewer / repair 呼叫）

| Script | 使用者 | 用途 |
|---|---|---|
| `crop_and_preview.py` | extractor, repair | 一次完成裁切 + 全套 edge evidence preview |
| `crop_region.py` | extractor, reviewer (fallback) | 單次裁切（source region、reviewer fallback context） |
| `make_image_preview.py` | extractor, reviewer (fallback) | 單張 preview（source region preview、reviewer higher-res fallback） |
| `make_edge_previews.py` | repair | 單邊 edge strip（regenerate_missing_preview action） |
| `render_table_preview.py` | extractor, repair | 將結構化 `Table_N.json` 渲染成視覺預覽圖 |
| `validate_table_extraction.py` | extractor | 檢查 extractor output contract |
| `validate_table_review.py` | reviewer | 檢查 reviewer output contract |

Table lane 目前沒有專用的 `table_build_repair_report.py`，repair agent 手動組裝 repair report。

### Orchestration 工具（parent 呼叫）

| Script | 用途 |
|---|---|
| `render_pages.py` | PDF → 完整解析度頁面圖片 |
| `make_image_preview.py` | 頁面圖片 → 受限尺寸 page preview |
| `table_promote_to_canonical.py` | 搬檔到 canonical |
| `table_build_review_packet.py` | 從 canonical tables.json 產生 review packet |
| `table_check_review_gate.py` | 讀 visual_review.json，回傳 exit code |
| `table_build_repair_request.py` | 從 visual_review.json 產生 repair requests |
| `table_merge_repair.py` | 套用 repair report 的 file_copies + manifest_patches 到 canonical |
| `table_divide_review_packet.py` | 分割 review packet 給 N 個 reviewer（parallel） |
| `table_merge_reviews.py` | 合併 N 份 visual_review.json |
| `table_divide_repair_requests.py` | 分割 repair requests 給 N 個 repair worker（parallel） |
| `table_merge_repair_reports.py` | 合併 N 份 repair_report.json（含 path rewriting） |

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
  <paper_dir>/tables/{workers,canonical,reviewers,repairs}

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

### 1a. [spawn agent] 啟動 table_extractor

Prompt = `agents/subagent_prompts/table_extractor.md` 全文 + assignment block：

```text
---
## Assignment
paper_dir: <paper_dir>
worker_id: worker_01
output_root: <paper_dir>/tables/workers/worker_01
artifact_root: <paper_dir>/tables/workers/worker_01
pages: 全部頁面
```

Extractor 寫出 `workers/worker_01/`（含 table_candidates.json、table_index.json、table_decisions.json、Table_N.json、tables.json、crops/、previews/、rendered_tables/、source_regions/、boundaries/）。

Table extraction 的核心是結構化資料擷取（讀表格內容、判斷 header/body/footnote 結構、處理 merged cells），crop 是次要的。

Extractor 在完成前會自己做 self-check。

### 1b. [script] Promote to canonical

```bash
python3 agents/scripts/table_promote_to_canonical.py \
  --source <paper_dir>/tables/workers/worker_01 \
  --canonical <paper_dir>/tables/canonical \
  --mode extraction
```

搬 `tables.json`、`Table_N.json`、`crops/`、`previews/`、`rendered_tables/`。不搬 `table_decisions.json`（planning trace）、`table_candidates.json`、`table_index.json`、`source_regions/`、`boundaries/`。

注意：`Table_N.json` 也需要搬到 canonical，因為 reviewer 和 repair 都需要讀取結構化 JSON。

## Step 2: Review

### 2a. [script] 建立 review packet

```bash
python3 agents/scripts/table_build_review_packet.py \
  "<paper_dir>/tables/canonical/tables.json" \
  --review-round round_00 \
  --output "<paper_dir>/tables/reviewers/round_00/reviewer_01/review_packet.json"
```

### 2b. [spawn agent] 啟動 table_reviewer

Prompt = `agents/subagent_prompts/table_reviewer.md` 全文 + assignment block：

```text
---
## Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
canonical_artifact_root: <paper_dir>/tables/canonical
output_root: <paper_dir>/tables/reviewers/round_00/reviewer_01
review_packet: <paper_dir>/tables/reviewers/round_00/reviewer_01/review_packet.json
scope: review_packet.json 中的全部 tables
```

Reviewer 同時檢查：
1. **Crop 邊界**：cyan 線規則（邊界貼合可見內容、排除周圍正文）。
2. **結構準確度**：結構化 JSON 是否準確反映來源表格的 header/body/footnote 結構和逐字內容。

Reviewer 會建立 structural inventory（列數、欄數、標題層數、註腳數），從來源和 JSON 各計一次，兩者必須一致。

#### Parallel review（可選）

建議每個 reviewer 負責 3-5 個 tables（表格 review 比其他 lane 更耗 context，需要逐字比對儲存格內容）。

```bash
# 分割
python3 agents/scripts/table_divide_review_packet.py \
  <full_review_packet.json> --workers N --output-dir reviewers/round_00

# 啟動 N 個 reviewer subagents IN PARALLEL（每個用不同的 reviewer_id 和 review_packet）

# 合併
python3 agents/scripts/table_merge_reviews.py \
  reviewer_01/visual_review.json reviewer_02/visual_review.json ... \
  --review-round round_00 --output reviewers/round_00/merged/visual_review.json
```

任何一個 reviewer 失敗 → 不 merge，回報 blocked。不嘗試 partial merge。

### 2c. [script] Promote review to canonical

```bash
python3 agents/scripts/table_promote_to_canonical.py \
  --source <paper_dir>/tables/reviewers/round_00/reviewer_01 \
  --canonical <paper_dir>/tables/canonical \
  --mode review
```

Parallel mode 時 source 改為 `reviewers/round_00/merged`。覆寫 `canonical/visual_review.json`。

## Step 3: Gate

### 3a. [script] 讀 gate

```bash
python3 agents/scripts/table_check_review_gate.py \
  "<paper_dir>/tables/canonical/visual_review.json"
```

### 3b. [judgment] 決定下一步

| Exit code | 意義 | 動作 |
|---|---|---|
| 0 | pass | Table lane close。 |
| 1 | needs_repair | 進入 Step 4。 |
| 2 | blocked | 停止並回報（repair round limit、human_check、異常）。 |

預設最多 4 個 repair rounds。Parent 不得自己做 visual judgment 來 override reviewer。

## Step 4: Repair

### 4a. [script] 建立 repair request

```bash
python3 agents/scripts/table_build_repair_request.py \
  "<paper_dir>/tables/canonical/visual_review.json" \
  --repair-round round_01 \
  --output "<paper_dir>/tables/repairs/round_01/repair_requests_merged.json"
```

Table repair request 可能包含：
- Crop 修復方向：`expand_*`/`shrink_*`/`recrop`
- 結構修復方向：`split_header_level`、`merge_wrapped_cell`、`split_false_row`、`correct_cell_text`、`add_missing_footnote`、`fix_title_separator`、`fix_sub_column`

### 4b. [script] 保存 canonical snapshot

```bash
cp -R <paper_dir>/tables/canonical/* \
  <paper_dir>/tables/repairs/round_01/before_snapshot/
```

### 4c. [spawn agent] 啟動 table_repair

Prompt = `agents/subagent_prompts/table_repair.md` 全文 + assignment block：

```text
---
## Assignment
paper_dir: <paper_dir>
repair_round: round_01
repair_id: repair_01
canonical_artifact_root: <paper_dir>/tables/canonical
repair_artifact_root: <paper_dir>/tables/repairs/round_01/repair_01
request_file: <paper_dir>/tables/repairs/round_01/repair_requests_merged.json
source_review: <paper_dir>/tables/canonical/visual_review.json
```

Table repair 有兩類 action：
- `recrop`：調整 crop 邊界。
- `fix_structure`：修正結構化 JSON（cell text、header level、wrapped cell、footnote 等）。需要同時更新 `Table_N.json` 和重新渲染 table preview。

先修 crop（因為結構要從正確的 crop 讀取），再修結構。

Repair agent 寫 `decisions.json`（含 `new_crop_px` 和/或 `structure_corrections`），手動組裝 `table_repair_report.json`。

#### Parallel repair（可選）

建議每個 repair worker 負責 3-5 個 tables。

```bash
# 分割（greedy balancing by request count）
python3 agents/scripts/table_divide_repair_requests.py \
  <repair_requests_merged.json> --workers M --output-dir repairs/round_01

# 啟動 M 個 repair subagents IN PARALLEL（每個用不同的 repair_id 和 repair_requests_assigned.json）

# 合併（含 repair_output path rewriting）
python3 agents/scripts/table_merge_repair_reports.py \
  repair_01/repair_report.json repair_02/repair_report.json ... \
  --repair-round round_01 --output repairs/round_01/merged_repair_report.json
```

任何一個 repair agent 失敗 → 不 merge，回報 blocked。

### 4d. [script] Merge repair to canonical

```bash
python3 agents/scripts/table_merge_repair.py \
  "<repair_report.json>" \
  --repair-root "<repair_artifact_root>" \
  --canonical "<paper_dir>/tables/canonical"
```

Parallel mode 時用 merged report，`--repair-root` 指向 `repairs/round_01/`。

腳本先 validate（dry-run），全部通過才 execute。有 old_value mismatch → 報錯停止，canonical 不被動到。

`table_merge_repair.py` 的行為：
- `repair_report.json` 的 `status` 是 `incomplete` → exit code 2，parent 必須 block 或重新分派，不得靜默 close。
- `merge.needs_parent_merge` 為 `false` → 不需要 merge，跳過。
- `repair_round`、`repair_id` 必須和 assignment 一致。

注意：table repair 的 `file_copies` 可能包含 `kind: "structured_json"`（`Table_N.json`）和 `kind: "rendered_table_preview"`，除了標準的 crop/preview/boundary kinds。

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
- 靜默覆蓋另一個 table 或 crop id。
- repair_report 的 status 是 `incomplete` 時靜默 close。
- 跳過 review 直接 close（repair merge 後一定要 re-review）。

## Review & repair 規則

- 預設最多 4 個 repair rounds，除非使用者明確改變。
- 任何改動 crop、preview、manifest、`Table_N.json` 或 rendered table preview 的 repair 都讓先前 review 失效，必須重新完整 review。
- 每輪 review 都審查當前 canonical 的全部 tables（不做 partial review reuse）。
- 不使用 hash；round numbering + 不覆寫舊目錄 + stage barrier 就是 stale review 防線。
- Reviewer 同時檢查 crop 邊界和結構化 JSON 準確度。一個表格可能 crop 通過但結構不通過。
- Structural inventory matching 是 table review 的必要步驟——列數、欄數、標題層數、註腳數都要從來源和 JSON 各自計數。
- Repair request 可能同時包含 crop 和結構修復方向。先修 crop，再修結構。
- 結構修復時保留來源原文（含錯字）。只修正擷取錯誤（misread），不修正來源錯誤。
- `Table_N.json` 和 rendered table preview 也要 promote 到 canonical。

## 輸出格式

- Agent primary reports 和 decisions 只能是 JSON。
- Parent 可以做機械式 JSON cleanup 或允許清單內的 patch，但不能編造 verdicts、findings、coverage、source evidence、crop coordinate、table structure 或 scientific values。
