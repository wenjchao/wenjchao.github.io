# 鵪鶉活體影像 Imaris/MATLAB 軌跡定量與方向性統計

1. 引用自哪篇 paper: developmental-organization-sensory-sympathetic-ganglia
2. Outline (任務主線): 鵪鶉活體影像 Imaris/MATLAB 軌跡定量與方向性統計
3. Method:

作者要看被 PAX7-enh-Citrine 標亮的鵪鶉神經脊細胞在 6 小時內怎麼移動。共軛焦顯微鏡 (Zeiss LSM 710 Meta) 每次只對焦到一個薄層並收集該層的螢光，把焦點沿 z 軸一層一層往下移，就能組成一整段厚度的立體影像 (Z-stack)——這裡涵蓋胚胎背側整段神經管、上方 ectoderm 與周圍 mesoderm。每隔一段時間重掃一次，6 小時累積下來就是一個 4D 影像 (x, y, z, t)。接著把影像丟進 Imaris (v10.0.1, Bitplane)：先用 spot detection 在每個時間點把每個發綠光的細胞抓成一顆 3D 座標點，再用 track linking 演算法把不同時間點的點按「距離近且亮度相符」原則連起來，形成每顆細胞的立體軌跡。作者選 spot detection 而非完整 3D segmentation，是因為 PAX7 陽性細胞在神經管背側很密集，完整 segmentation 常把兩顆相鄰細胞誤合併，spot detection 只挑亮度峰值中心就沒這個問題。

有一個絕不能省的前處理：胚胎後緣延伸 (posterior elongation) 造成的整體 drift。6 小時內鵪鶉胚胎自己還在長長，整個胚胎相對顯微鏡視野持續往後漂。這是背景本身的移動，不代表細胞主動跑；不扣掉的話每顆細胞的軌跡都會被灌入這段背景位移，看起來大家都朝著同個方向跑。作者用 somite（胚胎背側像一節節串珠、之後長成脊椎的分節結構）當「不動參考物」，因為 somite 一旦形成就相對脊椎軸固定、只跟著胚胎整體漂而不會主動變形。他們在 FIJI 的 Brightfield 通道對每個 somite 圈矩形，取矩形的 centroid 當這個 somite 的位置點，每個時間點量一次就得到「這個 somite 在 6 h 內漂了多遠」。somite 均值長度 81 ± 1 μm (n = 92 somites, 6 embryos) 同時提供一個穩定的長度尺，讓「跨越一個 somite」變成可量化閾值。

作者把 Imaris 匯出的每顆細胞軌跡讀進 MATLAB (v R2021a)，做兩件事：先從整條軌跡算出總位移 (total displacement)、沿頭尾方向分量 (rostrocaudal) 與沿內外側方向分量 (mediolateral)；再減去該細胞起點所在 somite 在同一 6 h 內的位移，等於把該 somite 當成不動的原點。這樣算出來的位移才是相對於胚胎自己的真實遷移。為什麼一定要先校正才做 t-test？因為若不扣背景漂移就直接比 FGFi 組跟 DMSO 組，兩組差異可能只是因為當天胚胎延伸速度不一樣（FGF 訊號本身也影響胚胎延伸），沒法歸因給細胞遷移本身。校正後每顆細胞的位移向量可以再轉成方向 (角度)，做出方向性 histogram：橫軸是角度、縱軸是落在該角度區間的細胞數。統計檢定用 Prism GraphPad (v10.0.2) 的雙尾 t-test。

在 DMSO 對照 (n = 237 cells / 4 embryos) 與 FGFi (infigratinib) 組 (n = 243 cells / 4 embryos) 之間，作者看到 rostrocaudal >1-somite 遷移比例從 19.35% 掉到 1.35%；rostrocaudal displacement 顯著下降 (P = 0.0129)；mediolateral displacement 顯著上升 (P = 0.0237)；total displacement 沒差別。這個對比之所以敢下「FGF 訊號是頭尾軸移動所必需」的結論，關鍵在前面兩道防線：第一，人工檢查並在 MATLAB 端剔除 Imaris track linking 錯連的軌跡（否則單一個「一步暴衝」或「方向突然反轉」的假軌跡就會把 displacement 分布拉出長尾、污染方向性 histogram）；第二，drift normalization 把胚胎延伸的貢獻扣乾淨，剩下的差異只能歸給細胞本身遷移行為的改變，不會被「FGFi 剛好也降低胚胎延伸速度」污染成假陽性。

4. 工具與材料:

- **Imaris (v10.0.1, Bitplane)**: 商用 3D/4D 影像分析軟體；本文用其 time-lapse registration + spot detection + track linking 抓每顆 PAX7-Citrine+ 細胞的立體軌跡。
- **MATLAB (v R2021a)**: 商用工程計算環境；讀入 Imaris 匯出的 track 座標，計算 total/rostrocaudal/mediolateral displacement 並執行 somite-based drift normalization。
- **FIJI**: 開源生醫影像分析軟體；本文用其 Brightfield 通道對每個 somite 圈矩形取 centroid 當位置點，另用平行 rostrocaudal 軸的直線量 somite 長度 (均值 81 ± 1 μm)。
- **Prism GraphPad (v10.0.2)**: 商用統計繪圖軟體；本文用來畫 bar/scatter plot 並跑雙尾 t-test 比較 FGFi 與 DMSO 兩組 displacement。
- **Confocal Z-stack**: 共軛焦顯微鏡沿 z 軸逐層掃描組成的立體影像；本文涵蓋神經管背側 + ectoderm + mesoderm，6 h time-lapse 形成 4D (x,y,z,t)。
- **Spot detection + track linking**: Imaris 抓細胞的兩步演算法：先在每個時間點把亮點抓成 3D 座標，再依距離與亮度一致性連成跨時間的軌跡。適合密集 PAX7+ 細胞的追蹤，比完整 segmentation 抗誤合併。
- **Somite-based drift normalization**: 扣除胚胎 posterior elongation 造成的背景漂移的核心步驟：每條 track 位移減去起點 somite 的位移，等於把 somite 當不動原點。
- **方向性 histogram**: 把每顆細胞校正後的位移向量轉成角度，統計落在各角度區間的細胞數；用以判斷細胞是沿頭尾軸還是沿內外側軸走。

5. 與此篇文章的關係:

在《Developmental organization of sensory and sympathetic ganglia》這篇文章中，作者為了直接看到未離管神經脊細胞的移動方向並檢驗 FGF 訊號的因果角色，把 6 h time-lapse confocal Z-stack 的 PAX7-Citrine+ 軌跡丟進 Imaris + MATLAB pipeline 量化。這一步吃 4D 影像資料，產出每顆細胞校正過胚胎延伸背景的 rostrocaudal/mediolateral 位移與方向性 histogram，直接證明 infigratinib 阻斷 FGF 後頭尾軸長距離遷移從 19% 掉到 1%，把 MVBA 統計上「祖先跨 level」的推論升級為活體上「FGF 為頭尾遷移所必需」的因果結論。
