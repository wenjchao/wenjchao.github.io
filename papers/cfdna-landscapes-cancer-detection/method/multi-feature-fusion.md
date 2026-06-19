---
subitem_id: "3-H"
title: "多特徵融合分類器與 tissue-of-origin (CancerSEEK / SPOT-MAS / Shield / 多模態 ML)"
---

# 多特徵融合分類器與 tissue-of-origin (CancerSEEK / SPOT-MAS / Shield / 多模態 ML)

**Subitem:** 3-H · **Slug:** `multi-feature-fusion`

## 主線
把上述 mutation、CNV、fragmentation、methylation、end motif、甚至 protein biomarker 等異質特徵整併到單一 ML pipeline，提供更高的 sensitivity 與可信的 tissue-of-origin 預測，以服務真正的多癌篩檢與 high-risk surveillance 情境。

## 技術解析
多特徵融合分類器 (multi-feature fusion classifier) 要解決的問題是：早期癌的腫瘤 DNA 在血漿裡常常占比不到萬分之一，任何單一指標的異常都微弱到容易被雜訊吃掉。它的做法是把同一管血同時量出六種來源不同的數字——突變位點清單、染色體段落的增減 (CNV)、碎片長度與覆蓋度分布 (fragmentation profile)、每個 CpG 位點的甲基化比例、碎片末端 4 鹼基偏好 (end motif)，以及驗血常見的循環蛋白質濃度——攤平串成一條超長的特徵向量丟給機器學習。模型吐出兩個答案：一是『這人有沒有癌』的機率，二是『若有癌最可能來自哪個器官』的排名，後者就叫來源組織判讀 (tissue of origin)。為什麼非要這個器官指認？因為多癌篩檢若只說『你身上有癌』卻不指方向，醫師接下來只能讓你做全身掃描、各種內視鏡、隨機切片，這種痛苦過程叫『診斷大冒險』(diagnostic odyssey)，把它收斂到單一器官能省下大量時間與不必要的侵入性檢查。

本綜述列出的第一個代表平台是 CancerSEEK (Cohen 2018, ref 78)，走『驗血科 + 基因科』兩條線並行：基因端用 PCR 一口氣放大 61 個小片段 (61-amplicon PCR panel)，只盯著 16 個常見癌症驅動基因上最常出毛病的幾個鹼基；蛋白端則用免疫吸附法 (immunoassay) 同時量 8 種血液蛋白質指標 (8-protein immunoassay)，例如卵巢癌會升高的 CA-125、胰臟癌會升高的 CA19-9、大腸癌的 CEA。為什麼非要硬加蛋白質？因為它跟 cfDNA 是完全獨立的訊號軸——DNA 訊號取決於『癌細胞死了多少、把多少 DNA 倒進血裡』，蛋白質指標則來自『癌細胞還活著時分泌或剝落多少』，兩條來源不同、雜訊不會重疊；當早期癌 ctDNA 還少到撈不到突變時，蛋白質可能已經先漂上來。挑哪 8 種？作者從一大堆候選池中挑出對 8 種癌敏感度最好的子集，每一種癌都有至少一個蛋白指針會升高；這些蛋白也具器官偏好，順便給來源組織判讀 (tissue of origin) 一個方向感。模型用隨機森林 (random forest) 投票輸出『最像哪個器官』的排名，覆蓋 breast、colorectum、oesophagus、liver、lung、ovary、pancreas、stomach 共 8 種癌。

第二個代表平台是 SPOT-MAS (Nguyen 2023, ref 77)，把『一份建好的 NGS library 榨出四種訊號』玩到極致。它做兩件實驗：先用雜交捕獲 (hybrid-capture) 把 450 個事先選好的甲基化熱點區（約 18,000 個 CpG 位點）撈出來做亞硫酸鹽轉換定序 (bisulfite sequencing)，再做一輪覆蓋全基因組的淺層亞硫酸鹽定序 (WGBS)。神奇的是，這同一份定序資料同時餵出四種特徵：每個 CpG 位點的甲基化比例、每段染色體的 read 數變化 (CNV)、每條 read 的末端 4 鹼基組合分布 (end motif)，以及全基因組的碎片長短分布 (fragmentation profile)。四種訊號交給機器學習做兩件事：『有沒有癌』與『若有癌是 breast、colorectum、stomach、lung、liver 哪一種』。為什麼能擠進同一條 pipeline？因為它們本來就藏在同一份 paired-end reads 裡，只是用不同方式去『讀』同一筆原始資料而已。

第三個代表平台是 Shield (Guardant Health, ref 133)，主打大腸癌偵測，要處理的是『甲基化與突變如何在同一份 library 裡共存而不互相干擾』。它的招式是在建庫前先用分子條碼 (barcode) 把『帶甲基化的 cfDNA 片段』與『沒甲基化的片段』分別貼上不同標籤；之後對大約 100 萬鹼基 (~1 Mb) 的目標區域做雜交捕獲定序，每條 read 因此同時帶著三類資訊：APC、KRAS 這類大腸癌驅動基因的突變、CpG 甲基化狀態，以及片段被切斷的精確位置 (fragment end position)。三種訊號合起來餵給分類器，輸出單一個『是不是大腸癌』的機率。在 ECLIPSE 試驗（22,877 名受試者）中，整體期別敏感度 83%、特異度 90%、陰性結果可信度 (NPV) 99.9%；但 stage I 只抓到 65%、癌前病灶 (APL) 更只有 13%，所以早期偵測仍是這套組合最弱的環節。

三大平台都不是萬靈丹，最常踩到的兩個失敗模式必須同時看。第一是『指錯器官』：Galleri PATHFINDER 試驗 (NCT02421796, n=6,662) 偵測到的 35/121 癌症個案中，有 29 個 (83%) 第一順位 tissue-of-origin 猜對；反過來看仍有約六分之一會被先導向錯誤器官——醫師可能先安排了大腸鏡、胃鏡，等全做完才發現真正病灶在肺，這段繞路既花時間又多一次侵入性檢查，所以多癌篩檢通常仍需要『前兩到三順位都查』或結合其他分類器交叉比對。第二是『stage I 仍是普遍罩門』：早期腫瘤體積小、丟進血裡的 ctDNA 常常不到萬分之一，每毫升血漿總共只有約 1,500 份完整基因組，能撿到的腫瘤碎片本來就極少。多特徵融合提升的是『把同一份血裡的訊號榨乾』的效率，無法從根本上增加可用 DNA，背景雜訊（CHIP、germline、採檢前處理偏差）也是固定的。所以儘管特徵越疊越多，stage I 偵測率仍會撞天花板——Shield 在 ECLIPSE 對 stage I 只有 65%、Galleri 在真實世界 stage I 實體癌只有 8%。要真正突破得靠別的招：用藥物暫時增加 ctDNA 釋放、用多基因風險評分 (polygenic risk score) 先篩出高風險者、或改用長讀長定序 (long-read sequencing)。

Box 1 提到的三段式臨床驗證路徑也屬於這個 module 的核心紀律，因為多特徵融合模型最容易在這裡翻車。第一段『發現階段』(discovery) 通常拿手邊現成樣本 (convenience sample) 來訓練，但這些樣本的採血管、儲存時間、人群組成都跟真實的篩檢對象不一樣，模型很容易學到的不是癌症本身，而是『這些樣本剛好都是怎麼採的』。第二段『case-control 重訓』強制改用統一 SOP 重新採樣的病人對健康人對照組，把前一階段學到的虛假特徵洗掉。第三段『prospective intended-use cohort』才把模型放進真實場景——例如把肺癌分類器放在符合 LDCT 條件的高風險者身上，看陰性預測值 (NPV) 與陽性預測值 (PPV) 還撐不撐得住。三段都過了才能談分析驗證 (analytical validation) 與上市。如果跳過 prospective 重訓直接上線，模型大概率會在真實世界翻車——Galleri 的真實數據就是現成例子：case-control 中 stage I 還能抓到 18%，到了真實世界對 stage I 實體癌只剩 8%。

## 工具與材料清單 (Toolchain)
- **multi-feature fusion classifier**：把同一管血量出來的突變、CNV、碎片分布、甲基化、末端 motif、循環蛋白等多種異質特徵串成一條向量，交給機器學習同時輸出『有沒有癌』與『來源器官』。
- **CancerSEEK (ref 78)**：Cohen 2018 提出的早期多癌篩檢平台，結合 61-amplicon PCR 驅動基因突變與 8 種循環蛋白質 immunoassay，用 random forest 預測 8 種癌的 tissue of origin。
- **61-amplicon PCR panel**：CancerSEEK 用 PCR 一口氣放大 61 個小片段，覆蓋 16 個常見癌症驅動基因上最常出毛病的 hotspot 鹼基。
- **8-protein immunoassay**：CancerSEEK 用免疫吸附法平行量 8 種血液蛋白濃度（含 CA-125、CA19-9、CEA 等），補上 DNA 之外的獨立訊號軸，也提供器官偏好。
- **SPOT-MAS (ref 77)**：Nguyen 2023 的四模態大腸癌等多癌平台，把同一份 bisulfite library 同時擠出 methylation、CNV、end motif、fragmentation 四種特徵。
- **hybrid-capture bisulfite sequencing**：用核酸探針把目標區域 cfDNA 撈出來、做亞硫酸鹽轉換後定序的甲基化平台；SPOT-MAS 用 450 個區域 / 18,000 個 CpG 位點。
- **Shield (ref 133)**：Guardant Health 的大腸癌專屬血液檢測，建庫前先以分子條碼分開甲基化與未甲基化片段，再對 ~1 Mb 目標區做 hybrid-capture，同時量 APC/KRAS 突變、甲基化、片段末端位置。
- **ECLIPSE trial**：Shield 的前瞻臨床驗證試驗 (NCT04136002, n=22,877)，整體期別敏感度 83%、特異度 90%、NPV 99.9%、stage I 65%、APL 13%。
- **Galleri PATHFINDER (ref 79)**：GRAIL 的 multi-cancer 甲基化檢測前瞻試驗 (NCT02421796, n=6,662)，偵測到的 35/121 癌症個案中有 83% tissue-of-origin 第一順位猜對。
- **tissue of origin (ToO)**：分類器在判定『有癌』之後，再給出『最可能來自哪個器官』的排名，用來縮短後續診斷大冒險。
- **diagnostic odyssey**：陽性結果但不知道癌症在哪個器官時，被迫做全身掃描、多種內視鏡、隨機切片的繞遠路過程；tissue of origin 預測就是為了把它縮短。
- **NPV (negative predictive value)**：陰性預測值，測陰性者真的沒病的比例；篩檢場景最關鍵的指標，Shield 在 ECLIPSE 達 99.9%。
- **三段式臨床驗證路徑 (Box 1)**：discovery convenience sample → case-control with uniform SOP → prospective intended-use cohort → analytical validation，逼模型逐段擺脫採檢前處理 artifact 才能上市。
- **convenience sample overfit**：用手邊現成樣本訓練時，case 與 control 的採檢條件不同，模型容易把 pre-analytical artifact 學成癌症訊號，到 prospective 場景就崩盤——Galleri stage I 從 case-control 18% 掉到真實世界 8%。

## 與此篇文章的關係
在《Genomic and fragmentomic landscapes of cell-free DNA for early cancer detection》這篇 Review 中，作者要回答的大問題是：cfDNA 早期篩檢能不能從『單一特徵、單一癌種』走向真正可用的多癌篩檢。為此 Review 盤點了 CancerSEEK、SPOT-MAS、Shield、Galleri PATHFINDER 等多特徵融合分類器，把前面章節討論的 mutation、CNV、fragmentation、methylation、end motif 與循環蛋白質彙整到同一個機器學習模型，吃進同一管抽血的多種特徵、產出『是否有癌』與『tissue of origin』兩個臨床端可直接行動的輸出。這個 module 是整篇 Review 的收斂段：說明 ML 整合是目前最務實的早癌篩檢主路線，同時點出 stage I 偵測與 tissue-of-origin 預測仍是共同罩門。

## 已沿用 Baseline 詞彙
cfDNA, ctDNA, WGBS, CpG, CNV, stage I, PCR, NGS, LDCT, fragmentation profile, 甲基化, 亞硫酸鹽, CHIP, Galleri, Shield
