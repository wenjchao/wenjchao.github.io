# Beamforming 與 B-mode 影像重建演算法

1. 引用自哪篇 paper: wearable-ultrasound-technology
2. Outline (任務主線): Beamforming 與 B-mode 影像重建演算法
3. Method: 
   想像 array 上每顆 element 都單獨噴出一圈圈聲波。若它們同時噴，波會像石頭丟進水池形成的同心圓向四面散去；但只要稍微錯開每顆的觸發時間，這些同心圓在某個方向、某個深度疊在一起時就會強強相加，其他方向則互相抵消——靠這套『誰先誰後起立』的時序密碼 (beamforming) 就能不轉動探頭，把聲波束朝指定角度發射並聚焦到指定深度。每顆 element 收到的射頻訊號 (radiofrequency signal, RF) 是一條『時間-振幅』曲線；聲波速度大致固定，所以時間可以換算成深度。當 beamforming 把波束朝不同方向發射、各方向各得到一條深度線，把這些線並排起來就形成 2D 切面影像 (B-mode)；更多角度都掃過就成了 3D 體積影像。
   Plane wave、mono-focusing、wide-beam compounding 三種策略各自在『frame rate、解析度、FOV』三選一裡做取捨。Plane wave 是全 array 同步發射一張寬寬的大平面波，一次掃到一大片，frame rate 很高，但因為沒聚焦所以畫面比較糊。Mono-focusing 是把所有 element 的時序錯開讓波在某個深度疊出焦點，焦點處非常清楚，但離開焦點深度就糊掉。Wide-beam compounding 則是發散的波從很多不同角度連續打、把多張影像疊在一起，FOV 大、品質高，但要等多次發射、frame rate 低，運動時容易出 artefact——代表案例是 Hu et al. *Nature* 2023 (ref. 63) 用 wide-beam compounding 做高品質 cardiac B-mode。策略要按目標器官的運動速度挑：心跳這種快速動態應用建議用 plane wave 換 frame rate，膀胱容積這種幾乎不動的場景可以放心用 wide-beam compounding 換高品質。
   Beamforming 的時序計算基於『每顆 element 在設計位置上』這個假設。但 flexible / stretchable array 貼到頸動脈或胸口曲面時，element 之間真實間距會略偏離原設計，每顆到同一個回波點的距離也跟著變——本來該疊在一起的波疊不準，這就是相位畸變 (phase aberration)；頻率越高、波長越短，一點點位置偏差佔波長的比例越大，影像因此更糊。文獻整理出兩條補償路：硬體派把元件位置『量出來』，用 3D 相機 (ref. 63)、應變感測器 (ref. 36) 或光纖 (ref. 216) 即時告訴電腦每顆 element 跑到哪裡，再回頭修正 beamforming 用的延遲值；軟體派則用『影像品質代價函數』反推延遲——把延遲值當未知數，迭代調整到影像最有秩序（最小化 entropy；ref. 217）、相位最一致（最小化 phase error；ref. 218）、斑點最穩（speckle brightness 變異最小；refs 219, 221）、或 element 間訊號最同調（最大化 coherence factor；ref. 220）。兩條路各有缺點：硬體加裝 sensor 增加貼片厚度，軟體迭代計算開銷大且容易卡 local minimum，所以實務上常並行用，硬體給粗修、軟體做細調。
4. 工具與材料: 
   - **beamforming**: 靠錯開各 element 的發射時序與振幅，利用聲波建設性／破壞性干涉把波束朝指定方向、聚焦指定深度。
   - **radiofrequency signal (RF)**: 每顆 element 收到的時間-振幅曲線；聲速固定，時間軸即可換算成深度。
   - **plane wave**: 全 array 同步發射一張大平面波，一次掃寬幅但無聚焦，frame rate 高、解析度低。
   - **mono-focusing**: 錯開時序讓波在某深度疊出焦點，焦點處解析度高、離焦處模糊。
   - **wide-beam compounding**: 多角度發散波連續打再疊加，FOV 大、品質高但 frame rate 低，運動易有 artefact (Hu et al. *Nature* 2023, ref. 63)。
   - **phase aberration**: Flexible / stretchable array 因 element 真實位置偏離設計值，導致波到達時間不一致、影像散焦；高頻更明顯。
   - **硬體位置量測 (3D camera / strain sensor / optical fibre)**: 用額外感測器即時量 element 真實座標，再回頭修正 beamforming 延遲值 (refs 63, 36, 216)。
   - **迭代代價函數 (entropy / phase error / speckle brightness / coherence factor)**: 軟體派用影像品質指標當代價函數，迭代搜尋延遲值，分別對應影像亂度、相位一致性、斑點變異與訊號同調性 (refs 217–221)。
5. 與此篇文章的關係: 
   在《Wearable ultrasound technology》這篇 Review 中，作者為了讓 wearable B-mode 在動態皮膚表面仍能成像，介紹了 beamforming 策略與 phase aberration 補償。它吃 array 各 element 的射頻訊號進來，依應用情境挑選 plane wave / mono-focusing / wide-beam compounding，再透過硬體位置量測或軟體迭代補償彎曲拉伸造成的相位錯位，輸出可用的 2D / 3D 解剖影像給下游的 FCN-32 分割或 elastography 分析。