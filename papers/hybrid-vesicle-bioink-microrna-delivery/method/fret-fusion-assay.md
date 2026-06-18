# FRET 膜融合定量分析

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): FRET 膜融合定量分析
3. Method: 
   作者用 FRET (Förster resonance energy transfer) 把「膜融合」轉成可量化的光學訊號。FRET 是兩種染料之間的「能量接力」：當會發綠光的 NBD 染料被激發後，如果旁邊有能吸收綠光的 Rhod 染料在 10 nm 之內，能量會「直接傳過去」、由紅色 Rhod 代替發光。FRET 效率隨距離 6 次方下降，只在 ~ 10 nm 內有效；意思是只要兩個染料的平均距離拉開一點點，紅光就會明顯掉、綠光就會升高。膜融合的本質正是「把原本擠在 Lip 膜上的染料稀釋到 Lip + EV 的更大膜面積」，FRET 訊號的變化就能直接量到融合程度。為什麼 FRET 對「真融合」敏感、對「物理聚集」不敏感？聚集只是兩顆完整囊泡黏在一起，染料還是擠在原本的 Lip 膜上、彼此距離沒變，FRET 訊號就不會變——這個「能區分真融合 vs 假聚集」的分辨能力是其他光學方法做不到的。

   實驗用的染料對是兩種磷脂類似物：NBD-PE 與 Liss Rhod-PE (Avanti Polar Lipids)。它們的下半部是真的磷脂尾巴、會自然嵌進 Lip 的脂質雙層；NBD 受 460 nm 激發發射 530 nm 綠光，剛好被 Rhod 吸收後再發 588 nm 紅光，是典型的 FRET donor/acceptor 對。為什麼把染料插進 Lip 而不是 EV？因為 Lip 是作者自己合成的、可以在製膜時把 2% (w/w) NBD-PE + 2% Rhod-PE 直接拌進原料磷脂，染料密度精準可控；EV 是天然分泌的、後染會引入額外干擾。流程是：把雙標記 Lip 跟 EV 以 Lip:EVs = 1:2、1:1、2:1 的不同比例共培育並 sonicate 成 hELs，再放進微孔盤式光譜儀 (microplate reader)，用 460 nm 激發、掃描 500–650 nm 發射光譜。讀數有兩個關鍵峰：530 nm (NBD 綠光) 與 588 nm (Rhod 紅光)；融合越成功，染料被稀釋越多、530 nm 增強、588 nm 衰減。

   為了把這對波長訊號合成一個可比較的指標，作者計算 FRET 效率 $= \dfrac{F_{588}}{F_{588} + F_{530}} \times 100$。這個比值的設計目的不是好看，而是消除三類干擾：(1) 不同 well 的樣品濃度差異、(2) 染料的光漂白 (photobleaching)、(3) 儀器光路微小差異——這三項都會「同比例」影響兩個波長的絕對訊號，做比值就把分子分母同步消掉，剩下的只有 distance-dependent 的 FRET 效率本身。這就是 ratiometric 量測的標準做法，可以讓不同樣品之間直接比較融合程度。

   染料比例不是隨便選 2% 的。比例太低 (例如 0.5%)，膜上 NBD 跟 Rhod 的平均距離超過 10 nm、根本沒有 FRET 接力，基準訊號太弱、後續融合造成的變化會被淹沒在雜訊裡。比例太高 (例如 10%)，染料分子在膜上彼此擠到一起會「自己壓自己」(self-quenching)——基準訊號反而降低、融合稀釋後 530 nm 訊號的解讀也會亂掉。2% (w/w) 是「能形成足量 FRET pair、又不自我淬熄」的常用工作濃度。
4. 工具與材料: 
   - **FRET (Förster resonance energy transfer)**: donor → acceptor 之間距離 < 10 nm 才會發生的能量接力，效率隨距離 6 次方下降，是膜距離的奈米級量尺。
   - **NBD-PE (donor)**: 把 NBD 螢光染料接在 PE 磷脂頭基的類似物；激發 460 nm、發射 530 nm 綠光，會自然嵌進 Lip 膜。
   - **Liss Rhod-PE (acceptor)**: 把 Rhodamine 接在 PE 磷脂頭基的類似物；吸收 530 nm、發射 588 nm 紅光，與 NBD 配對形成標準 FRET pair。
   - **Förster 距離 (~ 10 nm)**: NBD/Rhod 對的 FRET 有效距離；距離翻倍、訊號掉成 1/64。
   - **FRET efficiency 公式**: $\text{FRET\,efficiency (\%)} = \dfrac{F_{588}}{F_{588}+F_{530}} \times 100$；ratiometric 設計消除濃度、光漂白與儀器漂移。
   - **Microplate reader (Ex 460 / Em 500–650 nm 掃描)**: 微孔盤式光譜儀，激發單一波長後掃描整段發射光譜。
   - **Self-quenching**: 染料在膜上太擠時彼此壓抑訊號的現象；2% (w/w) 是避開自我淬熄的常用濃度上限。
   - **Ratiometric measurement**: 用兩個波長訊號的比值代替單一波長，把濃度、漂白、光路差異同步消掉的標準量測法。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了證明「co-incubation + probe-sonication」做出的 hELs 真的是「膜層級融合」而不只是「物理聚集」，採用了 NBD-PE / Liss Rhod-PE 雙染料的 FRET assay。它解決了一般 DLS、size 量測無法區分「真融合 vs 假聚集」的瓶頸，把分子層級的膜稀釋變成可量化的 530 nm / 588 nm 光譜變化，為下游 FACS 表面 marker、DLS 物理特性提供分子尺度的融合佐證。
