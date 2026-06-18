# 條碼比對與 abundance 量化 (Barcode amplicon abundance analysis)

1. 引用自哪篇 paper: crispr-all-genetic-perturbation-language
2. Outline (任務主線): 條碼比對與 abundance 量化 (Barcode amplicon abundance analysis)
3. Method:
   這套分析的輸入是短讀定序機 (NextSeq) 吐出來的原始檔 (fastq)——一行一行 DNA 序列，每行對應「某顆細胞身上的擾動條碼被讀到一次」。為了把錢花在刀口上，作者不做全基因組定序，而是用 PCR 把含條碼的那段反覆複印放大 (amplicon-seq) 再丟去定序，每個 library member 至少讀到一千次。比對工具改用 R 裡專做生物序列的套件 Biostrings：先把所有設計好的 11 字母條碼編成電話簿索引 (PDict)，再拿每一條 read 去查 (vwhichPDict)，唯一規則是「完全一致才認」(zero mismatches)。看似太嚴，其實是設計上的妙招——條碼挑選時就要求任兩條至少差三個字母 (hamming distance ≥3)，含一個錯字的 read 看起來仍然跟原本的條碼最接近、不會誤指，嚴格比對只會安全濾掉不確定的 read。輸出是一張 Excel 風格的計數表，行是 652 個 (或 10,240 個) 構築、列是樣本，後面所有差異分析都建立在這張計數表上。最後把 Input (還沒被癌細胞挑釁前的條碼分佈) 跟 Chronic Stimulation (對打六輪兩週後再讀一次) 兩管計數丟進 DESeq2，算出每個構築的對數倍數變化 (Log2 Fold Change) 與多重檢定校正後的 p 值——倍數大代表這個改造讓細胞長得更壯、被選出來；倍數小或變負代表這個改造拖後腿。

   這條 pipeline 真正容易翻車的地方藏在兩個小細節裡。第一個是裁掉 AGCG 疤痕。AGCG 是 cloning 時 Type IIS 切口留下的四字母常數疤痕，所有條碼後面都接著它。但定序機碰到「整批 read 同一個位置都是同一字母」的常數區，雷射偵測會集體變鈍、品質下降，AGCG 容易被讀成 ANCG 或 AGCC。如果不先裁掉，這四個低品質字母會讓整條 read 跟字典不完全一致而被剔除，計數系統性偏低。作者寫了一段 bioawk 小腳本 (custom bioawk script) 在比對前統一削掉，留下乾淨的 11 字母去查表。第二個是 DESeq2 本身。直接拿原始計數相除有兩個盲點：每個樣本送進定序機的總 read 數本來就有差，深度差異會偽裝成倍數變化；條碼計數又是離散變數、小數量時雜訊極大。DESeq2 先用 median-of-ratios 把各樣本的總量差異算掉，再假設計數服從 negative binomial 分布——一個能同時描述「平均值」和「離散程度」的計數機率模型——用所有條碼一起估離散程度，最後才報每個條碼的 Log2 Fold Change 跟對應 p 值。這樣得到的倍數才公允、p 值才能信。

   DESeq2 的 design 寫成 `~ Donor + Condition` 不是隨手寫的。這次 screen 把 CACTUS library 同時打進 8 位健康捐贈者的 T 細胞，donor 之間 T 細胞本來就有體質差異——有人天生條碼 A 多、有人天生條碼 B 多，跟刺激無關。如果 design 只寫 `~ Condition`，這些 donor 差異會全部被當成隨機雜訊、訊號被淹沒；寫 `~ Donor + Condition` 等於告訴模型「先把每位 donor 自己的偏好扣掉，再看 Chronic vs Input 是否真的多/少」，8 位 donor 各自配對比較再合併，訊號就乾淨。另一個和條碼設計綁在一起的設計理由是 hamming distance ≥3 的硬規定。Illumina 平台每個鹼基大約 0.1–1% 機率讀錯，11 字母條碼出現一個錯字的機率落在 1–10%，每 10–100 條 read 就有一條帶錯。若只要求 hamming ≥2，一個錯字就可能把條碼 A 變得跟條碼 B 幾乎一樣、模糊地帶誤指。要求 ≥3 之後，含單一錯字的 read 看起來仍然跟原本的條碼最接近，不會被認錯。

   這套流程最容易壞掉的兩個情境都和「看起來無關緊要的細節」有關。第一個是跳過 AGCG trim 直接餵 raw fastq 給 vwhichPDict。zero-mismatch 規則意味著只要 read 尾端的 AGCG 被讀成 ANCG，整條 read 就會被視為查無此條碼直接丟掉；如果 Input 跟 Chronic 兩管的測序深度或品質略有不同，丟掉的比例會不一致，算出的倍數變化就帶著一層假訊號——你以為某個構築被選出來，其實只是 trim 沒做、計數被系統性壓低。第二個是只用 1 位 donor 跑這個 design：所有「Chronic vs Input 倍數差異」都跟這位 donor 的個人偏好綁在一起根本分不開，可能根本不是改造效果而是 donor 體質偏好；而且下一位病人 T 細胞會不會有同樣表現也沒辦法驗證，排行榜可能只對這一位捐贈者有效。8 位 donor 與 design `~ Donor + Condition` 兩件事是配套，少一個都不行。

4. 工具與材料:
   - **amplicon-seq (NextSeq)**: 用 PCR 把含 11 bp barcode 的那段反覆複印放大再丟去 NextSeq 短讀定序，每個構築達 ≥1000× 覆蓋度。
   - **fastq**: 短讀定序機輸出的原始檔，每行對應一條讀到的 read 與其品質。
   - **Biostrings PDict / vwhichPDict**: R 裡的條碼字典查表工具：PDict 把所有 11 bp barcode 編成電話簿索引、vwhichPDict 拿每條 read 完全一致地查表 (zero mismatches)。
   - **ShortRead readFastq**: R 套件 ShortRead 用來把原始 fastq 讀進 R 環境的函式。
   - **custom bioawk script**: 作者寫的小腳本，在比對前把 read 尾端的 AGCG 常數疤痕削掉，避免低品質字母拖累 zero-mismatch 比對 (參 reference 120)。
   - **hamming distance ≥3**: 11 bp barcode 之間至少差三個字母的最小編輯距離，使含單一定序錯誤的 read 不會誤指到另一條 barcode。
   - **DESeq2**: 差異豐度分析的 R 套件：用 median-of-ratios 校正樣本深度，再以 negative binomial 模型估計每個 barcode 的 Log2 Fold Change 與 adjusted p-value。
   - **design = ~ Donor + Condition**: DESeq2 的設計公式：先扣掉每位 donor 的個人偏好，再比較 Input vs Chronic Stimulation 的真實效應。
   - **Log2 Fold Change**: 「Chronic / Input」取對數倍數變化，倍數大代表改造讓細胞被選出來，倍數負代表拖後腿。

5. 與此篇文章的關係:
   在《A unified genetic perturbation language for human cellular programming》這篇文章中，作者要從 CACTUS meta-library 與 10,240 組合 library 的池化 T 細胞慢性刺激實驗中，公平比較數百到上萬個改造構築誰能讓細胞長得更壯。這套條碼比對與 DESeq2 分析吃的是 NextSeq amplicon-seq 的 fastq，產出的是「每個構築刺激前後的 Log2 Fold Change 排行榜」，直接餵給下游的 hit 篩選與組合分析。它解掉了「短條碼無法用 bowtie 比對」與「8 位 donor 體質差異會淹沒擾動訊號」兩個瓶頸。
