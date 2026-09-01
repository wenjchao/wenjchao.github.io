# 輸送現象 Transport phenomena ：經驗公式

## 內文
1. 粒子擴散：$J_n = -D \frac{\partial \rho_n}{\partial x}$ （即 Fick’s law）
   1. $J_n = \rho_n v$ 為數量通量
   2. $\rho_{n}$ 為空間中的數量密度
   3. 擴展為三維的話則寫作 $J = -D \nabla \rho_{n}$
   4. 等式兩邊同時再取散度：$\nabla \cdot J_n = -D \nabla^2 \rho_n$
      又因為粒子質量守恆（連續性原理），即 $\frac{\partial \rho_n}{\partial t} + \nabla \cdot (\rho_n \vec v) =0$
      ⇒ $\frac{\partial \rho_n}{\partial t} = D \nabla^2 \rho_n$
2. 能量擴散：$J_E = -\kappa \frac{\partial T}{\partial x}$ （即 Fourier's law）
   1. $J_E$ 為能量通量
   2. 擴展為三維的話則寫作 $J = -\kappa \nabla T$
   3. 再對空間微分，亦可寫成 $\frac{\partial T}{\partial t} = D \nabla^2 T$
3. 動量擴散：$J_p = -\eta \frac{\partial v_y}{\partial x}$（即 Newton’s law of viscosity）
   1. $J_p$ 為動量通量，亦即為剪應力 $\tau$
   2. $\eta$ 為 **<u>黏度 viscosity</u>**
4. 液體在多孔物質中的擴散：$J_q = -\frac{k}{\mu} \nabla p$（Darcy's law）
   1. $J_q$ 為體積通量，即巨觀下的流速
   2. k 為 peramability，滲透率。如果是有方向性的物質則 k 也有方向性
   3. $\mu$ 為 **<u>黏度 viscosity</u>**
   4. p 為壓力
