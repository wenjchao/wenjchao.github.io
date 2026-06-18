# 原代 T 細胞分離、刺激與電穿孔 Knockin

1. 引用自哪篇 paper: pooled-knockin-cellular-immunotherapy
2. Outline (任務主線): 原代 T 細胞分離、刺激與電穿孔 Knockin
3. Method: 
   原代 T 細胞要從健康人類捐血者的血液裡分出來。作者先用 Lymphoprep 分層液配 SepMate 離心管，把血液離心成幾層後，挑出中間那層的「周邊血液有單一細胞核的白血球大群」(PBMC，peripheral blood mononuclear cells)——這層含 T 細胞、B 細胞、NK 細胞與單核球。接著用 EasySep Human T Cell Isolation Kit 做負選 (negative selection)：抗體混合物去黏住「不是 T 細胞」的那群細胞，磁柱再把這些被黏住的拉走，留下來「沒被抗體碰過」的就是純化 T 細胞。為什麼不直接正選 T 細胞？因為正選用的抗體會直接黏在 T 細胞的 CD3 或 TCR 上，等於把後續要刺激的開關先佔住了，反而會干擾下一步的活化；負選保留乾淨且不啟動的細胞。
   純化好的 T 細胞要先「叫醒」才能接受 knockin。作者把表面塗上 anti-CD3 與 anti-CD28 抗體的 Dynabeads (ThermoFisher Cat# 40203D) 以 1:1 比例跟 T 細胞混在一起，等於模擬抗原呈現細胞同時按下 TCR 與共刺激這兩個開關；再加上推細胞增殖與存活的三種細胞因子組合 (IL-2 500 U/mL、IL-7 5 ng/mL、IL-15 5 ng/mL)，培養 48–56 小時後 T 細胞大量進入分裂期。為什麼非要進入分裂期？因為細胞要做精準修補時必須拿「跟斷裂處長得一樣」的 DNA 當參考，預設用的是剛複製出來的姊妹染色單體——這只在 S/G2 期才存在。其他時候細胞會走預設修補法 NHEJ，直接把斷裂頭尾胡亂接回去（常常加減幾個鹼基造成 indel），根本不會拿模板來縫。如果跳過預刺激直接打靜止 T 細胞，Cas9 還是會切，但只會留下 indel，整合率塌到接近零，整個 screen 報廢。
   刺激好的 T 細胞拿來做電穿孔——用高電壓的短脈衝瞬間打開細胞膜上一堆小孔，外面的 RNP 與 HDR template 就隨著電場灌進細胞，幾秒鐘後小孔自己關回去。作者用 Lonza 4D 96 孔機台、特定脈衝代碼 EH115（沿用 Roth et al., 2018 在原代 T 細胞 HDR knockin 系統比過、效率與存活折衷最好的程式），每孔 P3 buffer 20 μL 含 75 萬至 100 萬細胞 + 3.5 μL RNP (50 pmol) + 1–3 μg HDR template；脈衝完立即加 80 μL 預溫培養基 (XVivo15 + IL-2 500 U/mL) 靜置 15 分鐘，後續每 2–3 天補新鮮 IL-2。為什麼模板量挑 1–3 μg？太少（0.1 μg 級）切斷的細胞旁邊找不到足夠模板可配對，整合率直接掉；太多（10 μg 級）大量游離 DNA 在細胞質會被當成病毒入侵，啟動 cGAS-STING 警報、釋放干擾素自我攻擊，細胞會死掉一大半，沒整合的模板也會干擾下游 PCR 定量。1–3 μg 是「夠模板做 HDR、又不到觸發警報」的窗口。和病毒感染最大的差別是：病毒會把 DNA 隨機塞進染色體某處、每顆細胞拿到份數還不一定，電穿孔搭配 Cas9 切刀則讓模板精準縫在 TRAC 一個位置上。
4. 工具與材料: 
   - **PBMC**: 周邊血液裡有單一細胞核的白血球大群 (peripheral blood mononuclear cells)，含 T/B/NK/單核球。
   - **Lymphoprep + SepMate**: 比重分層液與配套離心管，把血液離心分層後抽出中間 PBMC 層。
   - **negative selection**: 用抗體把非 T 細胞黏住、磁柱拉走，留下未被抗體接觸的乾淨 T 細胞。
   - **anti-CD3/CD28 Dynabeads**: 表面塗 anti-CD3 與 anti-CD28 抗體的微珠 (ThermoFisher Cat# 40203D)，模擬抗原呈現細胞同時按下 TCR 與共刺激開關。
   - **IL-2 / IL-7 / IL-15**: 推 T 細胞增殖與存活的三種細胞因子組合，本實驗劑量分別為 500 U/mL、5 ng/mL、5 ng/mL。
   - **NHEJ**: 非同源末端接合，細胞預設的「胡亂接回」修補法，常造成 indel；HDR 不活躍時會佔主導。
   - **HDR**: 同源重組修復，以姊妹染色單體或外來模板為參考精準縫補斷裂，僅在 S/G2 期活躍。
   - **Lonza 4D + EH115**: Lonza 4D 96 孔電穿孔機台與沿用 Roth et al., 2018 最佳化的脈衝代碼。
   - **P3 buffer**: Lonza 配套的電穿孔緩衝液，內含 RNP 與 HDR template。
   - **cGAS-STING**: 細胞質游離 DNA 感應器，模板過量會誤觸警報引發干擾素反應殺死細胞。
5. 與此篇文章的關係: 
   在《Pooled Knockin Targeting for Genome Engineering of Cellular Immunotherapies》這篇文章中，作者為了非病毒地把 36 種 HDR template 縫進原代 T 細胞的 TRAC 位點，採用了 PBMC 分離 + CD3/CD28 預刺激 + Lonza EH115 共電穿孔的流程。它解決了 T 細胞在 G0 沉睡狀態下 HDR 不活躍、模板根本縫不進去的瓶頸。產出的活化、剛被電穿孔的 T 細胞會作為下游 pooled screen 與 in vivo 注射的原料。
