# 線性可乘性模型 (multiplicative scaling model)

1. 引用自哪篇 paper: chromatin-structure-regulatory-activity
2. Outline (任務主線): 線性可乘性模型 (multiplicative scaling model)
3. Method: 
   作者把「CRS 與 landing pad 是否獨立」這個概念性假說直接寫成數學式：$E_{ij} = C_i L_j + \varepsilon$，其中 $\varepsilon \sim N(0, \sigma^2)$ 是隨機誤差。$E_{ij}$ 是前一步算出的 log₂ RNA/DNA ratio；$C_i$ 是「CRS i 自己的固有強度」，不論放哪個 landing pad 都一樣；$L_j$ 是「landing pad j 對所有 CRS 統一的倍率」，不論放什麼 CRS 都用這個倍率縮放。因為 $E_{ij}$ 已經在 log 空間，原空間的乘法在 log 空間就是加法，模型可以直接交給 R 語言的線性擬合函數 (`lm()` in R) 處理，寫法大約是 `lm(E ~ CRS + LandingPad)`：把每個 CRS 與每個 landing pad 當類別變數丟進去，工具會替你解出每個係數。為了讓係數可唯一識別，作者把 CRS1 與 LP1 設為「參考基準」(reference level)，其他 $C_i$ 報的是「比 CRS1 強多少」，其他 $L_j$ 報的是「比 LP1 強多少」。

   為什麼挑「乘法」而非「加法」？加法模型 ($E = C_i + L_j$ 在原空間) 等於說「不管 CRS 是強是弱，位置都加一個固定值」；乘法模型則對應「位置是個倍率，強 CRS 被放大得多、弱 CRS 被放大得少，但放大比例相同」。生物機制偏向後者——染色質緻密的位置對所有轉錄因子等比例壓低結合機率，自然呈現同倍率縮放。模型擬合度直接驗證了這個直覺：全資料 Pearson R = 0.90、Spearman $R_s$ = 0.91。為什麼擬合度高就能宣稱「獨立」？邏輯是反證式的——如果 CRS 真的會「挑」landing pad (例如 CRS-A 偏偏在 LP-B 特別強)，$E_{ij} = C_i L_j$ 抓不到 CRS-A 在 LP-B 的異常值、殘差會大。但實際殘差小到只比 replicate 之間的隨機雜訊大一點點。如果真有特異交互存在，其影響規模不可能比實驗本身的雜訊還小——所以「殘差 ≈ replicate noise」就把「強烈特異交互」這個假設擠出去了。

   作者沒有只報全資料 R = 0.90 就收手。第一道補強是「留一交叉驗證」(cross-validation, R = 0.83)：把資料切成幾份，用一部分擬合係數、再拿來預測沒看過的另一部分，重複幾次取平均。這道驗證排除了「考前看答案」式的 overfitting——若模型只是把每個觀察值用來訓練自己的係數、再用同一筆觀察值打分，R 自然會虛高；R 從 0.90 略降到 0.83 但仍然很高，代表模型抓到的是真能泛化的規律。第二道補強是第二代資料：reporter 上游還有第三個元件，最小啟動子 (minimal promoter)，分 Hsp68 與 MinP 兩種。作者把模型擴成 $E_{ijk} = C_i + L_j + P_k$ (log 空間) 再擬合，結果 R = 0.82 仍然很高，說明 promoter 與 CRS、landing pad 三者都是獨立模塊。第二代延伸把「組合性 (modularity)」的適用範圍從「CRS × 位置」推廣到「CRS × 位置 × promoter」。

   這套擬合有兩個常見地雷。第一，前一步「為什麼要取 $\log_2$」的伏筆在這裡兌現：線性擬合工具 `lm()` 本質只會抓加法關係。如果真實關係是 $E = C_i \times L_j$ (乘法)，硬拿原始 ratio 丟 lm() 用加法去擬，模型抓不到「強 CRS 被高倍率放大、弱 CRS 被低倍率放大」這種等比例縮放——殘差圖會呈漏斗形偏離，R 大幅下降。先取 $\log_2$ 就把乘法轉成加法，lm() 才能正確抓到 $C_i$ 與 $L_j$。第二，類別變數一定要指定 reference level：把所有 CRS、所有 landing pad 都做成 dummy variable 一起丟，會出現「所有 $C_i$ 加 1、所有 $L_j$ 減 1 預測值完全不變」的共線性，演算法解不出唯一係數。R 的 `lm()` 預設會自動丟掉每類的第一個 level，但若用自製設計矩陣或其他工具，沒明確挑 CRS1、LP1 當參考基準，模型可能根本不收斂。
4. 工具與材料: 
   - **$E_{ij} = C_i L_j + \varepsilon$**: 本論文核心模型；log 空間下相當於 $C_i + L_j$ 的加性線性回歸。
   - **$C_i$**: CRS i 的固有強度，不隨 landing pad 變動。
   - **$L_j$**: landing pad j 對所有 CRS 統一的倍率，不挑 CRS 序列。
   - **lm() in R**: R 語言內建的線性回歸函數；以 $E$ ~ CRS + LandingPad 即可解出 $C_i$、$L_j$。
   - **reference level**: 類別變數模型必須挑一個 level 當參考基準（本研究選 CRS1 與 LP1）以消除共線性。
   - **cross-validation**: 把資料切成幾份、用一部分擬合再去預測另一部分；本研究 CV R = 0.83，排除 overfitting 疑慮。
   - **extended model with promoter term**: 第二代資料加入 promoter identity 後仍維持線性加性形式且 R = 0.82。
   - **log-additive ≡ multiplicative**: log 空間下的加法等價於原空間的乘法，這是本研究能用 lm() 擬合乘法模型的根本。
5. 與此篇文章的關係: 
   在《A massively parallel reporter assay dissects the influence of chromatin structure on cis-regulatory activity》中，作者要把「CRS 與染色質環境是否獨立」這個概念性問題變成可檢驗的數學陳述。這套線性可乘性模型吃前一步的 $E_{ij}$ 矩陣、用 R 的 `lm()` 解出 $C_i$ 與 $L_j$，並以 R = 0.90 的擬合度反證「特異交互不可能大」，直接把 modularity 假說推到一個可量化的結論，再交給下游 ANOVA 拆分變異。
