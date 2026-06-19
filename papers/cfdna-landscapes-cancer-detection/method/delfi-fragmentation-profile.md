---
subitem_id: "3-B"
title: "DELFI 全基因組 fragmentation profile + Machine Learning 分類器"
---

# DELFI 全基因組 fragmentation profile + Machine Learning 分類器

**Subitem:** 3-B · **Slug:** `delfi-fragmentation-profile`

## 主線
把整個基因組切成 bin，計算每個 bin 內「短片段 / 長片段比值」與 coverage，形成跨基因組的 fragmentation profile，並交由機器學習辨識癌 vs 健康人之間的全基因組 chromatin / CNV 訊號差異。

## 技術解析
整套 DELFI 流程是把「血液裡漂浮的 cfDNA 長什麼樣」翻譯成分類器看得懂的數字陣列。先抽血、離心拿到血漿，用標準雙端定序 (paired-end sequencing) 對 cfDNA 做一次很粗的全基因組定序——每個位置平均只讀 1 到 2 次 (shallow WGS, 1–2× coverage)。雙端的好處是每讀一次就同時知道一段 cfDNA 的兩端落點，能直接量出這段碎片的長度。接著把整個基因組切成大小固定的格子 (genome-wide bins，DELFI 預設約 5 Mb 一格)，計算每格兩件事：碎片總共有幾條 (coverage)、其中「短片段 (約 100–150 bp) 對長片段 (約 151–220 bp) 的比值」是多少 (short:long fragment ratio)。為什麼用比值而不用平均長度？因為比值能自動把不同樣本間的 coverage 差異消掉，又能把「染色質打開、碎片變短」這種結構性訊號放大兩次。為什麼一定要切格子？因為全基因組總體的單一數字會把所有區段差異平均掉；切成幾百個格子之後，每格的微弱偏移獨立保留，整條向量就會出現可辨認的形狀。再把染色體大段的拷貝數增減 (chromosomal CNV) 與粒線體 DNA 相對量 (mtDNA representation) 串進去，整個向量丟給機器學習，由分類器輸出「健康 vs 癌症」的機率。

這套方法的生物機制根植於細胞核裡 DNA 的擺放方式。DNA 並不是攤平的，而是一段一段繞在一顆顆名為 nucleosome 的小蛋白線軸上：繞上去的 147 個鹼基被線軸蓋住，外面的酵素切不到，只有兩顆線軸之間裸露的縫隙才會被切斷。所以血液裡撿到的碎片大多剛好等於「一個線軸 + 一段縫隙」的長度，約 167 bp。染色質被打開的區段，線軸排列被擠亂、DNA 更暴露，碎片被切得更短、總量也下降；染色質緻密的區段，線軸整齊排列，碎片保持完整、長度集中在 167 bp。癌細胞與健康細胞的染色質「哪裡開、哪裡關」分布不同，反映在血液碎片上就是「哪些格子變短、哪些格子變長」。這也是為什麼健康人的 fragmentation profile 會與淋巴球酵素消化模式 (lymphocyte nuclease digestion) 以及大尺度染色質結構圖 (Hi-C open/closed compartments) 高度相關——血液碎片本身就是一份染色質擺位的拓本。除此之外，染色體大段的拷貝數增減 (chromosomal CNV) 與粒線體 DNA 相對量 (mtDNA representation) 是另外兩條獨立的癌症線索：CNV 會讓對應格子的 coverage 同步抬高或壓低，mtDNA 在許多癌種拷貝數會變動。把這兩個特徵和短：長比一起串進向量，等於同時告訴分類器表觀與基因兩個層面的證據，即便某種癌的染色質訊號很弱，CNV 也能補位。

為什麼是 1–2× 這種淺到不行的 WGS 而非深定序？因為 DELFI 的訊號不是「某個位點有沒有突變」，而是「上百個格子的形狀對不對」。每個 5 Mb 格子在 1–2× 下也能收到幾千條片段，足以把短：長比與 coverage 平均成穩定數字；把 coverage 加深到 30×，每格數字只會精準一點點，但成本翻 15 倍——對「最後拿幾百個格子加總形狀」這件事是極低邊際效益的浪費。反過來，篩檢場景必須對應大量無症狀健康人，每次檢測成本必須壓低才能擴張；1–2× sWGS 用一般 PCR-based library prep 就能完成，沒有特殊酵素也沒有 hybrid capture，是「能擴張到全民篩檢」的等級。為什麼一定靠機器學習？因為健康人之間短：長比本來就有不小的個體差異，任何單一格子的偏移大多還在健康人變異範圍內，設固定門檻會抓到一堆假陽性。癌症真正的訊號是「上百個格子同時微微偏向某方向」，這種組合形狀沒辦法用單一門檻描述，必須用 ML 同時看上百個維度、再加上 CNV 與 mtDNA 自動加權整合，學出能分隔健康與癌症的分類超平面。

這套方法最常見的兩個壞掉方式都跟「資料品質」而非演算法本身有關。第一，pre-analytical 污染：cfDNA 一離開細胞就極脆弱，採血管放太久、運送溫度不對、離心速度不夠，白血球會在管內裂解，把它們自己的長段基因組 DNA 倒進血漿，同時釋出的酵素還會把原本完整的碎片繼續切短。兩件事都會歪掉短：長比，分類器在訓練集上學到的判別面，到新 cohort 會被批次差異整個推偏，AUC 崩盤。所以標準作業要求 EDTA 採血管、4 小時內完成雙離心，把這條雜訊源關掉。第二，訓練 cohort 偏差：如果只用已被確診（多為晚期、ctDNA 比例高）的病人 vs 健康捐血者當訓練集，分類器很容易學到「強訊號 + 採樣流程差異」這種假特徵；到真實篩檢面對無症狀早期癌，ctDNA 比例可能低到萬分之一以下，原本的判別面看不見這麼弱的訊號。這就是為什麼 FirstLook Lung 必須在 958 人前瞻 case-control 上重訓並驗證，最終達到陰性結果可信度 (NPV) 99.8%、整體 sensitivity 80%、specificity 58% 才被視為臨床可用。

## 工具與材料清單 (Toolchain)
- **Shallow WGS (1–2×)**：對 cfDNA 做極淺的全基因組雙端定序，每位置只讀 1–2 次，足以支撐 bin-level 統計。
- **Paired-end sequencing**：同一條 cfDNA 的兩端都被讀出，能直接還原片段長度。
- **Genome-wide bins**：把整個基因組切成數百個約 5 Mb 的固定格子，每格獨立計算特徵。
- **Short:long fragment ratio**：每個 bin 內短片段 (~100–150 bp) 對長片段 (~151–220 bp) 的比值，對 chromatin 開放狀態敏感。
- **Coverage**：每個 bin 內 cfDNA 片段的總條數，會被 CNV 與 chromatin 開放同時影響。
- **Fragmentation profile**：將所有 bin 的短：長比與 coverage 拼成的全基因組碎片整體分布圖。
- **Chromosomal CNV**：染色體大段的拷貝數增減，可從 bin-level coverage 直接讀出。
- **mtDNA representation**：粒線體 DNA 在 cfDNA 中的相對量，許多癌種會改變此比例。
- **Hi-C open/closed compartments**：將染色體分成「打開 / 關起來」兩種空間區塊的染色質結構圖。
- **Lymphocyte nuclease digestion**：用淋巴球被酵素消化後的片段分布當健康參照，驗證 DELFI 訊號的生物合理性。
- **Machine learning classifier**：多維度模型整合上百個 bin + CNV + mtDNA 特徵，輸出癌 vs 健康機率。
- **FirstLook Lung**：DELFI 家族商業化的肺癌前篩血液檢測；前瞻 case-control (n=958) 全期 sensitivity 80%、specificity 58%、NPV 99.8%。
- **NPV**：陰性結果可信度——測陰性者真的沒癌的比例；FirstLook Lung 達 99.8%。

## 與此篇文章的關係
在《Genomic and fragmentomic landscapes of cell-free DNA for early cancer detection》這篇 Review 中，作者要為「血液篩癌如何突破 targeted panel 天花板」找出可行路徑。DELFI 正是 Review 推崇的代表方法：吃進一份 1–2× shallow WGS 的 paired-end BAM，產出一條跨基因組 bin 的 short:long ratio + coverage + CNV + mtDNA 特徵向量，交給機器學習分類器。這套設計解決了 targeted panel「只看 <1% 基因組」與「無法整合 chromatin 訊號」的瓶頸，並把產出餵給下游 FirstLook Lung 等臨床分類器使用。

## 已沿用 Baseline 詞彙
cfDNA, ctDNA, nucleosome, low-coverage WGS, fragmentation profile, DELFI, FirstLook, NPV
