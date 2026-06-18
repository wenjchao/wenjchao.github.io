# 1480 nm 雙端泵浦與 WDM 注入

1. 引用自哪篇 paper: high-pulse-energy-mamyshev-laser
2. Outline (任務主線): 1480 nm 雙端泵浦與 WDM 注入
3. Method: 
作者用兩台 1,480 nm 雷射雙端泵浦：Pump 1 是商用 Connet 半導體雙偏振合成模組 (820 mW)，Pump 2 是 Lumibird 的 Raman 光纖雷射（衰減到 959 mW），分別接到晶片兩端的 WDM 埠再送進晶片。為什麼挑 1,480 nm 而非 980 nm？鉺有兩個常用泵浦窗：980 nm 把鉺抬到更高能階後 phonon relaxation 跳下來、量子虧損大、效率較低；1,480 nm 直接抬到放大上能階、效率較高。更重要的是 1,480 nm 與訊號 1,550 nm 都在光纖通訊 C 波段附近，商用高功率 1,480 nm 雷射二極體、WDM、光纖元件成熟便宜——作者另外點名 Lumentum S35/S36 (600 mW) 與 Anritsu AF4B type E (650 mW) 兩款小封裝商用品作為未來可整合的替代選項。

為什麼要從「兩端」泵浦？1,480 nm 泵浦光被鉺吸收後本身會衰減：靠近泵浦端的鉺被點得很亮、遠端只剩零星亮著。如果只從一端泵浦，整條 42 cm 波導的反轉粒子數會從一端到另一端遞減，1,550 nm 訊號光跑過去時近端被放大很多、遠端反而被吸收（沒點亮的鉺仍是吸收態），整體增益反而不夠。從兩端同時泵浦，前後兩道指數衰減互相補位，腔內反轉粒子數沿軸向「U 形對稱」分佈，平均下來比單端均勻得多，整條波導都有正增益——這是 sub-meter 高增益腔能跑起來的關鍵。

WDM (波分多工器) 是一個三埠元件：一埠進 1,480 nm 泵浦、一埠出 1,550 nm 訊號、一個共用埠接到晶片。內部是一片薄膜濾波器：對 1,480 nm 透明、對 1,550 nm 反射。作者特地挑「1,480 pass / 1,550 reflect」版本（Ascentta FWDM-45-L-10-FA），這樣 1,550 nm 訊號從泵浦埠漏出去的隔離度更高、回到泵浦雷射造成寄生反射的風險更低。寄生反射在 Mamyshev oscillator 裡是大忌——Sec. 2-E 講過自啟動需要腔內寄生反射 < −42 dB，否則自啟動失敗，所以 WDM 隔離度的選擇與後續啟動策略直接綁定。

晶片邊緣有一段「漸縮」的 inverse taper 把波導從 350 nm 寬慢慢往外擴張，把光模式放大讓光纖端面對得上。對接的光纖叫 Coherent UHNA7（一種特高數值孔徑、模場很小的光纖），端面切得很平，被 Thorlabs NanoMax 微米級調整台架在晶片旁邊。兩個端面之間塗 Thorlabs G608N3 折射率匹配凝膠（n ≈ 1.5，剛好介於光纖 n ≈ 1.46 與晶片波導之間），消除空氣縫隙造成的 Fresnel 反射——這層凝膠的目的不只是省功率，更重要的是把界面磨平、避免反射回腔內變成寄生反射干擾自啟動。整片晶片放在 TEC 控溫的金屬塊上、用熱敏電阻回授維持溫度穩定。對位偏個 µm 耦合損耗就會從 1.26 dB 跳到 5 dB 以上，腔內功率瞬間不夠、雷射起不振；作者用同片無摻雜參考波導校準後，1,540–1,570 nm 平均 fibre-to-fibre 損耗 2.52 dB，扣除 SMF–UHNA7 接續損 0.62 dB 後單面耦合損 1.26 dB（理論模擬 1.45 dB）。

4. 工具與材料: 
   - **dual-end pumping**: 從晶片兩端同時注入 1,480 nm 泵浦，反轉粒子數沿軸向 U 形分佈、整條波導都有正增益。
   - **1480 nm pump diode**: 本論文用 Connet 半導體 (820 mW) 與 Lumibird Raman 光纖雷射 (959 mW) 雙端供泵；未來可換 Lumentum S35/S36 或 Anritsu AF4B 等小封裝商用品。
   - **WDM (Ascentta FWDM-45-L-10-FA)**: 薄膜濾波波分多工器，1,480 pass / 1,550 reflect，提升 1,550 nm 對泵浦的隔離度避免寄生反射。
   - **inverse taper**: 晶片端面的漸縮波導，把 350 nm 寬模式放大以對接光纖。
   - **UHNA7 lensed fiber**: Coherent 特高數值孔徑光纖，端面切平與晶片 inverse taper 對接。
   - **index-matching gel (Thorlabs G608N3)**: 折射率約 1.5 的凝膠塗在光纖–晶片接面，消除 Fresnel 反射避免寄生反射干擾自啟動。
   - **NanoMax flexure stage**: Thorlabs 微米級調整台，用於光纖–晶片對位。
   - **TEC**: 半導體致冷塊，配合 thermistor 回授維持晶片溫度穩定。
   - **coupling loss**: 光纖–晶片單面耦合損耗 1.26 dB（理論模擬 1.45 dB），由同片無摻雜參考波導校準。
5. 與此篇文章的關係: 
在《High-pulse-energy integrated mode-locked laser using a Mamyshev oscillator》這篇文章中，作者要在 42 cm 的 Er:Si3N4 波導內建立空間平均的反轉粒子數以提供 Mamyshev oscillator 所需的高增益。雙端 1,480 nm 泵浦 + 「1,480 pass / 1,550 reflect」WDM 注入解決了「單端泵浦造成遠端反吸收」與「寄生反射破壞自啟動」這兩個瓶頸，把兩台商用泵浦雷射的功率有效送進晶片並把 1,550 nm 訊號乾淨抽出，是 Sec. 2-E 自啟動鎖模與 Sec. 2-F 脈衝壓縮能拿到 nJ 級輸出的功率前提。
