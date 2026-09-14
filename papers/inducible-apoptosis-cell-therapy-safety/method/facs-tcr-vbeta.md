# 流式細胞術免疫表現型分析與 TCR Vβ 剖析

1. 引用自哪篇 paper: inducible-apoptosis-cell-therapy-safety
2. Outline (任務主線): 流式細胞術免疫表現型分析與 TCR Vβ 剖析
3. Method:
      iCasp9 本身塞在細胞內部、抗體染不到，作者利用同一段 mRNA 靠 2A 拆解碼一起表現的 ΔCD19 當外顯替身：ΔCD19 是被切掉訊號尾巴的 B 細胞表面蛋白，正常 T 細胞天生沒有，所以血中一看到「CD3⁺（T 細胞）且 CD19⁺（外掛標籤）」的雙陽細胞，就一定是被改造裝上 iCasp9 的那批。流式儀器 (FACSCanto II) 一顆一顆掃過去，就能算出每毫升血中 CD3⁺CD19⁺ 細胞數，時間軸拉出來就是 iCasp9-T 細胞在體內的擴增與清除動力學曲線。作者同時把 CD4、CD8、CD45RA/RO、CD62L、CD27、CD28、CD127 全部貼上，讓每顆細胞在儀器裡呈現一組獨特的顏色組合，判定回輸進去的到底是幫助型 (CD4)、殺手型 (CD8)、還是待命型的 central memory 或現役型的 effector memory 分群。
   為了在 rescue 之後檢查倖存 T 細胞是「多元大隊」還是「單一 clone 暴衝」，作者從蛋白層面切入 TCR Vβ 剖面：每顆 T 細胞頭上都掛著一支專屬的辨識器 (T cell receptor)，它的可變段 (Vβ) 從人類大約 24 個家族中挑一個組出來；健康又多元的族群應該 24 個家族各佔一點百分比，寡株擴增則某一兩個家族會凸起。作者用 IO Test Beta Mark 套組 (Beckman Coulter) 一次把對應 24 個 Vβ 家族的抗體全染上，在流式儀器上量各家族百分比。之所以要全覆蓋而不是抽查幾個，是因為只染 3-4 個家族的話，rescue 後若倖存細胞正好集中在你沒染的家族之一，會誤判成細胞消失、或漏掉寡株尖峰。
   為了證明 rescue 後倖存的 T 細胞還保有抗病毒能力，作者把 ADV、CMV、EBV、survivin、HCV 這幾個蛋白各自切成一連串 15 個胺基酸、彼此重疊 11 個胺基酸的短胜肽 (overlapping peptide library)，這樣不管 T 細胞認的是哪一小段都能被喚醒。把 PBMC 與胜肽庫混在一起孵過夜，同時加上 Brefeldin-A——一種擋住高基氏體到分泌路徑的藥，讓 T 細胞造出的 IFN-γ 全部堆在細胞內、不會分泌跑掉。染色順序也關鍵：先在活細胞外面染 CD3/CD8/CD19，再用打洞液 (Cytofix/Cytoperm) 讓抗體鑽進細胞內染 PE-抗 IFN-γ；如果反過來先戳穿再染表面，Cytofix 會打壞某些表面 epitope 的立體結構、CD3/CD19 訊號會失真，且死細胞非特異染色會把百分比稀釋掉。
4. 工具與材料:
   - **FACSCanto II**: BD 的流式細胞儀，主要負責一顆一顆掃 T 細胞、依表面標籤組合分類與計數。
   - **CD3⁺CD19⁺ 雙陽門**: 以 CD3 定 T 細胞身分、以 ΔCD19 當開關存在的替身，兩者同陽即判定為 iCasp9-T 細胞。
   - **T 細胞亞群 marker panel (CD4/CD8/CD45RA/RO/CD62L/CD27/CD28/CD127)**: 組合表面染色讓每顆細胞呈現獨特顏色組合，用來分幫助型/殺手型與 naïve/central memory/effector memory 分群。
   - **TCR Vβ 剖面 (IO Test Beta Mark, Beckman Coulter)**: 一次把對應約 24 個 Vβ 家族的抗體全染上，量各家族百分比以判定多株性。
   - **Overlapping peptide library (15-mer, overlap 11 aa)**: 把 ADV/CMV/EBV/survivin/HCV 蛋白切成互相重疊的短胜肽庫，喚醒認得該蛋白的 T 細胞。
   - **Brefeldin-A**: 擋住高基氏體到分泌路徑的藥，讓 T 細胞造出的 IFN-γ 堆在細胞內好被抗體染。
   - **Cytofix/Cytoperm**: 固定並通透細胞膜的溶液，讓抗體鑽進細胞內染細胞內的 IFN-γ。
   - **PE-anti-human IFN-γ**: PE 螢光標記的抗 IFN-γ 抗體，在流式讀出「認得病毒的 T 細胞」百分比。
5. 與此篇文章的關係:
   在《Inducible Apoptosis as a Safety Switch for Adoptive Cell Therapy》這篇文章中，作者要驗證 iCasp9 安全開關的「觸發前擴增、觸發後清除、清除後保留抗病毒能力」三段動力學，因此把流式細胞術 (FACS) + TCR Vβ 剖析 + 細胞內 cytokine 染色綁在同一批 PBMC 上：吃進去的是每個時點抽的血樣，吐出來的是給 qPCR 對照的 CD3⁺CD19⁺ 絕對計數、亞群組成、Vβ 家族百分比與抗病毒 T 細胞的 IFN-γ 反應，把「開關能秒殺又能留下 useful 免疫池」的臨床證據撐起來。
