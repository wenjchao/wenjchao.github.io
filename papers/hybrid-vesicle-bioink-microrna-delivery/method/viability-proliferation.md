# Cell Viability / Proliferation 標準化評估

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): Cell Viability / Proliferation 標準化評估
3. Method: 
   細胞活性的第一道檢驗是 Live/Dead 雙染。作者把 CFs 以 25 × 10³ cells cm⁻² (2D 培養) 或 5 × 10⁶ cells ml⁻¹ (嵌入 GelMA 的 3D 培養) 的密度接種，加入要測的 NV 後，於指定時間點 (1, 3, 7 天) 把 2 µl ml⁻¹ Ethd-1 + 0.5 µl ml⁻¹ Calcein AM 的混合液加入孔中，37 °C / 5% CO₂ × 30 分鐘，再用 Zeiss Axio Observer D1 螢光顯微鏡拍照。Calcein AM 的設計很巧妙：本身是酯化版、無電荷又脂溶性高、能穿膜進入細胞質；一旦進細胞會被內生酯酶切掉酯鍵、變成帶負電的 calcein 並發綠光，被「鎖」在細胞質內。死細胞因為膜破了 calcein 會漏出去，所以只有「膜完整 + 酯酶活著」兩條件都符合才會發綠。Ethd-1 則反過來——它是兩個 ethidium 接在一起、帶兩正電的大分子，完整膜進不去；細胞一死膜破洞，Ethd-1 就鑽進去卡進 DNA 雙螺旋兩條鏈之間 (intercalation)，紅色螢光增強好幾百倍。所以螢光顯微鏡下活的綠、死的紅，乾淨俐落。

   第二道檢驗是 PrestoBlue 代謝活性。它的主成分是 resazurin (藍色、不發光)，進活細胞後被粒線體上的還原酶 (reductase) 接收兩個電子變成 resorufin (粉紅色、強螢光)——代謝越活躍、還原越快、顏色越紅。試劑用完整 DMEM 培養基依 1:9 比例稀釋、與細胞共孵育 30 分鐘，再用 plate reader 讀吸光度。這裡有個小細節：為什麼要同時讀 570 nm 和 600 nm？570 nm 是 resorufin 的吸收峰，但會受培養基顏色、孔板差異等光路雜訊污染；600 nm 處 resorufin 幾乎不吸收，所以 600 nm 訊號就是純背景。雙波長相減可校正每孔個別差異。最後再把每孔的 Day n 讀數除以自己的 Day 1 讀數作為 fold change，目的是消除 Day 0 播種時 ±10~20% 的細胞數誤差，讓後續比較只反映「真的長了多少」而不是「一開始就比較多」。

   兩個 assay 為什麼一定要平行做？因為「活著」這件事不只一個層次。Live/Dead 只看膜有沒有破，但有些細胞會處在「膜還沒破、代謝卻已經停」的亞健康狀態 (例如 G0 休止期或慢性毒性累積)，這在 Live/Dead 看起來和健康細胞一樣綠。如果只做 Live/Dead 就下結論「無毒」，會錯過某個 NV 配方把代謝壓得很低的隱性毒性。PrestoBlue 補上「粒線體有沒有在工作」這層定量指標，才能識別出來。一個量物理門禁、一個量能量代謝，兩者結合才能完整描述細胞到底有多活。
4. 工具與材料: 
   - **Live/Dead assay**: Calcein AM (染活) + Ethd-1 (染死) 雙染螢光法，看細胞膜完整性。
   - **Calcein AM**: 酯化版穿膜染料，進細胞質後被酯酶切掉酯鍵變帶負電 calcein 並發綠光，僅活細胞發綠。
   - **Ethidium homodimer-1 (Ethd-1)**: 雙正電 DNA 嵌入染料，膜破才進得去細胞核發紅光，僅死細胞發紅。
   - **PrestoBlue (resazurin)**: 藍色非螢光試劑，被活細胞粒線體還原為粉紅 resorufin 並發強螢光，量化代謝活性。
   - **Resorufin**: PrestoBlue 還原後的螢光分子，570 nm 為其吸收峰。
   - **雙波長扣背景 (570 / 600 nm)**: 用 600 nm 處 resorufin 不吸收的特性做純背景扣除，校正每孔光路差異。
   - **Fold change over Day 1**: 把 Day n 讀數除以自己的 Day 1 讀數，消除播種誤差。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者要驗證 hELs 與 Gel-hEL 都不會對 CFs 造成毒性。為此採用 Live/Dead + PrestoBlue 雙 assay 平行檢視，解決了「單一指標無法區分健康活著與亞健康活著」的瓶頸。兩個 assay 分別吃同批 CFs 進來，產出膜完整性與粒線體代謝活性兩個獨立讀數，供後續 NV 配方安全性與增殖效果的判定。
