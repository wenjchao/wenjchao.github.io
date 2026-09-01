# 勒壤得變換（Legendre transformation）：如何變換函數的自變量

## 內文
1. 對於任意二元函數 $F(x,y)$ 而言，F 隨著 x & y 的變化而變化，即 $dF =\frac{\partial F}{\partial x}dx + \frac{\partial F}{\partial y}dy$
2. 如果想把自變數 x & y 換掉，則可以定義兩個新函數 P & Q：$P = \frac{\partial F}{\partial x}，Q=\frac{\partial F}{\partial y}$，此時 $\frac{\partial P}{\partial y} = \frac{\partial Q}{\partial x} =\frac{\partial^2 F}{\partial x\partial y}$
   1. $dF =\frac{\partial F}{\partial x}dx + \frac{\partial F}{\partial y}dy = Pdx+Qdy$
   2. $d(Px) = xdP + Pdx$
3. 定義新函數G使 $dG = d(F-Px) = Pdx+Qdy -xdP - Pdx = Qdy -xdP$
   ⇒ 變換完成，成功把 x 換成 P ，此時函數 G 變成自變量 P & y 的函數
