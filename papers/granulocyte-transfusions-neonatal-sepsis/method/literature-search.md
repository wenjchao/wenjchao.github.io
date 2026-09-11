# 多資料庫文獻檢索與試驗鑑別策略

1. 引用自哪篇 paper: granulocyte-transfusions-neonatal-sepsis
2. Outline (任務主線): 多資料庫文獻檢索與試驗鑑別策略
3. Method:
   系統性回顧的原料就是別人做過的試驗，所以第一步是把全世界可能相關的試驗盡量撈乾淨。作者用 Cochrane Neonatal Review Group 的標準檢索式 (search strategy)，在 2011 年 7 月、不限語言，橫掃多個資料庫——CENTRAL、MEDLINE（含 PREMEDLINE）、EMBASE、CINAHL——再加會議摘要（Pediatric Academic Societies、European Society for Paediatric Research）、BIOSIS 生物學摘要，以及 ClinicalTrials.gov、clinical-trials.com 上進行中的試驗，還直接寫信向作者索取未發表資料。檢索式的骨架，是把各種「白血球輸注」的講法用 OR 全串起來（granulocyte、buffy coat、leukocyte、neutrophil 各自 near transfusion），再和「新生兒」的詞用 AND 相交，最後限定在人類。
檢索式裡有兩個關鍵工具，都是為了不漏抓。醫學文獻有一套標準主題詞 (MeSH)，排成樹狀的上下位關係；把某個主題詞「展開 (explode)」，等於連同它底下所有更細的子詞一次全選，例如展開 granulocytes 就同時抓到各類顆粒球。另一個是「近鄰算符 (near)」，要求兩個字靠得夠近才算命中，例如 granulocyt* near transfusion* 只挑「顆粒球」與「輸注」相鄰出現的文章，比單純要求兩字都出現更精準，能避免抓進一大堆不相干的文獻。
為什麼要跨這麼多資料庫，還去挖會議摘要、未發表資料、又不限語言？一方面是把檢索的敏感度 (sensitivity) 拉到最高，寧可先多抓、之後再篩；更關鍵的是要對抗發表偏差 (publication bias)——結果漂亮的研究比較容易被期刊登出來，陰性或沒差的結果常被壓在抽屜裡、或只出現在會議摘要。若只搜主流資料庫、只收英文，留下的證據就會系統性地偏向正面結果，把療效講得比實際更好。因此作者連灰色文獻 (grey literature：試驗註冊庫、未發表通訊等非正式來源) 都一起挖。
反過來說，如果檢索偷懶，只搜一個資料庫、只收英文，最後的合併結論就會被系統性地帶偏：漏掉的多半是那些沒登上主流英文期刊的陰性或小型試驗，於是被合併的樣本偏向「看起來有效」，算出來的合併療效被高估，整篇回顧因此不可靠。這正是檢索階段要盡量窮盡、而不是找到幾篇就收手的原因。
4. 工具與材料:
   - **標準檢索式 (search strategy)**: Cochrane Neonatal Review Group 的標準搜尋語法，本回顧橫跨多庫套用。
   - **醫學主題詞展開 (MeSH explode)**: 選定一個標準主題詞連同其所有下位子詞一次全選，避免漏抓。
   - **近鄰算符 (near)**: 要求兩個字相鄰出現才算命中，比單純要求兩字皆有更精準。
   - **灰色文獻 (grey literature)**: 會議摘要、試驗註冊庫、未發表通訊等非正式發表來源。
   - **發表偏差 (publication bias)**: 正面結果較易被期刊登出、陰性結果被壓下的系統性偏差，全面搜索用以對抗它。
   - **檢索敏感度 (sensitivity)**: 檢索抓全相關研究的能力，此處刻意拉到最高，寧可先多抓再篩。
   - **資料庫 (CENTRAL / MEDLINE / EMBASE / CINAHL)**: 本回顧橫掃的主要文獻資料庫。
5. 與此篇文章的關係:
   在《Granulocyte transfusions for neonates with confirmed or suspected sepsis and neutropenia》這篇 Cochrane 回顧中，作者要合併全世界的隨機試驗來回答顆粒球輸注是否有效。多資料庫檢索是整條流程的入口，用高敏感度檢索式跨庫、挖灰色文獻、不限語言，解決了發表偏差可能遺漏陰性試驗的瓶頸。它的產出是一份盡量窮盡的候選文獻清單，交給下一步的 PICO 篩選。
