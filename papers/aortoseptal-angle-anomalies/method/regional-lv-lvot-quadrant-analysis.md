# Regional LV-LVOT quadrant analysis (LVOT 四象限分區量化)

1. 引用自哪篇 paper: aortoseptal-angle-anomalies
2. Outline (任務主線): Regional LV-LVOT quadrant analysis (LVOT 四象限分區量化)
3. Method: 
LV-LVOT 接合處是出口圓管最靠近心室的一圈。作者在這一圈上依解剖方位畫四等分線——上 (superior，靠近主動脈那一側)、下 (inferior，貼著心室中膈那一側，也是 DSS 病灶幾乎都長出來的位置)、前 (anterior)、後 (posterior)，每個象限是這圈圓周上的一塊弧形壁面區域。把該象限所有壁面節點的四個指標 ($\hat{p}_{\mathrm{ave}}$、OSI、TSM、$\left|\mathrm{WSSdiv}\right|$) 在象限內取平均，得到一個代表該象限的數字；再把四個 AoSA 模型 (160°/145°/130°/115°) 同一象限的數字並排，以 160° baseline 為基準算其他模型的百分比變化。例如在 ≤130° 模型，inferior LVOT 的 TSM 比 160° 增加超過 45%、$\left|\mathrm{WSSdiv}\right|$ 下降超過 66%——一個下方象限就同時抓到兩個指標的強烈變化，且都集中在 DSS 好發位置。
為什麼變化會『特別集中』在 inferior 象限？AoSA 接近 160° 時 jet 跟 LVOT 軸幾乎同向，順流出去；AoSA 變陡到 ≤130° 後 jet 被擠歪、偏向出口的 superior 側，但接下來的下游正是 inferior 象限——jet 撞偏後在這裡形成 recirculation bubble，貼壁的剪應力既高 (TSM 升高) 又集中朝同一個 fixed point 擠壓 (|WSSdiv| 下降)。換句話說，inferior 是『jet 偏向 superior』與『下游打轉』兩個效應的會合點，所以變化最劇烈也最具特異性。
為什麼一定要分四象限而不是整段平均？因為整段平均會把 inferior 的劇烈變化 (TSM +45%、|WSSdiv| -66%) 跟 anterior/posterior 那些沒明顯變化甚至反向變化的位置稀釋掉。本研究還觀察到 posterior LVOT 反而出現 WSS expansion (>57% 增加)、跟 inferior 的 contraction 方向相反——放在一起平均直接互相抵消。分四象限後，inferior 的高 TSM + 強收縮特徵 (與 DSS 好發位置幾乎完全共定位) 才能浮上來。為什麼是四塊而不是兩塊或八塊？兩塊太粗，inferior 跟 anterior/posterior 又被合在一起、特異性鈍化；八塊太細，每塊節點少、平均統計噪音大、跨模型差異可能不顯著。四象限對應到解剖學上『前後、上下』的最自然分法，既能保留 inferior 特異性、又每塊節點數夠多，是 anatomically meaningful 與 statistically meaningful 的折衷。
4. 工具與材料: 
- **LV-LVOT junction quadrant partition**: 把出口圓管最靠近心室的一圈依解剖方位切成四塊弧形壁面區域。
- **Superior quadrant**: 上方象限，靠近主動脈那一側；陡 AoSA 模型在這裡量到 jet 偏向與 $\hat{p}_{\mathrm{ave}}$ 增加 >130%。
- **Inferior quadrant**: 下方象限，貼著心室中膈，也是 DSS 病灶臨床上最常長出來的位置；陡 AoSA 模型 TSM +45%、|WSSdiv| -66%。
- **Anterior / posterior quadrant**: 前/後兩個象限，分別呈現不同的 WSS 與壓力變化趨勢 (例如 posterior 出現 WSS expansion >57%)。
- **Per-quadrant averaging of $\hat{p}_{\mathrm{ave}}$ / OSI / TSM / $\left|\mathrm{WSSdiv}\right|$**: 把整張壁面 map 在每個象限內各取一個平均值，得到代表該象限的單一數字。
- **% change vs 160° model**: 以最鈍的 160° AoSA 為 baseline，計算其他三個陡角模型同一象限指標的百分比變化。
5. 與此篇文章的關係: 
在《Significance of aortoseptal angle anomalies to left ventricular hemodynamics and subaortic stenosis》這篇文章中，作者為了證明 AoSA 變陡『特異地』加重 DSS 好發位置 (inferior LVOT)，採用了 LV-LVOT 接合處的四象限分區量化。它解決了整段 LVOT 平均會把 inferior 劇烈變化跟 anterior/posterior 反向變化互相抵消的瓶頸；它吃進前面所有壁面指標 ($\hat{p}_{\mathrm{ave}}$、TSM、OSI、$\left|\mathrm{WSSdiv}\right|$) 的 map，產出 Fig. 5 的象限百分比變化柱狀圖，直接支持 inferior LVOT TSM +45%、|WSSdiv| -66% 與 DSS 病灶共定位的核心結論。
