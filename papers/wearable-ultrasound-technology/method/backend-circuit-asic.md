# 後端電路整合 (Discrete → Multiplexed → ASIC)

1. 引用自哪篇 paper: wearable-ultrasound-technology
2. Outline (任務主線): 後端電路整合 (Discrete → Multiplexed → ASIC)
3. Method: 
   後端電路的最小單元是「每顆元件背後配一組完整電路」。控制器 (controller) 下指令、發射器 (transmitter) 把指令變成 50 V 級的高壓類比脈衝 (high-voltage analog pulse) 擠壓電元件發聲、收發切換開關 (T-R switch) 在發射瞬間隔離接收電路避免高壓灌進去把它燒壞、接收器 (receiver) 負責讀回波——先把 µV 級訊號放大到 V 級（少了這步訊號淹沒在雜訊地板裡）、濾掉電源與通訊頻段的雜訊、再數位化交給後端 DSP 或 ML 演算法（電腦只能讀數字不能讀類比）。四塊缺一不可，且必須照這順序，引自 Chen & Pertijs *Open J. SSCS* 2021 (ref. 78)。連續波都卜勒則加上 clock generator + quadrature demodulator 做相位解碼 (Kenny et al. *Sci. Rep.* 2021, ref. 69; Fig. 3b)。
   陣列規模一上來，每顆元件配一組 T/R 立刻撐不住——8 元件就要 8 組、32 元件 32 組、wearable 根本塞不下。多工器 (multiplexer) 就是一顆『多進一出』的電子開關，可以按時間切換哪顆元件接到後面共用的 T/R。Lin et al. *Nat. Biotechnol.* 2024 (ref. 68) 用一顆 multiplexer 把 32 顆元件輪流接到同一對 T/R，電路數從 32 組壓到 1 組。更進階：多顆 multiplexer 串接時可以注入微秒級時間差，讓每顆元件以不同時間發聲、合成出可偏轉的主光束——這就是相位延遲 (phase delay) 達成波束偏轉 (beam steering) 的電路實作 (Pashaei et al. *IEEE TBioCAS* 2020, ref. 36)。8-element 各自配對 (Hettiarachchi et al. ref. 80; Yang et al. ref. 81) → multiplexed 32-element 共用一對 T/R → 多 multiplexer 串接做 phased array，是後端電路在陣列規模上的標準演化路徑。
   再進一步往 wearable 縮就必須走到特定應用積體電路 (ASIC, application-specific integrated circuit)：現成晶片每顆只解一個功能，整套組起來至少手掌大，訊號還要拉長線吸雜訊；ASIC 是專門為這個應用客製，可以把 transmitter + receiver + T/R switch + multiplexer 全部塞進 mm² 級、貼在 transducer 正下方訊號路徑短到幾百微米。論文整理三組數字：4-channel sensing ASIC = 9.89 mm² (ref. 82)；therapeutic ASIC 單元 4 mm²、16 元素 6.25 mm²、1024 元素 96.04 mm²，受 CMOS 製程節點 (180 nm vs 350 nm)、單極或雙極脈衝產生器 (unipolar vs bipolar pulser) 與移位暫存器 (shift register) 寬度影響 (refs 83, 84, 85)。sensing ASIC 重點在『讀清楚微弱回波』所以塞了 T/R switch、低噪放大器、高解析度 ADC，吃面積；therapeutic ASIC 重點在『大功率推固定波形』，主要是 pulser，不需要 ADC，單元很省但元素數量一多照樣堆。最後無線傳輸在 Bluetooth（短距低功耗，適合送血壓、心率等少量資料；Lin et al. ref. 68）與 Wi-Fi（高頻寬，適合送 B-mode 影像；Luo et al. *ACS Nano* 2023, ref. 86）之間依『要送什麼資料 + 多久充一次電』選擇。
   失敗情境最具警示性的是省掉 T-R switch：發射瞬間 50 V 高壓會直接灌進接收電路，接收器原本只預期讀 µV 級訊號、動態範圍頂多幾 V，過壓會把低噪放大器與 ADC 燒掉，整顆貼片發第一發就壞。T-R switch 不是優化選項而是保命電路。
4. 工具與材料: 
   - **Transmitter**: 發射器；把控制指令變成 50 V 級高壓類比脈衝擠壓電元件發聲。
   - **Receiver**: 接收器；把 µV 級回波放大到 V 級、濾掉帶外雜訊、再數位化交給後端 DSP / ML 演算法。
   - **T-R switch**: 收發切換開關；發射瞬間把接收電路與元件隔絕，避免 50 V 高壓灌進敏感的低噪放大器把它燒壞，是保命電路而非優化選項。
   - **Multiplexer**: 多工器；多進一出的電子開關，讓多顆元件輪流共用一對 T/R 電路，把 channel count 從 N 壓到 1，並可注入時間差做 phase delay 達成 beam steering。
   - **Phase delay / Beam steering**: 相位延遲與波束偏轉；用 multiplexer 串接注入微秒級時間差，讓每顆元件以不同時序發聲合成可任意角度偏轉的主光束 (Pashaei et al. *IEEE TBioCAS* 2020, ref. 36)。
   - **ASIC**: 特定應用積體電路 (application-specific integrated circuit)；專為 wearable 客製的 mm² 級晶片，把 transmitter + receiver + T/R switch + multiplexer 整合並貼在 transducer 正下方縮短訊號路徑。
   - **Sensing ASIC**: 感測用 ASIC，含 T/R switch、低噪放大器、高解析度 ADC，4-channel ≈ 9.89 mm² (ref. 82)。
   - **Therapeutic ASIC**: 治療用 ASIC，重點為 pulser，不需 ADC；單元 4 mm²、16 元素 6.25 mm²、1024 元素 96.04 mm² (refs 83, 84, 85)。
   - **Unipolar vs Bipolar pulser**: 單極／雙極脈衝產生器；bipolar 較省面積但需更精細電路設計，是 ASIC 面積落點的關鍵變數之一。
   - **Bluetooth vs Wi-Fi**: Bluetooth 短距低功耗適合少量資料 (Lin et al. ref. 68)；Wi-Fi 高頻寬適合 B-mode 影像 (Luo et al. *ACS Nano* 2023, ref. 86)。
5. 與此篇文章的關係: 
   在《Wearable ultrasound technology》這篇 Review 中，作者為了把整台 benchtop 超音波後端塞進貼片，介紹了「discrete → multiplexed → ASIC」三段演化。Discrete 給單元電路打底；multiplexer 解開 channel count 暴增與 phased array 時序兩個問題；ASIC 用 mm² 級客製晶片把整套電路塞到 transducer 正下方。再加上 Bluetooth/Wi-Fi 無線傳輸，後端終於可以放進電池供電的貼片，連回手機或雲端。這條後端微型化路徑是 wearable 從『實驗室原型』走向『可日常穿戴』的最後一道工程關卡。