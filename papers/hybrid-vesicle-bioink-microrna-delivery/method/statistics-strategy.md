# 統計檢定策略 (依樣本數動態切換)

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): 統計檢定策略 (依樣本數動態切換)
3. Method: 
   為什麼要看樣本數動態切換檢定？Parametric 檢定（如 ANOVA、t-test）有一個前提：每組資料的母群必須接近常態分佈、各組變異數差不多。樣本數大時 (n > 8 是常見經驗值)，中央極限定理會把樣本平均值的分佈拉成近常態，這個前提通常成立、檢定也夠穩健。但小樣本 (例如 n = 4) 下中央極限定理收斂不夠：母群本身若偏態或有極端值，一兩個極端點就能把樣本平均拉很遠，看起來像「組間有顯著差異」其實只是隨機抖動。non-parametric 檢定（如 Kruskal–Wallis）改用「排名」當資料——把所有數值排成一列看各組排名分佈，極端值只貢獻「最大」這個排名而不貢獻數值大小，對偏態與離群值更穩健。

   本文採用兩條對稱路線。大樣本路線 (n > 8)：先用變異數分析 (one-way 或 two-way ANOVA) 判斷「四組裡至少有一組不一樣」——one-way 看單一因子 (例如只變 NV 種類)、two-way 同時看兩個因子並驗證交互作用 (例如 NV 種類 × 時間點)；ANOVA 顯著後再用 Tukey post hoc 做兩兩比較，並自動校正「比很多次容易誤抓假陽性」的問題。小樣本路線 (n < 8)：改用 Kruskal–Wallis test（ANOVA 的 non-parametric 對應，用排名比較各組），顯著後用 Holm–Sidak 多重比較校正。兩條路線結構對稱，差別只在中間引擎一個是「平均值＋變異數」、一個是「排名」。

   兩個關鍵設計值得拆開看。n = 8 這個切換閾值不是統計理論的硬閾值、而是經驗共識——在大多數生醫實驗中，每組 n ≥ 8 時 ANOVA 對常態偏離的抗性才足夠穩健；低於 8 容易出現假陽性，所以許多生物統計教科書與 biology methods 文獻建議「n < 8 改 non-parametric」。另外，作者把顯著等級分成三層：∗ p < 0.05、∗∗ p < 0.01、∗∗∗ p < 0.001——因為 p = 0.04 跟 p = 0.0001 都算「顯著」，但後者「隨機產生這個結果」的機率只有萬分之一、證據強度差很多。三層星號讓讀者一眼看出某個比較是「剛好踩線」還是「強到不能再強」。所有數值報為 mean ± SD。

   兩個常見失敗模式。第一：不管樣本數直接用 ANOVA + Tukey——在 n = 3~5 下常態與變異數齊一假設沒辦法檢驗，隨機抖動會被誤判為顯著（假陽性），後續結論建立在這些假陽性上、整條論證鏈被誤導。改成 Kruskal–Wallis 雖然檢定力較弱，但宣稱的顯著差異更可信。第二：ANOVA 顯著後跳過 post hoc 直接宣稱某對顯著——ANOVA 只告訴你「至少有一組不一樣」，沒指出是哪一對，跳過 post hoc 等於越權陳述，可能挑到其實沒差的兩組。所以「ANOVA → Tukey」或「Kruskal–Wallis → Holm–Sidak」一定要配套執行。
4. 工具與材料: 
   - **Parametric test**: 假設母群常態分佈、變異數齊一的檢定，包含 ANOVA 與 t-test，n > 8 時較穩健。
   - **Non-parametric test**: 不假設母群分佈、改用排名比較的檢定，包含 Kruskal–Wallis test，小樣本下更安全。
   - **One-way / Two-way ANOVA**: 變異數分析；one-way 看單一因子分多組、two-way 同時看兩個因子並驗證交互作用。
   - **Tukey post hoc test**: ANOVA 顯著後做的兩兩比較，自動校正多重比較的假陽性風險。
   - **Kruskal–Wallis test**: ANOVA 的 non-parametric 對應；用排名比較多組是否來自相同分佈。
   - **Holm–Sidak correction**: 多重比較校正方法，本文用於 Kruskal–Wallis 後的兩兩比較。
   - **Significance levels (∗ ∗∗ ∗∗∗)**: 三層顯著等級分別對應 p < 0.05、p < 0.01、p < 0.001，呈現證據強度差異。
   - **Mean ± SD**: 所有數值的呈現格式：平均值加減標準差，反映集中趨勢與分散度。
   - **n = 8 切換閾值**: 本文採用的經驗閾值；n > 8 走 parametric (ANOVA)、n < 8 走 non-parametric (Kruskal–Wallis)。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了在不同樣本規模下穩定區辨四組水膠 (GelMA / Gel-Lip / Gel-EVs / Gel-hEL) 的力學、釋放、表達量差異，採用了「依樣本數動態切換 parametric / non-parametric」的統計策略。它解決了「小樣本下硬套 ANOVA 容易假陽性」的瓶頸：吃進各組原始量測值與對應 n，產出統一三層星號的顯著比較結果，讓 SEM 孔徑 (n=50)、compression test (n=4)、Live/Dead (n=9) 等不同實驗都有可比較且不誇大的統計依據。
