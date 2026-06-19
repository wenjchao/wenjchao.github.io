# 目標

這是一份給 figure_reviewer agent 看的指引。

此流程使用場景與目標：
- 輸入：一個 paper directory、review round / reviewer assignment、`canonical_artifact_root`、已完成的 figure extraction 成果（schema 以 `figure_extractor.md` 定義的 `figure_extraction.v2` 為準），以及需要時可呼叫的 preview / crop helper。
- 讀取位置：
    - `shared/pages/`：完整解析度頁面圖片，這是審查來源版面的最高依據。
    - `shared/previews/`：頁面預覽圖片。
    - `lanes/figures/canonical/`：已合併的 figure extraction 成果（`figure_candidates.json`、`figure_index.json`、`figure_decisions.json`、`figures.json`，以及 crop PNG 和 extractor 產生的 preview）。
- 輸出位置：`<paper_dir>/lanes/figures/reviews/round_<N>/reviewer_<ID>/`
- 輸出：
    - `visual_review.json`：逐一記錄每張 figure 的視覺審查結果，包含來源證據、裁切證據、視覺清單、逐 crop unit 邊緣檢查、缺陷與修復請求。
    - `previews/`：reviewer 自行從頁面圖片建立的來源預覽與來源邊界預覽。所有 preview 檔名必須含 `_preview` 後綴。
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

- `agents/scripts/crop_region.py`：從 rendered page image 建立 source context crop 和 source edge crop。
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

3. 從 `figure_decisions.json` 和 `figures.json` 取得每張 figure 的 `figure_id`、`figure_label`、`crop_units[]`（`crop_id`、`page`、`crop_px`、`image_file`、`preview`、`edge_previews`、`role`）、`caption_text`、`expected_panels`。`figure_label` 只從 extractor manifest 複製，用來幫助人類閱讀與對照；穩定識別仍以 `figure_id` 為準。

4. 建立本輪 reviewer preview 目錄，例如 `lanes/figures/reviews/round_00/reviewer_01/previews/`。Reviewer 自建的 evidence previews 都放在這裡，不覆蓋 extractor 或 canonical 目錄中的檔案。

### 建立來源證據

5. 對每張要審查的 figure，從 `shared/pages/page_N.png` 建立 reviewer 自己的來源預覽圖，寫入 `previews/`：
   - 來源頁面概覽或來源區域預覽：顯示 figure 在頁面中的上下文，包含 figure、caption 邊界、附近正文和 page chrome。同頁的多個 crop units 可以共用一張來源頁面概覽。
   - 每個 crop unit 各自建立四個來源邊界預覽（上、下、左、右）：使用 `figure_decisions.json` 中該 crop unit 的 `crop_px`，從頁面圖片裁出跨越 crop boundary 的條帶，並用 `crop_region.py` 的 `--hline`（上下邊界）或 `--vline`（左右邊界）在 crop boundary 位置疊一條紅線。條帶必須讓紅線兩側的內容都清楚可辨。

   即使 extractor 已提供預覽圖，也必須建立 reviewer 自己的來源視圖。Reviewer 不能只用 extractor 的 framing 判斷。

6. 讀取 reviewer 建立的來源預覽圖與來源邊界預覽。如果邊界預覽無法判斷內容是否延伸到 crop 外，建立更大或更清楚、但仍符合讀圖限制的預覽後再判斷。

### 建立視覺清單

7. 判斷 crop 之前，先從來源頁面證據建立 `expected_visual_units`——依圖的類型，以適當粒度列出來源中可見的視覺元件：
   - 圖表型：plot area、軸標題、tick labels、legend、color bar、annotation。
   - 示意圖或化學流程圖：object groups、arrows、callouts、molecule groups、condition labels、terminal objects。
   - 顯微圖或矩陣型：tiles/cells、channel labels、row/column labels、scale bars、figure-internal legends。
   - 簡單單圖：至少記錄一個明確單元，例如 `main_plot`、`main_diagram` 或 `main_image_panel`。

   清單必須從來源頁面視圖建立，不從 caption 或 crop 建立。`expected_panels` 為空時更必須做視覺清單。

8. 將 `figure_decisions.json` 中的 `expected_panels` 複製到審查項目中。

### 讀取裁切證據

9. 讀取每個 crop unit 的 final crop 預覽圖。若 `figures.json` 指向的 canonical preview 不存在，不要從 final crop 圖片補建 reviewer preview；該 figure 直接標 `fail`，在 `defects` 和 `repair_request` 寫明 `missing canonical preview`。若 final crop 圖片本身不存在，該 figure 也直接標 `fail`。

10. 讀取每個 crop unit 的上、下、左、右邊界預覽。若缺少 canonical edge preview，不要從 final crop 圖片補建 reviewer edge preview；該 figure 直接標 `fail`，在 `defects` 和 `repair_request` 寫明 `missing canonical edge preview`。不要只看整張 crop preview 就決定 pass。

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

14. 對每個 crop unit，逐一檢查上、下、左、右四個邊界。每條邊都要比較同一個 crop unit 的 final crop edge preview 與 reviewer source edge preview。每條邊的判定：

    通過的 condition 只有三種：
    - `clean_margin`：crop edge 在 figure 外側，有空白邊距。
    - `figure_border_complete`：crop edge 與完整的 figure-internal border、frame 或 panel boundary 一致。
    - `intentional_full_bleed_edge`：來源圖有意延伸到邊緣，且沒有內容被切掉。

    其他任何狀態都是 `fail`，包括：`content_cut`、`content_touches_edge_uncertain`、`caption_visible`、`body_text_visible`、`page_chrome_visible`、`adjacent_content_visible`、`unknown`。

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
- 從 extraction manifests 讀到的 `image_file`、`preview`、`edge_previews` 都是 artifact root 相對路徑。Reviewer 讀檔時用 `canonical_artifact_root` resolve，寫入 review report 時仍保留同一個相對路徑字串。
- canonical crop evidence 存在時，`crop_previews_read` 和 `edge_checks.*.crop_evidence` 應使用 canonical manifest 中同一組 artifact root 相對路徑，例如 `previews/Figure_1_bottom_preview.png`。
- Reviewer 自己建立的 source evidence previews 放在 review output 目錄，不在 canonical artifact root 裡，因此可以記錄為 paper-dir-relative path，例如 `lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_context_preview.png`。
- 不要把 `lanes/figures/canonical/` 或絕對路徑加進 canonical crop evidence 欄位。

正確寫法：

```json
{
  "crop_preview": "previews/Figure_1_preview.png",
  "crop_evidence": "previews/Figure_1_bottom_preview.png",
  "source_evidence": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_bottom_preview.png"
}
```

### 基本欄位

- `visual_review.json` 使用 `schema_version: "figure_review.v2"`。v2 schema 以本文件內的 JSON example 與規則為準。
- 最上層包含 `schema_version`、`review_round`、`reviewer_id`、`scope`、`status`、`figures`、`summary`。
- `review_round` 必須和所在目錄 `round_<N>` 一致；`reviewer_id` 必須和所在目錄 `reviewer_<ID>` 一致。
- `visual_review.json.status` 只使用 `pass` 或 `fail`。只要任何 figure 的 `decision` 是 `fail`，最上層 `status` 就必須是 `fail`。
- 每個 figure 的 `decision` 只使用 `pass` 或 `fail`，不使用 `blocked`。如果 artifact、crop image、preview 或 source evidence 缺失，該 figure 標 `fail`，缺失原因寫在 `defects`、`notes`、`missing_canonical_artifacts` 和 `repair_request`。
- `figure_id` 是穩定識別欄位。`figure_label` 只從 extractor manifest 複製，用來讓人類快速對照圖號；如果 `figure_label` 和來源圖說或 manifest 明顯衝突，標 `fail` 並提出 `manifest_correction`。
- `checks`、`edge_checks` 中每條邊的 `status`、`decision` 只使用 `pass` 或 `fail`。不要使用 `not_applicable`；沒有某種元素時，只要沒有缺失，該檢查就是 `pass`。
- `expected_visual_units` 與 `observed_visual_units` 必須是非空陣列。通過時，`observed_visual_units` 的 `unit_id` 必須能對應 `expected_visual_units`。
- `observed_visual_units[].status` 使用 `present`、`incomplete` 或 `missing`。通過時，每個 expected visual unit 都必須有對應的 observed unit，且 status 為 `present`。
- `crop_hashes` 記錄每個 reviewed crop image 的 SHA-256，格式為 `sha256:<hash>`。key 使用 `crop_id`。
- `missing_canonical_artifacts` 記錄 canonical crop evidence 缺失；沒有缺失時使用空陣列。每個 entry 至少包含 `crop_id`、`kind`、`expected_path`，若缺的是單邊 edge preview，還要包含 `edge`。`kind` 使用 `crop_preview` 或 `edge_preview`。
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

canonical crop evidence 存在時，每個 `crop_units[]` 都必須各自有四邊 edge_checks。結構使用 `crop_units` 陣列，與 extractor 的 `crop_units[]` 一致，方便 validator 檢查每個 crop unit 是否都有四邊。若 canonical crop evidence 缺失，該 crop unit 改列在 `missing_canonical_artifacts[]`，不得假造 edge_checks。

- `edge_checks.crop_units[].crop_id` 必須對應 `figures.json.figures[].crop_units[].crop_id`。
- `edge_checks.crop_units[].edges` 必須包含 `top`、`bottom`、`left`、`right`。
- `edge_checks.crop_units[].edges.*.status` 只使用 `pass` 或 `fail`。

每條邊包含 `status`、`condition`、`source_evidence`、`crop_evidence`、`notes`。`source_evidence` 和 `crop_evidence` 分開記錄，對應 SKILL 原文 "Record the source edge previews separately from the crop edge previews"。

`condition` 的通過值：`clean_margin`、`figure_border_complete`、`intentional_full_bleed_edge`。

`condition` 的失敗值：`content_cut`、`content_touches_edge_uncertain`、`caption_visible`、`body_text_visible`、`page_chrome_visible`、`adjacent_content_visible`、`unknown`。

### evidence read

- `source_previews_read`：記錄 reviewer 從頁面圖片建立的 source context previews（flat array）。
- `source_edge_previews_read.crop_units[]`：記錄每個 crop unit 的 reviewer source edge previews。
- `crop_previews_read.crop_units[]`：記錄每個實際讀過的 final crop preview 與 final crop edge previews。不要把缺失的 canonical preview 假裝成已讀。
- 每個 `figures.json` 中的 `crop_units[].crop_id`，都必須在 `source_edge_previews_read.crop_units[]` 和 `crop_hashes` 中各出現一次。若 canonical crop preview 和 edge previews 完整存在，也必須在 `crop_previews_read.crop_units[]` 和 `edge_checks.crop_units[]` 中出現一次；若 canonical crop evidence 缺失，必須改列在 `missing_canonical_artifacts[]`，並讓該 figure `decision: "fail"`。
- `edge_checks.crop_units[].edges.*.source_evidence` 必須使用和 `source_edge_previews_read` 中相同的 path；`edge_checks.crop_units[].edges.*.crop_evidence` 必須使用和 `crop_previews_read` 中相同的 path。若 crop evidence 缺失，不要填假 path；用 `missing_canonical_artifacts[]` 記錄缺失的 canonical path。
- 這個結構比 flat list 稍長，但能避免 multi-page / multi-region figure 的 preview 和 edge check 對錯 crop unit。

### repair_request

- 通過的 figure：`repair_request` 設為 `null`。
- 未通過的 figure：`repair_request` 必須存在，並以 extractor / repair agent 能執行的方式描述。
- `action` 優先使用：`recrop`、`manifest_correction`、`provide_clearer_source_evidence`、`regenerate_missing_preview`；無法歸類時可自訂 snake_case action，並在 `constraint` 說明原因。
- `direction` 使用方向，例如 `expand_bottom`、`shrink_left`。如果 action 是 `regenerate_missing_preview`，`direction` 使用空陣列。
- 如果 canonical crop preview 或 edge preview 缺失，`repair_request.action` 使用 `regenerate_missing_preview`，`defects` 必須包含 `missing canonical preview` 或 `missing canonical edge preview`，`constraint` 指出要從 canonical crop PNG 重新建立缺失的 canonical preview / edge preview。
- 這類 request 必須把同一組 `missing_canonical_artifacts[]` 複製到 `repair_request.missing_canonical_artifacts[]`，讓 parent 和 repair worker 不需要從 notes 解析缺哪些檔案。
- 不要在 `repair_request` 中寫 `current_crop_px`、`proposed_crop_px`、bbox array 或座標鍵；像素由 extractor / repair agent 根據來源頁面決定。

## visual_review.json example

> 以下 example 展示一個 pass figure（Figure_1，單一 crop unit）與一個 fail figure（Figure_2，兩個 crop units）。`source_edge_previews_read`、`crop_previews_read`、`edge_checks` 都使用 `crop_units[]` 結構，確保每個 crop unit 獨立追蹤四邊。
> `edge_checks` 中的 `source_evidence` / `crop_evidence` 使用和 `source_edge_previews_read` / `crop_previews_read` 相同的 path。

```json
{
  "schema_version": "figure_review.v2",
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
      "source_previews_read": [
        "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_context_preview.png"
      ],
      "source_edge_previews_read": {
        "crop_units": [
          {
            "crop_id": "Figure_1",
            "edge_previews": {
              "top": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_top_preview.png",
              "bottom": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_bottom_preview.png",
              "left": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_left_preview.png",
              "right": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_right_preview.png"
            }
          }
        ]
      },
      "crop_previews_read": {
        "crop_units": [
          {
            "crop_id": "Figure_1",
            "crop_preview": "previews/Figure_1_preview.png",
            "edge_previews": {
              "top": "previews/Figure_1_top_preview.png",
              "bottom": "previews/Figure_1_bottom_preview.png",
              "left": "previews/Figure_1_left_preview.png",
              "right": "previews/Figure_1_right_preview.png"
            }
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
            "edges": {
              "top": {"status": "pass", "condition": "clean_margin", "source_evidence": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_top_preview.png", "crop_evidence": "previews/Figure_1_top_preview.png", "notes": "Top edge has whitespace above visual panels."},
              "bottom": {"status": "pass", "condition": "clean_margin", "source_evidence": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_bottom_preview.png", "crop_evidence": "previews/Figure_1_bottom_preview.png", "notes": "Bottom axis labels complete; external caption outside crop."},
              "left": {"status": "pass", "condition": "clean_margin", "source_evidence": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_left_preview.png", "crop_evidence": "previews/Figure_1_left_preview.png", "notes": "Left y-axis labels complete."},
              "right": {"status": "pass", "condition": "figure_border_complete", "source_evidence": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_right_preview.png", "crop_evidence": "previews/Figure_1_right_preview.png", "notes": "Right edge follows panel C boundary."}
            }
          }
        ]
      },
      "defects": [],
      "decision": "pass",
      "repair_request": null,
      "notes": "Panels A-C and all expected visual units present. Single crop unit has four passing edge checks. No external caption, page chrome, or adjacent content visible."
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
      "source_previews_read": [
        "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_source_context_preview.png"
      ],
      "source_edge_previews_read": {
        "crop_units": [
          {
            "crop_id": "Figure_2_part_1",
            "edge_previews": {
              "top": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_1_source_top_preview.png",
              "bottom": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_1_source_bottom_preview.png",
              "left": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_1_source_left_preview.png",
              "right": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_1_source_right_preview.png"
            }
          },
          {
            "crop_id": "Figure_2_part_2",
            "edge_previews": {
              "top": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_2_source_top_preview.png",
              "bottom": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_2_source_bottom_preview.png",
              "left": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_2_source_left_preview.png",
              "right": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_2_source_right_preview.png"
            }
          }
        ]
      },
      "crop_previews_read": {
        "crop_units": [
          {
            "crop_id": "Figure_2_part_1",
            "crop_preview": "previews/Figure_2_part_1_preview.png",
            "edge_previews": {
              "top": "previews/Figure_2_part_1_top_preview.png",
              "bottom": "previews/Figure_2_part_1_bottom_preview.png",
              "left": "previews/Figure_2_part_1_left_preview.png",
              "right": "previews/Figure_2_part_1_right_preview.png"
            }
          },
          {
            "crop_id": "Figure_2_part_2",
            "crop_preview": "previews/Figure_2_part_2_preview.png",
            "edge_previews": {
              "top": "previews/Figure_2_part_2_top_preview.png",
              "bottom": "previews/Figure_2_part_2_bottom_preview.png",
              "left": "previews/Figure_2_part_2_left_preview.png",
              "right": "previews/Figure_2_part_2_right_preview.png"
            }
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
            "edges": {
              "top": {"status": "pass", "condition": "clean_margin", "source_evidence": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_1_source_top_preview.png", "crop_evidence": "previews/Figure_2_part_1_top_preview.png", "notes": "Top edge clean."},
              "bottom": {"status": "pass", "condition": "clean_margin", "source_evidence": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_1_source_bottom_preview.png", "crop_evidence": "previews/Figure_2_part_1_bottom_preview.png", "notes": "Bottom edge clean; x-axis title complete."},
              "left": {"status": "pass", "condition": "clean_margin", "source_evidence": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_1_source_left_preview.png", "crop_evidence": "previews/Figure_2_part_1_left_preview.png", "notes": "Left edge clean."},
              "right": {"status": "pass", "condition": "clean_margin", "source_evidence": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_1_source_right_preview.png", "crop_evidence": "previews/Figure_2_part_1_right_preview.png", "notes": "Right edge clean."}
            }
          },
          {
            "crop_id": "Figure_2_part_2",
            "edges": {
              "top": {"status": "pass", "condition": "clean_margin", "source_evidence": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_2_source_top_preview.png", "crop_evidence": "previews/Figure_2_part_2_top_preview.png", "notes": "Top edge clean."},
              "bottom": {"status": "fail", "condition": "content_cut", "source_evidence": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_2_source_bottom_preview.png", "crop_evidence": "previews/Figure_2_part_2_bottom_preview.png", "notes": "Source view shows panel B x-axis title below current crop edge."},
              "left": {"status": "pass", "condition": "clean_margin", "source_evidence": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_2_source_left_preview.png", "crop_evidence": "previews/Figure_2_part_2_left_preview.png", "notes": "Left edge clean."},
              "right": {"status": "pass", "condition": "clean_margin", "source_evidence": "lanes/figures/reviews/round_00/reviewer_01/previews/Figure_2_part_2_source_right_preview.png", "crop_evidence": "previews/Figure_2_part_2_right_preview.png", "notes": "Right edge clean."}
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
      "notes": "Fig. 2 fails because Figure_2_part_2 cuts off figure content visible in the reviewer-created source bottom preview."
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

Reviewer 使用兩類圖片：extractor 產生的 final crop evidence，以及 reviewer 自己從頁面圖片建立的 source evidence。所有給 reviewer 讀的圖片都必須是 preview，檔名含 `_preview`，並符合讀圖尺寸限制。

- 頁面圖片：`shared/pages/page_3.png`
  - 角色：來源真相。Reviewer 不直接讀完整解析度頁面圖片，而是從它建立 bounded previews。
- reviewer 來源區域預覽：`lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_context_preview.png`
  - 角色：從頁面圖片產生，顯示 figure 在原始頁面中的上下文，包括 figure、caption boundary、附近正文與 page chrome。
- reviewer 來源邊界預覽：`lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_bottom_preview.png`
  - 角色：從頁面圖片裁出跨越 crop boundary 的條帶，在 boundary 位置疊紅線。用來獨立判斷邊界是否切掉內容或混入非 figure 內容。
- final crop 預覽：`previews/Figure_1_preview.png`
  - 角色：顯示 extractor 實際產生的 final crop。
- final crop 邊界預覽：`previews/Figure_1_bottom_preview.png`
  - 角色：extractor 產生的邊界條帶，同樣從頁面圖片裁出、含紅色 boundary line。必須和 reviewer source boundary preview 對照。

# 規則

## 權責

- `figure_reviewer` 只做 independent visual review。
- 不建立新的 final crop。不修改 extraction manifests。不修改 final crop 圖片。不修改來源 PDF。
- 可以建立 reviewer source evidence previews。
- 如果 crop 不合格，標 `fail` 並提出 repair request；不要直接修。
- helper 可以建立 reviewer source preview、source edge preview、hash，也可以執行機械驗證；但 helper、validator、manifest 和 crop coordinate 都不能替 reviewer 判定 visual quality。`pass` 必須由 reviewer 讀過 source evidence、canonical final crop preview 和 canonical 四邊 edge previews 後判斷。

## 圖片與讀取限制

- reviewer 不得直接視覺讀取完整解析度頁面圖片、完整解析度 crop 圖片或高解析度 raw edge strip。
- reviewer 讀取單張圖片時，兩邊都不得超過 1600 px。
- reviewer 一次讀多張圖片時，每張兩邊都不得超過 1400 px，且批次要小。
- 若可用 evidence image 超過限制，先建立受限尺寸 preview 再讀取，並記錄路徑。
- 所有 reviewer 建立的 preview 都寫在本輪 review 輸出的 `previews/` 目錄，不覆蓋 extractor 產生的 preview。
- 如果 canonical preview 或 edge preview 缺失，reviewer 不補建、不覆蓋、不把 reviewer-local preview 當作 canonical crop evidence。該 figure 直接 `fail`，並用 `missing_canonical_artifacts[]` 和 `repair_request.action: "regenerate_missing_preview"` 交給 repair。

## 來源獨立性

- rendered page image 是 reviewer 的來源真相。
- extractor 提供的 preview 可以參考，但不能取代 reviewer 從 rendered page image 獨立建立的 source evidence。
- 每張 figure 都必須有 reviewer 自建的 source context preview。
- 每個 `crop_units[]` 都必須有 reviewer source edge previews，且四個方向都要能看到 crop edge 內外兩側。
- 如果 source edge preview 無法判斷內容是否延伸到 crop 外，建立更大或更清楚的 bounded view 後再決定。

## 視覺清單規則

- `expected_visual_units` 從 reviewer source evidence 建立，不從 caption 或 crop 建立。
- `observed_visual_units` 從 final crop evidence 建立。
- 通過時，`observed_visual_units` 的 `unit_id` 必須完整對應 `expected_visual_units`。
- `expected_panels` 為空時，仍必須建立 `expected_visual_units`；不能因為沒有 panel label 就不做視覺清單。
- 如果 `figure_decisions.json.expected_panels` 和來源頁面實際可見 panels 不一致，該 figure 應標 `fail`，要求 manifest correction 或 recrop，不要默默放行。

## 邊緣檢查規則

- 每個 `crop_units[]` 都獨立做上、下、左、右四邊檢查。
- 每條邊都要同時看 final crop edge preview 和 reviewer source edge preview，並在 edge_checks 中分別記為 `crop_evidence` 和 `source_evidence`。如果 final crop edge preview 缺失，不做視覺補判，直接標缺失並要求 repair 重新建立 preview。
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
- 如果 canonical crop preview 或 edge preview 缺失，使用 `regenerate_missing_preview`，不要在 reviewer 目錄補建後當作 canonical evidence。

## Local self-check

- 寫完 `visual_review.json` 後，只做 reviewer-local self-check。
- Self-check 確認 JSON 可 parse、summary counts 和 figures list 一致。每個 reviewed crop unit 都必須有 source evidence 與 hash；crop evidence 和 edge checks 必須存在，除非該 crop unit 已列入 `missing_canonical_artifacts[]` 並產生 `regenerate_missing_preview` repair request。
- 第一階段不執行 parent canonical validation，也不呼叫舊的 shared `validate_figures.py` 作為 reviewer 的正式 gate。
- Local self-check 通過不代表 parent close；parent close 仍以 `visual_review.json.status == "pass"` 且所有 figure decision pass 為準。
