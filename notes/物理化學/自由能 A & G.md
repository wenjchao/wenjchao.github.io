# 自由能 A & G

## 內文
1. 根據 Clausius inequality，$d S_{sys} ≥ \frac{dq_{env}}{T}$ ⇒ $dq_{env} - T dS_{sys} ≤ 0$
2. 定容下 $dU = dq_{env}$ ⇒ $dU - T dS_{sys} ≤ 0$
   因此定義 **<u>Helmholtz energy</u>** $A = U - TS_{sys}$
   這樣對於任何定溫定容下的反應， $dA = dU - T dS_{sys} ≤ 0$
3. 定壓下 $dH = dq_{env}$ ⇒ $dH - T dS_{sys} ≤ 0$
   因此定義 **<u>Gibbs energy</u>** $G = H - TS_{sys}$
   這樣對於任何定溫定壓下的反應， $dG = dA - T dS_{sys} ≤ 0$
4. Helmholtz energy A 的性質：
   1. 對於任何狀態下（不用定溫、定壓、定容），均可以寫出
      $\begin{cases} dU = dq_{env} + dw_{env} \\ dq_{env} - T dS_{sys} ≤ 0 \end{cases}$ ⇒ $dU - T dS_{sys} ≤ dw_{env}$
   2. 如果在定溫下，則可以把 $A = U - T S_{sys}$ 寫成 $dA = dU - T dS_{sys}$
      ⇒ 定溫下 $dA ≤ dw_{env}$ ⇒ $\Delta A ≤ \Delta w_{env}$
      即 $\Delta A$ 為 **<u>定溫下外界可感受到系統所做的最大的功</u>** （不需定容）
   - 注意：因為是對外做功，所以 $\Delta A$ 、$\Delta w_{env}$ 都 < 0
5. Gibbs energy G 的性質：
   1. 對於任何狀態下（不用定溫、定壓、定容），均可以寫出
      $\begin{cases} dH = dq_{env} + dw_{env} + P_{sys}dV + VdP_{sys} \\ dq_{env} - T dS_{sys} ≤ 0 \end{cases}$
      ⇒ $dH - T dS_{sys} - VdP_{sys} ≤ dw_{env}+ P_{sys}dV$
   2. 如果在定溫下，則可以把 $G = H - T S_{sys}$ 寫成 $dG = dH - T dS_{sys}$
      ⇒ 定溫下 $dG - VdP_{sys} ≤ dw_{env}+ P_{sys}dV$
   3. 如果在定壓下，則還可以化簡：$dG ≤ dw_{env}+ P_{sys}dV$
   4. 其中 $dw_{env}$ 為外界感受到系統做的功，分為膨脹功 $-P_{env}dV$ 及非膨脹功 $dw_{other}$
      $dw_{env} = -P_{env}dV + dw_{other}$
      ⇒ $dG ≤ dw_{env}+ P_{sys}dV = dw_{other}-P_{env}dV +P_{sys}dV$
      因為通常只討論平衡狀態（比較簡單），即 $P_{sys} = P_{env}$（同 焓 H 的定義）
      ⇒ $\Delta G ≤ \Delta w_{other}$
      即 $\Delta G$ 為 **<u>定溫定壓下外界可感受到系統所做的最大的非膨脹功</u>**
      - 注意：因為是對外做功，所以 $\Delta G$ 、$\Delta w_{env}$、$\Delta w_{res}$ 都 < 0
