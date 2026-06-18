# 血壓量化模型 (Vessel diameter → Blood pressure)

1. 引用自哪篇 paper: wearable-ultrasound-technology
2. Outline (任務主線): 血壓量化模型 (Vessel diameter → Blood pressure)
3. Method: 
   穿戴貼片不直接量血壓——它做的是「量動脈管子鼓得多大」。具體流程是：超音波打進動脈、前壁與後壁各回一道反射，A-mode（送出去與彈回來的原始聲波訊號 radiofrequency signal 直接畫成距離圖）讀兩道反射的時間差就知道兩壁間距、也就是動脈當下的直徑。心臟每跳一下壓力推大、管子撐大、回波時間差變大；心臟休息時管子縮小、時間差變小，連續記錄就得到一條動脈壁鼓動的直徑波形 (arterial diameter waveform)。接著套用已知的「diameter–pressure」數學模型把每個瞬間的直徑換成那一瞬間的血壓——簡化版的模型把動脈當彈性管、寫成「壓力 = 某常數 × 直徑變化量 + 基準壓力」，這個常數就是動脈硬度係數 (arterial stiffness coefficient)。串起來就是跨整個心跳週期的連續血壓曲線 (continuous blood pressure waveform)。
   為什麼非得校正？動脈硬度因人而異——20 歲健康人的動脈軟、係數小；70 歲高血壓患者的動脈硬、係數可能大上好幾倍；直接套人口平均常數會有 10–20 mmHg 的個體誤差。所以實務上要請使用者先用充氣帶式血壓計 (cuff) 量一次「現在的真實血壓」、同時讓貼片記下「現在的真實直徑」，把這組值代入模型解出個人化動脈硬度係數 (initial calibration)，之後貼片就自己跑下去 (refs 25, 56, 91, 114–117)。這個假設背後是動脈壁的物理：動脈壁含彈性蛋白與膠原纖維，低壓時主要由彈性蛋白決定彈性、鼓張比例近線性；短時間內動脈組成不變，「壓力 ↔ 直徑」曲線就是穩定的——就像水球愈吹愈大，只要橡膠彈性不變，吹多大反映打多少氣壓。
   臨床血壓金標準有兩種：充氣帶式血壓計 (cuff) 是門診常見綁在手臂上充氣那個，準但只能每幾分鐘量一次；插進動脈量壓力的金標準 (arterial line) 把細管插進橈動脈或股動脈直接接壓力感測器，能連續量但侵入。Zhou et al. Nat. Biomed. Eng. 2024 (ref. 93) 把貼片量的血壓跟這兩種比，平均差異 (mean difference) < 3 mmHg、差異的標準差 (standard deviation of difference) < 4 mmHg；不只在乖乖坐著時準，受試者日常活動、門診、心導管室 (cardiac catheterization laboratory)、加護病房 (intensive care unit, ICU) 也都成立。臨床通常要求 mean difference < 5 mmHg、SD < 8 mmHg 才算可接受，這套數字已跨過門檻。
   這套模型有兩個明顯壞點。第一，動脈硬度係數會漂移：粥狀硬化進展、水腫、降壓藥、年齡增加都會慢慢改變硬度，校正鎖住的還是幾週前那個值，貼片讀出的血壓會慢慢偏離真實值，作者點出這是目前模型最大的限制，需要加入隨時間變動的血管壓力動態模型或定期再校正一次 (ref. 118) 才能撐長期居家連續監測。第二，A-mode 量到的是貼片正下方那條聲束的回波，如果貼片在使用者轉手腕、揮手時偏離動脈幾毫米，聲束會打到旁邊的靜脈、肌肉、或乾脆失去前後壁兩道反射，diameter 波形變得時有時無、時大時小，套進模型就吐出怪數字——這就是為什麼 Lin et al. Nat. Biotechnol. 2024 (ref. 68) 要用 32-element array 一次掃過手腕、用 ML 自動挑「正好對準動脈」的那條訊號補對位失敗。
4. 工具與材料: 
   - **A-mode**: 把原始 radiofrequency signal 沿距離 / 時間軸畫成單條波形，看反射來自哪個深度。
   - **Arterial diameter waveform**: 動脈前後壁回波時間差隨心跳變化的波形，反映動脈鼓動。
   - **Diameter–pressure model**: 把動脈當彈性管、用「壓力 = 動脈硬度係數 × 直徑變化 + 基準壓力」把直徑換成血壓。
   - **Arterial stiffness coefficient**: 決定動脈鼓張對壓力反應斜率的個人化常數，年齡與疾病會讓它漂移。
   - **Initial calibration**: 用 cuff 量一次基準血壓、同時讓貼片記基準直徑，把這組值代回模型解個人化動脈硬度係數。
   - **Continuous blood pressure waveform**: 把每個瞬間的直徑換算後串起來的連續血壓曲線，跨整個心跳週期。
   - **Cuff**: 門診常見的充氣帶式血壓計，準但只能每幾分鐘量一次。
   - **Arterial line**: 插進動脈接壓力感測器的金標準，能連續量但侵入。
   - **Mean difference / Standard deviation of difference**: 與臨床參考的平均差與差異標準差，本研究 < 3 mmHg / < 4 mmHg 跨過臨床 5/8 mmHg 門檻。
   - **Cardiac catheterization laboratory / ICU**: 心導管室與加護病房，作為跨情境臨床驗證的對照場景。
5. 與此篇文章的關係: 
   在《Wearable ultrasound technology》這篇 Review 中，作者要把連續血壓監測搬出醫院、放到日常活動裡。Diameter–pressure model 吃進穿戴貼片的 A-mode radiofrequency signal、輸出連續血壓波形，解決傳統 cuff 只能每幾分鐘量一次、arterial line 侵入又只能床邊使用的瓶頸；輸出再交給 multimodal fusion 與臨床決策模型做後續判讀。Zhou et al. Nat. Biomed. Eng. 2024 (ref. 93) 驗證了跨日常活動、門診、心導管室、ICU 的臨床等級準度。