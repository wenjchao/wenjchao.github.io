# 旋轉：兩觀察系間有角速度 $\vec{\omega_0 } =\frac{d}{dt}\theta(t)$

## 內文
- 注意：
  - 在二維平面上，角速度 ω 是純量（贗純量，即在鏡子中會正負顛倒的純量）。
  - 在三維空間中，角速度 ω 則是向量，方向根據右手定則指向轉軸（贗向量，即在鏡子中方向會反過來的向量 ex: 磁場）

1. 某物 m 在兩觀察系中的位置 $\vec {r_{慣}} = \vec {r_{非慣}}$
2. 某物 m 在兩觀察系中的速度分別為 $\vec {v_{慣}}$ & $\vec {v}_{非慣}$ ⇒ $\vec {v_{慣}}= \vec {v_{非慣}}+\vec{\omega}\times \vec r$
3. 某物 m 在兩觀察系中的加速度分別為 $\vec {a_{慣}}$ & $\vec {a}_{非慣}$ ⇒ $\vec {a_{慣}} = \frac{dv}{dt} = \vec{\omega}'\times \vec r + {\omega}^2\vec r+ 2*\vec{\omega}\times \vec {v_{非慣}}+ \vec {a_{非慣}}$

   [[旋轉：兩觀察系間有角速度 vecomega0 =fracddttheta(t)/2. & 3. 的證明|摘要]]
4. 慣性系 S 中 $\vec{F}= m\vec {a}_{慣} = m(\vec{\omega}'\times \vec r + {\omega}^2\vec r+ 2*\vec{\omega}\times \vec {v}_{非慣}+ \vec {a}_{非慣})$ 等式自然成立
5. 非慣性系 S’ 中
   $\vec{F} \ne m\vec {a}_{非慣}\xRightarrow{怎麼辦} \vec{F} +(- \vec{\omega}'\times \vec r - {\omega}^2\vec r- 2*\vec{\omega}\times \vec {v}_{非慣}) = m\vec {a}_{非慣}$
   新增三個假想力 $- \vec{\omega}'\times \vec r$、$- {\omega}^2\vec r$、$- 2*\vec{\omega}\times \vec {v_{非慣}}$，這樣等式就成立了
6. $- \vec{\omega}'\times \vec r$ 稱為 **歐拉力**，與角速度的變化成正比，若角速度 $\vec{\omega }$ 不變則歐拉力 = 0
7. $- {\omega}^2\vec r$ 稱為 **慣性離心力**，與角速度的平方成正比，方向向外
8. $- 2\vec{\omega}\times \vec {v}_{非慣}$ 稱為 **科里奥利力（科氏力）**，如果在地球北半球 ⇒ $\vec{\omega }$ 方向朝向北極星 ⇒ $\vec{\omega}\times \vec {v}_{非慣}$ 方向自己推（基本上就是往 $\vec {v}_{非慣}$ 右邊）
