---
name: review-equation-extraction
description: Independently review extracted equation crops and LaTeX by comparing rendered source equation regions, final crops, and rendered/text LaTeX previews.
argument-hint: <output_dir> [round]
---
This document is composed of bilingual English-Chinese parallel text. The Chinese version is for the user's reading, so keep it natural, fluent, and easy to read while preserving full consistency between the two languages.
這份文件由中英雙語對照組成。中文對照是給我看的，請務必保持兩語言內容完全一致，並讓中文流暢通順、易於閱讀。

# Review Equation Extraction

Review a completed `extract-equation` stage. Your job is defect finding, not confirmation. Do not modify equation crops or LaTeX artifacts.

Rendered page images are ground truth. The equation crop and LaTeX are outputs to audit against the rendered source.

## File Contract

Read:

- `<output_dir>/equations/equations.json`
- `<output_dir>/equations/equation_decisions.json`
- `<output_dir>/equations/equations_mechanical_validation.json`, if present
- rendered pages under `<output_dir>/pages/`
- final equation crops/previews and rendered LaTeX previews, if present
- `../_shared/references/equation_schemas.md`

Write:

- reviewer evidence previews under `<output_dir>/equations/previews/reviewer_round_<N>/`
- `<output_dir>/equations/equation_visual_review.json`
- `<output_dir>/equations/equations_validation.json`

Do not edit crops, `equation_decisions.json`, or `equations.json`. If an output is bad, fail it and write a repair request.

## Image Rule

Do not read full-resolution pages, crops, or raw strips directly. Create bounded reviewer evidence first: both dimensions <=1600 px, and <=1400 px for multi-image reads.

## Required Reads

For every equation, read:

- a reviewer-created bounded source region from the rendered page showing the full displayed equation, number, and surrounding prose boundary
- the final equation crop preview
- the LaTeX string in `equations.json`
- rendered LaTeX preview when available. If the preview is raw text (`text_fallback`), note the limitation, but do not fail the equation solely for renderer fallback.
- targeted source/crop edge previews for top, bottom, left, and right boundaries

If small notation or crop boundaries are hard to judge, create targeted higher-resolution bounded source/crop edge previews before deciding.

For large equation sets, follow the orchestrator's batching scope.

## Review Standard

An equation passes only if:

- the equation number is correct
- the crop includes the complete displayed equation and number
- surrounding prose, page chrome, and unrelated math are excluded
- top, bottom, left, and right crop edges are clean and supported by evidence
- LaTeX matches the visible math structure
- subscripts, superscripts, primes, bars, hats, dots, roots, matrices, cases, brackets, and summation/integral limits are preserved
- multiline alignment and line breaks are represented where meaningful
- no unresolved uncertainty is hidden inside a pass

Uncertainty is failure. Do not pass with notes like "probably", "unclear", "mostly", or "minor".

## Output

Before writing `equation_visual_review.json`, read `../_shared/references/equation_schemas.md` for the exact schema. Include the round number passed by the orchestrator as a top-level `round` field.

Each equation entry includes `equation_id`, equation number, source/crop/rendered preview paths, source/crop edge preview paths, crop hashes, checks, `edge_checks`, defects, decision, repair request, and notes. Use only `pass` or `fail`.

For a failed equation, write concrete defects and semantic repair directions such as `expand_crop_left`, `expand_crop_bottom`, `remove_surrounding_prose`, `correct_latex_symbol`, `correct_latex_structure`, `add_alignment`, `fix_equation_number`, or `mark_uncertain_symbol`. Do not propose exact coordinates.

`summary.equation_count`, `summary.pass_count`, and `summary.fail_count` must match the `equations` list.

## Final Validation

After writing `equation_visual_review.json`, run:

```bash
python3 skills/_shared/scripts/validate_equations.py \
  "<output_dir>" --write "<output_dir>/equations/equations_validation.json"
```

If validation fails because evidence images are oversized, leave the failure for the orchestrator's mandatory `normalize_visual_evidence.py` step. Do not edit extraction outputs to force a pass.

---

# 中文對照

# 審查方程式擷取

## 中繼資料

- name: `review-equation-extraction`
- description: 透過比較已轉出的來源方程式區域、最終裁切圖，以及 LaTeX 的圖片或文字預覽，獨立審查方程式裁切圖和 LaTeX。
- argument-hint: `<output_dir> [round]`

## 任務

審查已完成的 `extract-equation` 階段。你的工作是找缺陷，不是背書。不要修改方程式裁切圖或 LaTeX 成果。

已轉成圖片的頁面是審查時的最終依據。方程式裁切圖和 LaTeX 是要拿來對照來源頁面的輸出。

## 檔案契約

讀取：

- `<output_dir>/equations/equations.json`
- `<output_dir>/equations/equation_decisions.json`
- `<output_dir>/equations/equations_mechanical_validation.json`，如果存在。
- `<output_dir>/pages/` 下的頁面圖片。
- 最終方程式裁切圖/預覽圖，以及 LaTeX 預覽圖，如果存在。
- `../_shared/references/equation_schemas.md`

寫出：

- `<output_dir>/equations/previews/reviewer_round_<N>/` 下的審查者證據預覽圖。
- `<output_dir>/equations/equation_visual_review.json`
- `<output_dir>/equations/equations_validation.json`

不要編輯裁切圖、`equation_decisions.json` 或 `equations.json`。如果輸出有問題，將該方程式判定為未通過，並寫出修復請求。

## 圖片規則

不要直接讀完整解析度頁面、裁切圖或原始條帶。先建立受限尺寸的審查證據：單張圖片兩邊都不超過 1600 px；多圖讀取時兩邊都不超過 1400 px。

## 必要讀取

每個方程式都要讀：

- 由審查者建立的受限尺寸來源區域，顯示完整顯示方程式、編號和周圍正文邊界。
- 最終方程式裁切預覽圖。
- `equations.json` 中的 LaTeX 字串。
- 可用時，讀取 LaTeX 預覽圖。如果預覽是原始文字回退，也要記錄限制，但不要只因渲染器回退就判定為未通過。
- 上、下、左、右邊界的目標來源/裁切邊緣預覽圖。

如果小型記號或裁切邊界難以判斷，先建立更高解析度但仍受限尺寸的來源或裁切邊緣預覽圖，再做決定。

大型方程式集合應遵循協調器批次範圍。

## 審查標準

方程式只有在下列全部成立時才通過：

- 方程式編號正確。
- 裁切圖包含完整顯示方程式和編號。
- 排除周圍正文、頁面固定元素和無關數學。
- 上、下、左、右裁切邊緣乾淨且有證據支持。
- LaTeX 符合可見數學結構。
- 下標、上標、撇號、橫線、帽號、點、根號、矩陣、分段函數、括號和求和/積分上下限都已保留。
- 有意義的多行對齊和換行已表示。
- 通過結果中沒有隱藏未解決不確定性。

只要仍不確定，就不能判定為通過。不要用「大概」、「不清楚」、「多半」或「小問題」這類註記把方程式判定為通過。

## 輸出

寫 `equation_visual_review.json` 前，先讀 `../_shared/references/equation_schemas.md` 取得精確結構。把協調器傳入的輪次號寫成最上層 `round` 欄位。

每個方程式項目包含：`equation_id`、方程式編號、來源/裁切/轉出預覽路徑、來源/裁切邊緣預覽路徑、裁切圖雜湊、checks、`edge_checks`、defects、decision、repair request 和 notes。只使用 `pass` 或 `fail`。

對未通過的方程式，寫出具體缺陷和語義修復方向，例如 `expand_crop_left`、`expand_crop_bottom`、`remove_surrounding_prose`、`correct_latex_symbol`、`correct_latex_structure`、`add_alignment`、`fix_equation_number` 或 `mark_uncertain_symbol`。不要提出精確座標。

`summary.equation_count`、`summary.pass_count` 和 `summary.fail_count` 必須與 `equations` 列表一致。

## 最終驗證

寫 `equation_visual_review.json` 後執行：

```bash
python3 skills/_shared/scripts/validate_equations.py \
  "<output_dir>" --write "<output_dir>/equations/equations_validation.json"
```

如果驗證因證據圖片過大而未通過，把這個問題留給協調器透過必要的 `normalize_visual_evidence.py` 步驟處理。不要為了強迫驗證通過而編輯擷取輸出。
