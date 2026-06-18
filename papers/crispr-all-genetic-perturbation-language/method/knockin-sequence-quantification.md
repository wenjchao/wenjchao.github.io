# Knockin coding sequence 量化 (kallisto/bustools alignment to custom codon-optimized reference)

1. 引用自哪篇 paper: crispr-all-genetic-perturbation-language
2. Outline (任務主線): Knockin coding sequence 量化 (kallisto/bustools alignment to custom codon-optimized reference)
3. Method:
   作者塞進細胞的 knockin 基因不是直接抄人類自己的版本。他們會先做一道「同義改寫」(codon optimization)：胺基酸序列保持不變，但盡量換成人類細胞翻譯起來最順手的密碼子，順便把可能被細胞誤剪掉的位點消掉。改寫後的 DNA 拼字跟內源版本差很多——同一個蛋白卻長得像「外國版字典」。標準單細胞定序對齊軟體 Cellranger 是拿著「人類內建字典」(GRCh38) 去查每段 read 屬於哪個基因，外國版拼字對不上，所以這些讀數會被當成沒對到任何基因直接丟掉。後果是每顆細胞的「真的表達了哪個外來基因」這件事在轉錄組裡看不到——但作者已經用條碼幫每顆細胞配上「應該裝了哪個 knockin」的標籤，且條碼在合成過程會發生 barcode swapping (條碼跟實際裝進去的基因對不上)；沒有第二套獨立證據，這些指派錯誤就抓不出來。

   解法是另做一本「只收外國版」的小字典。作者把所有要塞進細胞的 codon-optimized 序列——各種 CAR 訊號零件、過表達的人類基因、合成基因，再加上每個構築上游都共有的標記蛋白 tNGFR 與 CAR 共通段——通通寫進一份自製參考序列檔 (custom fasta)；連共通段都放進去，是為了讓落在這段的讀數也能被認出是「knockin 表達群」的一員，提高訊號量。Cellranger 不能讀自製字典，所以對齊工具換成 kallisto v0.46.2 與 bustools v0.41.0 這對姊妹工具：kallisto 是快速假對齊器，不去追究 read 落在染色體哪一格，只判斷它應該屬於小字典裡哪一條序列，速度很快、且能直接吃自製 fasta；bustools 專門處理 10X 單細胞資料的條碼與 UMI。整條流程拆成「拆包裹、對名字、排隊、計數」四個動作：`kallisto bus --tech 10xv3` 拆包裹，把 10X v3 讀數分成細胞身分條碼 (cell barcode)、分子身分條碼 (UMI)、cDNA 序列三段，並把 cDNA 對自製字典做假對齊；`bustools correct` 對名字，把細胞條碼跟 10X 官方白名單比對一次，定序機讀錯一個鹼基也可以還原回去；`bustools sort` 排隊，把所有記錄按細胞、分子、序列三層排好；`bustools count` 計數，數每顆細胞讀到了哪個 knockin、各讀了幾條獨立分子，最後生出一張「細胞 × knockin」的計數表。每個 10X lane 獨立跑一次，避免不同批次互相污染。算完的計數表用 Seurat 的 `AddMetaData` 黏進原本的單細胞物件，每顆細胞就同時有「條碼說裝了什麼」和「mRNA 證明真的表達了什麼」兩套標籤可以對照 (Fig S6J)。

   為什麼一定要弄出第二套真值？因為條碼指派只是間接證據——它說「這顆細胞讀到了 11 個字母的條碼 X」，卻不能直接證明真的表達了基因 X。PacBio 長讀定序顯示，單類別子庫只有 74–92% 的構築條碼跟元件對得起來，剩下的就是 barcode swapping 造成的指派錯誤。sequence-based 量化則是直接從 mRNA 看到「細胞真的在表達哪段 codon-optimized 序列」，這個證據鏈跟條碼的雜訊完全無關。兩套答案一致時，這顆細胞的指派就高信心；不一致就剔除。不過這套 sequence 驗證有應用邊界：knockout 用的 Cas12a gRNA、knockdown 用的 miR-E shRNA 都只有不到 100 個鹼基，太短了，kallisto 的假對齊抓不穩。只有 OE 基因與 synthetic gene 這類完整 ORF 夠長才能在自製字典裡被認出，所以這套 orthogonal validation 只覆蓋四類擾動裡的兩類。

   如果偷懶不做自製字典、直接拿 Cellranger 對 GRCh38，比對率基本是 0——它把每顆細胞的 knockin 表達量算成 0，跟「這顆細胞真的什麼都沒裝」分不出來。於是 barcode 指派變成孤證：條碼說裝了 LTBR、卻沒有任何 sequence 訊號可以證實，barcode swapping 造成的指派錯誤無從抓出，下游 module score 與差異表達分析會被污染細胞拖偏。另一種比較輕微的失誤是自製字典做不完整：若只收各 knockin 各自不同的段、漏掉上游 tNGFR/CAR 共通段，落在共通段的讀數會找不到家被丟掉。不會誤指派，但每顆細胞分到的 knockin 訊號量被砍掉一截——本來該被認出的細胞可能因訊號太弱被判定「沒裝」，敏感度下降，跟 barcode 的交叉驗證就更難達成一致。

4. 工具與材料:
   - **codon optimization**: 同義改寫：胺基酸序列不變，但換成人類細胞翻譯起來最順手的密碼子，並消除可能被誤剪的 splice site。
   - **GRCh38**: Cellranger 用的「人類內建字典」——標準人類參考基因組，找不到 codon-optimized 改寫過的外來序列。
   - **Cellranger**: 10X Genomics 官方的單細胞定序對齊軟體，預設拿 GRCh38 去查每段 read 屬於哪個基因。
   - **custom fasta reference**: 作者自製的「只收外國版」小字典，包含所有 codon-optimized CAR 訊號零件、OE 基因、合成基因，加上 tNGFR 與 CAR 共通段。
   - **kallisto v0.46.2**: 快速假對齊器：不追究 read 落在染色體哪一格，只判斷屬於字典裡哪條序列，可直接吃自製 fasta。
   - **bustools v0.41.0**: kallisto 的姊妹工具，專門處理 10X 單細胞資料的條碼與 UMI，跑 correct → sort → count 三步。
   - **cell barcode / UMI**: 10X v3 化學讀數開頭的兩段條碼：前者標記細胞身分、後者標記每條獨立 mRNA 分子。
   - **AddMetaData (Seurat)**: 把外部計數表黏進 Seurat 單細胞物件的函式，讓每顆細胞同時帶 barcode 與 sequence 兩套標籤。
   - **orthogonal validation**: 兩套互相獨立的真值——barcode 指派 vs sequence 量化——交叉核對，過濾 barcode swapping 造成的錯誤指派。
   - **barcode swapping**: 池化迭代克隆過程中條碼跟實際裝進去的元件對不上的現象；PacBio 顯示單類別 fidelity 約 74–92%。

5. 與此篇文章的關係:
   在《A unified genetic perturbation language for human cellular programming》這篇文章中，作者要證明 CRISPR-All-seq 抓到的單細胞擾動指派是可信的。為此他們採用了 kallisto/bustools 對自製 codon-optimized fasta 的假對齊流程，解決了 Cellranger 用 GRCh38 對齊不到 codon-optimized knockin 序列的瓶頸。這條 pipeline 吃 10X 原始 fastq，輸出每顆細胞的 knockin 表達計數，當作 barcode 指派的旁證，過濾掉 barcode swapping 造成的污染細胞。
