---
name: extract-equation
description: Extract displayed equations as verified crop images and LaTeX records, using rendered PDF pages as ground truth.
argument-hint: <pdf_path> <output_dir> [mode] [scope]
---
This document is composed of bilingual English-Chinese parallel text. The Chinese version is for the user's reading, so keep it natural, fluent, and easy to read while preserving full consistency between the two languages.
這份文件由中英雙語對照組成。中文對照是給我看的，請務必保持兩語言內容完全一致，並讓中文流暢通順、易於閱讀。

# Extract Equation

Extract displayed equations from one PDF into crop PNGs plus LaTeX metadata.

Rendered page images are ground truth. PDF text extraction may help locate candidates, but equation scope and LaTeX must be decided from visual evidence.

PDF text extraction loses spatial relationships between symbols, so subscripts, superscripts, fraction layout, limits, and alignment cannot be reliably inferred from text flow. Always transcribe LaTeX from rendered-page evidence.

## Modes

- `initial_extraction`: scan the assigned scope and produce the full equation artifact contract.
- `initial_extraction_batch`: same work, but write only inside the batch output directory assigned by the orchestrator.
- `continue_incomplete_extraction`: audit existing artifacts first, then continue from the first missing contract item.
- `repair_from_visual_review`: read `equation_repair_requests.json` and repair only requested equations.

In repair mode, do not rediscover the whole paper unless the request says the equation inventory is wrong.

## File Contract

Read:

- `<pdf_path>`
- `<output_dir>/pages/page_<N>.png`, creating pages with `render_pages.py` if needed
- in repair mode: `<output_dir>/equations/equation_repair_requests.json`

Write under `<output_dir>/equations/`:

- `equation_candidates.json`
- `equation_index.json`
- `equation_decisions.json`
- `Equation_<N>.png`
- bounded previews under `previews/`
- rendered LaTeX previews under `rendered_latex/`
- `equations.json`
- `equations_mechanical_validation.json`

If no displayed equations exist, write empty `equation_candidates.json`, `equation_index.json`, `equation_decisions.json`, and `equations.json`, then run mechanical validation.

Before writing any JSON manifest, read `../_shared/references/equation_schemas.md` for exact field names and shapes.

## Image Rule

Do not read full-resolution rendered pages, full-resolution crops, or raw high-resolution strips directly. Read bounded previews only: both dimensions <=1600 px, and <=1400 px for multi-image reads.

Use:

```bash
python3 skills/_shared/scripts/crop_region.py ...
python3 skills/_shared/scripts/make_image_preview.py ...
```

## Scope Rules

Default scope is `all_displayed`: extract every displayed (centered/offset) equation, whether numbered or unnumbered. This includes equation blocks in propositions, lemmas, corollaries, and appendix proofs.

For unnumbered equations, assign synthetic `equation_number` values using the page-anchored pattern `unnumbered_p<page>_<seq>` (e.g., `unnumbered_p7_1`). The `equation_id` follows the normal sequential pattern (`Equation_1`, `Equation_2`, etc.) regardless of numbering status.

If the orchestrator specifies `scope: numbered_only`, extract only equations with explicit visible numbers such as `(1)`, `(2)`, `Eq. 1`. Mention important unnumbered displays in `notes` but do not extract them.

Scan every page in the assigned scope. If the orchestrator assigns a page range, scan that range. If no range is assigned, scan every page of the PDF including appendices, supplementary proofs, and endmatter. Do not assume equations only appear in the main body.

If no equations are found, write empty `equation_candidates.json`, `equation_index.json`, `equation_decisions.json`, and `equations.json`, then run mechanical validation (should pass with 0 count).

Exclude inline math, ordinary variable definitions in running prose, chemical structure diagrams, and figure panels in all scope modes.

## Workflow

1. Render pages if needed.
2. Read bounded page previews for the assigned scope. Treat page hints from the orchestrator as hints, not truth.
3. Identify displayed equation candidates and write `equation_candidates.json`.
4. Write `equation_index.json` to commit which candidates are real displayed equations before deciding crop boundaries or LaTeX.
5. For each indexed equation, read a bounded source region showing the full equation and surrounding prose boundary.
6. Decide crop boundaries and LaTeX from visual evidence. Use page-keyed `crop_px` and `image_files` arrays.
7. Write `equation_decisions.json` before cropping or final serialization.
8. Crop `Equation_<N>.png`, then create crop and source previews.
9. Write `equations.json`.
10. Render LaTeX previews (uses pdflatex when available, falls back to matplotlib then text):
   ```bash
   python3 skills/_shared/scripts/render_latex_preview.py \
     "<output_dir>/equations/equations.json" "<output_dir>/equations/rendered_latex" --batch
   ```
   This writes `rendered_latex_renderer` and `rendered_latex_previews_read` into each equation in `equations.json`. Previews help review but do not replace visual comparison with the source.
11. Write the human-readable LaTeX summary:
   ```bash
   python3 skills/_shared/scripts/generate_latex_summary.py \
     "<output_dir>/equations/equations.json"
   ```
12. Read the source region and crop preview. Compare the crop and LaTeX against the visible math.
13. Run:
   ```bash
   python3 skills/_shared/scripts/validate_equations.py \
     "<output_dir>" --mechanical-only --write "<output_dir>/equations/equations_mechanical_validation.json"
   ```

If validation fails, repair the artifacts and rerun it before returning.

## LaTeX Rules

- Preserve fractions, superscripts, subscripts, roots, matrices, cases, summation/integral limits, Greek letters, operators, and meaningful alignment.
- Use `\frac{...}{...}`, `^{...}`, `_{...}`, `\sqrt{...}`, `\sum`, `\int`, and `\begin{aligned}...\end{aligned}` where appropriate.
- Accent variants: use `\hat{x}` for single-character accents, `\widehat{XY}` for multi-character spans. Same for `\tilde`/`\widetilde`, `\bar`/`\overline`, `\dot`/`\ddot`. Compare accent width in the source image to choose between narrow and wide variants.
- Multi-line environments: preserve `\begin{aligned}`, `\begin{cases}`, `\begin{pmatrix}` structure. Do not flatten multi-line equations to a single line.
- Store the equation number in metadata, not inside `latex`, unless the user asks for display-ready full text.
- Record unresolved symbol ambiguity in `uncertainties`; a passing extraction has no unresolved uncertainties.

## Verification

An equation passes only when:

- the crop includes the full displayed equation and its number
- no surrounding prose/page chrome is included
- top, bottom, left, and right crop edges are clean
- the LaTeX matches the visual equation structure
- small notation is complete: subscripts, superscripts, limits, primes, bars, hats, dots, and Greek letters
- multiline alignment, cases, matrices, or bracketed structures are preserved

- multi-line equations are cropped as a single block; do not split unless the equation spans a page break
- page-spanning equations: crop each page's portion separately, list both in `image_files`, and note the split in `notes`

Use only `pass` or `fail`. Uncertainty is `fail` until repaired or recorded as a terminal condition by the orchestrator.

## Repair Mode

Repair requests describe the defect and direction, not exact coordinates. Valid repair directions include `expand_crop_left`, `expand_crop_bottom`, `remove_surrounding_prose`, `correct_latex_symbol`, `correct_latex_structure`, `add_alignment`, `fix_equation_number`, and `mark_uncertain_symbol`.

After repair, update `equation_decisions.json`, affected crop/previews/rendered preview, `equations.json`, and `equations_mechanical_validation.json`. Do not edit old round snapshots.

---

# 中文對照

# 擷取方程式

## 中繼資料

- name: `extract-equation`
- description: 使用已轉成圖片的 PDF 頁面作為最終依據，將顯示方程式擷取為已驗證的裁切圖和 LaTeX 紀錄。
- argument-hint: `<pdf_path> <output_dir> [mode] [scope]`

## 任務

從一份 PDF 擷取顯示方程式，輸出裁切 PNG 和 LaTeX 中繼資料。

已轉成圖片的頁面是最終依據。PDF 文字擷取可以協助定位候選項，但方程式範圍和 LaTeX 必須根據視覺證據決定。

PDF 文字擷取會失去符號之間的空間關係，因此下標、上標、分式版面、上下限和對齊都不能可靠地從文字流推斷。LaTeX 一律要從頁面圖片證據轉寫。

## 模式

- `initial_extraction`：掃描指派範圍，並產生完整方程式成果契約。
- `initial_extraction_batch`：工作相同，但只寫入協調器指派的批次輸出目錄。
- `continue_incomplete_extraction`：先稽核既有成果，再從第一個缺失的契約項目繼續。
- `repair_from_visual_review`：讀取 `equation_repair_requests.json`，只修復被要求的方程式。

在修復模式中，除非請求指出方程式清單錯誤，否則不要重新發現整篇論文。

## 檔案契約

讀取：

- `<pdf_path>`
- `<output_dir>/pages/page_<N>.png`，必要時用 `render_pages.py` 建立。
- 修復模式中的 `<output_dir>/equations/equation_repair_requests.json`。

寫到 `<output_dir>/equations/`：

- `equation_candidates.json`
- `equation_index.json`
- `equation_decisions.json`
- `Equation_<N>.png`
- `previews/` 下的受限尺寸預覽圖
- `rendered_latex/` 下的 LaTeX 預覽圖
- `equations.json`
- `equations_mechanical_validation.json`

如果沒有顯示方程式，寫出空的 `equation_candidates.json`、`equation_index.json`、`equation_decisions.json` 和 `equations.json`，再執行機械式驗證。

寫任何 JSON 清單檔前，先讀 `../_shared/references/equation_schemas.md`，取得精確欄位名稱和形狀。

## 圖片規則

不要直接讀完整解析度頁面、完整解析度裁切圖或原始高解析度條帶。只讀受限尺寸預覽圖：單張圖片兩邊都不超過 1600 px；多圖讀取時兩邊都不超過 1400 px。

使用：

```bash
python3 skills/_shared/scripts/crop_region.py ...
python3 skills/_shared/scripts/make_image_preview.py ...
```

## 範圍規則

預設範圍是 `all_displayed`：擷取所有顯示方程式，也就是置中或獨立成行的方程式，無論是否編號。這包含命題、引理、推論和附錄證明中的方程式區塊。

對未編號方程式，使用頁面錨定的合成 `equation_number`，格式為 `unnumbered_p<page>_<seq>`，例如 `unnumbered_p7_1`。無論是否編號，`equation_id` 都使用正常連續格式，例如 `Equation_1`、`Equation_2`。

如果協調器指定 `scope: numbered_only`，只擷取明確可見編號的方程式，例如 `(1)`、`(2)`、`Eq. 1`。重要的未編號顯示方程式可在 `notes` 提到，但不要擷取。

掃描指派範圍中的每一頁。如果協調器指派頁面範圍，就掃描該範圍。如果沒有範圍，就掃描 PDF 每一頁，包括附錄、補充證明和文末材料。不要假設方程式只出現在正文。

如果沒有找到方程式，仍要寫空的 candidates、index、decisions 和 equations 檔，然後執行機械式驗證；0 個方程式時應通過。

排除行內數學、正文中的普通變數定義、化學結構圖，以及圖面板中的數學。

## 工作流程

1. 必要時轉出頁面圖片。
2. 讀取指派範圍的受限尺寸頁面預覽圖。協調器提供的頁面提示只是提示，不是最終依據。
3. 找出顯示方程式候選，並寫 `equation_candidates.json`。
4. 寫 `equation_index.json`，先確定哪些候選項是真正的顯示方程式，再決定裁切邊界或 LaTeX。
5. 對每個已列入索引的方程式，讀取受限尺寸來源區域，顯示完整方程式和周圍正文邊界。
6. 根據視覺證據決定裁切邊界和 LaTeX。使用依頁面 keyed 的 `crop_px` 和 `image_files` 陣列。
7. 在裁切或最終序列化前寫 `equation_decisions.json`。
8. 裁切 `Equation_<N>.png`，再建立裁切預覽圖和來源預覽圖。
9. 寫 `equations.json`。
10. 轉出 LaTeX 預覽圖；可用時使用 pdflatex，否則依序退回 matplotlib 和文字：
    ```bash
    python3 skills/_shared/scripts/render_latex_preview.py \
      "<output_dir>/equations/equations.json" "<output_dir>/equations/rendered_latex" --batch
    ```
    這會在 `equations.json` 的每個方程式中寫入 `rendered_latex_renderer` 和 `rendered_latex_previews_read`。預覽圖有助審查，但不能取代與來源視覺方程式的比較。
11. 寫人可讀的 LaTeX 摘要：
    ```bash
    python3 skills/_shared/scripts/generate_latex_summary.py \
      "<output_dir>/equations/equations.json"
    ```
12. 讀取來源區域和裁切預覽圖，把裁切圖和 LaTeX 與可見數學比較。
13. 執行：
    ```bash
    python3 skills/_shared/scripts/validate_equations.py \
      "<output_dir>" --mechanical-only --write "<output_dir>/equations/equations_mechanical_validation.json"
    ```

如果驗證未通過，先修復成果並重新執行驗證，再回覆。

## LaTeX 規則

- 保留分式、上標、下標、根號、矩陣、分段函數、求和/積分上下限、希臘字母、運算子和有意義的對齊。
- 適當使用 `\frac{...}{...}`、`^{...}`、`_{...}`、`\sqrt{...}`、`\sum`、`\int` 和 `\begin{aligned}...\end{aligned}`。
- 重音變體：單字元重音使用 `\hat{x}`，多字元範圍使用 `\widehat{XY}`。`\tilde`/`\widetilde`、`\bar`/`\overline`、`\dot`/`\ddot` 也是同理。要比較來源圖片中的重音寬度來選擇窄或寬版本。
- 多行環境：保留 `\begin{aligned}`、`\begin{cases}`、`\begin{pmatrix}` 等結構。不要把多行方程式壓成單行。
- 方程式編號存在中繼資料中，不要放進 `latex`，除非使用者要求可直接顯示的完整文字。
- 未解決的符號歧義記錄在 `uncertainties`；通過的擷取不得有未解決不確定性。

## 驗證

方程式只有在下列條件全部成立時才通過：

- 裁切圖包含完整顯示方程式和編號。
- 不包含周圍正文或頁面固定元素。
- 上、下、左、右裁切邊緣乾淨。
- LaTeX 符合可見方程式結構。
- 小型記號完整，包括下標、上標、上下限、撇號、橫線、帽號、點和希臘字母。
- 保留多行對齊、分段函數、矩陣或括號結構。

多行方程式應作為單一區塊裁切，不要拆開，除非方程式跨頁。跨頁方程式要分別裁切每頁部分，列在 `image_files`，並在 `notes` 說明分割。

只使用 `pass` 或 `fail`。只要仍有不確定性，就使用 `fail`，直到修復完成，或由協調器記錄為終止狀態。

## 修復模式

修復請求描述缺陷和方向，不提供精確座標。有效修復方向包括 `expand_crop_left`、`expand_crop_bottom`、`remove_surrounding_prose`、`correct_latex_symbol`、`correct_latex_structure`、`add_alignment`、`fix_equation_number` 和 `mark_uncertain_symbol`。

修復後，更新 `equation_decisions.json`、受影響的裁切圖/預覽圖/轉出預覽圖、`equations.json` 和 `equations_mechanical_validation.json`。不要編輯舊輪次快照。
