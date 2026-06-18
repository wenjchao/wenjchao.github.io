# RT-qPCR 相對量化 (2^-ΔΔCt 法)

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): RT-qPCR 相對量化 (2^-ΔΔCt 法)
3. Method: 
   RT-qPCR 是把「mRNA 多寡」轉成可量化數字的兩段式流程。第一段：mRNA 本身是 RNA 不能直接被 PCR 放大，所以先用反轉錄酵素 (reverse transcriptase) 把它抄成 DNA 版本 (cDNA)，這一步稱 reverse transcription (RT)。第二段：即時定量 PCR (quantitative PCR, qPCR) 把 cDNA 一輪一輪複製，每輪加一種會嵌進雙股 DNA 才會亮的染料 (SYBR Green)——染料在水溶液中幾乎不發光，但一夾進雙股 DNA 中間螢光跳升好幾百倍。每多一輪 DNA 量翻倍、螢光也翻倍，儀器在每輪結束讀一次螢光，記錄「累積到偵測閾值需要幾輪」這個數字，稱 cycle threshold (Ct)。Ct 越小，代表起跑線上的 mRNA 越多。

   把 Ct 換算成可比較的「倍率」要走兩次相減。第一次 ΔCt = Ct(GAPDH) − Ct(β-actin)：同一管內把目標基因 Ct 減掉內參基因 Ct——如果這管 RNA 加得比較多，兩個 Ct 都會往左偏、相減就把樣品量差異抵消掉。第二次 ΔΔCt = ΔCt(處理組) − ΔCt(control)：再跟沒處理的對照樣本相減一次，把基準歸零。最後套 $2^{-\Delta\Delta C_t}$——因為 PCR 在理想狀況下每輪 DNA 量翻倍、N 輪後產量正比於 $2^N$，Ct 差 1 代表起跑量差 2 倍，這個指數關係剛好可以把 Ct 的對數差還原成倍率。結果 = 1 代表跟對照一樣、< 1 代表被打下去 (knockdown)、> 1 代表被推高。

   為什麼挑 β-actin 當內參、而不是用 GAPDH 自己當基準？問題出在 GAPDH 在這篇研究本身就是被打的目標——它的 mRNA 量本來就會在實驗組下降。如果用它當尺，所有變化會被它自己的下降抵消、看起來像 miRNA 完全沒效果（ΔCt 永遠等於 0）。所以作者改用另一個在各種細胞與處理下表現量都很穩定的 housekeeping gene β-actin 當內參，「打誰就不能用誰當尺」這條紀律才不會被破壞。另外，作者最後報的是「相對於 control 的倍率」(fold-change over control)，而不是絕對 mRNA 拷貝數——因為 qPCR 直接給出的 Ct 會隨樣品量、機器、試劑批號浮動，用 fold-change 才能跨樣品、跨實驗直接比較。

   反轉錄 (RT) 這一步若效率很差，所有基因的 cDNA 起跑量都偏低、Ct 整體往右偏；但只要 RT 對 GAPDH 與 β-actin 的偏好相同，第一次相減 (ΔCt) 仍能把整體偏低抵消掉。真正會壞的情境是「RT 對不同基因偏好不同」：若它對 GAPDH 特別沒效率而對 β-actin 正常，ΔCt 就會被引入假訊號。本文用商業化試劑 (QuantiTect Reverse Transcription Kit) 就是要確保 RT 對各基因偏好接近一致。
4. 工具與材料: 
   - **Reverse transcription (RT)**: 用反轉錄酵素把 mRNA 抄成它的 DNA 版本 (cDNA)，讓後續 PCR 能處理。
   - **quantitative PCR (qPCR)**: 每輪 PCR 即時讀螢光的版本，可同時放大 DNA 與記錄累積曲線。
   - **SYBR Green**: 一種雙股 DNA 嵌入式螢光染料，游離時幾乎不發光、嵌進雙股 DNA 後螢光跳升好幾百倍。
   - **Cycle threshold (Ct)**: qPCR 累積到偵測閾值需要的循環數；Ct 越小代表起跑線上的 mRNA 越多。
   - **$2^{-\Delta\Delta C_t}$ 法**: 兩次相減把樣品量差異與基準歸零，再用 PCR 每輪翻倍的指數關係 ($2^N$) 把 Ct 對數差還原成相對倍率。
   - **β-actin (endogenous control)**: 本研究選用的內參基因，因為它在各種細胞與處理下表現穩定、且不是被 knockdown 的目標 GAPDH。
   - **QuantiTect Reverse Transcription Kit**: Qiagen 商業化 RT 試劑，用於把總 RNA 反轉錄成 cDNA、確保各基因 RT 效率接近一致。
   - **Rotor-Gene SYBR Green PCR Kit**: Qiagen 商業化 SYBR Green qPCR 試劑，本文用來在 Rotor-Gene 儀器上做即時定量。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了證明 miRNA 真的被遞送進細胞質並關掉目標基因，採用了 RT-qPCR 的 $2^{-\Delta\Delta C_t}$ 相對量化法。它解決了「Ct 數字本身會隨儀器與樣品漂移、不能直接拿來比」的瓶頸：吃進各組細胞萃取的 total RNA，產出 fold-change over control 的相對倍率（如 CFs 中 GAPDH 被打到 ~0.3），讓 hELs 的靶向性與 GelMA 不阻擋遞送這兩個關鍵結論有可比較的數字基礎。
