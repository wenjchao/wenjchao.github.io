# pGL transfer vector 與 CRS library 構築

1. 引用自哪篇 paper: chromatin-structure-regulatory-activity
2. Outline (任務主線): pGL transfer vector 與 CRS library 構築
3. Method: 
   供體質體 (transfer vector) 的核心結構是 `loxFAS — CRS — Hsp68 最小啟動子 — dsRed (cBC 藏 3' UTR) — loxP`。兩端的 loxFAS 與 loxP 跟染色體上的插座配對，方便 Cre 把整段塞進去。中間是要測的 CRS 開關，下游接一段最小啟動子 (Hsp68 minimal promoter)——這是一段「自己幾乎開不起來，需要上游 CRS 點亮才轉錄」的微弱啟動子；若改用 CMV 這種強啟動子，dsRed 訊號會主要由啟動子貢獻，CRS 強弱差異就被淹沒。再下游是紅色螢光報導蛋白 (dsRed)，其 mRNA 3' UTR 裡藏著一個 CRS 身分條碼 (cBC)，定序時就能知道讀到的訊號來自哪款 CRS。骨架是 pGL4.23 質體。CRS 池本身由 Agilent 用微陣列 (microarray) 化學合成——同一片晶片上同時合成幾千條 130 bp DNA，每條序列由使用者各自指定；合成完後從晶片洗下成混合池，以方向專一性選殖 (directional cloning) 透過 XhoI / AgeI 切位一次塞進 transfer vector 的固定位置。

   兩個位置安排值得細看：(1) cBC 為什麼藏在 dsRed 的 3' UTR？因為 cBC 必須跟著 mRNA 一起被定序出來，又不能破壞別的功能——3' UTR 在轉錄起始之後（保證被讀到）、又不在 ORF 內（不會把條碼翻譯成胺基酸干擾 dsRed 折疊）、也不在 5' UTR（不會卡住核糖體啟動位置）。3' UTR 本身就是 mRNA 上「給註釋用」的空白區，剛好適合塞身分條碼。(2) CRS 為什麼用 XhoI + AgeI 兩種不同切位而不是同款酶兩端切？因為很多 enhancer 對方向其實敏感，若同款切位讓 CRS 可正可反插入，同一個 cBC 對應的 CRS 一半正向一半反向、訊號被洗成糊。兩種不同酶產生不同黏端，CRS 只能以唯一方向裝進去。

   為什麼每個 CRS 配 25 個獨立 cBC？因為單一 cBC 的訊號會被各種雜訊放大：PCR 擴增可能把某個 cBC 撈到爆量 (PCR jackpot)、某顆細胞剛好轉錄爆發、條碼可能被定序漏掉等等。25 個獨立 cBC 等於同一個 CRS 被 25 個獨立樣本同時測量，最後取平均，雜訊在數學上縮小 $\sqrt{25} = 5$ 倍——這正是 replicate R 能推到 0.66 的關鍵保險。如果只配一個 cBC，雜訊原封不動直接出現在 CRS 估計值上，replicate R 會跌到接近 0、整篇結論做不出來。

   第一代 310 個 CRS 不是亂挑，而是從 Kwasnieski et al. 2014 Genome Res. 的 episomal MPRA 資料中精選——只取「重複測量誤差 s.e.m. < 0.1」的高再現性元件，再依 ENCODE 染色質片段註釋 (Hoffman 2013, Ernst & Kellis 2012 ChromHMM) 分為強增強子、弱增強子、被抑制區三類，每類分高低活性兩亞群 + control。第二代再做三件事的同步替換來驗證結論的普遍性：(1) 從 K562 gDNA 直接 PCR 擴 13 個文獻已驗證的全長 enhancer (LP34–LP59) 進來；(2) 在 reverse primer (LP82–LP85) 上加 10-bp barcode 切換 Hsp68 與 MinP 兩款 minimal promoter；(3) 同步驗證 modularity 是否仍成立。組裝改用 NEB HiFi DNA Assembly（Gibson Assembly 改良版，利用 5' 外切酶 + 同源末端重疊一管把三段以上 DNA 無痕拼接），效率比傳統限制酶切-連接高很多。
4. 工具與材料: 
   - **pGL4.23 transfer vector**: 供體質體骨架；核心結構 `loxFAS — CRS — Hsp68 — dsRed(cBC) — loxP` 透過 NheI/BamHI 次選殖入內。
   - **Hsp68 / MinP minimal promoter**: 兩款最小啟動子，自己幾乎開不起來、需要上游 CRS 點亮才能轉錄；第二代以末端 barcode 切換驗證 modularity 不受 promoter 種類影響。
   - **dsRed reporter**: 紅色螢光蛋白，作為 CRS 活性的轉錄產物讀數；mRNA 3' UTR 內藏 cBC。
   - **cBC (content barcode)**: CRS 身分條碼，藏在 dsRed mRNA 3' UTR；每個 CRS 配 25 個獨立 cBC 以平均掉 PCR/定序雜訊。
   - **Agilent OLS oligo pool**: 微陣列化學合成的 130-bp 客製化 DNA 池，一次平行合成數千條 CRS 候選序列。
   - **Directional cloning (XhoI / AgeI)**: 兩種不同限制酶切位產生不同黏端，強迫 CRS 以唯一方向插入 transfer vector，避免反向插入造成的訊號雜訊。
   - **NEB HiFi DNA Assembly**: Gibson Assembly 改良版，利用 5' 外切酶 + 同源末端重疊一管完成多片段無痕拼接；第二代多片段組裝用。
5. 與此篇文章的關係: 
   在《A massively parallel reporter assay dissects the influence of chromatin structure on cis-regulatory activity》這篇文章中，作者要平行測幾百個 CRS 在多個位置的活性，因此需要一批可被 Cre 一次塞進 landing pad 的供體質體。本步驟以 pGL4.23 為骨架，用 Agilent 微陣列合成 130-bp CRS 池並各配 25 個 cBC，解決了「如何同時準備幾百條帶身分標籤、可定向置換的 CRS reporter」的瓶頸，產出 transfer vector library，作為下一步 Cre 介導 cassette exchange 的彈藥。
