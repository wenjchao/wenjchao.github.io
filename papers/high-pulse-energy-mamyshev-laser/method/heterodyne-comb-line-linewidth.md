# 異質拍頻 (Heterodyne) 與梳線線寬量測

1. 引用自哪篇 paper: high-pulse-energy-mamyshev-laser
2. Outline (任務主線): 異質拍頻 (Heterodyne) 與梳線線寬量測
3. Method: 
雷射輸出在頻率軸上是一排等距的「梳齒」(comb line)。要量單一根梳齒的光學線寬，作者拿一支極細的單頻參考雷射 (Koheras Adjustik single-frequency erbium fiber laser) 跟它面對面拍頻——兩道光在 50:50 directional coupler 合波後送進 balanced photodetector (Discovery DSC720-39)，偵測器把「兩者頻率之差」搬到 RF 頻段。這根差頻 RF 訊號的 Lorentzian 寬度等於兩道光光學線寬之和，當參考雷射比梳齒細很多時，量到的寬度就幾乎是梳齒本身的光學線寬。為了避免上千根梳齒同時湧進偵測器、彼此差頻互相蓋掉，前面先放一個可調窄帶反射器 (tunable fiber Bragg grating, FBG, AOS GmbH) 預選 ~1552 nm 那一小段，只留下對應參考雷射附近的少數梳齒。Balanced photodetector 的好處是兩道光共用的強度噪音會在差分時相消，極細的拍頻訊號才浮得出來。

拍頻訊號送進 Rohde & Schwarz FSW ESA 取 100 ms 的同相 (I)、正交 (Q) 時間段，從中重建瞬時相位；用 Welch's method（把長訊號切段、各自做 FFT 後平均）對相位的時間導數做估計，得到頻率雜訊功率譜密度 (frequency noise PSD)。在 200 kHz offset 處的雜訊底擬合即得光學 Lorentzian 線寬，本工作為 31.4 kHz；1–100 kHz 範圍內的雜訊底 < $5 \times 10^4$ Hz²/Hz。參考雷射 Koheras Adjustik 是亞 kHz 線寬的單頻 erbium fiber laser，遠細於 ~31 kHz 的目標 comb line，所以它對拍頻寬度的貢獻可忽略，量到的就是 comb line 自己的寬度。

上述只能量一個波長附近的線寬，為了驗證梳齒在整段 C 波段都存在、間距正確，作者把 FBG + Koheras 換成 Toptica CTL——一支可在 1530–1570 nm 連續調頻的單頻雷射，在這 40 nm 範圍內挑九個波長依序量拍頻，每個波長都能在 ±1 GHz 內找到一根 comb line，等於把整段譜的梳齒完整性掃過一遍。這套量測有兩個容易踩雷的地方：若跳過 FBG 預選，上千根梳齒會跟參考雷射打出一堆差頻覆蓋整個 RF 頻段，目標拍頻被淹沒；若參考雷射自己線寬就有幾百 kHz，量到的拍頻寬度幾乎是參考雷射的寬度，目標 comb line 的真實窄度被掩蓋而扣不回來。所以「窄帶預選 + 亞 kHz 參考雷射」是這套方法不可省略的兩道保險。

4. 工具與材料: 
   - **Koheras Adjustik single-frequency erbium fiber laser**: 亞 kHz 線寬的單頻參考雷射，當作量梳齒線寬的「尺」。
   - **AOS GmbH tunable fiber Bragg grating (FBG)**: 可調窄帶反射器，預選 ~1552 nm 一小段，只讓參考雷射附近的少數 comb line 進入偵測器。
   - **Discovery DSC720-39 balanced photodetector**: 兩顆光二極體做差分輸出，把兩道光的差頻搬到 RF，並透過共模抑制壓低共用強度噪音。
   - **50:50 directional coupler**: 把參考雷射與 comb 等比合波後送進 balanced photodetector。
   - **Rohde & Schwarz FSW ESA (I/Q 模式)**: 取 100 ms 的 I/Q 段並重建瞬時相位，供下游頻率雜訊 PSD 計算。
   - **Welch's method**: 把長訊號切段、各段 FFT 後平均估計 PSD，壓低統計波動。
   - **Frequency noise PSD**: 頻率雜訊功率譜密度；其雜訊底乘 π 給出光學 Lorentzian 線寬。
   - **Toptica CTL**: 1530–1570 nm 連續可調的單頻雷射，用於在整段 C 波段確認梳齒完整性。
5. 與此篇文章的關係: 
在《High-pulse-energy integrated mode-locked laser using a Mamyshev oscillator》這篇文章中，作者為了證明整合 Mamyshev oscillator 不只節拍乾淨、單一光學梳齒也夠純，採用了「FBG 預選 + 單頻參考雷射 heterodyne」方法。它解決的具體瓶頸是：純粹用光學頻譜儀只能看到整段梳的形狀，看不見單一梳齒的 kHz 級寬度。它把雷射輸出的單一梳齒吃進來，產出 31.4 kHz 的 Lorentzian 線寬給下游做頻率梳純度宣稱。
