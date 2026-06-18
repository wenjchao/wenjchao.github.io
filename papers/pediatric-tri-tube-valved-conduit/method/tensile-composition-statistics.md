# Tensile 與組成統計（ANOVA / t test / Linear regression）

1. 引用自哪篇 paper: pediatric-tri-tube-valved-conduit
2. Outline (任務主線): 判斷 explanted leaflet/root 的 modulus、UTS、collagen、protein、cellularity 是否隨植入時間變化，並比較 preimplant、native、Gen 1、Gen 2 之差異。
3. Method:

這個子項處理的是「怎麼把植入後取出的瓣膜跟原料、原生瓣葉、另一代設計做數字上的對照」。作者要回答兩個層次的問題。第一層：「這個量會不會隨植入時間越久而改變？」例如膠原蛋白密度是不是 36 週的瓣葉比 12 週的高？做法是把每個量對應植入時間畫散點圖，跑線性回歸 (linear regression) 找一條 $y = ax + b$ 最能穿過所有點的直線，看斜率 $a$ 是不是顯著不等於零；如果 *P* > 0.05 代表「沒有足夠證據說 a 不是 0」，作為「無時間趨勢」的操作型判據，可以把所有時間點的瓣膜當同一群處理。作者也用決定係數 $R^2$ 量化這條直線解釋了多少變異——例如 leaflet height 的 $R^2 = 0.33$ 表示「時間軸只能解釋 leaflet 高度變異的三分之一」。第二層：「沒有時間趨勢的話，這群瓣膜跟『原料管 (preimplant tube)』『原生肺動脈瓣葉 (native ovine pulmonary)』『另一代設計』比起來平均值差多少？」做法是 one-way ANOVA 一次比多組均值，再用 Tukey 事後檢定 (Tukey post hoc) 細看「哪兩組真的有差」。ANOVA 只給整體 *P* 值——「至少有一組跟其他組不同」；Tukey 則把所有兩兩配對都跑一次並調整 *P* 值以避免「多次比較撞到顯著」這種偽陽性。每個量都跑這套程序，最後得出「哪些屬性是植入後維持／改善／退化」的結論。

除了主流程，作者還有兩個比較需要不同工具。第一個是「同一片組織的環向 vs 軸向」這種方向比較。同一片組織會切出兩條方向不同的長條，兩個讀數來自同一個樣本，不是兩群獨立樣本。配對 t 檢定 (paired t test) 的邏輯是：對每個樣本算「環向 − 軸向」這個差值，再檢定這群差值的平均是不是 0。它把「個體之間本來就有的差異」當成共同基線消除掉，只留下「方向」這個變數的影響，比把所有環向放一堆、所有軸向放另一堆敏感得多。第二個是「跟 Flameng 2011 (ref 17) 的歷史基準鈣含量 1.11 µg/mg dry weight 比」。Flameng 文獻只給這個單一平均值、沒有原始樣本可以重新跑統計，於是改用單樣本 t 檢定 (one-sample t test)：把 1.11 µg/mg 當成一個給定常數 $\mu_0$，問「Gen 2 leaflet 樣本群的平均，是否顯著低於這個基準？」這是「無法重做對方實驗時」貼近文獻的標準退路。代價是：對方資料的不確定度完全沒被考慮進來，所以結論只能說「我們的樣本顯著低於 Flameng 報告的最低界」。

為什麼要設計成「先跑線性回歸，無時間趨勢才 pool」這個流程？想像植入 12 週的瓣膜本來就會比 52 週的軟一點。如果直接把所有時間點混在一起算平均，再跟原料管或原生瓣葉比，「越久越硬」這個訊號會被同組內的高低互相抵消，變成一個平淡無奇的均值——明明有變化卻看不出來。所以作者先讓資料對時間自己證明「沒有 trend」（斜率 = 0 不能被拒絕），這時 pool 才是合理的；如果 trend 確實存在，就必須分時段呈現。Proteomics 那一塊則設計得不太尋常：用 two-way ANOVA + Bonferroni 但寫明「不對多重比較校正」。為什麼？一次量大約 250 個蛋白，每個都跑檢定的話光靠隨機就會撞到很多假顯著，標準做法是 multiple-testing 校正。但這次只有 4 個 tube batch，校正之後幾乎沒有蛋白會顯著，整張結果就空了。所以作者把這份分析明確定位成「描述性探索」——目的是看 batch 間有沒有明顯系統差異，不是宣告任何單一蛋白「確定差異」。讀者要把它當「篩出可疑差異供後續追問」的工具，不能拿來確認單一蛋白的顯著性。

這套統計流程有兩個容易誤判的地方。第一是「無時間趨勢」的判據在小樣本下可能假象：線性回歸常常因為點太少而檢定不出顯著斜率，於是 *P* > 0.05、被當成「沒有時間趨勢」進入 pool 流程。但實際上趨勢可能存在，只是檢力不夠看不出來。一旦 pool 起來，不同時間點的差異會在均值中互相抵消，後續 ANOVA 跟 preimplant 或 native 比就會看起來「沒差」，作者就會錯誤地寫「植入時間不影響這個量」。所以除了看 *P* 值，最好也看 $R^2$ 跟散點分布——如果散點明顯有走勢只是樣本不夠多，要在文中標注「無顯著趨勢但需更多樣本確認」，不要直接定論。第二是 one-sample t test 對歷史基準的偏差：把 Flameng 2011 的 1.11 µg/mg 當固定常數 $\mu_0$ 來檢定，意味著「假設那篇文獻的數字沒有任何不確定度」。實際上對方那個數字也是從某個樣本群算出來的均值，本身有標準誤；把這個不確定度當零會讓檢定看起來比實情更有力。第二個隱藏風險是樣本前處理差異——作者用 hydroxyproline assay + dry-weight 標準化，Flameng 那篇可能用稍有不同的去水化或鈣定量程序，absolute number 在兩個實驗室之間未必直接可比。所以這個比較的結論最好保守地寫成「我們的瓣膜鈣含量顯著低於 Flameng 報告的下限」，不要外推成「絕對比 bovine valve 少 33 倍」。

4. 工具與材料:

   - **One-way ANOVA + Tukey post hoc**: 比多組均值；ANOVA 看整體有沒有差、Tukey 指認是哪兩組差。
   - **Paired t test**: 比同一樣本不同方向（環向 vs 軸向），用差值消除個體間變異。
   - **One-sample t test**: 把文獻單一數值 (Flameng 1.11 µg/mg) 當固定常數，檢定樣本群是否顯著偏離。
   - **Linear regression slope = 0 test**: 把時間當 x、量當 y 擬合直線，若 *P* > 0.05 視為無時間趨勢，可 pool 所有時間點。
   - **Coefficient of determination (R²)**: 決定係數，量化直線解釋了多少變異；leaflet height R² = 0.33。
   - **Two-way ANOVA + Bonferroni (no multi-test correction)**: Proteomics 用兩因子 (蛋白類別 × batch) 比較，但因樣本小不對 ~250 蛋白整體校正；定位為描述性探索。
   - **Significance level P < 0.05**: 本研究所有檢定的臨界值。
   - **Flameng 2011 historical mean (1.11 µg/mg dry weight)**: bovine valve 鈣含量下限，作者用 one-sample t test 比對。

5. 與此篇文章的關係:

這篇論文要證明生物工程瓣膜在生長羊體內 52 週後不只「沒壞」、而是真的隨宿主一起 remodel，因此產生大量跨時間點 (12/20/36/62 週)、跨組別 (preimplant tube、native ovine、Gen 1、Gen 2)、跨方向 (環向 vs 軸向) 的 modulus、UTS、collagen、protein、cellularity、鈣含量資料，這個 module 提供把這張龐雜表格轉成可宣稱結論的統計骨架。它的角色是「先用 linear regression 檢驗時間趨勢，無趨勢才 pool，再用 one-way ANOVA + Tukey 比較四組均值」的決策流程，並用 paired t test 處理同一瓣膜內的各向異性、用 one-sample t test 把 Gen 2 鈣含量直接對比 Flameng 2011 的歷史基準 1.11 µg/mg dry weight。這套設計讓拉伸力學測試 (G)、組織生化定量 (J) 與 proteomics (K) 各自產出的數字都能落到同一個統計框架內被比較，並透過 historical control 策略省下重做 Contegra 對照組的動物用量。其結果直接支撐論文核心宣稱——工程瓣膜在植入後維持原生瓣葉等級的力學性能、累積膠原與細胞、且鈣化顯著低於既有 bovine valve——這些定量結論若沒有這個 module，就只能停在 histology 的「眼睛印象」層級。
