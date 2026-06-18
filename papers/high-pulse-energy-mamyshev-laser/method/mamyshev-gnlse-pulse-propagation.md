# Mamyshev 腔內 GNLSE 脈衝傳播模擬

1. 引用自哪篇 paper: high-pulse-energy-mamyshev-laser
2. Outline (任務主線): Mamyshev 腔內 GNLSE 脈衝傳播模擬
3. Method: 
Mamyshev 雷射腔是一條兩端各放一個 WBG 反射器的直線波導（長 l = 0.42 m）——這就是線性腔。脈衝在腔裡來回跑：從左端 WBG 反射後往右走（前向，z: 0 → l），到右端 WBG 反射後往左走（後向，z: l → 0），這樣算一個 round trip。模擬要做的是把脈衝的複數場包絡 A(z, t) 沿著波導從 0 一步步推到 l、再推回 0，端點處乘上 WBG 反射譜當下一輪的起點。每跑一個 round trip 後脈衝會被 SPM 與增益慢慢塑型，重複跑直到形狀不再改變——這就找到穩態鎖模解。傳播方程式是 $\frac{\partial A}{\partial z} = -\frac{i\beta_2}{2}\frac{\partial^2 A}{\partial t^2} + \frac{g-\alpha}{2}A + i\gamma|A|^2 A$（Eq. 1）。逐項翻譯：第一項描述色散，β₂ = 0.715 ps²/m 是正色散 (normal GVD)，紅快藍慢，脈衝被拉長產生 chirp；第二項描述淨增益，g(z) 是 erbium 在每個位置提供的增益（由 2-B 速率方程靜態模型給出），α = 10 dB/m 是背景損耗；第三項描述 Kerr 非線性，γ = 1.145 W⁻¹m⁻¹，負責把光譜噴寬 (SPM)，是 Mamyshev 機制能擠掉弱光的物理引擎。整體 round-trip GDD = 0.601 ps²。怎麼解 Eq. 1？GNLSE 同時包含色散（在頻域 ω² 是純乘法）與非線性（在時域 |A|² 是純乘法），直接用差分法解很慢。Split-step Fourier method (SSFM，Agrawal 5th ed., ref. 47) 把短距 dz 切成兩半：先在時域作用非線性半步、快速傅立葉變換 (FFT) 到頻域作用色散整步、再 IFFT 回時域作用剩下半步非線性。每件事都在對它最簡單的域裡發生，整體計算 O(N log N)。模擬還做了兩個尺度分離簡化：第一，WBG 物理長度只有約 0.4 mm，遠短於 0.42 m 的腔長，把它當作瞬時的線性反射（複數反射譜由 3-G TMM 給出），不去細算 grating 內部色散；第二，腔內前向與後向脈衝雖會在中央區段空間重疊，但頻譜被兩個 WBG 分到不同窄帶，cross-phase modulation 累積效應遠小於 SPM，可忽略，前後向當獨立傳播。

為什麼非要雙向？因為線性腔的 erbium 增益剖面 g(z) 是雙向耦合的——同一位置 z 的反轉粒子數 n(z) 取決於該位置看到的「前向訊號平均功率 + 後向訊號平均功率 + 雙向泵浦」總和（這正是 2-B 速率方程靜態模型的核心）。要正確算 g(z) 必須同時追蹤兩方向訊號的平均功率，否則前向會多算增益、後向會少算。為什麼非要正色散？傳統光纖鎖模常用反常色散靠孤子，但整合波導的 γ 比光纖高三個數量級，孤子方程的 soliton number N 一上就破萬，會發生 soliton fission（一個脈衝裂成好幾個）與 wave-breaking（脈衝邊緣自己崩掉）。作者改用正色散 (β₂ = 0.715 ps²/m，normal GVD)：色散與非線性方向不再「抵消」而是「同向拉開」，脈衝被拖成有序的線性 chirp（紅頭藍尾），這種脈衝對 SPM 反應較溫和，能累積 ~20π 的單回程非線性相位仍不崩裂。3-F 的維度標準化分析直接給出 normal GVD + N ~ O(10) 這個 wave-breaking-free 的安全區，本工作的 0.42 m 腔長就落在這個區。最後兩個容易壞掉的地方：SSFM 的 dz 切太大時，算符分裂的二階誤差會在光譜邊緣（高 ω 處）冒出虛假震盪，讀者會誤判 Mamyshev 噴出來的光譜寬度；跳過前後向自洽時，前向跑過後 erbium 已被抽掉一部分能量，後向跑過時看到的真實增益會比假設低，穩態解會收斂到實際根本不存在的脈衝形狀。所以作者用 Algorithm 1 的雙層迭代——內層做前後向平均功率自洽、外層做 pseudo-time 推進場形——缺一不可。模擬程式碼釋出於 Zenodo (https://doi.org/10.5281/zenodo.18732611) 供讀者複現。

4. 工具與材料: 
   - **Generalized nonlinear Schrödinger equation (GNLSE, Eq. 1)**: 描述複數場包絡 A(z,t) 在含色散、增益/損耗、Kerr 非線性的波導中演化的偏微分方程式。
   - **Split-step Fourier method (SSFM)**: 把短距 dz 切成「時域非線性半步 + FFT 頻域色散整步 + IFFT 時域非線性半步」的數值解法，依 Agrawal Nonlinear Fiber Optics 5th ed. ref. 47。
   - **正色散 β₂ = 0.715 ps²/m (normal GVD)**: 本工作 Si₃N₄ 波導的群速度色散，紅快藍慢、避免孤子崩裂，是 Mamyshev wave-breaking-free 區的核心參數。
   - **Kerr 非線性係數 γ = 1.145 W⁻¹m⁻¹**: Si₃N₄ 高侷限波導的 Kerr 非線性係數，比光纖高三個數量級，由 3-E COMSOL 全向量計算給出。
   - **腔長 l = 0.42 m，round-trip GDD = 0.601 ps²**: Mamyshev 直線腔幾何，決定模擬區間與每 round trip 累積的色散量。
   - **雙向自洽 + WBG 瞬時反射假設**: 把前後向脈衝獨立傳播但共用同一個 g(z)，端點用 TMM 算的複數 WBG 反射譜當瞬時邊界。
   - **公開 MATLAB 程式碼 (Zenodo 18732611)**: 本模擬完整原始碼釋出於 Zenodo，供讀者複現。
5. 與此篇文章的關係: 
在《High-pulse-energy integrated mode-locked laser using a Mamyshev oscillator》這篇文章中，作者為了在製作晶片前先在數值空間鎖定鎖模穩定區，採用了 GNLSE + split-step Fourier method 的雙向脈衝傳播模擬。它解決了「整合 Mamyshev 直線腔無法靠單向 NLSE 算對增益」的瓶頸：吃進 2-B 速率方程的 g(z) 與 3-G TMM 的 WBG 反射譜，產出穩態鎖模解的頻譜、能量與 chirp 演化，是 3-C 自洽搜索演算法的核心子模組，也是後續 SCG (3-H) 的輸入脈衝來源。
