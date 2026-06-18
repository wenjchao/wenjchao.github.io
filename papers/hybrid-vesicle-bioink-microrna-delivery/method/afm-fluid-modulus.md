# 表面 nano-topography 與 Modulus (AFM, in-fluid)

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): 表面 nano-topography 與 Modulus (AFM, in-fluid)
3. Method: 
   AFM (atomic force microscopy, 原子力顯微鏡) 的核心是一根極細的探針固定在像跳水板的懸臂 (cantilever) 末端：探針逐點戳過樣本表面，表面凹凸讓懸臂上下彎曲；一束雷射打在懸臂、反射到位置感測器，從反射光偏移就能算出探針陷下去多少 (= 表面高度)。同一個探針在每個點還會「按下去、再放開」一次，記錄施力與形變的關係 (力-形變曲線)，把曲線餵進 DMT 接觸力學模型就能算出該點的局部楊氏模數。整個量測在液體環境 (in-fluid) 進行——水膠 70-90% 是水，乾燥後會塌縮變硬、量到的模數跟細胞實際感受的差好幾個數量級，所以非得泡在水裡測不可。作者用 Bruker Dimension Icon AFM 搭配 ScanAsyst-Fluid+ 銳尖探針：tip 約 2 nm 提供高橫向解析、150 kHz 共振頻率兼顧水中成像速度與穩定、0.7 N m⁻¹ 彈簧常數偏軟適合水膠這類軟材料 (太硬的探針會把表面戳爛、模數量得偏高)。

   掃描參數 scan rate 設 1 Hz (探針每秒來回掃一條線，太快追不上表面起伏、太慢熱漂移會扭曲影像)、512 samples/line (每線取 512 點，足以解析次微米形貌)。取得的影像包含 height image 與 DMT modulus map，必須先 flatten 才能進一步分析：AFM 樣本台與樣本本身一定有微小傾斜，原始高度圖帶整片的傾斜或弧形 baseline；如果不 flatten 直接算 RMS 粗糙度，這片大斜面會被誤計入「粗糙度」，RMS 數字被嚴重放大，不同樣本間傾斜不同還會讓 Gel-Lip / Gel-hEL / Gel-EV 的比較失準。flatten 把整片斜面扣掉後，得到的 RMS 才反映 NV 聚集帶來的真正奈米級粗糙度。

   DMT (Derjaguin–Muller–Toporov) 模數是把力-形變曲線餵進 DMT 接觸力學模型擬合得到的「局部楊氏模數」。不同接觸模型對「黏附力如何納入計算」有不同假設：Hertz 完全忽略黏附力，適合無黏的硬材料；JKR 納入強黏附力，適合像很黏的橡膠；DMT 介於兩者中間，假設黏附力存在但偏弱，剛好適合水膠這種軟、有些許黏性但不算強黏的體系，所以同一條力-形變曲線餵進 DMT 算出來的模數比 Hertz 更接近真實值。

   為什麼非得做 AFM-DMT 而不是只做巨觀壓縮測試？壓縮測試把整塊水膠壓扁，量到的是 bulk Young's modulus，反映整片樣本平均硬度——但細胞不會體驗巨觀力學，它感受的是貼著的那一片奈米區域。AFM-DMT 用 pico indenter 戳奈米區域，能逐點掃出「軟硬地圖」、看到 NV 在某些區域聚集造成的局部硬點。實驗結果剛好呼應這點：Gel-EV 與 Gel-hEL 的巨觀壓縮模數低於 Gel-Lip，但 AFM-DMT 平均反而較高——因為較小的 EV / hEL 在水中會向外擴散、聚集在水膠表面以靜電鍵結再形成，pico indenter 量到的就是這些聚集區。若整套實驗只做乾燥狀態的 AFM，水擴散機制不存在，這個「nano vs bulk 力學差異」的關鍵發現就直接消失，無法支撐 NV-GelMA 鍵結強度與局部聚集行為的解釋。
4. 工具與材料: 
   - **AFM (atomic force microscopy)**: 原子力顯微鏡，用懸臂末端的極細探針逐點戳樣本表面，量出形貌與局部模數。
   - **Bruker Dimension Icon AFM**: 本研究使用的 AFM 機型，能在水下 (in-fluid) 操作。
   - **ScanAsyst-Fluid+ sharp-tipped cantilever**: Bruker 專為水下成像設計的銳尖探針，tip 約 2 nm，提供高橫向解析。
   - **in-fluid imaging**: 在液體環境 (水) 中進行 AFM 成像，保留水膠的膨潤狀態，量到的模數才反映細胞實際感受的「濕」介面。
   - **RMS (root mean square roughness)**: 表面均方根粗糙度，從 AFM 高度圖計算的奈米級表面起伏程度。
   - **DMT modulus**: Derjaguin–Muller–Toporov 模數，把 AFM 力-形變曲線餵進 DMT 接觸力學模型算出的局部楊氏模數，適合軟、有些許黏性但不算強黏的水膠體系。
   - **image flatten**: AFM 影像預處理，扣除整片樣本的傾斜或弧形 baseline，避免假性 RMS 放大。
   - **pico indenter**: AFM 探針作為奈米級壓痕器的角色，能逐點量出局部硬度地圖。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了在「細胞實際感受的尺度」上量測 Gel-NVs 水膠的力學與粗糙度，採用了 in-fluid AFM 搭配 DMT 接觸模型。它解決了「巨觀壓縮測試看不見 NV 局部聚集」與「乾燥下測模數失真」的雙重瓶頸，吃入水合的 Gel-NVs 樣本，產出 RMS 粗糙度與 DMT 模數地圖，與下游壓縮測試、SEM 孔徑、釋放曲線交叉解讀 NV 在水膠中的聚集行為與鍵結強度。
