# Figure Lane Open Issues

這份文件整理目前 `agents` 中，讓 figure lane 還不能穩定跑起來的問題。每條都包含：

- 問題在哪裡
- 我建議怎麼改
- 修改完應該長怎樣

目標不是一次定案，而是讓我們可以一條一條討論、決策、再回頭改 `SKILL.md`、subagent prompts、shared scripts 或 schema。

## 討論順序建議

1. 先決定 runtime layout：`worker_output/worker_XX` 還是 `batches/batch_XX`。
2. 決定 figure v2 schema 是否正式保留 `crop_units[]`。
3. 決定 reviewer output 是 `visual_review.json` 還是 gate-level `review_batch.json`。
4. 決定 repair handoff 是 `repair_requests_merged.json` 還是 `repair_manifest.json`。
5. 最後才寫 parent divide / merge / gate 細節。

## 1. Figure-Only Mode 還不明確

### 問題在哪裡

`SKILL.md` 目前描述的是完整 pipeline：text、figure、table、equation、reassembly 都會跑。可是現在我們想先讓 figure lane 跑起來，parent orchestrator 還沒有一個正式的「只跑 figure lane」模式。

目前會造成的問題：

- user 要求「先跑 figure lane」時，orchestrator 不知道是否要建立其他 lanes。
- figure lane 跑完後，不知道應該 stop、handoff、還是繼續 reassembly。
- trace / gate / final response 不知道如何表達「只完成 figure lane」。

### 建議怎麼改

在 `SKILL.md` 加一個 `figure_lane_only` execution mode。這個 mode 只做：

1. init run layout
2. render pages / previews
3. run figure extraction batches
4. merge to figure canonical
5. figure mechanical validation
6. figure review
7. repair loop
8. figure lane close gate
9. stop and report figure artifacts

### 修改完應該長怎樣

```text
Modes:
  full_pipeline:
    run all lanes, handoff, reassembly, final review

  figure_lane_only:
    init -> render pages/previews -> figures extraction -> canonical merge
    -> canonical mechanical validation -> figure review barrier
    -> repair loop -> figure lane close -> stop
```

Final response in `figure_lane_only` should report:

- `lanes/figures/canonical/figures.json`
- figure crops and previews location
- validation status
- review status
- repair rounds run
- unresolved findings / residual risk

## 2. Runtime Layout 和 Existing Shared Scripts 不一致

### 問題在哪裡

目前 `SKILL.md` 用：

```text
lanes/figures/worker_output/worker_01/
lanes/figures/repair/round_01/
```

但既有 shared scripts 和 newer pipeline reference 用：

```text
lanes/figures/batches/batch_01/
lanes/figures/repairs/round_01/
```

特別是 `skills/_shared/scripts/merge_batch_manifests.py` 明確吃：

```bash
--batches-dir "<paper_dir>/lanes/figures/batches"
--canonical-dir "<paper_dir>/lanes/figures/canonical"
```

如果維持 `worker_output/`，現有 merge script 不能直接用。

### 建議怎麼改

我建議改回 `batches/batch_XX`。原因：

- extraction output 本質上就是 batch-local output。
- shared merge scripts 已經採用 `batches`.
- review / repair 才使用 `round_XX`，語意比較乾淨。
- 可以直接繼承 old/new pipeline 的 gate vocabulary。

### 修改完應該長怎樣

```text
lanes/
  figures/
    batches/
      batch_01/
        figure_candidates.json
        figure_index.json
        figure_decisions.json
        figures.json
        Figure_1.png
        previews/
        source_regions/
        edges/
    canonical/
      figure_candidates.json
      figure_index.json
      figure_decisions.json
      figures.json
      Figure_1.png
      previews/
    reviews/
      round_00/
        reviewer_01/
          visual_review.json
          previews/
    repairs/
      round_01/
        repair_requests_merged.json
        repair_01/
          repair_report.json
          crops/
          previews/
    validation/
```

如果我們決定保留 `worker_output/worker_XX`，那就要新增一個 v2 merge script 或讓現有 merge script 支援 `worker_output`.

## 3. Figure v2 Schema 和 Current Validator 不相容

### 問題在哪裡

目前 hand-written figure prompts 採用 v2 schema：

- `crop_units[]`
- `crop_units[].image_file`
- `crop_units[].preview`
- `crop_units[].edge_previews`
- `crop_hint_px` for candidates
- `figure_decisions.json` 和 `figures.json` 不在 figure 層寫 derived fields，例如 `pages`、`image_files`、`crop_count`

但 `skills/_shared/scripts/validate_figures.py` 仍偏向舊 schema：

- candidate 層期待 `crop_px`
- decision 層期待 figure-level `crop_px`
- decision 層期待 `output_files`
- final manifest 期待 `image_files`
- visual review validator 期待較舊的 flat `source_edge_previews_read` / `crop_previews_read`

所以就算 agent 按新 prompt 寫對 v2 JSON，validator 也可能 fail。

### 建議怎麼改

先做一個明確決策：

- A. 正式採用 v2 schema，更新 validator / merge scripts。
- B. 暫時回退到舊 schema，讓現有 shared scripts 先能跑。

我建議採用 A，因為 `crop_units[]` 更適合：

- multi-region figure
- cross-page figure
- 同一 figure 多個 crop
- repair 時只改其中一個 crop unit

### 修改完應該長怎樣

`validate_figures.py` v2 mode 應該檢查：

- `figure_candidates.json`
  - top-level `schema_version: "figure_extraction.v2"`
  - candidate 使用 `crop_hint_px`
  - candidate 有 `source_region_ids`
  - top-level 有 `unexpected_labeled_figures`
- `figure_index.json`
  - figures 可以有 `pages`
  - figures 有 `source_region_ids`
  - top-level 有 `omitted_candidates`
- `figure_decisions.json`
  - figures 不需要 figure-level `pages`、`crop_px`、`output_files`
  - 每個 figure 有 `crop_units[]`
  - 每個 crop unit 有 `crop_id`、`page`、`crop_px`、`image_file`、`preview`、`edge_previews`、`role`
- `figures.json`
  - `crop_units[]` 必須與 `figure_decisions.json` 對應 figure 完全一致
  - `verification.result` 可以是 `fail`，但此時 top-level status 必須是 `incomplete`
  - 所有 image/preview/edge paths 都存在

需要新增或修改：

```text
skills/_shared/scripts/validate_figures.py
skills/_shared/scripts/merge_batch_manifests.py
skills/_shared/references/figure_schemas.md
```

## 4. Mechanical Validation 不應刪除，但語意要改

### 問題在哪裡

目前 extractor、reviewer、repair prompt 都有 mechanical self-check 或 final validator 的概念，所以看起來像 parent 的 mechanical validation 是重複的。

但實際上它們檢查的是不同層級：

- extractor self-check：worker-local artifacts 是否自洽
- repair self-check：repair-local artifacts 是否自洽
- parent mechanical validation：canonical after merge / after repair 是否自洽
- reviewer：視覺品質是否真的 pass

如果刪掉 parent mechanical validation，canonical merge 後的錯誤會沒人抓。

### 建議怎麼改

不要刪 mechanical validation。改成三層命名：

```text
local self-check:
  agent 在自己的 output 目錄檢查檔案、paths、manifest 一致性

canonical mechanical validation:
  parent 在 merge 到 canonical 後檢查 canonical truth

visual acceptance:
  reviewer 讀 source/crop/edge previews 後做獨立判定
```

### 修改完應該長怎樣

Figure lane flow 應寫成：

```text
extractor batch -> extractor local self-check
parent merge -> canonical mechanical validation
reviewer visual review -> parent merge review findings
repair worker -> repair local self-check
parent repair merge -> canonical mechanical validation
reviewer visual review again
lane close gate
```

Gate rule：

```text
Validator pass alone never closes the lane.
Reviewer pass without canonical mechanical validation also does not close the lane.
Both are required.
```

## 5. Reviewer Output 有兩套格式

### 問題在哪裡

目前 hand-written reviewer prompt 輸出：

```text
lanes/figures/reviews/round_00/reviewer_01/visual_review.json
```

但 old/new pipeline gate policy 使用：

```text
lanes/<lane>/reviews/round_XX/batches/batch_YY.json
```

且 schema 是：

```text
skills/_shared/schemas/review_batch.schema.json
```

兩者差異：

- `visual_review.json` 很適合 figure-specific detailed review。
- `review_batch.json` 很適合 cross-lane gate / repair manifest。
- 如果只保留 `visual_review.json`，generic gate scripts 不能直接吃。
- 如果只保留 `review_batch.json`，figure-specific edge checks 會被壓扁，除非放在 additional fields。

### 建議怎麼改

短期我建議保留 `visual_review.json` 作為 figure-specific truth，但 parent 需要再產生一份 gate summary。

選項 A：

```text
reviews/round_00/reviewer_01/visual_review.json
reviews/round_00/reviewer_01/review_batch.json
```

選項 B：

```text
reviews/round_00/batches/batch_01.json
```

其中 `batch_01.json` 是 `review_batch` shell，內部用 additional field 包完整 `visual_review`.

我偏好 B，因為 gate path 統一，但要保留詳細欄位。

### 修改完應該長怎樣

```json
{
  "schema_name": "review_batch",
  "lane": "figures",
  "round": 0,
  "batch": "reviewer_01",
  "scope": [{"figure_ids": ["Figure_1", "Figure_2"]}],
  "input_artifacts": [],
  "verdict": "fail",
  "coverage": {
    "assigned_surfaces": ["figures"],
    "coverage_percent": 100,
    "figures_checked": 2,
    "figures_total": 2,
    "pages_not_checked": [],
    "blocked_surfaces": [],
    "notes": []
  },
  "findings": [],
  "figure_visual_review": {
    "schema_version": "figure_review.v2",
    "figures": []
  }
}
```

Parent 可從 `figure_visual_review.figures[].repair_request` 轉成 repair requests。

## 6. Repair Handoff 有兩套格式

### 問題在哪裡

目前 hand-written repair prompt 讀：

```text
lanes/figures/repair/round_<N>/repair_requests_merged.json
```

新版流程讀：

```text
lanes/figures/repairs/round_<N>/repair_manifest.json
```

`repair_manifest.json` 是 generic gate contract；`repair_requests_merged.json` 是 figure-specific action contract。兩者各有用途。

### 建議怎麼改

短期先採用 figure-specific `repair_requests_merged.json`，因為它更清楚：

- assigned repair worker
- `figure_id`
- `crop_ids[]`
- `action`
- `direction`
- `constraint`
- defects
- evidence paths

但位置改成 `repairs/`，與其他流程一致：

```text
lanes/figures/repairs/round_01/repair_requests_merged.json
```

中期再讓 parent 同時產生 generic `repair_manifest.json`，把 `repair_requests_merged.json` 當 figure-specific payload。

### 修改完應該長怎樣

```text
lanes/figures/repairs/round_01/
  repair_manifest.json               # generic gate-level manifest
  repair_requests_merged.json        # figure-specific repair contract
  before_snapshot/
  before_snapshot.json
  repair_01/
    repair_report.json
    crops/
    previews/
  after_snapshot.json
```

`repair_manifest.json` 可以引用：

```json
{
  "figure_repair_requests": "lanes/figures/repairs/round_01/repair_requests_merged.json"
}
```

## 7. Parent Divide 規則不夠具體

### 問題在哪裡

`SKILL.md` 目前只說 worker/reviewer/repair 都可以 divide into parallel agents，但沒有明確 ownership rule。

這會造成：

- 兩個 extractor 都擷取同一張 figure。
- reviewer coverage 重疊或漏掉。
- repair workers 同時改同一個 figure/crop unit。
- parent merge 時不知道 conflict 是 block 還是擇一。

### 建議怎麼改

先制定 ownership：

- extraction ownership：以 page range 為主。
- review ownership：以 `figure_id` 為主。
- repair ownership：以 `figure_id` 為主，同一 figure 不拆給多個 repair workers。

### 修改完應該長怎樣

```text
Extraction divide:
  batch_01: pages 1-5
  batch_02: pages 6-10
  Each worker may inspect neighboring page previews for context, but may only own figures whose primary caption/visual anchor is in assigned pages.

Review divide:
  reviewer_01: Figure_1, Figure_2
  reviewer_02: Figure_3, Figure_4
  Reviewers read full canonical, but only write decisions for assigned figure_ids.

Repair divide:
  repair_01: Figure_2
  repair_02: Figure_4
  All crop_units of the same figure stay with one repair worker.
```

## 8. Parent Merge Contract 不夠具體

### 問題在哪裡

目前只說 parent/script merges worker outputs，但沒有說：

- JSON 如何合併
- paths 如何從 worker-local 改成 canonical
- crop PNG / previews 如何複製
- duplicate `figure_id` 怎麼辦
- 同一 figure 跨 batch 怎麼辦
- `unexpected_labeled_figures` / `omitted_candidates` 怎麼保留

### 建議怎麼改

Parent merge 必須是 deterministic，且只能做 mechanical work。遇到需要 judgment 的 conflict 就 block。

### 修改完應該長怎樣

Merge steps:

```text
1. Load all batch manifests.
2. Validate each batch with local v2 validator.
3. Check duplicate figure_id / crop_id.
4. Check cross-manifest figure_id consistency.
5. Copy crop PNGs to canonical.
6. Copy previews/source_regions/edges to canonical or canonical subdirs.
7. Rewrite worker-local paths to canonical paths.
8. Merge JSON lists.
9. Preserve unexpected_labeled_figures and omitted_candidates in a parent merge report.
10. Run canonical mechanical validation.
```

Conflict rules:

```text
duplicate figure_id with same label/page/caption:
  block; parent cannot decide which crop is better

duplicate figure_id with different label/page:
  block; likely assignment/schema error

same page figure split across adjacent extraction batches:
  block unless parent has an explicit ownership rule

missing crop/preview path:
  block canonical promotion
```

## 9. Cross-Batch Figure Boundary 還沒定義

### 問題在哪裡

如果 extraction 用 page ranges，figure 可能跨頁或 caption/visual 分散在 adjacent pages。現在沒有規則說誰負責。

### 建議怎麼改

加「primary anchor」規則：

- 若 figure caption 在 assigned page，該 batch owns figure。
- 若 caption 不清楚，主要 visual region 所在 page owns figure。
- 若跨頁 figure 的 anchor 在 assigned page，該 worker 可讀下一頁並產生多個 crop units。
- 被看到但不歸自己擁有的 labeled figure 放入 `unexpected_labeled_figures`。

### 修改完應該長怎樣

```text
Worker may read context pages outside assignment when needed.
Worker may only output official figures whose primary anchor belongs to its assignment.
Out-of-assignment labeled figures must be reported, not extracted.
```

## 10. Render / Preview / Helper Commands 沒有固定

### 問題在哪裡

`SKILL.md` 寫 `scripts/render_pages.py`，但 repo 裡實際 shared script 是：

```text
skills/_shared/scripts/render_pages.py
skills/_shared/scripts/make_image_preview.py
skills/_shared/scripts/crop_region.py
```

subagent prompts 也說「指定 helper」，但 parent 沒有明確傳入 helper paths。

### 建議怎麼改

在 `SKILL.md` 明確定義 helper command contract，parent dispatch subagent 時必須把這些路徑放進 prompt。

### 修改完應該長怎樣

```bash
python3 skills/_shared/scripts/render_pages.py \
  "<paper_dir>/input/source.pdf" \
  "<paper_dir>/shared/pages" \
  --dpi 300

python3 skills/_shared/scripts/make_image_preview.py \
  "<paper_dir>/shared/pages/page_N.png" \
  "<paper_dir>/shared/previews/page_N_preview.png" \
  --max-width 1400 --max-height 1400

python3 skills/_shared/scripts/crop_region.py \
  "<paper_dir>/shared/pages/page_N.png" \
  <x1> <y1> <x2> <y2> \
  "<output_png>" \
  --padding 0
```

## 11. Review Merge / Finding Dedupe 規則不足

### 問題在哪裡

`SKILL.md` 說 reviewer 都完成後 merge reviews，再 repair。但沒有定義：

- 多個 reviewer 對同一 figure 一 pass 一 fail 怎麼辦
- 多個 fail findings 如何去重
- fail finding 如何轉 repair request
- reviewer incomplete / malformed JSON 如何處理

### 建議怎麼改

採保守規則：任何 assigned reviewer 對 figure fail，該 figure 就需要 repair 或 explicit defer/override。

### 修改完應該長怎樣

```text
Review merge:
  - all assigned review outputs must exist and be valid JSON
  - pass + fail conflict -> fail
  - duplicate repair requests dedupe by figure_id + crop_ids + action + direction
  - conflicting repair directions for same crop -> keep both constraints and mark conflict in merged request
  - malformed reviewer output -> cannot close review barrier; spawn replacement or block
```

Example merged request:

```json
{
  "request_id": "Figure_2_req001",
  "assigned_repair_id": "repair_01",
  "figure_id": "Figure_2",
  "figure_label": "Fig. 2",
  "crop_ids": ["Figure_2_part_2"],
  "action": "recrop",
  "direction": ["expand_bottom"],
  "constraint": "Include the missing panel B x-axis title; stop before external caption.",
  "defects": [
    "Panel B bottom x-axis title is cut off."
  ],
  "source_reviews": [
    "lanes/figures/reviews/round_00/reviewer_01/visual_review.json"
  ],
  "evidence_paths": []
}
```

## 12. Repair Parent Merge / Snapshot 規則不足

### 問題在哪裡

Repair prompt 說 repair agent 不直接寫 canonical，parent merge / replace 到 canonical。但 `SKILL.md` 沒有定義 parent 如何做：

- before snapshot
- copy repair-local crops to canonical
- update `figure_decisions.json`
- update `figures.json`
- verify hash
- after snapshot
- stale review invalidation
- failed repair rollback

### 建議怎麼改

把 repair parent responsibilities 寫入 `SKILL.md`。

### 修改完應該長怎樣

```text
Before repair dispatch:
  parent writes repairs/round_XX/before_snapshot/
  parent writes repairs/round_XX/before_snapshot.json with hashes
  parent writes repair_requests_merged.json

After repair worker completes:
  parent reads repair_report.json
  parent verifies repair-local crops and hashes
  parent copies repair-local images/previews to canonical targets
  parent updates canonical figure_decisions.json and figures.json mechanically
  parent runs canonical mechanical validation
  parent writes after_snapshot.json
  parent marks previous reviews stale for changed figures
```

Rollback:

```text
If parent merge or validation fails after repair, restore canonical from before_snapshot and record repair_reverted.
```

## 13. Repair Round Limit 不一致

### 問題在哪裡

Current `SKILL.md` says default max repair rounds is 4. Old/new pipeline references often say 3.

這不是技術問題，但會讓 gate behavior 不一致。

### 建議怎麼改

明確選一個。我的建議：

- figure lane default max repair rounds: 4
- full pipeline default max repair rounds: 3 or 4 另行決定

因為 figure crop 邊界很容易需要多一輪，4 對 figure lane 合理。

### 修改完應該長怎樣

```text
Default max repair rounds:
  figures: 4
  tables: 3
  equations: 3
  text: 3
  reassembly: 3
```

或若要簡化：

```text
Default max repair rounds: 4 for every lane unless user overrides.
```

## 14. Trace / Gate / Artifact Registry 還不完整

### 問題在哪裡

`SKILL.md` 有列 trace files，但沒有說 figure lane 每個階段要寫哪些 event，也沒有說 artifact registry 要登記哪些 artifacts。

如果沒有 trace / registry，之後很難知道：

- 哪個 worker 產生哪個 batch
- 哪個 merge report 對應哪次 canonical
- 哪些 review 因 repair stale
- 哪些 outputs 是 official artifacts

### 建議怎麼改

先定義最小 trace events。

### 修改完應該長怎樣

```text
trace/run.jsonl:
  figure_render_started
  figure_render_completed
  figure_merge_started
  figure_merge_completed
  figure_validation_completed
  figure_repair_merge_completed

trace/agents.jsonl:
  figure_extractor_spawned/completed
  figure_reviewer_spawned/completed
  figure_repair_spawned/completed

trace/gates.jsonl:
  figures_extraction_merge_gate
  figures_review_round_00_gate
  figures_repair_round_01_gate
  figures_lane_close_gate

trace/artifact_registry.json:
  canonical figure JSONs
  canonical crop PNGs
  canonical previews
  validation reports
  merged review reports / repair request manifests
```

## 15. Agent Dispatch Prompt Template 缺失

### 問題在哪裡

`SKILL.md` 說 prompt 都在 `subagent_prompts`，但 parent dispatch 時應該填什麼 concrete input/output/scope 沒寫。

如果 parent 只把 prompt 丟給 subagent，subagent 可能不知道：

- `paper_dir`
- assigned pages / figure_ids / repair_id
- write scope
- helper command paths
- expected output files
- forbidden paths

### 建議怎麼改

在 `SKILL.md` 增加 dispatch template。

### 修改完應該長怎樣

```text
When spawning a figure extractor, parent must include:
  - prompt reference
  - paper_dir
  - batch_id
  - assigned pages
  - allowed write directory
  - helper commands
  - required output files
  - note that parent owns canonical merge

When spawning a reviewer, parent must include:
  - review_round
  - reviewer_id
  - assigned figure_ids
  - canonical dir
  - allowed review output dir
  - helper commands

When spawning a repair worker, parent must include:
  - repair_round
  - repair_id
  - repair_requests_merged.json
  - assigned request_ids
  - canonical dir read-only
  - repair-local output dir writable
```

## 16. Empty Figure Scope 的 Merge/Validation Policy 不清楚

### 問題在哪裡

Extractor prompt 有說如果範圍內沒有 labeled figure，仍要寫四個 JSON，`figures` 為空。但 current merge script 舊版會把 empty merged list 視為 error。

### 建議怎麼改

Parent / validator 要區分：

- whole paper has no figures
- this batch has no figures
- expected figures missing

Batch-level empty 可以 pass；canonical whole-paper empty 只有在 all batches 都沒有 unexpected/missing expected figures 時才 pass。

### 修改完應該長怎樣

```text
batch_02 has no figures:
  allowed if status complete and no expected figures assigned

canonical has no figures:
  allowed only if all batches complete and no labeled figures were reported in unexpected_labeled_figures
```

## 17. `figures.json.status = incomplete` 的 Gate 行為不清楚

### 問題在哪裡

Extractor 可以記錄 failed figure，並將 `figures.json.status` 設為 `incomplete`。但 parent 不知道這時候要：

- merge 到 canonical 後 review？
- 直接重新 extraction？
- 直接 repair？
- block？

### 建議怎麼改

把 incomplete 分成兩類：

- mechanical incomplete：缺檔、JSON 壞、crop 不存在。不能 promote。
- visual incomplete：crop 存在但 extractor 自己覺得 fail。可以 promote to canonical for review/repair，但 gate cannot close。

### 修改完應該長怎樣

```text
If batch is mechanically invalid:
  do not merge; fix/respawn extractor.

If batch is mechanically valid but visual status incomplete:
  merge to canonical with status incomplete;
  run reviewer;
  create repair requests from extractor verification + reviewer findings.
```

## 18. Source Regions / Edges / Previews 的 Canonical Placement 要定義

### 問題在哪裡

Extractor prompt 會產：

```text
source_regions/
edges/
previews/
```

但 parent merge 後 canonical 是否要保留同樣結構，還是只保留 previews 和 final crops，沒有定義。

### 建議怎麼改

保留所有 visual evidence，但 canonical 下做清楚分類。

### 修改完應該長怎樣

```text
lanes/figures/canonical/
  figure_candidates.json
  figure_index.json
  figure_decisions.json
  figures.json
  Figure_1.png
  previews/
    Figure_1_preview.png
    Figure_1_top_preview.png
  source_regions/
    batch_01_p003_src001.png
  edges/
    Figure_1_top.png
```

Path rewrite rule：

```text
All paths in canonical JSON should be relative to <paper_dir>.
All copied evidence files must have collision-safe names.
```

## 19. Current Shared Figure Merge Script 不支援 v2 Path Rewrite

### 問題在哪裡

`merge_batch_manifests.py` 目前做的是簡單 list merge 和 PNG/previews copy。它不知道 v2：

- `crop_units[].image_file`
- `crop_units[].preview`
- `crop_units[].edge_previews`
- `source_regions[].source_image`
- `source_regions[].source_preview`
- worker-local path rewrite

### 建議怎麼改

更新 `merge_batch_manifests.py` 或新增 `merge_figure_v2.py`。

### 修改完應該長怎樣

```bash
python3 skills/_shared/scripts/merge_figure_v2.py \
  --batches-dir "<paper_dir>/lanes/figures/batches" \
  --canonical-dir "<paper_dir>/lanes/figures/canonical" \
  --report "<paper_dir>/lanes/figures/validation/figures_merge_report.json"
```

Report should include:

```json
{
  "status": "pass",
  "batch_count": 2,
  "figures_merged": 8,
  "files_copied": [],
  "paths_rewritten": [],
  "conflicts": [],
  "warnings": []
}
```

## 20. Current Figure Validator Review Shape 不支援 v2 Reviewer Shape

### 問題在哪裡

Hand-written reviewer prompt uses:

```json
"source_edge_previews_read": {
  "crop_units": []
}
```

Current validator expected older flatter structures in parts of its code.

### 建議怎麼改

Validator v2 should inspect per-crop-unit review evidence:

- every `crop_units[].crop_id` appears exactly once in:
  - source edge previews
  - crop previews
  - edge checks
  - crop hashes
- every edge has both source and crop evidence
- pass requires every edge status pass

### 修改完應該長怎樣

```text
review figure pass iff:
  - decision == pass
  - all checks pass
  - every crop unit has top/bottom/left/right edge checks
  - every crop hash matches current canonical crop
  - source evidence exists and is reviewer-created
```

## 21. Parent 不應用自己的 Judgment 補 Artifacts

### 問題在哪裡

`SKILL.md` 有說 parent 不能做 extraction/review judgment，但 merge/repair 流程中仍可能有模糊地帶。例如：

- parent 從 crop files 回填 `figures.json`
- parent 合併 reviews 時改寫 defect
- parent 幫 reviewer 補 pass notes
- parent 決定 duplicate crop 哪個比較好

### 建議怎麼改

加一個 explicit parent boundary：

```text
Parent can:
  copy, merge, rewrite paths, validate JSON, hash, snapshot, assign work

Parent cannot:
  invent crop boxes, visual verdicts, defects, pass notes, expected panels, visual units, scientific values
```

### 修改完應該長怎樣

如果 merge 需要 judgment：

```text
block and spawn a resolving agent, or ask human.
```

## 22. Reviewer 和 Repair 的 Final Validator Responsibility 應重新分配

### 問題在哪裡

Reviewer prompt 說寫完 `visual_review.json` 後必定執行 final validator，寫到 `figures_validation.json`。Repair prompt 說 parent merge 後必須重新 canonical mechanical validation。

這裡有一點混亂：reviewer 不應該負責 canonical final gate；parent 比較適合負責 validator invocation，因為 validator 是 gate input。

### 建議怎麼改

Reviewer 可以做 optional local support validation，但正式 validation 由 parent 做。

### 修改完應該長怎樣

```text
Reviewer:
  writes review JSON and evidence previews
  may run helper checks if useful
  does not own gate validation report

Parent:
  validates reviewer JSON shape
  runs canonical figures validation with review JSON
  writes lanes/figures/validation/figures_validation.json
```

## 23. File Names and Paths Need One Canonical Convention

### 問題在哪裡

Current v2 prompt says `image_file` should be a path, e.g.

```text
lanes/figures/worker_output/worker_01/Figure_1.png
```

Old schema says `image_files` should be filenames only.

這是 schema 決策問題，不是小 typo。

### 建議怎麼改

For v2, use relative paths from `<paper_dir>` everywhere. This makes worker-local and canonical artifacts explicit.

### 修改完應該長怎樣

```json
{
  "crop_id": "Figure_1",
  "page": 3,
  "crop_px": [120, 300, 2380, 1850],
  "image_file": "lanes/figures/canonical/Figure_1.png",
  "preview": "lanes/figures/canonical/previews/Figure_1_preview.png",
  "edge_previews": {
    "top": "lanes/figures/canonical/previews/Figure_1_top_preview.png",
    "bottom": "lanes/figures/canonical/previews/Figure_1_bottom_preview.png",
    "left": "lanes/figures/canonical/previews/Figure_1_left_preview.png",
    "right": "lanes/figures/canonical/previews/Figure_1_right_preview.png"
  },
  "role": "complete figure"
}
```

Validator should resolve these paths relative to `<paper_dir>`.

## 24. Figure Inventory Repair Policy 還不清楚

### 問題在哪裡

Repair prompt 說不要重建 figure inventory，也不要新增全新 figure。但 reviewer 可能發現：

- canonical missing a figure
- label wrong
- candidate link wrong
- expected panels wrong

這些不是單純 recrop。

### 建議怎麼改

分級：

- crop defect：repair worker can recrop.
- manifest defect within assigned figure：repair worker can propose manifest correction.
- missing/new figure：block current repair; spawn extractor continuation or human decision.

### 修改完應該長怎樣

```text
If reviewer finds missing figure:
  parent creates extraction-continuation request, not normal crop repair.

If reviewer finds wrong panel list:
  repair request action = manifest_correction.

If reviewer finds wrong label/caption for same figure:
  repair request action = manifest_correction.
```

## 25. First Runnable MVP Should Be Narrower

### 問題在哪裡

Trying to solve all lanes and all figure edge cases at once will make the first run hard to debug.

### 建議怎麼改

先定義 MVP:

- one PDF
- one figure extraction batch for all pages
- one reviewer
- one repair worker at a time
- v2 schema
- parent canonical merge even if only one batch
- no reassembly

### 修改完應該長怎樣

MVP command flow:

```text
init paper_dir
render pages
create shared previews
spawn figure_extractor batch_01 all pages
validate batch_01 v2 mechanical-only
merge batch_01 -> canonical
validate canonical v2 mechanical-only
spawn figure_reviewer reviewer_01 all figures
parent builds repair_requests_merged.json
if fail:
  snapshot canonical
  spawn figure_repair repair_01
  parent merges repair output
  validate canonical
  rerun reviewer
close figure lane
```

This MVP should pass before we add:

- multiple extraction batches
- multiple reviewers
- multiple repair workers
- review_batch wrapper
- generic repair_manifest wrapper
- full handoff to reassembly

