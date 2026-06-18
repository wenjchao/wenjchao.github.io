# 巨觀力學 (Compression Test)

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): 巨觀力學 (Compression Test)
3. Method: 
   把水膠切成標準圓餅（直徑約 7 mm、厚 1 mm）放在兩片平行金屬板之間（儀器：ADMET MTESTQuattro），上板以固定速度往下壓直到樣本破裂。儀器同時記下兩個量：板施加的力 F 與板已經往下壓了多少距離 ΔL。應力 (stress, σ) = F 除以樣本剖面積 A，代表「單位面積上承受多少力」；應變 (strain, ε) = ΔL 除以原始厚度 L₀，代表「壓縮了原本的百分之幾」。把所有時間點的 σ 對 ε 畫出來就是「應力-應變曲線」。標準化成 1 mm 厚度很重要：因為應變定義是 ΔL/L₀，樣本厚度不統一的話「同樣的絕對下壓量」對不同樣本意義完全不同，10–20% 應變區間對應的絕對深度不一致，模數就摻雜了厚度差。從應力-應變曲線取 10–20% 應變這個線性段算斜率——曲線最前面 (<5%) 板剛接觸有「接觸瑕疵」斜率不可靠，>30% 水膠網路被壓垮進入非線性或破壞區、斜率也不代表材料彈性；10–20% 才是 GelMA 最乾淨的線性彈性區間。這個斜率就是 Young's modulus (E)。

   為什麼 NV 嵌進去後 Young's modulus 會從 5.1 kPa（純 GelMA）升到 8.7–11.1 kPa？Young's modulus 跟「網路中每單位體積的交聯點數」直接相關——交聯越多、整體越難變形、模數越高。NV 嵌進 GelMA 後表面跟 GelMA 鏈形成非共價鍵 (氫鍵、靜電交互作用)，等於在原本的共價交聯網裡多加了一堆「縫合點」(pseudo-crosslinker)；總交聯密度上升、模數跟著升。鍵越強的 NV 加的縫合點越多：Gel-Lip 11.1 ± 1.9 kPa（最強）、Gel-hEL 9.5 ± 0.6 kPa（中間）、Gel-EV 8.7 ± 1 kPa（最弱），剛好反映 Lip > hEL > EV 的鍵強排序。為什麼還要做 compression 而不只 AFM？AFM-DMT 只量表面附近的奈米局部硬度，沒辦法回答「整塊水膠對埋在裡面的細胞而言有多硬」；compression 把整塊平均得到 bulk modulus，兩者互補。論文裡 Gel-EV / Gel-hEL 的 DMT 比 Young's 高的不對稱，正是因為 NV 在水中往表面遷移聚集——AFM 量到聚集點、compression 量到平均背景。每組 n = 4 是「材料夠用、組間比較還夠」的折衷，自動落在「n < 8 用 Kruskal–Wallis 或 Holm–Sidak」的小樣本統計範疇，避免假陽性。
4. 工具與材料: 
   - **ADMET MTESTQuattro**: 本研究使用的力學測試儀，parallel-plate 配置可做單軸壓縮，同步記錄力 F 與位移 ΔL。
   - **parallel-plate compression**: 兩片平行金屬板擠壓樣本的測試模式，常用於量水膠 bulk Young's modulus。
   - **stress (σ)**: 應力，σ = F / A，板施加的力除以樣本剖面積，單位 Pa。
   - **strain (ε)**: 應變，ε = ΔL / L₀，壓縮量除以原始厚度，無單位。
   - **Young's modulus (E)**: 應力-應變曲線線性彈性段的斜率 σ/ε，代表材料對壓縮的整體抵抗力。
   - **10–20% 應變區間**: GelMA 軟水膠最乾淨的線性彈性段：低於 5% 有接觸瑕疵、高於 30% 進入非線性或破壞。
   - **pseudo-crosslinker**: 嵌進 GelMA 的 NV 透過表面非共價鍵增加交聯密度，是 NV 升高 Young's modulus 的力學機制。
   - **n = 4 樣本量**: 每組壓縮做 4 塊樣本，落在 n < 8 範疇，論文統計改用 Kruskal–Wallis 或 Holm–Sidak 而非 ANOVA。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了提供「整塊水膠對細胞而言有多硬」的 bulk 力學參數，採用了 parallel-plate 單軸壓縮測試。這套方法解決了「AFM-DMT 只看奈米表面、無法代表整塊」的限制，把三種 NV 嵌入後對水膠交聯密度的整體影響量化成 Gel-Lip 11.1、Gel-hEL 9.5、Gel-EV 8.7 kPa 的單一數字，與 SEM 孔徑、AFM 局部模數、累積釋放曲線一起支撐 NV-GelMA 鍵強的排序結論。
