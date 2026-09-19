# 離體強散射組織與活體小鼠光譜偵測

1. 引用自哪篇 paper: wideband-indium-phosphide-nanolasers
2. Outline (任務主線): 離體強散射組織與活體小鼠光譜偵測
3. Method:

   作者用一路加碼的散射強度做離體驗證。最基礎的散射模擬是 3M Magic Tape:每片 80 μm 厚、散射體均勻,反覆貼疊到 17 層(1.36 mm)構成一個「可控加厚的濃霧」;量到 speckle(散斑)尺寸 ∝ √厚度、閾值泵浦能量 ∝ 厚度²,兩條關係都吻合光子擴散區 (photon diffuse regime) 的理論。接著改用水浸雞胸肉切成 1–2 mm 與 1 cm 兩種厚度貼在粒子上面,泵浦從組織頂端往下打、雷射從頂端往上收:1–2 mm 樣品理所當然收得到,1 cm 樣品(相當於小鼠側身深組織厚度)平均閾值泵浦 <10 mW 仍能收到高 SNR 的窄帶雷射峰。為了呈現「NIR-I InP 打敗 NIR-II InGaAsP」不是選擇性報導,作者專程搭一台完整的 NIR-II 對照:主機是 Olympus FV3000 雷射掃描共焦顯微鏡,泵浦源改成 1064 nm 3 ns/2 MHz 的 Spectra Physics VGEN-ISP-POD,光譜儀端接 NIR-II 專用機(Sensor Unlimited 2048 InGaAs linescan camera,≈370 photoelectrons/count),物鏡選 NIR 優化的 Olympus IMS LCPLN20XIR (20×, 0.45 NA)。同一片雞胸肉輪流量兩套系統,結果 NIR-II 只穿得過 1–2 mm、進不了 1 cm,主因是 InGaAs 相機暗雜訊比矽 EM-CCD 大 1–2 個數量級。

   動物端用 10 週齡、20–25 g 的 BALB/c 母鼠(Jackson Laboratory),腹腔注射 ketamine(氯胺酮,解離型麻醉)+ xylazine(甲苯噻嗪,強止痛/肌肉鬆弛)混合劑麻醉。作者驗了三個注射位點。第一個是乳腺脂肪墊 (mammary fat pad):把 LP-tagged GFP-4T1 注入乳頭旁約 2 mm 位置、深度 ≈ 3 mm,模擬乳癌原位微環境,實測 137 顆 tagged cells 的光譜條碼在活體都可被 recover。第二個是尾靜脈:用 cannula(細長注射管)慢慢送入 PBS 稀釋成 2 000–5 000 顆/50 μL 的細胞懸液,細胞隨血流以 2–4 mm/s 通過視野,每顆停留 ≈0.2 秒。第三個是耳血管:血流慢到 0.32–0.4 mm/s、每顆細胞停留 ≈2 秒,適合長時間追同一顆細胞。因為 LP 只給光譜條碼、看不見解剖位置,作者另外用兩個獨立成像技術做空間錨點:光學同調斷層掃描 (OCT,1310 nm 掃頻雷射客製系統) 量出尾部血管直徑 200 μm、皮下 800 μm 深;兩光子顯微鏡 (Olympus FV4000MPE) 靜脈注射 rhodamine-dextran(2 百萬 MW,不易漏出血管壁的螢光染料)描出耳血管的樹狀圖。所有動物協定經 Mass General Brigham IACUC 核可(#2017N000021)。

   整套「1 cm 雞胸肉仍能收到訊號」的物理根源在兩個機制。第一是窄帶對抗寬頻:組織打進去的泵浦光會激發膠原、色素等寬頻自發螢光,譜寬約 60 nm;InP 雷射線寬 <1 nm,只要把偵測頻寬縮到 0.3 nm 剛好包住整條雷射線,自螢光背景就被砍成 0.3/60 = 1/200——訊號沒動、背景減 200 倍,SNR 提升 200 倍,對數表達為 10·log₁₀(200) ≈ 23 dB。這個機制不依賴組織透明度,而是靠光譜對比。第二是光子擴散:泵浦光進組織後每走一段就被散射一次、方向亂掉,平均要走的路徑遠長於直線距離,進入光子擴散區 (photon diffuse regime);此區泵浦通量密度以 $1/L^2$ 衰減,因此「閾值泵浦能量 ∝ 厚度²」,同時「speckle 尺寸 ∝ √厚度」,兩個標誌都對上作者從 1 到 17 層膠帶的實驗數據。

   為什麼要重搭一整台 NIR-II 系統做對照、而不是引用文獻數字?因為別組用的組織、切片厚度、泵浦能量、暗計數校正都不一樣,直接對照沒說服力;作者的做法是「同一片雞胸肉、同一片鼠殼」兩套系統輪流量,只留下「材料 + 偵測器」是變數,才能可信地宣稱 NIR-I 路線勝出。三個注射位點也分工明確:乳腺脂肪墊測靜態原位標記,尾靜脈測 2–4 mm/s 快流下的 0.2 秒抓取,耳血管測 0.32–0.4 mm/s 慢流下同一顆細胞持續 ≈2 秒的追蹤。兩個容易踩雷的操作環節:一是麻醉,ketamine + xylazine 劑量不到位,鏡下老鼠呼吸太急、視野每 0.5 秒就震一次,單顆細胞 0.2 秒的雷射峰根本抓不到;二是尾靜脈注射太快,細胞懸液會撐破血管壁、外漏到皮下,量到的訊號不再與血流相關,流速估算失去意義。另外若省掉 OCT 與兩光子成像,一顆訊號到底在靜脈或動脈、離皮多深都無從得知,「200 μm 血管直徑」「2–4 mm/s 流速」全部無法錨定。

4. 工具與材料:
   - **3M Magic Tape 散射模擬**: 每層 80 μm 厚的均勻散射膠帶,疊到 17 層(1.36 mm),量 speckle 尺寸 ∝ √厚度、閾值 ∝ 厚度²,檢驗系統落在光子擴散區。
   - **水浸雞胸肉 1 cm**: 模擬小鼠側身深組織的散射樣品;閾值泵浦 <10 mW 即可收到 InP 窄帶雷射峰,NIR-II 對照則抓不到。
   - **NIR-II 對照系統**: Olympus FV3000 共焦顯微鏡 + 1064 nm 3 ns/2 MHz Spectra Physics 泵浦 + Sensor Unlimited 2048 InGaAs linescan 相機 + Olympus IMS LCPLN20XIR (20×, 0.45 NA);作為 InP + 矽 EM-CCD 的公平對照。
   - **光子擴散區 (photon diffuse regime)**: 泵浦光多次散射後方向亂掉、通量密度 ∝ 1/L² 衰減;speckle 尺寸 ∝ √L、閾值 ∝ L² 是兩個實驗簽名。
   - **0.3 nm 偵測頻寬 SNR 提升**: 把偵測窗口從 60 nm 自螢光收縮到 0.3 nm 恰好包住雷射峰,背景砍 1/200 倍、SNR 提升 200 倍 (≈23 dB)。
   - **BALB/c 母鼠**: 10 週齡、20–25 g,Jackson Laboratory 採購,腹腔注射 ketamine + xylazine 混合劑麻醉。
   - **乳腺脂肪墊注射**: 把 LP-tagged GFP-4T1 注入乳頭旁約 2 mm、深度 ≈ 3 mm,模擬乳癌原位微環境;實驗中量到 137 顆 tagged cells 光譜條碼可 recover。
   - **尾靜脈 cannula 注射**: PBS 稀釋 2 000–5 000 顆/50 μL 慢注,細胞隨血流 2–4 mm/s 通過視野,每顆停留 ≈0.2 秒。
   - **耳血管慢流追蹤**: 血流 0.32–0.4 mm/s、每顆細胞停留 ≈2 秒,適合長時間追同一顆細胞。
   - **OCT (1310 nm 掃頻雷射)**: 客製 OCT 系統定位血管深度與直徑,尾部血管 200 μm 直徑、皮下 ≈800 μm 深。
   - **兩光子顯微鏡 + rhodamine-dextran**: Olympus FV4000MPE 兩光子鏡,靜脈注射 2 百萬 MW 的 rhodamine-dextran 螢光染料,描出耳血管樹狀圖。
   - **IACUC 動物協定 #2017N000021**: Mass General Brigham 動物照護與使用委員會核可的協定編號,規範所有 in vivo 實驗。

5. 與此篇文章的關係:

   在《Wideband Tuning and Deep-Tissue Spectral Detection of Indium Phosphide Nano-Laser Particles》這篇文章中,作者為了驗證 InP LP + 矽 EM-CCD 系統能在真正的散射組織裡辨識單顆細胞,採用「膠帶 → 雞胸肉 → 活鼠皮下/血管/顱骨」的階梯式離體 + 活體驗證。它解決了「NIR-II LP + InGaAs 相機在 1 cm 深組織抓不到訊號」的瓶頸——同一片雞胸肉輪流量兩套系統做公平對照,並用 OCT + 兩光子把 LP 光譜錨到解剖結構。這一步吃前面的 100 nm 厚殼 LP-tagged GFP-4T1 細胞,產出活體流速、原位定位與跨組織 SNR 數據,直接支持深組織 barcoding 的應用宣稱。
