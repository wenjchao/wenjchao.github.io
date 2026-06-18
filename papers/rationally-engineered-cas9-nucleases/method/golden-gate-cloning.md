# Golden Gate Cloning 製作 Cas9 點突變庫

1. 引用自哪篇 paper: rationally-engineered-cas9-nucleases
2. Outline (任務主線): 高通量、無縫地把 31 個單點突變、34 個多點組合，以及 SaCas9 的對應突變導入 Cas9 哺乳動物表現質體，作為 specificity 篩選的素材。
3. Method:

作者要逐字改寫 SpCas9 這個酵素的胺基酸序列。第一輪是 31 個單點突變：把 nt-groove 中 31 個帶正電的胺基酸位點，一次只改一個，逐個換成電中性的丙胺酸 (alanine substitution)。第二輪是 34 個組合突變：把第一輪表現最好的幾個位點疊起來、做在同一條 Cas9 上。同樣的策略也搬到 SaCas9，產出 12 條對應的單點與雙點突變。所有改好的 Cas9 都要裝回能在人類細胞裡開機表達的質體裡——SpCas9 用 pX330（Zhang lab 既有質體，內含為人類細胞最佳化的 SpCas9 ORF 加 sgRNA 插槽）、SaCas9 用同套餐的 pX601。為什麼不用傳統的定點突變 (site-directed mutagenesis)？因為要做 ~65 條質體，逐條跑 PCR 太慢；而且很多舊式 cloning 在接點會留下幾個額外鹼基當疤痕，對 Cas9 這種一字之差就改變功能的長 ORF 來說，疤痕本身就是新突變，會把實驗讀數污染掉。所以作者選了 Golden Gate cloning——一種能「同時切＋黏」、接點不留多餘鹼基的無痕拼裝法 (protocol 來自 Engler et al. 2009 PLoS One)。

Golden Gate 的核心動作分三步：把 Cas9 序列用 PCR 拆成左右兩段、把兩段 PCR 產物連同已經切開的受體載體一起丟進同一管反應液、再加一款特殊切刀 (BsaI 或 BbsI)。這款切刀為什麼特別？普通限制酶（如 EcoRI）就在它認的那段序列正中央剪一刀，剪完留下的黏端永遠跟識別碼綁在一起、不能改；BsaI 與 BbsI 則屬於 Type IIS 切刀——「認在這裡、剪在那裡」：識別位與切點是分開的，認完之後往下游固定幾個鹼基才下刀，留下 4 個鹼基的黏端 (4-nt overhang)。關鍵是這 4 個鹼基不在識別位裡面，所以可以由使用者在引子上自由寫。作者在每條 SpCas9 引子的 5′ 端綁了 `ATGGTCTCA` 標籤：`GGTCTC` 是 BsaI 的識別碼，後面跟著預先寫好的 4 鹼基客製黏端。PCR 跑出來的片段兩端都帶這個標籤。BsaI 進場後認到 `GGTCTC` 就往下游 1 鹼基剪一刀，把標籤連同識別碼一整段切掉、丟掉，最終構築裡完全找不到 `GGTCTC` 的痕跡——這就是「無痕 (scarless)」的意思。SaCas9 換用 BbsI、5′ 標籤是 `ATGAAGACTA`，原理一樣。

點突變（例如 K810A）到底是怎麼在 Golden Gate 接點「拼出來」的？作者把每條 Cas9 拆成兩段 PCR 跑：左半段一路擴增到突變位前一格就停、右半段從突變位後一格開始一路擴增到尾，兩段在突變位這裡相接。秘訣是負責拼接的那 4 個鹼基黏端，作者直接在引子裡寫成突變後的密碼子（例如要把 K 改成 A，黏端就含 alanine 的密碼子）。左段尾端的黏端、右段開頭的黏端、加上中間的 4 鹼基新密碼子，BsaI 切完之後三者一拼，密碼子就自動換好 (codon swap)，整條 Cas9 ORF 重新縫起來時這個位置已經是突變版。同一個位置想做不同突變，只要換引子就好——所以 Table S1 才需要列出 96 條 primer，每條 primer 都把標籤、識別碼與一個特定突變密碼子組合好；31 個位點 × 多種突變才能用同一套標準流程量產。

為什麼選 Golden Gate 而非別的方案？如果改用 Gibson assembly，接點要留 20–40 鹼基的同源臂讓兩段「相認」，這些同源臂會永久留在最終質體上、無法做到真正的無痕。Golden Gate 只需要 4 個鹼基黏端就能定義拼裝順序，黏端寫在引子裡可程式化、反應一鍋搞定、做完無痕，是通量、無痕、客製化三件事的最佳折衷。受體載體的兩個切口為什麼要用 AgeI 與 EcoRI？因為 pX330/pX601 上要被替換的那段 Cas9 序列剛好被這兩個天然切點夾住。作者先用 AgeI＋EcoRI 把這段切掉、把載體變成一條「兩端各有獨特黏端」的線性骨架；同時刻意把左 PCR 片段最左端的 BsaI 黏端設計成跟 AgeI 切口相容、右 PCR 片段最右端的黏端設計成跟 EcoRI 切口相容。三塊（左 PCR、右 PCR、線性骨架）只有一種拼法能讓所有黏端完美配對，確保拼錯方向的副產物近乎為零。為什麼 SpCas9 用 BsaI、SaCas9 卻換成 BbsI？因為 Type IIS 酶要做到「只切標籤、不切 Cas9 本體」，前提是 Cas9 ORF 內部碰巧沒有這款酶的識別碼。SpCas9 的 4 kb 序列裡天然沒有 `GGTCTC`（BsaI 識別碼）但有 `GAAGAC`（BbsI 識別碼），SaCas9 則相反——所以兩款 Cas9 被迫各配各的酶。

這套流程有三類失敗模式要小心。第一，黏端鹼基寫錯：4 個鹼基是兩段 PCR 接合的唯一密碼，引子上寫錯一個字母會讓兩端對不齊、整管反應液裡只剩散落的片段，轉化大腸桿菌長不出菌落；更糟的狀況是錯誤黏端剛好跟「不對的」片段互補、拼出 frame-shift 的廢蛋白。Table S1 整整列出 96 條 primer，每一條的 5′ 標籤都要嚴格檢查，不能寫錯一個字。第二，Cas9 ORF 內出現識別碼：BsaI 是無差別切刀，看到 `GGTCTC` 就剪，如果 ORF 中段碰巧也有 `GGTCTC`，反應一啟動切刀會把 Cas9 中段也剪一刀、把要拼回去的字當場剪壞——這就是為什麼酶必須配 ORF 序列、SpCas9 配 BsaI、SaCas9 配 BbsI。第三，拼完不定序：PCR 過程中聚合酶可能隨機把某個字母抄錯，如果不挑單菌落 Sanger 定序確認，這條質體可能除了故意改的 K810A 之外還偷偷帶了沒打算改的副作用突變；後續測 specificity 時看到效果改善，根本分不清是來自 K810A 還是副作用突變——整批篩出來的「明星突變」可能根本不是它本身的功勞。

4. 工具與材料:

   - **Golden Gate cloning**: 一鍋同時切+黏的無痕拼裝法 (Engler et al. 2009 PLoS One)，用一款 Type IIS 切刀加客製黏端，把多片段一次組裝、接點不留多餘鹼基。
   - **Type IIS restriction enzyme**: 識別位與切點分家的特殊限制酶；「認在這裡、剪在那裡」，因此可以在引子上自由寫客製黏端。
   - **BsaI**: Type IIS 切刀，識別碼 `GGTCTC`，往下游 1 鹼基切出 4 個鹼基黏端；SpCas9 突變庫使用。
   - **BbsI**: Type IIS 切刀，識別碼 `GAAGAC`；SaCas9 ORF 內天然不含此識別碼，因此 SaCas9 突變庫改用 BbsI。
   - **4-nt overhang**: Type IIS 酶切割後留下的 4 個鹼基黏端，序列可由引子自訂；Golden Gate 用這 4 個鹼基定義拼裝順序，並把點突變密碼子直接嵌在這裡。
   - **pX330**: Zhang lab 常用的哺乳動物表現質體，內含為人類細胞最佳化的 SpCas9 ORF 與 sgRNA 插槽；作為 SpCas9 突變庫的模板質體。
   - **pX601**: pX330 的 SaCas9 版本；作為 SaCas9 突變庫的模板質體。
   - **AgeI / EcoRI overhang**: pX330/pX601 受體載體上夾住要被替換的 Cas9 區段的兩個天然切口；Golden Gate 的左右 PCR 片段黏端被設計成分別跟 AgeI 與 EcoRI 切口相容。
   - **ATGGTCTCA / ATGAAGACTA**: 引子 5′ 端的標籤序列：前者用於 SpCas9 (BsaI 識別碼 `GGTCTC` + 1 鹼基緩衝 + 客製黏端起點)；後者用於 SaCas9 (BbsI 識別碼 `GAAGAC` + 2 鹼基緩衝)。
   - **Codon swap**: Golden Gate 點突變的核心技巧：把突變後的密碼子直接寫進左右 PCR 接合處的 4 鹼基黏端，拼裝時自動把 WT 密碼子換成突變密碼子。
   - **Alanine substitution**: 把某個胺基酸換成電中性、側鏈最簡單的丙胺酸，用以「拔掉」該位點原本的化學貢獻；本論文用來中和 nt-groove 31 個帶正電位點。
   - **Site-directed mutagenesis (對比方法)**: 傳統定點突變法：每改一個位點都要把整條質體跑一輪長 PCR，慢且通量低；Golden Gate 是其替代方案。
   - **Single-point mutant / Combinatorial mutant**: 本研究的兩階段產物：第一輪 31 條 SpCas9 單點 alanine 突變 + 12 條 SaCas9 對應單/雙點突變；第二輪把 SpCas9 上效果最佳的單點疊成 34 條組合突變。

5. 與此篇文章的關係:

這篇論文的研究核心是改造 SpCas9 來提升 specificity，作者先從晶體結構鎖定 nt-groove 上 31 個帶正電的候選殘基，接下來必須把這份「結構假說清單」物理上轉成一批可送進人類細胞的點突變質體，否則整套機制假說無法被實驗檢驗——Golden Gate Cloning 正是把假說轉成材料的關鍵環節。作者要平行產出 31 條 SpCas9 單點 alanine 突變、34 條多點組合，以及 SaCas9 對應的 12 條突變共近 80 條質體，傳統 site-directed mutagenesis 必須一條一條跑長 PCR，通量不夠且接點會留疤痕，會在 Cas9 這條一字之差就改功能的長 ORF 裡引入額外干擾；Golden Gate 借助 Type IIS 限制酶 (SpCas9 配 BsaI、SaCas9 配 BbsI) 把客製 4-nt 黏端寫在引子裡，能一鍋同時切＋接、接點無痕，並把目標位點的新密碼子直接嵌進拼接黏端，使「換哪個位點、換成什麼胺基酸」變成只改引子序列的標準化操作。在整條 pipeline 裡，本 module 緊接著結構引導的 nt-groove 殘基定位 (module 1)，把計算挑出的位點清單變成可表現的質體庫；產出的 pX330/pX601 衍生質體再進入 HEK293T 的 Cas9 + sgRNA 共轉染，後續才能由 targeted deep sequencing 與 BLESS 雙層 readout 量化 on-target 效率與 off-target 譜，最終篩出 eSpCas9(1.0)、eSpCas9(1.1) 兩條贏家變體。沒有這個高通量無痕的質體建構步驟，後面的篩選與全基因組驗證都失去素材。
