# ddG_bind 計算驗證 SSM 設計正確性

1. 引用自哪篇 paper: de-novo-design-of-luciferases
2. Outline (任務主線): ddG_bind 計算驗證 SSM 設計正確性
3. Method: 
   SSM 實驗告訴作者「哪些位置動了會壞」，但壞的原因有兩種：對「黏受質」很重要 (binding)、或對「催化過渡態」很重要 (catalysis)，SSM 本身分不出來。為了把這兩條軸拆開，G. R. Lee 開發了一套計算 SSM 模擬流程：對 LuxSit 受質結合口袋的每個位置，把 WT 胺基酸換成其他 19 種，每換一次都用 Rosetta 算一次結合自由能差 ddG_bind = ΔG(mutant–substrate) − ΔG(WT–substrate)。負數代表突變後跟受質黏得比 WT 更牢；正數代表黏得更鬆。為什麼要客製這套流程？因為 Rosetta 內建協定能算單一突變，但要對「每個位置 × 19 種胺基酸」做同樣標準的鬆弛、同樣的配體姿勢處理、同樣的能量函數，必須包成可重複跑的管線，才能保證跨位置、跨突變的結果能互相比較。
對比方式很直觀：每個 binding-site 位置畫一張散點圖，橫軸是 Rosetta 算的 ddG_bind（越往左代表越黏受質），縱軸是 SSM 實驗量到的相對活性。每個位置有 19 個點，紅點代表 WT (LuxSit) 那顆胺基酸 (Extended Data Fig. 5)。若 WT 紅點落在散點圖最左邊，意思就是當初電腦設計挑出來的這顆胺基酸在 19 個競爭者裡真的是對結合最有利的選項。這條結論對設計模型有兩層意義：Rosetta 能量函數在這個系統下可信、設計模型給的口袋結構也是對的。負責 π–π stacking 與疏水堆疊的位置都呈現這個漂亮的「WT 紅點最左」型態 (Extended Data Fig. 5d–f)——這正是作者敢說 LuxSit 設計「在受質結合上是 near-optimal」（已接近最佳）的依據。
更精彩的發現在 Y14–H98 與 D18–R65 兩組催化雙殘基 (catalytic dyad)。這四顆 WT 殘基的 ddG_bind 都不是最低 (Extended Data Fig. 5a, b)——換成其他胺基酸理論上能讓 LuxSit 跟基態 DTZ 結合得更牢。乍看像是設計失誤，其實正是設計正確的指紋。因為催化要穩定的不是基態，而是過渡態；要把殘基擺在剛好對準過渡態幾何的位置，往往意味著對基態結合而言不算最舒服。這個被刻意「綁」在不舒服姿勢上的狀態，就是非平衡的預先組裝 (preorganization)。所以 Y14–H98 與 D18–R65 的 WT ddG_bind 不是最低，反而正是它們「不是為了 binding 而是為了催化」的客觀指紋——如果它們的 WT 也剛好是 binding 最佳殘基，那它們很可能根本就不是催化殘基、只是包覆受質的座墊。
為什麼要花力氣多算這層 ddG_bind？因為 SSM 實驗只告訴你「動了會壞」、不告訴你壞的是 binding 還是 catalysis。ddG_bind 把 binding 這條軸單獨量出來，拿去跟實驗活性比，就能把 SSM 結果機制化地切成兩類，而不是停留在「這個位置改不得」這種黑盒結論。如果跳過這層比對：(1) 無法判定 Y14–H98 與 D18–R65 到底是催化還是結合殘基，可能誤推成「LuxSit 的結合特別仰賴這四顆殘基」這種錯誤詮釋；(2) 更嚴重的是無法把核心設計原則「催化殘基必須非平衡預先組裝在過渡態幾何上、而不是擺在 binding 最佳位置」提煉成可遷移的設計守則。整套方法論的轉化價值就少了一條腿。此外，這層比對本身有一個前置條件：負責 π-stacking 與疏水堆疊的 binding 殘基必須先通過 sanity check (WT 紅點落在最左)，後面對催化殘基的推論才站得住——這是兩段式邏輯，缺一不可。
4. 工具與材料: 
   - **ddG_bind**: 結合自由能差，定義為 ΔG(mutant–substrate) − ΔG(WT–substrate)；負數表示突變比 WT 黏得更牢，正數表示更鬆。
   - **Rosetta-computed binding energy**: 用 Rosetta 套件估出來的蛋白–配體交互作用能，含結構鬆弛後的最終值。
   - **Computational SSM simulation pipeline**: G. R. Lee 開發的客製流程，對每個 binding-site 位置 × 19 種胺基酸跑同一套標準計算，產出可跨位置比較的 ddG_bind 圖。
   - **catalytic dyad (Y14–H98, D18–R65)**: 兩組關鍵催化雙殘基；它們的 WT ddG_bind 並非最低，反映它們是為了過渡態幾何被預先組裝、而非為了 binding 而存在。
   - **preorganization**: 把殘基刻意鎖在對基態不夠舒服、卻對過渡態幾何剛好對準的非平衡姿勢上；催化的物理基礎。
   - **near-optimal sequence (for binding)**: 計算 ddG_bind 顯示 WT 在 19 種替代裡黏得最牢，代表設計挑出的序列已接近結合最佳。
   - **π–π stacking / hydrophobic packing residues**: 口袋裡負責芳香環平行疊放或疏水堆疊的位置；其 WT ddG_bind 通常落在散點圖最左，是 sanity check 的對照組。
5. 與此篇文章的關係: 
   在《De novo design of luciferases using deep learning》這篇文章中，作者為了搞清楚 SSM 實驗找到的關鍵殘基到底是負責「黏受質」還是負責「催化」，採用了 G. R. Lee 開發的 ddG_bind 計算 SSM 模擬流程。它解決了「SSM 只能告訴你哪裡動了會壞、但分不清原因」的瓶頸：把口袋每個位置的 19 種突變算一輪 ddG_bind 後與實驗活性對比。產出的結論「Y14–H98、D18–R65 的 WT 不是 binding 最佳殘基」直接提煉成可遷移的設計原則。
