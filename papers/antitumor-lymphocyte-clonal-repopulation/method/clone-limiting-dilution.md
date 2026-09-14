# 極限稀釋單株化與細胞激素分泌抗原特異性測試

1. 引用自哪篇 paper: antitumor-lymphocyte-clonal-repopulation
2. Outline (任務主線): 極限稀釋單株化與細胞激素分泌抗原特異性測試
3. Method:
      作者要在單株層級直接證明「活體重建的優勢 clone 認的靶是 MART-1」。第一步是「極限稀釋 (limiting dilution)」——把輸注前 TIL 一路稀釋到每孔平均分不到 1 顆細胞（實務上 ~0.3 顆），依 Poisson 分布多數孔是 0 顆、極少數孔剛好 1 顆；把這些孔各自培養長出來，就是同一顆母細胞的後代——一個 clone。作者由此拿到 M1C3（來自病人 9 輸注前 TIL 的 Vβ12+ 純 clone）與 S1A5（來自病人 10 輸注前 TIL 的 Vβ7+ 純 clone）。第二步鎖定表位：MART-1 蛋白第 27 到 35 位（AAGIGILTV）這 9 個 amino acid 的短片段，能被 HLA-A2 展示窗掛出來——這「短片段 + 展示窗」的組合就是「表位 (epitope) MART-1: 27-35」。
   接著作者對兩個 clone 跑「細胞激素分泌測試」(cytokine secretion assay, refs 11 & 14)。T 細胞被辨識天線抓到熟悉表位後會分泌一組發炎性訊號分子，作者測三種：干擾素-γ (IFN-γ) 是殺手 T 細胞活化的經典指標、也會逼腫瘤把 MHC 展示窗掛出來；顆粒球-巨噬細胞集落刺激因子 (GM-CSF) 會招募並活化免疫吞噬細胞；腫瘤壞死因子 α (TNF-α) 會直接誘導腫瘤細胞死亡。作者拿 MART-1: 27-35 peptide 與 HLA-A2+ 526 / HLA-A2⁻ 938 兩個黑色素瘤細胞株去刺激。526 是 HLA-A2+，能把 MART-1 表位掛到展示窗上；938 是 HLA-A2⁻，就算細胞內有 MART-1 也沒有匹配的展示窗。如果活性只落在 526 身上，就證明是嚴格「HLA-A2 + MART-1」的組合在做事——排除跟 HLA-A2 無關的一般毒殺，也排除跟 MART-1 無關的其他抗原反應。
   為什麼把 M1C3 / S1A5 抓出來、確認它們認 MART-1: 27-35，就能推論這是活體重建的優勢 clone？作者的推論鏈需要三個確認：一是活體優勢 clone 屬於 Vβ12（病人 9）或 Vβ7（病人 10）家族——靠 Vβ 抗體 FACS 確認；二是輸注前 TIL 裡有同家族 clone——靠 CDR3 定序（見 2-D、3-B）確認；三是那個 clone 認的靶是 MART-1: 27-35——就是這個 clone assay 補上的。三個確認到位，才能宣稱「輸注前 TIL 裡的這支 clone 就是活體重建的優勢 clone」。單株 cytokine 分泌只證明「認得抗原且能分泌訊號」，但殺癌能力還沒直接測，所以作者再做一次「專一性溶胞測試」(specific lysis assay, Fig 2A)：對 526 / 938 分別測輸注前 TIL、輸注後 PBL、pretreatment PBL 三個時點——治療前 PBL 對 526 幾乎沒有溶胞活性，治療後 PBL 有、輸注前 TIL 也有，證明這個殺傷力是新引入的、不是原本背景。
   這一步的兩個關鍵失敗模式要注意。第一，如果 M1C3 / S1A5 對 MART-1: 27-35 完全沒反應，就代表活體優勢 clone 認的可能是別的抗原（例如其他分化抗原），MART-1 就不是主導反應的靶——「用 self-antigen MART-1 做免疫療法可行」的核心結論會被抽掉底盤。第二，如果極限稀釋濃度沒控好、每孔平均分到 2–3 顆細胞，長出來的其實是多 clone 混合而不是純 clone；這時 cytokine assay 看到的 MART-1 反應可能是雜牌 clone 裡剛好一支認 MART-1 貢獻的，CDR3 定序也會看到多條序列。作者把濃度控到每孔平均 0.3 顆才安心宣稱「一井 = 一 clone」。
4. 工具與材料:
   - **Limiting dilution**: 把 TIL 稀釋到每孔平均分不到 1 顆的方法，依 Poisson 分布保證極少數孔剛好長出單一 clone。
   - **M1C3 / S1A5**: 從病人 9 (Vβ12+) 與病人 10 (Vβ7+) 輸注前 TIL 分離出的兩個單株 T cell clone，作者用來確認 MART-1 專一性。
   - **MART-1: 27-35 epitope (AAGIGILTV)**: MART-1 蛋白第 27–35 位的 9-mer 短片段，可由 HLA-A2 展示窗呈遞給 T 細胞辨識。
   - **Cytokine secretion assay**: 量測 T 細胞遇到抗原後分泌的 IFN-γ、GM-CSF、TNF-α 等訊號分子，做為 clone 抗原特異性與活化的功能讀數（refs 11 & 14）。
   - **HLA-A2+ 526 vs HLA-A2⁻ 938**: 配對黑色素瘤細胞株對照組——確認毒殺是嚴格「HLA-A2 + MART-1」限制的，而非非特異毒殺。
   - **Specific lysis assay**: 體外殺傷測試（Fig 2A），對輸注前 TIL / 輸注後 PBL / pretreatment PBL 分別測，直接看 clone 是否能溶解 HLA-A2+ 腫瘤細胞。
5. 與此篇文章的關係:
   在《Cancer Regression and Autoimmunity in Patients After Clonal Repopulation with Antitumor Lymphocytes》這篇文章中，作者為了替「輸注前 TIL 裡的某支 clone 就是活體重建的優勢 clone」這個因果鏈補上抗原特異性這一環，採用了「極限稀釋單株化 + 細胞激素分泌測試」。它解決了「Vβ 家族偏斜可能來自非特異擴增」的疑慮，吃進病人 9 與病人 10 輸注前 TIL，產出兩個純 clone (M1C3、S1A5)，直接證明它們認的抗原就是 MART-1: 27-35，把 clonal repopulation 論述的最後一塊拼圖鎖死。
