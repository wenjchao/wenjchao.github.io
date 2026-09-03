# AmpliSeq MPAS 大量平行擴增子定序驗證與 AF 定量

1. 引用自哪篇 paper: developmental-organization-sensory-sympathetic-ganglia
2. Outline (任務主線): AmpliSeq MPAS 大量平行擴增子定序驗證與 AF 定量
3. Method:

作者採用『多重擴增子平行定序』(multiplex parallel amplicon sequencing, MPAS) 對 WGS 呼出的候選 MV 做超深度驗證。它跟 WGS 差在哪？WGS 是全基因組每個位置平均讀 30-300 次；MPAS 則是一整組預先設計好的 PCR 引子 (primer)——上千對，每一對只鎖定一個特定位置——同時上場把這幾千個位置各自放大幾百萬倍，其他位置完全不理，等於只讀這幾千個位置、但每個位置讀 ~10,000 次。這種超深度的關鍵是把 AF 的信賴區間收得非常窄：AF = 1% 在 300× 深度只拿到 3 支 alt reads，binomial 95% CI 約 $[0.2\%, 2.9\%]$；同樣 AF 在 10,000× 拿到 100 支，CI 收到 $[0.8\%, 1.2\%]$。作者要用不同神經節間的 AF 差異反推祖先族群大小，這種精準度是硬需求。Illumina AmpliSeq 演算法確保上千對 primers 熔解溫度 (Tm) 一致、每個 amplicon <175 bp、沒有 primer-dimer 衝突，才能在同一個 PCR 反應內 multiplex 而不打架。

作者的 panel 除了 candidate MV 之外，還特別摻入已知的雜合 (het) 與純合 (hom) 對照位點：ID06 是 2,546 mosaic + 212 het + 101 hom (amplicon pool 208852)、ID07 是 2,607 + 181 + 101 (208853)、ID08 是 1,893 + 143 + 91 (212497)。這些對照有三個校準用途：第一，het 位點 (gnomAD 上 AF 約 48-52%) 若 MPAS 讀出的 AF 明顯偏離 50%，就代表這一段 amplicon 的 PCR 或定序有系統性偏差；第二，hom 位點應該 100% alt，若讀出 3% ref reads，這 3% 就是背景污染加定序誤差的總量；第三，也是最重要的——把每位 donor 自己的 het/hom 分布收集起來當校準基準，替該 donor 量身訂做 5% FDR 門檻。作者實測的 hom lower-bound cutoff 是 ID06 = 0.0279、ID07 = 0.0455、ID08 = 0.0035，跨 donor 差了整整一個數量級；若套統一 cutoff，ID07 會全部漏過假陽性、ID08 會把真訊號一起濾掉，donor-specific 校準完全不能省。

上機工序如下。DNA 先稀釋到 5 ng/μl (用 AmpliSeq Library PLUS 384 rxn kit 附的 low Tris-EDTA)，接著跑 multiplex PCR 把上千個目標位點同時擴增；接下來的 FUPA (Functional un-primed primer amplification) 是把殘留 primer 與 primer-dimer 消化掉——這些殘料若留在 library 裡會嚴重佔 sequencing 資源。然後用 CD Indexes (Combinatorial Dual Indexes) 貼上兩段 8 bp 樣本條碼，讓下游 pooled sequencing 能辨識每支 read 屬於哪個 sample。每 plate 帶一個 unrelated control DNA，Qubit dsDNA HS 定量後上機。關鍵操作：ID06、ID07、ID08 三個 pool 各自佔一個 lane，實體分開。這是為了防止 index hopping——NovaSeq 這種 patterned flowcell 上，游離 index 會意外跳到別的 sample 的 read 上，比率可達 1-2%。如果三位 donor 混同一 lane，donor A 才有的 MV 會冒出來在 donor B 資料中被誤認為跨 donor shared clone (生物上不可能)；同一 donor 內部也會被污染。分 lane 一勞永逸切斷這條污染。

最終產出方面：ID06 FASTQ 209.2 GB、ID07 49.1 GB、ID08 143 GB (另加 ID07 snMPAS 150 GB)，達到目標 ~10,000×/variant。驗證率為 827/2,546 (32.5%) ID06、252/2,607 (9.7%) ID07、511/1,893 (27.0%) ID08 的 candidate MV 通過 MPAS。低於 100% 是正常的——WGS pipeline 呼出的 candidate 本來就有相當比例是 sequencer artifact 或 germline heterozygous 邊界值。反過來想，若 panel 裡跳過 het/hom 對照位點會有三條連鎖後果：無法為每位 donor 建立專屬 FDR (統一 cutoff 讓跨 donor 比較不公平)；無法察覺 amplicon-level bias；AF 差異的顯著性檢定失去校準基準——一個看起來 DRG 3% vs SG 1% 的差異，你不知道究竟是真的 clonal 分離還是這段 amplicon 剛好在 DRG 樣本裡過度擴增。整篇論文核心的 AF 比較都會失去可信度。

4. 工具與材料:

- **AmpliSeq Custom DNA Panels**: Illumina 官方 amplicon 設計服務 (document 1000000036408v07)，可訂做上千對 primers 針對指定位點做 multiplex PCR。
- **MPAS (Multiplex Parallel Amplicon Sequencing)**: 用 amplicon panel 把上千個位點同時放大並超深度定序 (~10,000×) 的方法，可精準量測 AF。
- **Amplicon panel**: 上千對預先設計的 PCR primers 集合，只鎖定指定位點、其他基因組完全忽略。
- **Heterozygous (het) control**: gnomAD 上 AF ~48-52% 的已知位點，用來校 amplicon 擴增偏差。
- **Homozygous (hom) control**: 應為 100% alt 的位點，用來估背景污染與定序誤差總量。
- **FUPA (Functional un-primed primer amplification)**: AmpliSeq 官方酶處理，把殘留 primer 與 primer-dimer 消化掉。
- **CD Indexes**: Combinatorial Dual Indexes，替每個 sample 貼兩段 8 bp 樣本條碼供 pooled sequencing。
- **Unrelated control DNA**: 每 plate 帶一份無血緣 DNA，用來監測跨樣本污染。
- **Qubit dsDNA HS**: 以螢光染料精準定量雙股 DNA 濃度的試劑組。
- **Index hopping**: pooled sequencing 中游離 index 誤跳到別 sample 的 read 上，NovaSeq 上可達 1-2%；本研究用『分 lane 上機』避免。
- **Donor-specific FDR cutoff**: 用該 donor 自己的 het/hom 分布量身訂做的 5% 假陽性率門檻，本研究實測 hom lower-bound = 0.0279 (ID06)、0.0455 (ID07)、0.0035 (ID08)。

5. 與此篇文章的關係:

在《Developmental organization of sensory and sympathetic ganglia》這篇文章中，作者為了確認 WGS 呼出的候選 mosaic variant 是真的、並精準量出它們在每顆神經節裡的 AF，採用了 Illumina AmpliSeq 的多重擴增子平行定序 (MPAS)。這一模塊解決了『WGS 深度不夠算不出 AF 差異、也分不清 sequencer artifact』的兩個瓶頸，把每個候選位點打到 ~10,000× 並收 binomial 95% CI 到 ±0.2%，最終產出 ID06 827、ID07 252、ID08 511 個通過驗證的 mosaic variant，直接餵給下游的 geoclone 空間映射、階層叢集與 hypergeometric 群體大小估計。
