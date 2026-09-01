# Continuous energy level ⇒ Equipartition theorem $\langle E\rangle = \frac{1}{2} kT$﻿

## 內文
1. 前提假設：
   1. Additive energy：每個 component of energy 彼此獨立，相加即為總 energy
      - 現實：經常有 coupled energy ex: Non-Ideal Gases（某粒子位能與其他分子的位置有關）, Coupled Oscillators（原子之間有鍵結減少自由度）, Quantum Systems
   2. Energy in Quadratic form：能量可以寫成 $E = ax^2$，其中 x 為某物理量，例如動能 $\frac{1}{2}mv^2$，彈力位能 $\frac{1}{2}kx^2$
      - 現實：重力位能 $E = \frac{-GMm}{r}$ 不適用，要改用 Virial Theorem
2. 所求平均能量 $\langle E \rangle$ 即為
   $$
   \langle E \rangle = \int_{-\infin}^{\infin} E(x)p(x)dx= \frac{\int_{-\infin}^{\infin}(ax^2)e^{-ax^2/k_BT}dx}{\int_{-\infin}^{\infin}e^{-ax^2/k_BT}dx}
   $$
   其中 $p(x) = \frac{e^{-E(x)/k_BT}}{\int_{-\infin}^{\infin}e^{-E(x)/k_BT}dx}$，$e^{-E(x)/k_BT}$ 為 Boltzmann factor
   - 注意：之所以用 dx 而非 dE 是因為我們是 sum up over all possible microstate，而每個 microstate 是用 position 或是 velocity 來認定而非 energy
3. 分別計算分子分母的高斯積分：
   $$
   \frac{\int_{-\infin}^{\infin}(ax^2)e^{-ax^2/k_BT}dx}{\int_{-\infin}^{\infin}e^{-ax^2/k_BT}dx} = \frac{\frac{k_BT}{2}\sqrt{\frac{k_BT\pi}{a}}}{\sqrt{\frac{k_BT\pi}{a}}} = \frac{1}{2}k_BT
   $$
   即所有 component of energy 都有平均能量 $\langle E \rangle = \frac{1}{2}k_BT$
