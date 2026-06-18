# miRNA 的 EV 內部裝載與游離 miRNA 移除

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): miRNA 的 EV 內部裝載與游離 miRNA 移除
3. Method: 
   作者用 passive loading 把 miRNA 裝進奈米囊泡 (NVs)。相對於「主動裝載」要用電穿孔或化學試劑在成形囊泡上打洞 (效率高但會破壞 EV 表面蛋白)，passive loading 直接把 miRNA 在融合的兩段式流程中一起加進來：100 nM miRNA 跟 100 µg ml⁻¹ 的 EVs/lecithin 一起在 37 °C 共培育 12 h、再 probe-sonication 4 min；當 sonication 把膜撕成碎片、碎片在 5 秒 off-pulse 重新捲合的瞬間，附近的 miRNA 會被自然包進肚子。優點：完全不用打洞、EV 表面 CD9/CD63/CD81 等靶向標誌完整保住——這對下游「hELs 必須保留 EV 靶向能力」的核心命題是不可妥協的前提；代價是封包效率略低 (約 63–76%)，但這個取捨值得。

   作者用了兩種商業 miRNA mimic (Horizon Discovery 的 miRIDIAN 系列) 來扮演不同角色。miRNA-DY547 是「螢光示蹤版」——序列沒有特定靶基因，重點是接了 DY547 紅色染料，方便用螢光顯微鏡看 miRNA 在細胞裡的位置、用 plate reader 量它的濃度算封包效率。miRNA GAPDH 是「功能性版」——序列剛好對到 GAPDH 基因 3′-UTR、能把這個管家基因關小聲，用來測「miRNA 真的進到細胞質有沒有產生功能效果」的讀數。一個追蹤位置與濃度、一個讀功能，互補配對。

   Loading 完之後必須把外面的「游離 miRNA」徹底撈乾淨，作者用兩道步驟。第一道：Amicon Ultra-0.5 ml 10 kDa MWCO 過濾管 (MilliporeSigma) 離心——MWCO (molecular weight cut-off) 是膜孔指標，10 kDa 表示 < 10 kDa 的水、鹽、緩衝液可以穿過去進到下方，> 10 kDa 的 NV (~10⁷ Da) 留在上方。這道主要是「快速濃縮 NV + 清掉小分子雜質」。第二道：100 000 × g × 70 min × 4 °C 的超高速離心——把 NV (連同肚子裡的 miRNA) 沉到管底成 pellet，游離 miRNA 因為水溶性高、密度不夠，仍留在 supernatant；4 °C 是為了避免長時間離心讓 miRNA 被 RNase 降解。「100 000 × g × 70 min × 4 °C」是 EV 領域跑了幾十年累積的標準參數。注意：作者主流程刻意避開 UC 分離 EV (Module 2 用 ATPS 取代)，但這裡只是「分離已包好的 NV vs 游離 miRNA」、不是初步分離 EV，UC 的膜傷害在這個用途下可以接受。

   拿到分離後的 supernatant 之後，封包效率 (Encapsulation Efficiency, EE) 公式是 $\text{EE (\%)} = \left( 1 - \dfrac{\text{free}}{\text{loaded}} \right) \times 100$。「loaded」是一開始加進去的 miRNA 總量 (100 nM)；「free」是 supernatant 裡漂浮的游離 miRNA，用 DY547 螢光在 Ex/Em 525/570 nm 對 DY547 標準曲線換算。為什麼用扣除法而不是直接量「包進去的」？因為直接量必須先用界面活性劑破囊，但破囊會稀釋樣品、染料還可能在破囊瞬間被淬熄，訊號嚴重低估。扣除法穩定可靠，實測：Lip EE = 63% ± 2.21%、hELs = 65% ± 2.18%、EVs = 76% ± 3.12%——EV 比 Lip 高的原因是 Lip 表面負電強 (zeta = −35.67 mV)、跟同樣帶負電的 miRNA 排斥較強；EV 表面負電弱 (zeta = −5.6 mV)、排斥較小、包得多。失敗模式提醒：如果跳過兩道清洗、直接量總 miRNA 訊號，分子裡 + 分子外的訊號會混在一起、EE 看起來接近 100%，但實際遞送量遠低於報告值，量化體系直接崩潰。
4. 工具與材料: 
   - **Passive loading**: 在膜融合的兩段式流程中讓 miRNA 跟著被碎片捲入囊泡的裝載法；不打洞、保住 EV 表面蛋白。
   - **miRNA-DY547 (miRIDIAN mimic, Horizon Discovery)**: 螢光示蹤用 miRNA mimic；接 DY547 紅色染料，用於量封包效率與細胞內定位。
   - **miRNA GAPDH (miRIDIAN Housekeeping Positive Control #2)**: 功能性 miRNA mimic；序列對到 GAPDH 3′-UTR，用於測 knockdown 效果。
   - **Amicon Ultra-0.5 ml 10 kDa MWCO**: 離心過濾管；MWCO 10 kDa 表示 < 10 kDa 小分子穿過、NV 留上方，用於濃縮 NV 與清除小雜質。
   - **MWCO (molecular weight cut-off)**: 過濾膜的分子量門檻，大於 cut-off 留下、小於通過。
   - **Ultracentrifugation (100 000 × g × 70 min × 4 °C)**: EV 領域標準離心參數；把 NV 沉到 pellet、游離 miRNA 留 supernatant。
   - **DY547 標準曲線 (Ex/Em 525/570 nm)**: 用 DY547 染料螢光建立濃度-強度線性關係，把光訊號換成 miRNA 濃度。
   - **Encapsulation Efficiency (EE)**: 封包效率公式 $\text{EE} = (1 - \text{free}/\text{loaded}) \times 100$；扣除法避免破囊低估。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了把 miRNA 這個基因調控指令穩定地裝進已融合好的 hELs，採用了 passive loading + 兩道清洗 + DY547 螢光定量這套流程。它解決的是「主動裝載會破壞 EV 表面靶向蛋白」與「未清洗的游離 miRNA 會污染 EE 計算」兩個瓶頸，產出有可靠 EE 數字 (Lip 63%、hELs 65%、EVs 76%) 的 miRNA-laden NVs，作為下游細胞攝取、GAPDH knockdown 與 GelMA 嵌入實驗的核心輸入材料。
