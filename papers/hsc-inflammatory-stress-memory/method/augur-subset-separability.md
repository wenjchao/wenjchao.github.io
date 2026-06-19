---
subitem_id: "3-F"
title: "Augur 子集可分性檢定"
---

# Augur 子集可分性檢定

**Subitem:** 3-F · **Slug:** `augur-subset-separability`

## 主線
量化 PBS / TNF / LPS 三條件下 HSC-I vs HSC-iM 「能不能被機器學習器分開」，以隨機森林在 150 次 subsample 上的 AUC 分佈作為「TNF/LPS 是否真的把記憶寫進染色質」的客觀指標。

## 技術解析
差異表現 (DEG) 在 HSC-I vs HSC-iM 這種記憶細胞研究有兩個痛點：兩群即使有真實差異，每個單一基因差距都不大，顯著基因清單往往不長；且 reviewer 容易質疑『你的子集只是 over-clustering 出來的假群』。Augur (Skinnider et al. Nat Biotechnol 2021) 換個角度：把兩群當分類問題，訓練一個機器學習器來區分，看它在『從未看過的新細胞』上能不能猜中。隨機森林 (random forest，同時訓練很多棵決策樹、每棵看不同子集的特徵 + 不同子集的細胞、最後合議投票) 特別適合這個問題——對特徵共線性魯棒、訓練快，且『袋外誤差』(out-of-bag error，每棵樹只看 63% 細胞，剩下 37% 自然當測試集) 本身就是天然 cross-validation。本研究用 Augur v1.0.3。

兩種模態各自選最適合 random forest 的特徵格式。RNA 端用 top 2,000 highly variable genes (HVG)——細胞之間表現量變異最大的 2,000 個基因，是 single-cell 分析的標準特徵集合；若直接餵 ~20,000 個基因，分類器會被雜訊壓垮並容易 overfit。ATAC 端問題更嚴重：raw peak 矩陣可能有 100,000+ 個 peak、每個 peak 在每顆細胞只有 0–2 個 fragment 非常稀疏，random forest 在二元稀疏矩陣上分裂效益低、樹深度上不去，即使兩群真有差異 AUC 也會被噪音壓到接近 0.5。LSI (latent semantic indexing) 把這 100,000 個稀疏 peak 壓成 50 個連續變數，每個都帶整體染色質模式的訊號，random forest 才能跑出穩定 AUC。

Augur 每一輪從 HSC-I 與 HSC-iM 各隨機抽固定數目細胞訓練隨機森林、剩餘當測試集算 AUC——若直接拿全部細胞訓練再回測，AUC 永遠接近 1 (overfitting)，看不出條件間差異。重複 150 次目的有二：得到 150 個 AUC 的分布而不只一個點值才能算平均與信賴區間；PBS、TNF、LPS 三條件之間做統計比較需要每條件都有分布。作者用 two-sided Wilcoxon rank-sum test 比較條件間 AUC 分布——AUC 被限制在 [0, 1] 分布偏態，t-test 假設常態分布會把信賴區間算錯；Wilcoxon 是非參數檢定只看排序，對 AUC 的偏態較穩健。

只在 PBS 條件下跑 Augur 得 AUC = 0.7 只能說『HSC-iM 跟 HSC-I 在 PBS 下勉強可分』，無法回答『TNF/LPS 是不是把記憶刻深了』。三條件各跑一次後可以做兩種對比：跨條件比 AUC——若 TNF 條件下 AUC = 0.95 顯著高於 PBS 條件下 0.7，這個提升只能用『TNF 把兩群差異拉開』解釋；同樣在 ATAC 端再跑一遍——若 ATAC 端 AUC 在 TNF 下也顯著上升，就直接證明『記憶刻在染色質而非短暫 mRNA』。Augur 在三條件 × 兩模態的設計裡是核心定量證據——比 GSEA 之類的單檢定更難被質疑。

## 工具與材料清單 (Toolchain)
- **Augur v1.0.3**：把兩群當分類問題、用隨機森林算可分性的工具；Skinnider et al. Nat Biotechnol 2021 ref. 93。
- **Random forest**：同時訓練很多棵決策樹、每棵看不同子集特徵與細胞、最後合議投票的分類器；對共線性魯棒，訓練快。
- **AUC (area under ROC curve)**：分類器在不同閾值下 true positive rate vs false positive rate 曲線下面積，0.5 為擲銅板、1.0 為完美。
- **150 次 subsample**：每輪各從兩群隨機抽固定數目細胞訓練、剩餘當測試集；分布用於跨條件 Wilcoxon 比較。
- **Out-of-bag (OOB) cross-validation**：隨機森林每棵樹只看 ~63% 細胞、剩下 37% 自然當測試集，避免 overfitting。
- **Top 2,000 HVG**：細胞之間表現量變異最大的 2,000 個基因，single-cell 標準特徵集合。
- **LSI (50 components)**：ATAC 端標準的稀疏矩陣降維 (類似 TF-IDF + SVD)，把 100,000+ 個 peak 壓成 50 個連續變數。
- **Two-sided Wilcoxon rank-sum**：非參數兩組分布比較，對 AUC 這種有界、偏態的量比 t-test 穩健。
- **三條件 × 兩模態設計**：PBS / TNF / LPS × RNA / ATAC 六格 Augur，跨條件 AUC 提升證明 TNF/LPS 把差異拉開；ATAC 端提升直接證明記憶刻在染色質。
