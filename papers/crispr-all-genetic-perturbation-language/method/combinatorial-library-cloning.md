# 10,240-member 四維組合 library 之迭代池化克隆

1. 引用自哪篇 paper: crispr-all-genetic-perturbation-language
2. Outline (任務主線): 10,240-member 四維組合 library 之迭代池化克隆
3. Method:
   作者要一次造出「Domain × Gene × Knockout × Knockdown」四維全組合 library。他們從前一步 CACTUS 排行榜裡挑出每類別的強選手：CAR 訊號零件 10 個、過表達基因 16 個、knockout 標的 8 個、knockdown 標的 8 個，相乘得到 $10 \times 16 \times 8 \times 8 = 10{,}240$ 種獨一無二的四維組合。每一條構築都共用一層底座：前段接 tNGFR（從 NGF 受體切掉訊號尾巴、只留表面段的報告蛋白，讓流式能抓出成功 knockin 的細胞），接著是 FMC63 CD19-scFv（辨識癌細胞 CD19 表面標記的抗體片段，組成完整 CAR 的辨識頭），兩端再各接一段 TRAC homology arm（與 TRAC 基因組區段同源的序列，幫助構築精準插到 TRAC 位點）。整池克隆採「池化迭代克隆 (iterative pooled cloning)」策略：先把 Domain 子庫整池混好，再用 CRISPR-All 的兩套 Type IIS 切口（BsaI 切內部 stuffer、BbsI 切外部 stuffer）整池切開、把 Gene 子庫整池接上，接著依序加上 Knockout、Knockdown 子庫。每一輪都是池進池出，反應數量固定，最終一次拿到 10,240 種四維組合。

   造出來的池子要送進 T 細胞才有用——10,240 種不同 insert 之所以能精準落到同一個基因組座標，靠的是兩端的 TRAC homology arm。電穿孔同時送進 enCas12a 把 TRAC intron 1 切出一個雙股斷裂，細胞啟動自身的修補機制 (homology-directed repair, HDR)：它會去找「跟斷裂兩側序列一樣的模板」，把模板中間的內容複製貼回斷裂處。提供的構築就是那個模板，中間夾的四元組合跟著被貼進 TRAC 位點。每條構築兩端都一樣，不管中間是什麼組合都會落在同一座標。實測 5 位捐贈者平均整合效率 35%、100% 庫呈現、90% 構築濃度落在 1 log 內——意思是 library 每一條都被代表到，且最強最弱濃度差不超過 10 倍，這對下游池化篩選的統計力是關鍵。

   為什麼挑 10,240 而不是把整個 CACTUS 排行榜全組合？池化篩選有個硬指標：每條構築至少要 1000 顆成功編輯的 T 細胞當樣本量（pool screen coverage ≥ 1000×），否則統計信號會被細胞數雜訊蓋過。10,240 × 1000 = 一千萬顆編輯 T 細胞，已經逼近單一捐贈者能提供的上限。所以作者改用兩段式策略：先用 CACTUS 一輪 ×1 篩選找出每類別前段強選手 (8-16 個)，再讓這些強選手互相搭配。1000× 的物理意義是「每條構築一開始有 1000 顆細胞當代表」——重複刺激會大量殺死細胞，若起點只有 10 顆可能歸零，根本分不出「真的負調節」與「樣本太少剛好死光」。1000× 是讓最後條碼計數差異 (log2 fold change) 落在 DESeq2 算得出統計顯著性的範圍。

   迭代池化克隆有個固有雜訊：每一輪 Type IIS 切口加接合，都有機率讓 Domain-A 的元件跑去跟 Gene-B 的條碼黏在一起，產生「條碼跟實際裝進去的元件對不上」的跨段對接 (template switching)。四輪累積下來——單類別 fidelity (signaling domain 92.3%、gene 92.2%、knockout 76.2%、knockdown 74.5%) 連乘約 48%，實測 PacBio 顯示 60% 構築四個位置都正確。如果直接用 short-read amplicon 跑下游，short-read 只能讀 11 bp 條碼，分辨不出條碼對應的元件是不是設計上那個——40% 名實不符的 chimera 會被當成真實組合送進 hit list，得到的「最強組合」可能根本沒被裝進去過。為了避開這個陷阱，作者改用 PacBio HiFi 長讀定序，一條 read 從頭讀到尾同時看到條碼與四個元件序列，等於替每個組合算出可信度上限，把這 40% 雜訊納入下游 DESeq2 的誤差模型。

4. 工具與材料:
   - **iterative pooled cloning**: 池化迭代克隆，把每一類子庫整池切開再整池接上下一類，反應數固定就能造出 10,240 種四維組合。
   - **tNGFR**: 從 NGF 受體切掉訊號尾巴、只留表面段的報告蛋白，讓流式能抓出真的成功 knockin 的細胞。
   - **FMC63 CD19-scFv**: 辨識癌細胞 CD19 表面標記的抗體片段，是基本款 CAR 的辨識頭，組成所有構築共用的 CAR 底座。
   - **TRAC homology arm**: 與 TRAC 基因組區段同源的序列，配合 enCas12a 切口讓構築透過 HDR 精準插入 TRAC 位點。
   - **homology-directed repair (HDR)**: 細胞自身修補雙股斷裂的機制，會找與斷裂兩側相同的模板把中間內容複製貼回，被作者借來定點插入。
   - **Type IIS 切口 (BsaI / BbsI)**: CRISPR-All 用來重複切割內部/外部 stuffer 的兩套切酶系統，使每輪都能精準切開再接上下一個元件。
   - **template switching**: 池化接合反應中元件序列跑去跟錯誤條碼黏在一起，造成「條碼跟實際裝進去的元件對不上」的跨段對接雜訊。
   - **PacBio HiFi 長讀定序**: 一條 read 從頭讀到尾的高保真長讀技術，能同時看到條碼與四個元件序列，量化每個組合的構築完整度。
   - **pool screen coverage (1000×)**: 池化篩選的覆蓋度門檻，每條構築起點至少 1000 顆編輯細胞，才能讓 DESeq2 算出有統計力的條碼計數差異。
   - **library representation**: library 中每一條構築都至少被代表到的比例，本研究在 5 位捐贈者中達 100%、90% 構築濃度落在 1 log 內。

5. 與此篇文章的關係:
   在《A unified genetic perturbation language for human cellular programming》這篇文章中，作者為了驗證 CRISPR-All 能跨類別組合擾動是否真能跑得通，採用了「迭代池化克隆」一次造出 10,240 種四維組合 library。它解決了「四類擾動以往各自為政、組合空間永遠無法窮舉」的瓶頸，吃進 CACTUS ×1 篩出的強選手清單，產出可直接電穿孔進 T 細胞的構築池，餵給下游重複刺激 pool screen 與 PacBio fidelity 校正。
