# Geoclone 空間映射與軸向 AF 標準差比較

1. 引用自哪篇 paper: developmental-organization-sensory-sympathetic-ganglia
2. Outline (任務主線): Geoclone 空間映射與軸向 AF 標準差比較
3. Method:

作者先把每個通過 MPAS 的 mosaic variant，在每顆神經節被讀到的 AF 開根號後，畫上一張人體神經節位置圖（想成一個標了 C1、C2…T12、L1…等左右對的方格圖），每個方格填的顏色深淺就是 √AF——這張圖就叫「geoclone」，一眼可以看出這款 clone 貼紙貼到哪些節、貼多濃。為什麼要用 √AF 而不是直接用 AF？因為 AF 有個怪毛病：AF 極小時 (0.01) 自然變異也極小、AF 中等時 (0.3) 變異最大、AF 接近 1 時又變小。這種變異隨 AF 值變化的特性 (heteroscedasticity) 會讓「兩軸的 SD 比較」失真——低 AF clone 兩軸的 SD 都貼近 0 看不出差異，高 AF clone 兩軸的 SD 都很大也看不出差異。開根號是統計上的 variance-stabilizing transformation：轉換後不同 AF 大小的 clone 都有可比較的變異量級，兩軸 SD 才能公平比較。

接著作者問這 clone 的關鍵問題：它是「同一節脊椎的 DRG + SG 一起有」還是「同種神經節橫跨很多節」？用兩個方向各取 12 個相鄰觀察值算 SD。rostrocaudal SD：只看一整條同型態神經節（例如左側 SG T1–T12），算這 12 個 AF 的 SD。dorsoventral SD：只看某節相鄰的 3 個 level（例如 T5、T6、T7）的左右 DRG + SG 合起來 ≈ 12 顆，算這批 AF 的 SD；窗口一格一格往下滑 (rolling-3-level)。SD 小代表 AF 在這個方向很一致 (clone 沿此軸連貫)、SD 大代表 AF 沿此軸亂跳 (clone 不沿此軸連貫)。所以「rostrocaudal SD 小 vs dorsoventral SD 大」就等於「clone 沿頭尾方向一致、沿背腹方向不一致」——這正是「clone 更 restricted 於同型態神經節」的直接統計特徵。

為什麼兩軸都刻意取 12 個觀察值、湊得一樣多？因為 SD 有個煩人的特性：樣本數越少 SD 期望值越大 (統計波動)、樣本數越多 SD 越接近母體真值。頭尾方向可以拿到 24 個 level (C1 一路到 L5)、背腹方向若只看單一 level 只有 4 顆；不管樣本數直接算 SD，rostrocaudal 會偏小、dorsoventral 會偏大——這時就算 clone 沿兩軸一樣均勻，也會看到「dorsoventral SD 遠大於 rostrocaudal SD」的統計人為偏差，不是真的 clone 分佈差異。刻意讓兩軸都湊到 12 個觀察值，才把 sample size 這個混淆變數擋掉，SD 差異真正反映 clone restriction。統計上作者選 Mann-Whitney U 這種無母數雙尾檢定而非 t-test，因為 SD 分布通常偏斜、對 outlier 極度敏感，t-test 前提會破功；Mann-Whitney U 只看兩組的排序、不受分布形狀影響、對 outlier robust。

最後一個必要的守門動作：作者把 ID06 一批 clustered variants 事先從估算中剔除，這批 variant 疑似來自「單一晚期 clone 局部大擴增」——AF 特別高、只集中在少數幾顆鄰近神經節。如果不排除會有兩個災難：這 clone 在某軸看起來「連貫」的假 pattern 會被誤讀成 fate restriction 的證據；且這 clone 的 AF 特別大會直接主導平均 SD，把整體結論拉走。剔除後才不會被「一顆晚期 clone 的巨響」蓋掉「數百個早期 clone 的真訊號」。所有結果最後以 ggplot2 (v3.4.3) 的 violin plot 呈現 SD 分布、contour plot 呈現 DV vs LR 的 AF 差異、ComplexHeatmap (v2.16.0) 補上聚類 dendrogram；geoclone 圖以 hg38 座標對應 body plan schematic。

4. 工具與材料:

- **geoclone**: 把每個 mosaic variant 的 √AF 描到人體神經節 body plan 圖上的空間分布地圖。
- **√AF (sqrt-AF)**: AF 的平方根轉換，做為 variance-stabilizing transformation，讓不同大小 AF 的 clone 都有可比較的變異量級。
- **rostrocaudal SD**: 沿一整條同型態神經節 chain (例如左側 SG T1–T12) 的 12 個 AF 的標準差。
- **dorsoventral SD (rolling-3-level)**: 以相鄰 3 個 level 的左右 DRG+SG (~12 顆) 為一個滑動窗口，算窗口內 AF 的標準差。
- **12 對 12 sample size 控制**: 兩軸都刻意湊到 12 個觀察值，把 sample size 差異對 SD 期望值的偏誤擋掉。
- **Mann-Whitney U (two-tailed)**: 無母數雙尾檢定，比較兩軸 SD 分布的差異，對偏斜分布與 outlier 都 robust。
- **ggplot2 (v3.4.3)**: R 繪圖套件，畫 violin plot 與 contour plot 呈現 SD 分布與雙軸 AF 差異。
- **ComplexHeatmap (v2.16.0)**: R 熱圖套件，補上聚類 dendrogram 呈現神經節之間的整體 clonal 關係。
- **clustered variant 排除**: 把 ID06 的 late clone local expansion variants 從估算中剔除，避免單一晚期 clone 的巨大 AF 蓋掉早期 clone 訊號。

5. 與此篇文章的關係:

在《Developmental organization of sensory and sympathetic ganglia》這篇文章中，作者為了回答「NC clone 到底是被脊椎位置分群、還是被神經節種類分群」這個世紀爭議，把 MPAS 驗證後的 mosaic variant 用 geoclone 描到人體 body plan 圖上，再以 rolling-3-level rostrocaudal vs dorsoventral SD 的 Mann-Whitney U 檢定量化比較。這解決了「直接看 geoclone 是主觀、SD 對 sample size 敏感易產生假訊號」的雙重瓶頸，為「clone 沿頭尾軸連貫、沿背腹軸斷裂」提供了統計基礎；下游 hypergeometric 模型才能在此基礎上推估 fate split 與 L/R split 的祖細胞群大小。
