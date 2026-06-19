# 目標

這是一份給 `mapping_merger_repair` agent 看的指引。

`mapping_merger_reviewer` 看完 merger 寫出的 `paper.html` 後，用 `visual_review.json` 列出所有 `required` finding。你的工作是**只改 paper.html**，把每個 required finding 修掉，讓讀者看到的最終 HTML 沒有可見的 rendering bug。

**核心約束：你只能改 `<paper_dir>/mapping/canonical/paper.html`，不能碰其他任何檔案。**

- 不改 mapping JSON（`mapping.<key>.json`）—— mapping 的對應錯誤是 `mapping_reviewer` 該抓的，不是這裡的工作。
- 不改 source panel content（`method.json`、`summary.json`）—— 那些是上游 lane 的責任，且改了會讓下次 merger 重跑覆蓋你的 patch；用戶在外層會看到 `merger_bugs` 報告自己決定是否改源檔。
- 不改 merger script（`mapping_merger_script.py`）—— script 的 bug 由 user 在收到 `merger_bugs` 報告後決定是否改。
- 不重跑 merger script。重跑會把你改的 paper.html 蓋掉。

理解這個取捨：你的 patch 是**對「這一份」交付物的最終修飾**。merger 下次重跑會回到壞狀態。所以 `merger_bugs` 報告（reviewer 已經寫好）必須完整呈給 user，才能形成真正的閉環。

# 流程

## Step 1: 讀取

- **review**：`<paper_dir>/mapping/reviewer/<round>/<reviewer_id>/visual_review.json`（或 assignment 指定的路徑）。
- **paper.html**：`<paper_dir>/mapping/canonical/paper.html`（current state，merger 寫出的最新版本）。
- 對照 review 的 `findings[]`，把 `severity == "required"` 的全部撈出來。`advisory` 不必處理。

## Step 2: 對每個 required finding 規劃 patch

對每筆 `required` finding：

1. **定位**：用 finding 的 `location` + `surface` + notes 中的具體字串，在 paper.html 中找到要改的位置。可用 grep / search 而不是計算 byte offset——reviewer 寫的 offset 可能在 patch 過程中漂移。
2. **判斷 patch 範圍**：
   - **字元級 wrap**（bare math、Greek 殘留）：在原 token 兩側加 `\\(` 與 `\\)` 或 `$ $`。例：`r_T \\leftarrow r_S; E_i^\\alpha` → `\\(r_T \\leftarrow r_S; E_i^\\alpha\\)`。確保你包的是一個合法 MathJax expression，括弧成對。
   - **chip / label 文字截短**：找到對應 `<span class="rank-badge">…</span>` / `.ct-item label` / `<div class="layer-title">…</div>`，把文字改成 ≤ 5 字的壓縮版。**不要**改 anchor `id` 或 `data-*` attribute——只改 visible text node。
   - **anchor 漏標**：在 panel 對應段落內，找到 finding 指出的 phrase 字串，包成 `<a class="hl hl-<color>" id="…" data-id="…" data-targets="…">…</a>`。`id` 與 `data-id` 取自 mapping JSON 對應 phrase，`data-targets` 取自 phrase 的 `paper_snippets[].snippet_id`（空白分隔）。`<color>` 從 `source_key` 映射（`l1`→`summary`、`method_mN`→`mN`）。
   - **panel 內亂碼 / template token**：用語意還原（去找 method.json / summary.json 對應段落的純文字），整段替換。**只動該段，不要連同周圍 markup 一起重寫**。
   - **mark / note misalign**：finding 已給 `data-id`，去 paper 段落中找漏的 `<mark id="…" data-id="…">…</mark>`、margin rail 中找對應 `<span class="margin-note n-<color>" data-id="…">…</span>`，補上缺的一邊。
3. **MathJax / CSS 一致性**：包數學前後不要破壞既有 `\\(...\\)` 或 `$...$` 配對；改 chip 文字後 chip 容器 width 不需動（CSS auto）。改完不要產生新的裸 token（例如把 `αRPT` 改 `\\(\\alpha\\)RPT` 是對的，改成 `αRPT` 又一次是錯的）。

## Step 3: 執行 patch

用 Edit / Write 直接改 `<paper_dir>/mapping/canonical/paper.html`。
- 同一份 finding 改一處就夠；不要連帶改鄰近合法內容。
- 不要把 `paper.html` 整檔重寫，只 patch 對應段落。
- 改完後 paper.html 仍要是合法 HTML——括弧成對、tag 配對、屬性值用雙引號包好。

## Step 4: 寫 repair log

寫 `<output_root>/repair_log.json`，schema `mapping_merger_repair.v1`：

```json
{
  "schema_version": "mapping_merger_repair.v1",
  "worker_id": "worker_01",
  "patches": [
    {
      "finding_condition": "bare_math_leak",
      "finding_location": "panel offset ~25340, m7 refined_0 卡片",
      "action": "wrapped_math",
      "before": "(r_T \\leftarrow r_S; E_i^\\alpha)",
      "after": "\\(r_T \\leftarrow r_S; E_i^\\alpha\\)",
      "lines_changed": 1
    },
    {
      "finding_condition": "chip_overflow",
      "finding_location": "m7 toggle chip label",
      "action": "shortened_label",
      "before": "7-MIRD α-emitter 劑量學公式：按粒子類別分項計算吸收劑量",
      "after": "7-MIRD公式",
      "lines_changed": 1
    }
  ],
  "skipped": [
    {
      "finding_condition": "anchor_missing",
      "finding_location": "h-method_m7-009 main_line phrase",
      "reason": "Phrase 字串包含 LaTeX 數學，包成 anchor 後會破壞 MathJax 配對；建議源檔層處理。已在 merger_bugs 記過。"
    }
  ]
}
```

- 每個 required finding 必須在 `patches` 或 `skipped` 之一出現過——不准沉默跳過。
- `skipped` entry 必須有 `reason`；reason 應該指向 `merger_bugs`（reviewer 寫的）對應條目，讓 user 知道這條已被記錄。

## Step 5: Self-check

寫完後：
1. JSON 可 parse。
2. `schema_version` 正確。
3. paper.html 仍是合法 HTML（用 simple check：開啟 file，grep 確認沒有 `</body>` 之後還有 markup、沒有未閉合的 `<mark>` 等）。
4. 所有 `required` finding 都在 patches 或 skipped 中出現。
5. patches 中 `before` 應該不再在當前 paper.html 中存在（被 `after` 取代）。`skipped` 中的 finding 內容仍存在於 paper.html（正常，因為跳過）。

# 不做的事

- 不改任何源檔（mapping JSON、method.json、summary.json）。
- 不改 merger script。
- 不重跑 merger。
- 不處理 `advisory` finding（只處理 `required`）。
- 不刪掉 `merger_bugs` entry——那是 reviewer 留給 user 的。
- Patch 不要連帶清理 / 重新排版 / 改進無關段落。最小修改原則：改一個 finding 對應的最小範圍。

# 完成判定

- `<paper_dir>/mapping/canonical/paper.html` 內所有 `required` finding 的具體 reader-visible 症狀都已消失。
- `<output_root>/repair_log.json` 列出每筆 finding 的處置（patched 或 skipped + reason）。
- 沒碰任何其他檔案。
