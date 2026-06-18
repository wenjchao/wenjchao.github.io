# Surface mesh node tracking algorithm (表面節點追蹤演算法)

1. 引用自哪篇 paper: aortoseptal-angle-anomalies
2. Outline (任務主線): Surface mesh node tracking algorithm (表面節點追蹤演算法)
3. Method: 
心室一個週期會大幅收縮再舒張，作者使用可移動網格的有限元方法 (Arbitrary Lagrangian-Eulerian, ALE) 讓網格跟著心室壁一起變形。為了不讓單元被拉到又長又扁，ANSYS 每一個時間步都會把網格『抹平』(smoothing) 並重新切一次 (remeshing) 來維持品質。代價是：重切之後，這一格還是上一格的『同一塊壁面』，但表面計算節點 (surface mesh nodes) 的位置與編號都換了——電腦不再知道『時步 t 的第 137 號點』就是『時步 t+1 的哪一號點』。於是作者寫了一支自製的 MATLAB 追蹤腳本 (in-house MATLAB algorithm，見 Appendix A.4，程式公開於 `github.com/RaiderDoc/MATLAB_tracking_algorithm.git`)，把每個時間步的表面節點座標讀出來、根據幾何位置把『相鄰時步的最近節點』配對成同一個物理位置，強制建立一張一對一節點對應表 (one-to-one node correspondence)。有了這張表，後續才能對『同一塊壁面』在不同時間點的瞬時 WSS 做時間積分。
這張對應表看似只是『資料對齊』，卻是論文成立的關鍵。TSM、OSI、WSS divergence 三個指標都是『同一壁面位置一整個週期的時間積分』；對應表建好後，每個物理位置都有一串對齊的時間序列，三條公式就能各自套上去——這也是為什麼一道對齊動作同時解鎖了三個下游指標。那為什麼不乾脆放棄 ALE、改用其他不需要 remeshing 的方法？因為 ALE 是目前處理大幅變形邊界最自然的策略，網格直接黏在壁面上動，邊界層內的速度梯度與 WSS 解析度最高。替代方案 (例如 immersed boundary) 不必 remeshing，但壁面節點不在實際邊界上，近壁 WSS 解析度會明顯下降；這篇研究的核心指標就是 WSS，當然不能犧牲解析度。作者的策略因此是『ALE 該怎麼做就怎麼做、節點失聯的副作用我自己後處理補救』。
如果完全不做這套節點追蹤、直接用 ANSYS 預設輸出來算 TSM/OSI 會怎樣？下一個時間步同一個節點 ID 已經被搬到別的位置上，等於把『東邊一下、西邊一下』的剪應力硬加在一起。算出來的 TSM 與 OSI 數值在每個位置上都摻雜其他位置的訊號，完全失去物理意義——下游所有『AoSA 變陡讓 inferior LVOT WSS 升高 45%』、『WSS 散度降低 66%』這類結論全部站不住。這也是為什麼過去文獻多半只敢報瞬時 WSS、很少呈現 cycle-averaged 3D LV WSS map，也是作者把這段後處理工具開源的理由——一旦 ALE 模擬要做時間平均，這道關卡就繞不過去。
4. 工具與材料: 
- **Arbitrary Lagrangian-Eulerian (ALE)**: 讓網格跟著變形邊界一起動的可移動網格策略，是處理大幅變形心室最自然的方法。
- **Remeshing / Smoothing**: ANSYS 在每個時間步把網格抹平、重切一次，維持單元品質；副作用是節點編號失聯。
- **Surface mesh nodes**: 心室內壁上用來計算瞬時 WSS、壓力的表面計算節點。
- **In-house MATLAB tracking algorithm**: 作者自製的 MATLAB 腳本，根據幾何位置把相鄰時步的最近節點配對，建立一對一節點對應表 (Appendix A.4，公開於 GitHub)。
- **One-to-one node correspondence**: 強制建立的時步間節點對應表，讓電腦能在每個物理位置抓到完整的時間序列。
- **Cycle-averaged WSS metrics (TSM / OSI / WSS divergence)**: 需要『同一壁面位置一整個週期時間積分』才能算出的三個指標，全部依賴節點對應表。
5. 與此篇文章的關係: 
在《Significance of aortoseptal angle anomalies to left ventricular hemodynamics and subaortic stenosis》這篇文章中，作者為了量化四個 AoSA 變體 LV 壁面的 cycle-averaged WSS 環境，採用了自製的 MATLAB 表面節點追蹤演算法。它解決了 ALE 動態 remeshing 後相鄰時步節點 ID 失聯、TSM/OSI/WSS divergence 無法做時間積分的瓶頸；它吃進 ANSYS 每個時步輸出的節點座標，產出一對一對應表，直接供下游所有 cycle-averaged 壁面指標計算使用。
