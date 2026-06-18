# 樣本數估算（Proportional-Hazards Sample Size）

1. 引用自哪篇 paper: pediatric-tri-tube-valved-conduit
2. Outline (任務主線): 在動物倫理限制下決定 group 1 (tri-tube) 需要幾隻才能在 80% power 偵測比 group 0 (tube-in-tube) 顯著延長的 valve 存活時間。
3. Method:

在開始植入羊之前，作者先問一個倫理導向的問題：「假設新版三管狀瓣膜真的比舊版『管中管』好那麼多，至少要用幾隻羊才看得出統計差異？」這個問題交給 UCSF 提供的網頁版樣本數計算機 (UCSF web-based sample size calculator)，背後跑的是 Schoenfeld 1983 年提出的「比例風險回歸」公式 (proportional-hazards regression model)。這個模型的核心假設叫「比例風險」：兩組受試者在任意時間點瞬間壞掉的機率比值 (hazard ratio) 是固定的——不論是植入後第 5 週還是第 40 週，group 1 (tri-tube) 壞掉的瞬時機率永遠是 group 0 (tube-in-tube) 的 0.125 倍。假設成立時，整條存活曲線的差異就能濃縮成一個常數 HR，公式再把它連同 α、power 反推「最少要幾隻」。

作者餵進計算機的五個參數各有來頭。(1) 舊版瓣膜的中位存活時間 14 週——這是來自同一個實驗室、同一種羊、同一套手術流程、過去 8 隻 tube-in-tube 的真實資料 (Reimer et al. 2017)，用內部 prior 比借文獻更貼近實驗條件。(2) 新版預期平均存活 52 週——對應 1 年的研究終點。(3) 風險比 HR = 0.125 (1/8)——代表「新版每週瞬間壞掉的機率只剩舊版的 12.5%」，從 14 週 vs 52 週存活在指數分布假設下反推。(4) 顯著水準 α = 0.05 雙尾——「明明沒差卻誤報有差」這種錯的容忍度設 5%；雙尾代表結果方向不預先寫死，付出多 20% 樣本的代價換 IACUC 與期刊普遍接受的嚴謹度。(5) 失追率 = 0——羊養在實驗設施內、終點是「regurgitation 達中度即提前犧牲」、最長 52 週也會主動取出，沒有追不到的問題。輸出：n = 6 隻就能達到 80% 的統計力 (power = 1 − β，β = 0.2，意思是「如果新版真的好到 HR = 0.125，這場實驗有 80% 機率成功偵測到」)。

為什麼 HR 越小、需要的樣本越少？想像兩條存活曲線：HR 接近 1 代表「兩組壞得差不多」，要分辨它們得收非常多事件才能在雜訊裡看出細微差距；HR = 0.125 代表「新版只剩 1/8 的瞬時壞掉率」，兩條曲線分得很開，少數幾個事件就足以在統計上看清楚。Schoenfeld 公式的數學寫法是「需要的事件數正比於 $(z_{\alpha/2} + z_{\beta})^2 / (\ln \mathrm{HR})^2$」，HR 越偏離 1、分母越大、需要的事件越少。但這也帶來一個失敗模式：HR 估太樂觀就會 underpower。如果作者寫 0.125 但實際只有 0.5，需要的事件數會暴增約 16 倍，6 隻羊根本不夠，可能誤殺一個真正有效的設計。所以 HR 不能隨便填，必須有 mechanistic 理由——這篇的依據是 ANSYS 模擬證明「commissure 上的應力被分散了，預期壽命應該大幅改善」。事後 actual HR 算出 0.123，與假設 0.125 幾乎一致，反過來證明前期估算合理。

原本估的 n = 6 只適用於「tri-tube 整體 vs tube-in-tube」這條主比較。但實驗進行到一半，作者發現 Gen 1 後期有 root 長太快的失敗模式，把剩下的 3 隻羊改植入加 sleeve 的 Gen 2。這樣一拆，Gen 1 變 4 隻、Gen 2 變 3 隻，兩個 cohort 都沒到原本估的 6 隻，「Gen 1 vs Gen 2」這個次要比較本來就 underpowered。作者也誠實註明：Kaplan-Meier 比較 Gen 1 vs Gen 2 拿到 P > 0.05，不能說「兩代沒差」，只能說「樣本不夠看不出差」；改用 time-independent 的 PI index 才補救出 P = 0.015 的差異訊號 (細節在 3-B 與 3-D 模塊)。原本針對 tri-tube 整體 vs tube-in-tube 的 power = 0.8 設計則仍然成立，最終得到 P = 0.0024 的顯著差異。

4. 工具與材料:

   - **proportional-hazards regression model**: 比例風險回歸模型，分析存活時間的標準工具，假設兩組瞬時壞掉率的比值（HR）隨時間固定。
   - **Schoenfeld 1983 formula**: Schoenfeld 提出的樣本數估算公式，需要的事件數正比於 (z_{α/2}+z_β)² / (ln HR)²。
   - **UCSF web-based sample size calculator**: UCSF Clinical and Translational Science Institute 提供的線上樣本數計算機，內建 Schoenfeld 公式。
   - **hazard ratio (HR)**: 風險比，group 1 瞬時壞掉率對 group 0 的比值，本研究假設 0.125、事後 0.123。
   - **median survival = 14 weeks**: 舊版 tube-in-tube 的同實驗室內部 prior，來自過去 8 隻羊。
   - **α = 0.05 two-tailed**: 顯著水準，誤報差異的容忍率 5%，雙尾代表結果方向不預先寫死。
   - **power = 0.8 (β = 0.2)**: 統計力 80%，意思是真有 HR = 0.125 差異時有 80% 機率偵測到。
   - **censoring rate = 0**: 失追率設 0，因為動物在設施內、終點為提前犧牲，沒有追不到的情形。
   - **n = 6 per group**: 計算輸出的最小樣本數；實際因中途改設計拆成 Gen 1 (n=4) + Gen 2 (n=3)。

5. 與此篇文章的關係:

這篇研究是一項在生長羊模型中比較新版 tri-tube 與舊版 tube-in-tube 瓣膜存活時間的大型動物實驗，受 IACUC 動物倫理限制必須在開始前回答「最少要幾隻才能看出差異」這個量化問題，這個模塊就是用 Schoenfeld 1983 比例風險公式搭配 UCSF 線上計算機提供答案的角色。它的好處在於把模糊的「樣本要多少才夠」轉成可審查的數字——餵入舊版 14 週中位存活、新版預期 52 週、HR = 0.125、α = 0.05、censoring = 0，輸出 n = 6 即可達 80% power，這個數字既能拿去通過 IACUC 提案、又把動物用量壓到下界。它與其他模塊緊密搭配：上游用同實驗室 8 隻 tube-in-tube 的歷史資料 (Reimer 2017) 與 ANSYS 應力分析提供 HR 的 mechanistic 依據，下游則為 Kaplan-Meier + log-rank 檢定 (3-D 模塊) 設定 power 前提，最終在 tri-tube vs tube-in-tube 主比較拿到 P = 0.0024、actual HR = 0.123 幾乎命中假設。但這個 power 設計只覆蓋主比較，當實驗中途因 root 過度生長分出 Gen 2 cohort 時，Gen 1 vs Gen 2 比較變成未預先 power 的次要分析，迫使作者改用 time-independent 的 pulmonary insufficiency index 作為輔助指標，凸顯了前期 power 設計範圍的邊界。
