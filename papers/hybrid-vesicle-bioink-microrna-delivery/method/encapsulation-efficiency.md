# miRNA Encapsulation Efficiency 公式

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): miRNA Encapsulation Efficiency 公式
3. Method: 
   封裝效率 (encapsulation efficiency, EE) 要回答的是「真的進到囊泡裡的 miRNA 占總投入的百分比」。直覺做法是把囊泡打破、直接量裡面的 miRNA，但 miRNA 是一段很短的單股 RNA，只要露在水溶液中就會被殘留的 RNase 切斷或被破囊的機械剪切弄碎，測到的數字會比真實值偏低。作者改採扣除法：先量總共投入多少 miRNA、再量沒被包進去而漂在外面的游離 miRNA，相減就是「成功進到囊泡裡的量」。為了把游離 miRNA 單獨抓出來，作者用兩道分離：先用孔徑很小的離心過濾管 (Amicon Ultra 10 kDa MWCO) 讓 miRNA 通過、囊泡卡在膜上方；再用 100 000 × g、70 分鐘的超高速離心把含囊泡的部分沉到管底，剩下的上清液就是純游離 miRNA。

   怎麼把上清液裡的游離 miRNA 變成可比的數字？作者選了帶橘紅色螢光標記的 miRNA-DY547 當示蹤分子，先用一系列已知濃度的純 miRNA-DY547 溶液在激發 525 nm／發射 570 nm 下量螢光強度，畫出「濃度 vs 螢光強度」的標準曲線；之後把樣品的螢光強度丟進這條曲線就能反推出濃度。比起無標記版本需要走 RT-qPCR 只能算相對量，DY547 的強度與濃度呈線性，可以直接讀出絕對 µg 數。最後套進公式 $\mathrm{EE}\,(\%) = \left(1 - \dfrac{\text{free miRNA}}{\text{loaded miRNA}}\right) \times 100$——loaded 是當初投入的總量、free 是上清液算出的游離量。實測：Lip 63% ± 2.21%、hELs 65% ± 2.18%、EVs 76% ± 3.12%。

   EE 數字背後其實藏著一條因果鏈。miRNA 因為磷酸骨架帶負電，如果囊泡表面也是強負電（zeta potential 很負），兩個負電互推、miRNA 就不容易留在囊泡裡。實測完全符合這個趨勢：Lip 表面最負 (−35.67 mV) → EE 最低 (63%)；EVs 接近中性 (−5.6 mV) → EE 最高 (76%)；hELs 介於兩者中間 (−12.3 mV) → EE 65%。把 EE 跟 zeta potential 並排看，就證明 EE 差異不是隨機，而是被表面靜電直接決定的。

   這套扣除法的準確度完全綁在分離步驟上。第一個失敗點：超高速離心如果離心力不夠或時間太短，部分囊泡會還浮在上清，上清測到的螢光就會把「囊泡內 miRNA」也算成「游離」，free 被高估、EE 被低估。第二個失敗點：Amicon 過濾管的孔徑若挑太大，囊泡本身會漏進濾液，free 與 loaded 兩端都被污染、整個比值失去意義。第三個失敗點：螢光標準曲線只在某段濃度區間呈線性，樣品讀值若高到偵測器飽和或低到被儀器背景噪音蓋過，反推回來的濃度都會失真，實務上必須稀釋讓樣品落在曲線中段。
4. 工具與材料: 
   - **Encapsulation efficiency (EE)**: 「真的進到囊泡裡的 miRNA 占總投入的百分比」，以 $(1 - \text{free}/\text{loaded}) \times 100$ 算出。
   - **miRNA-DY547**: 帶橘紅色螢光標記的 miRNA mimic，做為可在 Ex/Em 525/570 nm 直接定量的示蹤分子。
   - **Amicon Ultra 10 kDa MWCO**: 孔徑很小的離心過濾管，讓游離 miRNA 通過、把囊泡卡在膜上方。
   - **100 000 × g 超高速離心 (70 min)**: 把含囊泡的下半部沉到管底，上清液留下純游離 miRNA。
   - **螢光標準曲線**: 以已知濃度的純 miRNA-DY547 建立的「濃度 vs 螢光強度」線性對應，把樣品的螢光值反推為絕對濃度。
   - **Zeta potential**: 囊泡表面的靜電勢，越負代表靜電排斥力越強；本研究中 zeta 越負、EE 越低。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了比較 Lip、EVs、hELs 三種奈米囊泡裝載 miRNA 的能力，採用了「螢光標記扣除法」量化封裝效率 (EE)。這套方法避開了「破囊直接定量」會造成的 RNA 降解低估，吃進「投入量 + 上清液游離量」兩個讀數、產出三組 EE 百分比 (63% / 65% / 76%)，為下游「為什麼 hELs 仍能有效裝載 miRNA」的論證與 zeta potential 對照分析提供量化依據。
