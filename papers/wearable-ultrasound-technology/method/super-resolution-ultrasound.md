# 超解析超音波 (Localization Microscopy + Structured Illumination)

1. 引用自哪篇 paper: wearable-ultrasound-technology
2. Outline (任務主線): 超解析超音波 (Localization Microscopy + Structured Illumination)
3. Method: 
   任何波（光波、聲波）能解析的最小細節大約等於波長的一半左右——這就是波長對應的最小可解析尺寸 (diffraction limit)。穿戴超音波貼片常用 ~3 MHz、波長約 0.5 mm，比這更細的微血管全部糊在一起。提高頻率縮短波長會讓聲波穿不深，不適合穿戴；所以作者轉用兩種「軟體繞過」的超解析路線。第一條是一顆一顆定位再累積 (ultrasound localization microscopy, ULM)。流程是：注入微小氣泡顯影劑 (microbubble contrast agent)——直徑只有幾微米、會在超音波下強烈反射；控制濃度低到「同一張影像裡每顆氣泡都隔得開」；雖然每顆氣泡都被 diffraction limit 模糊成 ~0.5 mm 的光斑，但這個光斑的中心位置可以用 sub-wavelength 精度算出來；用高速整片掃描 (ultrafast imaging) 每秒拍上千張、追蹤氣泡隨血流移動、記下幾十萬個中心位置；最後把所有位置疊成一張點陣圖，自然顯現出比波長還細的血管走向 (Errico et al. Nature 2015, ref. 224)。
   第二條路是 structured illumination。原理借自莫爾紋：把兩張一格一格的條紋透明片疊在一起、輕輕轉一個角度，會看到一片明暗交錯的大條紋——兩個高頻條紋互相干涉產生一個比兩者都低頻的合成條紋 (moiré fringes)。超音波貼片發出一張規律條紋光罩 (periodic multifocal pattern) 打進組織，這張條紋與組織本身的微細結構互相干涉、產生 moiré fringes。組織的高頻細節雖然超過 diffraction limit、超音波本來看不到，但被 moiré fringes 編碼成低頻訊號 (frequency down-mixing) 後就能被偵測。再把條紋平移幾次、各拍一張、用演算法把這幾張同時解出來，就把組織的高頻細節還原成一張單一的高解析影像 (refs 225, 226, 227)。
   為什麼模糊光斑的中心仍能用 sub-wavelength 精度找到？因為 diffraction limit 限制的是「能不能分辨兩個相鄰光斑」，不是「單一光斑中心在哪」。只要視野裡同一個 diffraction limit 範圍內只有一顆氣泡，那團模糊光斑的能量分布幾乎是對稱的，演算法可以擬合一個高斯函數把中心算到 1/10 波長以下。這就是為什麼非要把微泡稀釋到能個別解析的濃度 (low microbubble concentration)——兩顆氣泡靠太近、能量分布變雙峰、中心就算不準了；低濃度保證 spatial separability，代價是每張只能累積很少乾淨定位點，要靠 ultrafast imaging 大量連拍把總定位點堆上去 (acquisition time 通常幾分鐘到幾十分鐘)，這是精度 vs 速度的根本取捨。為什麼這兩條路線特別適合 wearable？因為傳統「換高頻探頭」會讓聲波穿不深、wearable form factor 也撐不起更密元件陣列；ULM 與 structured illumination 都把超解析推到軟體與發射策略——ULM 用原有陣列做 ultrafast imaging 加注射微泡，structured illumination 只改變發射時序與相位讓元件組成 periodic multifocal pattern——所以對 wearable 來說特別合理 (paragraph 117)。
   這兩條路線各自有典型壞法。ULM 怕兩件事：第一，微泡濃度沒壓好，同一視野裡多顆氣泡擠在 diffraction limit 內，中心擬合算出的「中心」落在兩顆氣泡中間，畫出的點陣圖會充滿假位置、血管走向變亂麻；第二，acquisition time 不夠，每個血管段需要被氣泡走過足夠多次才能被「畫」出來，累積定位點數不夠的話血管圖只剩稀疏的點集、看不出連續血管網。這也是 ULM 在 wearable 最難的地方——使用者不見得能乖乖坐 30 分鐘。Structured illumination 在 wearable 上的特殊壞點是條紋對齊：它需要每張條紋平移幾微米精準累積，但 wearable 貼片會跟著皮膚一起變形伸縮，條紋之間相對位置一漂移，moiré fringes 解出的「高頻細節」會變成假紋路；實務上需要 ultrafast imaging 同時偵測元件位置補正、或限定使用者短時間靜止量測。
4. 工具與材料: 
   - **Diffraction limit**: 波對應的最小可解析尺寸，約為波長的一半，是傳統超音波解析的物理底線。
   - **Sub-wavelength resolution**: 比波長還細的影像細節，超解析方法的最終目標。
   - **Microbubble contrast agent**: 直徑幾微米、超音波下強烈反射的微泡顯影劑，是 ULM 的「螢光分子」對應物。
   - **Ultrasound localization microscopy (ULM)**: 稀疏微泡 + 中心定位 + ultrafast imaging 累積幾十萬定位點，重建出 sub-wavelength 血管圖。
   - **Low microbubble concentration**: 把微泡稀釋到每張影像裡兩顆氣泡不擠在同一個 diffraction limit 內，保證可個別定位。
   - **Acquisition time**: 累積足夠定位點所需的總拍攝時間，ULM 通常需要幾分鐘到幾十分鐘。
   - **Periodic multifocal pattern**: 規律條紋光罩，由 transducer 元件以不同時序相位組成，用來與組織干涉產生 moiré。
   - **Moiré fringes**: 兩個高頻條紋干涉產生的低頻合成條紋，把組織的高頻細節編碼成可被偵測的低頻訊號。
   - **Structured illumination**: 平移幾次條紋、各拍一張、用演算法合成單張高解析影像的超解析路線。
   - **Ultrafast imaging**: kHz 級高速整片掃描，是 ULM 累積大量定位點與 structured illumination 補位置漂移的共用底座。
5. 與此篇文章的關係: 
   在《Wearable ultrasound technology》這篇 Review 中，作者要解決穿戴貼片用低頻聲波看不到 sub-wavelength 微血管的根本限制。Ultrasound localization microscopy 與 structured illumination 把超解析從硬體（換高頻探頭）轉移到軟體與發射策略，吃進貼片既有的 radiofrequency signal 與微泡顯影劑，輸出比 diffraction limit 還細的血管影像。這讓 wearable form factor 在不換探頭的條件下保留通往微血管影像的延伸路線，雖然 acquisition time 與條紋對齊仍是待解工程瓶頸。