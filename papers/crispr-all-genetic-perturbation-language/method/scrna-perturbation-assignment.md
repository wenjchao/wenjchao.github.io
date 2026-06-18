# scRNA-seq 處理與 perturbation assignment (CRISPR-All-seq pipeline)

1. 引用自哪篇 paper: crispr-all-genetic-perturbation-language
2. Outline (任務主線): scRNA-seq 處理與 perturbation assignment (CRISPR-All-seq pipeline)
3. Method:
   整個 CRISPR-All-seq pipeline 的核心是把「每顆細胞的轉錄組」與「這顆細胞被裝了什麼改造」綁在同一個 Seurat object 裡。輸入是同一個 10X lane 跑出來的兩條 library：基因表現原始檔與條碼擴增原始檔。能順便讀到兩件事是因為 10X v3 化學的設計——每顆凝膠珠上的釣鉤從 5′ 到 3′ 依序是「同顆細胞共用的 cell barcode → 每條分子獨有的 UMI → 一段 oligo-dT」，油滴內 oligo-dT 黏上 mRNA 3′ 端的 polyA 後反轉錄，所以讀出的 cDNA 一定從 3′ 端開始。作者把 CRISPR-All 條碼擺在 mRNA 3′UTR 緊鄰 polyA，這個位置剛好被優先抓到，同一條 cDNA 上自動同時帶著 cell barcode、UMI 跟 construct barcode。兩條 library 對深度需求不同：GEX 要量化全基因組數萬個基因，每細胞 ~20,000 reads 即可；construct barcode 需要每細胞 >20 barcode-UMI 才能讓 deMULTIplex2 穩定指派，所以作者把 cDNA 拆成 25% 跑 GEX、75% 跑 barcode amplicon，後者再用 18 + 12 cycle 兩輪 PCR 放大後深度定序。GEX 那條用 Cellranger v6.0.0 算出細胞-基因計數矩陣載進 Seurat v5.2.0；barcode 那條由作者腳本拆解 (R1 前段是 cell barcode、後段是 UMI、R2 是 construct barcode)，產生細胞-construct 計數矩陣。值得注意的是作者刻意不糾正條碼小錯字、也不合併 UMI——因為 construct barcode 設計時已經至少差三個字母 (hamming ≥3)，零錯誤搜尋本來就不會誤指，強行合併反而會把真實低豐度 construct 跟背景雜訊混在一起，破壞 deMULTIplex2 的指派模型。deMULTIplex2 對每顆細胞看到的 construct 計數擬合 negative binomial 混合分布——一種同時描述『真實訊號』與『雜訊背景』的計數模型——超過閾值的 construct 才算被裝到這顆細胞身上：剛好一個過關代表乾淨指派；兩個以上同時過關叫多重指派 (multiplet)；一個都沒過關標 negative。multiplet 與 negative 都從分析剔除。

   完成指派後，細胞還要過三道品質把關才能進下游分析。`unique features > 1000` 排掉捕獲失敗的空滴 (活細胞應該表達上千個基因)；`total UMIs < 40,000` 排掉一滴油塞兩顆細胞的雙聯體；`mitochondrial reads < 10%` 排掉細胞膜破損的死細胞 (細胞膜破時 cytoplasmic mRNA 流失、線粒體 mRNA 相對升高)。三條合起來保證留下的細胞乾淨、單一、健康。接下來最關鍵的設計是「兩階段批次校正」。第一階段在細胞層級：三位 donor 跑了 7 個 10X lane，donor 之間 T 細胞本來就有體質差異 (年齡、性別、活化狀態)，直接畫 UMAP 細胞會按 donor 群聚而非按改造類別群聚。Seurat v5 的 IntegrateLayers 函式搭配 Harmony 演算法 (一種反覆做分群與線性校正的批次對齊法) 把不同 donor 的細胞拉到同一張低維空間，讓同一種改造的細胞不分 donor 都聚在一起。第二階段在 pseudobulk 層級：把每位 donor × 每個 construct 的所有細胞加總成一筆觀測值 (AggregateExpression)，再用 limma 的 removeBatchEffect 以 donor 與 perturbation type 為 batch variable 扣掉這兩層偏移，剩下的差異才是這個 construct 特有的訊號。Harmony 是給細胞用的、limma 是給 pseudobulk 用的，目標跟尺度都不同，缺一不可。最後用 FindMarkers (預設 Wilcoxon，透過 presto 加速) 對每個 construct 找差異基因、算 Log2 Fold Change vs GFP-knockin 控制組。

   這條 pipeline 有三個容易壞掉的環節。第一個是 barcode swapping——它跟單字母讀錯完全不同：在池化 PCR 或油滴內反轉錄擴增的中間步驟，某條延伸中的 cDNA 跳到另一條 template 上繼續延伸，結果一條最終產物上「cell barcode 是細胞 A 的、construct barcode 卻來自細胞 B 的構築」。每段條碼自己讀起來都對，hamming 距離跟 zero-mismatch 規則察覺不到——錯的是兩段條碼的配對。同一顆細胞會看到一些不該屬於它的 construct 計數變成背景雜訊，這就是為什麼非靠 deMULTIplex2 的統計分布分離 signal vs background 不可，而不能簡單地「看到 construct X 的 read 就算這顆細胞裝了 X」。第二個是不剔 multiplet 跟 negative：multiplet 同時帶兩種 perturbation 的轉錄組訊號，會把 marker 拉向兩種改造的平均、把純粹 A vs 純粹 B 的差異糊掉；negative 訊號太弱無法歸類，留進來當對照只會稀釋真實差異訊號，FindMarkers 算出的 effect size 跟 p 值都會被壓低。第三個是跳過 Harmony 直接畫 UMAP：donor 間 HLA、性染色體相關基因、活化狀態差異本來就遠大於任何單一 perturbation 的轉錄組變化，FindMarkers 找出來的會是 donor-specific 基因而不是 perturbation-specific 訊號，跨 donor 一致的擾動 signature 完全找不出來。三道防線缺一不可。

4. 工具與材料:
   - **10X GEM-X Universal 3′ GEX v3**: 10X 單細胞 3′ 化學：每顆 gel bead 釣鉤帶 cell barcode + UMI + oligo-dT，反轉錄從 mRNA 3′ polyA 起始，順便抓到 3′UTR 內的 construct barcode。
   - **25% / 75% cDNA split**: 把同一管 cDNA 拆 25% 跑 GEX library、75% 跑 barcode amplicon library，後者再 18 + 12 cycle PCR 放大深度定序。
   - **Cellranger v6.0.0**: 10X 官方 pipeline，把 GEX fastq 處理成 cell × gene 計數矩陣 (每 cell 約 20,000 reads)。
   - **Seurat / SeuratObject v5.2.0**: R 裡分析單細胞轉錄組的主流套件；用 IntegrateLayers + Harmony 做 donor 整合、AggregateExpression 做 pseudobulk、FindMarkers 找差異基因。
   - **deMULTIplex2**: 以 negative binomial 混合分布擬合每顆細胞的 construct UMI 計數，分離 signal vs background 並指派 perturbation；同時標出 multiplet 與 negative。
   - **HarmonyIntegration**: 細胞層級批次校正：反覆分群再線性校正，把不同 donor / lane 的細胞拉到同一張低維空間。
   - **AggregateExpression + limma removeBatchEffect**: pseudobulk 層級批次校正：把 donor × construct 加總成觀測值後，以 donor + perturbation type 為 batch variable 扣掉偏移。
   - **presto**: Wilcoxon rank sum test 的高效實作，被 FindMarkers 預設用來在大數據上跑差異表達。
   - **barcode swapping**: 池化 PCR 或油滴內 RT/PCR 時 cDNA 跨 template 跳躍，導致 cell barcode 與 construct barcode 配對錯誤的背景污染。
   - **Cell QC cutoff**: unique features > 1000 (排空滴) + total UMIs < 40,000 (排雙聯體) + mitochondrial reads < 10% (排死細胞) 三條閾值。

5. 與此篇文章的關係:
   在《A unified genetic perturbation language for human cellular programming》這篇文章中，作者要把 CACTUS 與組合 library 在 T 細胞慢性刺激後的擾動效應放到單細胞解析度看清楚。這套 CRISPR-All-seq pipeline 吃 10X GEM-X v3 的兩條 library，吐出一個整合了基因表現矩陣與每顆細胞 perturbation 指派的 Seurat object，給下游 marker 比較與跨平台 module scoring (LTBR、MED12 signature) 用。它解掉了「Perturb-Seq / OverCITE-Seq / PoKI-Seq 各只能搭配一種擾動類別」的瓶頸，是跨類別單細胞讀出能成立的關鍵。
