# AlphaFold2 結構預測作為設計 in silico filter

1. 引用自哪篇 paper: de-novo-design-of-luciferases
2. Outline (任務主線): AlphaFold2 結構預測作為設計 in silico filter
3. Method: 
   AF2 是一個只看蛋白序列就能預測 3D 結構的深度學習模型，跟前面的 RosettaDesign / MPNN 完全獨立——沒看過設計圖、不知道作者本來想折成什麼樣。RosettaDesign 跟 ProteinMPNN 都是「給我一個目標結構、我幫你找序列」，設計時心裡有預設答案；AF2 是「給我一條序列、我告訴你它會折成什麼」，訓練資料、架構、目標函數都跟設計工具不同。所以 AF2 的預測結果如果跟設計模型吻合，等於「兩個獨立的判斷者都同意這條序列會折成這個形狀」，比單看 RosettaDesign 自己評分可靠得多——就像考試讓兩個彼此不通氣的老師判同一份卷子，兩個都打高分才算過。具體怎麼比？作者把設計出的序列丟給 AF2 各自預測一個結構，然後跟原本的設計模型疊在一起，量主鏈每個 Cα 原子的距離差 (Cα RMSD)。1 Å (Ångström) = 0.1 奈米，跟一個原子直徑差不多；LuxSit 的 1.35 Å 代表每個 Cα 平均偏離 1.35 Å，遠小於一個胺基酸鍵長 (~3.8 Å)，整個主鏈骨架幾乎重合——結構生物學上 RMSD < 2 Å 算「同 fold」、< 1.5 Å 算「幾乎一樣」。同時讀 pLDDT (predicted local-distance difference test)：0–100 分，每個位置一個分數，代表 AF2 對該位置預測的把握；> 90 通常很可信。第二輪 h-CTZ 把門檻訂在 pLDDT > 92。為什麼兩個 metric 都要看？因為 pLDDT 高只代表 AF2「對自己有信心」，不代表它預測的形狀跟設計者想要的一樣——AF2 可能高度自信地說這條序列會折成另一個 fold、活性中心全錯；所以必須同時要求 RMSD 小，確認 AF2 確定的形狀就是設計要的形狀。再來，AF2 只能告訴你蛋白會折成什麼樣，不能直接告訴你「DTZ 會不會被抓住」。所以作者再加兩個輔助 filter：contact molecular surface 量化「DTZ 與蛋白口袋的接觸面積」（面積愈大代表 DTZ 被包得愈緊），Rosetta-computed binding energy 量化「DTZ 跟蛋白互動的能量穩定程度」（能量愈低代表結合愈穩）。AF2 + 這兩個物理 filter 加起來，等於同時審「蛋白會不會折對」「DTZ 會不會被抓住」「催化幾何穩不穩」三件事。最後值得提一個時間軸：AlphaFold2 是 2021 年才發表的工具，第一輪 DTZ 設計時 AF2 剛出來還沒被廣泛整合到 design pipeline，作者只能靠 Rosetta 能量分數當主要 filter，所以訂了 7,648 條 oligo 大撒網——但 Rosetta 分數只說「在預設骨架下這條序列能量低」、無法判斷真實 foldability，最後只撈到 3 個有活性 (0.04%)。第二輪 h-CTZ 設計時 AF2 已成熟，作者把它加進來當主要 filter，只訂 46 條仍撈到 2 個有活性 (4.3%)。AF2 filter 把 wet-lab 成功率從 0.04% 拉到 4.3%，幾乎 100 倍提升——前一個 wet-lab 大撒網的成本被 AF2 這個計算工具吸收掉了。
4. 工具與材料: 
   - **AlphaFold2 (AF2)**: 只看序列就能預測 3D 結構的深度學習模型 (Jumper 2021)，與 RosettaDesign / MPNN 演算法獨立、可當外部評審。
   - **pLDDT**: AF2 對自己預測有多自信的局部分數 (0–100)；本研究第二輪要求 > 92。
   - **Cα RMSD**: AF2 預測結構與設計模型主鏈每個 Cα 原子的平均距離差；LuxSit 為 1.35 Å，表示骨架幾乎重合。
   - **Contact molecular surface**: DTZ 與蛋白口袋接觸面積的量化指標；面積愈大代表 DTZ 被包得愈緊。
   - **Rosetta-computed binding energy**: Rosetta 算出的 DTZ 與蛋白互動能量；能量愈低代表結合愈穩。
   - **In silico filter**: 在訂 oligo 前純靠計算淘汰差的設計、把實驗成本壓低的步驟；本研究將 wet-lab 成功率從 0.04% 拉到 4.3%。
5. 與此篇文章的關係: 
   在《De novo design of luciferases using deep learning》這篇文章中，作者為了避免直接把 50,000 個 RosettaDesign / MPNN 輸出全部訂成 oligo，採用了 AlphaFold2 的 pLDDT 與 Cα RMSD 雙條件作為主要 in silico filter。這個方法解決了「Rosetta 物理能量無法保證真實 foldability」的瓶頸，讓設計模型由獨立深度學習模型再審一次，把第二輪 h-CTZ 設計從 50,000 候選壓到 46 條訂單，產出 wet-lab 成功率 4.3% 的精選池，直接交給下游 oligo pool 合成與 colony 篩選。
