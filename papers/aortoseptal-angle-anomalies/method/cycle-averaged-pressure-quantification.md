# Cycle-averaged pressure quantification (週期平均壓力量化)

1. 引用自哪篇 paper: aortoseptal-angle-anomalies
2. Outline (任務主線): Cycle-averaged pressure quantification (週期平均壓力量化)
3. Method: 
心室是一個大袋子，下面接著一條相對細的出口管 (LVOT)。血液從大袋子被擠進細管時流速被迫加快，根據能量守恆，流速加快的代價就是『流體推牆壁的壓力 (static pressure) 變低』——這個窄口靜壓掉下去的現象叫 Venturi 效應。AoSA 平緩 (160°) 時射流方向和 LVOT 軸幾乎平行，血流順順地通過窄口；AoSA 變陡 (≤130°) 後射流和出口軸出現急轉彎，血液被擠偏到 LVOT 上緣並在轉折處被擠得更急、流速更快，所以 LVOT 整段的時間平均壓力被吸得越低。
要把這個壓力下降量化，作者在內腔表面挑每一個點，把它從心跳開始 (t=0) 到結束 (t=T) 每一個瞬間量到的壓力 p 全部加起來、再除以 T，得到該位置的週期平均壓力 $p_{\mathrm{ave}} = \frac{1}{T}\int_{0}^{T} p\,dt$。同樣的算法在內腔每一個位置都跑一次，就能畫出整面內壁的『時間平均壓力地圖』。
但要在四個 AoSA 模型之間直接比較，光有 $p_{\mathrm{ave}}$ 還不夠：AoSA 越陡整段壓力都會下降一截，如果四張圖各自上色，色階各自拉到自己的範圍，看起來顏色都差不多，『誰真的比較低』反而看不出來。作者改採『四張共用一支尺』的線性標準化：$\hat{p}_{\mathrm{ave}} = \frac{p_{\mathrm{ave}} - p_{\mathrm{ave,min}}}{p_{\mathrm{ave,max}} - p_{\mathrm{ave,min}}}$，分母的 max/min 取『四個模型整體一起算』而不是每個模型自己，所以每一點的 $\hat{p}_{\mathrm{ave}}$ 落在 0 (整體最低) 到 1 (整體最高) 之間。如果用每個模型自己的 max/min，每張圖最高都會被拉成 1、最低都被拉成 0，看起來『一樣強』但其實絕對量級差很多——LVOT 局部 (例如 inferior 區 > 22% 下降、superior 區 > 130% 上升) 的差異會在視覺上被壓平，根本看不見。共用尺後這些區域差異才會浮出來。
4. 工具與材料: 
- **Venturi 效應**: 流體經過縮窄通道時流速被迫加快、靜壓相應下降的現象；LVOT 變窄變彎會強化此效應。
- **週期平均壓力 ($p_{\mathrm{ave}}$)**: 內腔表面某點瞬時靜壓 p 沿一個心動週期 [0,T] 做時間平均，畫出整面內壁的時間平均壓力地圖。
- **線性標準化 ($\hat{p}_{\mathrm{ave}}$)**: 以全部四個 AoSA 模型聯集的整體 max/min 當分母做線性縮放，讓 0=整體最低、1=整體最高，使跨模型比較有意義。
5. 與此篇文章的關係: 
在《Significance of aortoseptal angle anomalies to left ventricular hemodynamics and subaortic stenosis》這篇文章中，作者要回答『AoSA 變陡是否會在 LVOT 製造 SAM 相關的負壓』。他們在每個內壁節點算出 $p_{\mathrm{ave}}$，再以四模型整體 max/min 做線性標準化 $\hat{p}_{\mathrm{ave}}$，把不同 AoSA 模型的絕對量級拉到同一支色階。這一步把節點追蹤產出的時間序列壓力資料，轉成 Fig. 4A/Fig. 5A 那種可直接視覺比較與分區量化的標準化地圖。
