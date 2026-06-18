# Homology-search 演算法（補強 DSB-score 的 off-target 偵測）

1. 引用自哪篇 paper: rationally-engineered-cas9-nucleases
2. Outline (任務主線): DSB-score 僅能找出最強的 OT；論文額外設計 homology 評分把更多疑似 Cas9-induced cluster 從背景中拉出來，補足 BLESS sensitivity。
3. Method:

BLESS 全基因組剖析雖然不挑位置，但它收到的訊號裡同時混著「Cas9 真的剪斷」的痕跡和「細胞自己平常就會留下的隨機斷裂」(background DSB) 兩種來源。前一步沿用 Ran et al. Nature 2015 的 DSB-score (protocol 見本論文 Methods 引用 ref 21) 作為第一道濾網——它看每個位置兩側讀數的尖峰形狀，分數高的就是「斷得很整齊、像 Cas9 切的」。問題是這道濾網只能撈出訊號最強的那幾個脫靶位點 (bona-fide off-target)；中低訊號的真 OT 會被埋進背景、被當雜訊丟掉。對這篇論文來說後果很嚴重——作者要證明 eSpCas9(1.1) 在「全基因組層面也沒新冒出 OT」，如果濾網漏掉一堆中低訊號 OT，結論會直接滑成偽陰性的「看起來沒新 OT」。所以作者再補一層判斷，不看訊號強弱，改看「序列像不像 Cas9 該剪的地方」。

補強濾網的做法分三步。第一步先把 BLESS 在每個位置記到的局部斷點集群 (DSB cluster) 取其座標的中位點 (median)，當作「Cas9 真正下刀的中心點」——比起平均值，中位點更不會被偶發雜訊讀數拉偏。第二步以這個中心點為錨，往左右各拉 50 個鹼基當作搜索視窗：BLESS 對下刀點的定位精度本來就在幾十個鹼基的尺度，±50 nt 剛好把真正的 cut site 包進來、又不會把太多無關位置一起拉進來污染。第三步在這個視窗裡標出所有 NGG 與 NAG 出現的位置——這 3 個鹼基的「門牌」叫 protospacer-adjacent motif (PAM)，是 Cas9 下刀前一定要先認得的訊號，所以掃描時不掃 PAM 沒蓋到的位置等於先把「Cas9 機制上根本不可能剪」的地方剔除。針對每個 PAM，從它上游往左數 20 個鹼基當候選 protospacer，跟 20 個鹼基的 sgRNA 一個字母一個字母對齊；然後視窗向旁邊移一格、再找下一個 PAM、再對一次，像拿一把固定寬度的尺沿著 DNA 一格一格滑過去——這就是 sliding-window scanning。

每次對齊都會打出一個相似度分數 (homology score / similarity score)，權重是：對得上的字母 match = +3，對不上的字母 mismatch = −1，sgRNA 與 DNA 之間多一個或少一個字母 (insertion / deletion) = −5。三類權重的差距對應 Cas9 真實的生化偏好——Cas9 對 PAM 遠端的 mismatch 本來就有點容忍，所以扣 1 分輕罰；但對 sgRNA 和 DNA 中央擠出一個鼓包 (bulge) 的 indel 極度敏感、幾乎切不動，所以扣 5 分重罰。如果把 indel 懲罰調得跟 mismatch 一樣輕，演算法會允許大量「序列中央鼓一個包」的對齊也拿高分，把背景位置誤判成 OT，閾值線就守不住乾淨的分離。一個 cluster 視窗裡會掃出很多個 PAM 候選、各自打出一個分數；演算法只取「視窗裡最高分的那一個對齊」作為這個 cluster 的代表分數——因為 Cas9 既然在這個 cluster 真的剪了，一定是用其中對得最好的那個位置下刀。20 個鹼基的 guide 全對加 3 個鹼基的 PAM 全對等於 $20 \times 3 + 3 \times 3 = 69$ 分，這是 perfect on-target 的滿分上限——cluster 的 homology score 越接近 69，就越像「Cas9 該剪的地方」。

閾值 > 50 並不是先驗挑的，而是資料給出來的天然斷崖——作者拿 BLESS 排名前 200 的斷點集群，每個都回去用 targeted deep sequencing 量真實 indel，確認哪些是 bona-fide OT、哪些是背景；把這 200 個依 homology score 排開，會看到 > 50 的那群全部驗得到 indel、≤ 50 的那群全部驗不到，兩群完全不重疊，所以 50 是「不漏 OT、不撈背景」的最佳切點。掃描時把 NGG 跟 NAG 都納入也是為了不漏掉 OT——SpCas9 主要靠 NGG 下刀，但生化上 NAG 也能用，已知部分真 OT 就落在 NAG 上，只挑 NGG 會把這群整批漏掉。在最終的 OT 判定上，論文同時保留 DSB-score 與 homology score 兩個指標：前者問「BLESS 訊號上這裡到底有沒有真的被剪」，後者問「這段序列從演化上像不像 Cas9 會找的地方」；有的位置 DSB-score 很高但序列其實不像 OT（背景熱點），有的位置序列很像但訊號太弱（過去會被漏掉）——雙軸排序才能把這兩類錯誤同時擋住。Table S3 同時列 DSB 與 Similarity Score 兩欄，並把 13 個 VEGFA(1) 候選與 5 個 EMX1(1) 候選 OT 跨三個 Cas9 變體 (WT / K855A / eSpCas9(1.1)) 並列比較——可以看到 eSpCas9(1.1) 在這些候選 OT 上的 rep 1/2 indel% 多數降為 0，正好支撐主結論。

4. 工具與材料:

   - **DSB cluster**: BLESS 在每個位置記到的局部斷點集群；同一個 Cas9 剪刀痕跡會回放成附近一小段位置上聚集的多個斷點。
   - **Cluster median**: DSB cluster 內所有斷點座標的中位點，用來當「Cas9 真正下刀的中心點」，比平均值更耐雜訊。
   - **搜索視窗 ±50 nt**: 以 cluster median 為錨，往左右各拉 50 個鹼基作為 homology 搜索範圍；對應 BLESS 幾十 bp 的定位精度。
   - **PAM (NGG / NAG)**: protospacer-adjacent motif，Cas9 下刀前必須先認得的 3 個鹼基門牌；SpCas9 主要用 NGG，低效率下也能用 NAG。
   - **Sliding-window scanning**: 在搜索視窗內逐位移動，對每個 NGG / NAG 上游取 20 bp guide-match 並與 sgRNA 比對的掃描法。
   - **Homology score (Similarity Score)**: 對齊產生的相似度分數，權重為 match +3、mismatch −1、insertion / deletion −5；對應 Cas9 對 mismatch 容忍但對 bulge 敏感的生化偏好。
   - **Perfect on-target score = 69**: 20 bp guide 全對 (60) + 3 bp PAM 全對 (9) 的滿分上限；cluster 分數越接近 69 越像真 OT。
   - **Cluster 取最大值**: 視窗內所有 alignment 中取最高分作為 cluster 的 homology score，避免被同窗內無關 PAM 拖低。
   - **Threshold > 50**: 在前 200 BLESS DSB loci 中，homology score > 50 可完全分離 bona-fide OT 與背景；由 targeted deep sequencing 驗證得出的天然斷崖。
   - **DSB-score (Ran et al. Nature 2015)**: 前一道濾網，看 BLESS 在 cut site 兩側讀數的尖峰形狀；只能撈到訊號最強的 OT，需 homology score 補強。
   - **Table S3**: 並列 13 個 VEGFA(1) 與 5 個 EMX1(1) 候選 OT 的 Similarity Score、DSB score、rep 1/2 indel%，跨 WT / K855A / eSpCas9(1.1) 三個變體比較。

5. 與此篇文章的關係:

這篇 paper 要證明改造後的 eSpCas9(1.1) 與 K855A 在全基因組層級不會冒出新的脫靶（off-target, OT），因此用 BLESS 不偏地標出所有 DNA 雙股斷裂（DSB）後，需要把「Cas9 真的剪的」從「細胞自己平常就會留下的背景斷裂」中區分出來。前一步沿用 Ran et al. 2015 的 DSB-score 看訊號形狀，但這道濾網只能撈出最強的幾個 OT，中低訊號的真 OT 會被埋進背景，使陰性結論有「只看 top hits 就下定論」的風險。homology-search 在此補位：它換一個完全不同的維度，直接檢查 DSB cluster 附近的序列像不像 sgRNA 該認的地方，靠 PAM 為錨、滑動視窗對齊、以 match +3 / mismatch −1 / indel −5 的權重打分，並以閾值 > 50 把 BLESS 前 200 個 cluster 切成真 OT 與背景兩群。它的好處是把 BLESS 的 sensitivity 拉高、又不至於誤抓背景，盲點與 DSB-score 不重疊，雙軸排序才能同時擋住「序列像但訊號弱」與「訊號強但序列不像」兩類錯誤。下游則接回 targeted deep sequencing 對每個候選 OT 量真實 indel%，最終匯整到 Table S3，與 DSB-score、三個 Cas9 變體的 indel 數據並列，撐起「改造版沒有新 OT」這個主結論。
