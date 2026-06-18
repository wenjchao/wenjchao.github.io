# 統計比較與分群評估

1. 引用自哪篇 paper: chromatin-structure-regulatory-activity
2. Outline (任務主線): 統計比較與分群評估
3. Method: 
   ANOVA 已經告訴我們 CRS 序列維度貢獻 16% 的變異，但沒回答「ENCODE 把 CRS 標為 SE 那群真的比標 R 那群強嗎」這個更細的群組比較問題。作者用 Wilcoxon 排序檢定 (Wilcoxon rank-sum test) 來比兩群——它是一種非參數方法 (non-parametric)，不假設資料服從常態分布，做法是把兩群觀察值放一起依大小排名、看兩群排名平均是否顯著不同。輸出 P 值，Fig. 4b 報的是 *P < 0.1、**P < 0.05 兩級顯著性。比較的對象正是 ENCODE 在 K562 上的三類既有標註：強增強子 (Strong enhancer, SE)、弱增強子 (Weak enhancer, WE)、被壓制區 (Repressed, R)——作者沒重新分類，直接拿 ENCODE 標籤去測試「模型擬出的 $C_i$ 真的能反映這份分類嗎」。圖表呈現用統一規範的箱形圖：中線是中位數 (median)、箱子上下緣是 25% 分位 (Q1) 與 75% 分位 (Q3)、箱子高度即四分位距 (IQR = Q3 − Q1，代表中間 50% 的範圍)、兩條觸鬚從 Q1 − 1.5 × IQR 延伸到 Q3 + 1.5 × IQR，超出觸鬚的點視為離群。Fig. 2b、3a/b、4d/e 全採同一套規範。

   為什麼挑 Wilcoxon 而非更常見的 t test？關鍵是 CRS 表現量資料的特性：即使取 $\log_2$ 仍常呈偏態與長尾——強增強子的活性可能比一般 CRS 高好幾倍，長尾上總有幾個極端值。t test 假設資料常態、用平均值比較，平均值很容易被一個極端值拉偏。Wilcoxon 看排名，極端值的「絕對值多大」不重要，只看它的「排名」如何——強 CRS 不管強到多誇張，也只是「排第一」而不是「比平均高 1000」。所以 Wilcoxon 報的顯著性更穩健地反映「兩群整體位置是否真的不同」，而不會被離群值拉走。對應的失敗模式：如果硬用 t test，SE 群中少數異常強的 CRS 會把整群平均拉高，給出虛假的高顯著性 (或反過來被異常值搞糊反而不顯著)，無法忠實反映「分布位置」是否不同。

   Figure 3a 把 CRS 在 LP1 上分成 low / medium / high 三群、再看這個分群順序在其他 LP 是否保留。但這個檢驗有個漏洞——萬一 LP1 剛好是個特殊位置、它的排名本身就和別的 LP 不同呢？讀者可以追問「以 LP3 分群再看其他 LP，結果還會這樣嗎」。Supplementary Fig. 4 直接補強這一點：作者把同樣的「分群 + 看其他 LP」操作換成以任一 landing pad 為 reference 都跑一遍 (以 LP3 分群再看其他、以 LP5 分群再看其他、…)，結果排序保留的現象都成立。這就排除了「排序保留只是 LP1 特殊性的偽影」這個替代解釋，把 rank preservation 升格為跨所有 LP 的一般性質。

   另一個可預期的批評是：「結果只反映 130 bp 短序列的偽影，真實的全長 enhancer 可能天生強或有自我保護能力對抗位置效應」。為了堵住這個質疑，作者第二代 library 特地引入 13 段在文獻中已被驗證的全長增強子 (literature-validated full-length enhancers，長度大於 130 bp)，把它們和第一代的 130 bp 短 CRS 並列在同一個 patchMPRA 平台上量，結果用箱形圖呈現 (Fig. 4e)。結果發現這些「明星級」全長 enhancer 不見得比短 CRS 強、也沒有特別能對抗位置效應——modularity 結論在 enhancer 的自然形式上同樣成立。這就把「短序列偽影」這個替代解釋直接擋下。
4. 工具與材料: 
   - **Wilcoxon rank-sum test**: 非參數檢定，比較兩群觀察值的排名分布；用於 SE / WE / R 三類 $C_i$ 的群間比較 (Fig. 4b)。
   - **non-parametric**: 不假設資料服從常態分布的統計檢定家族；對偏態與離群值穩健。
   - ***P < 0.1, **P < 0.05**: Fig. 4b 標註的兩級顯著性閾值。
   - **box plot (median / Q1 / Q3 / whiskers / IQR)**: Fig. 2b, 3a/b, 4d/e 共通箱形圖規範：中線中位數、上下緣 Q1/Q3、觸鬚至 ±1.5 × IQR。
   - **ENCODE SE / WE / R 三分類**: Strong enhancer / Weak enhancer / Repressed，來自 ENCODE K562 segmentation 標註；本步驟直接套用，不重新分類。
   - **literature-validated full-length enhancers (> 130 bp)**: 第二代 library 引入 13 段文獻驗證過的全長 enhancer，用以排除「短序列偽影」的替代解釋。
   - **rank preservation across LPs**: 以任一 landing pad 當分群 reference，CRS low/medium/high 排序都在其他 LP 保留 (Supplementary Fig. 4)。
5. 與此篇文章的關係: 
   在《A massively parallel reporter assay dissects the influence of chromatin structure on cis-regulatory activity》中，作者要進一步檢驗「ENCODE 既有染色質分類是否真的能預測 CRS 強度」並排除「短序列偽影」這類替代解釋。這套統計比較吃前一步擬合得到的 $C_i$ 與 ENCODE 標籤，以 Wilcoxon 排序檢定比較分類群、以 reference-agnostic 補強驗證 rank preservation、以全長 enhancer 對照排除短序列特有現象，產出 Fig. 4b、Supplementary Fig. 4、Fig. 4e 三張關鍵圖。
