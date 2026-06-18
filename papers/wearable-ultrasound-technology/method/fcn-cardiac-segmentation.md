# B-mode 卡心臟分割與功能量化 (FCN-32 fully convolutional network)

1. 引用自哪篇 paper: wearable-ultrasound-technology
2. Outline (任務主線): B-mode 卡心臟分割與功能量化 (FCN-32 fully convolutional network)
3. Method: 
   穿戴心臟貼片 24 小時連續錄下一張張 B-mode 心臟切面，每張裡左心室那個袋狀腔室藏在心肌中間。「自動分割」就是讓電腦逐張影像、把每個像素都標上「這個點屬於左心室腔內」或「不屬於」——輸出是一張同尺寸的黑白遮罩 (mask)，白色代表左心室、黑色代表其他組織。有了每張遮罩的面積、配合幾何模型，就能估算左心室在那一刻的容積。把整段監測串起來會得到一條隨時間起伏的「容積曲線」：心臟舒張到最大稱為 end-diastolic volume (EDV)、收縮到最小為 end-systolic volume (ESV)。從這條曲線可以一次算出四個臨床數字：心臟每跳一次擠出的血量 stroke volume = EDV − ESV、每分鐘總輸出 cardiac output = stroke volume × 心率、射血分率 ejection fraction = (EDV − ESV) / EDV——這三個是評估心衰竭的核心指標。
   為什麼要選全卷積神經網路 (fully convolutional network, FCN-32)？關鍵在「分割」這個任務的特殊性。一般用來分類圖片的 CNN 最後幾層是「全連接層」，會把整張影像壓縮成一個分類結果（例如「這張裡有左心室」），但沒辦法告訴你左心室在哪、邊界長什麼樣——空間位置資訊全被丟掉。FCN 把那幾層全連接層也換成卷積層，整個網路從頭到尾都用卷積，輸出可以是和輸入同尺寸的像素分類圖。FCN-32 的「32」指最深層特徵圖比輸入小 32 倍，再透過 upsampling 放大回原尺寸——是 FCN 家族裡最早、最直接的版本，計算量小、適合穿戴端有限的算力。Hu et al. 2023 心臟貼片就是用 FCN-32 做即時 LV 分割。
   為什麼穿戴心臟貼片非用自動分割不可？因為 24 小時連續錄影每小時就生出幾萬張 B-mode 切面，靠人盯著一張張描左心室邊界根本不可能；而且穿戴的核心承諾就是「不需要專業 sonographer 介入」，否則等於失去穿戴意義。但目前 FCN-32 的弱點也很明顯：它是用一群人標好的 B-mode 影像訓練的，泛化範圍還受限。一旦換到分布外的新使用者——心臟形狀偏離訓練樣本、貼片角度偏一點、皮下脂肪厚度不同——模型可能把左心室描歪、把心肌也標進腔內，或漏標一塊，後續算出來的 EDV、ESV、ejection fraction 全部失真，對心衰竭量化會直接誤導治療決策。論文因此提出兩條擴展方向：few-shot learning 讓模型用少量新使用者標註就能適應、reinforcement learning 讓模型根據量測結果回饋自我修正，把自動化從「同分布內可用」推向「跨個體可用」。
4. 工具與材料: 
   - **FCN-32 (fully convolutional network)**: 把分類 CNN 的全連接層全部換成卷積層，輸出像素級分類遮罩；32 指最深層下採樣比。
   - **影像分割 (image segmentation)**: 把每個像素標上「屬於某類組織/不屬於」的像素級分類任務。
   - **Left ventricle (左心室)**: 心臟內主要把血擠到全身的腔室；自動分割的目標。
   - **End-diastolic volume (EDV) / End-systolic volume (ESV)**: 左心室舒張到最大、收縮到最小時的容積。
   - **Stroke volume / Cardiac output / Ejection fraction**: 從 EDV、ESV、心率算出的三個臨床心臟功能指標，用來評估心衰竭。
   - **Few-shot learning**: 用少量新使用者標註讓模型快速適應的學習策略，解決分布外泛化問題。
   - **Reinforcement learning**: 讓模型根據量測結果回饋自我修正的學習策略。
5. 與此篇文章的關係: 
   在《Wearable ultrasound technology》這篇文章中，作者為了讓心臟貼片連續錄下的 B-mode 影像能直接產出臨床心臟功能指標，採用了全卷積神經網路 (FCN-32) 自動分割左心室。這套方案解決了 24 小時錄影產生數萬張切面、無法靠 sonographer 人工判讀的瓶頸；它吃進連續 B-mode 影像、產出左心室遮罩，再由幾何公式換算 stroke volume / cardiac output / ejection fraction，直接交給臨床做心衰竭評估。