# 直接驅動的 Si<sub>3</sub>N<sub>4</sub> Supercontinuum 產生

1. 引用自哪篇 paper: high-pulse-energy-mamyshev-laser
2. Outline (任務主線): 直接驅動的 Si<sub>3</sub>N<sub>4</sub> Supercontinuum 產生
3. Method: 
Mamyshev 輸出的脈衝是拖尾的 (chirped) ——不同顏色前後排成有序隊伍。作者先把這串脈衝送進約 2.5 m WDM 後續光纖、光隔離器 + 2.18 m pigtail、偏振控制器 (3.43 m) 與一段 1550 nm 透鏡光纖 (~2 m)，這幾段加起來大約 10 m，剛好把不同顏色重新對齊（線性壓縮 chirp），峰值功率被推到千瓦級。透鏡光纖把光對到第二片晶片上的 43.7 mm 螺旋型 Si₃N₄ 波導 (D7802，依 photonic damascene 製程，Liu et al., Nat. Commun. 2021 製作)，截面 2.07 µm × 0.70 µm。強脈衝在這條波導裡發生自相位調變 (self-phase modulation, SPM) 與孤子分裂，把單色光譜「噴」成從 736 nm 一路延伸到 2,331 nm 的連續光譜——跨度 1.5 個八度，20-dB 頻寬 18.7 THz。整段過程不接任何外部放大器。把光譜噴寬的引擎就是 SPM：強光走進波導時，材料折射率因光強瞬間升高 (n = n₀ + n₂I)，光自己給自己一個額外相位 φ(t) = −n₂I(t)ωL/c。脈衝中央最亮、邊緣較弱，所以額外相位也是中央最大、邊緣最小，這個「隨時間變化的相位」對時間求導就是瞬時頻率的偏移：脈衝前緣紅移、後緣藍移，原本窄頻光譜被噴開到包含許多新顏色。SPM 要有效率，還得讓不同顏色在波導裡同步前進，這就靠色散工程波導 (dispersion-engineered)：作者調整截面寬高，把近零色散區設計在 telecom C-band 附近，剛好對到 Mamyshev MLL 中心波長 1550 nm，新顏色才不會走太快太慢被脈衝甩掉。

波導長度直接決定非線性相位積得多大。模擬顯示 43.7 mm 剛好是 octave-spanning 開始發生的長度——前段的色散會先把光纖殘餘的 chirp 自動修掉、後段才開始噴顏色。把波導加長到 175 mm 雖然能再往兩端延伸光譜，但同調性 (coherence) 會下降，孤子分裂走得太遠、不同 round-trip 之間的相位關係越來越亂，所以 43.7 mm 是「夠寬到 1.5 個八度、又還能保持同調」的折衷。能量帳也算得剛好：過去整合 MLL 只有 pJ 級脈衝必須先外接桌上型 EDFA，這顆 Mamyshev 直接打出 ~1 nJ，經 10 m SMF 壓到 147 fs 後，on-chip 平均功率 ~18 mW、峰值功率 ~450 W，已經夠在 43.7 mm 波導裡累積足夠的非線性相位——這正是整條鏈不接外部放大器的關鍵證據。最後量出來的光譜要可信，還得閃開光譜分析儀本身的陷阱：光譜分析儀 (Yokogawa AQ6375 + AQ6373) 用光柵把不同波長分開，但波長 λ 的光在「2λ」位置會出現二階繞射峰；SCG 在 900–1200 nm 區段強度很高，如果不擋，它在 1800–2400 nm 區會假裝成額外峰，把真正的長波長尾巴蓋住。所以作者在 1800–2400 nm 量測時插入兩片 Thorlabs FELH1250 long-pass filter（截止 1250 nm），擋掉 900–1200 nm 那段光，光柵就只能看到真正的長波長訊號。

4. 工具與材料: 
   - **43.7 mm Si₃N₄ 螺旋型色散工程波導 (D7802)**: 截面 2.07 µm × 0.70 µm 的 dispersion-engineered 波導，在 telecom C-band 附近接近零色散，是 SCG 噴顏色的舞台。
   - **Photonic damascene 製程 (Liu et al. 2021)**: D7802 樣品的製作流程，提供超低損、可工程化色散的 Si₃N₄ 波導。
   - **1550 nm lensed fiber**: 透鏡光纖，把 SMF 中的脈衝聚焦對到晶片邊緣 inverse taper，耦合損 ~2.5 dB。
   - **~10 m SMF 線性壓縮鏈**: 包含 WDM 後段、光隔離器 pigtail、偏振控制器與透鏡光纖共 ~10 m SMF，用 1550 nm 反常色散補償 Mamyshev 輸出的 chirp。
   - **自相位調變 (SPM)**: 強光自己改折射率產生隨時間變化的相位，瞬時頻率偏移把光譜噴寬。
   - **Yokogawa AQ6375 / AQ6373 OSA**: 兩台光譜分析儀並用以覆蓋從可見光到 2.4 µm 的全波長。
   - **Thorlabs FELH1250 long-pass filter**: 截止 1250 nm 的長通濾波器，量 1800–2400 nm 時擋掉 900–1200 nm 光，避免光柵 OSA 的二階繞射偽影。
5. 與此篇文章的關係: 
在《High-pulse-energy integrated mode-locked laser using a Mamyshev oscillator》這篇文章中，作者為了證明 nJ 級晶片 MLL 已經跨過驅動非線性效應的能量門檻，採用了直接驅動的 Si₃N₄ supercontinuum 量測。它解決了「過去整合 MLL 必須外接桌上型 EDFA 才能做 SCG」的瓶頸：吃進 Mamyshev 的 1 nJ 脈衝、經 ~10 m SMF 壓到 147 fs 後直接耦合進 43.7 mm 色散工程波導，產出 1.5-octave (736–2,331 nm) 的超連續光譜，為紅外光譜、OCT 與晶片化自參考頻率梳鋪好原料。
