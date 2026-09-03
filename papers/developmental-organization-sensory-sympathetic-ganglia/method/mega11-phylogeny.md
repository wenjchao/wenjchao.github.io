# MEGA11 最小演化系統發育樹與端支排列檢定 (單核 phylogeny)

1. 引用自哪篇 paper: developmental-organization-sensory-sympathetic-ganglia
2. Outline (任務主線): MEGA11 最小演化系統發育樹與端支排列檢定 (單核 phylogeny)
3. Method:

每顆單核在 184 個 MV 位點上都會被 snMPAS 判定成無突變、帶突變或測不到 (dropout)。作者把這 184 個位點依固定順序寫成一條「假 DNA 序列」(pseudo-sequence)——例如某顆核在位點 1 是 A、位點 2 是 G、位點 3 是 T…直到 184 個位點寫完。這樣做是為了讓 MEGA、MUSCLE 這類設計給真實 DNA 序列的建樹工具能直接沿用它們既有的「比對、算距離、建樹」演算法。因為 dropout 一定會讓不同核的序列出現空格，作者接著用 MUSCLE (常用的多序列對齊軟體) 把所有 pseudo-sequence 對齊到同一長度、處理這些缺口，再依 snMPAS 實際 genotype 手動確認 gap 位置，避免後面算距離時把不同位點誤配到一起。

作者建樹選的是 Minimum Evolution 最小演化法：所有可能的家族樹裡，總支長 (每根樹枝長度加總) 最短的那棵就是最合理的解釋——因為演化被假設盡量少變。實際運算時，MEGA v11.0.13 先用 Neighbour-joining 鄰接法快速給一棵不錯的起始樹，再用 close-neighbour-interchange (CNI, 交換相鄰分支的局部搜索) 反覆試「把兩根鄰枝互換一下會不會更短」，直到再也找不到更短的為止。兩顆核之間的距離不是直接數 mismatch (那樣會漏算兩個位點又變又變回去的回突變)，而是用 Maximum Composite Likelihood 距離：同時考慮各種鹼基替換的相對速率與整體鹼基組成偏差，把「觀察到的差異」校正回「其實累積了多少替換事件」。

樹的末梢一定會兩兩葉子共用一個小內部節點——這對葉子就叫 terminal branch pair (末梢兄弟)，代表這兩顆單核在樹上最鄰近、最可能是姊妹細胞。作者把每對兄弟依照兩片葉子的身分組合分類：T3-SG:T3-SG、T3-DRG:T3-DRG、T3-DRG:T3-SG、same-level、cross-level 等；再問「這種組合出現的次數是否顯著多或少於隨機」。permutation test 就是把 224 顆核的 label 打亂重貼、重跑統計一萬次得到隨機分布，再對照實際觀測值算 P value。用 permutation 而不用 t-test 或 chi-square，是因為樹上兄弟對彼此並不獨立，只有靠打亂 label 直接生成 empirical null 分布才不會被錯的分布假設污染。方向性上作者採 one-tailed：如果 SG 內部有 local clonal expansion，T3-SG:T3-SG 應該顯著多於隨機；如果 DRG 與 SG 是分開的 lineage，T3-DRG:T3-SG 應該顯著少於隨機。最終結果 T3-SG:T3-SG P=0.0011 顯著偏多、T3-DRG:T3-SG P=0.0427 顯著偏少，兩個方向同時吻合預測。

值得一提的是為什麼作者用 224 顆核建樹、卻只有 75 顆帶 cell type 標籤——因為兩者要求的資源不同：224 顆核 (含未帶 RNA 資訊的 raw 核) 撐住樹拓撲的解析度，只有同時測到 RNA 的 75 顆才能給出「T3-DRG 神經元」這種精確身分供 permutation 統計。這個混用讓樹的骨架不打折、label 精度也保留。統計門檻方面，作者採 bootstrap > 95 作為 clade 支持度顯著標準，與前一步 pvclust 的 AU P > 95% 概念相近但少了 multiscale 修正。此外 snMPAS 的 dropout rate ~19% 會讓某些位點在某顆核測不到，MEGA11 的 pairwise deletion 選項針對每一對序列各自排除 missing 位點以免整條序列被丟掉，代價是遠距對的距離估計較易失真——這也是為什麼只有訊號夠強的 T3-SG:T3-SG 與 T3-DRG:T3-SG 兩類 pair 能穿透 noise 達到顯著。若把這一步拆開——只建樹不做 permutation，只能主觀看「SG 好像跟 SG 常黏在一起」但沒有隨機基準；只做 permutation 不建樹，根本無法定義誰是末梢兄弟。兩步一起才能把「兄弟細胞的身分組合」量化為統計顯著性。

4. 工具與材料:

- **pseudo-sequence**: 把每顆核在 184 個 MV 位點的 allele 依固定順序串成一條假 DNA 序列，讓序列導向的建樹工具能直接處理。
- **MUSCLE**: 常用多序列對齊工具，用來把所有 pseudo-sequence 對齊到同一長度、處理 dropout 造成的缺口；作者再依 snMPAS genotype 手動修正 INDEL。
- **Minimum Evolution (ME)**: 找總支長最短的樹當家族樹的建樹準則，假設演化盡量少變。
- **Neighbour-joining (NJ)**: 快速的貪婪聚合建樹法，本子項用來給 ME 一棵不錯的起始樹。
- **close-neighbour-interchange (CNI, search level 1)**: 局部搜索法，反覆試「把兩根相鄰分支互換一下會不會讓總支長更短」，直到找不到更短為止。
- **Maximum Composite Likelihood 距離**: 兩顆核之間的距離度量，同時考慮各鹼基替換速率與鹼基組成偏差，把觀察到的差異校正回實際替換事件數 (避免遠距對被回突變低估)。
- **MEGA v11.0.13**: 分子演化統計軟體，整合以上建樹演算法與 bootstrap 支持度計算。
- **pairwise deletion**: MEGA 的處理 missing 位點選項；每一對序列各自排除 missing 位點，避免一條 pseudo-sequence 因為一個 gap 就整個丟掉。
- **bootstrap > 95**: MEGA 的 clade 支持度顯著門檻，對應 α=0.05；表示 1,000 次抽樣重建樹中該 clade 出現超過 95% 才算穩定。
- **terminal branch pair**: 樹末梢共用同一小內部節點的兩片葉子 (末梢兄弟)，代表這兩顆單核在樹上最鄰近、最可能是姊妹細胞。
- **permutation test (10,000 次)**: 把 224 顆核的 label 打亂重貼、重跑統計一萬次得到 empirical null 分布，再對照觀測值算 one-tailed P value。

5. 與此篇文章的關係:

在《Developmental organization of sensory and sympathetic ganglia》這篇文章中，作者要在單核解析度上證明 DRG 與 SG 屬於各自 clonally 獨立的 lineage，於是採用 MEGA11 的 Minimum Evolution 建樹加末梢兄弟 permutation 檢定。這個方法解決了 bulk pvclust 只能給出神經節之間、無法直達單細胞層的親等瓶頸；它吃 snMPAS 給出的 184 位點 genotype pseudo-sequence，產出末梢兄弟身分配對的顯著性 (T3-SG:T3-SG P=0.0011 偏多、T3-DRG:T3-SG P=0.0427 偏少)，把「clone 分家依身分不依位置」的結論推進到單核級證據。
