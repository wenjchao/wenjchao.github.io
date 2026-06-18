# One-way FSI with ALE flow solver (ALE 動態網格 FSI 流場求解)

1. 引用自哪篇 paper: aortoseptal-angle-anomalies
2. Outline (任務主線): One-way FSI with ALE flow solver (ALE 動態網格 FSI 流場求解)
3. Method: 
第五步是讓電腦真的去算「血在這顆會跳的 LV 裡怎麼流」。作者用商用求解器 ANSYS 2019 R3 (ANSYS Inc.) 解血液動力學，採任意拉格朗日—歐拉法 (ALE, Arbitrary Lagrangian-Eulerian；引用 Donea 等 1982 [30])。一般 Navier-Stokes 的標準寫法假設你站在不動的觀察框 (歐拉觀點) 看流體流過，但這裡的流體域邊界本身在動，固定網格會被壁面戳穿。ALE 讓網格自己以一個「網格速度 W」移動，被設成跟著變形邊界走；每個時間步求解器把邊界節點推到該瞬間位置、再對內部網格做平滑 (smoothing) 與重劃 (remeshing)，避免元素被擠扁拉長。控制方程因此把 (V − W) 寫進對流項：動量方程 ρ{∂V/∂t + [(V − W)·∇]V} = ∇·τ + f，意思是求解器站在移動網格上看到的相對流體速度是 (V − W)。若網格剛好跟著流體走 (W = V) 對流項消失、若網格不動 (W = 0) 就還原成標準 Navier-Stokes，所以這是涵蓋兩個極端的通用形式。連續方程 ∇·V = 0 則因為血液不可壓縮，與 W 無關。
血液被當成層流 (laminar)、不可壓縮 (incompressible)、牛頓流體 (Newtonian)，密度 ρ = 1050 kg/m³、黏度 μ = 0.0035 kg/(m·s)，數值沿用作者群先前研究 [27,28]。三個假設各自簡化一個面向：層流是因為 LV 內血流的雷諾數確實落在層流區間；不可壓縮對常溫液體成立；牛頓近似則是基於先前比較研究顯示非牛頓修正對 peak-systolic LV 流場影響很小。整套耦合方式是 one-way FSI——子項 D 的殼層位移單向驅動流體邊界，不把流體壓力回饋回去動結構。選 ALE 而不選 immersed boundary 或固定網格+內插，是因為 LV 壁變形幅度雖大 (ESV 到 EDV 體積變化超過一倍)，但軌跡完全由 cine-MRI 指定；對「大幅變形、軌跡明確」的情境，ALE 能讓網格貼著壁面走、邊界層完整保留，是最直接的選擇。
求解收斂上採用「跑四個心動週期、只取第四週期分析」的策略。求解器啟動時的初始流場是人造的「全部速度為零」起始條件，第一週期的流場大部分是「從零追趕」的暫態 (渦環還沒形成、射流位置還在追趕)，若把這份資料當生理流場比較四個 AoSA 變體，會把暫態偽影誤認成真實差異。連跑四個週期到時間收斂 (cycle-to-cycle convergence)、再取最後一週期，等於先讓電腦熱機再量測，是 CFD 守紀律。不過 ALE 在每個時間步 smoothing/remeshing 雖能維持網格品質，卻有一個惡名昭彰的副作用：同一個壁面位置在不同時間步上對應到不同節點編號——節點對應斷掉。任何需要時間積分的 WSS 指標 (TSM、OSI、WSS divergence) 都得在「同一節點隨時間累加」的前提下算，節點斷了就累加不起來。這就是過去 ALE FSI 研究普遍避談 cycle-averaged WSS 的原因，也直接動機化了後續 in-house MATLAB 節點追蹤演算法的需求。
4. 工具與材料: 
- **ANSYS 2019 R3**: 商用 CFD/FSI 求解器，承擔本研究全部血流模擬計算。
- **ALE (Arbitrary Lagrangian-Eulerian)**: 讓網格以網格速度 W 跟著變形邊界移動，能處理大幅但軌跡明確的壁面變形；引用 Donea 等 1982 [30]。
- **Navier-Stokes (ALE 形式)**: 連續方程 ∇·V = 0；動量方程 ρ{∂V/∂t + [(V − W)·∇]V} = ∇·τ + f，把網格速度 W 寫進對流項。
- **laminar / incompressible / Newtonian**: 血液假設：層流、不可壓縮、牛頓流體；ρ = 1050 kg/m³、μ = 0.0035 kg/(m·s)。
- **smoothing / remeshing**: 每個時間步重新平滑或重劃內部網格以維持元素品質，副作用是節點對應斷掉。
- **cycle-to-cycle convergence**: 連跑四個心動週期讓暫態消散，取第四週期分析。
5. 與此篇文章的關係: 
在《Significance of aortoseptal angle anomalies to left ventricular hemodynamics and subaortic stenosis: A numerical study》中，作者要在四個 AoSA 變體上算出整顆 LV 在一個心動週期內的血流場，所以使用 ANSYS 2019 R3 的 ALE one-way FSI：殼層位移驅動可移動網格、求解非定常 Navier-Stokes。這套求解吃子項 D 的時變壁面與瓣口速度進來，產出 LV 內部三維瞬時流場，是後續所有 WSS 與壓力指標的基礎。
