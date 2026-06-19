# ECT 柱頭位移→力學量化

1. 引用自哪篇 paper: engineered-cardiac-tissue-rcm
2. Outline (任務主線): ECT 柱頭位移→力學量化
3. Method: 

PDMS 柱在小形變範圍 (大約 <50 µm、柱徑 <2 mm) 內遵守胡克定律 (F = k·Δx)：只要事先知道每根柱子的「剛度 k」(每被拉 1 µm 需要多少 mN)，再從影片量出柱頭被拉了幾 µm，相乘就是力。作者用 CellScale 出的桌上型微力學測試儀 Microtester MT-LT 預先把每批 PDMS 柱的剛度量出來：拿一根空的 PDMS 柱，用儀器推它移動已知距離 (例如 100 µm)、量這樣需要多少力 (例如 0.5 mN)，做出一條「位移→力」校正曲線，這就是該批柱子的剛度 k (校正流程沿用 Tamargo et al. 2021 ACS Biomater. Sci. Eng.)。實際分析時攝影機只錄柱頭位置，再用 GVN Lab 自寫的 Python (https://github.com/GVNLab) 跑 computer vision 物件追蹤，把每一幀的柱頭中心抓出來、算出位移，乘上剛度就是即時的力。

ECT 一直被掛在柱間，柱頭從來不會回到「沒裝組織前的零位」，所以作者把力拆成三個讀值：(1) 被動張力 (passive tension) = 組織完全放鬆時柱頭仍被拉著、那段殘留位移換算的力，對應臨床上「舒張期心肌的硬度」，是 RCM 最關鍵的指標；(2) 主動力 (active force) = 從最放鬆到最收縮、柱頭額外被拉的位移換算的力，對應臨床上「心肌收縮時擠出的力」；(3) 總力 (total force) = active + passive，是柱頭被拉到最高點時的總拉力。為什麼一定要拆？因為 RCM 的病理特徵就是「passive 上升 + active 下降」，這兩股力方向相反，加總起來可能互相抵消、被誤判為正常；只有拆開才能分別抓到「鬆不開」與「擠不動」這兩面指紋。再對柱頭位移時間序列取一階導數，得到收縮速度與舒張速度：上升段斜率最陡的那一刻是收縮速度，下降段最陡是舒張速度。另外算 time to 50% relaxation：從每一下跳動的最高點開始計時，到柱頭往回退到「峰高的一半」所經的時間。這個指標臨床上特別敏感——心肌變僵時鬆得越慢、這段時間就越長；它也直接對應臨床心臟超音波在量舒張功能時常用的時間指標。

兩個容易踩雷的點。第一是標定漂移：PDMS 的剛度對溫度與基準/固化劑配比都敏感，如果在室溫做標定但實驗在 37°C 跑，量到的力會系統性偏高 (PDMS 熱下變軟)，不同批 PDMS 的配比微差也會被當成基因型差——例如 A 批柱子比較軟，量出來「該基因型 active force 比較小」其實只是柱子的問題，所以標定必須「同批 PDMS、同溫度、每批都做」。第二是操作員偏差：影像分析的計算部分是全自動沒人為偏差，但「哪些 ECT 算壞掉要剔除」仍是人為——某條組織因人為破壞或自發脫柱 (每批 12 條會掉 1–2 條)，這條要不要排除？如果操作員已經知道這條是病人型還是校正型，可能會不自覺地剔除「不符合預期」的數據 (確認偏誤)。作者強制操作員在剔除階段對基因型完全不知情 (blinded)，分析完成後才把標籤對回去。

4. 工具與材料: 
- **milliPillar platform (Tamargo et al. 2021)**: 把 ECT 掛在兩根 PDMS 柱間的 3D 平台，每個 reactor 含 6 條組織，柱頭位移可換算成力。
- **Microtester MT-LT (CellScale)**: 桌上型微米級雙懸臂力學測試儀，預先量每批 PDMS 柱的剛度建立 displacement→force 校正曲線。
- **Hooke's law (F = k·Δx)**: PDMS 在小形變內為線彈性材料的物理關係，是把影像位移翻譯成力的數學基礎。
- **Computer vision object tracking**: GVN Lab Python (https://github.com/GVNLab) 內含的演算法，逐幀抓出柱頭中心算出位移。
- **Active force**: 從最放鬆到最收縮柱頭額外被拉的力，對應臨床上「心肌收縮時擠出的力」。
- **Passive tension**: 組織完全放鬆時柱頭仍被拉著、殘留位移換算的力，對應臨床上「舒張期心肌的硬度」，RCM 最關鍵指標。
- **Total force**: active + passive，是柱頭被拉到最高點時的總拉力。
- **Contraction / relaxation velocity**: 對位移時間序列取一階導數，上升 / 下降段斜率最陡那一刻分別代表收縮、舒張速度。
- **Time to 50% relaxation**: 柱頭從峰退到一半所需時間；對噪音較魯棒，且直接對應臨床心臟超音波的舒張功能時間指標。
- **Blinded analysis**: 操作員在剔除壞掉 ECT 時對基因型不知情，避免確認偏誤；分析完成後才把標籤對回去。

5. 與此篇文章的關係: 
在《Engineered cardiac tissue model of restrictive cardiomyopathy for drug discovery》中，作者要證明 FLNC ΔGAA 突變真的造成「鬆不開」這個 RCM 核心臨床表型，所以用 milliPillar 平台把 ECT 掛在兩根 PDMS 柱間。透過先用 Microtester MT-LT 標定 PDMS 剛度、再以 computer vision 追柱頭位移，把影像翻譯成 active force / passive tension / relaxation velocity / time to 50% relaxation 這幾個直接對應臨床舒張參數的量。輸出用於兩基因型 ECT 比較與下游 trequinsin 救援驗證。
