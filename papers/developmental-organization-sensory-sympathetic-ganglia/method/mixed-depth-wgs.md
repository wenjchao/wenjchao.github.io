# 混合深度 WGS 策略 (300× 器官 + 30× 神經節)

1. 引用自哪篇 paper: developmental-organization-sensory-sympathetic-ganglia
2. Outline (任務主線): 混合深度 WGS 策略 (300× 器官 + 30× 神經節)
3. Method:

作者要撈的 mosaic variant (MV) 在單一組織裡對偶基因頻率 (AF) 常小於 1%——意思是「100 顆細胞裡只有 1 顆有這個錯字」。想把訊號從 sequencer 噪音裡挑出來，同一個位置至少要看 100 次以上；因此全基因體定序 (WGS) 的定序深度 (coverage) 就是這個實驗最核心的資源分配問題。假設某位置真實 AF = 1%，讀 300 次時平均會有 3 條 alt read 命中，剛好卡在 caller 的 3 條 alt 最低門檻；讀 30 次時平均只有 0.3 條，多數狀況根本連一條都沒讀到。

所以作者把資源折衷成雙軌設計。每位 donor 只挑 8–17 個器官樣本 (腦、心、腎、肝) 做 300× WGS 高敏感撈 candidate MV 清單；剩下數十顆神經節則做 30× 淺度 WGS，只求「這個 MV 在這顆神經節裡有沒有讀到」的粗略證據，補上跨組織的共享 clone 分佈。若所有樣本都做 300×，光是每 library ≥120 GB output 就把預算炸掉；若都做 30×，AF <5% 的 MV 幾乎全部漏掉。300× 部隊負責「敏感撈候選」、30× 部隊負責「補充哪些神經節共享 clone」，把資源用在刀口上。

建庫的細節都是為了讓每條 read 的品質吃到底。DNA 先用 Covaris 超音波打斷到峰值約 400 bp，再用兩次磁珠篩選 (double-size selection) 保留 300–600 bp——這是 Illumina 兩端各讀 150 bp (PE150) 的甜蜜區，太短會讓兩端完全重疊浪費 read、太長則兩端跨不到而配對失敗。300× library 用 KAPA HyperPrep PCR-Free 套組略去 PCR 擴增：PCR 每輪都可能抄錯一個鹼基、產生 5–10 條帶著同一個假 alt allele 的 read，AF <1% 的真 MV 就會被淹沒。作者付出的代價是需要 1.0 μg input DNA，換來的是候選 MV 都是真訊號而非 PCR 副本。

上機時多 library 混在一 lane，需要靠條碼把 read 分回各自來源；作者用唯一雙端條碼 (UDI, unique dual index)——DNA 兩端各加一段 8 bp barcode，兩端組合唯一對應一樣本，單端出錯還能被另一端救回。同時掺 0.5–1% PhiX 這種短且鹼基平衡的病毒基因體，做 sequencer 每個 cycle 的 base-calling 校正。更關鍵的是三位 donor 的 pool 分開 lane 上機——因為即使有 UDI，index hopping (index 被 sequencer 跳錯) 仍極低機率發生。若跨 donor 混 lane，跳錯的 read 會讓「這位 donor 有這個 MV」的判斷被別位 donor 污染。分 lane 是最物理的隔離手段。最後上機以 Illumina NovaSeq 6000 S4 flowcell 跑 PE150、雙 index、Q30 >90%、每 library 目標 ≥120 GB output；原始 FASTQ 上傳 SRA PRJNA799597。

4. 工具與材料:

- **Whole-genome sequencing (WGS)**: 把 DNA 隨機打碎、上機讀取全基因體序列的方法，本研究以深度區分兩軌用途。
- **Coverage / depth (300× vs 30×)**: 每個鹼基位置平均被讀到幾次；300× 可捕捉 AF ~1% 的稀有 MV、30× 只可靠看到 AF ≥5%。
- **KAPA HyperPrep PCR-Free**: 跳過 PCR 擴增的建庫套組 (Roche KK8505)，避免 PCR 抄錯鹼基混入假 MV。
- **Covaris microtube sonication**: 以超音波把 DNA 打斷至峰值 ~400 bp 供下游 PE150 定序。
- **Double-size selection**: 用磁珠篩選片段長度 300–600 bp，落在 Illumina PE150 的最佳 insert size 區間。
- **Unique dual index (UDI)**: DNA 兩端各加 8 bp barcode 唯一對應一樣本，抵抗 sequencer 分讀錯誤。
- **PhiX**: 短且鹼基平衡的病毒基因體，摻 0.5–1% 供 sequencer 每個 cycle 的 base-calling 校正。
- **NovaSeq 6000 S4 flowcell**: Illumina 高通量定序機台；本研究以 PE150、Q30 >90%、每 library ≥120 GB output 為上機規格。
- **Index hopping**: 多 library 同 lane 上機時 index 被跳錯貼到別 library；作者以三 donor 分 lane 做物理隔離。

5. 與此篇文章的關係:

在《Developmental organization of sensory and sympathetic ganglia》這篇文章中，作者為了在 187 顆神經節加對照器官上抓 AF <1% 的稀有 mosaic variant，採用了 300× 器官 + 30× 神經節的混合深度 WGS 策略。它解決了「單一深度無法同時滿足高敏感呼叫與跨數十樣本可負擔成本」的取捨困境，為下游 MosaicHunter / DeepMosaic / MosaicForecast / Mutect2∩Strelka2 四工具聯合呼叫提供了每位 donor 2,000–3,000 個 candidate MV 的原料。
