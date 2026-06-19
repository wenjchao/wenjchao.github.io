---
subitem_id: "3-H"
title: "TARGET-seq+ 的 dream 線性混合模型差異表現"
---

# TARGET-seq+ 的 dream 線性混合模型差異表現

**Subitem:** 3-H · **Slug:** `target-seq-plus-dream-lmm`

## 主線
對含 DNMT3A / TET2 CH 突變與非 CH 對照之骨髓 TARGET-seq+ 資料，用 limma-voom 為基礎的 dream linear mixed model 同時校正 donor、age、sex、FACS 板批次，並把 cell type、CH status 與 clone genotype 作為固定效應做差異表現。

## 技術解析
作者手上有來自 MARCH 隊列的骨髓 TARGET-seq+ 資料——這是一種板式 (plate-based) 單細胞流程：每顆細胞先用 FACS 單獨分進 384 孔板的一個孔，孔裡同時做三件事，全細胞 mRNA、針對 DNMT3A 與 TET2 等位置的目標 amplicon、以及 FACS 分選時記錄的細胞表面標記 (index sort)。三條資訊串起來就能同時知道「這顆細胞長什麼基因表達、表面長什麼樣、自己 DNA 有沒有那個 CH 突變」。要對這份資料做差異表現，作者打算回答四個彼此獨立的問題：CH vs non-CH、HSC1 vs HSC2 (對應 HSC-I / HSC-iM)、同一位 CH 病人內 CH-WT vs CH-mut，以及 HSC1-dominant vs HSC2-dominant 階層。

問題是直接拿 DESeq2 或 Wilcoxon 不夠用。TARGET-seq+ 的細胞不獨立：一位 CH 病人可能貢獻 300 顆細胞，這 300 顆共享同一個 donor、同一張 sort 板，若當 300 個獨立樣本送進 Wilcoxon，sample size 會被灌成 300、p 值被推到極小——這就是 pseudoreplication (偽重複)，會大量產出偽陽性差異基因。作者改用線性混合模型 (linear mixed model, LMM) 解這道題。具體做法是把因子拆成兩類：固定效應 (fixed effect) 是研究問題本身想正式比較的，例如 cell type、CH status、clone genotype；隨機效應 (random effect) 是「會造成額外變異但我不想逐一比較」的因子，例如 donor、FACS 板批次。模型先承認同一位 donor 內、同一張板內的細胞共享基線，再算固定效應是否真把基線推開。

但 RNA-seq 也不能直接丟原始 read count 進 LMM，因為 counts 是整數又有「平均越低、變異越大」的特性。RNA-seq 領域既有的 limma-voom 流程的做法是兩步：先把 counts 轉成對每百萬讀數中該基因比例取對數的 log-CPM，再觀察「每個基因平均 log-CPM vs 變異」這條關係曲線，按曲線給每個觀察值一個精準度權重——表達低變異大的點權重給低、表達高變異穩的點權重給高，limma 再用這些加權值跑線性模型。傳統 limma 不支援 random effect，dream (variancePartition 套件 v1.22.0 / v1.33.0) 正是把 voom 這套加權流程嫁接到 LMM 上的擴充。本研究 normalize 採 scran 算 size factors (依單細胞鄰居資訊算，比 DESeq2 中位比更耐零值稀疏的單細胞資料) 轉 log-norm，再丟 dream，最後用 `eBayes` 做基因層級檢定。

對應四個問題，作者用四種配方。CH vs non-CH 是跨人比較，sample type 為固定效應，sample、age、sex、FACS-sorting plate 都當共變項或隨機效應扣掉。HSC1 vs HSC2 在同一位 donor 內就看得到，donor 反而是天然配對對照不必當共變項，cell type 為固定效應，只校正 sex。同一位 CH 病人內 CH-WT vs CH-mut 比較，clone 為固定效應、sample 與 plate 當混合效應扣掉，donor 之間的差異天生被抵銷。HSC1-dominant vs HSC2-dominant 階層比較則以階層為固定效應、sample、sex、plate 當隨機效應扣。原則一致：「比較對象決定哪些因子需要扣」。

為什麼一定要把 FACS-sorting plate 當批次扣掉？因為 TARGET-seq+ 是板式流程，每張 384 孔板需要獨立做 lysis、反轉錄、放大、加 barcode，板與板之間反轉錄效率、引子批次、定序覆蓋深度都會有系統性差異。如果「偏高板」剛好都裝 CH 樣本、「偏低板」剛好都裝 non-CH 樣本，板批次效應會被誤認成 CH 訊號。作者在每個比較裡都明確把 FACS-sorting plate 寫進共變項或隨機效應；此外每次 sort 都納入同一份 NOC153 骨髓樣本當技術對照，提供跨板校正的基準線。

作者把同一套 dream 框架延伸到轉錄因子調控組 (regulon) 的活性差異。先用 pySCENIC (v0.12.0) 配 `motifs-v10nr_clust-nr.hgnc-m0.001-o0.0.tbl` motif 表，把每個轉錄因子周邊真的帶有對應 motif 的目標基因留下、剪掉假目標；再用 AUCell 給每顆細胞每個 regulon 打一個 0-1 之間的活性分數。把這個分數當「假基因」丟回同一套 dream LMM 與固定 / 隨機效應結構，用 likelihood ratio test (比較含固定效應的完整模型 vs 不含固定效應的縮減模型) 算 p 值，就能回答「哪些轉錄因子整組目標在某個比較裡被整體推上推下」。

## 工具與材料清單 (Toolchain)
- **TARGET-seq+**：板式 (plate-based) 單細胞流程，每孔同時做全細胞 mRNA、DNMT3A / TET2 等目標 amplicon、FACS index sort 三條資訊，讓基因表達 + 突變狀態 + 表面標記能在同一顆細胞上對齊。
- **linear mixed model (LMM)**：同時容納固定效應與隨機效應的線性模型；隨機效應吸掉同一位 donor / 同一張板內細胞共享的基線變異，避免 pseudoreplication。
- **fixed effect**：研究問題本身想正式比較的因子；本研究例子有 cell type、CH status、clone genotype、dominant HSC group。
- **random effect**：會造成額外變異但研究者不想逐一比較的因子，模型把它當成共享變異吸掉；本研究例子有 donor、FACS-sorting plate、有時還有 sex / age。
- **dream (variancePartition v1.22.0 / v1.33.0)**：把 voom 加權流程嫁接到 LMM 上的差異表現工具，支援 random effect；本研究每個基因用 dream 擬合、用 eBayes 計算 p 值。
- **limma-voom**：RNA-seq 經典管線：voom 先把 counts 轉成 log-CPM 並按平均-變異關係給精準度權重，limma 再對加權值跑線性模型；本研究透過 dream 取得 random effect 支援。
- **scran size factors**：把表現相似的細胞 pool 起來算 size factor 再解迴單細胞的 normalization 方法；比中位比更耐零值稀疏的單細胞資料。
- **FACS-sorting plate batch effect**：TARGET-seq+ 每張 384 孔板的反轉錄效率、引子批次、定序覆蓋深度都會有系統性差異；本研究在每個比較裡都把 plate 寫進共變項或隨機效應。
- **NOC153 technical control**：作者每次 sort 都納入同一份 NOC153 骨髓樣本當技術對照，提供跨板校正的基準線。
- **DNMT3A / TET2**：兩個最常見的 CH 突變基因；TARGET-seq+ 用目標 amplicon 在每顆細胞上 genotype 這兩個位置。
- **clone (CH-WT vs CH-mut)**：同一位 CH 病人骨髓裡帶相同突變的子代細胞群；CH-WT vs CH-mut 比較在病人內以 clone 為固定效應做，donor 差異被天然抵銷。
- **pySCENIC (v0.12.0) + AUCell regulon activity**：pySCENIC 用 motif 表 (motifs-v10nr_clust-nr.hgnc-m0.001-o0.0.tbl) 剪掉假目標基因留下真正帶 motif 的目標；AUCell 給每顆細胞每個 regulon 打 0-1 活性分數，再丟回同一套 dream LMM 做差異。
- **likelihood ratio test**：比較含固定效應的完整模型 vs 不含固定效應的縮減模型，算固定效應是否顯著；本研究 regulon 差異活性用此法取 p。
