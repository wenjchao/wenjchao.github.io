# 重複率拍頻、時序抖動與相位雜訊量測

1. 引用自哪篇 paper: high-pulse-energy-mamyshev-laser
2. Outline (任務主線): 重複率拍頻、時序抖動與相位雜訊量測
3. Method: 
作者要量這顆雷射的「節拍乾不乾淨」，做法是把光脈衝串照在一顆耐高光功率的 p-i-n 光二極體 (Discovery DSC40S) 上——它把每一發光脈衝轉成一發電脈衝，這串電脈衝丟到看頻率分佈的儀器 (electrical spectrum analyzer, ESA, Keysight N9020A) 上，會在 175.5 MHz 處冒出一根高聳的尖峰，叫拍頻 (frep tone)；尖峰相對於旁邊背景雜訊高出多少 dB 就是拍頻 SNR——本工作量到 105 dB @ 10 Hz RBW。光二極體前面刻意加一個光衰減器，把功率壓到甜蜜點，避免 p-i-n 飽和把訊號變形。

「拍頻乾不乾淨」進一步可拆成兩個指標：時序抖動 (timing jitter) 與 Lorentzian 線寬。時序抖動是「每一發脈衝相對於理想節拍提早或延後幾飛秒」的隨機偏差；它的頻域表親叫單邊帶相位雜訊 (single-sideband phase noise, SSBPN)，把每個 offset 頻率上「節拍偏離理想正弦波多少」用 dBc/Hz 畫出來。兩者透過 $T_j = \frac{1}{2\pi f_\mathrm{rep}}\sqrt{2 \int 10^{\mathrm{SSBPN}(f)/10}\,df}$ 換算——本工作在 10 kHz–10 MHz 這段「快抖動」範圍積出 59.1 fs。Lorentzian 線寬則對應「雷射頻率隨機微抖」帶來的鐘形寬度：白頻率雜訊在相位雜訊圖上會走出 $1/f^2$ 斜率的直線，對 1 kHz–50 kHz 那段擬合就能反推 Lorentzian 線寬，本工作得 0.012 mHz——極窄，代表長時間頻率穩定度極佳。

這套量測中有兩個地方特別容易「讓儀器自己變成雜訊源」、把雷射誤判得比實際吵，作者各下了一道保險。第一道是量相位雜訊不能直接用 ESA——ESA 的本底雜訊比這顆雷射的相位雜訊還高，量到的根本是儀器底，會算出假大的線寬與抖動；所以改用專門設計給相位雜訊量測的 Rohde & Schwarz FSUP26 signal source analyzer，本底雜訊壓得遠低於一般 ESA。第二道是光功率必須剛好——p-i-n 一旦飽和，振幅起伏會被翻譯成額外相位起伏 (AM-to-PM conversion)，相位雜訊曲線整段假性抬高；對應策略是用高功率耐受 p-i-n + 前置光衰減器，把光功率壓到線性區甜蜜點。為了乾淨分離目標尖峰，作者中間還串了一條窄帶濾波鏈：Mini-Circuits ZX75BP-1062-S+ 帶通留 6 次諧波、ZX75BP-188-S+ 加 SLP-250+ 留基頻；ZFL-1000LN+ 低雜訊放大器把弱訊號拉到儀器最佳工作點，但寬頻量測時刻意不接預放，避免放大器自己飽和產生假諧波。

4. 工具與材料: 
   - **Discovery DSC40S high-power p-i-n photodiode**: 耐高光功率的光二極體，把光脈衝串轉成電脈衝串，能在強光下維持線性，避免飽和污染相位雜訊。
   - **Keysight N9020A ESA**: 看頻率分佈的儀器 (electrical spectrum analyzer)，用來量 175.5 MHz 處拍頻尖峰的 SNR。
   - **Rohde & Schwarz FSUP26 signal source analyzer**: 專門量相位雜訊的儀器，本底雜訊比一般 ESA 低，才聽得見這顆雷射安靜到什麼程度。
   - **Mini-Circuits ZX75BP-1062-S+ / ZX75BP-188-S+ / SLP-250+ / ZFL-1000LN+**: 窄帶濾波鏈 + 低雜訊預放大器，分離 frep 基頻與 6 次諧波並把弱訊號拉到儀器工作點。
   - **Timing jitter $T_j$**: 脈衝對理想節拍提早/延後幾飛秒的隨機偏差，由 SSBPN 積分得來；本工作 10 kHz–10 MHz 積得 59.1 fs。
   - **Single-sideband phase noise (SSBPN)**: 時序抖動的頻域版本，把每個 offset 頻率上偏離理想正弦波多少用 dBc/Hz 表示。
   - **$1/f^2$ slope fitting**: 白頻率雜訊在相位雜訊圖上呈現的特徵斜率；對 1 kHz–50 kHz 擬合可反推 Lorentzian 線寬。
   - **Lorentzian linewidth**: 白頻率雜訊在拍頻譜上形成的鐘形寬度，本工作擬合得 0.012 mHz。
   - **AM-to-PM conversion**: 光二極體飽和時把振幅起伏翻成相位起伏，會虛假抬高量到的相位雜訊。
5. 與此篇文章的關係: 
在《High-pulse-energy integrated mode-locked laser using a Mamyshev oscillator》這篇文章中，作者為了證明整合 Mamyshev oscillator 的同調性能跟光纖 MLL 平起平坐，採用了「高功率耐受 p-i-n 光二極體 + signal source analyzer」的相位雜訊量測鏈。它解決的具體瓶頸是：一般 ESA 的本底雜訊與光二極體飽和都會把相位雜訊高估，看不見這顆雷射真正有多安靜。它把前段壓縮過的脈衝串吃進來，輸出 105 dB 拍頻 SNR、59.1 fs 時序抖動與 0.012 mHz Lorentzian 線寬給下游論文做同調性背書。
