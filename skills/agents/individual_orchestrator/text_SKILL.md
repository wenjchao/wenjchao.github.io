# 目標

這是一份給 pipeline orchestrator 看的指引。

此流程使用場景與目標：
- 輸入：一個 PDF 檔案。
- 輸出：後續可重組成 HTML / Markdown 的 lane artifacts。
- 目標：最大程度讓輸出的 HTML / Markdown 貼近原始 PDF，以利後續閱讀、分析與筆記。

本檔案描述 text lane。

# 結構

## 目錄結構

```text
<paper_dir>/
  shared/
    source.pdf
    pages/              # 完整解析度頁面圖片
    previews/           # 受限尺寸 page previews
  text/
    scanner/            # scanner 輸出
      extracted.json
    worker/             # worker 輸出
      round_00/
        worker_01/
          paragraphs.json
        worker_02/
          paragraphs.json
        worker_03/
          paragraphs.json
        merged/         # merger 輸出
          paragraphs.json
      round_01/
        worker_01/      # repair 通常只需一個 worker
    reviewer/           # reviewer 輸出
      round_00/
        reviewer_01/    # 可有多個平行 reviewer
          visual_review.json
        reviewer_02/
          visual_review.json
      round_01/
        reviewer_01/
    canonical/          # live state — 所有 downstream agent 的唯一讀取來源
      extracted.json
      paragraphs.json
      visual_review.json
```

`canonical/` 是所有下游 agent 的唯一 handoff root。

### Round 命名

- `worker/round_00/` + `reviewer/round_00/`：initial assembly + 第一次 review。
- `worker/round_01/` + `reviewer/round_01/`：修 round_00 review 發現的問題 + re-review。
- 依此類推。不覆寫舊 round。

## 工具

所有 script 在 `agents/scripts/`。

| Script | 用途 |
|---|---|
| `render_pages.py` | PDF → 完整解析度頁面圖片 |
| `make_image_preview.py` | 頁面圖片 → 受限尺寸 page preview |
| `extract.py` | PDF → 字詞層級文字 + 座標（extractor 呼叫） |

## Subagent prompts

| Prompt | 角色 |
|---|---|
| `subagent_prompts/text_scanner.md` | 從 PDF 擷取字詞層級文字 + 座標，產出 extracted.json |
| `subagent_prompts/text_worker.md` | 讀 extracted.json + source.pdf + page previews，從 word 座標和版面分析組裝段落，產出 paragraphs.json。同時用於 initial assembly 和 repair。 |
| `subagent_prompts/text_merger.md` | 合併多個 worker 的 paragraphs 輸出，reconcile overlap 區域，產出合併後的 paragraphs.json |
| `subagent_prompts/text_reviewer.md` | 讀 canonical paragraphs.json + extracted.json，審查段落品質（文字忠實度 + 來源追溯 + 覆蓋 + 連貫性），產出 visual_review.json |

# 流程

Pipeline 是 scan → parallel assemble + merge → review → repair loop。

Parent 只做三種動作：
- **[script]** 跑 render/preview/extract script（機械操作）
- **[spawn agent]** 啟動 subagent（委派判斷）
- **[mechanical]** 搬檔或組裝 JSON（不需判斷）

所有段落組裝和品質判斷由 subagent 做。Parent 不組裝段落、不判斷邊界、不改寫文字。

Subagent 規則：
- 所有 scanner、worker、reviewer 都要啟動獨立 subagent。不得用 parent 的工作取代 subagent。
- Subagent prompt 必須使用指定的 prompt 檔案全文，不得摘要、改寫、截斷。Parent 唯一可以做的修改是在末尾附加 assignment block。
- Agent 啟動失敗 → 先修正 prompt/tool/context，重試。仍失敗 → 回報 blocked。

## Step 0: 前置工作

**[script]** 建立 paper directory，render pages，建立 page previews。

```bash
mkdir -p <paper_dir>/shared/pages <paper_dir>/shared/previews \
  <paper_dir>/text/{scanner,worker,reviewer,canonical}

cp <source.pdf> <paper_dir>/shared/source.pdf

python3 agents/scripts/render_pages.py \
  "<paper_dir>/shared/source.pdf" "<paper_dir>/shared/pages" --dpi 300

# 為每頁建立 preview
for page in <paper_dir>/shared/pages/page_*.png; do
  base=$(basename "$page" .png)
  python3 agents/scripts/make_image_preview.py \
    "$page" "<paper_dir>/shared/previews/${base}_preview.png" --max-dim 1568
done
```

如果 shared/ 已由其他 lane 建立，跳過 render，直接建立 `text/` 目錄結構。

## Step 1: Scan

### 1a. [spawn agent] 啟動 text_scanner

Prompt = `text_scanner.md` 全文 + assignment block：

```text
---
## Assignment
paper_dir: <paper_dir>
output_root: <paper_dir>/text/scanner
```

Scanner 跑 `extract.py`，逐頁 QC，**去除 blocks 後**寫出 `<paper_dir>/text/scanner/extracted.json`。

### 1b. [mechanical] Promote to canonical

把 `scanner/extracted.json` 複製到 `canonical/`。

## Step 2: Assemble（平行 + merge）

Initial assembly 使用多個 worker 平行處理，每個 worker 負責一段重疊的頁面範圍。完成後由 merger 合併。

### 2a. [mechanical] 決定 worker 分配

Parent 用頁碼範圍機械切分，不需要讀 PDF 判斷章節結構。原則：
- 每個 worker 分配 6-12 頁。
- 相鄰 worker 之間有 2-3 頁 overlap（overlap 頁面被兩個 worker 同時處理）。
- References 頁面獨立成一個 worker（機械性高）。
- 每個 worker 的 assignment 標明 `owned_pages`（專屬）和 `overlap_pages`（共享）。

典型 24 頁論文的分配範例（references 從 page 20 開始）：
- worker_01: pages 1-8（owned: 1-6, overlap: 7-8）
- worker_02: pages 7-18（overlap: 7-8, owned: 9-16, overlap: 17-18）
- worker_03: pages 17-20（overlap: 17-18, owned: 19-20，body + back matter）
- worker_04: pages 20-24（owned: 20-24，references 專用）

### 2b. [spawn agents] 平行啟動多個 text_worker

每個 worker 使用 `text_worker.md` 全文 + assignment block：

```text
---
## Assignment
paper_dir: <paper_dir>
mode: initial
worker_id: worker_01
output_root: <paper_dir>/text/worker/round_00/worker_01
pages: [1, 2, 3, 4, 5, 6, 7, 8]
owned_pages: [1, 2, 3, 4, 5, 6]
overlap_pages: [7, 8]
```

所有 workers 平行啟動。每個 worker 組裝其 `pages` 範圍內的所有段落（包含 overlap 頁面）。Worker 不需要知道其他 worker 的存在。

### 2c. [spawn agent] 啟動 text_merger

所有 workers 完成後，啟動 merger。Prompt = `text_merger.md` 全文 + assignment block：

```text
---
## Assignment
paper_dir: <paper_dir>
output_root: <paper_dir>/text/worker/round_00/merged

workers:
  - worker_id: worker_01
    path: <paper_dir>/text/worker/round_00/worker_01/paragraphs.json
    pages: [1, 2, 3, 4, 5, 6, 7, 8]
    owned_pages: [1, 2, 3, 4, 5, 6]
    overlap_pages: [7, 8]
  - worker_id: worker_02
    path: <paper_dir>/text/worker/round_00/worker_02/paragraphs.json
    pages: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    owned_pages: [9, 10, 11, 12, 13, 14, 15, 16]
    overlap_pages: [7, 8, 17, 18]
  - worker_id: worker_03
    path: <paper_dir>/text/worker/round_00/worker_03/paragraphs.json
    pages: [17, 18, 19, 20, 21, 22, 23, 24]
    owned_pages: [19, 20, 21, 22, 23, 24]
    overlap_pages: [17, 18]
```

Merger 在 overlap 區域選擇最佳版本（通常是能看到更多相關頁面的 worker），reconcile 邊界，重新編號，寫出合併後的 `paragraphs.json`。

### 2d. [mechanical] Promote to canonical

把 merger 的 `paragraphs.json` 複製到 `canonical/`。

## Step 3: Review（可平行）

Review 可以用多個 reviewer 平行處理，每個 reviewer 審查對應頁面的段落。

### 3a. [mechanical] 決定 reviewer 分配

不必沿用 Step 2a 的頁面範圍分配。每個 reviewer 審查「段落所在頁面落在其範圍內」的段落。Coverage 檢查也按同樣的頁面範圍。

### 3b. [spawn agents] 平行啟動多個 text_reviewer

每個 reviewer 使用 `text_reviewer.md` 全文 + assignment block：

```text
---
## Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
output_root: <paper_dir>/text/reviewer/round_00/reviewer_01
paragraph_ids: [1, 2, ..., 80]
```

### 3c. [mechanical] 合併 review 並 promote to canonical

Parent 合併所有 reviewer 的 `visual_review.json`：對每個段落取所有 reviewer findings 的 union（overlap 區域的段落可能被兩個 reviewer 審查，同一 condition + severity 的 finding 去重）。合併後的 `visual_review.json` 必須涵蓋所有段落（1 到 N）。複製到 `canonical/`。

## Step 4: Gate

**[mechanical]** Parent 讀 `canonical/visual_review.json`：

- 所有段落的 `findings` 都是空陣列 → text lane close。
- 有 `severity: "required"` 的 findings → 進入 Step 5。
- Repair round limit 達到（預設 4 輪）→ 停止並回報 blocked。

Parent 不得自己做段落組裝判斷來 override reviewer。Repair output 有 fail 段落時不得靜默 close。

## Step 5: Repair

Worker 直接從 canonical 讀取 `paragraphs.json` + `extracted.json` + `visual_review.json`，不需要 parent 建立中間檔案。

### 5a. [spawn agent] 啟動 text_worker（repair mode）

Parent 從 `canonical/visual_review.json` 取出有 `severity: "required"` finding 的 paragraph_ids。

```text
---
## Assignment
paper_dir: <paper_dir>
mode: repair
worker_id: worker_01
output_root: <paper_dir>/text/worker/round_01/worker_01
paragraph_ids: [28, 29, null]
```

`paragraph_ids` 中的 `null` 表示不屬於特定段落的問題（如 missing_content），worker 需要在對應區域新增段落。

### 5b. [mechanical] Promote repair to canonical

Repair worker 輸出完整的 `paragraphs.json`（不只修復的段落），並在頂層包含 `modified_paragraphs`（新編號的 list）。直接複製到 `canonical/`，取代舊檔。

### 5c. 回到 Step 3（re-review）

回到 Step 3，但 `paragraph_ids` 使用 repair 輸出的 `modified_paragraphs`，只對被修改的段落做完整審查。
