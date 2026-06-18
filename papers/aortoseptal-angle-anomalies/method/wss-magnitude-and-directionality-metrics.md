# WSS magnitude & directionality metrics (TSM 與 OSI)

1. 引用自哪篇 paper: aortoseptal-angle-anomalies
2. Outline (任務主線): WSS magnitude & directionality metrics (TSM 與 OSI)
3. Method: 
牆面摩擦力 (WSS) 在每一點不只有『多用力』，還有『往哪邊刷』——它是一個沿著內壁切面的向量 $\overline{\boldsymbol{\tau}}$。早期只報大小 $|\overline{\boldsymbol{\tau}}|$，就像只記錄『今天手有多痠』、卻沒記錄『是被一直往前搓還是被前後甩』——這兩種累法對內皮細胞 (endothelial cells) 的訊號完全不同。被穩定單向流長期吹著的細胞會排得整齊、傾向健康保護狀態；反覆換方向的剪力會讓細胞偏向發炎、增生、組織重塑，常和血管病灶位置吻合。所以作者同時量兩個指標：時間平均剪應力大小 (TSM) 與震盪指數 (OSI)，它們在數學上獨立——光看 TSM 分不清『一直被同方向強壓』與『被左右大力來回搓』；光看 OSI 又會把『方向很亂但力道很小』誤判成壞地方。
TSM (Temporal Shear Magnitude) 的式子是 $\mathrm{TSM} = \frac{1}{T}\int_{0}^{T}|\overline{\boldsymbol{\tau}}|\,dt$：在某個位置上，每個瞬間都有一個 WSS 向量，把它的大小 ($|\overline{\boldsymbol{\tau}}|$，不管方向、純看強度) 從 t=0 加到 t=T、再除以週期長度，就得到 TSM。可以理解成『不分方向，這個位置一整顆心跳平均被刷多用力』——只要被刷就貢獻數字，不會因方向來回抵消而變小。
OSI (Oscillatory Shear Index) 的式子是 $\mathrm{OSI} = \frac{1}{2}\!\left[1 - \frac{|\int_{0}^{T}\overline{\boldsymbol{\tau}}\,dt|}{\int_{0}^{T}|\overline{\boldsymbol{\tau}}|\,dt}\right]$，關鍵在分子分母的順序差別：分子是『把每個瞬間的 WSS 向量先連方向一起相加，最後才取大小』；分母是『每個瞬間先取大小 (不管方向)，再相加』。如果整顆週期方向都一致，向量怎麼加都不會抵消，分子分母相等、分數 = 1，整體 OSI = 0 (純脈動單向流)；如果方向左右來回對沖，向量相加時互相抵消，分子變小、分數趨近 0，整體 OSI 趨近 0.5 (純震盪雙向流)。
兩個指標的價值要從『少看會錯過什麼』和『前置條件不足會壞掉』兩面看。少看 OSI 會錯過：本研究 LV 後壁延伸到心尖那一片區域同時呈現高 OSI (>0.3) 但 TSM 中等，只看 TSM 會以為那裡『沒事』，但 OSI 告訴我們那塊內壁長期被方向反覆換的剪力震盪——正是渦流結構的特徵。前置條件方面，TSM 與 OSI 的時間積分要求『同一個物理位置在每個瞬間都拿得到 WSS 向量』，必須先靠 in-house MATLAB tracking algorithm 把不同時步的節點對應起來，否則積分等於把不同位置的 WSS 加在一起、結果變成雜訊。
4. 工具與材料: 
- **WSS 向量 ($\overline{\boldsymbol{\tau}}$)**: 內壁某一點的牆面摩擦力，沿內壁切面有大小與方向；TSM、OSI 都從這個向量算出。
- **TSM (Temporal Shear Magnitude)**: $\mathrm{TSM} = \frac{1}{T}\int_{0}^{T}|\overline{\boldsymbol{\tau}}|\,dt$，量化『一整顆心跳平均被刷多用力』。
- **OSI (Oscillatory Shear Index)**: $\mathrm{OSI} = \frac{1}{2}[1 - \frac{|\int\overline{\boldsymbol{\tau}}dt|}{\int|\overline{\boldsymbol{\tau}}|dt}]$，量化『方向是穩定還是來回對沖』；0=純單向、0.5=純震盪。
- **endothelial cells (內皮細胞)**: 內壁的感力細胞，對單向高剪力與震盪剪力的反應方向相反；是 WSS 指標背後的生物學動機。
5. 與此篇文章的關係: 
在《Significance of aortoseptal angle anomalies to left ventricular hemodynamics and subaortic stenosis》這篇文章中，作者要回答『AoSA 變陡是否會在 LVOT 製造對內皮細胞最不利的剪應力環境』。他們吃進前一步節點追蹤產出的 WSS 時間序列，輸出 TSM 與 OSI 兩張地圖。這兩個指標獨立量化『大小』和『方向震盪』，產出 Fig. 4B/C 與 Fig. 5B/C，讓下游 quadrant 分析能識別出 inferior LVOT 同時被高 TSM 與相對穩定的單向剪力雙重打擊的位置。
