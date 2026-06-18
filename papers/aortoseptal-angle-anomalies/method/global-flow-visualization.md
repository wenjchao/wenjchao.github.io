# Global flow visualization (massless particle injection)

1. 引用自哪篇 paper: aortoseptal-angle-anomalies
2. Outline (任務主線): Global flow visualization (massless particle injection)
3. Method: 
ANSYS 算出來的『3D 速度場』本質上是『整個血液體積、每一格、每一時刻都有一個速度向量』的龐大資料集。如果直接畫成密集箭頭圖，整個心室裡塞滿了朝各種方向的小箭頭，人眼幾乎抓不到結構——『哪裡有渦流』『哪裡有噴流』『哪裡血液不太動』全被淹沒在箭頭海裡。為了把它變直觀，作者用兩個工具：體積渲染 (volume rendering) 把整個 3D 速度量級投影成半透明立體圖，整個 LV 內部速度高低分布一眼看到；再疊上虛擬粒子軌跡顯化流場流向。
作者在血液體積裡放了一群『虛擬粒子』(在電腦裡而已)，刻意設成『沒有重量、沒有慣性』(massless)——它們不會反過來干擾血液流動，也不會因慣性偏離流線，純粹流到哪裡跟到哪裡，留下的軌跡忠實地等於流場本身的流線。注入點選在二尖瓣口 (mitral orifice)，因為舒張期 (diastole) 血液正是從這裡灌入 LV——從『血液故事的源頭』開始追蹤，粒子會跟著血流一路經過 LV 內部、再從 LVOT 噴出。整套追蹤透過 ANSYS 內建的 Eulerian-Lagrangian 框架完成：前一步 ALE/Navier-Stokes 用 Eulerian 算出速度場 (固定座標等流體經過)，這一步用 Lagrangian 把粒子放進這個速度場、追蹤它們的位置 (跟著粒子走)。
這套可視化要找的是三個跟心動週期不同階段對應的流場特徵：舒張期渦環 (血液從二尖瓣灌進 LV 後在下游圍成的環狀漩渦)、收縮期 jet (心室收縮時從 LVOT 噴出的高速射流，作者取 peak systole t = 0.83 s 與 E-wave t = 0.33 s 兩個時刻的快照看)、recirculation bubble (陡角模型 jet 撞偏上緣後在下緣形成的回流區，Fig. 3 標 `b`，是陡角才會出現的關鍵特徵)。為什麼 TSM/OSI/|WSSdiv| 之外還要這套？因為量化指標只描述『內壁被什麼樣的力作用』——是『果』；可視化補上的是『血液怎麼流』——是『因』。看到陡角模型 jet 撞偏上緣、下緣出現 recirculation bubble，就能把『陡角→jet 偏→下緣 recirculation→下緣 WSS 異常』整條因果鏈串起來。
這套方法非 massless 不可。有質量的粒子有慣性，會出現『流場已經轉彎，但粒子還想直直走一段才轉』，軌跡偏離真正的流線；更麻煩的是質量還會反過來推流場 (two-way coupling)，原本要可視化的流場本身被改寫。結果就是軌跡圖不再是流場的忠實反映，看到的渦環或 recirculation bubble 可能是粒子慣性自己造成的假象。
4. 工具與材料: 
- **massless particles**: 電腦裡的虛擬追蹤點，沒有重量、不影響流場、不因慣性偏離流線；軌跡就是流場流線的忠實顯像。
- **mitral orifice injection**: 在舒張期把虛擬粒子放在二尖瓣口 (血液進入 LV 的源頭)，讓粒子完整跟過 LV 內部到 LVOT 噴出的流場演化。
- **Eulerian-Lagrangian 框架 (ANSYS 內建)**: Eulerian 法固定座標解出速度場；Lagrangian 法把虛擬粒子放進這個速度場追蹤其位置。本研究兩者結合。
- **volume rendering**: 把整個 3D 速度量級投影成半透明立體圖，相對於 2D 切片能保留立體上下文。
- **vortex ring / jet / recirculation bubble**: 三個關鍵流場特徵——舒張期入流形成的環狀漩渦、收縮期 LVOT 高速噴流、陡角模型下緣的回流氣泡 (Fig. 3 標 `b`)。
5. 與此篇文章的關係: 
在《Significance of aortoseptal angle anomalies to left ventricular hemodynamics and subaortic stenosis》這篇文章中，作者算出量化 WSS 指標後，仍需解釋『血液到底怎麼流』才會把陡角和下緣異常剪力連起來。他們用 ANSYS 內建的 Eulerian-Lagrangian 框架在二尖瓣口注入無質量虛擬粒子並做體積渲染，產出 Fig. 3 與 Supplementary Video 1，把抽象速度場變成可辨識的渦環、jet、recirculation bubble，讓 quadrant 分析的數字差異能對應到具體的流場結構解釋。
