# NGS-based Indel 量測 (targeted deep sequencing)

1. 引用自哪篇 paper: rationally-engineered-cas9-nucleases
2. Outline (任務主線): 對每個 Cas9 變體 × sgRNA 的 on-target 與已知 off-target 位點，以 Illumina 深度定序定量 indel 率，作為 specificity / efficiency 評分依據。
3. Method:

為了給每個 Cas9 變體配上 sgRNA 一個 specificity / efficiency 分數，作者需要一支「能同時清點正確位置和已知剪錯位置上各被剪過多少次」的尺。流程是：先把 Cas9 變體 + sgRNA 質體用 Lipofectamine 2000 共轉染進 HEK293T/293FT 細胞，等大約 3 天讓 Cas9 充分剪斷 DNA、細胞用接合修補把斷口接回去並在斷口附近多塞或少掉幾個鹼基 (indel)，再用 QuickExtract (Epicentre) 把細胞煮成粗基因組 DNA。接著針對每個要量的位點（on-target 一個、Hsu et al. 2013 已經整理好的 EMX1(1)、VEGFA(1) 等已知 off-target 各一個）各設計一對「鎖定基因組 DNA 的引子 (locus-specific primer)」做 PCR，把那一小段放大成幾百萬份目標片段 (amplicon)。最後上 Illumina 次世代定序 (Illumina NGS) 一次讀幾百萬條短 DNA，每個位點要被讀到一萬條以上才夠，把帶有 indel 的 reads 除以總 reads 算出該位點的 indel%，這就是 Cas9 在該位點剪過幾刀的代理分數。樣本量在這裡是個挑戰：第一輪就要篩 31 個單點突變、之後再加 34 個組合突變，每個都要配 sgRNA、量 on/off-target 多個位點，後續驗證更擴到 24 條 sgRNA 跨 10 個基因座。為了一鍋處理，每個樣本都要先接上自己獨家的身分證 (sample barcode)，一起丟進 Illumina 讀完再按 barcode 拆回。

把幾百個樣本一鍋上機，必須先解決兩件事：每段 DNA 兩端要接上 Illumina 機器認得的 P5/P7 adapter、每個樣本要有獨家 barcode。若一輪 PCR 就把 locus-specific 序列、barcode、adapter 全寫進同一條引子，這條引子會長到 80 鹼基以上，又貴又容易合成失敗，每個樣本都要客製一整套，成本爆炸。所以作者改用兩段式 PCR (依 Hsu et al. 2013, Nat. Biotechnol. 31:827)：第一輪只用 locus-specific primer 把目標位點放大成 amplicon，但在引子 5′ 端先掛一個通用的短把手 (PCR handle，例如 `CCATCTCATCCCTGCGTGTCTCc…`)；第二輪換成通用引子去咬這個把手，把 Illumina P5/P7 adapter 和該樣本獨家的 sample barcode 一次接上。第二輪這支引子很巧妙——3′ 端是跟 PCR handle 完全互補的短序列、5′ 端直接是 adapter+barcode 序列，掛在外面不咬任何東西；PCR 延伸時 DNA 聚合酶會把整條引子當成新合成 DNA 鏈的一部分往下接，於是新合成的 DNA 兩端就帶上了 adapter+barcode。這就是「fusion PCR」把外加尾巴物理融合到既有產物上的機制，也是上百樣本能用幾條通用引子搞定的關鍵。

幾個關鍵時間點與選擇都不是隨便挑的。先看 harvest 時機：indel 是修補留下的，太早 Cas9 才剛開始剪、細胞還沒修完，indel 還沒累積；太晚則沒剪到的細胞也分裂得很多，訊號被稀釋。轉染後約 3 天是訊號峰值的折衷點。再看抽 DNA 方式：作者要處理上百個樣本，QuickExtract (Epicentre) 只是「熱裂解 + 變性蛋白酶」（24 孔 80 µL、96 孔 20 µL，65°C 15 min → 68°C 15 min → 98°C 10–15 min）就把細胞煮成粗 DNA 上清，雖然粗、但下一步 PCR 反正會放大目標位點，作為模板綽綽有餘，速度比傳統管柱純化快得多。整套兩段式 PCR 與 barcode 流程則沿用 Hsu et al. 2013 的 protocol，目的是讓 indel% 數值能直接和那篇文章整理好的 OT 清單對得上、跨論文比較才公平。最後 efficiency 驗證階段為什麼要鋪 24 條 sgRNA 跨 10 個基因座？因為只挑 EMX1(1)、VEGFA(1) 會被反問「會不會新版 Cas9 只是在這兩條 sgRNA 上剛好還行、其他 sgRNA 整體活性下降？」，所以作者用箱形圖把 24 條 sgRNA 的 on-target indel% 分布畫出來 (Fig. 3A,B)，配上用 anti-SpCas9 抗體做的 Western blot (Fig. 3C) 確認新版 Cas9 在細胞裡的蛋白量等於或高於 WT，再加上轉染 72 小時後的 CellTiter-Glo 存活測試 (Fig. S11)，把「會不會其實是表現量低」「會不會其實是把細胞毒死」這兩條替代解釋一起鎖死。

這套 NGS 流程有三個會直接讓結論翻車的失敗模式。第一是定序深度不夠。作者要量的 off-target indel% 可以低到 0.2% 以下；若某個 amplicon 只讀到 1,000 條 reads，0.2% 等於只有 2 條 reads 帶 indel，這已經被 Illumina 本身約 0.1–1% 的隨機讀錯洗掉，新版 Cas9 的 specificity 數字會被高估。所以每個位點都要讀到萬條以上。第二是跳過 Western blot。如果不用 anti-SpCas9 抗體比新版 Cas9 與 WT 的蛋白量，「indel% 下降」就會被替代解釋成「其實是新版 Cas9 表現量本來就低、東西少自然剪得少」，這正是前人「降低 Cas9 劑量」舊招的後遺症；Fig. 3C 把這條退路堵死。第三是 sample barcode 設計不夠獨家。Illumina 讀 barcode 也有約 1% 機率讀錯一鹼基，若兩個樣本 barcode 只差一鹼基，就有 1% 機率把 A 樣本的 reads 分到 B 樣本去。對只有 0.2% indel 的 off-target 量測來說，這條污染足以把新版 Cas9 與 WT 的差異洗平、跨樣本看起來都差不多。所以作者沿用 Hsu 2013 的 barcode 設計（互相至少差 2–3 鹼基）就是為了堵住這條失敗鏈。

4. 工具與材料:

   - **Illumina NGS (next-generation sequencing)**: 次世代定序機，一次平行讀幾百萬到幾億條短 DNA（每條約 150 鹼基），是本研究量化 indel% 的核心讀數來源。
   - **amplicon**: 用一對引子在 PCR 中針對特定基因組位點放大出來的目標 DNA 片段，每個 on/off-target 位點各做一個 amplicon。
   - **locus-specific primer**: 第一輪 PCR 用的、序列鎖定基因組目標位點的引子（Table S2 列出全套），5′ 端額外掛了通用 PCR handle。
   - **PCR handle**: 掛在第一輪 primer 5′ 端的通用短序列（例如 `CCATCTCATCCCTGCGTGTCTCc…`），讓第二輪通用引子有共同咬合點。
   - **two-step / fusion PCR**: 依 Hsu et al. 2013 (Nat. Biotechnol. 31:827) 的兩段式 PCR：第一輪做 locus-specific 擴增 + 通用 handle，第二輪用 fusion 引子把 Illumina adapter 與 sample barcode 接上。
   - **Illumina P5 / P7 adapter**: Illumina 定序機認得的兩端通用尾巴序列，每段要上機的 DNA 必須先帶上才能黏上晶片開讀。
   - **sample barcode**: 每個樣本獨家的短 DNA 身分證，讓上百個樣本一鍋上機，事後按 barcode 拆回每個樣本的 reads；獨家性靠互相至少差 2–3 鹼基確保。
   - **indel**: 細胞用接合修補修 Cas9 切口時多塞或少掉幾個鹼基的小傷痕 (insertion / deletion)；本研究以「該位點 reads 帶 indel 的比率」作為 Cas9 在該位點剪過幾刀的代理分數。
   - **QuickExtract DNA extraction kit (Epicentre)**: 熱裂解 + 變性蛋白酶的快速粗 DNA 抽取試劑（24 孔 80 µL、96 孔 20 µL，65°C/68°C/98°C 各 10–15 min），上百樣本可平行處理。
   - **Western blot 蛋白表現量校正**: 用 anti-SpCas9 抗體比 WT、K855A、eSpCas9(1.0)、eSpCas9(1.1) 在細胞裡的 Cas9 蛋白量 (Fig. 3C)，排除「specificity 提升只是因為表現量下降」。
   - **anti-SpCas9 antibody**: 辨識 SpCas9 蛋白的特異抗體，是 Western blot 校正的關鍵試劑。
   - **CellTiter-Glo (Promega)**: 量轉染 72 小時後活細胞 ATP 螢光的存活測試 (Fig. S11)，排除「indel% 下降是因為細胞死光」這條替代解釋。

5. 與此篇文章的關係:

這篇論文的核心宣稱是 eSpCas9(1.0)/(1.1) 在 off-target 位點 indel 從幾個百分點被壓到偵測不到、同時 on-target 切割不變，因此整個證據鏈最需要的就是一支「能同時清點 on-target 與已知 off-target 各被剪過幾刀」的高解析度尺，這正是本 module 用 Illumina targeted deep sequencing 量 indel% 的角色。深度定序的好處是解析度可下探 0.01–0.1%，遠優於 T7E1/Surveyor 約 1–2% 的下限，足以把 WT 在 EMX1(1)/VEGFA(1) OT 的幾個百分點和變體的「測不到」清楚分開；搭配 Hsu 2013 的兩段式 fusion PCR 與 sample barcode，可把 31 個單點突變、34 個組合突變、跨 10 個基因座的 24 條 sgRNA 一鍋上機平行量化，否則篩選根本跑不完。它在 method 鏈中銜接的位置是：上游接 §2-B Golden Gate 做出的點突變質體庫與 §2-C 在 HEK293T/293FT 的 Cas9+sgRNA 共轉染樣本，下游把 indel% 餵給 §3-A 的 specificity / efficiency 評分以選出三條贏家變體 (K855A、eSpCas9(1.0)、eSpCas9(1.1))，並為 §2-E 的 BLESS 全基因組 DSB 候選位點提供 targeted 驗證 (Fig. 5C,D、Table S3)。同時它與 Fig. 3C 的 anti-SpCas9 Western blot 與 Fig. S11 的 CellTiter-Glo 並聯，把「specificity 提升其實是表現量下降或細胞被毒死」這條替代解釋一起鎖死，讓 indel% 的下降可以被解讀為酵素本身變得更挑剔，而非單純訊號被稀釋。
