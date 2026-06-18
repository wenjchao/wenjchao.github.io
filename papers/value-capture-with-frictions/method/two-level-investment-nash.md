# 資源開發 biform game 的 Nash 均衡刻畫 (Two-level investment characterization for endogenous heterogeneity)

1. 引用自哪篇 paper: value-capture-with-frictions
2. Outline (任務主線): 資源開發 biform game 的 Nash 均衡刻畫 (Two-level investment characterization for endogenous heterogeneity)
3. Method:
   資源投資完成後，誰是領先者由最終 value creation V_i + r_i 是否大於對手決定。利潤函數要分兩段寫（paper Eq. 49）：若領先，公式是 (1 − f)(1 − α)((V_i + r_i) − (1 − f)(V_j + r_j)) − c r_i^2；若落後，公式只有 f(1 − f)(1 − α)(V_i + r_i) − c r_i^2。換句話說，每家做投資決策時得先假設「我會領先還是落後」，再套對應那條公式做最佳化，這就是 piecewise（分段）的意思。對 r_i 取一階微分，領先段的邊際回報是 (1 − α)(1 − f)、落後段的邊際回報是 (1 − α)f(1 − f)。直覺：領先者只要被買方撮合到（機率 1 − f）就能在每個客戶身上多賺 (1 − α) 比例的能力提升；落後者只有「自己到、對手缺席」這唯一情境才賺，發生機率 f(1 − f) 比 1 − f 小一截。把邊際回報除以 2c（凸成本一階條件）就得到兩個最適投資水準：r^H = (1 − f)(1 − α)/(2c)、r^L = f(1 − f)(1 − α)/(2c) = f · r^H。差距 r^H − r^L = (1 − α)(1 − f)^2/(2c) 隨摩擦 f 上升而下降——摩擦越大、強弱兩種劇本下的投資差越小。這是 Lemma 1 的內容。
   Lemma 1 把策略空間從「所有非負實數 r_i ≥ 0」壓縮到「只有兩個離散選項 {r^H, r^L}」。在這之上 Proposition 7 證明對稱均衡不存在：若兩家都重押 r^H，Supplier 2（V_2 ≤ V_1）反正注定落後，偏離到 r^L 可以保住落後地位、卻省下大量資源成本，顯式利潤差 (1 − α)^2(1 − f)^4 / (4c) > 0；若兩家都輕押 r^L，Supplier 1 偏離到 r^H 不只能維持領先、還能大幅利用領先邊際回報，所以也想偏離。兩條對稱路線都被同方向的偏離誘因擊破，剩下的均衡必定是「一家 r^H、一家 r^L」的不對稱結構。當 V_1 = V_2 時這個結論也成立——Corollary 1 證明兩家初始完全相同也會自動分化，這就是 endogenous heterogeneity（內生異質性）。
   剩下的問題是「誰拿 r^H、誰拿 r^L」可以是哪些組合。leapfrogging 均衡 (r_1^* = r^L, r_2^* = r^H) 必須三條件同時成立：(a) 可行性 V_1 + r^L < V_2 + r^H；(b) Supplier 2 不偏離到 r^L；(c) Supplier 1 不偏離到 r^H。Appendix 2 用顯式利潤代數推得 (b)(c) 都等價於 V_1 − V_2 < (1 − α)(1 − f)^2 / (4c)，這比可行性條件 V_1 − V_2 < r^H − r^L = (1 − α)(1 − f)^2 / (2c) 更嚴格（差一半），所以 (b)/(c) 才是真正約束。Proposition 7 因此斷言：當 V_1 − V_2 < (1 − α)(1 − f)^2 / (4c)，sustaining 與 leapfrogging 兩個均衡並存；當 V_1 − V_2 超過門檻，只剩 sustaining 均衡為唯一 pure strategy Nash 均衡。門檻右側隨 f 上升而下降，意味著摩擦越大、能容忍的初始差距越小、翻盤門檻越嚴；同時 r^H − r^L 也被摩擦壓小，落後者即使賭重押也搶不到足夠能力提升反超。這正是摘要說「摩擦保護弱者活下來、卻不幫他翻盤」的數學機制——摩擦對 sustainability 是正向、對 leapfrogging 是反向。
   為什麼 Proposition 7 的均衡判定都靠閉式不等式而非 Brouwer / Kakutani 之類的固定點定理？因為 Lemma 1 把策略空間離散到 {r^H, r^L}，Stage 1 退化為 2 × 2 對局，所有均衡可用「比較四個利潤差是否同號」窮舉判定。閉式不等式 V_1 − V_2 < (1 − α)(1 − f)^2 / (4c) 同時給出 leapfrogging 存在條件與 sustaining 唯一性條件。Brouwer / Kakutani 是為「連續策略空間 + 連續最佳反應對應」設計的高階機器，本模型透過分段把連續問題降到離散，這些定理全程用不到。多重均衡的選擇則靠 Schelling (1960) 的 focal point 概念——賽局內部無法決定哪個被玩，社會、文化、敘事因素讓某個均衡「顯眼」、雙方共同預期它會發生。作者把 focal point 連結到「管理者藉由形塑預期建立可持續優勢」的策略涵義，給予「期望管理」一個正式的賽局論意義：誰先讓對方相信自己會贏，那個均衡就成真。
   兩個常見失敗模式。其一：Π_i 在「自己能力剛好等於對手」這個點不可微——左導數 1 − f、右導數 f(1 − f)。如果用光滑近似硬寫成一條函數做 FOC，會把這個「領先 vs. 落後」的關鍵跳躍塗掉，得到的單一最適會落在 r^H 與 r^L 之間的某個中間點，但這個中間點誰也不會選——既不是領先者的最佳反應、也不是落後者的最佳反應。整個 endogenous heterogeneity 與 leapfrogging 結構從根本被抹平，paper 想證明的兩大命題都消失。其二：如果作者忽略 leapfrogging 與 sustaining 並存、只報告 sustaining 均衡，sustainability 就退化為「初始優勢一定可持續」的靜態結論。但 Proposition 7 的真正貢獻是「sustainability 是策略性問題不是天命」：當 V_1 − V_2 落在門檻以下，leader 的優勢並非不可撼動。Figure 7 把 V_1 − V_2、f、c 三軸切出「sustainability region」，也是依賴多重均衡是否消失這個連續調控機制。少了多重均衡這層，footnote 19 對 sustainability 的策略定義（「follower 是否有誘因 out-invest leader」而非「優勢能維持多久」）就站不住。
4. 工具與材料:
   - **資源開發投資 r_i**: Stage 1 每家供應商選擇的能力提升量；最終 value creation 變為 V_i + r_i。
   - **凸二次成本 c(r_i) = c r_i^2**: 資源開發的單一刻畫，c > 0 為難度參數；二次型保證一階條件解出單一最適。
   - **piecewise profit function (paper Eq. 49)**: 依「自己最終能力是否大於對手」分兩段寫的利潤函數；不可微的分段點正是領先 / 落後身分翻轉的位置。
   - **兩個離散最適水準 r^H, r^L (Lemma 1)**: r^H = (1 − f)(1 − α)/(2c)、r^L = f(1 − f)(1 − α)/(2c) = f · r^H；領先用 r^H、落後用 r^L。
   - **sustaining 均衡**: (r_1^* = r^H, r_2^* = r^L)；初始 leader 維持並擴大領先；恆存在。
   - **leapfrogging 均衡**: (r_1^* = r^L, r_2^* = r^H)；初始弱者反超變領先；存在 iff V_1 − V_2 < (1 − α)(1 − f)^2/(4c)。
   - **翻盤閉式門檻 (Inequality (1))**: V_1 − V_2 < (1 − α)(1 − f)^2/(4c)；同時刻畫 sustainability 邊界，三軸 (V_1 − V_2, f, c) 連續調控。
   - **Schelling focal point**: 多重均衡選擇的賽局外機制；本 paper 連結到「管理者形塑期望」這個策略動作。
   - **Endogenous heterogeneity (Corollary 1)**: V_1 = V_2 時所有 pure strategy Nash 均衡仍 asymmetric，異質性內生於賽局互動。
5. 與此篇文章的關係:
   在《Value Creation and Value Capture with Frictions》這篇文章中，作者要回答「初始優勢能否被翻盤」這個 sustainability 問題。他們採用了 piecewise profit + Lemma 1 + Proposition 7 這套兩階段投資 Nash 刻畫，吃進 Stage 2 的閉式 value capture 公式與凸成本 c r_i^2，產出兩個離散最適投資水準 r^H、r^L 與閉式翻盤門檻 V_1 − V_2 < (1 − α)(1 − f)^2/(4c)，解決「想刻畫動態 sustainability 又不想引入時間軸做 dynamic programming」的瓶頸，並透過多重均衡與 Schelling focal point 給予「管理者形塑預期」一個正式的策略意義。
