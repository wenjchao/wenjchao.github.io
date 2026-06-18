# 動態光散射微流變 (DLSμR) 與創變遵從性量測

1. 引用自哪篇 paper: collagen-microgel-bioprinting
2. Outline (任務主線): 動態光散射微流變 (DLSμR) 與創變遵從性量測
3. Method: 
DLSμR 的核心是「在凝膠裡放一群被熱能推著跑的探針，看它們能跑多遠」。作者把 2 μm 大小的塑膠小球拌進膠原凝膠裡——這個尺寸特別重要：比膠原網絡的孔大很多，粒子被網絡卡在原地，能反映網絡本身的力學；如果用 0.2 μm 級小粒子，會直接從網絡孔之間鑽過去，量到的就只是孔內水的黏度。表面 PEG 修飾也很關鍵：未修飾的塑膠球會吸附膠原、被黏死在網絡上動不了；羧酸基 (-COOH) 則讓粒子帶負電不結團、均勻分散。膠化後，這些小球被熱能推著做布朗運動。一道 633 nm 雷射打進樣品池，被小球散射出來的光強度隨小球位置而漲落——漲落越快、代表小球跑得越遠、凝膠越軟。Zetasizer 用 173° 反向角度（避免穿透樣品本身吸收）收散射訊號，計算出小球位置隨時間的「平均平方位移」MSD ⟨Δr²⟩(t)。

光有 MSD 還不是力學量，作者用 Equation 3 把它翻譯成 creep compliance J(t)：$\langle \Delta r^2 \rangle = \frac{k_B T}{\pi a} J(t)$。J(t) 的意思是「在凝膠上施一個固定大小的力，凝膠會慢慢凹下去」——凹下去的速度與深度，除以你施的力，就是 J(t)，單位是每 Pa 應力造成多少應變。J(t) 越大代表材料越軟、越容易被慢慢拉變形。Equation 3 的物理是「廣義 Stokes–Einstein 關係」：粒子被熱能 k_B T 推著走、被周圍材料黏住，能跳多遠跟材料的軟硬有關；把粒子半徑 a 代進去做幾何修正後，MSD 就能直接換成 J(t)。前提有兩個：粒子只被熱能驅動（被動微流變）、粒子位移夠小不擾動網絡（線性響應）。

Bulk rheometer 量「慢攪」（低頻）時有三個現實問題：擺動一次要好幾分鐘、夾在板間的薄樣品邊緣會脫水、凝膠本身可能還在持續結構演化，三件事疊起來讓低頻段數字不可信。DLSμR 沒有這些麻煩——樣品裝在 40 μL 密封 cuvette 不會蒸發；不施外力，凝膠保持原狀；探針本身是熱被動運動，幾小時的量測都不會破壞網絡。所以 DLSμR 補上了 bulk rheometer 不可靠的「小時等級慢鬆弛」這段——這正好是細胞用力拉扯網絡的時間尺度。作者明文要求 37 °C 控溫（PHYS 在低溫下會更穩定，誤控溫則 J(t) 混入溫度依賴性）、40 μL 密封 cuvette 防蒸發、n ≥ 3 重複，並避免粒子聚集（聚集後幾顆變成一團大物移動緩慢、MSD 被低估、凝膠看起來比實際硬）。

為什麼這個方法在這篇是不可取代的？Bulk rheometry 雖然可以看到 PHYS 在低頻 G' 開始下降的趨勢，但 0.1 rad s⁻¹ 對應的時間尺度大約 10 秒，遠短於細胞收縮的小時級拉扯。如果只靠 bulk 數據，作者最多只能說「PHYS 比 SPAAC 在低頻下軟一點」，無法直接證明「在細胞作用的時間尺度上，PHYS 還在持續變形而 SPAAC 完全卡住」。DLSμR 把時間軸拉長到幾小時，量到的 J(t) 顯示 PHYS 持續上升、SPAAC 平坦——這才是「細胞拉七天 PHYS 縮到 25%、SPAAC 維持 >90%」這個現象的力學根源。少了 DLSμR，整篇論文「網絡時間鬆弛 → 細胞引致收縮」的核心因果鏈就斷了。
4. 工具與材料: 
   - **Zetasizer Nano ZS (633 nm laser, 173° backscatter)**: Malvern 的 DLS 儀器，用反向角度收集小球散射光的漲落，計算 MSD。
   - **2 μm PEG-coated carboxylated latex tracer**: 尺寸大於膠原網絡孔的探針小球；PEG 防止吸附膠原、羧酸基防結團，確保只受熱能驅動且均勻分散。
   - **Mean square displacement (MSD, ⟨Δr²⟩)**: 探針位置隨時間的平均平方變化量，反映「小球能跳多遠」、即材料的局部軟硬。
   - **Creep compliance J(t)**: 單位應力下的應變隨時間變化；越大表示材料越軟、越容易被慢慢拉變形。
   - **Equation 3 (generalized Stokes–Einstein)**: $\langle \Delta r^2 \rangle = \frac{k_B T}{\pi a} J(t)$；把 MSD 直接翻譯成 J(t) 的物理關係。
   - **Passive microrheology**: 不施外力，只靠熱能推動探針的微流變模式；可在 37 °C、長時間、密封 cuvette 中安全量測。
   - **40 μL cuvette + 37 °C control**: 密封小體積樣品池與精確控溫，避免蒸發與 PHYS 溫度依賴性混入量測結果。
5. 與此篇文章的關係: 
   在《Embedded 3D Bioprinting of Collagen Inks into Microgel Baths to Control Hydrogel Microstructure and Cell Spreading》這篇文章中，作者為了在細胞時間尺度上量化 PHYS 與 SPAAC collagen 的力學差異，採用了動態光散射微流變 (DLSμR) 量測 creep compliance J(t)。這套被動探針方法解決了「bulk rheometer 在低頻段受蒸發、漂移與線性度限制無法可信量到小時級鬆弛」的瓶頸，產出 PHYS J(t) 持續上升、SPAAC J(t) 平坦的關鍵時域曲線，直接支撐「細胞引致收縮差異來自網絡時間鬆弛」的核心因果論證。
