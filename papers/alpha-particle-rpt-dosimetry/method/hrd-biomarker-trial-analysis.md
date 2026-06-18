# ²²³Ra 臨床試驗回溯性 HRD 生物標記分群

1. 引用自哪篇 paper: alpha-particle-rpt-dosimetry
2. Outline (任務主線): 在 metastatic castrate-resistant prostate cancer (mCRPC) 臨床數據中，驗證 HR DSB 修復路徑突變患者對 ²²³Ra 有更佳反應，把 synthetic lethality 概念從細胞模型轉譯至病人。
3. Method:
這個子項把 §2-B 細胞層級的合成致死假說搬到病人身上驗證。作者翻找 Johns Hopkins 既有的 190 名以骨轉移為主的 mCRPC 病歷，從中挑出 28 個曾經接受 standard-of-care ²²³Ra 治療的病人——²²³Ra 是 Ca²⁺ 的化學類似物，會自己跑到骨頭礦化最活躍的地方（也就是骨轉移處），把 α 粒子打在腫瘤旁邊。為什麼挑 ²²³Ra？因為它是目前唯一通過 FDA 並大規模用於 mCRPC 的 α-emitter standard-of-care 藥物，臨床病歷量遠超過任何 ²²⁵Ac/²¹³Bi 試驗，有足夠樣本可以做回溯性分群；雖然不是抗體導引、是化學親和力鎖定骨礦化，但造成的 DSB 機制跟其他 α-emitter 一樣是高 LET 損傷，HR 修補缺損理論上同樣會放大殺傷。為什麼用回溯性 (retrospective) 分析？因為已有累積病歷與檔案生檢可直接用，成本與時間遠低於前瞻性招募 + 隨機分組 + 追蹤幾年。代價是病人不是預先隨機分組、選樣偏誤難以完全控制，這份結果只是 synthetic lethality 在病人身上有訊號的概念驗證，不是定論性結果。

對這 28 個病人的腫瘤組織與血液檢體做兩種基因定序。Germline sequencing 找的是病人天生就帶在所有細胞裡的胚層突變（從血液白血球可以驗到），代表先天 HR 功能缺陷；somatic sequencing 則是腫瘤組織才有、後天累積的突變。兩種合起來才能完整抓到 HRD 表現型——只做 germline 會漏掉腫瘤後天演化的 HRD、只做 somatic 會漏掉先天遺傳的家族 HR 缺陷。Table 2 列出的 9 種突變類型代表 DNA 出錯的不同方式：missense（如 BRCA2 D3095E）換掉一個胺基酸，功能可能只輕微受損；frameshift（如 BRCA2 E164Qfs*23）插入或刪掉非 3 倍數鹼基、下游閱讀框錯位、產出截斷無功能蛋白；nonsense（如 CHEK2 R519X、ATM E2014X）把某密碼子換成 STOP、蛋白翻一半斷掉；splicing（如 ATR c.2634-1G>A）破壞剪接點、產出異常蛋白。Frameshift、nonsense、splicing 通常造成功能完全喪失，比較容易讓 HR 路徑徹底癱瘓。28 人中 10 個有任何一個 HR 基因被打壞歸為 HRD(+)、其餘 18 個沒有的歸為 HRD(−)。

比較兩組時挑哪個指標當主要終點是關鍵。PSA 是前列腺特異抗原、反映腫瘤細胞分泌活性；但 mCRPC 階段腫瘤已對荷爾蒙治療抗藥、PSA 變化跟治療效果脫鉤，Table 3 顯示兩組 PSA ≥50% 反應率都是 0%（p>0.99），完全分不出差異。ALP（鹼性磷酸酶）會在骨頭被破壞與重建時大量釋放到血液，骨轉移越活躍 ALP 越高；²²³Ra 直接攻擊讓 ALP 升高的源頭，所以是治療效果最敏感的指標。Table 3 結果：HRD(+) 組 ALP ≥30% 反應率 80%（8/10）、HRD(−) 只有 39%（7/18），p=0.04；HRD(+) 組 ALP 完全回到正常（在 baseline ALP 升高的病人中）的比例 100% vs 33%，p=0.03。Time-to-ALP progression：HRD(+) 10.4 月 vs HRD(−) 5.8 月，hazard ratio 6.4（95% CI 1.5–28.9）、p=0.005——這是這份分析訊號最強的終點。Overall survival：HRD(+) median 36.9 月 vs HRD(−) 19.0 月，HR 3.3、p=0.11。Time-to-next systemic therapy：9.7 vs 7.2 月，HR 1.5、p=0.39。方向都跟「HRD(+) 反應更好」一致，呼應 §2-B 細胞實驗的 RBE 跳升結論。

這份分析有兩個必須誠實承認的結構性限制。第一是小樣本與選樣偏誤：n=28、HRD(+) 只有 10 人，統計力不足——OS 中位 36.9 vs 19.0 月看起來差兩倍但 p=0.11 沒達顯著，time-to-next systemic therapy 完全沒訊號。同時病人不是預先隨機分組，HRD(+) 那 10 個可能剛好年紀較輕、骨轉移負荷較小、過去 chemotherapy 較少；反應好的部分可能不是 HRD 造成、而是這些干擾因素。第二是 HRD 突變光譜混合：Table 2 列的九個基因雖然都歸在 HR 路徑，但 BRCA2/PALB2 雙等位失能造成最強 HRD、ATM/CHEK2 失能 HR 仍能進行、Fanconi anemia 家族影響的是 DNA crosslink 修補。把這些一起歸到 HRD(+) 會稀釋訊號強度，反應好的可能只是 BRCA2 那幾個 frameshift 病人撐起來的、其他突變並沒有真正回應。所以這份結果定位為合成致死假說的概念驗證，下一步必須做前瞻性試驗（夠大樣本、預先按 HRD 分層再隨機分配 ²²³Ra）才能下定論——這也是把 §2-A、§2-B 的細胞機制完整轉譯到臨床決策的最後一步。
4. 工具與材料:
- **²²³Ra (Xofigo)**: Ca²⁺ 化學類似物的 α-emitter，會自己跑到骨頭礦化區把 α 粒子打在骨轉移處；mCRPC standard-of-care。
- **mCRPC**: metastatic castrate-resistant prostate cancer，骨轉移為主、已對荷爾蒙治療抗藥的攝護腺癌族群。
- **germline sequencing**: 從血液白血球驗到病人天生帶在所有細胞裡的胚層突變，代表先天 HR 功能缺陷。
- **somatic sequencing**: 從腫瘤組織驗到後天累積的突變，代表癌變過程中發展出的 HRD。
- **HRD (homologous recombination deficiency)**: BRCA2、ATM、CHEK2、PALB2、Fanconi anemia 家族等 HR 路徑基因任一被打壞的表現型。
- **missense / frameshift / nonsense / splicing**: DNA 出錯的四種主要方式；frameshift、nonsense、splicing 通常造成蛋白功能完全喪失。
- **PSA (≥50% response)**: 前列腺特異抗原；mCRPC 階段已對荷爾蒙抗藥、與 ²²³Ra 治療效果脫鉤，本研究兩組都 0%。
- **ALP (≥30% response, normalization)**: 鹼性磷酸酶，反映骨轉移活性；²²³Ra 治療效果最敏感的指標。
- **Time-to-ALP progression**: ALP 重新升高的時間；本研究 HR=6.4、p=0.005，是訊號最強的終點。
- **hazard ratio (HR)**: Cox proportional hazards 模型輸出的事件發生率比值；>1 代表 HRD(−) 組事件發生率較高。
- **retrospective analysis design**: 用既有病歷與檔案生檢做分群比較；成本低但無法隨機化、樣本量小、有選樣偏誤。
5. 與此篇文章的關係:
在《Dosimetry, Radiobiology and Synthetic Lethality: Radiopharmaceutical Therapy (RPT) with Alpha-Particle-Emitters》這篇文章中，作者為了把 §2-B 在 MDA-MB-231 細胞看到的「HR 修補缺損 + αRPT」合成致死強化效應翻譯到病人身上，採用了「²²³Ra mCRPC 病歷回溯性 HRD 生物標記分群」這套臨床轉譯工具（資料取自 Isaacsson Velho et al., Eur Urol 2018）。它解決了「細胞模型無法直接證明病人會有同樣反應」的瓶頸，產出 ALP ≥30% 反應 80% vs 39%、time-to-ALP progression HR=6.4 等支持訊號，作為未來前瞻性試驗用 HRD 突變先分層再隨機分配 αRPT 的概念驗證。
