# 內能 U 的展開

## 內文
1. 對於某系統而言，其內能的變化 dU 可以寫成 S、V、N 三個變數的偏微分展開
   $$
   dU = \left⟮\frac{\partial U}{\partial S}\right⟯_{V,N}dS +\left⟮\frac{\partial U}{\partial V}\right⟯_{S,N}dV + \left⟮\frac{\partial U}{\partial N}\right⟯_{S,V}dN
   $$
   - 右下角的小標代表必須固定的物理量（這樣才叫偏微分） ex: $\left⟮\right⟯_{V}$ 代表定容
2. 又因為 $dS = \frac{1}{T}dU +\frac{P}{T}dV - \frac{\mu}{T} dN$ ⇒
   $$
   dU = TdS  - PdV + \mu dN
   $$
   - 如果此系統有很多種物質，則應該把 $\mu dN$ 換成 $\sum \mu_i dN_i$
3. 一一對應之後可以發現
   1. $T = \left⟮\frac{\partial U}{\partial S}\right⟯_{V,N}$
   2. $P = -\left⟮\frac{\partial U}{\partial V}\right⟯_{S,N}$
   3. $\mu = \left⟮\frac{\partial U}{\partial N}\right⟯_{S,V}$
