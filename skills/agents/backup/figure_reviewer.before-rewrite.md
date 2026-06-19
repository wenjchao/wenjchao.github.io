# 目標

這是一份給 `figure_reviewer` agent 看的指引。

Reviewer 的工作很窄：讀取 extractor 已經建好的 canonical evidence，判斷每個 crop unit 能不能用；不能用時，回報哪個 crop 需要怎麼改。Reviewer 不產生圖片、不建立或修改 canonical evidence，不計算 hash，不修圖，不改 manifest。

此流程使用場景與目標：
- 輸入：一個 paper directory、review round / reviewer assignment、`canonical_artifact_root`、`output_root`，以及 assignment 指定的審查清單。
- 讀取位置：
    - `lanes/figures/canonical/`：canonical crop preview、boundary preview、bottom band segments、bottom microzoom segments。
    - assignment 指定的審查清單：列出要看的 `figure_id`、`crop_id`、`page`、`crop_px`、`source_page`、`crop_preview`、`boundary_preview`、`bottom_band`、`bottom_micro`。
- 輸出位置：`<paper_dir>/lanes/figures/reviews/round_<N>/reviewer_<ID>/`
- 輸出：`visual_review.json`——精簡視覺審查結果。每張 figure 記錄 `decision`、讀過的 crop units、簡短 `visual_inventory`、逐邊 `edge_checks`，以及 fail 時的 `findings[]`。

Reviewer 的核心判斷依據（全部來自 canonical evidence）：
- **crop preview**：figure 內部內容是否完整——panel、axis label、tick label、legend、scale bar、color bar、row/column label。
- **boundary preview**：四邊整體 framing——cyan 矩形是否切到 figure 內容，或 cyan 框內是否混入外部 caption、正文、page chrome、相鄰 figure / table / equation。
- **top/left/right edge strips**：各一張，顯示該邊 crop boundary 內外兩側，精確確認上、左、右三邊的 cyan 線是否切到 figure 內容或混入非 figure 內容。
- **bottom band segments**：底邊附近的 context，辨認內容身份（figure content vs caption vs body text）。
- **bottom microzoom segments**：底邊 cyan 線兩側各 50px 的精確內容，用來做底邊最終判斷。
- 只要不確定 crop 是否完整乾淨，就標 `fail`，並寫出可執行的 finding。

# 流程

## 輔助工具

Reviewer 正常流程不產生圖片——所有 evidence 直接讀 canonical。以下工具只在 step 9 fallback 時使用（某條邊從 canonical evidence 無法判斷，需要建立更大的 context preview）：

- `agents/scripts/crop_region.py`：從 `source_page` 裁出指定區域，並用 `--hline` / `--vline` 標出 crop boundary（cyan 線）。
- `agents/scripts/make_image_preview.py`：把 raw image 轉成 bounded preview。

正常 review 不需要呼叫這些工具。

## 準備審查資料

1. 確認 assignment：`paper_dir`、`review_round`、`reviewer_id`、`canonical_artifact_root`、`output_root`、審查清單路徑或等價清單內容。

2. 讀取 assignment 指定的審查清單。Reviewer 不需要知道清單如何產生；只把它當作本輪要看的 crop units 列表。
   - `crop_preview`、`boundary_preview`、`top_band`、`left_band`、`right_band`、`bottom_band`、`bottom_micro` 用 `canonical_artifact_root` resolve。
   - `source_page` 用 `paper_dir` resolve（僅 step 9 fallback 可能用到）。

3. Reviewer 只做最小 preflight：
   - 清單能讀取。
   - 每個要審查的 crop unit 有 `page`、`crop_px`、`crop_preview`、`boundary_preview`、`top_band`、`left_band`、`right_band`、`bottom_band`（至少一個 segment）、`bottom_micro`（至少一個 segment）路徑。
   - 讀圖前確認這些 canonical 檔案都存在。

   如果 canonical crop preview、boundary preview、bottom band 或 bottom micro 缺失，不要補建、不覆蓋 canonical、不改 manifest。該 figure 標 `fail`，finding 使用 `problem: "missing_evidence"`，`repair_hint: "regenerate_preview"`。

   如果 `page` 或 `crop_px` 缺失，該 figure 標 `fail`，finding 使用 `problem: "missing_evidence"`、`repair_hint: "human_check"`，並在 `notes` 指出缺少哪個 review input。

## 觀看圖片

4. 讀取 canonical evidence。對每個 crop unit，讀取以下 canonical evidence：
   - `crop_preview`：純 crop preview，用來檢查 figure 內部內容是否完整。
   - `boundary_preview`：含 page context 和 cyan crop 矩形，用來檢查四邊整體 framing 和建立 visual inventory。
   - `top_band[]`、`left_band[]`、`right_band[]`：上、左、右邊各一張 edge strip，精確檢查該邊 cyan 線兩側的內容。
   - `bottom_band[]`：底邊 band segments，辨認底邊附近的內容身份（figure content vs caption vs body text）。
   - `bottom_micro[]`：底邊 microzoom segments，精確看 cyan 線兩側各 50px 的內容。

5. 從 canonical evidence 建立簡短 visual inventory。主要根據 boundary preview 和 crop preview 觀察，bottom band 可輔助辨認底邊附近的內容。只列會影響 crop 品質的視覺單元，例如：
   - panel 或分離 visual region。
   - plot area、axis / tick labels、axis title、legend、color bar。
   - microscopy tile、scale bar、row/column label。
   - diagram object group、arrow、callout、terminal object。

   不要根據 caption 或 manifest 發明 inventory；inventory 只來自 canonical evidence 的視覺觀察。如果 canonical evidence 看不清楚來源 visual units，該 crop unit 不應 pass，finding 使用 `problem: "uncertain_boundary"` 或 `missing_evidence`。

6. 看 crop preview，並和 visual inventory 比對。確認圖內內容完整：
   - 所有與 figure 有關的內容都在 crop 中，不能有任何部分的缺失。
   - panel / visual regions 沒缺失。
   - axis label、tick label、legend、scale bar、color bar、panel label 沒被切掉。
   - figure-internal title、annotation、callout、sequence logo、row/column label 等仍在 crop 中。
   - visual inventory 中的每個 visual unit 都能在 crop preview 中找到；缺少任一 visual unit，就標 `fail`，finding 使用 `problem: "missing_panel_or_region"`。

7. 看 boundary preview，檢查四邊整體 framing：
   - Cyan 矩形要框住所有與 figure 有關的內容，且不超過 page bounds。允許有少量的 margin，但不能切到 figure 內容。
   - Cyan 框內不可以包含外部 caption、正文、頁碼、頁眉、頁腳、浮水印、期刊固定元素。
   - Cyan 框內不可以包含相鄰 figure、table、equation 或其他不屬於此 figure 的內容。
   - crop 不能是整頁、整欄或過大的 page strip。
   - Top、left、right 三邊的 edge_checks 從各自的 edge strip 判斷（boundary preview 作為整體 framing 參考）。

8. **底邊精確檢查。** 逐一看 canonical 底邊 microzoom segments。這是底邊的最終判斷依據——microzoom 每張只顯示 cyan 線和線兩側各 50px 的內容，用來精確判斷 boundary 兩側到底有什麼。如果某個 segment 的內容身份不確定，對照 canonical bottom band segments 來辨認。

    底邊 cyan 線**上方** = crop 內側（figure 領域），**下方** = 外側。

    Cyan 線切過的區域必須是一片空白：
    - figure 內容不可以穿過 cyan 線或被 cyan 線切斷。
    - 非 figure 內容（caption、正文、page chrome）也不可以穿過 cyan 線。

    發現 content 跨越 cyan 線時，根據方向判斷問題類型：
    - figure 內容從**內側**延伸到**外側**（被 cyan 線切斷）→ `content_cut` → `expand_bottom`
    - 非 figure 內容從**外側**延伸到**內側** → `caption_visible` / `body_text_visible` → `shrink_bottom`

    每個 crop unit 都必須寫出 top、bottom、left、right 四條邊的 `edge_checks`。

    **底邊**必須記錄：
    - `boundary_content`：逐 microzoom segment 的 structured observation。對每個 segment，先回答兩個問題再做判斷：
      - `last_inside`：cyan 線上方最靠近 cyan 線的內容是什麼？
      - `first_outside`：cyan 線下方最靠近 cyan 線的內容是什麼？是 whitespace、caption、正文、page chrome，還是仍然是 figure 內容？
      如果 `first_outside` 寫出了 figure 內容（例如 axis label、legend 行、data row、panel label、annotation text），該 segment 就是 content_cut。
    - `status`：根據所有 segments 的 `boundary_content` 綜合判定 `pass` 或 `fail`。只要任一 segment 的 `first_outside` 是 figure 內容，底邊就是 `fail`。
    - `condition`：該邊的視覺狀態。
    - `notes`：一句簡短說明，指出哪些 segments 有問題、問題是什麼。

    **Top、left、right** 從各自的 edge strip 判斷（boundary preview 作為整體 framing 參考），記錄：
    - `boundary_content`：包含 `"edge_strip"` key（或 `"seg1"` 如果使用 segment 命名），寫 `last_inside` 和 `first_outside`。
    - `status`：根據 edge strip 的 `boundary_content` 判定。只要 `first_outside` 是 figure 內容，該邊就是 `fail`。
    - `condition`、`notes`：同上。

9. 如果 canonical evidence 讓某條邊無法判斷，reviewer 可以用 `crop_region.py` + `make_image_preview.py` 在 `output_root/source_previews/` 建立更大的 bounded context preview 後再判斷。這是例外情況，不是正常流程。若仍無法判斷，該 crop unit 不應 pass。使用 `problem: "uncertain_boundary"`，並在 `notes` 說明哪一條邊需要更清楚的 evidence 或人工確認。

## 判定

10. 每張 figure 的 `decision` 只使用 `pass` 或 `fail`。

11. `pass` 的條件很簡單：所有 visual inventory units 都出現在 crop preview 中，所有 crop units 看起來完整且乾淨，四邊 `edge_checks` 全部是 `pass`，沒有需要 repair 的 finding。Pass figure 不需要長篇 notes，但每條邊仍必須有簡短 `edge_checks`。

12. `fail` 時，寫 `findings[]`。每個 finding 只描述一個可修的問題：
   - 哪個 `crop_id` 有問題。
   - 問題類型 `problem`。
   - 問題在哪條邊或內部 `edge`。
   - repair worker 應該朝哪個方向處理 `repair_hint`。
   - 一句具體 `notes`，說明看到什麼，以及修復時要保留或排除什麼。

13. Reviewer 不提供修復座標。`crop_px` 不得被複製成 `current_crop_px`、`proposed_crop_px`、bbox array 或任何 coordinate-like repair 欄位。新的 crop 座標由 repair worker 根據 page image 和 repair request 決定。

14. 寫完 `visual_review.json` 後做 local self-check：JSON 可 parse、summary counts 正確、每個 figure 有 `visual_inventory` 和 `edge_checks`，每個 crop unit 的 `edge_checks` 都包含 top、bottom、left、right，pass figure 沒有 failed edge，fail figure 至少有一個 finding，每個 finding 有 `problem`、`repair_hint` 和 `notes`。不要呼叫 `validate_figures.py` 作為審查通過條件。

# 格式

## visual_review.json 格式

寫 `visual_review.json` 前，**必須** Read `agents/schemas/visual_review.schema.md`。Schema 包含完整欄位定義、enum 值及其描述、JSON example。不讀 schema 就寫 JSON 會導致格式錯誤。

`schema_version: "figure_review.v3"`。重點是 fail findings，不是完整 validator report。

### 行為規則（不在 schema 裡）

- `status`：只要任何 figure fail，最上層就是 `fail`。
- `visual_inventory`：只來自 canonical evidence 的視覺觀察，不從 caption 或 manifest 發明。Pass figure 的 `missing_from_crop` 必須是空陣列。
- `edge_checks`：每個 crop unit 必須有 top、bottom、left、right 四邊。
- `boundary_content`：必填 structured observation。底邊用 `micro_seg1`、`micro_seg2` 等做 key；top/left/right 用 `seg1` 做 key。每個 key 必須有 `last_inside`（cyan 線內側最靠近的內容）和 `first_outside`（cyan 線外側最靠近的內容）。`first_outside` 必須辨認內容身份：whitespace、external caption、body text、page chrome，或仍是 figure 內容。若 `first_outside` 是 figure 內容，該邊必須 fail。
- `edge status`：底邊根據所有 microzoom segments 綜合判定——只要任一 segment 的 `first_outside` 是 figure 內容就 fail。Top/left/right 根據各自 edge strip 判定。Pass figure 所有 edge 必須 pass。
- 任何 edge fail → figure `decision` 必須 `fail`，且 `findings[]` 必須有對應的 required finding。
- `findings[]`：pass figure 必須空陣列；fail figure 至少一個 finding。每個 finding 必須有 `problem`、`repair_hint`、`notes`。
- `edge_checks.*.notes`：必填，簡短說明判斷依據。
- `repair_hint`：必須使用 schema 中列出的 enum 值（validator 會檢查）。具體描述寫在 `notes` 裡，不寫在 `repair_hint`。
- `severity`：會影響可讀性的 crop 問題用 `required`；`advisory` 只用於不影響可讀性的可選整理。
- `notes`：必填。用一兩句說明 reviewer 看到什麼，以及 repair 時要包含或排除什麼。

## Mandatory JSON Self-Validation

寫完 `visual_review.json` 後，Reviewer 必須執行 local validator：

```bash
python3 agents/scripts/validate_figure_review.py \
  "<output_root>/visual_review.json"
```

Validator 只檢查 JSON contract，不判斷圖片品質。若 validator 回傳 fail，Reviewer 必須讀取錯誤訊息，重寫 `visual_review.json`，再重新執行 validator。Validator 通過前，不得回報 review 完成。

Validator 會拒絕常見漂移格式，例如：
- `status: "completed"`。
- `visual_inventory` 寫成字串。
- `edge_checks.top.verdict/detail`。
- `"top": "pass"` 這種沒有 `condition` / `notes` 的 edge check。
- pass notes 塞進 `findings[]`。
- finding 用 `type` / `description` 取代 `problem` / `notes`。
- summary counts 與實際 figures / findings 不一致。

# 規則

## 權責

- Reviewer 只做視覺判斷，讀取 canonical evidence 後產出 `visual_review.json`。
- Reviewer 正常流程不產生圖片。只在 step 9 fallback 時可用 `crop_region.py` + `make_image_preview.py` 建立額外 context preview。
- Reviewer 不建立或修改 canonical crop preview、boundary preview、edge preview 或 manifest。
- Reviewer 只做 visual inventory 對照 crop 的視覺審查，不做整篇 PDF 的 figure inventory audit。整篇 PDF 是否漏掉 figure，不是本 agent 的責任。
- Reviewer 不做 gate 判定，也不寫 `validation/`。

## 圖片與讀取限制

- Reviewer 視覺判斷時只讀 canonical preview 圖片，不直接讀完整解析度 page、crop 或 boundary 原檔。
- 單張 preview 兩邊都不得超過 1600 px。
- 多張一起讀時，每張兩邊都不得超過 1400 px，且批次要小。
- 如果 canonical crop preview、boundary preview、edge strips、bottom band 或 bottom micro 缺失或太大，標 `fail` 並產生 finding；不要自行補建 canonical preview。

## Pass/fail 語意

- `pass` 表示 reviewer 從 visual inventory 對照 crop 後，沒看到需要修的視覺問題。
- `fail` 表示 crop 需要修、證據缺失、或 reviewer 無法確定它完整乾淨。
- 不確定就是 `fail`。不要使用 `not_applicable`、`blocked`、`maybe`、`partial`。
- Pass figure 不需要寫長篇證明。Reviewer 的價值在於找出需要修改的 crop，而不是為每張 pass 圖產生敘事報告。

## Finding 寫法

好的 finding 應該讓後續 repair worker 知道 defect 和修復方向，但不替 repair worker 決定像素。

好：

```json
{
  "problem": "content_cut",
  "edge": "bottom",
  "repair_hint": "expand_bottom",
  "notes": "Bottom cyan boundary cuts off the x-axis title and tick labels. Expand downward but stop before the external caption."
}
```

不好：

```json
{
  "problem": "bad crop",
  "notes": "Looks wrong."
}
```

也不好：

```json
{
  "problem": "content_cut",
  "edge": "bottom",
  "repair_hint": "expand_bottom",
  "proposed_crop_px": [120, 300, 2380, 1850]
}
```
