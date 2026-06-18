# 患者特異性壁面變形 (Patient-specific wall deformation prescription)

1. 引用自哪篇 paper: aortoseptal-angle-anomalies
2. Outline (任務主線): 患者特異性壁面變形 (Patient-specific wall deformation prescription)
3. Method: 
第四步是讓電腦裡那顆 LV「自己跳起來」。整個 LV 模型由兩個域組成 (Fig. 1A)：一層代表 LVOT + LV 壁的虛擬殼層 (fictitious shell)、與殼層內部包住的流體域 (fluid domain) 也就是血液體積。作者在殼層表面分布許多位移節點 (displacement nodes)，每個節點都從 cine-MRI 量到的真實壁面軌跡讀出「在每個時刻應該位於哪裡」，模擬時這些節點被強制按時間表移動，整層殼隨之變形。「虛擬」的意思是這層殼只當位移容器、不去計算肌肉如何產生力，繞過真實肌肉力學的所有複雜性。物理上，壁一動血就被帶著走：流體緊貼壁面的那一層必須跟壁面走一樣的速度 (no-slip)，加上血液不可壓縮，LV 體積縮小時等量血必須從打開的瓣膜擠出去、體積放大時必須從打開的入口吸進來。整套耦合採單向 (one-way coupling)：殼層位移驅動流體邊界，但流體壓力不回饋去動殼層——因為殼層本來就照 cine-MRI 的真實位移走，回不回饋都不會偏離真實軌跡，計算量大幅減少。
作者堅持用 cine-MRI 量到的真實變形、而不是寫一條 sin(t) 之類的理想化解析函數來驅動心臟跳動。原因是真實 LV 不是均勻收縮的球——它會扭轉、心尖往心底方向縮短、不同壁段的速率也不一樣。理想化函數會把這些不對稱完全洗掉，模擬出的血流會缺少真實心臟特有的非對稱渦環與射流。對本研究更致命的是：要量的就是「血流型態如何隨 AoSA 改變」這種細緻差異，如果連底層變形都被理想化抹平，AoSA 造成的細微改變更可能被洗掉而看不見。用 patient-specific 變形，相當於把真實心臟跳動這個複雜訊號完整保留下來。整套位移映射沿用作者群先前已發表的方法 [27,28]，細節見本論文 Appendix A.2。
瓣膜與入出流的處理同樣走「最便宜近似」路線。作者沒有真的建瓣膜幾何，而是在二尖瓣與主動脈瓣位置設兩個邊界，需要關閉時就強制把那個邊界的流速設成 0：收縮期二尖瓣設零流速 (mitral 關)、舒張期主動脈瓣設零流速 (aortic 關)。若省略這個約束，收縮期血會從兩端同時噴出、舒張期會從主動脈倒灌回來，完全不像真實單向循環。瓣膜葉片擾動、瓣膜逆流也因此不會被模擬，但對 LV 內主流場影響有限。入出流速度則是這樣推：因為血液不可壓縮，LV 體積在某瞬間變化多少就有相同體積的血進出。作者從 cine-MRI 拿到 LV 體積時變曲線 V(t)，對時間微分得到瞬時流量 dV/dt，再除以瓣口開口面積得到瞬時、空間均勻速度剖面 (transient spatially-uniform velocity profile)——整個瓣口斷面假設速度一致 (像活塞流)，犧牲了真實二尖瓣入流的非對稱渦環結構，但本研究焦點是 LVOT 出口附近的 WSS，這個簡化可接受。
4. 工具與材料: 
- **fictitious shell**: 虛擬殼層；代表 LVOT + LV 壁的薄殼結構，只當位移容器、不算肌肉力學。
- **fluid domain**: 殼層內部包住的血液體積，是 Navier-Stokes 求解的對象。
- **displacement nodes**: 分布在殼層表面的節點，從 cine-MRI 讀出每個時刻應在何處，被強制按時間表移動以驅動殼層變形。
- **one-way coupling**: 單向 FSI：殼層位移驅動流體邊界，但流體壓力不回饋去動殼層；因為殼層位移已被 MRI 完全指定，回饋多餘。
- **瓣膜零流速近似**: Aortic valve 在 diastole、mitral valve 在 systole 強制 zero flow velocity 代替真實瓣膜建模。
- **transient spatially-uniform velocity profile**: 瞬時、空間均勻入出流速度剖面，由 LV 體積時變對時間微分後除以瓣口面積得到。
5. 與此篇文章的關係: 
在《Significance of aortoseptal angle anomalies to left ventricular hemodynamics and subaortic stenosis: A numerical study》中，作者要讓四個 AoSA 變體用真實人類的心跳節奏推動血流，因此採用 patient-specific 壁面變形映射：把 cine-MRI 量到的壁面軌跡透過位移節點施加到虛擬殼層上，殼層位移再單向驅動流體域 (one-way FSI)。這條設定吃 cine-MRI 進來，產出時變壁面與瓣口流量，餵給下一步 ALE 流場求解。
