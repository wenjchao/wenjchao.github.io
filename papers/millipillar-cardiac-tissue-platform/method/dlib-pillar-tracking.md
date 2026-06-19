---
title: "Pillar 追蹤與絕對收縮力換算（dlib correlation tracker）"
subitem_id: "3-A"
---

# 主線
從 brightfield 影片中自動追蹤兩根 pillar 頭部於每一影格的位移，將其乘上前述線性彈性係數即可換算為絕對的 active force 與 passive tension（mN/mm²），達到「跨平台可比較」的力學讀值。

# 技術解析
作者寫了一隻 Python 腳本，呼叫 dlib C++ 函式庫 (github.com/davisking/dlib) 裡的相關性追蹤器 (correlation tracker)。使用者只要在第一張影格手動拉一個方框 (bounding box) 框住其中一支 pillar 頭部；之後每張影格電腦會自動找到「跟方框內畫面最像的那塊區域」並回報新座標，重複到影片結束，就得到 pillar 頭隨時間的位置序列。判斷相似度的方法承襲 Bolme et al. CVPR 2010 提出的自適應相關濾波器 (adaptive correlation filter)：先把方框內影像翻譯成方向梯度直方圖 (HOG features)——每個小格裡邊緣往哪個方向走、有多強——再用餘弦相關 (cosine correlation) 找出新影格中最像的位置；每追完一張就以最小平方法 (least squares update) 微調濾波器參數，把新樣貌加進參考樣板裡，所以 pillar 在影片中燈光漸變、角度小幅扭曲都不會追丟，這就是「自適應」的意思。為什麼要這麼繞、不直接比畫素亮度？想一下相機在培養箱裡的處境：燈光偶爾跳一下、相機自動曝光偶爾調整，整張畫面亮度就會整體跟著抖；畫素級比對會誤以為目標跑掉。HOG 只看區域內邊緣方向，跟絕對亮度無關；餘弦相關進一步只算兩張 HOG 指紋的夾角、不在意絕對強度，剛好把光照干擾整段擋掉。讀到位置之後怎麼換成力？肌條兩端各撐住一根 pillar，收縮時兩根同時往中間靠，所以兩根都要追，各自位移加起來才是組織真正的長度變化；基準點取「未刺激時兩根 pillar 之間的距離」，整個 well 微微晃動也會抵銷、只剩肌條訊號。把這個總位移 Δx 乘上 Microtester 階段量好的線性彈性係數 k 就得到當下絕對力 F = k·Δx；再除以肌條橫截面積，換算成 mN/mm² 應力 (stress)，消除肌條粗細差異，讓 milliPillar 的讀值可以跟其他平台甚至活體心肌數據放在同一張圖上比較。為什麼挑 dlib 而不是 template matching 或深度學習追蹤？純 template matching 會被光照微變整死；深度學習雖然強，但需要大量標註資料和 GPU，跟「讓任何實驗室都能照做」的目標衝突；dlib 只要畫一次方框、不必訓練模型，在普通筆電上就能即時處理 20 fps、4800 影格 (與 ET/MCR/FFR 自動刺激同步) 的長片段。最後兩個容易出包的環節都落在使用者身上：第一影格方框若畫太大，HOG 會被背景紋理稀釋、追蹤器容易鎖到旁邊的相似紋理；若畫偏沒對準 pillar 頭中心，整段都以偏移位置為基準，絕對力會被系統性高估或低估。而且相關性追蹤器本身不會察覺追丟——它只負責回報「最像方框的那塊」，就算已經跳到隔壁細胞團或培養液雜質也照報並持續更新樣板。所以作者建議錄影前先跑一輪 analysis stimulation 讓組織適應，並人工抽查影片首末幀方框位置是否合理，避免拿到一條「看起來很合理卻完全錯」的力學曲線。

# 工具/方法/材料
- **Brightfield video**：倒立顯微鏡下的亮場影片，用一般白光照明、無螢光，是追蹤 pillar 位移的原始輸入。
- **dlib correlation tracker**：dlib C++ 函式庫提供的相關性追蹤器 Python 介面，使用者畫一次方框後可逐影格回報目標位置。
- **Bounding box**：使用者在第一影格框出 pillar 頭部的矩形，作為追蹤器的初始樣板。
- **Adaptive correlation filter**：Bolme et al. CVPR 2010 的自適應相關濾波器：以最小平方法即時更新濾波器，適應目標外觀變化。
- **HOG features**：方向梯度直方圖，把影像區域內邊緣方向與強度整理成紋理指紋，對亮度與小幅形變不敏感。
- **Cosine correlation**：把兩條向量歸一化後求內積 (= 夾角餘弦)，只看方向不在意絕對強度，相似度衡量穩健。
- **Least squares update**：每張影格追完後用最小平方法微調濾波器參數，把新樣貌納入參考樣板。
- **Force–displacement coefficient k**：Microtester 量測得到的線性彈性係數，F = k·Δx；與本平台 pillar 通用、無 hysteresis。
- **Active force (mN/mm²)**：肌條收縮時兩根 pillar 位移 × k ÷ 橫截面積得到的主動收縮應力。
- **Passive tension (mN/mm²)**：肌條於靜息時對 pillar 的恆定拉力，反映 hydrogel + 細胞被動硬度。
- **20 fps × 4800 frames recording**：與 ET/MCR/FFR 自動刺激程式同步的錄影參數，提供約 240 秒長片段給追蹤器。

# 與此篇文章的關係
在《milliPillar: A Platform for the Generation and Real-Time Assessment of Human Engineered Cardiac Tissues》這篇文章中，作者為了讓任何實驗室都能用一般倒立顯微鏡量到「絕對」收縮力，採用 dlib correlation tracker 自動追蹤亮場影片中兩根 pillar 頭部位移。它解決了既有平台只能輸出「相對」位移、難以跨研究比較的瓶頸；以 Microtester 量到的線性係數 k (見 module 11) 為輸入，產出 mN/mm² 主動收縮力與被動張力，餵給下游 ET/MCR/FFR/PRP 統計分析。
