# Indel quantification 與 specificity ratio scoring

1. 引用自哪篇 paper: rationally-engineered-cas9-nucleases
2. Outline (任務主線): 從 amplicon NGS reads 算出每個 (Cas9 variant × sgRNA × locus) 的 indel 比率，並據此排序 31 個單點與 34 個組合突變的 specificity / on-target trade-off。
3. Method:

這個子項的核心是把『Cas9 在某個位置剪了多少次』翻譯成可比較的數字。作者把每個基因座那一小段 DNA 用 PCR 擴增、上機定序，每條讀回來的 read 都跟原版序列比對；如果在 Cas9 預期下刀的位置多了或少了幾個鹼基，就算留下了一道小傷口 (indel)。indel 來自細胞自己的修補系統 (NHEJ 非同源端連接)——它焊接斷口時常多塞或漏掉幾個字母、留下永久痕跡。最後用『有傷口的 reads ÷ 全部 reads』算出該組合 (這個 Cas9 變體 × 這條 sgRNA × 這個基因座) 的小傷口比率 (indel%)，作為 Cas9 在該位置切割活性的代用值。改造 Cas9 想同時做到兩件事——該剪的剪、不該剪的別剪——所以作者把每個變體的成績單拆成兩軸：『目標位點』(on-target indel%) 衡量幹活能力，『已知會剪錯的位置』(off-target indel%) 衡量挑剔程度，兩軸都拿好成績才算贏家。

有了這張雙軸成績單，作者再用兩個指標把 31 個單點與 34 個組合突變排成名次。第一個指標叫剪錯倍率降低量 (off-target fold reduction)：原版 Cas9 在某個剪錯位置 (OT site) 的 indel% 除以該突變版在同位置的 indel%。第二個指標是該剪的位置 indel% 有沒有跟原版一樣高。Fig. 2A 的單點篩選門檻是『在 EMX1(1) 的三個剪錯位置全部降到原版的 1/10 以下 (≥10× fold reduction)，且 on-target 不掉』，31 個變體中 5 個達標；另外 6 個降幅在 2–5× 之間，列為次階。但即使是前 5 名，剪錯位置仍殘留約 0.5% 的 indel%，沒歸零，所以單點還不夠。作者把這 5 名兩兩、三三疊在同一支 Cas9 上，跑 34 種組合 (Fig. 2C)，把入選門檻提高到『EMX1(1) OT1、VEGFA(1) OT1、VEGFA(1) OT2 三個剪錯位置都低到 NGS 偵測不到』，8 種組合達標。最終留下兩支三點組合：eSpCas9(1.0) = K810A/K1003A/R1060A、eSpCas9(1.1) = K848A/K1003A/R1060A——共享 K1003A/R1060A 兩個核心位置，只在第三點交換；單點代表 K855A 也一併保留，三條贏家進入後續驗證。

為什麼還要把入選的 14 個突變版拿 24 條 sgRNA × 10 個基因座做更大規模的 on-target 量測 (Fig. 3A)？因為篩選階段只用 EMX1(1) 和 VEGFA(1) 兩條導引，會踩到兩個陷阱：一是只看剪錯倍率降低量會把『真的變挑剔』和『整體活性下降』混為一談，後者一樣會讓剪錯位置 indel% 跌 10 倍，但代價是該剪的位置也不剪；二是某個突變可能剛好不影響這兩條 sgRNA 跟 Cas9 表面的接觸，但碰到序列特殊的其他 sgRNA 就鈍化。作者把每個變體在 24 條 sgRNA 上的 on-target indel% 全部除以原版分數做標準化，再畫成盒鬚圖 (normalized box-and-whisker plot, Fig. 3B)——盒鬚的中位數與分散程度跟原版幾乎重疊，代表 K855A、eSpCas9(1.0)、eSpCas9(1.1) 在跨 sgRNA 場景下都沒變鈍。Fig. 3C 的 Western blot 再確認三條變體蛋白量與原版相當或更多，排除『其實是表現量降低才看起來更挑剔』的解釋。

為了直接看 Cas9 的辨識嚴格度有沒有提升，作者再做一輪錯配掃描。他們拿 VEGFA(1) 這條導引序列當實驗對象，沿著 PAM (Cas9 必須先認出的識別碼) 往遠端數，在第 1 到第 20 個位置每處故意造一個錯字 (single-base mismatch scan)，做出 20 條只差一個字的導引；另外再做一輪『連續兩個位置同時造錯字』(consecutive double-base mismatch scan)。每條錯字導引都拿原版、K855A、eSpCas9(1.0)、eSpCas9(1.1) 各剪一遍量 indel%，然後排成熱圖 (Fig. 4B, C)：橫軸是錯字位置、縱軸是 Cas9 變體、顏色代表剪了多少。原版 Cas9 對 PAM 旁前 7–12 nt 種子區的錯字很敏感、但對 PAM 遠端的錯字相對寬鬆，差一兩個字照剪。改造版則連 PAM 遠端的單一錯字都讓它剪不動了，等於把『嚴格比對』從種子區一路延伸到整條 sgRNA——換句話說，原版只在意導引前段、改造版整條導引每個字都會挑剔。

最後作者把 eSpCas9 跟前人最常用的特異化招數正面比一場。在這篇論文發表前，提升 Cas9 特異性的主流方法是把導引序列剪短到 17 或 18 nt 的截短導引 (truncated sgRNA, Fu et al.)。作者把 K855A、eSpCas9(1.0)、eSpCas9(1.1) 與『原版 + 截短 sgRNA』放在同一張 indel% heatmap 上 (Fig. S6)，掃過三條 sgRNA、共 24 個已知剪錯位置，並用統一門檻『indel% < 0.2%』算每組消掉多少個剪錯位置。結果 eSpCas9(1.1) 把 22 個壓到 0.2% 以下，原版+截短 sgRNA 只壓掉 14 個，且在 5 個位置反而剪得更兇——這是『漏剪一個 OT、開了另一個 OT』的偷渡現象。作者另外試把截短 sgRNA 疊到 nt-groove 突變上 (Fig. S12) 看能否再上層樓，結果 EMX1(1) 用 18 nt 截短時突變還勉強能切；VEGFA(1) 用 17 nt 截短時，每個突變的 on-target 都崩盤——意思是 eSpCas9 已把 Cas9 的辨識嚴格度推到極限，再疊截短就連對的位置都剪不動，這條結構改造路線跟舊招無法互相加成。

4. 工具與材料:

   - **indel%**: 把該位置 amplicon 定序的『有 insertion/deletion 的 reads ÷ 全部 reads』，作為 Cas9 在該位置切割活性的代用值。
   - **NHEJ (非同源端連接)**: 細胞修補雙鏈斷裂的主要系統；焊接時常多塞或漏掉幾個鹼基，留下永久痕跡，是 indel 訊號的來源。
   - **off-target fold reduction**: 原版 Cas9 在某 OT site 的 indel% ÷ 突變版在同 OT site 的 indel%；前 5 名單點要求 ≥10×，次階為 2–5×。
   - **on-target indel%**: Cas9 在預期目標位點留下的小傷口比率，作為『該剪的剪不剪』的衡量軸。
   - **off-target indel%**: Cas9 在已知會剪錯位置 (OT site) 留下的小傷口比率，作為『不該剪的剪不剪』的衡量軸。
   - **K855A**: 31 個單點 alanine 突變中入選的代表，作為單點贏家進入後續 24 sgRNA × 10 loci 與 BLESS 驗證。
   - **eSpCas9(1.0)**: 三點組合突變 K810A/K1003A/R1060A；在 EMX1(1) OT1、VEGFA(1) OT1、VEGFA(1) OT2 上 indel% 已降到偵測下限。
   - **eSpCas9(1.1)**: 三點組合突變 K848A/K1003A/R1060A；在跨 sgRNA on-target 上略勝 1.0 版，作為全基因組驗證的主力。
   - **24 sgRNA × 10 loci normalized box-and-whisker plot**: Fig. 3A,B 的驗證矩陣：14 個入選突變在 24 條 sgRNA、10 個基因座上的 on-target indel% 除以原版做標準化、畫盒鬚圖，篩出跨 sgRNA 都不變鈍的變體。
   - **single-base mismatch scan**: 對 VEGFA(1) 在 PAM 距離 1–20 nt 每個位置造一個錯字，量每個 Cas9 變體 indel%，呈現於 Fig. 4B 熱圖。
   - **consecutive double-base mismatch scan**: 對 VEGFA(1) 連續兩個位置同時造錯字，量每個 Cas9 變體 indel%，呈現於 Fig. 4C。
   - **PAM-proximal seed (7–12 nt)**: 原版 Cas9 對 PAM 旁前 7–12 nt 的錯字最敏感；eSpCas9 把嚴格度延伸到 PAM 遠端整條導引。
   - **truncated sgRNA**: Fu et al. 提出的特異化舊招，把導引序列剪短到 17 或 18 nt；本論文 Fig. S6 對照下消掉 14/24 OT、但在 5 處反而升高。
   - **Fig. S6 22/24 vs 14/24 比較**: 用 indel% < 0.2% 為門檻，eSpCas9(1.1)+完整 20 nt 導引消掉 22/24 OT、原版+截短 sgRNA 只消掉 14/24，且新增 5 處剪錯。
   - **Fig. S12 互斥性測試**: 把截短 sgRNA 疊到 nt-groove 突變上：EMX1(1) 18 nt 還能切，VEGFA(1) 17 nt 連 on-target 都崩盤，顯示兩條路線無法加成。

5. 與此篇文章的關係:

這篇論文要從 31 個 nt-groove 正電殘基的 alanine 單點與 34 個組合突變中，挑出「真的變挑剔、又不會變鈍」的 Cas9 改造版，因此必須有一套能同時量化 on-target 與 off-target 切割活性、且可平行跑數十個變體的客觀分數，這個 indel quantification 與 specificity ratio scoring 模組就是整篇篩選的計分板。它的好處是把 amplicon NGS reads 直接換算成 indel%，再以「off-target 倍率下降」與「跨 24 sgRNA × 10 基因座的 on-target 保留度」兩條軸並列排名，能一次排除「其實是整體活性掉了才看似特異」與「只在少數 sgRNA 走運」兩種偽贏家，最終濃縮出 K855A、eSpCas9(1.0)、eSpCas9(1.1) 三條贏家變體。它銜接在結構引導的 nt-groove 殘基定位與 Golden Gate 突變庫建構之後，吃進 HEK293 共轉染產出的 amplicon 深度定序資料，輸出進入 mismatch scan 熱圖 (Fig. 4) 與 truncated sgRNA 舊招對照 (Fig. S6)，並把最終勝出的 K855A 與 eSpCas9(1.1) 交棒給 BLESS 全基因組 DSB profiling 做不偏驗證，是整條「結構假說 → 高通量點突變 → 雙層 specificity 讀出」pipeline 的中樞篩選層。
