---
subitem_id: "3-D"
title: "Fragment end position / end motif 分析 (E-index / GALYFRE / Jiang / motif diversity score)"
---

# Fragment end position / end motif 分析 (E-index / GALYFRE / Jiang / motif diversity score)

**Subitem:** 3-D · **Slug:** `fragment-end-position-motif`

## 主線
統計 cfDNA 末端落點與末端 4-mer 序列偏好的全基因組分布，捕捉與 DNA methylation、gene expression、nuclease 活性連動的 fragment-end 訊號，作為甲基化的 surrogate。

## 技術解析
從一份 sWGS paired-end BAM 出發，每段 cfDNA 兩端的座標都被讀出來了。第一個訊號叫片段末端在基因組的座標 (fragment end position)：把所有 reads 的「端點落點」加總，就得到「剪刀在哪裡剪得特別頻繁」的分布圖。第二個訊號叫末端 4-mer motif：抓每段末端 4 個鹼基（例如 `CCCA`、`CGTA`），4 個鹼基共 256 種組合，計次後算頻率分布。motif diversity score 是把 256 種 motif 的分布變化用 Shannon-like 公式壓成一個純量，分布越集中、分數越低；E-index 與 GALYFRE 進一步把端位與 motif 偏好整合進癌 vs 健康分類。為什麼這些末端訊號不是雜訊？因為 cfDNA 不是 DNA 自己斷掉的，而是被體內幾種特定的核酸酶（例如 DNASE1L3、DFFB）切出來的；每一種酶都有自己「愛切的位置」——有的偏好兩顆 nucleosome 中間的 linker、有的偏好某種鹼基組合旁邊。癌症病人因為細胞凋亡途徑改變、酶活性比例改變、染色質可及性改變，整個拓本會系統性偏移。

為什麼 end motif 能當 DNA methylation 的 surrogate？DNA 甲基化 (5mC) 直接坐在某些 cytosine 上，會改變那段 DNA 與切 cfDNA 的核酸酶之間的化學作用力——某些含 CpG 的 4-mer 在高度甲基化區段比較常被選為切點。再者，甲基化高的區段通常 nucleosome 排得更緊、染色質更壓縮，這也會改變切點落點偏好。換句話說，「end motif 的整體分布」其實偷偷攜帶了「附近的甲基化狀態」資訊。FRAGMA 與 Noë et al. 就是反向利用這個關聯，用機器學習從 end motif 頻率直接迴歸出甲基化等級，整個流程避開了 bisulfite 化學步驟、不會把寶貴的 cfDNA 燒掉。motif diversity score 在肝癌 (HCC) 升高也是同樣邏輯的延伸：健康人血漿主要由 DNASE1L3 這支「挑食」的酶切 cfDNA，末端 4-mer 集中在少數幾種組合；HCC 病人肝細胞受損、DNASE1L3 表達下降，其他「不太挑食」的酶補位上場，把切點打散到各種 motif 上，256 種組合的分布變得更均勻，diversity 隨之升高。

為什麼要用 motif diversity score 這種「壓成一個數字」的指標，而不是直接餵 256 個 motif 頻率？因為每個樣本能撿到的 cfDNA 條數有限，罕見 motif 出現頻率忽高忽低、容易讓分類器學到雜訊或批次差異。把分布均勻度用 Shannon-like 公式壓成純量後，個別罕見 motif 的浮動相互抵消，只留下「整體偏好是集中還是散開」這個穩定訊號——剛好與 DNASE1L3 活性是否被取代直接掛勾。GALYFRE 進一步把端位與 motif 結合，原因是這是兩條獨立的生物訊號：端位告訴你「剪刀偏好在哪個座標下手」，反映染色質結構與 nucleosome 排列；motif 告訴你「剪刀偏好旁邊是哪種鹼基」，反映切酶本身的序列偏好。同時用「位置線索」與「序列線索」雙重判讀，10 癌種分類 sensitivity 比單獨用一種高很多。

end motif 與切點不平整 (jaggedness) 量的就是「最末端那幾個鹼基的細節」，這恰好是 ex-vivo 任何額外酶活性最先污染的訊號。採血後若離心延遲、溫度過高、運送時間長，白血球釋出的酶會把原本完整的 cfDNA 末端再啃一次，整個 motif 譜和 jaggedness 分布就被推偏。所以這類 metric 在跨 cohort 比較時動不動就崩盤——作者明確警告這是 fragment-end 方法目前最大的弱點，必須依賴一致的 pre-analytical SOP 與酶活性更穩的訊號搭配使用。另一個尚未解決的問題是生物機制：在人類癌中「motif 譜改變到底有幾成來自酶活性改變、幾成來自染色質結構改變、幾成來自細胞來源改變」目前仍未完全釐清，分類器背後的生物變數其實是混合的。臨床部署時還必須搭配可解釋性更高的 feature 做交叉驗證。

## 工具與材料清單 (Toolchain)
- **Fragment end position**：cfDNA 末端在基因組的座標分布，反映 nuclease 切點偏好與 chromatin 結構。
- **End 4-mer motif**：cfDNA 末端 4 個鹼基的序列組合，共 256 種，反映切酶序列偏好。
- **Motif diversity score**：把 256 種 motif 的分布用 Shannon-like 公式壓成一個純量，HCC 中升高。
- **E-index**：多癌種端位偏好指數。
- **GALYFRE**：把 end position 與 end motif 結合的 10 癌種分類器。
- **FRAGMA**：從 end motif 反推 methylation 等級的工具，避開 bisulfite 化學步驟。
- **Jaggedness**：切點不平整度，量的是 cfDNA 末端兩股是否齊頭。
- **DNASE1L3**：健康人血漿中主要切 cfDNA 的「挑食」核酸酶；HCC 中其表達下降。
- **Pre-analytical SOP**：採血、離心、運送、儲存的標準作業流程；對 end motif / jaggedness 影響極大。

## 與此篇文章的關係
在《Genomic and fragmentomic landscapes of cell-free DNA for early cancer detection》這篇 Review 中，作者要為「不想做 bisulfite 也能讀到甲基化」的多癌篩檢場景找出替代特徵。Fragment end position 與 end motif 系列方法吃進同一份 sWGS BAM，產出 256-dim motif 頻率、端位分布與 motif diversity score，餵給 E-index、GALYFRE、FRAGMA 等分類器。它把甲基化、染色質、nuclease 活性多重生物訊號濃縮成 fragment-end 統計量，但對 pre-analytical 處理極度敏感的弱點也被作者反覆警告。

## 已沿用 Baseline 詞彙
cfDNA, ctDNA, 甲基化, nucleosome, sWGS
