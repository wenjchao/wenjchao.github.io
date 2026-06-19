# 目標

這是一份給 figure_reviewer agent 看的指引。

此流程使用場景與目標：
- 輸入：一個 paper directory、review round / reviewer assignment、已完成的 figure extraction 成果（以新版 `figure_extractor.md` 為準），以及需要時可呼叫的 preview / crop helper。
- 讀取位置：
    - `shared/pages/`：完整解析度頁面圖片，這是審查來源版面的最高依據。
    - `shared/previews/`：頁面預覽圖片。
    - `lanes/figures/canonical/`：已合併的 figure extraction 成果，包含 figure JSON、final crop PNG，以及 extractor 產生的 previews。
    - `lanes/figures/validation/`：機械式驗證結果，如果已存在。
- 輸出位置：`lanes/figures/reviews/round_00/reviewer_01/`
- 輸出：
    - `visual_review.json`：逐一記錄每張 figure 的視覺審查結果，包含來源證據、裁切證據、視覺清單、邊界檢查、缺陷與 repair request。
    - `previews/`：reviewer 自行從頁面圖片建立的來源預覽、來源邊界預覽，以及必要時建立的 final crop / edge previews。所有 preview 檔名必須含 `_preview` 後綴。
    - `figures_validation.json`：final validator 的結果，寫在 `lanes/figures/validation/`。寫完 `visual_review.json` 後必定執行。

- 目標：獨立判斷每個 final crop 是否視覺完整且乾淨。完整表示 figure 內容沒有被切掉；乾淨表示 crop 中沒有混入外部 caption、正文、page chrome 或相鄰內容。
- 邊界：
    - 此 agent 只做 visual review，不做裁切、不修改 extraction 成果、不修改來源 PDF。
    - 如果 crop 有問題，標 `fail` 並提出 repair request；實際修復由 extractor 或 repair agent 執行。
    - reviewer 可以建立自己的審查用 preview，但不能覆蓋 extractor 產生的任何檔案。
    - 不要讓 extractor 提供的 preview 框住判斷範圍；reviewer 必須從頁面圖片獨立建立或確認自己的來源證據。

# 流程

## 工作流程

### 準備審查資料

1. 確認 reviewer assignment：本輪要審查的 figure 範圍、review round 和 reviewer id。若未指定 reviewer id，使用輸出目錄名稱，例如 `reviewer_01`。

2. 讀取 figure extraction artifacts：
   - `figure_candidates.json`
   - `figure_index.json`
   - `figure_decisions.json`
   - `figures.json`
   - `figures_mechanical_validation.json`，如果已存在

   如果必要 artifact 缺失，不要自行補寫 extraction artifact；在 `visual_review.json` 中將受影響的 figure 標 `fail` 或回報 blocked reason。

3. 從 `figure_decisions.json` 和 `figures.json` 取得每張 figure 的 `figure_id`、`figure_label`、`crop_units[]`、`caption_text`、`expected_panels` 與對應頁碼。`crop_units[]` 至少要能對應 `crop_id`、`page`、`crop_px`、`image_file`、preview 與 edge previews。`figure_label` 只用來幫助人類對照圖號；穩定識別仍以 `figure_id` 為準。

4. 建立本輪 reviewer preview 目錄，例如 `lanes/figures/reviews/round_00/reviewer_01/previews/`。Reviewer 自建的 evidence previews 都放在這裡，不覆蓋 extractor 或 canonical 目錄中的檔案。

### 建立來源證據

5. 對每張要審查的 figure，從 `shared/pages/page_N.png` 建立 reviewer 自己的來源預覽，寫入本輪 `previews/`：
   - 來源頁面概覽或來源區域預覽：顯示 figure 在頁面中的上下文，包含 figure、caption 邊界、附近正文和 page chrome。
   - 來源邊界預覽：每個 `crop_units[]` 都要各自建立上、下、左、右四個來源邊界預覽。同頁的多個 crop units 可以共用來源頁面概覽。

   來源邊界預覽應使用 `figure_decisions.json` 中的 `crop_px`，讓預覽同時顯示裁切邊界內側與外側內容。

   即使 extractor 已提供預覽圖，也必須建立或確認 reviewer 自己的來源視圖。Reviewer 不能只用 extractor 的 framing 判斷。

6. 讀取 reviewer 建立的來源預覽與來源邊界預覽。如果邊界預覽無法判斷內容是否延伸到 crop 外，建立更大或更清楚、但仍符合讀圖限制的預覽後再判斷。

### 建立視覺清單

7. 判斷 crop 之前，先從來源頁面證據建立 `expected_visual_units`。這份清單描述來源 figure 中應被保留的可見視覺單元，不從 caption 或 final crop 推測。

8. `expected_visual_units` 應依圖型使用合適粒度：
   - 圖表型：plot area、axes / tick labels、axis titles、legend、color bar、annotation。
   - 示意圖或化學流程圖：object groups、arrows、callouts、molecule groups、condition labels、terminal objects。
   - 顯微圖或矩陣型：tiles / cells、channel labels、row / column labels、scale bars、figure-internal legends。
   - 簡單單圖：至少記錄一個明確單元，例如 `main_plot`、`main_diagram` 或 `main_image_panel`，不要留空。

9. 將 `figure_decisions.json` 中的 `expected_panels` 複製到審查項目中。

### 讀取裁切證據

10. 讀取每個 `crop_units[]` 的 final crop preview。若 `figures.json` 指向的 preview 不存在，先從實際 final crop 圖片建立 reviewer preview；若 final crop 圖片本身不存在，該 figure 直接標 `fail`。

11. 讀取每個 `crop_units[]` 的上、下、左、右四個 final crop edge previews。若缺少 edge preview，先從實際 final crop 圖片建立 reviewer edge preview。不要只看整張 crop preview 就決定 pass。

12. 為每個被審查的 final crop PNG 計算 SHA-256，寫入 `crop_hashes`。如果 crop 之後被修改但審查未更新，validator 會用 hash 偵測過期審查。

13. 從 final crop 記錄 `observed_visual_units` 和 `observed_panels`。通過審查時，兩組 visual units 必須對應，兩組 panels 也必須對應。如果 extractor 的 `expected_panels` 明顯錯誤，標 `fail` 並要求 manifest correction 或 recrop，不要默默修正後放行。

### 視覺審查

14. 比對來源證據與裁切證據。逐一確認：
    - 來源中可見的所有 panels 都出現在 crop 中
    - 來源中所有重要 visual units 都出現在 crop 中，即使沒有 panel label
    - panel labels、axes、tick labels、legends、scale bars、insets、color bars、row / column labels 和 plot boundaries 都完整
    - crop 排除外部 caption 和圖外 legend
    - crop 排除周圍正文
    - crop 排除頁碼、頁眉、頁腳、浮水印、期刊固定元素和其他 page chrome
    - crop 不包含相鄰 figure、table、equation 或無關頁面內容
    - crop 不是只把 figure 包在裡面的大頁面條帶

15. 對每個 `crop_units[]` 獨立檢查上、下、左、右四個邊界。每條邊都要比較同一個 crop unit 的 final crop edge preview 與 reviewer source edge preview。

   通過的 edge condition 只有三種：
   - `clean_margin`：crop edge 在 figure 外側，有乾淨空白。
   - `figure_border_complete`：crop edge 與完整的 figure-internal border、frame 或 panel boundary 一致。
   - `intentional_full_bleed_edge`：來源 figure 有意延伸到頁面或 crop 邊緣，且沒有內容被切掉。

   其他狀態都是 `fail`，例如 `content_cut`、`content_touches_edge_uncertain`、`caption_visible`、`body_text_visible`、`page_chrome_visible`、`adjacent_content_visible`、`unknown`。

16. 對圖表型圖片，bottom edge 與 side edges 風險最高。折線圖、長條圖、散點圖、熱圖、Manhattan plot、帶座標軸的示意圖，都必須明確檢查 x 軸刻度與標題、y 軸標籤、legend、color bar 和 plot boundary 是否完整。

### 寫出 review 結果

17. 綜合所有檢查，為每張 figure 寫出 `decision`：
    - 全部 `checks` 和所有 crop units 的 `edge_checks` 都 `pass` → `decision: "pass"`。
    - 任何一項 `fail` → `decision: "fail"`，並填寫 `defects` 和 `repair_request`。

18. 判定為 `pass` 的 figure，`notes` 必須非空，說明：觀察到的 panels / visual units、各 crop unit 四邊為何乾淨、嵌入文字為什麼屬於 figure-internal content。`notes` 不得包含「也許」「可能」「看起來」「不清楚」「略微切到」「盡力」等不確定語氣，也不得提到任何已知缺陷。

19. 判定為 `fail` 的 figure，必須寫具體 `defects` 與 `repair_request`。Repair request 用方向和限制描述，不提供精確座標。例如要求 `expand_bottom`，並說明「include the missing bottom axis title; stop before the external caption」。

20. 寫出 `lanes/figures/reviews/round_00/reviewer_01/visual_review.json`。只要任何 figure 的 `decision` 是 `fail`，最上層 `status` 就是 `fail`。不要只根據 manifests 寫 `visual_review.json`；如果引用的 preview 缺失，該 figure 標 `fail`。

21. 寫完 `visual_review.json` 後，必定執行 final validator：

```bash
python3 ${CLAUDE_SKILL_DIR}/../_shared/scripts/validate_figures.py \
  "<paper_dir>" --write "<paper_dir>/lanes/figures/validation/figures_validation.json"
```

如果 validator 失敗，保留失敗結果；不要為了讓 validator 通過而修改 extraction manifests 或 review verdict。

22. 回報本輪讀過的來源與裁切 previews、通過/失敗的 figures、主要 defects、`visual_review.json` 路徑，以及 final validator 結果。

# 格式

## JSON 命名與 enum

### 基本欄位

- `visual_review.json` 使用 `schema_version: "figure_review.v2"`。
- `visual_review.json` 最上層包含 `schema_version`、`review_round`、`reviewer_id`、`scope`、`status`、`figures`、`summary`。
- `visual_review.json.status` 只使用 `pass` 或 `fail`。只要任何 figure 的 `decision` 是 `fail`，最上層 `status` 就必須是 `fail`。
- `figure_id` 是穩定識別欄位。`figure_label` 只從 extractor manifest 複製，用來讓人類快速對照圖號；如果 `figure_label` 和來源圖說或 manifest 明顯衝突，標 `fail` 並提出 `manifest_correction`。
- `expected_visual_units` 與 `observed_visual_units` 必須是非空陣列。通過時，`observed_visual_units` 的 `unit_id` 必須能對應 `expected_visual_units`。
- `crop_hashes` 記錄每個 reviewed crop image 的 SHA-256，格式為 `sha256:<hash>`。
- `summary.figure_count`、`summary.pass_count`、`summary.fail_count` 必須與實際 `figures` 列表一致。

### checks

- `checks` 的值只使用 `pass` 或 `fail`。不要使用 `not_applicable`；沒有某種元素時，只要沒有相關內容缺失，該檢查就是 `pass`。
- 建議優先使用下列 checks：`all_panels_present`、`visual_units_match`、`labels_axes_legends_complete`、`external_caption_excluded`、`body_text_excluded`、`page_chrome_excluded`、`no_adjacent_content`、`not_page_strip`。
- 如果遇到上列沒有涵蓋的審查項目，可以新增簡短 snake_case check name。新增 check 也只能填 `pass` 或 `fail`，並應在 `notes` 或 `defects` 中說明。

### edge_checks

- 每個 `crop_units[]` 都必須各自有四邊 `edge_checks`。
- `edge_checks.crop_units[].crop_id` 必須對應 `figures.json.figures[].crop_units[].crop_id`。
- `edge_checks.crop_units[].edges` 必須包含 `top`、`bottom`、`left`、`right`。
- `edge_checks.crop_units[].edges.*.status` 只使用 `pass` 或 `fail`。
- `edge_checks.crop_units[].edges.*.condition` 的通過值：`clean_margin`、`figure_border_complete`、`intentional_full_bleed_edge`。
- `edge_checks.crop_units[].edges.*.condition` 的失敗值：`content_cut`、`content_touches_edge_uncertain`、`caption_visible`、`body_text_visible`、`page_chrome_visible`、`adjacent_content_visible`、`unknown`。

### evidence read

- `source_previews_read` 記錄 reviewer 從頁面圖片建立或確認過的 source context previews。
- `source_edge_previews_read.crop_units[]` 記錄每個 crop unit 的 reviewer source edge previews。
- `crop_previews_read.crop_units[]` 記錄每個 crop unit 的 final crop preview 與 final crop edge previews。
- 每個 `crop_units[]` 都必須能在 `source_edge_previews_read.crop_units[]`、`crop_previews_read.crop_units[]` 和 `edge_checks.crop_units[]` 找到同一個 `crop_id`。
- 這個結構比 flat list 稍長，但能避免 multi-page / multi-region figure 的 preview 和 edge check 對錯 crop unit。

### repair_request

- 通過的 figure：`repair_request` 設為 `null`。
- 未通過的 figure：`repair_request` 必須存在，並以 extractor / repair agent 能執行的方式描述。
- `action` 優先使用：`recrop`、`manifest_correction`、`provide_clearer_source_evidence`。
- 如果上述 action 無法描述問題，可以新增簡短 snake_case action，並在 `constraint` 說明原因。
- `direction` 使用方向，例如 `expand_bottom`、`shrink_left`。
- 不要在 `repair_request` 中寫 `current_crop_px`、`proposed_crop_px`、bbox array 或座標鍵；像素由 extractor / repair agent 根據來源頁面決定。

## visual_review.json example

以下 example 展示一個 pass figure（單一 crop unit）與一個 fail figure（兩個 crop units）。每個 crop unit 都各自記錄 source edge previews、crop previews 和 edge checks。

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
      "expected_panels": ["A", "B"],
      "observed_panels": ["A", "B"],
      "expected_visual_units": [
        {
          "unit_id": "panel_A_plot",
          "type": "plot",
          "location": "left",
          "description": "Panel A plot with complete axes and legend."
        },
        {
          "unit_id": "panel_B_image",
          "type": "image_panel",
          "location": "right",
          "description": "Panel B image with complete scale bar."
        }
      ],
      "observed_visual_units": [
        {
          "unit_id": "panel_A_plot",
          "status": "present",
          "notes": "Axes and legend are visible."
        },
        {
          "unit_id": "panel_B_image",
          "status": "present",
          "notes": "Image panel and scale bar are visible."
        }
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
            "crop_preview": "lanes/figures/canonical/previews/Figure_1_preview.png",
            "edge_previews": {
              "top": "lanes/figures/canonical/previews/Figure_1_top_preview.png",
              "bottom": "lanes/figures/canonical/previews/Figure_1_bottom_preview.png",
              "left": "lanes/figures/canonical/previews/Figure_1_left_preview.png",
              "right": "lanes/figures/canonical/previews/Figure_1_right_preview.png"
            }
          }
        ]
      },
      "crop_hashes": {
        "Figure_1": "sha256:1111111111111111111111111111111111111111111111111111111111111111"
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
              "top": {
                "status": "pass",
                "condition": "clean_margin",
                "source_evidence": "Figure_1_source_top_preview.png",
                "crop_evidence": "Figure_1_top_preview.png",
                "notes": "Top edge has clean whitespace above the visual panels."
              },
              "bottom": {
                "status": "pass",
                "condition": "clean_margin",
                "source_evidence": "Figure_1_source_bottom_preview.png",
                "crop_evidence": "Figure_1_bottom_preview.png",
                "notes": "Bottom scale bar and axis labels are complete; external caption is outside the crop."
              },
              "left": {
                "status": "pass",
                "condition": "clean_margin",
                "source_evidence": "Figure_1_source_left_preview.png",
                "crop_evidence": "Figure_1_left_preview.png",
                "notes": "Left edge is outside the visual figure."
              },
              "right": {
                "status": "pass",
                "condition": "figure_border_complete",
                "source_evidence": "Figure_1_source_right_preview.png",
                "crop_evidence": "Figure_1_right_preview.png",
                "notes": "Right edge follows the complete panel boundary."
              }
            }
          }
        ]
      },
      "defects": [],
      "decision": "pass",
      "repair_request": null,
      "notes": "Fig. 1 passes. Panels A-B and all expected visual units are present. The single crop unit has four passing edge checks, and no external caption, page chrome, or adjacent content is visible."
    },
    {
      "figure_id": "Figure_2",
      "figure_label": "Fig. 2",
      "expected_panels": ["A", "B"],
      "observed_panels": ["A", "B"],
      "expected_visual_units": [
        {
          "unit_id": "panel_A_plot",
          "type": "plot",
          "location": "left",
          "description": "Panel A plot with complete x-axis title."
        },
        {
          "unit_id": "panel_B_plot",
          "type": "plot",
          "location": "right",
          "description": "Panel B plot with complete x-axis title."
        }
      ],
      "observed_visual_units": [
        {
          "unit_id": "panel_A_plot",
          "status": "present",
          "notes": "Panel A plot is complete."
        },
        {
          "unit_id": "panel_B_plot",
          "status": "incomplete",
          "notes": "Panel B bottom x-axis title is cut off."
        }
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
            "crop_preview": "lanes/figures/canonical/previews/Figure_2_part_1_preview.png",
            "edge_previews": {
              "top": "lanes/figures/canonical/previews/Figure_2_part_1_top_preview.png",
              "bottom": "lanes/figures/canonical/previews/Figure_2_part_1_bottom_preview.png",
              "left": "lanes/figures/canonical/previews/Figure_2_part_1_left_preview.png",
              "right": "lanes/figures/canonical/previews/Figure_2_part_1_right_preview.png"
            }
          },
          {
            "crop_id": "Figure_2_part_2",
            "crop_preview": "lanes/figures/canonical/previews/Figure_2_part_2_preview.png",
            "edge_previews": {
              "top": "lanes/figures/canonical/previews/Figure_2_part_2_top_preview.png",
              "bottom": "lanes/figures/canonical/previews/Figure_2_part_2_bottom_preview.png",
              "left": "lanes/figures/canonical/previews/Figure_2_part_2_left_preview.png",
              "right": "lanes/figures/canonical/previews/Figure_2_part_2_right_preview.png"
            }
          }
        ]
      },
      "crop_hashes": {
        "Figure_2_part_1": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
        "Figure_2_part_2": "sha256:3333333333333333333333333333333333333333333333333333333333333333"
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
              "top": {"status": "pass", "condition": "clean_margin", "source_evidence": "Figure_2_part_1_source_top_preview.png", "crop_evidence": "Figure_2_part_1_top_preview.png", "notes": "Top edge is clean."},
              "bottom": {"status": "pass", "condition": "clean_margin", "source_evidence": "Figure_2_part_1_source_bottom_preview.png", "crop_evidence": "Figure_2_part_1_bottom_preview.png", "notes": "Bottom edge is clean."},
              "left": {"status": "pass", "condition": "clean_margin", "source_evidence": "Figure_2_part_1_source_left_preview.png", "crop_evidence": "Figure_2_part_1_left_preview.png", "notes": "Left edge is clean."},
              "right": {"status": "pass", "condition": "clean_margin", "source_evidence": "Figure_2_part_1_source_right_preview.png", "crop_evidence": "Figure_2_part_1_right_preview.png", "notes": "Right edge is clean."}
            }
          },
          {
            "crop_id": "Figure_2_part_2",
            "edges": {
              "top": {"status": "pass", "condition": "clean_margin", "source_evidence": "Figure_2_part_2_source_top_preview.png", "crop_evidence": "Figure_2_part_2_top_preview.png", "notes": "Top edge is clean."},
              "bottom": {"status": "fail", "condition": "content_cut", "source_evidence": "Figure_2_part_2_source_bottom_preview.png", "crop_evidence": "Figure_2_part_2_bottom_preview.png", "notes": "Source view shows the panel B x-axis title below the current crop bottom edge."},
              "left": {"status": "pass", "condition": "clean_margin", "source_evidence": "Figure_2_part_2_source_left_preview.png", "crop_evidence": "Figure_2_part_2_left_preview.png", "notes": "Left edge is clean."},
              "right": {"status": "pass", "condition": "clean_margin", "source_evidence": "Figure_2_part_2_source_right_preview.png", "crop_evidence": "Figure_2_part_2_right_preview.png", "notes": "Right edge is clean."}
            }
          }
        ]
      },
      "defects": [
        "Panel B bottom x-axis title is cut off in Figure_2_part_2."
      ],
      "decision": "fail",
      "repair_request": {
        "action": "recrop",
        "direction": ["expand_bottom"],
        "constraint": "Include the missing panel B x-axis title; stop before the external caption below the figure."
      },
      "notes": "Fig. 2 fails because one crop unit cuts off figure content visible in the reviewer-created source bottom preview."
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

本節介紹 reviewer 會讀取或建立的圖片。所有給 reviewer 讀的圖片都必須是 preview，檔名含 `_preview`，並符合讀圖尺寸限制。

- 頁面圖片：`shared/pages/page_3.png`
  - 角色：source truth。Reviewer 不直接讀完整解析度頁面圖片，而是從它建立 bounded previews。
- reviewer 來源區域預覽：`lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_context_preview.png`
  - 角色：顯示 figure 在原始頁面中的上下文，包括 figure、caption boundary、附近正文與 page chrome。
- reviewer 來源邊界預覽：`lanes/figures/reviews/round_00/reviewer_01/previews/Figure_1_source_bottom_preview.png`
  - 角色：顯示 crop 邊界在來源頁面中的內外兩側，用來判斷邊界是否切掉內容或混入非 figure 內容。
- final crop 預覽：`lanes/figures/canonical/previews/Figure_1_preview.png`
  - 角色：顯示 extractor 實際產生的 final crop。
- final crop 邊界預覽：`lanes/figures/canonical/previews/Figure_1_bottom_preview.png`
  - 角色：顯示 final crop 的邊界狀態，必須和 reviewer source boundary preview 對照。

# 規則

## 權責

- `figure_reviewer` 只做 independent visual review。
- 不建立新的 final crop，不修改 extraction manifests，也不修改 final crop 圖片。
- 可以建立 reviewer evidence previews。
- 如果 crop 不合格，標 `fail` 並提出 repair request；不要直接修。

## 圖片與讀取限制

- Reviewer 不得直接視覺讀取完整解析度頁面圖片、完整解析度 crop 圖片或高解析度 raw edge strip。
- Reviewer 讀取單張圖片時，圖片兩邊都不得超過 1600 px。
- Reviewer 一次讀多張圖片時，每張圖片兩邊都不得超過 1400 px，且批次要小。
- 若可用 evidence image 超過限制，必須先建立 bounded preview，再讀 preview。
- Reviewer-created preview 都寫在本輪 review output 的 `previews/` 目錄。

## 來源獨立性

- Rendered page image 是 reviewer 的 source truth。
- Extractor previews 可以參考，但不能取代 reviewer 從 rendered page image 建立或確認的 source evidence。
- 每張 figure 都必須有 reviewer source context preview。
- 每個 `crop_units[]` 都必須有 reviewer source edge previews，且四個方向都要能看到 crop edge 內外兩側。

## 視覺清單

- `expected_visual_units` 來自 reviewer source evidence，不來自 caption，也不來自 final crop。
- `observed_visual_units` 來自 final crop evidence。
- 通過時，`observed_visual_units` 必須完整對應 `expected_visual_units`。
- 如果 `expected_panels` 為空，仍要建立 `expected_visual_units`；不能因為沒有 panel label 就不做視覺清單。

## 邊界審查

- 每個 `crop_units[]` 都要獨立做上、下、左、右四邊檢查。
- 每條邊都要同時看 final crop edge preview 和 reviewer source edge preview。
- 只要 figure content 被切掉，該 edge 是 `fail`。
- 只要 external caption、body text、page chrome 或 adjacent content 出現在 crop 中，該 figure 是 `fail`。
- 大幅寬圖可以接近整頁寬度，但不能是 lazy page strip；垂直方向仍應緊貼 figure。
- 圖表型圖片的 bottom edge 和 side edges 必須特別檢查 axes、tick labels、axis titles、legend、color bar 和 plot boundary。

## Pass/fail 語意

- `pass` 表示 reviewer 能用視覺證據說明 crop 完整且乾淨。
- `fail` 表示 crop 有缺陷、證據不足、仍不確定，或 reviewer 無法用視覺證據說明它完整且乾淨。
- 不確定就是 `fail`。
- 不要使用 `not_applicable`。
- 不要因為 crop mostly okay、best effort、或缺陷看起來 minor 就標 `pass`。
- 如果 `notes` 中需要承認 clipping、uncertainty 或 unresolved condition，該 figure 必須是 `fail`。

## Repair request

- Repair request 給 extractor / repair agent 使用，應描述要修什麼，不替 repair agent 決定像素。
- `action` 優先使用 `recrop`、`manifest_correction`、`provide_clearer_source_evidence`；必要時可新增簡短 action，並在 `constraint` 說明原因。
- 使用方向與限制，例如 `expand_bottom`、`shrink_left`，並說明要包含什麼、要排除什麼。
- 不寫 bbox、不寫 proposed crop coordinate、不寫 coordinate-like keys。
- 如果問題不是 crop，而是 manifest panel list 或 visual units 錯，使用 `manifest_correction`。
- 如果來源證據不足，使用 `provide_clearer_source_evidence`，不要假裝視覺通過。

## Stale review protection

- 每個 reviewed crop image 都必須計算 SHA-256，寫入 `crop_hashes`。
- 如果 crop image 在 review 後被修改，舊 review 不再有效。
- 若 validator 發現目前 crop hash 和 `visual_review.json.crop_hashes` 不一致，應拒絕該 review。

## Final validation

- Reviewer 的主要判斷寫在 `visual_review.json`。
- 寫完 `visual_review.json` 後，必定執行 final validator。
- Final validator 只有在 mechanical validation、extraction manifests、review evidence 與 `visual_review.json` 都一致時才可通過。
- 如果 final validator 失敗，保留失敗結果。
- 不得為了讓 validator 通過而修改 extraction manifests 或 review verdict。
