# 哈密頓主函數 S 的物理意義：最小作用量

## 內文
1. 把它對時間求導：$\frac{d S(q,P,t)}{d t} = \frac{\partial S}{\partial t} + \sum_j \frac{\partial S}{\partial q_j}\dot q_j + \sum_j\frac{\partial S}{\partial P_j}\dot P_j$
2. $\frac{\partial S}{\partial t} = -H$，$\frac{\partial S}{\partial q_j} = p_j$，$\dot P_j = 0$
   ⇒ $\frac{d S(q,P,t)}{d t} = -H + \sum_j p_j\dot q_j =  \sum_j p_j\dot q_j-H =L$
   ⇒ $S(q,P,t) = \int L dt$
   ⇒ $S(q,P,t)$ 其實即為最小作用量原理的**<u>最小作用量</u>**，$\delta S = 0$

- $S_0(q,P)= \sum_j p_jd q_j$ 則為**<u>簡約作用量</u>**，即若此系統滿足能量守恆，則 $\delta S_0 = 0$
- 另定義**<u>絕熱不變量</u>** $I_j= \frac{1}{2\pi}\oint p_jdq_j$即為週期運動在單一週期內相空間上的的相積分 ⇒ 即若此系統滿足能量守恆，或是能量（哈密頓量）改變得很慢，則絕熱不變量亦守恆
