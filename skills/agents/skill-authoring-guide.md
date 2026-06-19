This document is composed of bilingual English-Chinese parallel text. The Chinese version is for the user's reading, so keep it natural, fluent, and easy to read while preserving full consistency between the two languages.

# Skill Authoring Guide

This guide is for writing local skills that use models well instead of turning them into script runners.

Core rule:

- code extracts, transforms, validates, and serializes evidence
- the model interprets ambiguous evidence and makes meaning-bearing decisions
- audits verify and localize problems

If a skill does not make that split clear, it will drift toward brittle heuristics, rigid rituals, or fake certainty.

## Preflight

Before writing or rewriting a skill, check:

- The deliverable is clear.
- The ground truth is named explicitly.
- The first paragraph states the task, not project history.
- File inputs, outputs, and non-modified inputs are explicit when files are involved.
- The skill can stand alone if it may be used independently.
- The output format is proportional to the task.
- The skill leaves enough evidence for later review when later review matters.

## Code And Model Boundary

Helper scripts are evidence tools, not authority.

Code should handle:

- parsing
- rendering
- geometry
- normalization
- candidate generation
- deterministic validation
- mechanical serialization

The model should handle:

- ambiguous interpretation
- structure recovery
- semantic reconstruction
- crop/table/equation/text decisions when evidence is visual or meaning-bearing
- audit judgment
- faithful repair

Python may help navigate evidence or serialize model decisions. It must not replace model judgment when the task depends on meaning.

The boundary is certainty, not difficulty. Code should only perform operations that produce exactly one correct output for any valid input. If an operation can produce wrong output — even on rare inputs — it belongs to the model. This applies even when the operation feels mechanical, such as stripping document wrappers from an HTML file or detecting text artifacts with regex.

When a skill uses a decision record followed by mechanical serialization, the serialization script should run with only the decisions and fixed templates. If it must read another source file, it is choosing what to extract, and that choice belongs to the model. A serialization script that branches on text content rather than element type is doing model work.

When script-led drift is a realistic risk, name the failure signals in the skill. General signals: scripts that read evidence and emit final prose, rebuild loops that silently rewrite artifacts, or helpers treated as ground truth.

For complex semantic outputs, consider requiring a small decision record before mechanical serialization. Use this only when it makes authorship and review clearer; do not add ceremony to purely mechanical skills.

## Ground Truth

Every skill should say what counts as ground truth, such as:

- source PDF
- original image
- raw repository state
- user-provided text
- database or API response

If ground truth is missing, say what partial work is still possible and what cannot be verified.

Good pattern:

> The source artifact is the ground truth. Helper outputs are evidence, not truth. If evidence looks suspicious, inspect the source artifact and override bad helper output. Record uncertainty instead of guessing.

## Failure Mechanisms

Explain why the task fails, not just symptoms to search for.

Weak:

- watch for split words
- watch for fused words
- watch for mixed columns

Better:

- PDF extraction infers word boundaries from glyph spacing
- PDF extraction infers reading order from geometry
- captions, tables, and page chrome occupy the same visual page as body text

When the model understands the mechanism, it can handle cases not listed in examples.

## Runtime Shape

Good runtime skills:

- are short enough to hold in working memory
- ask the model to track 3-5 core judgment dimensions
- avoid mandatory diagnosis rituals unless the task is mechanical
- use examples to explain mechanisms, not to define the whole search space
- tell the model when to use a fast path and when to slow down
- allow honest uncertainty

Overload signs:

- many sections all trying to be the final takeaway
- long include/exclude taxonomies where one judgment question would work
- repeated explanations across related skills
- output formats that force ceremony even when there are no findings

Line count is only a smell, but useful:

- under 80 lines: usually healthy for a focused runtime skill
- 80-160 lines: reasonable for a complex skill
- over 160 lines: review for duplication and hidden checklists

## Output Design

Choose the least formal output that still supports downstream use.

- Simple tasks can produce concise prose.
- Structured reports are useful when another skill or reviewer will consume the result.
- Audit skills should not silently repair.
- Repair skills should define what can be changed and what must be preserved.
- Reviewer-style skills should separate artifact quality from process quality when both matter.
- When a skill determines whether work is complete, it must separate artifact quality from process compliance. A usable artifact produced by a noncompliant process is not a clean closure.

For document work, preserve:

- author wording
- names, units, symbols, citations, and references
- punctuation and bracket conventions when meaningful
- structural boundaries when the source shows a real break

Allowed changes should be limited to evidence-backed correction, such as extraction-induced splits, merges, ordering errors, or non-target contamination.

If a detail cannot be recovered, mark uncertainty instead of guessing.

## Bilingual Skill Translation

When a skill file is bilingual, the English section is the operational source text and the Chinese section is for the user's reading. The two sections must stay fully consistent, but consistency does not mean word-for-word English-shaped Chinese.

The Chinese section must not have translationese. It should read like a Chinese technical document written directly for the user: natural, clear, and easy to follow. The content must match the English; the sentence shape does not have to match the English.

Use these rules:

- Put the complete English section first, then start the complete Chinese section under the standard Chinese-counterpart heading. Do not interleave English and Chinese within each small section.
- Before translating, ask: "If this rule were originally written in Chinese, how would I say it?"
- Preserve the rule, action, condition, exception, and required result. Freely change word order, split or merge sentences, and turn English noun phrases into clear Chinese instructions.
- Avoid English grammar wearing Chinese words: awkward causatives, vague subjects, noun-heavy phrasing, and direct imports where normal Chinese is clearer.
- Use natural Chinese decisions and actions rather than literal verb-by-verb imports from English.
- Preserve only exact literals that are part of the execution contract: commands, paths, filenames, JSON keys, enum values, code identifiers, tool names, package names, and quoted output values.
- Keep Markdown structure aligned with the English section so a reader can compare sections easily.
- Preserve code blocks verbatim unless the code block is explicitly an explanatory prose example.
- Do not mechanically replace English inside identifiers, filenames, paths, commands, or JSON examples.
- Avoid half-translated phrases when a normal Chinese phrase is clear.
- If the Chinese sounds like translated English, rewrite it.

Good pattern:

- The English source says not to call a stage complete.
- The Chinese section expresses the same rule in natural Chinese technical writing.

Bad pattern:

- The Chinese section copies the English verb pattern mechanically and sounds unnatural.

For bilingual maintenance, update the English first when changing behavior, then update the Chinese to match. If the Chinese reveals that the English is vague, improve the English too.

## Evidence And Reviewability

For tasks that may be reviewed later, preserve observable evidence of important decisions.

Useful evidence can include:

- source files or page images read
- helper commands run
- intermediate candidates
- decision records before serialization
- validation summaries
- uncertainty notes

Trace requirements belong in the runtime or pipeline skill, not in every skill. The general principle is: if a later reviewer must distinguish model judgment from helper-script output, preserve enough evidence to make that distinction possible.

## Skill Types

### Mechanical

Examples: render pages, crop known coordinates, normalize glyphs, run deterministic checks.

Mechanical skills can be procedural and short. They do not need elaborate decision records.

### Hybrid

Examples: extract tables, extract figures, extract equations, assemble structured data from raw extraction.

Hybrid skills should name the ground truth, explain failure mechanisms, and keep helpers subordinate to model verification. If layout matters, visual evidence is usually required.

### Intelligence-First

Examples: reconstruct prose from ambiguous evidence, audit semantic fidelity, repair confirmed corruption, synthesize notes.

These skills should focus on fidelity, ambiguity, and judgment boundaries. They should not read like operating manuals.

## Cross-Skill Design

Avoid overlapping responsibilities.

Clean role separation:

- producer creates
- critic evaluates
- repair fixes confirmed defects
- reviewer judges process, residual risk, and closure

Across a pipeline, each schema, path convention, enum, scope rule, or execution contract should have one canonical home. Other skills should reference it rather than restating it in detail.

Do not make every skill run the whole pipeline. Do not make critic skills produce repaired artifacts unless repair is explicitly requested.

## Validation

Do not judge a skill only by whether the prompt sounds smart.

First-pass generated artifacts deserve more skeptical audits than artifacts that have already survived targeted repair and review.

Validate on a small mixed set:

- a clean simple case
- a visually busy or structurally ambiguous case
- a case with nearby non-target content

Check:

- correct content included
- wrong content excluded
- wording or structure preserved
- obvious corruption fixed
- no invented or restyled content
- cost and effort are reasonable
- process compliance as well as artifact quality, when the task is part of a pipeline

Automated checks tend to catch over-inclusion, such as contamination and duplication, more easily than under-inclusion, such as dropped content. Design validation to check both directions explicitly.

One proof of concept supports the direction. It does not replace broader validation.

## Anti-Patterns

Avoid these unless the task is truly mechanical:

- changelog-first skill
- wall-of-text runtime instruction
- mandatory diagnosis phase for every case
- fixed output ritual regardless of findings
- helper output treated as truth
- long taxonomy where one judgment question would work
- duplicate failure-theory sections across related skills
- multiple competing summaries or final takeaways
- Python that simulates reading comprehension with regexes and exception lists
- single opaque script that applies multiple semantic decisions and serializes the final artifact, making model authorship unverifiable

Better:

- state the task and ground truth early
- keep helper output optional and overridable
- explain mechanisms briefly
- let the model use adaptive depth
- keep uncertainty visible

## Bottom Line

Good skill design is restraint. Put each kind of intelligence where it belongs: code for mechanics, model for interpretation, audits for verification.

---

# 中文對照

這份文件由中英雙語對照組成。中文對照是給我看的，請務必保持兩語言內容完全一致，並讓中文流暢通順、易於閱讀。

# 技能撰寫指南

這份指南用來撰寫能善用模型的本地技能，而不是把模型降格成腳本執行器。

核心規則：

- 程式碼負責擷取、轉換、驗證和序列化證據。
- 模型負責解讀模糊證據，並做出涉及意義的決策。
- 稽核負責驗證結果並定位問題。

如果技能沒有清楚劃分這三種責任，就容易滑向脆弱的啟發式規則、僵硬流程，或看似確定但其實不可靠的結論。

## 預檢

撰寫或重寫技能之前，先檢查：

- 交付成果是否明確。
- 是否明確點名最終依據。
- 第一段是在說明任務，而不是交代專案歷史。
- 涉及檔案時，輸入、輸出和不可修改的輸入是否明確。
- 若技能可能獨立使用，它是否能獨立成立。
- 輸出格式是否與任務規模相稱。
- 若後續需要審查，技能是否留下足夠證據。

## 程式碼與模型的邊界

輔助腳本用來提供證據，不具權威性。

程式碼應處理：

- 解析
- 轉出圖片
- 幾何計算
- 正規化
- 產生候選項
- 確定性驗證
- 機械式序列化

模型應處理：

- 模糊解讀
- 結構恢復
- 語義重建
- 當證據是視覺證據，或決策本身涉及意義時，由模型決定裁切、表格、方程式和文字內容
- 稽核判斷
- 忠實修復

Python 可以協助瀏覽證據，或序列化模型已做出的決策；一旦任務取決於意義判斷，就不能讓 Python 取代模型。

劃分邊界的標準是確定性，不是難度。程式碼只能做「對任何有效輸入都保證產出唯一正確結果」的事。只要有可能出錯——即使機率很低——就該交給模型。剝離 HTML 文件包裝、用 regex 偵測文字殘留，這類操作感覺很機械，但都可能在意外輸入上出錯，所以仍該由模型處理。

如果技能採用「模型先寫決策紀錄、再由腳本序列化」的架構，腳本應只憑決策和固定模板就能執行。腳本一旦需要另外讀來源檔案，就代表它在決定要從中提取什麼——那是模型該做的判斷。序列化腳本若根據文字內容而非元素類型做分支，也是越界。

如果某個技能確實可能出現腳本主導的偏移，要在技能裡直接點名警訊。常見信號包括：腳本讀取證據後直接輸出最終文字、重建迴圈靜默覆寫成果檔，或把輔助工具的輸出當成最終依據。

面對複雜的語義輸出，可以考慮要求模型在機械式序列化前先寫一份小型決策紀錄。只有在這能讓作者責任和審查更清楚時才加；純機械技能不需要這層儀式。

## 最終依據

每個技能都應說清楚什麼才是最終依據，例如：

- 來源 PDF
- 原始圖片
- 原始 repo 狀態
- 使用者提供的文字
- 資料庫或 API 回應

如果缺少最終依據，要說明哪些部分仍可完成，哪些內容無法驗證。

好的寫法：

> 來源成果檔是最終依據。輔助工具輸出是證據，不是最終依據。如果證據看起來可疑，要檢查來源成果檔，並覆寫錯誤的輔助工具輸出。記錄不確定性，不要猜。

## 失敗機制

要說明任務為什麼容易失敗，不要只列出需要留意的症狀。

較弱的寫法是：

- 注意拆字
- 注意黏字
- 注意混欄

較好的寫法是：

- PDF 擷取會根據字形間距推斷字詞邊界
- PDF 擷取會根據幾何位置推斷閱讀順序
- 圖表說明、表格和頁面固定元素與正文位於同一個視覺頁面上

模型理解失敗機制後，就能處理範例沒有列出的情況。

## 執行時設計

好的執行時技能應該：

- 短到能留在工作記憶中
- 要求模型追蹤 3 到 5 個核心判斷面向
- 除非任務本身是機械性的，否則避免強制診斷儀式
- 用例子解釋機制，而不是用例子定義整個搜尋範圍
- 告訴模型何時可以快速處理，何時必須放慢
- 允許誠實標記不確定性

負擔過重的跡象包括：

- 很多章節都想充當最終重點
- 長篇包含/排除分類，其實可以由一個判斷問題取代
- 相關技能之間重複解釋同一件事
- 即使沒有發現問題，輸出格式仍強迫執行固定儀式

行數只是粗略警訊，但很有用：

- 80 行以下：對聚焦的執行時技能通常健康。
- 80 到 160 行：對複雜技能合理。
- 超過 160 行：應檢查是否有重複或隱藏檢查清單。

## 輸出設計

選擇能支援下游使用的最輕量輸出格式。

- 簡單任務可以產生精簡文字。
- 如果另一個技能或審查者會讀取結果，結構化報告會很有用。
- 稽核技能不應靜默修復。
- 修復技能應定義哪些內容可以改、哪些必須保留。
- 當成果品質和流程品質都重要時，審查型技能應分開處理兩者。
- 如果技能要判斷工作是否完成，就必須分清成果品質和流程合規性。即使成果可用，只要流程不合規，也不能算乾淨收尾。

處理文件時，要保留：

- 作者原文用語
- 名稱、單位、符號、引用和參考文獻
- 有意義的標點和括號慣例
- 來源中真實存在的結構邊界

只有在有證據支持時才可修正，例如修正擷取造成的拆分、合併、排序錯誤，或非目標內容污染。

如果細節無法恢復，要標記不確定性，不要猜。

## 雙語技能翻譯

如果技能檔案採用中英雙語，英文區是實際執行時的依據，中文區是給使用者閱讀的版本。兩者內容必須完全一致，但「一致」不代表逐字照搬英文句型。

中文區不能有直譯腔。它應該讀起來像一份直接寫給使用者的中文技術文件：自然、清楚、順口。內容必須和英文一致；句型不必和英文一致。

使用下列規則：

- 文件排列必須先完整寫完英文區，再用 `# 中文對照` 開始完整中文區。不要在每個小節內交錯放英文和中文。
- 翻譯前先問：「如果這條規則原本就是用中文寫的，我會怎麼說？」
- 保留規則、動作、條件、例外和必要結果。可以自由調整語序、拆句或合句，也可以把英文名詞片語改寫成清楚的中文指令。
- 避免披著中文詞的英文語法：彆扭的使役句、主詞不清、名詞堆疊，以及明明中文更清楚卻硬搬英文詞。
- 用自然中文描述判定和動作，例如「將該圖判定為未通過」，不要寫「讓圖失敗」；用「已知缺陷」，不要寫「承認的缺陷」。
- 只保留屬於執行契約的精確字面值：指令、路徑、檔名、JSON 欄位、枚舉值、程式識別名稱、工具名稱、套件名稱，以及被引用的輸出值。
- Markdown 結構要和英文區對齊，方便讀者比較。
- 程式碼區塊預設原樣保留；只有當它明確只是說明性文字範例時，才可以翻譯。
- 不要機械式替換識別名稱、檔名、路徑、指令或 JSON 範例內的英文。
- 不要寫半中半英的句子，例如「final artifact 品質」；如果「最終成果品質」清楚，就用中文。
- 如果中文讀起來像翻譯英文，就重寫。

好的翻譯：

- 英文："Do not call the stage complete."
- 中文：「不要將該階段標記為完成。」

不好的翻譯：

- 中文：「不要呼叫階段完成。」

維護雙語文件時，若要改變行為，先更新英文，再更新中文，使兩者一致。如果翻成中文時發現英文太模糊，也應順手改善英文。

## 證據與可供審查

對日後可能需要審查的任務，要保留關鍵決策的可觀察證據。

有用證據可包括：

- 讀取過的來源檔或頁面圖片
- 執行過的輔助指令
- 中間候選項
- 序列化前的決策紀錄
- 驗證摘要
- 不確定性註記

追蹤要求應放在執行時技能或流程技能中，不要每個技能都塞一份。原則是：如果後續審查者需要分辨某個結論是模型判斷還是輔助腳本輸出，就要保留足夠證據，讓這件事查得出來。

## 技能類型

### 機械型

例子：轉出頁面圖片、裁切已知座標、正規化字形、執行確定性檢查。

機械型技能可以短而程序化，不需要複雜的決策紀錄。

### 混合型

例子：擷取表格、擷取圖、擷取方程式、從原始擷取結果組裝結構化資料。

混合型技能應點明最終依據，解釋失敗機制，並讓輔助工具的輸出接受模型驗證。如果版面很重要，通常需要視覺證據。

### 判斷優先型

例子：從模糊證據重建文章、稽核語義忠實度、修復已確認的損壞、整理筆記。

這類技能應聚焦於忠實度、模糊處理和判斷邊界，不應寫成操作手冊。

## 跨技能設計

避免責任重疊。

清楚分工應該是：

- 產生者負責建立成果。
- 稽核者負責評估成果。
- 修復者負責修復已確認缺陷。
- 審查者負責判斷流程、剩餘風險和是否可以收尾。

在一條流程中，每個結構規格、路徑慣例、枚舉值、範圍規則或執行契約，都應只有一個標準歸屬。其他技能應引用它，而不是詳細重述。

不要讓每個技能都執行整個流程。也不要讓稽核技能產生修復成果，除非使用者明確要求修復。

## 驗證

不要只憑提示詞聽起來聰明，就判定技能設計良好。

第一次產出的成果，需要比已經過針對性修復和審查的成果更嚴格地稽核。

用一小組混合案例驗證：

- 乾淨簡單的案例
- 視覺繁忙或結構模糊的案例
- 附近有非目標內容的案例

檢查：

- 是否包含正確內容
- 是否排除錯誤內容
- 是否保留措辭或結構
- 是否修復明顯損壞
- 是否沒有發明內容或改寫風格
- 成本和工作量是否合理
- 當任務屬於流程的一部分時，流程合規性是否和成果品質一起達標

自動檢查通常比較容易抓到納入過多，例如污染和重複；比較不容易抓到遺漏，例如內容被漏掉。驗證設計必須明確檢查兩個方向。

一個概念驗證可以支持方向，但不能取代更廣泛的驗證。

## 反模式

除非任務本質上真的機械，否則避免下列寫法：

- 一開始就寫變更日誌的技能。
- 大段堆疊的執行時指令。
- 每個案例都強制進入診斷階段。
- 不管有沒有發現，都要求固定輸出儀式。
- 把輔助工具輸出當成最終依據。
- 用很長的分類表取代一個判斷問題。
- 在相關技能中重複同一套失敗理論。
- 多個互相競爭的摘要或最終重點。
- 用正規表示式和例外清單假裝在做閱讀理解的 Python。
- 用單一不透明腳本同時套用多個語義決策，並序列化最終成果，使模型作者責任無法查證。

更好的做法：

- 開頭就說清楚任務和最終依據。
- 讓輔助工具輸出保持可選、可覆寫。
- 簡短說明機制。
- 讓模型依情況調整處理深度。
- 保留可見的不確定性。

## 底線

好的技能設計靠的是克制。把每種智慧放在該放的位置：程式碼處理機械工作，模型處理解讀，稽核負責驗證。
