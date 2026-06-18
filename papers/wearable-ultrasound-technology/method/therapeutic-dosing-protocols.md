# 治療型超音波劑量學與生物耦合 (Therapeutic dosing protocols)

1. 引用自哪篇 paper: wearable-ultrasound-technology
2. Outline (任務主線): 治療型超音波劑量學與生物耦合 (Therapeutic dosing protocols)
3. Method: 
   治療型超音波與診斷型的差別在於『靠副作用做事』。聲波進入組織會產生兩條路徑的反應：機械效應 (mechanical effects) 包含聲流 (acoustic streaming，聲波推動組織液形成穩定流動) 與空蝕效應 (cavitation，溶在組織液裡的氣體被反覆拉脹擠壓變成微氣泡再破掉)，這些機械力可推細胞膜、推藥物穿屏障、輕推神經元；熱效應 (thermal effects) 來自聲波被吸收後變熱，可造成血管擴張、促進代謝、緩解疼痛。神經刺激靠機械、痛點減痛靠熱、傷口癒合兩者都用——所以治療參數要分別調節兩條路徑的比例。控制方法是四個旋鈕。頻率 (frequency) 決定穿透深度與解析度——治療通常 20 kHz 到 3 MHz。強度 (intensity) 決定每平方公分多少瓦特的能量打進組織。工作週期 (duty cycle) 控制『開多久關多久』比例避免熱累積。持續時間 (duration) 控制總劑量。四個旋鈕一起決定治療型超音波的 dose。
   傷口癒合的機制把『聲波打進組織』連到『細胞為什麼會分裂』。聲波負壓階段把溶在組織液裡的氣體拉出來形成微氣泡 (microbubble)；下一個正壓階段把氣泡擠破，瞬間產生微噴射 (microjet) 與小型震波 (shockwave) 推細胞膜、撕開細胞之間的縫隙、讓代謝旺盛起來。對纖維母細胞 (fibroblast) 來說，這些微小機械刺激被細胞膜上的力感受器讀到、訊號傳到細胞核、促進增殖與膠原蛋白沉積——細胞代謝加快、長得快，傷口就癒合得快。Ngo et al. *IEEE TUFFC* 2019 (ref. 12) 在 murine 3T3 fibroblast 上用 20 kHz、100 mW/cm² 暴露 24 小時，細胞代謝 +32% (P < 0.05)、增殖 +40% (p < 0.01) (ref. 181)。
   論文把五個治療型應用的參數窗清楚開出來。迷走神經調控 (vagus nerve stimulation) 用 1.3 MHz、~0.5 MPa 低壓聲波輕推神經元——頻率高才能聚焦頸部神經、強度低才不傷神經 (Pashaei et al. ref. 36; Fig. 4r)。經皮給藥面膜 (sonophoresis facial mask) ~10 分鐘、控制表面溫度 < 42 °C，靠聲流 + 微熱打開表皮屏障，皮膚含水量 +20%、玻尿酸加速吸收 (Li et al. *ACS Nano* 2022, ref. 11; Fig. 4s)。慢性傷口癒合 (chronic wound healing) 用 20–100 kHz、SPTA = 100 mW/cm²、每次 ≤ 15 分鐘（可累積至 4 小時無不良反應）——低頻才有強烈空蝕、低強度長時間累積，把人類傷口癒合時間從 12 週縮到 4.7 週 (Ngo et al. *IEEE TUFFC* 2019, ref. 12; Fig. 4p)。骨折癒合 (bone consolidation) 在大鼠股骨用可拉伸陣列、1 MHz、15 V、每天 25 分鐘 × 6 週，模量 +615%、骨密度 +30.2%、骨體積比 +39.4%、trabecular thickness +35.7% (Zhou et al. ref. 182)；Exogen 刺激器用 SPTA 30 mW/cm²、每天 20 分鐘 × 3 月，14 位 non-union 患者中 79% 達成骨癒合 (Lewis et al. ref. 183)。痛點減敏走另一條路：持續式聲波治療 (sustained acoustic medicine, sam) 每次 > 4000 J 的累積能量送到皮下 5 cm，靠長時間低強度累積熱劑量引發血管擴張與神經減敏；elbow tendinopathy 患者 6 週 NRS 疼痛分數下降 3.94 ± 2.15 點 (P = 0.004) (Best et al. *Phys. Sportsmed.* 2015, ref. 13; Fig. 4q)。Wound healing 靠 mechanical、pain relief 靠 thermal，效應路徑完全不同。
   整套劑量學被 FDA 兩條硬底線框住。第一條是去衰減的空間峰值時間平均強度 (derated spatial-peak temporal-average intensity, SPTA) ≤ 720 mW/cm² (ref. 200)——derated 是把組織衰減算進去後的等效強度，超過這條線熱能累積太快會直接燙傷組織。第二條是機械指數 (mechanical index, MI) ≤ 1.9 量化空蝕效應的破壞潛力——過高會讓 cavitation 失控撕裂組織；眼科應用更嚴 ≤ 0.23 因為眼睛無法承受 cavitation。論文 Supplementary Tables 3 & 4 還提供熱指數 (thermal index, TI) 對應 dwell time 的對照表 (ref. 66)，讓設計者把『打多久要停下來』直接讀出來。這套劑量學表格化設計是治療型 wearable 從『實驗室原型』變成『可家用裝置』的工程護欄。
4. 工具與材料: 
   - **Mechanical effects**: 機械效應；聲流 + 空蝕效應產生的機械力，可推細胞膜、推藥物穿屏障、輕推神經元放電。
   - **Acoustic streaming**: 聲流；聲波在組織中推動液體形成穩定流動，是 sonophoresis 推動分子穿過皮膚屏障的主要機制之一。
   - **Cavitation**: 空蝕效應；溶於組織液裡的氣體被反覆拉脹擠壓變成微氣泡 (microbubble) 再破掉，瞬間 microjet 與 shockwave 推細胞膜、撕開細胞縫隙。
   - **Thermal effects**: 熱效應；聲波被組織吸收後變熱，可造成局部血管擴張、促進代謝、緩解疼痛，是 sam 痛點減敏的主機制。
   - **Duty cycle**: 工作週期；發聲 on/off 比例，用來控制熱效應累積避免燙傷組織。
   - **Vagus nerve stimulation**: 迷走神經調控；用 1.3 MHz、~0.5 MPa 低壓聲波輕推頸部神經元 (Pashaei et al. ref. 36; Fig. 4r)。
   - **Sonophoresis**: 經皮給藥；用聲流 + 微熱打開表皮屏障讓保養品/藥物分子穿入真皮層 (Li et al. *ACS Nano* 2022, ref. 11; Fig. 4s)。
   - **Chronic wound healing**: 慢性傷口癒合貼片；20–100 kHz、SPTA = 100 mW/cm²、每次 ≤ 15 分鐘，把癒合時間從 12 週縮到 4.7 週 (Ngo et al. *IEEE TUFFC* 2019, ref. 12)。
   - **Bone consolidation**: 骨折癒合；1 MHz、每天 25 分鐘 × 6 週的可拉伸陣列在大鼠股骨模型把骨密度 +30.2%、模量 +615% (Zhou et al. ref. 182)。
   - **Sustained acoustic medicine (sam)**: 持續式聲波治療；每次 > 4000 J 累積熱劑量送到皮下 5 cm，引發血管擴張與神經減敏，6 週 NRS 疼痛分數下降 3.94 點 (Best et al. ref. 13; Fig. 4q)。
   - **Derated SPTA**: 去衰減的空間峰值時間平均強度；FDA 上限 720 mW/cm²，超過會熱燙傷組織 (ref. 200)。
   - **Mechanical index (MI)**: 機械指數；量化 cavitation 破壞潛力，FDA 上限 1.9，眼科 ≤ 0.23。
   - **Thermal index (TI)**: 熱指數；對應 dwell time 的安全表 (論文 Supplementary Tables 3 & 4, ref. 66)，把『打多久要停』直接讀出。
5. 與此篇文章的關係: 
   在《Wearable ultrasound technology》這篇 Review 中，作者為了把治療型超音波從醫院的高強度單次治療，轉成貼片可以在家連續長時做的低強度劑量學，整理了 frequency / intensity / duty cycle / duration 四個旋鈕、五個應用的代表參數窗（vagus stimulation、sonophoresis、wound healing、bone consolidation、pain relief），並用 FDA derated SPTA、MI、TI 三條安全上限把整套劑量學表格化。這套劑量地圖是治療型 wearable 從『實驗室原型』走向『家用裝置』的安全工程基礎，也接續了 2-D 機械架構（可拉伸陣列）與 2-E 後端電路（therapeutic ASIC）兩條工程鏈。