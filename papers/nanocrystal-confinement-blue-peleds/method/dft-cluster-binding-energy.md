# DFT 分子簇結合能與配位幾何計算 (ADF/AMS2023)

1. 引用自哪篇 paper: nanocrystal-confinement-blue-peleds
2. Outline (任務主線): DFT 分子簇結合能與配位幾何計算 (ADF/AMS2023)
3. Method:
   作者把 PbBr2 一顆和 OEGA 一條（或多條）放進量子化學軟體 (ADF/AMS2023)，讓電腦用密度泛函理論 (DFT) 解這群原子在不同擺位下的電子分布與總能量。流程是：擺幾種可能的牽手姿勢（醚氧單點、羰氧單點、兩點/三點/四點齊抓），讓軟體把每種姿勢鬆弛到能量最低點，再算複合物總能量 E_complex；定義分子簇結合能 Eb = (E_complex − E_PbBr2 − n·E_OEGA) / n，Eb 越負代表抓得越緊。OEGA 是柔性分子，隨手挑一個構象可能掉進高能量局部極值，所以多個起始構象都跑一遍幾何優化、取最穩定態才有代表性。技術細節上，泛函用 PBE（夠快又對配位鍵合理）+ D3-BJ 色散校正（補上 PBE 漏掉的范德華吸引），Pb 等重原子用 ZORA 把相對論效應塞進方程式；基組用三套價層加極化函數的 Slater-type orbital (TZP)，H/C/O/S 全電子算到底，Br/Pb 內層用凍結芯近似省計算量。

   OEGA 之所以特別，在於它身上同時帶「強而少」的羰氧 (carbonyl O，丙烯酸酯端基，單點 −0.74 eV) 與「弱而多」的醚氧 (ether O，聚乙二醇尾巴上約 9 個，單點 −0.67 eV)。羰氧像錨點先把 OEGA 拉近 Pb，醚氧再順著鏈條像冠醚樣把 Pb 包圍起來形成多齒結合 (chelation)。一個磁鐵抓 Pb 是 −0.67 eV，四個磁鐵在同一條繩子上同時抓住同一顆 Pb（四齒配位），結合能會疊加並因幾何鎖定達到 −1.51 eV。這就是螯合效應的關鍵——多隻手由於已被同條鏈帶到 Pb 附近、不必再從溶液中游過來，抓上去的「機率代價」幾乎不用付。

   光看單點 Eb 會得出錯誤結論：OEGA −0.67 eV 比 DMSO 單體 −1.07 eV 弱，照理 OEGA 抓不過 DMSO；但實驗 XPS/NMR 明明看到 OEGA 進入 Pb 第一配位殼層。化解矛盾的關鍵在 Gibbs 自由能 ΔG = 電子能 + 零點振動能 (ZPE) + 壓力體積項 + 0→298 K 熱能修正 − T·S。完整溶劑置換反應「OEGA + 4 DMSO·PbBr2 → OEGA·PbBr2 + 4 自由 DMSO」釋出 4 個原本被綁在 PbBr2 上、現在自由飄回溶液的 DMSO 分子，它們重新獲得平移轉動自由度，系統熵 S 大幅提升、−T·S 變得很負。算出來：OEGA 路徑 ΔG = −0.46 eV（自發進行），DMSO 路徑 ΔG = +0.20 eV（不自發），熵驅動的差距約 −0.66 eV。換句話說，OEGA 之所以贏，不是抓得更緊，而是「進入時釋放出更多自由分子」——這把表觀的能量劣勢翻成熵驅動的優勢。

4. 工具與材料:
   - **ADF/AMS2023**: 量子化學軟體套件，本研究用來在分子簇尺度執行 DFT 計算（Fonseca Guerra 1998、Velde 2001、Baerends 2025）。
   - **密度泛函理論 (DFT)**: 從電子密度近似求解多電子薛丁格方程式，獲得分子總能量、幾何與電荷分布。
   - **PBE 泛函**: 廣義梯度近似 (GGA) 交換關聯泛函，計算量低且對配位鍵能量合理。
   - **D3-BJ 色散校正**: Becke–Johnson damping 的 Grimme D3 色散校正，補回 PBE 漏掉的長程范德華吸引。
   - **ZORA 相對論 Hamiltonian**: 二階純量相對論近似，處理 Pb 等重原子內層電子的相對論性自旋-軌道效應。
   - **TZP Slater-type orbitals**: 三套價層加一套極化函數的 Slater-type 基組，精度與成本平衡。
   - **凍結芯近似 (frozen core)**: 把不參與化學鍵的內層電子固定不算 (Br 1s–3p、Pb 1s–4d)，省計算量。
   - **分子簇結合能 Eb**: Eb = (E_complex − E_PbBr2 − n·E_molecule) / n；OEGA 四齒配位 −1.51 eV、單點醚氧 −0.67 eV、羰氧 −0.74 eV、DMSO 單體 −1.07 eV。
   - **Gibbs 自由能 ΔG**: ΔG = E_ele + ZPE + pV + ΔU(0→T) − T·S，298 K、1 atm 下的完整熱力學指標；用 VASPKIT 計算。
   - **多齒螯合 (chelation)**: 同一條鏈上多個配位點同時抓住同一金屬中心，結合能近似疊加並因幾何鎖定增強。
   - **熵驅動置換**: OEGA + 4 DMSO·PbBr2 → OEGA·PbBr2 + 4 自由 DMSO，釋放自由 DMSO 提升熵，ΔG 從 +0.20 eV 翻成 −0.46 eV。

5. 與此篇文章的關係:
   在《In situ nanocrystal confinement for efficient blue perovskite LEDs》這篇文章中，作者為了解釋「為什麼明明 OEGA 單點抓 Pb 比 DMSO 弱，卻能搶進 Pb 的第一配位殼層」，採用 ADF/AMS2023 DFT 算分子簇結合能與完整溶劑置換 ΔG。這個計算吃 PbBr2 + OEGA 多種牽手姿勢的幾何結構，產出 Eb 與 ΔG 數值，把「OEGA 多齒螯合 + 釋放自由 DMSO 的熵增」這個機制量化，為下游 VASP 表面相穩定性計算與 MD 聚合動力學模擬奠定『OEGA 確實進得了 Pb 配位殼層』這個前提。
