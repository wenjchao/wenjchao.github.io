# Chemical potential $\mu$﻿ & molar Gibbs energy $G_m$﻿

## 內文
1. 在全部與化學位能 $\mu$ 有關的公式中，$\mu = \left⟮\frac{\partial G}{\partial N}\right⟯_{T,P}$ 這條最特別，因為 P、T 都是 Intensive Quantity (不隨數量增加而增加) ，因此固定 P、T 時 G 會與 N 成正比，即 $\mu = \frac{G}{N}$
   - 反之如果是用 $\mu = \left⟮\frac{\partial A}{\partial N}\right⟯_{T,V}$， V 是 Extensive Quantity，而你不可能在增加 N 的時候還固定某個 Extensive Quantity，這樣其他 Extensive Quantities 就不會跟著 N 成正比
2. 在某溫度 T 下的**理想氣體**而言，若已知某在壓力 $P^{\minuso}$ 之下的化學位能為 $\mu^{\minuso}(P^{\minuso},T)$，則另一個壓力 $P$ 之下的化學位能 $\mu(P,T) = \mu^{\minuso}(P^{\minuso},T) + kT\ln(\frac{P}{P^{\minuso}})$
   - 推導：對理想氣體而言，$\frac{\partial \mu}{\partial P} = \frac{1}{N}\frac{\partial G}{\partial P} = \frac{V}{N} = \frac{kT}{P}$ ⇒ $\int d\mu = kT \int \frac{1}{P}dP$
     ⇒ $\mu_2 - \mu_1 = kT [\ln(P_2) - \ln(P_1)]$
   - 通常 $P^{\minuso}$指的是標準狀態，即 1 bar
3. 在某溫度 T 下的**液體**而言，若已知某在壓力 $P^{\minuso}$ 之下的化學位能為 $\mu^{\minuso}(P^{\minuso},T)$，則另一個壓力 $P$ 之下的化學位能 $\mu(P,T) = \mu^{\minuso}(P^{\minuso},T) + \frac{V}{N} (P - P^{\minuso})$
   - 推導：液體不可壓縮，$\frac{\partial \mu}{\partial P} = \frac{1}{N}\frac{\partial G}{\partial P} = \frac{V}{N}$ 在不同壓力下皆為常數 ⇒ $\int d\mu = \frac{V}{N} \int dP$
     ⇒ $\mu_2 - \mu_1 = \frac{V}{N} (P_2 - P_1)$
4. 因為化學家通常使用莫耳數 n 而非粒子數 N，因此在化學中的化學位能 $\mu = \frac{G}{n} = G_m$，其中 $G_m$ 表示 **<u>molar Gibbs energy</u>**
   - 此時理想氣體的化學位能公式要寫成 $\mu(P,T) = \mu^{\minuso}(P^{\minuso},T) + RT\ln(\frac{P}{P^{\minuso}})$
