# Lumerical 3D FDTD 本徵模、Q 因子與遠場模擬

1. 引用自哪篇 paper: ultrasmall-dielectric-plasmonic-nanolasers
2. Outline (任務主線): Lumerical 3D FDTD 本徵模、Q 因子與遠場模擬
3. Method:
3D 有限差分時域法 (finite-difference time-domain, FDTD) 直接把描述電磁場行為的 Maxwell 方程「切成很小的空間格子與很短的時間步」，每一步用相鄰格子的電場更新本格子的磁場、下一步再反過來，就這樣讓場「一格一格地跳動」；優點是不假設任何解析形狀，任意奇怪的幾何、金屬、介電材料都能算，特別適合本論文「圓盤上多層薄膜 + 金屬基板」的複雜結構。作者要「找出」奈米盤的本徵模時，會在半導體內部塞一顆虛擬的電偶極 (electric dipole) 讓它「叮」一下同時發出所有頻率，只有腔真的能容納的頻率會在裡面來回反射不散；再擺一個 point-like time monitor 記錄某位置的 $E(t)$，做快速傅立葉轉換 (FFT) 進頻域，出現的尖峰就是本徵模。要看場長什麼樣還會擺一大片 2D 場監控器覆蓋整個模擬區，配上時間 apodization（中心 420 fs、寬度 100 fs 的高斯窗）濾掉 dipole 剛啟動的暫態，只取穩態訊號進 FFT，抽出來的模態圖才乾淨——這就是 Figure 2f、3b 那種彩色場圖的來源。

模擬精度靠三件事一起頂：mesh grid、邊界、材料常數。網格必須 ≤ 5 nm——工作波長 660 nm 進到折射率 3.4 的 InGaP 內部，介質裡的波長只剩約 200 nm；SPP 更是把場塞進金屬-半導體界面幾十奈米的薄層，格子太粗根本畫不出來。FDTD 用長方體格子逼近彎的圓盤邊界會出現「梯狀誤差」，作者在介面附近再套 Yu-Mittra 精修把這個階梯效應平均掉，讓模態頻率不會因假樓梯漂移。邊界用 perfectly matched layer (PML)——一層「無反射吸波海綿」，把出射的電磁波吸乾淨，模擬區看起來像通到無限遠的開放空間；若換成硬邊界，出射光會被反射回腔內產生假共振峰，Q 值也會被灌爆。材料常數方面，金的複折射率虛部直接決定 SPP 損耗，差一點點 Q 值就會偏 30-50%；作者選 CRC Handbook (Haynes, Lide, Bruno, 2016, ref 26) 這個標準參考來源，跟先前 CsPbBr₃ 電漿子雷射工作 (Cho et al., Sci. Adv. 2021) 使用同一組值，兩篇論文的模擬結果才彼此可比。

取模態頻譜峰的中心頻率 $\varpi_{\mathrm{res}}$ 與峰的半高全寬 $\Delta \varpi_{\mathrm{res}}$ 相除就是 $Q = \varpi_{\mathrm{res}} / \Delta \varpi_{\mathrm{res}}$，物理意義是「這個模態能量在腔裡存多久」——峰窄、Q 就高。460 nm disk-on-pillar 的 TE₄₁ 模 $Q \sim 430$ 屬於「乾淨腔」；360 nm disk-on-gold 的 SPP 高階 WGM $Q \sim 30$ 屬於「漏很快」，但因為 Purcell 因子 $F_m \approx 19$（相較純介電 2.3）夠大，仍能雷射。作者還額外算遠場輻射圖：近場 $|E|$ 分佈負責認出模態編號（TE₄₁ vs 高階 SPP），但光學實驗端量到的是離樣品很遠、進到物鏡的那束光的角度分佈；FDTD 把近場透過 near-to-far field 轉換到球面上得到遠場圖，才能跟 Figure 2e、3f 的 EMCCD 實測影像對號入座，宣稱「觀察到的模就是預測的模」。

若把 mesh 拉到 20 nm，遠比 SPP 場在金屬-半導體界面上的變化尺度粗——場的細節根本畫不出來，模擬出的 SPP 模會變得又淺又寬、Q 值嚴重低估，甚至看不到強耦合的快分量；輸出的 Purcell factor 直接失真，設計會被誤導。少了 Yu-Mittra 精修，圓盤側壁在格點上是階梯狀不平滑，共振頻率會漂 3-10 nm——奈米雷射的 gain band 才 80 nm 寬，這種漂移就足以讓「本來會雷射的尺寸看起來不會」的錯誤結論。所以 5 nm 網格與 Yu-Mittra 精修在此設計中不是可選項而是必要條件。
4. 工具與材料:
- **Lumerical 3D FDTD**: 本篇使用的商用 finite-difference time-domain 電磁模擬軟體，把 Maxwell 方程在空間格與時間步上離散化。
- **Electric dipole excitation**: 在腔內置一個虛擬電偶極廣頻激發所有模態，讓腔本身容納的頻率在裡面持續反射，用來抽出本徵模。
- **Mesh grid ≤ 5 nm**: 空間離散化尺寸；必須遠小於介質內波長 (~200 nm) 及 SPP 場厚度 (幾十 nm) 才能解析。
- **Yu-Mittra mesh refinement**: 在圓盤介面附近做特別精修，修正 FDTD 長方體格子逼近彎邊時的階梯誤差。
- **PML (perfectly matched layer)**: 邊界吸收層；無反射地吸掉出射電磁波，讓模擬區等效為開放空間，避免假共振。
- **Point-like time monitor + FFT**: 抽本徵模的核心操作：記錄某位置電場隨時間變化 $E(t)$，做快速傅立葉轉換進頻域，尖峰即為模態。
- **2D field monitor array**: 覆蓋整個模擬區的近場記錄面，配合時間 apodization 抽出模態的空間分佈圖。
- **時間 apodization (420 fs / 100 fs)**: 高斯窗函數，濾掉 dipole 剛啟動的暫態訊號只保留穩態，讓 FFT 出的模態圖乾淨。
- **Q factor = $\varpi_{\mathrm{res}} / \Delta \varpi_{\mathrm{res}}$**: 共振峰中心頻率除以半高全寬，代表能量在腔中儲存的相對時間；460 nm disk-on-pillar TE₄₁ Q~430、360 nm disk-on-gold SPP Q~30。
- **Purcell factor $F_m$**: $F_m = \frac{3}{4\pi^2}(Q_m/V_m)(\lambda/n)^3$；SPP 靠極小 $V_m$ 把 $F_m$ 拉到 19，即使 Q 低仍能主導自發輻射通道。
- **CRC Handbook 金光學常數**: 取自 CRC Handbook of Chemistry and Physics (Haynes, Lide, Bruno, 2016, ref 26)；SPP 損耗對複折射率虛部極敏感，此為兩篇論文可比之關鍵。
- **Near-to-far field transform**: 把近場資料轉換到球面遠場，得到 EMCCD 實測可對照的遠場輻射圖，確認觀察到的模態階數。
5. 與此篇文章的關係:
在《Ultrasmall InGa(As)P Dielectric and Plasmonic Nanolasers》這篇文章中，作者要在製作元件前先判斷「哪個直徑、哪種基板真的能雷射」。為此他們用 Lumerical 3D FDTD 模擬吃進奈米盤幾何與金的光學常數，吐出本徵模型的電場分佈、Q 因子、Purcell 因子與遠場輻射圖，直接指導 460 nm 純介電盤與 360 nm 電漿子盤的設計，並在量測後與 EMCCD 影像對號入座解讀模態階數，為 TRPL 與雷射閾值資料提供理論骨架。
