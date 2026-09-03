# Wnt1-Cre;TdTomato 早期胚 NC 單細胞 RNA-seq

1. 引用自哪篇 paper: developmental-organization-sensory-sympathetic-ganglia
2. Outline (任務主線): Wnt1-Cre;TdTomato 早期胚 NC 單細胞 RNA-seq
3. Method:

為了在剝離 (delamination) 前後不同時間點翻開 NC 的表現量帳本，作者用了一組會「只在 NC 起源細胞裡自動亮紅」的小鼠：Wnt1-Cre × R26R-LSL-TdTomato。原理是 Wnt1 這個啟動子只在 NC 打開、讓細胞裡出現 Cre 重組酶；另一條染色體上 ROSA26 位點事先塞了「LoxP - STOP - LoxP - TdTomato」，STOP 平常擋住紅螢光。Cre 一出現就把 STOP 剪掉，紅螢光永久打開——祖先曾是 NC 的細胞及其所有後代都會亮紅。作者取三個關鍵時間點的胚胎軀幹：剝離幾乎還沒開始 (E8.5)、剝離正在啟動 (E9.0)、已經剝離一段時間 (E9.5)，覆蓋 NC 剝離的整段窗口。組織解離後用螢光細胞分選 (FACS) 把 TdTomato+ 挑出，送進 10x Chromium 這個「把單顆細胞包進油滴、每顆貼上獨立條碼」的平台建 3′ library，再上 NovaSeq X 定序，就拿到每顆 NC 在各時間點表現哪些基因的完整表格。這裡的「pre-EMT NC」指的是還沒啟動上皮到間質轉換 (epithelial-to-mesenchymal transition, EMT)、仍緊貼神經管背面的那批 NC——剝離動作還沒發生，正是作者要盯緊的階段。

但是光靠 TdTomato 還不夠。它是「一旦亮就永遠亮」的紅燈——只能告訴你這細胞的祖先曾是 NC，卻分不出「現在是還沒剝離 (pre-EMT) 還是正在剝離 (delaminating)」。作者再靠兩個只在特定階段才會被打開的內生標誌基因當即時鐘：Zic1 在 pre-EMT NC 才高表現、Sox10 在剛要剝離的 NC 才高表現，這樣就能把紅細胞再切成「pre-EMT」與「delaminating」兩堆分別統計。接著檢查的關鍵基因是「感覺命運驅動轉錄因子」(Neurog1/2、Neurod1、Pou4f1) 與「交感命運驅動轉錄因子」(Ascl1、Phox2b)——它們不是「已經分化完成」才有的成品標記，而是「命運選擇的開關手」，前人研究已知打開它們的細胞就會走上感覺或交感路線。所以只要在 pre-EMT NC 裡就抓到一批細胞同時打開兩個以上感覺 driver、另一批打開交感 driver，就等於在「發車前」就看到駕駛已經拿了往東或往西的車票，直接支持「fate 早於剝離」。

為什麼一定要 FACS 先分再上 10x？因為 NC 只佔軀幹一小部分——作者實測 E8.5 約 5%、E9.0 約 10%、E9.5 約 15%，其餘都是神經管、體節、外胚層等其他細胞。整團 tissue 直接進 10x Chromium 的話，油滴裡絕大多數會是非 NC，切成 pre-EMT / delaminating 兩堆之後可能各剩不到一百顆，UMAP 上根本 cluster 不出 pre-EMT NC 這個小群，統計基礎就崩了。這也是為何各時間點都要 pool 至少兩窩胚胎才夠——早期胚太小、NC 太少，得靠併樣補樣本量。至於三時間點為何刻意只差 0.5 天？因為剝離這件事幾乎就在 E8.5–E9.5 這一天內密集發生。時間拉太遠（例如比到 E10.5）晚期樣本的 NC 已經開始成熟成 neuron/glia，感覺 / 交感 driver 的表現變成「已經下游的細胞」本來就有的特徵，就無法回答「剝離當下 fate 選好了嗎」這個原始問題。密集取樣才能剛好卡在命運決策的窗口。

這套設計有兩個一失守整條論證就報廢的環節。第一：如果不用 Zic1 / Sox10 把紅細胞再切成 pre-EMT vs delaminating 兩堆，直接把所有 TdTomato+ 細胞混一起看感覺 / 交感 driver，就算真的看到很多細胞開了感覺 driver，也會被反駁「這搞不好是那批正在剝離的細胞開的」——完全區分不出「命運早於剝離」與「命運跟剝離同時發生」。第二：如果作者拿的是「感覺神經元成熟後才有」的成品標記而不是 driver 轉錄因子，pre-EMT NC 幾乎不會表現，訊號會弱到看不到，反而會得出「pre-EMT NC 完全還沒選命運」的假結論。作者的做法剛好是精準挑「命運選擇的第一批推手」——它們是「已經上車、還沒開到終點」的階段才會打開，才能捕捉到命運剛選、分化未完的關鍵時刻。

4. 工具與材料:

- **Wnt1-Cre**: 只在 NC 起源細胞裡打開 Wnt1 啟動子、進而製造 Cre 重組酶的小鼠品系，用來把「祖先曾是 NC」的細胞標記出來。
- **R26R-LSL-TdTomato**: ROSA26 位點上「LoxP - STOP - LoxP - TdTomato」的報導基因，Cre 一出現就永久打開紅螢光。
- **FACS**: 螢光細胞分選 (fluorescence-activated cell sorting)，靠 TdTomato 紅光把 NC 從軀幹雜質中挑純。
- **10x Chromium Single Cell 3′ (v4)**: 把單顆細胞包進油滴、每顆貼上獨立條碼的單細胞 RNA-seq 平台。
- **NovaSeq X**: Illumina 高通量定序機，用來把 10x 建好的 library 一次定序到需要的深度。
- **EMT**: 上皮到間質轉換 (epithelial-to-mesenchymal transition)，細胞從彼此緊貼的上皮狀態鬆開成可獨立爬行的間質狀態，是 NC 剝離的必經程式。
- **Zic1**: 還沒剝離的 pre-EMT NC 才高表現的標誌基因，用來把 pre-EMT NC 挑出來單獨統計。
- **Sox10**: 正在剝離 (delaminating) 的 NC 才高表現的標誌基因，用來把剝離中的 NC 挑出來單獨統計。
- **sensory driver TFs (Neurog1/2、Neurod1、Pou4f1)**: 前人研究已知能推 NC 走感覺路線的一組命運驅動轉錄因子。
- **sympathetic driver TFs (Ascl1、Phox2b)**: 前人研究已知能推 NC 走交感路線的一組命運驅動轉錄因子。

5. 與此篇文章的關係:

在《Developmental organization of sensory and sympathetic ganglia》這篇文章中，作者為了回答「NC 的感覺 vs 交感命運是在剝離前還是剝離後才選好」這個世紀爭議，用 Wnt1-Cre;TdTomato 小鼠加上 10x Chromium single-cell RNA-seq，在 E8.5–E9.5 剝離窗口密集取樣 pre-EMT 與 delaminating NC。這解決了「無法直接檢視人類早期胚胎」的瓶頸，並把「命運早於剝離」的推論從單純 clonal barcode 訊號升級為 driver 轉錄因子表現的直接分子證據，為下游 RNA velocity 動力學分析與臨床神經母細胞瘤起源的重新定位提供 transcriptome 基礎。
