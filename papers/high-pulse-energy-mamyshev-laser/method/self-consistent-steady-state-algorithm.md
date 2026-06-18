# 自洽穩態鎖模搜索演算法 (Algorithm 1)

1. 引用自哪篇 paper: high-pulse-energy-mamyshev-laser
2. Outline (任務主線): 自洽穩態鎖模搜索演算法 (Algorithm 1)
3. Method: 
腔內 GNLSE 模擬最大的痛點是時間尺度差太多：erbium 族群動力學要 μs 級反應、腔的 round trip 卻只有 ns，硬模擬要算 10⁹ 級步驟，RAM 跟時間都吃不消。作者改採「假裝時間已停在穩態」的捷徑：直接找一個 input pulse 經過一個 round trip 回來會等於自己的不動點解。Algorithm 1 用兩層迴圈逼近這個解。外層 (j = 1 … M) 叫「偽時間步進 (pseudo-time stepping)」：每跑完一輪，把腔內場 A(ν, 0) × R_1(ν) 當作下一輪的初始 A，慢慢逼近穩定脈衝形狀。內層 (k = 1 … N) 則固定當前 A，反覆讓前向、後向脈衝跟前向、後向泵浦輪流走過波導：每往前走一個 dz 就用 Eq. 3 算當地 n(z)、Eq. 4 算 g(z)、split-step Fourier 推進訊號電場、同時更新泵浦功率；走完一趟再回來。內層的收斂判據是後向平均功率 |P_{avg,bwd,k}(0) − P_{avg,bwd,k−1}(0)| < tol。

「自洽 (self-consistent)」的物理意義是：腔內前向訊號、後向訊號、前向泵浦、後向泵浦四股光在每個 z 點同時搶 erbium 原子，它們的總強度決定當地 n(z)、n(z) 又決定當地 g(z)、g(z) 再回頭影響每股光走過這一段時被放大或吸收多少。所以不能先假設一個 g(z) 就推一遍——必須讓「用來算傳播的 g(z)」跟「傳播結束後反推回去的平均功率」一致。演算法每一輪把每個 z 點的前後向平均功率剖面存下來：當前輪前向傳播時拿後向上一輪結果查；算完前向再倒過來算後向時，又用剛算出的前向結果。如此來回把雙向耦合的「鎖鏈」收緊。

WBG 在演算法裡被當成一個瞬時頻域反射，直接把腔內場乘上 R_1(ν) 或 R_2(ν)。能這樣處理是因為 grating 物理長度（950 週期 × 半波長等級）跟整支 42 cm 波導比只是末端一小截，群延遲可忽略；R_1, R_2 由另一支 TMM 計算供給（見 3-G）。但晶片切面 (facet) 即使有 index-matching gel 仍會殘餘 Fresnel 反射，它跟 WBG 形成一段短的 Fabry-Pérot 腔，會把有效反射率扭曲、甚至支撐 parasitic CW lasing 把鎖模吃掉。作者把 facet 反射用 R_parasitic = 1.0 × 10⁻³ 跟 facet–grating 光程相關的相位 φ 疊回 R_i，得到 $R'_i = R_i + \sqrt{R_\mathrm{parasitic}}(1-|R_i|^2)e^{i\varphi}/[1 + R_i\sqrt{R_\mathrm{parasitic}}e^{i\varphi}]$，模擬時餵這個修正版。順帶一提，外層 j 不是真實時間軸——脈衝在外層每次更新之間沒有對應到任何物理時間，純粹是個 fixed-point 迭代，這也是『偽時間』命名的由來。

Algorithm 1 在腔長超過 57 cm、兩個 WBG 中心波長間距拉很大的區域常常不收斂——內層迭代的平均功率怎麼算都跳來跳去。這對應到實驗上實際觀察到的混沌脈衝態：腔內每 round trip 累積的非線性相位太多，脈衝落不到單一 attractor。所以演算法本身的『不收斂』就是「該參數點沒有穩定鎖模解」的訊號，可以拿來標記 (Δλ_f, l, P_p) 空間中的混沌邊界。另一種「壞」結果是收斂到 CW lasing 主導的 trivial 解——數值上有解、物理上沒用，代表那個落點上 parasitic 反射撐起的 CW 已經把鎖模壓下去，也要避開。

4. 工具與材料: 
   - **穩態解 (steady-state solution)**: input pulse 經一個 round trip 回來等於自己的不動點解；繞過暫態模擬。
   - **偽時間步進 (pseudo-time stepping)**: Algorithm 1 外層；每輪用上一輪輸出的 A 當下一輪輸入，逐步逼近不動點。
   - **自洽迭代 (self-consistent iteration)**: Algorithm 1 內層；前後向訊號與泵浦輪流走完波導，迭代到平均功率與 g(z) 一致。
   - **split-step Fourier method**: 標準 GNLSE 數值方法 (Agrawal, ref. 47)，把色散項與非線性項在每個 dz 分別在頻域/時域處理。
   - **WBG 反射 R_1(ν), R_2(ν)**: 由 TMM 算出的兩 grating 複數反射譜，在演算法中視為瞬時頻域乘法。
   - **R_parasitic 修正**: 把 facet Fresnel 反射 (R_parasitic = 1.0 × 10⁻³) 與 facet–grating 相位 φ 疊回 R_i 的閉合公式，描述短 Fabry-Pérot 對有效反射率的扭曲。
   - **混沌脈衝態 (chaotic pulsing)**: 腔長 > 57 cm + 大 grating 間距區域；Algorithm 1 不收斂，對應實驗觀察到的不穩定鎖模。
   - **trivial CW solution**: 演算法收斂到全 CW、無脈衝的解；代表 parasitic 反射撐起的 CW 把鎖模壓掉，需避開。
5. 與此篇文章的關係: 
在《High-pulse-energy integrated mode-locked laser using a Mamyshev oscillator》這篇文章中，作者用 Algorithm 1 把 Sec. 3-B 的速率方程增益與 GNLSE 脈衝傳播串成自洽穩態解，避免直接模擬 μs 級 erbium 族群動力學跨 ns 級 round trip。Algorithm 1 吃 R_1(ν), R_2(ν) 與 Table S2 參數，吐出 Mamyshev 腔的穩態鎖模解、供 Sec. 3-F 在 (Δλ_f, l, P_p) 設計空間掃出穩定地圖，並把不收斂區域標為混沌邊界。
