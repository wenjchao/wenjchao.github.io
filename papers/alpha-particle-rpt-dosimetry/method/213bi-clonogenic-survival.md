# 以 213Bi-標記抗體進行 α-particle 細胞照射與 clonogenic survival 分析

1. 引用自哪篇 paper: alpha-particle-rpt-dosimetry
2. Outline (任務主線): 在三陰性乳癌細胞中以特定 α-emitter–抗體複合物量化 α-particle 對細胞的殺傷 (D₀) 與 RBE，作為 synthetic lethality 強化效應的定量基線。
3. Method:
三陰性乳癌細胞 (MDA-MB-231) 表面有大量生長因子受體 EGFR，但缺少 ER、PR、HER2 這三個臨床常用標靶，是公認難治的乳癌亞型。作者把放射性元素鉍-213 (²¹³Bi) 黏在會抓 EGFR 的抗體 Cetuximab 上，做成 ²¹³Bi-Cetuximab。²¹³Bi 半衰期只有 45.6 分鐘，加進培養液後一小時內幾乎全部衰變完畢，對應一次乾淨的單次照射。²¹³Bi 就地衰變射出 α 粒子打進旁邊的癌細胞；隔幾天再看哪些細胞還能長出可見的後代菌落 (clonogenic survival assay)：能長代表那顆細胞當天活下來，不能長代表它被殺死或失去無限增殖能力。把不同劑量下「能長菌落的細胞比例」畫成存活曲線，低存活區段近似一條斜直線，斜率倒數叫 D₀——意思是「劑量再加多少 Gy，存活率會再掉一個 e 倍」。D₀ 越小代表細胞越脆弱。把參考輻射 Cs-137 γ 射線的 D₀ 除以同樣終點下 α 粒子的 D₀，就得到 α 的相對殺傷倍數 RBE。為什麼挑 37% 存活率為終點而不是 50%？因為 37% ≈ 1/e，剛好對應指數型存活曲線「下降一個自然倍數」的標準點。Table 1 顯示 ²¹³Bi-Cetuximab D₀ = 0.87 Gy、RBE = 3.7，落在 DOE 1996 panel 推薦的 3–5 區間，作為後續 synthetic lethality 放大效應的定量基線。

要理解這個基線數字的意義，得先回到 α 粒子本身的物理特性。α 每走 1 微米沉積的能量是一般 γ 射線的 100–1000 倍——這個能量密度叫線性能量轉移 (LET)，α 落在 60–200 keV/μm，γ 只有 0.2–0.5 keV/μm。意思是 α 沿著軌跡「一路放鞭炮」，把 DNA 兩條股在同一個位置幾乎同時打斷，造成雙股斷裂 (DSB)，還會在幾奈米內製造好幾個 DSB 擠在一起的群集 (clustered DSB)。細胞的修補機器面對多個就近重傷會接錯股、接歪甚至放棄，所以 α 的 D₀ 才會比 γ 小好幾倍。

對照組的設計也藏著一個容易被忽略的細節。²¹³Bi 就算沒黏到細胞，光是漂在培養液裡衰變射出的 α 粒子也會打到附近細胞。為了扣掉這個「不靠瞄準也會中彈」的背景，作者用 ²¹³Bi-Rituximab 當對照：Rituximab 原本是抓 CD20 的抗體，MDA-MB-231 不表現 CD20，所以這顆飛彈完全黏不上細胞、只在液體裡衰變。它打出的殺傷代表「純粹背景」。實際上 ²¹³Bi-Cetuximab (D₀=0.87) 與 ²¹³Bi-Rituximab (D₀=0.84) 幾乎一樣，說明這個體外劑量下大多數殺傷其實來自液體中亂飛的 α，而非貼到表面的瞄準照射，本身就是個重要的方法學發現。

Figure 4A 還拿 α 跟低 LET X 光比了一個分次照射實驗。X 光下「分兩次的存活率比單次高」，符合臨床放療「中間休息讓細胞修一點亞致死損傷」的觀察。但 Barendsen 把 9 Gy 拆成兩次 4.5 Gy、中間隔 12 小時打 α，兩個分次的資料點落在單次曲線上完全重合。這個負結果直接證明 α 造成的 DSB 群集修不回來，α 的 D₀ 不會被臨床分次策略稀釋掉。

最後想一個假設：如果不用 clonogenic survival 而改用 MTT 或 trypan blue 之類的短期細胞毒性測試呢？α 打出的 DSB 不一定立刻把細胞撐爆，很多細胞會看似正常活到分裂時才崩潰 (mitotic catastrophe)。短期試驗 24–48 小時只能看到「現在還會代謝、膜還沒破」，會把「快要死但還沒死」的細胞當成活著，嚴重低估 α 的殺傷。clonogenic survival 強迫細胞「分裂個 5–6 次長成肉眼可見菌落」才算活，正好抓得到生殖死亡。一旦讀數換成短期試驗，D₀ 會被高估、RBE 會被低估，整篇 synthetic lethality 的放大倍數就會看不出來。
4. 工具與材料:
- **MDA-MB-231**: 三陰性乳癌細胞株 (ER−, PR−, HER2−, EGFR+)，臨床上難治、可被 Cetuximab 抓到。
- **²¹³Bi-Cetuximab**: 把半衰期 45.6 分鐘的 α-emitter ²¹³Bi 黏在抗 EGFR 抗體上做成的「導引飛彈」，貼到癌細胞表面後就地衰變射出 α 粒子。
- **²¹³Bi-Rituximab**: irrelevant antibody 對照：Rituximab 抓 CD20，但 MDA-MB-231 不表現 CD20，用來扣掉液體中非特異性 α 衝擊的背景。
- **Cs-137 γ rays**: 作為參考輻射的低 LET 光子源，用來算 RBE 的分母。
- **clonogenic survival assay**: 把細胞分散培養、隔幾天看哪些還能長出可見後代菌落，抓得到 α 引發的延遲性生殖死亡。
- **D₀**: 存活曲線低存活區段斜率的倒數，代表劑量再加多少 Gy 存活率會再掉一個 e 倍；D₀ 越小越脆弱。Table 1 ²¹³Bi-Cetuximab D₀ = 0.87 Gy。
- **RBE**: α 相對於參考輻射的殺傷倍數，定義為 D₀(Cs-137)/D₀(α)；²¹³Bi-Cetuximab 基線 RBE = 3.7。
- **37% survival endpoint**: 37% ≈ 1/e，是指數型存活曲線「下降一個自然倍數」的標準終點。
- **Linear Energy Transfer (LET)**: 輻射每走 1 μm 沉積的能量；α 為 60–200 keV/μm，γ 為 0.2–0.5 keV/μm。
- **Clustered DSB**: α 沿軌跡在幾奈米內製造多個雙股斷裂擠在一起的群集，是高 LET 殺傷的關鍵分子特徵。
- **Fractionation 12 h split**: 把 9 Gy 拆成兩次 4.5 Gy 間隔 12 小時的設計，用來檢驗 α 引發的傷害是否能被細胞分次修復；α 結果顯示無修復。
- **Sublethal damage repair**: 低 LET 輻射分次後細胞利用中間休息時間修一點傷，存活率因此上升；α 不存在此效應。
5. 與此篇文章的關係:
在《Dosimetry, Radiobiology and Synthetic Lethality: Radiopharmaceutical Therapy (RPT) with Alpha-Particle-Emitters》這篇文章中，作者為了把 αRPT 推上臨床，必須先給出一個量化基準回答「α 對細胞到底多兇」。為此他在 MDA-MB-231 細胞上做 ²¹³Bi-Cetuximab 照射搭配 clonogenic survival，得出 D₀ 與 RBE。這套讀數解決了 αRPT 因投與活性低、無法直接量測吸收劑量而難以比較不同藥物的瓶頸，並把「沒有修復路徑缺陷時 RBE 約 3–5」的細胞基線交給下游 siRNA、HRD 病人分析作為對照。
