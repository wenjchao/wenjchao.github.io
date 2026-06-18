# 壓電材料選用：Ceramics / Crystals / Polymers 的工程取捨

1. 引用自哪篇 paper: wearable-ultrasound-technology
2. Outline (任務主線): 壓電材料選用：Ceramics / Crystals / Polymers 的工程取捨
3. Method: 
   穿戴式探頭的「引擎」是壓電材料——通電會自己變形、被壓會自己生電的振膜：發聲時靠電壓擠它高速振動推進組織，收回波時靠回波壓它生出微弱電壓給電路讀。要替 wearable 挑壓電材料，作者列出五個直接決定貼片性能的指標。壓電應變係數 (d33, pC/N) 量的是「同樣電壓能擠出多少形變」，d33 越大就越靈敏、越大聲。機電耦合係數 (k) 用 $k = (U_{ME}/U_{E})^{0.5}$ 算「丟進去的電能有多少真的變成聲能」，理想值是 1。聲阻抗 (Z = $\rho v$, MRayl) 是聲波在材料裡前進的阻力——軟組織 Z ≈ 1.6 MRayl，材料 Z 若離這個數字太遠，聲波就會在介面被反彈、進不去身體。居禮溫度 (Curie temperature) 是材料內部電偶極排列被熱打散、永久失去壓電性的門檻，決定了貼片能不能承受體溫、消毒與自體升溫。
   作者把候選壓電材料分三路。第一路是壓電陶瓷 PZT (Pb(Zr,Ti)O3)：d33 = 374–650 pC/N、k = 0.17–0.58、Z ≈ 30 MRayl、居禮溫度 > 300 °C，靈敏度與耐熱優秀但又硬又脆、聲阻抗離組織太遠。第二路是壓電晶體 PIN–PMN–PT：d33 衝到 1550 pC/N、k = 0.56–0.95、Z = 34 MRayl、居禮溫度 130–170 °C，幾乎是理想 transducer，但製程要精準控制溫度、壓力與冷卻速率，貴又脆。第三路是壓電高分子薄膜 PVDF / PVDF–TrFE：d33 只有 20–29 pC/N、k = 0.15–0.3、楊氏係數 2.0–3.5 GPa（陶瓷約 50 GPa）、Z = 3.7–3.9 MRayl 跟組織幾乎相同，柔軟可彎但壓電弱。應用情境因此自動把材料分流：要拍清楚的影像（心臟、血管）走 PZT 路線（Hu et al. *Nature* 2023, ref. 63 心臟貼片）；要小尺寸高效能就改用晶體（Du et al. *Sci. Adv.* 2023, ref. 23 乳房貼片）；只當麥克風收音的 reception-only 應用如光聲成像 (photoacoustic) 或單點水中麥克風 (hydrophone)，選 PVDF（van Neer et al. *Nat. Commun.* 2024, ref. 25 大面積柔性陣列）。
   但 PZT 那條 30 MRayl 的聲阻抗顯然太硬，作者因此主推「拆＋接」的 1–3 composite：把整片陶瓷縱向切成一根根細柱、柱子之間灌環氧樹脂 (epoxy polymer matrix)，做成 1 個方向的陶瓷柱嵌在 3 維連續軟膠裡的複合材料。這一刀同時換來兩個收益：整體 Z 因為密度與聲速被軟膠拉低，從 30 MRayl 降到 9–17 MRayl 往軟組織靠近；每根柱子側邊被軟膠隔開後只在厚度方向自由振動，厚度模態耦合係數 kt 直接逼近單晶體理想的 k33。對於 reception-only 的高分子，作者則強調看另一個數字——壓電電壓常數 g33 = d33 ÷ 介電常數。PVDF 的 d33 雖小，但因介電常數比陶瓷低很多，g33 反而衝到 200–300 V·m/N 比陶瓷高很多。對「微弱回波→大電壓」的純收音任務來說，g33 才是真正的賣點，這就解釋了 PVDF 在光聲與水中麥克風 reception-only 場景無可取代的位置。
   兩個典型踩雷情境提醒了材料選擇沒有彈性。其一，如果省略 1–3 composite 直接拿純 PZT 貼皮膚：Z 比約 19：1 的介面會把絕大部分能量反彈回陶瓷面，發射時聲波還沒進到身體內就損失一大半、深部組織聽不到回波，接收時又被介面再反彈一次，影像幾乎全是雜訊——這是 wearable PZT 不做 composite 等於不能用的門檻。其二，如果在治療型貼片上選用 PVDF：它的居禮溫度大約 170 °C，一旦持續放音自體升溫撞到這條線，分子鏈會自由翻動把整齊的 C-F 偶極打散、發生不可逆的去極化 (depolarization)，材料就「忘了自己會壓電」再也回不來。這就是為什麼治療型應用幾乎不選 PVDF、要留居禮溫度 > 300 °C 的陶瓷當安全餘裕。
4. 工具與材料: 
   - **PZT (Pb(Zr,Ti)O3)**: 靈敏度與耐熱優秀的壓電陶瓷，d33 = 374–650 pC/N、居禮溫度 > 300 °C，但聲阻抗 30 MRayl 太高、又硬又脆，需做成 1–3 composite 才適合 wearable。
   - **PIN–PMN–PT**: 壓電晶體（lead indium niobate–lead magnesium niobate–lead titanate），d33 = 1550 pC/N、k = 0.95，近乎理想 transducer，適合小尺寸高效能 imaging（如乳房貼片）。
   - **PVDF / PVDF–TrFE**: 壓電高分子薄膜，d33 雖低 (20–29 pC/N) 但聲阻抗 (3.7–3.9 MRayl) 接近軟組織且柔軟可彎，g33 高，適合 reception-only 應用如光聲成像、水中麥克風。
   - **壓電應變係數 (d33)**: 同樣電壓能擠出多少形變，單位 pC/N；越大代表 transducer sensitivity 越高，是發射與接收靈敏度的核心指標。
   - **機電耦合係數 (k)**: 丟進去的電能有多少真的變成聲能，$k = (U_{ME}/U_{E})^{0.5}$，理想值為 1；1–3 composite 可把 kt 推近單晶 k33 理想值。
   - **聲阻抗 (Z, MRayl)**: 聲波在材料裡前進的阻力，$Z = \rho v$；軟組織 ≈ 1.6 MRayl，材料 Z 離這數字越遠，介面反射越大、能量損失越多。
   - **居禮溫度 (Curie temperature)**: 材料內部電偶極排列被熱打散、永久失去壓電性的門檻；PZT > 300 °C、PVDF ~170 °C，決定貼片能不能承受治療時的自體升溫。
   - **1–3 composite**: 把陶瓷縱向切成細柱、柱間灌 epoxy polymer matrix 的複合材料；同時降低聲阻抗 (Z 從 30 → 9–17 MRayl) 並把 kt 推近理想 k33。
   - **壓電電壓常數 (g33)**: 同樣壓力能在材料兩端生出多少電壓，g33 = d33 ÷ 介電常數；PVDF 因介電常數低，g33 = 200–300 V·m/N 反而比陶瓷高，是純收音場景的關鍵指標。
   - **Reception-only**: 純收音、不用發射的 wearable 應用，例如光聲成像 (photoacoustic) 接收雷射激發的組織振動、或單點水中麥克風 (hydrophone)。
5. 與此篇文章的關係: 
   在《Wearable ultrasound technology》這篇 Review 中，作者為了讓超音波貼片能在皮膚上連續工作，必須先解決最底層的材料選擇問題：壓電陶瓷 PZT、晶體 PIN–PMN–PT、高分子 PVDF 三類材料各自在 d33、k、Z、居禮溫度之間有極大差異。作者把三類材料映射到 imaging / reception-only / therapy 三類應用情境，並推 1–3 composite 解掉 PZT 聲阻抗過高的問題。這份材料地圖是後續 stack 設計、stretchable 陣列、ASIC 整合的起點，下游所有 wearable 工程選項都建立在這一步選對材料之上。