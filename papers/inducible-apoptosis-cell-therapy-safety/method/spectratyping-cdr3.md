# 多重 PCR-based Spectratyping（CDR3 長度譜分析）

1. 引用自哪篇 paper: inducible-apoptosis-cell-therapy-safety
2. Outline (任務主線): 多重 PCR-based Spectratyping（CDR3 長度譜分析）
3. Method:
      每顆 T 細胞在還沒認識抗原之前，先在體內把 V、D、J 三塊基因片段隨機拼在一起組成自己專屬的辨識器 (T cell receptor)；拼接的接縫上還會被酵素隨機加或刪幾個核苷酸，最容易變異的區段叫 CDR3。這種隨機拼法讓每顆 T 細胞的 CDR3 長度略有不同——健康又多元的族群裡，CDR3 長度會呈現接近鐘形的高斯分佈；如果整批細胞都是同一顆的後代，CDR3 長度就會全部一樣、直方圖冒出一根尖峰。作者從富集的 CD3⁺CD19⁺ T 細胞取 mRNA 反轉錄成 cDNA，然後跑多重 PCR (multiplex PCR)——一管反應裡放好幾對引子，同時把 24 個 Vβ 家族的 CDR3 都擴增出來；產物再上毛細管電泳，儀器在管子出口讀螢光，短片段先到、長片段後到，畫出各家族的「CDR3 長度 vs. 螢光強度」直方圖。之所以要從 mRNA 而非 DNA 切入，是為了只量「當下正在表達 TCR 的活躍 T 細胞」，不被沒上工的殘留細胞稀釋。作者採用 Akatsuka 等人 1999 年 Tissue Antigens 已標準化的流程，把樣本送到 Fred Hutchinson Cancer Research Center 的 immune monitoring laboratory 執行——那家實驗室對每對引子做過效率校正，能避免引子強弱不均把家族百分比拉歪。
   流式 Vβ 抗體只能告訴你「這 24 個家族各佔幾成」，家族內部若同一顆細胞被暴衝式擴增成數萬份，抗體看到的百分比不變。CDR3 長度譜切進家族內部：同一個家族裡如果原本應該有 5-8 種長度呈鐘形，卻只剩下一根長度尖峰，就能揭露「家族內部寡株化」。作者以蛋白軸 (flow Vβ) + mRNA 軸 (spectratyping) 兩層 orthogonal 讀出，共同支撐 rescue 後恢復族群「多元大隊」的結論。需要注意 spectratyping 依賴同一家族抓到幾十上百條不同 CDR3 序列才能畫出鐘形；若 cDNA 量太少，某家族可能天然出現偽尖峰、被誤判為寡株，所以作者先富集 CD3⁺CD19⁺ 群、也倚賴 Fred Hutchinson 標準流程對輸入量的門檻要求來避免這類抽樣雜訊。
4. 工具與材料:
   - **Multiplex PCR (Akatsuka 1999 Tissue Antigens)**: 一管反應同時擴增多個 Vβ 家族 CDR3 的標準流程；比逐家族擴增更省樣本且更利於跨家族比較。
   - **CDR3 (T cell receptor 接合最變異區)**: T 細胞辨識器裡因 V-D-J 隨機拼接與接縫加減核苷酸而長度變異最大的區段，長度分佈即多株性指標。
   - **毛細管電泳**: 細塑膠管內填膠、DNA 在電場下依長度分離，儀器讀螢光形成長度 vs. 強度直方圖。
   - **Gaussian polyclonal pattern**: 多株健康族群 CDR3 長度呈鐘形分佈；寡株擴增則有偏高尖峰。
   - **Fred Hutchinson immune monitoring laboratory**: 執行本 spectratyping 的專職實驗室，已對每對 Vβ 引子做過效率校正以確保跨家族比較。
5. 與此篇文章的關係:
   在《Inducible Apoptosis as a Safety Switch for Adoptive Cell Therapy》這篇文章中，作者要證明 AP1903 rescue 後恢復的 CD3⁺CD19⁺ T 細胞不是被單一 clone 主導，因此在 flow Vβ 之外加做 multiplex PCR-based spectratyping：吃進去的是富集後 T 細胞的 mRNA，吐出來的是各 Vβ 家族 CDR3 長度分佈直方圖。它切進 flow Vβ 看不到的家族內部寡株化死角，為「rescue 後仍保有抗病毒功能」的臨床結論提供 mRNA 層獨立佐證。
