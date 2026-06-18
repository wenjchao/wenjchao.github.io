# Cre 介導定點 cassette exchange 與 FACS 富集

1. 引用自哪篇 paper: chromatin-structure-regulatory-activity
2. Outline (任務主線): Cre 介導定點 cassette exchange 與 FACS 富集
3. Method: 
   Cre 介導 cassette exchange 的任務是「用 Cre 這把精準鑰匙把 transfer vector library 一次塞進池化的 landing pad 細胞，再用 FACS 反向挑出真正換成功的細胞」。流程分四步：(1) 把 8 株不同位置的 landing pad 細胞混成一管 1.2 × 10⁶ K562 細胞（池化, pooled）——一次電穿同時處理 8 個位置。(2) 用 Neon Transfection System 電穿 (electroporation) 把 4 µg transfer vector library 加上 1 µg pBS185 CMV-Cre 質體 (Addgene 11916) 一起打進細胞；電穿利用瞬間高壓電在細胞膜上打開暫時的孔，讓質體擠進去。Cre 重組酶 (Cre recombinase) 來自 P1 噬菌體，認得 34 bp lox 序列，會把染色體 cassette 上的 `Hyg/TK-P2A-eGFP` 整段切掉、把 transfer vector 上的 `CRS-Hsp68-dsRed(cBC)` 同方向接回去；loxFAS 配 loxFAS、loxP 配 loxP，置換鎖死在唯一方向。(3) 培養 1 週讓細胞慢慢把舊 eGFP 蛋白透過稀釋與降解清掉——Cre 在 DNA 層面換掉 eGFP 那一刻，已表現的 eGFP 蛋白半衰期超過一天，需要時間衰退。(4) 用 FACS 反向挑「GFP 變暗」的細胞——以未電 Cre 的對照組 landing pad 細胞 GFP 強度分布的下尾 28% 為閾值，置換成功者落在此閾值以下。

   為什麼閾值是 GFP 下尾 28% 而不是 5% 或 50%？閾值是以「沒電 Cre」的對照組 landing pad 細胞自然 GFP 分布為基準——即使全部都有 eGFP，每顆螢光強度仍有自然波動，把對照組最暗的 28% 定為閾值。挑 5% 太嚴會擋掉很多成功者；挑 50% 太寬會把對照組細胞也收進來。實際置換後 40% 細胞落在此閾值下；扣掉對照組自然落入的 28%，多出的 12% 即真正成功置換的細胞——對應到 Cre-lox 整體置換效率約 12%，FACS gating 提供 $30\% / 12\% \approx 2.5$ 倍富集。

   為什麼要把 8 株 landing pad 細胞池化在同一管電穿，而不是一株一株做？因為分開做的話，試劑批次、Cre 效率、電穿狀態的微小差異會在「位置之間」造成系統性偏差——量到的「位置 A 比位置 B 響」可能只是 A 那管 Cre 比較好。池化策略 (pooling) 讓 8 個位置共享同一批 Cre、同一批 library、同一次電穿，位置間差異只能歸因於位置本身。樣本量也不是隨意挑的——作者要的覆蓋是「8 LP × 300 CRS × 平均 10 個獨立 barcode integrations」≈ 2.4 × 10⁴ 個組合都有細胞代表。考量 Cre 置換效率 12% 與 FACS 富集 recovery 後倒推，需要輸入 0.9 × 10⁶ 細胞；實際電穿打 1.2 × 10⁶ 留下安全餘裕。這個數字是先算好目標再回推輸入量的工程結果。

   兩個步驟若省掉，整個富集會壞在哪？(1) 如果跳過 FACS 直接用「電完 Cre」的細胞群跑下游條碼定序：Cre 整體置換效率只有 12%，88% 細胞其實沒換成功，仍帶原 cassette、沒有 dsRed mRNA 在表現；但電進細胞的 transfer vector 飄質體還在細胞核裡，gDNA 抽出來時 cBC 仍會被讀到，造成 DNA reads 嚴重稀釋而 RNA 訊號被淹沒，replicate R 跌、結論做不出來。FACS 反向挑 GFP 變暗剛好把訊號集中在那成功的 12%。(2) 如果電穿完馬上 FACS、沒等 1 週讓 GFP 衰退：已表現的 eGFP 蛋白半衰期超過一天，置換成功與未置換看起來一樣亮、根本切不開——FACS gating 整個失效。
4. 工具與材料: 
   - **Neon Transfection System (electroporation)**: 用瞬間高壓電在細胞膜上打開暫時透化孔，讓 transfer vector + Cre 質體進入 K562 細胞；4 µg library + 1 µg pBS185 CMV-Cre 共電穿 1.2 × 10⁶ cells。
   - **pBS185 CMV-Cre (Addgene 11916)**: 提供 Cre 重組酶來源的質體，CMV 啟動子驅動瞬間表現。
   - **Cre recombinase**: P1 噬菌體 site-specific recombinase，認 34 bp lox 序列；同款配同款做整段 cassette exchange。
   - **Pooled landing pad cells**: 8 株 (第二代 14 株) 不同位置的純系細胞混成一管，讓 8 個位置共享同一批試劑與 Cre，消除批次間偏差。
   - **GFP-negative FACS gating**: 以未電 Cre 的對照組 landing pad 細胞 GFP 強度下尾 28% 為閾值；置換成功者 eGFP 被換掉，GFP 訊號變暗落入此閾值以下。
   - **1 週 GFP 衰退期**: 等待已表現的 eGFP 蛋白透過細胞分裂稀釋與降解衰減；eGFP 半衰期 > 1 day，必須等待才能 FACS 區分。
   - **Cre-lox 置換效率 (約 12%)**: Cre 介導 cassette exchange 的整體成功率；FACS 提供 2.5× 富集 (30% sorted / 12% total)。
5. 與此篇文章的關係: 
   在《A massively parallel reporter assay dissects the influence of chromatin structure on cis-regulatory activity》這篇文章中，作者要把多種 CRS 同時測在多個基因組位置。Cre 介導定點 cassette exchange + GFP 負向 FACS 富集是這個目標的核心一步：解決了「Cre 置換效率只有 12% 會把訊號稀釋」的瓶頸，把成功置換的細胞富集 2.5 倍；產出的細胞群是下一步同步抽 RNA / gDNA、放大 cBC-gBC 條碼對的樣本來源。
