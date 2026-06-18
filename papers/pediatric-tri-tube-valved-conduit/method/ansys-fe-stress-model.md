# ANSYS 有限元素 valve diastolic stress 模型

1. 引用自哪篇 paper: pediatric-tri-tube-valved-conduit
2. Outline (任務主線): 用計算力學比較 tube-in-tube 與 tri-tube 兩種設計在 diastole 時的應力分佈，證明 tri-tube 把 commissure 縫線上的應力集中消解到 bulk matrix 內，給設計變更提供 mechanistic justification。
3. Method:

為了證明 tri-tube 設計在力學上比 tube-in-tube 優越、不只是 wet-lab 試錯，作者用有限元素分析 (finite element analysis, FEA) 在 ANSYS Workbench Transient Structural 軟體裡跑了兩個模型，比較兩種設計在 diastole 血壓下的應力分佈。整套計算的核心是把連續的瓣膜切成大量小元素，每個元素配上「材料怎麼回應壓力」的本構方程；告訴電腦邊界條件 (哪邊固定、哪邊可動) 與外加壓力波形，電腦就解一組巨大的聯立方程：每個節點怎麼動才能讓力平衡並符合材料硬度規則。解完後得到每個位置的應力 (見 Fig. 1H、I)。作者選擇把軸向與環向 stress-strain 曲線平均成一條 isotropic 曲線——雖然真實組織有 anisotropy (環向比軸向硬 2 倍)，但研究目的是「比較兩種設計的相對應力分佈」而非絕對數值，isotropic 簡化犧牲一些精度換取計算可行性，是工程模擬常見取捨。

本構方程選的是 Mooney-Rivlin (hyperelastic)，不是一般教科書的線性彈簧 (Hookean σ = E·ε)。為什麼？實際瓣膜組織的 stress-strain 曲線是「J 形」：低 strain 時很軟 (鬆弛的膠原蛋白纖維還沒拉直)，過了轉折點纖維開始排齊承擔力後突然變硬。Mooney-Rivlin 把這條 J 形曲線用幾個參數擬合進去，能正確預測「鬆鬆軟軟時的反應 + 拉緊後的反應」。瓣膜在 diastole 下承受血壓，瓣葉會從鬆弛被撐到接近極限——只有 Mooney-Rivlin 才能算出 commissure 那種「拉到極限後突然變硬」的應力集中，Hookean 會嚴重低估高應變區的應力。作者把單軸拉伸測試 (見 module 7) 得到的兩個方向 stress-strain 曲線取平均，擬合進 Mooney-Rivlin 方程作為材料定義。

幾何上，三片瓣膜的瓣葉、根部、commissure 都繞著中心軸每 120° 重複一次——這叫「三重旋轉對稱」。物理上意味整顆瓣膜的應力分佈也每 120° 重複，因此電腦只算 1/3 sub-domain，在切面加上對稱邊界條件得到的結果跟算整顆完全一樣，但計算時間與記憶體只要 1/3。Tube-in-tube 模型由內管 (leaflet) 與外管 (root) 組成，用 24,715 個 10-node tetrahedral elements；Tri-tube 模型則是兩個相鄰管的一半，用 23,093 個 elements。網格必須夠細才能解析 commissure 的 stress concentration——應力可能在 1 mm 內從低變到極高，元素太粗會把峰值平均掉、模擬反而看不出 stress concentration 這個正是要證明的現象。縫線用 merged-node suture points 模擬：強迫兩個來自不同管子的表面節點位置完全相同，等於無限硬、無體積的虛擬縫線把兩塊組織鎖在一起，避免把細縫線畫成有體積元素導致網格爆炸；葉片底部封口同樣用 merged-node 處理。邊界條件方面，上下緣是手術縫到原生肺動脈的吻合位置，軸向 (z) 與環向 (y) 都鎖死；中線上的節點根據對稱原理在 y 方向不能動，但徑向 (x) 與軸向 (z) 自由——模擬 diastole 時血壓把瓣葉往中央推、縫線位置可以略往中心位移的真實情境。三片瓣葉內折碰在一起的接觸由 Augmented Lagrange-based contact algorithm 處理：在每一步迭代時加上懲罰力與 Lagrange 乘子雙重約束，確保節點不穿透彼此又能正確傳遞接觸壓力。

輸出的應力熱圖 (Fig. 1H、I) 直接證明了設計變更的 mechanistic justification：tube-in-tube 的 commissure 應力集中在三條 commissure suture 點上，因為內管葉片的下拉力完全靠這幾條縫線傳到外管；而 tri-tube 因為沒有 commissure 縫線 (相鄰管子的軸向縫合線在別處)，commissure 位置的應力是連續分佈在 bulk matrix 內，沒有點狀集中。這張熱圖讓作者能向審稿人與監管單位解釋「tri-tube 為什麼預期會比 tube-in-tube 更穩定」——而不是只能說「我們試試看」。這就是「先計算後試驗」的經典策略：用低成本的 FEA 避免直接燒掉 4 隻昂貴的羊在一個機械上注定失敗的設計上。

4. 工具與材料:

   - **ANSYS Workbench Transient Structural**: 商用有限元素分析軟體與其暫態結構模組，用於跑 diastolic backpressure 下的瓣膜應力模擬。
   - **有限元素分析 (FEA)**: 把連續物體切成大量小元素，每個元素配本構方程，解聯立方程得到每個節點的應力與變形。
   - **Mooney-Rivlin (hyperelastic)**: 能擬合 J 形 stress-strain 曲線的本構方程，正確預測組織從鬆弛到拉緊的非線性反應。
   - **10-node tetrahedral element**: 10 個節點的四面體積木，是 3D FEA 的標準元素類型；本研究用 23,093–24,715 個。
   - **1/3 axisymmetric sub-domain**: 利用三重旋轉對稱只算 1/3 幾何，在對稱面加邊界條件，計算量降為 1/3。
   - **merged-node suture points**: 強迫兩個節點位置永遠相同的縫線簡化法，等於無限硬虛擬縫線、不需畫縫線體積。
   - **Augmented Lagrange-based contact algorithm**: 用懲罰力 + Lagrange 乘子雙重約束處理三片瓣葉接觸 (coaptation) 的演算法，避免穿透並穩定收斂。
   - **isotropic 簡化**: 把軸向與環向 stress-strain 曲線平均，犧牲 anisotropy 細節換取計算可行性。
   - **diastolic backpressure waveform**: 漸增 backpressure 的時間波形，作為模擬的外加載荷。
   - **stress concentration**: 應力在小範圍內急遽升高的現象；本研究比較它是集中在縫線 (tube-in-tube) 還是分散在 bulk matrix (tri-tube)。

5. 與此篇文章的關係:

這篇 paper 的核心主張是把前一代 tube-in-tube 設計改成 tri-tube 結構，讓 diastolic backpressure 由 bulk collagen matrix 承擔而非全部壓在 commissure 縫線上；要說服審稿人與監管單位「為什麼預期 tri-tube 會比 tube-in-tube 穩定」，光憑 wet-lab 試錯不夠，因此作者用 ANSYS 有限元素分析在 diastole 載荷下比較兩種設計的應力分佈，作為設計變更的 mechanistic justification。這個模型的好處在於以低成本計算先 map 出 stress concentration 的位置：tube-in-tube 應力集中在三條 commissure suture，而 tri-tube 應力連續分散在管壁基質內，輸出的 Fig. 1H/I 應力熱圖直接讓「縫線變 bulk matrix」的設計邏輯被視覺化，避免直接燒掉 4 隻昂貴的羊在注定失敗的設計上。模型輸入需要真實的軟組織非線性反應，因此 Mooney-Rivlin 本構的參數來自 module G 的軸向與環向單軸拉伸測試曲線，把濕實驗的材料數據接進乾實驗的模擬；輸出則為下游的 Bose Durapulse 耐久測試、pulse duplicator 水力測試、以及生長羊植入手術提供設計合理性，構成這篇「先計算後試驗」閉環裡的第一步乾實驗環節。
