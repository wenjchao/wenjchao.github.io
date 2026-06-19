---
subitem_id: "2-A"
title: "血漿 cfDNA 採集與前分析品管 (Pre-analytical handling)"
---

# 血漿 cfDNA 採集與前分析品管 (Pre-analytical handling)

**Subitem:** 2-A · **Slug:** `blood-plasma-cfdna-preanalytical`

## 主線
在抽血、離心、保存到 library prep 的全鏈條中，避免 cfDNA fragment end motif、jaggedness、size 分布被外源性降解污染，以保留後續所有 fragmentomic 訊號的真實性。

## 技術解析
血漿裡的 cfDNA 來自每天死掉的細胞——主要是程序性自殺 (apoptosis)、受傷崩裂 (necrosis) 與少量主動釋放 (active secretion)。細胞核裡的 DNA 平時纏在核小體這種小蛋白球上，細胞瓦解時核酸酶從蛋白球之間的縫隙下刀，留下「剛好繞一顆蛋白球」的 ~167 bp 短片段 (mononucleosome 片段) 與少量「繞兩顆」的 ~330 bp (dinucleosome 片段)。麻煩在於量太少：每毫升血漿大約只裝得下 1,500 份完整基因組量 (genome equivalents)，換算才幾個 nanogram。早期癌的 ctDNA 若只佔萬分之一，任何一個位置實際上只剩零條或一條訊號，整套 library prep 因此必須能從 100 pg–10 ng 的微量 input 出發，且過程中不能再損失。

標準骨架是四步：用含 EDTA 抗凝劑的採血管 (EDTA tube) 抽血、4 小時內處理、做兩輪離心 (double centrifugation) 留上清液、最後從上清液抽 cfDNA。每一步都有理由。EDTA 不只是抗凝劑——它把核酸酶活性所需的鈣、鎂離子綁走，讓核酸酶在試管裡「沒武器」；換成一般紅頭管，鈣留著、酵素繼續切 cfDNA，末端會被吃掉一截。4 小時的時間窗來自白血球的物理耐受：拖太久白血球膜崩、把自己的基因組 DNA 倒進血漿，把本來就稀薄的 cfDNA 稀釋成「血球味」。雙離心則是兩道網：低速網把整顆細胞撈走，高速網把細胞碎片再撈一次，避免後續抽 DNA 時把細胞內 DNA 一起抽出來污染 cfDNA pool。

為什麼採血管與時間窗會直接污染下游？因為兩件事同時發生。第一，白血球破掉後把自己的基因組 DNA 倒進血漿，整鍋 cfDNA 被洗成「血球味」；第二，白血球裡的核酸酶被釋出，繼續在試管裡啃 cfDNA 兩端，造成末端缺一兩個鹼基、雙股對不齊的小缺口 (jaggedness)，連帶讓 cfDNA 末端短序列偏好 (fragment end motif) 從反映體內狀態變成反映「試管放了多久」。把這樣的樣本送下游會出兩層問題：表層是 end motif、jaggedness、size 分布跨 cohort 不可比 (ref 110)；深層是用一批 SOP 不齊的 retrospective 樣本訓出來的機器學習分類器，會把「採血管差異」當成「癌 vs 非癌差異」學起來，換到 SOP 統一的前瞻 cohort 一驗證 AUC 就崩盤——這正是本 review 反覆警告的陷阱。雙離心的第二輪也省不得：少做一輪會讓殘留細胞碎片被一起抽進 library，size 分布跑出 >500 bp 的長片段，把 DELFI 賴以為生的「短 / 長片段比值」直接稀釋掉。

## 工具與材料清單 (Toolchain)
- **apoptosis / necrosis / active secretion**：cfDNA 在血漿中的三大來源：程序性自殺、受傷崩裂、與少量被主動釋出。
- **mononucleosome 片段 (~167 bp)**：DNA 繞一顆核小體蛋白球被保留下來的長度，是 cfDNA size 分布的主峰。
- **dinucleosome 片段 (~330 bp)**：DNA 繞兩顆核小體蛋白球被保留下來的長度，cfDNA size 分布的次峰。
- **genome equivalents**：「一份完整基因組那麼多的 DNA」的計量單位；每毫升血漿大約只裝得下 1,500 份。
- **input DNA (100 pg–10 ng)**：cfDNA library prep 必須能處理的微量 input 範圍。
- **EDTA 採血管 (EDTA tube)**：含 EDTA 抗凝劑的標準採血管，藉由螯合鈣鎂離子抗凝並抑制核酸酶。
- **雙離心 (double centrifugation)**：兩輪離心：低速去細胞、高速去細胞碎片，是 cfDNA 萃取前的標準程序。
- **fragment end motif**：cfDNA 兩端最後幾個鹼基的序列偏好，反映體內核酸酶活性，對採血管與時間窗極度敏感。
- **jaggedness**：cfDNA 末端缺一兩個鹼基、雙股對不齊形成的小缺口；放越久越嚴重。
- **標準 SOP (ref 110)**：EDTA 採血管 + 4 小時內雙離心；本 review 強調這是跨 cohort fragmentomic 訊號可比較的前提。

## 與此篇文章的關係
在《Genomic and fragmentomic landscapes of cell-free DNA for early cancer detection》這篇 review 中，作者要把 cfDNA fragmentomic 分類器推到能在無症狀人群篩癌的臨床等級。為此他們把血漿 cfDNA 採集與前分析品管 (Pre-analytical handling) 立為所有下游分析的「地基 SOP」：解決了 fragment end motif、jaggedness、size 分布會被採血管與運送時間污染、進而讓 retrospective ML 分類器在前瞻 cohort 崩盤的瓶頸。它為 DELFI、Galleri、cfMeDIP-seq 等所有下游 assay 提供乾淨、可比較的 cfDNA input。

## 已沿用 Baseline 詞彙
cfDNA, ctDNA, 核小體, DELFI, AUC
