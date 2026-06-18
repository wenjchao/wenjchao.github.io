# 生物相容性與功能驗證測試組合

1. 引用自哪篇 paper: deep-tissue-sound-printing
2. Outline (任務主線): 生物相容性與功能驗證測試組合
3. Method: 
   作者把生物相容性拆成兩個階段測，因為材料在體內會經歷兩種不同狀態、毒性來源也不同。prepolymer 階段（含 LTSL 但還沒交聯）是注射型液態，細胞被它整個包圍，要測的是 LTSL 與可能滲漏的游離交聯劑是否毒。US-gel 階段（FUS 交聯後）是留在組織上的固態網路，要測的是交聯網與殘留試劑、降解產物會不會慢慢誘發免疫反應。LTSL 在這套設計中不只是觸發機制、還是 cytotoxicity 屏障：未列印區的 LTSL 仍密封，細胞接觸到的只是表面的 PEG 與磷脂這些中性面；只有 FUS 焦點那一刻才放出 Ca²⁺ / NaIO₄ / TEMED。否則三者直接接觸細胞各有死法——游離 Ca²⁺ 擾亂細胞內鈣訊號啟動凋亡 (apoptosis)；NaIO₄ 是強氧化劑直接破壞膜脂與蛋白硫醇；TEMED 是三級胺、高濃度有刺激性並誘發活性氧 (ROS)。
   
   in vitro 主場用人皮膚纖維母細胞 (human dermal fibroblast, HDF, Lonza)，1×10⁵ cells/well 接種在 24-well 盤，樣本放在 transwell insert 裡。Transwell insert 是底部有小孔膜的小杯、掛在井裡像「掛籃」：細胞在井底、樣本在杯內，可溶性物質透過小孔擴散下去但材料碰不到細胞，排除「材料壓死細胞」「局部高滲透壓」「gel 膜阻斷氣體交換」三類偽陽性，剩下訊號才是真正的化學毒性。讀數用兩種互補指標：LIVE/DEAD 染色——calcein AM 進入活細胞被細胞內酵素切開發綠光、ethidium homodimer-1 只能進膜破細胞與 DNA 結合發紅光，ImageJ 數綠 /（綠+紅）得活細胞比例；PrestoBlue——含 resazurin、活粒線體把它還原成 resorufin 發紅螢光、亮度正比於整體代謝強度。LIVE/DEAD 看「幾顆活著」、PrestoBlue 看「活著的多有勁」，單用任一都會漏掉 sublethal toxicity。
   
   細胞列印測試用 C2C12 mouse myoblast (ATCC CRL-1772)、肌肉再生標準前驅細胞，3×10⁶ cells/ml 混入 alginate US-ink，用 8.75 MHz / 7 W / 10 mm min⁻¹ 印 13×13 mm cube，7 天 LIVE/DEAD 追蹤。為什麼選低功率中速、不是最高解析度組合？因為更高功率更慢速會把焦點停留時間拉長、升溫推到 43 °C 以上，對細胞產生 heat shock。寧可犧牲一點線寬精細度、換到細胞 7 天後仍幾乎都活著，這對「細胞列印」這個應用更重要。
   
   腫瘤這條線用兩種細胞、兩個尺度。T24 是人膀胱癌細胞，6×10³ 顆放進 Greiner Bio-One cell-repellent 96-well 盤（底盤特殊塗層讓細胞不貼底）培養 5 天聚成 3D 腫瘤球體 (spheroid)，模擬真實腫瘤的立體擴散難度；接 20 μl Dox (96 μM) 樣本暴露 30 分鐘後換培養基模擬膀胱排尿沖洗，共追 72 小時——問「藥停 30 min 釋出來的劑量能不能殺穿球體」。MB49 是小鼠膀胱癌細胞，5×10⁴ 顆用 31 號細針注入 C57BL/6J 小鼠膀胱壁建 orthotopic 原位腫瘤模型，4 天後做 in vivo DISP 列印——問「真實活體環境下能不能對準病灶印藥膠」。spheroid 補了「2D 培養盤太簡化」與「動物實驗成本太高」中間的缺口。
   
   in vivo 切片用 0.1 ml alginate US-ink 皮內注射、FUS 組 2.65 MHz / 7 W / 20 mm min⁻¹ 列印；1 週 / 4 週後 CO₂ 安樂死、10% formalin 固定、石蠟包埋、7 μm 切片。三個讀數互補：H&E 用海馬樹蘇木素 (haematoxylin) 染細胞核藍紫、伊紅 (eosin) 染細胞質粉紅，看整體有沒有壞死區、結構撕裂、大量發炎細胞浸潤。但 H&E 無法分辨免疫細胞種類與活化狀態，所以再加 immunofluorescence：F4/80 (Bio-Rad Cl:A3-1) 是小鼠巨噬細胞表面標誌 (pan-macrophage marker) 看聚集數量、CD80 (eBioscience 16-10A1) 是活化巨噬細胞共刺激分子看發炎開關、DAPI 染所有細胞核當底色。為什麼追 1 週與 4 週兩個時間點？因為材料免疫反應隨時間動態變化：24 h 內看到的多半是針孔與焦點加熱造成的急性物理刺激；7 天是巨噬細胞招募高峰、最能看出材料是否被視為敵人；4 週對應慢性反應——纖維包膜、降解產物累積。任一時間點正常都不代表其他時間點安全。
   
   兩種動物答的是不同問題。C57BL/6J 是免疫功能完整的近交系小鼠，跟同系 MB49 膀胱癌細胞配對植入而不會被免疫排斥——既能看本體免疫反應、又能評估 DISP 載藥對腫瘤的真實殺傷力；體型小，適合膀胱 catheter 灌注（用 BD Intima II IV catheter, 0.7 × 19 mm 經尿道灌注 200 μl 含 240 pM GV 的 alginate US-ink）。New Zealand white rabbit 答「能不能打進深層」：大腿肌肉群（adductor、biceps femoris）厚度可達 ≥ 15 mm，接近人類器官深度，且兔肌肉解剖與人接近。兔列印用 2.65 MHz transducer 配 customized cone（內裝 degassed water + ultrasound-transparent membrane 當聲學耦合柱，水的聲阻抗近組織、無反射穿到目標深度）；麻醉採三段式：acepromazine 0.25–1 mg kg⁻¹ SQ 鎮靜 → ketamine 35 mg kg⁻¹ + xylazine 5 mg kg⁻¹ IM 誘導 → isoflurane 1–5% 吸入維持，確保兔子完全不動、焦點才能對得準。Muscle flap 把表層肌肉手術翻折暴露深層目標再放回，比直接打穿厚層更可控。所有動物實驗依 IACUC protocol No. IA23-1810 / IA23-1859 / IA24-1904（Caltech）執行。
4. 工具與材料: 
   - **Human dermal fibroblast (HDF, Lonza, passages 4–10)**：in vitro 毒性測試主用細胞，1×10⁵ cells/well 接種 24-well 盤。
   - **Transwell insert**：底部有小孔膜的掛籃，材料碰不到細胞、只讓可溶性物質擴散，排除壓力 / 滲透 / 缺氧偽陽性。
   - **LIVE/DEAD Viability/Cytotoxicity Kit**：calcein AM 染活細胞（綠）+ ethidium homodimer-1 染死細胞（紅）；ImageJ 數活/總得存活率。
   - **PrestoBlue**：resazurin → resorufin 還原型代謝指標，Ex 540 / Em 590 nm 讀亮度量整體 metabolic activity。
   - **C2C12 mouse myoblast (ATCC CRL-1772)**：肌肉再生標準前驅細胞；3×10⁶ cells/ml 混入 alginate US-ink 做細胞列印 7 天追蹤。
   - **8.75 MHz / 7 W / 10 mm min⁻¹**：cell-laden 列印的「低功率中速」參數，犧牲解析度換 cell viability。
   - **T24 膀胱癌細胞 + 3D spheroid**：Greiner Bio-One cell-repellent 96-well 培養 5 天聚成球體，模擬腫瘤立體擴散。
   - **MB49 鼠膀胱癌 + C57BL/6J orthotopic model**：同系免疫競爭小鼠原位腫瘤模型，可看本體免疫與抗腫瘤效果。
   - **BD Intima II IV catheter (0.7 × 19 mm)**：經尿道灌注 200 μl 含 240 pM GV 的 alginate US-ink 至小鼠膀胱。
   - **H&E 染色**：haematoxylin 染核藍紫 + eosin 染細胞質粉紅；看整體組織結構與壞死。
   - **F4/80 + CD80 immunofluorescence**：F4/80 看 macrophage 數量、CD80 看活化狀態，DAPI 染核當底色，判讀免疫反應。
   - **1 週 / 4 週兩時間點**：對應巨噬細胞招募高峰（亞急性）與纖維包膜 + 降解產物累積（慢性）。
   - **New Zealand white rabbit + customized cone**：兔大腿深層肌肉模型；cone 內裝 degassed water + ultrasound-transparent membrane 當聲學耦合柱。
   - **三段式麻醉**：acepromazine SQ 鎮靜 → ketamine + xylazine IM 誘導 → isoflurane 吸入維持，確保動物不動。
   - **IACUC protocol IA23-1810 / IA23-1859 / IA24-1904**：Caltech 動物實驗倫理規範，所有動物實驗依此執行。
5. 與此篇文章的關係: 
   在《Imaging-guided deep tissue in vivo sound printing》這篇文章中，作者要證明 DISP 從化學設計到列印硬體不只能在 ink tank 表演、還能進真實活體。為此他們建構了系統性生物相容性與功能驗證測試組合：用 HDF + transwell + LIVE/DEAD + PrestoBlue 確認 prepolymer 與 US-gel 兩階段毒性、用 C2C12 確認細胞被一起印出來仍能存活 7 天、用 T24 spheroid + MB49 鼠原位腫瘤確認抗癌效果、用 1 週與 4 週的 H&E + F4/80 + CD80 切片確認長期免疫反應、用兔深層肌肉模型確認穿透 15 mm 仍安全。這套測試組合是 DISP 從概念邁向臨床的安全把關，也是支撐 in vivo 列印宣稱的關鍵證據鏈。
