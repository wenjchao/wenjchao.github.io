# Transducer Stack 與陣列幾何設計

1. 引用自哪篇 paper: wearable-ultrasound-technology
2. Outline (任務主線): Transducer Stack 與陣列幾何設計
3. Method: 
   作者把貼片從壓電元件向皮膚這一側拆成四層 stack，每一層都對應一個物理問題。背襯層 (Backing layer) 是黏在元件背面的「聲波海綿」，用金屬粉末混環氧樹脂 (metal–epoxy resin composite) 做成（Hu et al. *Nature* 2023, ref. 63）：壓電元件發聲時聲波會同時往前與往後跑，背後那束如不吸掉就會反彈回來與下一發訊號混在一起、把頻寬與空間解析度拖垮，背襯層的工作就是把它吃進去散熱掉。阻抗匹配層 (Matching layer) 塞在元件正面與皮膚之間，厚度剛好做成四分之一波長：從前介面進來的聲波被後介面部分反射，反射波在匹配層內走了 1/4 + 1/4 = 1/2 波長剛好與新進來的反射波相位相反、互相抵消，整個介面反射被消掉、聲波順暢進入皮膚（refs 23, 33, 64, 65）。矽橡膠聚焦透鏡 (silicone elastomer lens) 把模量接近軟組織的矽橡膠模成中央厚邊緣薄的凸透鏡形狀，靠路徑差自然把聲波聚到前方焦點；Bhuyan et al. (ref. 67) 更進一步用單層 elastomer 同時兼當聚焦透鏡與防汗刮的封裝層 (encapsulation)，少一層黏結介面、整片貼片變薄變柔。
   四層 stack 不是每個應用都全要。連續波都卜勒 (continuous-wave Doppler) 用兩顆元件一個一直發、一個一直收，靠收發訊號的頻率差算血流速度，根本不靠回波輪廓還原影像；背襯層吸不吸都不影響結果，Kenny et al. *Sci. Rep.* 2021 (ref. 69) 因此把 backing layer 直接省掉、貼片變薄。Lin et al. *Nat. Biotechnol.* 2024 (ref. 68) 在手腕測周邊動脈搏動，目標血管只在皮膚下幾毫米深，根本不需要聚焦到更深焦點，乾脆把矽橡膠透鏡省掉、stack 從四層減到三層。stack 簡化的判準很直白：這個應用真的需要這一層解決的物理問題嗎？
   陣列幾何最關鍵的設計法則來自相位陣列 (phased array)：透過讓每顆元件以不同時間差發聲，合成一束可任意角度偏轉的主光束 (main beam)；但同樣的時間差也會讓其他角度的副光束 (grating lobes，旁瓣) 跟著合成出來。當元件間距 (element pitch) 大於半個波長 (½ wavelength)，這些副光束會落在你想看的視野 (field of view, FOV) 內，把不該存在的回波當成真實影像疊上去——這是空間取樣不夠造成的混疊 (spatial aliasing)。把間距壓到 ≤ ½ wavelength，副光束才會被推到 FOV 之外、不影響影像（Zhang et al. *Nat. Electron.* 2023, ref. 24）。這條法則直接綁住陣列的物理尺寸：頻率越高、波長越短、間距要越小、製程越難。
   陣列幾何的高階選擇在「資料量 vs 影像維度」之間取捨。正交陣列 (orthogonal array) 是兩條線性陣列十字交疊，透過多工器 (multiplexer) 讓兩條共用交叉點的元件，可以同時抓兩個互相垂直的切面（例如心臟的長軸與短軸），Hu et al. *Nature* 2023 (ref. 63) 的心臟貼片即此架構——只用兩條 linear array 的元件數，就能換到兩個正交切面。二維陣列 (2D array) 則把元件排成一張 matrix，每顆都能單獨被定址、可重建完整 3D 體積影像，但代價是 channel count 平方成長，128×128 就要 16384 條線、wearable 完全塞不下，必須靠 ASIC 與多工器壓縮（refs 71, 72）。Orthogonal array 是 2D array 的窮人版，2D array 是畫面完整但連線爆炸。
   兩個失敗情境提醒了 stack 與陣列幾何的選擇有硬底線。其一，省略 matching layer 直接讓壓電 Z ≈ 30 MRayl 貼皮膚 Z ≈ 1.6 MRayl：大部分能量在介面被反彈，發射時聲波損失一大半，反彈回到元件內的能量會在元件正反面之間來回反射 (interfacial reverberation)，每個短脈衝拖出長尾巴、相鄰回波疊成一團，pulse 變胖、頻寬變窄、影像解析度直接劣化。其二，相位陣列 element pitch 偷做成 1 wavelength：副光束剛好落在 FOV 內某些角度，回波回來時電路分不清是主光束還是副光束貢獻，影像上會看到真正目標旁邊還疊著一個鬼影 (ghost echo)——對醫療診斷來說可能把不存在的腫瘤或血管當成真的，這就是 ½ wavelength 規則是相位陣列硬底線的原因。
4. 工具與材料: 
   - **Backing layer**: 黏在壓電元件背面的『聲波海綿』，金屬粉末混環氧樹脂製成，吸收向後傳的聲波避免反彈造成 reverberation。
   - **Matching layer**: 塞在壓電元件與皮膚之間的過渡層，厚度為四分之一波長；利用反射波相位差 1/2 波長互相抵消、消除介面反射。
   - **Quarter-wavelength rule**: Matching layer 厚度必須為四分之一波長 (λ/4) 的物理依據——使前後介面反射波相位相反互相抵消。
   - **Silicone elastomer lens**: 用模量接近軟組織的矽橡膠模成中央厚邊緣薄的凸透鏡，靠路徑差聚焦聲波，亦可同時兼做封裝層 (ref. 67)。
   - **Encapsulation**: 封裝層；保護元件、阻擋汗水與外傷，常用 silicone elastomer，可與 lens 共用單層減少黏結介面。
   - **Phased array**: 相位陣列；用元件間發聲時間差合成可任意偏轉的主光束 (main beam)，間距須 ≤ ½ wavelength 才不讓副光束 (grating lobes) 進入 FOV。
   - **Grating lobes**: 旁瓣／副光束；元件間距過大造成空間混疊產生的鬼影方向，會在影像上疊出 ghost echo。
   - **Linear array**: 一條直線排列的元件陣列；正交陣列即由兩條 linear array 互相垂直十字交疊組成。
   - **Orthogonal array**: 正交陣列；兩條 linear array 十字交疊，透過多工器共用交叉點元件，同時取得兩個正交切面（Hu et al. *Nature* 2023, ref. 63 心臟貼片）。
   - **2D array**: 二維陣列；元件排成 matrix 每顆可單獨定址，能重建完整 3D 體積影像，但 channel count 平方成長需 ASIC 與多工器壓縮（refs 71, 72）。
   - **Multiplexer**: 多工器；讓多顆元件輪流共用一組電路通道、壓縮 channel count，是 orthogonal array 與 2D array 在 wearable 上能存活的關鍵電路。
   - **Continuous-wave Doppler**: 連續波都卜勒；用兩顆元件一發一收靠頻率差算血流速度，因不重建影像可省略 backing layer (Kenny et al. *Sci. Rep.* 2021, ref. 69)。
5. 與此篇文章的關係: 
   在《Wearable ultrasound technology》這篇 Review 中，作者為了把貼片設計成『聲學上有效率、影像上不糊』，介紹了 backing/matching/lens/encapsulation 四層 stack 與線性／正交／相位／2D 陣列幾何的選用法則。Stack 解決能量穿越介面的效率，陣列幾何解決能不能掃描與 3D 成像；½ wavelength 規則與四分之一波長規則是兩條硬底線。這套 stack 與陣列邏輯把 2-A/2-B 的材料與微型元件，組裝成下游 2-D 機械架構與 2-E 後端電路可以接上的『聲學前端』。