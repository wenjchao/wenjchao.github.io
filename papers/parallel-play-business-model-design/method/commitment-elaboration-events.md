# Commitment 與 Elaboration 的事件級操作型定義

1. 引用自哪篇 paper: parallel-play-business-model-design
2. Outline (任務主線): Commitment 與 Elaboration 的事件級操作型定義
3. Method:
   原本「committed」「elaborated」這種詞讀起來像連續的狀態：「這家公司一直都很 commit」「他們在 elaborate 自己的活動系統」。作者拒絕這種模糊講法，要求每次出現這兩個動作時，都要在時間軸上釘一根針，記錄「哪一季發生、在哪家公司、針對哪個模板或哪類使用者」。每家公司就會有一條畫滿針的時間軸，五條軸並排（Langley 1999 的 parallel timeline comparison）就能直接用眼睛掃出「Zeus 在 2009 Q1 commit 時 Hercules 還沒；Icarus 早在 2008 就 commit 了」這種節奏差異。過程理論的關鍵不是「有沒有」做某件事，而是「什麼時候、用什麼節奏」做；把事件變成時間軸上的點，節奏差異才變得可見、可比、可教。
   Commitment 判定用雙條件，缺一不可。第一條：多位 informants 一致表示「選擇已經做出來了」——不只是創辦人嘴上說，要 VP 級主管、董事、投資人都認得這個轉折。第二條：該公司開始「只把資源投入所選的單一模板」——例如不再同時請律師走 SEC 流程又寫廣告投放工具，而是專心走其中一條。兩個條件都成立的那一季，就在時間軸上釘下 commitment 的針，並標上「commit 到哪個模板」（例如 Zeus → financial intermediary @ Q1 2009；Narcissus → advertising destination @ Q4 2008）。為什麼用季度而不是月或年？太細，受訪者事後根本記不清是 3 月還是 4 月做的決定，是假精確；太粗，會把同一年內五家公司的節奏差異整個壓平——Zeus Q1 押注、Hercules Q3 押注，在「年」這個粒度上會被當成同時。季度剛好讓多位 informants 都對得起來，又夠細看出公司之間幾個月的領先落後。雙條件這個設計本身就是在防「單 informant commitment」的風險——創業者事後敘述很容易把 commit 時間提前美化成「我們其實一直都知道要走這條路」，要靠資源實際只投單一模板的客觀流向交叉驗證才能擋下這層滑順。
   Elaboration 判定把活動系統拆成四類核心元素逐一看：(1) 使用者介面 (UI)；(2) 產品功能 (product features)；(3) 演算法 (algorithms)，例如評估投資績效的演算法；(4) 行銷 (marketing)。任何一類在某一季被加進去，就在時間軸上釘下對應的 elaboration 針。這四類涵蓋「客戶看到什麼 (UI、行銷)、用到什麼 (功能)、底層怎麼跑 (演算法)」三個層次，加起來才算活動系統真的被填血填肉。更關鍵的是加層級判定：不只看「有沒有加」，還看「是否針對特定使用者群調校 (tailored)」。例如 Hercules Q3 2009 採用「模仿知名社交網站的 social UI」就被編碼為朝 amateur 投資人方向 tailored elaboration——這顆針不只是「加了 UI」，而是「加了專屬給 amateur 的 UI」，未來如果要轉型給專業基金經理人就要拆掉重做。沒抓這層的話，Zeus 與 Hercules 在某段時間的針數會看起來差不多，但 Hercules 加的是「專為散戶調校」、Zeus 加的是「故意保留通用」，這在 parallel play 模型裡是「elaborate」與「pause before elaborating」的根本差別；沒區分 tailored，贏家「先暫停再 elaborate」的節奏完全會被洗掉。
4. 工具與材料:
   - **commitment (event-coded)**: 需同時滿足「多位 informants 一致」+「資源只投單一模板」，才釘下 commitment 的時間戳。
   - **elaboration (event-coded)**: 看 UI、product features、algorithms、marketing 四類核心 activity-system 元素哪一季被加進去，每一類各自釘針。
   - **tailored elaboration**: 加層級判定——不只看「有沒有加」，還看「是否針對特定使用者群調校」，量的是公司用掉多少商業模式彈性。
   - **business-model template**: 選定的賺錢模板，例如 financial intermediary 或 advertising destination；commitment 必須對應到一個明確模板。
   - **quarterly timestamp**: 時間戳粒度設在季度，平衡受訪者回憶可靠性與跨案例節奏差異的解析度。
   - **parallel timeline comparison (Langley 1999)**: 把五家公司的事件時間軸並排成五條橫線，用眼睛直接掃出「先後、節奏、間隔」這些跨案例差異。
   - **activity system (四類元素)**: 由 UI、product features、algorithms、marketing 四類元素組成，是 elaboration 編碼的覆蓋範圍。
5. 與此篇文章的關係:
   在《Parallel Play: Startups, Nascent Markets, and Effective Business-model Design》這篇文章中，作者要說明的核心結論之一是「贏家先 commit 一個模板、再刻意暫停才 elaborate」，這需要把過程動詞變成可以畫在時間軸上的事件。為此作者設計了 commitment 與 elaboration 的事件級操作型定義，吃進三波訪談與檔案資料，產出五家公司各自一條釘滿事件的季度時間軸；下游 Langley (1999) parallel timeline comparison 就靠這五條軸並排，把 parallel play 框架的時間節奏（圖 1 的核心畫面）變成可以被肉眼比較的證據。
