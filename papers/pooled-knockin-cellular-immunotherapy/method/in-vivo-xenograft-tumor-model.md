# In Vivo 實體腫瘤異種移植模型

1. 引用自哪篇 paper: pooled-knockin-cellular-immunotherapy
2. Outline (任務主線): In Vivo 實體腫瘤異種移植模型
3. Method: 
   為了在活體中驗證 pooled screen 的命中，作者把實驗搬進免疫不全小鼠 (NSG mouse, NOD/SCID/IL-2Rγ-null)——這種小鼠的 T、B、NK 三類免疫細胞都被基因剔除，等於「沒有自家警衛的實驗田」，人類腫瘤與人類 T 細胞都能在裡面活下來。小鼠右側腹皮下注射人類黑色素瘤細胞株 A375 長出實體腫瘤後，再從眼球後方靜脈叢注射 (retro-orbital injection) 把人類 T 細胞送進全身血流，T 細胞會自行循環到腫瘤位置。整個動物實驗分兩種模式：pooled 篩選把 36 種 knockin 構築的細胞混在一起輸入，看哪些構築讓 T 細胞鑽進腫瘤；個別構築驗證則只輸一種構築的細胞，看能不能真的把腫瘤縮小。
   兩種模式的腫瘤與細胞劑量差異反映各自的目的。Pooled 篩選注射 1×10^6 A375 並輸入 10×10^6 未純化的整批 T 細胞——其中只有約 10% 真的成功 knockin，平均下來每個構築佔約 0.3%，總量必須夠大才能讓每個構築都有足夠的細胞代表。個別構築驗證則先用 FACS 挑出 NY-ESO-1+（真的帶上構築）的 T 細胞 1.5×10^6 顆輸入，並把腫瘤起始量減半到 0.5×10^6 A375——因為這次目的不是收 TIL 而是看療效，腫瘤太大就算最強的構築也壓不住。腫瘤體積以游標卡尺量長、寬兩個方向直徑，套用橢球近似公式 $v = \frac{1}{6}\pi \cdot \text{length} \cdot \text{width} \cdot \frac{\text{length} + \text{width}}{2}$ 換算成每日腫瘤生長曲線。
   Pooled 篩選的另一個關鍵讀數是「進入腫瘤的 T 細胞 (TIL) 帶了哪些 barcode」。作者在注射後第 5 天取腫瘤——這個時間點是腫瘤已長到 TIL 願意進駐、選擇壓力又還沒把弱構築全部刷掉的取樣甜蜜點；太早收細胞還沒進腫瘤、太晚收只剩最後贏家。腫瘤被剪碎後過 70 μm 孔徑的尼龍濾網把單顆細胞篩出來，再放上 FACS 機，用兩種螢光抗體點名：CD45 是所有免疫細胞共通的表面標記，把人類 T 細胞跟 A375 腫瘤細胞分開；TCR 是 T 細胞才有的表面受體，把 T 細胞跟其他免疫細胞分開。雙陽性 (CD45+ TCR+) 細胞每隻小鼠約 10–20k 顆，就是真正鑽進腫瘤的 TIL，DNA 才拿去做 barcode 擴增。若跳過這道分選直接拿打散物去定序，barcode 訊號會被大量無關細胞稀釋到讀不出哪個構築勝出。
4. 工具與材料: 
   - **NSG mouse**: T、B、NK 三類免疫細胞被基因剔除的免疫不全小鼠 (NOD/SCID/IL-2Rγ-null)，人類腫瘤與人類 T 細胞都能在內穩定存活。
   - **A375**: 穩定表達 NY-ESO-1 的人類黑色素瘤細胞株，皮下注射建立實體腫瘤模型。
   - **Subcutaneous injection**: 皮下注射，把 A375 腫瘤細胞注入小鼠右側腹皮下層長出可量測的實體腫瘤。
   - **Retro-orbital injection**: 眼球後方靜脈叢注射，將 T 細胞送進全身血流的標準靜脈路徑；對 NSG 小鼠比尾靜脈穩定。
   - **TIL**: 腫瘤浸潤淋巴球 (tumor-infiltrating lymphocyte)，真正鑽進腫瘤組織內部的 T 細胞，是 pooled screen 的核心讀數來源。
   - **70 μm filter**: 70 μm 孔徑尼龍濾網，把剪碎後的腫瘤組織濾出單顆細胞、丟掉大塊組織碎片。
   - **CD45**: 所有人類免疫細胞共通的表面標記，FACS 用來把 T 細胞跟 A375 腫瘤細胞區分開。
   - **TCR surface marker**: T 細胞才有的表面受體，FACS 用來把 T 細胞與其他免疫細胞區分開。
   - **Tumor volume formula**: 把皮下腫瘤近似為扁橢球的體積公式 $v = \frac{1}{6}\pi \cdot \text{length} \cdot \text{width} \cdot \frac{\text{length} + \text{width}}{2}$，只需游標卡尺量長與寬兩個方向直徑。
5. 與此篇文章的關係: 
   在《Pooled Knockin Targeting for Genome Engineering of Cellular Immunotherapies》這篇文章中，作者為了找出能讓 T 細胞清除實體腫瘤的最佳外掛構築，採用了 NSG xenograft 模型。它解決了體外殺癌實驗無法重現腫瘤微環境壓力的瓶頸：上游接收電穿孔完成的 36 種 pooled knockin T 細胞與單獨純化的個別構築 T 細胞，下游同時產出 TIL barcode 豐度（給 PoKI-Seq 拆解細胞狀態）與腫瘤體積曲線，最終提名出 TGF-βR2-41BB 為唯一能完全清除腫瘤的構築。
