# 低溫敏感脂質體（LTSL）合成與交聯劑包封

1. 引用自哪篇 paper: deep-tissue-sound-printing
2. Outline (任務主線): 低溫敏感脂質體（LTSL）合成與交聯劑包封
3. Method: 
   DISP 的核心元件是低溫敏感脂質體 (low-temperature–sensitive liposome, LTSL)——一顆奈米大小的「油泡」，外面是兩層磷脂膜、裡面包水溶性交聯劑。要讓它在 ~41.7 °C 才開門，作者把膜配方鎖在 DPPC : MSPC : DSPE-PEG-2000 = 86 : 4 : 10 (mol%)，三個成分各管一件事：DPPC 是主結構脂，相變溫度 (Tm) 剛好落在 ~41.5 °C，是「體溫穩定、稍熱才開」的關鍵物理常數；MSPC 是 lysolipid（只有一條尾巴的磷脂），加熱相變後會被擠到膜的邊界把膜撐出奈米孔，是真正的「破孔劑」；DSPE-PEG-2000 末端接了 PEG 長鏈，像絨毛把膜面撐開，讓油泡不會彼此黏成團、進到體內也不易被免疫細胞快速吞掉。三者組起來，FUS 加熱到 ~41.7 °C 時 DPPC 從固態翻成流動態、MSPC 在邊界鑽孔、內容物在 30 秒內漏出來。
   
   LTSL 製備走的是「乾膜水化法 (dry lipid film hydration)」，可分四步。第一步把三種脂質按比例溶在 chloroform，用 rotary evaporator 邊轉邊揮乾，在燒瓶內壁留下一層薄薄的脂質膜。第二步把 500 mM CaCl₂ 水溶液倒進去、55 °C 攪拌 1 小時，脂質膜自動捲成多層脂質體 (multilamellar liposome)、把 Ca²⁺ 包進每一層之間。第三步用 extruder 在 55 °C 下把多層油泡反覆擠過孔徑固定的 polycarbonate 膜 ≥ 10 次，強迫油泡變成只剩一層膜、大小一致的單層脂質體 (unilamellar)——多層油泡像洋蔥，外層被加熱開孔了內層還封閉，釋放會不齊；單層、同大小才能在 ~42 °C 同步開門。擠出之所以選 55 °C，是因為這溫度已高於 DPPC Tm，膜處於流動態、擠過去會柔順重組、不會破裂；室溫操作會堵膜或讓油泡爆掉。第四步用 22,700 g × 90 min 高速離心三次，把溶液中沒進到油泡裡的游離 CaCl₂ 沖掉。
   
   要怎麼確認 Ca²⁺ 真的被關在油泡裡？作者用兩道交叉檢查。一是把離心上清液拿去量 UV-vis 吸光：如果還有游離 Ca²⁺ 會出現對應吸收峰，結果上清乾乾淨淨。二是用 Fura-2 AM——一種會跟 Ca²⁺ 結合後發螢光的指示劑——配上 two-photon 顯微鏡，直接看到一顆顆 LTSL 內部亮起來。再加上動態光散射 (DLS) 確認擠出後粒徑分佈又小又集中，以及量到表面電位 (zeta potential) = −17.31 mV，表示油泡之間互斥、不會聚成團，這是臨床注射前必要的穩定性指標。
   
   為什麼水化液要 500 mM 這麼濃？這是 payload 考量。每顆 LTSL 內部體積很小，要在後續釋放時達到「能讓 alginate 真的結成膠」的劑量，內部濃度必須拉得很高——作者測到每顆油泡裡 Ca²⁺ 約 240 mg dl⁻¹，這樣 50 wt% LTSL 加進 alginate 後、FUS 一打、瞬間釋出量才會達到 ionic crosslink 閾值。同一套 lipid 膜配方也適用其他兩種化學：把 hydration 液換成 47 mM NaIO₄ 就成 NaIO₄-LTSL（給 GelCA 用的氧化交聯劑），換成 50% v/v TEMED 就成 TEMED-LTSL（給 PEGDA 用的自由基聚合催化劑）。膜的設計只做一次、要換交聯機制只要換內容物，這也是為什麼 DISP 能同時涵蓋離子、自由基、氧化三種完全不同的交聯反應。
   
   整套設計有兩個失敗模式特別致命。一是 MSPC 比例：放太少（< 2%）FUS 加熱到 ~43 °C 也開不出足夠的孔，30 秒釋放率達不到 ~77%、墨水到體內按下按鈕也膠不起來；放太多（> 8%）膜在 37 °C 體溫下就有過多邊界缺陷，油泡在針筒裡就漏光 Ca²⁺、整管預先膠住堵針。作者鎖在 4 mol% 是這條相變斷崖的最佳折衷。二是高速離心三次純化：如果沒把溶液中游離 CaCl₂ 沖乾淨，這些離子會立刻和 alginate 反應、在針筒裡先把墨水膠住，連注射都做不到；就算僥倖打進體內，沿路擴散的游離 Ca²⁺ 也會在不該交聯的地方亂膠並刺激組織。每次離心後抽掉上清、再重新分散，直到 UV-vis 量上清液看不到 Ca²⁺ 為止。
4. 工具與材料: 
   - **DPPC**：主結構脂，相變溫度 (Tm) ~41.5 °C，是 LTSL 體溫穩定、~42 °C 才開門的關鍵物理常數。
   - **MSPC (lysolipid)**：單條尾巴磷脂，相變後在膜邊界堆積把膜撐出奈米孔的「破孔劑」；放 4 mol%。
   - **DSPE-PEG-2000**：末端接 PEG 的脂質，PEG 像絨毛把膜面撐開，避免油泡聚集、延長體內循環時間；放 10 mol%。
   - **乾膜水化法 (dry lipid film hydration)**：先把脂質溶於 chloroform、揮乾留薄膜，再加水溶液水化捲成多層脂質體的標準 LTSL 製備流程 (Needham et al., 2013; Ta & Porter, 2013)。
   - **Extrusion (擠出均一化)**：用 extruder 在 55 °C 把多層油泡反覆擠過 polycarbonate 膜 ≥ 10 次，得到單層、大小一致的 LTSL。
   - **Multilamellar → unilamellar**：多層脂質體像洋蔥、釋放會不齊；擠出後變單層、同尺寸才能在 ~42 °C 同步開門。
   - **高速離心 (22,700 g × 90 min × 3 次)**：把沒進到油泡裡的游離 CaCl₂ 沖掉，避免在針筒內預先膠化或損傷組織。
   - **動態光散射 (DLS)**：Malvern Nano ZS Zetasizer 量 LTSL 粒徑分佈，確認擠出後又小又集中。
   - **Fura-2 AM**：與 Ca²⁺ 結合後發螢光的指示劑，配 two-photon 顯微鏡證明 Ca²⁺ 真的在 LTSL 內部。
   - **表面電位 (zeta potential)**：Ca²⁺-LTSL 量到 −17.31 mV，表示油泡之間互斥、膠體穩定。
   - **500 mM CaCl₂ hydration / 240 mg dl⁻¹ payload**：高濃度 hydration 液確保每顆 LTSL 內 Ca²⁺ 劑量足夠，後續釋放才能達到 ionic crosslink 閾值。
   - **NaIO₄-LTSL / TEMED-LTSL**：同樣 lipid 配方但 hydration 液換成 47 mM NaIO₄ 或 50% v/v TEMED，分別用於 GelCA 氧化交聯與 PEGDA 自由基聚合。
5. 與此篇文章的關係: 
   在《Imaging-guided deep tissue in vivo sound printing》這篇文章中，作者要解決「離子交聯型 hydrogel 一旦預混就膠化、無法注射，游離交聯劑接觸組織又有毒」的核心瓶頸。為此他們做出 LTSL——一種 37 °C 完全密封、~41.7 °C 才在膜上開奈米孔的脂質奈米載體，把 Ca²⁺、NaIO₄、TEMED 等交聯劑事先鎖起來；下游 US-ink 配方化、FUS 列印、影像引導全部仰賴這顆「按下按鈕才開門」的油泡作為化學觸發基石。
