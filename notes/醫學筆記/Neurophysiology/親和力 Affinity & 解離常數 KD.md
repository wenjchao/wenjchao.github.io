# 親和力 Affinity & 解離常數 $K_D$

## 內文
對於任何反應 $\ce{A + B <=>[v_{on}][v_{off}] AB}$ 而言

1. $v_{off} = k_{off}[AB]$，$v_{on} = k_{on}[A][B]$，（v 反應速率，k 是速率常數）
2. $\frac{d[AB]}{dt} = v_{on} - v_{off}$
3. 平衡時 $v_{off} = v_{on}$
4. 解離常數 $K_D = \frac{[A][B]}{[AB]}= \frac{k_{off}}{k_{on}}$（單位為 M）
5. 親和力 Affinity $= \frac{1}{K_D}$

對於 ligand & channel 的關係， $\ce{A + Unbinded Channel <=>[v_{on}][v_{off}] Binded Channel}$

1. $v_{off} = k_{off}$，$v_{on} = k_{on}[A]$，（v 反應速率，k 是速率常數）
   - 因為實驗通常都是 single channel patch clamp，因此
2. 平衡時 $v_{off}*[\mathrm{Binded}] = v_{on}*[\mathrm{Unbinded}]$
3. 解離常數 $K_D =\frac{[A][\mathrm{Unbinded}]}{[\mathrm{Binded}]} = \frac{k_{off}}{k_{on}} = \frac{v_{off}}{v_{on}}*[A]$（單位為 M）、親和力 Affinity $= \frac{1}{K_D}$
   - 此處 $K_D$ 稱為 $EC_{50}$
4. 移項： $\frac{[\mathrm{Binded}]}{[\mathrm{Unbinded}]} = \frac{[A]}{K_D}$
5. $\mathrm{P(Binded)} = \frac{[\mathrm{Binded}]}{[\mathrm{Unbinded}] + [\mathrm{Binded}]} = \frac{[A]}{[A] + K_D} = \frac{1}{1+({K_D}/{[A]})}$
6. $\mathrm{P(Unbinded)} = \frac{[\mathrm{Unbinded}]}{[\mathrm{Unbinded}] + [\mathrm{Binded}]} = \frac{K_D}{[A] + K_D} = \frac{1}{1+({[A]}/{K_D})}$
7. 當 $[A] = K_D$ 時，$[\mathrm{Binded}] = [\mathrm{Unbinded}]$，即 $\mathrm{P(Binded)} =\mathrm{P(Unbinded)} = 0.5$

- 注意：這裡的 ligand 可以指任何與 channel 結合的東西：
  1. ligand-gated ion channel 的 ligand (ex: Glutamate 和 NMDA receptor 結合)
  2. 與 ion channel 結合的 ion 本身 (ex: Ca channel 需要和 Ca 結合，這樣才能進行 selection)
  3. Blocker（ex: TEA、TTX、ball and chain 的 chain）
