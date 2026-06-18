# Barcoded HDR Template 庫設計與大量製備

1. 引用自哪篇 paper: pooled-knockin-cellular-immunotherapy
2. Outline (任務主線): Barcoded HDR Template 庫設計與大量製備
3. Method: 
   作者要做的是 36 條給細胞用的「修補模板」(HDR template)：當 Cas9 把 T 細胞的 TRAC 基因座切開後，細胞會抓附近一段同樣序列的 DNA 把切口補回去。所以每條模板兩端各接一段與 TRAC 完全一樣的「導向標」(homology arm)，告訴細胞「請把我接在這裡」。中間則是一條「一個啟動子驅動多個蛋白」的串接構造 (polycistronic)：TCRβ → 拆解碼 (2A peptide) → 候選功能基因 (Insert X) → 拆解碼 → 帶 6 bp barcode 的 TCRα V 區。2A peptide 的原理是讓核糖體翻譯到尾巴某個位置時跳過一個鍵 (ribosomal skipping)，前段蛋白直接從核糖體掉出來、後段繼續被翻譯，同一條 mRNA 就能拆出三個獨立蛋白。barcode 直接嵌進 TCRα V 區本來就「可以隨意換鹼基都不影響蛋白功能」的彈性位置 (degenerate bases)，與功能 DNA 只隔 ~400 bp，一次 PCR 就能同時帶出兩段。產線分三段：先用 Benchling 設計，向 IDT 訂雙股 DNA 小片段 (gBlock)；再用 Gibson Assembly（一種把多段 DNA 一次拼成環狀質體的等溫反應，使用 NEB E2611L）把 gBlock 個別接進已有 NY-ESO-1 TCR 骨架的 pUC19；最後從質體用高保真 PCR 酵素 (Kapa HiFi HotStart) 大量擴增 amplicon，磁珠純化 (1.0× SPRI)、NanoDrop 量濃度、1% agarose 膠確認大小。
   整條模板還有一個關鍵小心機：作者把 3' 同源臂最末端的 ~10 bp 故意改成「與基因組對不上」的版本 (homology arm mismatch，取自 Paquet et al., 2016)。HDR 成功時這段會被基因組真實序列覆蓋；沒整合的自由模板則保留 mismatch 版本。下游 PCR 反向引子刻意設在 mismatch 外側的真實基因組區，只有真正整合進染色體的版本才同時擁有「插入物的條碼」與「外側基因組序列」兩個引子位點。沒這層設計的話，電穿孔送進去的模板大部分沒整合、只是飄在細胞質裡，數量遠多於真正縫進染色體的版本，PCR 訊號會被它們蓋過。barcode 用 6 bp 也是精算過的：$4^6 = 4096$ 種組合遠多於 36 個構築，撞號機率可忽略；同時短到能塞進 TCRα V 區的彈性位置而不破壞受體折疊。整段 amplicon 控制在 ~400 bp，剛好落在 Illumina 2×150 bp paired-end 短讀的覆蓋範圍，定序時直接讀完整段，barcode 與功能身分天然綁定。
4. 工具與材料: 
   - **HDR template**: 給細胞用來把 Cas9 切口縫回去的 DNA 模板；兩端與目標基因組同源，中間是想塞入的序列。
   - **TRAC locus**: T 細胞 TCRα 鏈所在的固定基因座，是這篇研究選定的統一插入點。
   - **Homology arm**: 模板兩端與基因組完全相同的序列，當作細胞抄寫時的對齊導向。
   - **Homology arm mismatch**: 在 3' 同源臂末端刻意改 ~10 bp 與基因組對不上，使 HDR 成功後該段被基因組真實序列覆蓋，作為下游選擇性 PCR 的指紋。
   - **Polycistronic**: 一條 mRNA 用拆解碼串連多個蛋白編碼區，使一個啟動子能同時驅動多個蛋白表現。
   - **2A peptide**: 讓核糖體翻譯到尾巴特定位置時跳過一個鍵 (ribosomal skipping) 的拆解碼，把同一條 mRNA 拆成多個獨立蛋白。
   - **6 bp barcode**: 嵌在 TCRα V 區彈性位置的 6 鹼基身分條碼，$4^6 = 4096$ 種組合遠多於 36 個構築。
   - **Degenerate bases**: TCRα VJ 接合區本來就可以隨意更換鹼基而不影響蛋白功能的位置，是 barcode 借住的空位。
   - **gBlock**: 廠商 (IDT) 化學合成的雙股 DNA 小片段，作為組裝原料。
   - **Gibson Assembly**: 把多段有同源末端的 DNA 在等溫下一次拼成環狀質體的反應；此處使用 NEB E2611L master mix。
   - **pUC19**: 常見細菌質體骨架，作者預先放入 NY-ESO-1 TCR 模組，作為每個 Insert X 的承載載體。
   - **Kapa HiFi HotStart**: 高保真 PCR 酵素，用於從質體大量擴增 HDR template amplicon。
   - **SPRI (1.0×)**: 用磁珠吸附 DNA 並去除短片段與酵素的純化法 (Beckman Coulter A63880)。
   - **Paquet et al., 2016**: homology arm mismatch 策略的原始引用，本研究借用其概念實現選擇性擴增。
5. 與此篇文章的關係: 
   在《Pooled Knockin Targeting for Genome Engineering of Cellular Immunotherapies》這篇文章中，作者為了一次比較 36 個候選外掛基因對 T 細胞的增益效果，需要先把每個候選做成可被 PCR 大量複製、又能在後續定序時與其他成員區分的 DNA 模板。本子項建立的「barcoded HDR template 庫」解決了「同一位點公平比較」與「選擇性讀出真正整合事件」兩個瓶頸，產出 36 條 polycistronic 模板交給下游 RNP 共電穿孔步驟 (2-C) 使用，並為 2-H 的 on-target barcode 擴增鋪好引子位點。
