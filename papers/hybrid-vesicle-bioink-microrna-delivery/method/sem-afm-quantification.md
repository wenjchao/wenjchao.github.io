# SEM 孔徑與 AFM 影像的後處理量化

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): SEM 孔徑與 AFM 影像的後處理量化
3. Method: 
   為了量化加入 NV 後 GelMA 孔徑的變化，作者用掃描式電子顯微鏡 (SEM) 取剖面影像。流程的關鍵兩步是「凍乾 + 鍍金」：水膠 90% 以上是水，直接放進 SEM 真空腔會瞬間爆掉、孔結構也會塌陷，所以先 −80 °C 冷凍 + 真空乾燥整夜、再 lyophilize 凍乾，把水從固態直接升華成氣態移除，孔網才能保留原形。水膠本身不導電，電子束打上去會堆積靜電讓影像花掉，所以再用濺鍍儀在表面薄薄鍍一層金 (sputter coating) 讓電子有路可走、表面也能把電子打回來。最後用 JEOL JSM-IT100、加速電壓 15 kV 拍剖面圖，每組 3 個樣本人工量 50 個孔取平均，得到 GelMA 加不同 NV 之後的孔徑分布。

   SEM 看到的是凍乾後的結構骨架，但細胞實際接觸的是水合介面，所以作者另用原子力顯微鏡 (AFM) 在水裡量。儀器是 Bruker Dimension Icon AFM，配上一根專為水中量測設計的細針 (ScanAsyst-Fluid+ sharp-tipped cantilever，共振頻率 150 kHz、彈簧常數 0.7 N m⁻¹)；樣本泡在液體裡 (in-fluid)，細針一行一行掃 (每秒 1 行、每行 512 點)，同時記錄「探針每一點被壓上去多深」和「該點要施多大力」，得到 height image + force-deformation 雙重資料。掃完的圖會帶有樣本傾斜與掃描器漂移 (scanner drift) 等低頻偏差——直接算粗糙度會把這些當成「真實起伏」算進去、每張圖傾斜程度又不同無法跨樣本比，所以先做 flatten 把整張圖數值上拉成平面。接著對拉平後的 height image 算均方根粗糙度 (RMS)：先取整張圖平均高度當基準線，再對每 pixel 算「離基準線多遠的平方」，全部平均後開根號得 $\text{RMS} = \sqrt{\frac{1}{N}\sum_{i=1}^{N}(z_i - \bar{z})^2}$，代表整個表面起伏的平均振幅。

   同一次掃描還能算出局部硬度——DMT modulus。每一點的探針壓樣本訊號是一條「施力 F vs 壓入深度 δ」的曲線，DMT 模型把它擬合成 $F = \frac{4}{3} E^* \sqrt{R}\, \delta^{3/2} + F_{\text{adh}}$ ——其中 $E^*$ 是材料的等效模數 (reduced modulus，越硬越大)、$R$ 是探針尖端的曲率半徑、$\delta$ 是壓入深度、$F_{\text{adh}}$ 是黏附力。為什麼選 DMT 不選 JKR？兩個模型差在「探針把樣本拔起來時，材料會不會被拉出一個小尖頭 (neck)」：JKR 假設黏附很強、會拉出 neck，適合軟黏材料；DMT 假設黏附弱、拔起來就乾脆分開，適合彈性主導、黏附偏弱的水膠網路。硬套 JKR 反而會把 GelMA 模數低估。

   孔徑、RMS、DMT 模數三個讀數要同時量，因為它們從不同維度共同支持「NV-GelMA 鍵結強度」這個結論。光看孔徑：可能只代表「材料縮水多寡」；光看 RMS：可能只是 NV 偶然黏在表面的隨機分布；光看 DMT：可能只是局部含水量差異。三者放一起就互相佐證：Lip-GelMA 孔最小 (NV 把網拉緊、交聯密度上升) + Young's modulus 最高 (11.1 ± 1.9 kPa) + 加上釋放最慢——共同指向 Lip 與 GelMA 之間鍵結最強 (Lip 上的磷酸基與 GelMA 上的胺基形成 H-bond)。更有意思的是 in-fluid AFM 量到 Gel-EVs 和 Gel-hEL 的局部 DMT 反而比 Gel-Lip 高，作者解釋成「EVs 與 hELs 因為與 GelMA 鍵結較弱、慢慢向表面遷移再聚集」——這個動態行為只有水合狀態下才看得到，凍乾的 SEM 視角會錯過。三個讀數任一個單獨看都能找到別的解釋，三個一起才能排除其他可能、收斂到鍵結強度排序 Lip > hELs > EVs。
4. 工具與材料: 
   - **SEM (掃描式電子顯微鏡)**: 用電子束打凍乾樣本表面、收二次電子成像；JEOL JSM-IT100、15 kV 拍 GelMA 剖面孔徑。
   - **Lyophilization (凍乾)**: 把樣本內的水從固態直接升華成氣態移除，避免真空腔中的水膠塌陷。
   - **Sputter coating (鍍金)**: 用濺鍍儀在不導電的水膠表面鍍一層薄金，讓 SEM 電子束有路可走、避免靜電累積。
   - **AFM (原子力顯微鏡)**: Bruker Dimension Icon，用細針掃描樣本表面同時得到 height image 與 force-deformation 曲線。
   - **In-fluid AFM**: 把樣本泡在液體中量，模擬細胞實際接觸水膠的水合狀態；補強 SEM 凍乾視角無法看到的動態行為。
   - **ScanAsyst-Fluid+ sharp-tipped cantilever**: 為水中量測設計的 AFM 探針，共振頻率 150 kHz、彈簧常數 0.7 N m⁻¹。
   - **Image flattening**: AFM 後處理步驟，數值上把整張圖拉成平面，扣掉樣本傾斜與掃描器漂移等低頻偏差。
   - **RMS (均方根粗糙度)**: $\sqrt{\frac{1}{N}\sum(z_i - \bar{z})^2}$；代表整個表面起伏的平均振幅。
   - **DMT modulus**: Derjaguin-Muller-Toporov 接觸模型，擬合 force-deformation 曲線得到局部材料硬度；適用於黏附弱、彈性主導的水膠。
   - **JKR 模型**: 另一種接觸模型，假設黏附強、會拉出 neck，適用於軟黏材料；不適合 GelMA。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了證明三種 NV 與 GelMA 基質之間的鍵結強度排序 (Lip > hELs > EVs)，採用了 SEM 孔徑量化與 AFM in-fluid 後處理量化。它解決了單一影像方法無法區分「縮水、表面分布、局部硬度」三個獨立因素的瓶頸，吃進每組 50 個 SEM 孔徑與整張 AFM height image，產出孔徑分布、RMS 粗糙度、DMT 模數三組可統計的數值，再與 Young's modulus、釋放動力學交叉驗證鍵結強度。
