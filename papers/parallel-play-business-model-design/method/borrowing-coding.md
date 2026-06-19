# Borrowing 行為的可驗證編碼程序 (Verifiable coding protocol for "borrowing")

1. 引用自哪篇 paper: parallel-play-business-model-design
2. Outline (任務主線): Borrowing 行為的可驗證編碼程序 (Verifiable coding protocol for "borrowing")
3. Method:
   「borrowing」這個詞在訪談裡常出現——「我們也看了同行在做什麼」「我們有參考他們的介面」——但這太模糊，可能是真借、也可能是創辦人事後美化。作者把這個軟詞變成一張有規格的收據。第一步是給操作型定義 (operational definition)：把 borrowing 嚴格定為「明知地採用了另一家公司在商業模式上使用的元素」(knowingly adopting another firm's BM element)。關鍵字是「明知地」(knowingly)——排除掉「碰巧雷同」「不知不覺被影響」的情況，必須有意識地拿過來才算。為什麼非要先給操作型定義？因為如果不定義，每個 coder 心中標準不同（有人覺得「只要看過就算」、有人覺得「要原封不動搬才算」），跨案例的編碼結果就會雜亂。
   每一次被認定的 borrowing 事件都必須登記四欄資料：(1) 借了什麼具體元素？UI、資料供應商、測試用戶、平台、詞彙、還是概念？(2) 向誰借？是同類同儕新創 (peer) 還是相鄰產業老牌 (established substitute)？(3) 什麼時候借的（精確到季度）？(4) 借用的理由 (rationale) 是什麼？這四欄裡 rationale 看似多餘，但其實是關鍵的彈藥——後續要排除「borrowing 之所以有效是因為帶來合法性」這個對立解釋（§3E 第 1 條），就必須在資料層級就把動機記下來。如果 Zeus 在 Q1 2007 借同行 UI 的理由是「省工程師時間」而非「想被看起來像同行那一掛」，這條解釋差異才立得起來。最後表 4 就列出 5 家公司各自的所有 borrowing 事件，可以一行一行比對。
   Peer 跟 established substitute 是兩種完全不同的對手：peer 是跟你同期出生、做同一件事但還沒成名的新創（例如 social investing 圈裡的其他 4 家）；established substitute 是來自相鄰已成熟產業、提供替代解決方案的老牌業者（例如 Morgan Stanley、UBS、Fidelity 這些傳統理財公司）。判斷依據是 Porter (1996) 與 Adner & Kapoor (2016) 的競爭策略定義，再加 Lounsbury & Rao (2004) 的雙重檢驗：(i) 外部專家是否把兩者歸到同一產業類別？(ii) 兩者是否互相發動競爭動作（打對手廣告、互相挖角）？兩條都要有才算同類。如果不區分，最後只會得到「Zeus 借了 8 次、Icarus 借了 2 次」這種粗統計，看不出 Zeus、Hercules「大量向 peer 借」、Icarus「向 substitute 借而非 peer」這條 parallel play 模型核心的差異軸線。
   整套編碼最關鍵的把關是：每一次 borrowing 事件「必須有 2 位以上 informants 一致確認」才算成立。這個門檻的機制很物理——如果只憑一個人說「我們 Q1 借了 Zeus 的 UI」，可能是真的、可能記錯季度、可能是事後想顯得自己機靈、也可能是想把對手抹黑成被自己抄。一個人的單方面宣稱無法區分這四種狀況。但如果要求兩位以上獨立 informants（例如 Hercules 的 VP product 加 Hercules 的董事，或 VP product 加 Zeus 的工程師）都指出同一件事，四種誤判同時發生在兩個獨立來源的機率就低很多。如果省略這個門檻，假陽性（自誇抄過某 X）與假陰性（隱瞞抄過某 X）會同時湧入，且因每家公司的人格傾向不同、偏誤方向不一致，跨案例的 borrowing 統計（表 4）會失去信度，「贏家大方借、輸家不肯借」的核心對比直接被噪聲蓋住。
4. 工具與材料:
   - **Operational definition of borrowing**: 「明知地採用了另一家公司在商業模式上使用的元素」(knowingly adopting another firm's BM element)，關鍵字『明知地』排除碰巧雷同與不知不覺被影響。
   - **≥2 informant 共識門檻**: 每一次 borrowing 事件必須有兩位以上獨立受訪者一致確認才算成立，靠『獨立來源同時誤判低機率』過濾單 informant 不可信訊號。
   - **四欄登記制**: 每一次 borrowing 事件登記：借了什麼元素、向誰借、何時借（精確到季度）、借用理由 (rationale)。
   - **活動系統元素類型**: borrowing 對象細分為 UI、資料供應商、測試用戶、平台、詞彙、概念六類，後續才能跨公司比對借用樣態。
   - **Peer vs established substitute 區分**: peer 是同期同類新創，substitute 是相鄰已成熟產業的老牌；判斷靠 Porter (1996)、Adner & Kapoor (2016) 定義 + Lounsbury & Rao (2004) 的『同產業類別 + 互相發動競爭動作』雙重檢驗。
   - **Rationale (借用理由) 紀錄**: 區分『策略性借用（省研發時間）』與『跟風模仿（求合法性）』，是排除合法性說對立解釋 (§3E) 的必要彈藥。
5. 與此篇文章的關係:
   在《Parallel Play: Startups, Nascent Markets, and Effective Business-model Design》(McDonald & Eisenhardt, 2020) 這篇文章中，作者要把『贏家大方向同儕借、輸家堅持自做』這個跨案例核心對比立在硬資料上。他們採用了 borrowing 行為的可驗證編碼程序：吃前一步訪談與檔案資料，產出一張嚴格的四欄事件表（借什麼、向誰借、何時借、為何借），並要求每事件有 ≥2 informants 一致確認。這個編碼解決了軟性策略行為易被事後美化的瓶頸，為下游跨案例比較、表 4 列表與 §3E 對立解釋排除提供乾淨可審計的變量。
