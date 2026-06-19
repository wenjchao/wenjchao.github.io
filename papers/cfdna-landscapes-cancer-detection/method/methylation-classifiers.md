---
subitem_id: "3-G"
title: "cfDNA-based methylation 分類器 (Galleri / cfMeDIP-seq / cfTAPS / AlphaLiquid / FRAGMA)"
---

# cfDNA-based methylation 分類器 (Galleri / cfMeDIP-seq / cfTAPS / AlphaLiquid / FRAGMA)

**Subitem:** 3-G · **Slug:** `methylation-classifiers`

## 主線
將 bisulfite、EM-seq、TAPS、MeDIP 或 end-motif-derived methylation signal 轉成 per-region 甲基化特徵向量，以多癌篩檢與 tissue-of-origin 為目標訓練分類器。

## 技術解析
整套 methylation 分類器流程分三層。第一層是讀甲基化：把血漿 cfDNA 拿出來，用四選一的方法把 5mC 訊號轉成 NGS 看得懂的鹼基變化——bisulfite / EM-seq / TAPS 把沒甲基化的 C 變成 T、留下 5mC 還是 C；cfMeDIP-seq 用抗 5mC 抗體把甲基化片段拉下來；FRAGMA 則完全不做化學轉換，從 fragment end motif 反推。第二層是把訊號整理成 per-region 數字：把基因組分成「區域」——可以是 Galleri 的 17.2 Mb hybrid-capture panel、cfMeDIP-seq 的全基因組 CpG bin、或 AlphaLiquid 用的 cell-type-specific 差異甲基化區段 (differentially methylated regions, DMRs)，對每區算「這區裡甲基化 read 佔多少」。第三層是分類器：把所有 region 的甲基化值串成一條向量，再加上 fragmentation 或 CNV 等其他 cfDNA 特徵，丟給機器學習訓練多癌篩檢加上 tissue-of-origin head。Galleri 用 17.2 Mb hybrid-capture bisulfite + 139× 深度，stage I 18% → stage IV 93% 是這條 pipeline 的代表性表現。為什麼 methylation 能同時做兩件事？因為每種細胞的「靜音譜」不同，DMR 是 cell identity 的天然指紋；癌細胞兩個 hallmark（promoter 過度甲基化壓住保護機制、全基因組去甲基化讓本該被壓住的區段反活化）又保留了原本組織的簽名。

四條化學路線的差異在「怎麼讓 NGS 看得到 5mC」。bisulfite 用 HSO3- 強酸把沒甲基化的 C 化學變成 U，PCR 後變 T；5mC 抵抗這個反應依然是 C，所以定序時看到 C 就是甲基化、看到 T 就是未甲基化。EM-seq 把這套化學換成酵素 (TET2 + APOBEC) 一步步做，效果一樣但 DNA 損傷小很多——這就是為什麼能從 100 pg input 起跑。TAPS 反過來：用 TET 把 5mC / 5hmC 氧化成 5caC，再用 pyridine borane 還原為 DHU，PCR 後變 T；換句話說 TAPS「把甲基化直接改寫」而非「把非甲基化燒掉」，因此 DNA 損傷最少。MeDIP 走完全不同路線：不做化學轉換，改用抗 5mC 抗體直接把含甲基化的片段釣下來，保留完整 fragment 結構，能與 fragmentomic 訊號共存。第五條路線 FRAGMA 完全不做化學轉換或免疫沉澱：它的關鍵觀察是甲基化會改變 cfDNA 末端在哪些位置被切，end motif 分布本身就攜帶「附近甲基化狀態」資訊。FRAGMA 用機器學習從一份 sWGS 的 end motif 直接迴歸 per-region methylation level，input 不會被燒掉。代價是訊號間接、雜訊比直接讀大。

為什麼 Galleri 選 17.2 Mb hybrid-capture / 139× 而不是 whole-genome bisulfite？因為 WGBS 對極微量 cfDNA 來說 reads 會被攤太薄，每個 CpG 平均只覆蓋幾條 read，遠不足以可信呼叫 methylation level。Galleri 改走 targeted：先離線挑出 17.2 Mb 跨多癌種最具辨識力的 methylation region（約佔基因組 0.5%），hybrid capture 把 reads 集中砸到這些區段，達到 139× 深度——足以做 single-CpG resolution 量化。代價是看不到 panel 外的訊號，所以 stage I 只有 18% sensitivity，但 stage IV 能達 93%。為什麼 cfMeDIP-seq / EM-seq / TAPS / FRAGMA 並存？因為 Galleri panel 外的 ctDNA 訊號完全看不到；cfMeDIP-seq 走全基因組免化學轉換路線，能同時看數千個甲基化區段並保留 fragment 結構；EM-seq 把 input 下限壓到 100 pg，特別適合針切、CSF、urine 這類極稀少樣本；TAPS 的 DNA 損傷最少，適合需要保留更多原始片段的應用；FRAGMA 完全跳過化學轉換、直接從 sWGS BAM 反推 methylation，可與 DELFI / GEMINI / ARTEMIS 共用同一份 BAM，是「化學成本最低」的選項。每條路線在 input 量、解析度、保留 fragment 結構、pipeline 整合度上各有 niche。

所有 methylation 分類器都共享兩個結構性失敗模式。第一是 stage I 敏感度集體偏低：stage I 腫瘤體積小、釋出 cfDNA 量極少，ctDNA 在血漿中的比例常低於萬分之一。不管 methylation 用哪條化學路線讀，能撈到的 ctDNA molecule 數本來就少，要在 1,500 個 diploid genome equivalent / mL 的限制下偵測到 stage I 訊號是個物理性瓶頸。Galleri 在試驗中 stage I 只有 18% sensitivity，真實世界更只有 8%。解決之道並非換另一種化學，而是把 methylation 與 fragmentation、CNV、end motif 等多模態整合（如 AlphaLiquid 整合 methylation + fragmentation + CNV、SPOT-MAS 整合四種特徵），讓每條 read 同時被多種訊號利用。第二是 bisulfite 降解 input：bisulfite 是強酸條件，會把 cfDNA 進一步打碎並使部分鹼基脫落，整體回收率常常不到一半。一管血只能撈到 ~1,500 個 diploid genome equivalent，bisulfite 一輪燒下來再丟掉一半以上，對 stage I 幾乎是致命的——這也是為什麼 EM-seq、TAPS、cfMeDIP-seq、FRAGMA 被陸續開發，每一條都在解決「bisulfite 把 input 燒光」這個共同弱點。

## 工具與材料清單 (Toolchain)
- **Bisulfite conversion**：用 HSO3- 強酸把未甲基化 C 變成 U，5mC 保留為 C；DNA 損傷大。
- **EM-seq**：用 TET2 + APOBEC 等酵素做等價轉換，DNA 損傷小，input 可低至 100 pg。
- **TAPS**：TET 氧化 + pyridine borane 把 5mC/5hmC 直接改寫成 T，DNA 損傷最少。
- **cfMeDIP-seq**：用抗 5mC 抗體把甲基化片段拉下來，免化學轉換、保留 fragment 結構。
- **FRAGMA**：從 sWGS 的 end motif 反推 per-region methylation，跳過所有化學/免疫步驟。
- **Galleri panel**：17.2 Mb hybrid-capture bisulfite + 139× 深度的商用多癌甲基化分類器；stage I 18%、stage IV 93%。
- **AlphaLiquid Screening**：EM-seq 整合 methylation + fragmentation + CNV 的多模態分類器。
- **DMR (differentially methylated region)**：在不同細胞型態或癌 vs 健康之間甲基化程度顯著不同的基因組區段。
- **Per-region methylation vector**：把每個 region 的甲基化比例排成的特徵向量，是分類器的輸入。
- **Multi-cancer + tissue-of-origin head**：同一個分類器同時輸出「是否癌」與「最像哪個組織」。

## 與此篇文章的關係
在《Genomic and fragmentomic landscapes of cell-free DNA for early cancer detection》這篇 Review 中，作者要說明「為什麼甲基化路線存在五條化學差異很大的方法」。這些分類器吃進 cfDNA 後用各自的化學或推論方法產出 per-region methylation 向量，餵給 multi-cancer 加上 tissue-of-origin 分類器。它們解決了「targeted panel 看不到 panel 外訊號」與「bisulfite 燒掉寶貴 input」兩種瓶頸，但 stage I 偵測率集體偏低，仍要靠多模態整合（如 AlphaLiquid、SPOT-MAS）補足。

## 已沿用 Baseline 詞彙
cfDNA, ctDNA, 甲基化, Galleri, machine learning, tissue-of-origin
