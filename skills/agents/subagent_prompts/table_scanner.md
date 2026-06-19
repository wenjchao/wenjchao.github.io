# 目標

這是一份給 table_scanner agent 看的指引。

此流程使用場景與目標：
- 輸入：一個 paper directory（含 `shared/pages/`、`shared/previews/`）、pages 範圍。
- 輸出：`<output_root>/table_plan.json`
- 目標：辨識 paper 中所有有標籤的表格，產出一份表格清單給下游 worker agent 使用。
- 邊界：此 agent 只負責辨識。不裁切表格、不擷取結構化資料、不寫 tables.json。

# 流程

## Step 1: 確認前置條件

確認 `shared/pages/page_N.png` 和 `shared/previews/page_N_preview.png` 對所有 assignment 頁面都存在。若缺少，回報 blocked。

## Step 2: 掃描頁面並辨識表格

逐頁讀 page preview，辨識所有有標籤的表格（"Table"、"TABLE"、"Extended Data Table"、"Supplementary Table" 等 label）。頁面圖片是 ground truth——PDF 文字或表格輔助工具只提供候選證據，表格範圍必須根據視覺證據決定。

- 每張表格的範圍包含：表格標籤、標題、全部欄標題、全部資料列、全部註腳。
- 掃描所有頁面，包括附錄、補充材料和文末材料。不要假設表格只出現在正文。
- 一次掃完所有頁面，不得 defer 到「後續 pass」。
- 跨頁表格記錄到同一個 table 的多個 crop_units 裡（每頁一個 entry）。
- 排除嵌在圖面板中的表格（除非使用者明確要求）。
- 排除頁首/頁尾、正文、圖說、方程式、頁面固定元素（期刊頁首、作者列、頁碼、分隔線、出版商 logo、DOI 頁尾）。
- 看到疑似表格但不列入的項目，記錄到 `excluded`。`excluded` 只放「判斷後確定不是有標籤表格」的候選，不放「是表格但決定稍後處理」。
- `caption_text` 含上標、化學式、相似字元時，用 Read tool 讀 `shared/source.pdf` 對應頁面確認正確文字。

## Step 3: 寫出 table_plan.json 並自檢

寫出 `table_plan.json`（格式見下方 `# 格式`），然後做 local self-check：
- JSON 可 parse。
- `schema_version` 是 `"table_plan.v1"`。
- `tables` 是陣列。
- 每個 table 有 `table_id`（唯一、filename-safe）、`table_label`（非空）、`table_type`（`main`/`extended`/`supplementary`/`other`）、`caption_text`、`crop_units`（非空陣列）。
- 每個 crop unit 有 `page`（整數）和 `crop_px`（`[x1, y1, x2, y2]`，四個整數，`0 ≤ x1 < x2`，`0 ≤ y1 < y2`）。
- `excluded` 是陣列（可為空）。
- 頁面交叉檢查：對每個表格重新讀取該頁 page preview，確認表格在該頁可見、`page` 值和讀取的檔名頁碼一致。

# 格式

`table_plan.json`，`schema_version: "table_plan.v1"`。

## Example

```json
{
  "schema_version": "table_plan.v1",
  "tables": [
    {
      "table_id": "Table_1",                           // filename-safe，不含空格
      "table_label": "Table 1",                        // 照 paper 原文的顯示 label
      "table_type": "main",                            // main|extended|supplementary|other
      "caption_text": "Table 1. Summary of electrochemical sensor performance...",
      "crop_units": [
        {"page": 8, "crop_px": [60, 200, 2420, 3100]}
      ]
    },
    {
      "table_id": "Table_3",
      "table_label": "Table 3",
      "table_type": "main",
      "caption_text": "Table 3. Drugs detected by electrochemical sensors...",
      "crop_units": [                                  // 跨頁表格：每頁一個 entry
        {"page": 10, "crop_px": [60, 200, 2420, 3200]},
        {"page": 11, "crop_px": [60, 100, 2420, 2800]}
      ]
    }
  ],
  "excluded": [],                                      // 不列入 tables 的項目，陣列必須存在
  "notes": []
}
```

## 規則

- **`caption_text`**：表格標籤 + 標題文字。表格內的欄標題、資料列、註腳屬於表格內容，不算 caption。
- **`crop_units`**：每個 entry 有 `page`（int）和 `crop_px`（`[x1, y1, x2, y2]`，完整解析度頁面圖片 pixel 座標，從 page preview 用 scale factor 換算）。單頁表格一個 entry；跨頁表格多個 entry（每頁一個）。
- **`crop_px`**：**寧可大不要小**——涵蓋表格可能佔據的最大範圍（含標籤、標題、全部欄標題、全部資料列、全部註腳）。Worker 會用 boundary preview 收緊，hint 太小則 worker 要多輪擴展。排除外部正文和明顯的 page chrome（頁眉、頁碼）。
- **`excluded`**：不列入 tables 的項目。每項：`label`（nullable）、`page`、`reason`、`notes`。`reason` 建議值：`outside_assignment`、`not_a_table`、`embedded_in_figure`、`figure_misclassified`、`equation_misclassified`、`page_chrome`。
