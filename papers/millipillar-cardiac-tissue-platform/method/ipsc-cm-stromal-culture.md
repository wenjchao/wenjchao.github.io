---
title: "iPSC 來源心肌細胞（CM）與基質細胞的培養與分化"
subitem_id: "2-C"
---

# 主線
提供可重複、達到 ≥85% 純度的 iPSC-CM，並搭配多種基質細胞 (NHCF、iCF、NHDF)，以驗證 milliPillar 平台跨細胞株、跨基質細胞來源的通用性。

# 技術解析
iPSC 是萬用幹細胞，要往心肌走得靠化學提示。作者採用 Burridge et al. *Nat. Methods* 2014 的「化學定義分化法」依序加入 GSK3 抑制劑、Wnt 抑制劑等小分子，第 7 天即可看到培養盤上一團團自跳動細胞——iPSC-CM。但盤上仍混進非心肌雜細胞，作者於是第 10 天切換到「無葡萄糖 RPMI + B27 + 213 µg/mL ascorbic acid」啟動代謝純化 (glucose-starvation / lactate purification)：心肌可把乳酸經乳酸脫氫酶 (LDH) 轉成丙酮酸進入粒線體 TCA，缺糖照常活；其他細胞依賴糖解，沒葡萄糖 3–4 天內 ATP 斷崖凋亡。第 13 天切回正常 RPMI-B27 讓存活心肌回血到第 16 天。

第 17 天解離前先泡 5 µM Y-27632 (ROCK 抑制劑) 4 小時——失去鄰居的單細胞會啟動 ROCK 觸發的脫鉤性凋亡 (anoikis)，預先封鎖可把存活率從 30–40% 拉到 70%。接著用 95 U/mL collagenase type II + 0.6 mg/mL pancreatin 在低鈣解離緩衝液 37 °C 搖 10 分鐘，溫和移液管 trituration 後 100 × g 離心 5 分鐘收細胞，可凍存於 CryoStor CS10。解離後送進流式細胞分析儀，用結合 cardiac troponin T (cTnT，心肌肌節專屬調節蛋白) 的螢光抗體逐顆量純度，要求 ≥85% 才能進下游組織製造。門檻設太高大多批次會被卡、設太低則雜細胞稀釋肌條的收縮力與電耦合品質；跳過純化更會讓心肌被持續增殖的纖維母細胞擠到一邊，肌條 1–2 週內被纖維化拉變形。

心肌組織不是只有心肌細胞，還需要纖維母細胞 (fibroblast) 鋪結構支架與訊號交流。作者刻意用三種來源測試：NHCF-V (Lonza，成人心室原代心臟纖維母細胞)、iPS-CF (從 iPSC 自分化的心臟纖維母細胞)、NHDF (Lonza，來自皮膚、與心臟無關的纖維母細胞)。為什麼故意把皮膚 fibroblast 也丟進去？因為要證明 milliPillar 不挑基質——若只用 NHCF 驗證，審稿人會合理質疑「會不會只是這支剛好分泌某個成熟因子？換成別的就不行了？」這種平台無法移植到其他實驗室。三種來源都長出可收縮肌條，才能下「平台不挑基質細胞」這個結論。

# 工具/方法/材料
- **化學定義分化法 (Burridge et al. 2014)**：依序加入 GSK3 抑制劑、Wnt 抑制劑等小分子把 iPSC 推向心肌，第 7 天起出現自跳動細胞。
- **Glucose-starvation / lactate purification**：第 10 天起改用無糖 RPMI + B27 + ascorbic acid，利用心肌獨特的乳酸代謝能力剔除非心肌雜細胞。
- **Y-27632 (ROCK 抑制劑)**：解離前 4 小時泡 5 µM，封鎖 ROCK 路徑避免單細胞 anoikis，存活率從 30–40% 拉到 70%。
- **Collagenase type II + pancreatin**：95 U/mL + 0.6 mg/mL 於 37 °C 低鈣緩衝液 10 分鐘解離細胞層，切斷 ECM 與 desmosome。
- **Cardiac troponin T (cTnT)**：心肌肌節專屬調節蛋白，作為流式純度品管的金標記。
- **Flow cytometry (cTnT+ ≥85%)**：逐顆量螢光的細胞分析儀，把純度門檻訂在 85% 作為下游製造的入口品管。
- **CryoStor CS10**：細胞凍存液，5–10 M cells/mL 條件下保存解離後的 iPSC-CM。
- **NHCF-V (Lonza)**：成人心室原代心臟纖維母細胞，主基質細胞。
- **iPS-CF**：從 iPSC 自行分化得到的心臟纖維母細胞，內部來源備案。
- **NHDF (Lonza)**：皮膚原代纖維母細胞，作為「非心臟來源」的對照以驗證平台不挑基質。

# 與此篇文章的關係
在《milliPillar: A Platform for the Generation and Real-Time Assessment of Human Engineered Cardiac Tissues》中，作者要證明 milliPillar 不僅在特定細胞配方下能用，而是任何實驗室帶自己的 iPSC 與纖維母細胞都能複製。本步驟採用 Burridge 化學定義分化法加乳酸純化拿到 ≥85% iPSC-CM，並刻意配對 NHCF、iCF、NHDF 三種纖維母細胞，解決了「平台是否依賴特定細胞批次」的可重現性質疑。它吃 iPSC 與商業纖維母細胞進來，產出含品管證明的單細胞懸浮液給下游 hydrogel 包埋使用。
