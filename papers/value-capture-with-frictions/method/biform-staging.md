# Biform game 時序基底 (Biform staging convention)

1. 引用自哪篇 paper: value-capture-with-frictions
2. Outline (任務主線): Biform game 時序基底 (Biform staging convention)
3. Method:
   作者為所有後續擴充建立一條統一的『上下半場』時序：上半場是 Stage 1 非合作賽局，每家供應商各自獨立做結構決定——基準模型不需要這個階段；進入擴充章決定『要不要進場』(Enter / Stay out)；資源開發擴充章決定『要砸多少錢練功』 (r_i ≥ 0，成本是二次型 c(r_i)=c·r_i^2)。下半場是 Stage 2 合作賽局：給定上半場行動之後，先由隱形玩家 nature 擲骰決定『今天哪些供應商被買方看見』(對應前一節的摩擦)，再用核加上 α 議價權重把每個玩家的期望 value capture 算出來。上半場廠商選擇自己的策略時，已完全推算過下半場會怎麼分餅再反推回去——這就叫 rational expectations，把『下半場分配 → 上半場決策依據』的因果鏈鎖緊，整個賽局只剩一個自洽均衡可解。這套設計叫 biform game (Brandenburger & Stuart 2007)，字面就是『兩個形式』拼起來。
   求解方式是逆向歸納 (backward induction)：先解下半場、再倒推上半場。給定上半場所有可能的行動組合，每一種都丟進核加 α 算出對應的 Π_i；這些 Π_i 就成為上半場每家廠商在做 Nash equilibrium 計算時的『期望收益表』。因為下半場的分配規則在所有上半場狀態下都通用，所以倒推時不必每次重來——這正是 biform 把通用合作賽局結構放在 Stage 2 的設計優勢。
   為什麼非建立這條 staging convention 不可？後續兩個擴充都需要『先做結構決定、再分餅』這條時序：進入決策必須在『進場後預期能分多少』之前先做；資源投資同樣是『投資完才上場交易』。如果每章都自己重新定義時序，作者就得寫兩遍核加 α 加摩擦的映射。統一 staging 讓 Stage 2 變成一個共用模組，所有擴充把自己的 Stage 1 結構決策插上去即可。一個小細節：第 5 部分把 Π_i 的含義從『Stage 2 value capture』重載為『分餅扣掉投資成本後的淨利潤』，作者在 footnote 16 明示這個重載——這是為了讓不同章的命題可以直接對照，犧牲符號嚴格性換來表達連貫。反過來說，如果跳過 staging 直接把進入或投資塞進賽局：少了 Stage 1，進入與投資只能當作模型外的初始條件，無法從廠商的最大化問題內生推出；少了 rational expectations，上半場行動可能與下半場結果不一致——廠商以為自己進場後能分 100 元決定進場、結果下半場核算出他只能分 30 元，均衡就破功了。
4. 工具與材料:
   - **biform game**: Brandenburger & Stuart 2007 提出的兩階段賽局結構：Stage 1 非合作賽局處理結構決定，Stage 2 合作賽局處理價值分配。
   - **Stage 1 (noncooperative)**: 上半場：廠商各自獨立做結構性決策（進入、投資水準），無法協商。
   - **Stage 2 (coalitional)**: 下半場：先由 nature 抽出可接觸子集，再用核加 α 算出每個玩家的期望 value capture。
   - **Nash equilibrium**: 每家廠商都做最佳反應的均衡概念，在 Stage 1 的離散行動空間上使用。
   - **rational expectations**: Stage 1 決策時廠商已完全推算過 Stage 2 的分配結果再反推回去，鎖死兩階段一致性。
   - **backward induction**: 逆向歸納——先解 Stage 2 封閉式 Π_i，再把這張收益表餵給 Stage 1 求 Nash equilibrium。
   - **c(r_i)=c·r_i^2**: 資源投資的二次型成本函數，c > 0 是資源開發難度的單一刻畫參數。
   - **Π_i 符號重載**: footnote 16：在 §5 資源開發章，Π_i 被重新定義為『Stage 2 value capture 減去投資成本』。
5. 與此篇文章的關係:
   在《Value Creation and Value Capture with Frictions》這篇文章中，作者為了把進入決策與資源投資兩個離散選擇與合作賽局分配整合，採用了 biform game 兩階段時序。它解決的瓶頸是：純合作賽局無法表達『有人選擇不進場』這種離散行動，純非合作賽局又得指定一個價格機制 (Bertrand / Cournot) 才能談分配。這條 convention 吃 2-A 與 2-B 的特徵函數與摩擦為輸入，產出 Stage 2 的閉式 Π_i 與 Stage 1 的離散決策空間，直接交給後續進入與資源開發兩個擴充共用。
