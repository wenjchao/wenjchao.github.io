# COMSOL 有限元模擬交聯劑擴散

1. 引用自哪篇 paper: collagen-microgel-bioprinting
2. Outline (任務主線): COMSOL 有限元模擬交聯劑擴散
3. Method: 
在 FRAP 量出 PEG-BCN 的擴散係數後，作者用 COMSOL Multiphysics (Version 5.6) 的『稀薄溶質運輸 (Transport of Diluted Species)』模組做時域研究，預測 PEG-BCN 從浴擴散進入列印絲後的時空濃度分佈。物理模型用 Fickian 擴散——分子由濃度高的地方往低的地方流，流量正比於濃度梯度 ($J = -D \nabla C$)，質量守恆給出 $\partial C / \partial t = D \nabla^2 C$。幾何上把列印絲建成 3D 圓柱、直徑等於噴頭出口內徑，外圍是支撐浴。初始條件 (t = 0) 對應實驗配置：浴一開始預溶 5 mg mL⁻¹ PEG-BCN、墨水裡完全沒有；邊界設為外圍 no-flux (浴是封閉儲庫不會漏)、墨水–浴界面允許 PEG-BCN 自由擴散通過。擴散係數直接套 FRAP 量到的值：浴 D ≈ 50 μm² s⁻¹、collagen-azide 墨水 D ≈ 65 μm² s⁻¹，且 D 視為時間不變——這個簡化由 FRAP 在 0–2 h 內 D 幾乎不掉的實測背書 (見 2-G)。

有限元法把列印絲切成數十萬個小四面體 (mesh)，在每個四面體裡用簡單多項式近似濃度，再拼回整體。圓柱絲的曲面邊界與墨水/浴擴散係數不同——手算解析解很困難，但有限元能直接吃。作者選 physics-controlled 的『Extra Fine』四面體網格，邊界附近自動加密，確保剛開始擴散時 PEG-BCN 從 0 跳到 5 mg mL⁻¹ 的陡梯度被解析清楚 (粗網格會把陡梯度人為平滑、低估擴散速率)。模擬時域 0–2 h，涵蓋實驗的整個 SPAAC 交聯窗口。為了讓結論對不同噴頭都適用，作者分別模擬 22 G、27 G、32 G 三種規格的列印絲——擴散到中心的時間尺度 $\tau \sim L^2/D$ 隨絲半徑平方放大：22 G (絲半徑 ≈ 205 μm) τ ≈ 11 min、27 G (105 μm) τ ≈ 3 min、32 G (50 μm) τ ≈ 40 s，告訴作者 27 G 與 32 G 都能在 2 h 內讓 SPAAC 達飽和。

這個模擬有兩條命門。第一條是邊界條件必須對應實驗——若外圍誤設為 sink (PEG-BCN 可流出)，浴濃度會在模型中持續下降，墨水拿到的 PEG-BCN 被低估，COMSOL 會給出『2 h 內 SPAAC 達不到飽和』的悲觀結論誤導實驗。實際浴是封閉儲庫、PEG-BCN 總量遠大於墨水需要，故 no-flux 才正確。第二條是若省略 COMSOL 模擬、直接套 2 h 到所有噴頭，22 G 大噴頭印出的絲很可能中心 2 h 還沒拿到足量 PEG-BCN，取出時中心軟塌、後續存活率與形態觀察全部報廢。FRAP 量 D + COMSOL 預測時空分佈一前一後，正是『實驗 + 預測』完整證據鏈，為下游列印參數設計背書。
4. 工具與材料: 
   - **COMSOL Multiphysics, Version 5.6**: 有限元軟體；本研究用『Transport of Diluted Species』模組做時域擴散研究。
   - **Transport of Diluted Species**: COMSOL 的稀薄溶質運輸模組，求解 Fickian 擴散方程 $\partial C/\partial t = D\nabla^2 C$。
   - **Fickian diffusion**: 假設通量正比於濃度梯度 ($J = -D\nabla C$)、D 為常數的最簡擴散模型。
   - **3D 圓柱絲幾何**: 把列印絲建成圓柱、直徑等於噴頭出口內徑，外圍包覆支撐浴。
   - **初始 5 mg mL⁻¹ / 0**: 支撐浴 t=0 時 PEG-BCN 為 5 mg mL⁻¹，墨水內為 0，對應實驗配置。
   - **No-flux 外邊界**: 把整缸浴視為 PEG-BCN 不會外漏的封閉儲庫；浴-墨水界面則允許自由擴散。
   - **Extra Fine 四面體網格**: physics-controlled 自動在邊界加密的網格，確保陡濃度梯度被解析。
   - **22/27/32 G 噴頭規格**: 三種噴頭直徑分別印出半徑 ~205、~105、~50 μm 的絲，對應不同擴散到中心的時間。
5. 與此篇文章的關係: 
   在《Embedded 3D Bioprinting of Collagen Inks into Microgel Baths to Control Hydrogel Microstructure and Cell Spreading》這篇文章中，作者要確認『SPAAC 交聯 2 h』對不同噴頭印出的絲都來得及讓 PEG-BCN 擴散到中心，否則列印絲心未交聯就會崩。為此作者把 FRAP 量到的 D 餵進 COMSOL Multiphysics 的 Transport of Diluted Species 模組，對 22 G、27 G、32 G 三種噴頭分別跑 0–2 h 的時空濃度模擬。模擬結果為 2 h 反應時間與選定的 27 G 噴頭做了量化背書，是讓下游細胞列印與微結構量化結果可信的關鍵預測支柱。
