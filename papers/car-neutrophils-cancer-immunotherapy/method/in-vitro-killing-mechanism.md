# 體外抗腫瘤殺傷與殺傷機制解析（突觸／吞噬／ROS／NET／訊號）

1. 引用自哪篇 paper: car-neutrophils-cancer-immunotherapy
2. Outline (任務主線): 體外抗腫瘤殺傷與殺傷機制解析（突觸／吞噬／ROS／NET／訊號）
3. Method:
   確認細胞是真嗜中性球後，接著要量它到底多會殺腦癌 (GBM)、又是怎麼殺的。殺傷力的量法，是把腫瘤細胞和嗜中性球按不同比例混在一起共培 24 小時，再數還剩多少腫瘤活著；這個比例叫效靶比 (effector-to-target ratio, E:T)，本研究用 3:1、5:1、10:1 三檔。共培後以 CD45 抗體區分殺手與腫瘤、Calcein AM 標出活細胞，再用流式細胞術數活腫瘤——結果 CLTX-T-CAR 那組殺得最兇。而在動手殺之前，嗜中性球得先跟腫瘤緊緊貼上、形成一個專門用來動手的接觸面，叫免疫突觸 (immunological synapse)，它的標誌是細胞骨架蛋白 F-actin 大量集中到貼合面（極化）。作者用螢光染 F-actin 數突觸，發現 CLTX-T-CAR 與腫瘤形成的突觸明顯較多，碰到正常細胞時幾乎不形成，說明這種貼合是專一的。
貼上腫瘤後，嗜中性球同時使出三招：直接把腫瘤整顆吞掉（吞噬）、朝腫瘤噴出一團有毒的活性氧 (ROS)、以及吐出由自己 DNA 織成的黏網把腫瘤纏住 (嗜中性球胞外陷阱，NET)。要證明每一招都真的有出力，作者用三種只擋某一招的藥各自關掉來看：Cytochalasin D (CytoD) 擋吞噬、N-乙醯半胱胺酸 (NAC) 清活性氧、propofol 擋 NET（3 µg/mL 以上才明顯）；三種藥都讓殺傷力下降，反過來證明三條路各有貢獻。這裡有個必須小心的地方：CytoD 其實同時擋住吞噬與 NET（兩者都要用到細胞骨架重組），所以它壓下的效果不能全算在吞噬頭上——這正是要另外用只擋 NET 的 propofol 來交叉驗證的原因。相關抑制劑用法參考 Esmann et al. (2010)、Neubert et al. (2018) 與 Meier et al. (2019)。
除了外顯的三招，作者也追進細胞內部，看是哪條訊號線把『認到腫瘤』翻成『動手殺』。他們用西方墨點 (western blot) 比較腫瘤刺激前後訊號蛋白的磷酸化（開機）狀態，發現 CLTX-T-CAR 嗜中性球碰到腦癌後，Syk 與 Erk1/2 兩個訊號蛋白的磷酸化明顯增加，且比 CLTX-NK-CAR 那組更強。這指向一條 Syk-vav1-Erk 路徑：CAR 一黏上腫瘤表面的 MMP2，就沿著這條線接力把『開打』的命令往下傳，驅動吞噬、ROS 與 NET 三招攻擊。整個嗜中性球-腫瘤接合與 Syk 依賴殺傷的框架參考 Matlung et al. (2018)，Erk 介導細胞毒性參考 Li et al. (2018)。
4. 工具與材料:
   - **效靶比 (effector-to-target ratio, E:T)**: 每一顆腫瘤配幾顆殺手細胞的比例，本研究測 3:1、5:1、10:1 三檔。
   - **細胞毒性檢測 (cytotoxicity assay)**: 共培後以 CD45 + Calcein AM 染色、流式數活腫瘤，量化殺傷力。
   - **免疫突觸 (immunological synapse)**: 殺手與腫瘤緊密貼合、以極化 F-actin 為標誌的攻擊接觸面，是殺傷前提。
   - **Cytochalasin D (CytoD)**: 阻斷細胞骨架重組的抑制劑，會同時擋住吞噬與 NET。
   - **NAC (N-乙醯半胱胺酸)**: 抗氧化劑，清除活性氧 (ROS) 以驗證 ROS 途徑的貢獻。
   - **propofol**: 只擋 NET 形成的藥物（3 µg/mL 以上明顯），用於交叉驗證 NET 貢獻。
   - **PicoGreen**: 定量上清中胞外 DNA 的螢光染料，用來量 NET 形成量。
   - **西方墨點與 Syk-Erk 路徑**: 以 p-Syk、p-Erk1/2 的磷酸化量，推斷 CAR 結合 MMP2 後的 Syk-vav1-Erk 訊號活化。
5. 與此篇文章的關係:
   在《Engineering chimeric antigen receptor neutrophils from human pluripotent stem cells for targeted cancer immunotherapy》這篇文章中，作者為了確認 CAR 嗜中性球是怎麼殺死腦癌的，用細胞毒性檢測搭配專一抑制劑與 Syk-Erk 訊號分析做機制解構。這一步解決了「殺傷到底靠哪幾條路」的問題，證明吞噬、ROS 與 NET 三管齊下、並由 Syk-Erk 路徑驅動。它吃進 CAR 嗜中性球與 GBM 細胞，產出一組機制證據，為後續仿生模型與體內實驗鋪路。
