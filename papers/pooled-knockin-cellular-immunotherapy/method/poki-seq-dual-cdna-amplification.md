# PoKI-Seq 單細胞 cDNA 雙路擴增（轉錄組 + barcode）

1. 引用自哪篇 paper: pooled-knockin-cellular-immunotherapy
2. Outline (任務主線): PoKI-Seq 單細胞 cDNA 雙路擴增（轉錄組 + barcode）
3. Method: 
   PoKI-Seq 的關鍵巧思是把同一池 cDNA 拆兩路、各自做一條 library，最後靠 cell barcode 把兩條結果在分析時接回去。整套流程拆四步：第一，把細胞與帶 cell barcode 的膠珠裝進 10x Chromium 微流道的奈升油滴 (GEM) 裡，每顆油滴是獨立反應槽，細胞在裡面裂解、所有 mRNA 反轉錄成 cDNA 時都接上同一個 cell barcode 與每條 mRNA 專屬的 UMI；幾千顆細胞同時被處理，定序時靠 cell barcode 把屬於同一顆細胞的 reads 重新歸隊。油滴回收後做 11 個循環的初步擴增。第二，把這池 cDNA 分成兩份——25% 走標準 scRNA-seq 做轉錄組 library，50% (20 μL) 走靶向擴增。第三，靶向那一份用兩支特製引子：正向認 10x 加上去的 cell barcode 上游接頭、反向認 TCRα 那段帶 knockin barcode 的序列，這樣只有「真正帶 knockin 構築的 cDNA」會被放大。第四，靶向 amplicon 經 0.8× AMPure 磁珠純化後再做 9 個循環的 i7 index PCR 加上樣本身分標籤，丟進 NovaSeq SP 跑配對端 28×8×98 並摻 25% PhiX——PhiX 是 PhiX174 噬菌體的均勻鹼基 control DNA，補回靶向 amplicon 因起頭序列相同而造成的鹼基不均，讓 Illumina 機器能正常做影像對位與校正。
   為什麼兩條 library 能把每顆細胞的轉錄組對應到它的 knockin 裝備？因為兩條走的是同一池 cDNA。10x 在反轉錄時就把 cell barcode 與 UMI 黏到每條 cDNA 的 5' 端；無論這條 cDNA 之後走轉錄組那條路還是靶向 PCR 那條路，5' 端那段 cell barcode + UMI 都還在。定序時靶向 amplicon 的 Read1 還是讀到 cell barcode、Read2 讀到 knockin barcode，分析時把同一個 cell barcode 出現的「轉錄組基因數量」與「knockin barcode 身分」直接 join，每顆細胞就同時有「狀態」與「裝備」兩筆資料。UMI 在這裡扮演去重的關鍵：同一條原始 mRNA 在 PCR 中會被複製出好幾份 reads，但這些 reads 共享同一個 UMI，分析時折成一個計數即可還原原始 mRNA 條數；少了 UMI，PCR 偏好放大某些 mRNA 的雜訊會被直接當成基因表現量，整套計數失準。
   cDNA 為什麼是 25% 給轉錄組、50% 給靶向、剩 25% 備份？因為靶向擴增只認得帶 knockin 構築的特定 cDNA，這類分子在全細胞 cDNA 池裡只佔很小一塊；要從裡面撈到足夠 reads 給每顆細胞配對到構築，必須投入比較多的 cDNA 起始量。轉錄組那邊本來就涵蓋所有基因，標準 input (25%) 已經足夠。
   兩個常見壞掉點要注意。第一，一顆細胞可能因為兩個原因讀到不只一個 knockin barcode：兩條染色體都被整合 (biallelic)、各自帶不同條碼；或 10x 油滴裡剛好兩顆細胞裝在一起 (droplet doublet)。分析時若超過兩個 knockin barcode 就直接濾掉，並要求至少 3 個獨立 UMI 都讀到同一個 knockin barcode 才正式指派，避免把 PCR 雜訊誤判成條碼。第二，如果不摻 PhiX，靶向 amplicon 在開頭幾個循環鹼基組成幾乎一樣，Illumina 機器的影像對位會混亂，後續 base calling 大量錯誤，整片 lane 的資料品質崩盤、連同 lane 的其他樣本都會被連累——25% PhiX 是定序界處理低多樣性樣本的標準補救。
4. 工具與材料: 
   - **10x Chromium**: 微流道把單顆細胞與一顆預刻 cell barcode 的膠珠裝進奈升油滴 (GEM) 進行 in-droplet 反轉錄的單細胞平台。
   - **Cell barcode**: 10x 膠珠上預刻的細胞身分條碼，反轉錄時黏到該細胞所有 cDNA 的 5' 端。
   - **UMI**: Unique Molecular Identifier，每條 mRNA 反轉錄時黏到的隨機識別碼，用於 PCR 去重還原原始分子數。
   - **Targeted barcode PCR**: 用 p5 forward 與 TCRα-read2 reverse 兩支特製引子，從同一池 cDNA 中只擴增帶 knockin 構築的分子。
   - **i7 index PCR**: 靶向 amplicon 純化後再跑 9 個循環加上樣本身分索引的二次 PCR。
   - **AMPure XP 0.8×**: 磁珠純化試劑，0.8× 比例保留中等以上長度的目標 amplicon、去除短雜訊。
   - **NovaSeq SP / S4**: Illumina 高通量定序儀，跑 PoKI-Seq 的轉錄組與靶向 amplicon library。
   - **PhiX spike-in 25%**: PhiX174 噬菌體均勻鹼基 control DNA，補回低多樣性樣本的鹼基不均，避免 Illumina 影像對位失敗。
5. 與此篇文章的關係: 
   在《Pooled Knockin Targeting for Genome Engineering of Cellular Immunotherapies》這篇文章中，作者為了同時測量每顆 T 細胞的「裝了哪個 knockin 構築」與「處於什麼細胞狀態」，採用了 PoKI-Seq 雙路 cDNA 擴增策略。這個方法解決了 pooled screen 只能看豐度卻無法看細胞狀態的瓶頸，吃進 10x Chromium 產出的 cell-barcoded cDNA 池，產出可在 cell barcode 層次配對的轉錄組與 knockin 構築兩筆資料，作為後續分辨 TCF7 偏 naive、TGF-βR2-41BB 偏 effector 的決定性證據。
