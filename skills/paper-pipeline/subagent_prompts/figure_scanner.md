# 目標

這是一份給 figure_scanner agent 看的指引。

此流程使用場景與目標：
- 輸入：一個 paper directory（含 `shared/pages/`、`shared/previews/`）、pages 範圍。
- 輸出：`<output_root>/figure_plan.json`
- 目標：辨識 paper 中所有有標記的 figure，產出一份圖表清單給下游 worker agent 使用。
- 邊界：此 agent 只負責辨識。不裁切 figure、不產生 crop 圖片、不寫 figures.json。

# 流程

## Step 1: 確認前置條件

確認 `shared/pages/page_N.png` 和 `shared/previews/page_N_preview.png` 對所有 assignment 頁面都存在。若缺少，回報 blocked。

## Step 2: 掃描頁面並辨識圖表

逐頁讀 page preview，辨識所有有標記的 figure（"Fig."、"Figure"、"Extended Data Fig." 等 label）。

- 只要是與文章內容有關的圖片，即使是插圖、示意圖，或是沒有帶任何 figure label 的圖片，都要列入 figures。
- 表格和方程式不列入 figures，有其餘的 pipeline agent 負責。
- 對每張 figure，填寫一個 figure 物件，如果因為跨頁、跨欄因此被切成多個部分，記錄到 crop_units 裡面。
- 看到疑似圖但不列入 figures 的項目，記錄到 `excluded`。

## Step 3: 寫出 figure_plan.json 並自檢

寫出 `figure_plan.json`（格式見下方 `# 格式`），然後做 local self-check：
- JSON 可 parse。
- `schema_version` 是 `"figure_plan.v1"`。
- `figures` 是陣列。
- 每個 figure 有 `figure_id`（唯一、filename-safe）、`figure_label`（非空）、`figure_type`（`main`/`extended`/`supplementary`/`other`）、`caption_text`、`crop_units`（非空陣列）。
- 每個 crop unit 有 `page`（整數）和 `crop_px`（`[x1, y1, x2, y2]`，四個整數，`0 ≤ x1 < x2`，`0 ≤ y1 < y2`）。
- `excluded` 是陣列（可為空）。

# 格式

`figure_plan.json`，`schema_version: "figure_plan.v1"`。

## Example

```json
{
  "schema_version": "figure_plan.v1",
  "figures": [
    {
      "figure_id": "Figure_1",                       // filename-safe，不含空格
      "figure_label": "Fig. 1",                      // 照 paper 原文的顯示 label
      "figure_type": "main",                         // main|extended|supplementary|other
      "caption_text": "Fig. 1 | Generation of idealized scaffolds...",
      "crop_units": [
        {"page": 2, "crop_px": [60, 80, 2420, 1900]}
      ]
    }
  ],
  "excluded": [],                                    // 不列入 figures 的項目，陣列必須存在
  "notes": []
}
```

## 規則

- **`caption_text`**：外部圖說文字。圖內嵌入的文字（圖例、座標軸標籤、panel label）屬於 figure 內容，不算 caption。
- **`crop_units`**：每個 entry 有 `page`（int）和 `crop_px`（`[x1, y1, x2, y2]`，完整解析度頁面圖片 pixel 座標，從 page preview 用 scale factor 換算）。單頁 figure 一個 entry；跨頁 figure 多個 entry。
- **`crop_px`**：**寧可大不要小**——涵蓋 figure 可能佔據的最大範圍。Worker 會用 boundary preview 收緊，hint 太小則 worker 要多輪擴展。排除外部 caption 和明顯的 page chrome（頁眉、頁碼）。
- **`excluded`**：不列入 figures 的項目。每項：`figure_label`（nullable）、`page`、`reason`、`notes`。`reason` 建議值：`outside_assignment`、`not_a_figure`、`table_misclassified`、`equation_misclassified`、`watermark_or_page_chrome`。
