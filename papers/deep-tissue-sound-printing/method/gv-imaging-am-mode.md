# GV 影像演算法與 AM-mode 即時膠化驗證

1. 引用自哪篇 paper: deep-tissue-sound-printing
2. Outline (任務主線): GV 影像演算法與 AM-mode 即時膠化驗證
3. Method: 
   作者把列印過程從「盲打」變成「即時看到」，靠兩種互補的對比訊號。「中空氣囊的奈米對比劑」(gas vesicle, GV) 是細菌用來上浮的奈米級空心管，外殼是蛋白、裡面是氣體；氣體與水的密度差很大，超音波經過時會被 GV 非線性散射，在影像上形成亮點。當聚焦超音波焦點壓力夠高時，GV 蛋白外殼被壓塌、氣體溶進水裡，亮點消失——這就是「打到焦點了」的視覺訊號。「對 Ca²⁺ 敏感的工程化 GV」(GV-Ca²⁺ sensor) 則是把 GV 外殼上的 GvpC 蛋白工程化成「沒 Ca²⁺ 時包得很緊不太散射、抓到 Ca²⁺ 後構象變鬆、散射變強」。所以當 LTSL 在焦點釋放出 Ca²⁺ 後，Ca²⁺ 擴散到的地方 GV-Ca²⁺ sensor 就被「點亮」，把交聯邊界直接畫出來（fig. S36 的橫切剖面可從亮度分布量出印製線寬）。
   
   GV 的訊號很弱，要讓它在組織背景中被看清，作者用「cross-propagating amplitude modulation」(xAM, Maresca et al. 2018) 演算法。基本想法是：先打一發「全振幅」、再打兩發「半振幅」，把兩發半振幅影像加起來與全振幅相減。線性反射（組織、骨頭）「半 + 半 = 全」會被相減歸零；非線性反射（GV）兩個半振幅加起來會比全振幅小，相減後留下殘差。xAM 進一步用兩束從不同方向交叉的脈衝做這個振幅調變，更乾淨地抑制側向漏光。最後線性背景幾乎被消光，只剩 GV 的非線性訊號，對比度大幅提升。
   
   影像端用「多執行緒可程式 ultrasound 平台」(Verasonics Vantage)，可以由使用者自己寫超音波發射序列（含 xAM 三脈衝），配上「線性陣列探頭」(L22-14vX linear array) 中心頻率 15.625 MHz。掃描時用 64 條 ray line（聲波在組織中走的方向）覆蓋影像範圍，每條 ray line 把同一畫面 accumulate 50 次（重複擷取、平均掉隨機雜訊），把訊噪推到能看見墨水裡稀疏 GV 的程度，最後每個像素橫向 50 μm、軸向 1 μm。這個解析度剛好可以看清楚 ~150 μm 寬的列印線條。
   
   為什麼要同時用「GV 崩解 → 對比消失」與「GV-Ca²⁺ sensor → 對比出現」兩種訊號？兩者各回答不同問題：前者告訴你「FUS 真的打到目標位置了」（能量靶向確認）；後者告訴你「LTSL 真的把 Ca²⁺ 放出來、交聯化學發生了」（化學反應確認）。只用前者，ink 若包封失敗、Ca²⁺ 沒放出來，膠體還是不會形成；只用後者，沒辦法即時知道 FUS 是否準確對準。兩者一起構成完整的「列印成功」判據。相比之下，MRI 引導 HIFU（ref 37, 38）只能量焦點溫度——看不到實際膠體形狀，也看不到 Ca²⁺ 擴散邊界；GV 則是可放進 ink 本身的奈米對比劑，用一般的 ultrasound 探頭就能成像、不必另外植入 MRI 線圈，讓即時看見列印的方案更便宜、更便攜。
   
   如果只用普通 B-mode 看 GV 而不做 xAM，畫面會被組織與骨頭的線性反射訊號佔滿，GV 的非線性散射只是一小撮亮點被埋在背景裡。你看到一片亮，分不清是組織還是 GV，也看不出 FUS 一打過去之後「GV 那點亮度有沒有降低」。xAM 把線性背景幾乎全部抵消，剩下的影像主要來自 GV——FUS 一打、GV 崩解，畫面上對應位置會明顯變暗一塊；GV-Ca²⁺ sensor 在 Ca²⁺ 擴散到的地方變亮，也才有對比度可看。沒做 xAM，這套即時影像引導就退化成「打了也不知道有沒有打到」。
4. 工具與材料: 
   - **Gas vesicle (GV)**：中空氣囊的奈米對比劑，外殼蛋白、內部氣體，非線性散射超音波形成亮點；高聲壓下塌陷導致對比消失。
   - **GV-Ca²⁺ sensor**：把 GvpC 蛋白工程化成『有 Ca²⁺ 才散射』的 GV，Ca²⁺ 擴散到的位置 AM signal 才會亮，直接畫出膠體邊界（Jin et al. 2023）。
   - **Cross-propagating amplitude modulation (xAM)**：用兩束交叉脈衝做 amplitude modulation，把線性背景幾乎消光、留下 GV 非線性殘差（Maresca et al. 2018）。
   - **Verasonics Vantage**：多執行緒可程式 ultrasound 研究平台，使用者可自寫 xAM 序列。
   - **L22-14vX linear array**：中心頻率 15.625 MHz 的線性陣列探頭，提供 lateral 50 μm × axial 1 μm 解析度。
   - **Ray line / accumulate**：Ray line 是聲波在組織中走的方向；accumulate 50 次是重複擷取同畫面以平均掉隨機雜訊。
   - **B-mode imaging**：從超音波回波重建灰階解剖影像，用於確認 catheter 是否進入膀胱、墨水是否到達病灶。
5. 與此篇文章的關係: 
   在《Imaging-guided deep tissue in vivo sound printing》這篇文章中，作者為了讓深層列印不再是「打了也不知道是否成功」，採用了 GV 與 GV-Ca²⁺ sensor 兩種 acoustic biomolecule 對比劑搭配 xAM 演算法。它解決了「MRI 引導 HIFU 只看得到溫度、看不到膠體形狀」的瓶頸：把對比劑直接放進 US-ink，用一般 ultrasound 探頭即時呈現「FUS 是否打中」與「Ca²⁺ 擴散到哪裡」，直接為下游 in vivo 膀胱腫瘤列印提供影像引導與成功判據。
