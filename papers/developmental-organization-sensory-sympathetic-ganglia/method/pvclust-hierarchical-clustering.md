# 階層叢集與 pvclust bootstrap 檢定 (bulk 神經節 phylogeny)

1. 引用自哪篇 paper: developmental-organization-sensory-sympathetic-ganglia
2. Outline (任務主線): 階層叢集與 pvclust bootstrap 檢定 (bulk 神經節 phylogeny)
3. Method:

作者要把三位捐贈者身上近兩百顆神經節的親屬關係一次畫出來，靠的是一張「條碼 × 神經節」的大表格：每一直行代表一顆神經節，每一橫列代表一個 MPAS 驗證過的錯字條碼 (MV)，表格裡的數字是該條碼在該神經節的比例 (AF) 開根號。餵給階層叢集 (hierarchical clustering) 演算法後，程式先找最像的兩顆神經節黏成一對，再把這對當成新節點繼續往上合，最後長成一棵親戚樹 (dendrogram)。兩顆神經節「像不像」用曼哈頓距離 (Manhattan distance) 判斷：逐個條碼看差多少，取絕對值後全部加起來——像在棋盤格街道上算總距離，數字愈小愈像親戚。作者再用 ComplexHeatmap 套件把 dendrogram 放在 heatmap 側邊一起呈現，方便對照哪些神經節共享哪些條碼。

光畫一棵樹還不算數——那可能只是這一批 MV 剛好排成那樣。作者用 r-pvclust 把原始條碼表隨機抽樣一萬次，每抽一次就重新畫一棵樹，最後統計「同樣那兩顆神經節被畫成兄弟」的次數比例，得到一個叫近似無偏 P 值 (approximately unbiased P value, AU) 的穩定度分數。pvclust 在計算 AU 時還會扣掉「抽樣次數會偏袒某些分支」的系統偏誤，比單純的 bootstrap frequency 更公正。作者把 AU >95% 當作「穩定分支」的門檻——相當於統計上常用的 5% 顯著性水準：一萬次重抽裡至少 9,500 次都把這兩顆歸為兄弟，反過來說「其實不是兄弟卻剛好被抽出來像兄弟」的機率不到 5%。低於這個門檻的分支就不敢當結論用。

在跑演算法前，作者還做了兩個看似技術細節但決定成敗的前處理。第一，AF 為什麼先開根號？因為有些條碼 AF 特別高（例如 0.4）、大部分條碼卻很稀薄（AF 只有 0.01）。若直接把 AF 加起來算距離，高 AF 條碼會壓過所有低 AF 條碼，最後的樹形只反映一兩個大 clone 分布在哪。開根號能把大數字壓小、把小數字相對抬高（$\sqrt{0.4} \approx 0.63$、$\sqrt{0.01} = 0.1$），讓稀薄的小 clone 也對距離有貢獻。第二，為什麼選 Manhattan 而不用常見的 Euclidean distance？神經節的條碼矩陣其實很稀疏——大部分條碼在大部分神經節都是 AF = 0。Euclidean 把差值平方，任何一個條碼差很多就會蓋掉所有其他小差異；Manhattan 只加絕對值，讓「很多個小差異」和「一個大差異」各自算數，稀疏矩陣裡的整體相似度不會被個別 outlier 拖走。

跑完之後，18 個 AU >95% 的穩定分支裡有 16 個由「同型態、跨 2–6 個 level」的神經節組成（例如 T2-DRG 跟 T5-DRG 穩定黏在一起），0 個由「同 level DRG + SG」組成（同一節脊椎上下對的感覺節+交感節從來沒被穩定判為兄弟）。這個結果就是作者主張「clonal 分群主要由型態決定、而非位置決定」的統計骨幹——因為 bootstrap 支撐的分支結構直接把這個對比可視化，讀者不必再爭辯「這只是視覺 pattern」還是「這只是碰巧」。

4. 工具與材料:

- **r-pvclust (v2.2.0)**: R 套件；把叢集分析加上 bootstrap 一萬次，並算出校正過的近似無偏 P 值 (AU)，量化每根分支的穩定度。
- **ComplexHeatmap (v2.16.0)**: R 套件；把 dendrogram 與 heatmap 並排畫在同一張圖，方便同時看樹的形狀與條碼分布。
- **√AF matrix**: 把每個 MV 在每顆神經節的 allele frequency 開根號後排成的「條碼 × 神經節」表格，作為叢集分析的輸入。開根號是為了不讓高 AF 大 clone 壟斷距離。
- **Manhattan distance**: 兩顆神經節條碼向量逐格差值取絕對值再相加，得到的距離。對稀疏矩陣比 Euclidean 更穩健。
- **Hierarchical clustering**: 反覆把最相似的兩個節點合併成新節點，最後長出一棵親戚樹 (dendrogram) 的分群方法。
- **Bootstrap resampling**: 從原始資料隨機抽樣重建結果，藉重複計算次數估分支穩定度。本文採 10,000 次重抽。
- **Approximately unbiased P value (AU)**: pvclust 對 bootstrap frequency 進一步扣掉抽樣次數依賴偏誤後的分支穩定度分數；AU >95% 對應 5% 顯著性水準。

5. 與此篇文章的關係:

在《Developmental organization of sensory and sympathetic ganglia》這篇文章中，作者為了回答「神經脊細胞的感覺 vs 交感命運是否早於離管」，先用 pvclust 對三位捐贈者近兩百顆神經節的 √AF 矩陣做階層叢集加一萬次 bootstrap。這一步吃 MPAS 驗證過的錯字條碼表，產出一棵標了 AU P 值的親戚樹，篩出 18 個 AU >95% 的穩定分支，供下游做「同型態跨 level vs 同 level 跨型態」的直接對比。它是把「bulk 神經節間的 clonal 訊號」變成可被統計檢定的分群結果的關鍵一步。
