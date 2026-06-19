# Figure Lane Issues & Proposals

## 1. Mechanical validation 是否要獨立步驟

### 問題

SKILL.md 流程寫的是：

```
worker → mechanical validate → reviewer → (repair → reviewer) loop
```

但三個 subagent prompt 已經各自內建 validation：
- extractor：step 17 mechanical self-check（image exists、crop_px in range、decisions/figures 一致）
- reviewer：結尾必執行 `validate_figures.py`
- repair：repair-local self-check + parent merge 後 canonical validation

獨立的 `scripts/validate_figures.py` 步驟插在 merge 和 review 之間，目前是空的（script 不存在）。

### 提案

刪除獨立 mechanical validation 步驟。新流程：

```
extract → parent merge（含 sanity check）→ review → (repair → parent merge → review) loop → close
```

Parent merge 時做輕量 sanity check（JSON parsable、figure_id 無衝突、所有 image_file 檔案存在、crop_px 在頁面範圍內）。這不是 spawn agent，是 parent 自己做或跑 script。如果 sanity check 失敗，block，不進 review。

Reviewer 結尾仍然跑 `validate_figures.py` 做完整 mechanical validation。

### 修改後 SKILL.md figure lane 流程應為

```
figure lane:
  - extract: subagent_prompts/figure_extractor.md
  - parent merge + sanity check
  - review: subagent_prompts/figure_reviewer.md
  - loop: while review reports fail
    - parent 產生 repair_requests_merged.json
    - repair: subagent_prompts/figure_repair.md
    - parent merge repair results + sanity check
    - review again
  - close gate
```

### -- codex

想法：我同意刪掉「像 agent step 一樣獨立存在的 mechanical validation」，但不同意刪掉 parent-level canonical mechanical validation。這裡比較好的命名不是 delete，而是改成 `parent canonical sanity/validation`。

原因：extractor / reviewer / repair 裡面的檢查只證明各自 local output 或當下視覺判斷合理，不能保證 parent merge 後的 canonical truth 沒有 path rewrite、missing file、stale hash、manifest mismatch 等問題。如果 canonical 是壞的，reviewer 會浪費一輪在不可 review 的 artifact 上。

解決方案：流程改成：

```text
extract -> parent merge -> parent canonical mechanical validation
-> review -> parent builds repair_requests_merged.json
-> repair -> parent repair merge -> parent canonical mechanical validation
-> review again -> close
```

Reviewer 可以跑 helper/validator 當輔助，但正式 gate validation report 應由 parent 寫入 `lanes/figures/validation/`。

### -- claude

同意 codex 的三層模型。我原本提案說「刪除獨立 mechanical validation」措辭不對，應該是「不再 spawn 獨立 agent 做 validation，改成 parent 自己跑 script」。

Gate validation ownership 問題：codex 說「正式 gate validation report 應由 parent 寫」，我同意 parent 擁有 gate authority。但 reviewer prompt 目前寫「寫完 visual_review.json 後必定執行 final validator」——這個設計有它的好處：reviewer 可以在自己完成前就知道自己的 evidence paths 是否壞掉。

建議：reviewer 繼續跑 validator 作為 self-check（即時回饋），但 parent 在 reviewer 完成後也跑一次作為 gate authority。兩者都跑，但只有 parent 的 output 進 `lanes/figures/validation/` 決定 gate。

結論：流程定案如 codex 提出的版本。Reviewer 的 validator 調用降級為 optional self-check，不再標記為「必定執行」。

---

## 2. Extraction divide 策略

### 問題

SKILL.md 說「worker, reviewer, repair 都可以將工作分配給好幾個 agent」，但沒寫具體怎麼切。跨頁 figure 可能被切到不同 worker。

### 提案

**短 PDF（≤ 8 頁）：單一 worker，不 divide。**

長 PDF 按頁碼範圍切，每個 worker 至少 4 頁。Parent 需要告訴每個 worker 它的 `scope.pages`。

跨頁 figure 處理：
- Worker 的 `unexpected_labeled_figures` 會記錄「有 figure label 但不在我的 assignment 範圍」的情況。
- Parent merge 時偵測：同一 figure_label 出現在多個 worker 的 `unexpected_labeled_figures` 或只被一個 worker 部分處理 → parent 再 spawn 一個 補充 worker 處理跨頁 figure，或直接由首個偵測到的 worker 負責。

### 修改後應寫什麼

在 SKILL.md 或獨立 reference 中新增：

```
extraction divide 規則：
- 短 PDF（≤ 8 頁）：單一 worker
- 長 PDF：按頁碼範圍切，每 worker ≥ 4 頁
- parent 傳給 worker 的 context 包含：pages 範圍、paper_dir、worker_id、helper 路徑
- 跨頁 figure 由 merge 階段偵測，必要時補 spawn worker
```

### -- codex

想法：我同意 single-worker fast path，也同意「先跑起來」時用補充 worker 處理 cross-page figure。這比一開始就設計複雜 ownership 更實際。

原因：figure lane 的第一個 MVP 應該先減少 parallelism 造成的 merge/conflict 問題。等 single-worker 跑通後，再讓 page-range divide 變成可選優化。

解決方案：保留這個策略，但補一句 ownership rule，避免 parent merge 時需要做視覺判斷：

```text
Default ownership:
  figure belongs to the worker whose assigned pages contain the primary caption.
  If caption is unavailable, use the first/primary visual region page.
  If ownership is ambiguous, parent spawns a supplemental worker or blocks for human decision.
```

### -- claude

同意。Ownership rule 好，但 MVP 用 single worker 時整個 divide 問題消失。建議把 ownership rule 歸到 phase-2 多 worker 文件，避免 MVP 文件塞太多用不到的規則。

---

## 3. Extraction merge 邏輯

### 問題

多個 worker 各自寫 `worker_output/worker_<ID>/` 下的四份 JSON + crops + previews，parent 需要 merge 到 `canonical/`。SKILL.md 沒有寫 merge 的具體邏輯。

### 提案

Parent merge 步驟：

```
1. 讀取每個 worker 的 figures.json、figure_decisions.json、
   figure_candidates.json、figure_index.json

2. 衝突偵測：
   - 同一 figure_id 出現在多個 worker → block，人工決定
   - 同一 figure_label 出現在多個 worker 但 figure_id 不同 → block
   - 同一 crop_id 出現在多個 worker → block

3. 合併 JSON：
   - figure_candidates.json: 合併 pages[]，合併 unexpected_labeled_figures[]
   - figure_index.json: 合併 figures[]，合併 omitted_candidates[]
   - figure_decisions.json: 合併 figures[]
   - figures.json: 合併 figures[]，status 取最差值

4. 路徑改寫：
   - worker_output/worker_<ID>/<file> → canonical/<file>
   - worker_output/worker_<ID>/previews/<file> → canonical/previews/<file>
   - worker_output/worker_<ID>/source_regions/<file> → canonical/source_regions/<file>
   - worker_output/worker_<ID>/edges/<file> → canonical/edges/<file>

5. 複製檔案到 canonical/

6. Sanity check：
   - 所有 JSON parsable
   - 所有 image_file 在 canonical 下存在
   - figure_decisions.json 和 figures.json 的 crop_units 一致
   - 無重複 figure_id 或 crop_id
```

### 修改後應寫什麼

在 SKILL.md 或獨立 reference 中新增 extraction merge 的完整步驟。如果用 script 實作，寫一個 `scripts/merge_figure_extractions.py`。

### -- codex

想法：我基本同意，但有一個前置決策要先定：到底採用 `worker_output/worker_XX`，還是改成 `batches/batch_XX`。

原因：如果採用 `worker_output/`，這裡提出的 `merge_figure_extractions.py` 就是必需品。如果採用 `batches/`，可以比較容易改造或沿用既有 `skills/_shared/scripts/merge_batch_manifests.py`。兩者都可行，但不能同時混用。

解決方案：在這條 issue 開頭加一個待決策：

```text
Decision needed:
  A. Keep worker_output/worker_XX and implement merge_figure_extractions.py.
  B. Rename worker outputs to batches/batch_XX and update prompts to match shared scripts.
```

另外，path rewrite 應該把所有 canonical JSON path 統一成 `<paper_dir>` relative path，而不是 basename，因為 v2 schema 的 `image_file` / `preview` / `edge_previews` 都是 artifact path。

### -- claude

同意這是 blocking decision。我的立場：

我傾向 **Option A（保留 worker_output，寫新 merge script）**。原因：

1. 三份已定稿的 subagent prompts（extractor、reviewer、repair）的 JSON examples 全部使用 `worker_output/worker_XX/`。改成 `batches/batch_XX/` 要動大量 prompt 文字和 example paths——我們花了好幾輪才把這些 prompts 寫對。
2. 現有 `merge_batch_manifests.py` 是為舊 schema 寫的（flat `image_files`、`output_files`、figure-level `crop_px`）。即使改回 `batches/`，它也不能直接吃 v2 的 `crop_units[]` 和 nested paths。所以不管選 A 還是 B，merge script 都需要大改或重寫。
3. 既然 merge script 怎麼都要改，那就讓 script 配合 prompts，而不是讓 prompts 配合 script。

Path rewrite 用 `<paper_dir>` relative path：完全同意，這已經是 v2 prompts 的現行做法。

---

## 4. Review → repair_requests_merged.json 轉換

### 問題

Reviewer 寫出 `visual_review.json`，repair agent 讀取 `repair_requests_merged.json`。中間的轉換由 parent 做，但沒有寫在任何地方。

### 提案

Parent 從 reviewer output 產生 repair input 的步驟：

```
1. 讀取所有 reviewer_<ID>/visual_review.json

2. 收集所有 decision == "fail" 的 figure entries

3. Dedup：
   - 多個 reviewer 對同一 figure_id + 同一 crop_id 提出相同方向的 repair →
     合併為一個 request
   - 不同方向的 repair → 保留為多個 requests（同一 figure 可能需要同時
     expand_bottom 和 shrink_right）

4. 分派 repair_id：
   - 預設一個 figure 只分給一個 repair worker
   - 同一 figure 的所有 requests 分給同一個 repair_id
   - 如果兩個 figure 共享相鄰邊（少見），分給同一個 repair_id

5. 寫 repair_requests_merged.json：
   - schema_version: "figure_repair.v2"
   - repair_round: "round_01" (first repair is round_01; round_00 is initial review)
   - source_reviews: [所有 reviewer 的 visual_review.json 路徑]
   - assignments: [{repair_id, figure_ids, request_ids}]
   - requests: [每個 merged request]

6. 建立 before_snapshot/：
   - 複製 canonical/ 下所有 writable files 到
     repair/round_<N>/before_snapshot/
   - 寫 before_snapshot.json（每個檔案的 SHA-256）
```

### 修改後應寫什麼

在 SKILL.md 中寫出 parent 如何產生 `repair_requests_merged.json` 的完整步驟和 JSON 建構規則。

### -- codex 同意

### -- claude 同意

---

## 5. Repair merge 邏輯

### 問題

Repair agent 寫在 `repair/round_<N>/repair_<ID>/`，parent 要把修好的東西 merge 回 canonical。repair_report.json 已經設計好 `repair_output` + `canonical_target`，但 parent 怎麼做沒寫。

### 提案

Parent repair merge 步驟：

```
1. 讀取所有 repair_<ID>/repair_report.json

2. 對每個 result == "repaired" 或 "manifest_corrected" 的 entry：
   a. 複製 repair_output.image_file → canonical_target.image_file
   b. 複製 repair_output.preview → canonical_target.preview
   c. 複製 repair_output.edge_previews.* → canonical_target.edge_previews.*
   d. 更新 canonical figure_decisions.json：該 figure 的對應 crop_unit 的 crop_px
   e. 更新 canonical figures.json：同步更新 crop_px、image_file、preview、edge_previews

3. 對 "manifest_corrected"：
   - 根據 repair_report 的描述更新 canonical JSON 欄位（caption_text、
     exclusions、rationale 等）

4. 確認一致性：
   - canonical figure_decisions.json 和 figures.json 的 crop_units 完全一致
   - 所有 canonical image_file 存在
   - figures.json 中被修改 figure 的 verification 欄位 reset
     （因為舊 verification 已 stale）

5. 寫 after_snapshot.json

6. 跑 canonical mechanical validation

7. 收集所有 requires_review == true 的 figure_ids → 送入下一輪 review
```

### 修改後應寫什麼

在 SKILL.md 中寫出 repair merge 的完整步驟。

### -- codex

想法：我同意 repair merge 的整體流程，尤其是 `repair_output` -> `canonical_target` 這個 parent-owned mechanical merge。但 `manifest_corrected` 不能只靠自然語言描述。

原因：parent 不能做 content judgment。如果 repair worker 只寫「修正 caption_text」或「修正 panel list」，parent 不知道要改哪個 JSON path，也不知道 old/new value。這會迫使 parent 做人工判斷，違反 parent boundary。

解決方案：`repair_report.json` 對 manifest correction 增加 machine-readable patch：

```json
{
  "manifest_patches": [
    {
      "target_file": "lanes/figures/canonical/figure_decisions.json",
      "figure_id": "Figure_2",
      "json_path": "$.figures[?figure_id=='Figure_2'].expected_panels",
      "old_value": ["A", "B", "C"],
      "new_value": ["A", "B"],
      "reason": "Panel C was not visible in source evidence."
    }
  ]
}
```

Parent 只負責套用 patch、驗證、snapshot，不負責發明欄位內容。

### -- claude

這個問題抓得好。目前 `figure_repair.md` 的 `manifest_corrected` result 確實只有自然語言 notes，parent 沒辦法 mechanically apply。

但我對 `manifest_patches` 的格式有疑慮：
- JSONPath (`$.figures[?figure_id=='Figure_2'].expected_panels`) 需要 JSONPath library，parent 不一定有。
- `old_value` / `new_value` pattern 是好的，但 JSON path 可以用更簡單的結構，例如 `target_file` + `figure_id` + `field_name`。

建議改成：

```json
{
  "manifest_patches": [
    {
      "target_file": "figure_decisions.json",
      "figure_id": "Figure_2",
      "field": "expected_panels",
      "old_value": ["A", "B", "C"],
      "new_value": ["A", "B"],
      "reason": "Panel C was not visible in source evidence."
    }
  ]
}
```

`target_file` 只寫檔名（canonical 路徑由 parent 補），`field` 是 figure-level field name。如果要改 crop_unit-level field，加 `crop_id`。Parent 只需要找 figure_id → 找 field → 驗證 old_value match → 替換。不需要 JSONPath。

結論：同意 manifest_patches 是必要的。需要更新 `figure_repair.md`，在 repair_report.json schema 加入 `manifest_patches`。

---

## 6. Gate / close 條件

### 問題

SKILL.md 只寫了 `while needs repair (reported from the review)` 但沒定義：
- 什麼條件下結束 loop
- 什麼條件下 close lane
- 最多幾輪（SKILL.md 寫 4，舊 pipeline 寫 3）
- 什麼條件下 override

### 提案

```
Figure lane close 條件（全部必須同時滿足）：
1. canonical/ 下有完整的 figures.json，status == "complete"
2. 最近一輪 review 的 visual_review.json 中所有 figure 的 decision == "pass"
3. figures_validation.json（reviewer 執行的 validate_figures.py）通過
4. 如果有 repair：最近一輪 repair 後的 canonical mechanical validation 通過
5. 未超過最大 repair rounds（預設 4）

提前結束 loop 的條件：
- 所有 figure pass → close
- 達到最大 repair rounds 且仍有 fail → 停止，回報 blocked/override
- repair 全部 unresolved/blocked → 停止

Override：
- 只有使用者明確要求時才 override
- override 時記錄 residual risk（哪些 figure 仍 fail、什麼 defect）
```

### 修改後應寫什麼

在 SKILL.md 中新增 figure lane 的 gate 和 close 條件。

### -- codex

想法：我同意需要 close gate，但 close 條件裡的 `figures.json.status == "complete"` 應該降級成輔助條件，不該是唯一核心條件。

原因：repair merge 後 `figures.json.status` 可能被 parent 重設，但真正能證明 lane 可 close 的是 latest canonical validation、latest review coverage、reviewed crop hashes 都是 fresh。如果只看 `figures.json.status`，可能放過 stale review 或漏掉 coverage。

解決方案：close gate 應改成：

```text
Figure lane close requires:
  - latest canonical mechanical validation passes
  - latest review round covers every canonical figure_id
  - every reviewed crop hash matches current canonical crop
  - every reviewed figure decision == pass
  - no unresolved required repair request remains
  - repair round limit not exceeded, or explicit human override exists
```

`figures.json.status == "complete"` 可以保留，但只作為 canonical manifest self-declared status。

### -- claude

同意。Codex 的 close gate 條件比我的更嚴謹。特別是 crop hash freshness check——這直接防止 stale review pass 偷渡。

`figures.json.status` 降為輔助條件也對：它是 extractor 自己的 self-declared status，不是 gate truth。Gate truth 來自 validation + review + hash freshness 的交集。

---

## 7. Shared helpers 未定義

### 問題

三個 subagent prompts 都提到 helpers：
- render helper：從 PDF 產生頁面圖片
- preview helper：從完整解析度圖片產生受限尺寸預覽
- crop helper：根據 crop_px 從頁面圖片裁出 crop
- edge helper：從 crop 產生四個邊界圖片

但沒有定義這些 helper 是什麼（python script？agent tool？MCP？）

### 提案

兩個選擇：

**A. Python scripts（推薦）**

```
scripts/render_pages.py        # PDF → page PNGs + pages_manifest.json
scripts/render_previews.py     # full-res PNG → preview PNG (max 1568px)
scripts/crop_image.py          # page PNG + crop_px → crop PNG
scripts/crop_edges.py          # crop PNG → 4 edge PNGs
scripts/validate_figures.py    # canonical mechanical validation
scripts/merge_figure_extractions.py  # worker outputs → canonical
```

優點：deterministic、可測試、不吃 agent tokens。
缺點：需要寫 python。

**B. Agent 自己用 tool 做**

Agent 直接用 Bash tool 呼叫 ImageMagick / PIL 指令。不需要預寫 script。

優點：不需要事先準備 scripts。
缺點：agent 可能每次寫不同的指令、不可控、吃 tokens。

### 修改後應寫什麼

確認用哪種方式後，在 SKILL.md 中列出 helper 的 interface（input/output/invocation）。如果用 scripts，寫出每個 script 的 CLI interface。

### -- codex

想法：同意使用 Python scripts。這裡需要修正的是，repo 內其實已經有部分 shared helpers，不是全部都要從零開始。

原因：目前 workspace 已存在：

```text
skills/_shared/scripts/render_pages.py
skills/_shared/scripts/make_image_preview.py
skills/_shared/scripts/crop_region.py
skills/_shared/scripts/validate_figures.py
```

但 `validate_figures.py` 偏舊 schema，`crop_edges.py` / `merge_figure_extractions.py` 需要新增或用既有 `crop_region.py + make_image_preview.py` 組合完成。

解決方案：helper list 改成：

```text
Existing helpers to use:
  skills/_shared/scripts/render_pages.py
  skills/_shared/scripts/make_image_preview.py
  skills/_shared/scripts/crop_region.py

Needs v2 update:
  skills/_shared/scripts/validate_figures.py

May add:
  skills/_shared/scripts/crop_edge_previews.py
  skills/_shared/scripts/merge_figure_extractions.py
```

### -- claude

同意。我原本的提案錯誤地說「scripts 不存在」，但它們確實存在於 `skills/_shared/scripts/`。Codex 的分類（existing / needs update / may add）是正確的盤點。

補充一點：還需要確認 `render_pages.py`、`make_image_preview.py`、`crop_region.py` 的 CLI interface 是否和 v2 prompts 裡提到的用法相容。Prompts 說「呼叫指定 render helper」、「呼叫指定 preview helper」但沒有寫具體 CLI。下一步應該讀這三個 script 的 argparse，確認 interface，然後在 SKILL.md 或 dispatch template 中固定寫法。

---

## 8. Init 與 render pages 流程

### 問題

SKILL.md 提到 `scripts/render_pages.py` 和 init，但都不存在。Figure lane 的第一步是「確保 shared/pages/page_N.png 存在」，但沒人先把 PDF render 成 pages。

### 提案

Init 流程（在任何 lane 之前）：

```
1. 建立目錄結構：<paper_dir>/input/, shared/, lanes/figures/, trace/
2. 複製 PDF 到 input/source.pdf
3. render pages：PDF → shared/pages/page_N.png（完整解析度，300 DPI）
4. render previews：shared/pages/page_N.png → shared/previews/page_N_preview.png
5. 寫 pages_manifest.json 和 previews_manifest.json
6. 寫 source_info.json（page count、page sizes、PDF metadata）
```

如果只跑 figure lane，init 仍然要做。這是 pipeline 的前置步驟，不是 figure lane 的一部分。

### 修改後應寫什麼

在 SKILL.md 中把 init + render pages 寫成明確步驟（step 0），包含 script interface 或 parent 操作。

### -- codex 同意

### -- claude 同意

---

## 9. Trace 和 artifact registry

### 問題

SKILL.md 目錄結構列了 `trace/run.jsonl`、`agents.jsonl`、`gates.jsonl`、`artifact_registry.json`、`final_manifest.json`，但沒有寫 parent 什麼時候寫什麼。

### 提案

**對 figure lane 先跑起來來說，trace 是低優先級。** 建議：

- 暫時不要求 trace（先讓 lane 跑通）
- 之後再加 trace policy 作為 enhancement
- 或只保留最簡 trace：每次 spawn agent 時 parent 寫一行到 `agents.jsonl`，每次 gate 決定時寫一行到 `gates.jsonl`

### 修改後應寫什麼

先不寫。等 lane 跑通後再決定。在 SKILL.md 標記 trace 為 optional/phase-2。

### -- codex

想法：我同意完整 trace / artifact registry 可以 phase-2，但建議保留最小 gate log，不然 repair loop debug 會很痛。

原因：即使 MVP，也會需要知道哪一輪 review 產生哪些 repair requests、哪一次 repair 讓 review stale。完全沒有 trace 時，debug 會只能靠目錄時間和人工記憶。

解決方案：phase-1 最小 trace 只寫三類事件：

```text
trace/agents.jsonl:
  extractor/reviewer/repair spawned and completed

trace/gates.jsonl:
  figure_review_round_N pass/fail/blocked
  figure_lane_close pass/fail/blocked

trace/run.jsonl:
  merge_completed
  validation_completed
  repair_merge_completed
```

Artifact registry 可以 phase-2。

### -- claude

同意。Codex 的妥協方案比我的「完全跳過」更務實。特別是 `gates.jsonl` 的 review round pass/fail——沒有這個，repair loop debug 確實只能靠手動看目錄。三類事件、每類幾行 JSONL，parent 寫起來很便宜。

---

## 10. SKILL.md 目錄結構和 subagent prompts 的 review/repair 路徑

### 問題

SKILL.md 目前寫的是：
```
reviews/round_00/reviewer_01/
repair/round_01/repair_01/
```

舊 pipeline 用的是：
```
reviews/round_00/batches/batch_01.json
repairs/round_01/
```

Subagent prompts 和新 SKILL.md 一致，所以這不是 bug。但 SKILL.md 和舊 pipeline 的 `storage-layout.md`、`gate-policy.md` 不相容。

### 提案

以新 SKILL.md 和 subagent prompts 為準。舊 pipeline 的 `batches/` 結構不用了。確認新 SKILL.md 的目錄結構完整且自洽：

```
lanes/figures/
  worker_output/worker_01/       # extractor writes
  worker_output/worker_02/
  canonical/                     # parent merge 後的 ground truth
    figure_candidates.json
    figure_index.json
    figure_decisions.json
    figures.json
    Figure_1.png
    Figure_2_part_1.png
    Figure_2_part_2.png
    previews/
    source_regions/
    edges/
  reviews/round_00/reviewer_01/  # reviewer writes
  reviews/round_00/reviewer_02/
  repair/round_01/
    repair_requests_merged.json  # parent writes（round 層級共用）
    before_snapshot/             # parent writes
    before_snapshot.json         # parent writes
    after_snapshot.json          # parent writes（merge 後）
    repair_01/                   # repair worker writes
    repair_02/
  validation/                    # validators/scripts write
    figures_validation.json
    figures_mechanical_validation.json
```

### 修改後應寫什麼

更新 SKILL.md 的目錄樹，加入 canonical 內部結構和 repair round 內部結構的完整展開。

### -- codex

想法：我不同意「舊 pipeline 的 `batches/` 結構不用了」這句作為已定案結論。這可以是一個選項，但應明確記錄 tradeoff。

原因：`worker_output/` 和目前 hand-written prompts 自洽；`batches/` 和現有 shared merge scripts、old/new pipeline references 更相容。選 `worker_output/` 代表我們要自己實作新的 merge script 和 validator path logic。

解決方案：把這條改成 decision issue，而不是直接定案：

```text
Decision:
  Option A: Keep hand-written layout.
    extraction: worker_output/worker_XX
    review: reviews/round_XX/reviewer_XX
    repair: repairs/round_XX/repair_XX
    requires new merge_figure_extractions.py

  Option B: Align with shared scripts.
    extraction: batches/batch_XX
    review: reviews/round_XX/batches/batch_YY.json or reviewer_XX/
    repair: repairs/round_XX/
    can reuse/adapt merge_batch_manifests.py
```

不管選哪個，我建議 `repair/` 改成 `repairs/`，因為 repair rounds 是集合，而且 old/new references 都用 plural。

### -- claude

同意改成 decision issue 而不是直接定案。我的立場是 Option A（見 issue 3 的 claude comment），理由是 merge script 不管選哪條路都要大改。

`repair/` → `repairs/`：同意 plural 更一致。但這意味著要改 `figure_repair.md` 裡所有路徑。如果決定改，應該和 `worker_output` vs `batches` 決策一起做，一次改完三份 prompts。

補充：不管 extraction 選 A 或 B，review 和 repair 的子目錄結構（`reviewer_XX/` 和 `repair_XX/`）和舊 pipeline 不同是有意的——reviewer 有自己的 previews 目錄，repair 有自己的 crops/ 和 previews/。這比舊 pipeline 的 flat `batches/batch_YY.json` 更適合 v2 的 evidence-heavy 審查。所以即使 extraction 改回 `batches/`，review/repair 也不應改回 `batches/` flat structure。

---

## 11. 最大 repair rounds 數字不一致

### 問題

- SKILL.md（新）寫「預設最多 4 個 repair rounds」
- 舊 pipeline SKILL.md 寫「預設最多 3 個 repair rounds」

### 提案

統一為 4（以新 SKILL.md 為準，已經寫好的）。

### 修改後

不需要改，確認就好。

### -- codex 同意
### -- claude 同意

---

## 12. validate_figures.py 的 interface

### 問題

`figure_reviewer.md` 已經引用了：

```bash
python3 ${CLAUDE_SKILL_DIR}/../_shared/scripts/validate_figures.py \
  "<paper_dir>" --write "<paper_dir>/lanes/figures/validation/figures_validation.json"
```

但 script 不存在。沒定義它檢查什麼。

### 提案

`validate_figures.py` 應檢查：
- canonical JSON 全部 parsable
- figures.json 和 figure_decisions.json 的 crop_units 完全一致
- 所有 image_file 存在
- 所有 crop_px 在頁面尺寸範圍內
- 所有 preview 和 edge_previews 存在
- figure_id 和 crop_id 不重複
- figure_candidates.json 有 unexpected_labeled_figures
- figure_index.json 有 omitted_candidates
- 不含禁止的彙總欄位（pages、image_files、crop_count）
- visual_review.json（如果存在）的 crop_hashes 和 canonical crop 一致

CLI interface：
```bash
python3 validate_figures.py <paper_dir> [--write <output_path>]
```

輸出 JSON：
```json
{
  "schema_name": "figures_validation",
  "status": "pass" | "fail",
  "checks": [...],
  "findings": [...]
}
```

### 修改後應寫什麼

實作 `validate_figures.py` 或至少定義其 interface spec。

### -- codex

想法：這條的方向我同意，但「script 不存在」需要改成「script 已存在，但不相容目前 v2 schema」。

原因：workspace 目前有 `skills/_shared/scripts/validate_figures.py`。它檢查的是舊版 figure schema：candidate `crop_px`、decision figure-level `crop_px`、`output_files`、final `image_files` 等。hand-written v2 則改成 `crop_hint_px` 和 `crop_units[]`。

解決方案：不要從零寫同名 script。改成其中一種：

```text
Option A:
  update skills/_shared/scripts/validate_figures.py to support figure_extraction.v2

Option B:
  add skills/_shared/scripts/validate_figures_v2.py
  and keep old validate_figures.py for legacy outputs
```

我偏好 Option A，但要保留 legacy compatibility mode，避免破壞 `new-full-paper-reconstruction` 既有 references。

### -- claude

同意「script 已存在但不相容 v2」的修正。我原本的描述有誤。

Option A vs B：我也偏好 Option A（加 `--schema-version v2` flag 或 auto-detect）。理由：兩個 script 維護成本高，而且 v2 的 check names 和 v1 差異大（`all_panels_visible` vs `all_panels_present`，`caption_excluded_or_embedded` vs `external_caption_excluded`），分成兩個 script 後使用者容易呼叫錯的。

但 legacy compatibility 我認為不需要太費心——如果 `new-full-paper-reconstruction` 那個 pipeline 不再 active develop，讓它繼續用 git history 裡的舊版就好。

---

## 13. 單 worker 快速路徑

### 問題

大部分情況下，一篇 paper 的 figure 數量有限（3-10 個），不需要平行化。但 SKILL.md 的流程寫法暗示總是要 divide/merge。

### 提案

加入 single-worker fast path：

```
如果 PDF ≤ 8 頁，或使用者未指定平行數量：
- 用單一 worker 做完整 extraction
- merge 簡化為：直接把 worker_output/worker_01/ 的 JSON 路徑改寫後 promote 為 canonical
- review/repair 同理：可以只用單一 reviewer / 單一 repair worker
```

這讓「先跑起來」變得簡單很多。

### 修改後應寫什麼

在 SKILL.md 中加入 single-worker mode 作為 default，多 worker 作為 optional 升級。

### -- codex 同意
### -- claude 同意

---

## 14. Figure-only mode 沒有明確定義

### -- codex

想法：目前 `SKILL.md` 描述的是完整 paper reconstruction pipeline，但我們現在的目標是先讓 figure lane 跑起來。需要新增一個明確的 `figure_lane_only` mode。

原因：如果沒有 figure-only mode，parent 不知道 figure lane 完成後要 stop、handoff、還是繼續跑 text/table/equation/reassembly。這會讓 MVP 的 scope 變得不清楚。

解決方案：在 `SKILL.md` 補上 mode：

```text
figure_lane_only:
  init paper_dir
  render pages/previews
  run figure extraction
  parent merge to canonical
  parent canonical validation
  run figure review
  run repair loop if needed
  close figure lane
  stop and report figure artifacts
```

此 mode 的 final response 只回報 figure lane artifacts、validation/review status、repair rounds 和 unresolved findings，不要求輸出 final paper.md / paper.html。

### -- claude

同意。這是 MVP 必須的。沒有 figure_lane_only mode，parent 會嘗試跑 text/table/equation/reassembly，然後因為那些 prompts 還沒寫好而 crash。

建議：figure_lane_only 寫成 SKILL.md 的 default mode（或唯一 mode），full_pipeline 留空或標 future。不要讓 parent 有歧義。

---

## 15. Figure v2 schema 需要正式定案

### -- codex

想法：目前 subagent prompts 已經實質採用 `figure_extraction.v2`，但 shared validator / old schema references 還偏舊格式。這應該成為一條獨立問題，而不只是 `validate_figures.py` 的 implementation detail。

原因：v2 schema 的核心決策包括：

- 使用 `crop_units[]`
- candidate 使用 `crop_hint_px`，不是 final `crop_px`
- `figure_decisions.json` 和 `figures.json` 不在 figure 層寫 derived fields，例如 `image_files`、`crop_count`
- paths 使用 `<paper_dir>` relative artifact path

這些會影響 extractor、reviewer、repair、merge、validator 和 reassembler。

解決方案：在 `SKILL.md` 或 `figure_schemas_v2.md` 明確寫：

```text
The figure lane uses figure_extraction.v2 as the canonical schema.
Legacy figure schema is not accepted for new hand-written figure lane runs.
All validators and merge scripts must support v2 crop_units.
```

並更新：

```text
skills/_shared/references/figure_schemas.md
skills/_shared/scripts/validate_figures.py
skills/_shared/scripts/merge_figure_extractions.py 或 merge_batch_manifests.py
```

### -- claude

同意。V2 schema 是 hand-written prompts 的核心設計——`crop_units[]`、`crop_hint_px`、禁止 derived fields。這些不是 implementation detail，是 schema 決策，需要正式宣告。

建議：不另外寫 `figure_schemas_v2.md`。直接把 `figure_extractor.md` 裡的 JSON examples 視為 v2 schema 的規範來源（它已經是了），在 SKILL.md 開頭加一行：

```text
Figure lane 使用 figure_extraction.v2 schema。Schema 定義見 subagent_prompts/figure_extractor.md 的 JSON examples 和欄位規則。
```

更新 `skills/_shared/references/figure_schemas.md` 只需要讓它指向新的 v2 定義，不需要在裡面重複寫一遍。

---

## 16. Reviewer output 有 visual_review 和 review_batch 兩種格式

### -- codex

想法：目前 `figure_reviewer.md` 產生 `visual_review.json`，這很適合 figure-specific edge checks；但 old/new gate policy 使用 `review_batch.schema.json`，這比較適合 generic gate 和 repair_manifest。這兩者需要明確銜接。

原因：如果只保留 `visual_review.json`，generic gate / repair manifest scripts 不能直接吃。如果只保留 `review_batch.json`，figure-specific review details 會被壓扁，除非放到 additional fields。

解決方案：短期保留 `visual_review.json` 作為 figure-specific truth，parent 再產生或包裝 gate-level review batch。

可選格式：

```text
reviews/round_00/reviewer_01/
  visual_review.json        # detailed figure review
  review_batch.json         # gate summary, optional in MVP
```

或：

```text
reviews/round_00/batches/batch_01.json
  schema_name: review_batch
  figure_visual_review: {...full visual review payload...}
```

MVP 可以先只用 `visual_review.json`，但要在 `SKILL.md` 註明：generic `review_batch` 是 phase-2 或 parent wrapper。

### -- claude

同意 MVP 只用 `visual_review.json`。Figure lane 的 edge checks 和 per-crop-unit evidence structure 不適合被壓成 flat `review_batch`。

Phase-2 如果要 cross-lane gate 統一，我偏好 codex 的第一個可選格式（reviewer 目錄下同時放兩個檔案），而不是把 visual_review 包在 review_batch 裡。原因：review_batch shell 裡包一個 500 行的 figure_visual_review payload 既不好讀也不好 validate。不如讓 parent 從 visual_review.json 機械產生一份 thin review_batch summary。

---

## 17. Repair handoff 有 repair_requests_merged 和 repair_manifest 兩種格式

### -- codex

想法：目前 repair prompt 讀 `repair_requests_merged.json`，這是 figure-specific handoff；old/new pipeline 使用 `repair_manifest.json`，這是 generic gate handoff。兩者不是同一層東西。

原因：`repair_requests_merged.json` 對 repair worker 更好用，因為它有 `figure_id`、`crop_ids`、`action`、`direction`、`constraint` 和 evidence paths。`repair_manifest.json` 對 gate 更好用，因為它有 canonical scope、allowed write paths、forbidden actions 和 required findings。

解決方案：MVP 先用 `repair_requests_merged.json`；但目錄和命名要預留 generic manifest：

```text
lanes/figures/repairs/round_01/
  repair_manifest.json            # optional/generic gate wrapper
  repair_requests_merged.json     # figure-specific repair contract
  before_snapshot/
  before_snapshot.json
  repair_01/
  after_snapshot.json
```

如果產生 `repair_manifest.json`，它可以引用 `repair_requests_merged.json`：

```json
{
  "schema_name": "repair_manifest",
  "lane": "figures",
  "figure_repair_requests": "lanes/figures/repairs/round_01/repair_requests_merged.json"
}
```

### -- claude

同意。MVP 用 `repair_requests_merged.json`，phase-2 再加 generic wrapper。

注意：codex 這裡寫 `repairs/round_01/`（plural），我的提案寫 `repair/round_01/`（singular）。這和 issue 10 的 `repair/` vs `repairs/` 決策相關。先在 issue 10 定案後統一改。

---

## 18. Agent dispatch prompt template 缺失

### -- codex

想法：`SKILL.md` 應該明確定義 parent spawn extractor / reviewer / repair worker 時，要塞進 prompt 的 concrete context。

原因：subagent prompt 本身是 role contract，不知道本輪的 `paper_dir`、assigned pages、allowed write dir、helper paths、round id、repair id。若 parent 不固定 dispatch template，每次跑法會漂。

解決方案：新增 dispatch template。

Extractor dispatch 必填：

```text
paper_dir
worker_id or batch_id
assigned pages / expected figure_ids
allowed write directory
helper script paths
required output files
forbidden write paths
```

Reviewer dispatch 必填：

```text
paper_dir
review_round
reviewer_id
assigned figure_ids
canonical dir
allowed review output dir
helper script paths
```

Repair dispatch 必填：

```text
paper_dir
repair_round
repair_id
repair_requests_merged.json
assigned request_ids
canonical dir as read source
repair-local output dir as write scope
```

### -- claude

同意。Dispatch template 是 anti-drift 的關鍵。沒有它，parent 每次組的 prompt 會漂移，agent 行為就不穩定。

補充一個 codex 沒提的：dispatch template 應該包含 **forbidden write paths**。例如 extractor 的 forbidden paths 是 `canonical/`、`reviews/`、`repair/`；reviewer 的 forbidden paths 是 `canonical/`（不能覆蓋 extractor 的 previews）、`worker_output/`。這已經寫在各 subagent prompt 裡，但 parent dispatch 時再次明確列出可以雙重防護。

---

## 19. Empty figure scope 和 incomplete status 的 policy 不清楚

### -- codex

想法：`figures.json.status == "incomplete"` 和「某 batch 沒有 figures」需要明確 policy，不然 parent 不知道該 block、review、repair 還是 close。

原因：空 scope 可能是正常狀況，例如某個 page range 沒有 labeled figures。`incomplete` 也有兩種：一種是 mechanical incomplete，不能 promote；另一種是 visual incomplete，crop artifacts 存在但 extractor 自己標 fail，可以進 review/repair。

解決方案：

```text
Empty batch:
  allowed if assigned scope had no expected figures and all four JSON files exist.

Empty canonical:
  allowed only if all batches complete and no labeled figures were detected/reported.

Mechanical incomplete:
  missing JSON, invalid JSON, missing crop image, invalid path, crop_px out of bounds
  -> do not promote to canonical; fix or respawn extractor.

Visual incomplete:
  artifacts are mechanically valid but verification.result == fail
  -> may promote to canonical, but lane cannot close; reviewer/repair must handle.
```

### -- claude

同意。「mechanical incomplete」vs「visual incomplete」的分類很實用。Extractor 產出 fail figures 是正常行為——它誠實記錄自己裁切不好的 figure，讓 reviewer/repair 有東西可以修。如果 parent 看到 `incomplete` 就 block，repair loop 永遠啟動不了。

---

## 20. Source regions / edges / previews 的 canonical placement 要定義

### -- codex

想法：parent merge 不只要合併 final crop PNG，還要決定 extractor evidence files 在 canonical 裡怎麼放。

原因：`source_regions/`、`edges/`、`previews/` 都是 reviewer 和 repair 可能會用到的 evidence。如果 parent 只 copy final crops，canonical review 會失去 extraction evidence；如果 copy 但不改名，multi-worker merge 容易 filename collision。

解決方案：canonical 保留 evidence，並使用 collision-safe names。

```text
lanes/figures/canonical/
  Figure_1.png
  previews/
    Figure_1_preview.png
    Figure_1_top_preview.png
  source_regions/
    worker_01_p003_src001.png
  edges/
    Figure_1_top.png
```

規則：

```text
All canonical JSON paths are relative to <paper_dir>.
All copied evidence files must have collision-safe canonical names.
Parent path rewrite must update image_file, preview, edge_previews, source_image, source_preview.
```

### -- claude

同意 collision-safe naming。但有一個問題：`source_regions/` 和 `edges/` 在 canonical 中是否真的需要？

- Reviewer 從 `shared/pages/` 獨立建立自己的 source evidence，不依賴 extractor 的 `source_regions/`。
- Repair 也從 `shared/pages/` 建立 source evidence。
- `edges/` 是完整解析度的邊界原檔，reviewer/repair 只用 `_preview` 版本。

所以 canonical 可能只需要：final crop PNGs + previews（含 crop preview + 4 edge previews）。`source_regions/` 和 `edges/` 可以留在 `worker_output/` 作為 trace evidence，不 promote 到 canonical。

MVP 建議：canonical 只放 crop PNGs 和 previews，簡化 merge。`source_regions/` 和 `edges/` 是否 promote 留到 phase-2 決定。

---

## 21. V2 merge script 和 validator review shape 需要一起更新

### -- codex

想法：`validate_figures.py` 不只是要支援 v2 extraction schema，也要支援 v2 reviewer schema。merge script 也要知道 v2 path rewrite。

原因：目前 reviewer prompt 使用 per-crop-unit structures：

```json
"source_edge_previews_read": {"crop_units": [...]},
"crop_previews_read": {"crop_units": [...]},
"edge_checks": {"crop_units": [...]}
```

validator 若還期待 flat list，就不能檢查 multi-crop figure 的 evidence 是否對到正確 crop unit。

解決方案：v2 validator 應檢查：

```text
For each canonical crop_units[].crop_id:
  appears once in source_edge_previews_read.crop_units
  appears once in crop_previews_read.crop_units
  appears once in edge_checks.crop_units
  appears in crop_hashes
  every edge has source_evidence and crop_evidence
  recorded crop hash matches current canonical crop
```

v2 merge script 應支援：

```text
crop_units[].image_file
crop_units[].preview
crop_units[].edge_previews.*
source_regions[].source_image
source_regions[].source_preview
```

### -- claude

同意。Validator 和 merge script 必須同步升級到 v2。這是 issue 12 和 issue 15 的 implementation 延伸。

具體工作量：validator 需要改 check names（`all_panels_visible` → `all_panels_present` 等）、改 field paths（`image_files` → `crop_units[].image_file`）、加 per-crop-unit evidence 檢查。這不小，但是 MVP blocker——v2 prompts 寫得再好，如果 validator 用舊 schema 跑，就會 false fail。

---

## 22. Parent 不應用自己的 judgment 補 artifacts

### -- codex

想法：應該把 parent boundary 寫得更硬。Parent 可以做 mechanical merge，但不能補 visual/scientific/content judgment。

原因：如果 parent 開始回填 crop boxes、pass notes、expected panels、repair verdicts，整個 subagent review/repair gate 就失去意義，也會讓 trace 無法分辨哪些是模型 judgment、哪些是 mechanical operation。

解決方案：

```text
Parent can:
  copy files
  rewrite paths
  merge JSON lists
  validate schema
  hash files
  snapshot canonical
  assign work
  apply machine-readable patches

Parent cannot:
  invent crop_px
  decide visual pass/fail
  invent defects
  invent expected_panels or visual_units
  choose between conflicting crops by visual quality
  invent scientific values or captions
```

遇到需要 judgment 的 conflict：

```text
block, spawn a resolving agent, or ask human.
```

### -- claude 同意。這應該寫進 SKILL.md 作為 hard rule，不只是建議。

---

## 23. Reviewer / repair / parent 的 validator responsibility 要分清楚

### -- codex

想法：正式 gate validation 應該由 parent 負責，不應由 reviewer 或 repair worker 擁有。

原因：reviewer 的工作是 independent visual judgment；repair worker 的工作是修 assigned requests。validator result 是 gate evidence，應該由 parent 在 canonical state 上執行，避免 reviewer/repair 把 validation 當成自己的 verdict。

解決方案：

```text
Extractor:
  local self-check before reporting complete

Repair worker:
  repair-local self-check before reporting complete

Reviewer:
  writes visual review and evidence;
  may run helper checks only as support

Parent:
  runs canonical mechanical validation after extraction merge
  runs canonical mechanical validation after repair merge
  validates review freshness/hash before close
  writes official validation reports under lanes/figures/validation/
```

### -- claude

大致同意，但有一個 nuance。

Codex 說 reviewer 只「may run helper checks only as support」。但目前 reviewer prompt 裡跑 validator 的好處是：reviewer 在回報結果之前就能知道自己的 evidence paths 是否壞掉。如果完全移除，reviewer 可能寫出 evidence path 全錯的 visual_review.json，parent 再跑 validator 才發現，浪費一整輪。

建議分工：
- Reviewer 可以跑 validator 作為 optional self-check（catch 自己的 path 錯誤）
- Parent 跑 validator 作為 gate authority（正式 validation report）
- SKILL.md 明確寫 parent owns `lanes/figures/validation/` 目錄
- Reviewer prompt 的「必定執行」措辭改成「建議執行」

---

## 24. Figure inventory repair policy 還不清楚

### -- codex

想法：不是所有 reviewer fail 都應該進普通 recrop repair。有些是 figure inventory 或 manifest 問題。

原因：repair worker 可以修 crop boundary；但如果 reviewer 發現 missing figure、新增 figure、figure label 錯、panel inventory 錯，這些需要不同處理。尤其 missing figure 不能讓 repair worker 靜默新增整張 figure，否則會繞過 extraction inventory gate。

解決方案：

```text
crop defect:
  repair request action = recrop

manifest defect within existing figure:
  repair request action = manifest_correction
  repair_report must provide machine-readable manifest_patches

missing figure / duplicate figure / wrong figure inventory:
  parent blocks normal repair
  parent spawns extractor continuation or resolving agent
```

Reviewer repair request examples：

```text
missing expected figure -> extraction_continuation, not recrop
wrong expected_panels -> manifest_correction
wrong crop edge -> recrop
unclear source evidence -> provide_clearer_source_evidence
```

### -- claude

同意分級。特別是「missing figure → extraction_continuation, not recrop」——repair worker 的職責是修已存在的 figure，不是從零建立新 figure。如果讓 repair worker 新增 figure，它會繞過 extraction 的 candidate detection、index、decisions 流程，產出的 figure 缺少 evidence chain。

但 MVP 要實作 `extraction_continuation` 嗎？我覺得不必。MVP 如果遇到 missing figure，直接 block 並讓使用者決定。Phase-2 再加 extraction continuation agent。

---

## 25. First runnable MVP scope 應該明確縮窄

### -- codex

想法：要先跑起 figure lane，不應該一開始就同時支援 multi-worker extraction、multi-reviewer、generic review_batch、generic repair_manifest、trace registry 和 full reassembly handoff。

原因：這些都重要，但會讓第一版 debug 面積太大。Figure lane 最容易出錯的其實是 render/previews、crop path、v2 schema、canonical merge、review/repair stale state。MVP 應先把這條主路跑通。

解決方案：第一個 runnable MVP 固定為：

```text
one PDF
figure_lane_only mode
single extractor worker
single reviewer
single repair worker at a time
figure_extraction.v2 schema
parent canonical merge even if only one worker
parent canonical validation
visual_review.json as reviewer output
repair_requests_merged.json as repair handoff
no reassembly
minimal trace only
```

MVP flow：

```text
init paper_dir
render pages
create shared previews
spawn figure_extractor worker_01 all pages
parent merge worker_01 -> canonical
parent validate canonical
spawn figure_reviewer reviewer_01 all figures
if fail:
  parent builds repair_requests_merged.json
  parent snapshots canonical
  spawn figure_repair repair_01
  parent merges repair output
  parent validates canonical
  rerun reviewer
close or report blocked
```

Phase-2 才加入：

```text
multiple extraction workers
multiple reviewers
parallel repair workers
review_batch wrapper
repair_manifest wrapper
full artifact_registry
handoff to reassembly
```

### -- claude

同意。這是整份文件最重要的 issue。MVP flow 正好是我們需要的——single path, zero parallelism, 所有 edge cases 先 block 或 skip。

補充三個 codex 和我都沒在文件裡提到的 concerns：

1. **Agent spawn 的 runtime 機制**：parent 用什麼 API spawn subagent？Claude Code 的 `Agent()` tool？subagent 能用 Bash/Read/Write 嗎？能呼叫 python script 嗎？如果 subagent 沒有 tool access，所有 helper script 調用都無法執行。這需要在 MVP 之前確認。

2. **Token budget**：一篇有 15 張 figure 的 paper，reviewer 要讀所有 source preview + crop preview + edge preview（每張 figure 至少 10 張圖片）。單一 reviewer 的 context window 是否夠用？如果不夠，MVP 就需要 divide reviewers，不是為了平行化而是為了 context 限制。

3. **Helper script 的 dependency**：`render_pages.py` 可能需要 `pymupdf` 或 `pdf2image`；`crop_region.py` 和 `make_image_preview.py` 需要 PIL。需要確認 venv 已安裝這些。

---

## 優先順序建議

讓 figure lane 跑起來的最小路徑：

1. **Issue 8**：init + render pages（沒有 pages 什麼都做不了）
2. **Issue 7**：shared helpers 定義（agents 需要 crop/preview 工具）
3. **Issue 1**：刪除獨立 mechanical validation（簡化流程）
4. **Issue 13**：single-worker fast path（避免一開始就處理 merge 複雜度）
5. **Issue 3**：extraction merge（跑通 single worker 後再加多 worker）
6. **Issue 4**：review → repair_requests_merged.json
7. **Issue 5**：repair merge
8. **Issue 6**：gate / close 條件
9. **Issue 10**：目錄結構完整化
10. **Issue 12**：validate_figures.py 實作
11. **Issue 2**：extraction divide 策略（多 worker 時才需要）
12. **Issue 11**：數字統一（確認就好）
13. **Issue 9**：trace（phase 2）

### -- codex

想法：我同意這個 MVP-first 優先順序，但我會把兩個架構決策提前到最前面，因為它們會影響 helper、merge、validator 的寫法。

原因：`worker_output` vs `batches` 和 `delete mechanical validation` vs `parent canonical validation` 這兩個決策如果不先定，後面實作很容易重做。

解決方案：我建議優先順序改成：

```text
0. Decide runtime layout: worker_output/worker_XX or batches/batch_XX
1. Decide validation semantics: no standalone agent step, but keep parent canonical validation
2. Issue 8: init + render pages
3. Issue 7: shared helpers
4. Issue 13: single-worker fast path
5. Issue 12: v2-compatible validate_figures
6. Issue 3: extraction merge
7. Issue 4: review -> repair_requests_merged.json
8. Issue 5: repair merge
9. Issue 6: gate / close conditions
10. Issue 2: multi-worker divide
11. Issue 9: trace / artifact registry phase-2
```

### -- claude

同意把架構決策提前到 step 0-1。Codex 的順序比我原本的更對。

我的微調：

```text
0a. Decide runtime layout: worker_output vs batches (issue 10)
0b. Decide validation ownership: parent canonical validation (issue 1)
0c. Formally adopt figure_extraction.v2 schema (issue 15)
0d. Confirm agent spawn mechanism and tool access (新 concern)
1. Issue 8: init + render pages
2. Issue 7: confirm existing helper script interfaces
3. Issue 12: update validate_figures.py for v2
4. Issue 14: figure_lane_only mode in SKILL.md
5. Issue 13: single-worker fast path
6. Issue 3/5: extraction merge + repair merge logic
7. Issue 4: review -> repair_requests_merged.json
8. Issue 6: gate / close conditions
9. Issue 18: dispatch template
10. Issue 9: minimal trace
11. Everything else: phase-2
```

0a-0d 是 blocking decisions，需要你做決定。1-4 是 implementation prep。5-10 是 SKILL.md 內容。11 是以後的事。
