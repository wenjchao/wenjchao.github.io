# 目標

這是一份給 pipeline orchestrator 看的指引。

此流程使用場景與目標：
- 輸入：四條 lane（figure、equation、table、text）的 canonical 產出 + 來源 PDF（`shared/source.pdf`）。
- 輸出：完整可讀的論文（`paper.html`）。
- 目標：輸出應讀起來像原始論文——正確文字、LaTeX 方程式、HTML 表格、圖片，全部按正確順序排列。

本檔案描述 reassembly lane。此 lane 在四條 extraction lane 全部 close 後才啟動。

# 結構

## 目錄結構

```text
<paper_dir>/
  shared/
    source.pdf
    pages/
    previews/
  figures/canonical/          # figure lane 產出（只讀）
  equations/canonical/        # equation lane 產出（只讀）
  tables/canonical/           # table lane 產出（只讀）
  text/canonical/             # text lane 產出（只讀）
  reassembly/
    worker/
      round_00/
        worker_01/
          paper.html
          figures/
      round_01/
        worker_01/
    reviewer/
      round_00/
        reviewer_01/
          visual_review.json
      round_01/
        reviewer_01/
    canonical/
      paper.html
      visual_review.json
      figures/
```

`canonical/` 是 live state。四條 extraction lane 的 canonical 對 reassembly lane 是只讀的。

## Subagent prompts

| Prompt | 角色 |
|---|---|
| `subagent_prompts/reassembly_worker.md` | 讀四條 lane 的 canonical + source.pdf，組出 paper.html |
| `subagent_prompts/reassembly_reviewer.md` | 審查 paper.html 是否忠實於 PDF，產出 visual_review.json |

# 流程

Pipeline 是 reassemble → review → repair loop。

Parent 只做兩種動作：
- **[spawn agent]** 啟動 subagent（委派判斷）
- **[mechanical]** 搬檔（不需判斷）

所有內容決策由 subagent 做。Parent 不清理文字、不決定 float 位置、不判斷忠實度。

Subagent 規則：
- 所有 worker、reviewer 都要啟動獨立 subagent。不得用 parent 的工作取代 subagent。
- Subagent prompt 必須使用指定的 prompt 檔案全文，不得摘要、改寫、截斷。Parent 唯一可以做的修改是在末尾附加 assignment block。
- Agent 啟動失敗 → 先修正 prompt/tool/context，重試。仍失敗 → 回報 blocked。

## Step 0: 確認前置條件

確認四條 extraction lane 都已 close（canonical 中沒有 required findings）。建立 `reassembly/` 目錄結構。

## Step 1: Reassemble

### 1a. [spawn agent] 啟動 reassembly_worker

```text
---
## Assignment
paper_dir: <paper_dir>
mode: initial
worker_id: worker_01
output_root: <paper_dir>/reassembly/worker/round_00/worker_01
```

Worker 讀四條 lane 的 canonical + source.pdf，寫出 `paper.html`、`figures/`。

### 1b. [mechanical] Promote to canonical

把 worker 的 `paper.html`、`figures/` 複製到 `reassembly/canonical/`。

## Step 2: Review

### 2a. [spawn agent] 啟動 reassembly_reviewer

```text
---
## Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
output_root: <paper_dir>/reassembly/reviewer/round_00/reviewer_01
```

Reviewer 讀 `reassembly/canonical/paper.html`，對照 source.pdf，審查忠實度，寫出 `visual_review.json`。

### 2b. [mechanical] Promote review to canonical

把 reviewer 的 `visual_review.json` 複製到 `reassembly/canonical/`。

## Step 3: Gate

**[mechanical]** Parent 讀 `reassembly/canonical/visual_review.json`：

- `findings` 為空 → reassembly lane close。論文完成。
- 有 `severity: "required"` 的 findings → 進入 Step 4。
- Repair round limit 達到（預設 4 輪）→ 停止並回報 blocked。

Parent 不得自己做忠實度判斷來 override reviewer。

## Step 4: Repair

### 4a. [spawn agent] 啟動 reassembly_worker（repair mode）

```text
---
## Assignment
paper_dir: <paper_dir>
mode: repair
worker_id: worker_01
output_root: <paper_dir>/reassembly/worker/round_01/worker_01
```

Worker 讀 `reassembly/canonical/paper.html` + `reassembly/canonical/visual_review.json`，根據 findings 直接修正 `paper.html`。

### 4b. [mechanical] Promote repair to canonical

把 worker 的 `paper.html`、`figures/` 覆蓋 `reassembly/canonical/`。

### 4c. 回到 Step 2

回到 Step 2，啟動 reviewer re-review。
