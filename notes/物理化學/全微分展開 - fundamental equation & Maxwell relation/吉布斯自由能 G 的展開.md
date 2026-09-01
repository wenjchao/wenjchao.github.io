# 吉布斯自由能 G 的展開

## 內文
1. 對於某系統而言，其自由能的變化 dG 可以寫成 T、P、N 三個變數的偏微分展開
   $$
   dG = \left⟮\frac{\partial G}{\partial T}\right⟯_{P,N}dT +\left⟮\frac{\partial G}{\partial P}\right⟯_{T,N}dP + \left⟮\frac{\partial G}{\partial N}\right⟯_{T,P}dN
   $$
   - 右下角的小標代表必須固定的物理量（這樣才叫偏微分） ex: $\left⟮\right⟯_{V}$ 代表定容
2. 又因為
   $$
   dG = dH - d(TS) = TdS  +VdP + \mu dN - TdS - SdT \\ = VdP + \mu dN  - SdT
   $$
   - 如果此系統有很多種物質，則應該把 $\mu dN$ 換成 $\sum \mu_i dN_i$
3. 一一對應之後可以發現
   1. $S = -\left⟮\frac{\partial G}{\partial T}\right⟯_{P,N}$
   2. $V = \left⟮\frac{\partial G}{\partial P}\right⟯_{T,N}$
   3. $\mu = \left⟮\frac{\partial G}{\partial N}\right⟯_{T,P}$
