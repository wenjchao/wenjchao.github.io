# αRPT 體內定量影像：定量 planar 與 SPECT 影像取得時間積分活性

1. 引用自哪篇 paper: alpha-particle-rpt-dosimetry
2. Outline (任務主線): 解決 αRPT 投與活性低、光子產率低的影像挑戰，獲得 $\tilde{A}(r_S,T_D)$ 所需的時間積分活性，作為 MIRD 劑量公式輸入。
3. Method:
αRPT 劑量計算的物理本質是 MIRD 公式（Eq. 1–4，見 §3-A）「每次衰變放出的能量 × 衰變總次數 ÷ 器官質量」。其中「衰變總次數」由 $\tilde{A}(r_S,T_D)$ 描述——某個源組織 $r_S$ 從藥物注射開始算起、到時間 $T_D$ 為止，總共發生了多少次放射性衰變，也就是時間-活性曲線下面積。拍不到 $\tilde{A}$，整個劑量計算就無法啟動。但 αRPT 拍照面臨雙重壓力。第一是「燈泡很少」：α-emitter 的治療劑量比傳統 β-emitter 療法低一到兩個數量級（從幾十 mCi 變成 sub-mCi），因為一發 α 殺傷力太大、加多就會超標。第二是「燈泡不發可見光」：α 衰變本身只射 α 粒子、不發 γ，γ camera 看不到 α；伴隨衰變鏈雖然有少量 γ 光子，但分支比例小、能量還散在不同峰位，γ camera 計數率極低、訊號雜訊比差。傳統 β-emitter 療法（例如 ¹³¹I）治療劑量大、γ 又強，這個問題不存在。

作者列出兩個方向的影像方案。Quantitative planar imaging 是「γ camera 從前後幾個固定角度各拍一張平面影像」，常規做法是病人前後各拍一張 conjugate view、用衰減校正抵消身體厚度的吸收，再把每個器官的計數轉成放射性活性（Hindorf et al. Nucl Med Commun 2012 對 ²²³Ra-chloride、Alpharadin；Carrasquillo et al. EJNMMI 2013 對 ²²³Ra-dichloride 的 mCRPC phase I PK/biodistribution）。優點是快、可以一次掃全身，適合追蹤藥物在大範圍器官間的分布變化。缺點是 2D 影像把不同深度的器官重疊在一起。Quantitative SPECT 則是 γ camera 圍著病人繞一圈、拍多角度投影、再用電腦反算回 3D 橫切面亮度地圖，能解析器官重疊與深度差異（Ghaly, Sgouros & Frey 系列 ²²⁷Th 與雙同位素 ²²³Ra/²²⁷Th 同步重建；He et al. J Med Imaging Radiat Sci 2019 ²¹²Pb SPECT）。代價是掃描時間長、量化演算法複雜，所以通常只對少數關鍵器官（腎、骨髓、轉移病灶）做精準量化。

雙同位素 SPECT 的關鍵在於：²²⁷Th 衰變後會變成 ²²³Ra，所以注射 ²²⁷Th 進病人體內後，體內同時有母核 ²²⁷Th 和子核 ²²³Ra 在衰變、各自放出特徵能量不同的伴隨 γ 光子。γ camera 像「會分顏色」的相機，能依光子能量分窗（energy window）同時記錄不同能峰；重建時再做「能窗之間互相干擾的串擾校正 (downscatter correction)」——高能量光子在身體裡會散射、落到低能量窗污染另一個核種訊號，必須先模擬出散射貢獻再扣掉。校正完後兩個核種在每個位置的活性可以分別量化，這對「²²³Ra 偏骨、²²⁷Th 可能分布到其他組織」的劑量分配計算很關鍵。另一條備援策略叫 validated surrogate imaging agent：跟 αRPT 用同一個導引分子（抗體或小分子）、但把放射性元素換成容易拍照的核種，比如把 ²²⁵Ac-抗體換成 ¹¹¹In-同款抗體，抗體照樣去找腫瘤，但 ¹¹¹In 放出大量 γ，可以用一般 SPECT 清楚拍出來。前提是兩個藥物的 pharmacokinetics 與 biodistribution 必須先經實驗驗證一致（validated），不然 surrogate 量到的曲線跟真實 αRPT 對不上、推估的 $\tilde{A}$ 也錯。

兩個容易壞掉的環節值得提醒。第一是時間取樣不夠：$\tilde{A}$ 是時間-活性曲線下面積，要把這條曲線描出來至少需要血流期、累積期、排出期多個時間點（典型的取樣節奏是打針後 4 h、24 h、48 h、72 h、168 h），再用兩到三個指數衰減模型擬合。如果只拍一次，看到的只是某個瞬間的點，不知道在曲線上是上升段、頂點還是下降段，整個 AUC 估計可能誤差 2–5 倍，MIRD 公式進去的 $\tilde{A}$ 直接錯。第二是衰減校正：γ 光子穿過人體軟組織會被吸收、γ camera 看到的計數一定比實際少。planar 用 conjugate view 幾何平均假設衰減均勻；SPECT 則用 CT 影像當「衰減地圖 (attenuation map)」精算每條光子路徑經過多少骨頭與軟組織。如果校正用的衰減係數不對（把骨密度算成軟組織、漏算肋骨擋住肺裡的訊號），器官活性會被低估或高估幾十個百分比。對 αRPT 這種訊號本來就弱的應用，衰減校正錯了更難從雜訊裡發現，要靠標準化 phantom 校驗才能維持量化精度。輸出的 $\tilde{A}$ 接下來會被餵進 §3-A 的 MIRD 公式算出每個器官的分項吸收劑量，並乘上 §2-D 預臨床取得的 apportionment factor 推估 sub-organ 真實劑量。
4. 工具與材料:
- **time-integrated activity ($\tilde{A}$)**: 源組織從投與到時間 $T_D$ 內累積的衰變次數，即時間-活性曲線下面積；MIRD 劑量公式的核心輸入。
- **quantitative planar imaging**: γ camera 從前後固定角度拍 2D 投影、用 conjugate view 衰減校正後算器官活性；適合全身快速取樣。
- **quantitative SPECT**: γ camera 繞病人一圈拍多角度投影、電腦反算 3D 橫切面活性地圖；對腎、骨髓等關鍵器官做精準量化。
- **²²³Ra-chloride (Alpharadin)**: Hindorf 2012 用於骨轉移定量 planar imaging 的 α-emitter 藥物。
- **²²³Ra-dichloride**: Carrasquillo 2013 mCRPC phase I PK/biodistribution 研究的 α-emitter 藥物。
- **dual-isotope SPECT (²²³Ra/²²⁷Th)**: 同一次掃描開兩個能窗、做 downscatter 校正後分別量化母核 ²²⁷Th 與子核 ²²³Ra 的活性。
- **²¹²Pb SPECT**: He et al. 2019 開發的 ²¹²Pb 體內定量 SPECT 重建方法。
- **validated surrogate imaging agent**: 與 αRPT 用同一導引分子、但換成容易拍照的核種（如 ¹¹¹In）；前提是 PK 與 biodistribution 已驗證一致。
- **attenuation correction (conjugate view / attenuation map)**: 校正 γ 光子被身體吸收造成的訊號低估；planar 用 conjugate view 幾何平均，SPECT 用 CT 衰減地圖。
- **downscatter correction**: 雙同位素 SPECT 中扣除高能量光子散射污染低能量窗的校正。
5. 與此篇文章的關係:
在《Dosimetry, Radiobiology and Synthetic Lethality: Radiopharmaceutical Therapy (RPT) with Alpha-Particle-Emitters》這篇文章中，作者為了解決「αRPT 投與活性低、α 不發 γ、伴隨 γ 又微弱」導致 MIRD 劑量公式 $\tilde{A}$ 拍不出來的瓶頸，採用了「quantitative planar imaging + quantitative SPECT + 雙同位素重建 + surrogate imaging agent」的影像工具包（protocol 取自 Hindorf 2012、Carrasquillo 2013、Ghaly/Sgouros/Frey 系列、He 2019）。它的輸入是病人多時間點的 γ camera 計數，產出是每個源組織的時間積分活性，下游被 §3-A 的 MIRD 公式吃進去算分項吸收劑量，再乘上 §2-D 的 apportionment factor 推估 sub-organ 真實劑量。
