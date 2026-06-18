# In Vitro 選擇壓力與功能驗證

1. 引用自哪篇 paper: pooled-knockin-cellular-immunotherapy
2. Outline (任務主線): In Vitro 選擇壓力與功能驗證
3. Method: 
   作者把混合細胞放進五種模擬「不同腫瘤微環境」的條件做 pooled screen。第一是標準刺激（anti-CD3/CD28 Dynabeads 1:1）：細胞同時拿到 TCR 訊號跟共刺激訊號，模擬正常活化。第二是過度刺激（cell:bead 1:5）：訊號太強、模擬細胞容易耗竭或自殺的高壓力情境。第三是只給 TCR 訊號、不給共刺激的孤立刺激——作者用 NY-ESO-1 dextramer (Immudex Cat# WB3247-PE) 1:50 稀釋染 12 分鐘室溫。dextramer 是把「NY-ESO-1 抗原片段加上能呈現它的 MHC 分子」掛在一條長糖骨架上做成的螢光多聚體，像「一根只插滿目標的棍子」，T 細胞的 NY-ESO-1 TCR 一抓住就被啟動（signal 1），但棍子上沒有 CD80/CD86 這些共刺激分子（signal 2）。第四是加入 25 ng/mL 人類 TGF-β1，模擬腫瘤分泌抑制訊號。第五是完全不刺激，看哪種構築能讓細胞自己活下來。為什麼非要五種並列？因為每個改造策略對應的優勢都不一樣：dominant negative Fas 只在「過度刺激容易引發自殺」的條件下才有優勢，TGF-βR2 系列只在「加 TGF-β」的條件下才勝出，IL2RA 過表現只在「無刺激」條件下才搶得到 IL-2 鼓勵訊號。多條件並列才能讓每個構築在自己的擅長場合被看見。
   勝出構築進入 arrayed 驗證後，作者用兩種功能讀數比對它們的真實戰力。第一是 in vitro killing assay：把 T 細胞跟 A375-nRFP（會被 NY-ESO-1 TCR 認出的黑色素瘤，細胞核被改造成發紅光，引用 Zaretsky et al., 2016）以不同兵敵比例 (E:T) 共培養，放進 IncuCyte ZOOM 延時顯微鏡，每隔一段時間自動拍一張，數畫面上的紅點（活著的癌細胞核）有多少；T 細胞殺得愈兇，紅點下降愈快，這個下降曲線就是殺癌速度的量化指標，跑 4–5 天，培養基是 cRPMI + 50 U/mL IL-2 + 葡萄糖。第二是 cytokine release assay：T 細胞被刺激後會把 IFN-γ、IL-2、TNF-α 從細胞裡分泌出去，直接染胞外會看不到，因為它們跑光了。作者先加 Brefeldin A 擋住細胞內貨物運送的高基氏體 (Golgi)，讓本來要分泌的 cytokine 卡在胞內 4 小時，再用 FIX & PERM Kit 把細胞固定 + 戳洞，讓帶螢光的抗體鑽進細胞跟卡住的 cytokine 結合，最後用流式細胞儀讀 IFN-γ-PE、IL-2-APC、TNF-α-PacBlue 的強度——強度高代表這顆細胞分泌很多。沒加 Brefeldin A 的話訊號會被壓平，分不出強弱。另外用 CFSE 染色追蹤分裂代數，量化每個構築讓 T 細胞繁殖的能力。
   為什麼 pooled screen 後還要重做 arrayed knockin？因為 pooled 結果有三層噪音：殘餘的 template switching 約 10%（條碼對應到別人的功能基因）、biallelic integration 約 25%（一顆細胞兩條染色體都被縫入）、加上細胞之間互相影響（強構築旁邊有弱構築，弱的也被拉著繁殖）。直接相信 pooled 命中、跳到 in vivo 動物實驗，可能花了很多老鼠才發現命中是假陽性。Arrayed knockin 把每個構築拉出來「一個構築一管細胞」單獨測 killing、proliferation、cytokine——沒有 switching、沒有競爭，重測勝出才確認這個構築單獨拿出來也真的有效。這道驗證是 pooled screen 到 in vivo 之間不可少的過濾器。
4. 工具與材料: 
   - **selection pressure**: 讓某些構築被選擇性富集或耗竭的條件，本研究設五種模擬腫瘤微環境的情境。
   - **CD3/CD28 Dynabeads (1:1 vs 5:1)**: 標準刺激 vs 過度刺激的細胞:珠比例，模擬正常活化或耗竭/AICD 壓力。
   - **NY-ESO-1 dextramer**: 把 NY-ESO-1 抗原片段加 MHC 掛在長糖骨架上的螢光多聚體 (Immudex Cat# WB3247-PE)，提供 signal 1 但無 signal 2。
   - **TGF-β1 (25 ng/mL)**: 人類 TGF-β1 蛋白 (Miltenyi)，加入培養模擬腫瘤分泌的抑制訊號。
   - **A375-nRFP**: 穩定表達 NY-ESO-1、細胞核改造成發紅光的人類黑色素瘤 (ATCC CRL-1619；引用 Zaretsky et al., 2016)。
   - **IncuCyte ZOOM**: Essen 出品的延時顯微鏡，自動拍 RFP+ 核數隨時間下降以量化 T 細胞殺癌速度。
   - **Brefeldin A**: 阻斷 Golgi 運輸的藥物，讓 cytokine 卡在胞內以供細胞內染色。
   - **FIX & PERM Kit**: ThermoFisher 出品的細胞固定 + 戳洞試劑，讓螢光抗體進入細胞染色 IFN-γ / IL-2 / TNF-α。
   - **CFSE**: 進入細胞後均勻分配給子代的螢光染料，每分裂一次螢光減半，可追蹤分裂代數。
   - **arrayed knockin**: 一個構築一管細胞、不池化，單獨重測 killing/proliferation/cytokine，排除 pooled 噪音造成的假陽性。
5. 與此篇文章的關係: 
   在《Pooled Knockin Targeting for Genome Engineering of Cellular Immunotherapies》這篇文章中，作者為了在動物實驗前找出真正有效的抗腫瘤改造，採用了五種選擇壓力 + arrayed knockin 雙層驗證。它解決了 pooled screen 命中可能來自 template switching、biallelic integration 或細胞競爭噪音的瓶頸。產出的勝出且 arrayed 驗證有效的構築（如 TGF-βR2-41BB）會作為下游 in vivo 異種移植實驗的精選候選。
