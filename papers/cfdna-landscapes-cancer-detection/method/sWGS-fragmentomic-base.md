---
subitem_id: "2-E"
title: "Low-coverage Whole-genome Sequencing (sWGS) 作為 fragmentomic 基底"
---

# Low-coverage Whole-genome Sequencing (sWGS) 作為 fragmentomic 基底

**Subitem:** 2-E · **Slug:** `sWGS-fragmentomic-base`

## 主線
用 standard PCR library prep + 1–10× shallow WGS，產出帶有原始 fragment size、end position、coverage 與 sequence 資訊的 paired-end reads，作為 DELFI、GEMINI、ARTEMIS、Griffin、CRAG、E-index 等下游分類器的「共用原料」。

## 技術解析
1× 覆蓋的意思是「如果把所有定序資料平均攤到整顆 ~3 Gb 基因組上，每個位置平均被讀 1 次」。1-2× 等於整顆基因組「每個位置只看到 1-2 條 cfDNA 片段」——少到根本沒辦法判斷單一突變真假，但意思也是你拿到了「所有位置都有資料」的全景圖。對比一下：30,000× 的 targeted 是「<0.1 Mb 內每個位置看三萬次」，sWGS 是「3 Gb 內每個位置看一兩次」，兩者面積差三萬倍、深度差兩萬倍。建庫策略是 standard PCR library prep + paired-end sequencing：同一條 cfDNA 兩端各定序一次，定序儀產出兩條 reads，比對 reference 後就知道這條 cfDNA「從哪裡開始、到哪裡結束、總長多少 bp」。為什麼這麼淺反而能比 targeted 看到更多訊號？關鍵在特徵維度的轉換——sWGS 全基因組可切成數萬個 bin，每個 bin 都能算 short:long 比值、end motif 偏好、coverage、突變頻率；任何單一 bin 訊號都很弱，但全基因組數萬個 bin 同時往同一方向偏移時，加總強度遠超 targeted 在單一位置的深度優勢。DELFI 用 1-2× 達到 NPV 99.8% (ref 128) 的根本原因就在這。

同一份 paired-end BAM 等於一份「無損原料」——每條 cfDNA 的起點、終點、長度、序列、比對位置都記下來了。不同分類器只是從同一份 BAM 抽不同特徵：DELFI (ref 47) 抽「每個 bin 的短:長片段比值」算 fragmentation profile；GEMINI (ref 60) 抽「每個 region 的突變頻率分布」；ARTEMIS (ref 67) 抽「k-mer 拼到 1,280 種 repeat element 的比例」；Griffin (ref 116) 抽「TFBS 周圍的 coverage 凹陷」；ichorCNA (ref 57) 抽「全基因組 bin coverage 推 CNV」。一管血、一份 sWGS BAM，可以同時支援 detection、tissue-of-origin、tumour fraction 三個任務，不必為每個分析重抽。這是 review 主張「先撒網、再分層」的核心優勢。

兩個地方需要在標準 sWGS 之外加選項。第一是當你想抓 35-80 bp 的超短片段——這些是轉錄因子直接保護下來的 cfDNA (ref 111)，標準雙股 PCR library prep 對這麼短的片段效率差，必須改用 single-stranded library prep：先把 cfDNA 變成單股、單股接 adapter 再回補成雙股，35-80 bp 的片段也能存活。第二是當你想看 >600 bp 的長片段或直接讀 5mC——short-read (Illumina) 一次最多解 ~600 bp (ref 90)，看不到更長的片段；Nanopore (refs 88, 89) 與 SMRT (ref 90) 兩種長讀技術可以讀 >10 kb，而且 Nanopore 讀的是 DNA 過孔時的電流變化、5mC 過孔的電流模式跟 C 不同，SMRT 讀的是聚合酶動力學、5mC 模板會讓酵素停頓——兩者都能直接從訊號偵測甲基化，不必 bisulfite。長片段帶更多 CpG，對 tissue-of-origin 推論更有利。

兩個常見坑必須避開。第一，如果做 single-end (只讀一端)，fragment 長度與另一端 motif 全部消失，DELFI 的 short:long ratio、E-index、motif diversity 都會失效——一定要 paired-end。同樣致命的是 GC bias：PCR library prep 對不同 GC 含量區段的擴增效率不同，GC 太高或太低的區段 reads 會偏少，這跟癌 vs 健康無關，純粹是 library 的事。沒做 GC bias 校正 (refs 116, 124) 時 Griffin 的 TFBS 凹陷會被 library bias 整片蓋掉，分類器學的就不是癌訊號而是 library bias。第二，input cfDNA 太少 (<1 ng) 時 library prep 必須加更多輪 PCR 補產量，結果是「原始分子很少、PCR 拷貝很多」——表面覆蓋還在，去除 PCR duplicate 後真正獨立的 cfDNA 分子數驟降。DELFI 賴的是每個 bin 有夠多獨立 fragment，一個 bin 只剩 3-5 條 unique fragment 時統計噪音會大於癌訊號偏移量；GEMINI 的 regional mutation frequency 也算不準。所以 sWGS 表面便宜，對 input 量還是有下限 (通常 ≥ 1-5 ng cfDNA)，前面 pre-analytical 沒做好，後面 ML 分類器再厲害也救不了。

## 工具與材料清單 (Toolchain)
- **sWGS (shallow / low-coverage WGS)**：1-10× 全基因組淺定序，提供整顆基因組的 fragmentomic 共用原料。
- **Paired-end sequencing**：同一條 cfDNA 兩端各定序一次，獲得起點、終點、長度與兩端序列。
- **Standard PCR library prep**：雙股 cfDNA 接 adapter + PCR 放大的標準建庫流程。
- **Single-stranded library prep (ref 111)**：先把 cfDNA 變成單股再接 adapter，可保留 35-80 bp 的 TF-保護超短片段。
- **35-80 bp TF-protected fragments**：轉錄因子直接保護下來的超短 cfDNA 片段，需 single-stranded library prep 才能保留。
- **Short-read 上限 ~600 bp (ref 90)**：Illumina 一次定序的片段長度上限，超過此長度需 long-read 平台。
- **Nanopore long-read (refs 88, 89)**：從 DNA 過孔的電流訊號直接讀出 5mC，可解 >10 kb 片段。
- **SMRT long-read (ref 90)**：從聚合酶動力學偵測 5mC，可解 >10 kb 片段。
- **Shared paired-end BAM**：同一份 sWGS 比對結果可同時餵給 DELFI、GEMINI、ARTEMIS、Griffin、ichorCNA。
- **GC bias 校正 (refs 116, 124)**：扣除 PCR 對不同 GC 含量區段擴增效率差異造成的偽覆蓋偏差；focal coverage 分析的必要步驟。
- **PCR duplicate**：同一原始分子的多份 PCR 拷貝；去除後才能算 unique fragment 數。

## 與此篇文章的關係
在《Genomic and fragmentomic landscapes of cell-free DNA for early cancer detection》這篇 review 中，作者要說服讀者放棄 targeted deep sequencing、改走多特徵 ML 路線。Low-coverage Whole-genome Sequencing (sWGS) 作為 fragmentomic 基底就是這條新路線的「共用原料」：解決了 targeted panel 只能看 <1% 基因組、且每分析都要重抽血的瓶頸。一份 sWGS BAM 同時供 DELFI、GEMINI、ARTEMIS、Griffin、ichorCNA 等多個分類器抽取 fragmentation、mutation、repeat、TFBS coverage、CNV 等異質特徵，為下游多特徵融合分類器 (例如 SPOT-MAS、AlphaLiquid) 提供 detection、tissue-of-origin、tumour fraction 三任務的單一基底。

## 已沿用 Baseline 詞彙
cfDNA, DELFI, NPV
