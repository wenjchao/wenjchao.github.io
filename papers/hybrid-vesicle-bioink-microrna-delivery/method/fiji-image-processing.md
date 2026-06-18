# 影像處理 (Fiji)

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): 影像處理 (Fiji)
3. Method: 
   Fiji 是科學影像分析軟體 ImageJ 的「擴充包預裝版」(Fiji = Fiji Is Just ImageJ)，免費、開源、跨平台，內建大量生物影像專用的分析插件。比起 Photoshop（修圖導向）或顯微鏡內建軟體（廠牌綁定），Fiji 直接讀取每個像素的灰階值、可以重複跑同一套腳本。本研究的所有 confocal / fluorescence 影像都過 Fiji 一次——共軛焦影像是多通道的：DAPI（藍）標細胞核、F-actin（綠）標細胞骨架、miRNA-DY547（紅）標 miRNA 貨物，原始檔案把三層疊在一起，要分別量某個通道的訊號必須先用 Fiji 拆開。為什麼整篇只用 Fiji 一個軟體？因為不同軟體對「強度怎麼算、threshold 怎麼挑、細胞核怎麼切」的細節都不同，混用會讓跨組比較被軟體差異污染；統一用 Fiji 就把這個系統性偏差鎖死。

   拆完通道之後 Fiji 提供兩種讀法：mean intensity（每個像素亮度的平均值）反映平均訊號濃度、integrated density（mean × 面積）反映總量。但直接報絕對強度有兩個問題。第一：不同視野細胞密度差很多，擠的視野自然亮、稀的視野自然暗，跟「每顆細胞吃了多少 PKH67-NV」其實無關——所以本文 fig 2(D) 把 PKH67 通道的 mean intensity 除以 DAPI 通道的細胞核數，得到「平均每顆細胞的訊號」，才能跨視野、跨組公平比較。第二：螢光絕對強度跟激發雷射功率、曝光時間、增益這些成像參數綁在一起，同一個樣品換個設定就亮一倍——所以本文把 PKH67-EVs 設為 100%，hELs (59.6%)、Lip (9.4%) 換算成相對比例，這樣的比例不受成像設定影響。

   Fiji 怎麼從 DAPI 影像「數」出細胞核？DAPI 把細胞核染成亮藍色，在影像上是「黑底亮斑」的高對比結構。Fiji 的標準流程是：先用 threshold 把亮度高於某個值的像素標成前景；再用 watershed 算法把擠在一起的兩顆細胞核切開；最後用 analyze particles 自動數出獨立斑塊的數量。整套跑下來 30 秒就能數出一張影像有幾顆細胞核——比手算快、結果也可重現。

   兩個常見失敗模式。第一：量強度時沒扣背景。影像本身就有一層基底亮度（相機暗電流、自體螢光、雜散光散射），若直接量原始強度，低訊號組（例如 PKH67-Lip 9.4%）會被背景墊高、組間差異被壓縮；Fiji 標準做法是先量背景區的平均強度、再從目標區減掉。第二：DAPI 計數時忘了做 watershed 切割。細胞擠的時候相鄰核會在 threshold 後融成一個大斑塊，analyze particles 把兩顆當一顆數，總細胞數低估、「強度／細胞核」被相應高估——在 confluent 條件下這個誤差會放得很大，所以 watershed 是 DAPI 計數的必要前處理。
4. 工具與材料: 
   - **Fiji (Fiji Is Just ImageJ)**: ImageJ 的擴充包預裝版，免費開源跨平台，內建大量生物影像分析插件，可重複跑同一套腳本。
   - **Channel splitting (通道分離)**: 把共軛焦影像疊在一起的多色通道（DAPI 藍 / F-actin 綠 / miRNA-DY547 紅）拆成單獨灰階圖層分別量化。
   - **Mean intensity / integrated density**: Fiji 的兩種強度讀法；前者是像素亮度平均（訊號濃度），後者是 mean × 面積（總訊號量）。
   - **DAPI 細胞核計數 (threshold + watershed + analyze particles)**: Fiji 標準流程：threshold 找亮斑、watershed 切開黏在一起的核、analyze particles 自動數出獨立顆數。
   - **Intensity per nucleus (歸一化)**: 把 PKH67 通道強度除以 DAPI 細胞核數，消除視野間細胞密度差異，得到「每顆細胞的訊號」。
   - **Fluorescence intensity ratio (%)**: 把某一組設為 100%、其他組換算成相對比例，消除激發功率、曝光時間等成像參數造成的絕對強度漂移。
   - **ZEISS LSM 880 with Airyscan**: 本研究所用的共軛焦顯微鏡，輸出多通道 confocal 影像給 Fiji 處理。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了量化 PKH67-NV 攝取率、miRNA-DY547 細胞質定位、不同細胞型別的靶向特異性，採用 Fiji 統一處理所有 confocal / fluorescence 影像。它解決了「不同軟體量強度的基準不同、跨組比較被軟體差異污染」的瓶頸：吃進 ZEISS LSM 880 拍的多通道影像，產出 PKH67 強度／DAPI 計數的相對攝取比例 (EVs 75.2% / hELs 59.6% / Lip 9.4%)，為下游 hELs 繼承 EV 靶向能力的論證提供可重現的影像定量基礎。
