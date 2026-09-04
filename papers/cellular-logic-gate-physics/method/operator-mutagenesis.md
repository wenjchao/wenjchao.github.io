# λP(R-O12) O_R1 操縱子的定點突變

1. 引用自哪篇 paper: cellular-logic-gate-physics
2. Outline (任務主線): λP(R-O12) O_R1 操縱子的定點突變
3. Method:
   作者要動的是 cI 抓握 DNA 的那副「插座」，技術上用的是定點突變 (site-directed mutagenesis)——一種「只改指定字母、其他一字不動」的 DNA 精修：先設計一段短的合成 DNA 當模板，想改哪個字母就在模板上寫哪個字母，再用聚合酶把整段質體按這條模板重新複製一次，指定位置就換好字母、其他跟原版完全一樣。這跟「亂射一堆突變、事後篩選能用的」隨機文庫策略正好相反：定點突變一次只做一個候選版本、精準得像拿雕刻刀刻字，適合「已經知道要動哪裡」的場景。那要動的位置又為什麼挑 O_R1，不動 O_R2、O_R3？λP(R) 這段 DNA 上原本有三個 cI 抓握位點，作者早就把 O_R3 從合成啟動子 λP(R-O12) 刪掉了（cI 對 O_R3 親和力弱，留著也影響不大）；剩下 O_R1、O_R2 才是主戲，而 cI 對 O_R1 的天生親和力比 O_R2 高約 10 倍、總是先抓 O_R1，一抓上又會透過蛋白間互動立刻把另一個 cI 二聚體拉上 O_R2（協同結合）。所以 O_R1 是整條合作結合的起手位——動 O_R1 等於直接切掉起頭那一步，整條連鎖就散掉,是最省力的削弱點。

   「換掉幾個 bp 就能顯著降低結合力」在分子層面上是這樣運作的:cI 單體有一段折成 α 螺旋、露在蛋白表面的短區段叫「第三段 α 螺旋 (α-helix 3)」,它就是負責辨識 DNA 序列的探針。兩個 cI 單體先兩兩結合成 cI 二聚體,兩條 α-helix 3 剛好對稱地插進 DNA 上蛋白最容易讀的凹槽 (major groove) 相鄰的兩段裡,用胺基酸側鏈跟 DNA 特定鹼基「握手」形成 hydrogen bond 與 van der Waals 接觸。這也是為什麼 17 bp 操縱子由「兩個對稱 half-site」組成——因為蛋白這邊剛好是兩隻手。若把 half-site 上負責握手的鹼基換掉,握手直接斷開、整體結合能就大幅下降;改幾個 bp 就相當於斷幾隻手,斷幾隻決定削弱多少。

   作者實作出來的原始 O_R1 序列是 `TACCTCTGGCGGCGGTGATA`，從左邊數第 4、5、6 位動刀，做出三個階梯式版本：mut4 只把第 4 位 C 換成 A（1 bp 動）；mut5 在 mut4 基礎上再把第 6 位 C 換成 A（2 bp 動）；mut6 在 mut5 基礎上再把第 5 位 T 換成 G（3 bp 動）。（為什麼專挑第 4、5、6 位是靠位置權重矩陣的先驗，屬「共識序列驅動的突變位點挑選」模組的討論。）三個 O_R1 突變都固定與最弱的 RBS-3 搭配，形成 `pINV-107-mut4/pINV-112-R3`、`pINV-107-mut5/pINV-112-R3`、`pINV-107-mut6/pINV-112-R3` 三條測試線——這是一個「只變 operator 削弱程度、其他變數全部鎖住」的 3×1 掃描矩陣。為什麼要固定 RBS-3？因為上一步已經確認 RBS-3 能把死線推回可分辨的 inverse sigmoid，本步驟要問的是「在這條可用基準線之上，再削 operator 能不能把曲線微調得更漂亮」；變因單一，量到的曲線差異才能乾脆歸因給 operator 突變。

   作者刻意把這一層改造分成兩種類別。RBS 是所有基因表現都會用的通用零件，換一條較弱的 RBS 可以直接套到任何 repressor/promoter 對上——這叫通用改造。但 operator 上的鹼基序列與該 repressor 的 α-helix 3 側鏈化學是「一對一配對」的：cI 對 λ operator 的握手偏好跟 lacI 對 lac operator 完全不同，這裡挑的 mut4/5/6 序列直接搬到 lacI/p(lac) 上毫無意義。所以 operator 突變只對「這一組 repressor/promoter」有效——這叫元件特異改造。作者在論文結論明白指出策略：新元件先試通用招 (RBS)、需要特化時再讀文獻做元件特異的突變，前者可移植、後者需為每組零件重新設計。

   Figure 12 的結果指出：mut5、mut6 都削過頭——2、3 個 bp 的破壞太狠，把 cI 對 O_R1 的握手斷得太多。就算把 IPTG 開到最大、細胞裡的 cI 濃度衝到滿檔，cI 二聚體也再沒辦法穩定坐上 O_R1、把 λP(R-O12) 鎖住，輸出 EYFP 永遠亮著。這種閘不是 inverter，而是「永遠開著」的死開關——輸入變化再大也拉不下輸出，一樣沒有用。只有 mut4 落在甜蜜點：只斷 1 隻手，剛好把過強的靈敏度打回可控範圍，量出漂亮的 inverse sigmoid，成為後續蓋更大電路的良好候選零件 `pINV-107-mut4/pINV-112-R3`。這個結果同時倒過來回答了「為什麼還要做這層 operator 突變」——只換 RBS 到 RBS-3 已能把死線救回 inverse sigmoid，但曲線形狀還不是最漂亮，需要 operator 突變當第二個獨立可調參數再微調一次。所以 operator 突變不是「取代 RBS 改造」，而是「疊在 RBS 改造之上」的微調層——兩層改造互補、缺一則得不到最終這個乾脆好用的閘。

4. 工具與材料:
   - **定點突變 (site-directed mutagenesis)**: 以合成寡核苷酸為模板、只在指定位置換掉指定字母、其他序列一字不動的 DNA 精修技術；適合「已知要改哪裡」的場景，不同於隨機文庫策略。
   - **cI 二聚體 (cI dimer)**: 兩個 cI 單體兩兩結合形成的複合物，兩條 α-helix 3 對稱插進 DNA major groove 兩段、握上 17 bp operator 的兩個 half-site。
   - **α-helix 3**: cI 單體 amino domain 中露於蛋白表面的辨識螺旋，負責跟 DNA major groove 上的特定鹼基「握手」形成 hydrogen bond 與 van der Waals 接觸。
   - **major groove**: DNA 雙螺旋外露的較寬凹槽，蛋白最容易讀取序列資訊的位置；cI α-helix 3 就從這裡插進去做序列辨識。
   - **17 bp 對稱操縱子與兩個 half-site**: λ operator 由兩個對稱的 half-site 組成，剛好對應 cI 二聚體的兩隻手，是「為什麼是 17 bp、為什麼對稱」的物理基礎。
   - **O_R1 / O_R2 / O_R3 三個 cI 抓握位點**: 野生型 λP(R) 上三個 cI operator；作者的合成啟動子 λP(R-O12) 刪掉了親和力最弱的 O_R3，只留 O_R1、O_R2。cI 對 O_R1 親和力比 O_R2 高約 10 倍，是合作結合的起手位。
   - **mut4 / mut5 / mut6 三檔突變**: 作者對 O_R1 序列 `TACCTCTGGCGGCGGTGATA` 做的三個階梯式版本：mut4 (第 4 位 C→A,1 bp)、mut5 (再加第 6 位 C→A,2 bp)、mut6 (再加第 5 位 T→G,3 bp)。
   - **pINV-107-mut4/mut5/mut6 × pINV-112-R3**: 三個 O_R1 突變質體與最弱 RBS-3 質體配對形成的 3×1 掃描矩陣；固定 RBS-3、只變 operator 削弱程度，變因單一便於歸因。
   - **通用改造 vs 元件特異改造**: RBS 替換屬通用改造 (可套到任何 repressor/promoter 對)；operator 突變屬元件特異改造 (與該 repressor 的 α-helix 3 側鏈化學一對一配對，換系統無效)。作者建議新元件優先試通用招、需要特化時再做元件特異的突變。

5. 與此篇文章的關係:
   在《The Device Physics of Cellular Logic Gates》這篇文章中，作者為了把已被 RBS 替換初步救活、但形狀仍不夠漂亮的 cI/λP(R-O12) 反相器再微調到理想的 inverse sigmoid，採用了 O_R1 定點突變。這個方法解決了「還需要第二個獨立可調參數才能同時優化 gain 與 noise margin」的瓶頸，把 3 個 O_R1 突變質體 (mut4/mut5/mut6) 固定與最弱 RBS-3 搭配、產出 3×1 測試矩陣，最終得到 `pINV-107-mut4/pINV-112-R3` 這個對 IPTG 反應乾脆、可以直接串到下游電路的候選閘，並提供「通用招之外還要一手元件特異招」的通則供後續元件庫累積。
