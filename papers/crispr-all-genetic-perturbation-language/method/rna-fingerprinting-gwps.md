# RNA Fingerprinting 跨擾動相似度 (RNAFingerprinting against GWPS reference)

1. 引用自哪篇 paper: crispr-all-genetic-perturbation-language
2. Outline (任務主線): RNA Fingerprinting 跨擾動相似度 (RNAFingerprinting against GWPS reference)
3. Method:
   作者要回答的問題是：CRISPR-All-seq 在 T 細胞上抓到的擾動表型（MED12 KO、TCF7L1 OE 等），有沒有在「全人類基因擾動的指紋大百科」裡找到對應？這裡的「投影」是隱喻，底下是真實數學動作——CRISPR-All-seq 在 T 細胞做 MED12 KO 影響的全基因表達變化可以寫成一條長向量（每個基因都有一個上下調的數字），這就是這個擾動的「指紋」。Reference 選的是 GWPS (Genome-Wide Perturb-Seq, Replogle et al. 2022)：他們把 CRISPRi 系統性地把 K562 慢性骨髓白血病細胞株裡近一萬個人類基因一個個關小，再逐顆細胞讀轉錄組，目前是唯一覆蓋全人類基因的 Perturb-Seq 資料庫，所以即使細胞型不一樣也是「指紋百科」的唯一現成版本。其他 Perturb-Seq 通常一次只挑幾百個 target，會出現「查不到」的死角；GWPS 的全基因覆蓋消除這個歧義。

   比對怎麼做？RNAFingerprinting 套件（作者用 v0.0.0.900，搭配 RNAFingerprintingData v0.1.0 提供已處理的 GWPS reference）把 query 指紋寫成 reference 所有指紋的加權混合（$y = X \beta + \epsilon$），$\beta$ 就是「query 由 reference 中各擾動貢獻多少分」的權重表。這個寫法比「兩條向量直接做相關」更能在近萬個 reference 裡找到真正的單一對應，而不會被一堆部分相關的擾動稀釋掉訊號。內部用 Bayesian regression 算每個權重的後驗分布——這比 cosine similarity 多了一個關鍵能力：每個係數都附信賴區間，把「點數高且很穩」跟「點數高但不穩」明確區分開來。為什麼這個區分重要？GWPS 裡有些擾動只測了幾十顆細胞，那條指紋本身雜訊大；如果用 cosine similarity，只會看到一個點數例如 0.81，分不出是「真的像」還是「雜訊湊出的像」。Long Island City plot 上會出現一堆假高峰誤導結論。Bayesian regression 給的信賴區間能直接把雜訊高峰標成「寬區間 = 不可信」，避免被假訊號帶偏。

   視覺化部分用套件預設的 Long Island City plot：x 軸把 GWPS 資料庫裡所有近萬個擾動依某種順序排成一長條（形狀像紐約 Long Island City 沿河看出去的高低天際線），y 軸是 query 對每個擾動的 Bayesian regression 係數，並畫出信賴區間，最像 query 的擾動在圖上冒出尖峰。作者用這張圖標出 CRISPR-All-seq 的 MED12 KO 與 TCF7L1 OE 在 GWPS 中找到了對應擾動 (Fig S7C)。如何解讀跨細胞型的對應？作者並不要把 K562 跟 T 細胞畫等號——這次分析的目的是找「跨細胞型保留」的核心擾動程式。MED12 是 RNA pol II 的 Mediator 複合體成員，它影響的轉錄調控機制在大多數人類細胞共通；GWPS 在 MED12 那一頁跟 T 細胞看到的指紋對得起來，反而強化了「這個訊號真的是 MED12 的核心程式」這個結論。至於 T 細胞特異的擾動效果，這個分析本來就會回報「沒對應」——這是預期內、不是缺陷。

4. 工具與材料:
   - **GWPS (Genome-Wide Perturb-Seq)**: Replogle et al. 2022 發表的 K562 全基因 CRISPRi Perturb-Seq 圖譜，目前唯一覆蓋近萬個人類基因的擾動指紋大百科。
   - **K562**: 慢性骨髓白血病細胞株，GWPS 用的底盤細胞；與本研究的 T 細胞不同型，但仍可比對跨細胞型保留的轉錄程式。
   - **RNAFingerprinting v0.0.0.900**: Satija lab 釋出的跨擾動相似度比對 R 套件；把 query 指紋寫成 reference 指紋的加權混合，用 Bayesian regression 算貢獻權重。
   - **RNAFingerprintingData v0.1.0**: 同套件提供的預處理 reference 資料包，含 GWPS 處理好的擾動指紋矩陣，省去 query 端自行下載重算的步驟。
   - **Bayesian regression**: 迴歸方法之一，輸出每個係數的後驗信賴區間；比 cosine similarity 多一個「相似度是否穩固」的判斷依據。
   - **Long Island City plot**: 套件預設的視覺化：x 軸把 reference 擾動排一長條，y 軸是 query 對應每個擾動的 Bayesian 係數與信賴區間，尖峰即為對應擾動。
   - **Mediator 複合體 (MED12)**: RNA pol II 共活化子的核心成員之一；它影響的轉錄調控機制在大多數人類細胞共通，所以 K562 vs T 細胞的指紋仍可對應。
   - **全基因 fold-change vector**: 把某擾動下每個基因的上下調倍率排成一條長向量，每個 entry 對一個基因；query 與 reference 的指紋都用這個格式表示。

5. 與此篇文章的關係:
   在《A unified genetic perturbation language for human cellular programming》這篇文章中，作者要進一步證明 CRISPR-All-seq 抓到的 MED12 KO 與 TCF7L1 OE 表型對應到的是基因本身的核心程式、而不是 T 細胞或新平台的雜訊。為此他們採用了 RNAFingerprinting 對 GWPS reference 的跨擾動投影，解決了「沒有 T 細胞版本的全基因 Perturb-Seq」這個瓶頸。這個方法吃 CRISPR-All-seq 的 query 擾動 fold-change 向量、產出 Long Island City plot 上的對應擾動與信賴區間，作為「跨細胞型保留」結論的旁證。
