# FACS 兩參數 gating + tetramer 定量作為 clonal 佔比追蹤

1. 引用自哪篇 paper: antitumor-lymphocyte-clonal-repopulation
2. Outline (任務主線): FACS 兩參數 gating + tetramer 定量作為 clonal 佔比追蹤
3. Method:
      為了在同一時間軸上量化「MART-1 反應 clone 佔 CD8+ 的百分比」，作者用螢光細胞分選 (fluorescence-activated cell sorting, FACS)：把病人血液裡的細胞一顆顆流過雷射，量它們被什麼螢光抗體貼上。第一步是在散點圖上用 anti-CD8 的螢光挑出「屬於殺手型 T 細胞」的那一群（第一層 gate），把 B cells、NK cells、CD4+ 這些跟主題無關的族群排除掉——這一步很關鍵，因為 lymphodepletion 之後不同細胞群的恢復速率不同，如果把它們都算進分母，MART-1 clone 佔比曲線會被非相關族群的漲落扭曲。進到 CD8+ 這個 gate 內之後，再看第二個螢光通道 (anti-Vβ 抗體或 A2/MART tetramer) 的陽性比例，算出來的才是純粹的「clone 佔殺手型 T 細胞的百分比」。
   第二個螢光通道裡的關鍵試劑是 HLA-A2/MART-1 peptide tetramer。作者把 HLA-A2 分子在體外先裝上 MART-1: 26-35(27L) 這段短肽，再用 biotin-streptavidin 骨架把四份綁在一起、掛上螢光——這個複合物表面等於同時亮出四份 MART-1 招牌，只有天線正好認得「HLA-A2 + MART-1」組合的 T 細胞才會被它染上。為什麼一定要四聚化？因為 T 細胞天線對單一 pMHC 的親和力其實很弱（幾 µM 等級），單個 HLA-MART 複合物一洗就掉，FACS 讀不到訊號；四份綁在一起可以同時貼到同一顆細胞表面的多個天線上，多點結合累積成足以停留的強讀數 (avidity boost)。分子交互作用機制 (TCR-pMHC binding) 跟體內辨識完全一樣，只是「誰貼誰」的方向反了：體內是目標細胞掛招牌給 T 細胞看，tetramer 則是作者手上的染色試劑掛滿招牌來染 T 細胞。
   Fig 1E 每條曲線各有分工：Vβ12 家族抗體（實心方塊）跟蹤病人 9 主導 clone、Vβ7 家族抗體（實心菱形）跟蹤病人 10 主導 clone、Vβ14（實心三角）當作「同族其他家族」的參照、其他 Vβ 家族的平均值（空心圓）代表背景 repertoire 應有的水準、A2/MART tetramer（實心圓）代表抗原專一性讀數。五條同框讓兩個獨立指標互相對照：只用 anti-Vβ 會高估，因為 Vβ12 家族底下有很多不同 clone、其中一部分不見得認 MART-1，抗體會全部算進來；只用 tetramer 則會低估，因為它對親和力太低或辨識略變異胜肽的 clone 抓不到，事實上病人 10 的主導 clone 對 A2/MART-1: 26-35(27L) tetramer 反應弱、只認 native MART-1: 27-35 胜肽，如果只看 tetramer 讀數會誤判他治療失敗。多加一條 Vβ7 曲線同時顯示 Vβ7+ 佔 CD8+ 九成七，才把病人 10 救回來當作 responder。只有 Vβ 曲線與 tetramer 曲線同時貼在一起、且高度吻合，才能宣稱是「同一個 MART-1 反應 clone 主導」。
   「clonal repopulation」的重點是持續，所以曲線必須拉長時間軸。作者從輸注當天 (day 0) 一路測到病人 9 的 day 123、病人 10 的 day 159，五條曲線在整段時間內同框比對，發現主導 clone 都維持在 CD8+ 的 60~97% 以上超過 4 個月——這才是「持久 clonal dominance」的直接證據。如果只取 day 7 高峰的一個時點，作者頂多能宣稱「lymphocytosis 期間曾有 clone 主導」，遠達不到論文的結論。
4. 工具與材料:
   - **螢光細胞分選 (FACS)**: 把細胞一顆顆流過雷射、量它們被什麼螢光抗體貼上，並在散點圖上分群定量。
   - **兩參數 gating**: 先用 anti-CD8 螢光挑出殺手型 T 細胞當分母，再在此群內看第二個螢光通道 (Vβ 或 tetramer) 的陽性比例。
   - **anti-Vβ7 / Vβ12 / Vβ14 抗體**: 只染指定 Vβ 家族的抗體；讀出的是天線「款式」而非抗原專一性。
   - **A2/MART tetramer (HLA-A2/MART-1: 26-35(27L) peptide tetramer)**: 四份掛好 MART-1 招牌的 HLA-A2 複合物、用 streptavidin 骨架綁在一起、掛螢光；四聚化用 avidity boost 讓弱結合累積成 FACS 可讀的強訊號，讀出的是抗原專一性。
   - **biotin-streptavidin 骨架**: 把四份 HLA-A2/peptide 綁在一起變 tetramer 的分子接頭。
   - **orthogonal readout**: Vβ 抗體與 tetramer 是兩個獨立的軸；兩軸同時吻合才能宣稱同一 clone 主導。
   - **longitudinal tracking**: 從 day 0 追到病人 9 的 day 123、病人 10 的 day 159，把時間軸上的 clone 佔比畫成曲線來判定持久性。
   - **native MART-1: 27-35 vs. altered peptide 26-35(27L)**: tetramer 用的是 27L altered peptide；病人 10 clone 只認 native 27-35，是必須同時保留 Vβ 讀數的具體案例。
5. 與此篇文章的關係:
   在《Cancer Regression and Autoimmunity in Patients After Clonal Repopulation with Antitumor Lymphocytes》這篇文章中，作者要在幾個月的時間軸上量化「輸入的 MART-1 反應 clone 佔病人殺手型 T 細胞的百分比」，靠單一抗體或單一 tetramer 都可能會估錯。因此作者採用了 FACS 兩參數 gating 加 tetramer 定量：吃進病人各時點的週邊血樣本，先以 anti-CD8 鎖定分母、再讓 anti-Vβ 抗體與 A2/MART tetramer 兩個獨立指標同框讀出，產出 Fig 1E 這條「主導 clone 在 CD8+ 中維持 60~97% 超過 4 個月」的長期曲線，作為 clonal repopulation 的核心定量證據。
