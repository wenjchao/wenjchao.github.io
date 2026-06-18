# Skill / Pipeline 改寫目標

這份文件給之後修改 hand-written-pipeline skill、pipeline spec、subagent prompt 的 agent 看。目標不是把文件寫得最短，也不是把所有細節都鋪開，而是讓人和 agent 都能快速、流暢、準確地理解流程。

改寫時請參考：
- `figure_worker.md`、`figure_reviewer.md`：已驗證的成功改寫範例。以此為文風、結構與資訊密度的標準。

# 改寫目標

好的新版文件應該做到：
- 人可以順著讀，不需要在腦中重新整理流程。
- agent 可以直接執行，不需要猜 artifact 的角色、輸出位置或失敗語意。
- 每個重要 contract 都明確存在，但同一件事不要重複講。
- 名詞穩定，同一個 artifact 不要在不同段落換不同名字。
- 流程步驟具體，但不要把固定短枚舉拆成過長的 checklist。

讀者應該能在第一次閱讀時理解：
- 這個 agent 的責任邊界。
- 每個 artifact 的角色。
- 每一步為什麼在這裡。
- 哪些東西是 final output，哪些只是工作中間檔。
- 哪些失敗可以記錄，哪些失敗不能放行。
- 哪些規則是不能被下一個 agent 偷偷改掉的 contract。

這份文件的讀者不只是 agent，也是人。不要只為了節省 token 而壓縮到難讀；也不要因為怕漏掉資訊而把同一個規則用不同說法反覆寫。

# 文件架構要先讓陌生讀者進入系統

好的改寫不是把舊 skill 壓成更短的 contract list，而是重排成一個人能順著理解的結構。讀者即使不知道 project 在做什麼，也應該能先建立整體圖像，再讀細節。

建議順序：
- `# 目標`：先說這個 agent 做什麼、輸入是什麼、輸出是什麼、責任邊界在哪裡。
- `# 流程`：照實際工作順序寫，讓讀者知道先做什麼、下一步做什麼、每個 artifact 在何時產生。規則跟著它執行的 step 放。
- `# 格式`：`## Example`（帶行內註解的 JSON）+ `## 規則`（只放 Example 看不出來的約束）。

不要有獨立的「圖片檔案」或「規則」頂層段落。規則折進流程或格式。三段式（目標/流程/格式）在四條 lane 的改寫中已驗證為最佳結構。Example 帶行內 `//` 註解是格式的主角，取代獨立的 Fields 或 schema section。`## 規則` 用 flat bullet list，不用 `###` 子標題。

架構混亂的症狀：讀者要跳來跳去才能拼湊完整流程，或同一個概念散在三個 section 各講一部分。修法：如果一個 section 的內容可以全部歸入其他 section，就合併。合併前列搬運對照表確認零遺漏。

舊版 skill file 常見的問題不是資訊不足，而是把 mode、contract、schema、workflow、validation 混在工程規格結構裡。熟悉 pipeline 的人可以慢慢拆出意思，但第一次讀的人很難知道整個 agent 到底如何運作。新版文件應該先建立閱讀路徑，再放規則細節。

## 流程段與規則段的分工

流程段不只是做事順序的索引，也可以包含該 step 當下必須知道的短規則。讀者應該能順著流程做下去，不必一直跳到規則段查基本判斷。

規則預設跟著它執行的 step 放在流程段。只有符合下列情況時，才抽到格式段的規則區：
- 跨多個 step 都會用到。
- 太長，放在流程段會打斷閱讀。
- 有獨立概念身份，之後會被人或 agent 反覆引用。

同一條規則只放一個主要位置。流程段可以短句提醒，但不要和格式段逐字重複。

不要有獨立的 `# 規則` 頂層段落。如果所有規則都已經在流程段或格式段有家，就不需要另開一個段落。

驗證清單（self-check）inline 在 prompt 的最後一步，不依賴外部 Python validator。靈活性優先——prompt 可以隨時改，script 改了要重新部署。

# 寫作方式

## 保留自然的中文節奏

可以保留必要的英文術語，例如 `figure_worker agent`、`figure`、`crop`、`preview`、`boundary preview`、`worker/worker_01/`。不要硬翻成讀起來不自然的中文。

好的寫法：
- 這是一份給 figure_worker agent 看的指引
- 此步驟是候選/source context 檢查，用來決定圖表成員與裁切決策，不是驗證最終裁切成果。
- final crop 永遠從頁面圖片裁出，不要從裁切區域來源圖片或其他中間圖片再裁一次。

不好的寫法：
- 這是一份給工作代理看的說明
- 執行初始圖表擷取階段之候選來源脈絡查核
- 產出最終圖表裁剪成品之前應完成全部必要驗證事項

## 資訊密度要剛好

如果一段內容是固定短枚舉，可以寫成一句話。

好的寫法：

```md
為每張完整解析度最終裁切圖片建立四個邊界預覽，包括：上邊界、下邊界、左邊界、右邊界。
```

不好的寫法：

```md
為每張完整解析度最終裁切圖片建立四個邊界預覽，包括：
- 上邊界
- 下邊界
- 左邊界
- 右邊界
```

但如果每一項都需要 agent 逐一檢查，就應該保留 checklist。例如 boundary preview 四邊檢查、verification 必填欄位、self-check 項目，都適合列點。

另一種比 checklist 更好的 framing 是「常見失敗」：把檢查項目框成「常見但非全部的問題 pattern」，結尾加「如果看起來不對，即使不符合上面任何 pattern，也要調查」。這讓 agent 知道該注意什麼，但不會照表操課、放棄使用判斷力。Checklist 適合機械性驗證（JSON 欄位、檔案存在），常見失敗適合需要判斷的審查（邊界品質、文字忠實度）。

## 長段落要分組

可讀性問題的症狀：一個 section 超過 15 條 bullets 讀到中間忘了開頭；或 heading 下面只有一兩行，打斷閱讀節奏。修法：太長就用 `###` 分成小節（約 10-15 條），太短就和相鄰段落合併。分組不是為了形式整齊，而是讓讀者先看到 mental model，再讀細節。

小節標題應該回答「這一組規則在解決什麼問題」，例如「輔助工具能力邊界」「邊界決策」「Pass/fail 語意」，不要只用抽象分類。

## 規則要回答讀者真正會卡住的問題

**主原則：在維持可讀性與不簡化資訊的前提下，盡可能精簡。** 衡量標準是——一個沒看過這個 project 的朋友，能不能讀完規則就知道怎麼寫？做不到就要再調整，不要為了更短的句子犧牲可讀性。

不要把規則寫成抽象原則，也不要硬套固定模板。如果這條規則是在管 JSON 或檔案，就直接說清楚：欄位叫什麼、允許哪些值、檔案叫什麼、要放在哪裡。

不是每條規則都要回答全部問題。請按讀者真正會卡住的點分組，不要按抽象概念分組。常見類別（不限於這些）：
- 欄位命名：一條管一個概念。先寫唯一正確欄位名，再把同類誤寫放在旁邊。
- 欄位位置：這個欄位寫在哪份 JSON 的哪一層。
- 欄位邊界：兩個欄位語意接近時，明確說「X 進 A、Y 進 B」。
- 必填規則：每項至少要有哪些欄位、條件性必填的觸發條件。
- 流程順序：按操作順序寫。先做什麼、再做什麼、失敗時回到哪一步。
- 驗證判準：按判斷結果寫。什麼情況 pass、什麼情況 fail、需要讀哪些 evidence。
- finding notes：reviewer 的 notes 不能只寫症狀（"seg8 有文字"），必須解釋成因（"兩欄排版讓右欄文字 y 更高"）。只寫症狀會導致 repair worker 盲目微調。
- 例外：單獨寫清楚，不要藏在長句裡。
- source 層級：`shared/source.pdf`（Read tool, pages 參數）是文字 ground truth，preview 是版面 ground truth，extraction canonical 是結構化資料來源。三者有衝突時以 source.pdf 為準。Preview 解析度不足以確認上標、相似字元（`i` vs `j`、`ν` vs `v`）或小字 caption。
- 誤報防線：reviewer 的誤報比漏報傷害更大——false positive 觸發錯誤修復，讓 repair loop 越修越壞。不確定時讀 source.pdf 再判斷；仍無法判定則不標。
- 模糊地帶不標：worker 的選擇如果合理（如邊界多留幾 pixel、LaTeX 用 `\cdot` 而非 `\times`），即使 reviewer 自己會做不同選擇，也不構成 finding。只標明確違反規則或明確損壞。每條 lane 的 prompt 應提供各自的灰色地帶舉例。這條規則防止 repair loop 永遠不收斂。

長段落或同類規則多條時，給每條 bullet 一個 label prefix，例如「位置：⋯⋯」「邊界：⋯⋯」「必填：⋯⋯」。label 幫讀者一眼分辨類別，跳過不相關的條目，也方便回頭快速定位。

寫規則時特別注意這幾點：
- 先給正確寫法，再給禁止寫法。
- 禁止項目要貼在它所屬的概念旁邊，不要把不同類型的禁用名稱混成一串。
- 一條 bullet 只處理一個概念；座標、圖片路徑、例外、single source 不要壓成同一句。
- 例外放在它發生的位置，避免讀者把局部規則誤讀成全域規則。
- 長規則用 subpoints 降低負擔，但短枚舉不要硬拆。
- 相似但角色不同的欄位應該並列展示差異，不要散在兩節各講一次。
- 抽象理由移出規則本體。`schema drift`、`derived field`、`single source of truth` 可以放在原因裡，但規則本身要先告訴讀者該怎麼寫。

好的規則把讀者需要的答案放在規則本身：
- 裁切座標只叫 `crop_px`，不要寫成 `crop`、`crop_bbox` 或 `crop_region`。
- 所有圖片路徑寫進 JSON 的 `previews` 欄位（relative path），不要讓下游用 glob 推導。

過度精簡的規則雖然短，但讀者要自己拼湊上下文：
- `crop_px` 唯一；禁用 `crop`/`crop_bbox`/`crop_region`。

抽象的規則只給設計理由，沒回答怎麼寫：
- 使用 single source of truth，避免 derived field 造成 schema drift。

三者的差別是：好的規則讓讀者不用推理就知道怎麼寫；過度精簡的規則要讀者自己腦補連接詞與上下文；抽象的規則只給設計理由，還要讀者翻譯成欄位、檔名或操作步驟。抽象詞可以用來解釋原因，不能取代具體指引。

## 規則要寫成可執行的時序

規則應寫成 agent 執行時能遵守的時序。需要先完成的事，要寫成 pre-condition，不要寫成事後狀態描述。

好的寫法：
- agent 要讀 source context 之前，必須先建立 source region preview。

不好的寫法：
- 被 agent 實際讀過的 candidate，必須有 source region preview。

後者像事後描述，容易讓 agent 以為讀完再補也可以。

## 一個概念只命名一次

內容重複的症狀：同一個概念在兩個 section 各講一次，用不同措辭。修法：留主要位置的完整版，其他位置刪掉或改成一句 cross-reference。

先在格式段的 Example 或規則中定義名稱、路徑與角色。後面的流程只使用已定義的名字，不要重新分類同一批 artifact。

好的結構：
- 圖片路徑在 JSON 的 `previews` 欄位定義一次，後面的流程和規則只引用這些路徑。
- 座標只叫 `crop_px`，寫在 `crop_units[]` 裡，全文一致。

不好的結構：
- 在 `# 格式` 定義圖片路徑的命名慣例，在 `# 規則` 又重新描述一次，在流程段再用不同名字稱呼。

章節之間可以互相 cross-ref，但 cross-ref 要自然、穩定。用「對應的圖片角色見『## 圖片檔案』」這類人能讀懂的說法，不要用 plan 編號或臨時代號。若標題對應 JSON 欄位，可以用「中文標題（field_name）」保留搜尋入口。

# 改寫流程

改寫 prompt 前先列搬運對照表（每條規則的舊位置 → 新位置），確認零遺漏。改動只動需要動的行，不動周圍文字。「無損搬運」是底線。

## 不要刪掉會影響行為的 contract

舊版文件裡很多內容不是重複，而是會影響 agent 行為的 contract。改寫時應保留這類內容：
- 權責邊界：這個 agent 做什麼、不做什麼。
- 輸出路徑：artifact 寫到哪裡。
- artifact 角色：plan/extraction/visual_review 各階段 JSON 的差異。
- preview 規則：哪些圖片可以給 agent 讀，尺寸限制是多少。
- 座標規則：所有 JSON 座標都用頁面圖片 pixel coordinate。
- 裁切規則：final crop 永遠從頁面圖片裁，不從中間圖片再裁。
- caption policy：外部 caption 存 `caption_text`，不放進 crop。
- failed 語意：failed 可以被記錄，但不能算成功。
- stale file 防線：重跑時 segment 數量可能改變，殘留的舊檔案帶著錯誤狀態。需要在 script 層、prompt 層、canonical promote 層三處清理。

不該加的「contract」：不要在 prompt 中加「告訴 A 說 B 會做什麼」的 awareness lines（例如「reviewer 會檢查你的 word_ids」）。重要的是兩邊都有實質的檢查標準，不是讓 A 知道 B 的存在。如果 A 和 B 都需要同一條規則，就在兩邊各寫一次，而不是在 A 加一行「B 也會看這個」。

可以刪掉或合併的是：
- 同一條規則用不同名詞重講。
- 已在 artifact 定義中說明過的角色，後面又完整重複一次。
- 固定短枚舉被拆成多行造成閱讀中斷。
- 抽象但不改變行為的語句，例如「請謹慎處理」「確保完整性」。

## 不要把 pipeline spec 壓成 contract 摘要

pipeline spec 需要讓人看見流程如何展開。若只留下「必須產生 A/B/C」「不得做 X/Y/Z」，雖然短，但人讀起來會像規格表，不像可執行流程。

好的流程步驟應該包含：
- 這一步讀什麼。
- 這一步寫什麼。
- 這一步的 artifact 是什麼角色。
- 這一步不是什麼。
- 這一步如果失敗，應該怎麼處理。

## 判斷一段文字是否該改

改寫時可以用這幾個問題檢查：

- 這段是否讓人更容易照流程操作？
- 這段是否避免 agent 做錯事？
- 這段是否引入了舊版沒有、也尚未決定的新規則？
- 這段是否和前文重複，只是換了名詞？
- 這段如果刪掉，會不會失去一個重要 contract？
- 這段如果合併成一句，資訊是否仍完整？
- 這段如果拆成列點，是否真的更好讀？

如果答案不明確，優先保留舊版的寫法節奏，再補入必要 contract。

# JSON 與 Schema

JSON schema 應避免 derived fields。能從單一來源推出的資訊，不要在另一層重複寫，否則容易 drift。

例如頁碼如果已由 `crop_units[].page` 表達，figure 層就不要再寫 `pages`、`crop_count` 等衍生欄位。

條件性必填欄位要明確寫出觸發條件。不要只寫「必要時填寫」；要說清楚什麼情況必填、什麼情況可省略。

設計 JSON 時考慮平行化：讓平行 workers 的 output 只需 concat arrays 就能 merge。不需要 derived fields（status、summary）在 merge 時重算。Worker JSON 只包含它處理的 items。

Pass/fail 用 `findings[]` 決定：空 findings = pass，非空 = fail。不需要 decision、status、summary 欄位——derived 欄位是 schema drift 的來源。

工具的 stdout JSON 結構要和最終 JSON 的對應欄位一致，agent 可以直接搬進 output，不需要手動轉換路徑格式或重新組裝欄位。

不要發明不必要的中間產物。如果 agent 可以直接寫最終輸出，不要強迫它先寫一份中間 JSON 再轉換。多一個 artifact = 多一層可以出錯的地方、多一份需要維護的 schema。問自己：這個中間檔有誰會讀？如果只有同一個 agent 自己讀，它就不該存在。

## JSON example

JSON example 是給人和 agent 建立 schema 直覺，不只是 validator 測試資料。

好的 JSON example 應該：
- 欄位少而有代表性。
- 明確呈現 plan / extraction / visual_review 各階段 JSON 的角色差異。
- 能看出多區域 figure 如何用同一個 `figure_id` 關聯多個 `crop_units`。
- 能看出 failed figure 可以被記錄（verification.result = fail），但不影響 pass 語意（findings[] 空 = pass）。
- 路徑、preview 命名、`caption_text`、`crop_px` 都符合正文 contract。

不要為了完整而塞入大量罕見欄位。若某欄位只服務未來 validator，但目前 pipeline 還未決定，就先不要放進主 example。

Example 是 prompt 中最強的行為信號。Agent 會模仿 Example 的每一個行為——包括你不想要的。如果 Example 展示跳過某些 segment，agent 就學會跳過；如果 Example 的 review 全部 pass，agent 就傾向 rubber-stamp。設計 Example 時，假設 agent 會把它當作「正常操作」的定義。

Reviewer rubber-stamp 的根因通常是 prompt 措辭，不是缺少 script 或 validator。軟性語氣（「可以考慮」「建議檢查」）和展示跳過的 Example 合在一起，讓 agent 不認真審查。修法是改 prompt 的措辭和 Example，不是加更多基礎設施。

有時候一條明確禁令比重新設計 Example 更簡單有效。與其改 Example 來暗示「不可以跳過 segment」，不如直接寫一行「boundary_content 必須包含該邊的每一個 segment，不得跳過」。直接、明確、不會被誤讀。

