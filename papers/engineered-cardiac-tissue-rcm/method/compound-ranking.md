# 化合物排序與庫策略

1. 引用自哪篇 paper: engineered-cardiac-tissue-rcm
2. Outline (任務主線): 化合物排序與庫策略
3. Method: 

整套排序像一個三道閘門。第一道閘門是「化合物庫怎麼挑」：作者刻意把三個已上人類使用紀錄的庫疊起來——FDA-approved Drug Library (Enzo Life Sciences)、Pharmakon (MicroSource Discovery Systems)、Tested-In-Humans Collection (Yale Center for Molecular Discovery)，總計 2,185 個分子。第二道閘門是「跨時間點共識」：把鈣 τ 模組吐出的 τ 加藥前後倍數變化 (fold change) 分別在 t = 1 h、t = 3 h 各排一次序，各取前 100 名，再取兩個前 100 名的交集當驗證清單。第三道閘門是「正交驗證」：把交集出來的 hit 先拿到 patient iPSC-CM (確認不只在 GCAMP6 背景才有效)，再回到 3D ECT 量真正的 active force / passive tension。三道閘門都通過才算 hit，最後勝出的是 trequinsin。

為什麼挑「兩個時間點各取 top-100 再取交集」而不是「z-score threshold > 3」或「聯集」？交集排序的精神是「同一個分子在兩個獨立讀數上都名列前茅，才有資格留下」。z-score 絕對門檻會被整盤分布形狀影響——換批細胞、分布變一點，hit 名單就抖動。聯集 (1 h 或 3 h 任一進前 100) 會把「曇花一現的化學擾動」也納入、偽陽性飆高。交集則要求一個分子要兩次都被擲中——若兩次完全隨機，從 2185 個分子各擲 100 個交集只能命中 100 × (100/2185) ≈ 4 個，所以實際交集超過 4 個就有顯著富集；且這個 filter 不依賴任何分布假設、不需要設絕對閾值，特別適合 single-pass 篩選。

為什麼挑「已上人體」三個庫疊起來？這是 drug repurposing 策略——挑至少進過人體的分子，找到 hit 後可以直接接上既有的人體安全、藥代與劑量資料，不需要從零跑毒理。三個庫各有定位：FDA-approved 多是已上市藥、Pharmakon 是經典生物活性庫、Tested-In-Humans 是進過臨床但未必上市的化合物；三者覆蓋的靶點與化學骨架不同，疊起來才能讓「PDE3 抑制劑」這類其實已有人試過的分子有機會被掃到。對小團隊預算而言，2,185 個分子也剛好是 384 孔板可承受的尺寸 (約 6 片板)，踩在「足夠多樣 + 不爆預算」的甜蜜點。

如果作者把交集 hit 直接報告為 RCM 救援藥物、跳過 patient iPSC-CM 與 3D ECT 驗證，會在兩層出問題。第一層是基因背景單一：篩選只跑在 GCAMP6^ΔGAA^ 這一條細胞線上 (WTC11 加上鈣指示器並敲入突變)，整套表型可能受 WTC11 背景或 GCAMP6 表現量影響。若沒拉到第二條獨立的 patient iPSC-CM (本研究來自三歲男童的 FLNC^ΔGAA^ 線) 確認效應仍在，就無法區分「真的救援 RCM」與「對這條 reporter 線特殊有效」。第二層是讀值單一：2D τ 縮短只代表鈣回收變快，但 RCM 臨床核心是 passive tension 升高——鈣動力學改善不保證真的把肌肉繃緊放鬆。跳過 3D ECT 可能把「鈣訊號好看但 passive tension 沒救」的化合物誤報為療效藥物，重蹈傳統 PDE3 抑制劑「2D 看似有效、臨床卻惡化」的覆轍。

4. 工具與材料: 
- **FDA-approved Drug Library (Enzo Life Sciences)**: 已上市藥物的化合物庫，全部具備人體安全與藥代資料，適合 drug repurposing。
- **Pharmakon (MicroSource Discovery Systems)**: 經典生物活性庫，覆蓋多種靶點與化學骨架，與 FDA 庫互補。
- **Tested-In-Humans Collection (Yale Center for Molecular Discovery)**: 進過臨床但未必上市的化合物庫，補足前兩個庫的化學空間。
- **τ fold change 排序**: 以「τ 加藥後 / τ 加藥前」的倍數對化合物排序，是篩選的主要排名依據。
- **Top-100 交集 (intersection ranking)**: 1 h 與 3 h 各取 τ 變化前 100 名，取兩個前 100 名的交集當驗證清單，要求同一分子在兩個時間點都名列前茅。
- **正交驗證 (orthogonal validation)**: 把 2D τ 篩出的 hit 拉到第二條獨立細胞線 (patient iPSC-CM) 及 3D ECT 量真正力學，確認效應跨基因背景、跨讀值都成立。

5. 與此篇文章的關係: 
在《Engineered cardiac tissue model of restrictive cardiomyopathy for drug discovery》這篇文章中，作者要從 2,185 個化合物找出能救援 FLNC^ΔGAA^ RCM 舒張缺陷、且能直接走 drug repurposing 的小分子。為此他們設計化合物排序與庫策略，把鈣 τ 模組吐出的 fold change 分別在 1 h 與 3 h 各排前 100 名再取交集，最後將交集 hit 拉到 patient iPSC-CM 與 3D ECT 做正交驗證，用「跨時間點共識 + 跨平台驗證」兩道過濾把 trequinsin 挑出來，再交給下游急性處置模組做療效與安全測試。
