# CRISPR-Cas9 等基因校正與等基因敲入

1. 引用自哪篇 paper: engineered-cardiac-tissue-rcm
2. Outline (任務主線): CRISPR-Cas9 等基因校正與等基因敲入
3. Method: 

病人這一株 iPSC 雖然帶 FLNC ΔGAA 突變，但他全身其他基因也有專屬於他的變異，拿陌生的健康人細胞當對照不能歸因到 FLNC。所以作者做兩條互補的對照：第一條叫「等基因校正 (isogenic correction)」，用 CRISPR 把病人細胞的那顆缺三字母突變改回正常版 (FLNC^ψWT^)，當作除了那顆突變外其他基因完全相同的雙胞胎對照；第二條反過來叫「等基因敲入 (isogenic knock-in)」，把同一個 ΔGAA 缺口用同樣的 CRISPR 流程硬塞進一條完全無關的健康細胞 WTC11-GCAMP6 (GCAMP6^ΔGAA^)，當作獨立第二背景的驗證。任何表型若在「校正後消失」且「敲入後重現」，就一定是這顆突變本身造成的。

編輯工具是 RNP 電穿孔——作者先在試管裡把 Alt-R S.p. HiFi Cas9 Nuclease V3 蛋白和引導 RNA (sgRNA) 預先組裝成一顆完成品的核糖核蛋白複合物 (RNP)，再用 Amaxa 4D-Nucleofector + P3 Primary Cell 4D X Kit L、程式 CA-137 短暫高壓電擊細胞膜，把這顆預組好的剪刀直接送進細胞。比起會在染色體留下整合痕跡、且持續表達易脫靶的 Cas9 質體轉染，RNP 是剪完即逝、幾小時內就被細胞降解，乾淨許多。sgRNA 是一段 20 個鹼基的引導 RNA（本研究用 `ACCGUUGAACUUGACAUCGA`），告訴 Cas9 蛋白要在染色體哪個位置咔嚓剪一刀。Cas9 剪斷雙股 DNA 後，作者另外送進一條設計好的單股修補模板 (ssODN)——上面寫著「應該長這樣」的正確序列；細胞走同源重組修補 (HDR) 路徑把 ssODN 當範本照抄，斷口就被精準改寫。同一條 sgRNA、只換 ssODN：校正時 ssODN 帶正常序列、敲入時帶 ΔGAA 版本，就達成雙向編輯。

為什麼非要用 HiFi 版 Cas9？因為單一病童 iPSC 沒辦法反覆嘗試，脫靶風險特別致命。Alt-R S.p. HiFi Cas9 Nuclease V3 (IDT) 是經點突變改造的高保真版，在 sgRNA 與 DNA 配對不完美時會降低活性，把脫靶剪切壓得很低。編輯完成後，作者用引子 Forward `GGAGTGCTACGTCTCTGAGC` / Reverse `CAGAAGTCACCCTGTTCCCC` PCR 擴增目標區段、做 Sanger 定序——但混合細胞群的 Sanger trace 是一團重疊多峰的混亂波形。Synthego ICE (Inference of CRISPR Edits) 線上工具能把這團波形反推回「裡面有多少比例是何種編輯結果」，回報精準編輯效率與 indel 種類，不用每株都建純系才知道有沒有成功。

電穿孔過後是一鍋什麼都有的混合細胞——有些 ssODN 成功修補、有些卡在隨機 indel、有些根本沒被剪到。要拿到「整株細胞都帶同一種基因型」的乾淨細胞株，必須稀釋到單細胞、長成 colony 再挑。但 iPSC 一旦被拆成單顆就會啟動細胞凋亡死掉一大半，所以加 CloneR (Stem Cell #05888) 抑制單細胞凋亡訊號。流程是電穿孔後恢復 48 h，3 × 10⁶ cells 鋪到 10 cm Matrigel 培養盤的 mTeSR Plus + CloneR 中，7–10 天後挑 colony，最後用 Sanger 與正常核型逐株確認，產出 FLNC^ψWT^ 與 GCAMP6^ΔGAA^ 兩條乾淨細胞株。為什麼一定要 isogenic 雙向而不只做一條校正？萬一這株病人 iPSC 在建株過程剛好還累積了其他突變，光校正掉 FLNC 仍可能殘留干擾；反向 knock-in 把同一缺口塞進完全無關的 WTC11-GCAMP6 健康背景，若兩條獨立背景都在「有突變時出現表型、沒突變時消失」，這個雙向因果鏈就堵住了所有 N=1 推廣質疑。

4. 工具與材料: 
- **RNP 電穿孔**: 把 Cas9 蛋白與 sgRNA 預組成核糖核蛋白複合物後電進細胞，剪完即逝、不留人為痕跡。
- **Alt-R S.p. HiFi Cas9 Nuclease V3**: IDT 提供的高保真版 Cas9，在 sgRNA 與 DNA 配對不完美時降低活性，把脫靶剪切壓低。
- **sgRNA**: 20 個鹼基的引導 RNA，本研究用 `ACCGUUGAACUUGACAUCGA` 引 Cas9 至 FLNC 目標位點。
- **ssODN**: 單股修補模板 DNA，提供 HDR 修補時的「應該長這樣」範本，校正版與敲入版各一條。
- **HDR**: 同源重組修補路徑，細胞把斷口照 ssODN 範本精準改寫，達成定向編輯。
- **Amaxa 4D-Nucleofector + P3 Kit + CA-137 程式**: Lonza 電穿孔儀的細胞型號專屬程式，把 RNP 送進 iPSC。
- **Synthego ICE**: 線上工具，從混合 Sanger trace 反推 indel 比例與精準編輯效率。
- **CloneR**: Stem Cell #05888，抑制 iPSC 單細胞凋亡的小分子混合物，讓單細胞能長成 colony。
- **isogenic correction / knock-in**: 等基因校正＋等基因敲入雙向對照，排除個體遺傳背景干擾、提供獨立背景驗證。
- **WTC11-GCAMP6**: 已內建鈣指示器 GCAMP6 的健康 iPSC 細胞株，作為第二獨立背景接收 ΔGAA 敲入。

5. 與此篇文章的關係: 
在《Engineered cardiac tissue model of restrictive cardiomyopathy for drug discovery》這篇文章中，作者為了把 FLNC c.7416_7418delGAA 突變的因果關係從「單一病童」推廣到「這個突變本身」，採用了 CRISPR-Cas9 RNP 電穿孔的等基因雙向編輯。它解決了「N=1 病人 vs. 陌生健康人對照會被個體遺傳背景污染」的瓶頸，產出 FLNC^ψWT^ 校正株與 GCAMP6^ΔGAA^ 敲入株兩條對照，為下游 2D 鈣訊號分析、ECT 力學量測與藥物篩選提供獨立雙背景驗證材料。
