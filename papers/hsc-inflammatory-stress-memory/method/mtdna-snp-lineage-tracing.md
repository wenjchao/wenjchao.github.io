---
subitem_id: "3-I"
title: "自然遺傳多型 + mtDNA 雙重 lineage 追蹤"
---

# 自然遺傳多型 + mtDNA 雙重 lineage 追蹤

**Subitem:** 3-I · **Slug:** `mtdna-snp-lineage-tracing`

## 主線
不用外加條碼，純靠 (1) CB 捐贈者之間的 SNP 與 (2) mtDNA 變異把 HSC 子集連到下游髓系後代，並驗證 HSC-iM 的轉錄程式是否真的被「遺傳」給單核球。

## 技術解析
人類骨髓不能像細胞株那樣外加慢病毒條碼——整合會擾動 HSC 的染色質狀態，正好破壞作者想量的記憶印記。作者改挖出每位捐贈者天生不同的拼字差異 (single-nucleotide polymorphism, SNP)：62 位 CB 捐贈者混在同一條實驗線裡，每顆細胞的定序讀段都帶著「我是哪位捐贈者的孩子」這個天然指紋；每個人基因組散落上百萬處 SNP，足以把 62 人一一分開。為了把上游 HSPC 與下游進階子代放進同一張底圖，他們先用 pysam (v0.15.1) 合併三條 sort lane 的 BAM 檔、samtools (v1.17) 排序與建索引；合併後的 BAM 餵給 SoupOrCell v2.5 (protocol 見 Heaton et al. 2020 Nat Methods)，由它從讀段抽取 SNP 字母比例、把指紋相近的細胞自動分群。如此就能順著家譜在 27,492 顆 HSPC、34,755 顆 progenitor 與 20,280 顆 CD33⁺ 髓系細胞共 82,527 顆細胞間追蹤。SoupOrCell 並不知道有幾位捐贈者，作者把要分幾群 (K) 從 1 掃到 30，看「總對數似然」(total log likelihood) 曲線轉折點落在哪裡。本研究 K = 15 時對數似然最高，且和另一條獨立預測的捐贈者性別最一致，所以採用 15 條 genetic clade。掃描的兩端都有壞處：K 太低，多位捐贈者擠進同一群、HSC-iM 訊號被稀釋；K 太高，同一位捐贈者被拆成假 sub-clade，每群細胞太少統計失效。15 條 clade 中，作者再用上游 scMultiome 標好的 HSC 身分回看：若一條 clade 的 HSC 中 ≥ 95% 屬於同一群，就標為該群 dominant；落在 12–60% 區間 (兩群混雜) 就標為非特異性。最終得到 HSC-iM dominant 3 條、HSC-I dominant 9 條、非特異性 3 條共 12 條 informative clades。

primary 骨髓的 TARGET-seq+ 只有 RNA、沒有 ATAC，沒辦法直接套 xenograft 那條多模態 pipeline。作者改採兩段推斷：先把 primary BM 的捐贈者分成 HSC-I dominant 與 HSC-iM dominant 兩類，把同一類底下所有 HSC 合併成 pseudobulk，用 EdgeR 找「在 5 個以上 cell type 都顯著差異 (FDR < 0.10)」的 702 個 trajectory genes──這 702 個基因就是 HSC-I → HSC-iM 兩條岔路的指針。再以 SAM v1.0.1 (一種專為單細胞設計的降維方法) 把細胞嵌進低維空間，配 Harmony 校正捐贈者批次，最後用 Louvain 解析度 1.5 切 15 群。每群依「primary BM HSC-I 或 HSC-iM 細胞的組成比例」標回 HSC-I 派或 HSC-iM 派，把 primary 細胞也接上同一張家譜。光靠 SNP 只能分到「哪一位捐贈者」，同一捐贈者內 niche 環境差異仍可能讓單核球看起來不一樣——reviewer 會質疑：「會不會差異不是 HSC-iM 遺傳，而是捐贈者間的環境差?」作者再加一層 mtDNA 變異追蹤：每顆細胞除了核 DNA，還有上百到上千份小型環狀粒線體 DNA (mtDNA)；mtDNA 偶爾自然突變、後代細胞會原樣繼承，等於在同一捐贈者底下又能切出更細的子家族 (clone)。作者借用 Weng et al. 2024 Nature 的真實人類 mtDNA 變異資料 (protocol 見 ref. 8)，要求每個 clone 至少含 3 顆 HSC 與 3 顆 CD14 單核球才算數，最後篩出橫跨 13 位捐贈者的 213 個 clone。同捐贈者內比較不同 clone，就把「捐贈者間環境差」這個混淆變數徹底切掉。

作者沒有把 clade 二分成 HSC-iM/HSC-I 後直接比較，而是設一條連續尺度：對每位捐贈者（或每個 mtDNA clone）的 HSC pool，用 AUCell 把 HSC-iM 200 基因程式打成一個 0–1 的平均分──分數越高代表上游 HSC 越像 HSC-iM。接著把同捐贈者的單核球 RNA 合併成 pseudobulk，用 DESeq2 把單核球每個基因的表現量回歸到上游 HSC 的 HSC-iM 平均分。如果某個基因隨上游分數一起上升，DESeq2 會給它高 rank；整條 rank list 丟進 GSEA，看 HSC-iM 程式整體是否顯著富集。富集 = HSC-iM 程式真的「跟著家譜傳給」下游單核球；這個連續迴歸同時在 donor-level (32 人) 與 clone-level (213 clones) 都顯著，雙重設計同時排除人與人之間的差異與同人內 niche 差異，才能宣稱「分子記憶被遺傳」。

## 工具與材料清單 (Toolchain)
- **SNP (single-nucleotide polymorphism)**：DNA 上人人不一樣的單點拼字差異；每個人散落上百萬處，可當天然指紋區分捐贈者。
- **SoupOrCell v2.5**：從 scRNA-seq 讀段抽取 SNP 字母比例、無需參考基因組就把細胞依基因型分群的工具 (Heaton et al. 2020 Nat Methods)。本研究 K 掃 1–30，取 K = 15。
- **pysam v0.15.1 / samtools v1.17**：合併、排序、建索引 BAM 檔的程式包，把三條 sort lane (HSPC、progenitor、髓系) 的讀段放進同一張底圖。
- **genetic clade**：SoupOrCell 切出的 SNP 基因型分群，每條 clade 對應一位捐贈者的細胞家族。HSC pool 內 ≥ 95% 同群即標為 dominant。
- **EdgeR**：對 pseudobulk RNA-seq 找跨樣本差異基因的統計套件；本研究用來找 5 個以上 cell type 同時 FDR < 0.10 的 702 trajectory genes。
- **SAM algorithm v1.0.1**：一種專為單細胞 RNA 設計的降維方法，能避免 PCA 對少數變異的過度權重；本研究與 Harmony、Louvain res = 1.5 串起來把 primary BM 細胞切成 15 群。
- **mtDNA (mitochondrial DNA)**：細胞自帶的小型環狀粒線體 DNA；自然突變後子代細胞會原樣繼承，等於同捐贈者內的子家族編號 (Weng et al. 2024 Nature)。
- **mtDNA clone**：同一位捐贈者底下，共享某個 mtDNA 突變的細胞子家族；要求每個 clone 至少 3 顆 HSC + 3 顆 CD14 單核球，篩出 213 clones × 13 donors。
- **AUCell**：把一組 200 基因程式在每顆細胞上打成 0–1 連續分數的工具；本研究用來算每位捐贈者 HSC pool 的「HSC-iM 平均分」。
- **DESeq2 連續變數迴歸**：把 pseudobulk 表現量對一個連續變數（上游 HSC-iM 平均分）做回歸，輸出整條基因 rank list 給 GSEA 富集分析。
