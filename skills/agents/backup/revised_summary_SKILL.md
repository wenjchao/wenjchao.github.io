# Revised Summary Pipeline

## 目標

這是一份給 pipeline orchestrator 看的指引。

此 lane 的輸入與舊 `summary` lane 相同：一篇已準備好的科學論文（`<paper_dir>/reassembly/canonical/paper.html`）。輸出也是一份可與舊 lane 競賽的 layer-1 中文摘要。

此 lane 的第一優先不是「最短、最乾淨、最像論文摘要」，而是「第一次接觸這篇論文的讀者能順著讀懂」。忠實度是紅線；在忠實的前提下，教學性、中文流暢度與讀者可轉述性高於資訊密度與 token 效率。

此 lane 也必須比上一版 `revised_summary` 精簡。上一版把 fact map、brief、draft review、refine、final review 全部拆開，token 成本高，卻沒有穩定保護教學性。新版改用少量完整教學稿作為主要搜尋單位，再用 reviewer 挑出最有教學價值的稿子，最後由 synthesizer 重新定稿。它不做多層中間 artifact 競賽，也不依賴局部 repair 拯救壞中文。

最終輸出：
- `<paper_dir>/revised_summary/canonical/summary.json`
- `<paper_dir>/revised_summary/canonical/<paper_id>_revised_summary.md`

`summary.json` 使用 `summary_final.v1`，shape 對齊舊 `summary/canonical/summary.json`，方便下游直接比較。

## 參數

| 變數 | 預設 | 說明 |
|---|---:|---|
| `{{TEACHER_WORKER_COUNT}}` | 6 | 完整教學稿 worker 數量。這是主要搜尋成本。 |
| `{{TEACHER_REVIEWER_COUNT}}` | 3 | 第一輪 reviewer 數量。Reviewer 只評完整稿，不評中間 brief。 |
| `{{SELECTED_CANDIDATE_COUNT}}` | 3 | 進入 synthesis 的 teacher candidates 數量。 |
| `{{SYNTHESIZER_COUNT}}` | 2 | 根據 top teacher candidates 重新定稿的 synthesizer 數量。 |
| `{{FINAL_JUDGE_COUNT}}` | 1 | 最終 judge 數量。預設單一 judge，降低 token。 |
| `{{TOP_K}}` | 3 | final `summary.json` 保留的摘要數量。 |
| `{{VOTES_PER_BALLOT}}` | 7 | 每位 reviewer 或 judge 的選票總數。 |
| `{{TARGET_MIN_CHARS}}` | 1200 | 完整摘要建議最少中文字數。 |
| `{{TARGET_MAX_CHARS}}` | 1600 | 完整摘要建議最多中文字數。 |

`TARGET_*` 是教學摘要的軟範圍。若刪到 `TARGET_MAX_CHARS` 會破壞第一次讀者的理解路徑，worker 可以略超，但必須在 `notes` 說明保留理由。

## 流程

Parent 只做兩種動作：
- **[spawn agent]** 啟動 subagent。
- **[mechanical]** 搬檔、改 id、聚合票數、抽取 JSON。

所有內容撰寫、忠實度判斷、語感判斷由 subagent 做。Parent 不改寫正文，不判斷哪篇比較好。

Subagent prompt 必須使用指定 prompt 檔案全文，不得摘要、改寫、截斷。Parent 唯一可以做的修改是在末尾附加 assignment block。

### Step 0: 準備

**[mechanical]** 建立 revised_summary 目錄。`paper_file = <paper_dir>/reassembly/canonical/paper.html`。

### Step 1: Teacher Drafts

**[spawn agent]** 平行啟動 `{{TEACHER_WORKER_COUNT}}` 個 `revised_summary_teacher_worker`：

```text
---
Assignment
paper_dir: <paper_dir>
paper_file: <paper_file>
teacher_id: teacher_01
target_min_chars: <{{TARGET_MIN_CHARS}}>
target_max_chars: <{{TARGET_MAX_CHARS}}>
output_root: <paper_dir>/revised_summary/teacher/worker/round_00/teacher_01
```

Teacher worker 直接寫完整中文教學稿。它可以輸出 compact teaching trace，但不輸出舊 `summary_worker` 那種巨大 `thinking_process`。Trace 的用途是讓 reviewer 看見它如何處理第一次讀者會卡住的概念。

**[mechanical] Promote**
1. 收集 `teacher/worker/round_00/teacher_*/output.json`。
2. 確認 `schema_version` = `"revised_summary_candidate.v1"`、`stage` = `"teacher_draft"`。
3. 將 `candidate_id` 依 assignment 固定為 `teacher_XX`，寫入 `canonical/teacher/candidate/teacher_XX.json`。

### Step 2: Teaching Review

**[spawn agent]** 平行啟動 `{{TEACHER_REVIEWER_COUNT}}` 個 `revised_summary_teacher_reviewer`：

```text
---
Assignment
paper_dir: <paper_dir>
paper_file: <paper_file>
reviewer_id: reviewer_A
selected_count: <{{SELECTED_CANDIDATE_COUNT}}>
votes_per_ballot: <{{VOTES_PER_BALLOT}}>
output_root: <paper_dir>/revised_summary/teacher/reviewer/round_00/reviewer_A
```

Reviewer 只評完整稿，不要求 repair plan。評分順序是：
1. 忠實度是否有紅線錯誤。
2. 第一次讀者能不能順著讀懂，且讀完能用自己的話轉述。
3. 中文是否像自然散文，不像論文摘要、翻譯稿或筆記。
4. 方法是否具體到能理解「作者怎麼知道」，但沒有變成 protocol。
5. 證據與限制是否足以讓主線可信。

短而乾淨但缺乏教學路徑的稿子要降權。Reviewer 不應獎勵過度壓縮。

**[mechanical] Promote + tally**
1. 複製 reviewer `review.json` 到 `canonical/teacher/voting/review_X.json`。
2. 聚合 `global_evaluation.votes`，寫 `canonical/teacher/vote_tally.json`。
3. 取票數前 `{{SELECTED_CANDIDATE_COUNT}}`，寫 `canonical/teacher/selected_candidates.json`。
4. Sanity check：總票數 = `{{TEACHER_REVIEWER_COUNT}} * {{VOTES_PER_BALLOT}}`。

### Step 3: Synthesis

**[spawn agent]** 平行啟動 `{{SYNTHESIZER_COUNT}}` 個 `revised_summary_synthesizer`：

```text
---
Assignment
paper_dir: <paper_dir>
paper_file: <paper_file>
synthesizer_id: finalist_01
selected_candidates_path: <paper_dir>/revised_summary/canonical/teacher/selected_candidates.json
teacher_vote_tally_path: <paper_dir>/revised_summary/canonical/teacher/vote_tally.json
teacher_reviews_dir: <paper_dir>/revised_summary/canonical/teacher/voting
target_min_chars: <{{TARGET_MIN_CHARS}}>
target_max_chars: <{{TARGET_MAX_CHARS}}>
output_root: <paper_dir>/revised_summary/synthesis/worker/round_00/finalist_01
```

Synthesizer 不是 repair worker。它讀 top teacher candidates 與 reviewer 意見，借用其中最有教學價值的 moves，從頭寫一篇新的 final candidate。它可以保留好標題、好鋪墊、好比喻、好數字支點，但不能把幾篇稿子硬接成拼貼文。

**[mechanical] Promote**
1. 收集 `synthesis/worker/round_00/finalist_*/output.json`。
2. 確認 `schema_version` = `"revised_summary_candidate.v1"`、`stage` = `"synthesis"`。
3. 寫入 `canonical/synthesis/candidate/finalist_XX.json`。

### Step 4: Final Candidate Pool

**[mechanical]** 建立 final candidate pool：
1. 將所有 `canonical/synthesis/candidate/finalist_XX.json` 複製到 `canonical/final/candidate/`。
2. 將 `canonical/teacher/selected_candidates.json` 中 rank 1 的原始 teacher candidate 也複製到 `canonical/final/candidate/`。

保留 rank 1 原始 teacher candidate 是防線：如果 synthesis 變得太平、太抽象或拼貼感太重，final judge 可以選回原稿。

### Step 5: Final Judge

**[spawn agent]** 平行啟動 `{{FINAL_JUDGE_COUNT}}` 個 `revised_summary_final_judge`：

```text
---
Assignment
paper_dir: <paper_dir>
paper_file: <paper_file>
judge_id: judge_A
top_k: <{{TOP_K}}>
votes_per_ballot: <{{VOTES_PER_BALLOT}}>
output_root: <paper_dir>/revised_summary/final_judge/round_00/judge_A
```

Final judge 只在 final candidate pool 中選稿，不修改正文。若 `{{FINAL_JUDGE_COUNT}}` > 1，Parent 聚合所有 judge votes；預設為 1 以節省 token。

**[mechanical] Promote + final tally**
1. 複製 judge `review.json` 到 `canonical/final_voting/review_X.json`。
2. 聚合 votes，寫 `canonical/final_voting/vote_tally.json`。
3. 取票數前 `{{TOP_K}}`，進入 final extraction。若 final pool 候選少於 `{{TOP_K}}`，保留全部候選。

### Step 6: Final Extraction

**[mechanical]** Parent 讀 `canonical/final_voting/vote_tally.json` 與 `canonical/final/candidate/*.json`，寫 `canonical/summary.json`：

```json
{
  "schema_version": "summary_final.v1",
  "items": [
    {
      "source_summary_id": "finalist_01",
      "rank": 1,
      "vote_total": 5,
      "main_line": "主線句",
      "refined_final_output": ["第一段...", "第二段..."]
    }
  ]
}
```

抽取規則：
1. `source_summary_id` 取 candidate 的 `candidate_id`。
2. `main_line` 取 candidate 的 `main_line`。
3. `refined_final_output` 取 candidate `paragraphs[].content`，依原順序組成字串陣列。
4. `vote_total` 來自 final tally。

### Step 7: Markdown Generation

**[inline LLM task]** Parent 讀 `canonical/summary.json` rank 1，產生 `<paper_id>_revised_summary.md`：

```markdown
---
title: "<中文短標題>"
---

# 主線
<main_line>

# 摘要
<rank 1 refined_final_output 段落>
```

Title 必須點名研究對象或核心概念，而且要帶有主張。不要用純比喻標題，也不要用「如何」「探討」這類太平的學術題名。

## 格式

此 orchestrator spec 只定義跨階段 handoff。各 subagent 的完整 JSON schema 以對應 prompt 的 `# 格式` 為準。

### 通用投票規則

- 所有 `review.json` 的票數陣列都叫 `global_evaluation.votes`。
- 票數物件只含 `item_id` 與 `votes`。
- 投票長度由 assignment 的 `selected_count` 或 `top_k` 決定；總和由 assignment 的 `votes_per_ballot` 決定。
- 不使用 top-level `status`、`decision`、`summary` 這類可由 findings 或 votes 推出的欄位。
- 同票時用 `item_id` 字典序穩定排序。

### vote_tally.json

每個 voting stage 的 tally shape 相同：

```json
{
  "schema_version": "revised_summary_vote_tally.v1",
  "per_reviewer": [
    {
      "reviewer_id": "reviewer_A",
      "votes": [
        { "item_id": "teacher_03", "votes": 5 },
        { "item_id": "teacher_01", "votes": 2 }
      ]
    }
  ],
  "totals": [
    { "item_id": "teacher_03", "votes": 12 },
    { "item_id": "teacher_01", "votes": 8 }
  ],
  "top": ["teacher_03", "teacher_01"]
}
```

`totals` 依票數降序排列；同票時用 `item_id` 字典序穩定排序。`top` 的長度由該 stage 的 selected count 決定。

### selected_candidates.json

```json
{
  "schema_version": "revised_summary_selected_candidates.v1",
  "items": [
    {
      "candidate_id": "teacher_03",
      "rank": 1,
      "vote_total": 12,
      "path": "revised_summary/canonical/teacher/candidate/teacher_03.json"
    }
  ]
}
```

`path` 相對於 `<paper_dir>`。Synthesizer 讀此檔後，依 `items[].path` 開啟實際 candidate JSON。

### candidate JSON

Teacher worker 與 synthesizer 都輸出 `revised_summary_candidate.v1`。同一 schema 讓 Parent 可以把 teacher candidate 與 synthesis candidate 放進同一個 final pool。

```json
{
  "schema_version": "revised_summary_candidate.v1",
  "candidate_id": "teacher_01",
  "worker_id": "teacher_01",
  "stage": "teacher_draft",
  "title": "染色質位置多半放大縮小，而不是重排 DNA 開關",
  "main_line": "這篇論文發現...",
  "audience_contract": "寫給第一次接觸這篇論文的讀者。",
  "paragraphs": [
    {
      "role": "problem",
      "reader_question": "讀者讀這段前會問什麼？",
      "reader_checkpoint": "讀完後應該能用自己的話說什麼？",
      "content": "自然中文段落。",
      "source_claims": ["paper abstract", "Fig. 1"]
    }
  ],
  "teaching_trace": [
    {
      "issue": "外行人不知道 DNA 開關是什麼。",
      "move": "先說它是控制基因讀取強弱的局部 DNA，再掛回 DNA 開關這個詞。"
    }
  ],
  "borrowed_moves": [],
  "self_check": [
    {
      "condition": "reader_checkpoint",
      "notes": "每段都有可轉述 checkpoint。"
    }
  ],
  "notes": []
}
```

規則：
- `stage` 只能是 `"teacher_draft"` 或 `"synthesis"`。
- `paragraphs[]` 是 final extraction 的唯一正文來源。
- `reader_question` 與 `reader_checkpoint` 每段必填，不能寫成「理解方法」「知道結果」這種空話。
- `source_claims` 是短文字來源標記，不要求精準 quote，但必須足以讓 reviewer 知道該段 claims 來自論文哪一類 evidence。
- `teaching_trace` 要短，只記錄真正影響讀者理解的轉譯決策。不要輸出完整推理樹。
- `borrowed_moves` 在 teacher draft 可為空陣列；synthesis candidate 必須填 3 到 8 條。
