# GelMA 合成與 NV-laden Hydrogel 製備

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): GelMA 合成與 NV-laden Hydrogel 製備
3. Method: 
   原始 gelatin（豬皮膠原蛋白水解產物）只在 30°C 以下會物理結凍，37°C 體溫就化開，撐不住 3D 列印形狀。作者在 gelatin 鏈上接一些「拉鍊牙齒」(甲基丙烯酸基團, methacryloyl group)，UV 照射時這些牙齒會彼此扣在一起、形成永久共價網——這就叫 gelatin methacryloyl (GelMA)。合成方法 (改自 Nichol 等與 Loessner 等的標準 protocol)：先把 gelatin 在 50°C DPBS 裡溶成 10% (w/v) 清澈溶液（50°C 避免它凝固），再「逐滴」加入甲基丙烯酸酐 (methacrylic anhydride, MA)，每 1 g gelatin 加 400 µl。MA 是疏水的、跟水不互溶；如果一次倒下去會在水面形成油層、被水水解成沒用的 methacrylic acid，逐滴加才能讓每一滴 MA 立刻被攪拌分散、遇到 lysine 胺基反應的機率最大。50°C 攪 2 h 後加 2 倍體積 DPBS 終止反應。接著裝進 12 kDa MWCO 透析膜 (SpectraPor) 在 40°C 透析 5 天、每天換水至少 2 次，把剩餘 MA 與 methacrylic acid（對細胞有毒）擴散出去——透析偷懶下游細胞會被毒死；最後 freeze-dry 得到乾的 GelMA 粉長期保存。

   使用時把乾粉溶在 DPBS 配成 7.5% GelMA、加 0.5% 光啟動劑 (Irgacure D-2959)，UV 照 20 秒就完成固化。背後的化學是這樣：甲基丙烯酸基團尾巴有 C=C 雙鍵，平時很穩定不會自己反應；Irgacure D-2959 吸收 UV 後裂成兩個自由基，自由基撞上 C=C 雙鍵把它打開、產生新自由基，連鎖反應 (chain-radical polymerization) 把鄰近 GelMA 鏈共價綁成永久網。為什麼挑 7.5% + 0.5% PI 這組數字？7.5% GelMA 是「軟硬剛好給細胞住」的折衷——低於 7.5% 太軟撐不住形狀、孔太大留不住 NV；高於 10% 太硬、細胞跑不動。0.5% PI 則是「夠快但不毒」的折衷——濃度太低自由基產量少、需要更長 UV 時間（長 UV 本身會殺細胞）；太高則 PI 殘留也有毒性。0.5% + 20 秒 UV 是這篇做出來的甜蜜點。

   嵌 NV 進 GelMA 不能直接把乾粉加進含 NV 的水裡——溶解 GelMA 需要 50–80°C，但 NV 是磷脂膜囊泡，這個溫度會把膜熔糊、表面辨識分子變性，內裝的 miRNA 提早漏光、EV 對 CF 的特異性也消失，hELs 兩大賣點同時失效。所以作者拐個彎用「等比稀釋」策略：先做好濃度兩倍的 15% GelMA + 1% PI 溶液（不含 NV，可放心加熱溶解）和 200 µg ml⁻¹ NV 懸浮液（常溫操作），要用時兩者 1:1 等體積混合，最終得到 7.5% GelMA + 0.5% PI + 100 µg ml⁻¹ NV 的目標配方。NV 只在最後混合那一刻短暫接觸溫溫液體，不必經歷溶解時的高溫長時間。
4. 工具與材料: 
   - **gelatin**: 豬皮膠原蛋白部分水解產物；本研究的明膠來源，30°C 以下結凍、37°C 體溫化開。
   - **methacrylic anhydride (MA)**: 雙頭甲基化試劑，可把甲基丙烯酸基團接到 gelatin 上的 lysine 胺基；疏水、會被水水解成 methacrylic acid，需逐滴加入。
   - **gelatin methacryloyl (GelMA)**: 明膠側鏈接上甲基丙烯酸基團後的衍生物，UV 照射可永久共價固化成水膠網。
   - **Irgacure D-2959**: Sigma 出的光啟動劑 (photoinitiator)，吸收 UV 後產生自由基啟動 GelMA 的連鎖聚合反應。
   - **SpectraPor 12 kDa MWCO 透析膜**: 孔徑只讓 12 千道爾頓以下小分子通過的透析膜，用來移除反應後殘留的 MA 與 methacrylic acid。
   - **freeze-dry / lyophilize**: 冷凍乾燥：在低溫真空下把水昇華掉，得到可長期保存的乾燥固體 GelMA 粉。
   - **UV photocrosslinking**: 光啟動劑吸收紫外光產生自由基、攻擊甲基丙烯酸基團的 C=C 雙鍵、把鄰近 GelMA 鏈共價綁成網的反應，約 20 秒完成。
   - **chain-radical polymerization**: 自由基連鎖聚合：自由基撞上 C=C 產生新自由基，再撞下一個，連鎖把單體綁成長聚合物或交聯網。
   - **DPBS**: 杜貝可氏磷酸緩衝液，pH 接近生理值的緩衝溶劑，用來溶解 gelatin/GelMA 與作為終止反應的稀釋液。
   - **等比稀釋策略**: 先各自做好濃度兩倍的 GelMA 溶液與 NV 懸浮液、再 1:1 混合，避免 NV 接觸高溫長時間溶解過程。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了把驗證過的 hELs 嵌進可 3D 列印的水膠基質，採用了 GelMA 合成搭配等比稀釋的 NV 嵌入法。這套方法解決了「明膠 37°C 會化、NV 又怕 50°C 高溫」的雙重瓶頸，把上游做好的 hELs 與下游待印的細胞同時打包進一個固化後不化、嵌入過程不傷 NV 的水膠墨水，為後續 SEM 孔徑、AFM 模數、3D 列印形狀保真度等實驗提供共用的水膠平台。
