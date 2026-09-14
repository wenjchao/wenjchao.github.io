# Vβ 全家族 RT-PCR 的核酸層級 repertoire 分析

1. 引用自哪篇 paper: antitumor-lymphocyte-clonal-repopulation
2. Outline (任務主線): Vβ 全家族 RT-PCR 的核酸層級 repertoire 分析
3. Method:
      作者從三種樣本抽出 RNA 做 RT-PCR (reverse transcription PCR)：先用反轉錄酶把 T 細胞裡的 TCR β 鏈 mRNA 抄成一段 DNA (cDNA)，再用一組自己設計、涵蓋人類所有 Vβ 基因家族的引子 (Vβ family-specific primer set) 分別去放大每個家族的訊號；每個家族的引子只黏在自家保守段落上，配上共通的 constant-region 引子，就能逐一比較誰的訊號特別強、誰幾乎沒訊號。這一步讀的是「這顆樣本裡的 T 細胞正在生產哪一款天線」，屬於 RNA 層級的 repertoire，與 FACS 抗體只看細胞表面蛋白是兩個獨立層級。詳細引子設計見 supporting material (ref 11)。
   作者對三種 RNA 樣本平行做這套 RT-PCR：輸注前實驗室裡準備打回去的 TIL、治療後從病人血液抽出來的週邊血淋巴球 (PBL)、以及病人 9 於 day 20 手術切下的腫瘤生檢組織。三處樣本並排比對，可以一次追出「同一支 clone 從實驗室 → 血液 → 腫瘤」的軌跡是否連貫。
   為什麼要在 FACS 抗體 panel 已經看到 Vβ12+ 佔 CD8+ 六成、Vβ7+ 佔九成七之後，還多做一輪 RT-PCR 佐證？因為 FACS 抗體 panel 有三個內建盲點：第一，有些 Vβ 家族根本沒有商用抗體，主導 clone 若剛好落在這些家族就會被完全漏掉；第二，抗體有時對相近家族有交叉反應，可能把訊號歸到錯的家族；第三，有些 T 細胞表面的 Vβ 蛋白表現量偏低，抗體貼不上但細胞其實還在。RT-PCR 從 RNA 端獨立掃全部家族，訊號來自 mRNA 而非表面蛋白，正好補上這三個漏洞。反過來說，如果 RT-PCR 用的引子組漏掉某些家族，那些家族的 mRNA 再多也不會被放大出來——所以作者刻意強調自己設計的引子涵蓋全部 Vβ 基因家族，這是 RT-PCR 讀數可信的前提。兩層讀數同時指向同一個家族被極端偏斜，才能宣稱是「單一 clone 主導」而不是「單一 Vβ 抗體亮」。
4. 工具與材料:
   - **RT-PCR (reverse transcription PCR)**: 先用反轉錄酶把 mRNA 抄成 cDNA，再用 PCR 放大，用來讀「這顆樣本的細胞現在正在生產哪些 Vβ 天線」的 RNA 層級豐度。
   - **Vβ family-specific primer set**: 作者設計、涵蓋人類全部 Vβ 基因家族的一組引子，每支引子只黏在自家保守段落上，配上共通 constant-region 引子逐一放大每個家族。
   - **反轉錄酶 (reverse transcriptase)**: 把 mRNA 抄成 cDNA 的酵素；沒有它 mRNA 就無法變成 PCR 能讀的 DNA 模板。
   - **週邊血淋巴球 (PBL)**: 從病人血液抽出來的淋巴球，是 RT-PCR 的三種樣本之一，代表 clone 在循環中的狀態。
   - **腫瘤生檢 RNA**: 病人 9 於 day 20 切下腫瘤組織後抽出的 RNA，用來看主導 clone 是否也出現在腫瘤內部。
5. 與此篇文章的關係:
   在《Cancer Regression and Autoimmunity in Patients After Clonal Repopulation with Antitumor Lymphocytes》這篇文章中，作者要證明過繼輸入的 T 細胞 clone 真的在體內把血液佔滿，靠 FACS 抗體 panel 讀 Vβ 蛋白會遇到幾個抗體盲點。為此作者採用了 Vβ 全家族 RT-PCR：吃進輸注前 TIL、治療後 PBL 與病人 9 的腫瘤 RNA，用涵蓋全家族的引子從 RNA 層級掃出每個 Vβ 的相對豐度，交叉驗證 FACS 讀出的極端偏斜真的來自單一 clone，而不是抗體 panel 造成的錯覺。
