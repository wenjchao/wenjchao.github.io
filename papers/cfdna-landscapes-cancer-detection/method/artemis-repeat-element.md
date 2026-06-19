---
subitem_id: "3-F"
title: "Repeat element landscape — ARTEMIS k-mer alignment-free framework"
---

# Repeat element landscape — ARTEMIS k-mer alignment-free framework

**Subitem:** 3-F · **Slug:** `artemis-repeat-element`

## 主線
繞過短讀無法唯一比對至重複序列的根本限制，改以 ~1.2 billion 個能唯一識別 1,280 種 repeat element 的 k-mer，從 standard WGS 計算 cfDNA 中重複元件的全局豐度變化，作為 chromatin / 結構變異的 surrogate feature。

## 技術解析
ARTEMIS 整個流程跳過傳統 align-to-genome 那一步。為什麼必須跳過？因為重複序列是同一段 DNA 模板在基因組裡複製貼上幾百到幾千份，一條 150 bp 的短讀若落在這種模板裡面，與所有複本完全一樣相符，比對軟體無法決定它真的來自哪一份，會回報「multi-mapping」並把 mapping quality 標為 0，下游分析通常直接丟掉。長讀雖能跨越整段重複，但 cfDNA 本身就是 ~167 bp，長讀根本派不上用場。ARTEMIS 改走 alignment-free k-mer 路線：第一步先離線建好辭典——從 reference 上每一型 repeat 的代表序列中，挑出「只在這一型 repeat 才會出現」的長度為 k 的小字串 (k-mer)，1,280 種 repeat 累積出大約 12 億個唯一識別 k-mer。第二步是線上掃描：拿一份標準 WGS 的 cfDNA reads，不做 alignment，直接逐條 read 拆成 k-mer 比對辭典——每個 k-mer 出現一次就計一票，最後把同屬一型 repeat 的票數加總、用 reads 總數正規化，就得到一個 1,280 維的 repeat 豐度向量。第三步把這個向量丟給機器學習，輸出癌 vs 健康加上 tissue-of-origin。

為什麼 cfDNA 中 repeat element 的相對豐度會在癌症中改變？重複序列在細胞裡身負三個與癌症高度相關的角色：第一，衛星 DNA 主要分布在染色質緻密區 (heterochromatin)，當腫瘤把這些區段打開或鎖住，cfDNA 上相對應的 repeat 豐度就會升降；第二，LINE-1、Alu 等重複元件是結構變異 (structural variation) 的熱點，重組與插入會直接改變這些 repeat 的拷貝數；第三，腫瘤常出現整體 DNA 去甲基化，原本被甲基化壓制的 LINE-1 / LTR 反活化、相對 representation 上升。所以 repeat 豐度向量同時是「染色質 + 結構變異 + epigenetic」三條訊號的混合代理 (surrogate)。為什麼也能做 tissue-of-origin？因為不同組織的染色質結構與 DNA 甲基化模式各有自己的「重複序列開合譜」——肝細胞與肺上皮細胞在 LINE-1、Alu、衛星 DNA 上的相對豐度本來就不同。當腫瘤把某個組織的細胞死亡量推高，那個組織的特有 repeat fingerprint 就會被放大進 cfDNA，多癌訓練後同一個分類器 head 可以同時輸出「是否癌」與「最像哪個組織的指紋」。

為什麼選擇 unique k-mer 而不是直接比對整段 repeat 模板？如果用整段模板，比對結果還是會 multi-map，因為模板在基因組各處都有複本。改用 unique k-mer 等於 in-silico 篩出一群「只出現在這型 repeat、不出現在任何其他位置」的小字串——掃描時只需做字串比對 (string match)，不需要考慮對齊到哪條染色體；只要 read 裡出現任何一個專屬 k-mer 就能放心歸到該 repeat type，把「無法比對」的根本難題轉成「字典查詢」。為什麼辭典做到 1.2 billion 個 k-mer 這麼大？因為 1,280 種 repeat 的家族與亞家族內部本身有序列變異，每一種變體都要被涵蓋；同時每個 k-mer 又必須通過「全基因組唯一」這個嚴格檢查。要在不犧牲唯一性的前提下涵蓋所有亞型的所有變體，自然需要極大量的 k-mer——12 億是這三個約束（唯一性、亞型覆蓋率、k 長度選擇）平衡後的結果。

k-mer 字串比對對單一鹼基錯誤很敏感：一條 read 上有一個錯字，那段對應的 k-mer 就不再匹配辭典，這個 repeat type 的計數就少一票。ARTEMIS 在每條 read 上會抓多個 k-mer，加上幾億條 reads 平均下來，個別錯字損失會被平均掉。但若整體 sequencing error rate 升高（某批 library 品質差），整片 repeat 計數會被同步壓低，分類器把它誤判為「該 repeat 表現量低」——所以 quality filtering、估計每批 library 的 error rate 不可省。第二個失敗模式是 CNV 與 repeat 訊號混淆：腫瘤的染色體大段拷貝數增減會直接讓某些重複序列豐富區段的拷貝數變多或變少，連帶推高或壓低該 repeat type 的 k-mer 計數。如果 ARTEMIS 只看 repeat representation 而不知道 CNV，會把 CNV 造成的機械性偏移誤判為染色質或 epigenetic 改變。實務上必須與 ichorCNA / DELFI tumour fraction 等 CNV 估計一起進入分類器，或在 repeat 計數中先做 CNV 校正——否則 multi-cancer 訊號中很大一部分其實只是 CNV 在說話。

## 工具與材料清單 (Toolchain)
- **ARTEMIS**：Alignment-free k-mer 框架，從 standard WGS 計算 1,280 種 repeat element 的相對豐度。
- **k-mer**：長度為 k 的 DNA 小字串，是 ARTEMIS 字典與比對的基本單位。
- **Alignment-free**：不需先比對到參考基因組，改用字串字典查詢繞開 repeat region 的 multi-mapping 難題。
- **Unique k-mer dictionary (~1.2 billion)**：in-silico 篩出只出現在特定 repeat type 的 k-mer 集合，是 ARTEMIS 的核心辭典。
- **Repeat element types (1,280)**：ARTEMIS 能解析的重複序列分類規模。
- **LINE / SINE / LTR / 衛星 DNA**：主要 repeat 家族；分別與結構變異、轉錄活性、heterochromatin 連動。
- **Structural variation surrogate**：ARTEMIS 的 repeat 偏移可間接反映 SV，因 LINE-1 / Alu 為 SV 熱點。
- **CNV co-feature**：與 ichorCNA / DELFI tumour fraction 等 CNV 估計一起進入分類器，避免 repeat 偏移被 CNV 偽訊號污染。

## 與此篇文章的關係
在《Genomic and fragmentomic landscapes of cell-free DNA for early cancer detection》這篇 Review 中，作者要說明「為什麼 cfDNA 半個基因組都是重複序列卻長期被忽略」。ARTEMIS 吃進同一份標準 WGS BAM，用 ~12 億個 unique k-mer 字典產出 1,280 維 repeat 豐度向量，提供給多癌篩檢分類器與 tissue-of-origin head。它解決了短讀無法唯一比對重複區段這個根本限制，把先前被丟棄的「半個基因組」訊號搶回來，與 DELFI、GEMINI 在同一份 BAM 上共用、互補。

## 已沿用 Baseline 詞彙
cfDNA, WGS, machine learning, tissue-of-origin
