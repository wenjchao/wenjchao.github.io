# 整合 MLL 驅動的 THz-TDS 系統

1. 引用自哪篇 paper: high-pulse-energy-mamyshev-laser
2. Outline (任務主線): 整合 MLL 驅動的 THz-TDS 系統
3. Method: 
Mamyshev MLL 輸出的脈衝經 WDM 後先走一段 SMF 預先補償部分 chirp、再經偏振控制器與光纖式 PBS（兼作衰減器把功率壓到 PCA 可承受範圍）、再用 50:50 splitter 分成兩條路。一條送到發射端光導天線 (Tx PCA，Menlo Systems TERA15-TX-FC)：PCA 內部是一片光導半導體 (photoconductive substrate)，上面長了兩根金屬電極形成天線。沒光時半導體絕緣，飛秒光脈衝照到天線間隙會在皮秒內把半導體打通電流；加上 0–100 V 偏壓，瞬間導通就有短瞬電流，根據 Maxwell 方程 dJ/dt 正比於輻射電場，天線就輻射出一道脈衝寬度同樣在皮秒尺度的兆赫茲電磁波。THz 光路用 Thorlabs 金屬離軸拋物面鏡準直/聚焦、全長約 25 cm。另一條經 Thorlabs ODL100 自由空間延遲線後送到接收端 PCA (TERA15-RX-FC)：Rx PCA 沒外加偏壓，反過來讓入射的 THz 電場當作「外電場」拉動光脈衝瞬間打出的載子，得到瞬時電流——電流大小就是該時刻 THz 電場的取樣值。為什麼非要用機械延遲線一點點推進？因為 THz 電場本身在皮秒尺度起伏，任何電子取樣卡都跟不上。THz-TDS 的核心招數是把「時間解析度」換成「位置解析度」：只要讓採樣光脈衝晚 0.1 ps 抵達，就量到 0.1 ps 之後的 THz 電場值，0.1 ps 等於光走 30 µm，ODL100 雙程 20 mm/s 的延遲線在毫米級位置上慢慢推進，就能把整段 THz 電場逐點掃出來，這就是 THz-TDS 名稱裡「時域」的本意。

Rx PCA 輸出電流只有 100–500 nA，被 PCA 自身與電子電路的 1/f 雜訊埋沒。作者在 Tx 端對偏壓做 23 kHz 方波調變（Falco WMA-300 高壓放大器在 Keysight 33622A 函數產生器驅動下提供 0–100 V），等於把 THz 訊號搬到 23 kHz 載頻上；Rx 訊號送進 lock-in 放大器 (SRS SR630，內建跨阻放大器 10⁶ V/A) 只解出 23 kHz 載頻附近的成分。23 kHz 是刻意避開電源工頻 50/60 Hz 與 PCA 自己的 1/f 雜訊主要區段。為了把功率全留給 PCA，這條光路也刻意不接光隔離器——Mamyshev oscillator 對 PCA 端少量回反射相對寬容。資料處理還要躲兩個污染：PCA 內建 1 m fiber pigtail 會把脈衝拉寬，所以作者在自相關儀前插入同長度 1 m 光纖當「假 pigtail」，量到的脈寬才反映 PCA 內部實際脈寬（約 200 fs）；多次掃描的主峰時間會抖動，若不先對齊就直接時域平均會把尖峰平均成虛胖的峰，所以每次掃描都先做主峰 temporal alignment 再平均約 5 min。最後對時域波形做加窗 FFT 得到 ~7 GHz 解析度頻譜，達到 90 dB 動態範圍與 5 THz 頻寬。把這台 TDS 拿來示範兩個應用。厚度量測：把一片雙面拋光的高阻浮帶 (float-zone) Si 晶圓插進 THz 光路，主脈衝穿過 wafer 後部分會在兩面之間多反射一次再出來形成「回音」，延遲量 Δt_rt = 11.93 ps 對應 wafer 內部一個來回，用 n_Si = 3.4173 套 $d = c \Delta t_{rt}/(2 n_{Si})$ 算出厚度 523.3 µm，跟標稱值 525 µm 吻合；解析度下限由主峰 3 dB 寬度 (0.35 ps) 決定，約 15.4 µm。材料識別：把乳糖粉 (Adipogen SA) 與一般麵粉分別裝在對 THz 透明的塑膠袋中量穿透譜，計算吸收 A(f) = −ln T(f)，乳糖在 ~0.53 THz 有特徵吸收峰、麵粉沒有，兩者一眼分得開；大氣水氣的多根吸收線則用 HITRAN2024 線表 (Gordon et al. 2026) 比對校驗。

4. 工具與材料: 
   - **Menlo Systems TERA15-TX-FC / TERA15-RX-FC PCA**: 商用光纖耦合光導天線，分別擔任 THz 發射端與接收端，內建 1 m 光纖 pigtail 與高阻 Si 半球透鏡。
   - **Thorlabs 金屬離軸拋物面鏡**: 把 PCA 發出的弱發散 THz 準直再聚焦到接收端，全長約 25 cm 的 THz 光路。
   - **Falco WMA-300 + Keysight 33622A**: 高壓放大器與函數產生器，提供 Tx PCA 的 0–100 V、23 kHz 方波偏壓。
   - **SRS SR630 lock-in amplifier**: 內建 10⁶ V/A 跨阻放大器的 lock-in，把 23 kHz 載頻附近的 Rx 訊號從 1/f 雜訊中解出來。
   - **Thorlabs ODL100 自由空間延遲線**: 雙程 20 mm/s 的機械延遲線，把時間解析度換成位置解析度逐點掃 THz 時域波形。
   - **NI USB-6216 取樣卡**: 兩通道 DAQ，把 lock-in 的解調輸出數位化進電腦。
   - **厚度量測公式 d = c·Δt_rt/(2 n_Si)**: 以 n_Si = 3.4173、Δt_rt = 11.93 ps 算出 Si wafer 厚度 523.3 µm。
   - **HITRAN2024 水氣線表**: 光譜學標準線表（Gordon et al. 2026），用來比對校驗 THz 頻譜中的大氣水氣吸收線。
5. 與此篇文章的關係: 
在《High-pulse-energy integrated mode-locked laser using a Mamyshev oscillator》這篇文章中，作者為了證明 nJ 級晶片 MLL 能直接替代桌上型超快雷射，採用了透射式 THz-TDS 量測。它解決了「過去 THz-TDS 必須依賴桌上型光纖 MLL，成本與體積都壓不下去」的瓶頸：吃進 Mamyshev 的 ~200 fs 脈衝、產出 5 THz 頻寬與 90 dB 動態範圍的時域光譜，並直接示範 Si wafer 厚度量測 (523.3 µm) 與乳糖 / 麵粉的材料識別 (0.53 THz 特徵)，為手持化 THz 系統鋪好路。
