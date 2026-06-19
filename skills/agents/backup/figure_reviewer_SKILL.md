---
name: review-figure-extraction
description: Independently review extracted scientific figure crops by visually comparing source page/region previews against final crop previews, then write visual_review.json and final figures_validation.json.
argument-hint: <output_dir>
---
This document is composed of bilingual English-Chinese parallel text. The Chinese version is for the user's reading, so keep it natural, fluent, and easy to read while preserving full consistency between the two languages.

# Review Figure Extraction

You independently review a completed `extract-figure` run. Your job is not to create crops. Your job is to decide whether the extracted crops are visually complete and clean.

Rendered page images are the ground truth for review. Source page/region previews are only views derived from those rendered pages. Final crop previews show what was extracted. Python validators, JSON manifests, crop coordinates, image dimensions, OCR/text boxes, and pixel heuristics are evidence only. They cannot certify visual quality.

Extractor-provided previews are not sufficient source ground truth for a passing review. For every figure, create or read reviewer source views derived from the rendered page image. The reviewer must not be constrained by the extractor's framing of the problem.

Do not read full-resolution rendered pages, full-resolution crop PNGs, or raw high-resolution edge strips directly. Any image read by the reviewer must be bounded to at most 1600 px on both dimensions. For multi-image reads, use previews no larger than 1400 px on both dimensions and keep batches small. If the available evidence image is larger, create a reviewer preview first and record that path.

## File Contract

Read:

- `<output_dir>/figures/figure_candidates.json`
- `<output_dir>/figures/figure_index.json`
- `<output_dir>/figures/figure_decisions.json`
- `<output_dir>/figures/figures.json`
- `<output_dir>/figures/figures_mechanical_validation.json`, if present
- rendered page images or source page/region previews referenced by the manifests
- final crop previews referenced by `figures.json`
- shared preview helpers:
  - `${CLAUDE_SKILL_DIR}/../_shared/scripts/crop_region.py`
  - `${CLAUDE_SKILL_DIR}/../_shared/scripts/make_image_preview.py`

Write:

- `<output_dir>/figures/visual_review.json`
- `<output_dir>/figures/figures_validation.json`
- reviewer-created evidence previews under `<output_dir>/figures/previews/reviewer_round_<N>/` when needed

The orchestrator should pass the current review round number. If it does not, infer `N` as the next unused `reviewer_round_<N>` directory and record the generated preview paths in `source_previews_read`.

Do not modify the source PDF. Do not modify crop PNGs or extraction manifests. Creating reviewer evidence previews is allowed. If a crop is bad, fail it and explain the defect; let a later extraction pass repair the crop.

## Review Standard

For every figure, visually compare the source evidence against the final crop evidence.

The source evidence must come from the rendered page and must show the original figure context: full visual figure, nearby caption boundary, nearby body text, and page chrome. The crop evidence must show the final extracted crop.

A figure passes only if:

- all panels visible in the source are present in the crop
- all salient visual units visible in the source are present in the crop, even when the figure has no panel letters
- panel letters, axes, tick labels, legends, scale bars, insets, color bars, row/column labels, and plot boundaries are complete
- the crop excludes external captions and legends outside the visual figure
- the crop excludes surrounding body text
- the crop excludes headers, footers, page numbers, watermarks, journal labels, and other page chrome
- no adjacent figure, table, equation, or unrelated page content is included
- the crop is not a lazy page strip that merely contains the figure

If a crop is partially cut off, includes an external caption, includes page chrome, or has any unresolved visual condition, it fails. Do not accept a crop because it is "mostly okay."

Uncertainty is a failure. Do not mark a figure as pass if the notes would need words such as "maybe", "possibly", "seems", "unclear", "slightly clipped", "minor clip", or "best effort". A pass means you can visually account for the crop.

## Rendered-Page Source Evidence

Before judging the final crop, inspect the rendered page through bounded reviewer-created views. Do not review only the extractor's crop preview or only extractor-created page previews.

For every figure, create/read source evidence from `<output_dir>/pages/page_N.png`:

- a bounded page overview showing the figure in page context
- a bounded source region around the visual figure, including nearby caption boundary and page chrome
- bounded source boundary views around the proposed crop's top, bottom, left, and right edges

Use the crop box from `figure_decisions.json` to create source boundary views that show both sides of each crop edge, for example a bottom source boundary view should include content just inside and just outside the proposed bottom edge. If the boundary view does not show whether source content continues beyond the crop, make a larger or higher-resolution bounded view before deciding.

Do not read full-resolution rendered pages directly. "Look at the rendered page" means use the rendered page image as the source and inspect safe bounded views/tiles generated from it.

## Visual Inventory

Before judging the crop, build a generic visual inventory from the rendered-page source evidence. This is required for every figure and is especially important when `expected_panels` is empty.

`expected_visual_units` should list visible figure components at the right granularity for the figure type. Examples: for a chart, list plot area, axes/tick labels, axis titles, legends, color bars, and annotations; for a diagram or chemical scheme, list object groups, arrows, callouts, molecule groups, condition labels, and terminal objects; for microscopy or matrix-like figures, list tiles/cells, channel or row/column labels, scale bars, and figure-internal legends.

Then record `observed_visual_units` from the final crop. A passing review requires the observed unit IDs to match the expected unit IDs. If the source figure is simple, use one explicit unit such as `{"id": "main_plot", "type": "plot", "location": "center", "description": "single line chart with axes and legend"}` rather than leaving the list empty.

Do not use the caption text alone as the inventory. Do not build the inventory from the crop. The inventory must come from visual inspection of rendered-page source views.

## Required Visual Reads

For every figure, read at least:

- one reviewer-created source page overview or source region preview generated from the rendered page, showing the figure in its page context
- one final crop preview generated from the actual output crop

For every figure, also read targeted boundary previews for the top, bottom, left, and right edges. For chart-like figures, including line plots, bar charts, scatter plots, heatmaps, Manhattan plots, and axes-based diagrams, explicitly verify that axis titles, tick labels, legends, color bars, and plot boundaries are complete. If the crop cuts off figure content at an edge, fail it. If forbidden neighboring content appears at an edge, fail it.

For every crop edge, compare the final crop edge against a source boundary preview covering the same source-page area. Record the source edge previews separately from the crop edge previews. The reviewer must decide whether each edge is clean:

- `clean_margin`: crop edge is outside the visual figure with whitespace margin
- `figure_border_complete`: crop edge coincides with a complete figure-internal border, frame, or panel boundary
- `intentional_full_bleed_edge`: source figure intentionally reaches the page/crop edge and no content is cut

Any other condition fails, including `content_cut`, `content_touches_edge_uncertain`, `caption_visible`, `body_text_visible`, `page_chrome_visible`, `adjacent_content_visible`, and `unknown`.

Do not write `visual_review.json` from manifests alone. If a referenced preview is missing, fail the figure because the visual evidence is incomplete.

Make bounded reviewer source previews from the rendered page even when extractor previews exist. Make targeted crop-edge previews whenever they are not already present. If an edge strip is too large to read safely, make a smaller preview of the strip before reading it. Record rendered-page source views in `source_previews_read`, rendered-page source boundary views in `source_edge_previews_read`, and final-crop/edge previews in `crop_previews_read`.

Compute SHA-256 hashes for every crop PNG reviewed and write them in `crop_hashes`. The final validator rejects stale reviews when the current crop hash differs from the reviewed hash.

Copy `expected_panels` from `figure_decisions.json` into each review entry, then record `observed_panels` from visual inspection of the source and crop. A passing review requires the lists to match exactly. If the extractor's expected panel list is wrong, fail the review and request a manifest correction or recrop rather than silently passing.

## Output Schema

Before writing `visual_review.json`, read `../_shared/references/figure_schemas.md` for the exact schema.

Write `visual_review.json` with top-level fields `status`, `figures`, and `summary`. For a complete JSON example, see `../_shared/references/figure_schemas.md`.

Each figure entry includes `figure_id`, `expected_panels`, `observed_panels`, `expected_visual_units`, `observed_visual_units`, `source_previews_read`, `source_edge_previews_read`, `crop_previews_read`, `crop_hashes`, `checks`, `edge_checks`, `defects`, `decision`, `repair_request`, and `notes`.

Use only `pass` or `fail` in `checks` and `decision`. Do not use `not_applicable`. If a figure has no axes or legends, `labels_axes_legends_complete` is `pass` when nothing relevant is missing.

For passing figures, `notes` must be non-empty and must state the visual evidence that matters: panels observed, edge cleanliness, and why any embedded text/rule is figure-internal rather than page chrome. Empty notes are not acceptable for a pass.

For passing figures, `expected_visual_units` and `observed_visual_units` must be non-empty lists with matching unit IDs. `source_edge_previews_read` and `crop_previews_read` must include top, bottom, left, and right edge evidence. `edge_checks` must include top, bottom, left, and right entries with a passing status and non-empty evidence.

A passing figure must not contain uncertainty language or admitted defects in `notes`. If you are not sure, fail the figure and request a targeted repair or clearer source preview.

`summary.figure_count`, `summary.pass_count`, and `summary.fail_count` must match the actual `figures` list.

For a failed figure:

- set the failed check values to `fail`
- add concrete defects, for example `"bottom x-axis label is cut off"` or `"external caption text visible in lower-right quadrant"`
- add a repair request at the level of abstraction the extractor can use, for example `{"action": "recrop", "direction": ["expand_bottom"], "constraint": "include the missing bottom axis/title area; stop before the external caption"}`
- set `decision` to `fail`
- set top-level `status` to `fail`

Do not propose exact coordinates unless the user explicitly asks. Use directions and constraints; the extractor decides pixels from the source page. Do not put `current_crop_px`, `proposed_crop_px`, bbox arrays, or coordinate-like repair keys inside `repair_request`.

## Final Validation

After writing `visual_review.json`, run the final validator:

```bash
python3 ${CLAUDE_SKILL_DIR}/../_shared/scripts/validate_figures.py \
  "<output_dir>" --write "<output_dir>/figures/figures_validation.json"
```

The final run passes only when both conditions are true:

- the mechanical validator accepts the extraction manifests and evidence paths
- `visual_review.json` exists and every reviewed figure passes

If final validation fails, preserve the failure. Do not edit manifests to make the validator pass unless you have visually verified the underlying crop quality.

## Trace Expectations

Report source and crop previews read, visual defects by figure ID, `visual_review.json` write status, and final validator command/result so the orchestrator can record the event log.

---

# 中文對照

這份文件由中英雙語對照組成。中文對照是給我看的，請務必保持兩語言內容完全一致，並讓中文流暢通順、易於閱讀。

# 審查圖擷取

## 中繼資料

- name: `review-figure-extraction`
- description: 透過視覺比對來源頁面/區域預覽圖與最終裁切預覽圖，獨立審查已擷取的科學圖裁切，並寫出 `visual_review.json` 和最終 `figures_validation.json`。
- argument-hint: `<output_dir>`

## 任務

你要獨立審查一次已完成的 `extract-figure` 執行。你的工作不是建立裁切圖，而是判斷擷取出的裁切圖是否視覺完整且乾淨。

審查時，已轉成圖片的頁面才是最終依據。來源頁面/區域預覽圖只是從頁面圖片產生的視圖；最終裁切預覽圖則顯示實際擷取結果。Python 驗證器、JSON 清單檔、裁切座標、圖片尺寸、OCR/文字框和像素啟發式判斷都只能作為證據，不能證明視覺品質合格。

擷取者提供的預覽圖不足以作為審查通過的來源依據。每一張圖都必須建立或讀取由頁面圖片產生的審查者來源視圖。審查者不能被擷取者原本的框定方式限制。

不要直接讀完整解析度的頁面圖片、完整解析度的裁切 PNG，或原始高解析度邊緣條帶。審查者讀取的任何圖片都必須受限在兩邊不超過 1600 px。多圖讀取時，每張圖片兩邊不超過 1400 px，且批次要小。如果可用證據圖片過大，先建立審查者預覽圖，並記錄該路徑。

## 檔案契約

讀取：

- `<output_dir>/figures/figure_candidates.json`
- `<output_dir>/figures/figure_index.json`
- `<output_dir>/figures/figure_decisions.json`
- `<output_dir>/figures/figures.json`
- `<output_dir>/figures/figures_mechanical_validation.json`，如果存在。
- 清單檔引用的頁面圖片或來源頁面/區域預覽圖。
- `figures.json` 引用的最終裁切預覽圖。
- shared preview helpers：
  - `${CLAUDE_SKILL_DIR}/../_shared/scripts/crop_region.py`
  - `${CLAUDE_SKILL_DIR}/../_shared/scripts/make_image_preview.py`

寫出：

- `<output_dir>/figures/visual_review.json`
- `<output_dir>/figures/figures_validation.json`
- 必要時，在 `<output_dir>/figures/previews/reviewer_round_<N>/` 下寫審查者建立的證據預覽圖。

協調器應傳入目前審查輪次。如果沒有傳入，就推斷下一個未使用的 `reviewer_round_<N>` 目錄，並在 `source_previews_read` 中記錄產生的預覽圖路徑。

不要修改來源 PDF。不要修改裁切 PNG 或擷取清單檔。可以建立審查者證據預覽圖。如果裁切有問題，將該圖判定為未通過並說明缺陷，交由後續擷取階段修復。

## 審查標準

每張圖都要把來源證據和最終裁切證據做視覺比較。

來源證據必須來自頁面圖片，並顯示原始圖的上下文：完整視覺圖、附近圖說邊界、附近正文和頁面固定元素。裁切證據必須顯示最終擷取出的裁切。

圖只有在下列全部成立時才通過：

- 來源中可見的所有分圖都出現在裁切中。
- 來源中所有重要視覺單元都出現在裁切中，即使該圖沒有分圖字母。
- 分圖字母、座標軸、刻度標籤、圖例、比例尺、插圖、色條、列/欄標籤和圖表邊界都完整。
- 裁切排除外部圖說和圖外圖例。
- 裁切排除周圍正文。
- 裁切排除頁首、頁尾、頁碼、水印、期刊標籤和其他頁面固定元素。
- 裁切不包含相鄰圖、表格、方程式或無關頁面內容。
- 裁切不是只把圖包含在內的大頁面條帶。

只要裁切切掉任何圖內容、包含外部圖說、包含頁面固定元素，或仍有未解決的視覺問題，就應判定為未通過。不要因為「大致可以」就接受裁切。

只要仍不確定，就不能判定為通過。如果註記中需要使用「也許」、「可能」、「看起來」、「不清楚」、「略微切到」、「小裁切」或「盡力」這類語氣，就不要標通過。判定通過代表你能用視覺證據說明裁切為什麼完整且乾淨。

## 頁面圖片來源證據

判斷最終裁切之前，先透過受限尺寸的審查者自建視圖檢查頁面圖片。不要只審查擷取者的裁切預覽圖，也不要只審查擷取者建立的頁面預覽圖。

對每張圖，從 `<output_dir>/pages/page_N.png` 建立或讀取：

- 顯示圖在頁面中位置的受限尺寸頁面概覽。
- 圍繞視覺圖的受限尺寸來源區域，包含附近圖說邊界和頁面固定元素。
- 擬定裁切上、下、左、右邊緣附近的受限尺寸來源邊界視圖。

使用 `figure_decisions.json` 中的裁切框建立來源邊界視圖，讓視圖同時顯示裁切邊緣內外兩側。例如底邊來源邊界視圖應包含擬定底邊內側和外側的內容。如果邊界視圖無法看出來源內容是否延伸到裁切外，先建立更大或較高解析度但仍受限尺寸的視圖，再做決定。

不要直接讀完整解析度頁面圖片。「查看頁面圖片」的意思是：以頁面圖片為來源，產生安全的受限尺寸視圖或切片後再檢查。

## 視覺清單

判斷裁切前，必須從頁面圖片來源證據建立一般視覺清單。每張圖都要做，尤其是 `expected_panels` 為空時。

`expected_visual_units` 應以適合圖類型的粒度列出可見圖元。例如：

- 圖表：列出繪圖區、座標軸/刻度標籤、軸標題、圖例、色條和標註。
- 示意圖或化學流程圖：列出物件群、箭頭、註解、分子群、條件標籤和末端物件。
- 顯微圖或矩陣型圖：列出格子/影像塊、通道或列/欄標籤、比例尺和圖內圖例。

接著從最終裁切記錄 `observed_visual_units`。通過審查要求觀察到的單元 ID 與預期單元 ID 一致。如果來源圖很簡單，也要使用一個明確單元，例如 `main_plot`，不要留空。

不要只根據圖說文字建立清單。不要從裁切圖建立清單。清單必須來自對頁面圖片來源視圖的視覺檢查。

## 必要視覺讀取

每張圖至少要讀：

- 一個由頁面圖片產生的審查者來源頁面概覽或來源區域預覽圖，顯示圖在頁面中的上下文。
- 一個由實際輸出裁切圖產生的最終裁切預覽圖。

每張圖也要讀上、下、左、右邊緣的目標邊界預覽圖。對圖表型圖片，包括折線圖、長條圖、散點圖、熱圖、Manhattan 圖和帶座標軸的示意圖，必須明確確認座標軸標題、刻度標籤、圖例、色條和圖表邊界完整。如果裁切邊緣切掉圖內容，或邊緣出現禁止的鄰近內容，就判定為未通過。

每個裁切邊緣都要把最終裁切邊緣和相同來源頁面位置的來源邊界預覽圖相比較。來源邊緣預覽圖要和裁切邊緣預覽圖分開記錄。審查者必須判斷每條邊是否乾淨：

- `clean_margin`：裁切邊在視覺圖外，有空白邊距。
- `figure_border_complete`：裁切邊與完整的圖內框線、邊框或分圖邊界一致。
- `intentional_full_bleed_edge`：來源圖有意延伸到頁面或裁切邊緣，且沒有內容被切掉。

其他任何狀態都應判定為未通過，包括 `content_cut`、`content_touches_edge_uncertain`、`caption_visible`、`body_text_visible`、`page_chrome_visible`、`adjacent_content_visible` 和 `unknown`。

不要只根據清單檔寫 `visual_review.json`。如果引用的預覽圖缺失，代表視覺證據不完整，應將該圖判定為未通過。

即使擷取者已提供預覽圖，也要從頁面圖片建立受限尺寸的審查者來源預覽圖。若缺少目標裁切邊緣預覽圖，也要建立。記錄頁面圖片來源視圖到 `source_previews_read`，記錄頁面圖片來源邊界視圖到 `source_edge_previews_read`，記錄最終裁切和邊緣預覽圖到 `crop_previews_read`。

為每個被審查的裁切 PNG 計算 SHA-256 雜湊，寫入 `crop_hashes`。如果目前裁切圖雜湊和審查時不同，最終驗證器會拒絕過期審查。

將 `figure_decisions.json` 中的 `expected_panels` 複製到每個審查項目，然後根據視覺檢查記錄 `observed_panels`。只有兩個列表完全一致，該圖才可通過審查。如果擷取者的預期分圖列表錯誤，應將審查判定為未通過，並要求修正清單或重新裁切，不要默默放行。

## 輸出結構

寫 `visual_review.json` 前，先讀 `../_shared/references/figure_schemas.md` 取得精確結構。

`visual_review.json` 的最上層欄位是 `status`、`figures` 和 `summary`。完整 JSON 範例見 `../_shared/references/figure_schemas.md`。

每個圖項目包含 `figure_id`、`expected_panels`、`observed_panels`、`expected_visual_units`、`observed_visual_units`、`source_previews_read`、`source_edge_previews_read`、`crop_previews_read`、`crop_hashes`、`checks`、`edge_checks`、`defects`、`decision`、`repair_request` 和 `notes`。

`checks` 和 `decision` 只使用 `pass` 或 `fail`。不要使用 `not_applicable`。如果圖沒有座標軸或圖例，只要沒有相關內容缺失，`labels_axes_legends_complete` 就可以是 `pass`。

審查通過的圖，其 `notes` 不得為空，必須說明重要視覺證據：觀察到的分圖、邊緣乾淨狀態，以及任何嵌入文字或線條為什麼屬於圖內內容，而不是頁面固定元素。

審查通過的圖，其 `expected_visual_units` 和 `observed_visual_units` 必須是非空列表，且單元 ID 必須一致。`source_edge_previews_read` 和 `crop_previews_read` 必須包含上、下、左、右邊緣證據。`edge_checks` 必須包含上、下、左、右項目，而且狀態必須通過、證據不得為空。

審查通過的圖，其 `notes` 不得包含不確定語氣，也不得提到任何已知缺陷。若仍有不確定之處，應將該圖判定為未通過，並提出具體修復要求，或要求提供更清楚的來源預覽圖。

對未通過的圖：

- 將未通過的檢查設為 `fail`。
- 加入具體缺陷，例如「底部 x 軸標籤被切掉」或「右下角可見外部圖說文字」。
- 加入抽象層級適合擷取者使用的修復請求，例如要求 `recrop`、方向為 `expand_bottom`，並附上包含/停止條件。
- 將 `decision` 設為 `fail`。
- 將最上層 `status` 設為 `fail`。

不要提出精確座標，除非使用者明確要求。使用方向和約束；像素由擷取者根據來源頁面決定。不要在 `repair_request` 中放 `current_crop_px`、`proposed_crop_px`、bbox 陣列或類似座標的鍵。

## 最終驗證

寫 `visual_review.json` 後，執行最終驗證器：

```bash
python3 ${CLAUDE_SKILL_DIR}/../_shared/scripts/validate_figures.py \
  "<output_dir>" --write "<output_dir>/figures/figures_validation.json"
```

最終執行只有在下列兩件事都成立時才通過：

- 機械式驗證器接受擷取清單檔和證據路徑。
- `visual_review.json` 存在，且每個被審查的圖都通過。

如果最終驗證未通過，就保留該結果。不要在沒有視覺確認裁切品質的情況下，為了通過驗證器而編輯清單檔。

## 追蹤紀錄要求

回報讀取的來源和裁切預覽圖、依圖 ID 列出的視覺缺陷、`visual_review.json` 寫入狀態，以及最終驗證器指令/結果，讓協調器可以記錄事件日誌。
