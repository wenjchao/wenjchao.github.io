---
name: review-table-extraction
description: Independently review extracted table crops and structured JSON by comparing rendered source table regions, final crops, and rendered table previews.
argument-hint: <output_dir> [round]
---
This document is composed of bilingual English-Chinese parallel text. The Chinese version is for the user's reading, so keep it natural, fluent, and easy to read while preserving full consistency between the two languages.
這份文件由中英雙語對照組成。中文對照是給我看的，請務必保持兩語言內容完全一致，並讓中文流暢通順、易於閱讀。

# Review Table Extraction

Review a completed `extract-table` stage. Your job is defect finding, not confirmation. Do not modify table crops or structured table artifacts.

Rendered page images are ground truth. The extracted crop and rendered JSON table preview are outputs to audit against the rendered source.

## File Contract

Read:

- `<output_dir>/tables/table_candidates.json`
- `<output_dir>/tables/table_index.json`
- `<output_dir>/tables/table_decisions.json`
- `<output_dir>/tables/tables.json`
- `<output_dir>/tables/tables_mechanical_validation.json`, if present
- rendered pages under `<output_dir>/pages/`
- final table crops/previews and rendered table previews
- `../_shared/references/table_schemas.md`

Write:

- reviewer evidence previews under `<output_dir>/tables/previews/reviewer_round_<N>/`
- `<output_dir>/tables/table_visual_review.json`

When the orchestrator assigns a batch scope, write the review to the path specified by the orchestrator (e.g., `previews/reviewer_round_<N>/batch_review_<M>.json`) instead of the root `table_visual_review.json`. Use the same schema; the orchestrator merges batch files into the root review.

Do not edit `Table_<N>.json`, crops, `table_decisions.json`, or `tables.json`. If an output is bad, fail it and write a repair request.

## Image Rule

Do not read full-resolution pages, crops, or raw strips directly. Create bounded reviewer evidence first: both dimensions <=1600 px, and <=1400 px for multi-image reads.

## Required Reads

For every table, read:

- a reviewer-created bounded source region from the rendered page showing title, full table body, footnote boundary, and nearby non-table content
- the final table crop preview
- the rendered preview of `Table_<N>.json`
- targeted source/crop edge previews for top, bottom, left, and right boundaries

If source context is insufficient to judge a boundary or footnote, create a targeted source edge/region preview before deciding.

Before judging the output, build a structural inventory from the rendered source: row count, column count, header level count, and footnote count. Then build the same inventory from the extracted JSON/rendered table preview. Passing review requires these inventories to match.

## Review Standard

A table passes only if:

- table number/title are complete and correct
- title separator (period, em-dash, colon) matches the source exactly
- all header levels, spanning headers, row labels, units, and footnote markers are represented
- row and column counts match the source
- wrapped source cells are not split into false rows
- all body cells appear in source order
- header and cell text matches the source character-for-character, including any misspellings or typos in the original — do NOT pass a table that has "corrected" source text
- symbols, inequalities, superscripts/footnote markers, and units are preserved
- footnote markers at start of footnote text match markers appearing in cells/headers
- all table footnotes are captured
- if the source table's first column has a two-part category + specific-item structure, verify the extraction captured both parts as separate columns
- the crop excludes surrounding prose, neighboring objects, and page chrome
- the crop top edge starts below any page header/running title (if top edge preview shows author names, journal identifiers, or DOI lines, the crop is too tall)
- the crop bottom edge ends above any page footer, page number, or body prose unrelated to the table
- top, bottom, left, and right crop edges are clean and supported by evidence
- the rendered JSON preview matches the source table structure

Uncertainty is failure. Do not pass with notes like "probably", "unclear", "mostly", or "minor".

## Output

Before writing `table_visual_review.json`, read `../_shared/references/table_schemas.md` for the exact schema.

Each table entry includes `table_id`, source/crop/rendered preview paths, source/crop edge preview paths, crop hashes, `expected_structure`, `observed_structure`, checks, `edge_checks`, defects, decision, repair request, and notes. Use only `pass` or `fail`. Compute `crop_hashes` as SHA-256 hex digests (matching `validate_tables.py`).

For a failed table, write concrete defects and semantic repair directions such as `split_header_level`, `merge_wrapped_cell`, `correct_cell_text`, `add_missing_footnote`, `expand_crop_bottom`, or `shrink_crop_top`. Do not propose exact coordinates.

`summary.table_count`, `summary.pass_count`, and `summary.fail_count` must match the `tables` list.

---

# 中文對照

# 審查表格擷取

## 中繼資料

- name: `review-table-extraction`
- description: 透過比較已轉出的來源表格區域、最終裁切圖和表格 JSON 的視覺預覽，獨立審查表格裁切圖與結構化 JSON。
- argument-hint: `<output_dir> [round]`

## 任務

審查已完成的 `extract-table` 階段。你的工作是找缺陷，不是背書。不要修改表格裁切圖或結構化表格成果。

已轉成圖片的頁面是審查時的最終依據。擷取出的裁切圖和 JSON 表格預覽，是要拿來和來源頁面比對的輸出。

## 檔案契約

讀取：

- `<output_dir>/tables/table_candidates.json`
- `<output_dir>/tables/table_index.json`
- `<output_dir>/tables/table_decisions.json`
- `<output_dir>/tables/tables.json`
- `<output_dir>/tables/tables_mechanical_validation.json`，如果存在。
- `<output_dir>/pages/` 下的頁面圖片。
- 最終表格裁切圖/預覽圖，以及轉出的表格預覽圖。
- `../_shared/references/table_schemas.md`

寫出：

- `<output_dir>/tables/previews/reviewer_round_<N>/` 下的審查者證據預覽圖。
- `<output_dir>/tables/table_visual_review.json`

如果協調器指派批次範圍，請把審查寫到協調器指定的路徑，例如 `previews/reviewer_round_<N>/batch_review_<M>.json`，而不是 root 的 `table_visual_review.json`。使用相同結構；協調器會把批次檔合併成 root 審查。

不要編輯 `Table_<N>.json`、裁切圖、`table_decisions.json` 或 `tables.json`。如果輸出有問題，將該表格判定為未通過，並寫出修復請求。

## 圖片規則

不要直接讀完整解析度頁面、裁切圖或原始條帶。先建立受限尺寸的審查證據：單張圖片兩邊都不超過 1600 px；多圖讀取時兩邊都不超過 1400 px。

## 必要讀取

每個表格都要讀：

- 由審查者建立的受限尺寸來源區域，顯示表題、完整表身、註腳邊界和附近非表格內容。
- 最終表格裁切預覽圖。
- `Table_<N>.json` 的視覺預覽。
- 上、下、左、右邊界的目標來源/裁切邊緣預覽圖。

如果來源上下文不足以判斷邊界或註腳，就先建立目標來源邊緣或區域預覽圖，再做判斷。

判斷輸出前，先根據來源頁面建立結構清單：列數、欄數、標題層數和註腳數。再根據擷取 JSON 或表格預覽建立同樣清單。只有兩份清單一致，表格才可通過審查。

## 審查標準

表格只有在下列全部成立時才通過：

- 表號和表題完整且正確。
- 表題分隔符，例如句點、破折號或冒號，與來源完全一致。
- 所有標題層級、跨欄標題、列標籤、單位和註腳標記都已表示。
- 列數和欄數符合來源。
- 來源中的換行儲存格沒有被拆成假列。
- 所有正文儲存格依來源順序出現。
- 標題和儲存格文字逐字元符合來源，包括原始錯字或拼字錯誤；不得通過已「修正」來源文字的表格。
- 符號、不等式、上標/註腳標記和單位都已保留。
- 註腳文字開頭的標記與儲存格/標題中的標記一致。
- 所有表格註腳都已擷取。
- 如果來源表格第一欄有「類別 + 具體項目」的雙層結構，確認擷取結果把兩部分分成不同欄。
- 裁切圖排除周圍正文、相鄰物件和頁面固定元素。
- 裁切圖上邊緣從頁首或 running title 下方開始；如果上邊緣預覽圖顯示作者名、期刊識別或 DOI 行，裁切太高。
- 裁切圖下邊緣停在頁尾、頁碼或無關正文之前。
- 上、下、左、右裁切邊緣乾淨且有證據支持。
- 表格 JSON 預覽符合來源表格結構。

只要仍不確定，就不能判定為通過。不要用「大概」、「不清楚」、「多半」或「小問題」這類註記把表格判定為通過。

## 輸出

寫 `table_visual_review.json` 前，先讀 `../_shared/references/table_schemas.md` 取得精確結構。

每個表格項目包含：`table_id`、來源/裁切/轉出預覽路徑、來源/裁切邊緣預覽路徑、裁切圖雜湊、`expected_structure`、`observed_structure`、checks、`edge_checks`、defects、decision、repair request 和 notes。

只使用 `pass` 或 `fail`。`crop_hashes` 必須計算為 SHA-256 十六進位摘要，與 `validate_tables.py` 一致。

對未通過的表格，寫出具體缺陷和語義修復方向，例如 `split_header_level`、`merge_wrapped_cell`、`correct_cell_text`、`add_missing_footnote`、`expand_crop_bottom` 或 `shrink_crop_top`。不要提出精確座標。

`summary.table_count`、`summary.pass_count` 和 `summary.fail_count` 必須與 `tables` 列表一致。
