# 目標

這是一份給 pipeline orchestrator 看的指引。

此流程使用場景與目標：
- 輸入：一個 PDF 檔案。
- 輸出：後續可重組成 HTML / Markdown 的 lane artifacts。
- 目標：最大程度讓輸出的 HTML / Markdown 貼近原始 PDF，以利後續閱讀、分析與筆記。

目前先實作第一階段：single worker、single reviewer、single repair worker 的 figure lane。這一版先把可跑通的 handoff 架起來，不做多 worker / 多 reviewer / 多 repair merge。

# 第一階段邊界

第一階段只跑 figure lane：

```text
render pages
-> extract with worker_01
-> parent promotes worker output into canonical/
-> reviewer_01 reads canonical/
-> parent promotes review output into canonical/
-> repair_01 reads canonical/
-> parent merges repair output into canonical/
-> rerun reviewer in the next round
-> close/block
```

第一階段固定使用：
- 一個 extraction worker：`worker_01`。
- 一個 reviewer：`reviewer_01`。
- 每個 repair round 一個 repair worker：`repair_01`。
- `canonical/` 是每個下游 agent 的唯一 handoff root。
- Round number 是 generation boundary：`reviews/round_00/` 審 extraction merge 後的 canonical；`repairs/round_01/` 修 `round_00` review 發現的問題；`reviews/round_01/` 審 `round_01` repair merge 後的 canonical。
- 不使用 hash。不要在 reviewer、repair report、gate 或 review freshness 中寫 crop hash。

下列事項保留到第二階段，不在第一階段處理：
- text、table、equation、reassembly lanes。
- 多個 extraction workers。
- page-range assignment file。
- cross-page figure ownership policy。
- supplemental workers。
- 多 worker extraction merge scripts。
- review divide/merge。
- repair divide/merge。
- parent canonical validation 作為正式 gate evidence。
- `validate_figures.py` 作為正式 close gate。

# 流程

## 流程總覽

你是 pipeline orchestrator。流程是：

1. Parent 建立 `<paper_dir>`，複製來源 PDF，render page images，建立 page previews。這是所有 lane 共用的前置工作，不屬於 figure lane 本身。

2. Parent 啟動 `figure_extractor` subagent。Extractor 寫入 `lanes/figures/worker_output/worker_01/`。

3. Parent 把 `worker_output/worker_01/` 整棵 promote 進 `lanes/figures/canonical/`。這一步只搬檔，不改寫 JSON path，不做多 worker 語意合併。

4. Parent 從 canonical `figures.json` 建立 `review_packet.json`，放在 `reviews/round_00/reviewer_01/`。Reviewer 讀這個 packet，自己在 `output_root/source_previews/` 建立 source evidence，再讀 source evidence 與 canonical crop / boundary / edge previews，寫出 `visual_review.json`。

5. Parent 把 `reviews/round_00/reviewer_01/review_packet.json`、`visual_review.json` 和 `source_previews/` promote 進 `canonical/reviews/round_00/reviewer_01/`。Gate 一律讀 canonical 裡的 promoted review。

6. 若 review 全部 pass，figure lane close。若 review 有 required findings，parent 從 canonical review 機械式建立 `repair_requests_merged.json`，並 promote 到 `canonical/repair_requests/round_01/repair_requests_merged.json`。

7. Parent 啟動 `figure_repair` subagent。Repair 讀 canonical extraction artifacts、canonical review 和 canonical repair request；repair output 寫入 `repairs/round_01/repair_01/`，不直接寫 canonical。

8. Parent 按照 `repair_report.json` 裡的 `merge.file_copies[]` 和 `merge.manifest_patches[]` 更新 canonical。任何 canonical crop / preview / manifest 被更新後，上一輪 review 失效；下一步一定是建立下一輪 `review_packet.json` 並重新啟動 reviewer。

Parent 不做 visual judgment。Parent 只搬檔、建立 packet、建立 repair request、套用 allowlisted merge 指令和做最小 mechanical preflight。

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

## Figure lane 目錄

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
          boundaries/
          previews/

      canonical/
        figure_candidates.json
        figure_index.json
        figure_decisions.json
        figures.json
        crops/
        source_regions/
        boundaries/
        previews/
        reviews/
          round_00/
            reviewer_01/
              review_packet.json
              visual_review.json
              source_previews/
        repair_requests/
          round_01/
            repair_requests_merged.json

      reviews/
        round_00/
          reviewer_01/
            review_packet.json
            visual_review.json
            source_previews/

      repairs/
        round_01/
          before_snapshot/
          repair_01/
            repair_report.json
            crops/
            boundaries/
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

Parent promote 後，canonical copy 在：

```text
lanes/figures/canonical/reviews/round_00/reviewer_01/
```

如果 `canonical/reviews/round_00/reviewer_01/visual_review.json` 有 required findings，parent 建立：

```text
lanes/figures/canonical/repair_requests/round_01/repair_requests_merged.json
lanes/figures/repairs/round_01/
```

`repairs/round_01/` 合併回 canonical 後，下一輪 review 寫到：

```text
lanes/figures/reviews/round_01/reviewer_01/
lanes/figures/canonical/reviews/round_01/reviewer_01/
```

之後依此類推：`repairs/round_N/` 修復 `canonical/reviews/round_(N-1)/` 發現的問題；`reviews/round_N/` 審查 `repairs/round_N/` 合併後的 canonical。不得覆寫舊的 review 或 repair 目錄。Round number 就是 generation boundary，不需要額外 `canonical_generation` 欄位。

## Artifact root 相對路徑

Figure extraction artifacts 裡指向 figure lane 檔案的 path，都使用 artifact root 相對路徑。也就是說，同一個 JSON path 會依照目前讀取它的 artifact root 解析：

- Extractor self-check / validator 時，artifact root 是 `<paper_dir>/lanes/figures/worker_output/worker_01/`。
- Reviewer 讀 crop / boundary / edge previews 時，artifact root 是 `<paper_dir>/lanes/figures/canonical/`；reviewer 自己建立並記錄的 `source_evidence` 以本輪 reviewer `output_root` 為 root。
- Repair 讀 canonical artifacts 時，artifact root 也是 `<paper_dir>/lanes/figures/canonical/`。
- Parent 搬 repair output 時，`repair_output` 以 `<paper_dir>/lanes/figures/repairs/round_<N>/repair_<ID>/` 為 root；`canonical_target` 以 `<paper_dir>/lanes/figures/canonical/` 為 root。

正確寫法：

```text
crops/Figure_1.png
previews/Figure_1_preview.png
previews/Figure_1_boundary_preview.png
previews/Figure_1_bottom_seg1_preview.png
source_regions/p003_src001.png
boundaries/Figure_1.png
```

不要在 figure artifact path 裡寫 worker、canonical 或絕對路徑：

```text
lanes/figures/worker_output/worker_01/crops/Figure_1.png
lanes/figures/canonical/crops/Figure_1.png
/absolute/path/to/crops/Figure_1.png
```

`shared/pages/page_3.png` 和 `shared/previews/page_3_preview.png` 不是 figure lane artifact，所以仍使用 paper-dir-relative path。

## 擷取 figure

Parent 啟動一個 `figure_extractor` subagent。Prompt 由兩部分依序拼接組成：

1. 讀取下列檔案的完整內容，原封不動作為 prompt 主體：

```text
agents/subagent_prompts/figure_extractor.md
```

2. 在末尾附加 assignment 區塊：

```text
---
## Assignment
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

Extractor 在 final response 前必須執行 individual validator：

```bash
python3 agents/scripts/validate_figure_extraction.py \
  "<paper_dir>/lanes/figures/worker_output/worker_01" \
  --paper-dir "<paper_dir>"
```

這個 validator 只檢查本 worker output：JSON 能 parse、必要檔案存在、artifact root 相對路徑 resolve 後能找到檔案、`figures.json` 和 `figure_decisions.json` 的 `crop_units` 一致，且每個 crop unit 都有 crop preview、boundary preview 和四邊 edge previews（每邊至少一個 segment）。它不是 parent canonical validation，不做 hash，也不判斷圖片品質。

## Parent promote worker output 到 canonical

Extractor 完成後，parent 把整棵 worker output promote 進 canonical：

```text
worker_output/worker_01/figure_candidates.json -> canonical/figure_candidates.json
worker_output/worker_01/figure_index.json      -> canonical/figure_index.json
worker_output/worker_01/figure_decisions.json  -> canonical/figure_decisions.json
worker_output/worker_01/figures.json           -> canonical/figures.json
worker_output/worker_01/crops/                 -> canonical/crops/
worker_output/worker_01/source_regions/        -> canonical/source_regions/
worker_output/worker_01/boundaries/            -> canonical/boundaries/
worker_output/worker_01/previews/              -> canonical/previews/
```

這一步只搬檔，不改寫 JSON path。因為 JSON path 已經是 artifact-root-relative，搬到 `canonical/` 後仍能用同一組 path 被 reviewer / repair 解析。

Parent promote 完成後，下一步就是讓 reviewer 讀 canonical。不要讓 reviewer 讀 `worker_output/`。

## 建立 review packet

Parent 在啟動 reviewer 前，從 `canonical/figures.json` 建立：

```text
lanes/figures/reviews/round_00/reviewer_01/review_packet.json
```

第一階段只有一個 reviewer，所以 packet 包含 canonical 中全部 figures。`review_packet.json` 是視覺審查清單，不是 canonical truth。它列出每個 figure / crop unit 的：

- `figure_id`
- `figure_label`
- `crop_id`
- `role`
- `page`
- `crop_px`
- `source_page`
- `crop_preview`
- `boundary_preview`
- `edge_previews`

`crop_preview`、`boundary_preview` 和 `edge_previews` 使用 canonical artifact root 相對路徑。
`page`、`crop_px` 和 `source_page` 用來讓 reviewer 自己從 rendered page 建立本輪 source evidence。Parent 不建立 source previews，不決定 reviewer 要看多大的 source context，也不做 visual judgment。

第一階段 packet shape 由 parent 管，格式如下：

```json
{
  "schema_version": "figure_review_packet.v1",
  "review_round": "round_00",
  "reviewer_id": "reviewer_01",
  "canonical_artifact_root": "lanes/figures/canonical",
  "figures": [
    {
      "figure_id": "Figure_1",
      "figure_label": "Fig. 1",
      "crop_units": [
        {
          "crop_id": "Figure_1",
          "role": "complete figure",
          "page": 3,
          "crop_px": [120, 300, 2380, 1850],
          "source_page": "shared/pages/page_3.png",
          "crop_preview": "previews/Figure_1_preview.png",
          "boundary_preview": "previews/Figure_1_boundary_preview.png",
          "edge_previews": {
            "top": ["previews/Figure_1_top_seg1_preview.png"],
            "bottom": ["previews/Figure_1_bottom_seg1_preview.png"],
            "left": ["previews/Figure_1_left_seg1_preview.png"],
            "right": ["previews/Figure_1_right_seg1_preview.png"]
          }
        }
      ]
    }
  ]
}
```

Parent 寫 `review_packet.json` 時的機械規則：

- 來源只能是當前 `canonical/figures.json`，不要從 `worker_output/` 或舊 review round 建 packet。
- 第一階段 single reviewer 必須包含 canonical 中全部 figures 和全部 crop units。
- `figure_id`、`figure_label`、`crop_id`、`role`、`page`、`crop_px` 從 canonical manifest 原樣帶入。
- `source_page` 由 `page` 機械轉成 paper-dir-relative path，例如 `shared/pages/page_3.png`。Parent 只確認檔案存在，不建立 reviewer source preview。
- `crop_preview`、`boundary_preview` 和 `edge_previews` 從 canonical crop unit 的 preview 欄位原樣帶入；parent 不補建 preview、不改路徑、不發明替代 evidence。
- `review_packet.json` 只是一份審查清單，不是 canonical truth；promote 到 canonical 後也只作為本輪 reviewer 實際 assignment trace。

## 審查 figure

Parent 啟動一個 `figure_reviewer` subagent。Prompt 由兩部分依序拼接組成：

1. 讀取下列檔案的完整內容，原封不動作為 prompt 主體：

```text
agents/subagent_prompts/figure_reviewer.md
```

2. 在末尾附加 assignment 區塊：

```text
---
## Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
canonical_artifact_root: <paper_dir>/lanes/figures/canonical
output_root: <paper_dir>/lanes/figures/reviews/round_00/reviewer_01
review_packet: <paper_dir>/lanes/figures/reviews/round_00/reviewer_01/review_packet.json
scope: review_packet.json 中的全部 figures
```

Reviewer 讀 `review_packet.json` 指定的 `source_page` / `crop_px`，在本輪 `output_root/source_previews/` 自己建立 reviewer-local source evidence，再讀這些 source evidence 以及 canonical crop preview、boundary preview 與 edge previews，並寫出：

```text
lanes/figures/reviews/round_00/reviewer_01/visual_review.json
```

Reviewer 不修改 canonical artifacts，不補建 canonical preview，不計算 hash。Reviewer 可以為本輪 review 建立 reviewer-local source previews，並從 source evidence 建立簡短 source-vs-crop visual inventory；每個 crop unit 都要寫 top/bottom/left/right 的 `edge_checks`。Reviewer 必須在回報完成前執行 `scripts/validate_figure_review.py` 驗證 `visual_review.json`，不合 contract 就重寫。Review 的重點是視覺判斷：crop 是否完整、乾淨；不完整時寫 `findings[]`。

## Parent promote review 到 canonical

Reviewer 完成後，parent 把本輪 review output promote 進 canonical：

```text
reviews/round_00/reviewer_01/review_packet.json  -> canonical/reviews/round_00/reviewer_01/review_packet.json
reviews/round_00/reviewer_01/visual_review.json  -> canonical/reviews/round_00/reviewer_01/visual_review.json
reviews/round_00/reviewer_01/source_previews/     -> canonical/reviews/round_00/reviewer_01/source_previews/
```

Parent promote review 到 canonical 後，下一步才是 gate / repair dispatch。Repair 只讀 canonical 裡 promoted review 與 repair request，不讀 reviewer output working directory。

## Gate

Parent 只根據 canonical 裡的 promoted review 做 gate：

```text
canonical/reviews/round_N/reviewer_01/visual_review.json
```

關閉條件：

```text
visual_review.json.status == "pass"
且每個 figure decision 都是 "pass"
且每個 crop unit 的 top/bottom/left/right edge_checks status 都是 "pass"
```

進入 repair 的條件：

```text
visual_review.json.status == "fail"
且至少一個 failed figure 有 severity == "required" 的 finding
```

阻塞條件：

```text
required next-step files are absent
repair round limit reached
review fails but no required finding can be converted into repair request
finding requires human_check
inventory / duplicate-id 類問題
```

Parent 不得自己做 visual judgment 來 override reviewer。

## 建立 repair request

如果 reviewer 發現 required findings，parent 從 canonical review 機械式建立：

```text
lanes/figures/canonical/repair_requests/round_01/repair_requests_merged.json
```

因為只有一個 repair worker，所以 assignment 很簡單。以下以第一輪 repair 為例：

```json
{
  "schema_version": "figure_repair.v3",
  "repair_round": "round_01",
  "source_reviews": [
    "reviews/round_00/reviewer_01/visual_review.json"
  ],
  "assignments": [
    {
      "repair_id": "repair_01",
      "figure_ids": ["Figure_1"],
      "request_ids": ["Figure_1_f001"]
    }
  ],
  "requests": [
    {
      "request_id": "Figure_1_f001",
      "assigned_repair_id": "repair_01",
      "figure_id": "Figure_1",
      "figure_label": "Fig. 1",
      "crop_ids": ["Figure_1"],
      "source_review": "reviews/round_00/reviewer_01/visual_review.json",
      "source_finding_id": "Figure_1_f001",
      "action": "recrop",
      "direction": ["expand_bottom"],
      "constraint": "Panels e-g are cut off below the bottom cyan boundary. Expand the crop to include the full panels and their axis labels, stopping before the external caption.",
      "defects": ["content_cut: bottom"]
    }
  ]
}
```

Parent 不在 repair request 裡發明座標。Repair request 只描述 defect、action、direction 和 constraint；新的 `crop_px` 由 repair worker 讀 source page evidence 後決定。

Parent 建立 repair request 時只做機械欄位轉換，不做 visual judgment：

- Top-level 必須包含 `schema_version`、`repair_round`、`source_reviews`、`assignments`、`requests`。
- `schema_version` 使用 `"figure_repair.v3"`。
- `repair_round` 是下一個 repair round，例如 `reviews/round_00/` 產生 `repairs/round_01/` 的 request。
- `source_reviews[]` 使用 canonical artifact root 相對路徑，例如 `reviews/round_00/reviewer_01/visual_review.json`。
- 第一階段只有 `repair_01`；`assignments[0].request_ids[]` 必須和 `requests[].request_id` 完全一致。
- 每個 request 必須包含 `request_id`、`assigned_repair_id`、`figure_id`、`figure_label`、`crop_ids`、`source_review`、`source_finding_id`、`action`、`direction`、`constraint`、`defects`。
- `request_id` 在整份 request file 中必須唯一，建議直接沿用 reviewer finding 的 `finding_id`。
- `source_finding_id` 來自 reviewer finding 的 `finding_id`。
- `crop_ids[]` 來自 reviewer finding 的 `crop_id`；若 `crop_id` 是 `null`，parent 只能在該 figure 只有單一 crop unit 時自動對應，否則 block。
- `defects[]` 由 `problem` 和 `edge` 組成，例如 `content_cut: bottom`。
- `constraint` 直接使用 reviewer finding 的 `notes`，不得加上 parent 自己猜的視覺描述。
- `direction[]` 由 `repair_hint` 轉換，例如 `expand_bottom`、`shrink_top`、`recrop`。
- `action` 由 `repair_hint` 機械決定：`expand_*`、`shrink_*`、`recrop`、`split_crop`、`merge_crop` 對應 `recrop`；`regenerate_preview` 對應 `regenerate_missing_preview`；`manifest_check` 對應 `manifest_correction`；`human_check` 直接 block。
- `missing_evidence` 若指向 canonical crop / boundary / edge preview，可以轉成 `regenerate_missing_preview`；若指向 reviewer 無法建立 source evidence 所需的 `source_page` / `crop_px`，parent 應修正 packet 或前置 page artifacts 後重跑 reviewer，不能派給 repair worker 猜測修圖。
- 只轉換 `severity == "required"` 的 findings；`advisory` 不進第一階段 repair request。
- Request 不得包含 `current_crop_px`、`proposed_crop_px`、bbox array 或任何座標鍵。

執行 repair 前，parent 先保存 canonical snapshot：

```text
canonical/ -> repairs/round_01/before_snapshot/
```

這是檔案 snapshot，不需要 hash manifest。

## 修復 figure

Parent 啟動一個 `figure_repair` subagent。Prompt 由兩部分依序拼接組成：

1. 讀取下列檔案的完整內容，原封不動作為 prompt 主體：

```text
agents/subagent_prompts/figure_repair.md
```

2. 在末尾附加 assignment 區塊：

```text
---
## Assignment
paper_dir: <paper_dir>
repair_round: round_01
repair_id: repair_01
canonical_artifact_root: <paper_dir>/lanes/figures/canonical
repair_artifact_root: <paper_dir>/lanes/figures/repairs/round_01/repair_01
request_file: <paper_dir>/lanes/figures/canonical/repair_requests/round_01/repair_requests_merged.json
source_review: <paper_dir>/lanes/figures/canonical/reviews/round_00/reviewer_01/visual_review.json
```

Repair worker 讀 canonical，寫出：

```text
lanes/figures/repairs/round_01/repair_01/repair_report.json
lanes/figures/repairs/round_01/repair_01/crops/
lanes/figures/repairs/round_01/repair_01/boundaries/
lanes/figures/repairs/round_01/repair_01/previews/
lanes/figures/repairs/round_01/repair_01/manifest_updates/   # 只有 manifest 欄位改變時才需要
```

Repair worker 不直接寫 `canonical/`。`repair_report.json` 必須清楚列出 parent 要搬哪些檔案、搬到 canonical 的哪個 target，以及是否需要套用 `manifest_patches[]`。`repair_output` 使用 repair artifact root 相對路徑；`canonical_target` 使用 canonical artifact root 相對路徑。

Repair worker 在 final response 前必須執行 individual validator：

```bash
python3 agents/scripts/validate_figure_repair.py \
  "<paper_dir>/lanes/figures/repairs/round_01/repair_01/repair_report.json"
```

這個 validator 只檢查 repair-local contract：`repair_report.json` 能 parse、repair-local paths 能 resolve、merge 指令完整、crop-unit manifest patches 同步覆蓋 `figures.json` / `figure_decisions.json`、summary count 正確。不做 hash，也不判斷修復後圖片是否最終接受；接受判定仍來自下一輪 reviewer。

## Parent merge repair output 到 canonical

Parent 只套用 `repair_report.json` 裡明確列出的 merge 指令。

Parent 讀 `repair_report.json` 時的必要 contract：

- Top-level 必須包含 `schema_version`、`repair_round`、`repair_id`、`status`、`source_request_file`、`repairs`、`merge`、`validation`、`summary`。
- `repair_round`、`repair_id`、`source_request_file` 必須和 parent assignment 一致。
- `status` 只能是 `complete` 或 `incomplete`；若是 `incomplete`，parent 不得靜默 close，必須 block 或重新分派。
- `merge.needs_parent_merge` 為 `true` 時，parent 只讀 `merge.file_copies[]` 和 `merge.manifest_patches[]` 來更新 canonical。
- `repairs[]`、`updated_crop_units[]`、`notes`、`summary` 是 trace 和 sanity check，不能取代 `merge.file_copies[]` / `merge.manifest_patches[]`。

允許的 parent 動作：
- 執行 `merge.file_copies[]`：將 repair-local crop、crop preview、boundary preview 或 edge preview 複製到指定的 canonical target。
- 執行 `merge.manifest_patches[]`：對同一個 `figure_id` / `crop_id` 套用允許清單內的 manifest patch，例如 `crop_px`、`image_file`、`preview`、`boundary_preview`、`edge_previews`、`verification`、`evidence_read` 和 repair notes。
- 只有當 `repair_report.json` 明確指定 canonical target manifest 時，才可以從 `manifest_updates/` 搬整份 replacement manifest。

`merge.file_copies[]` 的每個 entry 必須同時提供 source 和 target：

```json
{
  "kind": "crop_preview",
  "figure_id": "Figure_1",
  "crop_id": "Figure_1",
  "repair_output": "previews/Figure_1_preview.png",
  "canonical_target": "previews/Figure_1_preview.png"
}
```

`kind` 只使用 `crop`、`crop_preview`、`boundary_preview` 或 `edge_preview`。`edge_preview` entry 必須包含 `edge`（值為 `top`、`bottom`、`left` 或 `right`）和 `segment`（值為 `seg1`、`seg2` 等）。

`merge.manifest_patches[]` 的每個 entry 必須可以讓 parent 不做推理就套用：

```json
{
  "target_file": "figures.json",
  "operation": "replace",
  "scope": "crop_unit",
  "selector": {"figure_id": "Figure_1", "crop_id": "Figure_1"},
  "path": "crop_units[].crop_px",
  "old_value": [120, 300, 2380, 1390],
  "new_value": [120, 300, 2380, 1850]
}
```

Parent 只允許 `operation` 為 `replace` 或 `add_if_missing`。Parent 只允許 `target_file` 為 `figures.json`、`figure_decisions.json`，或在 request 明確要求 `manifest_correction` 時使用 `figure_index.json`。Parent 套用 `replace` 前必須先確認 `old_value` 和 canonical 目前值一致；套用 `add_if_missing` 前必須先確認目標欄位不存在；不一致就 block，不猜測、不強行覆蓋。若同一個 crop unit 在 `figures.json` 和 `figure_decisions.json` 都有相同欄位，repair report 必須提供兩份 patch，讓兩個 manifest 保持一致。若修復新增或修改 `edge_previews`，patch path 使用 `crop_units[].edge_previews.<edge>`。

不允許的 parent 動作：
- 代替 reviewer 或 repair worker 做 visual judgment。
- 自己發明新的 crop coordinate。
- 靜默覆蓋另一個 figure 或 crop id。
- 做 duplicate-id reconciliation。
- 做 multi-worker merge。
- 使用 hash freshness gate。

Parent 更新 canonical 後，先前 review 都失效。下一步一定是重新建立下一輪 `review_packet.json` 並啟動 `figure_reviewer`，不能直接 close。如果剛合併的是 `repairs/round_01/`，新的 review 寫到 `reviews/round_01/reviewer_01/` 並 promote 到 `canonical/reviews/round_01/reviewer_01/`。

# 格式

## 輸出格式

- Agent primary reports 和 decisions 只能是 JSON。
- Markdown reports 或 traces 必須由 JSON/JSONL 產生，不能成為 source of truth。
- Parent 可以做機械式 JSON cleanup 或允許清單內的 patch，但不能編造 verdicts、findings、coverage、source evidence、crop coordinate 或 scientific values。

# 規則

## 使用 subagent 的規則

- 這個 pipeline 中所有 worker、reviewer、repair 都要啟動獨立 subagents。
- 不得用 parent agent 的工作取代 worker、reviewer 或 repair subagent。
- 當工作需要 worker/reviewer/repair judgment 時，parent 不得自己執行 extraction、visual review、repair visual acceptance、text assembly、reassembly 或 final review。
- Subagent prompt 必須使用指定的 prompt 檔案全文，不得摘要、改寫、截斷或重新組織。Parent 唯一可以做的修改是在末尾附加 assignment 變數區塊。
- 如果 agent 啟動失敗，先修正 prompt、tool 或 context blockers，然後重試。若仍無法啟動 agents，停止並回報 `blocked`。

## Review 和 repair 規則

- Figure lane 預設最多 4 個 repair rounds，除非使用者明確改變 scope。
- 任何改動 crop、preview 或 manifest 的 repair 都會讓先前 review 失效，一定要重新完整 review。
- Parent 只在 promoted review 進 canonical 後建立 repair request。
- 第一階段不做 partial review reuse。每輪 review 都審查當前 canonical 的全部 figures。
- 第一階段不用 hash；round numbering + 不覆寫舊目錄 + stage barrier 就是 stale review 防線。

## 輔助工具

Figure lane 使用的輔助工具都放在本 skill 內：

```text
agents/scripts/render_pages.py
agents/scripts/make_image_preview.py
agents/scripts/crop_region.py
agents/scripts/make_edge_previews.py
agents/scripts/validate_figure_extraction.py
agents/scripts/validate_figure_review.py
agents/scripts/validate_figure_repair.py
```

輔助工具可以 render pages、建立 preview、裁切圖片、產生 edge previews 與 boundary preview、檢查檔案是否存在、驗證 extractor / reviewer / repair JSON contract；輔助工具不能判定 crop 是否視覺完整、caption 是否外漏、座標軸是否被切掉，或 figure 是否應該 pass。這些判斷必須由 extractor、reviewer 或 repair agent 讀過對應 previews 後完成。

`make_edge_previews.py` 負責從頁面圖片產生四邊 edge previews 和（可選的）boundary preview。它內部計算 margin 和 edge band 幾何，並在 edge strip 的 aspect ratio 超過 `--max-ratio` 時自動將該邊切分為多個 segment。`--max-ratio` 控制每段 segment（含 overlap）的最大長寬比——值越小，每段越接近正方形，boundary 附近的文字在 preview 裡越大；預設 1.3 保證即使很寬的 figure，每段 preview 短邊也有足夠解析度看清 boundary 附近的小字。每個 segment 輸出為 `_seg<N>_preview.png`（即使只有一個 segment 也使用 `_seg1`）。Boundary preview 使用 cyan 矩形標出 crop_px。加上 `--boundary` 會同時產生 boundary 圖片與 boundary preview。命令範例：

```bash
python3 agents/scripts/make_edge_previews.py \
  --page-image shared/pages/page_N.png \
  --crop-px <x1> <y1> <x2> <y2> \
  --crop-id <crop_id> \
  --output-dir <artifact_root>/boundaries \
  --preview-dir <artifact_root>/previews \
  --max-ratio 1.3 \
  --boundary
```

腳本將產生的檔案路徑以 JSON 輸出到 stdout。
