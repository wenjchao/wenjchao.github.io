# CRISPR-All-seq 單細胞建庫

1. 引用自哪篇 paper: crispr-all-genetic-perturbation-language
2. Outline (任務主線): CRISPR-All-seq 單細胞建庫
3. Method:
   CRISPR-All-seq 的核心設計是「把擾動身分證放在 10X 既有試劑剛好會吸到的位置」。10X 的核心是一顆顆塗了捕獲探針的小膠珠 (gel bead)：探針前段是這顆膠珠專屬的細胞身分條碼 (cell barcode)、中段是區分同一基因不同分子的隨機標籤 (UMI)、後段是一串 dT。當一顆細胞被包進與膠珠同一顆油滴後，這串 dT 就去抓 mRNA 屁股的 polyA 尾巴，從那個位置往前反轉錄 (reverse transcription) 成 cDNA。問題是反轉錄能讀進去的長度有限，越靠近 polyA 越容易被讀到。作者把 CRISPR-All 條碼陣列藏在 mRNA 3′UTR 緊鄰 polyA 的位置，10X 不用換試劑就會「順手」把條碼陣列一起反轉錄進 cDNA——這條 cDNA 同時帶著 cell barcode 與 perturbation barcode。為什麼條碼不放進蛋白質編碼區 (CDS)？因為那會被核糖體翻譯成一段莫名其妙的胺基酸，搞亂蛋白質本身——擾動就壞掉了。3′UTR 是「未轉譯尾段」：核糖體碰到 stop codon 後停下不會翻譯這段，所以條碼不會變成蛋白質的一部分，蛋白質維持原樣；同時這段 mRNA 仍帶 polyA、仍會被 10X 的 poly-dT 抓到，等於「對蛋白質透明、對定序機看得見」。

   反轉錄與補成雙股後先跑 ~10 次擴增把整池 cDNA 量做出來，接著切兩條路：25% cDNA 走標準 10X 3′ 基因表達 (GEX) library——切碎、黏接頭、加 index、上 NovaSeqX，Read1 28 bp / i7 10 bp / i5 10 bp / Read2 91 bp，每顆細胞約 20,000 reads，得到「這顆細胞所有基因的表達量」。剩下的 75% 走 barcode amplicon library，用兩輪 PCR 把條碼陣列那段專門挑出來放大：第一輪用 CRISPR-All Internal Stuffer 序列當正向引子、用 10X TruSeq Read 1 序列當反向引子——這支序列由 10X 膠珠探針提供，所以只有真正從膠珠 RT 出來的 cDNA 才會被擴增，18 cycles；第二輪用 Nextera Read 2 + TruSeq Read 1 加 sample index，12 cycles；上 NextSeq 550 定序。為什麼是 25/75 而不是平分？基因表達 library 拿到 ~20,000 reads/cell 就夠，條碼擴增 library 卻得撐到每顆細胞平均 ~20 barcode-UMI、背景 < 2 barcode-UMI 才能把「裝了哪些擾動」叫得準，需要更多起始材料才不會出現抽樣偏差。細胞輸入是慢性刺激後 FACS 分選活的 NGFR+ CAR-T，每 lane 灌 25,000 顆細胞，donor 1 用 3 lanes、donor 2/3 各 2 lanes，共 7 lanes，化學版本是 10X GEM-X Universal 3′ Gene Expression v3。

   條碼指派時刻意「不做」sequence correction 或 UMI collapse：因為 11 鹼基條碼一開始就從 hamming distance ≥ 3 的白名單裡挑——任兩個合法條碼至少差 3 個鹼基，定序機讀錯 1 個鹼基的條碼也不會剛好變成另一個合法條碼。在這個前提下，多做一道「把讀錯的條碼校正到最近的合法條碼」反而可能把雜訊污染合法計數，不如直接生「cell × construct 的 UMI 計數矩陣」再交給 deMULTIplex2 用統計方法指派擾動、把多重感染 (multiplet) 與訊號太弱的 (negative) 丟掉。實測下來 87.5% 通過 QC 的細胞可分配到 unique perturbation。

   這套設計可能在哪裡崩掉？第一個地雷是「條碼放錯位置」：10X 3′ 化學的捕獲是從 polyA 那端拉一條 dT 進去反轉錄，越靠近 polyA 越容易被讀到；條碼一旦放到離 polyA 超過幾百 bp 的位置（例如 5′UTR 或中段 CDS 內），反轉錄常常還沒走到那段就掉鏈，cDNA 上根本沒帶條碼陣列，下游 amplicon PCR 抓不到——大部分細胞會因為條碼讀不到而被歸成 negative、被 deMULTIplex2 丟掉，最後拿來分析的細胞數會嚴重縮水，甚至偏向某幾種條碼。第二個地雷是「跳過 amplicon library」：可以從 GEX library 裡偶然撈到一些條碼讀數，但 GEX 在建庫時會把 cDNA 切碎再篩 ~400 bp 大小、覆蓋廣度，分到條碼陣列那一段的 reads 很稀薄，每顆細胞平均只能撈到一兩個 barcode-UMI，而背景 noise 本身就有 < 2 barcode-UMI，根本分不出真訊號與污染——大量細胞的擾動指派變得模糊，能拿來分析的細胞數從 87.5% 大幅掉下來，跨擾動類別讀出計畫的統計力直接崩盤。

4. 工具與材料:
   - **3′UTR (未轉譯尾段)**: mRNA 在 stop codon 之後、polyA 之前的這段；不會被核糖體翻譯，但仍會被反轉錄。條碼陣列就藏在這段。
   - **polyA**: mRNA 屁股一長串 A；是 10X 膠珠 poly-dT 探針鉤住 mRNA、啟動反轉錄的入口。
   - **10X gel bead**: 塗了捕獲探針的小膠珠；探針依序是 TruSeq Read 1 — cell barcode — UMI — poly-dT。
   - **cell barcode**: 10X 膠珠專屬的細胞身分條碼，串接在 cDNA 上代表「這條來自哪顆細胞」。
   - **UMI**: 區分同一 mRNA 不同分子的隨機標籤；用於消除 PCR 重複擴增造成的計數膨脹。
   - **reverse transcription**: 把 mRNA 反轉錄成 cDNA；從 polyA 端啟動的反轉錄會優先讀到鄰近 polyA 的序列。
   - **GEM-X Universal 3′ Gene Expression v3**: 10X Genomics 的單細胞 3′ 端基因表達定序化學版本；CRISPR-All-seq 直接沿用，無需改試劑。
   - **25/75 cDNA split**: 把擴增後的 cDNA 切成 25% GEX library 與 75% barcode amplicon library；後者需更多起始材料才能撐到 ~20 barcode-UMI/cell。
   - **barcode amplicon PCR**: 兩輪 PCR，正向用 CRISPR-All Internal Stuffer、反向用 10X TruSeq Read 1，鎖住「從膠珠 RT 出來、且帶條碼陣列」的 cDNA。
   - **deMULTIplex2**: 把 cell × construct UMI 計數矩陣統計指派成 perturbation；自動丟掉 multiplet 與 negative。
   - **hamming distance ≥ 3**: 條碼白名單的設計約束：任兩個合法條碼至少差 3 個鹼基，讓 1 個鹼基讀錯也不會誤判到別張牌。

5. 與此篇文章的關係:
   在《A unified genetic perturbation language for human cellular programming》這篇文章中，作者為了同時讀出每顆 CAR-T 細胞的「裝了哪些擾動」與「整體基因表達狀態」，採用了 CRISPR-All-seq 把條碼陣列鎖進 mRNA 3′UTR 緊鄰 polyA。這個方法解決了傳統 Perturb-seq / OverCITE-seq / PoKI-seq 只能處理單一擾動類別的瓶頸，吃進慢性刺激後 FACS 分選的 NGFR+ CAR-T，產出與 GEX library 共享 cell barcode 的條碼擴增 library，供下游 Seurat 整合分析每個跨類別擾動組合的轉錄組指紋。
