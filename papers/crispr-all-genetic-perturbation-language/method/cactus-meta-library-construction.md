# CACTUS meta-library 之文獻 meta-analysis 與子庫合成

1. 引用自哪篇 paper: crispr-all-genetic-perturbation-language
2. Outline (任務主線): CACTUS meta-library 之文獻 meta-analysis 與子庫合成
3. Method:
   作者把 1990-01-01 到 2024-06-30 的文獻、專利與臨床試驗用同一套關鍵詞撈過一遍，篩出 613 篇相關文獻 + 75+ 個過去做過的 T 細胞 pooled / arrayed screen。然後把所有報告過「改這個基因會讓 T 細胞變強」的候選集中起來，去掉重複後得到一張 460 個獨立基因 / 設計的清單，再依改造類別拆成 7 個子庫，每個給一個植物代號方便識別：Cardon 收 5 個已上市的全長 CAR；Fishhook 收各種 CAR 抗原辨識 (binder) domain；Kingcup 收 43 個 CAR 內部訊號 domain；Saguaro 收 80 個天然基因的過表達 (OE)；Prickly Pear 收 48 個合成基因；Cholla 收 230 個基因 knockout（Cas12a 三聯 gRNA）；Torch 收 225 個基因 knockdown（miR-E shRNA）。七庫合起來叫 CACTUSv1 meta-library，共 636–652 個獨立 member (Tables S8, S16)，到下游 pooled screen 才把全部子庫混回同一池跑。

   為什麼要拆子庫？因為合成路徑不同。基因類（Cardon / Fishhook / Kingcup / Saguaro / Prickly Pear）每個 member 幾百到幾千鹼基，作者用 TWIST 或 Thermo 做 clonal gene synthesis——廠商把每個基因合成成獨立、純度高的片段，再逐條 NGS 驗證序列無誤後上 CRISPR-All cloning。小 RNA 類（Cholla 的 Cas12a 三聯 gRNA、Torch 的 miR-E shRNA）每條只有幾十到一百多鹼基，作者改用 TWIST / IDT 做單股 DNA 寡核苷酸池 (ssDNA oligo pool)——一次合成成千上萬條混在一池裡，再用 CRISPR-All 設計好的 5′/3′ External Stuffer primer 跑 10 cycle PCR 把 ssDNA 轉成可以克隆的 linear dsDNA。基因序列在合成前還要做兩層 codon optimization：第一層是換掉密碼子但不改胺基酸，讓序列用上人類細胞最偏好的密碼子提高翻譯效率；第二層是 TWIST API 或自寫腳本另外掃一輪，把序列裡長得像 splice site 的同義密碼子也換掉——這是因為 CRISPR-All 把 cloning scar 故意塞在內含子裡靠 spliceosome 剪掉，coding region 本身又長得像 splice site 的話內源 spliceosome 會誤切 coding region。

   為什麼這一翻譯之後就能跨類別頭對頭比？以前每篇研究用各自的 CAR 設計、cytokine 條件、刺激模型、讀數方式，技術差異本身就能造成排名差異——A 論文說 X 是 hit、B 論文說 Y 是 hit，不代表 X 比 Y 強，只代表他們在不同擂台上比。CRISPR-All 把所有 target 翻譯到同一架構、塞進同一個 background CAR (CD19-28ζ)、跑同一個 repetitive stimulation 模型、用同一條 amplicon-seq + DESeq2 流程。DESeq2 公式寫成 `~ Donor + Condition`：把 8 個 donor 的個體差異當固定變數扣掉，再看剩下的差異中哪些是 Input → Chronic Stimulation 條件帶來的，輸出每個 member 的 log2 fold change 與 adj P-value，拉高的就是抗 exhaustion 的 hit。為了再多一層雜訊校正，作者在 TRAC 同源臂後額外塞了 5 條 backbone barcodes——它們在每個 construct 都共享同一組、不分 target，扮演「同一 construct 內的技術重複」：5 條之間若豐度差異很大，就是合成、PCR、定序的技術噪聲在作祟，這個基線可以拿來校正每個 library member 真正的訊號。

   這套流程跳過幾個步驟都會壞。第一，若不做 CRISPR-All 標準化、直接把 30 年文獻的 target 用各家原始設計湊一池跑：每個 target 還帶著原本的 promoter、vector、條碼系統，技術變數讓某些 target 條碼天生比較容易擴增——你看到的 hit 全部分不清是生物訊號還是技術假象。第二，若只做標準 codon optimization、不掃 splice site：基因序列剛好含預測的 splice donor / acceptor 時，內源 spliceosome 會把 coding region 中段也當 intron 剪掉，蛋白做不完整，這個 library member 在 screen 裡會看起來像「沒效果」，其實是被自己的剪接機器破壞了。第三，若為了省錢把 Saguaro 的 80 個天然基因 OE 模組也改用 ssDNA oligo pool 做：ssDNA oligo pool 單條長度上限約 200 鹼基、錯誤率比 clonal synthesis 高一個數量級，又因為一次幾千條混在一池裡無法逐條 NGS 驗證；80 個天然基因平均長度遠超 200，硬塞 oligo pool 會大量做出嵌合產物 (chimera) 與 indel，整個 library 從源頭爛掉。所以基因模組必須走更貴但乾淨的 clonal gene synthesis。

4. 工具與材料:
   - **Systematic literature meta-analysis**: 1990–2024 跨 publications / patents / clinical trials 的統一關鍵詞檢索，篩出 613 文獻 + 75+ 個 T cell pooled/arrayed screen，輸出 460 個獨立 enhancement target 候選名單。
   - **Cardon / Fishhook / Kingcup / Saguaro / Prickly Pear / Cholla / Torch**: 七個 CACTUS 子庫的代號，分別對應 5 個 FDA-approved 全長 CAR、CAR binder domain、43 CAR signaling domain、80 天然基因 OE、48 合成基因、230 基因 knockout、225 基因 knockdown。
   - **CACTUSv1 meta-library**: 七子庫合併後共 636–652 個獨立 member，全部走 CRISPR-All 同一架構，是首次讓五大擾動家族在同一系統頭對頭比較的標準化 library。
   - **Clonal gene synthesis (TWIST / Thermo)**: 基因類子庫的合成路徑：每個 member 由廠商獨立合成成純度高的片段，逐條 NGS 驗證後上 CRISPR-All cloning；適合幾百到幾千鹼基的 OE 或 domain 模組。
   - **ssDNA oligo pool (TWIST / IDT)**: 小 RNA 類子庫的合成路徑：一次合成成千上萬條短 ssDNA 混在一池，再用 External Stuffer primer 跑 10 cycle PCR 轉成 dsDNA；適合幾十到一百多鹼基的 gRNA / shRNA 模組。
   - **External Stuffer primer 10 cycle PCR**: 把 ssDNA oligo pool 轉成可克隆的 linear dsDNA 的步驟；cycle 數壓低是為了減少 oligo 之間互換接成嵌合產物。
   - **Codon optimization with splice-site removal**: 雙層密碼子優化：除了配合人類偏好密碼子提高翻譯效率，另外掃描並用同義密碼子替換預測的 splice donor / acceptor，避免內源 spliceosome 誤切 coding region。
   - **Backbone barcodes (×5)**: 每個 construct 共享的同一組 5 條條碼，提供 pooled screen 內部技術重複；5 條之間的豐度差異反映合成 / PCR / 定序的技術噪聲基線。
   - **DESeq2 `~ Donor + Condition`**: 把 8 位 donor 的個體差異當固定變數扣掉後，再看 Input → Chronic Stimulation 條件帶來的條碼豐度變化，輸出每個 member 的 log2 fold change 與 adj P-value。

5. 與此篇文章的關係:
   在《A unified genetic perturbation language for human cellular programming》這篇文章中，作者為了首次讓 30 年來分散在不同論文裡的 T cell enhancement target 能在同一個 CAR-T 模型上頭對頭比較，採用了 CACTUS meta-library 的「文獻 meta-analysis + 七子庫差異化合成 + CRISPR-All 標準化克隆」流程。它解決了過去 single-perturbation-class 研究因 CAR 設計、刺激模型、條碼系統各異而無法跨類別比較的瓶頸，將 460 個候選翻譯成 636–652 個標準化 member，直接餵給下游重複刺激篩選與 DESeq2 分析。
