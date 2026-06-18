# DFT 量子化學計算反應能量輪廓

1. 引用自哪篇 paper: de-novo-design-of-luciferases
2. Outline (任務主線): DFT 量子化學計算反應能量輪廓
3. Method: 
   為了在動手設計口袋之前先把「化學現實」摸清楚，作者請 K. N. Houk 實驗室 (UCLA) 與西安交大的 D. Evans、P. Ma 用密度泛函理論 (Density Functional Theory, DFT)——一種從量子力學基本方程算出整個分子能量的工具——把整條發光反應切成七個關鍵停留點逐一計算（Extended Data Fig. 8a）。七個停留點依序是 Int1 (DTZ 脫質子後的陰離子)、Int2 (陰離子與 ³O₂ 剛碰在一起的複合物)、TS1 (兩者交換一顆電子的單電子轉移過渡態，single-electron transfer, SET)、Int3 (電子轉完後形成的 dioxetane——一個四元環過氧化物)、OSSTS2 (dioxetane 裂開前的開殼層單重態過渡態, open-shell singlet transition state)、Int4* (裂開瞬間的激發態)、Int5* (排出 CO₂ 後真正發光的最終產物)。把七點能量依反應順序連起來，就是一條反應能量輪廓 (free-energy profile)——曲線的山頂代表反應卡住的瓶頸，山谷代表暫時穩定的中間態。其中兩個停留點特別關鍵。Int1 陰離子態是反應起跑的前提：DTZ 中性形式下電子被緊緊綁在分子裡、氧氣搶不到；只有等 imidazopyrazinone 環上某個 N–H 把氫離子吐掉、那顆氮帶上負電後，整個分子的電子能階才被推高到能跳給三重態氧分子，反應才會起跑。Int3 dioxetane 則是發光的物理來源：碳-碳-氧-氧四元環角度被擠得很小、O–O 鍵又特別弱，等於一顆隨時想拆開的小彈簧；一旦拆開，兩個 C=O 雙鍵同時生成、多出的能量把其中一個 C=O 推進激發態，激發態回到基態時就把能量以一顆光子甩出去——這顆光子就是發光反應的最終產物。
DFT 結果直接告訴設計者「酵素該做什麼」。七步裡只有「陰離子形成」與「單電子轉移」這兩步的能量門檻會被周圍環境大幅左右——周圍越能穩定負電、越能調節質子來去，這兩步的門檻就降越多。其他步驟例如 dioxetane 自爆，能量本來就一路下坡、酵素插不插手都會自己跑完。結論明確：酵素的核心任務就是在燃料周圍打造一個能穩住負電的反應場 (reaction field)。再進一步看，DFT 輸出的部分電荷分佈顯示負電主要聚集在 imidazopyrazinone 環的 N1 那顆氮上。要穩住這個負電，最直接的辦法就是把一個帶正電的零件放到它隔壁——精胺酸 (Arg) 側鏈末端的 guanidinium 帶恆定正電、又能伸出多個 N–H 形成多重鹽橋，是天然胺基酸裡最適合的選手。整條 RifGen + RifDock 流程最頂層的硬規則「Arg guanidinium 強制放在 DTZ N1 旁邊」，源頭就在這條 DFT 曲線。
為什麼非得花這麼大力氣算 DFT？因為兩條替代路線都走不通：天然 marine luciferase 在發表時只有少數空殼結構 (apo)、沒人解出帶著燃料的版本 (holo)，沒有催化幾何可抄；DFT 標出來的關鍵中間態 Int2、TS1、OSSTS2 又都是壽命在皮秒到奈秒級的瞬時物種，普通酶動力學量不到。DFT 是目前唯一能把這些瞬時中間態量化到「能量差幾大卡」的工具。如果跳過 DFT 直接動手，最可能猜錯的方向有兩個：把正電零件擺去穩定中性 DTZ，氧氣永遠搶不到電子、反應起不來；或花力氣去加速 dioxetane 自爆，但這一步本來就自發、努力全白費。即使記得「該穩 anion」這條結論、卻忘了 DFT 的第二層發現——ΔG_SET 對周圍環境極性極度敏感——也會出問題：口袋如果太濕、太極性，電荷會被水分子搶走，鹽橋幾何再漂亮也救不回活性。所以 active site 必須同時滿足「Arg 擺在 N1 旁邊」與「口袋夠疏水、質子環境合宜」兩個條件，缺一不可。
4. 工具與材料: 
   - **Density Functional Theory (DFT)**: 一種從量子力學基本方程算出整個分子能量的工具；可對反應路徑上每個停留點分別計算 ΔG。
   - **free-energy profile**: 把反應路徑上各停留點的能量依順序連起來的曲線，山頂是反應瓶頸、山谷是暫穩中間態。
   - **Int1 (anionic DTZ)**: DTZ 在 imidazopyrazinone 環上脫質子後形成的陰離子，是反應起跑的前提。
   - **Int2 / Int3**: Int2 是陰離子 DTZ 與 ³O₂ 剛碰上的複合物；Int3 是電子轉移後形成的 dioxetane 四元環過氧化物。
   - **TS1 / OSSTS2**: TS1 是 SET 過渡態；OSSTS2 是 dioxetane 裂開前的開殼層單重態過渡態。
   - **single-electron transfer (SET)**: 陰離子 DTZ 把一個電子轉給三重態氧分子 (³O₂) 的步驟；ΔG_SET 對周圍環境極性極度敏感。
   - **dioxetane**: 碳-碳-氧-氧四元環過氧化物；環張力高、O–O 鍵弱，自發拆開時把能量推進激發態 C=O，回到基態時釋放光子。
   - **reaction field**: 受質周圍的化學環境（電性、質子活度、疏水度）；酵素的設計目標就是打造一個能穩定 anion 的反應場。
   - **NSF XSEDE (OCI-1053575) / NSFC 22103060**: 提供 DFT 計算所需高效能運算配額的兩個資助來源。
5. 與此篇文章的關係: 
   在《De novo design of luciferases using deep learning》這篇文章中，作者為了從零打造能催化人工燃料 DTZ 發光的酵素，先用密度泛函理論 (DFT) 計算整條發光反應的自由能輪廓。DFT 解決了「沒有 holo 結構可抄催化幾何、瞬時中間態又抓不到」的瓶頸，把 Int1–Int5 七個停留點與 TS 一次量化。產出的結論「酵素必須穩定 anion、放 Arg 在 imidazopyrazinone N1 旁」直接餵給下游 RifGen/RifDock 當作硬規則。
