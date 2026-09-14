# TCR β 鏈 V(D)J / CDR3 核酸定序作為 clonotype tracking

1. 引用自哪篇 paper: antitumor-lymphocyte-clonal-repopulation
2. Outline (任務主線): TCR β 鏈 V(D)J / CDR3 核酸定序作為 clonotype tracking
3. Method:
      T 細胞表面用來認目標的天線 β 鏈是這樣做出來的：染色體上有一堆 V、D、J 段基因片段，細胞成熟時隨機挑一段 V、一段 D、一段 J 拼在一起 (V(D)J recombination)，中間接點又會被酵素隨機加或減幾個鹼基。這樣拼出來的中間段——互補決定區 3 (complementarity-determining region 3, CDR3)——理論多樣性可以到 $10^{15}$ 到 $10^{18}$ 種以上，比人體所有 T 細胞的總數還多很多，任意兩個不同來源的 T 細胞產生一模一樣 CDR3 的機率極低。同一個 T 細胞分裂出來的所有後代 (clone) 則共用完全一樣的 CDR3，於是這段序列就成為 clone 出廠時被燒上的獨一無二分子指紋。呼應這件事，作者發現兩位病人的 MART-1 反應 clone 的 CDR3 在抗原結合區沒有序列相似性——同抗原、不同 TCR，是兩位病人各自從自己 repertoire 裡獨立解出的答案。
   拿到指紋的操作分兩層。第一層是「先建參考」：作者從輸注前的 TIL 用極限稀釋——把細胞稀釋到每個孔平均只有一顆——長出單一 T 細胞後代組成的純株，病人 9 那一株叫 M1C3（Vβ12+）、病人 10 那一株叫 S1A5（Vβ7+），並用 cytokine secretion assay 驗證這兩株純株就是能認 MART-1: 27-35 的 clone。接著從純株抽 DNA，用 β 鏈 V(D)J 專一引子放大出含 CDR3 的片段，把 PCR 產物切進質體、讓每個菌落只帶一條 DNA (DNA cloning)，再送 Sanger 定序，得到那條 clone 的 CDR3 核酸與翻譯出來的胺基酸序列（Fig 1D）——這就是後續要拿去比對的「參考指紋」。
   第二層是「六條抽樣」：作者對輸注前 TIL 與治療後 PBL 各取六個獨立 DNA cloning 事件分別去定序 (six-clone sampling)，看看六條序列是否幾乎都是同一條 CDR3。如果樣本裡是很多不同 clone 的混合，六條讀出來應該五花八門；六條全部落在同一條 CDR3、且與 M1C3 / S1A5 的參考指紋一致——這才敢宣稱是「單一 clone 大爆量」。單抽一兩條就算讀到同一條也可能只是巧合；假設樣本裡有一半其實是別的 clone，六條全部撞到主導 clone 的機率只有 $(1/2)^6 \approx 1.6\%$。在 Sanger 定序時代，這個樣本量已經足夠拒絕「多 clone 混合」這個對立假設。
   為什麼在 anti-Vβ 抗體與 Vβ 全家族 RT-PCR 之上還要多做這一層？因為 Vβ 讀數只到「家族層級」——Vβ12 家族底下可以有成千上萬條不同 T 細胞，anti-Vβ 抗體只能宣稱「這位病人現在體內 Vβ12 家族被偏斜到佔 CD8+ 六成」，卻沒辦法排除這 60% 是好幾條不同 Vβ12 clone 一起長出來的可能。加上 CDR3 定序，才能把「同家族」升級到「同一條 clone」；而「clonal repopulation」這個論述的重點就在 clonal，跳過 CDR3 這一環，論文的核心立論會被拆掉一半。搭配 CDR3 資料還讓作者得以量化估計 in vivo 擴增規模——病人 9 循環中 Vβ12+ MART-1-reactive 細胞從輸注時的 $1.2 \times 10^{10}$ 擴增到 $>5.0 \times 10^{10}$、病人 10 則從 $9.5 \times 10^{10}$ 擴增到 $>5.6 \times 10^{10}$——這是「同一支 clone 大量分裂」而非「多支 clone 疊加」的直接證據。
4. 工具與材料:
   - **CDR3 (complementarity-determining region 3)**: V(D)J 拼接與接點隨機加減鹼基所形成的中間段序列；理論多樣性 $10^{15}$–$10^{18}$，是 clone 出廠時被燒上的獨一無二分子指紋。
   - **V(D)J recombination**: T 細胞成熟時把 V、D、J 三段基因片段隨機拼在一起、接點隨機加減鹼基，生成獨一無二天線的過程。
   - **M1C3 / S1A5 (limiting-dilution T cell clone)**: 作者從病人 9 (Vβ12+) 與病人 10 (Vβ7+) 輸注前 TIL 以極限稀釋建立、經 cytokine assay 驗過認 MART-1: 27-35 的兩株單一 T cell clone。
   - **DNA cloning + Sanger 定序**: 把 PCR 產物切進質體讓每個菌落只帶一條 DNA、再送定序，讀出參考 CDR3 核酸與胺基酸序列（Fig 1D）。
   - **六條抽樣 (six-clone sampling)**: 對輸注 TIL 與治療後 PBL 各取六個獨立 DNA cloning 事件分別定序；若六條都落在同一 CDR3，可拒絕「多 clone 混合」假設。
   - **極限稀釋 (limiting dilution)**: 把細胞稀釋到每個孔平均只有一顆，讓長出的每個純株只源自單一 T 細胞後代，是取得 M1C3 / S1A5 的方法。
5. 與此篇文章的關係:
   在《Cancer Regression and Autoimmunity in Patients After Clonal Repopulation with Antitumor Lymphocytes》這篇文章中，作者要證明的核心是「clonal repopulation」——同一支輸入的 clone 在體內主導了淋巴系統。單靠 anti-Vβ 抗體與 Vβ 全家族 RT-PCR 只能看到家族層級，於是作者採用了 TCR β 鏈 V(D)J / CDR3 核酸定序：吃進 M1C3 / S1A5 純株、輸注前 TIL 與治療後 PBL 的 DNA，產出「輸注前實驗室 clone」與「治療後血液主導 clone」共用同一條 CDR3 分子指紋的證據，把家族層級的偏斜升級為單一 clone 的持續存在。
