---
title: "鈣訊號即時影像（GCaMP6f / Fluo-4）"
subitem_id: "2-G"
---

# 主線
在不破壞活體培養的條件下，以基因編碼鈣指示蛋白或染料即時擷取 milliPillar 組織之鈣瞬變 (calcium transient)，作為計算 Tau、FWHM、Contract/Relax 50/90、FW90M 等參數的原始訊號。

# 技術解析
心肌每跳一下都先把鈣離子從細胞內的小倉庫倒進細胞質、肌肉因此收縮，再迅速把鈣抓回倉庫放鬆，這條「鈣濃度先升再降」的曲線就叫鈣瞬變 (calcium transient)。錄下它就等於同時讀到「電指令何時送達、肌肉何時開始用力、何時鬆開」三個時刻。作者沒有把肌條夾出培養槽，而是直接把整片 milliPillar 滑上倒立螢光顯微鏡 (IX-81，Olympus) 的活體腔載台 (Stage Top Incubator，Tokai Hit)，37 °C、5% CO₂ 等同把培養箱搬到鏡頭下；鏡頭從玻璃底面往上拍 well 底的水平 pillar，肌條繼續在原培養液裡跳。感光端是科學級背照式 sCMOS 相機 (Zyla 4.2，Andor)，搭配 GFP 濾片組——用約 488 nm 藍光激發、只放 510 nm 綠色發射光進相機，足以在 20 fps 下解析每一拍鈣訊號的上升下降。

讓「鈣多少」變成「光多亮」的關鍵分子有兩種。第一種是基因編碼的鈣指示蛋白 (GCaMP6f，Chen et al. Nature 2013)：它是一塊被切開重接的綠螢光蛋白 (cpEGFP) 中間夾著鈣感測器 calmodulin 與它的靶肽 M13；沒鈣時 cpEGFP 開口鬆開、很弱，鈣一插進 calmodulin 就把 cpEGFP 開口闔上，整顆蛋白瞬間變亮，鈣退場時亮度回落。作者用的 WTC11-GCaMP6f iPSC 把這段序列插在 AAVS1 安全著陸點 (AAVS1 safe harbor locus) 的單一對偶，這個位置是科學界已知的「插入後不擾動鄰近基因」的座標；只插一條染色體留另一條野生型，避免兩份螢光蛋白塞爆細胞。第二種是 Fluo-4 AM (Invitrogen F14201) 這顆小分子染料，10 µM 泡入培養液 45 分鐘就會穿膜進細胞、鈣一抓上去就發綠光；它疏水容易結團，所以要搭 0.1% Pluronic F-127 (Sigma-Aldrich P2443) 這種把疏水分子包成小水球的助透劑才能均勻進細胞。

為什麼預設用 GCaMP6f 而把 Fluo-4 AM 當備案？GCaMP6f 是細胞自己合成的螢光蛋白，肌條養多久就跟著表達多久，要錄影直接照、完全不必拆組織或染色；Fluo-4 AM 每次都得重染 45 分鐘、會慢慢從細胞滲出，助透劑與染料殘留也可能干擾肌條收縮，長期或重複錄影並不划算。Fluo-4 AM 的價值是給「手上細胞株沒做 GCaMP6f knock-in」的使用者一個立刻能用的備案。

錄影設定都有目的。20 fps 是每秒抓 20 張，足以把每一拍鈣訊號的上升下降解析開。錄 4600 張畫面 (約 230 秒) 對應作者測 ET/MCR 的整段刺激節目，錄 300 張 (15 秒) 配 1 Hz 刺激則能抓到約 15 個鈣瞬變、足以平均出穩定數值。每次正式錄影前都先跑一次同樣的刺激當暖身 (analysis stimulation regimen)，因為剛被電的肌條會有一兩拍適應期，先讓組織進入穩態再錄第二次才不會把暖身雜訊算進去。

兩個常見坑要避開。第一是藍光毒性：488 nm 激發光照久會在細胞裡生出活性氧 (reactive oxygen species)，輕則螢光分子越拍越暗 (photobleaching)，重則肌條跳動異常甚至死亡；作者因此刻意把每段錄影壓到 15 秒到 4 分鐘以內，並用亮場影片驗證 ET/MCR 可得到一致結果，能用亮場就盡量別開藍光。第二是離開培養條件：心肌對溫度與 pH 極敏感，溫度從 37 °C 掉到室溫鈣回收會立刻變慢、Tau 拉長，二氧化碳跑掉跳動頻率與收縮力也會飄，所以非得用活體腔載台把培養箱搬到鏡頭下，否則所有時間動力學參數的基準線都會被改掉。

# 工具/方法/材料
- **GCaMP6f**：基因編碼鈣指示蛋白：cpEGFP 中間夾 calmodulin 與 M13，鈣一接上就讓蛋白瞬間變亮 (Chen et al. Nature 2013)。
- **WTC11-GCaMP6f iPSC**：GCaMP6f 序列插在 AAVS1 安全著陸點單一對偶的 iPSC 細胞株，可長期穩定報告鈣訊號。
- **AAVS1 safe harbor locus**：人類基因組中「插入外來基因後不會擾動鄰近基因」的座標，作者把 GCaMP6f knock-in 在這裡。
- **Fluo-4 AM**：小分子鈣螢光染料 (Invitrogen F14201)，10 µM、37 °C 45 分鐘可進入無 GCaMP 細胞，鈣一抓上去就發綠光。
- **Pluronic F-127**：非離子型助透劑 (Sigma-Aldrich P2443)，0.1% 把疏水 Fluo-4 AM 包成小水球助其進細胞。
- **Stage Top Incubator**：活體腔載台 (Tokai Hit STX)，把 37 °C、5% CO₂ 培養條件搬到顯微鏡下，肌條不必離開培養。
- **sCMOS camera Zyla 4.2**：Andor 科學級背照式感光晶片，靈敏、可 20 fps 拍下鈣訊號每一拍細節。
- **Inverted fluorescence microscope IX-81**：Olympus 倒立螢光顯微鏡，從玻璃底面往上對焦水平 pillar 與肌條。
- **GFP filter set**：488 nm 激發、510 nm 發射的標準綠螢光濾片組，把 GCaMP/Fluo-4 訊號從背景中切出來。
- **analysis stimulation regimen**：正式錄影前先跑一次相同刺激當暖身，讓組織進入穩態避免適應期雜訊。
- **photobleaching**：螢光分子被藍光照久後逐漸失去發光能力，是限制 GCaMP6f/Fluo-4 錄影時間的主因之一。

# 與此篇文章的關係
在《milliPillar: A Platform for the Generation and Real-Time Assessment of Human Engineered Cardiac Tissues》中，作者要在 21 天電刺激訓練前後比較同一條 iPSC 心肌組織的功能變化，因此採用 GCaMP6f knock-in 細胞配合活體腔載台 (Stage Top Incubator) 即時錄影鈣瞬變。此法解決了傳統 Fluo-4 AM 必須反覆染色、且需把組織搬出培養槽才能成像所造成的擾動與光毒性問題，產出的鈣螢光時間序列直接交給下游 Python 腳本萃取 Tau、FWHM、Contract/Relax 50/90 等指標。
