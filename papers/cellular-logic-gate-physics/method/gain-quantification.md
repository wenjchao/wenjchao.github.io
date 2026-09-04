# Transfer Curve 建構與 Gain 量化

1. 引用自哪篇 paper: cellular-logic-gate-physics
2. Outline (任務主線): Transfer Curve 建構與 Gain 量化
3. Method:
   FACS 每個實驗條件回傳的並不是單一數字，而是「數萬顆細胞各自的 ECFP 與 EYFP 亮度分布」。作者用兩步壓縮把它變成 transfer curve 上一個帶誤差棒的資料點：先取分布的中位螢光值當該條件的「輸入／輸出中央值」——細胞群的螢光分布常一邊拖長尾巴 (少數細胞特別亮或特別暗)，平均值會被離群者拉偏，中位數只看排到中間那顆的亮度，較穩；再標出涵蓋族群 95% 細胞的螢光區間當誤差棒，代表這個條件下細胞之間內在的散布幅度。

   把每個條件量到的 (median ECFP, median EYFP) 配對後畫在 log-log 座標上，中段陡峭區的斜率就是 gain (增益)。之所以用 log-log 座標，是因為它的斜率意義正好是「輸入變 1 倍時輸出變幾倍」，比 linear 座標更能對應到訊號放大／壓縮的直覺。作者對 `lacI/p(lac)` inverter 量到 gain = 4.72——中段輸入蛋白改變 1 倍，輸出蛋白會被反向拉動約 4.72 倍。這個數字大於 1 就是「訊號還原」能力的量化證據：即使前一級輸出稍有雜訊，經過這個閘之後也會被推回明確的高或低，多層閘串接時就不會逐級累積誤差。這麼陡的來源可追到 lacI 是「大家一起才有力」的 repressor——好幾個 lacI 蛋白必須手拉手 (pentameric 合作結合) 才能牢牢鎖上 p(lac) 啟動子，單體濃度稍過臨界值，多聚體就會加速形成、壓下輸出，天生給出陡峭轉折。

   作者刻意用「涵蓋 95% 細胞的螢光區間」而非標準差當誤差棒，是因為他要量的是族群的雜訊寬度、不是均值的不確定性。95% 區間直接畫出「95% 的細胞落在哪到哪」，讀者一眼就能看出「高輸入時的分布」與「低輸入時的分布」有沒有重疊——沒重疊就代表 noise margin 夠，這正是判斷 inverter 能不能串接時最想看的證據。

   但只看 gain 這個單一數字不夠——作者的判準要求 transfer curve 具備完整的「平-陡-平」三段 inverse sigmoid：兩端要平才有 noise margin (輸入的小抖動不會被放大到輸出)，中間要陡才有 signal restoration。改造前的 `cI/λP(R-O12)` 反相器就是反例：整條曲線幾乎是平線，中段沒有陡的翻轉，gain ≈ 0，直接判為不可用。這個「畫出曲線就直接看出可不可用」的判準，正是後續 Section 5 一連串 RBS／operator 改造有沒有救活閘的直接讀值。

4. 工具與材料:
   - **族群中位螢光 (median fluorescence)**: 每個實驗條件下族群 ECFP／EYFP 分布的中位數，作為 transfer curve 上一個資料點的中央值；對長尾分布較穩健。
   - **95% 涵蓋螢光區間**: 涵蓋族群 95% 細胞的螢光區間，作為 transfer curve 資料點的誤差棒，直接呈現族群內在的雜訊寬度。
   - **log-log gain (增益)**: 在 log-log 座標下 transfer curve 中段陡峭區的斜率，意義是「輸入變 1 倍時輸出被反向拉動幾倍」，量化 signal restoration 能力；本論文對 lacI/p(lac) 量到 4.72。
   - **平-陡-平 inverse sigmoid 判準**: 作者的可用性判準：transfer curve 必須具備兩端平坦 (noise margin) + 中段陡峭 (signal restoration) 且 gain > 1，才被列為可串接的候選 gate；平線響應直接判為不可用。
   - **lacI pentameric 合作結合**: lacI repressor 需要多個蛋白手拉手才能鎖上 p(lac) 啟動子，這種「一起才有力」的合作結合天生給出陡峭轉折，是 lacI/p(lac) gain = 4.72 的分子來源。

5. 與此篇文章的關係:
   在《The Device Physics of Cellular Logic Gates》這篇文章中，作者為了判斷手上的細胞 inverter 到底能不能當數位邏輯零件用，採用了 log-log transfer curve 建構與 gain 量化。這個方法把 FACS 給的族群螢光分布壓成一個帶 95% 誤差棒的資料點，並從中段斜率量到 lacI/p(lac) 的 gain = 4.72，直接為 signal restoration 與 noise margin 提供量化證據；同時把改造前 cI/λP(R-O12) 反相器的死線判為不可用，成為後續 Section 5 一切救活實驗的判準。
