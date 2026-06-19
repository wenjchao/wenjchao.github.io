---
name: extract-figure
description: Extract labeled figures from a scientific PDF as verified crop images by segmenting page visuals into candidate regions, then model-verifying figure membership and crop boundaries.
argument-hint: <pdf_path> <output_dir>
---
This document is composed of bilingual English-Chinese parallel text. The Chinese version is for the user's reading, so keep it natural, fluent, and easy to read while preserving full consistency between the two languages.

# Extract Figure

You extract every labeled figure from a scientific PDF as clean PNG crops.

This skill owns the whole figure-extraction task: candidate detection, figure/caption association, crop decisions, cropping, verification, and final manifests. Do not create a separate figure-segmentation stage.

The source PDF and rendered page images are the ground truth. Helper code may render pages, make previews, propose visual/text regions, crop rectangles, and validate schemas. Helper output is candidate evidence only. The model must decide which candidates are real figures, what belongs to each figure, and whether each crop is acceptable.

This skill is the extraction stage. It must produce crops, manifests, previews, and a mechanical preflight validation. It does not provide the final independent acceptance decision. A complete figure-extraction run must then use `review-figure-extraction`, which writes `visual_review.json` and the final `figures_validation.json`.

## Modes

Use `initial_extraction` when starting from the PDF and rendered pages.

Use `initial_extraction_batch` when the orchestrator assigns a page range or figure subset for a large paper. The batch run directory must use the normal run layout with local `pages/` and `figures/` directories. Produce complete batch-local artifacts only for assigned pages/figures. Do not write root paper-level artifacts outside the batch run directory.

Use `continue_incomplete_extraction` when an earlier extractor produced only partial artifacts, such as candidates/index without final crops or final manifests. Continue from the existing artifacts, but still complete the full extractor contract: decisions, crop PNGs, bounded previews, edge previews, `figures.json`, and mechanical validation. Do not let the parent orchestrator fill in crop decisions for you.

Use `repair_from_visual_review` when the orchestrator provides `repair_requests.json`. In repair mode, read only the failed figure requests plus the relevant manifests, source pages, and previews. Repair the requested figures unless the requested change affects a neighboring figure's crop. Do not parse the full visual review as the primary repair input; the orchestrator narrows it into `repair_requests.json`.

For each repaired figure, preserve the same `figure_id`, update `figure_decisions.json`, regenerate the crop and crop preview, reread the source context and final crop preview, update `figures.json`, and rerun mechanical validation. Do not leave stale crop coordinates in any manifest after recropping.

If a requested figure cannot be cleanly isolated as a single rectangle, report that in the extractor result and leave the latest manifest honest. The orchestrator, not this skill, decides terminal `uncropable` status after the repair limit.

## Visual Inspection Contract

Code cannot certify figure quality. Python helpers can render pages, crop rectangles, create previews, check file existence, and flag geometric risks. They cannot determine whether the crop is intact, whether a caption is leaking into the image, whether axes or legends are cut off, or whether a page strip merely contains the figure somewhere inside it.

For every accepted figure, the agent must visually inspect both:

- the original source evidence: the rendered page image or bounded page/region previews containing the full figure, caption boundary, nearby body text, and page chrome
- the final crop evidence: the cropped PNG or a bounded preview made from the final cropped PNG

Do not mark a figure as passing from JSON, dimensions, crop coordinates, OCR/text boxes, file existence, or Python pixel analysis alone. If the agent did not visually read the source page evidence and the final crop evidence, the figure is incomplete.

For each figure, compare the final crop against the source page evidence and explicitly check all crop edges. A passing crop must show the whole visual figure and no forbidden neighboring content. If any panel, axis label, legend, scale bar, inset, panel letter, row/column label, color bar, or plot boundary is cut off, the crop fails. If any external caption, body text, article header, footer, journal label, watermark, or page number remains visible in the crop, the crop fails unless it is truly embedded figure content rather than page layout text.

For chart-like figures, including line plots, bar charts, scatter plots, heatmaps, Manhattan plots, and axes-based diagrams, bottom and side edges are high risk. Always inspect source context and final-crop edge previews that show axis titles, tick labels, legends, color bars, and plot boundaries before marking these figures pass. If unsure whether a figure is chart-like, do the chart edge check.

Use only `pass` or `fail` for verification checks. A final `result: "pass"` is allowed only when all verification subchecks are `pass`; any uncertainty or unresolved visual defect is `fail`.

Common failure modes are page-strip crops, caption/chrome leakage, truncated figure content, trusting helper boxes as truth, and marking crops pass without reading source and final crop previews.

## File Contract

Read:

- `<pdf_path>`
- rendered page images in `<output_dir>/pages/`, creating them if needed
- `<output_dir>/figures/repair_requests.json` when running in `repair_from_visual_review` mode

Write:

- `<output_dir>/figures/figure_candidates.json`
- `<output_dir>/figures/figure_index.json`
- `<output_dir>/figures/figure_decisions.json`
- `<output_dir>/figures/<figure_id>.png` for each single-page figure
- `<output_dir>/figures/<figure_id>_page_<N>.png` for each page of a multi-page figure, unless you create one verified stitched image
- `<output_dir>/figures/previews/*.jpg` or `.png` for bounded page, region, and crop previews
- `<output_dir>/figures/figures.json`
- `<output_dir>/figures/figures_mechanical_validation.json`
- optional extractor repair notes in the agent response when a requested crop cannot be made cleanly

The downstream `review-figure-extraction` skill writes:

- `<output_dir>/figures/visual_review.json`
- `<output_dir>/figures/figures_validation.json`

Do not modify the source PDF.

If the paper has no labeled figures, write all JSON artifacts with empty figure lists and a passing validation result.

## Boundary

Include visual content belonging to labeled figures such as `Fig. 1` or `Figure 2`, including panels, panel labels, axes, scale bars, legends inside the visual panel, inset plots, and other figure-internal annotations.

Exclude:

- figure captions and legends outside the visual figure
- surrounding body text
- tables
- equations
- page headers, footers, watermarks, journal chrome, and page numbers
- supplementary figures unless they appear in the main PDF body and are labeled there

Treat a multi-panel figure as one figure unless the source explicitly labels separate figures.

Store captions in `caption_text`; do not include external captions in the crop image. If a title, label, legend, or short explanatory phrase is visually embedded inside the figure panel, include it and explain why in `rationale`.

## Internal Candidate Detection

`extract-figure` must first produce `figure_candidates.json`. This is the skill's internal visual-segmentation and association evidence. It is not a separate skill and not final truth.

Use any available mechanical or model-assisted evidence to propose candidates:

- page-image layout/object detection when available
- PDF text boxes or OCR boxes for captions, body text, headers, and footers
- connected visual components, ruling lines, whitespace gaps, and page bands
- bounded previews inspected by the model

If no mechanical layout detector is available, still write `figure_candidates.json`, but set `source` to `model_visual` for model-proposed regions and record the limitation. Do not call the run automatic in that case.

Candidate detection must separate region types before final crop decisions:

- `figure_visual`
- `caption`
- `body`
- `header`
- `footer`
- `table`
- `equation`
- `separator`
- `unknown`

Do not decide a final crop from a caption location alone. A figure needs visual region evidence.

## Image Size Strategy

Any image the agent reads must be bounded to at most 1600 px on both dimensions. For multi-image reads, use previews no larger than 1400 px on both dimensions and keep batches small. Never read full-resolution rendered pages, full-resolution crop PNGs, or raw edge-strip PNGs directly when either dimension exceeds 1600 px.

Use previews for discovery and verification:

```bash
python3 ${CLAUDE_SKILL_DIR}/../_shared/scripts/make_image_preview.py \
  "<output_dir>/pages/page_N.png" \
  "<output_dir>/figures/previews/page_N_preview.jpg" \
  --max-width 1400 --max-height 1400
```

The preview script reports scale factors. Convert preview coordinates back to rendered-page pixels before writing `bbox_px` or `crop_px`.

For crowded pages, create targeted region previews around candidate regions and inspect those before deciding the final high-resolution crop.

Final crop verification should read a bounded crop preview when the crop image is too large for reliable inspection:

```bash
python3 ${CLAUDE_SKILL_DIR}/../_shared/scripts/make_image_preview.py \
  "<output_dir>/figures/Figure_1.png" \
  "<output_dir>/figures/previews/Figure_1_preview.jpg" \
  --max-width 1400 --max-height 1400
```

For edge checks, crop a narrow boundary strip from the final crop or source page, then make a bounded preview of that strip before reading it.

```bash
python3 ${CLAUDE_SKILL_DIR}/../_shared/scripts/crop_region.py \
  "<output_dir>/figures/Figure_1.png" 0 <crop_height_minus_220> <crop_width> <crop_height> \
  "<output_dir>/figures/previews/Figure_1_bottom_edge_raw.png" --padding 0

python3 ${CLAUDE_SKILL_DIR}/../_shared/scripts/make_image_preview.py \
  "<output_dir>/figures/previews/Figure_1_bottom_edge_raw.png" \
  "<output_dir>/figures/previews/Figure_1_bottom_edge.png" \
  --max-width 1400 --max-height 700
```

Record only the bounded edge preview paths in `figures.json`. Keep raw strips only as intermediate files if needed.

## Workflow

Before writing any JSON manifest, read `../_shared/references/figure_schemas.md` for exact field names and shapes.

Before doing work in `continue_incomplete_extraction` mode, audit the current artifacts and state the first missing or stale step:

- check whether rendered pages exist under `<output_dir>/pages/`
- check whether page previews exist and are bounded to safe dimensions
- check whether `figure_candidates.json` exists and covers expected pages
- check whether `figure_index.json` exists and lists expected figure IDs
- check whether `figure_decisions.json` exists and has crop boxes/output files for every indexed figure
- check whether every referenced crop PNG exists
- check whether every crop has a bounded full preview plus bounded top/bottom/left/right edge previews
- check whether `figures.json` exists and matches current decisions/crops
- check whether `figures_mechanical_validation.json` exists and passes

Continue from the first missing step. Do not redo completed discovery unless visual evidence shows it is wrong.

In `initial_extraction_batch` mode, process only assigned pages and expected figure IDs. If the assignment omits a figure that is clearly visible on those pages, report it instead of silently adding it. If an expected figure is not visible on assigned pages, report it as unresolved for the orchestrator.

In `continue_incomplete_extraction` mode, start from the first missing artifact. If candidates and index already exist, do not redo discovery unless they are clearly wrong; continue at step 6 and complete the remaining extractor outputs.

In `repair_from_visual_review` mode, skip discovery steps 1-5 unless the repair request proves the original figure inventory is wrong. Start from the requested failed figures, reread their current decisions, source page context, and crop previews, then continue at step 7 for each requested figure.

1. Ensure rendered page images exist.
2. Create bounded page previews.
3. Produce `figure_candidates.json` by segmenting page images into visual/text regions and associating figure-like visual regions with caption candidates.
4. Read `figure_candidates.json`, page previews, and targeted candidate previews.
5. Write `figure_index.json` listing the labeled figures selected from candidates.
6. For each figure, verify the relevant candidate visual regions and excluded text/chrome regions.
7. Write `figure_decisions.json` in the strict schema below before any final crop command.
8. Crop mechanically with the shared crop helper.
9. Create and read crop previews for every output crop.
10. If a crop is wrong, update `figure_decisions.json`, rerun the crop, and verify again.
11. For every accepted figure, create and read bounded top, bottom, left, and right boundary previews. Record those paths in `crop_previews_read` and apply the verification rules below.
12. Write `figures.json` only after all crops are verified and every crop box matches the current files.
13. Run the validator in mechanical-only mode and write `figures_mechanical_validation.json`.
14. If mechanical validation fails, fix the artifact or report the extraction as incomplete. Do not call the overall run complete until `review-figure-extraction` independently passes the visual review and final validation.

Cropping command:

```bash
python3 ${CLAUDE_SKILL_DIR}/../_shared/scripts/crop_region.py \
  "<output_dir>/pages/page_N.png" <x1> <y1> <x2> <y2> \
  "<output_dir>/figures/<figure_id>.png" --padding 5
```

Validation command:

```bash
python3 ${CLAUDE_SKILL_DIR}/../_shared/scripts/validate_figures.py \
  "<output_dir>" --mechanical-only --write "<output_dir>/figures/figures_mechanical_validation.json"
```

## Candidate Manifest

Write `figure_candidates.json` before `figure_index.json`. Top-level shape is `{"pages": [...]}`. For complete JSON examples, see `../_shared/references/figure_schemas.md`.

Each page entry includes `page`, `page_image`, `page_size_px`, `regions`, and `figure_candidates`. Each region includes `region_id`, `region_type`, `bbox_px`, `source`, `confidence`, `text`, and `notes`. Each candidate includes `candidate_id`, `figure_label`, `caption_region_ids`, `visual_region_ids`, `excluded_region_ids`, `crop_px`, `confidence`, and `risks`.

Use `source` values:

- `layout_detector`
- `object_detector`
- `pdf_text`
- `ocr`
- `geometry`
- `model_visual`
- `manual`

If `source` is `model_visual` or `manual`, explain the limitation in `notes` or `risks`.

## Figure Index

Write `figure_index.json` after reading candidate evidence and before final crop decisions.

Top-level shape is `{"figures": [...]}`. Each figure includes `figure_id`, `figure_label`, `figure_number`, `figure_type`, `pages`, `candidate_ids`, `caption_text`, and `notes`. See `../_shared/references/figure_schemas.md` for a full example.

Use filename-safe `figure_id` values such as `Figure_1`, `Figure_2`, or `Extended_Data_Figure_1`. Do not use spaces in `figure_id`.

Use `figure_type` values:

- `main`
- `extended`
- `supplementary`
- `other`

## Decision Manifest

Write `figure_decisions.json` before any final crop command.

Top-level shape is `{"figures": [...]}`. Each figure includes identifiers, pages, region IDs, source images/previews read, `caption_text`, `expected_panels`, `crop_px`, `output_files`, `exclusions`, and `rationale`. See `../_shared/references/figure_schemas.md` for a full example.

Do not use alternate keys such as `label`, `file`, `crop`, `crop_bbox`, `crop_region`, or `output_file`.

For a multi-page figure, include one crop rectangle per page in `crop_px` and one output filename per crop in `output_files`, for example `Figure_4_page_6.png` and `Figure_4_page_7.png`. If you stitch multiple page crops into one image, record that explicitly in `rationale` and still preserve the per-page crop boxes.

## Final Manifest

Write `figures.json` only after every crop has been visually checked.

Top-level shape is `{"figures": [...]}`. Each figure includes identifiers, `pages`, `candidate_ids`, `image_files`, `crop_previews_read`, `caption_text`, `crop_px`, `verification`, and `notes`. See `../_shared/references/figure_schemas.md` for a full example.

`figures.json` must faithfully reflect `figure_decisions.json`. Do not rewrite figure IDs, crop boxes, captions, pages, candidate IDs, or output filenames while writing the final manifest.

Use verification values:

- `pass`
- `fail`

Do not use `not_applicable` in final verification. If a figure has no axes or legends, the relevant completeness check still passes when there is nothing missing or cut off.

Any `fail` or non-`pass` verification value means the extraction is not complete. A crop with a visible external caption, visible header/footer/chrome/watermark, adjacent body text, or any truncated figure content must have `result: "fail"` and the run must not be called complete.

## Verification

A crop is acceptable only after reading the cropped PNG or its bounded preview.

Check:

- all expected panels are visible and complete
- the `expected_panels` list itself is correct for the source figure; do not invent panels from caption cross-references or body text
- axes, labels, legends, scale bars, and panel letters are not cut off
- the crop follows candidate visual regions rather than caption text alone
- the caption is excluded unless it is visually embedded inside the figure panel
- page headers, footers, separator lines, journal section labels, and watermarks are excluded when possible
- no adjacent figure, table, body text, or page chrome is included
- the crop is not a lazy full-page or full-column screenshot

Large full-width figures are allowed, but the vertical crop should still be tight. If a crop uses almost the whole page width or more than most of the page height, scrutinize it for body text, captions, and chrome before accepting it.

When validating a crop, inspect at least the full crop preview and targeted edge previews of the top, bottom, left, and right boundaries. For chart-like figures, the bottom edge must show complete x-axis tick labels/title and the side edges must show complete y-axis labels, color bars, legends, and plot boundaries where present. If non-figure content touches an edge, shrink the crop. If figure content touches an edge, expand the crop. If both happen because the source layout interleaves caption/body text with figure panels, mark the figure incomplete rather than pretending the crop is clean.

Record all four edge preview paths in `figures.json`. A final crop with only a generic preview path is not complete, even if it looks acceptable at thumbnail scale.

Do not let an outer orchestrator or parent agent backfill `figures.json` from partial crop output. If the stage runs out of context after cropping but before verification and validation, the stage is incomplete.

## Trace Expectations

When traced by the orchestrator, report enough detail for it to log: candidate detection method, source/crop previews read, crop commands, manifest writes, validator command/result, and any unresolved figure-specific blockers.

Opaque scripts that identify figures and crop them without model-visible candidate evidence and crop decisions are not compliant for this skill.

---

# 中文對照

這份文件由中英雙語對照組成。中文對照是給我看的，請務必保持兩語言內容完全一致，並讓中文流暢通順、易於閱讀。

# 擷取圖

## 中繼資料

- name: `extract-figure`
- description: 從科學 PDF 擷取有標籤的圖，輸出已驗證的裁切圖片；先把頁面視覺內容切分成候選區域，再由模型驗證哪些內容屬於圖，以及裁切邊界是否正確。
- argument-hint: `<pdf_path> <output_dir>`

## 任務

你要從科學 PDF 中擷取每個有標籤的圖，輸出乾淨的 PNG 裁切圖。

此技能負責整個圖擷取任務：候選偵測、圖與圖說的關聯、裁切決策、裁切、驗證和最終清單檔。不要建立另一個獨立的圖切分階段。

來源 PDF 和已轉成圖片的頁面是最終依據。輔助程式可以轉出頁面圖片、建立預覽圖、提出視覺/文字區域、裁切矩形，並驗證結構規格；但這些輸出只能作為候選證據。模型必須判斷哪些候選項是真正的圖、每張圖應包含哪些內容，以及每個裁切是否可接受。

此技能負責擷取階段。它必須產生裁切圖、清單檔、預覽圖和機械式預檢驗證；但它不做最終的獨立接受判定。完整的圖擷取流程結束後，必須再使用 `review-figure-extraction`；該技能會寫出 `visual_review.json` 和最終 `figures_validation.json`。

## 模式

`initial_extraction` 用於從 PDF 和頁面圖片開始。

`initial_extraction_batch` 用於大型論文，由協調器指派頁面範圍或圖子集。批次執行目錄必須使用正常執行配置，並且只為指派頁面或圖產生完整的批次本地成果。不要寫入論文 root 層級的成果。

`continue_incomplete_extraction` 用於先前擷取者只產生部分成果時，例如只有候選項/索引，沒有最終裁切圖或最終清單檔。從既有成果繼續，但仍要完成完整擷取契約：決策、裁切 PNG、受限尺寸預覽圖、邊緣預覽圖、`figures.json` 和機械式驗證。不要讓父協調器替你補裁切決策。

`repair_from_visual_review` 用於協調器提供 `repair_requests.json` 時。修復模式中，只讀未通過的圖及其修復請求，以及相關清單檔、來源頁面和預覽圖。除非要求的變更會影響相鄰圖的裁切，否則只修復被要求的圖。不要把完整視覺審查當成主要修復輸入；協調器會先把它縮小成 `repair_requests.json`。

對每個已修復圖，保留相同 `figure_id`，更新 `figure_decisions.json`，重新產生裁切圖和裁切預覽圖，重新讀取來源上下文和最終裁切預覽圖，更新 `figures.json`，並重新執行機械式驗證。重新裁切後，不要讓任何清單檔保留過期裁切座標。

如果要求修復的圖無法乾淨隔離成單一矩形，請在擷取者結果中回報，並讓最新清單檔如實反映狀態。修復輪次用完後是否標記為終止狀態 `uncropable`，由協調器決定。

## 視覺檢查契約

程式碼不能證明圖品質。Python 輔助工具可以轉圖、裁切、建立預覽圖、檢查檔案存在，並標記幾何風險。它們不能判斷裁切是否完整、圖說是否外漏、座標軸或圖例是否被切掉，也不能判斷某個頁面條帶是否只是包含圖的一大塊截圖。

對每張準備判定為可接受的圖，代理都必須視覺檢查兩類證據：

- 原始來源證據：已轉成圖片的頁面，或受限尺寸的頁面/區域預覽圖；必須包含完整圖、圖說邊界、附近正文和頁面固定元素。
- 最終裁切證據：裁切後 PNG，或由最終裁切 PNG 建立的受限尺寸預覽圖。

不要只根據 JSON、尺寸、裁切座標、OCR/文字框、檔案存在或 Python 像素分析，就把圖判定為通過。

對每張圖，都要把最終裁切與來源頁面證據相比，並逐一檢查所有裁切邊緣。可接受的裁切必須顯示完整視覺圖，且不能包含禁止的鄰近內容。如果任何分圖、座標軸標籤、圖例、比例尺、插圖、分圖字母、列/欄標籤、色條或圖表邊界被切掉，就必須判定為未通過。如果外部圖說、正文、文章頁首、頁尾、期刊標籤、水印或頁碼出現在裁切中，也必須判定為未通過；除非它確實是圖內部內容，而不是頁面版面文字。

對圖表型圖片，例如折線圖、長條圖、散點圖、熱圖、Manhattan 圖和帶座標軸的示意圖，底邊和側邊最容易出問題。判定通過前，必須檢查來源上下文和最終裁切邊緣預覽圖，確認座標軸標題、刻度標籤、圖例、色條和圖表邊界完整。如果不確定某張圖是否屬於圖表型，也要做圖表邊緣檢查。

驗證欄位只使用 `pass` 或 `fail`。只有所有子檢查都是 `pass`，最終 `result: "pass"` 才允許。任何不確定性或未解決視覺缺陷都是 `fail`。

常見失敗模式包括：把裁切做成頁面條帶、誤含圖說或頁面固定元素、截斷圖內容、把輔助框當成最終依據，以及沒有閱讀來源與裁切預覽圖就標為通過。

## 檔案契約

讀取：

- `<pdf_path>`
- `<output_dir>/pages/` 中的頁面圖片，必要時建立。
- `repair_from_visual_review` 模式中的 `<output_dir>/figures/repair_requests.json`。

寫出：

- `<output_dir>/figures/figure_candidates.json`
- `<output_dir>/figures/figure_index.json`
- `<output_dir>/figures/figure_decisions.json`
- 每個單頁圖的 `<output_dir>/figures/<figure_id>.png`
- 多頁圖每頁的 `<output_dir>/figures/<figure_id>_page_<N>.png`，除非建立一張已驗證的拼接圖。
- `<output_dir>/figures/previews/` 下的頁面、區域和裁切預覽圖。
- `<output_dir>/figures/figures.json`
- `<output_dir>/figures/figures_mechanical_validation.json`
- 如果要求的裁切無法乾淨完成，可在代理回覆中提供選用修復註記。

下游 `review-figure-extraction` 技能寫：

- `<output_dir>/figures/visual_review.json`
- `<output_dir>/figures/figures_validation.json`

不要修改來源 PDF。

如果論文沒有有標籤的圖，寫出所有 JSON 成果，圖列表為空，且驗證結果通過。

## 邊界

包含屬於有標籤圖的視覺內容，例如 `Fig. 1` 或 `Figure 2` 的分圖、分圖標籤、座標軸、比例尺、圖內圖例、插圖和其他圖內標註。

排除：

- 外部圖說和圖例。
- 周圍正文。
- 表格。
- 方程式。
- 頁首、頁尾、水印、期刊固定元素和頁碼。
- 補充圖，除非它們出現在主 PDF 內文中，且在那裡有標籤。

除非來源明確標成不同圖，多分圖圖形視為一張圖。

圖說存入 `caption_text`；不要把外部圖說放進裁切圖。如果標題、標籤、圖例或短說明文字是視覺上嵌在圖面板內的內容，要包含它，並在 `rationale` 說明原因。

## 內部候選偵測

`extract-figure` 必須先產生 `figure_candidates.json`。這是技能內部的視覺切分和關聯證據，不是獨立技能，也不是最終依據。

可以使用任何可用的機械或模型輔助證據來提出候選項：

- 頁面圖片版面或物件偵測。
- PDF 文字框或 OCR 框，用於圖說、正文、頁首和頁尾。
- 連通視覺元件、線條、空白間隔和頁面帶狀區域。
- 模型檢查過的受限尺寸預覽圖。

如果沒有機械版面偵測器，仍要寫 `figure_candidates.json`；但對模型提出的區域，把 `source` 設為 `model_visual`，並記錄限制。不要把這種執行稱為自動化。

候選偵測必須在最終裁切決策前分開區域類型：

- `figure_visual`
- `caption`
- `body`
- `header`
- `footer`
- `table`
- `equation`
- `separator`
- `unknown`

不要只根據圖說位置決定最終裁切。圖需要視覺區域證據。

## 圖片尺寸策略

代理讀取的任何圖片，兩邊都不得超過 1600 px。多圖讀取時，每張兩邊不得超過 1400 px，且批次要小。不要直接讀完整解析度頁面、完整解析度裁切 PNG 或原始邊緣條帶。

探索和驗證都使用預覽圖。英文原文中的 `make_image_preview.py` 指令會回報縮放比例；寫 `bbox_px` 或 `crop_px` 前，要把預覽圖座標轉回頁面圖片像素座標。

擁擠頁面應建立針對性區域預覽圖，再決定最終高解析度裁切。

如果最終裁切圖太大，請先建立受限尺寸裁切預覽圖再讀取。邊緣檢查時，從最終裁切圖或來源頁面裁出窄邊界條帶，再建立受限尺寸預覽圖後讀取。

在 `figures.json` 中只記錄受限尺寸邊緣預覽圖路徑；原始條帶可作為中間檔保留。

## 工作流程

寫任何 JSON 清單檔前，先讀 `../_shared/references/figure_schemas.md`，取得精確欄位名稱和形狀。

在 `continue_incomplete_extraction` 模式中，先稽核目前成果，指出第一個缺失或過期步驟：

- `<output_dir>/pages/` 下是否有頁面圖片。
- 頁面預覽圖是否存在，且尺寸受限。
- `figure_candidates.json` 是否存在並覆蓋預期頁面。
- `figure_index.json` 是否存在並列出預期圖 ID。
- `figure_decisions.json` 是否為每個已索引圖提供裁切框和輸出檔。
- 每個引用的裁切 PNG 是否存在。
- 每個裁切是否有受限尺寸完整預覽圖，以及上、下、左、右邊緣預覽圖。
- `figures.json` 是否存在，且符合目前決策和裁切。
- `figures_mechanical_validation.json` 是否存在並通過。

從第一個缺失步驟繼續。除非視覺證據顯示已完成的發現結果有誤，否則不要重做。

在 `initial_extraction_batch` 模式中，只處理指派頁面和預期圖 ID。如果指派範圍內明顯有未列入的圖，回報它，不要靜默新增。如果預期圖不在指派頁面中，回報給協調器處理。

在 `repair_from_visual_review` 模式中，除非修復請求證明原始圖清單錯誤，否則跳過發現步驟，直接從未通過的圖、現有決策、來源頁面上下文和裁切預覽圖開始。

完整流程是英文原文列出的 14 步：確保頁面圖片存在、建立預覽圖、產生候選檔、寫索引、寫決策、裁切、建立並讀取預覽圖、做邊緣檢查、寫 `figures.json`，最後執行機械式驗證。任何機械式驗證未通過，都要修復成果或回報尚未完成。整體執行只有在 `review-figure-extraction` 獨立完成視覺審查並通過最終驗證後，才算完成。

## 清單檔

`figure_candidates.json`、`figure_index.json`、`figure_decisions.json` 和 `figures.json` 的形狀以上方英文和 shared schema 為準。

`figure_id` 要可安全作為檔名，例如 `Figure_1`、`Figure_2` 或 `Extended_Data_Figure_1`。不要在 `figure_id` 中使用空格。

`figure_type` 可用值：

- `main`
- `extended`
- `supplementary`
- `other`

`figure_decisions.json` 必須在任何最終裁切指令前寫出。不要使用 `label`、`file`、`crop`、`crop_bbox`、`crop_region` 或 `output_file` 這類替代鍵。

多頁圖要在 `crop_px` 中逐頁記錄裁切矩形，在 `output_files` 中逐頁記錄輸出檔名。如果把多頁裁切拼接成一張圖，要在 `rationale` 中明確記錄，並仍保留逐頁裁切框。

`figures.json` 只能在每個裁切都經視覺檢查後寫出。它必須忠實反映 `figure_decisions.json`；不要在寫最終清單時改寫圖 ID、裁切框、圖說、頁面、候選 ID 或輸出檔名。

驗證值只用 `pass` 或 `fail`。最終驗證不要使用 `not_applicable`。即使圖沒有座標軸或圖例，只要沒有缺失，相關完整性檢查就可以通過。

任何 `fail` 或非 `pass` 驗證值都表示擷取尚未完成。裁切圖若包含外部圖說、頁首/頁尾/固定元素/水印、相鄰正文，或有任何圖內容被截斷，必須設為 `result: "fail"`，不得稱完成。

## 驗證

只有在讀取裁切 PNG 或其受限尺寸預覽圖後，裁切才可接受。

檢查：

- 所有預期分圖都可見且完整。
- `expected_panels` 本身正確；不要因圖說交叉引用或正文文字而發明分圖。
- 座標軸、標籤、圖例、比例尺和分圖字母沒有被切掉。
- 裁切跟隨候選視覺區域，而不是只跟隨圖說文字。
- 圖說被排除，除非它是視覺上嵌在圖面板內的內容。
- 頁首、頁尾、分隔線、期刊章節標籤和水印在可行時被排除。
- 沒有相鄰圖、表格、正文或頁面固定元素。
- 裁切不是懶惰的整頁或整欄截圖。

大幅寬圖可以接受，但垂直裁切仍應緊湊。如果裁切幾乎使用整頁寬度，或高度超過大半頁，要特別檢查是否包含正文、圖說和頁面固定元素。

驗證裁切時，至少檢查完整裁切預覽圖，以及上、下、左、右邊界的目標邊緣預覽圖。對圖表型圖片，底邊必須顯示完整 x 軸刻度標籤/標題，側邊必須在存在時顯示完整 y 軸標籤、色條、圖例和圖表邊界。

如果非圖內容碰到邊緣，縮小裁切。如果圖內容碰到邊緣，放大裁切。如果兩者因來源版面交錯而同時發生，將該圖標記為未完成，不要假裝裁切乾淨。

在 `figures.json` 中記錄四個邊緣預覽圖路徑。只有一般預覽圖路徑的最終裁切不算完成。

不要讓外層協調器或父代理從部分裁切輸出回填 `figures.json`。如果階段在裁切後、驗證和最終清單前耗盡上下文，該階段就是未完成。

## 追蹤紀錄要求

被協調器追蹤時，回報足夠細節讓它記錄：候選偵測方法、讀取的來源/裁切預覽圖、裁切指令、清單檔寫入、驗證器指令/結果，以及任何未解決的圖特定阻礙。

如果不透明腳本在沒有模型可見候選證據和裁切決策的情況下識別並裁切圖，對此技能而言不合規。
