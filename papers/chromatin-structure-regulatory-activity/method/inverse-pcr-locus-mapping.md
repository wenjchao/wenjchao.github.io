# Inverse PCR-based landing pad 位點定位

1. 引用自哪篇 paper: chromatin-structure-regulatory-activity
2. Outline (任務主線): Inverse PCR-based landing pad 位點定位
3. Method: 
   Inverse PCR 的任務是把每個 gBC 對應到精確的人類基因組座標，巧思在於「先把整片區域剪成小段，再強迫每段自己彎成一圈」，這樣已知 cassette 序列與未知鄰居序列就被綁在同一圈上，從 cassette 內部向外設計的引子就能把鄰居擴出來。具體流程：從每株純系細胞拿 2 µg 基因體 DNA，用 Csp6I 這把限制酶（認 `G^TAC`，4-bp 識別位點理論每 256 bp 切一次）剪碎成幾百 bp 的小段。接著把切完的 DNA 大幅稀釋到 400 µl 並在 4°C 反應 16 小時做自我環化 (intramolecular self-ligation)——濃度低、溫度低，DNA 兩端遇到自己尾巴的機率遠勝於遇到別段，於是強迫每段自己接成一圈。用兩條向外設計的引子 LP01 / LP02 從 cassette 內部「背對背向外指」，沿著環互繞一圈在鄰居序列那邊匯合，擴出來的產物就含 cassette 邊緣的 gBC 加鄰居序列。PCR 產物上 Illumina MiSeq 定序，bioinformatics 把讀到的序列對齊到 hg19 人類參考基因組，每個 gBC 就有了精確座標。

   兩個小設計值得一提：(1) LP01 / LP02 引子尾巴除了配對序列外還加上 AscI 與 SphI 兩種罕見限制酶的切位——這跟 inverse PCR 本身擴增無關，是預留給後續接 Illumina adapter 用。PCR 完用這兩種酶切出黏端，adapter 就能以唯一方向接上去。(2) 整套 protocol 改自 Akhtar et al. 2013 Cell 的 TRIP 方法與 Wang et al. 2012 Genetics 的 'Calling cards'。這兩個方法都用「切—環—向外擴」把整合位點掃出來；本論文沿用核心框架但把後端從 Sanger 升級成 Illumina MiSeq 高通量定序，並挑 Csp6I 做切刀。

   為什麼把 reads 對齊到 hg19 而不是更新版的 GRCh38？因為作者後面要把 gBC 座標套到 ENCODE 公布的 K562 染色質地圖（ChromHMM 強增強子/弱增強子/抑制區註釋），而那整套地圖當時是建在 hg19 上。直接用 hg19 對齊，gBC 座標可以一對一套上 ENCODE 註釋；換成 GRCh38 反而要先做座標換算引入誤差。

   兩個步驟若省掉，整個定位會壞在哪？(1) 如果不稀釋直接在 50 µl 體積下 ligation，DNA 濃度太高、每段 DNA 兩端更容易遇到別段而不是自己尾巴，接出來的不是一個個小環而是好幾段串成的長條 (concatemer)。Inverse PCR 引子向外擴的邏輯只在自我環化時成立，遇到 concatemer 要嘛擴不出來、要嘛擴出 chimeric reads，把不相干的鄰居硬接在一起，gBC 對應到的座標全錯。(2) 如果只信 inverse PCR + MiSeq 結果而不做驗證 PCR，中間任何一步引入的 chimera 都可能被誤認為真實整合位點。作者再用一條 cassette 內部引子加一條位置特異引子做獨立確認——擴得出產物才算數，否則 inverse PCR 的「位點」可能只是 PCR 拼接假象，後續的染色質環境歸因就會錯。
4. 工具與材料: 
   - **Inverse PCR**: 「切—環—向外擴」的反向定位法 (protocol 改自 Akhtar et al. 2013 Cell 與 Wang et al. 2012 Genetics)，把已知 cassette 旁的未知鄰居序列擴增出來。
   - **Csp6I**: 認 `G^TAC` 4-bp 序列的限制酶 (Thermo Fisher)，理論每約 256 bp 切一次，讓鄰居片段落在 PCR 可擴增的長度範圍。
   - **Intramolecular self-ligation**: 在大體積 (400 µl)、低溫 (4°C, 16 h) 下用 T4 ligase 強迫每段 DNA 自我環化，避免分子間串接成 concatemer。
   - **LP01 / LP02 primers**: 兩條從 cassette 內部背對背向外指的引子；尾巴各帶 AscI / SphI 切位以利後續接 Illumina adapter。
   - **Illumina MiSeq**: 10 nM library loading 的桌上型高通量定序儀，讀出 inverse PCR 產物的 gBC + 鄰居序列。
   - **hg19 reference genome**: ENCODE Tier 1 K562 染色質註釋當時所建的人類參考基因組版本；對齊到 hg19 讓 gBC 座標可一對一套上 ENCODE 註釋。
   - **Verification PCR**: Cassette 內部 primer + 位置特異 primer 的獨立確認 PCR，排除 inverse PCR / chimera 偽陽性。
5. 與此篇文章的關係: 
   在《A massively parallel reporter assay dissects the influence of chromatin structure on cis-regulatory activity》這篇文章中，作者要解讀染色質環境如何影響 CRS，前提是知道每個 landing pad 落在染色體哪裡。Inverse PCR 把每株純系細胞的 gBC 對應到 hg19 座標，解決了「barcode 知道、位置不知道」的瓶頸；產出座標清單後，下一步才能套上 ENCODE 染色質地圖、把每個位點分類成強增強子、抑制區等環境。
