# PLS-DA + Ward Clustering Proteomics 熱圖

1. 引用自哪篇 paper: pediatric-tri-tube-valved-conduit
2. Outline (任務主線): 從 ~250 個蛋白中挑出最能區分 batch 的 top 25 蛋白，以視覺方式檢查 batch 間是否存在 ECM 組成的系統差異。
3. Method:

Gen 1 cohort 四隻羊裡，兩隻在 12/20 週瓣膜直徑暴增、提前失敗，另兩隻撐到 36/62 週才出狀況。審稿人會問：『會不會其實是你那四批 (batch) 原料管做出來品質不一樣，運氣好的兩隻分到好 batch、運氣差的分到壞 batch？』如果這個替代假說成立，整篇論文的『tri-tube 設計改良』結論就站不穩。作者必須回頭把四個 batch 的蛋白組成量出來（約 250 個 ECM 蛋白濃度，方法見 module 11 ECM Proteomics），證明 batch 之間沒有與 outcome 對應的系統差異。但 250 維資料如果全部畫熱圖，每個 batch 是一行、每個蛋白是一格，畫出來就是一片 250 格的長條，肉眼根本看不出哪個 batch 跟誰最像；而且大部分蛋白（譬如主要膠原蛋白 COL1A1、COL3A1）每個 batch 都差不多，對『分辨 batch』沒有貢獻——畫出來只是雜訊。

解決方法是先用偏最小平方判別分析 (PLS-DA, Partial Least Squares Discriminant Analysis) 從 250 個蛋白裡挑出 top 25。PLS-DA 是一種『監督式降維』方法——『監督式』意思是它在尋找新軸時知道每個樣本屬於哪個 batch（給了標籤）。具體做法：把 250 維蛋白濃度空間投影到一個只有幾條軸的新座標系，這幾條新軸是被特別挑出來、最能把不同 batch 的樣本拉開距離的方向。投影完之後，每個蛋白對這幾條軸的『貢獻權重 (loading)』可以算出來；把這些權重綜合一下，就得到一個叫變數重要性分數 (VIP, Variable Importance in Projection) 的分數，分數越高代表這個蛋白對『區分 batch』越重要。作者把 VIP 排名前 25 名的蛋白挑出來放進熱圖，這 25 個就是『最會說話』的蛋白。對比一下，PCA (Principal Component Analysis) 是『無監督』降維（只找『資料散得最開』的方向、不知道 batch 標籤）；PLS-DA 因為知道標籤，能更直接放大組間差異——但這也是它的危險：很容易在高維小樣本下『過度擬合 (overfitting)』，看似分得很開但其實是雜訊，所以作者把 PLS-DA 當視覺探索工具，最終統計結論交給 Fig. 2E/F 的 two-way ANOVA（見 module 16）。

挑出 top 25 蛋白後，熱圖還要讓相似的 batch 排在相鄰列才好讀。作者算的是歐幾里得距離 (Euclidean distance)：兩個 batch 各自有 25 個蛋白濃度，把對應蛋白的濃度差平方加總再開根號，就得到這兩個 batch 在 25 維空間的距離。接著用 Ward 演算法 (Ward clustering algorithm) 做凝聚式階層聚類：一開始每個 batch 自成一群，然後每一輪把『合併後組內變異增加最少』的兩群合起來，重複到所有 batch 合進同一個總群。合併過程畫出來就是一張倒著長的樹狀圖 (dendrogram)，樹枝越低代表越相似、越高代表差異越大。為什麼選 Ward 而非『最近鄰連結 (single linkage)』？因為 single linkage 容易產生『鏈狀效應 (chaining)』把所有 batch 串成一條鏈、看不出分群，Ward 則傾向產生緊密球狀群，對『每個 batch 內 3 個 replicate 應該很相似、不同 batch 應該分開』的情境特別合適。最後作者把 25 個蛋白依七大功能分類 (Basement Membrane、ECM-affiliated、FACIT collagen、Fibrillar collagen、Matricellular、Structural ECM、Cellular/Secreted) 分組著色，這是 ECM 領域基於 gene ontology 的標準分類，讓 reviewer 一眼能看出『差異是不是集中在某一個結構家族』。

Fig. S1 最後給出的結論：四個 batch 在樹狀圖上沒有與 outcome (12/20 週失敗 vs 36/62 週成功) 對應的分群模式——12 週的 batch 可能跟 36 週的 batch 聚在一起、20 週的反而跟 62 週的聚一起。再配合 Fig. 2E、Fig. 2F 的二因子 ANOVA，除了『纖維狀膠原 (fibrillar collagen) 總量』batch 間有差之外，個別膠原類型 (COL1A1、COL3A1、COL5A1 等) 在 batch 間都沒差。綜合視覺 (PLS-DA 熱圖) 與量化 (two-way ANOVA) 兩條證據，作者把『材料 batch 不穩定造成 outcome 差異』這條退路堵死，迫使讀者去看細胞反應或機械力學的解釋。失敗模式上要記住兩點：(1) PLS-DA 在高維小樣本 (12 樣本 vs 250 蛋白) 下容易過擬合，找到的『分群』可能只是雜訊——必須搭配 ANOVA 才能做出最終統計判斷，不能只給熱圖；(2) Ward 聚類比 single linkage 更適合這種小組互比的視覺呈現，否則鏈狀效應會掩蓋真實分群結構。

4. 工具與材料:

   - **PLS-DA (Partial Least Squares Discriminant Analysis)**: 監督式降維方法，把高維蛋白濃度空間投影到能最大化區分組別 (batch) 的低維軸，並用 VIP 分數排出每個蛋白的區分重要性。
   - **VIP (Variable Importance in Projection)**: PLS-DA 計算每個蛋白對投影軸的綜合貢獻權重，分數越高代表越能區分組別；本研究取 VIP top 25 蛋白做熱圖。
   - **Euclidean distance**: 把兩個 batch 在 25 維蛋白濃度空間中對應蛋白的差平方加總再開根號，得到的『直線距離』，作為 Ward 聚類的距離度量。
   - **Ward clustering algorithm**: 凝聚式階層聚類演算法，每輪合併能使組內變異增加最少的兩群；產生緊密球狀分群，比 single linkage 適合 batch 比較。
   - **Dendrogram**: Ward 聚類合併過程的樹狀圖，樹枝越低代表兩群越早合併、越相似；熱圖依此順序排列 batch。
   - **Seven ECM functional classes**: Basement Membrane / ECM-affiliated / FACIT collagen / Fibrillar collagen / Matricellular / Structural ECM / Cellular-Secreted，ECM 領域基於 gene ontology 的標準分類，用來判斷差異是否集中於某一結構家族。
   - **Overfitting (PLS-DA caveat)**: PLS-DA 在高維小樣本下會找到看似完美分離 batch 但只是雜訊的軸；本研究以 two-way ANOVA 作為量化備援避免此陷阱。

5. 與此篇文章的關係:

這篇論文在 Gen 1 cohort 中觀察到四隻羊裡有兩隻在 12/20 週就因瓣膜直徑暴增而提前失敗、另兩隻撐到 36/62 週，作者必須回應審稿人會問的替代假說：「結果差異會不會只是因為四批 (batch) 原料管的 ECM 組成本身不一樣？」本 module 的角色是把 ECM proteomics (module 11) 量到的約 250 個蛋白濃度做監督式降維，挑出 VIP top 25 最能區分 batch 的蛋白，再用 Euclidean distance + Ward 演算法做階層聚類，把 batch 與蛋白的相似關係視覺化成 Fig. S1 的熱圖加樹狀圖。好處有三：(a) 250 維資料直接畫熱圖完全看不出分群，PLS-DA 先把訊號濃縮到最具區分力的 25 個蛋白才讓肉眼看得到差異；(b) Ward 聚類傾向產生緊密球狀群、避免 single linkage 的鏈狀效應，特別適合 batch 間互比的視覺呈現；(c) 把 25 個蛋白依 ECM 七大功能類別著色，可一眼判斷差異是否集中在某一結構家族。在搭配上，這個熱圖只當描述性視覺檢查，最終統計判斷交給 Fig. 2E/F 的 two-way ANOVA (module 16) 補上量化證據，兩條證據合起來才把「材料 batch 不穩定造成 outcome 差異」這條退路堵死，迫使讀者去看細胞反應或 cyclic stretching 機制的解釋。
