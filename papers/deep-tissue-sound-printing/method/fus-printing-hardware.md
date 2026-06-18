# FUS 列印硬體與印製流程

1. 引用自哪篇 paper: deep-tissue-sound-printing
2. Outline (任務主線): FUS 列印硬體與印製流程
3. Method: 
   整台機器像反向版的 3D 噴墨機，但「噴頭」換成一顆聚焦超音波換能器 (focused ultrasound transducer)：它是一面凹面的壓電陶瓷盤，通電震動發出超音波；凹面把所有波前折射到一個焦點，能量像放大鏡聚焦陽光集中在比一毫米還小的點上。作者準備三個頻率對應不同情境：8.75 MHz (Sonic Concepts H-108) 焦點最小、能印 150 μm 細線但只夠淺層；2.65 MHz (Sonic Concepts H-102) 焦點稍大卻能穿透 ≥ 15 mm 豬肉、雞肉做深層列印；1.1 MHz 作為更深穿透對照。8.75 MHz 那一支再加一組「阻抗匹配網路 (matching network)」電感電容，讓功率放大器 (Electronics & Innovation A075 RF amplifier) 與換能器阻抗一致，能量不會反射回放大器燒壞訊號鏈；訊號鏈前端是 Tektronix AFG3252 訊號產生器，初次定位則用 Panametrics 5072PR pulse-receiver + Rigol DS1054 示波器靠脈衝回聲反推焦距。換能器裝在可程式化的三軸機械手臂上，由 G-code 控制走位（功率 2–25 W、速度 2–2300 mm min⁻¹，table S3）。寫好 G-code → 機台移動到目標點 → 射出超音波 → LTSL 在焦點開孔釋出交聯劑 → 那一點當場膠化 → 移到下一點重複，直到走完整張圖案。
   
   焦點看不見、要靠量才會出現。作者先用 pulse-receiver 反推焦距，再用「光纖水中聲壓計 (fiber-optic hydrophone, Precision Acoustics)」精細量焦點壓力分布——細的光纖探頭尖端被聲波擾動，光相位變化反推聲壓；探頭裝在精密三軸手臂 (Velmex X-slide) 上逐點掃過 X-Z 與 X-Y 平面畫出壓力地圖，整套量測在除氣水 (ONDA Aquas-10) 中進行避免氣泡反射干擾，最後與 COMSOL FEM 模擬出來的壓力地圖比對。墨水盛在 2 mm 厚的塑膠框「墨水槽 (ink tank)」裡，上下兩面用 TPX® polymethylpentene 膜密封——這種塑膠的聲學阻抗跟水幾乎一樣，超音波全穿透不反射；底下再鋪 2 mm 厚 2 wt% agarose 模擬皮下軟組織。為什麼這麼挑剔？如果改用普通塑膠或玻璃，聲學阻抗錯配，反射波會跟入射波疊加形成「駐波」，焦點以外也升溫，原本只該膠化的點變成一片區塊都膠化，線條糊掉、甚至整槽提前膠化。作者還規定焦點離槽側邊 ≥ 10 mm，並用 37 °C 水浴模擬體溫——若用 23 °C 室溫，焦點要從 23 °C 推到 41.7 °C 需更多功率、熱擴散更不可控、線條斷斷續續，也無法把 ex vivo 條件直接搬到 in vivo。
   
   為什麼焦點會升溫？超音波是壓力波，在介質傳播時被分子摩擦轉成熱，這個比例叫聲吸收係數 α，焦點處能量最密集所以升溫最快，實際升溫由「輸入功率 × 曝露時間 × 材料 α」決定。作者用兩道控制把溫度停在 41.7~43 °C：一是 COMSOL 模擬不同頻率/功率/速度下焦點升溫曲線，先在電腦預估安全範圍；二是把細的線內熱電偶 (wire thermocouple, Pico TC-08) 插進真實 US-ink、讓 FUS 焦點掃過熱電偶當下記錄實際溫度曲線 (fig. S12、S13、S29)。為什麼 alginate 線條 8.75 MHz 給 2–14 W、2–2300 mm min⁻¹ 這麼寬範圍？因為功率拉高、速度放慢 → 焦點停留時間長、線變寬、適合厚膠；功率調低、速度加快 → 線細到 150 μm 但承載厚度有限。Table S3 列出已驗證搭配：pork tissue 下三角形 2.65 MHz / 18 W / 15 mm min⁻¹；細胞列印 8.75 MHz / 7 W / 10 mm min⁻¹（低功率保護細胞）；in vivo 膀胱 2.65 MHz / 7 W / 20 mm min⁻¹（深層、低劑量）。離子交聯水膠還留了一條「印錯可擦」後門：0.025 M EDTA 浸 5 分鐘就能讓 alginate US-gel 從組織上整片脫落 (protocol 採自 Najjar et al. 2004 Am. J. Ophthalmol.)，原理是 EDTA 把 egg-box 結構裡的 Ca²⁺ 鈕扣一個個拔下來，整片膠就鬆掉，給臨床留一個「暫時支架治療結束後可移除」的選項。
4. 工具與材料: 
   - **Focused ultrasound transducer**：凹面壓電陶瓷盤，把波前折射到焦點，能量集中在比 1 mm 還小的點。
   - **Matching network**：電感電容組成的阻抗匹配電路，讓功率放大器與換能器阻抗一致以避免反射損耗。
   - **Function generator + RF amplifier**：Tektronix AFG3252 + Electronics & Innovation A075，產生並放大射頻訊號驅動換能器。
   - **Pulse-receiver (pulse-echo)**：Panametrics 5072PR，靠脈衝回聲反推焦距，初次定位焦點位置。
   - **Fiber-optic hydrophone**：光纖尖端被聲波擾動的相位變化反推聲壓，繪製焦點壓力地圖。
   - **G-code 三軸定位**：可程式化的三軸機械手臂，依 G-code 走位、功率 2–25 W、速度 2–2300 mm min⁻¹。
   - **Ink tank**：2 mm 厚塑膠框、上下 TPX 膜密封，底下鋪 agarose 模擬皮下軟組織。
   - **TPX® polymethylpentene 膜**：聲學阻抗近水的塑膠膜，超音波全穿透不反射、避免駐波。
   - **Agarose 底墊**：2 mm 厚 2 wt%，模擬軟組織聲阻抗並吸收多餘熱。
   - **Wire thermocouple**：Pico TC-08 + 細線熱電偶內嵌 US-ink 量焦點實際升溫，驗證模擬參數。
   - **EDTA 去交聯**：0.025 M 浸 5 min 螯合 egg-box 中的 Ca²⁺，使 alginate US-gel 從組織脫落。
5. 與此篇文章的關係: 
   在《Imaging-guided deep tissue in vivo sound printing》這篇文章中，作者為了讓 US-ink 能在水浴 37 °C 模擬體溫條件下被精準掃描成 150 μm 等級圖案、並穿透 ≥ 15 mm 組織，搭建一台 FUS 焦點 + G-code 三軸定位列印硬體。它解決了 NIR 列印只能穿幾毫米、且既有 sono-ink 缺乏可程式化掃描的瓶頸，把 hydrophone 校準過的焦點接到 G-code 機台。產出的列印台直接供下游影像導引模組（GV）與活體實驗使用。
