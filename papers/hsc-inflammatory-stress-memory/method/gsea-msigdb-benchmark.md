---
subitem_id: "3-E"
title: "GSEA 與 8,312 gene set 大規模對照基準測試"
---

# GSEA 與 8,312 gene set 大規模對照基準測試

**Subitem:** 3-E · **Slug:** `gsea-msigdb-benchmark`

## 主線
把作者定義的 HSC-iM 程式 (top 200 genes) 丟到 8,312 個外部 gene set 一起跑 GSEA 並做共同多重檢定校正，量化「HSC-iM 在 COVID/CH/ageing/SCD 上的富集到底有多 enrich 到普世顯著」。

## 技術解析
作者要回答的問題是：『HSC-iM 程式在 ICU-COVID、CH、ageing、SCD 等隊列上的富集到底有多顯著？』直接平均 200 個 HSC-iM 基因的 log2FC 會錯過『全體小幅但一致上升』的訊號，所以採用基因集富集分析 (gene set enrichment analysis, GSEA)：先把每個比較裡所有基因依差異表現排名（用 DESeq2 test statistic 而非 log2FC，因為 test statistic = log2FC / standard error 已校正散度，能避免低表現高方差基因搶位）；接著沿排名走，每碰到 HSC-iM 基因加分、非 HSC-iM 扣分，曲線最高點為 enrichment score；用置換 1,000,000 次估零分布算 p value。實作用 fgsea v1.18.0 的 `fgseaMultilevel`——這個版本能精確估到 1e-50 等級的 p value，搭配 `eps = 0` 禁止下界截斷；gene set 大小限制 15–500 (`minSize`、`maxSize`)，避免太小統計力不足或太大不夠專一。

光說『HSC-iM 顯著』還能被質疑成是 cherry-picking，所以作者把它丟進一場大型對照競賽。背景集從兩個來源拼成：Gary Bader Lab 的 `Human_GOBP_AllPathways_no_GO_iea` (2023-04 版) 提供基因本體生物程序，MSigDB 提供化學遺傳擾動 (CGP)；過濾大小 15–500 後 GOBP 留 6,653、CGP 留 2,615，總共 9,270 個。為了讓所有差異表現比較共用同一套競爭池，作者再做第二輪過濾：要求一個 gene set 至少 3 個基因同時出現在所有 7 條 rank list (older-aged vs young HSC、ICU-COVID vs control HSC/monocyte、DNMT3A-mutant vs control HSC、TET2-mutant vs control HSC 等)，最後留 8,312 個。HSC-iM 與 HSC-I 程式自己再加進去成 8,314，共用 Benjamini-Hochberg FDR 校正。共同檢定的精神是：要保持 FDR < 0.05 需要 p value 比未校正版小 8,314 倍。如果 HSC-iM 在 ICU-COVID 排第一、在 ageing 勝過 99.4%，這個排名不是『單一檢定剛好顯著』，而是『放在整個基因集天空都壓得住別人』。

GSEA 結果作者用 EnrichmentMap (Merico et al. 2010) 視覺化：把所有 FDR < 0.01 的 gene set 兩兩比較基因重疊率，重疊高的用粗邊連起來，發炎相關 gene set 會自然連成一團、quiescence 連成另一團，比讀幾十行表格清楚得多。為了把 HSC-iM 投回單細胞層級看，RNA 用 AUCell（gene set 在每顆細胞表現量排名中是否擠在前面），ATAC 用 chromVAR v1.14.0 (Schep et al. 2017)——ATAC 是 peak × cell 的 0/1 稀疏矩陣，AUCell 算不穩；chromVAR 對一組 peak 集合，把每顆細胞讀數總和跟『隨機抽相同 GC 比例 peak』比較，算偏差 Z-score 作為富集。hg19 → hg38 用 rtracklayer v1.52.1 chain 對齊。若把 `nPermSimple` 從 1,000,000 降到 1,000，前幾百名 gene set 會全擠在 `p < 0.001` 同點，HSC-iM 排不出第一名——這也是為何百萬置換是排名解析度的必要條件。

## 工具與材料清單 (Toolchain)
- **fgseaMultilevel (fgsea v1.18.0)**：多階置換版 GSEA，可精確估到 1e-50 等級的 p value；參數 nPermSimple = 1,000,000、eps = 0、minSize = 15、maxSize = 500。
- **DESeq2 test statistic**：log2FC / standard error 的信噪比，作為 GSEA 排名統計量；比直接用 log2FC 更穩定。
- **Human_GOBP_AllPathways_no_GO_iea (2023-04)**：Gary Bader Lab 提供的基因本體生物程序集合，過濾後 6,653 個 gene set 作為 GSEA 背景。
- **MSigDB CGP**：MSigDB 的化學遺傳擾動集合，過濾後 2,615 個 gene set 與 GOBP 合併。
- **8,312 個 gene set 共同 FDR**：兩輪過濾後 7 條 rank list 共用的競爭池，加上 HSC-iM/HSC-I 程式成 8,314，共用 Benjamini-Hochberg FDR 校正。
- **EnrichmentMap**：把 FDR < 0.01 的 gene set 用基因重疊率連成網，發炎與 quiescence 等主題自然分群；Merico et al. 2010。
- **AUCell (RNA scoring)**：把一組 gene 投到每顆細胞，問是否擠在表現量排名前段；用於 HSC-iM 程式在單細胞 RNA 上的富集評分。
- **chromVAR v1.14.0 (ATAC scoring)**：對 ATAC peak 集合算與『隨機抽相同 GC 比例 peak』的偏差 Z-score 作為富集；針對 peak × cell 的 0/1 稀疏矩陣設計；Schep et al. 2017。
- **rtracklayer v1.52.1 chain**：用 hg19 → hg38 的座標 chain 檔把不同來源 ATAC peak 對齊到統一基因組版本。
