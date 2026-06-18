# Doppler 訊號處理與自動 envelope tracing

1. 引用自哪篇 paper: wearable-ultrasound-technology
2. Outline (任務主線): Doppler 訊號處理與自動 envelope tracing
3. Method: 
   貼片發出一束已知頻率的聲波打進血管，紅血球反射的聲波再回到貼片。紅血球朝貼片跑來，回波會被壓縮變成稍高的頻率；遠離則被拉長變稍低——就像救護車鳴笛經過你身邊那種音調變化 (Doppler shift)。電路比對發射波與回波之間的時序錯位 (相位差 phase difference)：相位向前挪表示朝貼片移動、向後挪表示遠離，挪得越多速度越快，從中反推紅血球當下的速度與方向。一束聲波怎麼進出血管，又分兩種模式：持續發聲、持續收音 (continuous-wave Doppler) 用兩顆元件、一顆送一顆收，整條聲束路徑上的血流通通混在一起算，速度準但「在哪個深度流的」分不出來；一發一收的脈衝式 (pulsed-wave Doppler) 則靠來回時間 (time of flight) 鎖定深度，代價是訊號處理複雜很多。拿到了「某深度紅血球當下的速度」之後，作者整理出三種看法。spectral Doppler 把血流速度沿時間軸畫成一條曲線 (spectrogram)，看得到收縮期高峰與舒張期低谷；曲線外緣最高點就是收縮期最高血流速度 (peak systolic velocity)，外緣在下次收縮前的低點就是舒張末期血流速度 (end diastolic velocity)，兩者是臨床判讀的核心指標。colour Doppler 算多次脈衝—回波的平均相位差，把朝貼片來的塗紅、遠離的塗藍，疊在 B-mode 灰階圖上看血流方向。power Doppler 把多次脈衝—回波的訊號功率加總，反映「有多少紅血球在動」，對微小血流特別靈敏但看不出方向。
   貼片要把 spectral Doppler 做成連續監測有兩個技術前提。一是高階顯示卡 (graphics processing unit, GPU)：每秒要處理上千條原始聲波訊號 (radiofrequency signal) 才能做出夠細的速度曲線，還要同時跑 B-mode 灰階影像確認貼片有沒有跑位，傳統 CPU 序列算根本來不及；GPU 擅長一次平行處理上千條同類運算，正好對到這個需求 (Chang et al. IEEE TUFFC 2009, ref. 105)。二是自動描出血流波形外緣 (automated envelope tracing)：穿戴貼片本來就要 24 小時持續抓 peak systolic velocity 與 end diastolic velocity，如果還得靠技師對著螢幕描曲線，這個模式根本不成立；演算法直接把外緣框出來、把兩個臨床指標報出來，貼片才能脫離操作員 (Zhou et al. Nature 2024, ref. 72; Fig. 3e)。
   Doppler 訊號處理有兩個常見壞點。第一，血流並不是體內唯一在動的東西——肌肉、血管壁、皮下脂肪在呼吸與心跳下都在低速來回擺動 (tissue motion)，這些訊號會與血流訊號疊在同一條曲線上，把舒張末期那段本來該很平的部分污染成假高峰，臨床指標讀錯、連續趨勢全偏掉，所以 GPU 要邊量邊濾、後段也要再用 clutter filter 把組織擾動切掉。第二，continuous-wave Doppler 沒有深度解析，脖子裡頸動脈、頸靜脈、表淺小血管的訊號會全部混疊在同一條曲線上，根本切不出單一血管，需要鎖定特定深度時必須改用 pulsed-wave。
4. 工具與材料: 
   - **Doppler shift**: 紅血球朝貼片來時回波頻率被壓縮變高、遠離則被拉長變低，類似救護車經過時的音調變化。
   - **Phase difference**: 發射波與回波在時間軸上的錯位量；錯位多寡與紅血球速度呈線性關係，用於反推血流速度與方向。
   - **Continuous-wave Doppler**: 兩顆元件、一顆送一顆收，整條聲束路徑上的血流混在一起算速度，準但無深度解析。
   - **Pulsed-wave Doppler**: 一發一收的脈衝模式，靠來回時間 (time of flight) 鎖定深度，能單獨量某層血管的血流。
   - **Spectral Doppler**: 把血流速度沿時間畫成曲線 (spectrogram)，顯示收縮期高峰與舒張期低谷。
   - **Colour Doppler**: 算多次脈衝—回波的平均相位差，把方向以紅藍著色疊在 B-mode 灰階圖上。
   - **Power Doppler**: 把多次脈衝—回波的訊號功率加總，反映在動的紅血球數量，對微小血流靈敏但看不出方向。
   - **Graphics processing unit (GPU)**: 高階顯示卡，能平行處理上千條 radiofrequency signal 同時跑 imaging + spectral Doppler 並即時抑制 tissue motion 干擾。
   - **Automated envelope tracing**: 演算法自動描出 Doppler 波形外緣，直接吐出 peak systolic velocity 與 end diastolic velocity，省去人工描曲線。
   - **Peak systolic velocity**: Doppler 曲線外緣最高點，對應心臟收縮把血擠出來時的最快血流速度。
   - **End diastolic velocity**: Doppler 曲線外緣在下次收縮前的低點，對應心臟休息時的殘餘血流速度。
   - **Tissue motion**: 肌肉、血管壁、皮下脂肪受呼吸心跳低速擺動產生的訊號，會疊在 Doppler 曲線上需要被濾掉。
5. 與此篇文章的關係: 
   在《Wearable ultrasound technology》這篇 Review 中，作者整理穿戴貼片如何把連續、無操作員的血流監測搬出醫院。Doppler 訊號處理與自動 envelope tracing 把貼片收到的 radiofrequency signal 變成可即時讀出的 peak systolic 與 end diastolic velocity，解決傳統做法需要技師對著螢幕描曲線、無法 24 小時連續監測的瓶頸。它接著被血壓量化、頸動脈與胎兒監測等下游模塊直接拿來當血流讀數來源。