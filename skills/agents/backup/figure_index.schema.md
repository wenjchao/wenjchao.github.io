# figure_index.json

`schema_version`: `"figure_extraction.v3"`

## Enums

- `figure_type`：
  - `main`：主文 figure（Fig. 1, Fig. 2 等）
  - `extended`：Extended Data figure
  - `supplementary`：Supplementary figure
  - `other`：其他（例如 graphical abstract）
- `omitted_candidates[].reason`（建議值，可自訂 snake_case）：
  - `not_a_figure`：不是 figure（例如裝飾性圖片）
  - `duplicate_of_other_candidate`：和另一個 candidate 重複
  - `table_misclassified`：實際上是 table
  - `equation_misclassified`：實際上是 equation
  - `watermark_or_page_chrome`：浮水印或頁面固定元素

## Fields

- `scope.pages`: int array
- `figures[]`:
  - `figure_id`: filename-safe string (e.g. `Figure_1`, `Extended_Data_Figure_1`)
  - `figure_label`: display label (e.g. `Fig. 1`, `Extended Data Fig. 1`)
  - `figure_type`
  - `pages`: int array (此階段還沒有 `crop_units`，所以 figure 層保留 `pages`)
  - `candidate_ids`, `source_region_ids`
  - `caption_text`
  - `notes`
- `omitted_candidates[]`: `candidate_id`, `reason`, `notes` (conditional)

## Example

```json
{
  "schema_version": "figure_extraction.v3",
  "worker_id": "worker_01",
  "scope": {
    "pages": [3, 4]
  },
  "figures": [
    {
      "figure_id": "Figure_1",
      "figure_label": "Fig. 1",
      "figure_type": "main",
      "pages": [3],
      "candidate_ids": ["p003_c001"],
      "source_region_ids": ["p003_src001"],
      "caption_text": "Fig. 1. Short caption title...",
      "notes": []
    }
  ],
  "omitted_candidates": [],
  "notes": []
}
```
