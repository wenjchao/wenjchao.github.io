# 體外重複刺激 (Repetitive Stimulation) 池化篩選實驗系統

1. 引用自哪篇 paper: crispr-all-genetic-perturbation-language
2. Outline (任務主線): 體外重複刺激 (Repetitive Stimulation) 池化篩選實驗系統
3. Method:
   編輯完 6 天的 CAR-T 細胞先抽出來當「刺激前」(Input)，剩下的丟進培養皿跟活的癌細胞 (Nalm6) 一起養。CAR-T 認到癌細胞會啟動、增殖、把癌細胞殺光；過 2–3 天作者再送一批新的 Nalm6 進去，逼 T 細胞再啟動一次——這樣反覆 6 輪、約 2 週，把臨床上 CAR-T 在病人體內不斷遭遇新癌細胞的「慢性刺激」壓縮到培養皿。最後再抽一次細胞 (Chronic Stimulation)。Nalm6 本身是人類急性 B 淋巴白血病細胞 (ATCC)，表面本來就有 CD19；作者又把一段強啟動子插在內源 BCMA 基因起始位置前，FACS 分選出穩定 BCMA+ 的細胞，這樣同一株既能被 CD19 CAR 也能被 BCMA CAR 攻擊，省去重複建系。讀出用兩種：第一是條碼擴增定序 (amplicon-seq) 把每個 library member 的條碼比例從 Input 到 Chronic Stimulation 拉出來——比例上升就是勝出；第二是流式儀加固定濃度的 CountBright Plus 計數珠，把存活 CAR-T (NGFR+) 與 Nalm6 (CD19+) 換算成絕對數量，看 T 細胞擴了幾倍、癌細胞被壓到多低。

   為什麼「每 2–3 天送一批新 Nalm6 連續兩週」就能對應臨床 CAR-T 的耗竭？T 細胞每次認到癌細胞、CAR 訊號被點燃，會啟動一波活化、增殖與殺傷；如果短時間反覆遇到抗原，細胞內部的 exhaustion 程式（一群跟 NR4A、TOX、NFAT 相關的轉錄因子）就會被推上來——表面 PD-1、TIM-3、LAG-3 上升、殺傷與增殖能力同時下滑，正是臨床上 CAR-T 一段時間後失效的狀態。體外把這件事壓縮成「每 2–3 天遇到新癌細胞、連續兩週」，能在培養皿裡把腫瘤微環境裡幾個月的壓力濃縮成兩週看完。

   幾個參數都不是隨便挑的。效應細胞對目標細胞比例 (E:T) 設在 1:8，代表 T 細胞少、Nalm6 多，等於把 T 細胞放進「被癌細胞淹沒」的處境，跟臨床上腫瘤微環境的真實壓力比較像；比例倒過來（10:1）的話，一兩天內癌細胞就被殺光、沒有第二輪的抗原刺激，做不出 exhaustion，比例再壓低 T 細胞會直接被吞沒。每個 library member 平均要分到至少 1000 顆成功編輯的 T 細胞做為起始覆蓋，否則 input 的隨機抽樣抖動會大過真正的擴增差異，定序時根本看不出哪個改造在增多。至於 6 輪刺激 (~2 週)，是過去 Lynn 與 Roth 等人的重複刺激模型中「exhaustion 表型已經出來，但細胞還沒整批死光」的時窗——早於這個點看不出差異，晚於這個點訊號被消滅。

   這套系統幾個常見的壞法：E:T 拉到 10:1 會在第一輪就把 Nalm6 全部清掉，後面 5 輪沒對手——讀數變成「誰急性殺得快」而不是「誰能撐過慢性消耗」，跟要篩的 persistence 表型對不上；只做一輪也一樣，所有改造都還在第一波增殖期、條碼比例還沒拉開差距就停手，整池讀起來像沒有任何改造有效。覆蓋度沒到時更隱蔽：某個 member 起始只分到 50 顆細胞，input 抽到的條碼數就已經像在賭骰子，可能單純隨機沒抽到就被誤判成「慢性刺激後消失」。最後是適用範圍——這套擂台用的是 CD19-28ζ (Yescarta) 當背景 CAR，挑出的最強改造組合會跟 28ζ 這個訊號零件的生理特性綁在一起；換成 4-1BBζ 或對手換成實體腫瘤時排行榜次序可能就會洗牌。所以這個讀數要看成「在 CD19-28ζ + B-ALL 模型下的 persistence 排行榜」，不是「在病人體內絕對最強」。

4. 工具與材料:
   - **Repetitive Stimulation**: 每 2–3 天送一批新 Nalm6 進 CAR-T 培養皿、共 6 輪約 2 週，把腫瘤微環境的慢性抗原暴露壓縮到體外，是觀察 persistence 與 exhaustion 的標準功能讀出。
   - **Nalm6 BCMA+ CD19+**: 人類急性 B 淋巴白血病細胞株 (ATCC)，內源就帶 CD19；作者額外把 SFFV 啟動子插在內源 BCMA 起始位置前並 FACS 分選 BCMA+，做成可被 CD19 與 BCMA CAR 雙靶向的對手細胞。
   - **E:T = 1:8**: 效應細胞對目標細胞比例設成 T 細胞少、Nalm6 多，逼 T 細胞反覆被抗原淹沒，是能撐到第 6 輪又能持續刺激的折衷點。
   - **CD19-28ζ / Yescarta**: 第二代 CD19 CAR (上市產品 Yescarta) 作為背景 CAR；整個篩選結果都綁在這款訊號零件上。
   - **amplicon-seq**: 把細胞基因組裡的 CRISPR-All 條碼擴增後上 NextSeq，計算每個 library member 在 Input 與 Chronic Stimulation 之間的條碼比例變化。
   - **CountBright Plus**: 流式時加入的固定濃度計數珠，把樣品中 CAR-T (NGFR+) 與 Nalm6 (CD19+) 換算成絕對細胞數，提供 amplicon-seq 之外的獨立讀數。
   - **1000× coverage**: Pooled screen 統計力門檻，每個 library member 在 input 至少分到 ~1000 顆成功編輯的 T 細胞，否則隨機抽樣抖動會蓋過真實擴增差異。
   - **exhaustion 程式**: CAR 反覆刺激後驅動的 NR4A / TOX / NFAT 轉錄程式，伴隨 PD-1 / TIM-3 / LAG-3 表面上升與殺傷增殖能力下降；是這套模型要篩出「能抵抗它」的改造的目標。

5. 與此篇文章的關係:
   在《A unified genetic perturbation language for human cellular programming》這篇文章中，作者為了在同一座功能擂台上排出所有 CRISPR-All 擾動的優劣，採用了體外重複刺激 (Repetitive Stimulation) 系統作為 CACTUS meta-library 與 10,240-member 組合 library 的功能讀出。它解決了「臨床 CAR-T exhaustion 只能在病人體內看到、無法在培養皿快速比較大量擾動」的瓶頸，把連續兩週反覆遇到 Nalm6 的處境壓縮成 amplicon-seq 可量化的條碼豐度變化，直接餵給下游條碼比對與 DESeq2 統計分析。
