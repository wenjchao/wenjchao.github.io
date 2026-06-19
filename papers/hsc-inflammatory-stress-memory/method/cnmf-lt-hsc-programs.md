---
subitem_id: "3-A"
title: "Consensus NMF 拆解 LT-HSC 轉錄程式"
---

# Consensus NMF 拆解 LT-HSC 轉錄程式

**Subitem:** 3-A · **Slug:** `cnmf-lt-hsc-programs`

## 主線
在 3,381 顆 CB LT-HSC 中以非監督式 cNMF 分解出穩定的轉錄程式 (quiescence、cycle priming、inflammation 等)，並以 silhouette + Frobenius reconstruction error 同時最佳化模組數量，作為下游所有「HSC-iM signature」推斷的基底。

## 技術解析
作者把 3,381 顆從臍帶血純化出來的長期造血幹細胞 (CB LT-HSC) 的 RNA 量疊成一張「細胞 × 基因」大表，再拆回幾本「同類細胞在做的轉錄工作」的工作簿。拆解方法叫非負矩陣分解 (NMF)：它保證每顆細胞的表現量都能寫成幾本工作簿的正權重加總，符合『表現量不可能是負的』這個生物事實。NMF 單跑一次結果會晃，所以作者用 consensus NMF (cNMF v1.3.4, Kotliar et al. eLife 2019)，反覆跑 100 次再取每次都長一樣的版本當共識。每本工作簿——也就是一個程式 (program)——就是一份「基因 + 權重」的清單，同一顆細胞可以同時翻幾本，這比把細胞硬切成幾群的傳統做法細緻得多。輸入 cNMF 要餵兩份資料：原始 count 表 (`--counts`) 用來算統計、SCTransform v2 校正過深度的數值 (`--tpm`) 用來實際分解。

決定『一共有幾本工作簿』是 cNMF 最關鍵的參數。作者把 K 從 2 掃到 15，同時看兩條曲線挑甜蜜點：silhouette 分數量『每次重跑這 K 本簿子長得有多像』，越高越穩定；Frobenius 重建誤差量『用這 K 本簿子重組原始表現矩陣有多接近』，越低擬合越好。只看 silhouette 會挑太小、只看 Frobenius 會挑太大；兩條一起看，找『穩定性還沒崩、誤差已經失速』的共同拐點才安全。拿到 K 本簿子後 cNMF 不會自動命名，作者把每本的 top 100 高權重基因抓出來，丟給 MSigDB hallmark + 自編 HSC 基因清單，用 fgsea v1.18.0 的 `fora` 函數做 over-representation 檢定：top 100 大量落在『TNFα signaling via NFκB』類就是發炎程式，落在『細胞週期抑制』類則是靜止程式。

作者沒有直接用其中一份資料集的 top 200 當 HSC-iM signature，而是同時跑 BD Rhapsody (板式) 與 10X CB Multiome (微滴) 兩個平台、兩條 cNMF。這兩種平台對 mRNA 的捕捉效率與噪音分布都不一樣，單跑任一邊得到的 top 200 會帶平台偏差，拿去比對 COVID、CH、ageing、SCD 那麼異質的人類資料集就會吃虧。作者的策略是找出兩邊都跑出來、基因組成大致重疊的對應程式，再把同一基因在兩邊的權重做幾何平均 (要兩邊都高才會高分)，取幾何平均後 top 200 當共識 meta-program，作為後續所有「HSC-iM signature」推斷的基底。

這條 pipeline 有兩個容易踩雷的地方。其一，跳過 SCTransform v2 直接拿原始 count 丟給 cNMF，每顆細胞被測到的 mRNA 總量不平均會被學成『高深度簿子 vs 低深度簿子』兩本偽程式——根本不是生物學差異，只是測序深度偏差，HSC-iM signature 到了別的資料集就對不上。其二，K 直接拉到上限 15，cNMF 會把同一個生物程式硬拆成兩三本、或把單顆 outlier 細胞的雜訊獨立成程式；這些碎掉的簿子在 Rhapsody 與 10X 之間找不到對應，meta-program 合併直接做不出來。

## 工具與材料清單 (Toolchain)
- **cNMF (consensus NMF)**：把細胞 × 基因表現量矩陣拆成幾本『工作簿』的非監督式分解方法，反覆跑 100 次後取共識；本研究用 v1.3.4 (Kotliar et al. eLife 2019)。
- **NMF (non-negative matrix factorization)**：保證所有權重為正的矩陣分解；符合『基因表現量不可能是負的』這個生物事實。
- **Program**：cNMF 給出的一本工作簿，等於一份『基因 + 權重』清單；同一細胞可同時翻幾本。
- **K (工作簿數量)**：cNMF 要預先決定的程式總數；本研究掃 K = 2–15 並用兩條曲線挑甜蜜點。
- **Silhouette score**：量『跨重複跑這 K 本簿子長得多一致』的穩定性指標，越高越穩定。
- **Frobenius reconstruction error**：量『用 K 本簿子重組原始表現矩陣有多接近』的擬合指標，越低越精確。
- **SCTransform v2**：把原始 count 轉成『扣掉深度後的殘差』的標準化方法；cNMF 的 `--tpm` 欄位餵的是它的輸出。
- **fgsea fora**：對每本程式 top 100 基因做 over-representation 檢定，用 MSigDB hallmark + 自編 HSC 基因清單反推程式身分；本研究用 fgsea v1.18.0。
- **Meta-program**：跨平台 (Rhapsody + 10X) 對應程式經幾何平均後取 top 200 基因的共識清單，作為 HSC-iM signature 的基底。
