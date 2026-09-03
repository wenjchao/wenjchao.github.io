# 鵪鶉胚胎電穿孔活體影像與 FGFR 藥物擾動

1. 引用自哪篇 paper: developmental-organization-sensory-sympathetic-ganglia
2. Outline (任務主線): 鵪鶉胚胎電穿孔活體影像與 FGFR 藥物擾動
3. Method:

作者先把一顆鵪鶉受精蛋開窗、把胚胎連同蛋清移到含 agar-albumin 的培養皿裡繼續發育 (ex ovo culture)。等胚胎到 Hamburger-Hamilton stage 4 (HH4)——此時 NC 剛被誘導、還完全沒開始從神經管剝離——用玻璃毛細管把一小滴含螢光報導基因的 DNA 注在胚胎表面，再用 NEPA21 脈衝器的鉑金板電極上下夾住胚胎，打三下 3 V、50 ms 的短脈衝把 DNA 擠進背側的神經板細胞（這一步叫電穿孔，原理是短高壓電讓細胞膜暫時裂出小洞、DNA 趁機被吸進去，脈衝結束後膜自己封回來）。這段 DNA 帶的是「PAX7 enhancer 或 FoxD3 enhancer + H2B-Citrine / H2B-EGFP」——這兩段增強子只在 NC 前驅細胞裡被打開，所以電穿孔雖是亂槍打鳥，最後只有真正是 NC 的細胞會亮綠；螢光還特意綁在 H2B 這個染色質組蛋白上，把訊號集中成細胞核大小的亮點，方便自動追蹤。等胚胎再發育幾小時到 HH9/HH11，作者把它移到 Zeiss LSM 710 共軛焦顯微鏡上，在 37.5°C 保溫罩裡連拍 6 小時 time-lapse，每顆亮綠 NC 的位置變化一格一格記下來。

為了問「NC 剝離前會不會跨過中線跑到另一側」，作者做了一個古典的單側電穿孔設計：把 DNA 只打到胚胎左半邊，並額外加一顆 H2B-emiRFP670 紅螢光當「電穿孔真的只成功在左側」的內建驗證。幾小時後如果右側也出現只有從左側標記過的細胞才會有的綠螢光，就代表這顆 NC 真的跨過中線。同樣為了因果驗證 FGF 訊號的角色，作者用 pan-FGFR 抑制劑 infigratinib (NVP-BGJ398) 10 μM 泡胚胎——這顆小分子藥的原理是卡住 FGFR 內側「像小發電機的酵素部位 (tyrosine kinase)」的能量入口，讓 FGFR1–4 家族成員都發不了電，就算細胞外 FGF 還在，訊號也傳不下去。作者在 agar-albumin dish 背側先滴 20 μl 藥、胚胎放上去、再從腹側加另外 20 μl，確保藥物同時從上下兩面滲進；先泡 1.5 h 讓 FGFR 訊號達到「被完全擋住」的穩態，才開始拍片。這樣才能捕捉到真正的擾動效果，而不是拍到訊號還沒被擋住的過渡期。

拍完 6 h time-lapse 後，訊號進 Imaris (v10.0.1)——這個軟體先做 time-lapse 對位、抵消整個胚胎在保溫罩裡的震動，再對每個 H2B 亮點做 3D spot detection 與 track linking，把「這一格哪顆 = 下一格哪顆」串成一條軌跡。track 位置匯出到 MATLAB 做位移計算，但這裡有一個關鍵校正：鵪鶉胚胎在 6 h 內身體後端會持續向後拉長，整個胚胎在顯微鏡座標系裡整體漂移。如果只看每顆 NC 的絕對位置變化，會誤把「胚胎整體被拉走」當成「細胞自己往後動」。作者的解法是在 FIJI 的 Brightfield channel 上用矩形選區的中心點標定每個 somite (胚胎背側一段一段像串珠的節段，未來會發育成脊椎與肌肉) 的位置，量出 somite 位移，再把每顆 NC 的位移都減掉「牠所在 somite 的位移」，剩下的才是「這顆細胞相對胚胎自己動了多少」。校正後就能乾淨算出頭尾方向 (rostrocaudal) 與內外側方向 (mediolateral) 的分別位移量，最後在 Prism 裡做 two-tailed t 檢定，比較 DMSO 對照組（n = 237 cells / 4 embryos）與 FGF 抑制組（n = 243 cells / 4 embryos）的差異。

這套設計有兩個一失守整段實驗就報廢的環節。第一：如果作者拿的是「不管什麼細胞都會亮」的常開啟動子（例如 CMV）而非 NC-specific enhancer，電穿孔亂槍打鳥後神經管本體、外胚層、體節細胞都會亮綠，tracking 出來的軌跡混入大量非 NC 細胞運動，「NC 有 21.2% 跨越 somite 頭尾移動」這種乾淨數字就會被稀釋到看不見。第二：如果跳過 somite drift normalization，胚胎後端拉長會讓所有細胞看起來都朝尾端漂，結論會荒謬地變成「100% NC 都在做 rostrocaudal 遷移」，且 infigratinib 讓 rostrocaudal 移動下降的效應也無從偵測（背景已被漂移灌滿）。這也是為什麼作者要花額外力氣把 somite 中心用 FIJI 逐顆標定的原因——沒有這一步，後面所有量化結果都不能信。

4. 工具與材料:

- **HH4 (Hamburger-Hamilton stage 4)**: 鵪鶉胚胎發育早期分期，NC 剛被誘導、還完全沒剝離的時間窗。
- **ex ovo culture**: 把胚胎連蛋清從蛋殼取出、放到 agar-albumin 培養皿繼續發育，方便顯微鏡即時取像。
- **電穿孔 (NEPA21)**: 打三下 3 V × 50 ms 短脈衝讓細胞膜暫時裂出小洞、DNA 被吸進去，脈衝結束後膜自己封回。
- **PAX7 enhancer / FoxD3 enhancer**: 只在 NC 前驅細胞裡被打開的增強子片段，驅動螢光只在 NC 表現，避免電穿孔亂槍打鳥。
- **H2B-螢光融合**: 螢光蛋白綁在 H2B 組蛋白上、集中在細胞核，讓自動追蹤能把每顆細胞視為獨立亮點。
- **H2B-emiRFP670**: 第二顆遠紅螢光，用來驗證單側電穿孔真的只成功在一邊，作為 midline-crossing 實驗的內建對照。
- **Zeiss LSM 710 + GaAsP 488 nm 偵測器**: 共軛焦顯微鏡搭配高靈敏綠光偵測器，能在保溫罩內連拍 6 小時 3D time-lapse。
- **infigratinib (NVP-BGJ398)**: pan-FGFR 小分子抑制劑，10 μM 卡住 FGFR1-4 的酵素能量入口，讓四個家族成員都發不了電。
- **Imaris**: 3D 影像分析軟體，做 time-lapse 對位、spot detection 與 track linking，把亮點串成軌跡。
- **somite drift normalization**: 在 FIJI 標定 somite 中心，把每顆 NC 的位移減掉所在 somite 位移，扣除胚胎整體後端伸長造成的漂移。

5. 與此篇文章的關係:

在《Developmental organization of sensory and sympathetic ganglia》這篇文章中，作者為了驗證「NC 在剝離前就沿頭尾方向遠距離遷徙、甚至跨越中線」這個從人體 MV 條碼與小鼠 CRISPR 分析推得的模型，用鵪鶉 HH4 胚胎的 ex ovo 電穿孔搭配 PAX7 / FoxD3 enhancer 報導基因做 6 h 活體共軛焦影像。這解決了「小鼠胚胎不透明無法即時 tracking」與「人類胚胎不可觸及」的雙重障礙，把靜態的 clonal 分布推論升級為動態的細胞軌跡；再以 pan-FGFR 抑制劑 infigratinib 打斷訊號，把 FGF 對 rostrocaudal 遷移的角色從「相關」升級為「因果」。
