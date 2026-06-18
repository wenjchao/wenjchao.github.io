# Landing pad 位點到 ENCODE 染色質環境的注釋

1. 引用自哪篇 paper: chromatin-structure-regulatory-activity
2. Outline (任務主線): Landing pad 位點到 ENCODE 染色質環境的注釋
3. Method: 
   每株 clonal 細胞的 inverse PCR 已經把 gBC 對應到一段獨特的基因組序列，作者把這段序列比對到人類基因組標準版 (hg19 reference)，找出每個 landing pad 落在染色體幾號、座標幾。然後把座標丟進 ENCODE 計畫已經公開的 K562 染色質狀態地圖 (ENCODE segmentation tracks, ChromHMM 與 Segway 等方法產出，Hoffman et al. 2013 / Ernst & Kellis 2012)，地圖直接吐回「這個位置在 K562 裡屬於哪一類片段」——strong enhancer、weak enhancer、transcribed、repressed 等等。為什麼不自己重做 ChIP-seq？ENCODE 的 K562 是 Tier 1 reference，深度與品質遠超單一實驗室能做的規模，作者的 landing pad 就建在 K562 親代細胞裡，染色質環境本來就該一致——自己再做只是以更小樣本量重複別人已經做得很好的事。

   這張染色質地圖背後的學習方法叫 ChromHMM (Ernst & Kellis 2012)，它把基因組切成等長小區塊 (例如 200 bp)，每個區塊像一張記分卡：每個 histone mark 對應一個欄位，有訊號打 V、沒訊號打 X。整張基因組有幾百萬張這樣的記分卡，ChromHMM 用 hidden Markov model 自動把它們聚成幾個典型模式群——例如「H3K4me3 + H3K27ac 都打 V」幾乎等於 active promoter——每個群就對應一種染色質狀態，最後輸出基因組每一塊的狀態標籤。

   光看 ENCODE 四類大標籤還不夠，因為「repressed」這個籠統類別其實混了兩種不同的壓制機制：DNA 直接被甲基化封死的「永久壓制」，與 Polycomb 蛋白複合體拉緊的「可逆壓制」。後者帶有 H3K27me3 這個特殊化學標記——histone H3 蛋白尾部第 27 號離胺酸被 PRC2 加上三個甲基，再招來 PRC1 把附近 DNA 纏緊、推走轉錄機器，讓基因處於「壓住但隨時可釋放」狀態，這在文獻上叫 facultative heterochromatin (可逆性異染色質)。所以作者額外把 H3K27me3 / Polycomb 標到 Supplementary Fig. 1 與 Table 2 上——如果只看大標籤，兩種壓制會被混為一談、$L_j$ 倍率分布會看起來像隨機噪聲；標出來之後才看得出「同樣是 repressed、H3K27me3+ 的位點仍允許 reporter 部分表現」這個關鍵分辨力。

   作者從幾十株純系裡挑出來進入下游 patchMPRA 的，最終只有 15 個 landing pad。一是成本考量：每多一個位點，下游就要乘上「幾百個 CRS × 25 個 cBC × 2 個生物重複」這個倍數的 PCR 與定序量；二是設計上不是隨機抽樣而是刻意「策展」——從 dozens of 純系挑出 15 個刻意涵蓋多種染色質狀態的位點 (curated landing pad panel)，特別納入兩種 corner case：(a) 染色質地圖標為 repressed 但實際允許 reporter 表現的位點；(b) 標為 transcribed 但 reporter 反而被壓住的位點。這些反例對檢驗「multiplicative model 是否在所有環境都成立」比多挑幾個普通位點有用得多——如果模型在這種壓力測試下仍然成立，結論才真的可信。
4. 工具與材料: 
   - **hg19 reference**: 人類基因組標準版第 19 版；inverse PCR 拿到的序列比對到它得到每個 landing pad 的染色體座標。
   - **ENCODE segmentation tracks**: ENCODE 計畫對 K562 等 Tier 1 細胞株產出的「每段基因組屬於哪種染色質狀態」公開地圖；本研究直接查詢使用。
   - **ChromHMM**: 用 hidden Markov model 從多個 histone marks 的 V/X 訊號模式自動切分基因組片段的方法 (Ernst & Kellis 2012)。
   - **Segway**: 與 ChromHMM 平行的另一種基因組分段方法 (Hoffman et al. 2013)，也是 ENCODE segmentation 的來源之一。
   - **histone marks**: histone 蛋白尾部的化學修飾（甲基化、乙醯化等），不同組合對應不同染色質狀態，是 ChromHMM/Segway 的輸入特徵。
   - **H3K27me3**: histone H3 第 27 號離胺酸被 PRC2 加上三個甲基的標記，是 Polycomb 型可逆壓制 (facultative heterochromatin) 的指紋。
   - **Polycomb (PRC1 / PRC2)**: 把基因壓住的蛋白質複合體；PRC2 寫入 H3K27me3 標記，PRC1 被招來後把 DNA 纏緊、推走轉錄機器。
   - **curated landing pad panel (15 sites)**: 從幾十株 clonal 細胞中刻意挑出涵蓋多種 ENCODE 類別並包含 corner case 的 15 個位點，用於檢驗 multiplicative model 的邊界。
5. 與此篇文章的關係: 
   在《A massively parallel reporter assay dissects the influence of chromatin structure on cis-regulatory activity》這篇文章中，作者為了把每個 landing pad 對應到「它座落於哪種染色質環境」，採用了 ENCODE segmentation tracks 直接查表的方法。它解決了「自己重做 ChIP-seq 成本過高且品質難以勝過 ENCODE Tier 1 reference」的瓶頸，把 inverse PCR 拿到的 hg19 座標轉成 strong enhancer / repressed 等狀態標籤，作為 $L_j$ 倍率解讀與 multiplicative model 邊界檢驗的染色質背景資料。
