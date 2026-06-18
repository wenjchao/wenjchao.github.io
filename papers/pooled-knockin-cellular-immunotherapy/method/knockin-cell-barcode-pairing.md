# Knockin Barcode 與 Cell Barcode 配對

1. 引用自哪篇 paper: pooled-knockin-cellular-immunotherapy
2. Outline (任務主線): Knockin Barcode 與 Cell Barcode 配對
3. Method: 
   每顆細胞在 PoKI-Seq 裡掛著兩個獨立來源的條碼：細胞編號 (cell barcode) 是 10x 機器在每顆細胞被包進油滴時、由小珠子上的 DNA 蓋上去的，整顆細胞所有 mRNA 都帶同一個 cell barcode；構築身分條碼 (knockin barcode) 是作者在設計 36 種 DNA 模板時，刻意在每個模板的 TCRαV 區藏一段 6 個鹼基的獨特序列，T 細胞接到哪一份模板，這段 6 bp 序列就會永久寫進染色體並被轉錄出來。但 10x v3 標準的 scRNA-seq 只讀 mRNA 最後 91 個鹼基，knockin barcode 躲在轉錄本更上游讀不到，所以作者把同一份 cDNA 拆兩路：25% 走標準轉錄組、50% 走「以 knockin barcode 為目標」的靶向 PCR 擴增 (amplicon)，得到一段同時帶 cell barcode 和 knockin barcode 的短片段。Illumina 從兩端各讀一次：Read1 讀頭端的 cell barcode 與 UMI、Read2 讀尾端的 knockin barcode，剛好一端一個。
   配對動作用的是 R 的短序列分析套件 ShortRead 中的模式比對函式 matchPattern。比對的「圖樣」是 TCRα 3' 端那段已知序列加上一段 6 個位置可變的退化鹼基 (degenerate bases)，可變的位置就是 knockin barcode 該出現的格子。掃 Read2 找到 knockin barcode 後，回頭抓「同一對」的 Read1（Illumina 雙端定序對同一條 amplicon 各讀一次，兩端輸出的 fastq 同行就保證同一條原始分子，不是猜的），從中讀出 cell barcode 與 UMI，完成「這條 mRNA 副本 → 這顆細胞 → 這個構築」三層配對。比對時允許 1 個鹼基錯配——因為定序機器每讀 100 個鹼基大約錯 1 個，6 bp 全對上會丟掉一大堆只錯一格的真實 reads；但 36 條 barcode 之間差距 ≥ 2，1 mismatch 還能正確判定屬於哪條，不會誤分到別的構築。0 mismatch 會把能指派的細胞量壓得太低；2 mismatch 又會讓鄰近 barcode 互相重疊、構築身份混亂。
   光是「比對到」還不夠，作者再加兩道過濾。第一道：要求至少 3 個 UMI 同 barcode 才指派——1 個 UMI 只代表「1 條 mRNA 分子讀到這個 barcode」，可能來自油滴外漏的 mRNA、上機時索引被機器搞混 (index hopping)、或 PCR 過程偶發跑錯模板；3 個獨立 UMI 等於 3 條不同的原始 mRNA 都指向同一個構築，三條同時出錯的機率極低，能濾掉一大半偽配對。第二道：把「同時讀到超過 2 個 knockin barcode」的細胞剔除——一顆人類 T 細胞最多 2 條 TRAC allele，所以理論上最多帶 2 個不同的 knockin barcode；讀到 3 個以上最可能是油滴包到兩顆細胞 (doublet)、或 PCR 過程的 template switching 把別個構築的 barcode 黏進來，這類細胞無法唯一指派構築，留著只會污染後續分析。
4. 工具與材料: 
   - **cell barcode**: 10x 油滴內小珠子上的 DNA 標籤，把整顆細胞所有 mRNA 標成同一個編號。
   - **knockin barcode**: 作者在每個 polycistronic 模板的 TCRαV 區藏的 6 bp 獨特序列，整合進染色體後永久標記細胞拿到哪一個構築。
   - **UMI**: 反轉錄時加的隨機 DNA 標籤，每條原始 mRNA 拿到唯一標籤，用來區分真實分子與 PCR 副本。
   - **ShortRead matchPattern**: R 的短序列分析套件 (Morgan et al., 2009) 中的模式比對函式，用一段含退化鹼基的圖樣掃 fastq reads 找出 knockin barcode。
   - **degenerate bases pattern**: TCRα 3' 端已知序列加上 6 個可變位置，用於 matchPattern 對位、抓出每個構築的 barcode。
   - **1 mismatch 容忍**: 允許 1 個鹼基錯配，平衡定序錯誤造成的真實 read 損失與鄰近 barcode 誤分的風險。
   - **≥3 UMI 指派門檻**: 要求同一細胞至少 3 個獨立 UMI 都讀到同一 knockin barcode 才指派，濾掉污染與單一證據力過低的偽配對。
   - **> 2 knockin barcodes 過濾**: 剔除同時帶 3 個以上 barcode 的細胞，避免 doublet 或 template switching 干擾構築身份指派。
   - **Read1 / Read2 配對**: Illumina 雙端定序對同一條 amplicon 從兩端各讀一次，輸出 fastq 同行保證來自同一條原始分子，用來把 knockin barcode 與 cell barcode + UMI 物理配對。
5. 與此篇文章的關係: 
   在《Pooled Knockin Targeting for Genome Engineering of Cellular Immunotherapies》這篇文章中，作者要在 PoKI-Seq 的單細胞層次回答「每顆細胞到底拿了 36 種構築裡的哪一個」，於是用 ShortRead matchPattern 演算法把 amplicon Read2 上的 knockin barcode 對回同一對 Read1 上的 cell barcode 與 UMI。這一步解決了 10x 標準轉錄組讀不到上游 knockin barcode 的瓶頸，把預處理後的細胞-基因矩陣加上每顆細胞的構築身份標籤，交給下一步 cluster enrichment 與 pseudo-bulk 差異表達分析使用。
