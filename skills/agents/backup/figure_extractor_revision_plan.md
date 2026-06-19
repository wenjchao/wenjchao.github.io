# figure_extractor.md 修訂決策 plan

這份 plan 用來逐條檢查目前新版 `figure_extractor.md` 要如何繼續修。它不是最終 prompt，也不是 schema；每一條都需要先決定「採用 / 不採用 / 改寫後採用」，再更新 `figure_extractor.md`。

參考文件：
- `figure_extractor_SKILL.md`：舊版 skill 的原始 contract。
- `figure_extractor.md`：目前新版草稿。
- `backup_original.md`：文風、流暢度與資訊密度標準。
- `backup_full.md`：新版過程中收集到的 contract 素材。
- `rewrite_goals.md`：改寫方向指南。

# 修訂總原則

- 補回會直接影響輸出正確性的 contract。
- 刪掉只會造成 schema drift、重複或誤導的欄位。
- 保留新版已經變好的設計，例如 `crop_units`、`crop_hint_px`、`evidence_read`、`_preview` 命名。
- 每個 artifact 只命名一次；後面規則只使用已定義的名字。
- 不把 initial extractor 又寫回舊版「全模式 skill」。
- 如果某條規則其實屬於 orchestrator、repair、review 或 validator，要明確決定它放在哪裡，不要偷偷塞回 extractor。

# A. 一定要補回的 anti-drift contract

## A1. 欄位名稱與單一真相來源

決策：採用。這條規則在防兩種常見錯誤：同一個意思被寫成不同欄位名稱，以及同一份資訊被寫在兩個地方後彼此對不上。

要補的內容：
- 裁切座標只叫 `crop_px`，不要寫成 `crop`、`crop_bbox` 或 `crop_region`。
- 最終裁切圖片路徑只叫 `image_file`，而且只放在 `crop_units[]` 裡。不要使用 `file`、`output_file`、`output_image`。
- `figure_index.json` 可以保留 `pages`，因為它只是先列出有哪些正式 figure，還沒有 `crop_units`。
- 到了 `figure_decisions.json` 和 `figures.json`，頁碼與圖檔路徑都以 `crop_units` 為準：
  - 頁碼讀 `crop_units[].page`
  - 圖檔路徑讀 `crop_units[].image_file`
  - figure 層不要再重複寫 `pages`、`image_files`、`crop_count`

原因：
- 欄位名稱越多，agent 越容易自創變體，後續 validator 或下游 reader 也越難判斷哪個才是真的。
- 同一份資訊只放一個地方，之後重裁、repair 或合併結果時才不會出現兩邊不同步。

## A2. 明文列出 enum

決策：採用。放在 `# 格式` 下新增 `## JSON 命名與 enum` 一節，集中列出三個 enum，每個 enum 標明適用 JSON 與欄位。

要補的內容：
- `region_type`（用於 `figure_candidates.json` 的 `regions[]`）：`figure_visual`、`caption`、`body`、`header`、`footer`、`table`、`equation`、`separator`、`unknown`。
- `source`（用於 `figure_candidates.json` 的 `regions[].source`）：`layout_detector`、`object_detector`、`pdf_text`、`ocr`、`geometry`、`model_visual`、`manual`。`source` 為 `model_visual` 或 `manual` 時，必須在該 region 的 `notes` 說明證據限制。
- `figure_type`（用於 `figure_index.json`、`figure_decisions.json`、`figures.json` 的 figure object）：`main`、`extended`、`supplementary`、`other`。

原因：
- JSON example 只示範部分值，agent 會自創 `region_type: "figure"`、`source: "vision_model"` 之類的變體。

## A3. `expected_panels` 填寫規則

決策：建議補。

要補的內容：
- `expected_panels` 只能根據圖中實際可見的 panel label 或明確視覺結構填寫。
- 不要因為 caption、cross-reference 或正文提到 `Panels A-D` 就自動發明 panel。
- 如果 panel label 不清楚，應在 `notes` 或 `rationale` 說明，不要把不確定的 panel 當成已確認。

原因：
- 新版 JSON example 有 `expected_panels`，但目前正文沒有規則。
- 這是常見錯誤：agent 會從文字推測圖上不存在或看不清的 panel。

建議位置：
- 放在 `## 視覺驗證`。

## A4. `figure_id` 與檔名規則

決策：建議補。同 figure 的多個 crop（多頁或多區域）統一使用 `<figure_id>_part_<N>.png`，不用 page-based 檔名。

要補的內容：
- `figure_id` 必須 filename-safe，不含空格，例如 `Figure_1`、`Figure_2`、`Extended_Data_Figure_1`。
- 單一 crop 圖片使用 `<figure_id>.png`。
- 多個 crop（多頁或多區域）統一使用 `<figure_id>_part_<N>.png`，所有 parts 共用同一個 `figure_id`。
- `crop_id` 在同一 figure 內唯一；頁碼與位置由 `crop_units[].page` 和 `crop_units[].role` 表達，不塞進檔名。

原因：
- 沒寫就容易出現 `Figure 1.png`、`fig1-left.png`、`page6 crop.png` 等不穩定檔名。
- page 和 part 疊加會造成 `Figure_3_page_6_part_2.png` 這類脆弱命名。

## A5 / A6. page-strip 與邊界決策

決策：採用，放在 `## 視覺驗證`。原本的 page-strip / full-column 失敗模式不要寫成平行規則，而是放進邊界檢查流程的第一步。

完稿內容：
- 邊界檢查先看 crop 形態，再讀四個邊界預覽。
  - 若 crop 像整頁、整欄或大頁面條帶，不能直接標 `pass`。
  - 大幅寬圖可以接近整頁寬度，但垂直方向仍必須緊貼 figure，且不得混入正文、外部圖說、頁碼、頁眉、頁腳或其他 page chrome。
- 四邊檢查時，非 figure 內容碰邊就縮小 crop，figure 內容碰邊就放大 crop。調整後必須更新 `figure_decisions.json`、重裁、重建 preview，並重新檢查。
- 若 figure 內容和非 figure 內容因版面交錯而無法乾淨分離：
  - 優先保留 figure 的全部內容，不要為了排除非 figure 內容而切掉 figure。
  - 將該 figure 標 `fail`，並在 `notes` 說明原因。

原因：
- 這條規則把 page-strip 高風險檢查和 edge preview 決策放在同一個流程裡：先排除偷懶的大裁切，再決定縮小、放大或 fail。

# B. 應補回，但可精簡的 contract

## B1. 輔助工具能做什麼 / 不能做什麼

決策：採用，放在 `## 視覺驗證` 的開頭，不另開 helper 小節。

完稿內容：
- 這裡的輔助工具，指 render、preview、layout detection、OCR、crop、file check、coordinate check 等 script 或 detector。
- 輔助工具可以產生候選證據、建立預覽圖片、執行裁切、檢查檔案是否存在、檢查座標是否在頁面範圍內。
- 輔助工具不能判斷 figure 是否完整、caption 是否外漏、座標軸或圖例是否被切掉，也不能判斷 crop 是否只是 page strip。
- 所以輔助工具輸出只能當作 candidate evidence，不是 final truth。`pass` 必須由 agent 讀過 source context、final crop preview 和 edge previews 後判斷。

## B2. 高頻失敗模式清單

決策：採用，放在 `## 視覺驗證` 結尾。這不是 JSON 欄位，而是視覺檢查時要特別防的常見錯誤。

完稿內容：
- 不要把整頁、整欄或大頁面條帶當成 figure crop。
- 不要把外部 caption、頁眉、頁腳、頁碼、浮水印或其他 page chrome 裁進 figure。
- 不要切掉座標軸、圖例、比例尺、panel label、color bar 或其他 figure 內容。
- 不要把輔助工具產生的 bbox 當成最終裁切真相。
- 不要在沒有讀 source context preview、final crop preview 和四個 edge previews 的情況下標 `pass`。

## B3. mechanical validation 階段

決策：目前只要求 mechanical self-check，不產生固定 validation artifact。等 validator v2 定案後，再決定是否寫 `figures_mechanical_validation.json` 或其他 validation JSON。

完稿內容：
- 寫出 `figures.json` 前，先做 mechanical self-check。
- self-check 至少確認：
  - 每個 `crop_units[].image_file` 實際存在。
  - 每個 `crop_px` 都在對應頁面尺寸範圍內。
  - `figures.json` 的 `crop_units` 和 `figure_decisions.json` 對應 figure 的 `crop_units` 完全一致。
  - 每張 final crop 都有 final crop preview 和四個 edge previews。
  - `figure_candidates.json` 最外層必須有 `unexpected_labeled_figures`，`figure_index.json` 最外層必須有 `omitted_candidates`；兩者都可以是空陣列。
  - figure 層不出現可由 `crop_units` 推得的彙總欄位，例如 `pages`、`image_files`、`crop_count`（呼應 A1）。
- self-check 失敗時，必須修正 artifact 後重檢；不能把壞 manifest 寫成成功。
- self-check 通過不代表視覺驗證通過。視覺驗證仍然必須讀圖判斷。

## B4. worker 回報內容

決策：採用精簡版。這不是新的 JSON schema，而是 worker 完成時要回報給 orchestrator / parent agent 的摘要，方便外層追蹤進度與問題。

完稿內容：
- 回報候選是怎麼找到的，例如 layout detector、OCR、model_visual 或 manual。
- 回報讀過哪些 source context previews、final crop previews 和 edge previews。
- 回報寫出了哪些 JSON，例如 `figure_candidates.json`、`figure_index.json`、`figure_decisions.json`、`figures.json`。
- 回報產生了哪些 crop files。
- 回報哪些 figures 是 `pass`，哪些是 `fail`。
- 回報還有哪些 unresolved blockers。
- 不回報 validator command / result，除非 mechanical validator 已經定案。

# C. 建議刪掉或重新設計的新版欄位

## C1. `include_external_caption_in_crop`

決策：移除。

原因：
- 外部 caption 永遠不放進 crop，這是硬規則。
- 永遠是 `false` 的欄位沒有資訊量。
- 欄位存在會暗示某些情況可以設成 `true`。

需要修改：
- 從 `figure_decisions.json` example 移除。
- 由正文 `外部圖說永遠不放進最終裁切圖片，只存入 caption_text` 承擔這個 contract。

## C2. `crop_plan` 與 `notes`

決策：移除 `crop_plan`，也不要把 `single_region` / `multi_region` 改塞進 `notes`。

說明：
- `crop_plan` 是一個摘要欄位，原本用來說這張 figure 是單一 crop 還是多個 crop，例如 `single_region`、`multi_region`。
- 但這件事已經可以直接從 `crop_units` 看出來：
  - 一個 `crop_units` = 一張 crop。
  - 多個 `crop_units` = 同一 figure 有多張 crop。
- 如果保留 `crop_plan`，就會多一個不一致來源。例如 `crop_plan` 寫 `single_region`，但 `crop_units` 其實有兩個。
- `notes` 是自由文字備註，用來解釋欄位本身看不出來的事，例如為什麼要拆成兩張 crop、為什麼某段文字被排除、為什麼這張 figure 標 `fail`。
- `notes` 不應拿來重複 `crop_units` 已經能看出的資訊。不要在 `notes` 寫「this is multi_region」這類 summary。

需要修改：
- 從 `figure_index.json` example 移除 `crop_plan`。
- 需要解釋拆分原因時，寫在 `notes` 或 `rationale`，但只寫真正的決策理由。

## C3. `decision_status`

決策：移除。現在沒有正式定義 `decision_status` enum，也沒有 workflow 會使用這個狀態做分支。

原因：
- 如果只有 `ready_to_crop` 一個值，它不提供資訊。
- 先不要發明不需要的 enum。等 repair、validator 或 orchestrator 真的需要 gating state 時，再重新設計。

需要修改：
- 從 `figure_decisions.json` example 移除 `decision_status` 欄位。

## C4. `unexpected_labeled_figures` / `omitted_candidates`

決策：保留並補規則。新版有 batch / orchestrator assignment，這兩個欄位用來讓 orchestrator 對帳：哪些有標記 figure 超出預期、哪些候選最後沒有被收進正式 figure index。

要補的內容：
- 位置：`unexpected_labeled_figures` 寫在 `figure_candidates.json` 最外層；`omitted_candidates` 寫在 `figure_index.json` 最外層。
- 邊界：「有 label 但不該由本 worker 處理」進 `unexpected_labeled_figures`；「candidate 偵測有產出但 agent 判斷不是正式 figure」（誤偵測、誤判 table/equation、watermark、page chrome）進 `omitted_candidates`。
- `unexpected_labeled_figures[]` 必填 `figure_label`、`page`、`reason`；`caption_text` 讀得到時必填，讀不到填 `null`。
- `omitted_candidates[]` 必填 `candidate_id`、`reason`。
- `notes`：條件性必填——`reason` 為自訂值、`caption_text` 為 `null`、或情況需要額外解釋時必填；其餘可省略。
- `reason` 採半開放：能歸類時用以下建議值，否則自訂 snake_case。
  - `unexpected_labeled_figures.reason`：`outside_assignment`、`unexpected_page`、`not_in_global_index`（最後一項僅在本 worker 能讀到 global index 或 assignment list 時使用）。
  - `omitted_candidates.reason`：`not_a_figure`、`duplicate_of_other_candidate`、`table_misclassified`、`equation_misclassified`、`watermark_or_page_chrome`。
- 兩個欄位都必須存在，內容可為空陣列（空陣列代表 agent 檢查過、沒有這類情況）。

原因：
- batch / worker 並行時，單一 worker 只看自己的 scope。這兩個欄位讓 orchestrator 可以發現跨 worker 的遺漏、重複或 assignment 問題。

需要修改：
- 確認 `figure_candidates.json` example 在最外層有 `unexpected_labeled_figures`。
- 確認 `figure_index.json` example 在最外層有 `omitted_candidates`。
- 在 `## JSON 命名與 enum` 補上兩個 `reason` 欄位的半開放規則。
- 在 B3 mechanical self-check 保留「兩個最外層 array 必須存在，可為空陣列」這條檢查。


# D. 新版好發明，應保留但寫精準

## D1. `crop_units`

決策：保留，並讓 `crop_units` 成為 decision / final crop 的唯一來源。

要補的內容：
- 每個 final crop 都寫成 `crop_units[]` 裡的一個 object，至少包含 `crop_id`、`page`、`crop_px`、`image_file`、`role`。
- 同一 figure 有多頁或多個視覺區域時，使用多個 `crop_units`，並共用同一個 `figure_id`。
- `figure_decisions.json` 和 `figures.json` 必須使用同一組 `crop_units`。`figures.json` 不得改寫 decision manifest 裡的 `crop_id`、`page`、`crop_px` 或 `image_file`。
- 如果 `figures.json` 和 `figure_decisions.json` 的 `crop_units` 不一致，回到 `figure_decisions.json` 修正並重生 final manifest，不要直接手改 `figures.json`。

原因：
- 舊版用 `crop_px` 陣列和 `output_files` 陣列靠順序對齊，multi-page / multi-region 時很容易錯位。
- `crop_units` 讓每個 crop 有自己的身分、頁碼、座標、輸出檔與角色，較容易檢查，也較不容易產生 derived field drift。

## D2. `crop_hint_px` vs `crop_px`

決策：保留 `crop_hint_px`，每個 `figure_candidates[]` 項目都必填，即使 single-region 時略有冗餘。

要補的內容：
- `crop_hint_px` 只出現在 `figure_candidates.json` 的 candidate 層，表示候選階段的裁切提示。
- `crop_px` 只出現在 `figure_decisions.json` 和 `figures.json` 的 `crop_units[]` 裡，表示已決定的最終裁切框。
- single-region 時，`crop_hint_px` 通常等於該 visual region 的 `bbox_px`；multi-region 時，`crop_hint_px` 可以是包住多個 visual regions 的 union 提示框。兩種情況下都不是 final crop。
- 不得直接把 `crop_hint_px` 當成 `crop_px`；最終 `crop_px` 必須經過 source context 檢查並寫入 `figure_decisions.json`。

原因：
- `crop_hint_px` 和 `crop_px` 分開，可以防止 agent 把候選框誤當成最終裁切框。
- single-region 時雖然略有冗餘，但一致填寫比條件式省略更穩定。

## D3. source context check vs final crop check

決策：保留。這兩個檢查是不同階段，不要合併。

要補的內容：
- 以下三個 verification 欄位都寫在 `figures.json.verification` 物件內。
- `verification.source_context_checked` 代表 agent 已讀過 page preview / source region preview，用來決定 figure 成員與裁切決策。
- `verification.final_crop_checked` 代表 agent 已讀過 final crop preview，用來檢查裁切成果本體。
- `verification.edge_previews_checked` 代表 agent 已讀過四個 edge previews，用來檢查邊界是否過緊、過鬆或混入非 figure 內容。

原因：
- 舊版容易把「候選/source context 檢查」和「final crop + edge previews 檢查」混在一起。
- 新版拆開後更能阻止 agent 跳過 source context。

## D4. `evidence_read`

決策：保留，並依階段分開記錄。

要補的內容：
- `figure_decisions.json` 的 `evidence_read` 記錄 source context 階段讀過的 preview，例如 `page_previews`、`source_region_previews`。
- `figures.json` 的 `evidence_read` 記錄 final verification 階段讀過的 preview，例如 `final_crop_previews`、`edge_previews`。
- 任何標成 `pass` 的視覺檢查，都必須能在 `evidence_read` 找到對應 preview：
  - `source_context_checked = "pass"` 時，必須能在 `figure_decisions.json.evidence_read.page_previews` 或 `source_region_previews` 找到對應條目。
  - `final_crop_checked = "pass"` 時，必須能在 `figures.json.evidence_read.final_crop_previews` 找到對應條目。
  - `edge_previews_checked = "pass"` 時，必須能在 `figures.json.evidence_read.edge_previews` 找到對應條目。
  - 沒有對應 evidence 時，不得標 `pass`。

原因：
- `evidence_read` 是 audit trail，不是裝飾欄位。它讓 self-check 或 orchestrator 可以檢查 agent 是否有讀過對應的 preview。

## D5. `schema_version`

決策：保留。

要補的內容：
- 所有 figure extraction JSON 都使用 `schema_version: "figure_extraction.v2"`。
- v2 schema 以本文件內的 JSON examples 與規則為準。
- 新版 prompt 不再引用舊版 `figure_schemas.md`，也不要求相容舊版 schema。

原因：
- 如果新版同時引用舊 schema，agent 會不知道 inline example 和外部 reference 哪個才是真相。

需要修改：
- 檢查 `figure_extractor.md` 和 `backup_full.md`，移除要求「寫任何 JSON 前先讀 `../_shared/references/figure_schemas.md`」的句子。
- 移除描述 JSON 最外層結構時又指向外部 `figure_schemas.md` 的句子，例如「See `../_shared/references/figure_schemas.md` for a full example」。

## D6. `role`

決策：保留，但不設 enum。

要補的內容：
- `role` 放在 `crop_units[]` 裡，用簡短文字說明該 crop 的角色，例如 `complete figure`、`left visual region`、`page 6 portion`。上述為範例，agent 可視 multi-region figure 的實際結構自訂簡短描述（例如 `top half`、`detail panel A`、`overflow on page 7`）。
- `role` 只描述 crop 在同一 figure 裡的用途，不用來表示 pass/fail，也不取代 `notes` 或 `rationale`。

原因：
- multi-page / multi-region figure 可能有多個 image files，`role` 可以讓人快速看懂每個 crop 的位置與用途。
- `role` 是給人類讀的自然語言註記，不是機械判斷依據；設 enum 反而會限制 multi-region 時表達 crop 角色的自由度。

## D7. `_preview` 後綴

決策：保留，並升格為強制命名規則。

要補的內容：
- 所有給 agent 讀的預覽圖片，檔名必須含 `_preview` 後綴。
- 不含 `_preview` 的圖片，agent 不得直接視覺讀取；需要檢查時，必須先建立對應 preview。
- 每個 preview 都必須有對應的完整解析度原檔或工作中間檔；manifest 或命名規則應能看出這個來源關係。

原因：
- `_preview` 是簡單但有效的 anti-confusion 規則，可以讓 agent 和人一眼分辨哪些圖片可讀、哪些是完整解析度原檔或中間檔。

# E. 架構邊界決策

## E1. `source_regions` 是必備還是按需？

決策：source_regions 按需產生，留在 candidate / source context 階段，不搬到 `figure_decisions.json`。

要補的內容：
- 位置：`source_regions` 寫在 `figure_candidates.json` 每個 page object 內，與該 page 的 `regions[]`、`figure_candidates[]` 平行。
- 內容與關聯：每個 source region 代表候選 / source context 檢查時用到的一個工作區域，含完整解析度原檔、preview、`source_region_id`，以及它對應的 `candidate_ids`。candidate 端用自己的 `source_region_ids` 陣列指回它用到的 source regions。
- 何時必填：只要 agent 要讀 source context、或 candidate 會進入 `figure_index.json`，就必須先建立 source region preview 與其完整解析度原檔。
- 何時可空：沒被讀也沒進入 index 的 candidate，可以沒有 source region。這類 candidate 的 `source_region_ids` 寫空陣列，不要省略欄位。
- 與 `evidence_read` 的關係：`figure_decisions.json.evidence_read` 只記錄實際讀過哪些 source region previews，不重新定義 source region 本身。

原因：
- source_regions 是 candidate / source context 檢查用的 evidence，不是 final crop decision 本身。語意上屬於 candidate 階段，搬到 decisions 會破壞「decisions = 純最終決策、candidates = 過程證據」的分層。
- 全部 candidates 都產生會 IO 爆量、容易形式化；只為實際被用的 candidate 產生最務實。
- 哪些 source region previews 真的被讀過，由 `evidence_read` 記錄，方便 self-check 或 orchestrator 檢查是否有對應 evidence。

## E2. 頁面圖片與頁面預覽由誰產生？

決策：頁面圖片與頁面預覽優先由上游產生；若本次 scope 內缺少約定檔案，extractor 依固定程序呼叫 render / preview helper 補齊。agent 不判斷「該不該 render」，只檢查「檔案存不存在」。

要補的內容：
- step 1：檢查 `shared/pages/page_N.png` 是否存在；不存在就呼叫指定 render helper 從輸入 PDF 產生缺失的 page image。
- step 2：檢查 `shared/previews/page_N_preview.png` 是否存在；不存在就呼叫指定 preview helper 由對應 page image 產生缺失的 page preview。
- 責任邊界：render 與 preview 都是 helper 行為（如 B1 所列），是程序性動作，不是 agent 判斷層。
- 路徑規則：補齊後仍使用約定路徑，不把臨時輸出路徑寫進 JSON。
- 失敗處理：若輸入 PDF 不存在、helper 不可用、helper 執行失敗，或輸出檔仍未產生，回報缺失並停下，不要靜默跳過。

原因：
- 「有 PDF 但沒有 page png / preview」是 pipeline lag 或重新執行時的常見情境。讓 extractor 用既有 helper 補齊，比卡住等上游有效率。
- 但「自我判斷權限」會造成飄移行為——改用程序性規則：缺檔 → 跑 helper → 失敗才停。

需要修改：
- 更新 workflow step 1 / step 2：page image 或 page preview 缺失時先呼叫指定 helper 補齊；helper 失敗才回報缺失。

## E3. Modes 放哪裡？

決策：extractor 只做 initial extraction，不處理 repair / continue / batch mode。

各 mode 的歸屬：
- repair：由 `figure_repair.md` subagent 負責（待建）。
- continue：靠 workflow 內建「從第一個缺失 artifact 接續」的行為，不需要 special mode contract。
- batch：不是 extractor mode，而是 orchestrator 概念。extractor 只依輸入的 `worker_id`、`scope.pages` / assignment 工作，並透過 `unexpected_labeled_figures` / `omitted_candidates`（見 C4）回報 scope 內的對帳問題。

repair 契約（屬於 `figure_repair.md`）：
- 必須保留同一 `figure_id`。
- 必須更新所有相關 manifest，不留下過期座標。
- 不讓父 agent 或 orchestrator 從部分裁切輸出回填 `figures.json`。

需要修改：
- `figure_extractor.md` 移除所有 modes 相關段落。
- `figure_extractor.md` 結尾補軟性指針：「本 agent 不處理 repair / continue / batch；repair 契約由 orchestrator / repair agent 另行定義。」
- plan 內部暫定 repair 契約歸 `figure_repair.md`；該檔案建好後，再把指針句換成具體路徑。

# F. 建議實作順序

## 第 1 輪：修 schema drift 和明確 enum

- [ ] 補替代鍵黑名單。
- [ ] 補 `region_type` enum。
- [ ] 補 `source` enum。
- [ ] 補 `figure_type` enum。
- [ ] 補 `figure_id` filename-safe 規則。
- [ ] 補多頁 / 多區域輸出檔名規則。
- [ ] 補 `schema_version: figure_extraction.v2` 與舊 schema 不相容說明。

## 第 2 輪：修視覺驗證與邊界決策

- [ ] 補 `expected_panels` 填寫規則。
- [ ] 補邊界決策樹（含 page-strip / full-column 形態前置與大寬圖特例）。
- [ ] 補 helper 能做什麼 / 不能做什麼。
- [ ] 補高頻失敗模式清單。

## 第 3 輪：刪掉或重設噪音欄位

- [ ] 從 `figure_decisions.json` 移除 `include_external_caption_in_crop`。
- [ ] 從 `figure_index.json` 移除 `crop_plan`。
- [ ] 從 `figure_decisions.json` 移除 `decision_status`。
- [ ] 補 `unexpected_labeled_figures` 的放置位置、填寫規則與 reason 規則。
- [ ] 補 `omitted_candidates` 的放置位置、填寫規則與 reason 規則。

## 第 4 輪：決定架構邊界

- [ ] 採用 E1：`source_regions` 按需產生，記在 `figure_candidates.json`。
- [ ] 採用 E2：頁面圖片與頁面預覽優先由上游產生；缺失時 extractor 呼叫指定 helper 補齊。
- [ ] 採用 B3：mechanical self-check；先確認 A1 砍 figure 層 `image_files` 已完成，否則 self-check 多 drift 點。
- [ ] 採用 E3：extractor 只做 initial extraction，不處理 repair / continue / batch mode。

## 第 5 輪：同步 JSON examples

- [ ] 確認 examples 移除已刪欄位。
- [ ] 確認 examples 使用 enum allowed values。
- [ ] 確認 `figure_decisions.json` 和 `figures.json` 的 `crop_units` 一致。
- [ ] 確認 failed figure 的 `status` 是 `incomplete`。
- [ ] 確認 empty figures case 有最小 example 或規則足夠清楚。

# G. 建議先做的最小修改集

如果你想先小步修，不一次大改，我建議先做這 7 件：

1. 補替代鍵黑名單。
2. 補三個 enum。
3. 補 `expected_panels` 規則。
4. 補 `figure_id` / 多頁檔名規則。
5. 補邊界決策樹（含 page-strip 形態前置）。
6. 移除 `include_external_caption_in_crop`。
7. 移除 `crop_plan`。

這 7 件最能提高正確性，也最不依賴外部架構決策。
