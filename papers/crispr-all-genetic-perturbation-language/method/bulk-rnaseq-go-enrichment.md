# Bulk RNA-seq 與 Gene Ontology 分析

1. 引用自哪篇 paper: crispr-all-genetic-perturbation-language
2. Outline (任務主線): Bulk RNA-seq 與 Gene Ontology 分析
3. Method:
   為了把組合擾動的非線性效應拆開，作者對 ×4 構築（28ζ-OX40-MED12-FAS）與其中每件單做的 ×1 構築（單 OX40 過表達、單 MED12 關掉、單 FAS 調弱）分別跑全轉錄組定序 (bulk RNA-seq)。所有樣本都送上 NovaSeq X Plus，每條 cDNA 兩端各讀 150 個鹼基 (150×150 paired-end)，比只讀一端更能精準對到正確的基因。原始 fastq 灌進 Nextflow 的 nf-core rnaseq pipeline (v24.10.5) 跑完整流程，內部用 salmon 做「不完整比對只算每段 transcript 大概有多少」的偽比對 (pseudo-alignment)——速度比傳統 alignment 快很多，但 isoform 計數同樣準。每個構築都跟同一個對照構築 `28ζ-GFP-NTgRNA-NTshRNA` 比，用 DESeq2 算出顯著差異表達基因清單 (DEG list)，門檻為 |log2 fold change| > 0.25（約 1.19 倍）且 adjusted p-value < 0.01。接著對「至少共享一個擾動」的兩個構築把 DEG 清單兩兩取交集，依交集的 pattern 分群成『base 增殖、代謝、DNA 複製』等模組——看哪些是 ×4 與三個 ×1 都共享、哪些只有某兩件聯手才出現、哪些只在 ×4 才冒出來。

   為什麼這套集合運算能把組合擾動拆成 stacking 與 interference？關鍵在於 DESeq2 算出的 fold change 先經過收縮 (lfcShrink, type='normal') 再篩 DEG。表現量很低的基因，原始 fold change 估計極不穩定——例如對照組只有 3 個 read、實驗組 24 個 read 算出來會像『暴漲 8 倍』，但這只是 read 隨機波動造成的雜訊。fold change 收縮用『全體基因 fold change 的分佈當先驗』把這類極端估計拉回中央，表現量越低、原始估計越極端的基因被拉得越多，高表現且穩定的基因幾乎不變。乾淨的 DEG 清單到手後，集合運算才有意義：(1) 一個基因同時出現在三個 ×1 與 ×4 的交集裡，代表三個擾動各自都動到、合在一起也保留——這就是 stacking 的『base 增殖』模組；(2) 一個基因只出現在『單 OX40 ∩ 單 MED12 ∩ ×4』而不在單 FAS，代表 OX40 與 MED12 兩件聯手才產生的代謝模組；(3) 一個基因在單 FAS、單 OX40 等個別 ×1 構築裡會動（例如『遷移程式』），但在 ×4 中消失，代表它被組合裡的其他擾動蓋過、抵銷掉了——這就是 interference。

   光知道『這群基因被組合動到』還不夠，得替每群基因貼上功能標籤才能解讀。Gene Ontology (GO) 是一個全人類基因的功能字典：每個基因事先被人工標註上一堆功能標籤（『參與 DNA 複製』『參與葡萄糖代謝』『屬於細胞膜』）。作者用 clusterProfiler R 套件 (v4.12.6) 的 enrichGO 對每個 DEG 交集做 GO 富集分析——這個函式拿一份 DEG 清單問：『這份清單裡標 DNA 複製的基因比例，比全基因組隨機抽一份相同大小的清單高很多嗎？』用超幾何檢定算出每個 GO term 的 p 值，再用 p-value cutoff 0.05 篩出顯著的標籤。『DNA 複製模組』『代謝模組』『遷移程式』這幾個名字就是這樣貼上去的。

   對照構築與分析流程的選擇背後都有設計理由。為什麼選 `28ζ-GFP-NTgRNA-NTshRNA` 當對照而不直接拿沒編輯的 T 細胞？因為直接比裸 T 細胞會把 CAR 訊號 (28ζ)、電穿孔 stress response、TRAC 位點被切開的訊號全部捲進 DEG 清單，污染擾動本身的真實效應。作者刻意設計『假擾動』對照——同樣帶 CAR、同樣走 knockin 流程、四個擾動格也填滿，但填的是無作用的占位（GFP 代替過表達基因、scrambled gRNA 代替 knockout、non-targeting shRNA 代替 knockdown），讓 control 與實驗組除了『真正的擾動』之外其他變數完全一致。為什麼不自己手刻分析 pipeline 而用 Nextflow 的 nf-core rnaseq pipeline？因為 bulk RNA-seq 的中段步驟（接頭裁切、註解選用、isoform 累加）每個細節都可能影響下游 DEG 結果，自製腳本容易出隱性 bug；nf-core 用 lockfile 鎖住軟體版本、被大量論文驗證過，等於把這部分外包給成熟流程，作者只需要負責下游 DESeq2、集合運算、GO 富集這幾個關鍵設計。

   這套流程有三個容易壞掉的環節值得注意。其一，DEG cutoff 失衡：太寬（|L2FC| > 0.1、adj P < 0.05）會讓兩萬個基因裡幾千個雜訊被當成 DEG，GO 富集分群失焦；太嚴（|L2FC| > 1、adj P < 0.001）則只剩最強烈的『DNA 複製』模組存活，組合擾動微妙的代謝協同與遷移 interference 全部被砍掉。作者的 |L2FC| > 0.25、adj P < 0.01 是寬到能保留組合效應、嚴到能擋下雜訊的折衷。其二，跳過 lfcShrink：表現量很低的基因會帶著『暴漲 8 倍』這類假 fold change 闖進 DEG 清單；雖然每個構築抓到的假 DEG 身份不同會被交集自動洗掉，但真 DEG 的訊號會被一大堆假 DEG 稀釋，分群時雜訊蓋掉真實的代謝/複製模組。其三，沒有共同對照：如果直接讓 ×4 跟單 OX40 互比，DEG 清單會混入『MED12 與 FAS 帶來的新效應』與『OX40 本身的差異』分不開誰是誰的功勞。把所有構築都對同一個對照算 DEG，每個 DEG 清單才變成『相對於同一個原點的擾動向量』，兩兩取交集才有明確的生物學意義。

4. 工具與材料:
   - **Bulk RNA-seq (全轉錄組定序)**: 把整管細胞的 RNA 全部混在一起萃取、轉成 cDNA、定序，輸出每個基因的平均表現量；訊號乾淨、覆蓋深，適合精確比較兩組之間的差異。
   - **NovaSeq X Plus, 150×150 paired-end**: Illumina 的高通量定序機；每條 cDNA 兩端各讀 150 個鹼基，比只讀一端更能精準對到正確的基因或 isoform。
   - **Nextflow nf-core rnaseq pipeline (v24.10.5)**: 社群維護的標準化 bulk RNA-seq 分析流水線，把 QC、接頭裁切、salmon 偽比對、count matrix 輸出全部串好；用 lockfile 鎖住軟體版本確保再現性 (Zenodo doi 10.5281/zenodo.17153746)。
   - **salmon (pseudo-alignment)**: 不做完整 base-by-base 比對，只用 k-mer 哈希直接估每段 transcript 大概有多少 read；比傳統 alignment 快 10 倍以上但 isoform 計數同樣準。
   - **DESeq2**: 差異表達分析的標準 R 套件；對 read 計數矩陣做負二項回歸，輸出每個基因的 log2 fold change 與 adjusted p-value。
   - **lfcShrink (type='normal')**: 把 DESeq2 算出的 log2 fold change 用『全體基因分佈當先驗』往中央拉，避免低表達基因產生暴漲假象，讓下游集合運算與排序變乾淨。
   - **DEG cutoff: |L2FC| > 0.25, adj P < 0.01**: 本研究用的差異表達基因篩選門檻；|L2FC| > 0.25 約等於至少差 1.19 倍，寬到能保留組合擾動的中等強度效應，p 值卡 0.01 嚴到能擋下雜訊。
   - **DEG list intersection**: 對『至少共享一個擾動』的兩個構築把 DEG 清單兩兩取交集；交集 pattern 對應 stacking（共享基因保留）與 interference（共享基因消失）兩種組合效應。
   - **Gene Ontology (GO) term enrichment**: GO 是全人類基因的功能字典；對一份 DEG 清單用超幾何檢定問『某個功能標籤在這份清單裡的比例是否顯著高於全基因組背景』，把 DEG 翻譯成『DNA 複製、代謝、遷移』等模組名稱。
   - **clusterProfiler::enrichGO (v4.12.6)**: R 中執行 GO 富集分析的標準套件；本研究用 p-value cutoff 0.05 篩出顯著 term。
   - **Control construct: 28ζ-GFP-NTgRNA-NTshRNA**: 『假擾動』對照構築：帶 CAR 訊號 (28ζ) 並走完整 knockin 流程，但四個擾動格都填無作用占位（GFP、scrambled gRNA、non-targeting shRNA），與實驗組共用一切變數除了真正的擾動。
   - **×4 / ×1 構築**: ×4 構築 = 同時做四件擾動（例如 28ζ-OX40-MED12-FAS）；×1 構築 = 四格中只有一格是真擾動、其他填占位（例如單 OX40 過表達）；兩者對同一對照算 DEG 才能做集合運算。

5. 與此篇文章的關係:
   在《A unified genetic perturbation language for human cellular programming》這篇文章中，作者要拆解四件齊發的 CRISPR-All ×4 組合構築（例如 28ζ-OX40-MED12-FAS）相對於個別單一擾動為什麼能多出 8 倍增殖力。為此他們對 ×4 與每個 ×1 構築跑 bulk RNA-seq（用 Nextflow nf-core 流程 + salmon + DESeq2），再對共享擾動的 DEG 清單兩兩取交集、用 clusterProfiler GO 富集替每個交集貼上功能標籤。這套分析直接把組合擾動的非線性效應切成『base 增殖、代謝、DNA 複製』等可解讀模組，並指認哪些單一程式被 interference 抵銷掉——是把行為層級的 ×4 增殖力提升轉譯成機制解釋的關鍵一步。
