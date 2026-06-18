# FRET 效率計算

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): FRET 效率計算
3. Method: 
   FRET (螢光共振能量轉移) 描述兩個螢光分子靠得很近 (距離小於 10 nm) 時的能量接力現象。用 460 nm 雷射激發供體 (donor, NBD-PE)，供體本該發出 530 nm 的綠光；但若旁邊就有個受體 (acceptor, Liss Rhod-PE)，能量會「直接 (非輻射)」傳給受體，由受體發出 588 nm 的紅光。所以兩者貼很近時，看到的是紅光強、綠光弱；一旦距離被拉開超過 10 nm，能量傳不過去，綠光就回升、紅光下降。為什麼對距離特別敏感？因為 FRET 效率對距離是六次方依賴：$E = R_0^6 / (R_0^6 + r^6)$，其中 R_0 是 Förster radius，大約 5 nm。r 從 5 nm 拉到 10 nm，效率就從 50% 掉到 ~1.6%——奈米級的距離變化被放大成劇烈的訊號變化，剛好適合偵測「兩個磷脂分子是否還在同一片膜上」這種小於 10 nm 的事件。

   FRET 效率公式 $\eta = F_{588} / (F_{588} + F_{530}) \times 100$ 是工程上非常聰明的設計。如果只看 588 nm 的絕對發射強度，會受樣本總濃度、儀器漂移、孔板雜訊干擾，跨樣本不能比較；把 $F_{588}$ 除以 $(F_{588} + F_{530})$ 後得到的是「紅光佔總發射的比例」——分母同時吸收了上述系統性偏差，分子分母同步漂移時相抵掉，最後得到的無單位百分比可以跨樣本直接比較。為什麼選 NBD-PE 跟 Liss Rhod-PE 這個配對？有三個理由：(1) NBD 發射峰 ~530 nm 跟 Rhod 激發峰 ~570 nm 有大量重疊 (spectral overlap)，這是 FRET 發生的前提；(2) Förster radius ~5 nm 剛好對應磷脂雙層的厚度，同膜兩分子能 FRET、不同膜兩分子立刻 FRET 斷掉，靈敏度剛剛好；(3) 兩種染料都掛在 PE 頭，可以直接當磷脂的一員插進雙層、不會破壞膜結構。

   FRET 量測有兩個關鍵的潛在陷阱。第一是染料必須真的插進 Lip 雙層：作者用 2% (w/w) 把 NBD-PE 與 Liss Rhod-PE 共溶於脂質再 sonicate 形成 Lip，並用透析或過濾去除游離染料。如果這步沒做好、染料游離在水裡，平均距離遠大於 10 nm 不會 FRET，加再多 EV 進來訊號也不會變。第二是必須做比例梯度：作者測了 Lip:EVs = 1:2、1:1、2:1 三組，看到「EV 越多 FRET 越單調下降」的劑量反應 (dose response)。如果只測一個比例，無法分辨訊號下降是融合驅動還是儀器雜訊；只有梯度的單調趨勢才能確認「真的有 EV 擠進 Lip 膜」。
4. 工具與材料: 
   - **FRET (Fluorescence Resonance Energy Transfer)**: 兩螢光分子距離 < 10 nm 時的能量接力現象，被當成奈米尺度的尺。
   - **NBD-PE (donor)**: 供體磷脂染料，激發 460 nm、發射 530 nm 綠光。
   - **Liss Rhod-PE (acceptor)**: 受體磷脂染料，接到能量後發射 588 nm 紅光。
   - **Förster radius (R_0)**: 能量傳遞效率剛好 50% 的距離，NBD/Rhod 配對約 5 nm，剛好匹配磷脂雙層厚度。
   - **FRET 效率公式**: $\eta = F_{588} / (F_{588} + F_{530}) \times 100$，無單位百分比、可跨樣本比較。
   - **Dose-response gradient (1:2, 1:1, 2:1)**: Lip:EVs 比例梯度，看 EV 越多 FRET 越單調下降的趨勢，確認訊號是融合驅動。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者要證明 EVs 與 Lip 真的發生了「膜層級融合」而非單純的物理混和。為此採用 FRET 效率指標 $\eta = F_{588} / (F_{588} + F_{530}) \times 100$，解決了「光看 size 變化無法區分融合與聚集」的瓶頸。它吃 NBD-PE / Rhod-PE 標記的 Lip + 三組比例的 EVs 進來，產出一條 EV-dose 對 FRET 效率的下降曲線，作為下游章節判定 hELs 真實融合度的量化證據。
