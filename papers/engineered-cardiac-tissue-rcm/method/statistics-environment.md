# 統計與環境

1. 引用自哪篇 paper: engineered-cardiac-tissue-rcm
2. Outline (任務主線): 統計與環境
3. Method: 

整套統計與環境鎖定走兩條軸。檢定選擇這條：兩個基因型的單一時間點比較 (例如 ΔGAA vs. ψWT 的 active force) 用 two-tailed Student's t-test；同一條組織加藥前後比較 (例如 trequinsin pre/post 的 passive tension) 用 repeated-measures two-way ANOVA 並加 Sidak 校正多重比較 (視設計也會用 Bonferroni 或 Dunnett)；t-test 與 ANOVA 都假設數據近常態，所以在跑檢定前先以 QQ-plot (把數據分位數對標準常態分位數作圖，越貼直線越像常態) 評估常態性。可重現性這條：所有統計圖在 GraphPad Prism 9 上重新繪製，影像分析腳本以 R Studio 4.0.2 與 Python 3.8.12 (Anaconda 發行版本) 執行，所有自寫程式碼推上 GitHub (https://github.com/GVNLab)、所有原始資料上傳 Mendeley (https://doi.org/10.17632/p5gfdv6skr.1)。任何人都能拿同一版 Prism / R / Python 跑同一份原始資料、得到完全相同的圖與 p 值。

為什麼 trequinsin pre/post 一定要用 repeated-measures two-way ANOVA 而不是獨立樣本 t-test？因為同一條 ECT 加藥前後量到的兩個讀值不是獨立的——它們共享這條組織的基線特性 (製作批次、細胞密度、柱頭錨點位置)。若硬用獨立樣本 t-test，這條組織自身基線變異會被算進組間變異、把訊噪比拉低，可能讓真有的藥效讀不出來。Repeated-measures ANOVA 的做法是把總變異拆成兩塊：「不同條組織之間的基線差異」(between-subjects)、「同一條組織前後變化」(within-subjects)。藥效只跟後者有關，所以從分母把前者扣掉、檢定威力大幅提升。Two-way 則是同時考慮兩個變數 (例如基因型 × 處理時間)，並用 Sidak 校正多重比較避免 p 值膨脹。這個設計直接對應臨床上「同一病人服藥前後比較」的格式。

為什麼有時用 Sidak、有時用 Bonferroni、有時用 Dunnett？三個方法的核心差別在「假設多嚴格 + 適合什麼比較設計」。Bonferroni 最直覺也最保守：把顯著性閾值 α 直接除以比較次數 (例如做 10 次比較就把 α 從 0.05 縮到 0.005)，完全不假設比較之間獨立性，但會把真效應也壓掉、power 偏低。Sidak 用 $1 - (1 - \alpha)^{1/n}$ 替代，在比較之間獨立時略寬鬆一點，是「ANOVA 內所有兩兩比較」常用的校正。Dunnett 專為「多個處理組對同一個對照組」設計 (例如 5 種濃度的藥對 DMSO 對照)，因為只比 5 次而非 5×4/2 = 10 次，校正強度更輕、power 比 Bonferroni 高很多。作者依實驗設計選對應方法——pre/post + 基因型雙因子用 Sidak；只跟單一對照比時用 Dunnett；最保守的情境用 Bonferroni 收尾。

三類問題會分別侵蝕結論可信度。第一，沒校正多重比較：每次比較有 5% 偽陽性風險，做 10 次比較整體偽陽性機率衝到 1 - (0.95)¹⁰ ≈ 40%——意思是即使所有處理都無效，幾乎一定會撈到「至少一個 p < 0.05」的假陽性 hit。作者用 Sidak / Bonferroni / Dunnett 把家族錯誤率壓回 0.05。第二，沒檢驗常態：t-test 與 ANOVA 都假設殘差近常態，若數據明顯偏態 (例如 passive tension 在 RCM 組有長尾)，p 值會嚴重失真；QQ-plot 是把樣本分位數對標準常態分位數作圖、越貼直線越像常態，可以一眼判斷是否該改用非參數檢定。第三，沒鎖軟體版本：R 與 Python 套件更新可能換預設演算法 (例如 ANOVA solver、亂數種子)，同一份原始資料在不同版本上跑會得到不同數字。作者把版本鎖在 R Studio 4.0.2、Python 3.8.12 (Anaconda)、Prism 9，並把所有自寫程式碼與原始資料公開，任何人都能完整重現所有數字與圖。

4. 工具與材料: 
- **two-tailed Student's t-test**: 兩個獨立基因型單一時間點比較的標準檢定；雙尾代表「不假設方向」。
- **repeated-measures two-way ANOVA**: 同一條 ECT 加藥前後配對 + 兩因子設計；把組織自身基線變異從分母扣掉、檢定威力遠大於獨立 t-test。
- **Sidak 校正**: 比較之間獨立時的多重比較校正 ($1 - (1-\alpha)^{1/n}$)；ANOVA 內兩兩比較常用。
- **Bonferroni 校正**: 把 α 直接除以比較次數的最保守校正；不假設比較獨立性。
- **Dunnett 校正**: 多處理組對單一對照組的專用校正；比較次數少、power 比 Bonferroni 高。
- **QQ-plot 常態性評估**: 把樣本分位數對標準常態分位數作圖；越貼直線越像常態，是 t-test / ANOVA 前的必要檢查。
- **GraphPad Prism 9**: 所有統計圖的繪製與檢定執行環境，版本鎖定確保重現性。
- **R Studio 4.0.2 / Python 3.8.12 (Anaconda)**: 影像分析與訊號處理 (pracma::findpeaks、computer vision tracking) 的執行環境；版本固定。
- **GitHub + Mendeley 公開**: 原始程式碼 (https://github.com/GVNLab) 與原始資料 (https://doi.org/10.17632/p5gfdv6skr.1) 公開，任何人都能完整重現結果。

5. 與此篇文章的關係: 
在《Engineered cardiac tissue model of restrictive cardiomyopathy for drug discovery》這篇文章中，作者每組 ECT 只有 3–12 條樣本卻要支撐「ΔGAA vs ψWT 力學差異」與「trequinsin 救援效果」等核心結論。為此他們設計統計與環境管理，吃前面所有模組吐出的數字 (active force、passive tension、τ、Pearson R、肌節角度等)，依比較設計選用 t-test / repeated-measures ANOVA / 適配的多重比較校正、並用 QQ-plot 確認常態，最後把整套程式碼與原始資料鎖在固定版本軟體上公開——產出可重現、可審計的 p 值，讓單一病例的小樣本研究仍能通過審稿人「N = 1 怎麼推廣」的挑戰。
