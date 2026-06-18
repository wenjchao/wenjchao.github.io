# BLESS 全基因組 DSB 標記與定序

1. 引用自哪篇 paper: rationally-engineered-cas9-nucleases
2. Outline (任務主線): 對 WT、SpCas9(K855A)、eSpCas9(1.1) 在 EMX1(1) 與 VEGFA(1) sgRNA 下產生的 DSB 進行不偏（unbiased）全基因組剖析，確認 specificity 提升不是只在已知 off-target 成立。
3. Method:

在驗證新版 Cas9 時，作者要回答一個關鍵問題：脫靶是否真的在全基因組層面減少了，而不是只在預先猜到的幾個位置變乾淨？前一節 (§2-D) 的 targeted deep sequencing 只能去看「事先猜會脫靶」的位置上修補後留下的小錯字 (indel)，預想之外的看不到。BLESS（全基因組雙股斷裂定位法；protocol 來自 Crosetto et al. 2013 Nat. Methods 10:361，Cas9 應用版沿用 Ran et al. 2015 Nature 520:186）反過來：直接列出整個基因組「DNA 雙股同時被剪斷的傷口 (DSB)」的座標，不預設位置。作者只挑三條 Cas9 進這場全基因組考試：原版 WT、單點突變 SpCas9(K855A)、三點組合的 eSpCas9(1.1)；每條 Cas9 各搭配兩條已知會大量脫靶的 sgRNA——EMX1(1) 與 VEGFA(1)，合計 6 組樣本。所有樣本都在轉染後 24 小時收細胞，比前一節 (~72 小時) 早得多，因為 BLESS 抓的是「斷口正在張開的當下」：細胞一旦把 DSB 修補回去，斷口閉合，接頭就再也黏不上去了。

BLESS 的核心動作是「在每個 DSB 斷口貼生物素標籤，再用磁珠把貼了標籤的片段一網打盡」。每組投入 10 × 10⁶ 顆 HEK293FT 細胞，因為每顆核裡 Cas9 切出來的 DSB 其實只有幾十處，起始細胞夠多訊號才浮得出背景。作者把細胞固定、把細胞核挑出來打洞 (permeabilization)，用 Proteinase K 在 37 °C 處理 4 分鐘咬掉斷口上的殘留蛋白，再立刻加 PMSF 把 Proteinase K 關掉——這兩步必須一氣呵成，否則殘留的 Proteinase K 會把後續要加的 DNA ligase 與接頭一起消化掉。接著加 200 mM 的「近端接頭 (proximal linker)」過夜 ligation：這是一段事先退火好的雙股小 DNA，一端帶生物素 (biotin)，另一端的形狀剛好能跟 DSB 暴露的斷口接上。標記完再做一次 Proteinase K 消化，先用 26G 細針物理擠壓做粗剪切，再用 BioRuptor 超音波打 20 分鐘（high 強度、50% duty cycle）把染色質碎成幾百個鹼基的均勻短片段。取 20 µg 碎片（streptavidin 磁珠的捕捉飽和量），用 streptavidin beads 把所有帶生物素的片段抓住——biotin 與 streptavidin 之間是自然界最強的非共價結合之一，再怎麼沖洗都掉不下來，沒貼標籤的背景片段就在這一步被沖走。最後在磁珠上把片段另一端再接上「遠端接頭 (distal linker)」200 mM 過夜 ligation，這樣每段片段兩端就都有可以擴增的 handle。

這兩段接頭其實都被設計成髮夾 (hairpin) 形狀：兩端先彎進來自我配對、外露的只剩會跟 DSB 接合的那一側，避免接頭之間在 ligation 時自己頭尾相黏成糊。但定序時又需要兩端都是線性可擴增末端，作者就在每個髮夾的彎處塞進一段 I-SceI 的 18 個鹼基辨識位——I-SceI 是來自酵母粒線體的稀有切位酶，在整個人類基因組裡幾乎找不到自然辨識位，所以在 37 °C 切 4 小時時只會切掉接頭髮夾、不會誤切細胞 DNA。一打開後片段兩端就變成可以 PCR 的末端，跑 18 個循環的 PCR 富集。這個循環數刻意壓低有兩個原因。第一，PCR 是指數放大，每多跑一輪就把「同一條原始片段被重複擴增」的偏差也指數放大，後續會被當成獨立 DSB cluster 變成假陽性。第二，循環太多還會讓不同片段在退火時黏成嵌合 read 污染下游的 DSB-score 演算法。18 是「擴增到上機門檻、又還沒被指數誤差污染」的安全上限。擴增完用 Illumina TruSeq Nano LT Kit 建庫上機定序。

為了把 Cas9 造成的 DSB 從「轉染本身就會冒出來的背景傷口」分開，每一輪 BLESS 都同時跑一個陰性對照：用相同的 Lipofectamine 2000 + 空白質體 pUC19 假轉染 (mock transfection) 平行走完整套流程。陰性對照如果只是「完全不轉染」，就無法扣掉脂質轉染試劑與外源 DNA 進細胞造成的應激背景；用 pUC19 補上這個變因，BLESS 看到的訊號才能歸因到 Cas9。整套流程裡幾個工程細節都有窄窗：Proteinase K 4 分鐘 + PMSF 滅活必須緊接著，否則酵素會繼續消化掉下一步要加的接頭與 ligase；超音波 20 分鐘剪切若太短會讓片段太長、磁珠連同周圍 DNA 一起捕捉，定位失準，若打太久太強會把帶生物素的那段直接打掉、磁珠空手而歸。這幾個參數合起來定義了 BLESS 訊號的可信度邊界。

4. 工具與材料:

   - **BLESS**: 全基因組雙股斷裂定位法。在固定後的細胞核裡把生物素接頭直接黏到每個 DSB 斷口，再用 streptavidin 磁珠富集、定序，得到全基因組所有 DSB 的座標。protocol 來自 Crosetto et al. 2013 Nat. Methods 10:361；Cas9 應用版沿用 Ran et al. 2015 Nature 520:186。
   - **DSB (double-strand break)**: DNA 兩條互補股在同一個位置同時被剪斷的傷口，是 Cas9 動刀當下留下的原始訊號，比下游 indel 早一步。
   - **unbiased genome-wide profiling**: 不預設「哪裡會脫靶」的全基因組掃描，能撈到事先沒想到的脫靶位點，與 targeted deep sequencing 互補。
   - **HEK293FT**: BLESS 實驗使用的人類細胞株。每組投入 10 × 10⁶ 顆細胞，以彌補每顆核裡 DSB 數量稀少導致的訊號雜訊比問題。
   - **24 h 收樣**: BLESS 在轉染後 24 小時就收細胞（比 §2-D 的 ~72 小時早得多），目的是趁多數 DSB 還沒被細胞修補閉合時就把斷口固定下來。
   - **Proteinase K + PMSF**: 在 37 °C 4 分鐘 Proteinase K 咬掉 DSB 附近的殘留蛋白後，立刻用 PMSF 把酵素關掉，避免它繼續消化後續要加的接頭與 ligase。
   - **proximal linker (biotin)**: 事先退火好的雙股短 DNA 接頭，一端帶生物素，能黏到 DSB 暴露的斷口。作者用 200 mM 高濃度、過夜 ligation，確保每個傷口都至少貼到一張標籤。
   - **26G needle + BioRuptor**: 兩段剪切策略：26G 細針物理擠壓做粗剪，BioRuptor 超音波 20 分鐘（high、50% duty cycle）把染色質打成均勻幾百 bp 片段，剪切窗口太短或太強都會失敗。
   - **streptavidin beads**: 表面塗有 streptavidin 蛋白的磁珠。streptavidin 與生物素間是自然界最強的非共價結合之一，沖洗時不易脫落，能把帶生物素的片段一網打盡。本實驗取 20 µg 染色質為捕捉飽和量。
   - **distal linker**: 在磁珠上接到片段另一端的第二段接頭，200 mM 過夜 ligation，讓每段片段兩端都有可以 PCR 擴增的 handle。
   - **hairpin linker + I-SceI**: 接頭設計成髮夾形狀避免自我相連；髮夾彎處嵌入 I-SceI 的 18 bp 罕見辨識位，最後 37 °C 切 4 小時打開髮夾，由於該辨識位在人類基因組幾乎不存在，不會誤切細胞 DNA。
   - **18 cycles PCR**: 刻意壓低的擴增循環數。多跑會放大 PCR duplicate 與嵌合 read，造成假陽性 cluster 污染 DSB-score；18 是「擴增到上機門檻、又還沒被指數誤差污染」的安全上限。
   - **TruSeq Nano LT Kit**: Illumina 建庫試劑套組，把 PCR 富集後的片段轉成可上機定序的 library。
   - **mock transfection (Lipofectamine 2000 + pUC19)**: 陰性對照組。用相同脂質轉染試劑送入無關空白質體 pUC19，平行跑完整 BLESS 流程，扣掉轉染本身造成的背景 DSB 訊號，分離出真正歸因於 Cas9 的訊號。

5. 與此篇文章的關係:

在《Rationally engineered Cas9 nucleases with improved specificity》這篇文章中，作者想解決前一階段 targeted deep sequencing 只能偵測「已知可能脫靶位置」的侷限。為了排除新版 eSpCas9 可能在基因組其他未知區域產生新脫靶位點的假陰性風險，作者採用了不偏（unbiased）的全基因組 BLESS 技術。BLESS 能直接標記細胞內剛產生的 DNA 雙股斷裂 (DSB) 並掃描整個基因組的切割狀況，為後續演算法過濾與再次 targeted sequencing 驗證提供基礎地圖，從而有力地證明新設計在全基因組層面減少 off-target 的安全性。
