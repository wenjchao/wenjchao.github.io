# Lentiviral landing pad cassette 構築

1. 引用自哪篇 paper: chromatin-structure-regulatory-activity
2. Outline (任務主線): Lentiviral landing pad cassette 構築
3. Method: 
   作者要在 K562 染色體上「先預鑄一塊塊插座」，之後才有辦法精準替換內容。他們把一段事先設計好的 DNA cassette 包進慢病毒 (Lentivirus)——一種能把外來 DNA 永久黏進細胞染色體的運輸工具，讓病毒把 DNA 隨機釘進細胞基因組的某個位置。慢病毒兩端原本帶有長重複片段 (LTR)，自帶啟動子會吵醒附近基因；作者把這個啟動子拆掉變成「整合後自己關機」(self-inactivating LTR)，避免污染後續訊號量測。每塊插座上面都刻著一個只屬於自己的 12 個鹼基的位置條碼 (gBC)，當作這塊插座的座標身分證；12 個鹼基排列出來有 $4^{12} \approx 1.7 \times 10^7$ 種，遠多於需要區分的細胞株數，幾乎不會撞號。Cassette 末端再加一段穩定 RNA 尾段的元件 (WPRE)，讓未來從這塊插座轉錄出來的 reporter mRNA 不容易被分解，定序時訊號才夠。

   插座中間 `loxFAS — CMV — Hyg/TK — P2A — eGFP — loxP — gBC — WPRE` 這串元件是「一個 CMV 啟動子一次驅動三件事」的精巧設計。Hyg/TK fusion 把抗 Hygromycin 的酵素與 HSV 胸苷激酶 (thymidine kinase) 縫成一條蛋白：加 Hygromycin 時這群細胞活下來（正向篩選），想反過來殺掉同一群細胞時，加 Ganciclovir 就能透過 TK 把細胞代謝成毒物（負向篩選）。中間的 P2A peptide 是一段拆解碼——核糖體翻譯到這裡時故意「跳過一個鍵」(ribosomal skipping)，前段蛋白直接從核糖體掉出來、後段繼續被翻譯，結果一條 mRNA 同時產出 Hyg/TK 與 eGFP 兩條獨立蛋白。eGFP 是綠色螢光蛋白，留給後續 FACS 挑選用。Cassette 兩端再分別放 loxFAS 與 loxP 兩款不對稱的方向辨識凹槽 (Lanza et al. 2012)；Cre 重組酶只認「同款配同款」，loxFAS 配 loxFAS、loxP 配 loxP，異款之間不反應。靠這個不對稱配對，後續 Cre 介導置換只能以「同方向、剛好一次」完成，不會把 CRS 接反或反覆切換。

   為什麼非要把 Hyg 跟 TK 縫成一條，而不只放一個 Hygromycin 抗性就好？因為作者需要兩種篩選力：先靠 Hygromycin 挑出已整合 cassette 的細胞，之後 Cre-lox 置換完還要靠 Ganciclovir + TK 殺掉「沒置換」仍帶原 cassette 的細胞。如果把這兩個基因分別用獨立啟動子驅動，表現比例容易跑掉，可能出現只表現 Hyg 卻不表現 TK 的細胞，到時候負篩就失靈；縫成融合蛋白 (Wong et al. 2005, Addgene 11684) 等於把鑰匙正反兩面綁死，兩種篩選力永遠成對存在。額外再塞 eGFP 進來也不是多此一舉——Hygromycin 只能告訴你「有沒有 cassette」，eGFP 卻能提供 FACS 等級的單細胞分選；更妙的是，後續 Cre 置換成功時整段 `Hyg/TK-P2A-eGFP` 會被換掉、GFP 訊號消失，這時反向挑「GFP 變暗」的細胞就能富集成功置換的群體。eGFP 同時兼任「初代挑單細胞」與「未來判斷置換成功」兩種任務。

   兩個設計細節如果省掉，整個實驗會壞在哪？第一個是 self-inactivating LTR：一般慢病毒 LTR 自帶啟動子，整合進染色體後會持續吵醒附近基因，把讀數整片污染——作者要量的是 CRS 開關活性，但訊號裡會混進 LTR 自帶的廣播，根本分不清哪部分是 CRS 的功勞。第二個是 lox 位點的不對稱性：如果兩端都用同款 loxP，Cre 會把 transfer vector 隨機方向裝進去，甚至裝完又被切走，置換永遠停不下來；只有 loxFAS / loxP 兩款不同 lox 配對才能鎖死「方向唯一、剛好一次」的置換結果。
4. 工具與材料: 
   - **Lentivirus (self-inactivating)**: 能把外來 DNA 永久釘進細胞染色體的運輸工具；兩端 LTR 啟動子被拆掉，整合後自己關機，不再干擾鄰近轉錄訊號。
   - **CMV promoter**: 強且持續開啟的啟動子，這裡用來驅動 `Hyg/TK-P2A-eGFP` 整條 mRNA。
   - **Hyg/TK fusion**: 抗 Hygromycin 酵素與 HSV 胸苷激酶縫成一條蛋白 (Wong et al. 2005, Addgene 11684)；加 Hygromycin 正向篩選、加 Ganciclovir 反向殺光。
   - **P2A peptide**: 讓核糖體翻譯到中段時跳鍵 (ribosomal skipping) 的拆解碼，使一條 mRNA 產出 Hyg/TK 與 eGFP 兩條獨立蛋白。
   - **eGFP**: 綠色螢光蛋白，作為 FACS 單細胞分選與 Cre 置換成功的雙重指示燈。
   - **loxFAS / loxP**: 兩款不對稱方向辨識凹槽 (Lanza et al. 2012)；Cre 只認同款配同款，強迫後續置換以唯一方向且剛好一次完成。
   - **gBC (genomic barcode)**: 12 個鹼基的位置條碼，緊鄰 loxP 下游；$4^{12} \approx 1.7 \times 10^7$ 種組合，作為每塊插座的座標身分證。
   - **WPRE**: 加在 3' UTR 的穩定 RNA 尾段元件，讓 reporter mRNA 累積足夠多以供定序。
   - **NheI + BamHI cloning**: 把整段 cassette 插入 self-inactivating lentiviral backbone 的兩個限制酶切位。
5. 與此篇文章的關係: 
   在《A massively parallel reporter assay dissects the influence of chromatin structure on cis-regulatory activity》這篇文章中，作者要量化 CRS 與染色質環境如何共同決定基因表現。為此他們需要「同一段 CRS 能被穩定放進基因組上多個已知位置」，因此先構築這個 self-inactivating 慢病毒 landing pad cassette。這個 cassette 解決了「沒有錨點就無法定點置換」的瓶頸，產出帶 gBC 標記的隨機整合事件池，作為下一步建立 clonal landing pad 細胞株的原料。
