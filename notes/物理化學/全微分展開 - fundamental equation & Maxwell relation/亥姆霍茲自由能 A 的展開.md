# 亥姆霍茲自由能 A 的展開

## 內文
1. 對於某系統而言，其自由能的變化 dA 可以寫成 T、V、N 三個變數的偏微分展開
   $$
   dA = \left⟮\frac{\partial A}{\partial T}\right⟯_{V,N}dT +\left⟮\frac{\partial A}{\partial V}\right⟯_{T,N}dV + \left⟮\frac{\partial A}{\partial N}\right⟯_{T,V}dN
   $$
   - 右下角的小標代表必須固定的物理量（這樣才叫偏微分） ex: $\left⟮\right⟯_{V}$ 代表定容
2. 又因為
   $$
   dA = dU - d(TS) = TdS  - PdV + \mu dN - TdS - SdT \\ = - PdV + \mu dN  - SdT
   $$
   - 如果此系統有很多種物質，則應該把 $\mu dN$ 換成 $\sum \mu_i dN_i$
3. 一一對應之後可以發現
   1. $S = -\left⟮\frac{\partial A}{\partial T}\right⟯_{V,N}$
   2. $P = -\left⟮\frac{\partial A}{\partial V}\right⟯_{T,N}$
   3. $\mu = \left⟮\frac{\partial A}{\partial N}\right⟯_{T,V}$
