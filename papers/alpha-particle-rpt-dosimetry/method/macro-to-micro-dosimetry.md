# Macro-to-micro 多尺度劑量學模型：把預臨床 micro-scale 結果轉譯至人類

1. 引用自哪篇 paper: alpha-particle-rpt-dosimetry
2. Outline (任務主線): 因人體無法直接取得 nephron 等 micro-scale α 分布資料，建立一套以「預臨床 organ + sub-compartment PK 求出 apportionment factor → 臨床 whole-organ quantitative imaging × apportionment factor → 預測 sub-compartmental 毒性」的轉譯流程。
3. Method:
α 粒子射程只有 50–100 μm，比腎小球、近端小管、骨小樑網眼都小，藥物若集中在某些 sub-compartment（器官內負責特定功能的小結構，例如腎小球、近端小管、骨小樑表面 endosteum），能量幾乎全留在它撞到的那個小結構裡。整顆腎臟「平均下來」可能只有 5 Gy，但真正受燒的近端小管可能有 30 Gy，差到 6 倍。整器官平均會把這個峰值平均掉，失去毒性預測力。相對地，β 粒子在組織裡走幾毫米，能量自然「攤平」，整器官平均已接近真實——這就是為什麼 αRPT 必須額外做一套 macro-to-micro 流程。

解法是把問題拆成「預臨床量微觀、臨床用整器官影像放大」兩段。預臨床端 (§2.D)：用 α-camera 拍出 ²²⁵Ac-抗體在腎切片裡每個 α 衰變的位置，組織病理量出 nephron 各 sub-compartment 在整顆腎臟裡佔的體積比例 (fractional occupancy)，配上 Hobbs et al. 2012 的 nephron-based kidney 幾何模型 [24]，算出 apportionment factor = 子結構吸收劑量 / 整器官吸收劑量（例如為 3，代表那一小塊劑量是整器官平均的 3 倍）。臨床端 (§2.E)：用量化 SPECT 或 planar imaging 在病人身上量整顆腎臟的時間積分活性 $\tilde{A}$，餵進 §3-A 的 MIRD 公式算出整器官平均 Gy，再乘上 apportionment factor，就得到那一小塊真正會壞掉的位置的 Gy 數。整套流程就是 Figure 7 的 macro-to-micro pipeline。理由很直接：臨床 SPECT 解析度大約 1 cm，而 sub-compartment 尺度只有 10–100 μm，差兩個數量級；只能犧牲動物取切片才能拿到 μm 級的真實答案。

光把比例表算出來還不夠，這套流程要過兩道驗證才能放心搬到人身上。第一道是「跨模型穩健性」：在小鼠、大鼠、不同抗體系統都量 apportionment factor，看數字是否相近（Josefsson et al. [25, 26] 在 ²²⁵Ac-7.16.4 系統做的就是這件事）。若各模型差很多，代表 apportionment factor 主要被該模型的藥物動力學左右、不是器官結構固有屬性，臨床外推就有大誤差。第二道是「內部毒性預測」：在同一個預臨床模型裡，用 sub-compartment 劑量去預測實際觀察到的毒性。Hobbs et al. 2012 ²²³Ra 骨髓毒性模型 [27] 是經典案例——²²³Ra 主要停在骨小樑表面，整顆骨頭平均下來骨髓劑量看似還好，但 sub-compartment 劑量可以解釋為什麼有些動物出現骨髓抑制。這條鏈通過後，才能放心把 apportionment factor 搬去人類。

想跳過動物模型、直接用人類整器官劑量乘上「教科書裡腎小球的體積比例」是不行的。教科書的「腎小球佔腎體積 5%」只是解剖學體積比例，預設「藥物均勻分布」；但 αRPT 的藥物正是專門集中在某些 sub-compartment，這份不均勻的活性分布才是 apportionment factor 的真正分子。用體積比例代替 apportionment factor 等於用「平均薪資」算「個人收入」，前提錯了結果就錯了——預測的 sub-compartment 劑量可能低估好幾倍，臨床上會以為腎臟還安全。
4. 工具與材料:
- **Sub-compartment**: 器官內執行特定功能的小結構，例如腎小球、近端小管、骨小樑表面 endosteum；α 毒性的真正落點。
- **Apportionment factor**: 子結構吸收劑量 / 整器官吸收劑量；macro-to-micro 流程的核心比例表。
- **Fractional occupancy**: 每個 sub-compartment 在整器官體積中佔的比例，由組織病理量得。
- **α-camera (§2.D)**: 預臨床用來在切片上畫出 α 衰變位置的影像工具，提供 μm 級活性分布。
- **Nephron-based kidney model (Hobbs 2012 [24])**: 把腎臟切成腎小球、近端小管等次結構幾何的計算模型，用來算 apportionment factor。
- **²²³Ra 骨髓毒性模型 (Hobbs 2012 [27])**: 內部驗證點：用 sub-compartment 劑量預測實際骨髓抑制，證實 macro-to-micro 流程可靠。
- **跨模型穩健性檢驗 (Josefsson [25, 26])**: 在不同預臨床模型量 apportionment factor，看是否一致，以判斷能否搬到人類。
- **量化 SPECT/planar imaging (§2.E)**: 臨床端取得整器官時間積分活性 $\tilde{A}$ 的影像工具；解析度約 1 cm，無法直接看 sub-compartment。
5. 與此篇文章的關係:
在《Dosimetry, Radiobiology and Synthetic Lethality: Radiopharmaceutical Therapy (RPT) with Alpha-Particle-Emitters》這篇文章中，作者為了預測 αRPT 在腎臟、骨髓等器官的真實毒性，採用了 Hobbs et al. 2012 的 nephron-based kidney 與骨髓毒性模型搭建的 macro-to-micro 流程。它解決了「人體無法直接取切片量 nephron 級 α 分布、但整器官平均劑量又會嚴重稀釋 sub-compartment 毒性」的瓶頸，吃進預臨床 α-camera 與組織病理資料以及臨床量化 SPECT 影像，產出 sub-compartment 級的 Gy 數，供下游劑量-毒性決策使用。
