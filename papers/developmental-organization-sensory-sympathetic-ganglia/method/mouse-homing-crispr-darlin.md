# Homing CRISPR 與 DARLIN 小鼠雙系譜條碼追蹤

1. 引用自哪篇 paper: developmental-organization-sensory-sympathetic-ganglia
2. Outline (任務主線): Homing CRISPR 與 DARLIN 小鼠雙系譜條碼追蹤
3. Method:

CRISPR barcoding 的核心邏輯是：細胞基因體上有一段人工設計的條碼陣列 (barcode locus)——通常是幾十個相似但不完全相同的靶點串在一起。Cas9 一旦啟動，會對這段陣列做多重切割，細胞用 NHEJ (非同源末端接合) 隨機修復，每個靶點被留下的 indel (小插入/缺失) 都不同；整段陣列組合起來的 indel pattern 就成為這顆細胞的「隨機身分證」，並因為編輯不可逆而被所有後代忠實繼承。Homing CRISPR 用的 MARC1 陣列還多一個巧思：把 gRNA 的靶序列直接編碼在 barcode 陣列本體上 (self-targeting)。當 Cas9 切了一個靶點、細胞用 NHEJ 修復後，這個靶點序列變了、Cas9 就切不到了，但陣列上還有很多同款靶點未被編輯，Cas9 會繼續一路切。每次細胞分裂 Cas9 都可能新增一筆 indel，barcode 複雜度隨時間累積，同一 lineage 早期和晚期產生的 indel 會疊加成長條紀錄——比一次性打 indel 的簡單設計能區分更多祖先關係。

作者要讓 Cas9 只在「即將脫層的 NC 細胞」啟動，靠的是三重雜交三個小鼠品系：(1) Sox10-Cre——Sox10 是 delaminating NC 特有的啟動子，Cre 是能剪掉 loxP 之間 DNA 的酵素；(2) ROSA26-LSL-Cas9-GFP——Cas9 前面被一段「loxP-Stop-loxP (LSL)」擋住不能表達，Cre 剪掉 Stop 後 Cas9 才被打開；(3) MARC1-PB7——Homing CRISPR 的條碼陣列。三者組合在同一隻小鼠上時，只有 Sox10 表達的 NC 細胞才會啟動 Cas9 開始編輯 MARC1，其他細胞維持乾淨。這個系統的弱點在於：Sox10 啟動子如果在其他組織細胞也短暫表達 (leakage)，Cas9 會在那些細胞也留 indel，之後解剖時被誤判為 NC 後代；反之若 Cre 啟動時大批 NC 早已 delaminate 完成，那 barcode 標記的是「delamination 之後」而非「之前」，時序整個對不上。

為了避免上一段那些單一系統偏誤，作者另外做一套 DARLIN 系統。DARLIN (Li et al. 2023) 用不同結構的 barcode 陣列，搭配「ObLiGaRe doxycycline-inducible Cas9 (ODInCas9)」——Cas9 平常關著，注射 doxycycline 才被打開，時機更精準。作者把懷孕母鼠在胚胎第 8.5 天 (E8.5, trunk NC 開始 delamination 的時點) 以 25 mg/g 體重劑量做 retro-orbital 眼窩後靜脈注射：口服 doxy 濃度上升慢、時窗會拖 24 h 以上；retro-orbital 一次把高劑量送進母體血液、幾小時到胚胎，時窗壓縮到幾小時。這對想標記「E8.5 delaminating NC」的實驗至關重要——早一天或晚一天標到的都是別的細胞群。E14.5 (6 天後) 解剖胚胎，把 sympathetic chain 與 DRG 的 rostral/caudal 半部分開、TRIzol 萃取 bulk RNA、targeted RT 讀 barcode。若兩套系統 (MARC1 與 DARLIN) 各自得到一致「同型態 clone 富集、跨型態幾乎缺席」的結論，就能大幅排除任一系統的偏誤。

barcode 的讀取用 targeted amplification + MiSeq。Cas9 編輯出來的 indel 都落在 barcode locus 這幾百 bp 的區域內，作者設計 primer 針對這段位點做 PCR 擴增，把 barcode locus 從整個基因體「拉」出來變成短片段，再上 Illumina MiSeq——MiSeq 通量低但讀長長、成本低，適合只讀一小段序列。每顆神經節的 barcode indel pattern 一被讀出，就能與其他神經節比對「共享哪些 indel」。分析流程沿用 Leeper et al. 2021 protocol、DARLIN 分析 code 見 GitHub (Human_DRG_SG/Analysis/Darline)。若某顆神經節 DNA 品質不佳、或 indel 剛好落在 primer 結合位讓 primer 貼不上導致 0 read，該樣本標為 missing 不進 phylogeny；作者每隻小鼠取數十顆 DRG/SG 留了緩衝，個別 dropout 不會毀掉整體結論。

4. 工具與材料:

- **Homing CRISPR (MARC1)**: 把 gRNA 靶序列編碼在 barcode 陣列本體，Cas9 可自我編輯累積 indel；MARC1-PB7 為本文使用品系 (MMRRC 0654240UCD)。
- **DARLIN**: 另一套獨立 CRISPR barcode 陣列 (Li et al. 2023)，搭配 dox-inducible Cas9 給精準時窗。
- **Sox10-Cre**: 以 Sox10 啟動子驅動 Cre 酵素，讓 Cas9 只在 delaminating NC 啟動 (JAX 025807)。
- **ROSA26-LSL-Cas9-GFP**: ROSA26 安全位插入 Cas9，前面用 loxP-Stop-loxP 擋住，Cre 剪 Stop 後 Cas9 才被打開 (JAX 026175)。
- **ObLiGaRe dox-inducible Cas9 (ODInCas9)**: 以 doxycycline 誘導 Cas9 表達的系統 (Lundin et al. 2020)，讓時窗精準到打針當下幾小時。
- **Retro-orbital injection**: 眼窩後靜脈注射，能把高劑量 doxy 快速送入母體血液再進胚胎，時窗壓到幾小時。
- **E8.5 (embryonic day 8.5)**: 小鼠 trunk NC 開始 delamination 的時點；DARLIN 誘導時機。
- **Targeted amplification + MiSeq**: 以 primer 專門擴增 barcode locus，再用低通量高讀長的 Illumina MiSeq 讀出 indel pattern。
- **NHEJ (non-homologous end joining)**: Cas9 切斷後細胞用 NHEJ 隨機加減 bp 修復，產生 indel barcode 的機制。
- **TRIzol RNA extraction**: 用 TRIzol 從 E14.5 胚胎組織萃取 bulk RNA，供 targeted RT + barcode 定序。

5. 與此篇文章的關係:

在《Developmental organization of sensory and sympathetic ganglia》這篇文章中，作者為了在小鼠上用可控時窗驗證「NC fate 早在 delamination 之前就已指派」的結論，採用了 Homing CRISPR MARC1 與 DARLIN 兩套獨立條碼系統。它解決了「單一 mouse line 可能有 Cre 滲漏或 barcode dropout 造成偏誤」的信度問題，把 E8.5 delaminating NC 上 Cas9 編輯的 indel pattern 讀出後對到 DRG/SG，供後續 phylogeny 交叉驗證與人類 MVBA 結果對照。
