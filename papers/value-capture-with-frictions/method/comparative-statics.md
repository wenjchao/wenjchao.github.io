# 期望 value capture 公式與比較靜態 (Closed-form expectation & comparative statics on f)

1. 引用自哪篇 paper: value-capture-with-frictions
2. Outline (任務主線): 期望 value capture 公式與比較靜態 (Closed-form expectation & comparative statics on f)
3. Method:
   把 Table 1 列出的四種「買方可接觸到哪些供應商」的機率當作權重，分別乘上「在那個情境下由核加 α 算出的 value capture」，加總得到單一閉式公式 V_G、Π_1、Π_2，每個變數都是 (f, V_1, V_2, α) 的代數函數，不再有隨機項。閉式 (closed-form) 在這裡指「用有限步加減乘除、冪次寫出來的代數式」——可以直接對任何變數做偏微分得到代數結果，後面 Proposition 1–3 的方向與曲率結論才能用「符號判斷」（這個式子是正還是負）解掉。Supplier 1 的 Π_1 拆兩項：第一項 (1 − f_1)(1 − f_2) 是「兩家都到場」的機率，此時 Supplier 1 從 V_1 − V_2 議價區間拿走 1 − α 比例；第二項 (1 − f_1)f_2 是「Supplier 1 到、Supplier 2 缺席」的機率，此時 Supplier 1 變成獨佔，可以從整個 V_1 區間拿走 1 − α 比例；兩項合併整理得到 Π_1 = (1 − f_1)(1 − α)(V_1 − (1 − f_2)V_2)。Supplier 2 只在「自己到、Supplier 1 沒到」這唯一情境拿到錢：Π_2 = f_1(1 − f_2)(1 − α)V_2。總價值期望則為 V_G = (1 − f_1)V_1 + (1 − f_1)f_2 V_2（paper Eq. 16）。
   比較靜態（comparative statics）就是「拿一階偏微分看：一旦摩擦增加一點點，誰賺的會變多還變少」，正負號就是方向。再做二階偏微分，可以讀出兩類額外訊息：曲率是凹還是凸（這就是 Proposition 2「倒 U 型」的判讀），以及兩個變數的互動效應 cross-partial（例如 ∂² Π_1 / ∂f_1 ∂f_2 是「對手摩擦增加時，自己摩擦的邊際成本如何變」，這就是 Proposition 1 (iii)「策略替代品」的數學判讀）。因為 Π_i 已經是顯式多項式函數，對 f、V_i、α 都能直接寫出代數導數，符號判斷只需要比較 V_1 / V_2、f / (1/2) 這類簡單不等式，所以整篇 Proposition 1–3 都不需要動用 envelope theorem 或 Topkis 的 monotone comparative statics 那些設計給「最佳化解隱式於 first-order condition」的高階機器。
   拿這套工具去讀 Π_i 對 f 的曲線，得到 Proposition 2 的倒 U 型結果。Π_2 = f(1 − f)(1 − α)V_2 是 f 的二次式，對 f 微分得 (1 − α)(1 − 2f)V_2，零點 f_2^* = 1/2。機制是：劣勢供應商只有在「Supplier 1 剛好沒被買方撮合到、自己卻被撮合到」這一格才賺到錢，這格機率 f(1 − f) 在 f = 1/2 最大。Π_1 對 f 的零點 f_1^* = 1 − V_1 / (2V_2)，需 V_2 > V_1 / 2 才落在 (0, 1) 內出現倒 U；若 V_2 ≤ V_1/2 則 Π_1 對 f 單調遞減、f_1^* = 0——劣勢供應商太差時，Supplier 1 即使對手在場也能從 V_1 − V_2 拿到不錯回報，沒誘因「希望對手消失」。又因為 V_1 ≥ V_2 必導致 f_1^* ≤ 1/2 = f_2^*，弱供應商永遠偏好更高摩擦——它只有在獨佔時賺錢，更希望把對手鎖在外面。這正是 Proposition 2 (iv) 的根源。
   Proposition 3 則改用「V_i 與 f 的 cross-partial」這把更銳利的尺。cross-partial ∂² Π_i / ∂V_i ∂f 解讀為「能力提升的邊際回報如何隨摩擦變動」，等同於問「rivalry 減少（f 下降）的同時、是否更值得投資能力（V_i 提升）」這個策略文獻關心的問題。Makadok (2009) 主張兩種策略合力對行業優勢為負，本 paper 在優勢供應商上重現此結果：∂² Π_1 / ∂V_1 ∂f = α − 1 < 0；並擴及劣勢供應商，得到符號隨 f 切換的有趣結果：∂² Π_2 / ∂V_2 ∂f = 1 − 2f，f < 1/2 為正、f ≥ 1/2 為非正。
   整套閉式 + 偏微分流程之所以非省略不可：如果作者沒先整合出閉式 Π_i 而用「每種情境做一次計算再平均」的程序式描述，後面所有「對 f 偏微分看符號」的代數題都做不到——只能對特定 (V_1, V_2, α) 數值跑一張表，看到「Π_2 在某幾點先升後降」的數值徵象，但無法給出 Proposition 2 那種「對所有合法參數都成立」的全域定性結論。同樣地，如果只報 own friction 偏微分、不報 cross friction 偏微分（∂² Π_i / ∂f_1 ∂f_2），則 Proposition 1 (iii)「摩擦是策略替代品」這個結論講不清楚——也就無法解釋「兩家供應商各自做廣告 / 開分店」的努力會互相壓低邊際回報、形成軍備競賽協調問題。
4. 工具與材料:
   - **四情境機率 (paper Table 1)**: 雙寡頭 (1 − f_1)(1 − f_2)、Supplier 1 獨佔 (1 − f_1)f_2、Supplier 2 獨佔 f_1(1 − f_2)、無服務 f_1 f_2；當權重把 Stage 2 撮合結果加權平均成閉式期望。
   - **期望總價值 V_G (paper Eq. 16)**: V_G = (1 − f_1)V_1 + (1 − f_1)f_2 V_2，即四情境下實際撮合的價值期望加總。
   - **Supplier 1 期望 value capture (paper Eq. 17)**: Π_1 = (1 − f_1)(1 − α)(V_1 − (1 − f_2)V_2)，由「雙寡頭分項」與「Supplier 1 獨佔分項」合併而成。
   - **Supplier 2 期望 value capture**: Π_2 = f_1(1 − f_2)(1 − α)V_2，只在「自己到、Supplier 1 缺席」這唯一情境貢獻。
   - **倒 U 型 (inverted U)**: Π_2 對 f 的曲線形狀；Π_1 在 V_2 > V_1/2 時也是倒 U，否則單調遞減。
   - **最佳摩擦 f_i^***: f_2^* = 1/2；f_1^* = 1 − V_1 / (2V_2) 在 V_2 > V_1/2 時為正、否則設為 0；弱供應商偏好更高摩擦（f_1^* < f_2^*）。
   - **策略替代品 (strategic substitutes)**: Proposition 1 (iii) 結論，∂² Π_i / ∂f_1 ∂f_2 < 0；對手摩擦增加時自己降摩擦的邊際回報變小。
   - **Makadok 型 cross-partial (∂² Π_i / ∂V_i ∂f)**: 「能力提升的邊際回報如何隨摩擦變動」；Π_1 上恆為 α − 1 < 0，Π_2 上為 1 − 2f 符號隨 f 切換。
   - **顯式偏微分**: Π_i 是多項式，直接寫導數比較參數即可；不必動用 envelope theorem 或 Topkis lattice-theoretic 機器。
5. 與此篇文章的關係:
   在《Value Creation and Value Capture with Frictions》這篇文章中，作者要證明 rivalry 強度（由摩擦 f 刻畫）如何牽動行業總價值、優勢與劣勢供應商的 value capture。他們採用了 closed-form expectation + comparative statics 這套技術，吃進 Stage 2 由核加 α 算出的四情境 value capture，把它們以 Table 1 的機率加權合成單一閉式 Π_i，產出可直接做一階 / 二階偏微分的代數函數給 Proposition 1–3 用，正面解決「機率匹配導致變數隨機、無法做方向判斷」的瓶頸。
