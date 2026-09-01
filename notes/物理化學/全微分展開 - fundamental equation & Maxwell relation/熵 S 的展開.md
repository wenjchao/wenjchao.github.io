# 熵 S 的展開

## 內文
1. 對於某系統而言，其熵的變化 dS 可以寫成 U、V、N 三個變數的偏微分展開 (見 <u>平衡</u> )
   $$
   dS = \left⟮\frac{\partial S}{\partial U}\right⟯_{V,n}dU +\left⟮\frac{\partial S}{\partial V}\right⟯_{U,n}dV + \left⟮\frac{\partial S}{\partial N}\right⟯_{U,V}dN\\= \frac{1}{T}dU  +\frac{P}{T}dV - \frac{\mu}{T} dN
   $$
   - 右下角的小標代表必須固定的物理量（這樣才叫偏微分） ex: $\left⟮\right⟯_{V}$ 代表定容
   - 如果此系統有很多種物質，則應該把 $\frac{\mu}{T} dN$ 換成 $\sum \frac{\mu_i}{T} dN_i$
2. 一一對應之後可以發現
   1. $\frac{1}{T}= \left⟮\frac{\partial S}{\partial U}\right⟯_{V,N}$ **<u>注意：這是定義</u>**
   2. $P = T\left⟮\frac{\partial S}{\partial V}\right⟯_{U,N}$
   3. $\mu = -T\left⟮\frac{\partial S}{\partial N}\right⟯_{U,V}$ **<u>注意：這是定義</u>**
