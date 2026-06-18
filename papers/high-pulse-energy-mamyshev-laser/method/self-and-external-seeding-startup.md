# 自啟動與外部啟動鎖模序列

1. 引用自哪篇 paper: high-pulse-energy-mamyshev-laser
2. Outline (任務主線): 自啟動與外部啟動鎖模序列
3. Method: 
傳統鎖模雷射靠飽和吸收體 (saturable absorber)：弱光被吸收、強光把吸收體飽和變透明，雜訊裡偶爾跳出來的小尖峰會被優先放大，自然演化成乾淨脈衝串。Mamyshev oscillator 沒有這個元件，改用「兩個錯開反射器 + SPM」——這個機制只對已經夠強、譜已被 SPM 拉寬的脈衝有效；剛開機時只有雜訊位準的弱光、譜很窄過不了反射器，雷射不會自己鎖起來，必須先「塞」一個夠強的種子進去。更糟的是腔內寄生背反射還會把雷射卡在低能量 CW 模式：模擬顯示要讓雜訊自發鎖模需要 R_parasitic < −42 dB，而本工作晶片切面 + 光纖端面只有 −27 dB，差了 15 dB；這就是為什麼必須額外引入啟動策略，未來改用 angled edge coupler + 匹配 fiber array (例如 FC/APC −60 dB) 才能完全純自啟動。

第一條路是自啟動 (self-seeding by pump modulation)：作者用 Koheron CTL300 或 SRS LDC502 的數位輸入給 1,480 nm 泵浦二極體電流加上 1.2–2.8 MHz 方波調變——把泵浦電流一下打開一下關上、每秒幾百萬次。鉺的反轉粒子數來不及跟上這麼快的變化，會發生弛豫振盪 (relaxation oscillation)：被推出穩態形成一連串短而強的 Q-switched 脈衝。這些脈衝雖然又寬又雜，但裡面總有一個尖峰功率夠高、把譜 SPM 拉寬到足以通過兩個 WBG，這就成了 Mamyshev 機制的種子，幾十個 round-trip 之後就會吸引到穩態鎖模脈衝。整個調變只開不到 10 秒，種子出現後關掉調變、雷射持續鎖模。實際流程是六步：(1) 開泵浦 (2) 設定加熱器、等 0.5 s 穩定 (3) 啟動調變 (4) 由光偵測器觸發或固定等待 (5) 關閉調變 (6) 微調功率與加熱器——這套流程可整段交給控制器自動跑。

第二條路是外部單脈衝啟動：直接給腔內塞一個現成的短脈衝種子，不靠雜訊抖出來。作者用一台商用桌上型鎖模光纖雷射 Menlo ELMO（輸出 51 fs 脈衝）當種子源。但這個種子有兩個問題：脈衝太短（譜太寬）會把腔內 attractor 帶偏；脈衝串太密（每秒上億發）會干擾後續觀察。作者用 Finisar Waveshaper 1000s 先做高斯型光譜濾波（帶寬 0.15–0.6 THz）把脈衝拉長一些、順手做 0.4 ps/nm 預色散補償；再用自製 EDFA 放大到 ~20 mW；最後用 EOSpace Mach-Zehnder 強度調變器 (一種能很快開關光通道的元件) + Aerodiode pulse picker board，由 Menlo trigger 同步「只挑出某一發脈衝、其餘擋掉」。最終晶片上看到的種子能量 15–45 pJ 即可可靠啟動，~20 個 round-trip 內進入穩態。

第三條路是延伸腔 Q-switching 啟動：把腔內損耗刻意先拉高（強度調變器關著＝高損耗），讓鉺增益繼續累積但雷射跑不起來；等增益累積到很高的時候突然打開強度調變器（降低損耗），存在鉺裡的能量瞬間爆出來形成一個很強的慢脈衝（24 ns、100 nJ）。這個慢脈衝不是鎖模脈衝，但能量夠強、後續在腔內循環時自己會分裂成幾個窄脈衝，再被 Mamyshev 機制收斂成單一鎖模脈衝。「延伸腔」的意思是用 EOSpace 強度調變器 + Thorlabs 環流器 (circulator) 在主腔外加一個可控的旁路臂，function generator 用 1 kHz、200 ns 寬的開窗訊號驅動，等於每秒「開閘」1,000 次。整個收斂過程 ~150 ns 進入雙脈衝態、~340 round-trip 後收斂為單脈衝、~3,000 round-trip 後雜訊衰減完畢。

三條路有不同的應用情境，因此都驗證過：pump modulation 最便宜、最自動化，未來做產品可以直接用商用 PWM driver 跑——這也是 Sec. 3-J 的統計化測時方法量化的主路。外部單脈衝啟動可以指定種子的脈衝寬度與相位，適合研究 Mamyshev attractor 結構——也就是「不同種子會不會收斂到相同最終態」這類物理問題。Q-switch 啟動則在 pump 功率較低或腔內雜訊 SNR 太差時派上用場，用大能量慢脈衝強行把腔推進鎖模。

4. 工具與材料: 
   - **saturable absorber**: 傳統鎖模雷射用的「強光才變透明」元件；Mamyshev oscillator 改用 spectral filtering + SPM 取代。
   - **self-seeding by pump modulation**: 對 1,480 nm 泵浦電流加 1.2–2.8 MHz 方波調變，引發弛豫振盪產生 Q-switched 種子脈衝。
   - **relaxation oscillation**: 反轉粒子數來不及跟上快速泵浦變化造成的震盪，形成 Q-switched 脈衝串。
   - **Koheron CTL300 / SRS LDC502**: 1,480 nm 泵浦二極體驅動器，具數位輸入可施加方波調變。
   - **Menlo ELMO MLL**: 商用桌上型鎖模光纖雷射 (51 fs)，作為外部單脈衝啟動的種子源。
   - **Finisar Waveshaper 1000s**: 可程式光譜整形器，做高斯型光譜濾波 (0.15–0.6 THz) 與預色散補償 (0.4 ps/nm)。
   - **Mach-Zehnder intensity modulator (EOSpace)**: 可快速開關光通道的強度調變器，搭配 pulse picker 挑出單一脈衝；延伸腔 Q-switch 也用同類元件。
   - **pulse picker (Aerodiode)**: 由 MLL trigger 同步挑出單一脈衝送進晶片。
   - **extended cavity Q-switching**: 主腔外加可控旁路臂的 Q-switch 啟動，function generator 1 kHz、200 ns 開窗驅動，產生 ~24 ns、~100 nJ 慢脈衝。
   - **circulator (Thorlabs)**: 光環流器，與強度調變器一起形成延伸腔的可控反射臂。
   - **R_parasitic**: 腔內寄生背反射比例，本工作 −27 dB，需 < −42 dB 才能完全純自啟動；未來改 angled edge coupler 可達 −60 dB。
5. 與此篇文章的關係: 
在《High-pulse-energy integrated mode-locked laser using a Mamyshev oscillator》這篇文章中，作者要展示晶片版 Mamyshev oscillator 不需外部桌上型鎖模雷射也能啟動，因此設計了三條啟動路徑——pump modulation 自啟動、外部單脈衝注入、延伸腔 Q-switch。這套啟動策略解決了「Mamyshev 沒有飽和吸收體就無法自啟動」與「晶片切面 −27 dB 寄生反射過強」的雙重瓶頸，把雜訊推上 nJ 級鎖模穩態的時間壓到 < 10 s 並接近 100% 成功率，是 Sec. 3-J 統計化啟動可靠度量測與整顆雷射「可自動化」的關鍵環節。
