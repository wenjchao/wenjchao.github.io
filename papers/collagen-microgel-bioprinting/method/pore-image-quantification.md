# 孔洞分數與直徑的影像量化

1. 引用自哪篇 paper: collagen-microgel-bioprinting
2. Outline (任務主線): 孔洞分數與直徑的影像量化
3. Method: 
PHYS 與 SPAAC 兩種膠原蛋白的網絡結構不同，作者用兩種成像模式分別取得『有膠 vs. 沒膠』的可分割對比。PHYS collagen 由自組裝纖維束構成，作者用 STELLARIS 5 共軛焦顯微鏡 (Leica) 的『反射模式 (confocal reflectance)』——讓雷射打進去後偵測纖維邊界散射回來的光，纖維亮、空隙黑。SPAAC collagen 是化學鎖死的均質網絡，沒有大尺度散射對比，作者改在 collagen-azide 上預混 1:20 的 AlexaFluor647 螢光標記，用螢光模式拍——膠的地方紅色螢光、洞的地方無訊號。兩條路都用共軛焦的針孔 (pinhole) 拒絕焦點外散射光，能沿 z 軸做光學切片 (圖 S4)、確認孔洞在絲的內部全層都有，而不是表面假象。

影像取得後進入量化階段，全程在 FIJI (ImageJ2, Version 2.3.0/1.53f, Schindelin et al. 2012 Nat. Methods, ref [73]) 完成。作者用閾值法 (thresholding) 把灰階影像二值化——亮度高於門檻 = 有膠 (白)、低於門檻 = 沒膠 (黑)，FIJI 自動抓出每塊黑區的面積、周長、直徑：『黑塊總面積 / 全圖面積』就是 void fraction；『黑塊最大跨距』就是 void diameter；孔徑直接用 FIJI 在影像上量距離得到分佈。細胞形態用同樣的 thresholding 流程從 CellTracker 標記影像中抓出 2D 投影面積與周長，面積 < 10 μm² 的物件被當雜訊濾除（一顆 corneal MSC 投影遠大於這個下限，小於這個值的幾乎必定是染色雜訊或細胞碎片）。最後用圓度公式 $\text{Circularity} = 4\pi \cdot \text{Area}/\text{Perimeter}^2$ 描述細胞攤開的程度——完美圓 = 1、細長伸展接近 0，取代主觀的『鋪展 vs. 不鋪展』二分判讀。整體收縮量則由 THUNDER imager (Leica, 2.5X air) 做整盤 tile-scan、再用 FIJI 量列印盤直徑。

為了讓量化結果可信，每樣品至少拍 5 個不同視野——膠內孔洞與細胞分布不均勻，單一視野可能落在密度局部極值，多視野取樣才能反映整體平均與標準差、讓後續 ANOVA 與 Mann-Whitney 檢定有意義。兩條主要失誤要避開：閾值挑太低會把不均勻染色的暗角誤判成孔、嚴重高估孔隙率；挑太高則把真的小孔誤判成材料、低估孔隙率，所以每張影像必須視覺檢查門檻一致。第二，用連續量圓度取代『鋪展 vs. 不鋪展』二分判讀——二分仰賴觀察者主觀直覺、不同人標準會漂移，圓度則保留分布尾端資訊、可做非參數統計。
4. 工具與材料: 
   - **Confocal reflectance**: 共軛焦反射模式，偵測 PHYS collagen 纖維邊界散射回來的光，纖維亮、空隙黑。
   - **Fluorescence microscopy + AlexaFluor647 1:20**: 對 SPAAC collagen 用螢光模式：在 collagen-azide 上預混 AlexaFluor647 標記，膠的地方紅色、洞無訊號。
   - **STELLARIS 5 confocal (Leica)**: 高解析共軛焦顯微鏡，搭配 10X 空氣、20X/40X 油浸物鏡拍微結構與細胞影像。
   - **THUNDER imager (Leica, 2.5X)**: 拍整盤 tile-scan 用，追蹤 7 天的收縮量。
   - **FIJI (ImageJ2, Version 2.3.0/1.53f)**: 影像量化的核心軟體；用閾值法二值化後抓黑塊面積、周長、直徑。
   - **Void fraction**: 二值化後『黑塊總面積 / 全圖面積』，量化孔隙率。
   - **Circularity = $4\pi \cdot \text{Area}/\text{Perimeter}^2$**: 細胞形態的無因次圓度指標，完美圓 = 1、伸展接近 0，取代主觀二分判讀。
   - **10 μm² 雜訊閾值**: 面積 < 10 μm² 的物件視為雜訊濾除，避免染色偽影汙染圓度統計。
   - **≥ 5 視野/樣品**: 每樣品至少 5 個不同視野，反映整塊膠的平均與標準差。
5. 與此篇文章的關係: 
   在《Embedded 3D Bioprinting of Collagen Inks into Microgel Baths to Control Hydrogel Microstructure and Cell Spreading》這篇文章中，作者要把『微結構』從顯微鏡影像翻譯成可統計、可比較的量化指標，否則無法驗證 3-A、3-B 推導的設計法則。為此作者用共軛焦反射 (PHYS) 與螢光 (SPAAC) 兩種成像策略取得對比，再以 FIJI 的閾值法量化 void fraction、void diameter 與細胞圓度。這套量化流程提供了 Figure 2–4 所有條形圖與 p 值背後的數據基礎，把『印出來長什麼樣』變成可被 ANOVA 或 Mann-Whitney 檢驗的客觀資料。
