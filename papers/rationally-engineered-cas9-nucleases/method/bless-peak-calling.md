# BLESS DSB peak calling 與 Cas9-specific DSB 篩選

1. 引用自哪篇 paper: rationally-engineered-cas9-nucleases
2. Outline (任務主線): 從 BLESS 全基因組 reads 中分出真正由 Cas9 造成的 DSB cluster 與背景 DSB，再以 ranking 比較三條 Cas9 變體的 genome-wide off-target spectrum。
3. Method:

BLESS 上一步 (§2-E) 在每個雙股 DNA 斷口 (DSB) 兩端黏上帶生物素的小尾巴，富集後拿去定序，所以每個被剪斷的位置周圍會堆出一群 reads，叫一個 DSB cluster。本步驟拿到的原始資料就是「全基因組座標上一堆 cluster」，問題在於這裡面只有少數是 Cas9 真兇，剩下絕大多數是細胞自己每天會產生的背景 DSB——複製叉撞牆、活性氧損傷、拓樸酶留的暫時切口都會被生物素標起來一起送進定序。要把真兇從路人裡挑出來，作者靠的是「reads 排列形狀」這個特徵。BLESS 的定序會產生兩個方向的 reads，從切點往左讀的叫 reverse（藍色）、往右讀的叫 forward（紅色）。Cas9 是平頭切、每次都切在同一個鹼基位置，所以兩股 DNA 在固定座標被切斷，紅藍 reads 會剛好從這個座標往外延伸、疊成尖銳對稱的雙峰（見 Fig. S7B）。背景 DSB 是不同細胞隨機壞掉的，斷點散在 cluster 範圍裡，沒有這種尖峰形狀。

作者把這個「尖銳對稱雙峰」的特徵量化成一個分數，叫 DSB score（雙股切口分數），分數越高代表這個 cluster 越像 Cas9 在這裡剪了一刀。整套計算流程沿用 Ran et al. 2015 Nature 那篇論文已經發表並驗證過的 Cas9-BLESS pipeline（protocol 見該論文 supplementary）。為什麼直接沿用而不重新設計？因為 Ran 2015 已經把這套 score 對 Cas9 驗證過一次，沿用它有兩個好處：結果可以直接跟既有 WT SpCas9 BLESS profile 對齊比較，少一層「我的 score 跟你的不一樣」的爭議；同時把方法學風險留給原 paper 去扛，本論文把力氣集中在「比較三條 Cas9 變體之間的差異」。

三條被比較的 Cas9 變體 (WT、SpCas9(K855A)、eSpCas9(1.1)) 分別配 EMX1(1) 與 VEGFA(1) 兩條 sgRNA 跑一次 BLESS，得到各自的 cluster 清單後按 DSB score 從高到低排（ranking），畫成 Manhattan plot：橫軸是「染色體座標一路鋪平」、縱軸是該位置的 DSB score，像曼哈頓天際線一樣立著的高樓就是 score 高、最像 off-target 的點（見 Fig. 5A,B）。為什麼用相對 ranking 而不訂絕對閾值？因為三條變體的 on-target DSB score 本身就不一樣——以 EMX1(1) 為例，Table S3 列出的 on-target DSB score 是 WT 6.13、K855A 12.85、eSpCas9(1.1) 13.77；硬訂「DSB score > 1 算 OT」會偏袒整體分數低的變體。改用 ranking 配後續逐一驗證，三條變體才能在公平基準上比。

光看 BLESS 還不夠下結論，因為 BLESS 抓的是「斷口本身」，斷口不見得會留下編輯痕跡——細胞有時會無痕修補回去。所以對 ranking 排在前面的 BLESS 候選 off-target，作者再回頭用 §2-D 的 targeted deep sequencing 直接把那段 DNA 定序、算該位置 indel%，把「真的有 Cas9 編輯過」這層證據補上（見 Fig. 5C,D 與 Table S3 的「Indel % (rep 1/2)」欄位）。這條兩層驗證鏈的順序不能反過來：targeted-seq 解析度極高但有「得先告訴我要看哪些位置」的限制，只能量預先設計引子的 amplicon，沒人想到的 OT 永遠看不到；BLESS 廣但解析度粗，剛好填補 targeted-seq 設計位置的盲點。最後的結論是 SpCas9(K855A) 與 eSpCas9(1.1) 不僅整體 off-target 訊號在全基因組層級降低，也沒在原 WT 沒踩過的新位置冒出新 off-target。

順帶說明三個容易出錯的捷徑。第一，如果不算 DSB score、直接用「該座標有多少 reads」排序找 off-target，會把基因組裡本來就脆弱、reads 永遠很多的「背景 DSB 熱點」（脆弱位點、重複序列）全部誤判成 Cas9 OT，前段排名會被假陽性淹沒。第二，如果只看 Manhattan plot 就下結論而省略 targeted-seq 驗證，會犯兩種錯：把有 DSB 但沒 indel 的 cluster 算進 OT 數量、或反過來 BLESS 對低頻切割 sensitivity 不夠而漏看真 OT；唯有兩層證據對齊才下得了「沒新 OT」這種強斷言。第三，如果只用 WT vs eSpCas9(1.1) 兩條 Cas9 比、或只用 EMX1(1) 一條 sgRNA 跑，會被反問「specificity 改善是不是整體切弱了？」「是不是只這條 guide 有效？」中間排一條單點突變 SpCas9(K855A) 與同時跑 EMX1(1) + VEGFA(1) 兩條序列差很多的 sgRNA，才能讓這兩個 alternative hypothesis 同時被排除。

4. 工具與材料:

   - **DSB cluster**: BLESS 在每個雙股 DNA 斷口周圍堆出的一群 reads；全基因組會得到一份 cluster 清單作為候選池。
   - **background DSB**: 細胞自己每天會產生的雙股斷口（複製叉撞牆、活性氧損傷、拓樸酶切口），與 Cas9 切口同時被 BLESS 標起來，需要 peak calling 排除。
   - **forward / reverse reads**: BLESS 定序產生的兩個方向 reads；從切點往右讀的紅色 (forward)、往左讀的藍色 (reverse)，在 Cas9 切點會疊成尖銳對稱的雙峰。
   - **DSB score**: 把「尖銳對稱雙峰」這個 Cas9 切口的形狀特徵量化成的分數；分數越高，cluster 越像真 Cas9 切口。
   - **Ran et al. 2015 Nature pipeline**: 本論文沿用的 Cas9-BLESS DSB score 計算流程（protocol 見 Ran 2015 supplementary），用以與既有 WT SpCas9 BLESS profile 直接對齊比較。
   - **Manhattan plot**: 把整個基因組座標一路鋪平作橫軸、DSB score 作縱軸的散點圖（Fig. 5A,B），用「天際線高樓」直觀呈現 genome-wide off-target 分布。
   - **ranking-based comparison**: 把每條 Cas9 變體的 cluster 按 DSB score 排序、看前 N 名，而非設絕對閾值；避免三條變體 on-target 強度不同造成的偏差。
   - **targeted deep sequencing validation**: 對 BLESS 排序前段的候選 OT 逐一回到 §2-D 的 amplicon 定序量 indel%（Fig. 5C,D、Table S3），補上 BLESS 看不到「是否真有 editing」的盲點。
   - **SpCas9(K855A) 對照**: 排在 WT 與 eSpCas9(1.1) 中間的單點突變變體；用來排除「specificity 改善只是因為整體切弱了」這個 alternative hypothesis。
   - **EMX1(1) + VEGFA(1) 雙 sgRNA**: 同時跑兩條序列差很多的 sgRNA，用來排除「specificity 改善只對某條 guide 有效」這個質疑。

5. 與此篇文章的關係:

這篇論文要證明改造後的 SpCas9(K855A) 與 eSpCas9(1.1) 真的提升了 specificity，最大的反駁威脅是「你只是把 off-target 推到原本沒人查過的地方」，因此整個 specificity 主張不能只靠對已知 OT 的 targeted deep sequencing，必須有一張 unbiased 的全基因組 DSB 地圖來補位，本子項正是負責把這張地圖讀出來的 peak calling 與分類步驟。它的好處在於沿用 Ran 2015 已公開驗證的 DSB score pipeline，三條 Cas9 變體都用同一把尺量，避免「新公式偏袒改造版」的爭議；同時以 ranking 而非絕對閾值比較，可以校正三條變體 on-target 強度不同帶來的偏差，並用紅藍 reads 對稱雙峰的形狀特徵把細胞自發背景 DSB 從候選池剔除。在 pipeline 上，它接在 §2-E 的 BLESS 全基因組 DSB 標記之後，吃 BLESS 產出的 cluster 清單，再把 ranking 前段的候選 OT 交給 §2-D 的 targeted deep sequencing 量 indel%、跑兩個 replicate 做最終裁判，形成「廣度由 BLESS 補、深度由 amplicon 補」的兩層驗證鏈。配合同時跑 EMX1(1) 與 VEGFA(1) 兩條 sgRNA 以及中間擺一條單點突變 K855A 作對照，本子項才能讓「specificity 改善不是來自整體切弱、也不是只對單一 guide 成立、更沒在新位置冒出 off-target」這三個結論同時站得住。
