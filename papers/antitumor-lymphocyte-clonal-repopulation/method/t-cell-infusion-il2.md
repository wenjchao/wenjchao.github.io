# 自體 T 細胞輸注與高劑量 IL-2 治療方案

1. 引用自哪篇 paper: antitumor-lymphocyte-clonal-repopulation
2. Outline (任務主線): 自體 T 細胞輸注與高劑量 IL-2 治療方案
3. Method:
      化療削減完成、ALC/ANC 掉到 <20/mm³ 後，作者把擴增好的 TIL 全部裝進點滴袋，經靜脈在 30–60 分鐘內一次滴完——不做分次、不做劑量爬升。每人平均一次收下 7.8 × 10¹⁰ 顆細胞（範圍 2.3–13.7 × 10¹⁰）。時機選在淋巴系統還幾乎是真空的當下，能在最短時間內把空出的「生態位」搶佔滿。細胞輸注之後緊接著高劑量 IL-2：720,000 IU/kg 一次性靜脈推注 (bolus)，每 8 小時重複，直到病人身體出現無法耐受的副作用才停 (to tolerance)。這個給法沿用 Rosenberg 1998 Ann. Surg. (ref 10) 治療黑色素瘤的標準版本；每位病人平均收到 9 劑（範圍 5–12），落點差這麼多，是因為 IL-2 副作用（血管漏水、血壓掉、發燒、少尿）逼近每個人不一樣的耐受邊界，作者不設固定劑數，而是每 8 小時重新評估。
   為什麼「削空 + 打細胞 + 高劑量 IL-2」這三段合在一起能觸發 clonal expansion？化療把宿主淋巴球清空後，原本由淋巴球消耗掉的 IL-7、IL-15 生長因子暫時囤在血液和淋巴組織裡——這是身體想把淋巴球拉回正常數量的「恆定性壓力」(homeostatic regulation)。剛輸入的 TIL 一進去就撞見食物過多、又沒有煞車的環境，會自動被推進「恆定性增殖 (homeostatic proliferation)」的模式補位。作者再疊加 IL-2 的高劑量 bolus：T 細胞的 IL-2 受體對「短時間濃度衝高」反應最強，一次性 bolus 能讓血中 IL-2 濃度瞬間拉到平時的數十倍，直接把 T 細胞的分裂機關推到高檔。慢速持續、低劑量的注射達不到這個瞬時峰值，只能讓 T 細胞維持存活但很少大量分裂——所以作者刻意選 bolus。
   部分病人第一輪後呈現「混合反應 (mixed)」或「部分反應 (PR)」——代表輸進去的 T 細胞確實有效但不足以壓過所有腫瘤，這時作者會再跑一輪完整的 ACT（削減 + TIL 輸注 + 高劑量 IL-2），把 clone 再推一波，避免單次不夠就下無效判定。若把 IL-2 這一味料抽掉，剛輸入的 TIL 雖能靠削減後暫時囤積的 IL-7、IL-15 撐一陣，但很難達到「佔血中殺手細胞 60–97%」這種戲劇性的 clonal expansion；歷史上不搭 IL-2 的 clone 輸注幾乎都在幾天內失去偵測訊號。反過來，若無視 to tolerance、硬要打滿 12 劑，IL-2 的副作用會逼近臨床安全邊界，可能造成嚴重低血壓休克與多器官衰竭。因此 Table 1 每位病人 5–12 劑的變化不是隨便定，而是動態判定的結果。
4. 工具與材料:
   - **Single IV infusion (30–60 min)**: 把 10¹⁰ 級 TIL 一次性經靜脈滴完，搶佔削減後空出的生態位。
   - **High-dose IL-2 (720,000 IU/kg bolus q8h)**: 每 8 小時一次靜脈推注，把血中 IL-2 濃度瞬間拉到平時數十倍，強推 T 細胞分裂；沿用 Rosenberg 1998 Ann. Surg. (ref 10)。
   - **To tolerance**: IL-2 給法的終點條件——不設固定劑數，只要病人出現無法耐受的副作用（低血壓、少尿、發燒）就停；平均 9 劑（範圍 5–12）。
   - **Homeostatic proliferation**: 淋巴削減後宿主體內 IL-7/IL-15 囤積、把新進 T 細胞自動推向分裂補位的機制。
   - **Second course of ACT**: 對混合反應或部分反應病人再跑一輪完整過繼細胞治療 pipeline 的補救策略。
5. 與此篇文章的關係:
   在《Cancer Regression and Autoimmunity in Patients After Clonal Repopulation with Antitumor Lymphocytes》這篇文章中，作者為了在削減好的病人身上真正觸發 T 細胞在體內的 clonal expansion，採用了「單次大量 TIL 靜脈輸注 + 高劑量 IL-2 bolus 每 8 小時 to tolerance」的組合。它解決了過去 T 細胞打進去很快消失、拿不到 objective response 的瓶頸，讓輸入的 tumor-reactive clone 有充足的分裂食物在真空環境下暴增。這一步接住上游 REP 擴增出的 7.8 × 10¹⁰ TIL，產出可長期在血液與腫瘤內偵測到的優勢 clone，供下游用 FACS、CDR3、IHC 等指標追蹤。
