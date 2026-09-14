# 腫瘤浸潤與 MHC 表現的免疫組織化學

1. 引用自哪篇 paper: antitumor-lymphocyte-clonal-repopulation
2. Outline (任務主線): 腫瘤浸潤與 MHC 表現的免疫組織化學
3. Method:
      為了看抗腫瘤 clone 是否真的鑽進實體腫瘤，作者在治療後不同時間點動手術切下腫瘤病灶（病人 9 於 day 20 與 day 57、病人 10 於 day 14），把切片薄片放到玻片上做免疫組織化學 (immunohistochemistry, IHC)——用一批各自「只認一種蛋白」的抗體染色。作者一口氣上了五支抗體：anti-CD8 抗體只染殺手型 T 細胞；anti-Vβ7 與 anti-Vβ12 抗體分別對應病人 10 與病人 9 主導 clone 的天線款式；另外兩支 anti-MHC class I 與 anti-MHC class II 抗體則染腫瘤細胞表面「亮出自己內部」的窗口。特別重要的是，作者拿病人 9 治療前的腫瘤（化療前切下的）與治療後 day 57 的腫瘤配成一對，把個體差異這個變數固定住，剩下的差異才能歸因於治療。
   IHC 真正的重頭戲在 MHC 這個讀數。MHC 是細胞表面一種「向外展示自己內部一小段蛋白」的窗口，T 細胞的天線就是靠這個窗口辨識目標；腫瘤細胞常會把窗口關小或關掉、把 MART-1 這種招牌藏起來。治療前病人 9 的腫瘤細胞幾乎不掛 MHC class I，MHC class II 更是完全不見；治療後 CD8+ 密集浸潤，同時 MHC I 與 MHC II 都大量掛回細胞表面。作者引用 Boehm et al., Annu. Rev. Immunol 1997 提出的機制：浸潤 T 細胞辨識到 MART-1 之後會就地分泌一種免疫警訊分子 interferon-γ (IFN-γ)，IFN-γ 貼到腫瘤細胞表面的受器上，逼細胞把原本沉默的 MHC 基因重新轉錄出來——等於在戰場上再點一盞燈，讓後續衝進來的 T 細胞更容易接著攻擊。
   問題來了：光靠 anti-Vβ12 染陽性其實還不夠強——Vβ12 家族底下有成千上萬種不同的 T 細胞，anti-Vβ12 只能證明浸潤的細胞「屬於 Vβ12 家族」，卻不能排除病人自己本來就有、剛好也是 Vβ12 家族、但辨識別的東西的 clone 趁 lymphodepletion 空窗自行展開。所以作者對病人 9 於 day 20 切下的腫瘤額外多做一步：把腫瘤裡的 RNA 抽出來，先反轉錄成 DNA 再擴增出 TCR β 鏈的 V(D)J 片段 (RT-PCR)，讀出裡面 CDR3 的分子指紋序列，跟輸注前實驗室裡那支 M1C3 clone 的指紋比對——結果完全對得上，這才把「同家族」升級成「同一條 clone」。另一個內部檢驗來自兩位病人剛好互為對照：病人 9 的腫瘤染出 Vβ12+ 陽性、Vβ7 幾乎陰性，病人 10 反過來只有 Vβ7+ 陽性——這種交叉互斥本身就是 anti-Vβ 抗體專一性的負對照。
4. 工具與材料:
   - **免疫組織化學 (immunohistochemistry, IHC)**: 用一批各自「只認一種蛋白」的抗體去染切片，一眼看出哪些細胞跑進了腫瘤內部。
   - **anti-CD8 / anti-Vβ7 / anti-Vβ12 抗體**: 分別只染殺手型 T 細胞，以及病人 10 與病人 9 主導 clone 的天線款式。
   - **anti-MHC class I / class II 抗體**: 染腫瘤細胞表面「亮出自己內部」的兩種窗口，用來判斷腫瘤有沒有把招牌掛回來。
   - **MHC class I / class II**: 細胞表面向外展示胞內胜肽的窗口；T 細胞的天線靠這個窗口辨識目標，腫瘤常把它關掉來躲藏。
   - **interferon-γ (IFN-γ)**: T 細胞辨識目標後分泌的免疫警訊分子，逼腫瘤細胞把沉默的 MHC 基因重新轉錄、把窗口掛回來（機制詳見 Boehm et al., Annu. Rev. Immunol 1997）。
   - **配對切片 (paired pre/post biopsy)**: 拿同一位病人治療前與治療後的腫瘤配成一對，把個體差異固定住，剩下差異才能歸因於治療。
   - **RT-PCR + CDR3 定序**: 把腫瘤 RNA 反轉錄成 DNA、擴增 TCR β 鏈 V(D)J 片段、讀出 CDR3 序列，把「同 Vβ 家族」升級為「同一條 clone」的分子指紋比對。
5. 與此篇文章的關係:
   在《Cancer Regression and Autoimmunity in Patients After Clonal Repopulation with Antitumor Lymphocytes》這篇文章中，作者為了證明過繼輸入的 T 細胞不只在血液裡繁殖、還真的進到實體腫瘤動手殺癌，採用了 IHC 加上腫瘤 RNA 的 RT-PCR / CDR3 定序。這套組合解決了「怎麼在體內原地確認 clone 身分與活性」的瓶頸：吃進治療前後配對的腫瘤切片與腫瘤 RNA，產出 CD8+ 浸潤、MHC I/II 上調、以及分子指紋等於輸注前 clone 的直接證據，把血液端的 clonal repopulation 資料延伸到腫瘤局部，完成整條追蹤閉環。
