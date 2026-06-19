# 目標

這是一份給 figure_extractor agent 看的指引。

此流程使用場景與目標：
- 輸入：一個 paper directory（含 `shared/pages/`、`shared/previews/`）、pages 範圍、`output_root`。
- 輸出位置：`<paper_dir>/figures/workers/worker_01/`
- 輸出：
    - `figures.json`：唯一的 extraction manifest。記錄每張 figure 的 crop 座標、圖片路徑、圖說、驗證結果。格式見「# figures.json 格式」。
    - `crops/`：完整解析度 final crop 圖片。
    - `previews/`：所有 evidence preview（crop preview、boundary preview、edge strips、bottom band、bottom microzoom）。
- 目標：讓每個 final crop 準確包含 figure 的上下左右邊緣——不要把 figure 的任何部分切掉，同時盡可能裁掉非 figure 的部分。
- 邊界：此 agent 只負責 initial extraction。不負責 reviewer、repair、canonical merge，也不修改來源 PDF。

# 工具

本 agent 裁切或建立 preview 時，只使用以下 local helper：

| Script | 用途 |
|---|---|
| `crop_and_preview.py` | 主要工具。一次完成 final crop + 全套 evidence preview（crop preview、boundary preview、四邊 edge strips、bottom band segments、bottom microzoom segments）。 |
| `crop_region.py` | 從頁面圖片裁出任意區域。用於偵測 page chrome 位置等輔助需求，不用於 figure final crop。 |
| `validate_figure_extraction.py` | 機械檢查 JSON contract、artifact path、必要檔案存在、座標範圍。不判斷視覺品質。 |

所有 script 在 `agents/scripts/`。

`crop_and_preview.py` 用法：

```bash
python3 agents/scripts/crop_and_preview.py \
  --page-image shared/pages/page_N.png \
  --crop-px <x1> <y1> <x2> <y2> \
  --crop-id <crop_id> \
  --output-dir <output_root>
```

一次產出：
- `crops/<crop_id>.png`：final crop
- `previews/<crop_id>_preview.png`：crop preview（檢查 figure 內部細節）
- `previews/<crop_id>_boundary_preview.png`：boundary preview（含 cyan 矩形，檢查四邊整體 framing）
- `previews/<crop_id>_top_seg1_preview.png`、`_left_seg1_preview.png`、`_right_seg1_preview.png`：三邊 edge strips
- `previews/<crop_id>_bottom_seg<N>_preview.png`：bottom band segments（底邊 context）
- `previews/<crop_id>_micro_bottom_seg<N>_preview.png`：bottom microzoom segments（底邊精準檢查）

重跑 `crop_and_preview.py` 會覆寫同一個 crop_id 的全部檔案。調整 crop_px 後直接重跑即可。

# 流程

## Step 1: 確認前置條件

確認 `shared/pages/page_N.png` 和 `shared/previews/page_N_preview.png` 對所有 assignment 頁面都存在。頁面圖片和 page preview 是 parent 在 Step 0 產生的，不是 extractor 的工作。若缺少，回報 blocked，不要臨場產生。

建立 output 目錄：`<output_root>/crops/`、`<output_root>/previews/`。

## Step 2: 偵測 page chrome

很多期刊頁面有固定元素（「Article」header、頁碼、期刊名等），會重複出現在多頁。這些元素不屬於任何 figure，必須從所有 crop 排除。

做法：讀前幾頁的 page preview，辨識重複出現的固定元素。記下它們的大約 y 座標範圍（例如「Article header + 底線到 page y ≈ 190」「頁碼在 page y > 3250」）。後續裁切時，所有 crop 的 top/bottom 自動避開這些區域。

這一步不需要產出檔案。在腦中記住即可，後續 Step 3 裁切時套用。

## Step 3: 掃描頁面並辨識圖表

逐頁讀 page preview，辨識所有有標記的 figure（有 "Fig."、"Figure"、"Extended Data Fig." 等 label 的圖）。

對每張 figure，記下：
- **figure_id**：filename-safe 識別碼，例如 `Figure_1`、`Extended_Data_Figure_1`
- **figure_label**：顯示用 label，例如 `Fig. 1`、`Extended Data Fig. 1`
- **figure_type**：`main`、`extended`、`supplementary`、`other`
- **page**：所在頁碼
- **caption_text**：外部圖說文字（從 PDF 或 page preview 讀取）
- **初步 crop_px 估計**：figure 視覺內容的大約邊界（頁面圖片 pixel 座標）

初步 crop_px 估計原則：
- 寧可偏大不要偏小。故意在四邊各外擴 20-40 px，寧可包含一些空白，也不要切到 figure 內容。
- 排除已偵測的 page chrome（Step 2）。
- 排除外部 caption——caption 只存入 `caption_text`，不放進 crop。
- 注意 figure 是否只佔單欄（旁邊有 body text）或跨全頁寬。

同時記錄：
- **unexpected_labeled_figures**：有 figure label 但不該由本 worker 處理的 figure。
- **omitted_figures**：看到候選區域但判斷不是正式 figure 的項目（裝飾圖、watermark 等）。

## Step 4: 裁切與視覺驗證

對每張 figure 執行以下循環：

### 4a. 裁切

用 `crop_and_preview.py` 執行初次裁切。

### 4b. 驗證 boundary preview

讀 boundary preview，檢查 cyan 矩形與周圍 context 的關係：

- **整體 framing**：cyan 矩形是否合理地框住 figure 內容？如果 crop 看起來像整頁、整欄或大頁面條帶，不能標 pass——figure crop 的垂直方向必須緊貼 figure，不得混入正文、外部圖說、page chrome。
- **四邊檢查**：沿每條 cyan 線看，有沒有 figure 內容（文字、線條、圖形）穿過 cyan 線？有的話，該邊太緊，需要放大 crop_px。cyan 線外側有沒有非 figure 內容（caption、正文、page chrome）貼到 cyan 線？有的話，該邊太鬆，需要縮小 crop_px。

### 4c. 驗證 crop preview

讀 crop preview，檢查 figure 內部細節是否完整：座標軸刻度、tick label、panel label、color bar、圖例、比例尺。

### 4d. 底邊精準檢查（按需）

圖表型圖片（折線圖、長條圖、散點圖、熱圖、帶座標軸的示意圖）的底邊風險最高。如果 boundary preview 中底邊看起來緊或不確定，讀 bottom microzoom segments 做精準確認。Microzoom 是底邊裁切判斷的最終依據。

非圖表型圖片（照片、diagram、化學結構）底邊風險較低，boundary preview 通常足夠。

### 4e. 調整與重裁

如果任何檢查發現問題，調整 crop_px，重跑 `crop_and_preview.py`（同一個 crop_id，會覆寫所有檔案），然後回到 4b 重新驗證。

調整原則：
- Figure 內容被切到 → 放大 crop_px（只能放大，不能縮小，因為是 figure 內容穿過 cyan 線）。
- 非 figure 內容混入 → 縮小 crop_px。
- Figure 內容和非 figure 內容因版面交錯而無法乾淨分離 → 優先保留 figure 全部內容，在 `notes` 說明有哪些非 figure 內容被包含以及原因。不要為版面限制標 fail。

### 4f. 記錄驗證結果

每張 figure 確認後，記下 verification 各項結果（見「# figures.json 格式」的 verification 物件）。所有標 pass 的 figure，每個 crop unit 都必須讀過 boundary preview 和 crop preview。

## Step 5: 寫出 figures.json

把所有 figure 的裁切結果、驗證結果寫入 `figures.json`。格式見「# figures.json 格式」。

- 可以記錄 `verification.result = "fail"` 的 figure，但只要任何 figure fail，`status` 就必須是 `incomplete`。
- 如果指定範圍中沒有有標記 figure，`figures` 為空，`status` 設為 `complete`。

## Step 6: 產生相容檔案

現有的 `validate_figure_extraction.py` 會檢查四個 JSON 檔案。為了通過驗證，在 figures.json 寫完後，用以下 Python 腳本從 figures.json 自動產生 `figure_candidates.json`、`figure_index.json`、`figure_decisions.json` 三個相容檔案：

```python
import json, os, glob

worker_dir = "<output_root>"
with open(os.path.join(worker_dir, "figures.json")) as f:
    manifest = json.load(f)

pages_set = set()
for fig in manifest["figures"]:
    for cu in fig["crop_units"]:
        pages_set.add(cu["page"])
all_pages = sorted(pages_set)

# --- figure_candidates.json ---
cand_pages = []
for p in all_pages:
    page_figs = [fig for fig in manifest["figures"]
                 if any(cu["page"] == p for cu in fig["crop_units"])]
    regions, src_regions, candidates = [], [], []
    for fig in page_figs:
        for cu in fig["crop_units"]:
            if cu["page"] != p:
                continue
            rid = f"p{p:03d}_r001"
            sid = f"p{p:03d}_src001"
            cid = f"p{p:03d}_c001"
            regions.append({"region_id": rid, "region_type": "figure_visual",
                "bbox_px": cu["crop_px"], "source": "model_visual",
                "confidence": 0.95, "text": None, "notes": []})
            candidates.append({"candidate_id": cid, "figure_label": fig["figure_label"],
                "visual_region_ids": [rid], "caption_region_ids": [],
                "excluded_region_ids": [], "source_region_ids": [],
                "crop_hint_px": {f"page_{p}": cu["crop_px"]},
                "confidence": 0.95, "risks": []})
    cand_pages.append({"page": p,
        "page_image": f"shared/pages/page_{p}.png",
        "page_preview": f"shared/previews/page_{p}_preview.png",
        "page_size_px": [2481, 3296], "regions": regions,
        "source_regions": [], "figure_candidates": candidates})

candidates_json = {"schema_version": "figure_extraction.v3",
    "worker_id": manifest.get("worker_id", "worker_01"),
    "scope": {"pages": all_pages, "notes": []},
    "pages": cand_pages,
    "unexpected_labeled_figures": manifest.get("unexpected_labeled_figures", []),
    "notes": []}

# --- figure_index.json ---
index_figs = []
for fig in manifest["figures"]:
    pages = [cu["page"] for cu in fig["crop_units"]]
    index_figs.append({"figure_id": fig["figure_id"],
        "figure_label": fig["figure_label"],
        "figure_type": fig["figure_type"],
        "pages": pages, "candidate_ids": fig.get("candidate_ids", []),
        "source_region_ids": fig.get("source_region_ids", []),
        "caption_text": fig["caption_text"], "notes": fig.get("notes", [])})

index_json = {"schema_version": "figure_extraction.v3",
    "worker_id": manifest.get("worker_id", "worker_01"),
    "scope": {"pages": all_pages},
    "figures": index_figs,
    "omitted_candidates": manifest.get("omitted_figures", []),
    "notes": []}

# --- figure_decisions.json ---
dec_figs = []
for fig in manifest["figures"]:
    crop_units = []
    for cu in fig["crop_units"]:
        cu_copy = dict(cu)
        crop_units.append(cu_copy)
    p = fig["crop_units"][0]["page"] if fig["crop_units"] else 0
    dec_figs.append({"figure_id": fig["figure_id"],
        "figure_label": fig["figure_label"],
        "figure_type": fig["figure_type"],
        "candidate_ids": fig.get("candidate_ids", []),
        "source_region_ids": fig.get("source_region_ids", []),
        "visual_region_ids": [], "caption_region_ids": [],
        "excluded_region_ids": [],
        "evidence_read": {
            "page_previews": [f"shared/previews/page_{p}_preview.png"],
            "source_region_previews": []},
        "caption_text": fig["caption_text"],
        "expected_panels": [],
        "crop_units": crop_units,
        "exclusions": [], "rationale": ""})

decisions_json = {"schema_version": "figure_extraction.v3",
    "worker_id": manifest.get("worker_id", "worker_01"),
    "figures": dec_figs, "notes": []}

for name, data in [("figure_candidates.json", candidates_json),
                    ("figure_index.json", index_json),
                    ("figure_decisions.json", decisions_json)]:
    with open(os.path.join(worker_dir, name), "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

用實際的 `output_root` 路徑取代 `<output_root>`，並根據實際 page size 調整 `page_size_px`。

## Step 7: 執行驗證

```bash
python3 agents/scripts/validate_figure_extraction.py \
  "<output_root>" --paper-dir "<paper_dir>"
```

若 validator 回傳 fail，修正後重跑。Validator 通過前不得回報完成。

# figures.json 格式

## 整體結構

```
{
  "schema_version": "figure_extraction.v3",
  "worker_id": "worker_01",
  "status":  →  "complete" 或 "incomplete"（見下方）,
  "figures": [ → figure 物件陣列 ],
  "unexpected_labeled_figures": [ → 見下方 ],
  "omitted_figures": [ → 見下方 ],
  "notes": []
}
```

- **status**：所有 figure 的 `verification.result` 都是 `pass` → `"complete"`；任何一張 `fail` → `"incomplete"`。
- **unexpected_labeled_figures**：有 figure label 但不該由本 worker 處理的 figure。每項包含 `figure_label`、`page`、`reason`、`notes`。`reason` 建議值：`outside_assignment`、`unexpected_page`。
- **omitted_figures**：辨識到但判斷不是正式 figure 的項目。每項包含 `figure_label`（nullable）、`page`、`reason`、`notes`。`reason` 建議值：`not_a_figure`、`table_misclassified`、`equation_misclassified`、`watermark_or_page_chrome`。
- 兩個陣列都必須存在，內容可為空陣列，代表 agent 檢查過、沒有這類情況。

## figure 物件

```
{
  "figure_id":       → filename-safe 字串，例如 "Figure_1"、"Extended_Data_Figure_1"
  "figure_label":    → 顯示 label，例如 "Fig. 1"、"Extended Data Fig. 1"
  "figure_type":     → "main" | "extended" | "supplementary" | "other"
  "candidate_ids":   → 字串陣列，可為空（相容舊格式用）
  "source_region_ids": → 字串陣列，可為空
  "caption_text":    → 外部圖說文字。若沒有外部圖說，填 null。
  "crop_units":      → crop_unit 物件陣列（見下方）
  "evidence_read":   → 見下方
  "verification":    → verification 物件（見下方）
  "notes":           → 字串陣列
}
```

**figure_id** 命名規則：不含空格，例如 `Figure_1`、`Extended_Data_Figure_1`。同一個 figure 的所有 crop_units 共用同一個 figure_id。

**caption_text**：外部圖說永遠不放進 final crop，只存在這個欄位。圖內嵌入的文字（圖內標籤、圖例、座標軸標籤、panel label 等）屬於 figure 內容，應保留在 crop 中。

**evidence_read**：記錄 agent 實際讀過哪些 evidence preview。

```
"evidence_read": {
  "final_crop_previews":   → 字串陣列（artifact-root-relative path）
  "boundary_previews":     → 字串陣列
  "bottom_band_previews":  → 字串陣列
  "bottom_micro_previews": → 字串陣列
}
```

**notes** 條件性必填：`caption_text` 為 null，或情況需要額外解釋時必填。

## crop_unit 物件

每個 crop_unit 代表 figure 的一個裁切區域。單一 figure 通常只有一個 crop_unit。跨頁或同頁多區域 figure 可以有多個 crop_units。

```
{
  "crop_id":            → filename-safe 字串，同 figure 內唯一。
                          單一 crop：和 figure_id 相同。
                          多 crop：figure_id + "_part_1"、"_part_2" 等。
  "page":               → int，頁碼
  "crop_px":            → [x1, y1, x2, y2]，完整解析度頁面圖片的 pixel 座標
  "image_file":         → artifact-root-relative path，例如 "crops/Figure_1.png"
  "preview":            → "previews/Figure_1_preview.png"
  "boundary_preview":   → "previews/Figure_1_boundary_preview.png"
  "top_band":           → 字串陣列，例如 ["previews/Figure_1_top_seg1_preview.png"]
  "left_band":          → 字串陣列
  "right_band":         → 字串陣列
  "bottom_band":        → 字串陣列（可能多個 segment）
  "bottom_micro":       → 字串陣列（可能多個 segment）
  "role":               → 自由文字短描述，例如 "complete figure"、"left panel region"
}
```

**路徑規則**：
- 所有 artifact path 使用 artifact-root-relative path（不含 `figures/workers/worker_01/` 或 `figures/canonical/`）。
- Shared page paths 使用 paper-dir-relative path（例如 `shared/pages/page_3.png`）。

**欄位命名**：
- 裁切座標只叫 `crop_px`，不要寫成 `crop`、`crop_bbox`、`crop_region`。
- 最終裁切圖片路徑只叫 `image_file`，只放在 `crop_units[]` 裡。
- Figure 層不寫 derived 欄位（`pages`、`image_files`、`crop_count`）——這些資訊已由 `crop_units` 表達。

## verification 物件

```
{
  "source_context_checked":   → "pass" | "fail"
  "final_crop_checked":       → "pass" | "fail"
  "boundary_preview_checked": → "pass" | "fail"
  "figure_content_complete":  → "pass" | "fail"
  "external_caption_excluded":→ "pass" | "fail"
  "page_chrome_excluded":     → "pass" | "fail"
  "no_adjacent_content":      → "pass" | "fail"
  "result":                   → "pass" | "fail"
}
```

各欄位語意：

| 欄位 | 意義 | pass 條件 |
|---|---|---|
| `source_context_checked` | agent 讀過 page preview，確認 figure 成員與裁切範圍 | 讀過 page preview |
| `final_crop_checked` | agent 讀過 crop preview，確認 figure 內部細節完整 | 座標軸、tick label、panel label、圖例、比例尺等都在 |
| `boundary_preview_checked` | agent 讀過 boundary preview，確認四邊 framing | cyan 線沒切到 figure 內容，也沒混入應排除內容 |
| `figure_content_complete` | figure 的所有視覺內容都在 crop 中 | 沒有被切掉的 panel、axis、legend |
| `external_caption_excluded` | 外部 caption 不在 crop 中 | caption 文字不在 cyan 矩形內 |
| `page_chrome_excluded` | 頁眉、頁腳、頁碼等不在 crop 中 | 無 page chrome 在 cyan 矩形內 |
| `no_adjacent_content` | 相鄰 figure、table、正文等不在 crop 中 | 無非本 figure 的內容在 cyan 矩形內 |
| `result` | 綜合判定 | 以上全部 pass |

只使用 `pass` 或 `fail`。不使用 `not_applicable`——沒有某種元素時，只要沒有缺失或截斷，就是 `pass`。

## 完整範例

```json
{
  "schema_version": "figure_extraction.v3",
  "worker_id": "worker_01",
  "status": "complete",
  "figures": [
    {
      "figure_id": "Figure_1",
      "figure_label": "Fig. 1",
      "figure_type": "main",
      "candidate_ids": [],
      "source_region_ids": [],
      "caption_text": "Fig. 1 | Generation of idealized scaffolds and computational design of de novo luciferases.",
      "crop_units": [
        {
          "crop_id": "Figure_1",
          "page": 2,
          "crop_px": [88, 90, 2395, 1840],
          "image_file": "crops/Figure_1.png",
          "preview": "previews/Figure_1_preview.png",
          "boundary_preview": "previews/Figure_1_boundary_preview.png",
          "top_band": ["previews/Figure_1_top_seg1_preview.png"],
          "left_band": ["previews/Figure_1_left_seg1_preview.png"],
          "right_band": ["previews/Figure_1_right_seg1_preview.png"],
          "bottom_band": [
            "previews/Figure_1_bottom_seg1_preview.png",
            "previews/Figure_1_bottom_seg2_preview.png"
          ],
          "bottom_micro": [
            "previews/Figure_1_micro_bottom_seg1_preview.png",
            "previews/Figure_1_micro_bottom_seg2_preview.png"
          ],
          "role": "complete figure"
        }
      ],
      "evidence_read": {
        "final_crop_previews": ["previews/Figure_1_preview.png"],
        "boundary_previews": ["previews/Figure_1_boundary_preview.png"],
        "bottom_band_previews": [],
        "bottom_micro_previews": []
      },
      "verification": {
        "source_context_checked": "pass",
        "final_crop_checked": "pass",
        "boundary_preview_checked": "pass",
        "figure_content_complete": "pass",
        "external_caption_excluded": "pass",
        "page_chrome_excluded": "pass",
        "no_adjacent_content": "pass",
        "result": "pass"
      },
      "notes": []
    }
  ],
  "unexpected_labeled_figures": [],
  "omitted_figures": [],
  "notes": []
}
```

# 圖片檔案

| 檔案 | 路徑範例 | 角色 | 由誰產生 |
|---|---|---|---|
| 頁面圖片 | `shared/pages/page_2.png` | 完整解析度原始頁面。所有 crop_px 座標的基準。 | Parent Step 0 |
| Page preview | `shared/previews/page_2_preview.png` | 受限尺寸頁面預覽（max 1568 px），agent 用來掃描辨識 figure。 | Parent Step 0 |
| Final crop | `crops/Figure_1.png` | 完整解析度 final crop，從頁面圖片裁出。 | crop_and_preview.py |
| Crop preview | `previews/Figure_1_preview.png` | Final crop 的受限尺寸預覽。用來檢查 figure **內部細節**。 | crop_and_preview.py |
| Boundary preview | `previews/Figure_1_boundary_preview.png` | Crop 加上四邊 context margin，用 cyan 矩形標出 crop_px。用來檢查**整體 framing**。 | crop_and_preview.py |
| Edge strips | `previews/Figure_1_top_seg1_preview.png` 等 | 各邊 crop boundary 內外兩側的條帶。精確檢查每邊 cyan 線。 | crop_and_preview.py |
| Bottom band | `previews/Figure_1_bottom_seg<N>_preview.png` | 底邊 context layer。確認 axis label、legend 是否被切到。 | crop_and_preview.py |
| Bottom microzoom | `previews/Figure_1_micro_bottom_seg<N>_preview.png` | 底邊 ±50 px 精準放大。底邊裁切判斷的最終依據。 | crop_and_preview.py |

**讀取限制**：agent 只能讀 `_preview` 結尾的圖片。不含 `_preview` 的圖片（完整解析度原檔）不得直接視覺讀取。單張 preview 兩邊不超過 1600 px；一次讀多張時每張不超過 1400 px。

# 規則

## 座標與裁切

- 所有寫入 figures.json 的 `crop_px` 都使用完整解析度頁面圖片的 pixel coordinate `[x1, y1, x2, y2]`。
- Final crop 永遠從頁面圖片裁出，不要從其他中間圖片再裁。
- Crop 貼到 page 邊（crop_px 任一邊等於 0 或等於 page 寬高）是 full-bleed，視覺驗證時不算 fail。

## 圖說與 page chrome

- 外部圖說永遠不放進 final crop，只存入 `caption_text`。
- 圖內嵌入的文字（圖內標籤、圖例、座標軸標籤、panel label、color bar、比例尺）屬於 figure 內容，應保留在 crop 中。
- 若某段文字是否屬於 figure 內部不確定，在 `notes` 說明，不能把不確定的裁切標成 pass。
- 應排除：正文、外部圖說、頁碼、頁眉、頁腳、期刊固定元素、浮水印、相鄰圖表。

## 跨頁與多區域 figure

- 多 panel figure 預設視為同一張 figure，除非原文明確標成不同 figures。
- 跨頁或同頁多區域 figure 可以有多個 `crop_units`，用同一個 `figure_id` 關聯。
- 不要為了做成單一矩形，而把中間正文或其他非 figure 內容一起裁進來。

## 視覺驗證核心規則

**不可以有任何圖片物體跨越 cyan 線。** 沿著每條 cyan 線檢查——只要有任何 figure 內容穿過 cyan 線，該邊就必須調整 crop_px。

驗證時的高頻失敗模式：
- 把整頁、整欄或大頁面條帶當成 figure crop。
- 把外部 caption、頁眉、頁碼裁進 figure。
- 切掉座標軸、圖例、比例尺、panel label、color bar。
- 圖表型圖片底邊的 x 軸刻度與標題、圖例被切掉——底邊風險最高，有疑慮時必須讀 bottom microzoom。

## 機械自檢

寫出 figures.json 後、回報完成前，必須執行 `validate_figure_extraction.py`。Validator 只檢查機械 contract（JSON schema、artifact path、檔案存在、座標範圍），不判斷視覺品質。Validator 失敗時修正後重跑；通過前不得回報完成。

## 空範圍

如果指定範圍中沒有有標記 figure：`figures` 為空，`status` 設為 `complete`。
