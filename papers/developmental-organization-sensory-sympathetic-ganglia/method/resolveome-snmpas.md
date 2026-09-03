# ResolveOME 單核共擴增與 snMPAS/snRNA-seq

1. 引用自哪篇 paper: developmental-organization-sensory-sympathetic-ganglia
2. Outline (任務主線): ResolveOME 單核共擴增與 snMPAS/snRNA-seq
3. Method:

Bulk MPAS 是把整顆神經節裡上千顆細胞混成一鍋 DNA 定序，AF 只能告訴你「這個 MV 在整顆神經節裡佔多少比例」，無法知道那個 MV 是屬於神經元 (neuron)、還是神經膠細胞 (glia)、也無法知道具體是哪顆細胞。作者要證明 clonal split 不是 bulk 混雜產生的 artifact，就必須把 MV 和細胞型別都定位到單一顆核。為什麼是「單核 (nucleus)」而不是「單細胞 (cell)」？冷凍過的死後神經節，細胞質裡的 mRNA 早就被酵素咬掉，但核膜還完整、核內的 pre-mRNA 與基因組 DNA 都保留得較好；加上神經元胞體橫跨百微米、軸突細長，硬打成單細胞會撕爛。作者用 BD Influx FACS 搭配 DAPI 染核（一種只跟雙股 DNA 結合才強烈發藍光的染料），把單顆細胞核逐個分揀到 96 孔盤，每孔一顆；ID07 的左側 T2-DRG、T2-SG、T3-DRG、T3-SG 各取 224 顆核。

接下來要在同一顆核裡同時抓 DNA 與 mRNA，關鍵是一條帶生物素的 poly-T 引子 (Biotin-dT primer)。反轉錄時，這條 primer 的 poly-T 尾巴與 mRNA 的 polyA 尾巴互補配對，做出反轉錄的第一股 cDNA；primer 頭上的生物素分子等於在每條 mRNA-derived cDNA 上貼了一張磁鐵貼紙。反應完成後倒入抗生物素磁珠 (streptavidin beads)——biotin 與 streptavidin 的結合力是自然界最強的非共價鍵之一 ($K_d \approx 10^{-15}\,\mathrm{M}$)，磁珠幾乎能 100% 把 mRNA-cDNA 拉出來，而沒有 biotin 的基因組 DNA 則一顆磁珠都黏不上。兩者於是被乾淨地物理分離，各自進到後續流程。

被抽出的基因組 DNA 只有兩份（雙倍體），要上 sequencer 至少要複製到幾百 ng——這就是全基因體擴增 (WGA, whole-genome amplification)。ResolveOME 這一步用引物模板導向擴增 (PTA, primary template-directed amplification) 而不是傳統 PCR。PTA 的關鍵是幾種特殊修飾過的核苷酸 (exonuclease-resistant terminator)：polymerase 走到這種核苷酸時鏈就被卡住不能繼續延伸，且 terminator 本身抗 exonuclease、不會被酵素咬掉，讓每段 amplicon 都被限制在幾百 bp 內、無法接力指數放大。結果全基因體所有位置都以近似線性速率累積，覆蓋均勻性比 PCR 好許多倍。這對後續要用 snMPAS 抓 AF 精準值是必要條件——PCR 造成的位點間偏誤在單核 WGA 上會直接毀掉 genotype call。

224 顆核裡一定有些擴增失敗或高 dropout 的爛核。作者採兩段式上機：先把每顆核用便宜的 low-pass PE50 (~2 M reads) 掃一次做 QC，合格的核才進到正式深度定序 (NovaSeq X Plus 25B FC 上 DNA PE150、RNA PE100)，避免把定序資源花在爛核上。snMPAS 的品質可以用 het/hom 對照位點自估：拿已知雜合的位點重新 genotype、看有幾成被讀成純合，反推 dropout rate 約 19%——即每顆核約 1/5 位點資訊遺失；拿已知純合的位點看有幾成被誤讀成雜合，反推 false positive rate 約 5%。dropout 在建 phylogeny 時被當作「缺資料」而非「無此變異」處理；false positive 則靠「MV 需在多顆核重複出現」的規則抑制。這對後面用 MEGA11 建 minimum evolution tree、permutation test T3-DRG:T3-SG 配對頻率而言，兩個誤差都需要被明確量化。

4. 工具與材料:

- **BioSkryb ResolveOME**: 商業化的單核 DNA+RNA 共擴增工作流，同時輸出 snMPAS 與 snRNA-seq 資料。
- **Biotin-dT primer**: 頭上綁 biotin 的 poly-T 引子；反轉錄後把所有 mRNA-cDNA 標記上 biotin 供 streptavidin 磁珠拉出。
- **Streptavidin beads**: 抗 biotin 磁珠 ($K_d \approx 10^{-15}\,\mathrm{M}$)，特異性把 mRNA-cDNA 從基因組 DNA 中物理分離。
- **PTA (primary template-directed amplification)**: 以 exonuclease-resistant terminator 做線性擴增的 WGA 化學，比 PCR 覆蓋均勻，適合單核。
- **SPRI beads**: Beckman Coulter B23319 磁珠，做尺寸選擇與純化以移除引子、殘餘試劑。
- **NEXTFLEX Unique Dual Index**: PerkinElmer NOVA-534100 條碼，讓多顆核 library 可混上機並各自區分。
- **Low-pass PE50 QC**: 以 ~2 M reads 淺度上機挑合格核，再送深度定序，避免爛核浪費預算。
- **snMPAS**: 在單核 WGA 產物上做 MPAS 定序，量測每顆核的 MV genotype。
- **BD Influx FACS + DAPI**: 以 DAPI 染色雙股 DNA 後用高精度 FACS 把單顆核分揀到 96 孔盤。
- **Dropout rate ~19%**: 用已知雜合位點被誤判為純合的比例估出的位點遺失率；phylogeny 時當缺資料處理。
- **False positive rate ~5%**: 用已知純合位點被誤判為雜合的比例估出的偽陽性水平；靠多核重複規則抑制。

5. 與此篇文章的關係:

在《Developmental organization of sensory and sympathetic ganglia》這篇文章中，作者為了排除「bulk MPAS 訊號可能來自組織混雜」的替代解釋，採用了 BioSkryb ResolveOME 單核共擴增工作流。它解決了「同一顆核同時提供 MV genotype 與 cell-type 分型」的技術瓶頸，把 ID07 左側 T2-DRG、T2-SG、T3-DRG、T3-SG 各 224 顆單核轉成 snMPAS + snRNA-seq 雙軌資料，供下游 MEGA11 minimum evolution tree 與 terminal branch permutation test 使用。
