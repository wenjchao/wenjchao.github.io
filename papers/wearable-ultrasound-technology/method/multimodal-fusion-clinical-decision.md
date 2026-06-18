# Multimodal Fusion 與臨床決策模型

1. 引用自哪篇 paper: wearable-ultrasound-technology
2. Outline (任務主線): Multimodal Fusion 與臨床決策模型
3. Method: 
   穿戴貼片只看超音波會錯過很多訊號：心律亂跳要看心臟電訊號圖 (electrocardiogram, ECG)、運動下代謝壓力要看汗水或組織液裡的乳酸（量汗液 / 組織液裡離子或代謝物的小型電極，electrochemical sensor 才看得到）、子宮收縮強度要看量子宮收縮的腹部感壓器 (tocodynamometer)、乳房腫塊要搭 X 光乳房攝影 (mammogram)。作者把這些感測器整合到同一片貼片或同一個 pipeline 裡同步取樣，再讓深度學習模型同時看。問題是 ECG 是電壓時序、ultrasound 是影像或波形、electrochemical sensor 是化學濃度數值，格式完全不同。卷積神經網路 (convolutional neural network, CNN) 把每個模態先用自己的編碼層轉成同一種「特徵向量」、再串在一起餵下游分類層；整個流程從原始訊號到疾病標籤一氣呵成 (end-to-end deep learning)，模型自動學到「ECG 出現 X 樣式 + ultrasound 出現 Y 樣式 → 屬於 Z 疾病」這種跨模式的共同特徵 (cross-modal feature extraction)。
   Review 列了四個具體案例。第一，把 ECG 與心臟超音波一起餵深度學習模型，心肌過度肥厚的遺傳性心臟病 (hypertrophic cardiomyopathy, HCM) 檢測 precision 比純超音波模型提升 33% (ref. 161)——理由是 HCM 在超音波上會看到左心室壁變厚，但高血壓、運動員心臟也會壁厚，光靠超音波分不清；加入 ECG 上特定的 Q 波與左心室高電壓特徵，CNN 用「電 + 形狀」聯合特徵把 HCM 從其他壁厚原因切出來。第二，把超音波量到的胎兒心率與感壓器量到的子宮收縮一起餵 CNN，把胎兒健康評估時間從醫師讀好幾小時縮成模型秒讀 (ref. 162)。第三，X 光 mammogram 與超音波影像用 ML 融合，降低放射科醫師判讀乳癌的人為錯誤率 (ref. 163)。第四，Sempionatto et al. Nat. Biomed. Eng. 2021 (ref. 91) 把超音波與化學感測器做在同一片貼片上：超音波量血管直徑換算血壓、化學電極量汗液乳酸，模型看到「血壓飆高 + 乳酸也飆高」判定運動壓力過大、「血壓飆高但乳酸還低」則判定尚在安全運動區，跳出對應建議 (Fig. 4m)。
   為什麼 CNN 可以自動抽跨模特徵？因為 CNN 的核心是一堆小型卷積核 (convolution kernel) 在輸入上滑動，學會「這小塊長這樣 → 對應某種局部特徵」。對 ECG 學到「QRS 波形」「ST 段抬高」、對 ultrasound 影像學到「左心室壁變厚」、對化學感測器學到「乳酸上升斜率」。每個模態各自訓練出自己的特徵抽取層後再串起來餵共同分類層，整個訓練自動調整 kernel 與權重去最大化分類目標，不需要醫師預先告訴模型哪些特徵重要。為什麼非得「在同一貼片同步取樣」？因為兩條訊號要被 CNN 學到共同特徵，必須對齊到同一時間點——血壓在第 3.2 秒飆起來、乳酸也在第 3.2 秒升起來，模型才連得起來。分用兩個獨立裝置事後對齊會有秒級誤差，運動下生理訊號秒級波動就足以讓「同步」變「錯位」。同一貼片同時走同一個 ASIC 與時鐘，從硬體層就保證對齊。
   Multimodal fusion 仍有兩個常見壞點。第一，如果只靠單模就會出歧義——例如超音波讀到胎兒心率忽然變慢，可能是真的胎兒缺氧、也可能只是子宮收縮把臍帶壓住的短暫變化；少了 tocodynamometer 那條訊號，要嘛漏掉真正缺氧、要嘛把生理變化誤判成異常。第二，深度學習模型只會它訓練時看過的共同模式，換到新個體（老人、孕婦、皮下脂肪較厚的人）ECG 基線與 ultrasound 紋理都不同，模型可能把正常判成 HCM 或反過來——這就是模型在新個體仍能準的能力 (generalizability) 不足。作者特別點名這是多模 wearable 還沒解決的核心挑戰，要靠跨中心、大族群、多重感測設定的資料一起訓練才能緩解。
4. 工具與材料: 
   - **Electrocardiogram (ECG)**: 貼在皮膚上量心臟電訊號的時序波形，提供心律、QRS、ST 等電學特徵。
   - **Electrochemical sensor**: 量汗液 / 組織液裡離子或代謝物濃度的小型電極，用於補捉乳酸、葡萄糖等代謝訊號。
   - **Tocodynamometer**: 貼在孕婦腹部的感壓器，量子宮收縮強度的時序波形。
   - **Mammogram**: 乳房 X 光影像，臨床乳癌篩檢的標準工具。
   - **Convolutional neural network (CNN)**: 用小型卷積核在輸入上滑動學局部特徵的深度模型，適合處理影像、時序、多模融合。
   - **End-to-end deep learning**: 從原始訊號到最終標籤一氣呵成的訓練流程，免去人工特徵抽取。
   - **Cross-modal feature extraction**: 模型自動學到「不同模態同時出現某組合 → 對應某疾病」的聯合特徵。
   - **Hypertrophic cardiomyopathy (HCM)**: 心肌過度肥厚的遺傳性心臟病，超音波單看壁厚難與高血壓 / 運動員心臟區分，需 ECG 互補。
   - **Generalizability**: 模型在訓練人群以外的新個體仍能維持準度的能力，是多模 wearable 仍未解決的核心挑戰。
5. 與此篇文章的關係: 
   在《Wearable ultrasound technology》這篇 Review 中，作者要解決穿戴貼片在複雜病程（如 hypertrophic cardiomyopathy、胎兒監測）下單一模態判讀準度不足的問題。Multimodal fusion 把 ultrasound 訊號與 ECG、tocodynamometer、mammogram、electrochemical sensor 等異質感測器在同一貼片同步取樣，再以 CNN 端對端融合，提供下游臨床決策更可靠的疾病標籤，並支撐 multimodal sensing 章節列出的多項實例（HCM 提升 33% precision、胎兒健康秒讀、乳癌錯誤率下降、運動壓力即時建議）。