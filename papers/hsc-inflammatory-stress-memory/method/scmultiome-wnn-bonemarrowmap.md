---
subitem_id: "3-B"
title: "scMultiome 預處理、WNN 整合與 BoneMarrowMap 細胞態指認"
---

# scMultiome 預處理、WNN 整合與 BoneMarrowMap 細胞態指認

**Subitem:** 3-B · **Slug:** `scmultiome-wnn-bonemarrowmap`

## 主線
在同一條 pipeline 中對齊 RNA + ATAC 雙模態、去除 ambient RNA、跨性別/捐贈者批次校正，並以 weighted nearest-neighbour (WNN) 整合 + BoneMarrowMap 投射把每顆細胞同時放到「雙模態 UMAP」與「26 種骨髓細胞態」上，這是後續所有 HSC 子集分群的基礎。

## 技術解析
這條 pipeline 的入口是 10X Genomics 的 scMultiome：在同一個細胞核裡同時測 RNA 與 ATAC——後者反映這顆細胞核裡哪些 DNA 段落是『鬆開可讀』的 (由 Tn5 轉位酶優先插入開放區段定義)。作者選 scMultiome 而非單做 RNA，是因為 inflammatory memory 的核心假設就是『mRNA 早就退了、染色質上的痕跡留下來』——只看 RNA 會把記憶細胞與普通細胞混在一起。原始 reads 先用 CellRanger-ARC v2.0.0 對到 GRCh38、用 MACS2 v2.2.7.1 重新 call peak。接著用 SoupX v1.6.2 (Young & Behjati 2020) 估每個樣本『湯裡有多濃的漂浮 RNA』再從每顆細胞扣除——這是 droplet 平台特有的背景，跳過它紅血球的血紅蛋白基因會四處污染分群。

QC 閾值分別擋三種雜訊：`nFeature_SoupX > 1,000` 砍破裂瀕死細胞、`pct_mito < 18%` 砍細胞膜破掉只剩粒線體 mRNA 的細胞、`TSS_enrichment > 1` 砍 Tn5 反應品質差的 ATAC。批次校正用 Harmony v0.1.1 (Korsunsky et al. 2019)，但有個特殊處境：62 位 CB 捐贈者被混在同一 pool，誰是誰要等 SoupOrCell 跑完才知道。作者先用『推斷的捐贈者性別』(男性有 Y reads、女性有 XIST) 當 Harmony 的 batch 變數，對 RNA 用 PC1–20、對 ATAC 用 LSI 2–30 (潛在語意索引降維後的維度)，把性別偏差洗掉後 HSC 子集才浮現。

RNA 與 ATAC 要合成同一張 UMAP 才能同時看『轉錄程式 + 染色質印記』，這就是 weighted nearest-neighbour (WNN, Seurat v4, Hao et al. Cell 2021) 的工作。WNN 讓每顆細胞自己投票哪邊可信：RNA 鄰居分得越開就給越高權重，ATAC 雜訊大則給低權重；最終鄰居圖是兩邊鄰居圖的加權平均。這個自適應設計很關鍵——ATAC 訊號比 RNA 稀疏約十倍，整批用同一權重會被 ATAC 拖糊。WNN 完成後把鄰居圖丟給 UMAP (min.dist = 0.2、spread = 1) 就是雙模態 UMAP；只用 RNA 做 UMAP 的話，HSC-iM 與 HSC-I 在恢復期 mRNA 已太像，兩群會混在一起。

拿到雙模態 UMAP 後，作者把每顆細胞投射到 BoneMarrowMap (Zeng et al. Blood Cancer Discov 2025)——作者先前訓練好的『人類骨髓 26 種細胞態地圖』。投射時超過 mapping error 中位數 + 2 MAD 的細胞被丟掉，等於『找不到合理位置就不要硬貼』。但 26 種還不夠細：HSC 在 BoneMarrowMap 是一個群，研究要的是 HSC-I 與 HSC-iM 兩個子集。作者於是在 WNN 鄰居圖上跑 Leiden 圖分群、把解析度從 0.1 掃到 10，每個都跟 BoneMarrowMap 的 26 類做混淆矩陣對齊；最終手動挑 res = 1、5、10 三個解析度的組合定義 HSC-I 與 HSC-II，未分群的 ~1% 細胞用最近鄰多數投票補標。

## 工具與材料清單 (Toolchain)
- **scMultiome (10X Genomics)**：同一個細胞核同時測 RNA 與 ATAC 的單細胞平台；ATAC 端由 Tn5 轉位酶優先插入開放染色質區段定義。
- **CellRanger-ARC v2.0.0**：10X 官方 scMultiome 對齊軟體，把 reads 對到 GRCh38 並輸出 RNA count 與 ATAC fragments。
- **MACS2 v2.2.7.1**：從 ATAC fragments 重新 call peak 的工具；本研究對 CB xenograft 三組 (PBS/TNF/LPS) 各自獨立 call。
- **SoupX v1.6.2**：估算 droplet 平台『漂浮 RNA 污染』(ambient soup) 並從每顆細胞扣除；Young & Behjati 2020 ref. 79。
- **Harmony v0.1.1**：scRNA/ATAC 的批次校正工具；本研究以推斷的捐贈者性別為 batch、對 RNA 用 PC1–20、對 ATAC 用 LSI 2–30。
- **LSI (latent semantic indexing)**：ATAC 端的稀疏矩陣降維方法，類似 TF-IDF + SVD，用於 Harmony 的低維輸入。
- **WNN (weighted nearest-neighbour)**：Seurat v4 的雙模態整合演算法，讓每顆細胞自己投票哪邊資訊量大、再以加權鄰居圖跑 UMAP；Hao et al. Cell 2021 ref. 49。
- **BoneMarrowMap**：作者先前訓練的人類骨髓 26 細胞態參考圖譜；用 reference projection 把新細胞貼標，並用 mapping error 中位數 + 2 MAD 作為拒答上限；Zeng et al. Blood Cancer Discov 2025 ref. 32。
- **Leiden clustering**：在 WNN 鄰居圖上跑的圖分群演算法，作者把解析度從 0.1 掃到 10 並與 BoneMarrowMap 的 26 類做混淆矩陣對齊。
- **QC 閾值組合**：`nFeature_SoupX > 1,000`、`pct_mito < 18%`、`nCount_ATAC > 1,000`、`nucleosome_signal < 2`、`TSS_enrichment > 1` 五條共同擋下破裂細胞、粒線體污染、ATAC 雜訊。
