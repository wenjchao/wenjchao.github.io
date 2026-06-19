---
subitem_id: "2-E"
title: "TARGET-seq+ 板式單細胞基因型 + 轉錄"
---

# TARGET-seq+ 板式單細胞基因型 + 轉錄

**Subitem:** 2-E · **Slug:** `target-seq-plus-genotyping`

## 主線
對 MARCH 隊列之骨髓 (含 DNMT3A/TET2 CH 與非 CH 對照) 同時取得「單細胞轉錄體 + 細胞表面 FACS index + DNMT3A/TET2 變異 genotyping」，將 CH-WT 與 CH-mutant 細胞在同一張 UMAP 上分辨並對應到 HSC1/HSC-I 與 HSC2/HSC-iM。

## 技術解析
MARCH 隊列從接受髖關節置換手術的中老年患者取得骨髓——這群病人本來就要切開髖骨，順手抽一管骨髓不額外造成痛苦，剛好涵蓋 CH 高發年齡層（60 歲以上），並包含帶 DNMT3A/TET2 突變與不帶突變的對照。樣本先用 CD34 MicroBead Kit 富集，再用 BD Fusion 預分選成 HSPC 與髓系兩群。接著上 Sony MA900：每塊 384-well 板每孔預先裝好 3 μl 的「破細胞 + 啟動逆轉錄」溶解液（含界面活性劑、RNase 抑制劑、逆轉錄引子），分選機把細胞用帶電液滴精準甩進指定孔同時開啟 index sort 模式——這顆細胞所有 FACS 螢光通道的強度與孔位編號被一起記下來，事後就能查每孔細胞當時的 CD34/CD38/CD90/CD45RA 表型。細胞一進孔就溶解，mRNA 與基因組 DNA 同時漂在 3 μl 溶解液裡；同孔接下來做兩件事——RNA 端用 oligo-dT 引子抓 mRNA polyA 尾巴做類 SMART-seq2 全轉錄體擴增；DNA 端用幾條專門針對 DNMT3A 與 TET2 突變熱點的引子做 multiplex PCR 鎖定那段 DNA。最後兩種 amplicon 一起送定序，讀回來就同時知道這顆細胞表現哪些基因，與它的 DNMT3A/TET2 是 WT 還是突變。Protocol 改自 Jakobsen et al. 2024 (Cell Stem Cell)。

為什麼 RNA 與 DNA 兩種文庫能在同一孔做、不互相干擾？兩端的 primer 互不重疊：oligo-dT 只抓 mRNA polyA 尾巴（gDNA 沒有 polyA），DNA 端引子只結合 DNMT3A/TET2 突變位點、不動 cDNA，等於同一鍋湯裡兩個漁夫各釣各的魚。為什麼用板式（384-well）而不是 10X droplet？因為 droplet 每細胞只分到奈升等級體積，無法同時做全轉錄體擴增與 multiplex targeted PCR；板式 384-well 有 μL 等級反應體積，可以一邊 SMART-seq2 一邊 targeted PCR，並天然支援 index sort 把 FACS 資料逐孔對應；代價是細胞數有限（本研究 8,998 顆通過 QC）。最後每次分選都納入一份固定來源的 NOC153 骨髓作為技術對照——板式每次 sort run 之間試劑批次、機台校正、PCR 條件總有些微差異會在 UMAP 上產生 batch effect，用 NOC153 在不同 run 之間的位置差異反推 batch 大小並校正，就像每次校準秤都用同一塊標準砝碼。

如果只做 scRNA-seq 不做 targeted genotyping，作者只能說「這位 CH 患者整體骨髓表現量長這樣」，無法在單細胞層次分辨「這顆帶 DNMT3A 突變」還是「這顆是同人骨髓的 WT」。CH 的關鍵生物學就在於同一個人骨髓裡 WT 與 mutant 細胞共存且互動——沒有 single-cell genotyping 就無法做本論文最關鍵的「CH-WT vs control」與「CH-mut vs CH-WT」兩條軸線，也就無法宣稱「DNMT3A/TET2 突變幾乎只在 HSC-iM 子集引發顯著基因改變」這個核心結論。同樣地，如果分選時沒開 index sort，每顆細胞的 FACS 表型就永遠消失，當 reviewer 問「HSC-iM 真的長在 LT-HSC 區還是被誤分群的 progenitor？」作者沒有 cross-modal metadata 就答不上來。

## 工具與材料清單 (Toolchain)
- **TARGET-seq+ (Jakobsen et al. 2024)**：板式單細胞同孔同時讀全轉錄體 (mRNA) 與 targeted DNA 突變的方法。
- **MARCH 隊列 (REC 17/YH/0382)**：從髖關節置換手術中老年患者取得 BM，覆蓋 CH 高發年齡層與 DNMT3A/TET2 突變 vs 對照。
- **Sony MA900 板式分選機**：把每顆細胞用帶電液滴精準甩進 384-well 指定孔，支援 index sort 模式。
- **FACS index sort**：分選時同步把每顆細胞各螢光通道強度與孔位記下來，提供 cross-modal 對應 metadata。
- **oligo-dT primer + 類 SMART-seq2**：RNA 端走 polyA 尾巴抓全轉錄體擴增，讀深度高。
- **Multiplex targeted PCR (DNMT3A/TET2 hotspot)**：DNA 端用專門針對突變熱點的引子鎖定 amplicon，可在單細胞解析度判 WT/mut。
- **384-well 板與 3 μl 溶解液**：μL 級反應體積讓同孔可同時做全轉錄體擴增與 targeted PCR；droplet 體積不夠。
- **NOC153 內部對照**：每次 sort run 都納入同一份骨髓，事後校正跨 run batch effect。
- **CD34 MicroBead Kit + BD Fusion 預分選**：把骨髓 HSPC (hCD45⁺CD34⁺CD19⁻CD33⁻) 與髓系 (CD33⁺CD34⁻) 先粗分。
