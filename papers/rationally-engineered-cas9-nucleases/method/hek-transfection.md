# HEK 細胞培養與 Cas9/sgRNA 共轉染

1. 引用自哪篇 paper: rationally-engineered-cas9-nucleases
2. Outline (任務主線): 把 Cas9 突變庫與 sgRNA 同時送入人類細胞，在內源 EMX1 / VEGFA / 其他 10 個基因座產生 indel，作為 specificity / on-target efficiency 讀出。
3. Method:

整個 2-C 子項是「在人類細胞培養皿裡做一場剪刀試切」：作者把『某個 Cas9 突變版本的 DNA 圖紙』和『一張寫了座標的 sgRNA 通緝令』兩條環狀 DNA 質體一起塞進人類腎臟細胞株 (HEK293T / HEK293FT)，靠脂質體載體 (Lipofectamine 2000) 把這兩條質體包成微小油泡帶進細胞。細胞讀完圖紙後自己做出改造剪刀和通緝令，剪刀拿著通緝令去切細胞自己的染色體上對應的基因，切完後細胞會手忙腳亂地把斷口接回去，常常多塞或少掉幾個鹼基，留下一個小疤 (indel)。讀數就是每個目標位置上「疤痕的比例 (indel %)」——疤越多代表那把剪刀越愛切那裡。作者把 Cas9 與 sgRNA 拆成兩條質體是因為這次要掃 31 個突變 × 數十條 sgRNA 的組合，分兩疊質體後要換哪一邊只需換對應那條，不必每個組合都重建完整質體。選用 HEK293T 與 HEK293FT 則是因為這兩株人類腎臟細胞容易養、轉染效率高，也是基因編輯領域的『標準對照細胞』，能直接跟前人在 EMX1 / VEGFA 報告的切割數字相比較。在目標座的選擇上，EMX1(1) 與 VEGFA(1) 是文獻 (Hsu et al. 2013, ref 3；Fu et al., ref 4) 已經把『正確位置和會被剪錯的位置』列得很清楚的兩條經典 guide，留給 specificity 比較用；另外 24 條 sgRNA 散落在 10 個不同基因座，則交給 on-target efficiency panel，檢查『變更挑剔的同時，剪正確位置的效率有沒有跟著掉』。

轉染這場戲在前一天就要備好舞台。作者在轉染前一天把細胞按密度鋪盤——24-well 盤每孔 ~120,000 顆細胞、96-well 盤每孔 ~30,000 顆，都是經驗上『明天剛好長到盤底七到八成』的密度。鋪太稀，細胞會被脂質體毒死；鋪太密，已經疊起來的細胞拿不到質體，下游表現就不均勻，indel% 訊號會被『有的細胞滿手 Cas9、有的完全沒有』的雜訊蓋掉。至於 Lipofectamine 2000 本身，是一種帶正電的人工脂質配方：帶負電的質體 DNA 跟它一混就抱成微小油滴，表面呈正電；細胞膜帶負電，油滴黏上去後被細胞包進去，再從內部囊泡漏出質體進入細胞核。對作者而言，重點是這種脂質體載體對 HEK293T/FT 效率高又溫和，不會像電穿孔那樣震碎細胞，同一批細胞才能同時表現足量的 Cas9 與 sgRNA。

Cas9 與 sgRNA 質體的劑量分成兩段。初步篩選 31 個突變時，作者每孔 24-well 丟 1000 ng Cas9 質體 + 450 ng sgRNA 質體——這個階段要把訊號拉到最大，方便看清楚哪幾個版本表現特別突出。然而高劑量是雙面刃：Cas9 越多本身就會切得更兇，連 off-target 也被切到飽和，所有版本表面上看起來都同樣『會剪錯』，內在挑剔度的差異就被高表現量蓋掉。因此後續用 24 sgRNA × 10 loci 系統性驗證時，作者把劑量壓到約 1/3：每孔 24-well 送 400 ng Cas9 + 100-200 ng sgRNA，每孔 96-well 則送 100 ng Cas9 + 25-50 ng sgRNA，這個量級更接近實際應用的 Cas9 用量，K855A、eSpCas9(1.0)、eSpCas9(1.1) 的差異才比得公平。每組樣本的 DNA 總量必須補成一致 (equal total plasmid)：因為 Lipofectamine 2000 是『按總 DNA 質量算油滴』的，如果不補齊，劑量低的組總 DNA 也少，連帶脂質毒性、轉染效率都不一樣——突變組看起來 off-target 很低時，你會分不清是『突變真的更挑剔』還是『就只是進入細胞的 Cas9 量更少』，整篇 specificity 結論就被『Cas9 表現量差異』污染。

indel 之所以能當 Cas9 切割活性的代理指標，背後是一條穩定的因果鏈：Cas9 切完雙股 DNA 後，細胞最常啟動一條『快速但粗糙』的修補路徑（非同源末端接合，NHEJ），兩端對齊不一定對得齊，常常多塞或少掉幾個鹼基，這個小疤就叫 indel。同一個位點被剪越多次、留下的小疤越多，所以『這個位點上有 indel 的 reads 占總 reads 的比例 (indel %)』就直接代表 Cas9 在那裡的切割活性。作者用這套讀數來打分 specificity 也跟 sgRNA 長度有關：標準 sgRNA 通緝令是 20 個字母，前人 (Fu et al. 2014, ref 12) 發現把通緝令從 5' 端剪短到 17 或 18 個字母（截短 guide RNA, truncated sgRNA），由於 sgRNA:DNA 配對能量本來就剛剛好，稍有不對就抓不住，理論上能降低 off-target。作者特別讓 EMX1(1) 配 18 nt guide、VEGFA(1) 配 17 nt guide 來直接重現對方的條件，當作 specificity 改善的『現有最佳對照』，後續才能正面比『短 guide + 原版 Cas9』vs.『標準長 guide + eSpCas9』哪個更乾淨。

為了堵住『eSpCas9(1.1) 看起來特別精準，會不會其實是因為它把細胞直接毒死、所以 off-target 那邊根本沒細胞活著被剪』這個尷尬反駁，作者另外做了細胞存活對照 (Fig. S11)。他們把 HEK293T 轉染 WT 或 eSpCas9(1.1)，養 72 小時後加入 CellTiter-Glo 試劑——這是一種測『細胞還活著的程度』的試劑，活細胞會自己做 ATP，把 ATP 拿去燒成螢光，螢光強度直接反映活細胞數量。結果兩組存活率一樣，等於把『specificity 改善來自毒殺細胞』這個 alternative hypothesis 直接擋掉，跟前面『等總質體量』『高劑量 vs 低劑量』兩個校正一起組成完整的內控套組。

4. 工具與材料:

   - **HEK293T / HEK293FT**: 兩株好養、轉染效率高的人類腎臟細胞株 (Fisher Scientific)，是基因編輯領域驗證 Cas9 活性的標準對照細胞。
   - **DMEM + 10% FBS**: 細胞培養基（Life Technologies DMEM + Gibco 胎牛血清），於 37 °C、5% CO₂ 下維持 HEK293 細胞。
   - **細胞接種密度 (cells/well)**: 轉染前一天鋪盤：24-well 約 120,000 cells/well、96-well 約 30,000 cells/well (Corning)，讓細胞在轉染當天剛好達到約 70-80% 滿盤的甜蜜點。
   - **Lipofectamine 2000**: Life Technologies 推出的陽離子脂質體載體，把帶負電的質體 DNA 包成微小油泡帶進細胞，效率高且對 HEK293T/FT 相對溫和。
   - **Cas9 質體 (Cas9 plasmid)**: 編碼某個 Cas9 突變版本的環狀 DNA 圖紙，轉染進細胞後由細胞自行翻譯出該 Cas9 蛋白。
   - **sgRNA 質體 (sgRNA plasmid)**: 編碼導引 RNA 的環狀 DNA 圖紙，轉染進細胞後由 RNA 聚合酶 III 啟動子直接轉錄成短小的 sgRNA。
   - **初步篩選劑量**: 每孔 24-well 送 1000 ng Cas9 質體 + 450 ng sgRNA 質體，用最大劑量放大訊號差異以找出 specificity 改善的候選突變。
   - **後續驗證劑量**: 每孔 24-well 送 400 ng Cas9 + 100-200 ng sgRNA；每孔 96-well 送 100 ng Cas9 + 25-50 ng sgRNA，較低劑量更貼近實際應用，避免高表現量蓋掉 specificity 差異。
   - **等總質體量 (equal total plasmid)**: 每組樣本以填充質體把總 DNA 質量補成一致，避免 Lipofectamine 2000 帶進細胞的脂質-DNA 油滴總量不同造成轉染效率與毒性偏差。
   - **EMX1(1) / VEGFA(1)**: 前人 (Hsu et al. 2013, ref 3；Fu et al., ref 4) 已完整刻畫過 on-target 與 off-target 位點的兩條經典 sgRNA，用於 specificity 直接比較。
   - **24 sgRNAs × 10 基因座**: 另選 24 條 sgRNA 散落在 10 個基因座，用來量 on-target efficiency panel，檢查 specificity 改善是否伴隨 on-target 切割效率下降。
   - **截短 guide RNA (truncated sgRNA, 18 / 17 nt)**: EMX1(1) 配 18 nt guide、VEGFA(1) 配 17 nt guide（Fu et al., ref 12），重現前人縮短 guide 提升 specificity 的條件，作為與 eSpCas9 比較的對照。
   - **indel %**: Cas9 切完 DNA 後細胞以 NHEJ 修補留下的小插入或缺失疤痕；NGS 中該位點 indel reads 佔總 reads 的比例，直接代表 Cas9 在該位點的切割活性。
   - **CellTiter-Glo viability assay**: Promega 的細胞存活定量試劑，量活細胞 ATP 產出的螢光強度；本研究於轉染後 72 小時量測，排除『specificity 提升來自毒殺細胞』的 alternative hypothesis。

5. 與此篇文章的關係:

這篇 paper 的核心目標是改造 SpCas9，讓它在 sgRNA 與 DNA 出現錯配時不再亂剪 off-target，但又不能犧牲 on-target 切割效率；要驗證這件事，作者必須有一個能在人類細胞內、同一條件下同時量到「剪對位置的力道」與「剪錯位置的次數」的活體測試平台，HEK 細胞共轉染就是承擔這個角色的步驟。把 Cas9 突變質體與 sgRNA 質體一起用 Lipofectamine 2000 送進 HEK293T / HEK293FT，可以讓 31 個單點突變、34 個組合突變和數十條 sgRNA 在同一套標準化的人類細胞背景下平行表現，並直接在 EMX1、VEGFA 等內源基因座留下 indel 作為切割活性讀數，避免使用報導質體或體外切割造成的偽差。作者特意拆成「初篩高劑量」與「驗證低劑量」兩段並補齊每孔總 DNA，是為了在高訊號階段不漏掉候選、又在公平劑量下分辨真實 specificity 差異，這直接服務於選出 K855A、eSpCas9(1.0)、eSpCas9(1.1) 三條贏家的決策。在 method 鏈中，這個 module 接在 Golden Gate 製作的點突變質體庫 (§2-B) 之後，把「結構假說產出的蛋白變體」轉成「細胞內的切割事件」，再交給下游的 amplicon NGS indel 量測 (§2-D)、BLESS 全基因組 DSB profiling (§2-E) 以及 CellTiter-Glo 存活對照 (Fig. S11) 收讀數，是整條 specificity 篩選流水線不可缺的細胞層輸入端。
