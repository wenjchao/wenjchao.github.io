---
title: "Pillar 力—位移線性回歸與材料變異性分析"
subitem_id: "3-D"
---

# 主線
將 Microtester 量測之力—位移數據擬合為線性彈性方程，提供可直接套用於影片分析的單一係數，並評估批次間 PDMS 機械變異。

# 技術解析
整個流程的目標是替每根 pillar 量出一條可以一勞永逸的「位移→力」換算尺，並確認這把尺真的穩定。Microtester MT-LT (CellScale) 是一台桌上型顯微力學儀，用 0.4064 mm 圓柱鎢梁配 1×1 mm 壓盤當推頭，把 milliPillar 夾在量測台上，以 8.5 µm/s (慢推避免動態效應，得到純靜態彈性反應) 沿垂直 pillar 軸向推 pillar 頭部 0–750 µm，沿途記錄一系列「位移、力」散點。作者用線性回歸把這些散點套到 F = k·Δx 這條直線——胡克定律的標準形式——求出唯一斜率 k，r² = 0.834 代表這條直線能解釋 83.4% 的資料變異，足以說明 pillar 在這個範圍內表現得像彈簧。為什麼 PDMS 在小形變下能線性？因為它是高分子交聯橡膠，內部一張立體網被輕推時只是把原本盤捲的鏈構象稍微拉直；推太深 (> 750 µm) 鏈被完全拉開就進入非線性，所以校準特地切在 750 µm 以下，確保影片中肌條收縮造成的 pillar 位移都落在安全區。然後驗證這把尺對來回都管用：作者讓 Microtester 一次推到底再退回來，比對推進去 (loading) 與收回 (unloading) 兩條力—位移曲線是否重合——結果完全重合、無 hysteresis (遲滯)。分子層級代表鏈被拉直是熱力學可逆過程、能量存進拉直的鏈、鬆開後完整還回，沒有內部摩擦或塑性流動。實務上的好處是：同一個 k 可以同時用在收縮 (pillar 被肌條拉) 與舒張 (pillar 被被動推回) 的換算上，校準一次後整個批次的影片分析都能直接套用、同一條組織測 21 天甚至 100 天也不必反覆搬出來重校。再來問：這個 k 會不會隨手工製作飄移？作者用兩層取樣：同一張 milliPillar 上量 4–6 根 pillar 看「同板內 pillar 之間差多少」，再換 4 個獨立批次製作的平台量看「不同次配 PDMS、不同次烤箱固化後 k 飄多少」(Supplementary Figure S3C)。結論是批次間變異 > 同板內變異，所以「同批同時製作、儘早使用」是必要規範。COMSOL Multiphysics 數值模擬則扮演對照角色——把 milliPillar 幾何 (頭直徑 0.8 mm、柄長 1.75 mm) 與 PDMS 機械參數丟進去解出理論上的應力分布，實驗量到的 k 若跟模擬一致就放心，若差太多代表 PDMS 模量或幾何有偏差、要回頭檢查製程。最後一個問題：使用 k 有兩條不可踩的紅線。第一條，r² = 0.834 只在 0–750 µm 範圍成立，超出就進入非線性區、實際力會偏離線性外推值好幾十個百分比，使用者必須確認影片中 pillar 位移都落在線性區內。第二條，作者明明發現批次間變異不小，如果為了省事拿 A 批的 k 直接套在 B 批的 pillar 影片上，等於用錯了刻度尺；在電刺激成熟化研究這種要做 paired t-test 的場合，系統偏移會讓「成熟前後差異」被誇大或縮小、結論可能完全錯誤，所以「同批同時製作、儘早使用」是必要而非建議。

# 工具/方法/材料
- **Microtester MT-LT (CellScale)**：桌上型顯微力學儀，配 0.4064 mm 鎢梁 + 1×1 mm 壓盤推頭，量 pillar 力—位移曲線。
- **8.5 µm/s 推進速度**：極慢推進以避免動態效應，得到純靜態彈性反應。
- **Hooke's law (F = k·Δx)**：胡克定律，線性彈簧基本關係；本模組以此擬合 pillar 力—位移數據。
- **Linear regression / r² = 0.834**：用最小平方法把 0–750 µm 散點擬合成直線，決定係數 0.834 證實線性近似。
- **750 µm 線性區邊界**：PDMS 在此範圍內近似線性彈簧；超過進入非線性必須重新校準。
- **Hysteresis test (loading/unloading)**：比對推進與收回兩條曲線是否重合，重合即無 hysteresis，一個 k 同時管收縮與舒張。
- **PDMS molecular elasticity**：高分子交聯橡膠在小形變下鏈構象變化為熱力學可逆，是線性彈性與無遲滯的分子根源。
- **Within-platform sampling (4–6 pillars)**：同一張 milliPillar 量多根 pillar，評估同板內變異。
- **Between-batch sampling (4 batches)**：換 4 個獨立 PDMS 批次量測，評估批次間機械變異；結論為「同批同時製作、儘早使用」。
- **COMSOL Multiphysics**：工程界常用數值模擬軟體；輸入 pillar 幾何與 PDMS 參數，解出理論彎曲應力分布作為實驗對照。

# 與此篇文章的關係
在《milliPillar: A Platform for the Generation and Real-Time Assessment of Human Engineered Cardiac Tissues》這篇文章中，作者為了讓 dlib correlation tracker 量到的 pillar 位移能直接換算成絕對 mN/mm² 應力，採用「Microtester 力—位移線性回歸 + hysteresis 驗證 + 兩層批次取樣」的校準流程。它解決了過去 pillar 平台只能給相對位移、無法跨研究比較的瓶頸，產出一個可長期重用、跨收縮舒張通用的 k，餵給下游 dlib 影片分析以輸出絕對力學讀值。
