# 流體的**局部導數 vs 本體導數**

## 內文
對於連續體質元的某個物理量 u 而言 (ex: 溫度、速度、密度…，可以是向量 or 純量)，因為該質元的位置會一直變化，因此若想了解該物理量如何變化，有兩種描述方法：

1. **<u>局部導數</u>**（歐拉表述）：鎖定某個位置，看當下該位置的物理量變化，記作 $\frac{\partial u}{\partial t}$
   - ex: 站在路口，觀察通過路口的汽車的速度變化
2. **<u>本體導數</u>**（拉格朗日表述）：跟蹤某一質元，看當下該質元的物理量變化，記作 $\frac{d u}{d t}$
   - ex: 跟蹤某輛車，觀察此車的速度變化

兩種觀察法觀察到的速度變化不一定相同 ex: 發現通過路口的車速度越來越快，不代表每台車都越開越快

⇒ 兩者的關係為 $\frac{du}{dt} = \frac{\partial u}{\partial t} + \frac{\partial u}{\partial x}\frac{dx}{dt} + \frac{\partial u}{\partial y}\frac{dy}{dt}+ \frac{\partial u}{\partial z}\frac{dz}{dt} = \frac{\partial u}{\partial t} + (\vec v\cdot\nabla) u$

$$
⇒ \frac{du}{dt} = \frac{\partial u}{\partial t} + (\vec v\cdot\nabla) u
$$
