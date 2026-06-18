# mRNA 架構之 Cas12a gRNA-array 多重 knockout 與 miR-E shRNA knockdown (Pol II–driven mRNA architecture for small-RNA effectors)

1. 引用自哪篇 paper: crispr-all-genetic-perturbation-language
2. Outline (任務主線): mRNA 架構之 Cas12a gRNA-array 多重 knockout 與 miR-E shRNA knockdown (Pol II–driven mRNA architecture for small-RNA effectors)
3. Method:
   細胞裡有兩台轉錄機器：Pol II 寫蛋白質基因的 mRNA，Pol III (常配 U6 啟動子) 本來只用來做 tRNA 這類短 RNA、傳統 gRNA/shRNA 就是借這條路。作者反其道而行，把 gRNA 與 shRNA 直接縫在「會被翻譯成蛋白質的 mRNA」尾巴 (3′UTR，即終止密碼子與 polyA 之間的非翻譯區段)，整條交給 Pol II 寫。前面的蛋白質照樣正常翻譯，後面的 small RNA 則靠別的酵素從 mRNA 上剪下來。為了讓「剪」這件事順利，作者在 3′UTR 上把三件事接成一排。第一段是 Triplex RNA 穩定元件——它折成 RNA 三股結構把 mRNA 尾段捏緊，擋住細胞質裡從 polyA 啃進來的外切酶。接下來才是主角。做 knockout 時，主角是同基因三條 gRNA 串成的 Cas12a 三聯 gRNA array (Cas12a 本身帶 pre-crRNA 自切活性，會在串接處把長 RNA 剪成三條獨立 mature gRNA)；Cas12a 蛋白靠電穿孔時外加一份 enCas12a mRNA 提供。做 knockdown 時，主角換成 miR-E scaffold——把 shRNA 包裝成像細胞自己的 microRNA 前驅體，於是細胞核的 Drosha 與細胞質的 Dicer 兩把內源剪刀會把它剪下、處理成 mature siRNA 去降解目標 mRNA，完全不需要外加酵素。作者拿 B2M、CD47、CD226、CD2 四個 T 細胞表面受體做示範，因為表面蛋白能直接用抗體流式染色逐顆細胞讀出敲除率，比測 RNA 直接得多。

   把炸藥拼進卡車後車廂 (3′UTR) 而不是放在自走砲車上的好處，是 Pol II 寫出來的 RNA 要被細胞認可成「正式 mRNA」並送出細胞核，必須湊齊完整啟動子、5′UTR、coding sequence、polyA、剪接修飾——這套品質檢驗是漂在細胞質裡尚未整合的環狀 DNA (episomal plasmid) 拿不到的，寫出來的 RNA 很快被當廢料處理。一旦構築透過 enCas12a 切斷的 TRAC 位點被 HDR 縫進染色體，整段才會被當正規基因表達。所以 small RNA 只在卡車正式停進染色體車庫後才會引爆，沒整合的細胞完全沒有擾動發生。整條 3′UTR 是三組獨立的加工反應接力：Triplex 把尾段捏緊保護不被降解、Cas12a 用自身 RNase 活性把 gRNA array 剪成三條獨立 gRNA、或 Drosha 與 Dicer 把 miR-E 處理成 mature siRNA。三組酵素互不干擾，這就是為什麼 small RNA 與 protein-coding gene 能同框組裝。

   為什麼作者要費這麼大工夫把 small RNA 從 U6 改搬到 Pol II mRNA？U6 是 Pol III 啟動子，只要構築進細胞、不管染色體有沒有接住它，U6 都會狂寫 gRNA。作者實測：U6 構築讓還沒成功整合 (KI−) 的細胞身上也產生 69% 的 CD47 knockout，整體細胞毒性高達 90%——大量本該當「未編輯對照」的細胞自己也被打殘。對 pool screen 來說這是致命的：條碼定序時看到某個構築變少，搞不清楚是擾動讓細胞變弱還是 U6 毒性把細胞先殺光。換成 Pol II mRNA 架構後，KI− 背景的 off-target knockout 壓到 <7%、毒性壓回 ~20%。挑 B2M、CD47、CD226、CD2 這四個基因做示範也是務實考量：它們都是 T 細胞表面受體，能直接被抗體染色、用流式逐顆細胞讀出敲除率；單一 knockout 達 60–80%、四重同時做仍維持 69–86%，確認架構不會因為塞了四套 small RNA 而互相打架或外溢。

   假設偷懶沿用 U6 會踩到兩條死路。第一，構築一進細胞 U6 就生產 gRNA，整顆細胞群裡有 69% 在「還沒整合就先被擾動了」的狀態下生長，這群細胞沒有 barcode 整合進染色體、後續定序讀不到，但它們的死活已經影響整個細胞池的構成。第二，90% 毒性殺掉的不是均勻分布的細胞，是對該 gRNA 比較敏感的細胞，等於變相在做選擇性篩除，pool screen 的初始 frequency 已經偏掉了。Triplex 不放也不行——細胞質的外切酶會從 polyA 那端啃進來，下游 gRNA array 或 miR-E 還沒被加工就先被降解，敲除效率掉一截。最後，Cas12a 與三聯 gRNA 是配套設計：單一 gRNA 一次只切一個位點、效率大約 30–50%；三聯同時切讓 knockout 衝到 60–80%。為什麼必須選 Cas12a 而不是 SpCas9？因為 Cas12a 自己會剪自己的 gRNA array，串成一條進細胞後它自動切成三條獨立 gRNA；SpCas9 沒有這個自切活性，連 array 都送不出去，knockout 效率歸零。

4. 工具與材料:
   - **Pol II (RNA Polymerase II)**: 細胞自己用來寫蛋白質基因 mRNA 的轉錄機器；本架構靠它的「需要完整啟動子—5′UTR—coding—polyA」品質檢驗來實現「沒整合就不表達」。
   - **U6 啟動子 (Pol III)**: 細菌專用、Pol III 驅動的小 RNA 啟動子，傳統 gRNA/shRNA 都借這條路，但因為不管 DNA 整合與否都狂寫 small RNA，造成 episomal off-target 與毒性，本架構刻意放棄。
   - **3′UTR**: mRNA 上終止密碼子與 polyA 之間的非翻譯區段；作者把 gRNA array / miR-E shRNA 縫在這裡，前面蛋白質照常翻譯不受影響。
   - **Triplex RNA 穩定元件**: 一段折成 RNA 三股結構的序列，放在 3′UTR 上游把 mRNA 尾段捏緊，擋住細胞質外切酶從 polyA 啃進來。
   - **Cas12a 三聯 gRNA array**: 同基因三條 gRNA 串成一排的 RNA 結構；Cas12a 本身帶 pre-crRNA 自切活性，會在串接序列把長 RNA 剪成三條獨立 mature gRNA，提升單一基因 knockout 效率至 60–80%。
   - **enCas12a**: 增強型 Cas12a (AsCas12a 變體)，本實驗以 mRNA 形式電穿孔提供活性酵素，同時負責切 TRAC 位點與切 array 出 mature gRNA。
   - **miR-E scaffold**: Fellmann et al. 2013 設計的 shRNA 骨架，把 shRNA 包裝成像細胞自己的 microRNA 前驅體，由內源 Drosha + Dicer 處理成 mature siRNA 降解目標 mRNA，不需外加酵素。
   - **Drosha / Dicer**: 細胞自有的兩把 microRNA 加工剪刀：Drosha 在細胞核切 pre-miRNA、Dicer 在細胞質再剪成 mature siRNA，負責把 miR-E shRNA 從 mRNA 上剪下並處理。
   - **episomal plasmid**: 還沒整合進染色體、漂在細胞質裡的環狀 DNA；U6 構築在這裡也狂寫 gRNA 造成 off-target，但 Pol II mRNA 架構在這裡寫不出可用 mRNA。
   - **TRAC 位點**: T 細胞 T 細胞受體 alpha chain 所在的染色體固定地址，本架構用 enCas12a 切開後 HDR 把整段構築縫進去，作為「成功整合」的單一判準。
   - **tNGFR**: 截短版 NGFR 表面標記，與 CRISPR-All 構築同框表達，作為「這顆細胞成功整合」的流式判讀指標。
   - **B2M / CD47 / CD226 / CD2**: 四個 T 細胞表面受體，用來示範四重 knockout；因為是表面蛋白，可直接用抗體流式染色逐顆細胞讀出敲除率。

5. 與此篇文章的關係:
   在《A unified genetic perturbation language for human cellular programming》這篇文章中，作者為了在原代 T 細胞同時跑多基因 knockout / knockdown，採用了 Pol II mRNA-embedded small-RNA 架構，把 gRNA array 與 miR-E shRNA 塞進 3′UTR。這解決了傳統 U6 構築在未整合細胞也狂寫 gRNA、造成 69% off-target knockout 與 90% 毒性的瓶頸，讓只有成功整合進 TRAC 的細胞才會被擾動。產物是一條乾淨可組裝的構築，直接餵給下游 CACTUS pool screen 做 barcode 對應的功能讀出。
