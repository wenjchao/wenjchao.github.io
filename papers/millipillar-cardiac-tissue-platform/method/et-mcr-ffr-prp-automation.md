---
title: "ET / MCR / FFR / PRP 自動量測程式"
subitem_id: "3-C"
---

# 主線
以單一自動化錄影流程一次萃取 excitation threshold (ET)、maximum capture rate (MCR)、force–frequency response (FFR) 與 post-rest potentiation (PRP)，取代過去逐項手動量測，消除眼測偏誤。

# 技術解析
這個程式的目的是一次拿到四個指標，分別捕捉電生理、力學與鈣倉庫三個獨立成熟化線索。ET (excitation threshold, 興奮閾值) 是把電壓從高慢慢降、組織再也跟不上每個電脈衝的最低電壓，ET 越低代表細胞越敏感、離子通道越成熟；MCR (maximum capture rate, 最大跟拍頻率) 是把頻率從慢往上加、組織再也跟不上的最高頻率，MCR 越高代表細胞復原越快；FFR (force–frequency response, 力—頻率反應) 是在不同頻率下量收縮力、看「越跳越快時力是變大還是變小」，越跳越用力是成年心肌的招牌；PRP (post-rest potentiation, 休息後反撲力) 是刺激暫停 20 秒再恢復、量首拍力的相對提升比，反映鈣倉庫 (肌漿網, SR) 的囤貨能力。要怎麼自動量到這四個？Arduino 刺激器按預先寫好的時程跑三段一次掃完：ET 段是 1 Hz、電壓 5 V 起每 5 秒降 0.5 V；MCR/FFR 段把電壓固定 5 V (確保高於 ET 不會因電壓太低跟不上)、頻率從 1 Hz 起每 20 秒加 0.5 Hz 至 4 Hz——同一段錄影同時算出 FFR 曲線和 MCR；最後 PRP 段刺激暫停 20 秒讓 SR 累積鈣，再以 1 Hz 重啟取首拍力。失同步偵測用「鎖時窗」：每個電脈衝後留 100–200 毫秒時間窗，看裡面有沒有對應的鈣峰或收縮峰，連續多次失同步才判 loss of capture，這比純計數穩健。要做到 24 顆組織整夜全自動，總控軟體 (Supplementary File S2) 把 Arduino 刺激器的當下參數、相機影格時間戳、顯微鏡 XY 平移台的位置三者鎖在同一時間軸上——若沒對齊，Arduino 已升頻但相機還在錄上一段會讓整條 FFR 錯位，XY 平移台提早移走會讓下一顆吃到別人的 PRP 起拍，整批參數整段不可用。為什麼要這麼大費周章自動化？因為手動量 ET 時研究員會受疲勞、主觀標準飄移影響，FFR 逐段算平均也容易因「這段看起來像離群」而選擇性剔除；自動化把所有 trace 套同一個閾值、同一段時間窗，跨組織、跨批次都用同一把尺，整段移除人為偏誤。品管則交給 FW90M (峰值九成高度橫切的塔頂寬)——這個指標對「組織內部收縮同步性」最敏感，組織裡若細胞各跳各的、峰頂會被拖寬；作者把 FW90M 上下各 10% 的離群組織剔除，留下的樣本才接近常態分布，paired t-test 才不會被離群點拉壞。最後一個埋伏要記住：如果一條組織有自激心律，這些自激峰可能剛好落在電脈衝後的時間窗裡被誤判為跟拍，組織明明已經失同步、ET/MCR 卻被高估；作者建議分析完仍要回原始影片人眼確認，特別是 ET 邊界與 MCR 上下，確認是真同步還是巧合落窗。

# 工具/方法/材料
- **ET (excitation threshold)**：1 Hz 下電壓從高慢慢降，組織仍能跟拍的最低電壓；反映離子通道敏感度。
- **MCR (maximum capture rate)**：電壓固定下頻率往上加，組織仍能逐拍跟拍的最高頻率；反映復原能力。
- **FFR (force–frequency response)**：不同頻率下平均 active force 的曲線；越跳越用力是成年心肌的招牌特徵。
- **PRP (post-rest potentiation)**：刺激暫停 20 秒後重啟，首拍力相對提升比，反映肌漿網鈣囤貨能力。
- **Voltage ramp 5 V → 0.5 V step / 5 s**：ET 量測的自動電壓掃描時程。
- **Frequency ramp 1 → 4 Hz / 0.5 Hz / 20 s**：MCR/FFR 共用的自動頻率掃描時程，電壓固定 5 V。
- **20 s rest interval**：PRP 量測必要的暫停時段，讓 SR 持續累積 Ca²⁺。
- **Loss-of-capture detection (鎖時窗)**：每個電脈衝後留 100–200 ms 時間窗檢查有無對應收縮/鈣峰；連續多次失同步才判 loss of capture。
- **Three-way synchronization**：總控軟體把 Arduino 刺激器、相機時間戳、XY 平移台位置鎖在同一時間軸，整夜自動巡迴 24 顆組織。
- **FW90M trimming (上下 10%)**：用 FW90M 量組織內部同步性、剔除離群組織，讓 paired t-test 樣本接近常態分布。
- **Spontaneous beating artifact**：組織自激心律可能巧合落在時間窗內被誤判同步，需人工複核 ET/MCR 邊界。

# 與此篇文章的關係
在《milliPillar: A Platform for the Generation and Real-Time Assessment of Human Engineered Cardiac Tissues》這篇文章中，作者為了在 24 顆組織同時驗證 21 天電刺激成熟化效應，採用「Arduino voltage/frequency ramp + 鎖時窗失同步偵測 + 三方同步軟體」一次自動萃取 ET / MCR / FFR / PRP。它解決了過去逐項手動量測耗時、判斷標準因人而異的瓶頸，把刺激—錄影—移台整段流程鎖在同一時間軸上，整夜跑完直接餵給下游 paired t-test 比較刺激前後。
