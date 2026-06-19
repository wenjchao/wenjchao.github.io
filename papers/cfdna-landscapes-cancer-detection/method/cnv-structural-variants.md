---
subitem_id: "3-A"
title: "Genome-wide structural variants 與 CNV 量化 (Digital karyotyping / PARE / ichorCNA / plasma aneuploidy)"
---

# Genome-wide structural variants 與 CNV 量化 (Digital karyotyping / PARE / ichorCNA / plasma aneuploidy)

**Subitem:** 3-A · **Slug:** `cnv-structural-variants`

## 主線
從 low-coverage WGS 中量化染色體尺度的 gains / losses 與 rearrangements，將「染色體不平衡的程度」直接換算為 ctDNA tumour fraction，作為腫瘤負荷的 noninvasive monitor。

## 技術解析
單鹼基突變是「基因組裡某一個 letter 從 G 變 A」——尺度只有 1 個鹼基。染色體尺度的 gain / loss 則是「整段甚至整條染色體 (10⁶-10⁸ bp) 多了或少了一份」——例如許多癌細胞 chr8q 是 3-4 份 (gain)、chr17p 只剩 1 份 (loss)；rearrangement 則是「兩段本來不相鄰的 DNA 被異常接在一起」(如 BCR-ABL 融合)。這些大尺度變化在癌細胞中極常見，源頭是癌細胞分裂時染色體不穩定 (chromosomal instability)。對 sWGS 這是天賜禮物：一條 10⁸ bp 的染色體切成數千個 bin，每個 bin 都會貢獻一點點「多了或少了」的訊號；ctDNA 即便只佔 1%，數千個 bin 的弱訊號平均後就能穩定說出「這條染色體整體偏高」。單一鹼基突變沒這個放大效應——萬分之一比例的突變在 1-2× 覆蓋下就是「不存在」。

工具家族是這樣分工的。Digital karyotyping (Wang et al. 2002, ref 49) 是想法上的祖師爺——把整顆基因組切成 bin、計算每個 bin 的 read 數；某段 bin 系統性偏高 = gain，偏低 = loss。PARE (Leary et al. 2010, ref 50) 是互補路線——看 paired-end reads 裡「兩端應該相鄰但實際比對到不同染色體 (discordant)」的事件，這種 discordant pairs 直接證明 rearrangement。Plasma aneuploidy score (refs 48, 58) 進一步把全基因組染色體不平衡程度量化成單一分數。ichorCNA (Adalsteinsson et al. 2017, ref 57) 與 DELFI tumour fraction (ref 58) 再上一層——用 hidden Markov model (HMM) 同時估「ctDNA 整體比例」與「每段 bin 屬於哪個 CNV state」。HMM 的關鍵是空間 prior：它假設「相鄰 bin 通常處於同一 state」(染色體 gain/loss 是大段一起的)，藉這個平滑把上千個 bin 的弱訊號聚合成一個「這整段是 gain」的判斷，比逐 bin 算 log-ratio 抗噪能力強好幾倍。最後輸出 tumour fraction 是個 0-1 的數字：「這管血裡多少比例的 cfDNA 來自腫瘤」。

review 還強調一個常被忽略的免費 feature——粒線體 DNA 拷貝數 (mtDNA copy number, ref 54)。每顆細胞裡 nuclear DNA 是兩份，但 mtDNA 是 100-1000 份。許多癌種的 mtDNA 拷貝數會異常 (高或低跟癌種有關)，這個變化在 cfDNA 中會反映成「比對到 mtDNA 的 reads 比例異常」。對 sWGS 來說同一份 BAM 已經有 mtDNA reads，平常被忽略——DELFI (ref 47) 與 FirstLook Lung (ref 128) 把 mtDNA representation 串到 chromosomal CNV 與 fragmentation 一起當特徵，邊際成本接近零卻能稍微推高敏感度。

兩個情境會讓 CNV-based tumour fraction 失效。第一是「低 ctDNA 比例下的偵測下限」——在 ctDNA <0.5% 時，gain 區段的 log-ratio 偏移幅度只有約 ±0.005，遠小於 1× 覆蓋下單 bin 的隨機噪音 (約 ±0.1)。即便 HMM 把相鄰 bin 拉在一起平滑，整段染色體的訊號也只能勉強推到偵測門檻邊緣，ichorCNA 通常直接回報 tumour fraction = 0。所以這套方法適合 tumour fraction >3-5% 的場景 (末期癌或治療反應追蹤)，不適合早期癌篩檢的 MRD 等級 (<0.01%)——後者得靠 DELFI 多特徵融合或 GEMINI 的 regional mutation 才能撈出來。第二是「老化族群白血球 CNV」——60 歲以上常見的鑲嵌型染色體變動 (mCAs) 與男性的失 Y 會在 cfDNA 中產生跟 ctDNA 幾乎一樣的訊號，光看 cfDNA 分不出來。解法跟 CHIP 一樣——平行做病人自己白血球的 WGS、扣掉白血球已有的 CNV；否則健康年長者會被誤判為早期癌，整套篩檢在老化族群的特異度會崩。

## 工具與材料清單 (Toolchain)
- **CNV (copy number variation)**：染色體尺度上某段 DNA 被多印或少印一份的變化，是癌細胞的標誌特徵。
- **Structural rearrangement**：本來不相鄰的兩段 DNA 被異常接合 (deletion / duplication / inversion / translocation)。
- **Chromosomal instability**：癌細胞分裂時染色體常被分錯，是 CNV 普遍出現的源頭。
- **Digital karyotyping (Wang et al. 2002, ref 49)**：把基因組切 bin、算每個 bin 的 read 數來推 CNV 的方法，CNV 量化的祖師爺。
- **PARE (Leary et al. 2010, ref 50)**：用 paired-end 中 discordant reads 找腫瘤特有 rearrangement。
- **Plasma aneuploidy score (refs 48, 58)**：全基因組染色體不平衡程度的單一綜合分數。
- **ichorCNA (Adalsteinsson et al. 2017, ref 57)**：用 hidden Markov model 同時估 ctDNA 比例與每段 bin 的 CNV state；輸出 tumour fraction。
- **DELFI tumour fraction (ref 58)**：DELFI 框架下從 CNV 推 ctDNA 比例的實作。
- **Hidden Markov model (HMM)**：把相鄰 bin 當成同一 state 強迫空間平滑，聚合弱訊號的統計模型。
- **mtDNA copy number (ref 54)**：粒線體 DNA 拷貝數，sWGS BAM 中的免費額外 feature；DELFI 與 FirstLook 都採用。
- **MRD (minimal residual disease)**：治療後殘留腫瘤量極低 (<0.01%) 的偵測場景；ichorCNA 在此場景失靈。
- **Mosaic chromosomal alterations (mCAs)**：老化族群白血球常見的染色體鑲嵌變動，會在 cfDNA 中混淆 ctDNA CNV 訊號。

## 與此篇文章的關係
在《Genomic and fragmentomic landscapes of cell-free DNA for early cancer detection》這篇 review 中，作者要從 cfDNA 量化「腫瘤現在多大、有沒有在長」。Genome-wide structural variants 與 CNV 量化 (digital karyotyping / PARE / ichorCNA / DELFI tumour fraction) 這條技術家族解決的是「不需要事先知道腫瘤序列、也能用 sWGS 直接推 tumour fraction」的瓶頸，把染色體不平衡的程度換算成 0-1 的 ctDNA 比例。它為治療反應追蹤、復發監測、以及 DELFI 多特徵融合分類器提供腫瘤負荷的定量 feature；但作者也指出它對早期癌篩檢的 MRD 等級 ctDNA (<0.01%) 失靈，必須讓位給多特徵 ML。

## 已沿用 Baseline 詞彙
cfDNA, ctDNA, WGS, DELFI, fragmentation, CNV, tumour fraction
