# 目標

這是一份給 pipeline orchestrator 看的指引。

此流程使用場景與目標：
- 輸入：一個 pdf 檔案。
- 輸出：後續可重組成 html 檔案與 md 檔案的 lane artifacts。
- 目標：最大程度讓輸出的 html / md 貼近原始 pdf，以利後續閱讀、分析與筆記。

目前先實作第一階段：讓 figure lane 用最少修改跑起來。下面先定義第一階段的邊界，再描述實際流程。

# 第一階段邊界

第一階段只跑 figure lane，目標是讓短 PDF 能走完：

```text
render pages -> extract -> copy canonical -> review -> repair -> review loop -> close/block
```

第一階段固定使用：
- 一個 extraction worker：`worker_01`。
- 一個 reviewer：`reviewer_01`。
- 每個 repair round 一個 repair worker：`repair_01`。
- `worker_output/worker_01/` 到 `canonical/` 的單純搬運，不做多 worker 語意合併。
- Reviewer 的 `visual_review.json` 作為 close/block/repair gate。
- Extractor、reviewer、repair 各自的 local self-check。

下列事項保留到第二階段，不在第一階段處理：
- text、table、equation、reassembly lanes。
- 多個 extraction workers。
- page-range assignment file。
- cross-page figure ownership policy。
- supplemental workers。
- 多 worker extraction merge scripts。
- parent canonical validation 作為 gate evidence。
- `validate_figures.py` 作為正式 close gate。
- review divide/merge。
- repair divide/merge。
- crop hash freshness gate。

# 流程

## 流程總覽

你是 pipeline orchestrator。流程是：

1. Parent 先建立 `<paper_dir>`，複製來源 PDF，render page images，建立 page previews。這是所有 lane 共用的前置工作，不屬於 figure lane 本身。

2. Parent 啟動 `figure_extractor` subagent，使用 `worker_01` 擷取全部頁面。

3. Extractor 完成 individual self-check 後，parent 把 `worker_output/worker_01/` 的成果整棵複製到 `canonical/`。這一步只是搬運，不做語意合併，也不改寫 JSON path。

4. Parent 啟動 `figure_reviewer` subagent，使用 `reviewer_01` 審查 canonical artifacts。Reviewer 只讀 `canonical/`、`input/source.pdf`、`shared/pages/` 與 `shared/previews/`，並寫出 `visual_review.json`。

5. Parent 讀取 `visual_review.json` 做 gate：
   - 全部 pass：figure lane close。
   - 有 repairable fail：parent 機械式建立 `repair_requests_merged.json`，再啟動 repair。
   - inventory 錯誤、缺檔、duplicate id、無法 repair 或 repair round 超過上限：block。

6. Parent 啟動 `figure_repair` subagent。每輪使用 `repair_01`。Repair 不直接寫入 `canonical/`，只在自己的 repair 目錄寫出修復圖片、preview 與 `repair_report.json`。

7. Parent 按照 `repair_report.json` 裡可機械執行的 merge 指令，把 repair output 搬進 `canonical/`，必要時套用 `manifest_patches[]`。改過 canonical 後，先前 review 失效，必須重新啟動 `figure_reviewer`。

## 前置工作：建立 paper directory 與 pages

Parent 在 figure lane 開始前先完成共同前置工作：

```text
<paper_dir>/
  input/
    source.pdf
  shared/
    pages/
      page_1.png
      page_2.png
      ...
    previews/
      page_1_preview.png
      page_2_preview.png
      ...
  lanes/
    figures/
      worker_output/
      canonical/
      reviews/
      repairs/
      validation/
  trace/
```

需要用到的 scripts 放在本 skill 底下，不直接呼叫 `skills/_shared/scripts/`：

```bash
python3 agents/scripts/render_pages.py \
  "<paper_dir>/input/source.pdf" \
  "<paper_dir>/shared/pages" \
  --dpi 300

python3 agents/scripts/make_image_preview.py \
  "<paper_dir>/shared/pages/page_N.png" \
  "<paper_dir>/shared/previews/page_N_preview.png" \
  --max-dim 1568
```

`render_pages.py` 會產生完整解析度頁面圖片。`make_image_preview.py` 會產生給 agent 讀取的受限尺寸 page preview。若輔助工具需要修改，修改 `agents/scripts/` 內的 local copy，不要改 `_shared` 版本。

## Figure lane 輸出位置

Figure lane 使用下列目錄：

```text
<paper_dir>/
  lanes/
    figures/
      worker_output/
        worker_01/
          figure_candidates.json
          figure_index.json
          figure_decisions.json
          figures.json
          crops/
          source_regions/
          edges/
          previews/

      canonical/
        figure_candidates.json
        figure_index.json
        figure_decisions.json
        figures.json
        crops/
        source_regions/
        edges/
        previews/

      reviews/
        round_00/
          reviewer_01/
            visual_review.json
            previews/

      repairs/
        round_01/
          repair_requests_merged.json
          before_snapshot/
          repair_01/
            repair_report.json
            crops/
            previews/
            manifest_updates/

      validation/
        # 保留給第二階段 canonical validation。
```

Figure lane 使用 `repairs/`，不要使用舊的 `repair/`。

## Round 命名規則

Initial review 一律寫到：

```text
lanes/figures/reviews/round_00/reviewer_01/
```

如果 `reviews/round_00/reviewer_01/visual_review.json` 產生 repairable fail，parent 建立：

```text
lanes/figures/repairs/round_01/
```

`repairs/round_01/` 合併回 canonical 後，下一輪 review 寫到：

```text
lanes/figures/reviews/round_01/reviewer_01/
```

之後依此類推：`repairs/round_N/` 修復 `reviews/round_(N-1)/` 發現的問題；`reviews/round_N/` 審查 `repairs/round_N/` 合併後的 canonical。不得覆寫舊的 review 或 repair 目錄。

## Artifact root 相對路徑

Figure extraction artifacts 裡指向 figure lane 檔案的 path，都使用 artifact root 相對路徑。也就是說，同一個 JSON path 會依照目前讀取它的 artifact root 解析：

- Extractor self-check 時，artifact root 是 `<paper_dir>/lanes/figures/worker_output/worker_01/`。
- Reviewer 讀 canonical 時，artifact root 是 `<paper_dir>/lanes/figures/canonical/`。
- Repair 讀 canonical 時，artifact root 也是 `<paper_dir>/lanes/figures/canonical/`。
- Parent 搬 repair output 時，`repair_output` 以 `<paper_dir>/lanes/figures/repairs/round_<N>/repair_<ID>/` 為 root；`canonical_target` 以 `<paper_dir>/lanes/figures/canonical/` 為 root。

正確寫法：

```text
crops/Figure_1.png
previews/Figure_1_preview.png
previews/Figure_1_bottom_preview.png
source_regions/p003_src001.png
edges/Figure_1_bottom.png
```

不要在 figure artifact path 裡寫 worker、canonical 或絕對路徑：

```text
lanes/figures/worker_output/worker_01/crops/Figure_1.png
lanes/figures/canonical/crops/Figure_1.png
/absolute/path/to/crops/Figure_1.png
```

`shared/pages/page_3.png` 和 `shared/previews/page_3_preview.png` 不是 figure lane artifact，所以仍使用 paper-dir-relative path。Reviewer 或 repair 自己建立的 evidence previews 如果不在 canonical artifact root 裡，也可以記錄為 paper-dir-relative path，例如 `lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_context_preview.png`。

## 擷取 figure

Parent 啟動一個 `figure_extractor` subagent，prompt 使用：

```text
agents/subagent_prompts/figure_extractor.md
```

Assignment：

```text
paper_dir: <paper_dir>
worker_id: worker_01
output_root: <paper_dir>/lanes/figures/worker_output/worker_01
artifact_root: <paper_dir>/lanes/figures/worker_output/worker_01
pages: 全部頁面
```

Extractor 寫出：

```text
lanes/figures/worker_output/worker_01/
```

Extractor 在 final response 前必須做 individual self-check。這個 self-check 只檢查本 worker output：JSON 能 parse、必要檔案存在、artifact root 相對路徑 resolve 後能找到檔案、`figures.json` 和 `figure_decisions.json` 的 `crop_units` 一致。它不是 parent canonical validation。

## Parent copy 到 canonical

Extractor 完成後，parent 把整棵 worker output 搬進 canonical：

```text
worker_output/worker_01/figure_candidates.json -> canonical/figure_candidates.json
worker_output/worker_01/figure_index.json      -> canonical/figure_index.json
worker_output/worker_01/figure_decisions.json  -> canonical/figure_decisions.json
worker_output/worker_01/figures.json           -> canonical/figures.json
worker_output/worker_01/crops/                 -> canonical/crops/
worker_output/worker_01/source_regions/        -> canonical/source_regions/
worker_output/worker_01/edges/                 -> canonical/edges/
worker_output/worker_01/previews/              -> canonical/previews/
```

這一步只搬檔，不改寫 JSON path。因為 `figures.json`、`figure_decisions.json` 等檔案內的 figure artifact path 已經是 artifact root 相對路徑，搬到 `canonical/` 後仍能用同一組 path 被 reviewer 解析。

## 審查 figure

Parent 啟動一個 `figure_reviewer` subagent，prompt 使用：

```text
agents/subagent_prompts/figure_reviewer.md
```

Initial review assignment：

```text
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
canonical_artifact_root: <paper_dir>/lanes/figures/canonical
output_root: <paper_dir>/lanes/figures/reviews/round_00/reviewer_01
scope: canonical/figures.json 中的全部 figures
```

Reviewer 寫出：

```text
lanes/figures/reviews/round_00/reviewer_01/visual_review.json
```

Reviewer 不修改 canonical artifacts，也不補建 canonical crop preview 或 edge preview。若 canonical crop preview / edge preview 缺失，該 figure 直接 fail，repair request 使用 `regenerate_missing_preview`，並寫明 `missing canonical preview` 或 `missing canonical edge preview`。Reviewer 可以做 `visual_review.json` 的 local self-check。Review 的重點是視覺判斷：final crop 是否完整、乾淨，四邊是否切掉 figure 內容或混入非 figure 內容。

## Gate

Parent 只根據 `visual_review.json` 做 gate。

關閉條件：

```text
visual_review.json.status == "pass"
且每個 figure decision 都是 "pass"
```

進入 repair 的條件：

```text
visual_review.json.status == "fail"
且至少一個 failed figure 有 repairable repair_request
```

阻塞條件：

```text
missing figure inventory
duplicate figure ids
wrong figure inventory
required next-step files are absent
repair round limit reached
review fails but no repairable request exists
```

Parent 不得自己做 visual judgment 來 override reviewer。

## 建立 repair request

如果 reviewer 發現 repairable fail，parent 從 `visual_review.json` 機械式建立：

```text
lanes/figures/repairs/round_01/repair_requests_merged.json
```

因為只有一個 repair worker，所以 assignment 可以很簡單。以下以第一輪 repair 為例：

```json
{
  "schema_version": "figure_repair.v2",
  "repair_round": "round_01",
  "source_reviews": [
    "lanes/figures/reviews/round_00/reviewer_01/visual_review.json"
  ],
  "assignments": [
    {
      "repair_id": "repair_01",
      "figure_ids": ["Figure_2"],
      "request_ids": ["Figure_2_req001"]
    }
  ],
  "requests": []
}
```

Parent 不在 repair request 裡發明座標。Repair request 只描述 defect、action、direction 和 constraint；新的 `crop_px` 由 repair worker 讀 source page evidence 後決定。若 action 是 `regenerate_missing_preview`，parent 必須把 reviewer report 裡的 `missing_canonical_artifacts[]` 搬進對應 request，讓 repair worker 機械式知道要重建哪些 preview。

執行 repair 前，parent 先保存 canonical snapshot：

```text
canonical/ -> repairs/round_01/before_snapshot/
```

## 修復 figure

Parent 啟動一個 `figure_repair` subagent，prompt 使用：

```text
agents/subagent_prompts/figure_repair.md
```

Repair assignment：

```text
paper_dir: <paper_dir>
repair_round: round_01
repair_id: repair_01
canonical_artifact_root: <paper_dir>/lanes/figures/canonical
repair_artifact_root: <paper_dir>/lanes/figures/repairs/round_01/repair_01
request_file: <paper_dir>/lanes/figures/repairs/round_01/repair_requests_merged.json
```

Repair worker 寫出：

```text
lanes/figures/repairs/round_01/repair_01/repair_report.json
lanes/figures/repairs/round_01/repair_01/crops/
lanes/figures/repairs/round_01/repair_01/previews/
lanes/figures/repairs/round_01/repair_01/manifest_updates/   # 只有 manifest 欄位改變時才需要
```

Repair worker 不直接寫 `canonical/`。`repair_report.json` 必須清楚列出 parent 要搬哪些檔案、搬到 canonical 的哪個 target，以及是否需要套用 `manifest_patches[]`。`repair_output` 使用 repair artifact root 相對路徑；`canonical_target` 使用 canonical artifact root 相對路徑。

## Parent 合併 repair output

Parent 只套用 `repair_report.json` 裡明確列出的 merge 指令。

允許的 parent 動作：
- 執行 `merge.file_copies[]`：將 repair-local crop、preview 或 edge preview 複製到指定的 canonical target。
- 執行 `merge.manifest_patches[]`：對同一個 `figure_id` / `crop_id` 套用允許清單內的 manifest patch，例如 `crop_px`、`image_file`、`preview`、`edge_previews`、`verification`、`evidence_read` 和 repair notes。
- 只有當 `repair_report.json` 明確指定 canonical target manifest 時，才可以從 `manifest_updates/` 搬整份 replacement manifest。

`merge.file_copies[]` 的每個 entry 必須同時提供 source 和 target：

```json
{
  "kind": "crop_preview",
  "figure_id": "Figure_2",
  "crop_id": "Figure_2_part_2",
  "repair_output": "previews/Figure_2_part_2_preview.png",
  "canonical_target": "previews/Figure_2_part_2_preview.png"
}
```

`kind` 只使用 `crop`、`crop_preview` 或 `edge_preview`。

`merge.manifest_patches[]` 的每個 entry 必須可以讓 parent 不做推理就套用：

```json
{
  "target_file": "figures.json",
  "operation": "replace",
  "scope": "crop_unit",
  "selector": {"figure_id": "Figure_2", "crop_id": "Figure_2_part_2"},
  "path": "crop_units[].crop_px",
  "old_value": [1320, 420, 2260, 1260],
  "new_value": [1320, 420, 2260, 1310]
}
```

Parent 只允許 `operation` 為 `replace` 或 `add_if_missing`。Parent 只允許 `target_file` 為 `figures.json`、`figure_decisions.json`，或在 request 明確要求 `manifest_correction` 時使用 `figure_index.json`。Parent 套用 `replace` 前必須先確認 `old_value` 和 canonical 目前值一致；套用 `add_if_missing` 前必須先確認目標欄位不存在；不一致就 block，不猜測、不強行覆蓋。若同一個 crop unit 在 `figures.json` 和 `figure_decisions.json` 都有相同欄位，repair report 必須提供兩份 patch，讓兩個 manifest 保持一致。

不允許的 parent 動作：
- 代替 reviewer 或 repair worker 做 visual judgment。
- 自己發明新的 crop coordinate。
- 靜默覆蓋另一個 figure 或 crop id。
- 做 duplicate-id reconciliation。
- 做 multi-worker merge。
- 把 parent canonical validation 當作 gate。

Parent 更新 canonical 後，改過的 figure 先前 review 都失效。下一步一定是重新啟動 `figure_reviewer`，不能直接 close。如果剛合併的是 `repairs/round_01/`，新的 review 寫到 `reviews/round_01/reviewer_01/`；如果剛合併的是 `repairs/round_02/`，新的 review 寫到 `reviews/round_02/reviewer_01/`。

# 格式

## 輸出格式

- Agent primary reports 和 decisions 只能是 JSON。
- Markdown reports 或 traces 必須由 JSON/JSONL 產生，不能成為 source of truth。
- Parent 可以做機械式 JSON cleanup 或允許清單內的 patch，但不能編造 verdicts、findings、coverage、source evidence、crop coordinate 或 scientific values。

# 規則

## 使用 subagent 的規則

- 這個 pipeline 中所有 worker、reviewer、repair 都要啟動獨立 subagents。
- 不得用 parent agent 的工作取代 worker、reviewer 或 repair subagent。
- 當工作需要 worker/reviewer judgment 時，parent 不得自己執行 extraction、visual review、repair visual acceptance、text assembly、reassembly 或 final review。
- 如果 agent 啟動失敗，先修正 prompt、tool 或 context blockers，然後重試。若仍無法啟動 agents，停止並回報 `blocked`。

## Review 和 repair 規則

- Figure lane 預設最多 4 個 repair rounds，除非使用者明確改變 scope。
- 任何改動 crop 或 manifest 的 repair 都會讓 repaired figure 先前的 review 失效，一定要重新完整 review。
- Reviewer 必須完整檢查規範之內應該檢查的所有內容。不能發現第一個問題就中斷 review 後直接 repair。
- Parent 只在 review 完成後建立 repair request。若未來 review 被 divide 成多個 reviewer，必須等所有 reviewer 完成並 merge review reports 後才進 repair。

## 輔助工具

Figure lane 使用的輔助工具都放在本 skill 內：

```text
agents/scripts/render_pages.py
agents/scripts/make_image_preview.py
agents/scripts/crop_region.py
```

輔助工具可以 render pages、建立 preview、裁切圖片、檢查檔案是否存在；輔助工具不能判定 crop 是否視覺完整、caption 是否外漏、座標軸是否被切掉，或 figure 是否應該 pass。這些判斷必須由 extractor、reviewer 或 repair agent 讀過對應 previews 後完成。
