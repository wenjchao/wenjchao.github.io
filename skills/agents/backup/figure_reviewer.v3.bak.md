# 目標

這是一份給 figure_reviewer agent 看的指引。

此流程使用場景與目標：
- 輸入：一個 paper directory、review round / reviewer assignment、`canonical_artifact_root`、已完成的 figure extraction 成果（schema 以 `figure_extractor.md` 定義的 `figure_extraction.v3` 為準），以及需要時可呼叫的 preview / crop helper。
- 讀取位置：
    - `shared/pages/`：完整解析度頁面圖片，這是審查來源版面的最高依據。
    - `shared/previews/`：頁面預覽圖片。
    - `lanes/figures/canonical/`：已合併的 figure extraction 成果（`figure_candidates.json`、`figure_index.json`、`figure_decisions.json`、`figures.json`，以及 crop PNG 和 extractor 產生的 preview）。
- 輸出位置：`<paper_dir>/lanes/figures/reviews/round_<N>/reviewer_<ID>/`
- 輸出：
    - `visual_review.json`：逐一記錄每張 figure 的視覺審查結果，包含來源證據、裁切證據、視覺清單、逐 crop unit 邊緣檢查、缺陷與修復請求。
    - `previews/`：reviewer 自行從頁面圖片建立的 source boundary preview（每個 crop_unit 一張，含 context margin + 紅色矩形）。所有 preview 檔名必須含 `_preview` 後綴。
- 第一階段不執行 parent canonical validator。Reviewer 可以做 local self-check，但 `visual_review.json` 才是本 agent 的正式輸出。

- 目標：獨立判斷每個 final crop 是否視覺完整且乾淨。完整表示 figure 的內容沒有被切掉；乾淨表示 crop 中沒有混入外部 caption、正文、page chrome 或相鄰內容。
- 邊界：
    - 此 agent 只做 visual review，不做裁切、不修改 extraction 成果、不修改來源 PDF。
    - 如果裁切有問題，標 `fail` 並提出修復請求；實際修復由 extractor 或 repair agent 執行。
    - reviewer 可以建立自己的審查用 preview，但不能覆蓋 extractor 產生的任何檔案。
    - 不要讓 extractor 提供的 preview 框住 reviewer 的判斷範圍；reviewer 必須從頁面圖片獨立建立自己的來源證據。

# 流程

## 輔助工具

Reviewer 需要建立來源證據時，只使用本 skill 內的 local helper：

- `agents/scripts/crop_region.py`：從 rendered page image 建立 reviewer 自己的 source boundary 圖片（crop + context margin + 紅色矩形）。支援多個 `--hline` / `--vline` 疊紅線（boundary 用 2 hline + 2 vline 畫矩形）。
- `agents/scripts/make_image_preview.py`：建立 reviewer 可讀取的受限尺寸 preview。

不要直接呼叫 `skills/_shared/scripts/...`。Reviewer 可以建立自己的 evidence previews，但不得覆蓋 extractor 或 canonical 目錄中的檔案。

## 工作流程

### 準備審查資料

1. 確認 reviewer assignment：本輪要審查的 figure 範圍、review round 和 reviewer id。若未指定 reviewer id，使用輸出目錄名稱（例如 `reviewer_01`）。

2. 讀取 `canonical_artifact_root` 下的 figure extraction artifacts：
   - `figure_candidates.json`
   - `figure_index.json`
   - `figure_decisions.json`
   - `figures.json`

   如果必要 artifact 缺失，不要自行補寫 extraction artifact；在 `visual_review.json` 中將受影響的 figure 標 `fail`，並在 `defects`、`notes` 和 `repair_request` 說明缺什麼。

3. 從 `figure_decisions.json` 和 `figures.json` 取得每張 figure 的 `figure_id`、`figure_label`、`crop_units[]`（`crop_id`、`page`、`crop_px`、`image_file`、`preview`、`boundary_preview`、`role`）、`caption_text`、`expected_panels`。`figure_label` 只從 extractor manifest 複製，用來幫助人類閱讀與對照；穩定識別仍以 `figure_id` 為準。

4. 建立本輪 reviewer preview 目錄，例如 `lanes/figures/reviews/round_00/reviewer_01/previews/`。Reviewer 自建的 evidence previews 都放在這裡，不覆蓋 extractor 或 canonical 目錄中的檔案。

### 建立來源證據

5. 對每個要審查的 crop unit，從 `shared/pages/page_N.png` 建立 reviewer 自己的 **source boundary 圖片** 與 preview，寫入 `previews/`：

   **Margin 公式**（與 extractor 一致，每邊獨立、clamp 到 page bounds）：

   ```text
   margin_top    = max(round(0.15 * (crop_y2 - crop_y1)), 250)
   margin_bottom = max(round(0.15 * (crop_y2 - crop_y1)), 250)
   margin_left   = max(round(0.15 * (crop_x2 - crop_x1)), 250)
   margin_right  = max(round(0.15 * (crop_x2 - crop_x1)), 250)

   ctx_x1 = max(0,        crop_x1 - margin_left)
   ctx_y1 = max(0,        crop_y1 - margin_top)
   ctx_x2 = min(page_w,   crop_x2 + margin_right)
   ctx_y2 = min(page_h,   crop_y2 + margin_bottom)
   ```

   **呼叫**：

   ```bash
   python3 agents/scripts/crop_region.py \
     shared/pages/page_N.png \
     ctx_x1 ctx_y1 ctx_x2 ctx_y2 \
     <reviewer_dir>/previews/<figure_id>_source_boundary.png \
     --padding 0 \
     --hline crop_y1 --hline crop_y2 \
     --vline crop_x1 --vline crop_x2

   python3 agents/scripts/make_image_preview.py \
     <reviewer_dir>/previews/<figure_id>_source_boundary.png \
     <reviewer_dir>/previews/<figure_id>_source_boundary_preview.png \
     --max-dim 1568
   ```

   即使 extractor 已提供 boundary preview，也必須建立 reviewer 自己的 source boundary preview。Reviewer 不能只用 extractor 的 framing 判斷 — 必須獨立從頁面圖片重建。

6. 讀取 reviewer 自建的 source boundary preview。如果 preview 中紅矩形邊上的某個元素無法判斷是否延伸到 crop 外（例如 stylized icon、小字），建立局部 zoom-in（仍符合讀圖限制）後再判斷，不要勉強做模糊判斷。

### 建立視覺清單

7. 判斷 crop 之前，先從來源頁面證據建立 `expected_visual_units`——依圖的類型，以適當粒度列出來源中可見的視覺元件：
   - 圖表型：plot area、軸標題、tick labels、legend、color bar、annotation。
   - 示意圖或化學流程圖：object groups、arrows、callouts、molecule groups、condition labels、terminal objects。
   - 顯微圖或矩陣型：tiles/cells、channel labels、row/column labels、scale bars、figure-internal legends。
   - 簡單單圖：至少記錄一個明確單元，例如 `main_plot`、`main_diagram` 或 `main_image_panel`。

   清單必須從來源頁面視圖建立，不從 caption 或 crop 建立。`expected_panels` 為空時更必須做視覺清單。

8. 將 `figure_decisions.json` 中的 `expected_panels` 複製到審查項目中。

### 讀取裁切證據

9. 讀取每個 crop unit 的 **final crop preview** (`crop_units[].preview`)。這張 preview 用來檢查 figure **內部細節**（座標軸、tick label、panel label、color bar 等）。若 `figures.json` 指向的 canonical preview 不存在，不要從 final crop 圖片補建 reviewer preview；該 figure 直接標 `fail`，在 `defects` 和 `repair_request` 寫明 `missing canonical preview`。若 final crop 圖片本身不存在，該 figure 也直接標 `fail`。

10. 讀取每個 crop unit 的 **canonical boundary preview** (`crop_units[].boundary_preview`)。這張 preview 用來檢查 **邊界裁切**（紅色矩形的四條邊是否切到 figure 內容、紅矩形外側是否混入正文 / caption / page chrome）。若缺少 canonical boundary preview，不要從 final crop 圖片補建 reviewer 自己的版本當 canonical 用；該 figure 直接標 `fail`，在 `defects` 和 `repair_request` 寫明 `missing canonical boundary preview`。不要只看 final crop preview 就決定 pass。

11. 為每個被審查的 final crop PNG 計算 SHA-256，寫入 `crop_hashes`。如果 crop 之後被修改但審查未更新，validator 會用 hash 偵測過期審查。

12. 從 final crop preview 記錄 `observed_visual_units` 和 `observed_panels`。如果 canonical final crop preview 缺失，這一步不做視覺補判，該 figure 已經因缺 evidence fail。通過審查要求：
    - `observed_visual_units` 的 `unit_id` 與 `expected_visual_units` 一致。
    - `observed_panels` 與 `expected_panels` 完全一致。如果擷取者的 `expected_panels` 明顯錯誤，將審查判定為 `fail`，要求修正。

### 視覺審查

13. 比對來源證據與裁切證據。逐一確認：
    - 來源中可見的所有 panels 都出現在 crop 中
    - 來源中所有重要 visual units 都出現在 crop 中，即使沒有 panel label
    - panel labels、axes、tick labels、legends、scale bars、insets、color bars、row/column labels 和 plot boundaries 都完整
    - crop 排除外部 caption 和圖外 legend
    - crop 排除周圍正文
    - crop 排除頁碼、頁眉、頁腳、浮水印、期刊固定元素和其他 page chrome
    - crop 不包含相鄰 figure、table、equation 或無關頁面內容
    - crop 不是只把 figure 包在裡面的大頁面條帶

14. 對每個 crop unit，**在 boundary preview 上逐一檢查上、下、左、右四條紅線邊**。同時讀 canonical boundary preview（extractor 產生）與 reviewer source boundary preview（自建），兩張都顯示同一塊 page context + 紅色矩形，可以對照確認 framing 一致。每條邊獨立給 verdict，但 evidence 都指向同一張 boundary preview，不需要分四張 edge 條。

    **核心規則：不可以有任何圖片物體跨越紅線。** 沿著每條紅線檢查，只要有任何 figure 內容（文字、線條、圖形、箭頭、色塊等）穿過紅線，該邊就是 fail。

    通過的 condition 只有三種：
    - `clean_margin`：紅線外側是空白（whitespace），與最近的 figure unit 之間沒有其他 figure 內容。
    - `figure_border_complete`：紅線與完整的 figure-internal border、frame 或 panel boundary 一致（沒有 figure 內容跨過紅線）。
    - `intentional_full_bleed_edge`：紅線壓在 page 邊（boundary preview 該側無 margin），來源圖有意延伸到頁邊且沒有內容被切掉。

    其他任何狀態都是 `fail`，包括：`content_cut`（figure 內容跨過紅線、被切掉）、`content_touches_edge_uncertain`、`caption_visible`、`body_text_visible`、`page_chrome_visible`、`adjacent_content_visible`、`unknown`。

15. 對圖表型圖片（折線圖、長條圖、散點圖、熱圖、Manhattan plot、帶座標軸的示意圖），底邊與側邊風險最高。必須明確確認 x 軸刻度與標題、y 軸標籤、legend、color bar 和 plot boundary 完整。

### 整體判定

16. 綜合所有檢查，為每張 figure 寫出 `decision`：
    - 全部 `checks` 和所有 crop units 的 `edge_checks` 都 `pass` → `decision: "pass"`。
    - 任何一項 `fail` → `decision: "fail"`，並填寫 `defects` 和 `repair_request`。

17. 判定為 `pass` 的 figure，`notes` 必須非空，說明：觀察到的 panels/visual units、各 crop unit 四邊為何乾淨、嵌入文字為什麼屬於 figure-internal 而非 page chrome。不得包含不確定語氣（「也許」「可能」「看起來」「不清楚」「略微切到」「盡力」等）。不得提到任何已知缺陷。

18. 判定為 `fail` 的 figure：
    - 填寫具體 `defects`，例如「底部 x 軸標籤被切掉」或「右下角可見外部圖說文字」。
    - 填寫 `repair_request`，使用方向與約束描述，不提供座標：
      - `action` 優先使用：`recrop`、`manifest_correction`、`provide_clearer_source_evidence`、`regenerate_missing_preview`；無法歸類時可自訂 snake_case action。
      - `direction` 使用：`expand_top`/`bottom`/`left`/`right`、`shrink_top`/`bottom`/`left`/`right`。如果 action 是 `regenerate_missing_preview`，`direction` 使用空陣列。

    不要因為 crop「大致可以」就標 `pass`。不確定就是 `fail`。

### 寫出 visual_review.json 與 local self-check

19. 寫出 `visual_review.json`。只要任何 figure 的 `decision` 是 `fail`，最上層 `status` 就是 `fail`。不要只根據 manifests 寫 `visual_review.json`——如果引用的 preview 缺失，該 figure 標 `fail`。

20. 寫完 `visual_review.json` 後，做 reviewer local self-check：JSON parse、summary counts 正確、每個 crop unit 都有 source evidence 與 hash；crop evidence 和 edge checks 必須存在，除非該 crop unit 已列入 `missing_canonical_artifacts[]` 並產生 `regenerate_missing_preview` repair request。不要呼叫舊的 shared `validate_figures.py` 作為第一階段 gate。

21. 回報本輪讀過的來源與裁切 previews、通過/失敗的 figures、主要 defects、`visual_review.json` 路徑，以及 local self-check 結果。

# 格式

## JSON 命名與 enum

### Artifact root 相對路徑

- `canonical_artifact_root` 是 `<paper_dir>/lanes/figures/canonical/`。
- 從 extraction manifests 讀到的 `image_file`、`preview`、`boundary_preview` 都是 artifact root 相對路徑。Reviewer 讀檔時用 `canonical_artifact_root` resolve，寫入 review report 時仍保留同一個相對路徑字串。
- canonical evidence 存在時，`crop_previews_read.crop_units[].crop_preview` 與 `boundary_preview` 應使用 canonical manifest 中同一組 artifact root 相對路徑，例如 `previews/Figure_1_preview.png`、`previews/Figure_1_boundary_preview.png`。
- Reviewer 自己建立的 source boundary previews 放在 review output 目錄，不在 canonical artifact root 裡，因此記錄為 paper-dir-relative path，例如 `lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_boundary_preview.png`。
- 不要把 `lanes/figures/canonical/` 或絕對路徑加進 canonical evidence 欄位。

正確寫法：

```json
{
  "crop_preview": "previews/Figure_1_preview.png",
  "canonical_boundary_preview": "previews/Figure_1_boundary_preview.png",
  "source_boundary_preview": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_boundary_preview.png"
}
```

### 基本欄位

- `visual_review.json` 使用 `schema_version: "figure_review.v3"`。v3 schema（boundary view 版本）以本文件內的 JSON example 與規則為準。
- 最上層包含 `schema_version`、`review_round`、`reviewer_id`、`scope`、`status`、`figures`、`summary`。
- `review_round` 必須和所在目錄 `round_<N>` 一致；`reviewer_id` 必須和所在目錄 `reviewer_<ID>` 一致。
- `visual_review.json.status` 只使用 `pass` 或 `fail`。只要任何 figure 的 `decision` 是 `fail`，最上層 `status` 就必須是 `fail`。
- 每個 figure 的 `decision` 只使用 `pass` 或 `fail`，不使用 `blocked`。如果 artifact、crop image、preview 或 source evidence 缺失，該 figure 標 `fail`，缺失原因寫在 `defects`、`notes`、`missing_canonical_artifacts` 和 `repair_request`。
- `figure_id` 是穩定識別欄位。`figure_label` 只從 extractor manifest 複製，用來讓人類快速對照圖號；如果 `figure_label` 和來源圖說或 manifest 明顯衝突，標 `fail` 並提出 `manifest_correction`。
- `checks`、`edge_checks` 中每條邊的 `status`、`decision` 只使用 `pass` 或 `fail`。不要使用 `not_applicable`；沒有某種元素時，只要沒有缺失，該檢查就是 `pass`。
- `expected_visual_units` 與 `observed_visual_units` 必須是非空陣列。通過時，`observed_visual_units` 的 `unit_id` 必須能對應 `expected_visual_units`。
- `observed_visual_units[].status` 使用 `present`、`incomplete` 或 `missing`。通過時，每個 expected visual unit 都必須有對應的 observed unit，且 status 為 `present`。
- `crop_hashes` 記錄每個 reviewed crop image 的 SHA-256，格式為 `sha256:<hash>`。key 使用 `crop_id`。
- `missing_canonical_artifacts` 記錄 canonical evidence 缺失；沒有缺失時使用空陣列。每個 entry 至少包含 `crop_id`、`kind`、`expected_path`。`kind` 使用 `crop_preview`（指 `crop_units[].preview`）或 `boundary_preview`（指 `crop_units[].boundary_preview`）。
- `summary.figure_count`、`summary.pass_count`、`summary.fail_count` 必須與實際 `figures` 列表一致。

### checks

`checks` 的值只使用 `pass` 或 `fail`。預設包含以下 key；如果遇到未涵蓋的審查項目，可以新增簡短 snake_case check name。新增 check 也只能填 `pass` 或 `fail`，並應在 `notes` 或 `defects` 中說明：

- `all_panels_present`
- `visual_units_match`
- `labels_axes_legends_complete`
- `external_caption_excluded`
- `body_text_excluded`
- `page_chrome_excluded`
- `no_adjacent_content`
- `not_page_strip`

### edge_checks

canonical boundary preview 存在時，每個 `crop_units[]` 都必須各自有四邊 edge_checks。結構使用 `crop_units` 陣列，與 extractor 的 `crop_units[]` 一致，方便 validator 檢查每個 crop unit 是否都有四邊。若 canonical boundary preview 缺失，該 crop unit 改列在 `missing_canonical_artifacts[]`，不得假造 edge_checks。

- `edge_checks.crop_units[].crop_id` 必須對應 `figures.json.figures[].crop_units[].crop_id`。
- `edge_checks.crop_units[].boundary_evidence.source` 指 reviewer 自建的 source boundary preview（paper-dir-relative）。
- `edge_checks.crop_units[].boundary_evidence.crop` 指 canonical 的 boundary preview（artifact-root-relative，等同 canonical manifest 中的 `crop_units[].boundary_preview`）。
- `edge_checks.crop_units[].edges` 必須包含 `top`、`bottom`、`left`、`right`，每邊各自獨立 verdict。
- `edge_checks.crop_units[].edges.*.status` 只使用 `pass` 或 `fail`。

每條邊包含 `status`、`condition`、`notes`。Evidence 由 crop_unit 層的 `boundary_evidence` 提供（一張 source boundary preview + 一張 canonical boundary preview 承擔該 crop_unit 全部四邊的 evidence），不需要 per-edge source_evidence / crop_evidence 欄位。

`condition` 的通過值：`clean_margin`、`figure_border_complete`、`intentional_full_bleed_edge`。

`condition` 的失敗值：`content_cut`、`content_touches_edge_uncertain`、`caption_visible`、`body_text_visible`、`page_chrome_visible`、`adjacent_content_visible`、`unknown`。

### evidence read

- `source_boundary_previews_read.crop_units[]`：記錄每個 crop unit 的 reviewer-built source boundary preview。
- `crop_previews_read.crop_units[]`：記錄每個 crop unit 實際讀過的 canonical final crop preview 與 canonical boundary preview。不要把缺失的 canonical preview 假裝成已讀。
- 每個 `figures.json` 中的 `crop_units[].crop_id`，都必須在 `source_boundary_previews_read.crop_units[]` 和 `crop_hashes` 中各出現一次。若 canonical final crop preview 與 boundary preview 完整存在，也必須在 `crop_previews_read.crop_units[]` 和 `edge_checks.crop_units[]` 中出現一次；若 canonical evidence 缺失，必須改列在 `missing_canonical_artifacts[]`，並讓該 figure `decision: "fail"`。
- `edge_checks.crop_units[].boundary_evidence.source` 必須使用和 `source_boundary_previews_read` 中相同的 path；`edge_checks.crop_units[].boundary_evidence.crop` 必須使用和 `crop_previews_read.crop_units[].boundary_preview` 中相同的 path。若 boundary preview 缺失，不要填假 path；用 `missing_canonical_artifacts[]` 記錄。

### repair_request

- 通過的 figure：`repair_request` 設為 `null`。
- 未通過的 figure：`repair_request` 必須存在，並以 extractor / repair agent 能執行的方式描述。
- `action` 優先使用：`recrop`、`manifest_correction`、`provide_clearer_source_evidence`、`regenerate_missing_preview`；無法歸類時可自訂 snake_case action，並在 `constraint` 說明原因。
- `direction` 使用方向，例如 `expand_bottom`、`shrink_left`。如果 action 是 `regenerate_missing_preview`，`direction` 使用空陣列。
- 如果 canonical crop preview 或 boundary preview 缺失，`repair_request.action` 使用 `regenerate_missing_preview`，`defects` 必須包含 `missing canonical preview` 或 `missing canonical boundary preview`，`constraint` 指出要從 canonical crop PNG 或 page image 重新建立缺失的 canonical preview / boundary preview。
- 這類 request 必須把同一組 `missing_canonical_artifacts[]` 複製到 `repair_request.missing_canonical_artifacts[]`，讓 parent 和 repair worker 不需要從 notes 解析缺哪些檔案。
- 不要在 `repair_request` 中寫 `current_crop_px`、`proposed_crop_px`、bbox array 或座標鍵；像素由 extractor / repair agent 根據來源頁面決定。

## visual_review.json example

> 以下 example 展示一個 pass figure（Figure_1，單一 crop unit）與一個 fail figure（Figure_2，兩個 crop units）。`source_boundary_previews_read`、`crop_previews_read`、`edge_checks` 都使用 `crop_units[]` 結構，每個 crop unit 對應一張 source boundary preview 和一張 canonical boundary preview，四邊 verdicts 共用這對 evidence。

```json
{
  "schema_version": "figure_review.v3",
  "review_round": "round_00",
  "reviewer_id": "reviewer_01",
  "scope": {
    "figure_ids": ["Figure_1", "Figure_2"],
    "notes": []
  },
  "status": "fail",
  "figures": [
    {
      "figure_id": "Figure_1",
      "figure_label": "Fig. 1",
      "crop_hashes": {
        "Figure_1": "sha256:a1b2c3d4e5f6..."
      },
      "missing_canonical_artifacts": [],
      "expected_panels": ["A", "B", "C"],
      "observed_panels": ["A", "B", "C"],
      "expected_visual_units": [
        {"unit_id": "panel_A_plot", "type": "bar_chart", "location": "top-left", "description": "Panel A bar chart with y-axis label and legend"},
        {"unit_id": "panel_B_plot", "type": "line_plot", "location": "top-right", "description": "Panel B line plot with error bars"},
        {"unit_id": "panel_C_heatmap", "type": "heatmap", "location": "bottom", "description": "Panel C heatmap with color bar and row/column labels"}
      ],
      "observed_visual_units": [
        {"unit_id": "panel_A_plot", "status": "present", "notes": "Bar chart, y-axis label, and legend visible."},
        {"unit_id": "panel_B_plot", "status": "present", "notes": "Line plot with error bars visible."},
        {"unit_id": "panel_C_heatmap", "status": "present", "notes": "Heatmap, color bar, and row/column labels visible."}
      ],
      "source_boundary_previews_read": {
        "crop_units": [
          {
            "crop_id": "Figure_1",
            "boundary_preview": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_boundary_preview.png"
          }
        ]
      },
      "crop_previews_read": {
        "crop_units": [
          {
            "crop_id": "Figure_1",
            "crop_preview": "previews/Figure_1_preview.png",
            "boundary_preview": "previews/Figure_1_boundary_preview.png"
          }
        ]
      },
      "checks": {
        "all_panels_present": "pass",
        "visual_units_match": "pass",
        "labels_axes_legends_complete": "pass",
        "external_caption_excluded": "pass",
        "body_text_excluded": "pass",
        "page_chrome_excluded": "pass",
        "no_adjacent_content": "pass",
        "not_page_strip": "pass"
      },
      "edge_checks": {
        "crop_units": [
          {
            "crop_id": "Figure_1",
            "boundary_evidence": {
              "source": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_boundary_preview.png",
              "crop": "previews/Figure_1_boundary_preview.png"
            },
            "edges": {
              "top":    {"status": "pass", "condition": "clean_margin", "notes": "Top red line has whitespace above visual panels."},
              "bottom": {"status": "pass", "condition": "clean_margin", "notes": "Bottom red line below axis labels; external caption outside red rectangle."},
              "left":   {"status": "pass", "condition": "clean_margin", "notes": "Left y-axis labels complete inside red rectangle."},
              "right":  {"status": "pass", "condition": "figure_border_complete", "notes": "Right red line follows panel C boundary."}
            }
          }
        ]
      },
      "defects": [],
      "decision": "pass",
      "repair_request": null,
      "notes": "Panels A-C and all expected visual units present. Single crop unit; boundary preview shows red rectangle with all four edges clean. No external caption, page chrome, or adjacent content visible."
    },
    {
      "figure_id": "Figure_2",
      "figure_label": "Fig. 2",
      "crop_hashes": {
        "Figure_2_part_1": "sha256:d4e5f6a7b8c9...",
        "Figure_2_part_2": "sha256:e5f6a7b8c9d0..."
      },
      "missing_canonical_artifacts": [],
      "expected_panels": ["A", "B"],
      "observed_panels": ["A", "B"],
      "expected_visual_units": [
        {"unit_id": "panel_A_scatter", "type": "scatter_plot", "location": "left", "description": "Panel A scatter plot with x/y axes and trend line"},
        {"unit_id": "panel_B_scatter", "type": "scatter_plot", "location": "right", "description": "Panel B scatter plot with x/y axes and color-coded points"}
      ],
      "observed_visual_units": [
        {"unit_id": "panel_A_scatter", "status": "present", "notes": "Panel A plot is complete."},
        {"unit_id": "panel_B_scatter", "status": "incomplete", "notes": "Panel B bottom x-axis title cut off."}
      ],
      "source_boundary_previews_read": {
        "crop_units": [
          {
            "crop_id": "Figure_2_part_1",
            "boundary_preview": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_1_source_boundary_preview.png"
          },
          {
            "crop_id": "Figure_2_part_2",
            "boundary_preview": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_2_source_boundary_preview.png"
          }
        ]
      },
      "crop_previews_read": {
        "crop_units": [
          {
            "crop_id": "Figure_2_part_1",
            "crop_preview": "previews/Figure_2_part_1_preview.png",
            "boundary_preview": "previews/Figure_2_part_1_boundary_preview.png"
          },
          {
            "crop_id": "Figure_2_part_2",
            "crop_preview": "previews/Figure_2_part_2_preview.png",
            "boundary_preview": "previews/Figure_2_part_2_boundary_preview.png"
          }
        ]
      },
      "checks": {
        "all_panels_present": "pass",
        "visual_units_match": "fail",
        "labels_axes_legends_complete": "fail",
        "external_caption_excluded": "pass",
        "body_text_excluded": "pass",
        "page_chrome_excluded": "pass",
        "no_adjacent_content": "pass",
        "not_page_strip": "pass"
      },
      "edge_checks": {
        "crop_units": [
          {
            "crop_id": "Figure_2_part_1",
            "boundary_evidence": {
              "source": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_1_source_boundary_preview.png",
              "crop": "previews/Figure_2_part_1_boundary_preview.png"
            },
            "edges": {
              "top":    {"status": "pass", "condition": "clean_margin", "notes": "Top red line clean."},
              "bottom": {"status": "pass", "condition": "clean_margin", "notes": "Bottom red line below complete x-axis title."},
              "left":   {"status": "pass", "condition": "clean_margin", "notes": "Left red line clean."},
              "right":  {"status": "pass", "condition": "clean_margin", "notes": "Right red line clean."}
            }
          },
          {
            "crop_id": "Figure_2_part_2",
            "boundary_evidence": {
              "source": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_2_source_boundary_preview.png",
              "crop": "previews/Figure_2_part_2_boundary_preview.png"
            },
            "edges": {
              "top":    {"status": "pass", "condition": "clean_margin", "notes": "Top red line clean."},
              "bottom": {"status": "fail", "condition": "content_cut", "notes": "Boundary preview shows panel B x-axis title sitting below the bottom red line — figure content is cut."},
              "left":   {"status": "pass", "condition": "clean_margin", "notes": "Left red line clean."},
              "right":  {"status": "pass", "condition": "clean_margin", "notes": "Right red line clean."}
            }
          }
        ]
      },
      "defects": ["Panel B bottom x-axis title 'Concentration (μM)' is cut off in Figure_2_part_2.png"],
      "decision": "fail",
      "repair_request": {
        "action": "recrop",
        "direction": ["expand_bottom"],
        "constraint": "Include missing panel B x-axis title; stop before external caption."
      },
      "notes": "Fig. 2 fails because Figure_2_part_2 boundary preview shows the bottom red line cutting through panel B x-axis title."
    }
  ],
  "summary": {
    "figure_count": 2,
    "pass_count": 1,
    "fail_count": 1
  }
}
```

# 圖片檔案

Reviewer 使用兩類圖片：extractor 產生的 canonical evidence，以及 reviewer 自己從頁面圖片建立的 source evidence。所有給 reviewer 讀的圖片都必須是 preview，檔名含 `_preview`，並符合讀圖尺寸限制。

- 頁面圖片：`shared/pages/page_3.png`
  - 角色：來源真相。Reviewer 不直接讀完整解析度頁面圖片，而是從它建立 bounded preview。
- Reviewer source boundary preview：`lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_boundary_preview.png`
  - 角色：從頁面圖片裁出 crop 加上四邊 context margin 的區域，並用紅色矩形（4 條線）標出 crop_px。reviewer 自建，用來獨立判斷紅矩形是否切掉 figure 內容或混入非 figure 內容。一張 preview 承擔該 crop_unit 全部四邊的審查 evidence。
- Canonical final crop preview：`previews/Figure_1_preview.png`
  - 角色：extractor 產生的 final crop preview。用來檢查 figure 內部細節（座標軸、tick label、panel label、color bar 等），保留高解析度，不含 context margin。
- Canonical boundary preview：`previews/Figure_1_boundary_preview.png`
  - 角色：extractor 產生的 boundary preview，與 reviewer source boundary preview 同 framing（crop + context margin + 紅色矩形），用來比對 reviewer 的獨立 framing 是否一致。

# 規則

## 權責

- `figure_reviewer` 只做 independent visual review。
- 不建立新的 final crop。不修改 extraction manifests。不修改 final crop 圖片。不修改來源 PDF。
- 可以建立 reviewer source evidence previews。
- 如果 crop 不合格，標 `fail` 並提出 repair request；不要直接修。
- helper 可以建立 reviewer source boundary preview、hash，也可以執行機械驗證；但 helper、validator、manifest 和 crop coordinate 都不能替 reviewer 判定 visual quality。`pass` 必須由 reviewer 讀過 source boundary preview、canonical final crop preview 和 canonical boundary preview 後判斷。

## 圖片與讀取限制

- reviewer 不得直接視覺讀取完整解析度頁面圖片、完整解析度 crop 圖片或完整解析度 boundary 圖片。
- reviewer 讀取單張圖片時，兩邊都不得超過 1600 px。
- reviewer 一次讀多張圖片時，每張兩邊都不得超過 1400 px，且批次要小。
- 若可用 evidence image 超過限制，先建立受限尺寸 preview 再讀取，並記錄路徑。
- 所有 reviewer 建立的 preview 都寫在本輪 review 輸出的 `previews/` 目錄，不覆蓋 extractor 產生的 preview。
- 如果 canonical final crop preview 或 boundary preview 缺失，reviewer 不補建、不覆蓋、不把 reviewer-local preview 當作 canonical evidence。該 figure 直接 `fail`，並用 `missing_canonical_artifacts[]` 和 `repair_request.action: "regenerate_missing_preview"` 交給 repair。

## 來源獨立性

- rendered page image 是 reviewer 的來源真相。
- extractor 提供的 boundary preview 可以參考，但不能取代 reviewer 從 rendered page image 獨立建立的 source boundary preview。
- 每個 `crop_units[]` 都必須有 reviewer 自建的 source boundary preview。framing 應與 extractor 的 boundary preview 一致（同樣的 margin 公式、同樣的紅色矩形）。
- 如果 source boundary preview 上紅矩形邊有元素無法判斷是否延伸到 crop 外（stylized icon、小字、軸刻度），建立局部 zoom-in（仍符合讀圖限制）後再決定。

## 視覺清單規則

- `expected_visual_units` 從 reviewer source evidence 建立，不從 caption 或 crop 建立。
- `observed_visual_units` 從 final crop evidence 建立。
- 通過時，`observed_visual_units` 的 `unit_id` 必須完整對應 `expected_visual_units`。
- `expected_panels` 為空時，仍必須建立 `expected_visual_units`；不能因為沒有 panel label 就不做視覺清單。
- 如果 `figure_decisions.json.expected_panels` 和來源頁面實際可見 panels 不一致，該 figure 應標 `fail`，要求 manifest correction 或 recrop，不要默默放行。

## 邊緣檢查規則

- 每個 `crop_units[]` 都獨立做上、下、左、右四邊檢查，evidence 共用該 crop_unit 的兩張 boundary preview（一張 canonical、一張 reviewer source）。
- 同時看 canonical boundary preview 與 reviewer source boundary preview，並在 `edge_checks.crop_units[].boundary_evidence.{source, crop}` 記錄路徑。如果 canonical boundary preview 缺失，不做視覺補判，直接標缺失並要求 repair 重新建立 preview。
- 通過的邊只有三種 condition：`clean_margin`、`figure_border_complete`、`intentional_full_bleed_edge`。其他都是 `fail`。
- 圖表型圖片的底邊與側邊風險最高：必須確認 x 軸刻度與標題、y 軸標籤、legend、color bar 和 plot boundary 完整。
- 大幅寬圖可以接近整頁寬度，但不能是 lazy page strip；垂直方向仍應緊貼 figure，且不得混入正文、外部圖說或 page chrome。

## Pass/fail 語意

- `pass` 表示 reviewer 能用視覺證據說明 crop 完整且乾淨。
- `fail` 表示 crop 有缺陷、證據不足、仍不確定，或 reviewer 無法用視覺證據說明它完整且乾淨。
- 不確定就是 `fail`。不要因為 crop mostly okay、best effort、或缺陷看起來 minor 就標 `pass`。
- 如果 `notes` 中需要承認 clipping、uncertainty 或 unresolved condition，該 figure 必須是 `fail`。
- 不要使用 `not_applicable`。

## Stale review protection

- 每個 reviewed crop image 都必須計算 SHA-256，寫入 `crop_hashes`，格式為 `sha256:<hash>`。key 使用 `crop_id`。
- 如果 crop image 在 review 後被修改，舊 review 不再有效。
- 第二階段 validator 可以用 crop hash 偵測 stale review；第一階段 parent 只需要知道修復後必須重跑 reviewer。

## Repair request 規則

- repair request 給 extractor / repair agent 使用，應描述要修什麼，不替 repair agent 決定像素。
- `action` 優先使用 `recrop`、`manifest_correction`、`provide_clearer_source_evidence`、`regenerate_missing_preview`；必要時可自訂 snake_case action，並在 `constraint` 說明原因。
- 使用方向與約束，例如 `expand_bottom` 並說明要包含什麼、要排除什麼。
- 不寫 bbox、不寫 proposed crop coordinate、不寫 coordinate-like keys。
- 如果問題不是 crop，而是 manifest 的 panel list 或 visual units 錯誤，使用 `manifest_correction`。
- 如果來源證據不足以做出判斷，使用 `provide_clearer_source_evidence`，不要假裝視覺通過。
- 如果 canonical final crop preview 或 boundary preview 缺失，使用 `regenerate_missing_preview`，不要在 reviewer 目錄補建後當作 canonical evidence。

## Local self-check

- 寫完 `visual_review.json` 後，只做 reviewer-local self-check。
- Self-check 確認 JSON 可 parse、summary counts 和 figures list 一致。每個 reviewed crop unit 都必須有 source boundary preview path 與 hash；canonical crop preview / boundary preview 路徑與 edge_checks 必須存在，除非該 crop unit 已列入 `missing_canonical_artifacts[]` 並產生 `regenerate_missing_preview` repair request。
- 第一階段不執行 parent canonical validation，也不呼叫舊的 shared `validate_figures.py` 作為 reviewer 的正式 gate。
- Local self-check 通過不代表 parent close；parent close 仍以 `visual_review.json.status == "pass"` 且所有 figure decision pass 為準。
