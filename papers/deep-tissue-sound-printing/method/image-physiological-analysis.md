# 影像處理與生理訊號分析（ImageJ、MATLAB filter、IR 量測）

1. 引用自哪篇 paper: deep-tissue-sound-printing
2. Outline (任務主線): 影像處理與生理訊號分析（ImageJ、MATLAB filter、IR 量測）
3. Method: 
   細胞先用 Live/Dead 雙螢光染色：calcein AM 進入活細胞、被「活細胞才有的酯酶」(esterase) 切掉掩護基後變成極性的綠色 calcein 困在細胞質、發強綠螢光；ethidium homodimer-1 是雙正電荷大分子，活細胞的完整脂膜會擋住它，只有膜破的死細胞會讓它鑽進 DNA 雙螺旋中間發紅螢光。螢光顯微鏡下就是一張「活綠、死紅」的合成圖。然後在 ImageJ（一個「開源生物影像分析軟體」）裡做閾值分割：分別把綠通道、紅通道二值化（比閾值亮的歸為訊號），用 particle analyzer 自動數白點個數，得到「活細胞數」與「死細胞數」，存活率 = live / (live + dead)。整個流程把「視覺判斷」變成「自動可重現的計數」。
   
   心臟與肌肉細胞會在皮膚上產生 mV 等級的電位變化，這就是心電圖 (electrocardiogram, ECG) 與肌電圖 (electromyography, EMG)。作者把含 CNT 的 conductive US-gel 直接印在皮膚上當電極：ECG 在左右手各貼一個工作電極、腿上貼參考；EMG 兩個工作電極貼 biceps brachii（手臂二頭肌）兩端、腿上貼參考。電極接到「開源生物電位讀取板」(SparkFun AD8232)，這片板上的儀器放大器把兩電極的電位差放大、初步濾波，輸出數位訊號到電腦。電腦端用 MATLAB 套一個「過濾掉 50 Hz 工頻干擾的數位濾波」(50 Hz low-pass filter)——家用電源在台灣與歐洲是 50 Hz 交流，會透過電容耦合在量測線路上留下 mV 級正弦振盪，而 ECG 的 P-QRS-T 波形只有幾百 μV，不濾掉就什麼都看不到。
   
   感測器要當「量尺」用，就得先建立校正曲線。線寬–電阻校正：金屬導體電阻 $R = \rho L / A$，作者把長度固定 10 mm、厚度固定 1 mm，使截面積 $A$ 與線寬 $w$ 成正比，理論上 $R \propto 1/w$。實作上印出不同寬度的 conductive US-gel 線條，用 CHI 660E electrochemical station 兩探針施加 1 V 量電流推電阻；$1/R$ 對 $w$ 畫圖呈線性（fig. S20C），就成了「想做多大電阻、查圖印多寬」的工程查表。溫度–電阻校正：把 conductive US-gel 放在 hot plate 上 20 → 70 °C，用「紅外線溫度計」(IR thermometer) 非接觸量表面溫度（避免接觸探針把熱量帶走），同時兩探針量電阻，配成「溫度 vs 電阻」校正曲線。未來貼皮膚量到電阻就能反推溫度。
   
   影像端若 ImageJ 閾值設太高會漏算較暗的活細胞、設太低又會把螢光背景算成細胞，同一張圖存活率可以從 95% 跳到 60% 或飆到 100%——整個 cell viability 結論被閾值決定，而非真實生物結果。最低要求是「同實驗組所有照片用同一個閾值」，且閾值先在『明顯活/明顯死』的對照片上校好。訊號端若不做 50 Hz low-pass，ECG 的 QRS 波形會被工頻干擾完全淹沒，從原始訊號根本看不出心跳，更別說『conductive US-gel 訊號品質可媲美商用電極』這種比較性結論——所有『我們的感測器很準』的圖都是後處理的結果，沒做後處理就拿原始訊號去比較毫無意義。
4. 工具與材料: 
   - **ImageJ**：開源生物影像分析軟體，作者用其閾值分割與 particle analyzer 自動數活/死細胞個數。
   - **Live/Dead 雙螢光染色**：calcein AM（活細胞變綠）+ ethidium homodimer-1（死細胞核變紅）的標準細胞存活率量測。
   - **SparkFun AD8232 ECG/EMG shield**：開源生物電位讀取板，內建儀器放大器與初步濾波，把皮膚電極差分訊號數位化輸出。
   - **50 Hz low-pass filter**：在 MATLAB 端套用的數位低通濾波，消掉家用電源 50 Hz 工頻干擾，才能看到 mV 級 ECG/EMG 波形。
   - **IR thermometer**：紅外線溫度計，用物體表面紅外輻射換算溫度；非接觸量測，避免探針把薄膜熱量帶走。
   - **CHI 660E electrochemical station**：電化學工作站，作者用兩探針 amperometry（1 V 施加、量電流）量印製線寬與電阻關係。
   - **Ri-Cdl ‖ Rp-CPEp 等效電路**：把 US-gel 的阻抗譜擬合成 ionic resistance + double-layer capacitor 並聯 polarization resistance + constant phase element，從 Nyquist plot 萃取材料電性參數（fig. S21）。
5. 與此篇文章的關係: 
   在《Imaging-guided deep tissue in vivo sound printing》這篇文章中，作者為了把細胞存活率、ECG/EMG 波形品質、線寬–電阻關係與溫度感測效能變成可重現的數字，採用了 ImageJ、SparkFun AD8232 + MATLAB 50 Hz low-pass filter、IR thermometer 與 CHI 660E 兩探針 amperometry 這套後處理工具鏈。它解決了「螢光照片、原始 ECG、感測器原始電阻」無法直接拿來互相比較的瓶頸：吃進各類原始量測，輸出存活率%、乾淨 P-QRS-T 波形、$R$–$w$ 與 $R$–$T$ 校正曲線，直接為論文圖 4 的功能性 US-gel 表徵與圖 5 的活體生物相容性結論提供量化基礎。
