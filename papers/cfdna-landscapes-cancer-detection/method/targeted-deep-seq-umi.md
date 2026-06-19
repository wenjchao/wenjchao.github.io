---
subitem_id: "2-B"
title: "Targeted 深度定序與錯誤校正定序 (Hybrid-capture / Amplicon + UMI consensus)"
---

# Targeted 深度定序與錯誤校正定序 (Hybrid-capture / Amplicon + UMI consensus)

**Subitem:** 2-B · **Slug:** `targeted-deep-seq-umi`

## 主線
把有限的 cfDNA reads 集中砸在已知癌症驅動基因 panel 上，並以分子條碼 + 生資 filter 把 NGS 錯誤率壓到單分子準位，使 panel 內的單一體細胞突變可被當作 ctDNA 證據。

## 技術解析
「把有限 reads 集中砸在 panel 上」有兩條路。第一條叫雜交捕捉 (hybrid capture)：在試管裡放滿人工合成的短 DNA 探針 (oligonucleotide probes)，序列對應癌症基因，cfDNA 流過時跟探針配對黏住，磁珠把這群「被釣到的」碎片拉下來定序，其他不相關碎片就洗掉。第二條叫擴增子定序 (amplicon)：設計一對 PCR 引子貼在想看區段兩端，PCR 把這段拷貝幾百萬倍。前者範圍可大 (~80 kb–17 Mb)、後者方便做小 panel。不管哪條路，產物都讀到 30,000× 深度——也就是每個鹼基平均被讀 30,000 次。為什麼要這麼多？因為早癌血裡 ctDNA 比例可能 <0.1%，1,000 條 reads 裡最多 1 條來自癌細胞；要讀夠多次才能看到那 30 條突變 read 並估算 ctDNA 比例。實際平台各有取捨：TEC-Seq (Phallen et al., ref 37) 用 hybrid capture 抓 58 個癌症基因 (panel 80.93 kb)、~30,000× 深度，是最經典的「panel + UMI」早癌偵測典範；Lung-CLiP (ref 39) 把 panel 擴到 266 基因 / 355 kb，再用機器學習區分 ctDNA mutation 與背景；CancerSEEK (ref 78) 走 amplicon 路線，61 段 PCR 同時掃 8 癌共通驅動基因，再合併 8 種血清蛋白；RealSeqS / A-PLUS (refs 157, 158) 比較特殊，用 PCR 擴增全基因組 ~350,000 個 Alu 重複元件，靠這些 reads 的分布推算染色體層級的數量異常 (aneuploidy)。

光靠深度讀還不夠，因為 NGS 每讀一個鹼基大約有 1/1000 (10⁻³) 機率讀錯，比早期 ctDNA 真實突變比例還高。錯誤校正分三層接力。第一層是單分子條碼 (UMI)：建庫時在每條 cfDNA 兩端接上 8 個隨機鹼基 ($4^8 = 65{,}536$ 種)，等於每條原始分子蓋一枚獨一無二的編號章；PCR 放大後，UMI 相同的 reads 代表「同一條原始分子的拷貝群」。第二層是多 read 共識序列 (consensus sequence)：演算法在群內每個位置做多數決，把 PCR 或定序機隨機犯的錯砍掉。第三層是生資 filter (bioinformatic filter)：扣掉系統性錯誤——某些三鹼基 context 容易被 polymerase 讀錯、低複雜度區擾流、雙股訊號不一致 (strand bias)。三層疊起來把錯誤率從 10⁻³ 壓到 <10⁻⁷ (ref 41)，這時 ctDNA 的單一突變才會比背景雜訊高，可以被視為真實證據。

為什麼 panel 內容挑的是「癌症驅動基因」？篩檢場景下你不知道這個人會得哪種癌、會壞在哪個基因，但跨病人跨癌種反覆出現的驅動基因就那幾十個 (TP53、KRAS、EGFR、PIK3CA…)。把 panel 砸在這些基因上等於用先驗知識提高在 <1% 基因組 footprint 內撞到突變的命中率；換成隨機 80 kb panel，多數讀到的是不會突變的安靜區，30,000× 深度全部浪費。Review 也明說這個取捨直接造成 targeted 法的天花板——panel 外的 ctDNA 訊號通通漏掉。

更麻煩的失敗模式是：UMI 已把技術錯誤壓到 <10⁻⁷，但仍然抓不準 ctDNA，因為血液裡本來就有非癌症的真實突變。隨年齡增長，骨髓裡某些白血球前驅細胞會自發累積突變 (常見落在 DNMT3A、TET2、ASXL1)，這群細胞擴增成一個 clone，學名 clonal haematopoiesis of indeterminate potential (CHIP，可譯「白血球無辜突變」)；當這群白血球死亡時，帶突變的 DNA 也被丟進血漿，跟 ctDNA 完全混在一起。UMI/consensus 會把它們當真實突變、分類器當成癌症證據——這是 targeted 法最大的假陽性來源。解法是平行抽病人的白血球做 WGS，把白血球自帶的突變從 plasma 訊號裡扣掉。除了 CHIP，panel 內還有 germline 變異、定序儀廠牌特有的系統性誤判、低 VAF 雜訊；Lung-CLiP 因此再串一層機器學習：除了「這個位置有沒有突變」，還看「帶這個突變的 cfDNA 碎片有多長、被切在哪、末端 motif 長什麼樣」——ctDNA 碎片普遍偏短，CHIP 碎片接近健康 cfDNA 長度分布，把這些 fragment-level 特徵餵給分類器，可以在 panel 結果上面再過濾出真正的腫瘤訊號。

## 工具與材料清單 (Toolchain)
- **hybrid capture**：用人工 DNA 探針把想看的癌症基因區從 cfDNA 池子裡釣下來，搭配磁珠純化。
- **amplicon sequencing**：用 PCR 引子直接擴增 panel 內的目標序列，產物送定序。
- **sequencing depth 30,000×**：每個鹼基平均被讀 30,000 次；早癌 ctDNA <0.1% 時，足以撞到 30 條突變 read。
- **unique molecular identifier (UMI)**：建庫時接在每條原始 cfDNA 兩端的隨機鹼基條碼，用來把 PCR 拷貝群圈在一起。
- **consensus sequence**：對 UMI 相同的拷貝群做多數決，產出代表原始分子的單條序列；扣掉隨機 PCR/定序錯誤。
- **bioinformatic filter**：在 UMI/共識之後再扣掉系統性錯誤 (三鹼基 context、低複雜度區、strand bias)。
- **TEC-Seq**：58 基因 hybrid capture panel (80.93 kb)、30,000× 深度，早癌偵測典範 (Phallen et al., ref 37)。
- **Lung-CLiP**：266 基因 / 355 kb hybrid capture + 機器學習，用 fragment-level 特徵區分 ctDNA mutation 與 CHIP 背景 (ref 39)。
- **CancerSEEK**：61-amplicon PCR panel + 8 種血清蛋白 immunoassay，多癌共通驅動基因 (ref 78)。
- **RealSeqS / A-PLUS**：PCR 擴增 ~350,000 個 Alu 重複元件，靠 reads 分布推算染色體層級的 aneuploidy (refs 157, 158)。
- **clonal haematopoiesis of indeterminate potential (CHIP)**：年齡相關的白血球無辜突變，會釋出帶突變的 cfDNA 混進 plasma，targeted 法最大的假陽性來源。
- **matched buffy coat WGS**：平行對病人白血球做全基因組定序，用來扣掉 CHIP 與 germline 變異。

## 與此篇文章的關係
在《Genomic and fragmentomic landscapes of cell-free DNA for early cancer detection》這篇 Review 中，作者把 targeted 深度定序 + UMI consensus (代表平台 TEC-Seq、Lung-CLiP、CancerSEEK) 列為早癌液態切片的「舊路代表」：它吃進 cfDNA 與 panel 內基因列表，產出單一體細胞突變作為 ctDNA 證據。這條路解決了 NGS 錯誤率 10⁻³ 把單分子訊號淹沒的瓶頸，把 panel 內錯誤壓到 <10⁻⁷，但也因為只能覆蓋 <1% 基因組與 CHIP 干擾，敏感度在第一期癌仍偏低。Review 用它當對照，襯托後面 sWGS + fragmentomic 路線為什麼必要。

## 已沿用 Baseline 詞彙
ctDNA, cfDNA, PCR, NGS, WGS, panel, machine learning, Lung-CLiP, CancerSEEK
