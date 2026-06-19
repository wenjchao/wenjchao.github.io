---
subitem_id: "3-E"
title: "Genome-wide somatic mutation profiling (GEMINI / Pointy 與 regional mutation frequency 模型)"
---

# Genome-wide somatic mutation profiling (GEMINI / Pointy 與 regional mutation frequency 模型)

**Subitem:** 3-E · **Slug:** `gemini-genome-wide-mutation`

## 主線
在 single-molecule (1×) WGS 條件下，捕捉跨整個基因組的體細胞突變「分布形狀」(而非個別點突變)，並用病人內部的 regional 對比扣除批次效應，做出比 targeted panel 更敏感的早期癌偵測。

## 技術解析
標準的點突變偵測需要每個位置被讀好幾次來投票，1× WGS 一個位置只被讀 1 次，根本無法確認任何單一突變是真實的。GEMINI 不去管「某個位點是不是真的突變」，改去算「整個 Mb 級 region 上，所有 reads 對齊到參考序列後不符合的位置數除以 reads 總數」——這個區域突變頻率 (regional mutation frequency) 反映的是「這塊區域的突變密度」而非個別位點。把全基因組數百個 region 的 mutation frequency 排成一條向量，就是這個人的「突變分布形狀」。為什麼這個 shape 本來就會有起伏？因為 DNA 複製越晚的區段、轉錄越沉默的區段、染色質越緊的區段，平常累積的突變率本來就比較高——複製機器在這些區段修錯機會少，DNA 損傷修復也比較弱。所以即便健康人，他全基因組的 regional frequency 也不是平的，而是有一個與 replication timing、染色質結構對齊的固定形狀。癌細胞的這些變數與健康細胞不同，regional shape 就跟著歪掉。

GEMINI 最關鍵的設計是「同一病人內部，region A 對 region B 的比值」(within-patient regional contrast)。為什麼這樣能扣掉 batch？因為不同樣本可能在不同定序儀、不同批次跑，每台機器的錯誤率不一樣；同一樣本所有 region 的觀測 frequency 會被「這台機器今天的錯誤率」等比例污染。如果直接拿病人 A 的 region X 跟病人 B 的 region X 比，machine bias 就會被誤判為癌症訊號。改用同病人 region A / region B 比值，分子分母都來自同一份 library 與同一台機器，instrument bias 在除法中被約掉，剩下的差異才是真正反映 region 之間生物學差異的訊號。為什麼這條 shape 偏移能反映癌症？因為腫瘤細胞往往加速增殖、改變表觀遺傳狀態：複製時間表變了、原本沉默的區段被打開、染色質擠壓模式不同——這些變數正好都是 regional mutation rate 的決定因子。當變數同步偏移，整條 shape 都被推，不只一個 region 動。分類器看的就是整體形狀的偏移，比單看任一個突變敏感得多。

為什麼 1× 而非 5× 或 30×？因為 GEMINI 在乎的是「每個 Mb region 上累積多少突變」，不是「某個位點到底有沒有突變」。即使 1× WGS，每個 Mb region 也能收到約一百萬個 reads，足以把該 region 的 mutation frequency 估準。把 coverage 加深到 5× 或 30×，每 region 的估計變異會再小一點，但真正的瓶頸是 batch / CHIP / 系統錯誤這類「不會因為加深就消失」的偏差。所以 GEMINI 設計成 1× 才能在不犧牲訊號的前提下把單樣本成本壓到 sWGS 等級，剛好能與 DELFI、ARTEMIS 共享同一份 BAM。為什麼 GEMINI 不直接做突變特徵 (signature)？因為 Pointy 那類 mutational signatures 告訴你「整體突變過程像哪種致癌機制（吸菸、UV、APOBEC）」，但對「region 之間的相對偏移」較不敏感。regional frequency 是另一條獨立資訊：直接捕捉染色質與複製偏移，與 DELFI 的 fragmentation profile 互補；而且 region 對 region 的比值天生適合 within-patient contrast 扣 batch。Pointy 與 GEMINI 不是替代關係，而是用不同維度解析同一份 1× WGS。

GEMINI 最常見的失敗模式都來自非腫瘤訊號的污染。第一是 CHIP：年紀大的人白血球本來就會累積一群非致癌體細胞突變 (clonal haematopoiesis)，這些白血球死亡時也會把帶有 CHIP 突變的 DNA 釋進血漿。若只看 plasma WGS，CHIP 突變會抬高某些 region 的 frequency 被誤判為癌症訊號——年齡偏差直接 inflate 假陽性。正確做法是同時對病人的白血球 (buffy coat WGS) 做一份 WGS，把 CHIP 來源的突變在 plasma signal 中扣掉。第二是 germline 與 library 錯誤：個體 inherited variation 與 PCR / 機器特定位點錯誤都會在每個 region 累積成固定的「假突變」訊號；若沒先對齊已知 germline 與系統錯誤位置進行 mask，這些 non-tumour 變異會抬高 regional frequency 扭曲整條 shape。所以 reference-based filtering + within-patient contrast + buffy coat 扣 CHIP 是三道必須同時上的關卡。

## 工具與材料清單 (Toolchain)
- **Single-molecule 1× WGS**：每位置平均只讀 1 次的全基因組定序，無法可信地呼叫單一突變但足以估計 region-level frequency。
- **Regional mutation frequency**：每個 Mb 級 region 上所有 reads 與參考序列不符合位置數除以 reads 總數，反映該區突變密度。
- **Within-patient regional contrast**：同一病人 region A / region B 比值，能在除法中約掉 instrument bias。
- **GEMINI**：用 within-patient regional mutation frequency contrast 偵測早期癌的 single-molecule WGS 方法。
- **Pointy**：從 low-coverage WGS 解 mutational signatures 的工具，捕捉整體突變過程類型。
- **Replication timing**：DNA 複製先後的時間表；late-replicating 區段累積突變率較高。
- **CHIP (clonal haematopoiesis)**：年紀大的人白血球累積的非致癌體細胞突變群；若不扣會被誤判為癌症訊號。
- **Buffy coat WGS**：對病人白血球做平行 WGS，用來扣除 CHIP 來源突變。
- **Germline variant masking**：在 regional frequency 計算前對齊已知 germline 位點做 mask，避免抬高假訊號。

## 與此篇文章的關係
在《Genomic and fragmentomic landscapes of cell-free DNA for early cancer detection》這篇 Review 中，作者要說明「為什麼放棄 deep targeted panel、改走 single-molecule WGS 反而更敏感」。GEMINI 吃進一份 1× WGS BAM 與配對 buffy coat WGS，用 within-patient regional contrast 產出一條跨基因組 mutation frequency 形狀向量，供下游分類器與 fragmentation profile 一起整合。它正是 Review 中「用 1× 訊號形狀打贏 30,000× 點訊號」的代表，解決了 batch effect 與 CHIP 兩個 targeted 法束手無策的瓶頸。

## 已沿用 Baseline 詞彙
cfDNA, ctDNA, WGS, CHIP, machine learning
