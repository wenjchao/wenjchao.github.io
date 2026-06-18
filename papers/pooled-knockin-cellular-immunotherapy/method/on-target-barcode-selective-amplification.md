# On-Target Barcode 選擇性擴增與深度測序

1. 引用自哪篇 paper: pooled-knockin-cellular-immunotherapy
2. Outline (任務主線): On-Target Barcode 選擇性擴增與深度測序
3. Method: 
   電穿孔時細胞被打了 1–3 μg 的 DNA 模板進去，絕大部分都飄在細胞質裡沒真的接到染色體上 (free HDR template)；這些飄著的模板上面也帶條碼，數量還遠多於真正整合到染色體裡的那幾份。如果直接 PCR 條碼，會把這堆沒接上的一起放大，讀出來的比例完全反映不了「哪個裝備真的裝上了」。所以必須設計一支只認得「已裝上染色體」的 PCR。整個流程拆成四步：第一，從細胞抽核酸——要算 DNA 層面用 QuickExtract 抽 gDNA，要算 RNA 表現層面則用 Trizol 抽 mRNA 再反轉錄成 cDNA；第二，做第一次選擇性 PCR (PCR1)，兩支引子一支夾在裝備內側、一支夾在基因組那段「故意對不上」的外側；第三，做第二次 PCR (PCR2) 把 Illumina 定序機需要的接頭與樣本條碼加上去；第四，用磁珠 (SPRI bead) 1.0× 比例把目標長度 (> 300 bp) 抓出來、引子二聚體洗掉，丟進 Illumina MiniSeq 跑配對端讀長 2×150 bp 的定序。為什麼分兩步 PCR？因為一步如果直接用帶長尾接頭的引子，那條長尾在基因組雜訊裡很容易亂貼到別處，做出來的 library 雜訊大、樣本還會交叉污染——兩步走可以先用短引子拿到乾淨的目標片段，第二步才加接頭。
   這支「只認整合過的 allele」的 PCR 之所以做得到，關鍵在 HDR 模板的同源臂設計。作者設計模板時，在 3' 端「貼到基因組的同源臂」裡刻意塞了一段約 10 個鹼基「對不上基因組」的小錯位序列 (homology arm mismatch)。當 HDR 真的把模板黏到染色體上時，這段錯位會被細胞自己的修補機制換成基因組原本的正確序列；如果模板沒整合、自己飄在細胞裡，這段錯位就維持原樣。PCR1 的下游引子刻意挑在「錯位外面、屬於基因組真實序列」的位置——只有「成功整合過、錯位已被換掉」的版本才會兩支引子都對得上去並擴增；飄著沒整合的模板，下游引子完全咬不到。另外條碼為什麼嵌在 TCRα V 區、距功能裝備只有 ~400 bp？因為 Illumina MiniSeq 的配對端讀長是 2×150 bp，一次只能讀 ~300 bp 的視窗，作者要讓 barcode 與功能裝備落在同一個 < 500 bp 的 amplicon 裡，PCR 才能一次放大兩者、定序才能一次讀完。
   整套擴增其實做了兩條獨立路徑：一條從基因組 DNA 走、一條從 mRNA 反轉錄出的 cDNA 走。為什麼要兩條？從 gDNA 算的條碼比例反映「這個裝備在族群裡接到了幾顆細胞」——是一個「人頭數」的指標；從 cDNA 算的條碼比例則反映「這個裝備正在被轉錄成 mRNA 的量」——是一個「火力強度」的指標。兩條路徑一起做，作者可以同時知道某個裝備是「裝得多」還是「表現得強」，並把兩者比值用來排除表現量差異造成的偏倚。
   這個流程有兩個容易壞的地方。第一，如果同源臂沒做錯位，下游引子只能改貼在同源臂裡面——但同源臂在飄著的模板上也存在，PCR 會把那一坨沒整合的模板一起放大，數量壓過真正整合的訊號，讀出來的條碼比例就變成「哪個模板電穿孔時打進去比較多」而非「哪個裝備真的有用」，所有篩選結論直接報廢。第二，PCR 循環數不能放任，作者把 PCR1 控制在 12、PCR2 控制在 10 個循環。每跑一個循環 DNA 量翻倍，但早期任何亂貼的誤差也跟著翻倍——循環太多會讓最早幾顆細胞的雜訊放大到主導全局 (PCR jackpot)，barcode 比例就失真；模板飽和後甚至會冒出兩段半路接起來的嵌合 amplicon。12 + 10 是「訊號夠強到能定序、但雜訊還沒主導」的折衷。
4. 工具與材料: 
   - **Homology arm mismatch**: 在 HDR 模板 3' 同源臂植入 ~10 bp 不匹配序列，整合後被基因組真實序列換掉，使 PCR 可區分整合 vs. 未整合。
   - **Nested PCR (PCR1 + PCR2)**: 兩步 PCR：PCR1 用短引子拿到乾淨目標、PCR2 加 Illumina 接頭與樣本身分條碼。
   - **SPRI bead 1.0×**: Solid Phase Reversible Immobilization 磁珠，1.0× 體積比保留 > 300 bp 片段、洗掉引子二聚體與短雜訊。
   - **QuickExtract**: 快速 gDNA 萃取試劑，適合大量樣本流程。
   - **Trizol + Direct-zol**: 從細胞抽 mRNA 的標準試劑組合，搭配 Maxima H RT 反轉錄成 cDNA。
   - **Illumina MiniSeq 2×150 bp**: 配對端讀長定序平台，一次可讀 ~300 bp 視窗，要求 amplicon 控制在這個範圍內。
   - **Kapa HiFi HotStart**: 高保真 PCR 酵素，用於 PCR1 的 12 個循環選擇性擴增。
5. 與此篇文章的關係: 
   在《Pooled Knockin Targeting for Genome Engineering of Cellular Immunotherapies》這篇文章中，作者為了精準定量每個 knockin 構築在 T 細胞族群裡的真實豐度，採用了 homology arm mismatch 配 nested PCR 的選擇性擴增策略。這個方法解決了細胞內殘留的未整合 HDR template 會壓過真實整合訊號的瓶頸，吃進細胞的 gDNA 或 cDNA，產出乾淨的 on-target barcode amplicon 給 Illumina 定序，作為下游 log2 fold change 計算與 pooled screen 排名的原料。
