# DLS 量測 size / PdI / Zeta-Potential 的解析

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): DLS 量測 size / PdI / Zeta-Potential 的解析
3. Method: 
   DLS (Dynamic Light Scattering) 不是直接「看」顆粒大小，而是量「顆粒在水裡跳得多快」反推。把雷射打進稀釋的奈米顆粒懸浮液，顆粒因水分子熱擾動隨機跳動 (Brownian motion)，會讓散射光強度隨時間快速波動。越小的顆粒在水裡跳得越快、散射光波動頻率越高。儀器把這個波動算成「自相關函數」(autocorrelation)，透過 Stokes-Einstein 關係反推出「流體力學直徑」(hydrodynamic size)——這個尺寸是「顆粒+其表面水化層」一起跳動時的有效直徑，比電鏡看到的乾燥粒子稍大。第二個參數 PdI (Polydispersity Index) 數學上等於「尺寸分佈的標準差除以平均尺寸」再平方，反映群體的均一度；0 代表所有顆粒大小完全一樣，0.3 是業界公認的「單分散」門檻，0.7 以上代表分佈寬到不能用單一群體描述。第三個參數 zeta potential 量的不是顆粒表面總電荷，而是「水化層外緣與自由水之間的電位差」——也就是顆粒在水裡「能影響到的有效靜電勢」。儀器在毛細管池兩端加電場、量顆粒的電泳遷移速度，再透過 Henry's equation 換算 zeta；越負（或越正）的顆粒彼此排斥越強、越穩定，接近 0 則容易聚集沉澱。Malvern Zetasizer Nano ZS 的標準設定也有講究。Scattering angle 173° 是「反向散射」模式，避免多次散射雜訊；refractive index 1.471 是磷脂膜系統的代表性折射率；absorbance 0.01 對應稀釋後的低吸光度。樣品在 ultrapure water 中稀釋至 200 µg/ml 是訊噪比的甜蜜點；用 ultrapure water 而不是 PBS 是因為 PBS 的高離子強度會壓縮水化層、把 zeta 拉接近 0（Debye 屏蔽），培養基的蛋白質則會吸附到表面改變化學。

   為什麼三個參數一起看就能判斷「hELs 物理上更接近 Lip 還是 EV」？三個參數獨立但互補。如果 hELs 只是物理混合而非真融合，DLS 應該看到雙峰、PdI 飆高；單一峰且 PdI ~0.25 代表 hELs 是均一群體，不是 Lip+EV 共存。尺寸上 hELs (37.31 nm) 跟 EV (37.45 nm) 幾乎一樣、明顯小於 Lip (52.13 nm)，代表 hELs 的整體骨架尺寸由 EV 主導。zeta potential 上 hELs (-12.3 mV) 介於 EV (-5.6 mV) 跟 Lip (-35.67 mV) 之間，代表表面被 Lip 的負電磷脂頭拉得更負——這正是 Lip 磷脂插入 EV 膜的化學證據。為什麼 hELs 尺寸跟 EV 接近而不是 Lip+EV 平均？Lip 大是因為 zeta 很負，磷脂間靜電排斥強、膜被撐開沒法緊密捲；hELs 的 zeta 落到 -12.3 mV，磷脂排斥力弱化，膜可以捲得更緊。再加上 sonication 製造的膜片段在重組時，小球比大球能量更穩定。三個參數一起讀：hELs 是融合產物，骨架像 EV、表面化學像 Lip 的混血版。如果只量 size + PdI、不量 zeta，會錯過這個融合驗證——Size + PdI 無法區分「真融合」跟「只是被 sonication 打變形的 EV、根本沒摻 Lip」這兩個假設；zeta 才是區分的化學指紋，跟 FRET 結果交叉驗證才完整。另一個失敗情境是 PdI 失控：如果是 0.6 而不是 0.25，代表分佈寬到 size 跟 zeta 平均值都會被多個群體拉扯到誰也不像的數字。本研究三組都 ~0.25 算過關，才有資格用平均值做後續比較。
4. 工具與材料: 
   - **DLS (Dynamic Light Scattering)**: 用雷射打散射光量顆粒 Brownian motion，反推流體力學直徑、PdI、zeta potential 三組互補參數。
   - **Hydrodynamic size**: 顆粒+水化層一起跳動時的有效直徑，比電鏡看的乾燥粒子稍大。
   - **PdI (Polydispersity Index)**: (尺寸標準差/平均) 的平方，反映群體均一度；< 0.3 算單分散、> 0.7 代表多群體混合。
   - **Zeta potential**: 水化層外緣與自由水之間的電位差，反映顆粒有效靜電勢；越負越穩定不團聚。
   - **Backscatter angle 173°**: DLS 反向散射模式，避免多次散射雜訊，對較濃樣品更準。
   - **Refractive index 1.471**: 磷脂膜系統的代表性折射率，DLS 反推大小時需要此值校正光傳播。
   - **Stokes-Einstein relation**: 把顆粒在水中的擴散係數轉換成流體力學直徑的物理公式。
   - **Henry's equation**: 把電泳遷移率轉換成 zeta potential 的物理公式。
   - **Debye 屏蔽**: 電解液離子壓縮顆粒水化層、把 zeta 拉接近 0 的現象；DLS 量 zeta 因此不能用 PBS。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了證明 hELs 是真融合產物而不只是物理混合，採用了 DLS 同時量 size / PdI / zeta potential 的三參數策略。這套方法解決了單一物理參數無法區分「真融合 vs. 物理混合」的瓶頸，輸入是 200 µg/ml ultrapure water 稀釋的 NV 懸浮液，輸出是「骨架像 EV、表面像 Lip 的混血版」這個融合驗證結論，與 FRET 結果交叉驗證並為下游 hEL 在水膠中的鍵結強度差異提供物理基礎。
