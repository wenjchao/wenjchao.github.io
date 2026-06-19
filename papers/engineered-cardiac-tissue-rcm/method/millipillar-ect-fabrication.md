# milliPillar 工程化心臟組織 (ECT) 製作

1. 引用自哪篇 paper: engineered-cardiac-tissue-rcm
2. Outline (任務主線): milliPillar 工程化心臟組織 (ECT) 製作
3. Method: 

milliPillar 是 Tamargo, Nash 等人 2021 年發表在 ACS Biomater. Sci. Eng. 的小型化 ECT 平台。作者先用 PDMS / Sylgard 184 (Dow #1024001) 這種透明矽膠倒入含電極的客製金屬模具中，固化後就有一個「中間有小水池、水池底部豎著兩根矽膠柱」的反應器，每個反應器含 6 條組織。每條組織用 500,000 顆細胞，其中 75% 是 iPSC-CM、25% 是人原代心臟纖維母細胞 (Lonza CC-2904，事先以 Fibroblast Growth Medium 3 預擴增)——為什麼要混纖維母細胞？因為真實心臟裡纖維母細胞會分泌 collagen 等細胞外基質把心肌互相連起來，純 iPSC-CM 凝膠會鬆散塌掉拉力傳不出去。細胞懸浮在 5 mg/mL Fibrinogen (Sigma F3879) 溶液裡，每孔注入 12 µL 細胞懸液 + 3 µL 12.5 U/mL Thrombin (Sigma T6884)。Thrombin 把 Fibrinogen 剪切聚合成纖維蛋白網，把細胞包進一坨果凍裡；這團果凍會主動收縮、緊緊夾住兩根 PDMS 柱，最後形成一條兩端錨在柱頭的會跳動的 3D 心肌小肉條。每跳一下就把柱頭往內拉一點，攝影機拍到的柱頭位移就是力學讀數的來源。

為什麼柱頭位移可以換算成力？兩根 PDMS 柱可以想像成兩根插在地上的彈簧棒，每跳一下心肌組織把柱頭往內拉、柱子彎一個角度；放鬆時柱子又彈回去。對彈性棒來說位移和拉它的力成正比，比例係數就是柱子的剛度。作者事先用 Microtester MT-LT (CellScale) 這台微力學測試儀去推柱頭、量「推多少力得到多少位移」，建立一條 displacement→force 對照曲線。實驗時只要從影片量到柱頭位移，乘以這條曲線的斜率就是當下心肌組織施加的力，這套標定流程沿用 Tamargo 2021。

Day 7 起作者同時切到 AlbuMAX 高脂培養基並啟動電刺激 ramp，這兩件事是必要的成熟化步驟。剛分化出來的 iPSC-CM 在代謝與電生理上仍接近胎兒期——主要靠糖酵解、肌節短而亂、跳動慢；成人心肌則靠脂肪酸氧化、肌節整齊、跟著穩定節律跳。代謝端 Day 7 起切到 RPMI + AlbuMAX (ThermoFisher 11020021)、高鈣低糖——AlbuMAX 是富含脂肪酸的純化白蛋白溶液，把細胞燃料從糖換成脂肪酸，逼它啟動 fatty acid oxidation（依 Feyen et al. Cell Rep 2020）。電機械端 Day 7 起 2 週 ramp，由 2 Hz 每 24 h 提升 0.33 Hz 直到 6 Hz，再恆定 1 Hz pacing；這個漸進加速模擬出生後心率上升的訓練過程，逼心肌學會以較高頻率穩定收縮。整體培養 4 週後，FLNC^ΔGAA^ vs FLNC^ψWT^ 的舒張差異才會放大顯現——沒有這一步，3D 模型可能對 RCM 視而不見。

前 3 天為什麼一定要加 5 mg/mL 6-aminocaproic acid？纖維蛋白凝膠才剛凝好就要面對細胞自己的「拆遷大隊」——iPSC-CM 與纖維母細胞會分泌 plasmin 等纖維蛋白溶解酶，本來功能是清理血凝塊，但在這裡會把作者剛做好的凝膠迅速溶解掉、組織塌陷脫柱。為了給細胞時間自己分泌 ECM 接管結構，前 3 天 B27 培養基裡加 5 mg/mL 6-aminocaproic acid (Sigma A7824)——它是 plasminogen 活化的競爭性抑制劑，等於暫時把拆遷大隊鎖在門外。3 天後細胞已經分泌足夠 collagen 等內生 ECM 自己撐住組織，6-aminocaproic acid 就可以撤掉。若忘記加，整批組織會在 24–48 h 內全部溶散，那一個月的細胞與 PDMS 反應器全部報廢。

4. 工具與材料: 
- **milliPillar 平台**: Tamargo, Nash et al. 2021 提出的小型化 ECT 平台，每反應器 6 條組織。
- **PDMS / Sylgard 184**: Dow #1024001 透明矽膠，倒模成含電極的反應器與柱子；柱子彎曲量即力學讀數。
- **Fibrinogen + Thrombin**: 5 mg/mL Fibrinogen + 12.5 U/mL Thrombin，Thrombin 剪切 Fibrinogen 聚合成纖維蛋白網包裹細胞。
- **心肌纖維母細胞比 (75/25)**: 75% iPSC-CM + 25% Lonza CC-2904 原代心臟纖維母細胞，模擬真實心臟組織比例提供 ECM 支撐。
- **6-aminocaproic acid**: Sigma A7824，5 mg/mL 加入前 3 天培養基，阻斷 plasmin 防止纖維蛋白凝膠被細胞溶掉。
- **AlbuMAX**: ThermoFisher 11020021，富含脂肪酸的白蛋白溶液，驅動 iPSC-CM fatty acid oxidation 代謝成熟。
- **電刺激 2→6 Hz ramp + 1 Hz pacing**: Day 7 起 2 週逐步提升頻率，再恆定 1 Hz；模擬出生後心率上升訓練 iPSC-CM 成熟。
- **Microtester MT-LT**: CellScale 的微力學測試儀，預先建立 PDMS 柱的 displacement→force 換算曲線。
- **active force / passive tension / relaxation velocity**: 從柱頭位移取得的 RCM 臨床相關力學讀值：主動收縮力、被動殘留張力、舒張速度。

5. 與此篇文章的關係: 
在《Engineered cardiac tissue model of restrictive cardiomyopathy for drug discovery》這篇文章中，作者為了直接量測 RCM 的核心臨床缺陷「被動張力上升、舒張速度變慢」，採用了 milliPillar 工程化心臟組織平台。它解決了「2D 平面培養根本量不到主動力與被動張力，而傳統大 EHT 通量太低」的瓶頸，把 iPSC-CM + 纖維母細胞的 3D 凝膠懸吊於兩根可量化的 PDMS 柱間，產出供下游藥物急性救援、結構免疫螢光與 sarcomere 量化使用的力學可讀組織。
