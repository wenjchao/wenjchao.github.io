---
subitem_id: "3-D"
title: "SCENIC+ 多模態 eRegulon 推斷與 GRN 重建"
---

# SCENIC+ 多模態 eRegulon 推斷與 GRN 重建

**Subitem:** 3-D · **Slug:** `scenicplus-eregulon-grn`

## 主線
把 27,492 顆異種移植 HSPC 同時整合 RNA + ATAC 推斷 enhancer-driven 轉錄因子調控網路 (eRegulon)，並對 HSC-iM 找出 NFKB1、JUNB、FOS、SMAD3 等驅動因子；同時以 RNA / ATAC 雙重 AUC > 0.4 並 FDR < 0.05 為篩選。

## 技術解析
SCENIC+ 從 27,492 顆 xenograft HSPC 推斷 enhancer-driven 調控網路前，先做兩件事壓低噪音。第一是縮樣：單細胞層級 RNA 與 ATAC dropout 太嚴重，gradient boosting 學到的會是『大家都 0』；作者用 Metacell-2 (Ben-Kiki et al. 2022) 把表現型最近似的細胞合併、目標 UMI 設 75,000，得到 1,476 個 metacell，訊號穩定且計算量降到 1/20。第二是把 ATAC 矩陣重新組織：直接看『哪些 peak 在 HSC-iM 比較開』太零散，作者用 pycisTopic v1.0.2 借 LDA 主題模型把 peak 分成 18 個 topic——每個 topic 是一組會在類似情境下同時打開的 peak。對每個 topic 內 peak，再用 pycisTarget v1.0.2 配 Aerts Lab `mc_v10_clust` motif 資料庫做 motif 富集：問『這群 peak 是不是特別擠滿某個 TF 的偏好序列？』掃了兩套位置——TSS ±10 kb 涵蓋遠端 enhancer、TSS -500/+100 bp 涵蓋核心 promoter。富集的 motif 對應到 TF 就拿到下一步。

傳統 SCENIC 只連 TF mRNA → target mRNA，看不到中間的 enhancer。SCENIC+ v0.1 (Bravo González-Blas et al. Nat Methods 2023) 把整條路重建：先過濾掉超過 0.5% 細胞缺失的 region 與 gene，接著 `merge_cistromes` 把同一個 TF 的標靶調控區 (peak) 全列成一個 cistrome；然後 `calculate_regions_to_genes_relationships` 對每個基因設 ±150 kb 搜索範圍——這個距離是 enhancer 與 target gene 物理互動的常見範圍 (由 Hi-C TAD 邊界決定)，太緊會錯過遠端 enhancer、太鬆 RAM 爆炸並引入 false positive。在這個範圍裡用 gradient boosting 訓一個模型：『metacell × peak 開放度』預測『metacell × gene 表現量』，每個 peak 的 importance 就被當成它對該基因的調控強度。再用 pySCENIC v0.12.0 推 TF → gene 直接關聯，最後 `build_grn` 用 GSEA 恢復方法把『TF → enhancer cistrome → target gene』三段串成 eRegulon。每個 TF 同時被報兩個 eRegulon：以 target gene 表現量算的 (gene-based AUC) 與以 target peak 開放度算的 (chromatin-based AUC)。

兩個 AUC 在每顆 metacell 上理論應該正相關——TF 真的活躍時 enhancer 開、target gene 也上升。作者把所有 TF 用 Pearson 算這兩個分數的一致性，r < 0.25 的 TF 整批剔除，剩 133 個 TF 過關。這道 QC 擋的是『motif 富集 false positive 或只開 enhancer 但 target gene 沒動的沈默 TF』。最後篩 HSC-iM 驅動因子又設兩道閾值：AUC > 0.4 (反向 < 0.6) 是『效應量門檻』，量該 TF 能多好區分 HSC-iM vs HSC-I；FDR < 0.05 是『統計顯著門檻』，控制 133 個 TF 多重檢定的偽發現率。兩道一起把關才能挑出『又顯著、又有效應』的 TF，而且 RNA / ATAC 兩端都要過。最後浮出 NFKB1 與 REL（NF-κB 家族）、JUNB 與 FOS（AP-1 家族）、SMAD3（TGF-β 訊號中繼）作為 HSC-iM 的驅動因子。對於跨條件 (TNF vs PBS、LPS vs PBS) 的 TF 網路構建，作者再對每個 TF→gene 連結把 RNA importance 與 ATAC importance 取幾何平均，再用 AUCell adaptive thresholding 切邊建出 GRN。

## 工具與材料清單 (Toolchain)
- **Metacell-2**：把表現型近似的單細胞合併成 metacell 以壓 dropout，目標 UMI 75,000，27,492 顆 → 1,476 個 metacell；Ben-Kiki et al. 2022。
- **pycisTopic v1.0.2**：借用 LDA 主題模型把 ATAC peak 分成 18 個 topic——每個 topic 是會在類似情境下同時打開的一組 peak。
- **pycisTarget v1.0.2**：對每個 topic 內 peak 用 Aerts Lab `mc_v10_clust` motif 資料庫做富集分析，找出對應的 TF；掃 TSS ±10 kb 與 -500/+100 bp 兩套。
- **SCENIC+ v0.1**：整合 RNA + ATAC 推斷 enhancer-driven 調控網路 (eRegulon)；把 TF → enhancer cistrome → target gene 三段串接；Bravo González-Blas et al. Nat Methods 2023。
- **cistrome**：同一個 TF 標靶的調控區 (peak) 集合，由 `merge_cistromes` 從 motif 富集字典與物件 peak 取交集而得。
- **gradient boosting (calculate_regions_to_genes_relationships)**：用 metacell × peak 預測 metacell × gene，提取每個 peak 的 importance 當作 region-to-gene 調控強度；搜索範圍 ±150 kb。
- **pySCENIC v0.12.0**：在 RNA metacell 上推 TF → gene 直接關聯，作為 SCENIC+ 整合的另一條路。
- **eRegulon**：某個 TF + 它綁的 enhancer cistrome + 這些 enhancer 控制的 target gene；同時報以 RNA 與 ATAC 算的兩個 AUC 分數。
- **Pearson r ≥ 0.25 一致性 QC**：RNA-based eRegulon AUC 與 chromatin-based eRegulon AUC 在 metacell 間 Pearson 相關 r < 0.25 的 TF 整批剔除，最後 133 個 TF 過關。
- **雙重 AUC > 0.4 + FDR < 0.05**：效應量門檻 + 統計顯著門檻，RNA 與 ATAC 兩端都要過，最後挑出 NFKB1、REL、JUNB、FOS、SMAD3 等 HSC-iM 驅動因子。
