# WSS topological skeleton: Eulerian fixed-point & manifold analysis (WSS 拓樸骨架分析)

1. 引用自哪篇 paper: aortoseptal-angle-anomalies
2. Outline (任務主線): WSS topological skeleton: Eulerian fixed-point & manifold analysis (WSS 拓樸骨架分析)
3. Method: 
前一步算 TSM 和 OSI 時，每個位置只算自己的時間平均，鄰居的剪力跟你無關。但 DSS 病灶不是均勻散佈在 inferior LVOT，而是集中在某個小區域——光說『這附近 TSM 高』沒辦法解釋『為什麼是這一格而不是隔壁那一格』。WSS 拓樸骨架反過來，把每個位置 cycle 平均後的 WSS 向量 $\overline{\boldsymbol{\tau}}$ 全部攤在內壁上，看整片箭頭排列形成什麼結構——哪裡所有箭頭都指向同一個點 (匯流口)、哪裡都從一個點射出去 (發散口)、哪裡是分流點 (鞍點)。這些『場的拓樸特徵』完全是空間結構的事，TSM/OSI 兩個單點統計量看不到，但卻能解釋病灶為什麼長在這一格。
作者借用 Mazzi et al. (Biomech. Model. Mechanobiol. 2019, [31]) 開發的 Eulerian 偵測法，並以 Wang, Wang & Li (J. Vis. 2018, [33]) 的 Poincaré 指標當判據。直觀做法是：在每個候選點周圍畫一個小圈，沿著圈走一圈、邊走邊紀錄『當地 WSS 箭頭指的方向轉了幾圈』——這個圈數 (除以 2π) 就是 Poincaré 指標。指標 = 0 表示沒有 fixed point；= −1 是鞍點 (saddle point，箭頭一半流進、一半流出)；= +1 是 node 或 focus (匯流口或發散口)。對 +1 的點，作者再算該處 WSS 向量場的 Jacobian 矩陣三個特徵值 (eigenvalues)：實部正負決定『向內收 (stable) 還是向外散 (unstable)』；有沒有虛部決定『直直收進來 (node) 還是轉著進來 (focus)』。組合起來把 +1 點細分成 stable/unstable node 或 focus 四種。
兩個 fixed point 之間有一條箭頭密集的骨架，叫 manifold——沿 stable manifold 走所有箭頭都收進 fixed point、沿 unstable manifold 走所有箭頭都從 fixed point 散出去。作者用一個更易計算的指標來量化這條骨架的局部行為：WSS 散度 $\nabla\cdot\overline{\boldsymbol{\tau}} = \frac{\partial\tau_1}{\partial x_1} + \frac{\partial\tau_2}{\partial x_2} + \frac{\partial\tau_3}{\partial x_3}$。散度 > 0 表示箭頭從這裡往外推開 (WSS stretching，擴張)；< 0 表示箭頭從四周往這裡擠進來 (WSS compression，收縮)，此物理對應引用 Zhang et al. (Sci. World J. 2013, [34])。為了跨模型比較，作者再把散度標準化為 $|\mathrm{WSSdiv}| = \frac{\nabla\cdot\overline{\boldsymbol{\tau}}}{|\nabla\cdot\overline{\boldsymbol{\tau}}|_{\max}}$，分母取四模型整體最大值，讓所有點落在 −1 到 +1 之間 (−1 = 整體最強收縮、+1 = 整體最強擴張)，共用同一支色階。WSS 收縮區的意義是『四周箭頭都往這塊內壁擠進來』——對細胞而言不只是被刷多用力 (TSM)、也不只是方向亂 (OSI)，而是被剪力從四面八方擠壓在同一塊。前人在血管 [43] 和瓣膜 [44] 已觀察到 WSS topological skeleton 異常與病灶共定位；本研究發現 inferior LVOT 同時是 TSM 上升超過 100% 的位置與 |WSSdiv| 下降超過 307% 的強烈收縮區，正好是 DSS 纖維膜臨床好發的位置——三個訊號共定位讓『力學環境異常 → DSS 形成』的假設多了一層更精細的證據。
這套分析的兩個關鍵步驟也說明它『少做會壞在哪』。如果只找 fixed point、不算 WSS 散度地圖，就只剩下『場為零的幾個離散點』，告訴你匯流口在哪，但兩個 fixed point 之間整片內壁究竟『收縮多強』完全抓不到——inferior LVOT 散度下降 307% 與 TSM 上升 100% 共定位的關鍵發現就跳不出來。如果做了散度卻跳過 $|\mathrm{WSSdiv}|$ 標準化，四模型散度絕對值差很多，每張圖各自上色看起來色塊強度差不多，但 130° 模型可能比 160° 強上好幾倍——共用色階才能讓陡角模型 inferior 區『散度由弱變強』的趨勢清楚呈現。
4. 工具與材料: 
- **WSS 向量場**: 把內壁每點 cycle 平均後的 WSS 向量攤成一張『風向圖』，是拓樸骨架分析的對象。
- **Eulerian fixed-point identification (Mazzi 2019, [31])**: 從 WSS 向量場找出 fixed point 並分類的固定座標方法，本研究主要參考文獻。
- **Poincaré index**: 繞候選點走一圈、紀錄 WSS 方向轉幾圈 (除以 2π) 得到的整數，用來判定 fixed point 類型 (0/−1/+1)；判據引用 Wang, Wang & Li 2018 [33]。
- **Jacobian eigenvalues**: 對 Poincaré 指標 = +1 的點計算其 Jacobian 矩陣三個特徵值，依實部正負與是否帶虛部把點細分為 stable/unstable node/focus。
- **saddle / node / focus**: WSS 向量場 fixed point 的拓樸類別：鞍點 (一半流入一半流出)、node (直直收/散)、focus (旋轉收/散)。
- **WSS 散度 ($\nabla\cdot\overline{\boldsymbol{\tau}}$)**: 量化某點 WSS 箭頭收縮 (負) 或擴張 (正) 的局部強度；物理對應引用 Zhang 2013 [34]。
- **標準化散度 ($|\mathrm{WSSdiv}|$)**: 把 WSS 散度除以四模型整體散度絕對值最大值，讓四個模型可在同一支色階下直接比較。
5. 與此篇文章的關係: 
在《Significance of aortoseptal angle anomalies to left ventricular hemodynamics and subaortic stenosis》這篇文章中，作者要解釋『為什麼 DSS 病灶就是集中在 inferior LVOT 那一小塊』。傳統 TSM/OSI 是單點時間統計量、答不出來。作者引入 WSS 拓樸骨架分析 (Mazzi 2019 Eulerian fixed-point + Poincaré index + Jacobian eigenvalues + 標準化散度)，吃進前一步的 cycle-averaged WSS 向量場，產出 fixed point 位置圖與 |WSSdiv| 地圖。這套指標讓作者首次在 LV 壁上同時看到 TSM 大幅上升與強烈 WSS 收縮共定位於 DSS 好發區，為下游 quadrant 量化提供關鍵的拓樸層證據。
