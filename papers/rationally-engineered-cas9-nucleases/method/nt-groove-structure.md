# 結構引導的 nt-groove 殘基定位與電性建模

1. 引用自哪篇 paper: rationally-engineered-cas9-nucleases
2. Outline (任務主線): 結構引導的 nt-groove 殘基定位與電性建模
3. Method:

整個方法是純電腦上的結構分析，目的是「在 Cas9 表面找出最可能影響 ncDNA 結合的正電殘基短名單」，給下游點突變實驗一份高品質的搜索清單。作者在分子視覺化軟體 PyMOL（Schrödinger）裡載入兩個別人解出來的 SpCas9 晶體結構檔——PDB 4UN3（Nishimasu et al. 2014 Cell）與 PDB 4OO8（Anders et al. 2014 Nature）——相當於把剪刀拆開、放在電腦上盯著看。接著用 PyMOL 內建的 APBS plugin（一個逐點計算「這裡帶多少電」的數值工具）算整顆 Cas9 表面的靜電位，把表面上色：紅色 = 負電、藍色 = 正電，色階尺規調在 −10 keV 到 +1 keV，方便看 groove 內部「藍藍一片」的位置（Fig. S2A–C）。為什麼同時用兩個結構檔？因為兩張照片拍到的鏡頭互補：4UN3 拍的是 Cas9 抱著 sgRNA 加 target DNA 的三元複合體，nt-groove 主體（夾在 RuvC 跟 HNH 兩塊刀刃中間那段凹槽）看得最清楚；4OO8 則特別解析 PAM-interacting domain（PI domain，認 PAM 序列的辨識區）連同 phosphate lock loop（K1107、E1108、S1109 那一小段）的細節，兩者搭配才能掃完 nt-groove 整條。為什麼鎖定 nt-groove 而不是動別的面？因為 sgRNA 結合面跟 PAM 辨識區都直接參與序列辨識，動了會連「正確位置」也認不出來；nt-groove 只負責「不挑序列、純用電性」穩住 ncDNA，動它只調「拉開狀態維持多穩」這個物理參數，不破壞辨識邏輯，正好命中「剪錯難、剪對不變」的甜蜜點。

光靠靜電上色還不夠，因為晶體照片其實漏拍了一段關鍵 DNA。被推開的那股 ncDNA 在晶體裡飄來飄去、影像是糊的或乾脆缺一段。所以作者必須在 PyMOL 裡「手動把這股 DNA 拉一條進去擺好」（hand-modeled ncDNA），擺位原則是讓 DNA 的磷酸骨架（每個核苷酸帶的負電顆粒）剛好落在「離正電殘基側鏈約 3 Å」的距離——這個距離在化學上是「兩個原子能不能形成氫鍵」的判定尺。為什麼盯著正電-負電這對吸引力？因為 DNA 整條就是一串「磷酸負電顆粒」掛在背骨上，凹槽內排了一群 Lys/Arg/His 的正電側鏈，兩者非專一地（不挑序列、只看電性）互相吸住，把被推開的 ncDNA 黏在 groove 內、不讓它彈回去跟 cDNA 合回去。把這群正電換成不帶電的 alanine 就等於把黏膠拔掉，ncDNA 容易回到原位，兩股 DNA 自然想把拉鏈合上——這時 sgRNA 跟 cDNA 必須配得夠完美，才贏得過「合上」的力把拉鏈撐開讓剪刀落下；對得不夠好的位置會輸掉這場拔河，剪刀剪不成，特異性就提升了。

把 ncDNA 擺好後，作者用三個條件同時過濾：(1) 殘基是 Lys、Arg 或 His 這三種帶正電的胺基酸；(2) 在電荷地圖上落在 nt-groove 那片藍區內、不是別的面；(3) 把 hand-modeled ncDNA 放好後，這個殘基側鏈到磷酸骨架的距離不超過 3 Å、有條件形成氫鍵。三關全過的胺基酸共 31 個，主要集中在 RuvC 跟 HNH 兩塊刀刃中間的凹槽，少數落在 PI domain 的 phosphate lock loop，完整列表包含 K775、R778、R780、K782、R783、K789、K797、Q807、K810、R832、K848、K855、R859、K862、K866、K890、K961、K968、K974、R976、H982、H983、K1000、K1003、K1014、K1047、K1059、R1060、K1107、E1108、S1109 等（見 Table S1）。為什麼這 31 個位置都打算換成 alanine？因為 alanine 的側鏈只有一個甲基，是中性、體積小、化學上幾乎啞巴；換成它等於「乾淨地把正電拔掉、不引入其他干擾」。換成 Gly（連甲基都沒有）會讓骨架變鬆，換成 Ser（帶羥基）又會引入新的氫鍵，alanine 剛好是「只移除電性、不引入新功能」的中性對照。為了把 31 個位置寫進下游 primer 設計（§2-B 的 Golden Gate cloning），作者再用序列註解軟體 Geneious v8.0.3（Kearse et al. 2012 Bioinformatics）把 Cas9 整條 1,400 多 aa 序列攤平，標上 RuvC、bridge helix (BH)、REC、HNH、PI 等 domain 範圍（Fig. S4），確認每顆候選殘基的編號跟所屬 domain。

這套流程有兩個明顯的脆弱點，值得在心裡記著。第一個是 ncDNA 的擺位完全靠人工：擺太遠會把真正會抓 ncDNA 的殘基排除掉、漏做關鍵突變；擺太近或角度偏了則會把根本不接觸 ncDNA 的殘基誤列入候選、白做工。作者的容錯設計是「3 Å 這把尺寬鬆但有化學依據」加上「下游一次做 31 個、看哪 5 個真的能把 OT 降十倍」——擺錯只會多一些假候選浪費實驗，不至於漏掉所有真候選。第二個脆弱點是「不靠結構引導」的替代方案有多差：如果不做這個前置篩選，要對 Cas9 全長 ~1,400 個胺基酸每個位置都換成其他 19 種胺基酸，光單點突變就要做 ~2.6 萬個，實驗量做不完；就算僥倖篩到 hit 也分不清是真的削弱 ncDNA 結合、還是蛋白整體不穩。結構引導把搜索空間縮了兩個數量級，每個 hit 還都自帶機制故事，這是它對下游所有實驗的最大貢獻。

4. 工具與材料:

   - **PDB 4UN3 (Nishimasu et al. 2014 Cell)**: SpCas9 抱著 sgRNA 加 target DNA 的三元複合體晶體結構檔，提供 nt-groove 主體（RuvC + HNH 之間那段凹槽）的視覺基礎。
   - **PDB 4OO8 (Anders et al. 2014 Nature)**: 另一個 SpCas9 結構檔，特別解析 PAM-interacting domain 連同 phosphate lock loop（K1107、E1108、S1109）的細節，補足 nt-groove 靠 PAM 端的視角。
   - **PyMOL (Schrödinger)**: 分子視覺化軟體，作者用來載入晶體結構檔、手動擺 ncDNA、檢視 domain 與電性。
   - **APBS plugin**: PyMOL 內建的靜電位計算外掛，逐點算分子表面「這裡帶多少電」並上色（紅 = 負、藍 = 正），色階 −10 至 +1 keV。
   - **nt-groove**: 夾在 RuvC、HNH、PI 三個 domain 之間的正電凹槽，靠非專一性靜電抓住被推開的 ncDNA、穩定 DNA 解旋狀態。
   - **RuvC / HNH domain**: SpCas9 的兩塊核酸酶刀刃，分別負責切 ncDNA 與 cDNA；nt-groove 主體就夾在這兩塊中間。
   - **PAM-interacting domain (PI domain)**: Cas9 上負責認 NGG PAM 序列的辨識區，內含 phosphate lock loop。
   - **ncDNA (non-complementary strand)**: Cas9 把雙股 DNA 拉開後，那條沒跟 sgRNA 配對、被擱在 nt-groove 裡的 DNA 股。
   - **hand-modeled ncDNA**: 因為晶體照片裡 ncDNA 影像不清晰，作者在 PyMOL 中手動把 ncDNA 擺進 groove，原則是讓磷酸骨架跟候選殘基側鏈落在約 3 Å 的氫鍵距離。
   - **3 Å hydrogen-bond 距離**: 化學上判斷「兩個原子能不能形成氫鍵」的距離尺，作者用來篩選哪些正電殘基真的有機會抓 ncDNA 磷酸骨架。
   - **Geneious v8.0.3**: 序列註解軟體（Kearse et al. 2012 Bioinformatics），用來把 Cas9 1,400 多 aa 序列攤平、標出 RuvC、BH、REC、HNH、PI 等 domain 邊界。
   - **alanine scanning**: 把候選殘基換成 alanine（只有一個甲基、中性、無功能的小胺基酸）的標準蛋白工程作法，目的是乾淨地移除原側鏈功能、不引入新干擾。
   - **31 個候選殘基**: 三關過濾後得到的正電 Lys/Arg/His 短名單，包含 K775、R778、K810、K848、K855、K1003、R1060 等，主要集中在 RuvC 與 HNH 中間，少數在 PI domain 的 phosphate lock loop（K1107、E1108、S1109）。

5. 與此篇文章的關係:

這篇 paper 想解決野生型 SpCas9 對 sgRNA mismatch 容忍度過高、在 PAM 遠端錯配時仍會切錯位點的根本問題，作者提出的假說是「nt-groove 用非專一性靜電抓住被推開的 ncDNA、阻止它和 cDNA 重新配對」，所以只要削弱這條靜電抓力，sgRNA 就必須配得更完美才剪得動。此 module 是整條 specificity 工程 pipeline 的起點，負責把這個機制假說落地成一份「該動哪些胺基酸」的可執行清單：作者在 PyMOL 裡疊用兩份互補的 SpCas9 晶體結構（4UN3 看 nt-groove 主體、4OO8 看 PAM 端的 phosphate lock loop），用 APBS 算出表面電性，再以手動擺入的 ncDNA 加上「Lys/Arg/His × 3 Å 氫鍵距離 × 落在 nt-groove 內」三條件，把 ~1,400 aa 全長飽和掃描的兩萬六千個版本砍到只剩 31 個候選殘基。這個前置篩選的好處是把實驗量降一個數量級之外，每個 hit 都自帶「中和正電 → ncDNA 不黏 → mismatch 撐不住」的物理解釋，讓後續 specificity 改善不會被「表現量降低」「整體活性下降」之類的 alternative explanation 解釋掉。在 method 鏈上，它直接餵給 §2-B 的 Golden Gate cloning（用這 31 個位點寫進 BsaI primer 做點突變庫），最終由 §2-D 的 targeted deep sequencing 與 §2-E 的 BLESS 全基因組驗證篩出 eSpCas9(1.0) 與 (1.1) 兩條贏家變體，整套結構引導策略的成敗都押在這一步的搜索空間能否同時夠小又夠準。
