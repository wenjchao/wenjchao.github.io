# 平面雙層 RSF 對照模擬

1. 引用自哪篇 paper: solid-ordered-bilayer-mechanics
2. Outline (任務主線): 平面雙層 RSF 對照模擬
3. Method:
   為了當囊泡結果的拓樸對照，作者另外建一份平面雙層 (flat patch) 系統。先用 CHARMM-GUI 線上膜搭建器 (Membrane Builder) 直接做一張平片：每葉片 324 顆脂質、共 648 顆，上下各墊 20 Å 水層；HSPC 系統依比例放 574 顆 DSPC + 74 顆 DPPC。CHARMM-GUI 預設輸出全原子座標（含氫），但本研究的 CHARMM36 united-atom 力場已經把每顆碳的氫融進那顆碳的有效原子，所以作者手動把氫原子全刪掉以對應這個力場——這套「先搭後刪氫」的折衷可繼承 CHARMM-GUI 對固態相的成熟拓樸，而不用自己處理脂質排列與初始 APL。其他模擬條件（NAMD 2.9、CHARMM36 united-atom、NPT、三維週期邊界）跟囊泡完全一樣，這樣才確保差別只在「平面 vs 球面」這個拓樸，不被力場或溫度差異污染。每個系統至少跑 100 ns，最後 50 ns 拿來做分析。

   彈性參數的萃取走的不是囊泡那邊的球諧波分析，而是 real-space fluctuation (RSF) 法 (Doktorova et al., PCCP 2017, ref 40；Johner et al., J. Phys. Chem. Lett. 2014, SI ref 6b)：不換基底，直接在 (x, y, z) 空間裡量每一顆脂質的局部變量。每顆脂質先畫一條指向 (director)：從頭基那邊（C2 與 P 兩顆原子的中點）拉到尾端（兩條尾巴最後一個碳的中點）。tilt 角 θ 就是這條 director 跟雙層整體法線的夾角——脂質越站直 θ 越接近 0，越躺平 θ 越大；lipid splay S_r 則是相鄰但弱相關的兩顆脂質之間 director 的散度，物理上是「相鄰兩顆脂質往不同方向歪開的程度」。tilt 對應「單一脂質要歪斜要花多少能量」、splay 對應「一塊小區域要彎曲要花多少能量」，剛好分別對映到 tilt 模量 κ_t 與彎曲剛性 κ。作者把所有時間步累積的 P(θ)、P(S_r) 轉成 potential of mean force (PMF)：因為熱平衡下 $F(x) = -k_{\mathrm{B}}T \ln P(x)$，PMF 的二次項係數就等於彈簧硬度這個彈性常數。再用二次函數在 [μ−σ, μ+σ] 範圍內擬合 PMF 的中央段，tilt 那邊抽出 κ_t、splay 那邊抽出 κ。擬合範圍鎖在中央一個標準差是因為這段熱平衡採樣最密、最符合線性彈簧假設；越往外尾巴採樣稀又會混進非線性耦合，硬擬會把非彈性成分算進去。APL 直接拿模擬箱面積除以脂質數做時間平均，KA 則沿用步驟 E 的 Waheed–Edholm 演算法。

   為什麼要花同樣力氣再做一遍平面系統？如果只報囊泡那邊「越固態反而越好彎」的反直覺結果，審稿人會立刻質疑是不是球面拓樸或方塊變形本身造成的人造效應。平面 patch 在同一份力場、同一個溫度、同一個分析路徑（Waheed–Edholm 共用）下跑，差別只在「沒有球面、沒有方塊變形」這一件事。如果平面 κ 也跟囊泡一樣下降，說明是脂質本身的特性；如果平面 κ 反而上升、囊泡卻下降，就明確指出反差來自拓樸。本研究剛好觀察到後者（Table 1：囊泡 κ 從 DMPC $7.22 \times 10^{-20}$ 降到 HSPC $3.55 \times 10^{-20}$ J；平面 κ 從 DMPC 約 $11.7 \times 10^{-20}$ 升到 HSPC $23.2 \times 10^{-20}$ J），這個趨勢相反正是「囊泡是剛硬小 patch 拼起來、patch 之間的折角讓整顆好彎」這個物理圖像的直接證據。

   整套 RSF 流程有兩個容易壞掉的環節值得注意。第一是水合層做太薄：平面 MD 系統會在 z 方向開週期邊界，等於上下無限重複多片膜，水層太薄會讓相鄰週期影像隔著薄水互相感受到對方的膜，最長波長的波浪被人為壓平、量出來的 κ 偏硬，tilt 分布也會被夾窄。20 Å 是經驗安全值——足夠把週期影像之間的耦合切斷，又不至於把模擬箱養得太大白白浪費算力。第二是 PMF 擬合範圍貪心：只有 PMF 中央區段才符合線性彈簧近似，越往外尾巴採樣越稀又混入非線性效應（脂質歪太多會撞到隔壁脂質、出現額外的耦合），固態膜還會多一份 shear elasticity。如果把擬合範圍拉到 [μ−3σ, μ+3σ]，等於把非線性段與大雜訊尾段都當成彈簧的一部分硬擬，二次項係數會被尾巴拉歪、數字偏大也偏不可重現。鎖在 [μ−σ, μ+σ] 是把「線性彈簧」這段最乾淨的訊號留下、其他都丟掉。
4. 工具與材料:
   - **planar bilayer (flat patch)**: 與囊泡相對的對照系統，648 顆脂質排成一張平片、上下各 20 Å 水層；只看局部 patch 性質、沒有球面拓樸。
   - **CHARMM-GUI Membrane Builder**: 線上膜搭建工具，自動處理脂質排列、水合與離子配置，輸出全原子初始座標。
   - **hydrogen removal**: 把 CHARMM-GUI 輸出全原子座標的氫原子全刪掉，以對應 CHARMM36 united-atom 力場。
   - **real-space fluctuation (RSF) method**: Doktorova et al. (PCCP 2017, ref 40) / Johner et al. (J. Phys. Chem. Lett. 2014, SI ref 6b) 的方法，直接在實空間量 tilt/splay 局部變量擬合彈性常數，不換基底。
   - **lipid director**: 脂質指向向量：從頭基的 C2–P 中點拉到尾端兩條尾巴最後一個碳的中點。
   - **tilt angle θ**: 脂質 director 與雙層法線之間的夾角；對應單一脂質歪斜的彈性常數 κ_t。
   - **lipid splay S_r**: 相鄰但弱相關脂質之間 director 的散度；對應 patch 彎曲的彈性常數 κ。
   - **potential of mean force (PMF)**: 由機率分布 P(x) 轉成的自由能曲線 F(x) = −kBT ln P(x)，二次項係數即為對應彈性常數。
   - **quadratic fit ([μ−σ, μ+σ])**: 在 PMF 中央一個標準差內做二次函數擬合，只保留線性彈簧段、避免非線性與雜訊尾段污染。
   - **tilt modulus κ_t**: tilt 方向的彈性常數，量「單一脂質要歪斜要花多少能量」。
   - **planar APL & KA pipeline**: APL 直接拿模擬箱面積除以脂質數做時間平均；KA 沿用步驟 E 的 Waheed–Edholm 演算法。
5. 與此篇文章的關係:
   在《Mechanical Properties Determination of DMPC, DPPC, DSPC, and HSPC Solid-Ordered Bilayers》這篇文章中，作者要解釋為何固態囊泡反而比液態好彎。他們用 CHARMM-GUI Membrane Builder 搭一份同力場的平面雙層，跑 real-space fluctuation (RSF) 法從 tilt/splay 萃取局部 κ_t 與 κ。這吃進與囊泡完全相同的力場與溫度條件，輸出 Table 1 最右欄的「平面 κ 隨 Tm 上升」結果，與囊泡 κ 隨 Tm 下降的趨勢正好相反，直接支持「囊泡是剛硬 patch 拼起來」的核心圖像。
