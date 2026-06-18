# 人類角膜 MSC 分離、擴增與細胞列印

1. 引用自哪篇 paper: collagen-microgel-bioprinting
2. Outline (任務主線): 人類角膜 MSC 分離、擴增與細胞列印
3. Method: 
作者要找的細胞必須兼顧『生理相關性』與『可量產』。角膜 MSC——從人類捐贈者角膜的中間膠原蛋白基質層分離出來的幹細胞 (mesenchymal stromal cell, MSC)——剛好兩者都有：它能在培養皿裡持續分裂擴增，本身又是角膜原生細胞，植回去引起免疫排斥的風險低。分離流程沿用 Du et al. Stem Cells 2005 與 Eslani et al. Stem Cells 2018 的既有 protocol，角膜由 Lions Eye Institute for Transplant and Research 提供。細胞在『MEM-Alpha + 10% FBS + GlutaMax + 非必需胺基酸 + Antibiotic-Antimycotic』的幹細胞培養基中擴增、每隔一天換液、長到 80% 滙合就用胰蛋白酶剝下繼代 (passage)；只使用第 5–10 代——太早數量不夠、太晚會開始老化漂移。列印前再以胰蛋白酶消化、計數、離心成顆粒，重懸到 6 mg/mL 的 collagen-azide 或未修飾 collagen 墨水裡，密度做到每毫升 3 × 10⁶ 顆細胞。

為什麼挑 3 × 10⁶ cells/mL 而不是更低或更高？細胞收縮膠原蛋白靠的是『很多顆同時拉』，密度太低（10⁵ 等級）幾乎看不到圓盤縮小，PHYS vs. SPAAC 的差異就被雜訊蓋過；密度拉太高（10⁷ 等級）細胞在膠裡互搶氧氣，列印 7 天後先餓死一批，量到的變成『缺氧死亡』而非材料對形態的影響。3 × 10⁶ 是常用的折衷密度，能看到明顯收縮（PHYS 7 天縮到原直徑 25%）同時維持 95% 以上存活率。

光做列印組還不夠：作者另外設計『直接倒進模子裡讓它凝固』的澆鑄對照 (cast control)——把同密度細胞混在 SPAAC（6 mg/mL collagen-azide + 5 mg/mL PEG-BCN）或 PHYS（6 mg/mL unmodified collagen）裡，注入直徑 4 mm、厚 0.5 mm 的矽膠小模，每樣品 10 μL，37 °C 1 小時交聯。這組沒經過擠出、沒有支撐浴介入，是『純材料對細胞行為的影響』參考點。有了它才能明確區分：細胞縮成球到底是『SPAAC 化學鎖死本身就禁止伸展』還是『沒有孔洞才禁止伸展』——cast SPAAC 也縮成球的事實，把鋪展差異的鍋釘在『有沒有孔洞』上。

細胞要不要驗存活與形態，作者用兩支染料分工：列印後 5 小時內先用 Live/Dead 雙染量存活率——Calcein AM 進入活細胞後被酯酶剪成綠色螢光（活細胞發綠光），Ethidium homodimer-1 則是帶電大分子，只有膜破洞的死細胞它才鑽得進去並結合 DNA 發紅光，兩色比例就是存活率；之所以限定 5 小時內判讀，是因為染料本身有微弱毒性、放太久反而會殺死健康細胞。要追形態就改用 CellTracker Green CMFDA——進細胞後被麩胱甘肽 (GSH) 以共價鍵『焊』在細胞自己的蛋白上，即使細胞分裂、伸長、移動，染料也黏得牢牢的。作者在裝進墨水前就先把細胞染好，整個 7 天的細胞 2D 形狀與圓度量測都是看這條綠光。確認兩種交聯機制下都 > 95% 存活，才能放心宣稱後續看到的形態差異是材料設計造成、不是創傷反應。
4. 工具與材料: 
   - **Corneal MSC**: 從人類捐贈者角膜基質層分離出的間質幹細胞，能擴增、植回去免疫排斥風險低，是角膜組織工程的種子細胞。
   - **MEM-Alpha 培養基**: Corning MEM-Alpha + 10% FBS + GlutaMax + 非必需胺基酸 + Antibiotic-Antimycotic，corneal MSC 的標準擴增培養基。
   - **Passage (繼代)**: 細胞長到 80% 滙合用胰蛋白酶剝下分到新皿；只使用第 5–10 代以避免老化。
   - **Cell density 3 × 10⁶ cells/mL**: 兼顧『收縮訊號夠強』與『細胞不缺氧』的常用組織工程列印密度。
   - **Live/Dead 雙染**: Calcein AM（活細胞酯酶發綠光）+ Ethidium homodimer-1（死細胞膜破洞才能進、結合 DNA 發紅光）；用於列印後 5 小時內量存活率。
   - **CellTracker Green CMFDA**: 靠麩胱甘肽 (GSH) 共價標記細胞內蛋白的綠色螢光染料，可穩定追蹤細胞形態數天，用於 7 天形態與圓度量測。
   - **Cast control**: 把細胞墨水直接注入矽膠模（4 mm × 0.5 mm，10 μL，37 °C 1 h 交聯）做凝固，作為『無列印、無支撐浴』的純材料對照組。
5. 與此篇文章的關係: 
   在《Embedded 3D Bioprinting of Collagen Inks into Microgel Baths to Control Hydrogel Microstructure and Cell Spreading》這篇文章中，作者瞄準的長期目標是 3D 列印人工角膜。本步驟提供與最終臨床場景對得上號的細胞——人類角膜 MSC，並以 Live/Dead 雙染、矽膠模澆鑄對照等方式驗證 > 95% 存活率。它的上游是 6 mg/mL 膠原墨水的合成、下游則是 SPAAC vs. PHYS 的孔洞鋪展與收縮量測，確保後續看到的形態差異是材料設計而非細胞創傷造成。
