# 流率與壁面剪切率的解析模型

1. 引用自哪篇 paper: collagen-microgel-bioprinting
2. Outline (任務主線): 流率與壁面剪切率的解析模型
3. Method: 
作者把『列印速度 F』當作整篇唯一的操作旋鈕。具體做法是固定 E/Δx——每往前走 1 mm，活塞就剛好推出固定體積的墨水——這樣不論 F 設快或慢，印出來的圖案幾何與每條絲的橫截面積都一模一樣，唯一不同的就是這條絲被『擠出來』的速度。在這個設計下，流率 (Equation 1) 變成 $\dot{Q} = A \cdot (E/\Delta x) \cdot F$：A 是注射筒截面積，括號乘出來的就是活塞每秒推進的距離。F 越快、Q̇ 越大。為什麼不反過來『固定 F、改 E』？因為那會同時改變絲的粗細與層高，後續看到的孔洞變化分不清是『搓得快慢造成』還是『絲變粗變細造成』。

知道流率後，作者要算的是『墨水在噴頭內被搓得多劇烈』——也就是壁面剪切率 $\dot{\gamma}_w$。直管內的流動，管中央流得最快、貼管壁的墨水幾乎不動，壁面附近被搓得最厲害。對於水這類牛頓流體，公式是 $\dot{\gamma}_w = 4Q/(\pi R^3)$；但膠原蛋白墨水是『擠得越快自己越稀』的非牛頓流體，所以要在方括號加上 Power-law 修正 (Equation 2)：$\dot{\gamma}_w = (\dot{Q}/\pi R^3) \cdot [3 + 1/n]$。n 是『多會變稀』的指數，n 越小越會變稀。對水（n = 1）方括號回到 4；對 n ≈ 0.3 的膠原墨水方括號約為 6.3——比牛頓公式大 60%，不修正會嚴重低估壁面剪切率，整條『$\dot{\gamma}_w$ vs. 孔洞分數』的設計曲線會整個位移。

公式裡的 n 怎麼來？作者在 ARESG2 旋轉流變儀（25 mm 鋸齒板對板，23 °C）上把墨水夾在兩片板中間，連續改變板轉速以掃過剪切率 10⁻² 到 10⁴ s⁻¹，量到的黏度 vs. 剪切率曲線在『剪切變稀段』剛好是直線；雙對數擬合 $\eta = K\dot{\gamma}^{n-1}$ 後（Fig. S5），斜率給 n − 1、截距給一致性指數 K（K 可以理解為『$\dot{\gamma} = 1$ 時的黏度』，是墨水稠度基準）。每種墨水——6 mg/mL collagen-azide、6 mg/mL unmodified collagen、35 mg/mL Lifeink——各自擁有一組 (K, n) 參數。

Equation 2 用『一個壁面剪切率』代表整根噴頭內部的流動，這個近似在窄噴頭（27 G，內徑 210 μm）是合理的；但換成大內徑噴頭（22 G）時就會崩——管中央的剪切區大到墨水在那裡幾乎沒被搓、黏度仍然很高、跟支撐浴幾乎不混；只有靠近壁面的薄殼被搓得稀、才大量夾帶微凝膠進入。結果就是『絲的中心沒孔、絲的外殼很多孔』的徑向不均。論文 Conclusion 段引用 Macosko (1996) 明確提出這條警語，是 $\dot{\gamma}_w$ 這個單值描述能否套用的邊界條件。
4. 工具與材料: 
   - **流率 Q̇ (Equation 1)**: 每秒擠出的墨水體積，$\dot{Q} = A \cdot (E/\Delta x) \cdot F$，列印速度 F 越快 Q̇ 越大。
   - **壁面剪切率 γ̇_w (Equation 2)**: 墨水貼噴頭內壁被搓的劇烈程度，$\dot{\gamma}_w = (\dot{Q}/\pi R^3) \cdot [3 + 1/n]$，是預測孔洞分數的關鍵物理量。
   - **Power-law 流體模型**: $\eta = K\dot{\gamma}^{n-1}$，描述『擠得越快越稀』的非牛頓流體；n 是剪切變稀指數、K 是一致性指數。
   - **E/Δx 固定設計**: 每 mm 路徑擠出固定體積墨水，鎖死絲的幾何，使列印速度 F 成為唯一操作變數。
   - **ARESG2 旋轉流變儀**: TA Instruments 出的旋轉流變儀，用 25 mm 鋸齒板對板做穩態剪切流動曲線以萃取 (K, n)。
   - **Macosko (1996)**: 標準教科書 Rheology: Principles, Measurements, and Applications，提供 Power-law 流體壁面剪切率與徑向梯度的解析框架。
5. 與此篇文章的關係: 
   在《Embedded 3D Bioprinting of Collagen Inks into Microgel Baths to Control Hydrogel Microstructure and Cell Spreading》這篇文章中，作者要把『列印速度』翻譯成可預測微觀孔洞的物理量。透過 Equation 1 把列印速度 F 變成流率，再用 Equation 2 加 Power-law 修正算出壁面剪切率 $\dot{\gamma}_w$。它的上游是流變儀量到的 (K, n)，下游則是黏度比設計法則——把 $\dot{\gamma}_w$ 代回 power-law 取得當下墨水黏度，與支撐浴零剪切黏度組成預測孔洞的單一無因次比。
