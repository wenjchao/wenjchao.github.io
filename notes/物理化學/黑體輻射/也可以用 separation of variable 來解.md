# 也可以用 separation of variable 來解

## 內文
此處以 $E_y$ 為例，$E_x$ 和 $E_z$ 就以此類推

$(\frac{\partial^2}{\partial x^2} + \frac{\partial^2}{\partial y^2} + \frac{\partial^2}{\partial z^2} ) E_y = \frac{1}{c^2} \frac{\partial^2 E_y}{\partial t^2}$

利用 separation of variable，令 $E_y = X(x)Y(y)Z(z)T(t)$ 的組合

且因為是波動方程，因此設 $T(t) = e^{i\omega t}$

$YZT\frac{\partial^2 X}{\partial x^2} + XZT \frac{\partial^2 Y}{\partial y^2} + XYT\frac{\partial^2 Z}{\partial z^2} = \frac{-\omega^2}{c^2}XYZT$

⇒ $\frac{1}{X(x)}\frac{\partial^2 X(x)}{\partial x^2} + \frac{1}{Y(y)}\frac{\partial^2 Y(y)}{\partial y^2} + \frac{1}{Z(z)}\frac{\partial^2 Z(z)}{\partial z^2} = \frac{-\omega^2}{c^2}$

令 $\begin{cases} \frac{1}{X(x)}\frac{\partial^2 X(x)}{\partial x^2} = -k_x^2\\ \frac{1}{Y(x)}\frac{\partial^2 Y(y)}{\partial y^2} = -k_y^2 \\ \frac{1}{Z(z)}\frac{\partial^2 Z(z)}{\partial z^2} = -k_z^2 \end{cases}$ 則有 $\begin{cases} X(x) = A_xe^{ik_xx} + B_xe^{-ik_xx}\\ Y(y) = A_ye^{ik_yy} + B_ye^{-ik_yy} \\ Z(z) = A_ze^{ik_zz} + B_ze^{-ik_zz} \\ k_x^2 + k_y^2 + k_z^2 = \frac{\omega^2}{c^2} \end{cases}$
