---
subitem_id: "2-C"
title: "T 細胞擴增培養與 CapTCR-seq"
---

# T 細胞擴增培養與 CapTCR-seq

**Subitem:** 2-C · **Slug:** `t-cell-expansion-captcr-seq`

## 主線
排除「重複發炎組 T 細胞比例上升是否來自單一純株擴增 (clonal expansion)」的可能性，用體外刺激後測定 TCR 多樣性指數 (Shannon's diversity)。

## 技術解析
作者要排除「重複發炎組 T 細胞變多是不是因為某一顆 T 細胞瘋狂複製」的可能。他們先用 FACS 負篩 (CD45⁺CD34⁻CD19⁻CD33⁻) 撈出約 30 萬顆 T 細胞——之所以走負篩而不是直接抓 CD3⁺，是怕 anti-CD3 抗體預先觸發 T 細胞活化干擾後續定量。撈到的細胞泡在 X-VIVO 20 + 5% 人類 AB 血清 + 30 U/ml IL-2 的培養液裡，加入塗了 anti-CD3 與 anti-CD28 抗體的磁珠 (Dynabeads，每細胞 0.5 顆珠)，養 8 天讓所有能反應的 T 細胞同步擴增。接著抽出基因組 DNA 丟給 CapTCR-seq (Mulder et al. 2018)——這是一套用探針把 TCR 基因座從整條基因組釣出來再定序的靶向捕獲方法。每顆 T 細胞在胸腺發育時會把 TCR 基因的 V、D、J 三個片段隨機拼接，接縫處還隨機加減幾個鹼基；這段最隨機的接縫叫 CDR3，理論上可拼出 10¹⁵ 種以上的不同序列，所以同一條 CDR3 出現多次就代表「這顆 T 細胞分裂出來的子代」。把每條 CDR3 在族群中的比例 $p_i$ 套進 Shannon 公式 $H = -\sum_i p_i \ln(p_i)$ (依 Brugman et al. 2015)：只有一條 CDR3 (純株擴增) 時 $H = 0$；種類愈多、分布愈均勻，$H$ 愈大。

為什麼非要 anti-CD3/CD28 Dynabeads 體外戳醒，而不直接做新鮮血液 TCR 定序？兩個原因疊在一起。其一，anti-CD3 與 anti-CD28 抗體分別模擬 APC 給 T 細胞的訊號 1 (有抗原給你看) 與訊號 2 (授權你動作)，兩個訊號同時到位才能戳醒 T 細胞；磁珠把兩個訊號物理上靠到一顆 APC 的距離內，所有活的 T 細胞不管專一性都會被同步活化。其二，這層擴增讓細胞從 30 萬長到上百萬、gDNA 從奈克拉到微克級，CapTCR-seq 的探針才抓得全。為什麼選 CapTCR-seq 而不是 bulk RNA-seq？因為 RNA-seq 受 TCR 表現量差異與 PCR bias 影響，活化高的細胞會叫得比較大聲讓族群比例失真；CapTCR-seq 直接從 gDNA 釣 TCR 基因座，每顆 T 細胞貢獻的基因組份數固定 (兩條染色體)，數 CDR3 份數就等於數細胞數，Shannon 才能準確反映純株結構。

如果作者只比較 T 細胞數量或 CD8/CD4 比例就下結論，會卡在三種情境分不開：是某顆碰巧認得抗原的 T 細胞瘋狂複製 (clonal expansion)、還是發炎讓全體 T 細胞均勻 homeostatic 增殖、還是 HSC-iM 真的多生了一批多元的 T 細胞？三者生物學意義天差地遠——clonal expansion 跟 HSC 記憶沒關係，是某個 T 細胞剛好遇到 antigen；沒有 CapTCR-seq + Shannon 這道讀數，「重複發炎組 T 細胞增加是因為 HSC 程式改變」的論述會被一句話打回。同樣地，如果跳過 8 天擴增直接做 CapTCR-seq，30 萬顆細胞的 gDNA 只有奈克級遠低於探針捕獲下限——少數恰好量夠的 clone 會主導讀數，讓 Shannon 假性偏低；擴增到微克級才能讓真正的多樣性結構被抓全。

## 工具與材料清單 (Toolchain)
- **FACS 負篩 (CD45⁺CD34⁻CD19⁻CD33⁻)**：排除 B、髓系、HSPC，保留所有 T 細胞且維持靜止狀態。
- **X-VIVO 20 + 5% AB serum + 30 U/ml IL-2**：T 細胞擴增培養基，IL-2 是 T 細胞最關鍵的增殖訊號。
- **anti-CD3/CD28 Dynabeads (0.5 beads/cell)**：把 APC 的訊號 1 與訊號 2 縮在一顆磁珠上模擬 immune synapse，戳醒所有 T 細胞同步擴增。
- **CapTCR-seq (Mulder et al. 2018)**：用探針從 gDNA 釣出 TCR 基因座再定序，每細胞貢獻份數固定，可直接量化 clonotype 比例。
- **CDR3 區段**：TCR V(D)J 重組接縫處的隨機序列，作為每顆 T 細胞的獨特指紋。
- **Shannon's diversity ($H$)**：$H = -\sum p_i \ln p_i$，同時抓族群豐富度與均勻度；純株擴增 $H = 0$。
- **QIAamp DNA Blood Mini Kit**：標準 gDNA 萃取套組，NanoDrop ONE 定量後送 CapTCR-seq。
