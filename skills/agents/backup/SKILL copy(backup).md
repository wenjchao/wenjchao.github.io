# 目標
這是一份給 pipeline orchestrator 看的指引

此流程使用場景與目標：
- 輸入：一個 pdf 檔案
- 輸出：各一份 html 檔案與 md 檔案
- 目標：最大程度讓輸出的 html 檔案與 md 檔案，貼近原始輸出的 pdf 檔案，以利後續閱讀、分析、筆記

# 流程

## 流程總覽

你是 pipeline orchestrator，你的工作流程是：

1. render pages: `scripts/render_pages.py`

2. 接著會進行四份平行的 pipeline。其中所有的 worker, reviewer, repair 都要 spawn 獨立的 subagents 來執行任務（prompt 都在 subagent_prompts 資料夾中）：
  - text lane:
    - extract text (first worker): `subagent_prompts/text_extractor.md`
    - assemble paragraphs (second worker): `subagent_prompts/text_assembler.md`
    - mechanical validate: `scripts/validate_text.py`
    - reviewer: `subagent_prompts/assemble_critic.md`
    - loop: while needs repare (reported from the review)
      - repair: `subagent_prompts/paragraph_repair.md`
      - review again

  - figure lane:
    - worker: `subagent_prompts/figure_extractor.md`
    - mechanical validate: `scripts/validate_figures.py`
    - reviewer: `subagent_prompts/figure_reviewer.md`
    - loop: while needs repare (reported from the review)
      - repair: `subagent_prompts/figure_repair.md`
      - review again

  - table lane:
    - worker: `subagent_prompts/table_extractor.md`
    - mechanical validate: `scripts/validate_tables.py`
    - reviewer: `subagent_prompts/table_reviewer.md`
    - loop: while needs repare (reported from the review)
      - repair: `subagent_prompts/table_repair.md`
      - review again

  - equation lane:
    - worker: `subagent_prompts/equation_extractor.md`
    - mechanical validate: `scripts/validate_equations.py`
    - reviewer: `subagent_prompts/equation_reviewer.md`
    - loop: while needs repare (reported from the review)
      - repair: `subagent_prompts/equation_repair.md`
      - review again

3. Handoff gate

4. reassemble lane:
    - worker: `subagent_prompts/reassembler.md`
    - mechanical validate (preflight)
    - reviewer: `subagent_prompts/final_reviewer.md`
    - loop: while needs repare (reported from the review)
      - repair: `subagent_prompts/reassembly_repair.md`
      - review again

## 平行處理

worker, reviewer, repair 都可以將工作分配 (divide) 給好幾個 agent，讓它們平行處理，這些結果再合併起來 (merge)。

即原本的 worker -> mechanical validate -> reviewer -> (repair -> reviewer) loop

變成 divide works -> parallelized workers -> merge works -> divide works to review -> parallelized reviewer -> merge reviews -> (divide repairs -> parallelized repairs -> merge repairs -> reviewer) loop

- `scripts/merge_figure_table_equation`

# 格式

## 輸出檔案與位置

- 所有輸出都必須放在 `<output_root>/<paper_slug>/` 下。

```text
<paper_dir>/
  input/
    source.pdf                         # parent/init copies
    source_info.json                   # init_run_layout.py writes
    source_info.md                     # render_markdown.py generates

  shared/
    pages/
      page_1.png                       # render pages process writes
      pages_manifest.json              # render pages process or parent writes
    previews/
      page_1_preview.png               # preview process writes
      previews_manifest.json           # preview process or parent writes

  lanes/
    figures/
      worker_output/worker_01/         # figure extractor writes (split by 0, 1 ...)
      worker_output/worker_02/         # figure extractor writes (split by 0, 1 ...)
      canonical/                       # parent/script merges worker outputs, then the review reports, then updated(repaired) products
      reviews/round_00/reviewer_01/   # figure reviewer write JSON (split by 0, 1 ...)
      reviews/round_00/reviewer_02/   # figure reviewer write JSON (split by 0, 1 ...)
      repair/round_01/repair_01/     # parent + repair worker write
      repair/round_01/repair_02/     # parent + repair worker write
      validation/                      # validators/scripts write

    tables/
      worker_output/worker_01/         # table extractor writes (split by 0, 1 ...)
      worker_output/worker_02/         # table extractor writes (split by 0, 1 ...)
      canonical/                       # parent/script merges worker outputs, then the review reports, then updated(repaired) products
      reviews/round_00/reviewer_01/   # table reviewer write JSON (split by 0, 1 ...)
      reviews/round_00/reviewer_02/   # table reviewer write JSON (split by 0, 1 ...)
      repair/round_01/repair_01/     # parent + repair worker write
      repair/round_01/repair_02/     # parent + repair worker write
      validation/                      # validators/scripts write

    equations/
      worker_output/worker_01/         # equation extractor writes (split by 0, 1 ...)
      worker_output/worker_02/         # equation extractor writes (split by 0, 1 ...)
      canonical/                       # parent/script merges worker outputs, then the review reports, then updated(repaired) products
      reviews/round_00/reviewer_01/   # equation reviewer write JSON (split by 0, 1 ...)
      reviews/round_00/reviewer_02/   # equation reviewer write JSON (split by 0, 1 ...)
      repair/round_01/repair_01/     # parent + repair worker write
      repair/round_01/repair_02/     # parent + repair worker write
      validation/                            # validators/scripts write

    text/
      extract_worker_output/worker_01/         # text extractor writes
      extract_worker_output/worker_02/         # text extractor writes
      assembler_output/worker_01/            # assembler worker 1 writes paragraphs_01.json
      assembler_output/worker_02/            # assembler worker 2 writes paragraphs_02.json
      canonical/extracted.json                 # parent/script merges extractor outputs
      canonical/paragraphs.json                # parent/script merges assembler outputs
      reviews/round_00/reviews_01.json         # text reviewer write JSON (split by 0, 1 ...)
      reviews/round_00/reviews_02.json         # text reviewer write JSON (split by 0, 1 ...)
      repair/round_01/repair_01/             # parent + repair worker write
      repair/round_01/repair_02/           # parent + repair worker write
      validation/                            # validators/scripts write

    reassembly/
      worker_output/worker_01/            # reassembler worker 1 writes final_paper_01.json
      worker_output/worker_02/            # reassembler worker 2 writes final_paper_02.json
      canonical/paper.html                # final product
      canonical/paper.md                  # final product
      reviews/round_00/reviewer_01/      # final reviewer write JSON (split by 0, 1 ...)
      reviews/round_00/reviewer_02/      # final reviewer write JSON (split by 0, 1 ...)
      repair/round_01/repair_01/        # parent + repair worker write
      repair/round_01/repair_02/        # parent + repair worker write
      validation/                         # final preflight/verification writes

  trace/
    run.jsonl                          # parent appends
    agents.jsonl                       # parent appends
    gates.jsonl                        # parent appends
    artifact_registry.json             # parent writes
    final_manifest.json                # parent writes
    run.md                             # render_markdown.py generates
    agents.md                          # render_markdown.py generates
    gates.md                           # render_markdown.py generates
    assets.md                          # render_markdown.py generates
```


## 輸出格式

- Agent primary reports 和 decisions 只能是 JSON。Markdown reports/traces 必須由 JSON/JSONL 產生。


# 規則

## 使用 subagent 的規則

- 這個 pipeline 中所有 worker, reviewer, repair 都要 spawn 獨立的 subagents。當使用者要求執行此 pipeline 時，必須 spawn 需要的 worker、reviewer、repair agents。
- 不得用 parent agent （你自己）工作來取代這些 subagents。如果 agent spawn 失敗，先修正 prompt、tool 或 context blockers，然後重試。若仍無法 spawn agents，停止並回報 `blocked`。
- 當工作需要 worker/reviewer judgment 時，parent 不得自己執行 extraction、visual review、text assembly、reassembly 或 final review。
- Parent 可以做機械式 JSON cleanup，但不能編造 verdicts、findings、coverage、source evidence 或 scientific values。

## validator 和 override 規則

- 除非使用者明確指定要 override 某個具體項目，或 pipeline policy 允許已記錄的 override，否則不要 override gates、findings 或 required review surfaces。每個 override 都必須記錄 residual risk。
- Gate 不能只因 validator success 就通過；必須具備 required reviewer coverage 和 trace evidence。

## review 和 repair 規則

- 除非使用者明確改變 scope，每個 lane 預設最多 4 個 repair rounds。
- 任何改動內容的 repair 都會讓 repaired artifact 先前的 reviews 失效，一定要重新完整 review 一次。
- 每個 review 都請完整檢查規範之內應該檢查的所有內容。如果 review 被 divide into parallelized reviewer，則應該等所有 reviewer 完成 review，merge 完所有的 review report 之後再進行 repair。切勿發現問題就直接 repair。
