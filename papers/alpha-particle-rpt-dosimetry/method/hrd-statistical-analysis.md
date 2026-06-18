# 統計分析：HRD(+) vs HRD(−) 反應比較與存活分析

1. 引用自哪篇 paper: alpha-particle-rpt-dosimetry
2. Outline (任務主線): 在 ²²³Ra mCRPC 回溯性研究中，量化 HRD 突變對治療反應與生存期的影響，作為 synthetic lethality 臨床轉譯的證據。
3. Method:
²²³Ra mCRPC 回溯性研究 (Isaacsson Velho 2018 [4]) 的反應定義是 12 週內 PSA 下降 ≥50% 或 ALP 下降 ≥30% (Table 3 footnote)。為什麼用兩個指標？PSA（前列腺特異性抗原）反映腫瘤全身活性；ALP（鹼性磷酸酶）反映骨頭重塑活性。²²³Ra 是骨向 α 藥、活性集中在骨轉移病灶，所以 ALP 才是它療效的真正「即時指針」；事實上 Table 3 顯示兩組 PSA ≥50% 反應率都是 0%，作者真正比對的是 ALP ≥30% response（HRD+ 80% vs HRD− 39%）與 ALP normalization（100% vs 33%）兩個 ²²³Ra 看得見差異的終點。

比較反應率時，在 HRD(+) 10 人、HRD(−) 18 人的小樣本下，2×2 列聯表用 Fisher's exact test 算 p 值：「假設兩組其實沒差，光憑機運看到 80% 與 39% 這麼大差距的機率」。p=0.04 代表這個機運只有 4%，習慣上 <0.05 視為兩組真的有差；ALP normalization 100% vs 33% 對應 p=0.03。比較時間到事件 (time-to-event) 則用 Cox 比例風險模型算 Hazard Ratio (HR)：HR = 兩組「下一秒發生事件的瞬間風險」之比。Time-to-ALP-progression HR = 6.4（HRD− 對 HRD+），對應中位時間 5.8 月 vs 10.4 月——HRD+ 撐得久將近兩倍；95% CI 1.5–28.9 下限大於 1、p=0.005 << 0.01，差異非常顯著。為什麼用 HR 而非單純比較 median？因為很多病人會在事件發生前被『censored』，Cox 同時用上「事件時間」與「censored 病人到目前撐到多久」的所有資訊，比 median 比較浪費更少資料。

這份分析特意採用回溯性 (retrospective) 框架：²²³Ra 已是 mCRPC 的標準療法，作者直接挖出 190 名 mCRPC 病人之中 28 名接受過 ²²³Ra 的子集，做 germline + somatic 定序分成 HRD(+) 10 人 / HRD(−) 18 人 (Table 2)，幾個月就能拿到方向性訊號，不必重新收案數年。它在 synthetic lethality 證據鏈中的角色是把細胞實驗的 8–15 倍 RBE 提升「先在真人身上驗證一次方向」，再撐起後續前瞻試驗或 PARPi + αRPT 組合療法的研究假說。比較大的差異藏在生存：overall survival HR=3.3、中位 36.9 vs 19.0 月，效應其實非常大，但 p=0.11 沒過 0.05——這是因為樣本只有 10 vs 18 人、統計檢力不足。

判讀這類小樣本回溯資料容易踩兩個坑。第一是「p 值膜拜」：把 OS HR=3.3、中位 36.9 vs 19.0 月、p=0.11 一律當作「沒效」，等於把「方向強烈、僅樣本不足」與「真的沒效」混為一談，會錯失 synthetic lethality 在真人的早期訊號、拖延正式前瞻試驗。第二是「選樣偏差」：190 人裡只挑出 28 名接受 ²²³Ra 的，背後可能有醫師選擇、體能狀態、先前治療等因素左右誰被開了 ²²³Ra；如果 HRD+ 與 HRD− 兩組在這些基線特徵不平衡，觀察到的反應差異會被基線差異混淆。作者因此明確把結論定位為「方向性證據」，認真的因果結論仍需前瞻 RCT 來驗。
4. 工具與材料:
- **PSA ≥50% response**: 12 週內前列腺特異性抗原較基線下降 ≥50% 的反應定義；²²³Ra 在這個指標兩組都是 0%。
- **ALP ≥30% response**: 12 週內鹼性磷酸酶較基線下降 ≥30% 的反應定義；²²³Ra 療效的主要終點。
- **ALP normalization**: 基線升高的 ALP 回到正常範圍；HRD+ 為 100% vs HRD− 為 33%（p=0.03）。
- **Fisher's exact test**: 小樣本 2×2 列聯表的精確檢定，用來算 ALP 反應率兩組比例差異的 p 值。
- **Cox 比例風險模型**: 處理 time-to-event 資料的回歸模型，產出 Hazard Ratio + 95% CI + p 值。
- **Hazard Ratio (HR)**: 兩組「下一秒發生事件的瞬間風險」之比；time-to-ALP-progression HR=6.4，OS HR=3.3。
- **95% confidence interval (95% CI)**: HR 點估計周圍的可信區間；下限 >1 才能說 HR 在統計上顯著偏離 1。
- **Censored**: 病人追蹤到某時間點仍未發生事件就被截止；Cox 模型仍能納入這些資訊，median 比較則做不到。
5. 與此篇文章的關係:
在《Dosimetry, Radiobiology and Synthetic Lethality: Radiopharmaceutical Therapy (RPT) with Alpha-Particle-Emitters》這篇文章中，作者為了把細胞層級的 synthetic lethality 假說在真人身上驗證，採用了 Isaacsson Velho 2018 的回溯性統計分析框架。它解決了「²²³Ra 早已是 mCRPC 標準療法、無法臨時啟動前瞻試驗測 HRD 影響」的瓶頸，吃進 28 名接受 ²²³Ra 病人的 germline + somatic 定序與療效資料，產出 Fisher's exact test 與 Cox HR 數字，供下游前瞻試驗與 PARPi + αRPT 組合療法假說使用。
