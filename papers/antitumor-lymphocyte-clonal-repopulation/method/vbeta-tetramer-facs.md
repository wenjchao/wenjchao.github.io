# TCR Vβ 家族的表型層級偵測

1. 引用自哪篇 paper: antitumor-lymphocyte-clonal-repopulation
2. Outline (任務主線): TCR Vβ 家族的表型層級偵測
3. Method:
      作者要證明「輸注進去的 TIL 真的在病人體內佔滿了淋巴系統」，用的是「螢光細胞分選 (fluorescence-activated cell sorting, FACS)」在蛋白層級直接量比例。每顆 T 細胞表面的辨識天線 (T cell receptor, TCR) β 鏈是由基因庫裡幾十個 V 段版本隨機拼一段當根部序列，等於每根天線出廠就有一個「Vβ 家族編號」(Vβ1、Vβ7、Vβ12、Vβ14…)；同一個 clone 的所有後代共用同一個編號。作者用一組會分別辨認不同 Vβ 家族的螢光抗體 (table S2) 去染輸注前 TIL 與輸注後週邊血淋巴球 (peripheral blood lymphocyte, PBL)，讓每顆細胞經過雷射被記錄綁上哪幾種顏色——一次能數幾萬顆，直接算出「CD8+ 中 Vβ12+ 佔幾成」。除了 Vβ 抗體，作者又加上一種 MART-1 tetramer：把「HLA-A2 展示窗 + MART-1 peptide」這一對抗原複合物做成 4 顆連在一起的螢光探針，當 T 細胞的天線真的認得 MART-1 就會四點抓住並亮起來。
   tetramer 的 peptide 版本作者故意用兩種：病人 9 用「HLA-A2/MART-1: 26-35(27L) altered peptide tetramer」——原生 27-35 跟 HLA-A2 展示窗的結合力天然偏弱、tetramer 訊號不穩，把第 27 位換成 leucine 之後結合力更強、訊號更清楚，多數 MART-1-reactive T 細胞的天線也還認得它。但病人 10 那支 clone 的天線細節不同，只認原生的 27-35，作者就針對他改回用原生型 peptide 做 tetramer——是一個「工具就手 vs. 天線挑剔」的權衡。
   為什麼要兩個讀出並列？Vβ 抗體只看家族編號、不管認什麼抗原；tetramer 只看認不認得 MART-1、不管家族編號。如果只用 Vβ 抗體看到「Vβ12 大量增生」，你其實不知道這批 Vβ12 是不是真的都認得 MART-1；如果只用 tetramer，也不知道它們屬於同一個家族。作者把兩個指標同時量、看落點是否重合——當 CD8+ 中 Vβ12+ 比例和 MART-1-tetramer+ 比例落在同一個數值，就代表這一群大量增生的細胞既屬於同一個家族、又都認得 MART-1——是同一個 clone。時間軸取樣同樣重要：pretreatment 當基線、1 週抓 clonal expansion 峰值、1 個月看 contraction 後的比例、再追到 123–159 天以上證明這不是曇花一現。一條曲線比單一時間點有說服力得多。
   只用單一指標會漏什麼？如果只看 Vβ 抗體，會被「非特異 Vβ 擴增」誤導——某個家族因感染或發炎大量出現時，看起來也像 clonal skew，但那批細胞不認 MART-1。如果只看 tetramer，會被 tetramer 版本卡住——例如作者慣用的 26-35(27L) 改構 tetramer 對病人 10 的 clone 完全不亮，沒有 Vβ7 抗體交叉驗證就會誤判他沒有 MART-1-reactive clone。此外，FACS 讀出「Vβ12+ 佔 CD8+ 的百分比」時，分母如果被 gate 錯（例如把單核細胞或碎片誤當淋巴球），比例會嚴重失真，下游結論全部跟著錯——所以作者要走 lymphocyte gate + CD8 抗體多重限縮，把非目標細胞先剔除。
4. 工具與材料:
   - **FACS (Fluorescence-activated cell sorting)**: 讓每顆細胞經過雷射、以螢光抗體讀出各種表面標記的儀器，一次能數幾萬顆；本實驗量 Vβ% 與 tetramer%。
   - **anti-Vβ antibody panel**: 一組會辨認不同 TCR Vβ 家族編號的螢光抗體 (table S2)，能算出「CD8+ 中某 Vβ 家族佔比」。
   - **HLA-A2/MART-1: 26-35(27L) tetramer**: 改構型 MART-1 四聚體探針，將第 27 位換成 leucine 提升與 HLA-A2 展示窗的結合力，用於病人 9。
   - **Native MART-1: 27-35 tetramer**: 原生型 MART-1 四聚體，用於病人 10（其 clone 只認 native epitope）。
   - **Peripheral blood lymphocyte (PBL) 取樣時序**: pretreatment、輸注後 1 週、~1 個月、123–159 天以上，用以繪出 clonal expansion 至長期持續的曲線。
5. 與此篇文章的關係:
   在《Cancer Regression and Autoimmunity in Patients After Clonal Repopulation with Antitumor Lymphocytes》這篇文章中，作者為了在活體內量化「輸注進去的 T 細胞是不是真的把病人淋巴系統重建了」，採用了 anti-Vβ 抗體 panel 與 MART-1 tetramer 雙讀出的 FACS。這一步解決了單一指標可能被非特異 Vβ 擴增或 tetramer 交叉反應誤導的瓶頸，它吃進不同時間點的病人 PBL 與輸注前 TIL 樣本，產出「Vβ% 與 tetramer% 隨時間變化」的曲線，直接支撐 clonal repopulation 的核心主張，供下游與 CDR3 定序、IHC 交叉比對。
