# 跨數據集擾動 signature 比對 (Module scoring vs OverCITE-Seq / Perturb-Seq)

1. 引用自哪篇 paper: crispr-all-genetic-perturbation-language
2. Outline (任務主線): 跨數據集擾動 signature 比對 (Module scoring vs OverCITE-Seq / Perturb-Seq)
3. Method:
   作者要驗證的是：CRISPR-All-seq 抓到的擾動表型，跟過去業界的單類別黃金標準比對得起來嗎？也就是說「同一種擾動在不同平台留下的指紋一不一樣」。OverCITE-Seq 與 Perturb-Seq 是過去業界各自針對「過表達」與「敲除」開發的單細胞讀出平台：前者把 ORF 圖書館塞進細胞、看每顆細胞表達了哪個 OE 基因；後者用 CRISPR 敲除每顆細胞的某個基因、看後續表型。兩個都只能做單一擾動類別，但各自針對的擾動類型訊號最乾淨——把它們當成標準卡，CRISPR-All-seq 比得過就證明大一統沒有犧牲精準度。資料直接從公開倉庫 GEO 抓 GSE193736（OverCITE-Seq, LTBR）與 GSM6568647/GSM6568648（Perturb-Seq, MED12）。

   怎麼從舊平台抽出「LTBR OE」或「MED12 KO」的指紋？作者把舊資料集的 OE/KO 細胞 vs control 細胞丟進 Seurat 的差異表達分析工具 `FindMarkers`，問「哪些基因因為這個擾動上下變化最大？」這裡特別不用 Seurat 預設的 Wilcoxon 檢定，改用 logistic regression test，因為 Wilcoxon 沒辦法把「捐贈者差異」這類雜訊變數一起拿掉。OverCITE-Seq 和 Perturb-Seq 的公開資料都來自不同捐贈者，同樣的 LTBR OE 樣本在不同個體上轉錄組基線就不一樣；不扣 donor 雜訊的話，top 50 DEG 名單會塞滿「捐贈者甲跟捐贈者乙不一樣」的基因，而不是真正的擾動下游，這張指紋搬去別的資料集就完全對不上。同時設 `min.pct = 0.02` 只看至少在 2% 細胞表達的基因，避開稀有訊號，取差異最大的 top 50 個基因當指紋。最後還有一個關鍵防呆：把擾動目標基因本身（LTBR、MED12）從清單裡刪掉。不然 LTBR 一定排在最前面（它就是被人為打開的那一個），兩邊 module score 都會在 LTBR 這條上看到一致上調，但這只證明「LTBR 自己」，沒驗證到下游真的啟動了同一群基因——這叫循環論證。處理 Perturb-Seq 資料前還多一步：因為它是 PBMC 混合細胞，裡面有 T 細胞、B 細胞、單核球等，要先挑出 T 細胞才能跟 CRISPR-All-seq 公平比。作者用 Azimuth PBMC reference（Satija lab 釋出的大型已標註細胞圖譜）自動把每顆細胞貼上身分標籤，保留 CD4 T、CD8 T 和 NK——保留 NK 是因為 T 細胞訊號相近偶會被 Azimuth 誤標成 NK，硬刪會把該留的 T 細胞一起丟掉。

   指紋抽好之後，要把它套到 CRISPR-All-seq 的細胞身上打分數。Module score 就是「把一群基因打包成一張分數卡」：先把這群指標基因在某顆細胞中的表達量取平均，再扣掉一批「表達高低差不多」的隨機對照基因的平均當基線，剩下來的數字越高就代表這顆細胞同時把這群指標基因打開的力道越強。為什麼要扣對照？因為細胞裡表達量高的基因通常一起漲一起跌——這是定序總量本身的雜訊，跟擾動無關。如果直接平均當分數，會被「這顆細胞整體比較活躍」帶高，分不清是 LTBR 真的把那群基因打開還是細胞本身吵。扣掉同表達高低的隨機基因當基線，剩下的差距才是擾動真正的貢獻。實際運算用 Seurat 的 `AddModuleScore` 一行搞定。最後結果：CRISPR-All-seq 三個捐贈者裡，LTBR OE 細胞與 MED12 KO 細胞的 module score 都顯著高於 GFP/AAVS1 控制組（Fig 5H, S7A），代表新平台真的捕捉到了與舊平台一致的擾動下游程式。

4. 工具與材料:
   - **OverCITE-Seq**: 業界針對「過表達」開發的單細胞讀出平台，把 ORF 圖書館塞進細胞後逐顆讀。本研究拿來作 LTBR OE 的指紋標準卡。
   - **Perturb-Seq**: 業界針對 CRISPR 敲除的單細胞讀出平台，逐顆細胞看 KO 後的轉錄組變化。本研究拿來作 MED12 KO 的指紋標準卡。
   - **GEO 資料倉庫**: NCBI 公開單細胞與表達資料倉庫；作者從這裡抓 GSE193736 (OverCITE-Seq) 與 GSM6568647/8 (Perturb-Seq)。
   - **FindMarkers (Seurat)**: Seurat 內的差異表達分析函式，比較兩群細胞間哪些基因表達差異最大。
   - **logistic regression test**: 可同時排除共變數的差異檢定；本研究用來在算 DEG 時 regress out 捐贈者差異。
   - **min.pct = 0.02**: FindMarkers 參數：只看至少在 2% 細胞中表達的基因，避開稀有訊號帶來的雜訊。
   - **top 50 DEGs**: 取差異表達分析中變化最大的前 50 個基因作為某個擾動的「指紋」；刪除目標基因本身以避免循環論證。
   - **Azimuth PBMC reference**: Satija lab 釋出的大型已標註 PBMC 細胞圖譜，自動為混合細胞貼身分標籤；保留 CD4 T、CD8 T、NK。
   - **AddModuleScore (Seurat)**: 把一群指標基因打包成單一分數的函式，扣掉同表達高低隨機基因的平均當基線，去除細胞整體活躍度的偏差。
   - **module score**: 每顆細胞同時上調指標基因群的力道分數；越高表示該細胞越接近該擾動的轉錄組指紋。

5. 與此篇文章的關係:
   在《A unified genetic perturbation language for human cellular programming》這篇文章中，作者的大目標是要證明 CRISPR-All-seq 這個一站式單細胞讀出沒有引入系統性偏差。為此他們採用了跨數據集擾動 signature 比對，解決了「新平台跟既有單類別黃金標準會不會抓到同樣下游」的瓶頸。這個方法吃 OverCITE-Seq、Perturb-Seq 公開資料抽出的 top 50 DEG 指紋，產出每顆 CRISPR-All-seq 細胞對應的 module score，作為新平台可信度的旁證，交給後續結論去支持「大一統不犧牲精準度」。
