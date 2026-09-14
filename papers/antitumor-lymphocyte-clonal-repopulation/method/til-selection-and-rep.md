# TIL 分離、腫瘤特異性篩選與快速擴增

1. 引用自哪篇 paper: antitumor-lymphocyte-clonal-repopulation
2. Outline (任務主線): TIL 分離、腫瘤特異性篩選與快速擴增
3. Method:
      作者要組出一支數量到 10¹⁰ 級、又真的認得腫瘤的 T 細胞部隊。第一步是從切下的黑色素瘤病灶裡撈出「腫瘤浸潤淋巴球 (tumor-infiltrating lymphocytes, TIL)」——這些細胞既然自己爬進腫瘤，代表它們的辨識天線本來就對得上腫瘤上的某個標籤。作者刻意把每一塊病灶都分成好幾口井獨立培養 (multiple parallel cultures)，各自獨立測特異性；一鍋養會把真正兇的 clone 稀釋掉。接著用「細胞激素分泌測試」(cytokine secretion assay，方法見 ref 11 supporting material)：把每口井分別跟病人自己的腫瘤細胞、或標準的 HLA-A2+ 黑色素瘤細胞株共培養——所有 13 位病人都是 HLA-A2+，代表他們的 MART-1 展示窗一致，能借標準株當比對對象。如果 T 細胞真的認得，就會被啟動分泌 IFN-γ；不反應的井直接淘汰。
   通過篩選的 TIL 再進入「快速擴增協議 (rapid expansion protocol, REP)」（Riddell & Greenberg 1990, J. Immunol. Methods, ref 28）。REP 這一鍋裡有三味料：抗 CD3 抗體 (OKT3) 直接抓住每顆 T 細胞的辨識天線根部給一個通用「開始分裂」訊號；照射過的異體餵養細胞 (irradiated allogeneic feeder cells) 自己不會再分裂，卻還帶著共刺激分子與養分；6000 IU/ml 的高濃度 IL-2 則是 T 細胞的「分裂食物」，逼被 OKT3 開機的 T 細胞持續分裂。三味合起來，1–2 個 cycle 就能把幾百萬顆起始 TIL 擴到平均 7.8 × 10¹⁰ 顆（範圍 2.3–13.7 × 10¹⁰），足夠一次臨床輸注用。TIL 分離與初步培養的 protocol 沿用 Rosenberg 1994 (ref 2) 與 Dudley 2002 (ref 5) 的作法。
   作者刻意不走「一個 clone 打天下」的路。過去他們把 TIL 挑成單一 CD8+ clone 再擴增送給 15 位病人，結果沒人有反應、細胞全部消失（Dudley 2002, ref 5）；原因之一是純化過度把 CD4+ helper 洗掉、失去對 CD8+ 存續有正貢獻的伴手（refs 19, 25）。所以他們改成「井級篩選、混合擴增」——只淘汰整口不反應的井，不再往單一 clone 純化，保住 CD4/CD8 混合比例（Table 1 每位病人的 CD8/CD4 差很大就是這個緣故）。另一個要小心的失敗模式是 OKT3 過度刺激：反覆做太多輪 REP 會把 T 細胞推向終末分化——體外數量漂亮、體內卻沒力氣分裂，於是作者只跑 1–2 個 cycle 就停手。反過來，若跳過細胞激素篩選一鍋直接擴增，最後 10¹⁰ 顆裡真正認得腫瘤的只佔一小部分，其餘都是 bystander，效力會被稀釋、也無法把後續腫瘤縮小歸因到特定 clone。
4. 工具與材料:
   - **TIL (tumor-infiltrating lymphocytes)**: 原本已經潛伏在腫瘤組織裡的 T 細胞；比從血液抽起始細胞多得多的腫瘤特異性比例。
   - **Multiple parallel cultures**: 作者把每塊病灶分成多口井獨立培養並獨立測特異性，避免高反應性 clone 被稀釋。
   - **Cytokine secretion assay**: T 細胞遇到熟悉抗原後分泌 IFN-γ 等訊號分子的定量測試；作者用它逐井淘汰無反應的 TIL 培養（見 ref 11）。
   - **HLA-A2**: 人類細胞表面的一種抗原展示窗，能剛好把 MART-1 的一段掛出來；13 位病人皆為 HLA-A2+，方便共用標準腫瘤細胞株做比對。
   - **REP (Rapid Expansion Protocol)**: 1–2 週把 T 細胞擴到 10¹⁰ 級的擴增方案；來自 Riddell & Greenberg 1990（ref 28）。
   - **OKT3 (anti-CD3)**: 抓 T 細胞辨識天線根部 CD3 給出通用開機訊號的抗體，是 REP 的第一味料。
   - **Irradiated allogeneic feeder cells**: 照射過使其失去分裂能力的異體 PBMC/LCL 細胞，只當共刺激與養分供應者。
   - **6000 IU/ml IL-2**: REP 中拉到高濃度的 T 細胞分裂食物，逼被 OKT3 開機的 T 細胞連續分裂。
5. 與此篇文章的關係:
   在《Cancer Regression and Autoimmunity in Patients After Clonal Repopulation with Antitumor Lymphocytes》這篇文章中，作者為了替 13 位病人備妥一支「數量足夠又真的認得腫瘤」的 T 細胞部隊，採用了 TIL 多株獨立培養、細胞激素分泌篩選加上快速擴增協議 (REP) 的三段組合。這一步解決了過去單一 CD8+ clone 純化後失去 CD4+ helper、體內存續不佳的瓶頸；它吃進病人切下的腫瘤病灶，產出平均 7.8 × 10¹⁰ 顆通過反應性驗證的混合 TIL，交給下游的淋巴削減病人做一次性靜脈輸注。
