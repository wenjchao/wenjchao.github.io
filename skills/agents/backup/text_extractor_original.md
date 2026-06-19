# 目標

這是一份給 text_extractor agent 看的指引。

此 agent 做一件事：從 PDF 擷取字詞層級文字和座標，產出 `extracted.json`。這是 text lane 的第一步，下游 assembler 依賴這些字詞來組裝段落。

- 輸入：paper directory（含 `shared/source.pdf`、`shared/pages/`、`shared/previews/`）。
- 輸出：`<output_root>/extracted.json`。
- 邊界：此 agent 負責擷取和品質檢查。不決定段落邊界、段落類型或段落文字。

# 流程

## 工具

| Script | 用途 |
|---|---|
| `extract.py` | PDF → 字詞層級文字 + 座標。 |

所有 script 在 `agents/scripts/`。

```bash
python3 agents/scripts/extract.py \
  "<paper_dir>/shared/source.pdf" \
  "<output_root>/extracted.json"
```

`extract.py` 會產出 `blocks`，但下游不使用。Extractor 只需確保 `words` 和 `artifact_regions` 正確。

## Step 1: 執行擷取

跑 `extract.py`，產出 `extracted.json` 初稿。

## Step 2: 逐頁品質檢查

頁面圖片是 ground truth。`extract.py` 的輸出是候選，需要對照頁面圖片驗證。

對每頁：
1. 讀 `extracted.json` 中該頁的 `words`、`artifact_regions`、`qc_notes`。
2. 如果版面、符號或 page chrome 可疑，讀對應的 page preview（`shared/previews/page_N_preview.png`）比對。
3. 判斷該頁乾淨、需要局部修正、或應記錄 `qc_notes` 警告。

檢查項目：
- 遺漏或重複字詞。
- 拆字（一個字被拆成多個 word entry）。
- 黏字（多個字被合成一個 word entry）。
- 未解決的 PUA 或 `(cid:N)` 殘留。
- 科學符號或單位損壞。
- 明顯錯誤的邊界框。

優先檢查：已有 `qc_notes` 的頁面、含大量 page chrome 的頁面、表格或圖靠近正文的頁面。乾淨頁面快速通過。

修復邊界：局部、機械式的修正可以做（拆字修復、PUA 替換）。不要決定段落邊界或改寫文字。無法安全修正的問題記錄在 `qc_notes`。

## Step 3: 寫出 extracted.json 並自檢

從 `extract.py` 的輸出中去除 `blocks`，寫出最終 `extracted.json`（格式見下方 `# 格式`），然後做 local self-check：
- JSON 可 parse。
- 每頁有 `page`（整數）、`width_pt`、`height_pt`、`words`（陣列）。
- 每個 word 有 `id`（唯一，格式 `p<NNN>_w<NNNNNN>`）、`text`（非空）、`bbox`（4 個數字）。
- `total_pages` 和 `pages` 陣列長度一致。

# 格式

`extracted.json`。

## Example

```json
{
  "source_pdf": "shared/source.pdf",
  "total_pages": 12,
  "pages": [
    {
      "page": 1,
      "width_pt": 612.0,
      "height_pt": 792.0,
      "rotation": 0,
      "words": [
        {
          "id": "p001_w000001",
          "text": "Abstract",
          "bbox": [72.0, 96.4, 128.2, 110.8],
          "font_name": "Helvetica-Bold",
          "font_size": 12.0
        }
      ],
      "artifact_regions": [
        {
          "id": "p001_a00001",
          "bbox": [0.0, 0.0, 612.0, 54.0],
          "type": "journal_header_candidate"
        }
      ],
      "qc_notes": []
    }
  ],
  "metadata": {}
}
```

## 規則

- **`words`**：字詞層級座標是預設表示。必要時可加 `chars` 陣列提供字元層級座標（CJK 或特殊符號）。
- **`artifact_regions`**：圖、page chrome、表格等非文字區域的候選。`type` 建議值：`figure_candidate`、`table_candidate`、`journal_header_candidate`、`footer_candidate`、`margin_candidate`。
- **`qc_notes`**：品質檢查中發現但無法安全修正的問題。下游 assembler 會參考這些 notes 來識別風險區域。
- 不要輸出 `blocks`、`pages[].full_text` 或其他聚合欄位。下游從 `words` 組裝一切。
