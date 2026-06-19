---
subitem_id: "2-D"
title: "cfMeDIP-seq：免疫沉澱式全基因組甲基化 (Bisulfite-free IP)"
---

# cfMeDIP-seq：免疫沉澱式全基因組甲基化 (Bisulfite-free IP)

**Subitem:** 2-D · **Slug:** `cfmedip-seq`

## 主線
不經化學轉換、直接用抗 5mC 抗體把甲基化 cfDNA 片段拉下來定序，以保留 cfDNA 完整 fragment 結構並同時取得全基因組甲基化分布。

## 技術解析
MeDIP (Weber et al. 2005, ref 82) 原本是給組織 DNA 設計的甲基化免疫沉澱定序；Shen et al. 2018 (ref 46) 把它針對 cfDNA 的微量 input 重新最佳化，叫做 cfMeDIP-seq。流程骨架是這樣：從血漿抽出 cfDNA、不打碎 (cfDNA 本來就是 167 bp 短片段)，接 adapter 做 library，加入只認甲基帽的抗體 (anti-5mC antibody)，抗體會抓住所有戴帽的 cfDNA 片段，再用磁珠把抗體連同片段一起拉下來、洗掉沒戴帽的，最後定序這群「被選出的甲基化 cfDNA」，看它們落在基因組哪裡。抗體的「抓手」(paratope) 是一個形狀互補的小袋子，剛好能容納 5mC 上頭那個小小的甲基；沒戴帽的普通 C 表面少了這顆疏水甲基，結合親和力差好幾個數量級，所以富集後留下的就是甲基化訊號富集數十倍的 library。

cfMeDIP-seq 的最大優勢是「不損傷 cfDNA」——整套流程裡 cfDNA 沒被任何化學試劑攻擊，只是被抗體物理上抓走，所以 fragment 長度、兩端鹼基序列、jaggedness 都完好如初。意思是同一管 cfMeDIP-seq library 可以同時餵給甲基化分類器與 fragmentation 分類器，兩種訊號互不污染——bisulfite 處理會把 167 bp 片段切成 50-80 bp 碎屑，根本做不到這件事。三種情境特別適合：input 量極微 (CSF、urine cfDNA) 時 bisulfite 會切壞；需要同時做 fragmentation feature 分析時化學法都會污染 size 訊號；目標是 region-level 全基因組訊號 (例如腦癌亞型分類, ref 83) 時 cfMeDIP-seq 廣度大、解析度足夠。反之需要 single-CpG 解析度時要走 WGBS 或 targeted bisulfite。

cfMeDIP-seq 是「全基因組」但「不是 single-CpG 解析度」。抗體抓的是「至少帶幾個甲基帽的整段 cfDNA」，所以一段 167 bp 片段裡如果只有一個 CpG 甲基化，整段也會被拉下來——你無法分辨到底是哪一個 CpG 在貢獻訊號。Shen et al. 2018 (ref 46) 用 189 plasma + 199 validation samples 在 7 種癌看 thousands of methylated regions；後續一個 608-sample 延伸研究 (ref 83) 分辨腦癌亞型。但如果硬把 cfMeDIP-seq 的 read count 當成 single-CpG methylation level 用，背景隨機富集會被當成真訊號，假陽性大量冒出來。另一個失敗模式是抗體批次效應——某段 region 的 IP 富集倍數會隨抗體 lot、IP 條件漂動；批次 A 訓練、批次 B 驗證時模型會把「批次差異」當「癌 vs 非癌差異」學，AUC 在新批次直接崩。解法是每次 IP 加 spike-in control DNA 當校正基準，把批次效應扣掉。

## 工具與材料清單 (Toolchain)
- **MeDIP (Weber et al. 2005, ref 82)**：原版甲基化 DNA 免疫沉澱定序，給組織 DNA 使用。
- **cfMeDIP-seq (Shen et al. 2018, ref 46)**：針對 cfDNA 微量 input 最佳化的 MeDIP 版本；保留 fragment 結構。
- **anti-5mC antibody**：只認甲基帽的抗體，paratope 形狀互補 5mC 上的甲基取代基。
- **Magnetic bead pulldown**：用磁珠把抗體連同被抓的甲基化 cfDNA 片段一起拉下來。
- **Thousands of methylated regions**：cfMeDIP-seq 一次定序可同時觀察的全基因組甲基化 region 數量。
- **189 plasma + 199 validation samples (7 cancers)**：Shen et al. 2018 的初代驗證 cohort，覆蓋 7 種癌。
- **608-sample brain cancer extension (ref 83)**：後續延伸研究，用同方法分辨腦癌亞型。
- **Region-level resolution**：cfMeDIP-seq 的解析度層級，不是 single CpG；適合 ML region-bin 特徵設計。
- **Spike-in control DNA**：每次 IP 加入的已知甲基化狀態外源 DNA，用以校正批次間 IP 效率漂移。

## 與此篇文章的關係
在《Genomic and fragmentomic landscapes of cell-free DNA for early cancer detection》這篇 review 中，作者要列出能繞開 bisulfite 降解問題的甲基化方案。cfMeDIP-seq 解決的是「化學轉換把極微量 cfDNA 切碎、又破壞 fragment 結構」的瓶頸：用抗體把戴甲基帽的 cfDNA 整片拉下來、完全不動 DNA。它為下游同時需要甲基化與 fragmentation 訊號的多模態分類器 (例如 SPOT-MAS、AlphaLiquid 思路) 提供乾淨的 region-level 甲基化特徵，特別適合 CSF、urine 等極微量場景。

## 已沿用 Baseline 詞彙
cfDNA, 甲基化, methylation, bisulfite, fragmentation, fragment, AUC
