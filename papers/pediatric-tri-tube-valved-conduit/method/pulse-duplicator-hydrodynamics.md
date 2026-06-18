# Pulse Duplicator 水力性能測試

1. 引用自哪篇 paper: pediatric-tri-tube-valved-conduit
2. Outline (任務主線): 在模擬肺動脈血流條件下量化 Gen 1、porcine、bovine valve 的 EOA、regurgitant fraction、systolic ΔP，確保植入時即具備臨床可用的水動力性能。
3. Method:

脈動模擬器 (pulse duplicator) 是一個閉環水路，由五個部件組成：(1) ViVitro Systems 商用波形產生器與往復泵，製造跟真實心跳一樣的脈動血流；(2) 蓄水槽存放測試液 (室溫 PBS)；(3) 瓣膜固定腔室——待測瓣膜先縫進兩段客製矽膠套筒 (custom silicone sleeves) 的內側，再把套筒插進腔室兩端的接口，腔室會在瓣膜外圍施加 16 ± 1 mmHg 的跨壁壓差 (transmural pressure gradient) 讓瓣膜外圍管壁 (root) 在每次脈動時跟著撐開又縮回 (cyclic root distention)，模擬真實肺動脈血管壁在心跳時的脈動撐張；(4) 可調順性腔室 (variable compliance chamber)，模擬血管的 Windkessel 彈性緩衝——一個含氣腔加液腔的容器，氣體被壓縮時吸收收縮期壓力峰、放鬆時推回液體維持舒張期流動，可調氣腔體積讓作者切換模擬肺動脈或主動脈不同彈性；(5) 機械雙葉單向閥放在泵下游，把待測瓣膜的測試環境跟泵的「推-吸」往復行為隔離開來，強制液體只往一個方向流。五個部件組合起來，目的是讓待測瓣膜置身於「跟真實肺動脈血流幾乎一樣」的脈動環境中量測性能。它跟前一個 Bose Durapulse 加速疲勞測試的目標不同：Durapulse 用 10 Hz 超生理頻率累積開合次數看「會不會壞」(durability)；pulse duplicator 用生理頻率與壓力的真實波形看「現在的水動力性能好不好」(EOA、壓差、回流量)——前者測壽命、後者測效能。

感測器配置：兩個 ViVitro 壓力轉換器分別裝在瓣膜上游與下游量瞬時壓力；瓣膜上游另裝一支 Carolina Medical 500 系列電磁流量計，利用法拉第定律 (液體穿過磁場產生與流速成正比的電壓) 量瞬時雙向流量。瓣膜端面則架一支 Canon EOS T3i 相機以 30 fps 錄影記錄開合狀況。所有訊號都用客製 LabVIEW 程式同步擷取——LabVIEW 是工程界標準的儀器整合工具，可以寫客製化程式自由定義多通道組合 (壓力 × 2、流量、相機觸發) 與輸出原始數據格式，比 ViVitro 自帶軟體的固定輸出彈性高得多，方便後續自己分開算 closing volume 與 leakage volume。流量目標設定為平均 4.0 LPM (升/分鐘) 模擬兒童心輸出量 (引自 Cattermole et al. 2017, Physiol. Rep.)，剛好對應植入時年齡的羔羊體型；用成人 5-6 LPM 太高、嬰兒 2 LPM 太低，都不能反映目標族群的水動力條件。流量靠泵衝程體積與頻率設定，壓力則由下游流阻、衝程體積與上游液壓頭三個參數獨立調節到生理範圍；每組測試至少記錄 10 個 cycle 取平均。

輸出指標有三個。第一是收縮期壓差 (systolic ΔP)：上下游兩支壓力轉換器讀數相減，收縮期取最高那段就是。第二是有效開口面積 (EOA)：把這個壓差代入 Gorlin 公式，再除以正向流量得「為了把這麼多液體推過去要多大的等效開口」——相當於血流被擠過瓣膜時的最小截面積。第三是回流分率 (regurgitant fraction)：把電磁流量計的瞬時雙向流量曲線切出逆向那段做積分，又分成兩塊——關閉量 (closing volume) 是瓣膜關閉過程中葉片往上游推回的少量液體 (像關門時門板把空氣推一下)，洩漏量 (leakage volume) 是瓣膜完全關閉後舒張期經由葉片不完美閉合縫隙反向漏出的液體；兩者相加再除以單一 cycle 正向衝程體積，就是回流分率。對比超音波只能用最大流速代入伯努利公式間接估算 ΔP，pulse duplicator 是直接量壓差與流量的黃金標準。

為什麼要在同一台 pulse duplicator 上一起測 Gen 1、Hancock 豬瓣、Contegra 牛瓣？因為不同廠商規格書是在各自不同的測試條件下做的 (流量、壓差、介質、頻率全部不同)，數字直接比不出實際差別；放在同一台、同一組參數下測才公平可比較。結果：Gen 1 在植入前就達到 < 3 mmHg 平均收縮期壓差、< 9% 回流分率、近 1 cm² 有效開口面積——與兩種臨床瓣膜相當，代表新瓣膜植入當下就具備臨床可用水動力性能，後續活體測試才有意義 (請看 Fig. S3 與 table S2)。兩個關鍵設計護欄不能省：(a) 可調順性腔室必須在且氣腔體積要對到肺動脈彈性——剛性閉環會把壓力波形變方波，瓣膜經歷的負載偏離生理、量到的壓差會偏高；(b) 機械雙葉單向閥必須隔離泵的「推-吸」往復行為——少了它泵每次推完會把瓣膜下游已流走的液體往回吸，被電磁流量計誤算成「瓣膜回流」、回流分率出錯 (這就是 Fig. S3C 看到瞬時前向流脈衝的成因，作者明說是泵相關現象、非瓣膜性能問題)。注意 Gen 2 並未在 pulse duplicator 測試。

4. 工具與材料:

   - **Pulse duplicator (customized, ref 28)**: 閉環水路平台，在生理頻率與壓力下模擬真實肺動脈血流，用於量瓣膜的 EOA、systolic ΔP、回流分率。
   - **ViVitro Systems wave generator + pump**: 商用波形產生器與往復泵，產生跟真實心跳一樣的脈動血流。
   - **Valve mounting chamber**: 瓣膜固定腔室，把縫進矽膠套筒的瓣膜固定在閉環中央並施加 16 ± 1 mmHg 跨壁壓差讓 root 脈動撐張。
   - **Variable compliance chamber**: 可調順性腔室，含氣腔加液腔模擬血管 Windkessel 彈性緩衝；可調氣體體積切換不同血管彈性。
   - **Mechanical bi-leaflet valve**: 機械雙葉單向閥放在泵下游，把瓣膜測試環境跟泵的推-吸往復行為隔離。
   - **ViVitro pressure transducer × 2**: 壓力轉換器分別裝瓣膜上下游量瞬時壓力，相減得 systolic ΔP。
   - **Carolina Medical 500 series 電磁流量計**: 利用法拉第定律量瞬時雙向流量；用來算 forward flow、closing volume、leakage volume。
   - **Canon EOS T3i 30 fps 端面錄影**: 瓣膜端面相機記錄開合狀況；30 fps 對生理頻率的開合動作已夠用。
   - **LabVIEW 客製擷取程式**: 工程界標準儀器整合工具，同步紀錄壓力 ×2、流量、相機觸發等通道並輸出原始數據供後處理。
   - **4.0 LPM 平均流量**: 兒童心輸出量平均值 (引自 Cattermole et al. 2017)，對應植入時羔羊體型。
   - **Gorlin 公式 EOA 計算**: 由 systolic ΔP 與正向流量推算有效開口面積，相當於血流被擠過瓣膜時的等效截面積。
   - **Regurgitant fraction = (closing + leakage) / forward × 100%**: 回流分率：將雙向流量曲線中逆向段拆成 closing volume 與 leakage volume 後標準化。

5. 與此篇文章的關係:

這篇 paper 的核心主張是新的 tri-tube valve (Gen 1) 能在生長中的羊體內維持肺動脈瓣功能 52 週，但在把昂貴又有 IACUC 限制的羊投入活體實驗前，必須先在體外證明這顆瓣膜「植入當下」就已具備臨床可用的水動力性能，否則後續的生長與耐久觀察都失去意義。pulse duplicator 扮演的就是這道「植入前合格門檻」：它把 Gen 1、臨床標準的 Hancock 豬瓣與 Contegra 牛瓣放進同一套生理頻率脈動環境，在統一的 16 mmHg 跨壁壓差與 4.0 LPM 兒童心輸出量條件下，直接量測 EOA、收縮期壓差與 regurgitant fraction，解決了不同廠商規格書因測試條件不一致而無法直接比較的限制，也比超音波只能用伯努利公式間接估壓差更接近黃金標準。在 method 鏈裡，它與前一站的 Bose Durapulse 加速疲勞測試形成互補——Durapulse 用超生理 10 Hz 看「會不會壞」，pulse duplicator 用生理波形看「現在性能好不好」；同時與更上游的 ANSYS 應力模擬呼應，把計算上預測的 commissure 應力分散轉成可量測的水動力指標。確認 Gen 1 達到 < 3 mmHg 壓差、< 9% 回流分率、近 1 cm² EOA 後，整個 in vivo 植入手術、後續超音波追蹤與組織學分析才有正當性銜接進行。
