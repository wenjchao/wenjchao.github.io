# Kaplan-Meier 存活分析與 Log-rank 檢定

1. 引用自哪篇 paper: pediatric-tri-tube-valved-conduit
2. Outline (任務主線): 把「freedom from moderate regurgitation」當成 valve 存活時間，比較 tube-in-tube (group 0) 與 tri-tube (group 1) 以及 Gen 1 vs Gen 2 的曲線差異。
3. Method:

存活分析原本是拿來描述「一群病人從某個起點到死亡之間的時間」的方法。作者把這個框架借過來：每顆瓣膜的起點是植入手術那天，「死亡」則重新定義成「回流首次升到中度」這個功能失效的時刻——這段時間叫 freedom from moderate regurgitation（瓣膜還沒漏到中度的存活時間）。把每組所有瓣膜的這段時間蒐集起來，畫一條 Kaplan-Meier 存活曲線：橫軸是時間、縱軸是「目前還沒到 endpoint 的比例」（從 1 開始）。每當有一隻動物的瓣膜回流首次達中度，曲線在那個時間點往下掉一個格子；若有動物因為非瓣膜原因中途退出，會在那個時間點打一個叉但不下墜（這叫 right-censoring）。曲線下墜得越慢、停在越高位置，代表越多瓣膜撐得越久。但光看兩條曲線「一條高、一條低」還不能下結論，可能只是樣本少造成的隨機抖動。Log-rank (Mantel-Cox) 檢定的做法是在每個有事件發生的時間點問：「假設兩組真的沒差，這個時間點預期會有多少隻瓣膜失敗？實際上看到幾隻？」把所有時間點的「實際 vs 預期」差異累加成一個卡方型統計量再換算成 *P* 值。作者算出 tube-in-tube vs tri-tube *P* = 0.0024（差異強烈、新設計顯著延長存活）、Gen 1 vs Gen 2 *P* > 0.05（沒測出顯著差異，但樣本太少不能反推「兩代沒差」）。

right-censoring 在這篇 valve 研究中扮演關鍵角色，必須拆開講。Gen 2 兩隻撐到 52 週還沒漏到中度就被計畫性犧牲——這兩隻在 Kaplan-Meier 框架裡屬於 censored 而非 failure：曲線在 52 週那一時間點打叉、不下墜，但這兩隻會從之後的剩餘樣本分母裡退場。這個設計確保「即使有人中途離開，仍能用剩下還在被追蹤的樣本估計失敗比例」，不會把 censored 動物錯誤地算成失敗或永遠成功。實作上作者用 GraphPad Prism——它的 Kaplan-Meier + Log-rank 是生醫實驗室的標準工具，輸入時間與事件指標就能算出 *P* 值與信賴區間，不必自己寫程式。為什麼是事後分析 (post hoc)？樣本數估算階段作者已經用 hazard ratio = 0.125 預估「需要 6 隻 tri-tube 羊」；存活分析則是「實驗跑完後再回頭把實際資料丟進去檢定當初預期的差異有沒有出現」。檢定結果還順手報「assumed hazard ratio = 0.125, actual = 0.123」——預期與實測幾乎一致，代表當初的 power 估算合理。

Gen 1 vs Gen 2 的 Kaplan-Meier 比較 *P* > 0.05 不能直接解讀成「兩代沒差」，所以作者另外補一招。Kaplan-Meier 把每顆瓣膜壓成「何時失敗」這個單一時間點，當 cohort 只有 3–4 隻時，幾個資料點根本拉不出顯著差異。為了補強，作者改抓「取出當下的 pulmonary insufficiency index」這個連續變數做 t test：每顆瓣膜給一個 0~5 的指數，再比兩組均值。連續變數能讓 t test 在小樣本下仍保有比類別變數高的敏感度，於是測出 *P* = 0.015 支持「Gen 2 設計確實減少回流」。簡言之，Kaplan-Meier 看時間軸長度、t test 看終點當下的嚴重度，兩個一起補出存活分析在小樣本下看不見的設計差異。

這套存活分析有兩個容易誤用的地方要小心。第一是 *P* > 0.05 的解讀：正確意思是「沒有足夠證據說兩組不同」，不是「證明兩組相同」。Gen 1 (n = 4) 與 Gen 2 (n = 3) 的 Kaplan-Meier 比較從一開始就沒有被預先 power——原本 n = 6 是 group 1 整體相對 group 0 的計算，中途分裂成兩代之後任一子組都不足以單獨檢定，所以這個 *P* 值只能說「樣本太少看不出」。如果直接寫成「兩代設計沒差」就會嚴重誤導讀者，這也是為什麼作者特地補 insufficiency index 的 t test 才能宣稱「Gen 2 在功能指標上確實優於 Gen 1」。第二是 censoring 編碼必須精準：Gen 2 三隻中有兩隻撐到 52 週還沒漏到中度，依設計被計畫性犧牲，在 Kaplan-Meier 框架裡應該算 censored。如果工作人員手滑把它們填成 failure，曲線就會在 52 週多掉兩個格子，新設計看起來提前失效，整條 tri-tube 曲線往下掉，log-rank 比 tube-in-tube 算出來的 *P* = 0.0024 會被稀釋甚至反轉。所以資料登錄階段必須清楚地把「事件 = 中度回流」「Censoring = 計畫性犧牲、非瓣膜原因退出」兩個欄位分開填。

4. 工具與材料:

   - **Kaplan-Meier survival curve**: 把「目前還沒到 endpoint 的比例」隨時間畫成階梯曲線。
   - **Freedom from moderate regurgitation**: 把「回流首次升到中度」當作瓣膜的失敗事件，這段時間視為存活時間。
   - **Log-rank (Mantel-Cox) test**: 在每個事件時間點累加「實際 vs 假設沒差時的預期」差異，換算成 *P* 值判斷兩條曲線是否真的不同。
   - **Right-censoring**: 在事件未發生前退出觀察的資料情境；曲線在該時間點打叉不下墜，但會從之後分母退場。
   - **GraphPad Prism**: 生醫常用統計軟體，輸入時間與事件指標即可跑 Kaplan-Meier + Log-rank。
   - **Post hoc analysis**: 實驗跑完後再回頭做的檢定；本實驗的存活檢定是設計後分析。
   - **Hazard ratio (assumed 0.125, actual 0.123)**: 事前假設與實測幾乎一致，代表當初 power 估算合理。
   - **Pulmonary insufficiency index t test**: 在 cohort 過小時用連續變數補 Kaplan-Meier 的敏感度不足，Gen 1 vs Gen 2 *P* = 0.015。

5. 與此篇文章的關係:

這篇論文要回答的核心問題是：新設計的 tri-tube valve 是否真的比前一代 tube-in-tube 在生長中的羊體內撐得更久，因此需要一個能把「瓣膜撐多久才開始嚴重漏血」量化成統計差異的工具，Kaplan-Meier 存活分析正是擔當這個角色——作者把「回流首次升到中度 (freedom from moderate regurgitation)」重新定義為瓣膜的失效事件，把每顆瓣膜從植入到失效的時間畫成階梯曲線，再用 Log-rank (Mantel-Cox) 檢定把兩條曲線的差異換算成 P 值。它的好處是能處理 right-censoring：Gen 2 中兩隻撐到 52 週仍未漏到中度而被計畫性犧牲的羊，可以在不被誤判成失敗、也不被當作永遠成功的情況下從分母退場，這對小樣本動物實驗特別關鍵。Kaplan-Meier 跟前段的 Schoenfeld 樣本數估算 (n = 6, 假設 hazard ratio = 0.125) 形成事前 / 事後對照，實測 hazard ratio = 0.123 幾乎吻合，證明 power 估算合理；同時也與 echocardiography 系列功能追蹤搭配——超音波負責偵測每顆瓣膜「何時」漏到中度提供事件時間，存活分析則負責把這些時間點集合成可比較的曲線。最後，因為 Kaplan-Meier 把瓣膜壓成單一時間點，在 Gen 1 (n = 4) vs Gen 2 (n = 3) 這種極小樣本下檢定不出差異，作者再以 explantation 當下的 pulmonary insufficiency index 做 t test (P = 0.015) 補上連續變數的敏感度，兩種檢定一搭一唱才能既證明 tri-tube 顯著優於 tube-in-tube (P = 0.0024)、又支持 Gen 2 在功能指標上優於 Gen 1。
