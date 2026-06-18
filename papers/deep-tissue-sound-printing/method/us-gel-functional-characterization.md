# 功能性 US-gel 表徵：導電、藥物釋放、黏附

1. 引用自哪篇 paper: deep-tissue-sound-printing
2. Outline (任務主線): 功能性 US-gel 表徵：導電、藥物釋放、黏附
3. Method: 
   Conductive US-gel 的導電度怎麼量？作者用 two-probe amperometry（兩探針法）：在印出來的 US-gel 線條兩端各黏一支電極（間距固定 10 mm），用 CHI 660E 電化學工作站施加 1 V 直流偏壓，量穩態流過的電流 I——電阻就是 R = V / I。為什麼用兩探針而不是四探針？因為兩探針簡單、能直接給整段線（含接觸電阻）的電阻，且列印線寬有限，不易擠四個電極點。同時作者把線寬 w 與電阻 R 一起量，發現遵循歐姆定律的幾何形式 $R = \rho L / (w \cdot t)$；只要 t 與 ρ 固定，R 就只與 1/w 成正比。這條 R ∝ 1/w 校正曲線之後可用 SEM 量出來的線寬反推應該量到的電阻、當品保檢查依據。
   
   有了這條電阻校正後，CNT-US-gel 就能變成貼皮膚的元件，作者示範兩種玩法。第一是溫度感測：CNT 在 alginate 網裡形成滲流網路 (percolation network)，溫度升高時 CNT 之間的距離與接觸狀態微微變動、電子穿隧機率改變、電阻隨之改變。作者把 CNT-US-gel 線放在加熱板上，用紅外線溫度計 (IR thermometer) 量表面溫度從 20 °C 升到 70 °C，同時兩探針量電阻；得到「溫度–電阻」校正曲線、斜率就是感測靈敏度。日常應用時，這段線貼到人皮膚上、皮膚溫度 ~30–37 °C 就會讓電阻變到對應值、反推皮膚溫度。第二是 ECG / EMG 收訊：作者用 SparkFun AD8232——open-source 心電 / 肌電專用的訊號放大模組（shield，意指擴充板）——配 CNT-US-gel 電極收訊。ECG 配置兩支貼左右手收心電向量差、第三支貼腿當參考地；EMG 配置兩支貼於 biceps brachii 兩端，肌肉收縮的動作電位在兩電極間產生電位差。再用 MATLAB 跑 50 Hz low-pass filter 去除家用電源工頻干擾，留下乾淨生理訊號。
   
   藥物釋放用兩種代表性分子模擬不同藥物。BSA（牛血清白蛋白，66 kDa）代表大分子生物製劑（如抗體、酶替代藥）；rhodamine B（479 Da 螢光染料）代表小分子化療藥（如 doxorubicin）。把 US-gel 做成 Φ7 × 2 mm 圓片各自吸滿 80 mg/ml BSA 或 160 mg/L RhB，浸到 2 ml PBS 中模擬體液，連續 7 天定時取上清量 UV-vis：BSA 量 279 nm（芳香族胺基酸的特徵吸收）、RhB 量 556 nm（其發色團特徵吸收）；各跑 calibration curve 把吸光換成濃度。為什麼要雙模型？因為 US-gel 是個交聯網，網孔 (mesh size) 大致固定；分子比孔小時幾乎自由擴散、接近孔大小時受空間阻擋擴散變慢——同測兩種就一次涵蓋大、小分子兩大藥物族，並揭露 gel mesh size 的有效範圍。為什麼要追 7 天？因為釋放通常分兩階段：初期 burst release（表面藥 1–24 h 快速釋出）與後期 sustained release（gel 深處藥幾天慢慢擴散）；只看 24 h 主要量到 burst phase、會誤判緩釋效率，要 7 天才看得到 plateau 與斜率。
   
   GelCA US-gel 的黏附強度量法就是把貼好的 OK 繃從貼面拉開：75 μl GelCA US-ink 倒在流變儀 8 mm 平板上、上板降下夾成 0.5 mm 薄層，先在 37 °C 平衡、再升溫到 43 °C 模擬 FUS 觸發；LTSL 釋放 NaIO₄、GelCA 上的 catechol 被氧化成 quinone、與上下兩板（模擬組織）共價反應形成黏結。膠化完成後上板以 0.5 mm min⁻¹ 緩慢往上拉、量正向力 (normal force) 隨位移的變化；力的峰值除以板接觸面積就是黏附強度（kPa）。作者也在豬心 / 牛筋膜上做 ex vivo 黏附測試（Fig. 4L），把實驗室數字接到真實組織黏合情境。
   
   結構表徵用 SEM (ZEISS 1550VP) + EDS (Oxford X-Max SDD)：把 freeze-dried US-gel 打上 5 nm Pt 鍍膜防 charging、10 kV 成像，看內部多孔網路與 CNT 在 alginate 裡的分散情形；EDS 同時掃描 Ca、C、N 等元素的空間分布，例如確認 Ca²⁺ 真的在 alginate 網裡（Fig. S5）。這也是 conductive US-gel 的品保關卡——如果 CNT 在拌墨水或膠化時聚成一團，會出現局部黑塊但黑塊之間絕緣間隙，整段電阻忽大忽小、ECG 訊號被雜訊蓋掉。Impedance 端用等效電路模型描述 US-gel 在交流訊號下的電化學行為：Ri 代表離子在 gel 內遷移的阻力、Cdl 代表電極—gel 介面的雙電層電容；Rp + CPEp 並聯描述介面處的法拉第電荷轉移與非理想電容（CPEp 是 constant phase element，用 Q_p, n_p 兩參數描述真實電極的非完美電容行為）。在 Nyquist plot 上擬合這四個元素，就能反推 gel 的電化學性能（Fig. S21D）。
4. 工具與材料: 
   - **Two-probe amperometry + CHI 660E**：兩端電極施加 1 V 直流偏壓量電阻 R = V/I；10 mm 電極間距。
   - **R ∝ 1/width 校正**：依歐姆幾何 $R = \rho L/(w t)$，線越粗電阻越小；以 SEM 線寬反推品保。
   - **Percolation network (CNT-alginate)**：CNT 在 alginate 網中形成連續導電路徑；分散均勻是低電阻與低雜訊的前提。
   - **IR thermometer**：量 hot plate 表面溫度 20–70 °C 與 CNT-US-gel 電阻同時對應，得感測靈敏度。
   - **SparkFun AD8232 ECG/EMG shield**：open-source 高輸入阻抗差動放大器擴充板，搭配 CNT-US-gel 電極收 ECG / EMG 訊號。
   - **50 Hz low-pass MATLAB filter**：去除家用電源工頻干擾，留下乾淨生理訊號。
   - **BSA + Rhodamine B 雙模型**：66 kDa 大分子模型 vs. 479 Da 小分子模型，一次涵蓋抗體與化療藥釋放動力學。
   - **UV-vis @ 279 nm / 556 nm**：分別量 BSA 芳香族胺基酸與 RhB 發色團的特徵吸收，配 calibration curve 換濃度。
   - **Burst → sustained release**：兩階段釋放：1–24 h 爆釋 + 數天緩釋；追 7 天才能完整刻畫。
   - **黏附強度 (kPa)**：流變儀 8 mm 平板拉脫測試：上板 0.5 mm min⁻¹ 抬升，最大力 / 接觸面積。
   - **SEM + EDS (ZEISS 1550VP + Oxford X-Max)**：10 kV、5 nm Pt 鍍膜；看多孔結構、CNT 分散與元素空間分布。
   - **Equivalent circuit (Ri + Cdl + Rp + CPEp)**：離子電阻、雙電層電容、法拉第電荷轉移、非理想電容；Nyquist plot 擬合得電化學參數。
   - **Mark-10 force gauge**：以 2 mm min⁻¹ 壓 Φ6 × 3.7 mm disk 量壓縮性質。
5. 與此篇文章的關係: 
   在《Imaging-guided deep tissue in vivo sound printing》這篇文章中，作者要證明 DISP 不只能在組織上印出形狀好看的水膠、還能印出真的有效能的功能元件。為此他們做了三條表徵主線：(1) 用 two-probe amperometry + IR + AD8232 + 50 Hz filter 證明 CNT-US-gel 可當溫度感測器與 ECG/EMG 電極；(2) 用 BSA + RhB 雙分子模型 + UV-vis 跑 7 天釋放證明 US-gel 能當小分子與生物製劑的緩釋載體；(3) 用流變儀拉脫測試 + 豬心 ex vivo 證明 GelCA US-gel 能當生物黏著貼片。這套表徵把 DISP 從「列印形狀」推進到「列印可量化效能的醫療元件」。
