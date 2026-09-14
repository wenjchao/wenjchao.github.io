# 週邊血淋巴球型態與功能性再刺激

1. 引用自哪篇 paper: antitumor-lymphocyte-clonal-repopulation
2. Outline (任務主線): 週邊血淋巴球型態與功能性再刺激
3. Method:
      作者用最直觀的一招證明活體內爆量的淋巴球「正在活化」：「血液抹片 (blood smear)」——把一滴病人的血滴在載玻片上、拉薄成一層、染上 Wright-Giemsa 染劑，直接放顯微鏡下看細胞外形。病人 9 (day 9) 和病人 10 (day 8) 的抹片顯示這些淋巴球有五個一起出現的特徵：「深染的細胞核 (hyperchromatic nuclei)」代表染色質正在被大量開讀當中——細胞忙著製造蛋白；「高核質比 (N/C ratio)」是細胞核大到把細胞質擠掉、分裂旺盛的淋巴母細胞招牌；「毒性顆粒 (toxic granulation)」是細胞質裡出現藍色顆粒，代表正在裝載毒殺武器 (granzyme, perforin)；「Dohle bodies」是細胞質裡的藍色小塊 RNA 富集區，也是活化訊號；合起來構成典型的「活化型 blastic morphology」。跟 FACS 只給比例不同，抹片直接讓病理科醫師眼見為憑。
   但形態學只能告訴你「這些細胞正在活化」，不能告訴你「活化的靶是不是腫瘤」，所以作者接著做「過夜再刺激 (overnight reactivation) 」的功能性測試。實作是：從病人 9 (day 9) 或病人 10 (day 8) 抽出血液淋巴球，浸在 600 IU/ml IL-2 的培養液裡過夜（相當於「重新充電」——REP 用的 6000 IU/ml 是強推分裂的擴增濃度，這裡只用維持型 600 IU/ml，剛好把細胞從壓抑狀態拉回可反應狀態而不觸發二次分化）。過夜後徹底洗掉 IL-2，才拿去接觸 MART-1 peptide 或 HLA-A2+ 腫瘤細胞，量分泌了多少 cytokine；同組還有一個沒過夜浸泡 IL-2 的對照（Fig 2C 的 striped vs solid boxes）。這麼做能同時檢驗兩件事：其一，細胞有沒有能力再度反應；其二，反應是否嚴格對得上 MART-1／HLA-A2+ 腫瘤這個特定的靶。
   兩層讀出合起來剛好互補：形態學鎖「當下確實活化」，過夜再刺激鎖「活化的靶就是 MART-1」——把「這些是抗腫瘤效應 T 細胞」的結論封死。反過來如果只看抹片、跳過過夜刺激，會有真實風險：活化型 blastic morphology 也能來自病毒感染（例如 EBV 引起的傳染性單核球增多症）、自體免疫發作、非特異發炎——事實上病人 9 事後確實出現了 EBV 相關的淋巴增生疾病，所以「看到很像效應細胞的形態」不等於「這些細胞在殺癌」。過夜再刺激這一步的細節也要小心：如果 IL-2 沒洗乾淨，殘留的 IL-2 會逼 T 細胞不管有沒有 MART-1 都分泌 IFN-γ，結論會變成「IL-2 效應」而不是「抗原特異性」；如果少了不做過夜浸泡的對照，也沒辦法區分反應是充電前就有還是充電後才有。作者兩種對照都做齊，才能把 signal 歸給抗原特異性。
4. 工具與材料:
   - **Blood smear (Wright-Giemsa 染色)**: 最直觀的形態學方法——顯微鏡下直接觀察每顆淋巴球的核形、核質比與細胞質顆粒。
   - **Hyperchromatic nuclei / high N/C ratio**: 「深染細胞核」與「高核質比」——染色質高度轉錄、細胞核相對細胞質膨大的活化淋巴母細胞外觀。
   - **Toxic granulation / Dohle bodies**: 細胞質裡的藍色顆粒（毒殺武器 granzyme/perforin 裝載）與 RNA 富集區，都是活化訊號。
   - **Blastic morphology**: 上述特徵合起來的典型活化 T 細胞外觀，與靜止淋巴球容易區分。
   - **Overnight reactivation (600 IU/ml IL-2)**: 把血液 T 細胞浸在維持型濃度 IL-2 過夜「充電」，洗淨後再測抗原特異性 cytokine 分泌；區別 REP 的 6000 IU/ml 擴增劑量。
5. 與此篇文章的關係:
   在《Cancer Regression and Autoimmunity in Patients After Clonal Repopulation with Antitumor Lymphocytes》這篇文章中，作者為了排除「活體內爆量的淋巴球其實是感染或非特異發炎的產物」這個懷疑，採用了「血液抹片形態學 + 過夜 IL-2 再刺激後測 cytokine」的雙讀出。它把「當下確實活化」與「活化的靶就是 MART-1／HLA-A2+ 腫瘤」兩件事分別鎖死。這一步吃進病人 9 (day 9) 與病人 10 (day 8) 的 PBL，產出直接的活化型形態證據與嚴格抗原限制的 cytokine 反應，補強 clonal repopulation 論述中「這批細胞真的能做事」的功能面。
