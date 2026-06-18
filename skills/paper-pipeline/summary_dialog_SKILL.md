# Summary Dialog Pipeline

## 目標

這是一份給 pipeline orchestrator 看的指引。

此流程使用場景與目標：
- 輸入：一篇已重組完成的科學論文（路徑慣例見下）。
- 輸出：一份外行人能讀懂的中文摘要（JSON + HTML），附完整的問答紀錄與審查報告。
- 目標：用「真實的不懂」生產「真實的懂」。提問的人沒讀過論文，所以問題是真的；寫文章的人只知道自己問來的東西，所以文章結構性地不可能夾帶沒解釋過的內容。
- 選角：整條 lane 是一位**頂級科普作家**（讀過論文的解釋者）和一位**頂級國中生**（提問並寫文章的 worker）的對話，最後由另一位頂級國中生（裸讀 reviewer）檢查能不能讀懂。**全程白話**：主線、問答、複述、成文，沒有任何一段文字是「內部用的、可以難懂」的——這條 lane 沒有內部行話。

與舊 summary lane 的差別：舊 lane 是單一 worker 自問自答（one-shot × N，靠投票挑好的）；本 lane 是一條對話驅動的單向流程＋review-repair loop。兩條 lane 並存，互不覆蓋。

## 流程總覽

```text
Step 1  解釋者（map）        讀論文 → map.json；parent 把主線一句寫進 transcript 當開場
Step 2  ┌→ worker（ask）       讀 transcript → 提問／reader_blocked／翻譯複述（一次只開一件職責）
        │  解釋者（answer）    讀論文＋transcript → 回答／國中版重講／裁決複述（事實＋越界）
        └─ 輪流重複，直到六件職責全 closed 或滿 {{DIALOG_BUDGET}} 回合
Step 3  worker（write）      只憑 transcript 寫出文章
Step 4  裸讀 reviewer（只看文章）＋ 解釋者（review：論文對賬），平行
Step 5  gate                 findings 全空 → close；有 required → Step 6
Step 6  worker（repair）     修文章；修不動的寫 needs_dialog → 加跑一小輪 Step 2 → 再修
        → 回 Step 4，只 re-review 修過的段落
```

對話可以用常駐會話或輪流 spawn 實作（兩種實作見 Step 2）。無論哪種，每一回合的發言都立刻落盤到 `transcript.json`——它是紀錄、斷點，也是唯一的真相。

## 參數

| 變數 | 預設 | 說明 |
|---|---|---|
| `{{DIALOG_BUDGET}}` | 24 | 對話回合上限（一回合 = worker 追加一次 + explainer 回應一次）。職責串行後回合數較多，平均一件職責約四回合。 |
| `{{ROUND_LIMIT}}` | 3 | review-repair 輪數上限。 |
| `{{CANDIDATE_COUNT}}` | 1 | 平行候選數。>1 時各候選擁有獨立的 dialog 與 worker，互不共享。 |

## 路徑慣例

`paper_file = <paper_dir>/reassembly/canonical/paper.html`。

explainer 在所有 mode（map / answer / review）讀的「論文」都指這個檔案。worker 與 reviewer_01 在任何情況下都不得讀它。

## 結構

### Subagent prompts

| Prompt | 角色 |
|---|---|
| `subagent_prompts/summary_dialog_explainer.md` | 頂級科普作家，全系統唯一讀過論文的角色，寫的每個字都是白話。三種 mode：出地圖（map）、回答提問（answer）、事實對賬（review）。 |
| `subagent_prompts/summary_dialog_worker.md` | 頂級國中生兼文章作者：邏輯極好、誠實、不讀論文。三種 mode：提問（ask）、成文（write）、修補（repair）。 |
| `subagent_prompts/summary_dialog_reviewer.md` | 另一位頂級國中生。只讀成品，逐句做過門測試與重講測試。 |

模型配置建議：worker 用文筆與追問力強的家族；explainer 與 reviewer 不挑模型，紀律夠即可。

### 目錄結構

```text
<paper_dir>/
  summary_dialog/
    scanner/
      map.json               # explainer（map mode）的地圖
    dialog/
      round_00/
        transcript.json      # 對話紀錄，雙方輪流追加
      round_01/              # repair 需要補問時的追加對話
    worker/
      round_00/
        worker_01/
          output.json
          output.html
      round_01/              # repair
        worker_01/
          output.json
          output.html
    reviewer/
      round_00/
        reviewer_01/         # 裸讀
          visual_review.json
        reviewer_02/         # 對源（explainer 的 review mode）
          visual_review.json
      round_01/
    canonical/               # live state——所有下游 agent 的唯一讀取來源
      map.json
      transcript.json
      output.json
      output.html
      visual_review.json
```

`round_00` = initial + 第一次 review。`round_01` 起為 repair + re-review。不覆寫舊 round。

### Step 1: Map

**[spawn agent]** 啟動 summary_dialog_explainer

```text
---
Assignment
paper_dir: <paper_dir>
mode: map
output_root: <paper_dir>/summary_dialog/scanner
```

Explainer 讀論文，寫出 `map.json`：主線一句（至多兩個逗號，差距藏在結果子句裡）、六件職責的論文對應位置、數字表（每個數字帶原文引句）。

**[mechanical]** Promote：複製 `scanner/map.json` 到 `canonical/`。再從 map 建立 `dialog/round_00/transcript.json` 的開場 turn：

```json
{
  "schema_version": "summary_dialog_transcript.v1",
  "turns": [
    { "turn_id": 0, "speaker": "explainer", "type": "seed",
      "duty": null,
      "content": "<map.json 的 main_line 一句，原文照抄，不再加料>" }
  ],
  "duties": [
    { "duty_id": "D1", "name": "卡在哪", "status": "open", "retell": null },
    { "duty_id": "D2", "name": "怎麼解的", "status": "open", "retell": null },
    { "duty_id": "D3", "name": "為什麼非它不可", "status": "open", "retell": null },
    { "duty_id": "D4", "name": "憑什麼信", "status": "open", "retell": null },
    { "duty_id": "D5", "name": "做到什麼程度", "status": "open", "retell": null },
    { "duty_id": "D6", "name": "還缺什麼", "status": "open", "retell": null }
  ]
}
```

### Step 2: Dialog（本 lane 的新原語）

worker 與 explainer 輪流發言，直到六件職責全部 `closed` 或回合數達 `{{DIALOG_BUDGET}}`。不論用哪種實作，三條不變：每一回合的發言立刻落盤到 `dialog/round_00/transcript.json`（append-only）；嚴格輪替，同一時間只有一方在發言；worker 職責串行（前一件複述未 confirm 不開下一件），duties 只有引用得出 confirm turn 才能改 closed。

**實作 A（建議）：混合常駐制。**
- **explainer 常駐**：開一個持續會話，開場餵入 explainer prompt＋論文，之後每回合只傳給它 worker 的新發言。論文只進 context 一次——這是最大的成本節省；它的工作靠能力不靠紀律，長會話的規則衰減對它傷害小。
- **worker 一次性 spawn**：它是全系統規則密度最高的角色（詞彙封閉、逐詞掃描、磚的規矩），每回合醒來重讀 prompt 和 transcript，紀律滿血。transcript 小，重讀不貴。

```text
---
Assignment（worker，每回合）
paper_dir: <paper_dir>
mode: ask
transcript: <paper_dir>/summary_dialog/dialog/round_00/transcript.json
```

Worker 追加這一步的發言（question / reader_blocked / retell，一次推進一步、不囤問題）。parent 把它轉給常駐 explainer，再把 explainer 的回應（answer / confirm / correct）寫回 transcript。

**實作 B（退路）：交替 spawn 制。** runner 無法腳本化維持會話時使用。兩個 agent 都一次性 spawn，各自讀 transcript、追加發言；explainer 的 assignment：

```text
---
Assignment
paper_dir: <paper_dir>
mode: answer
transcript: <paper_dir>/summary_dialog/dialog/round_00/transcript.json
```

Explainer 讀論文與 transcript，對每個未回應的 turn 追加 answer / confirm / correct。

**[mechanical]** 每回合後 parent 檢查 transcript：全部 duties `closed` → 結束迴圈；達 `{{DIALOG_BUDGET}}` → 結束迴圈（留下 open duties）。結束後 promote `transcript.json` 到 `canonical/`。

### Step 3: Write

**[spawn agent]** summary_dialog_worker

```text
---
Assignment
paper_dir: <paper_dir>
mode: write
worker_id: worker_01
transcript: <paper_dir>/summary_dialog/canonical/transcript.json
output_root: <paper_dir>/summary_dialog/worker/round_00/worker_01
```

Worker 只憑 transcript 成文，寫出 `output.json` + `output.html`。仍是 open 的 duty 不寫進正文，記在 `notes`。

**[mechanical]** Promote：複製 `output.json`、`output.html` 到 `canonical/`。

### Step 4: Review

**[spawn agent]** 平行啟動兩個 reviewer：

```text
---
Assignment
paper_dir: <paper_dir>
review_round: round_00
reviewer_id: reviewer_01
output_root: <paper_dir>/summary_dialog/reviewer/round_00/reviewer_01
```

reviewer_01 用 `summary_dialog_reviewer.md`（裸讀：只給 `canonical/output.json`，不給論文、不給 transcript）。
reviewer_02 用 `summary_dialog_explainer.md` 的 `mode: review`（對源：論文 + `canonical/output.json`）。

**[mechanical]** Promote：合併兩份 `visual_review.json`（concat items，`reviewer_id` → `"merged"`，同段落的 findings 以 condition + severity 去重），寫到 `canonical/`。

### Step 5: Gate

讀 `canonical/visual_review.json`：
- 所有段落 `findings` 為空 → lane close。
- 有 `severity: "required"` → Step 6。
- 達 `{{ROUND_LIMIT}}` → blocked，附未解 findings 清單。**這是硬上限：orchestrator 不得加開 round 續修，blocked 就是 blocked。**

Parent 不得自己做品質判斷 override reviewer；有 fail 不得靜默 close。

### Step 6: Repair

**[spawn agent]** summary_dialog_worker

```text
---
Assignment
paper_dir: <paper_dir>
mode: repair
worker_id: worker_01
transcript: <paper_dir>/summary_dialog/canonical/transcript.json
findings: <paper_dir>/summary_dialog/canonical/visual_review.json
current: <paper_dir>/summary_dialog/canonical/output.json
output_root: <paper_dir>/summary_dialog/worker/round_01/worker_01
```

Worker 逐條修 findings，只動被點名的段落。若某條 finding 靠 transcript 的知識修不動（是理解洞，不是文筆洞），worker 在 `notes` 寫 `needs_dialog` 並列出要問的問題——parent 此時跑一輪追加對話（`dialog/round_01/`，沿用 Step 2 機制，預算 5 回合，append 到 canonical transcript），然後重新 spawn repair。每個 repair round 至多一次追加對話。

**[mechanical]** Promote：以 `para_id` 替換 canonical `output.json` 中被修的段落，重新產 `output.html`。回到 Step 4，只 re-review 被修的段落，寫到 `reviewer/round_01/`。

## 格式

`map.json`（`summary_dialog_map.v1`）、`transcript.json`（`summary_dialog_transcript.v1`）、`output.json`（`summary_dialog.v1`）、`visual_review.json`（`summary_dialog_review.v1`）。各 schema 的 Example 與規則在對應的 subagent prompt 裡，此處不重複。

### 規則

- 隔離是本 lane 的 contract：worker 與 reviewer_01 在任何 mode 下都不得讀論文、map.json 的數字表或彼此的輸出。Assignment 裡只給上面列出的檔案。
- transcript 是 append-only：兩個 agent 都只能追加 turn 與更新 duties 狀態，不得改寫舊 turn。
- `{{CANDIDATE_COUNT}}` > 1 時，每個候選一套獨立的 `dialog/`、`worker/`，目錄加 `worker_02/`…後綴；review 與 gate 對每個候選獨立跑。
