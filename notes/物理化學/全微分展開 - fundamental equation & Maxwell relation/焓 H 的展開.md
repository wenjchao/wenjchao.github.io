# 焓 H 的展開

## 內文
1. 對於某系統而言，其焓的變化 dH 可以寫成 S、P、N 三個變數的偏微分展開
   $$
   dH = \left⟮\frac{\partial H}{\partial S}\right⟯_{P,N}dS +\left⟮\frac{\partial H}{\partial P}\right⟯_{S,N}dP + \left⟮\frac{\partial H}{\partial N}\right⟯_{S,P}dN
   $$
   - 右下角的小標代表必須固定的物理量（這樣才叫偏微分） ex: $\left⟮\right⟯_{V}$ 代表定容
2. 又因為
   $$
   dH = dU + d(PV) = TdS  - PdV + \mu dN + PdV + VdP \\= TdS +VdP + \mu dN
   $$
   - 如果此系統有很多種物質，則應該把 $\mu dN$ 換成 $\sum \mu_i dN_i$
3. 一一對應之後可以發現
   1. $T = \left⟮\frac{\partial H}{\partial S}\right⟯_{P,N}$
   2. $V = \left⟮\frac{\partial H}{\partial P}\right⟯_{S,N}$
   3. $\mu = \left⟮\frac{\partial U}{\partial N}\right⟯_{S,P}$
