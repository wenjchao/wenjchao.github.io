# scRNA-seq 與 scVelo differential kinetics 動力學分析

1. 引用自哪篇 paper: developmental-organization-sensory-sympathetic-ganglia
2. Outline (任務主線): scRNA-seq 與 scVelo differential kinetics 動力學分析
3. Method:

作者取 E8.5、E9.0、E9.5 三個時間點的 Wnt1-Cre;TdTomato+ 神經脊細胞（總共 16,115 顆）做 10x Chromium 單細胞 RNA-seq。第一步是把 reads 分成兩堆：短片段若比對到 intron 就當「初稿 pre-mRNA」(unspliced)、比對到 exon-exon junction 就當「定稿 mRNA」(spliced)，用 velocyto (v0.17.17) 對 mm10 基因組生 loom 檔，再用 loompy 把不同 replicate 的 loom 檔合併。第二步是降維與分群：Seurat 4 + SCTransform 標準化後，用主成分分析 (PCA) 把 16,000 個基因壓縮成 30 維、連結每顆細胞的 30 個最相似鄰居 (k-nearest-neighbour graph, k=30)，最後用 UMAP 畫平面圖並用 marker gene（Zic1 標未離管 NC、Neurog1/2 標感覺、Ascl1 標交感）給每個 cluster 貼 lineage 標籤。

有了 spliced 與 unspliced 讀數，就能算 RNA velocity。每個基因在穩定表現時初稿到定稿的比例是固定的；當細胞決定上調這個基因時，轉錄爆量會讓 unspliced 快速衝高、還沒剪接與累積成 spliced，unspliced/spliced 比例會暫時偏高。過幾個小時 spliced 才慢慢累積、比例回到穩態。反之下調時 unspliced 先掉、spliced 因半衰期較長還在，比例會暫時偏低。所以「unspliced 是否領先 spliced 的穩態值」就是這個基因往上還是往下走的訊號；把每顆細胞所有基因的方向拼起來，就能推出這顆細胞下一刻大概會往哪個 cell state 移動。

作者用 scVelo (v0.3.3) + Scanpy (v1.11.4) 執行動力學分析，設定幾個關鍵參數：`filter_and_normalize(min_shared_counts=20, n_top_genes=2000)` 只挑跨細胞變異最大的 2,000 個基因 (highly variable genes)——大部分 housekeeping gene 在每顆細胞的表現量都差不多，不但無法區分細胞狀態、還會稀釋統計 power；min_shared_counts=20 則把「連基本訊號都不夠」的低表現量基因先過濾掉，避免動力學擬合噴走。降維採 PCA 30 components + k-NN k=30。核心引擎 `recover_dynamics` 用的是 scVelo 的動力學模型 (dynamical model)：把每個基因的轉錄、剪接、降解速率當成三個可估參數，從所有細胞的 spliced/unspliced 讀數擬合出每個基因獨立的一套動力學參數。作者不用簡化的 stochastic model 是因為後續要比較「不同 lineage 的動力學是否不同」，需要一組可比較的 rate constants，只 dynamical model 提供這個接口。

作者挑一組候選 TF，跑 `differential_kinetic_test` 逐個檢定。做法是同一個 TF 分兩次擬合：一次用全體 NC 細胞、一次只用感覺（或交感）譜系細胞。scVelo 計算兩組擬合的殘差差異，經似然比檢定 (likelihood ratio test) 給出 P 值——若感覺譜系那組能顯著降低殘差，代表全體那組參數描述不了感覺譜系的動力學，這個 TF 在感覺譜系裡有自己一套動力學。結果：感覺線裡 Onecut1 顯著偏斜 (E8.5 P = 3.6e-3、E9.5 P = 5.9e-4)；交感線裡 Rfx4 在三個時間點都極度顯著 (P < 1e-64)。這些 TF 就是「未離管 NC 已經有 lineage-specific 動力學」的分子證據——為 MVBA 與小鼠 CRISPR 條碼推出的「fate 早於離管」結論，補上直接可觀察的轉錄機制。整個 pipeline 對 cluster label 高度敏感，所以作者先用 Zic1、Sox10、Neurog1/2、Ascl1 這些人類已知 marker 檢查 cluster 屬性再跑動力學比較，避免 lineage subset 混入其他細胞產生假陽性。

4. 工具與材料:

- **velocyto (v0.17.17)**: 把 scRNA-seq reads 依比對到 intron/exon-exon junction 分成 unspliced/spliced 讀數，輸出 loom 檔給 scVelo。
- **loompy (v3.0.6)**: 合併多個 replicate 的 loom 檔成單一 stage-specific 矩陣。
- **scVelo (v0.3.3) + Scanpy (v1.11.4)**: Python 套件；從 spliced/unspliced 比例推 RNA velocity，並提供 dynamical model 與 differential_kinetic_test 兩個關鍵函式。
- **Seurat (v4.0.5) + SCTransform**: R 套件；做細胞層級標準化、降維、分群、marker gene 標注 lineage。
- **Highly variable genes (n_top_genes=2000)**: 只挑跨細胞變異最大的 2,000 個基因進動力學擬合，避開 housekeeping gene 稀釋訊號。
- **Dynamical model (recover_dynamics)**: scVelo 對每個基因擬合完整的轉錄-剪接-降解速率常數，回溯每個基因獨立的動力學參數。
- **differential_kinetic_test**: 同一 TF 分別用「全體 NC」與「特定 lineage 細胞」擬合動力學，經似然比檢定給出「lineage-specific 動力學是否顯著」的 P 值。
- **Onecut1 / Rfx4**: 檢定挑出的候選 TF：Onecut1 在感覺譜系動力學顯著偏斜；Rfx4 在交感譜系跨三個時間點都極顯著 (P < 1e-64)。

5. 與此篇文章的關係:

在《Developmental organization of sensory and sympathetic ganglia》這篇文章中，作者為了確認 MVBA 推出的「NC fate 早於離管」不只是統計現象，而有實際分子驅動，把 E8.5–E9.5 Wnt1-Cre;TdTomato+ NC 單細胞 RNA-seq 跑 scVelo 動力學分析。這一步吃 spliced/unspliced reads，產出每個 TF 的動力學參數與 lineage-specific 顯著性 P 值，把 Onecut1（感覺）、Rfx4（交感）點名為未離管 NC 內部已在跑 lineage-biased 動力學的候選調控者。它讓「fate 早已被指派」的論斷從 clonal 統計升級為可指名 TF 的轉錄機制。
