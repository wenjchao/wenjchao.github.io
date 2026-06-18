# 進入均衡的 case 分析 (Case-based decomposition on f for entry equilibria)

1. 引用自哪篇 paper: value-capture-with-frictions
2. Outline (任務主線): 進入均衡的 case 分析 (Case-based decomposition on f for entry equilibria)
3. Method:
   Stage 1 每家供應商面對「進場（付固定成本 F）vs. 不進場（拿 0）」的選擇。決策邊界就是「進場後預期 value capture 剛好等於 F」這個零利潤條件，套不同情境（自己獨佔、雙寡頭、對手是否進場）就得到多個 f 的方程式，每個方程式的根都是 f 軸上一個臨界值。具體有六個：f_L^D 與 f_H^D 來自 Π_2^D = f(1 − f)(1 − α)V_2 = F 的兩根；\hat f_1 與 \hat f_2 來自 Π_1^D = (1 − f)(1 − α)(V_1 − (1 − f)V_2) = F 的兩根；f^M = 1 − F/((1 − α)V_1) 是 Supplier 1 獨佔零利潤點；\hat f_3 = 1 − F/((1 − α)V_2) 是 Supplier 2 獨佔零利潤點。作者證明六者嚴格排序 \hat f_1 < f_L^D < f_H^D < \hat f_2 < \hat f_3 < f^M。每段裡看 Π_1^D、Π_2^D、Π_1^M 三條水平線哪幾條落在 F 上方，就能判定誰會進場。Proposition 4 切出四大段：低摩擦 (0, f_L^D) 只有 Supplier 1 進場；中段 (f_L^D, f_H^D) 雙家都進；中高段 (f_H^D, f^M) 只有 Supplier 1 進場；高摩擦 (f^M, 1) 全空。Proposition 5 再把「單廠進入」拆細：(\hat f_1, f_L^D) 與 (f_H^D, \hat f_2) 區段 Supplier 1 連雙寡頭都能回本，進場是 dominant strategy，唯一均衡 = Supplier 1 獨佔；(0, \hat f_1) 與 (\hat f_2, \hat f_3) 區段兩家獨佔都賺錢但雙寡頭都虧錢，「我進你不進、你進我不進」都是 pure strategy Nash 均衡——兩個均衡並存、誰勝出在賽局內無法回答。
   四段背後的關鍵是三條曲線形狀：Π_2^D = f(1 − f)(1 − α)V_2 是 f 的倒 U，峰值 (1 − α)V_2/4 在 f = 1/2，所以「Supplier 2 在雙寡頭也賺錢」只在 f_L^D 到 f_H^D 之間成立；Π_1^D 也對 f 倒 U 但峰值更高、退場較晚，所以即使 Supplier 2 已退場，Supplier 1 在雙寡頭情境仍可回本；Π_1^M = (1 − f)(1 − α)V_1 對 f 單調遞減，零點 f^M 是整個故事的右側邊界。三條曲線疊起來把 F 那條水平線切成上方 / 下方交錯的區段。跨過 f_L^D 那一刻，市場結構從「Supplier 1 獨佔」突然切換成「兩家都進」：獨佔時行業總利潤是 Π_1^M − F，雙寡頭時是 Π_1^D + Π_2^D − 2F——多扣一份 F、餅又被分薄，行業總利潤往下跳一階（不是平滑下降）。跨過 f_H^D 時反過來跳回。Figure 5 的粗線就是這種階梯狀曲線，這正是「rivalry × 進入威脅交織出非單調、非連續」的核心數學表現。
   為什麼作者不寫一條統合的 Π_industry(f) 公式，而要拆成 case-based 結構陳述？因為行業總利潤對 f 根本不是連續函數，它在 f_L^D、f_H^D、f^M 三個地方跳階——任何「一條光滑公式」都會掩蓋這些跳躍、反而讓 paper 的核心發現消失。Case-based 陳述讓「每一段裡都是閉式 Π」「跨段的跳由 Proposition 4–5 用語言明示」這兩件事都得到表達。技術上，所有臨界值都是一元二次方程的根公式（不用 fixed-point 定理），所有均衡判定都靠「比較 Π^M, Π^D, F 之間誰大誰小」的不等式枚舉——因為 Stage 1 策略集是離散的 {Enter, Stay out}，賽局是 2 × 2 純策略矩陣，根本用不到 Brouwer / Kakutani 那類連續策略空間的存在性定理。
   兩個常見失敗模式：其一，如果 F 太大（超過 (1 − α)V_2/4 — Π_2^D 的峰值），Π_2^D 永遠低於 F、Supplier 2 在任何 f 都虧錢，雙廠區段 (f_L^D, f_H^D) 變空集合，Proposition 4 退化為「只有 Supplier 1 在某段進入 / 全空」這個無聊版本，整套 rivalry × 進入威脅互動故事垮掉——作者在 footnote 15 強制 F ≤ (1 − α)V_2/4 正是保護這段非空。其二，如果讀者照 Grant (2005) 教科書「五力獨立分析」，把同業競爭與進入威脅分兩欄打分數再加總，會把結構切換的離散跳抹平——摩擦 f 改變一點點可能跨過臨界值切換市場結構、行業總利潤跟著跳階；分開檢查就會把「低摩擦反而行業總利潤更高」這種反直覺判斷錯估成單向結論。Proposition 6 的「α 上升（買方議價力強）反而可能讓供應商總利潤上升」是同類驚喜，也是把單一力量孤立看會錯失的訊號。
4. 工具與材料:
   - **固定進入成本 F**: 供應商若選擇進場必須付的一次性成本；footnote 15 強制 F ≤ (1 − α)V_2/4 以保證雙廠區段非空。
   - **獨佔 value capture Π_i^M (paper Eq. 37)**: Π_i^M = (1 − f)(1 − α)V_i；單家進場時的事後收入。
   - **雙寡頭 value capture Π_1^D, Π_2^D (paper Eqs. 38–39)**: Π_1^D = (1 − f)(1 − α)(V_1 − (1 − f)V_2)；Π_2^D = (1 − f)f(1 − α)V_2；兩家都進場時的事後收入。
   - **六個臨界值 f_L^D, f_H^D, \hat f_1, \hat f_2, \hat f_3, f^M**: 各自為「某情境下零利潤」的方程式根；嚴格排序 \hat f_1 < f_L^D < f_H^D < \hat f_2 < \hat f_3 < f^M。
   - **Proposition 4 四段切分**: f 軸由 f_L^D, f_H^D, f^M 切成四段——單廠 / 雙廠 / 單廠 / 無進入；行業總利潤對 f 不連續、不單調。
   - **Proposition 5 子區間**: 「單廠進入」進一步切成「唯一是 Supplier 1」與「兩家皆可」兩個子集合，後者代表多重 pure strategy Nash 均衡。
   - **pure strategy Nash equilibrium**: Stage 1 在 {Enter, Stay out} 上的均衡；判定全靠「Π^M, Π^D 與 F 之間誰大誰小」的不等式枚舉。
   - **不連續跳躍 (jump in industry profit)**: 跨過臨界值時市場結構切換，行業總利潤呈階梯狀跳；Figure 5 的粗線為其視覺呈現。
5. 與此篇文章的關係:
   在《Value Creation and Value Capture with Frictions》這篇文章中，作者要證明「rivalry 與進入威脅不能分開分析」這個對教科書直覺的反例。他們採用了 case-based decomposition on f：吃進 Stage 2 算出的閉式 Π_i^M, Π_i^D 與固定成本 F，用零利潤條件解出六個臨界值切分 f 軸，產出 Proposition 4–5 的「四段 + 兩個多重均衡子區段」結構，正面解決「行業總利潤對 f 不連續、無法用單一公式表達」的瓶頸。
