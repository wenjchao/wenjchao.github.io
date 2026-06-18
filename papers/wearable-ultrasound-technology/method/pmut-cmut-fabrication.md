# 微機械超音波換能器 (PMUT / CMUT) 製程

1. 引用自哪篇 paper: wearable-ultrasound-technology
2. Outline (任務主線): 微機械超音波換能器 (PMUT / CMUT) 製程
3. Method: 
   塊狀壓電陶瓷再厲害，遇到 wearable 的兩個現實需求就卡住：陣列間距想做到幾十微米（fine-pitch），驅動電路想直接黏在每顆元件後面省線。原因是塊狀陶瓷靠金剛石鋸片切片，間距受刀寬卡在 100 µm 以上，電路也只能拉線出去外接。作者改用 MEMS（微機電製程）——半導體做晶片那一套微影、蝕刻、薄膜沉積，用同一片矽晶圓刻出微米級的鼓膜陣列，每顆元件對準精度到 µm 級、間距可壓到 10 µm，而且整片晶圓還能直接整合 CMOS 驅動電路。MEMS 換能器的兩大代表就是 PMUT 與 CMUT，差別在於那層鼓膜是怎麼被振起來的。
   PMUT (壓電式微型換能器, piezoelectric micromachined ultrasonic transducer) 像一張被框緊的鼓膜：一層薄薄的壓電膜上下夾兩片電極，整片膜透過 CYTOP（透明環狀高分子黏結膜，cyclic transparent optical polymer）牢牢黏到矽底材上（Fig. 1e, refs 52, 239）。通電時壓電膜在平面內想收縮但邊界被框死，只好像鼓面一樣上下凸起——這個彎曲式振動模態 (flexural mode) 跟塊狀陶瓷整塊厚度方向胖瘦的振動完全不同。性能落在 4.9 kPa/V @ 1.5 MHz（ref. 54），代表每多 1V 驅動就能推出 4.9 kPa 聲壓，工作電壓被壓得很低，剛好對得上電池供電的 wearable 需求；它也可以直接做在 polymer substrate 上提高 compliance（ref. 56）。代價是「邊界夾死」這條前提：CYTOP 黏結若鬆動，壓電膜的面內應變會在側向滑動中浪費掉、根本不會變成上下振動，聲壓歸零。
   CMUT (電容式微型換能器, capacitive micromachined ultrasonic transducer) 完全不靠壓電——底電極上挖一個真空封住的薄膜空腔 (vacuum-sealed cavity)，空腔上方蓋一張可彎曲薄膜，薄膜表面也有電極，兩極之間隔一層絕緣層（Fig. 1f, refs 57, 240）。發聲時加交流電壓，靜電吸力把薄膜往下吸再放開、來回振動；收音時回波壓薄膜改變電容、被讀為訊號。它的線性聲壓對電壓 21 kPa/V @ 1.85 MHz（ref. 60），比 PMUT 高約 4 倍，但代價是必須先給薄膜一個固定的偏壓 (Bias voltage)：用一個直流電壓把膜往下吸到很靠近底電極的位置 (pre-stress)，後續交流訊號才能在這個極限位置產生大電容變化。這個偏壓動輒數十 V，遠超鋰電池的 3.7 V，所以裝置內必須加一顆升壓電路 (boost converter) 把電池電壓抬起來（refs 61, 62）。真空空腔同樣是不可妥協的前提：一旦氣體滲入，氣壓阻尼會壓死整片膜的振幅與頻寬，CMUT 就完全失能。
   兩個設計在 wearable 場景分流明顯。PMUT 不需偏壓、工作電壓低、不必額外升壓電路，整顆貼片靠電池直接驅動就好，特別適合需長時間戴在身上的低功耗監測——Ding et al. (ref. 99) 用 PMUT 做腸鳴音監測 (bowel sound monitor) 即走這條路。CMUT 雖然要多一顆 boost converter 與更精密的真空封裝，但敏感度可達 PMUT 的 4 倍、頻寬廣、能配合 MEMS 微影的精度做成 fine-pitch 陣列，特別適合需要高解析度的植入式相位陣列——Seok et al. (refs 84, 85) 把 16-element 1D 與 2D CMUT phased array 整合 ASIC 做成慢性神經刺激器 (chronic neurostimulator implant) 是代表案例。選 PMUT 還是 CMUT，本質上是看裝置能不能承受 boost converter 帶來的功耗預算。
4. 工具與材料: 
   - **MEMS**: 微機電製程 (microelectromechanical systems)，把半導體微影、蝕刻、薄膜沉積用來在矽晶圓上刻出微米級可動結構，使換能器能與 CMOS IC 整合。
   - **PMUT**: 壓電式微型換能器 (piezoelectric micromachined ultrasonic transducer)，壓電膜被邊界框住、以彎曲式振動模態發聲，4.9 kPa/V @ 1.5 MHz，工作電壓低。
   - **CMUT**: 電容式微型換能器 (capacitive micromachined ultrasonic transducer)，靠靜電力拉動真空封住的薄膜空腔，21 kPa/V @ 1.85 MHz，敏感度比 PMUT 高約 4 倍。
   - **Flexural mode**: 彎曲式振動模態——薄膜在邊界被框住的條件下，平面內應變被強制轉成上下凸起的振動，是 PMUT 的核心發聲機制。
   - **Vacuum-sealed cavity**: CMUT 底電極上方真空封裝的薄膜空腔；提供薄膜無阻尼振動的條件，氣體滲入會立即崩壞振幅與頻寬。
   - **Bias voltage**: CMUT 用來把薄膜往下吸到極限位置 (pre-stress) 的固定直流偏壓，動輒數十 V，是敏感度衝到 21 kPa/V 的關鍵。
   - **Boost converter**: 升壓電路，把鋰電池的 3.7 V 升到 CMUT 所需的數十 V 偏壓；CMUT 設計成本中的必要功耗代價。
   - **CYTOP**: 透明環狀高分子黏結膜 (cyclic transparent optical polymer)，把 PMUT 壓電膜固定到矽底材上，承擔彎曲式振動模態所需的『邊界被夾死』物理前提。
   - **Fine-pitch array**: 間距小到幾十微米的密集換能陣列；MEMS 微影對準到 µm 級才得以實現，bulk piezoelectric 受鋸片刀寬限制做不到。
5. 與此篇文章的關係: 
   在《Wearable ultrasound technology》這篇 Review 中，作者為了讓 wearable 裝置擺脫塊狀陶瓷的兩個瓶頸——間距被鋸片卡死、電路無法同晶片整合——介紹了 MEMS 製程的 PMUT 與 CMUT 兩種微型換能器。PMUT 走低電壓電池直驅路線、適合監測；CMUT 走高敏感度路線、適合植入式相位陣列。這套微型化路徑承接 2-A 的材料地圖，往下接續 2-E 的 ASIC 整合，是 wearable 系統從『手錶大小』再縮一個量級的關鍵基礎。