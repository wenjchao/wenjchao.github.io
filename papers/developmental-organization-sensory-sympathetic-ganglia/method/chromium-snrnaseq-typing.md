# Chromium snRNA-seq 神經節細胞型分型

1. 引用自哪篇 paper: developmental-organization-sensory-sympathetic-ganglia
2. Outline (任務主線): Chromium snRNA-seq 神經節細胞型分型
3. Method:

10x Chromium 是一台微流體儀，關鍵動作是把幾千顆細胞核與幾千顆帶條碼的凝膠珠 (barcoded gel bead) 分別導進晶片的兩條微流道，兩條流道匯流後和油相形成大量小水滴，每顆水滴 (GEM, gel bead-in-emulsion) 剛好包住一顆核加一顆珠。凝膠珠在滴內溶解，把上面刻的獨一無二 barcode 釋出，讓這顆核裡所有 mRNA 反轉錄時都掛上同一個 barcode——所有 GEM 破裂混合後上機定序，只要看 barcode 就知道「這條 read 屬於哪顆核」。這種「一滴一核一珠」在物理上是靠 Poisson 稀釋做到：若平均每顆 GEM 對應 0.1 顆核，90% GEM 空、9% 含 1 核、<0.5% 含 2 核;珠則以稍高濃度確保多數 GEM 含 1 珠——這叫 double Poisson loading。

作者為什麼在已經有 ResolveOME 的情況下還要跑 Chromium？分工不同。ResolveOME 一顆核就要一組獨立試管、幾百顆已是極限，適合「同時要 MV genotype 與 cell type」的精細戶籍調查；Chromium 是把幾千顆核倒進微流體儀一次跑完的 pooled 高通量策略，沒有 WGA、只做 mRNA 反轉錄與 barcode 標籤，適合「這顆神經節裡各細胞型佔多少比例」這種 bulk-level 人口普查。作者要的「NC 起源 neuron/glia 比例」只需要細胞型分類、不需要每顆核都有 MV，所以由 Chromium 承擔。

從解剖到上機的流程也是為了讓 GEM 分配統計成立。神經節先用剪刀剪碎、手持研磨杵 (pellet pestle) 壓破細胞釋出核，懸浮在 1% 牛血清白蛋白緩衝液 (1% BSA sorting buffer)——BSA 像潤滑劑塗在核表面讓核不彼此黏，避免形成 doublet 團塊被 FACS 誤判成單顆。加 DAPI 染核後，BD Influx FACS 把有藍光的粒子（一定是核）挑出、把破細胞碎片濾掉，並把濃度定在 800–1,000 顆核/微升——太稀 (100/μl) 大部分 GEM 空掉、能定序的核數不夠，太濃 (3,000/μl) 則 doublet 汙染爆掉。若省了 BSA 或濃度沒控好，doublet 進 GEM 會產生 chimeric transcriptome，被誤判為「同時表達 neuron 與 glia marker 的怪細胞」。

上機後作者對 ID08 的 DRG (1,714 顆核) 和 SG (2,652 顆核) 做 snRNA-seq，用 Cell Ranger 對齊 hg19 (加 `--include-introns` 因為 snRNA 抓到很多 pre-mRNA)、Seurat 做 PCA/UMAP/FindClusters；每個 cluster 用已知 marker 判斷是 neuron、glial cell 還是免疫/血管細胞，屬於「NC 起源之 neuron + glia」的 cluster 加總佔 ~80%。這 80% 是後續 MVBA 論證的必要前提——因為 MV 只在 NC 後代裡追蹤才有意義，若只有 30% 的細胞是 NC 起源，clonal 訊號會被稀釋到看不見。

4. 工具與材料:

- **10x Chromium**: 微流體儀，把單核與 barcoded gel bead 包進油包水微滴 (GEM) 一次處理幾千顆核。
- **GEM (gel bead-in-emulsion)**: 每顆水滴剛好包 1 核 + 1 珠，barcode 讓每條 mRNA 事後可追回所屬核。
- **Double Poisson loading**: 以稀釋濃度讓多數 GEM 只包 1 核 1 珠，doublet 率壓在 <0.5%。
- **1% BSA sorting buffer**: 分揀懸浮液，BSA 塗在核表面防止彼此黏成 doublet 團塊。
- **DAPI 染核**: 與雙股 DNA 結合強烈發藍光的染料，供 FACS 精確辨認核而非細胞碎片。
- **BD Influx FACS**: 高精度流式分揀機，挑出 DAPI+ 單核並定濃度 800–1,000/μl 給 Chromium。
- **Cell Ranger --include-introns**: 10x 官方對齊軟體，加 include-introns flag 因 snRNA 含大量 pre-mRNA (帶 intron)。
- **Seurat**: R 套件做 QC 過濾、PCA/UMAP、FindNeighbors/FindClusters 與 marker 分型。

5. 與此篇文章的關係:

在《Developmental organization of sensory and sympathetic ganglia》這篇文章中，作者為了確認「MVBA 觀察到的 clonal 訊號主要屬於 NC 後代而非污染細胞」這一前提，採用了 10x Chromium snRNA-seq bulk-level 分型。它解決了「若非 NC 起源細胞比例過高，MV 訊號會被稀釋到看不見」的隱含疑慮，把 ID08 DRG 1,714 顆核與 SG 2,652 顆核轉成 cluster-level 細胞型組成表，估出 NC 起源之 neuron + glia 佔 ~80%，撐起下游 MVBA 邏輯的分子基礎。
