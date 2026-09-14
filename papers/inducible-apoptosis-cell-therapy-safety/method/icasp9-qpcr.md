# iCasp9 轉基因即時定量 PCR（Real-time qPCR）

1. 引用自哪篇 paper: inducible-apoptosis-cell-therapy-safety
2. Outline (任務主線): iCasp9 轉基因即時定量 PCR（Real-time qPCR）
3. Method:
      每個時點作者取 1×10⁶ 個 PBMC 萃 DNA，跑即時定量聚合酶鏈鎖反應 (real-time qPCR) 量 iCasp9 拷貝數。一般 PCR 是跑完 30-40 圈才看結果；qPCR 則是每一圈都拍一張螢光照片，起始模板越多、就越早跨過亮度閾值，這個「第幾圈跨閾值」叫閾值循環 (Ct)。PCR 每圈理想把目標 DNA 翻倍，所以 $N_0 \propto 2^{-\mathrm{Ct}}$——Ct 差一圈就對應起始量差一倍，這正是 qPCR 靈敏度的來源。作者事先用已知拷貝數的 iCasp9 質體跑一系列稀釋建出換算尺 (standard curve)，把病人樣本的 Ct 對到這條尺，就知道這管有多少份 iCasp9 DNA。單位選 copies/µg DNA 而非 copies/顆細胞，是因為 DNA 萃取回收率會跨批次浮動、而每 µg 基因組 DNA 對應的細胞數相對穩定，這樣不同時點才能公平比較 (Fig. 2B、Fig. 4B)。
   流式數的是「表面上還掛著 CD19 的細胞顆數」，qPCR 數的則是「基因組裡還帶著 iCasp9 序列的 DNA 拷貝數」。兩條讀出在極端情形下會分家：AP1903 觸發凋亡的當下，細胞膜破了、CD19 掉了，流式馬上就數不到，但 DNA 可能還沒被清除，qPCR 仍抓得到；反過來，濃度低到流式已進入雜訊區時，qPCR 靠指數放大仍能量到，本研究的可信下限低到 3 copies (Fig. 4B)。這條下限不是隨便定的：反應體積裡若只剩 1-2 份模板，Ct 變異會很大，甚至偶爾因為引子二聚或環境 DNA 污染出現假訊號，所以強制「至少能重複讀到 3 拷貝」才算可信，把 noise 排除在 rescue 效率評估之外。實測上 rescue 後 24 小時 qPCR 較基準值下降約 2 log (100 倍)，比 FACS 觀察到的 0.5 log 更敏感——這個「清除仍在持續」的訊號，正是靠 qPCR 才看得到。
4. 工具與材料:
   - **real-time qPCR**: 每一圈 PCR 都即時偵測螢光的定量 PCR，比一般 PCR 多了拷貝數量測能力。
   - **Ct (threshold cycle)**: 螢光累積剛好跨過閾值的圈數；Ct 越小代表起始 iCasp9 DNA 越多。
   - **Standard curve**: 用已知拷貝數的 iCasp9 質體稀釋跑出的 Ct-拷貝數換算尺，把 Ct 轉成絕對拷貝數。
   - **copies/µg DNA**: 本研究的定量單位，用 DNA 質量而非細胞數做分母以吸收萃取效率波動。
   - **Limit of detection (3 copies)**: qPCR 能可靠讀到的最低起始拷貝；低於此值視為 noise，不計入 rescue 效率評估。
   - **PBMC DNA extraction (1×10⁶ 細胞)**: 每時點的 DNA 輸入量，用於保證每次反應起始細胞數一致。
5. 與此篇文章的關係:
   在《Inducible Apoptosis as a Safety Switch for Adoptive Cell Therapy》這篇文章中，作者為了佐證 AP1903 誘導的 iCasp9-T 細胞清除是真正的凋亡而非暫時離開血液，採用了 iCasp9 轉基因即時定量 PCR。它以每時點 1×10⁶ 個 PBMC 的 DNA 為輸入，直接量基因組上還有多少份 iCasp9 拷貝，補上 FACS 只讀表面 CD19 的死角，並提供比流式靈敏一個量級的殘餘偵測 (下限 3 copies)，讓 30 分鐘 >90%、24 小時再降 2 log 的 rescue 動力學能被兩軌獨立佐證。
