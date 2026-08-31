# Mean Opening Time & Mean Closing Time

## 內文
對於 $\ce{ ? + C <=>[v_{open}][v_{close}] O + ?}$ 這個反應而言

1. mean opening time：每次打開的 duration 的平均，$=\tau = \frac{1}{v_{close}}$
   - 因為 mean opening time 就是 $\int_0^\infin e^{-v_{close}t}$ 積分，所以 $=\tau = \frac{1}{v_{close}}$
2. mean closing time：每次關起來的 duration 的平均，$=\tau = \frac{1}{v_{open}}$
3. 之所以用反應左右有兩個問號，是因為這裡不限定反應的種類，可以是 Voltage gated（無額外反應物）、Ligand gated（左邊加 Ligand）、Blocker gated（右邊加 Blocker）
4. <u>促進 channel 打開</u> & <u>阻止 channel 關閉</u> 有什麼不一樣？
   1. 促進 channel 打開是增加 $v_{open}$ ，阻止 channel 關閉是減少 $v_{close}$
   2. 如果系統平衡，則顯然平衡常數 $K = \frac{O}{C}=\frac{v_{open}}{v_{close}}$
   3. 就算兩系統 K 相等，即 Opening probability 固定，但
      1. 當 $v_{open}$ & $v_{close}$ 大時，mean opening time & mean closing time 都很小（一直開開關關）
      2. 當 $v_{open}$ & $v_{close}$ 小時，mean opening time & mean closing time 都很大（一直開或是一直關）
