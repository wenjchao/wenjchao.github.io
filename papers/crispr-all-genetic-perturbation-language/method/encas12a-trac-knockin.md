# enCas12a mRNA + plasmid HDRT 非病毒 TRAC 位點 knockin (Non-viral knockin via electroporation)

1. 引用自哪篇 paper: crispr-all-genetic-perturbation-language
2. Outline (任務主線): enCas12a mRNA + plasmid HDRT 非病毒 TRAC 位點 knockin (Non-viral knockin via electroporation)
3. Method:
   作者要在 T 細胞「醒過來進入分裂」時動手——活化 Day 2 用磁鐵把 anti-CD3/CD28 Dynabeads 吸掉，然後把細胞重懸在 Lonza P3 緩衝液裡，混入四種試劑：enCas12a 蛋白的 mRNA（剪刀）、plasmid HDR template（帶 TRAC 同源臂的 CRISPR-All 構築，當裝潢圖紙）、U6 啟動子表達的 gRNA 質體（告訴剪刀去哪剪，靶向 TRAC intron 1）、與 helper plasmid（提升整合效率的輔助 DNA）。把這管溶液放進 Lonza 4D Gen2 電穿孔機 96 孔板，用 pulse code EO-151 打一個瞬間電脈衝，細胞膜上短暫開出小孔讓所有試劑被推進細胞。Cas12a mRNA 被翻譯成蛋白後接到 gRNA，再去 TRAC 第一個 intron 切一刀；細胞用同源重組 (HDR) 修補時，會以 plasmid HDR 兩端「跟 TRAC 一模一樣的同源臂」當範本，把整段 CRISPR-All 構築填進切口。為什麼選 Day 2？因為 HDR 只在細胞處於 S/G2 分裂期時才會被啟動，這時細胞已進入旺盛分裂期；Day 0 還在 quiescent 期的細胞會優先用直接亂黏修補，HDR 效率很低。電擊完馬上加 75 µL 預溫 XVivo 15、在 cuvette 中 37 °C 靜置 15 分鐘讓細胞封口、再轉到培養盤繼續長。

   Cas12a 進細胞有三種寫法：直接送蛋白 (RNP)、送 mRNA、送 DNA 質體。送 DNA 質體會讓 Cas12a 持續表達好幾天到一週，每多一次切割就多一次 off-target 機會；更糟的是 DNA 質體本身可能整合進基因組變成永久表達 Cas12a 的細胞，下游 CACTUS 篩選會分不清表型是構築的功勞還是 Cas12a 持續活性製造的偏差。送 RNP 雖然乾淨，但量大時試劑成本高、體積也大，pooled 大規模實驗難放大。送 mRNA 剛好折衷——mRNA 進細胞翻譯出 Cas12a 後幾小時內就被降解，剪刀「開一次就收掉」，又不會像 DNA 那樣有機會整合到基因組。enCas12a 是改良過的 AsCas12a 變體，活性比原生版高很多，配 mRNA 暫時表達就足夠在 TRAC 上完成切割。另外體外轉錄這條 mRNA 時，作者把所有 uridine 換成 N1-Methylpseudouridine——細胞天生有 TLR7/8、RIG-I 等警報系統會辨識「外來 RNA」，未修飾的 uridine 一被偵測就觸發發炎反應與 mRNA 降解；換成 N1-Methylpseudouridine 後感應器辨識不出來，mRNA 能逃過警報撐到翻譯，順便提升穩定性與翻譯效率。這就是 BNT162b2 等 mRNA 疫苗使用的同一種修飾。

   為什麼把整合位點鎖在 TRAC 第一個 intron 而不是 AAVS1 等 safe harbor？TRAC 是 T 細胞表面 T 細胞受體 (TCR) α 鏈的基因，選它同時拿到三項好處：(1) 把外源 CRISPR-All 構築塞進 TRAC 等於同時把內源 TCRα 打斷，對 CAR-T 是有利的——避免內源 TCR 跟 CAR 競爭、也避免 TCR mispairing 造成移植排斥。(2) TRAC 在 T 細胞高表達，整合進 intron 1 後構築可直接借用 TRAC 自己的啟動子驅動下游 CAR 與報告基因，省去外加啟動子。(3) intron 是「會被細胞自動剪掉」的 DNA 區段，cloning 過程留下的 GTAA/AGCG 黏端疤痕剛好藏在 intron 裡，splicing 後完全剪掉，最終蛋白序列沒有疤痕。AAVS1、CCR5 等 safe harbor 雖然安全，但缺乏這三項組合優勢。

   電穿孔的四種試劑各有分工：enCas12a mRNA 3.0 µL 是切割力來源、HDR plasmid 0.5 µg 是修復範本、gRNA plasmid 0.5 µg 告訴剪刀去 TRAC 哪裡剪、helper plasmid 1.5 µg 則是一段約 4 kb 沒有功能基因的填充 DNA——它本身不編碼任何東西，但能提供額外 DNA 表面結合細胞的 DNA 損傷反應蛋白（如 DNA-PKcs、53BP1），間接讓細胞偏向選 HDR 而非直接亂黏的修復路徑。Lonza P3 buffer 是專為 T 細胞最佳化的電穿孔緩衝液，EO-151 是 Lonza 4D Gen2 為 T 細胞 knockin 內建的脈衝代碼。為什麼不直接用 lentivirus 把構築送進細胞？因為 lentivirus 整合進染色體的位置是隨機的，每顆細胞落在不同染色質環境、表達強度不一；同一顆細胞還可能拿到好幾份 lentivirus，下游 pooled screen 的 barcode-perturbation 對應關係就崩盤；另外 lentivirus 載體尺寸有約 8 kb 上限，CRISPR-All 構築要塞 ≥10 個 element + barcode array 通常會超過。非病毒整合到 TRAC 後，所有構築都落在同一個位置、每顆編輯成功的細胞只整合一份、條碼一對一，平均 editing efficiency ~35–40%，下游 CACTUS 篩選才能正確把表型對應到擾動組合。

4. 工具與材料:
   - **enCas12a**: 改良過的 AsCas12a 變體，活性比原生版高，本實驗以 mRNA 形式提供切割能力。
   - **plasmid HDR template (HDRT)**: 帶 TRAC 同源臂的 CRISPR-All 構築質體，當作細胞修補斷口時的「裝潢圖紙」。
   - **U6-driven gRNA plasmid**: 用 U6 啟動子表達 gRNA，靶向 TRAC intron 1 序列 5′-GCAGACAGGGAGAAATAAGGA-3′，指引 enCas12a 切割位置。
   - **helper plasmid**: 約 4 kb 沒有功能基因的填充 DNA，提供 DNA 表面結合 DNA-PKcs/53BP1，間接把細胞修補路徑推向 HDR。
   - **N1-Methylpseudouridine**: 修飾過的 uridine 鹼基，能讓 mRNA 逃避 TLR7/8、RIG-I 等警報感應器，同時提升穩定性與翻譯效率（BNT162b2 同款修飾）。
   - **NEB HiScribe T7 High Yield RNA Synthesis Kit**: 高表達 T7 體外轉錄試劑，本實驗用來合成 enCas12a mRNA，並把 uridine 全部替換為 N1-Methylpseudouridine。
   - **SPRI 純化**: 用磁珠在不同鹽濃度下選擇性結合 RNA/DNA 的純化方法，本實驗用來純化 mRNA。
   - **Lonza 4D Gen2 + P3 buffer + EO-151**: Lonza 4D Gen2 電穿孔機 + 專為 T 細胞最佳化的 P3 緩衝液 + 內建脈衝代碼 EO-151，是 T 細胞非病毒 knockin 的標準組合。
   - **TRAC intron 1 整合位點**: T 細胞 TCRα 鏈的第一個內含子，整合至此同時關掉 TCRα、借用 TRAC 啟動子驅動構築、並讓 cloning 疤痕藏進內含子。
   - **HDR (homology-directed repair)**: 細胞遇到 DNA 斷裂時用同源序列當範本修補的路徑，只在 S/G2 分裂期啟動。

5. 與此篇文章的關係:
   在《A unified genetic perturbation language for human cellular programming (CRISPR-All)》這篇文章中，作者為了把多個擾動 element 與 barcode array 一次性塞進原代 T 細胞，採用了 enCas12a mRNA + plasmid HDRT 的非病毒 TRAC knockin。這個方法解決了 lentivirus 隨機整合、構築尺寸上限與 barcode 對應崩盤的瓶頸，把所有 CRISPR-All 構築鎖在 TRAC intron 1 同一位置。它把 CACTUS 與 10,240-member 組合 library 餵進可比較、可定序、且每細胞一份的 T 細胞，為下游 amplicon-seq 與 CRISPR-All-seq 提供乾淨且可重複的編輯基底。
