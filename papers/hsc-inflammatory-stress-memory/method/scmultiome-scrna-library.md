---
subitem_id: "2-D"
title: "scMultiome / scRNA-seq 文庫建構與測序"
---

# scMultiome / scRNA-seq 文庫建構與測序

**Subitem:** 2-D · **Slug:** `scmultiome-scrna-library`

## 主線
對異種移植 HSPC、CD34⁺CD38⁺ progenitor 與 CD33⁺ 髓系後代分別建立可同時讀取同核 RNA + ATAC (scMultiome) 或單細胞 RNA (scRNA-seq) 的文庫，將「轉錄程式」與「染色質印記」放在同一張 UMAP 上做 WNN 整合。

## 技術解析
scMultiome 用兩步走：第一步把細胞膜打掉、只留下完整細胞核，這樣 RNA 與染色質都還在同一顆核裡；第二步把核懸液送進 10X Chromium 微流體晶片，晶片像三明治機把每顆核夾進一顆油滴，油滴裡有一段獨特的 24 鹼基細胞條碼，同條碼的 RNA 與 ATAC 訊號之後就知道來自同核。ATAC 端先用 Tn5 轉位酶（一種會把 DNA 切開並順手插一段定序頭的酵素）處理核，它只插得進染色質鬆開的位置；RNA 端用 polyT 引子捕獲 mRNA 的 polyA 尾巴。作者按下游問題分流平台：HSPC 與 progenitor 走 scMultiome（要看染色質記憶）；CD33⁺ 髓系後代細胞數多、染色質意義不大，改走 10X 3' v2 scRNA-seq；CB LT-HSC 另用 BD Rhapsody 板式平台跑一條讀深度更高的 scRNA-seq 來驗證 cNMF 程式。最後用 WNN (Hao et al. Cell 2021) 整合：對每顆細胞分別問「RNA 端最像我的鄰居是誰？」「ATAC 端最像我的鄰居是誰？」綜合成一張鄰居名單，再用 UMAP 攤平成同時反映轉錄與染色質狀態的二維地圖。

Tn5 怎麼「只挑開放染色質」？它的物理尺寸大約是 nucleosome（DNA 纏在 histone 蛋白球上的單位）的兩倍，實體進不去包緊的染色質，只有 nucleosome 不在的裸露 DNA——通常是 promoter、enhancer 等被打開的調控元件——Tn5 才插得進，讀回來的 reads 等於把全基因組的染色質開關地圖標出來。為什麼非要 RNA 與 ATAC 在同核量？分批跑只能說「TNF 組平均 RNA 這樣、ATAC 那樣」，那是群體層次的關聯；要證明「同一顆 HSC 同時把染色質鎖在開放 + 轉錄偏發炎」，必須兩訊號從同核同讀——這是 HSC-iM 記憶的分子定義。WNN 為什麼要動態加權而不直接拼接？因為 ATAC 維度（數十萬 peak）遠高於 RNA（萬個基因），直接拼會讓 RNA 被淹沒；WNN 對每顆細胞動態問「哪邊找鄰居清楚」，清楚的那邊權重高，例如純休眠 HSC 的 ATAC 可能比 RNA 更能定義身分，這時 ATAC 權重就會自動拉高。

如果只跑 scRNA-seq 不做 scMultiome，作者頂多能說 TNF/LPS 組 RNA 有些差異，無法宣稱分子記憶——因為 RNA 是即時被朗讀的狀態，急性發炎散去後 8–18 週內多半已回到 baseline；記憶其實寫在染色質。同樣容易被忽略的是批次混淆：三組處理 × 三個 CB pool 如果隨便排，「處理效應」會跟「池差異」分不開。作者的解法有三層——每個 pool 都同時包含 PBS、TNF、LPS（3 × 3 設計）；下游細胞按組合併分選後送同一 Chromium run；分析時用 Harmony 對推斷的捐贈者性別做 batch 校正，再用 SoupOrCell 從 SNP 把每顆細胞回溯到捐贈者。三層加起來讓「池 × 處理」confound 被攤平。

## 工具與材料清單 (Toolchain)
- **10X Genomics Chromium scMultiome RNA + ATAC**：把每顆細胞核包進油滴並掛上唯一細胞條碼，同核同時讀 RNA 與染色質開放性。
- **核分離 (nuclei isolation)**：把細胞膜打掉只留下完整核，讓 RNA 與染色質都在同一單位內。
- **Tn5 轉位酶**：切 DNA 並同時插定序頭的酵素，物理上只能插進 nucleosome 不在的裸露 DNA，是 ATAC-seq 的基礎。
- **polyT 引子**：RNA 端用來捕獲 mRNA polyA 尾巴的引子。
- **10X 3' v2 scRNA-seq**：用於 CD33⁺ 髓系後代等不需要 ATAC 的高細胞量樣本。
- **BD Rhapsody (板式 scRNA-seq)**：讀深度高的板式平台，用於 CB LT-HSC 驗證 cNMF 推出來的轉錄程式。
- **WNN (weighted nearest-neighbour)**：對每顆細胞動態加權 RNA 與 ATAC 找鄰居，整合成同一張雙模態 UMAP。
- **3 CB pool × 3 處理設計**：每個 pool 都包含 PBS/TNF/LPS 三條件，避免「處理 × 池」confound。
- **Harmony 批次校正**：以推斷的捐贈者性別為 batch 對 PC 空間做整合。
- **SoupOrCell**：從 BAM 上的 SNP 把混合 pool 的細胞回溯到單一捐贈者。
