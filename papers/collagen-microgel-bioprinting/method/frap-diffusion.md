# 螢光恢復後光漂白 (FRAP) 量測擴散係數

1. 引用自哪篇 paper: collagen-microgel-bioprinting
2. Outline (任務主線): 螢光恢復後光漂白 (FRAP) 量測擴散係數
3. Method: 
作者要量交聯劑 PEG-BCN 從支撐浴擴散進墨水的速度，但 PEG-BCN 本身不發光、FRAP 看不見它，所以改用一個分子量同為 20-kDa、卻能發出綠色螢光的『替身』——20-kDa 螢光葡聚醣 (FITC-dextran)——作為擴散替代物。具體做法是螢光恢復後光漂白 (Fluorescence Recovery After Photobleaching, FRAP)：把摻了 1 mg/mL 螢光葡聚醣的墨水或支撐浴裝進 96 孔盤，在共軛焦顯微鏡 (confocal) 下用 488 nm 雷射對著 110 × 110 μm 的小方塊全功率照 60 秒，把方塊內的螢光分子通通『漂白』成不再發光；接著改用弱光成像 90 秒，看周圍未漂白的分子靠隨機熱運動 (Brownian motion) 慢慢游回來把方塊重新填亮。亮度恢復得越快，分子在這個介質裡的擴散係數 (D) 就越大；強度恢復曲線交給 MATLAB 的 frap_analysis 程式 (Jönsson et al. Biophys. J. 2008) 擬合費克擴散 (Fickian diffusion) 解就能算出 D。

至於為什麼非要挑 20-kDa 不可：擴散速度跟分子大小直接相關，替身必須跟本尊體積匹配，PEG-BCN 是 20-kDa，葡聚醣也必須是 20-kDa。而 FITC-dextran 還是市售、不帶電、不會跟 collagen 非特異性黏附的中性擴散探針——換成更小的（例如 4-kDa）會跑太快、低估擴散時間；換成更大的反過來會高估；換成會跟 collagen 黏住的分子則完全失真。漂白時間 60 秒、漂白區 110 μm 也是經驗折衷：太短會漂不乾淨，太小則周圍分子瞬間就填回，儀器拍不到足夠時間點供擬合。

結果是明膠微粒浴內 D ≈ 50 μm²/s、collagen-azide 墨水內 D ≈ 65 μm²/s。然而 COMSOL 後續模擬會把 D 當『時間不變常數』算，所以作者特地在『正在交聯』的 SPAAC 樣品上每隔一段時間重做 FRAP，發現 2 小時內探針 D 維持在 60–70 μm²/s 幾乎沒變——意思是 SPAAC 凝膠化過程並沒有把 20-kDa 分子困住，恆定 D 假設成立。這兩個 D 因此被直接餵進 COMSOL Fickian 擴散模型，用來預測 PEG-BCN 從浴擴散進列印絲內部需要多久才能完成交聯。
4. 工具與材料: 
   - **FRAP (Fluorescence Recovery After Photobleaching)**: 螢光恢復後光漂白：在共軛焦下用 488 nm 雷射把小方塊內螢光分子漂白，再追蹤周圍分子游回來填亮的速度以求得擴散係數 D。
   - **20-kDa FITC-dextran**: 市售、中性、不黏 collagen 的螢光葡聚醣，分子量與 PEG-BCN 同為 20-kDa，作為 PEG-BCN 的擴散替代物。
   - **擴散係數 D**: 分子在介質中隨機熱運動造成的擴散快慢；在明膠微粒浴 ≈ 50 μm²/s、collagen-azide 墨水 ≈ 65 μm²/s。
   - **frap_analysis MATLAB 程式**: Jönsson et al. Biophys. J. 2008 提供的標準 FRAP 擬合工具，用於從亮度恢復曲線計算 D。
   - **Fickian diffusion**: 費克擴散：以濃度梯度推動的標準擴散方程，是 FRAP 擬合與下游 COMSOL 模擬共用的物理框架。
   - **STELLARIS 5 confocal (Leica)**: 本實驗用的共軛焦顯微鏡，同時擔任漂白與成像。
5. 與此篇文章的關係: 
   在《Embedded 3D Bioprinting of Collagen Inks into Microgel Baths to Control Hydrogel Microstructure and Cell Spreading》這篇文章中，作者為了在不殺死細胞的前提下交聯 SPAAC collagen，把 PEG-BCN 預先溶在支撐浴裡讓它擴散進列印絲。為了確認『2 小時擴散是否足夠完成交聯』，作者用 FRAP 量出 20-kDa 螢光葡聚醣作為 PEG-BCN 替身的擴散係數，把 D ≈ 50 μm²/s（浴）與 65 μm²/s（墨水）兩個輸入交給下游 COMSOL 模擬使用。
