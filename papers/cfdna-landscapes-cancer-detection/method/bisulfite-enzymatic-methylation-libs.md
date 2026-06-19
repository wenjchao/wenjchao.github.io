---
subitem_id: "2-C"
title: "Bisulfite 與酵素法甲基化建庫 (WGBS / Targeted bisulfite / EM-seq / TAPS)"
---

# Bisulfite 與酵素法甲基化建庫 (WGBS / Targeted bisulfite / EM-seq / TAPS)

**Subitem:** 2-C · **Slug:** `bisulfite-enzymatic-methylation-libs`

## 主線
將 cfDNA 上的 5mC / 5hmC 轉成可被 NGS 讀出的鹼基變化 (C→T)，使 plasma 中的 ctDNA 甲基化模式可被定量，並盡可能避免 bisulfite 對極微量 cfDNA 的降解。

## 技術解析
甲基化是身體用來「靜音」基因的化學標籤，常掛在 CpG 位點 (C 後面緊接著 G 的位置)。每種細胞身份對應一套自己的甲基化版圖，癌細胞的版圖會出現兩個典型異常——全基因組整體去甲基化 (global hypomethylation) + 抑癌基因 promoter 局部過度甲基化 (focal hypermethylation)。ctDNA 釋放進血漿時保留了這個版圖，所以從 plasma 讀甲基化既能判斷「有沒有癌」、也能反推「來自哪個器官」(tissue of origin)。問題是 NGS 機器只能讀「字長什麼樣」，看不到甲基標籤本身，必須先動一道化學手腳把甲基化的差別寫成定序看得到的鹼基變化。

於是經典手法亞硫酸鹽轉換 (bisulfite conversion) 上場。化學是：酸性高溫條件下，亞硫酸鹽把未甲基化的 C 上面的氨基拔掉，變成尿嘧啶 (U)；5 號碳被甲基化的 C (5mC) 上有甲基當保護傘，亞硫酸鹽拔不動，仍然是 C。PCR 把 U 配成 T 後下機，原本沒甲基化的位置變 T、原本有甲基化的位置維持 C，比對原始序列就能反推每個 C 位點的甲基化狀態。為什麼 5mC 擋得住？亞硫酸鹽要先把自己加在 C 的 5-6 號碳之間的雙鍵上才能脫氨，5mC 的 5 號碳已先被甲基卡住，亞硫酸鹽根本貼不上去——這個甲基既是甲基化的化學定義，也是擋掉 bisulfite 的物理擋板。

建立在這個化學原理上，Review 在 Table 2 列出四條落地路線，可照「轉換化學 × 覆蓋範圍」兩軸分。化學上：bisulfite 最經典但會燒爛 DNA；EM-seq (enzymatic methyl-seq, ref 86) 改用 TET2 + APOBEC 等酵素一步步把未甲基化 C 氧化成 U，100 pg DNA 就能起跑，AlphaLiquid Screening (ref 87) 採用；cfTAPS (refs 83, 84) 先用 TET 把 5mC + 5hmC 氧化成 5caC、再用吡啶硼烷 (pyridine borane) 把 5caC 變 T，等於「有甲基化的位置直接顯示為 T」(跟 bisulfite 相反方向的正向讀出)。覆蓋上：Chan et al. (ref 32) 用 WGBS 看 global hypomethylation；Galleri (GRAIL, ref 75) 用 hybrid capture 抓 17.2 Mb / 139× 深度涵蓋 >50 癌種；ELSA-seq (ref 76) 抓 1.05 Mb / 80,672 CpG；PanSEER (ref 74) 595 loci / 11,787 CpG；SPOT-MAS (ref 77) 把 450 region targeted bisulfite 與 WGBS 拼在一起。

為什麼要研發 EM-seq 與 TAPS？bisulfite 需要強酸 + 高溫 + 長時間孵育，這條件本身會把 DNA 大量斷裂——對 pg 等級 cfDNA 是災難。100 pg cfDNA 大約相當於 30 條基因組分量；bisulfite 跑完可能只剩 30 pg、也就是 9 條，原本稀有的 ctDNA 分子整個被刷掉。bisulfite 還會把末端鹼基啃掉，使這份樣本沒辦法同時拿來分析 fragment end motif 或 jaggedness。EM-seq 換成酵素反應、條件溫和；TAPS 走「正向讀出 + 溫和條件」雙重優化，alignment 也容易很多 (因為不像 bisulfite 把整本 cfDNA 都變成 T)。那 Galleri 為什麼還用 bisulfite？因為它的取捨是「寧可只看 1% 基因組、但每個 CpG 都讀很深」——用 panel 把 reads 集中砸在已知會差很多的位點上，加上較大 input 與冗餘 reads 補強，第一期癌仍維持 18% 敏感度、>99% specificity；代價是 real-world stage I solid tumours 只抓到 8% (ref 79)。

另一條容易翻車的失敗模式是轉換不完全。bisulfite 反應時間或溫度沒控好時，會有一群 unmethylated C 漏網沒被轉成 T；下機後這群 C 仍是 C，演算法以為「這個位置有甲基化」，整本健康人 cfDNA 的 promoter 都會被誤判成過度甲基化，分類器跟著把健康人錯判成癌。所以 bisulfite-based 平台都會在 library 裡摻入 unmethylated 內標 (spike-in) 監控轉換率；EM-seq 與 TAPS 也同樣需要轉換率 QC，但它們化學條件溫和、轉換更可控，這類失敗比較少出現。

## 工具與材料清單 (Toolchain)
- **5-methylcytosine (5mC)**：C 的 5 號碳被掛上甲基的修飾，最常見的 DNA 甲基化形式；CpG 位點上的 5mC 與基因靜音相關。
- **5-hydroxymethylcytosine (5hmC)**：5mC 被氧化一步形成的中間產物；TAPS 可同時讀出 5mC + 5hmC。
- **bisulfite conversion**：酸性高溫條件用亞硫酸鹽把未甲基化 C 脫氨成 U (PCR 後變 T)；5mC 因有甲基擋住而不被轉換。
- **WGBS (whole-genome bisulfite sequencing)**：全基因組 bisulfite + WGS，可看 global hypomethylation；Chan et al., ref 32。
- **Galleri (targeted bisulfite)**：GRAIL 開發的 17.2 Mb 甲基化 hybrid capture panel，~139× 深度，>50 癌種；ref 75。
- **PanSEER**：targeted bisulfite + PCR，595 loci / 11,787 CpG；ref 74。
- **ELSA-seq**：targeted bisulfite hybrid capture，1.05 Mb / 80,672 CpG；ref 76。
- **SPOT-MAS**：450 region targeted bisulfite + WGBS 混合策略；ref 77。
- **EM-seq (enzymatic methyl-seq)**：用酵素 (TET2 + APOBEC) 把未甲基化 C 轉成 U，條件溫和、100 pg 起跑；ref 86。AlphaLiquid Screening (ref 87) 採用。
- **cfTAPS (TET-assisted pyridine borane sequencing for cfDNA)**：先用 TET 把 5mC + 5hmC 氧化成 5caC、再用吡啶硼烷把 5caC 變 T；正向讀出、條件溫和；refs 83, 84。
- **CpG 位點**：C 後面緊接著 G 的雙核苷酸，最常被甲基化標籤掛上去的位置。
- **unmethylated spike-in**：在 library 裡摻入已知 unmethylated 的內標 DNA，用來監控 bisulfite/EM-seq/TAPS 的轉換率。

## 與此篇文章的關係
在《Genomic and fragmentomic landscapes of cell-free DNA for early cancer detection》這篇 Review 中，作者要比較 ctDNA 偵測的兩條主要訊號 (mutation vs methylation)。Bisulfite/EM-seq/TAPS 建庫家族就是甲基化路線的入口閘門：它吃進 cfDNA 與 panel 範圍，產出可被 NGS 讀為鹼基變化的甲基化訊號，餵給 Galleri、AlphaLiquid、cfTAPS 等下游分類器。Review 透過這組平台的演化 (bisulfite → EM-seq → TAPS) 說明：在極微量 cfDNA 上做甲基化，化學溫和度與 input 容忍度直接決定能不能抓到第一期癌。

## 已沿用 Baseline 詞彙
cfDNA, ctDNA, NGS, Galleri, WGS, hypomethylation, PCR, panel
