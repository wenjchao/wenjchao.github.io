---
subitem_id: "3-C"
title: "跨捐贈者解多工：SoupOrCell + 性別分類器 + 雙細胞偵測"
---

# 跨捐贈者解多工：SoupOrCell + 性別分類器 + 雙細胞偵測

**Subitem:** 3-C · **Slug:** `souporcell-demuxing`

## 主線
在無外部 genotype 參考的情況下，把多 CB 混合的 scMultiome 文庫解多工回單一捐贈者，並偵測跨捐贈者 doublet，這是本研究能用 62 位 CB 自然 SNP 做 genetic clade 追蹤的核心。

## 技術解析
為了同時拿到多位捐贈者的細胞又避免 inter-library batch effect，作者把 3 個 CB pool（共 62 位捐贈者）的細胞混在同一支 10X scMultiome 文庫裡跑。代價是『拿到一桶細胞，每顆不知道屬於誰』。SoupOrCell v2.5 (Heaton et al. 2020) 從 BAM 中所有 read 帶到的單核苷酸多型性 (SNP) 反推每顆細胞屬於哪位捐贈者：它先掃出所有出現 read 的 SNP 位點，每顆細胞在每個位點得到一個小計數 (例如 5 個 A、2 個 G)；接著用一個混合模型同時推估『假設有 K 位捐贈者各自的基因型』與『每顆細胞屬於每位捐贈者的後驗機率』，透過 EM 迭代收斂後就完成歸戶。事先不知道一桶裡有幾位捐贈者，作者把 K 從 1 掃到 30，每個 K 算一個總對數似然 (log-likelihood)，把曲線畫成 elbow plot 找『陡升轉微升』的拐點；本研究在 K = 15 出現拐點，對應到 15 位真正的捐贈者。如果跳過這一步，跨捐贈者 SNP 差異會被 PCA / UMAP 抓成主要變異方向，看起來像十幾條譜系，後面的 HSC-iM clade → CD14 monocyte 追蹤完全沒辦法做。

光靠 SoupOrCell 的 SNP 分群不夠，作者另用一把獨立的尺：性別。ATAC 端做法很直接，對 ATAC read depth > 6,000 的細胞，只要有一條 read 落到 Y 染色體就標男性、沒有就標女性。RNA 端比較細，用 Seurat 的 `AddModuleScore` 對每顆細胞算兩個模組分數——『Y 染色體基因 (扣掉與 X 共享的擬常染色體區)』與『女性專一表現基因 XIST + TSIX』，分數先做 min-max 標準化，再借 AUCell v1.14.0 的自適應閾值切：分數穿過閾值且另一性分數為 0 才採信。adaptive thresholding 的精神是讓演算法擬合分數的雙峰分布、挑兩峰之間最低點為切點，當男女比例懸殊時切點會自動調整。雙重採信（ATAC 與 RNA 都判同一性別）才算高置信度。性別接著當第二把尺：每個 SoupOrCell cluster 內細胞性別應該均一；若某 cluster 男女混雜，代表 K 不夠或該 cluster 該被拆。本研究 K = 15 後每個 cluster 性別均一，作者才確認解多工成功。

兩顆不同捐贈者的細胞被裝進同一液滴會產生跨捐贈者 doublet——這顆假細胞的 reads 同時帶兩套 SNP、有時還同時表現 Y 與 XIST。作者用兩條獨立路抓：(1) SoupOrCell 直接抓『同時屬於兩個 cluster 的細胞』，這是 heterotypic（兩位 donor）doublet；(2) scDblFinder v1.6.0 (Germain et al. 2021) 用人工合成 doublet 訓練機器學習器，從 RNA 表現量找『同時表達兩種 cell type marker』的細胞，能抓 homotypic 同 donor doublet。兩條交集後從下游剔除，並確認『同時表現 Y 與 XIST』會被兩條路同時捕捉。Fig. 5 的 genetic clade 追蹤再進一步：作者把 HSPC scMultiome、CD34⁺CD38⁺ progenitor scRNA-seq 與 CD33⁺ myeloid scRNA-seq 三個獨立庫的 gene expression BAM 用 pysam v0.15.1 合併、samtools v1.17 排序索引，一次性丟給 SoupOrCell 跑 K = 1–30，讓三個庫共享同一套捐贈者標籤。HSC pool 內 ≥ 95% 屬於某類才算 dominant clade（HSC-iM dominant n = 3、HSC-I dominant n = 9、非特異性 n = 3），這條跨庫共享標籤正是『把 HSC 子集連到下游 progenitor 與 myeloid 後代』的關鍵。

## 工具與材料清單 (Toolchain)
- **SoupOrCell v2.5**：從 BAM 中 SNP 位點 reads 以混合模型 EM 推估『K 位捐贈者基因型 + 每顆細胞屬於誰』的無參考解多工工具；Heaton et al. 2020。
- **elbow plot of log-likelihood**：把 K 從 1 跑到 30 的總對數似然畫成曲線，找『陡升轉微升』的拐點挑最佳 K；本研究 K = 15。
- **Seurat AddModuleScore**：對每顆細胞算一組基因（Y 染色體基因 vs XIST/TSIX）的模組平均分數，作為性別推斷輸入。
- **AUCell v1.14.0 adaptive thresholding**：擬合分數的雙峰分布、挑兩峰之間最低點為切點，避免人為硬切分位數。
- **scDblFinder v1.6.0**：用人工合成 doublet 訓練機器學習器，從 RNA 表現量找『同時表達兩種 cell type marker』的細胞，能抓同 donor doublet；Germain et al. 2021。
- **pysam v0.15.1 + samtools v1.17**：合併三個獨立庫 (HSPC scMultiome、CD34⁺CD38⁺ progenitor、CD33⁺ myeloid) 的 gene expression BAM 並排序索引，讓三個庫共享同一套 SoupOrCell 捐贈者標籤。
