# 超幾何模型估計 NC fate specification 群體大小上/下限

1. 引用自哪篇 paper: developmental-organization-sensory-sympathetic-ganglia
2. Outline (任務主線): 超幾何模型估計 NC fate specification 群體大小上/下限
3. Method:

作者的目標是回答「NC 的感覺 vs 交感命運分家」跟「NC 剝離往左邊 vs 右邊分家」哪件事發生得早。他把神經節依兩種方式分組：一是 DRG vs SG（感覺 vs 交感），二是左邊 vs 右邊（L vs R）。對每個 mosaic variant 依它在 group1 與 group2 出現的比例分類：只出現在其中一 group 的叫 group-specific，代表這 variant 一定是「兩 group 已經分家後才蓋的印章」；兩 group 都以類似比例出現的叫 shared，代表這 variant 是「分家前就蓋在共同祖先上」。分類的具體閾值是 0.667 < rate1/rate2 < 1.5 算 shared、超過 1.5 倍差異算 enriched——這兩個數字剛好互為倒數 (0.667 = 1/1.5)，對兩邊對稱處理；1.5 倍是「明顯超過 PCR amplification bias 與隨機讀取雜訊、又不至於漏掉真訊號」的中庸位置。

兩類 variant 帶完全不同的資訊，因此各用一條公式反推。Group-specific variant：想像分家時祖先池 n 顆細胞裡只有 1 顆帶 heterozygous mosaic（兩條 allele 只有一條帶）；帶突變的 allele 在整個 pool 的 allele 總數 (2n) 裡佔 $\dfrac{1}{2n}$——這就是 mean AF，反解得到 $n = \dfrac{1}{2 \bar{\mathrm{AF}}}$。這是下限是因為若實際帶突變的祖細胞不止 1 顆，n 會更大。例如某個 SG-only mosaic 在 SG 的 mean AF 是 0.02，代表 SG 分家後祖先池下限 = $1/(2 \times 0.02) = 25$ 顆。Shared variant：用超幾何分布 (hypergeometric distribution) 的逐步模擬——這個分布描述「一袋 N 顆球裡有 K 顆紅球，不放回抽 M 顆，抽到 x 顆紅球的機率」。作者的問題完全對應：分家時祖先池 N 顆、K 顆帶 mosaic；分家瞬間池子被隨機切成兩堆，兩堆各自的 AF 差異就是隨機抽樣的結果。池子越小差異越大、池子越大差異越接近平均。作者從 n=0 掃到 10,000、每 step 10 個細胞算 hypergeometric CI，找出「能容納觀測 AF 差異的最大 n」當共同祖先池的上限。

為什麼 pop size 大小可以直接對應到發育早晚？因為胚胎發育是從一顆受精卵指數增殖（1 → 2 → 4 → 8 → …），時間越早細胞總數越少。所以任何一個 fate decision 發生時的祖先池大小直接對應那個時間點。作者算出來的結果是：DRG/SG 分家（fate split）的祖先池明顯小於 L/R 分家（side split）的祖先池——直接證明命運選擇發生在剝離之前（那時 NC 還沒左右分家）。這是把純統計量「AF 差異」翻譯成「發育時序」的核心邏輯，也是為什麼作者能用「事後才拿得到的成年遺體樣本」反推「無法直接觀察的早期胚胎命運決策」——這繞過了 clonal analysis 一直以來「拿不到人類胚胎」的根本困境。

這套推論有兩個必守的門檻。第一是必須把 ID06 的 clustered variants 事先剔除。local clonal expansion 是「某顆後期 clone 在有限空間大量擴增」，AF 會特別高（例如 0.2）；帶進 lower bound 公式會得到 $n = 1/(2 \times 0.2) = 2.5$ 顆這種荒謬答案，錯誤結論會變成「fate split 發生在只有 2–3 顆細胞的極早期」。這個高 AF 完全不代表起源族群小，只代表後期擴增很兇。第二是 group 定義閾值不能訂太寬。若閾值放到 0.9，很多其實已經 enriched 的 variant 會被錯歸為 shared 混進 upper bound 模擬，把上限拉得比真實共同祖先池還大、fate split 會被誤判發生比實際晚；同時 group-specific variant 數量會被抽走，lower bound 樣本量不夠、估算不穩定。1.5 倍門檻就是要在「shared 池夠純」與「specific 池夠多」之間找平衡。這兩個守門動作缺一，整個「fate 早於 side」的結論都會被雜訊蓋掉。

4. 工具與材料:

- **group-specific MV**: 只在 DRG 或只在 SG 出現（或只在左/只在右）的 mosaic variant，代表兩 group 分家後才蓋的印章。
- **shared MV**: 兩 group 都以類似比例出現的 mosaic variant，代表分家前蓋在共同祖先上。
- **group 定義閾值 (0.667 / 1.5)**: rate1/rate2 落在 [0.667, 1.5] 算 shared、超過 1.5 倍算 enriched；兩數互為倒數對兩邊對稱。
- **Lower bound 公式 $1/(2\bar{AF})$**: 假設 mosaic 由單一 heterozygous 祖細胞產生，反推 group 分家後祖先池的最小可能大小。
- **hypergeometric distribution**: 「N 顆球有 K 顆紅、不放回抽 M 顆」的機率分布，用來模擬分家時祖細胞池被隨機切成兩堆的過程。
- **Stepwise simulation (n = 0 to 10,000, step 10)**: 掃描 1,000 個 grid、對每個 n 算 hypergeometric CI，找出能容納觀測 AF 差異的最大 n 當共同祖先池上限。
- **clustered variant 排除**: 把 ID06 的 late clone local expansion variants 剔除，避免高 AF 讓 lower bound 荒謬地估到 2–3 顆。

5. 與此篇文章的關係:

在《Developmental organization of sensory and sympathetic ganglia》這篇文章中，作者為了判斷「NC 的感覺 vs 交感命運分家」與「NC 剝離往左 vs 往右分家」哪件事發生得早，用 group-specific MV 加公式 $1/(2\bar{AF})$ 算 pop size 下限、用 shared MV 加超幾何分布逐步模擬算 pop size 上限，直接把 MPAS 拿到的 AF 差異翻譯成分家當下的祖細胞群大小。這解決了「無法直接觀察人類胚胎早期命運決策」的根本困境，並在此基礎上支持「fate split 早於 side split」→ NC 是在還沒剝離、還在神經管上時就已經被指派感覺或交感命運——這個結論直接改寫了 60 年來的 NC 多能性辯論。
