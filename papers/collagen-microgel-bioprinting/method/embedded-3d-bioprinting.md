# 客製化雙頭擠出生物列印 (Embedded 3D Printing)

1. 引用自哪篇 paper: collagen-microgel-bioprinting
2. Outline (任務主線): 客製化雙頭擠出生物列印 (Embedded 3D Printing)
3. Method: 
作者列印的關鍵設計是「固定 E/Δx」。E 是注射針筒活塞推進的距離，Δx 是龍門走過的列印路徑長；固定 E/Δx 等於「龍門每走 1 mm 路徑，活塞就推進固定一段」，每 1 mm 列印絲擠出的墨水體積一樣，細絲粗細不會因走得快慢而改變。在這個約束下，作者只剩 F（龍門速度）一個旋鈕：F 變大、龍門走得快，活塞為了維持 E/Δx 也必須跟著推得快，於是流率 Q̇ 隨之變大（Equation 1）。流率變大會立刻拉高壁面剪切率——靠近針頭內壁的那一層被黏在金屬壁上幾乎不動，管軸中心的墨水跑得最快，速度從壁面 0 到中心最大這個陡度就是剪切率；Equation 2 把流率、針頭半徑 R 與墨水的剪切變稀指數 n 整合成壁面剪切率 γ̇_w。如果 E/Δx 不固定，F 變大時會同時動到「每 mm 擠出量」與「剪切率」兩件事，孔隙率變化就分不清是哪個造成的——固定後 F 才成為乾淨的單一變數。

硬體是把 MakerGear M2 Rev E 塑膠列印機的熱擠出頭整個拆掉，換上能夾兩支 Replistruder 4 注射泵的雙擠出口模組——一支可裝 PHYS 墨水、一支裝 SPAAC 墨水，在同一次列印中切換而不需手動換針；控制板換成 Duet 2 WiFi + RepRapFirmware，可由 G-code 直接驅動兩支注射泵的活塞推進速率與龍門 F 同步協調。CAD 模型則由 Simplify3D 切片成 G-code。針具用 2.5 mL 氣密注射筒搭 27 G 平頭針：G 數字越大孔越小，27 G 對應內徑 ID = 210 μm；平頭針是 360° 對稱圓孔，避免斜口造成方向性偏流。預設 extrusion width 0.21 mm 剛好對應 27 G 的內徑、layer height 0.084 mm 約為 ID 的 0.4 倍（確保層間融合）、print speed 15 mm s⁻¹（掃描 0.1–30 mm s⁻¹ 範圍的中間值）。變因研究中另用 22 G（粗）與 32 G（細）針，量測不同內徑對剪切率與孔隙率的影響。

三種墨水的列印與交聯溫度都對應它們自身的物理：35 mg mL⁻¹ Lifeink 濃度高、分子距離短、自組裝速度快，特別在低速列印時針頭內滯留時間長，沒控好溫度就先在針內變果凍堵住，因此整個列印過程要在 4 °C 進行；6 mg mL⁻¹ unmodified collagen 與 collagen-azide 濃度低、自組裝慢得多，且 collagen-azide 根本無法靠物理路徑成網，室溫列印即可。列印完的交聯方案也不一樣：PHYS 在支撐浴內 37 °C × 45 min 加熱誘導自組裝；SPAAC 則必須留在室溫 × 2 h 等 PEG-BCN 從浴擴散進墨水反應——因為如果 SPAAC 也用 37 °C，明膠微粒浴會在 SPAAC 還沒交聯完就先融化，撐住形狀的浴消失、整個列印立刻塌掉。釋放成品時也是順著浴的物理特性：Pluronic 4 °C 液化、明膠微粒 37 °C 融化、Carbopol 無溫度可逆性需反覆強力沖洗；三種都要再用 PBS 充分洗一次。

細胞列印有兩個額外風險。第一是無菌：整套必須搬進無菌生物安全櫃進行，否則 7 天培養就會被污染。第二是剪切損傷：剪切率太高的針頭出口會對細胞造成機械損傷，作者選 27 G + 15 mm s⁻¹ 的組合對應約 2 500 s⁻¹，corneal MSCs 仍能維持 >95% 存活率（Live/Dead 確認）。如果走極端參數（例如 32 G 細針配 30 mm s⁻¹ 高速），雖然能掃出極高剪切率，但細胞還沒開始觀察就先死了。所以細胞列印通常守在預設參數，變因研究多半用無細胞墨水跑。
4. 工具與材料: 
   - **E/Δx 固定**: 龍門每走 1 mm 路徑，活塞推進固定一段，每 mm 填絲擠出的墨水體積不變；使 print speed F 成為調控流率與壁面剪切率的單一變數。
   - **Equation 1 (flow rate)**: $\dot{Q} = A \times \dfrac{E}{\Delta x / F}$；A 為針筒截面積，把列印速度 F 翻譯成墨水流率。
   - **Equation 2 (wall shear rate)**: $\dot{\gamma}_w = \dfrac{\dot{Q}}{\pi R^3}\left[3 + \dfrac{1}{n}\right]$；對 power-law 流體計算貼著針頭內壁那一層的剪切率。
   - **MakerGear M2 Rev E + Replistruder 4 + Duet 2 WiFi**: 把塑膠列印機改裝成雙頭注射泵生物列印機的硬體組合：拆掉熱擠出頭、加裝兩支可獨立驅動的 Replistruder 4 注射泵、控制板換成 Duet 2 WiFi + RepRapFirmware。
   - **Simplify3D → G-code**: 切片軟體，把 3D CAD 模型轉成龍門與兩支注射泵協調動作的 G-code 指令。
   - **27 G blunt-tip nozzle (ID = 210 μm)**: 27 號規格的平頭針，內徑 210 μm；360° 對稱圓孔避免方向性偏流，預設配 15 mm s⁻¹ 對應約 2 500 s⁻¹ 剪切率。
   - **Cell-laden printing parameters**: 27 G + 15 mm s⁻¹ + 3 × 10⁶ cells mL⁻¹ corneal MSCs；在無菌生物安全櫃內進行，存活率 >95%。
   - **Crosslinking + release protocol**: PHYS 37 °C × 45 min；SPAAC 室溫 × 2 h；釋放方式對應浴特性：Pluronic 4 °C 液化、gelatin MP 37 °C 融化、Carbopol 反覆沖洗。
5. 與此篇文章的關係: 
   在《Embedded 3D Bioprinting of Collagen Inks into Microgel Baths to Control Hydrogel Microstructure and Cell Spreading》這篇文章中，作者為了在同一台機器上掃描廣域剪切率、把孔隙率變化乾淨地歸因於剪切率，採用了改裝的雙頭擠出列印機並嚴格固定 E/Δx。這套設計解決了「改變列印速度同時改了填絲量與剪切率、變因混雜」的瓶頸，產出一系列覆蓋 0.1–30 mm s⁻¹ 的 PHYS / SPAAC 細胞列印樣品，直接交給下游 confocal 影像與 FIJI 量化分析。
