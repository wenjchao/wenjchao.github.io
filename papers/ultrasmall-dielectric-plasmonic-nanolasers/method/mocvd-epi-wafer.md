# 雙色磊晶晶圓的 MOCVD 客製化成長

1. 引用自哪篇 paper: ultrasmall-dielectric-plasmonic-nanolasers
2. Outline (任務主線): 雙色磊晶晶圓的 MOCVD 客製化成長
3. Method:
這個子項在做的事，就是「一次把整個雷射粒子的所有材料層預先烤在同一片晶圓上」。作者不自己長晶片，而是把層次配方交給廠商廈門 Powerway，對方用金屬有機化學氣相沉積 (MOCVD) 在直徑 3 吋 (~7.6 cm) 的 GaAs 底盤上，通入 trimethylgallium、trimethylindium 這類金屬有機前驅氣體與 phosphine、arsine 等 V 族氣體，在約 600–700 °C 的表面熱裂解、按秒切換氣體流量，一層一層長出 5 nm 到 400 nm 不等的 III-V 薄膜，達到原子級厚度精度。雙色晶圓由下往上這樣分區（Fig. 4a 上圖）：3 吋 GaAs 基板 → 400 nm GaAs 底部犧牲層 → 第一顆雷射盤（10 nm InGaP + 170 nm InGaAsP 主增益層 + 10 nm InGaP，發光 706 nm） → 400 nm GaAs 層間犧牲層 → 第二顆雷射盤（5 nm InGaP + 5 nm InGaAlP + 158 nm InGaP 主增益層 + 5 nm InGaAlP + 5 nm InGaP，發光 660 nm） → 300 nm GaAs 保護蓋層。兩個主增益層之所以發不同顏色的紅光，是因為半導體的發光波長由「能隙 (bandgap)」決定：InGaP 的能隙約 $1.88\,\mathrm{eV}$ 對應 660 nm 紅光，把配方裡一部分 P 換成 As 變成 InGaAsP、能隙下降到約 $1.76\,\mathrm{eV}$，波長就往紅移到 706 nm；於是同一片晶圓內建了兩個中心波長差 56 nm 的紅光源。

為什麼主增益層兩側非要各夾一層 5 nm 的 InGaAlP、最外側還要再包一層 5 nm 的 InGaP？答案是「井壁 + 隔水膜」兩件事。半導體被泵浦後產生的電子與電洞本該在增益層裡合體發光，但若跑到晶片表面，切割與加工留下的懸空鍵會變成陷阱把它們「靜靜消掉」不放光，這就是非輻射的「表面複合 (surface recombination)」。InGaAlP 的能隙比 InGaP 大，就像挖了兩道「深井壁」把載子鎖在中央 178 nm InGaP 主增益層裡（載子局限, carrier confinement），少了這一層 PL 亮度會變暗、閾值升高，甚至起不了雷射。但 InGaAlP 裡的 Al 特別怕水：一接觸細胞液就會慢慢氧化成疏鬆的 Al₂O₃，把原本平滑的盤面咬得凹凸不平——光在盤邊繞行時被粗糙面散射，Q 因子瞬間變差；同時 III 族離子逸出，還可能對細胞產生毒性。作者的解法是在 InGaAlP 兩面再各加一層 5 nm 的 InGaP 當「隔水膜」，把所有含 Al 的表面都藏在內部，外露的都是不含鋁的 InGaP。這樣同一顆盤既保有 InGaAlP 抑制表面複合的好處，又不會在水環境下降解。

設計上有三個非做不可的抉擇。第一，主增益層為什麼選 178 nm 厚的塊材 InGaP 而不是傳統的量子井 (quantum well)？因為這個奈米盤直徑只有 360–460 nm，光學模式（WGM）本身就已經很小，若增益層再更薄，光繞行時能「碰到」增益材料的比例（modal overlap）就會太低，得不到足夠增益。厚塊材把盤的中間段幾乎都填滿增益材料，光繞一圈能被放大到最大——這是把純介電雷射推到 460 nm 直徑的關鍵之一。第二，兩顆盤之間為什麼要插一層 400 nm 的 GaAs 而不是薄薄一層？因為 GaAs 是這片晶圓的犧牲層——稀 piranha 會選擇性把它溶掉——如果只留 5 nm，兩顆盤幾秒就同時掉下來，甚至黏成一顆雙層粒子把光譜搞亂；留 400 nm 給出足夠的「蝕刻時間窗」，工藝人員才能靠控制時間「先收上層一色、再收下層另一色」，把兩色粒子分批收集，這種「rainbow multilayer LP」設計沿用自 Dannenberg et al. (ACS Photonics 2021)。第三，為什麼把 MOCVD 委給廈門 Powerway 而不是自己長？因為 MOCVD 機台昂貴、arsine 有劇毒需要專門排廢、III-V 各層的組成與厚度重現性也需要長期經驗才能穩定；商用 foundry 已能保證 3 吋晶圓在整片面積內厚度均勻，作者只需交出配方，就把研發時間集中到後端奈米製程與雷射量測，這是「一次做整片 3 吋、百萬顆 LP」量產目標能實現的必要前提。
4. 工具與材料:
- **MOCVD (metal organic chemical vapor deposition)**: 把金屬有機前驅氣體 (如 trimethylgallium/indium) 與 V 族氣體 (phosphine, arsine) 通進加熱 (~600–700 °C) 的反應腔、在晶圓表面逐層長出 III-V 薄膜的長晶技術；可達原子級厚度精度。
- **3 吋 GaAs 基板**: 直徑約 7.6 cm 的單晶 GaAs 圓形底盤，作為所有 III-V 薄膜長晶與後續奈米加工的載體。
- **廈門 Powerway (Xiamen Powerway Advanced Materials Co. Ltd.)**: 本論文的商用 MOCVD 磊晶 foundry 供應商，作者交規格書、對方交出雙色多層晶圓成品。
- **主增益層 (178 nm InGaP)**: 第一片單色晶圓中央、能隙約 $1.88\,\mathrm{eV}$ 對應 660 nm 紅光的塊材增益層；為配合 subwavelength disk 提供足夠 modal gain，刻意做到 178 nm 厚。
- **主增益層 (170 nm InGaAsP)**: 第二片雙色晶圓下層、PL peak 706 nm 的另一種紅光增益材料；由 InGaP 部分 P 換 As 使能隙降到 $1.76\,\mathrm{eV}$。
- **In₀.₄₉(Ga₀.₅Al₀.₅)₀.₅₁P clad (5 nm)**: 夾在主增益層上下的高能隙 III-V 材料，作為載子局限 (carrier confinement) 井壁，抑制表面複合。
- **InGaP cap (5 nm)**: 貼在 InGaAlP clad 外側的不含 Al 隔水層，避免 Al₂O₃ 氧化與水中降解，同時保留 clad 抑制表面複合的效果。
- **GaAs 犧牲層 (300 nm cap / 400 nm 層間 / 400 nm 底層)**: 多處刻意夾入的 GaAs 層，用稀 piranha 選擇性溶掉以完成保護、層間分色與整片脫落。
- **rainbow multilayer LP 概念 (Dannenberg et al., ACS Photonics 2021, ref 24)**: 在同一片晶圓內堆疊多層不同能隙材料 + 犧牲層，一次量產多色 LP 的設計原型。
5. 與此篇文章的關係:
在《Ultrasmall InGa(As)P Dielectric and Plasmonic Nanolasers》這篇文章中，作者為了一次量產「數以百萬計、能覆蓋 80 nm 頻寬」的紅光雷射粒子條碼庫，把整套光學條碼的原料需求全部前置到晶圓設計，委託商用 foundry 以 MOCVD 客製磊晶預埋兩種紅光增益材料 (InGaP 與 InGaAsP) 加上多道 GaAs 犧牲層。這一步吃進的是實驗設計需求 (兩色、厚塊材、抗水環境)，交出的是可以直接進 UV 微影的多層 3 吋晶圓，是後續所有次波長奈米製程與生醫應用的物理起點。
