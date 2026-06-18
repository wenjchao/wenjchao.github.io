# Echocardiography 衍生指標計算

1. 引用自哪篇 paper: pediatric-tri-tube-valved-conduit
2. Outline (任務主線): 把 2D/3D 超音波量到的尺寸、流速轉成 EOA、systolic ΔP、cardiac output、pulmonary insufficiency index、freedom-from-moderate-regurgitation 等可比較指標。
3. Method:

這個子項處理的是「怎麼在不開胸的前提下，每隔幾週量化瓣膜還工作得好不好」。作者把探頭隔著羊胸壁放上去做胸壁外貼超音波 (transthoracic echocardiography)；植入當下因為胸已經打開，直接把探頭貼在心臟表面拍一輪 3D 影像建立基準 (epicardial 3D ultrasound)。畫面上抓兩類訊號：第一類是幾何量——瓣膜直徑、葉片在閉合時上下重疊的那段長度 (coaptation length)、從短軸正面看到的葉片游離邊總長 (free-edge length)；第二類是血流量——用彩色都卜勒 (Color Doppler) 把血流速度畫成顏色（朝探頭染紅、離開染藍、越亮越快），舒張期若有反向噴流就是回流，噴流越亮越粗代表漏得越嚴重。葉片重疊長度越長代表閉得越緊、容錯空間越大；Fig. 8 上作者直接畫一個括號從 5.0 mm 縮到 1.7 mm，就是在量這段重疊長度從寬鬆變得勉強。葉片本身有沒有跟著羊一起長大，則以植入後 1 週的游離邊總長為基準，看 52 週時長了百分之幾（例如 17–37%、25–34%）。

把這些原始量換成可比較儀表的部分，作者主要用三個指標。第一個是等效開口面積 (EOA) 與心臟收縮時瓣膜兩側的壓力差 (systolic ΔP)：把瓣膜想成擠出口的洞——洞越窄，要在同樣時間擠同樣血量就得加大推力，上下游壓力差越大；EOA 是「按目前流量與壓力差反推出來的有效洞口大小」，單位 cm²，systolic ΔP 單位 mmHg。EOA 越大、systolic ΔP 越小，代表瓣膜對血流的阻力越低、心臟做的功越少。第二個是 pulmonary insufficiency index：把「每跳一下漏回去的血量」除以「每跳一下打出去的血量」，得到一個無單位比值。為什麼用比值不直接報漏血量？因為羊體型每週都在變、心率也波動，絕對量會被這兩個因素帶著跑；改成比值後羊大羊小、跳快跳慢都能直接比，所以作者把它定位成 time-independent（不受時間軸影響）的設計版本比較指標——Gen 1 是 3.5 ± 0.4、Gen 2 是 2.2 ± 0.8，用 t test 比兩個數字得到 *P* = 0.015。

量測時程與數值錨點則是這樣安排的：植入當下、1 週、1 個月、之後每 2 個月一次，回流接近中度時再加密。1 週與 1 個月是「手術早期會不會壞」的觀察窗，縫線鬆脫、血栓、感染這類問題通常會在這段時間冒出；撐過去之後每 2 個月一次足以追蹤長期尺寸與漏血變化，又不會把羊壓得太累。一旦回流逼近作者設定的 endpoint（中度回流），就改密集追蹤精確抓「該取出」的時間點，避免犧牲時瓣膜已被持續沖刷到面目全非。心臟每分鐘打出多少血 (cardiac output) 這個量的合理範圍則以 Cattermole 等人 2017 的兒科正常值 4.0 LPM 為錨 (ref 29)：體外 pulse duplicator 跑 EOA 時就把流量設成 4.0 LPM，植入後超音波算出來的羊心輸出量也用 4.0 LPM 當對照，這樣結論才能對接到「兒科實際工況」而不是某個方便的實驗條件。

這套量測有兩條容易壞掉的地方要小心。第一是回流分級本身就是定義「瓣膜失敗時間」的標尺，把實際的中度回流誤判成輕度會讓作者延遲取出瓣膜、組織被沖刷到難以解讀；把輕度當中度則會提早犧牲、低估存活時間，整條 Kaplan-Meier 曲線往左偏，第二代相對第一代的設計優勢被稀釋。所以分級必須穩定地由同一套都卜勒影像判讀。第二是量測情境本身帶噪音：作者刻意不用麻醉、只用人工約束做超音波，避免麻醉藥讓心臟壓低、量到的數字偏離日常，代價是羊可能因為被抓住而緊張、心率瞬間竄高，那一刻 cardiac output 也虛高。Table 1 因此特別標一條「這次量測時心率異常」，等於提醒讀者單次極端值不要當趨勢——這是 in vivo 量測時保留誠實的標準動作。

4. 工具與材料:

   - **Transthoracic echocardiography**: 胸壁外貼超音波，每隔幾週非侵入式追蹤瓣膜尺寸與血流。
   - **Epicardial 3D ultrasound**: 植入當下把探頭貼在心臟表面拍 3D 影像建立基準。
   - **Color Doppler**: 彩色都卜勒，把血流方向與速度畫成顏色，反向噴流即為回流。
   - **Coaptation length**: 舒張期三片葉片上下重疊那段長度，越長代表閉合餘裕越大。
   - **Free-edge length**: 從短軸正面看葉片游離邊總長，以 1 週為基準看 52 週增長百分比，當葉片生長代理指標。
   - **EOA**: 等效開口面積 (effective orifice area)，由流量與壓力差反推的有效洞口大小，單位 cm²。
   - **Systolic ΔP**: 心臟收縮時瓣膜上下游平均壓力差，單位 mmHg；數值越低代表血流阻力越低。
   - **Cardiac output**: 心臟每分鐘打出的血量，單位 LPM；以 Cattermole 兒科 4.0 LPM 為參考。
   - **Pulmonary insufficiency index**: 每搏漏回去的血量除以每搏打出去的血量，time-independent 的回流嚴重度比較指標。
   - **Freedom from moderate regurgitation**: 把「回流首次達中度」當瓣膜失敗時間，供 Kaplan-Meier 存活分析使用。

5. 與此篇文章的關係:

在這篇研究中，超音波衍生指標是唯一能在不犧牲生長中羊隻的前提下，每隔幾週客觀回答「這顆工程瓣膜還工作得好不好」的工具，因此擔任 52 週縱貫追蹤的主力儀表板。作者透過胸壁外貼超音波加彩色都卜勒，把幾何量（瓣膜直徑、coaptation length、free-edge length）與血流量翻譯成 EOA、systolic ΔP、cardiac output、pulmonary insufficiency index 四個跨個體可比的數字，再以「首次達中度回流」作為瓣膜失敗事件定義，餵進 Kaplan-Meier 存活分析。它的好處有三：非侵入、無需麻醉，能高頻採樣不擾動實驗對象；time-independent 的 insufficiency index 排除了羊體型與心率波動的干擾，使 Gen 1 (3.5 ± 0.4) 與 Gen 2 (2.2 ± 0.8) 的 P = 0.015 差異具有設計學意義；cardiac output 對齊 Cattermole 兒科 4.0 LPM 也讓結論可外推到臨床工況。它與 pulse duplicator 體外水動力測試共用 EOA / systolic ΔP / cardiac output 的語彙，使「植入前體外性能」與「植入後體內表現」可無縫對照；提供的「失敗時間」是 Kaplan-Meier 存活曲線與 log-rank 檢定 (tube-in-tube vs tri-tube P = 0.0024) 的事件輸入；偵測到回流接近中度時觸發提前犧牲，又把動物精準交棒給後續的 histology、生化定量與力學測試，避免組織被持續沖刷到難以解讀，是整條「設計→計算→體外→體內→量化」閉環中銜接活體觀察與終點分析的關鍵節點。
