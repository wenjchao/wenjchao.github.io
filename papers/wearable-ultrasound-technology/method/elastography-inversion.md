# Elastography 反演演算法 (Quasi-static + Shear-wave)

1. 引用自哪篇 paper: wearable-ultrasound-technology
2. Outline (任務主線): Elastography 反演演算法 (Quasi-static + Shear-wave)
3. Method: 
   B-mode 影像的明暗對比靠的是聲阻抗差異——兩塊組織的 $Z = \rho v$ 差越大、邊界越亮。但很多臨床上重要的軟組織差異（例如肝硬化區、乳房腫瘤、肌肉拉傷）聲阻抗跟周圍正常組織差不多，硬度卻差很多，B-mode 上根本看不出邊界，醫生眼裡只是「一片均勻灰」。彈性影像 (elastography) 正是補這個盲區：把組織硬度變成另一張可看見的影像，與 B-mode 互補。它的核心做法是先量「組織位移場」——壓一下身體後，組織裡每個小點被推到哪去的向量地圖。怎麼量？對同一個位置先後拍兩次 RF 訊號（變形前、變形後），把兩條波形做相關分析 (correlation)：把後拍波形上下平移，看平移多少時跟前拍最像，那個平移量就是這一點的位移。對影像中每一個小點都做一次，就拼出整片組織的位移場。從位移場「反推」硬度則是個倒過來的問題：物理上同樣施一個力，軟的地方位移大、硬的地方位移小，位移場其實已經把硬度資訊「印」進去了，演算法的工作就是猜一組硬度分布、用正向模型算出對應的預測位移、跟實測位移比對，反覆微調 (iterative optimisation) 直到預測與實測差最小。
   論文整理出兩種把組織推一下的方式。Quasi-static elastography 靠外加壓力——例如把探頭往皮膚壓一點點，整片組織被慢慢壓縮，量壓前壓後的位移場，再以 iterative optimisation 找出能最小化「預測 vs 量測位移差」的 shear modulus 分佈 (Hu et al. 2023)。但這條路線有個結構性限制：使用者壓探頭的力道每次都不一樣，外加壓力 (applied stress) 無法精準量到，所以只能算出「這一區比那一區硬幾倍」這種相對 modulus。Shear-wave elastography 走另一條路：用聚焦超音波在組織內某一點打一發強脈衝、靠聲輻射力 (acoustic radiation force) 把那點的組織瞬間推開，產生一個橫向擴散的剪切波 (shear wave)，再用 ultrafast imaging 追這個波在組織裡的傳播速度 $v_s$。根據彈性力學，組織越硬剪切波傳得越快，Young's modulus $E \approx 3 \rho v_s^2$（$\rho$ 是組織密度，幾乎是水的密度）。只要量到速度，硬度的絕對數值就出來了，能跟臨床參考值直接比對 (Liu et al. 2024)。所以這兩條路線的差別其實是「需不需要絕對模量」：縱向追蹤同一人變化用 quasi-static 就夠了，做臨床切點判斷（例如肝硬度 > 10 kPa 懷疑肝硬化）必須用 shear-wave。
   實作上彈性影像有兩個工程細節要注意。第一是「先用 B-mode 預定位 ROI」：彈性影像每張需要前後兩次量測或追整段剪切波傳播，框率比 B-mode 慢一個量級。如果整片組織都做又貴又慢，所以先用 B-mode 框出醫師關心的小區域 (region of interest, ROI)、再只對 ROI 做彈性影像，效率好得多。第二是反問題本身的「不適定 (ill-posed)」風險：反推公式假設組織只有小變形，超過這個範圍正向模型本身就不準；相關分析量位移時若雜訊大（汗水、組織快速移動），單一像素的位移誤差會被反問題放大成整片組織的硬度誤差。實務上要把壓的幅度控制在 ~1% 應變以內，並把連續多張位移場做平滑化，否則 modulus 圖像會出現大片虛假的「假硬區」或「假軟區」。最後一個常見誤用是硬把 quasi-static 包裝成絕對 kPa 數字——按壓力道每次不同，同一個人一週量五次可能得到五個不同的「絕對值」。要做臨床切點判斷必須用 shear-wave，quasi-static 只能比「自己跟自己」相對變化。
4. 工具與材料: 
   - **Elastography (彈性影像)**: 把組織硬度變成可視影像的成像模式，補 B-mode 看不出的軟組織邊界。
   - **Tissue displacement field (組織位移場)**: 壓一下身體後組織裡每個小點被推到哪去的向量地圖。
   - **Correlation (相關分析)**: 把變形前後 RF 波形對齊平移、找最相似平移量作為位移的計算方法。
   - **Iterative optimisation (反覆試錯找最佳解)**: 猜一組硬度分布、算預測位移、比對量測值、反覆微調直到差最小的反問題解法。
   - **Quasi-static elastography**: 靠外加壓力推動組織、量位移場、反推相對 shear modulus 的彈性影像 (Hu et al. 2023)。
   - **Shear-wave elastography**: 用聲輻射力激發剪切波、量波速反推絕對 Young's modulus 的彈性影像 (Liu et al. 2024)。
   - **Acoustic radiation force (聲輻射力)**: 聚焦超音波脈衝在組織內局部推開組織、激發剪切波的力。
   - **Shear-wave velocity $v_s$ → Young's modulus $E \approx 3 \rho v_s^2$**: 組織越硬剪切波越快，從波速直接換算絕對楊氏模數。
   - **B-mode 預定位 ROI**: 先用 B-mode 框出感興趣區域、再只對該區做較慢的彈性影像，節省計算。
5. 與此篇文章的關係: 
   在《Wearable ultrasound technology》這篇文章中，作者為了讓穿戴貼片看見 B-mode 看不出邊界的軟組織病變（肝硬化、乳房腫瘤、肌肉損傷），採用了兩條 elastography 反演演算法——quasi-static 解相對 shear modulus、shear-wave 解絕對 Young's modulus。這套方案解決了聲阻抗對比不足與外加壓力無法精準量化的瓶頸；它吃進連續 RF 訊號、產出組織硬度地圖，直接供臨床做組織分區與病程縱向追蹤。