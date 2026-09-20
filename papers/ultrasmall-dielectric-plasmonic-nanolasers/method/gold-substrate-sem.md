# 電漿子雷射的 Au 基板部署與 SEM 位置關聯

1. 引用自哪篇 paper: ultrasmall-dielectric-plasmonic-nanolasers
2. Outline (任務主線): 電漿子雷射的 Au 基板部署與 SEM 位置關聯
3. Method:
拿到 silica-coated (或未包 silica 的裸) InGaP disk 懸浮液後，要把它們部署到 semiconductor-gold 介面上激發 SPP 高階 WGM 模。作者選商用多晶金基板 Platypus，它的 root-mean-square (RMS) 表面粗糙度只有約 0.7 nm——差不多幾個原子高度的起伏。這件事看似小，實際攸關成敗：SPP 是沿金-半導體介面貼著跑的波，任何幾 nm 的凸起都會把它散射掉、直接殺掉腔體 Q。若用一般實驗室濺鍍金 (RMS 幾 nm 起跳)，360 nm disk 上的 SPP Q 會從 ~30 掉到只剩 3-5，disk 根本點不亮；本文能把最小電漿子雷射做到 360 nm 直徑，選對基板的功勞不亞於 Purcell 增強。順帶一提，這款基板也是作者實驗室先前 CsPbBr₃ 電漿子雷射工作 (Cho et al., Sci. Adv. 2021, ref 21) 使用同一款——用同款材料才能對比不同增益材料在相同 SPP 環境下的表現，Purcell factor 從 2.3 (介電) 到 19 (電漿子) 才會是材料貢獻而非基板雜訊。部署方式非常直接：drop-cast (溶液滴塗)。用移液管把乙醇裡的 disk 懸浮液滴一滴到金上，乙醇室溫蒸發後 disk 就靠 van der Waals 力貼上金表面——因為金夠平、disk 夠輕，貼上後幾乎零距離地躺著，正好形成激發 SPP 所需的緊密介面。

為什麼用隨機 drop-cast 而不用光鑷或機械擺放讓 disk 精準排列？因為作者的量測目標是「單顆 disk 的光譜性能」，不是要把 disk 排成陣列做元件；只要一片視野內有幾十顆孤立、彼此距離夠大 (>10 μm) 的 disk 就夠用。drop-cast 一次能撒上百顆到視野中，隨手挑其中乾淨的量測即可；光鑷或機械擺放雖精準卻慢，還需要昂貴操縱系統，對「不需要陣列」的單顆量測是過度工程。

量測本身其實是「光學-結構逐一綁定」的問題。每顆 disk 的直徑、高度都直接決定它的雷射波長、閾值與 Q；同一批粒子雖然直徑目標一樣，但灰化與 RIE 仍會有 ±10-20 nm 散布，這足以讓兩顆看起來相同的 disk 雷射波長差 10 nm 以上。光學數據若不知道「這顆到底是 458 nm 還是 471 nm」，就沒法反推 WGM 模的階數或 Purcell factor 是否符合理論預測。作者的解法是量完光學後不換樣品直接標記：把泵浦脈衝能量拉到平常的十倍以上，對準目標 disk 旁邊幾微米處的空白金區域擊發——高能量脈衝把金局部加熱到熔點以上，留下一個 SEM 可見的坑或環 (Figure S10a)，坑的形狀直接標出「目標 disk 就在坑的東北 3 μm 位置」。之後把樣品送 SEM (Figure S10b)，操作者順著燒印圖案就能找回同一顆 disk、量出實際直徑、厚度與缺陷，把光學數據與物理結構一一綁定。若省掉這一步，SEM 下幾十顆長得都很像的 disk 完全沒法對號入座，Purcell factor 反推與 WGM 階數判定都會報廢——這是解決「量測完就找不回同一顆粒子」的實務招式。
4. 工具與材料:
- **商用多晶金基板 Platypus**: RMS 表面粗糙度 ~0.7 nm 的低粗糙度金基板；同一款也用於 Cho et al. (Sci. Adv. 2021, ref 21)，確保跨論文 SPP Q 可比。
- **RMS 表面粗糙度 (~0.7 nm)**: root-mean-square roughness；SPP 沿介面傳播時任何幾 nm 凸起都會散射掉波，決定電漿子腔體 Q。
- **drop-cast (溶液滴塗)**: 用移液管把乙醇 disk 懸浮液滴到金上，乙醇蒸發後 disk 靠 van der Waals 力貼上金表面，形成近零距離的 semiconductor-gold 介面。
- **高能量泵浦脈衝燒印 (Figure S10a)**: 把 pump fluence 拉到十倍以上，對目標 disk 旁空白金區域擊發、局部熔化金留下 SEM 可見坑/環當定位記號。
- **SEM 位置關聯 (Figure S10b)**: 光學量測完的樣品順著燒印圖案送 SEM，找回同一顆 disk 並量測實際直徑、厚度、缺陷，把光學數據與物理結構逐一綁定。
5. 與此篇文章的關係:
在《Ultrasmall InGa(As)P Dielectric and Plasmonic Nanolasers》這篇文章中，作者為了讓小到 360 nm 的自由 InGaP disk 借金基板激發 SPP 高階 WGM 而發雷射，把 disk 直接 drop-cast 到 RMS 0.7 nm 的商用 Platypus 金上，再用高能量泵浦脈衝在金表面燒印定位記號、事後送 SEM。這步解決了「單顆量測後找不回同一顆粒子」與「一般粗糙金會把 SPP 散射殺光」的雙重瓶頸，向下游供出「光譜數據 ↔ 真實直徑/厚度」逐一綁定的單顆資料集，讓 Q ~30、Purcell factor ~19 這些定量結論站得住腳。
