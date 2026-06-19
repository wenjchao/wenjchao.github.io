# iPSC 維持與心肌定向分化

1. 引用自哪篇 paper: engineered-cardiac-tissue-rcm
2. Outline (任務主線): iPSC 維持與心肌定向分化
3. Method: 

iPSC 平常住在「無 feeder 化學定義」的維持環境裡——mTeSR Plus (Stem Cell Technologies) 是專為人類 iPSC 設計的維持培養基，配上 Matrigel (Corning 354230) 鍍盤當基底膜替代品，讓細胞貼著生長。約每 4–6 天細胞長到 70% 滿盤時，用 0.5 mM EDTA 把細胞間的鈣依附鬆開做傳代。分化前 2 天先把 2 × 10⁶ 顆細胞鋪到 6-well 重整密度，再進入分化主軸：沿用 Burridge 等人 2014 年發表在 Nature Methods 的化學定義分化法。「化學定義」的意思是培養基每個成分都是明確化學物質、不含批次差異很大的血清，這樣每次分化結果才能重現。心肌定向的核心是時序性操弄 Wnt 訊號通路：先短暫用 CHIR99021 (Tocris #4423) 開啟 Wnt 把 iPSC 推往中胚層，過幾天再用 Wnt-C59 (Tocris #5148) 抑制 Wnt 把中胚層細胞推往心臟前體，最後讓細胞自然成熟為會自發跳動的心肌。底盤培養基 CDM = RPMI1640 + 白蛋白 + 抗壞血酸；到 Day 10 細胞開始自發跳動時切換為 RPMI1640 + B27 滋養液。

Day 10 已經跳動的心肌，作者再加 2 µM CHIR99021 做一次擴增，借用的是 Buikema 等人 2020 發表在 Cell Stem Cell 的策略。iPSC-CM 一旦分化成熟通常會退出細胞週期、不再分裂——這對需要大量細胞的實驗很麻煩。Buikema 的工作發現對已分化心肌再次給 2 µM CHIR99021 重新短暫活化 Wnt 訊號、搭配低接觸面積培養，可以哄騙這些心肌再進細胞週期一輪、把數量擴增 6–10 倍。本研究借用這一招是必要的，因為製作一條 ECT 就要 50 萬細胞、一個 reactor 6 條、跑兩個基因型多批次，沒有這一步根本湊不出細胞量。

為什麼用 0.5 mM EDTA 而不用 trypsin 傳代？iPSC 細胞之間靠鈣依賴型黏附蛋白 (E-cadherin) 黏在一起，EDTA 是輕度螯合劑會把鈣抓走、讓黏附鬆掉，使細胞團一塊塊浮起來——但細胞膜不會被破壞、細胞團也不會拆成單顆。比起 trypsin 把所有蛋白切掉、把細胞拆成單顆造成大量死亡，EDTA 是 iPSC 維持的標準溫和傳代方式。需要拆單顆的步驟（分化前鋪板、單細胞純系化）則另加 Y-27632 (Tocris #1254)——這是 ROCK 抑制劑，能阻斷 iPSC 被拆成單顆時啟動的「失去附著就自殺」訊號 (anoikis)，讓單細胞度過剛分散的脆弱期。

為什麼要強調兩個基因型用相同條件分化？整套研究的因果鏈條（FLNC ΔGAA → 心肌舒張缺陷）只有在兩個基因型其他條件完全相同時才成立。如果一邊用某批 CHIR99021、另一邊用另一批，或一邊 Day 10 切換 B27、一邊 Day 12 才切換，產出的 iPSC-CM 成熟度與純度就會不同——後續看到的舒張差異可能根本不是 FLNC 突變造成的，而是「一邊分化得比較不成熟」的人為差異。所以作者明定兩個基因型用同一個 Burridge 流程、同一批試劑、同一時間點操作，把分化變數鎖死。

4. 工具與材料: 
- **mTeSR Plus**: Stem Cell Technologies 出品的無 feeder 化學定義 iPSC 維持培養基。
- **Matrigel**: Corning 354230，作為基底膜替代品讓 iPSC 貼著生長的鍍盤材料。
- **0.5 mM EDTA 傳代**: 輕度螯合鈣離子鬆開 E-cadherin 黏附，溫和地拆細胞團為小塊。
- **Burridge 2014 化學定義分化法**: 以 RPMI1640 + 白蛋白 + 抗壞血酸取代血清，配合時序 Wnt 操弄分化心肌。
- **CHIR99021**: Tocris #4423，活化 Wnt 訊號的小分子；早期推中胚層、Day 10 後再加做心肌擴增。
- **Wnt-C59**: Tocris #5148，抑制 Wnt 訊號的小分子，把中胚層推向心臟前體。
- **Y-27632**: Tocris #1254，ROCK 抑制劑，阻斷 iPSC 單細胞 anoikis 死亡。
- **Buikema 2020 Wnt 二次活化策略**: 對已分化 iPSC-CM 再次給 CHIR99021 + 低接觸面積擴增 6–10 倍。
- **B27 滋養液**: Day 10 心肌跳動後切換的滋養補充劑，搭配 RPMI1640 維持心肌存活。

5. 與此篇文章的關係: 
在《Engineered cardiac tissue model of restrictive cardiomyopathy for drug discovery》這篇文章中，作者為了把 FLNC^ΔGAA^ 與 FLNC^ψWT^ 兩個 iPSC 基因型轉化成數量足夠、純度高的會跳動心肌細胞，採用了 Burridge 2014 化學定義分化法加上 Buikema 2020 的 Wnt 二次活化擴增。它解決了「血清批次差異會讓分化效率每次都不一樣」與「成熟 iPSC-CM 不再分裂、湊不出 ECT 所需細胞量」兩個瓶頸，產出供下游 2D 表型分析與 3D milliPillar ECT 組裝使用的兩個基因型心肌細胞庫。
