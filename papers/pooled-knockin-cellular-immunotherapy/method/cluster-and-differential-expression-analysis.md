# Cluster 與差異表達分析

1. 引用自哪篇 paper: pooled-knockin-cellular-immunotherapy
2. Outline (任務主線): Cluster 與差異表達分析
3. Method: 
   找出細胞狀態的步驟是這樣：先把每顆細胞放到前 30 個主成分定義的 30 維空間，計算「每顆細胞最像的 k 個鄰居是誰」，再進一步只連「彼此互相是鄰居」的細胞 (共享最鄰近圖 shared nearest neighbor graph, SNN)。在這張網上跑 Louvain 演算法：每顆細胞當一個節點、初始各自為政，每輪嘗試把節點搬去鄰居所在的社群，看「搬完後社群內部連線比隨機期望多了多少」（modularity Q）；只要搬能讓 Q 升高就保留，搬到沒辦法再升為止。Louvain 等於在找「社群內連得密、社群間連得稀」的天然切點，每個切出來的社群就是一個 cluster，這套是 Seurat 的 FindClusters 內建做法。「無監督」指作者沒事先告訴演算法「這顆是 naïve、那顆是 effector」，全由細胞相似度決定。切完 cluster 還是一堆編號，作者再看每個 cluster 高表達的標記基因 (hallmark genes)：CCR7 高 → naïve「年輕未上戰場」；MKI67 高 → 正在分裂的 proliferative；IFN-γ 與 GZMB 高 → 正在分泌殺敵武器的 effector——對應上之後每個編號就有了生物學名稱。
   知道每個 cluster 代表什麼狀態之後，作者要量化「每個構築偏好哪個 cluster」。最直覺的做法——直接數「TGF-βR2-41BB 細胞在這個 cluster 有幾顆」——會被一個陷阱誤導：有些 cluster 本來人數就大（例如靜止狀態的主流 cluster），任何構築都會在其中佔多數，結果所有 36 種構築都被誤判成富集在大 cluster。正確做法是問：「如果 36 種構築在所有 cluster 都均勻分布，這格應該有幾顆？實際有幾顆？」這個比較就是卡方檢定 (Chi-square test)：算每格的「觀察值 vs. 期望值」差距。但原始差距會被該格期望值大小放大（期望 1000 實際 1100 差 100 看似多，其實只 10% 偏差；期望 10 實際 30 差 20 看似少，但是 200% 偏差），所以再除以期望值的平方根、得到標準化殘差 (standardized residuals)——正值代表富集、負值代表耗竭、絕對值代表強度。作者把這些殘差畫成 Figure 5H 的熱圖。
   Cluster 富集只回答「在哪些狀態多」，但無法回答「裝了某構築的細胞整體轉錄組差在哪」。作者用 pseudo-bulk 策略：把帶同一構築的所有細胞當成一個大樣本，把它們的 UMI 計數逐基因加總起來，等於把單細胞資料壓回成一個 bulk RNA-seq 樣本，再對每個基因跑 Wilcoxon 秩和檢定（單細胞 counts 嚴重偏態、零膨脹，t-test 的常態假設不成立，Wilcoxon 只看排序對歪斜分布很穩定），挑出 |log2 fold change| > 0.8 的差異表達基因 (DEG)——大致是「比對照組多 1.7 倍 / 少 1.7 倍以上」，這是 Seurat 流程常用的中等嚴格度。為什麼非 pseudo-bulk 不可？若直接逐細胞跑統計，會把「同條件內細胞之間的隨機差異」誤判為「條件間真的差異」，加上資料量大會把微小差距吹成極小 p-value，產出大量假陽性。
   拿到 DEG 名單之後，作者再用兩種互補的 pathway 分析回答「這些 DEG 集體屬於哪些生物功能」。一是 REACTOME 路徑資料庫 + 超幾何檢定 (hypergeometric test)：把 DEG 名單當黑白二分，問「某條路徑（例如『細胞分裂』）的成員在我的 DEG 名單裡的比例，會不會比隨機抽更高？」答的是「DEG 是否過度集中在某條已知路徑」。二是預排序基因組富集分析 (preranked GSEA，由 fgsea R package 實作)：不切名單，而是把所有基因按差異強度排成一列，問「某條路徑的成員是不是集中聚在這條列的最上面或最下面？」答的是「即使每個基因只變一點點，但整條路徑會不會集體偏移？」兩種角度合用，能同時捕捉「大幅變化的少數明星基因」與「集體微幅變化的整條路徑」。
4. 工具與材料: 
   - **Seurat FindClusters (Louvain)**: 在 30-PC 空間建共享最鄰近圖 (SNN)，用 Louvain modularity 最大化找天然切點，產出無監督 cluster。
   - **Hallmark genes 註解**: 用 CCR7（naïve）、MKI67（proliferative）、IFN-γ / GZMB（effector）等標記基因把編號 cluster 對應到生物學意義的細胞狀態。
   - **Chi-square test + standardized residuals**: 比較每個 (cluster × 構築) 格的觀察值與期望值，再除以期望值平方根標準化，正值代表富集、負值代表耗竭，畫成 Figure 5H 熱圖。
   - **Pseudo-bulk 策略**: 把帶同一構築的所有細胞 UMI 計數逐基因加總，將單細胞資料壓回成 bulk RNA-seq 樣本，降低雜訊與避免假陽性。
   - **Wilcoxon rank sum test**: 非參數秩和檢定，只看排序不看絕對值，適用於 scRNA-seq 嚴重偏態、零膨脹的計數分布。
   - **|log2FC| > 0.8 DEG 門檻**: 差異表達基因門檻（約 1.7 倍差距），Seurat 流程常用的中等嚴格度，平衡敏感度與特異度。
   - **REACTOME + hypergeometric test**: 把 DEG 名單對 REACTOME 路徑資料庫做超幾何檢定，回答「DEG 是否過度集中在某條已知路徑」。
   - **fgsea preranked GSEA**: fgsea R package 實作的預排序基因組富集分析，把所有基因依差異強度排序，回答「某路徑的成員是否集體偏向最上或最下」，捕捉集體微幅變化。
5. 與此篇文章的關係: 
   在《Pooled Knockin Targeting for Genome Engineering of Cellular Immunotherapies》這篇文章中，作者要回答「TCF7 與 TGF-βR2-41BB 同樣讓 T 細胞數量變多，但細胞狀態究竟差在哪」這個問題，於是把 PoKI-Seq 預處理後、帶有構築身份標籤的單細胞矩陣丟進 cluster 與差異表達分析。這一步把細胞分到 naïve、proliferative、effector 等狀態，並用卡方標準化殘差與 pseudo-bulk DEG 量化每個構築的偏好，解釋了為什麼只有 TGF-βR2-41BB 真正進到 IFN-γ+ effector 狀態，把整篇論文的「abundance 命中」與「state 命中」拆開。
