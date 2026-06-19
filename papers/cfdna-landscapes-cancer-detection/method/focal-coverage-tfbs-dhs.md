---
subitem_id: "3-C"
title: "Focal coverage 分析於 TFBS / DHS / nucleosome-depleted regions (Griffin / LIQUORICE / Ulz / Bae)"
---

# Focal coverage 分析於 TFBS / DHS / nucleosome-depleted regions (Griffin / LIQUORICE / Ulz / Bae)

**Subitem:** 3-C · **Slug:** `focal-coverage-tfbs-dhs`

## 主線
從 sWGS 在數百到數千個 cell-type-specific regulatory site 上聚合 coverage 與 size，反推癌細胞 (或其組織起源) 的 transcription factor binding 與染色質開放狀態，使分類器能同時做 detection 與 tissue-of-origin。

## 技術解析
Focal coverage 方法都從一份 1–10× sWGS 出發。先挑一群「同類型」的調控位點，例如某個轉錄因子的數千個結合位點 (transcription factor binding sites, TFBS) 或 DNase I 敏感區 (DNase I hypersensitive sites, DHS)；對每個位點取中心向左右各 ±2 kb 的窗口，計算每個位置上 cfDNA 片段的覆蓋數 (coverage)。把成千上萬個位點的曲線「對齊中央」後相加平均，就得到一條 composite coverage profile：兩側是平均背景，中央會凹下去——因為 TF 蛋白卡在 DNA 上保護中央那一小段不被酵素切，橫跨中央的長片段變少。凹陷的深度與寬度就告訴你「這個 TF 在貢獻 cfDNA 的細胞裡有沒有正在結合」。為什麼非疊不可？因為每個 TFBS 在 sWGS 下平均只被幾條 cfDNA 片段碰到，單看一個點全是雜訊，疊上千個位點後系統性 dip 才會浮出。

為什麼 TF 卡在 DNA 上會讓中央 coverage 凹下去？活躍中的 TF 會把原本可能蓋上的 nucleosome 擠開，形成「線軸排不下去的小開窗 (nucleosome-depleted region, NDR)」，自己再佔在 DNA 上阻擋酵素接近——結果橫跨 TFBS 中心的長片段難以被產生，中央窄帶 coverage 下降。為什麼這個訊號能做 tissue-of-origin？因為每種細胞各自有一組「我這型細胞才會打開的調控位點」：當這些細胞死亡釋出 cfDNA 時，會把「自己的 TF dip 簽名」一起帶到血液裡。健康人血液主要來自白血球，所以白血球專屬位點的 dip 最深；若某病患血漿中肝細胞專屬 TF 位點的 dip 突然變深，就指向腫瘤可能在肝。小細胞肺癌 (SCLC) 案例就用 ASCL1 這個神經內分泌 TF 的 ~13,000 個結合位點分辨 SCLC vs NSCLC——同樣是肺癌，dip 形狀完全不同。

Griffin / LIQUORICE 都把 GC bias correction 列為必做步驟，原因是 PCR-based 建庫對 GC 含量太高或太低的區段有放大或壓低 coverage 的系統偏差——這是機器偏差，不是生物訊號。TFBS 與 NDR 經常坐落在 GC 含量特殊的區段，若不先校正，分類器看到的 dip 有可能其實是 library 的 GC 凹陷，與 TF 結合無關。為什麼非選 NDR / DHS / TFBS 而非隨機位點？因為隨機位點上每種細胞的 nucleosome 與 TF 分布大同小異，疊起來會是一條平坦線，分類器抓不到差異。NDR / DHS / TFBS 是「不同細胞才會打開的開關熱點」，dip 的深淺直接與「這型細胞活不活躍」掛勾。Bae et al. 進一步把 NDR 上的 coverage、size、mutation 三種特徵一起整合，就是因為 NDR 上同時帶有「染色質開合 + 突變偏好」兩條獨立訊號。

Focal coverage 方法雖然訊號性質乾淨，但每個位點只佔基因組極小一塊，所有 TFBS 加起來也僅用到全部定序資料的不到 1%。早期癌 ctDNA 比例可能低到萬分之一以下，dip 的變化幅度也跟著縮到接近雜訊邊緣。所以作者明白指出 focal coverage 不適合單獨拿來偵測，要與全基因組方法 (例如 DELFI 的 bin-wise fragmentation profile、GEMINI 的 regional mutation frequency) 搭配，才能補上 sensitivity 的缺口。另一個常被忽略的失敗模式是建庫方式：TF 直接保護的核心片段往往只有 35–80 bp，標準雙股 library prep 經常把這些超短片段丟掉。若想用 dip 的精細形狀辨識 TF 是否真的結合，必須改用單股 library prep (single-stranded library prep)，否則 dip 會被中等長度 cfDNA 洗成模糊凹槽。

## 工具與材料清單 (Toolchain)
- **TFBS (transcription factor binding site)**：轉錄因子在 DNA 上的結合位點，活躍時中央 coverage 會凹陷。
- **DHS (DNase I hypersensitive site)**：對 DNase I 特別敏感的染色質開放區，反映 cell-type-specific 開關位點。
- **NDR (nucleosome-depleted region)**：線軸排不下去的小開窗，是 TF 結合與調控發生的場域。
- **Composite coverage profile**：把成千上萬個同類位點的 coverage 曲線對齊相加得到的平均凹陷曲線。
- **Griffin**：TFBS coverage 分析工具，內含 GC bias 校正，適用多癌種。
- **LIQUORICE**：聚焦 DNase I 敏感區的 cfDNA coverage 分析工具，曾用於 Ewing sarcoma 兒科應用。
- **GC bias correction**：校正 PCR 建庫對 GC 含量極端區段的覆蓋偏差，避免被誤判為生物 dip。
- **ASCL1**：小細胞肺癌的神經內分泌譜系標誌 TF；用 ~13,000 個 ASCL1 結合位點即可分辨 SCLC 與 NSCLC。
- **Single-stranded library prep**：能保留 35–80 bp 超短片段的建庫方式，TFBS dip 精細形狀需要這類超短片段才能呈現。
- **Bae et al. NDR integration**：將 NDR 區域的 coverage、size、mutation 三特徵一起整合的分類策略。

## 與此篇文章的關係
在《Genomic and fragmentomic landscapes of cell-free DNA for early cancer detection》這篇 Review 中，作者要為多癌篩檢找出能同時做 detection 與 tissue-of-origin 的特徵。Griffin / LIQUORICE / Ulz / Bae 系列方法吃進同一份 1–10× sWGS BAM，在數千個 cell-type-specific TFBS / DHS / NDR 上聚合 coverage 得到 composite dip 曲線，產出一組「哪種細胞活躍」的指紋向量，提供給下游多模態分類器與 tissue-of-origin head。它補足了 DELFI 全基因組 fragmentation profile 看不見的「細胞身分」維度。

## 已沿用 Baseline 詞彙
cfDNA, ctDNA, nucleosome, sWGS, tissue-of-origin, machine learning
