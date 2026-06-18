# 脈衝壓縮與強度自相關量測

1. 引用自哪篇 paper: high-pulse-energy-mamyshev-laser
2. Outline (任務主線): 脈衝壓縮與強度自相關量測
3. Method: 
Mamyshev 腔在 normal GVD（正色散）下跑——紅色比藍色傳得慢一點。腔內 SPM 邊走邊把脈衝光譜拉寬，新長出來的紅色被甩到脈衝前半段、藍色甩到後半段，瞬時頻率沿時間線性變化——這就叫線性啁啾 (linear chirp)。直接從晶片輸出的脈衝因此被拖得很長，看起來不像鎖模脈衝；但這條 chirp 是「乾淨的線性」，意味著只要在外部加一段「藍色比紅色傳得慢」的負色散介質（anomalous dispersion），就能把所有顏色重新對齊到同一個時間點，壓成一個非常窄的峰。

作者用兩條互補的壓縮路徑。Path A 是「可調研究路線」：Output 1 → 光隔離器 → Finisar Waveshaper 1000s (可程式 GDD 調諧器) → 自製低非線性 EDFA → APE pulseCheck 自相關儀，總光纖路徑 ~11 m。Waveshaper 有 ~6 dB 插損所以必須補一段 EDFA；但商用 EDFA 用好幾公尺長的 erbium fiber，對 147 fs 級高峰值脈衝會引入額外色散與 SPM、把脈寬污染成失真版本。所以作者自製 EDFA：用 LIEKKI ER80-4/125-HD-PM 超高摻雜光纖（~50 cm 就有所需增益）+ 兩個 Thorlabs 980/1550 nm WDM + Aerodiode 980 nm 泵浦，總路徑短、累積色散與 SPM 都低，這就是「低非線性 EDFA」的意思。Path A 最佳值得到 187 fs。Path B 則是「最終量測路線」：Output 2 直接接 ~10 m 單模光纖 (SMF)，SMF 在 1,550 nm 天然是 anomalous GDD（≈ −0.22 ps²，符號剛好對著腔內 normal chirp）；不經 EDFA 直接得到 147 fs FWHM——這就是論文宣稱的最終脈寬。

147 fs 的脈衝太短，最快的光偵測器頻寬 (~70 GHz) 都看不到。強度自相關儀 (intensity autocorrelator) 用另一個辦法：把脈衝分成兩束、其中一束加上可變延遲 τ，兩束打進非線性晶體裡同時通過時才會產生二倍頻訊號——兩束時間錯開越多、重疊區越小、訊號越弱。量到的 IAC(τ) = ∫ I(t) I(t − τ) dt 是脈衝強度的自相關函數，從這條曲線的半高寬就能反推脈衝寬度（IAC 寬度約為脈寬的 1.41 倍對 Gaussian、1.54 倍對 sech²）。本論文用 APE pulseCheck USB 50 商用機台。

Path A 不是只挑一個最佳 GDD 就收工，作者把 Waveshaper 設定的 β₂ 從一個值慢慢掃到另一個值，每個值都記錄一條 IAC 曲線，最後得到一張二維圖 IAC(t, β₂)：橫軸時間、縱軸 β₂、顏色強度是 IAC 值。在某個 β₂ 處脈寬最短 (187 fs) 是 Path A 最佳壓縮值，但更重要的是這張二維圖本身——Sec. 3-D 的 Algorithm 2 會把它送進 PyTorch 自動微分，反推出脈衝的振幅與相位（自相關本身無法給相位）。所以色散掃描不只是找最佳值，也是相位重建演算法的輸入資料。

4. 工具與材料: 
   - **linear chirp**: 脈衝瞬時頻率沿時間線性變化，由腔內 normal GVD + SPM 共同產生，可由外部 anomalous GDD 完全補償壓縮。
   - **GDD**: 群延遲色散（二階色散 β₂），描述介質讓不同波長到達時間差的物理量。
   - **Finisar Waveshaper 1000s**: 可程式光譜整形器，作為 Path A 的可調 GDD 調諧器，~6 dB 插損。
   - **single-mode fiber (SMF)**: Path B 用 ~10 m SMF，1,550 nm 天然 anomalous GDD ≈ −0.22 ps² 直接補償腔內 normal chirp 得 147 fs。
   - **anomalous dispersion**: 藍色比紅色慢的色散，本論文用 SMF 提供以壓縮 Mamyshev 輸出的正 chirp。
   - **low-nonlinearity EDFA**: 自製低非線性 erbium 光纖放大器：LIEKKI ER80-4/125-HD-PM 高摻雜光纖 (~50 cm) + Thorlabs 980/1550 WDM + Aerodiode 980 nm 泵浦，避免商用 EDFA 多公尺 erbium fiber 對短脈衝的失真。
   - **intensity autocorrelator (APE pulseCheck USB 50)**: 用非線性二倍頻 IAC(τ) = ∫I(t)I(t−τ)dt 量 fs 級脈寬，IAC 寬度約為脈寬的 1.41–1.54 倍。
   - **dispersion scan**: 掃描 Waveshaper 的 β₂ 並記錄 IAC(t, β₂) 二維圖，既找最佳壓縮值也供 Algorithm 2 相位重建用。
5. 與此篇文章的關係: 
在《High-pulse-energy integrated mode-locked laser using a Mamyshev oscillator》這篇文章中，作者要證明腔內輸出的線性 chirp 脈衝可以被乾淨壓到亞 200 fs 並驗證脈寬。脈衝壓縮 + 強度自相關量測解決了「fs 級脈衝直接電子偵測量不到」與「商用 EDFA 多公尺 erbium fiber 會污染量測」兩個瓶頸，用 SMF 直壓 Path B 取得 147 fs 終結果、Waveshaper 掃描 Path A 取得色散掃描資料供 Sec. 3-D 相位重建演算法 (Algorithm 2)，是論文中「nJ 能量 + 147 fs 脈寬 + 千瓦級峰值功率」這項核心宣稱的最後一塊驗證。
