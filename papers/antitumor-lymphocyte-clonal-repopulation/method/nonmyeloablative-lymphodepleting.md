# 非清髓性淋巴削減化療

1. 引用自哪篇 paper: antitumor-lymphocyte-clonal-repopulation
2. Outline (任務主線): 非清髓性淋巴削減化療
3. Method:
      作者在輸入 T 細胞前，刻意先動手清空病人自己的免疫系統——這一步稱作「非清髓性淋巴削減化療」(nonmyeloablative lymphodepleting chemotherapy)。所謂「非清髓」是指化療只把血液和淋巴組織裡的淋巴球擊倒，不動到骨髓深處的造血幹細胞，讓病人不需要另做骨髓移植救援。實際操作是輸細胞前第 7 天起連打 2 天環磷醯胺 (cyclophosphamide, 60 mg/kg)，接著 5 天氟達拉濱 (fludarabine, 25 mg/m²)。等最後一劑氟達拉濱之後隔天、血液中的淋巴球絕對數 (ALC) 與嗜中性球絕對數 (ANC) 雙雙掉到 <20/mm³ 這個閥值，才把 T 細胞回輸——把「削夠深了嗎」這個抽象問題，換算成每天抽血能追蹤的兩個數字，當進下一步的閘門。protocol 改自 Childs et al. 2000 N. Engl. J. Med.（ref 27）。
   削減化療到底在削什麼？外來 T 細胞打進去就消失，是因為宿主端至少有三層壓力：血液和淋巴組織的空間被自家淋巴球佔滿；體內原本就有一群「免疫系統的煞車」(regulatory cells) 會主動關掉免疫反應；還有一套「恆定性壓力」(homeostatic regulation) 透過搶奪 IL-7、IL-15 這類生長因子把每群淋巴球維持在固定量。環磷醯胺在細胞內代謝成活性分子後鑽進 DNA 兩股之間打交聯，讓分裂中的細胞當場斷裂而死；氟達拉濱長得像 DNA 材料 (purine analogue)，被淋巴球優先吸收後把 DNA 合成卡住。兩支藥都特別會殺分裂中或代謝旺盛的細胞——淋巴球與調節性細胞剛好在這狀態，骨髓幹細胞相對休眠，因此不會被順帶波及。等於同時把「原房客」清空、把「煞車」拆掉、把「食物」讓出來——這就是作者所謂為 clonal repopulation 清出「生態位」(niche)。
   為什麼一定要削到這麼深？作者自己有前車之鑑：他們過去只送純化的 CD8+ T cell clone 給 15 位病人（其中有些也做過較淺的 nonmyeloablative conditioning），結果沒有任何一位有反應、細胞也全部消失（Dudley 2002, ref 5）。削減不到位會有三種壞法：名額被佔滿讓外來細胞無處可住、煞車還在讓外來細胞被關機、食物不夠讓外來細胞餓死。氟達拉濱對 CD4+ helper 特別狠、恢復也最慢（Cheson 1995 J. Clin. Oncol），這正是作者要的效果：連 helper 都不留下才夠空。反過來，若劑量再拉高把骨髓也一起炸掉就變成清髓，病人就得做骨髓救援。作者刻意停在「非清髓」這個臨界點：淋巴球歸零、骨髓還能重生。這種深度削減不是零代價，9 號病人事後發生 EBV 相關的淋巴增生、5 號病人得了短暫的呼吸道病毒感染，是要換得 clonal repopulation 必須承擔的副作用。
4. 工具與材料:
   - **Cyclophosphamide (Cy, 環磷醯胺)**: 一種 alkylating 化療藥，代謝後與 DNA 兩股形成交聯，讓分裂中的淋巴球死亡；本實驗劑量為 60 mg/kg × 2 天。
   - **Fludarabine (Flu, 氟達拉濱)**: purine 類似物，被淋巴球選擇性吸收後干擾 DNA 合成，尤對 CD4+ T 細胞削減深；本實驗劑量 25 mg/m² × 5 天。
   - **ALC (Absolute Lymphocyte Count)**: 每立方毫米血液中的淋巴球絕對數；作者以 ALC < 20/mm³ 當作可進入 T 細胞輸注的閘門條件之一。
   - **ANC (Absolute Neutrophil Count)**: 每立方毫米血液中的嗜中性球絕對數；同樣需 <20/mm³ 才進入輸注；治療後 day 11 左右自然恢復到 >500/mm³。
   - **Nonmyeloablative lymphodepletion**: 刻意把化療劑量停在「削光淋巴球但不摧毀骨髓造血幹細胞」的臨界點，病人不需骨髓移植救援。
   - **Regulatory cells / Homeostatic regulation**: 宿主本身壓抑免疫反應與維持淋巴球數量的兩層機制；作者藉削減化療同時解掉。
   - **Childs et al. 2000 N. Engl. J. Med. (ref 27)**: 原始 Cy+Flu 預處理 protocol 出處，本論文直接沿用改編。
5. 與此篇文章的關係:
   在《Cancer Regression and Autoimmunity in Patients After Clonal Repopulation with Antitumor Lymphocytes》這篇文章中，作者為了讓過去屢屢在體內消失的過繼 T 細胞真的活下來繁殖，先採用了「非清髓性淋巴削減化療」(Cy + Flu 預處理)。這一步解決了「宿主淋巴球佔滿名額、調節性細胞壓抑外來部隊、恆定訊號被搶光」三層瓶頸，並且刻意不摧毀骨髓造血，讓病人免於做骨髓救援。它為下游的 TIL 輸注與高劑量 IL-2 治療清出可用的「生態位」，是整套療程能達成 clonal repopulation 的第一塊拼圖。
