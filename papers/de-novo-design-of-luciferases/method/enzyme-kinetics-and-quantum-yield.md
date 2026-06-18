# 酵素動力學 (Michaelis–Menten) 與量子產率測定

1. 引用自哪篇 paper: de-novo-design-of-luciferases
2. Outline (任務主線): 酵素動力學 (Michaelis–Menten) 與量子產率測定
3. Method: 
   為了把 LuxSit、LuxSit-f、LuxSit-i 以及 h-CTZ 版本 HTZ3 系列與天然 luciferase 放在同一基準上比較，作者做了 Michaelis–Menten 動力學量測。流程是：把純化的酶固定到 100 nM，再準備一排不同濃度的 DTZ（從稀到飽和），分別倒進 plate reader 的孔裡——這是一台帶光偵測器的多孔讀盤儀，能在每個孔同步記錄發光強度隨時間的變化。為什麼 100 nM 而不是更高或更低？酶太少訊號讀不到，酶太多會在量測完成前把燃料耗光、偏離穩態假設；100 nM 是訊號夠亮又不會瞬間耗光燃料的中間區段。把不同 DTZ 濃度對應的初始發光速率畫成曲線，會看到典型的飽和形狀：燃料稀少時，酶這個有限工作站常空著，加更多燃料就能線性加快；燃料多到所有工作站隨時都有一個正在處理時，再加燃料也沒用，曲線水平。把這條曲線丟進 GraphPad Prism 8 擬合 $v = V_{\max} [S]/(K_m+[S])$，就可從中讀出 $V_{\max}$ 與 $K_m$。
為什麼一次要報 Km、kcat、kcat/Km 三個數字？這三個數字描述酶的不同面向：Km 是「酶到達半速率時需要多少燃料」，越小代表親和力越強；kcat 是「每個酶分子每秒最多翻多少次催化循環」，由 $V_{\max}/[E]$ 算出；kcat/Km 把兩者合起來代表整體催化效率，是不同酶之間最公平的比較指標。LuxSit-i 達到 $k_{\mathrm{cat}}/K_m = 10^6\,\mathrm{M}^{-1}\,\mathrm{s}^{-1}$，與天然 luciferase 同一量級。但 kcat 一個還不夠——光知道酶「翻得快」不等於知道「亮」，可能每次翻次都產熱沒產光。所以作者另外量了量子產率 (quantum yield)：把 50 nM 純化酶加進固定量 125 pmol 的 DTZ，等酶把燃料全部轉化完，整段時間累積的光子總數除以消耗的 DTZ 分子數，得到每個燃料平均產出多少光子。這個數字越接近 1 越好。把 kcat 和量子產率合在一起，才能得到 LuxSit-i 每秒總光子數比天然 RLuc 多 38% 這個結論。HTZ3-D2 的 $K_m = 7.9\,\mu M$、HTZ3-G4 的 $K_m = 19.5\,\mu M$，最大發光強度 Imax 分別為 LuxSit 的 25%、58%，所有資料取 n = 3、報 mean ± s.d.。
動力學量測之外，作者還在不同 pH 的緩衝液中追 LuxSit-i 的 luminescence decay 曲線，把這個酶接上更深的機制證據。DFT 計算指出 luciferase 反應的關鍵中間態是燃料變成帶負電的 anion，這一步對周圍 pH 極度敏感——pH 越高，溶液越鹼，越容易把燃料的質子拔掉形成 anion；pH 越低就難。果然，LuxSit-i 的速率隨 pH 系統性變化，曲線形狀完全符合「酶催化的關鍵步驟確實是穩定 anion」這個假設。沒做這層 pH 依賴測試，Km 和 kcat 的數字會看起來合理，但缺一塊把催化機制與設計初衷對齊的證據。
4. 工具與材料: 
   - **Michaelis–Menten 方程**: 酶速率對受質濃度的飽和模型 $v = V_{\max}[S]/(K_m+[S])$。
   - **Km**: 酶到達半速率時所需的燃料濃度，越小代表親和力越強。
   - **kcat**: 每個酶分子每秒最多翻多少次催化循環，由 $V_{\max}/[E]$ 算出。
   - **kcat/Km**: 整體催化效率，是跨酶最公平的比較指標；LuxSit-i 達到 $10^6\,\mathrm{M}^{-1}\,\mathrm{s}^{-1}$。
   - **luminescent quantum yield**: 每消耗一個燃料分子平均產出多少光子的效率比，越接近 1 越好。
   - **GraphPad Prism 8**: 擬合 Michaelis–Menten 曲線、做酶動力學參數估計的軟體。
   - **luminescence decay 曲線**: 在固定燃料下追時間衰減的曲線，用於 pH 依賴與動力學型態分析。
5. 與此篇文章的關係: 
   在《De novo design of luciferases using deep learning》這篇文章中，作者為了證明 LuxSit-i 真的可以跟天然 luciferase 同台比較，採用了 Michaelis–Menten 動力學擬合搭配量子產率量測。這個方法解決了「colony 亮度只能定性、跨酶比較無共同基準」的瓶頸，吃上一步純化的單體酶與標準濃度燃料，產出 Km、kcat、kcat/Km 與量子產率四組數字，直接交給下游的多工 reporter 應用論證 LuxSit-i 已達天然酶等級。
