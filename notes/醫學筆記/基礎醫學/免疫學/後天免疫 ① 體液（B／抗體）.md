# 後天免疫 ① 體液（B／抗體）

## 內文
### 一、Naïve B cell 的形成

1. **重組 BCR**：在 bone marrow，B cell 經 [[BCR 的重組與多樣性|BCR（B-cell receptor）重組]]，表面出現 **IgM**，進入未成熟階段。
2. **篩選自身反應**：重組產生的受體可能強烈辨認自身成分，因此成熟前要先篩選，減少自身組織傷害：改變受體，或移除這顆 B cell。
3. **繼續成熟**：通過篩選並存活者離開骨髓後繼續成熟。成熟 **naïve B cell** 表面同時有 **IgM、IgD**，兩者辨認相同抗原。

- Naïve 表示尚未因相應抗原而活化，此時還不會大量分泌抗體。
- 發育過程需要 **BTK（Bruton tyrosine kinase）** 酵素傳遞訊號；缺陷會阻礙成熟，使成熟 B cell 極少或缺如、各類抗體下降，如 [[Congenital Immunodeficiency|Bruton agammaglobulinemia]]。

### 二、進入周邊循環，遇到抗原進而活化

1. 成熟 naïve B cell 隨血液、淋巴進出 [[B cell 在淋巴器官的分布|周邊淋巴器官]]。這些器官集中抗原，增加 B cell 與抗原相遇的機會。
   - **抗原**是免疫受體能辨認的物質，例如蛋白質、細菌莢膜多醣。與 BCR 結合後把 **signal 1（抗原刺激）** 傳入細胞，也促使結合的物質被內吞。

2. 結合抗原還不夠，B cell 需要額外的活化訊號：
   1. 如果抗原**含蛋白質（<u>T-dependent</u>）**：這些抗原會分解成 **peptide（蛋白質的短片段）**，再與 [[MHC II 的抗原載入|MHC II]] 結合，一起移到 B cell 表面，供 helper T cell 辨認。這就是 B cell 作為 **APC（antigen-presenting cell）** 的工作。
   2. 如果抗原**只有 LPS、單純莢膜多醣（<u>T-independent</u>）**：它們不是蛋白質，不能分解出這種 peptide，也就不能藉 MHC II 呈現給 helper T cell。
      1. 重複排列的抗原可同時結合多個 BCR，病原相關刺激也可提供額外訊號。這些訊號足夠時，B cell 不靠 T cell 幫助也能反應
      2. 因為沒有 T cell signal，通常無法 class switching（產物以 IgM 為主），長期記憶也較有限。
      3. 多醣如果接上 carrier protein，製成 [[主動／被動免疫與疫苗應用|conjugate vaccine]]，同次內吞就有蛋白質，可呈現它的 peptide，因而有機會走 T-dependent 路線。

3. T-dependent 路線：

   **呈現 peptide 後，還要遇到能提供幫助的 CD4 helper T cell。** 它必須符合：
   1. 先前已由樹突細胞等 APC 活化。
   2. **TCR（T-cell receptor）** 能辨認這顆 B cell 表面的 peptide–MHC II。

   濾泡／germinal center 內主要由 **Tfh（T follicular helper cell，CD4 的一種）** 提供幫助：
   1. **接觸訊號**：相應 T cell 受抗原刺激後，表面可增加 [[B cell 與 helper T cell 的接觸訊號|CD40L（CD154）]]，與 B cell 的 **CD40** 結合，把抗原辨認之外的活化訊號傳入 B cell，稱 **共刺激（signal 2）**。
   2. **Cytokines**：T cell 分泌的 **IL-4（Th2、Tfh）與 IL-21（Tfh）** 結合 B cell 的相應受體，配合 CD40 等訊號，使 B cell 進入細胞週期、分裂。

4. **無論是否有 T cell 幫助，活化都需要足夠訊號：**
   1. 收到足夠的活化訊號 → 能辨認這個抗原的 B cell 增殖，產生更多子細胞，稱 clonal expansion
   2. **只有抗原刺激、缺少共刺激**：可進入 **anergy**，之後再遇到該抗原也無法正常活化。因此缺少 T cell 幫助，不代表能自動改走 T-independent 反應。
   - Anergy、Treg 的抑制，以及 **Fas–FasL 引發 apoptosis**，可在周邊限制自身反應性 B／T cells，形成 **peripheral tolerance**；失去限制可傷害自身組織。

### 三、活化之後：抗體變化與細胞分化

以下以 **T-dependent 反應** 為主。

- 注意：以下分別說明 class switching、GC 內的突變與篩選，以及細胞分化，但是**不同 B cell 不必依照下列順序完成，也不必經歷全部過程**。
  - class switching 可在 GC 外開始（較常見），也可以在 GC 內發生（較不常見）
  - 分化可在 GC 外開始（較不常見），也可以在 GC 內發生（較常見）

1. **Class switching：改接 constant region，改變抗體作用** (需要 T cell)

   B cell 活化後，T cell 繼續提供 **接觸訊號（CD40L–CD40）與 cytokines**，可促進 **class／isotype switching**；部分細胞仍保留 IgM。
   - **保留 variable region**：維持對原先抗原的辨認能力。
   - **切換 [[BCR 與抗體的結構|heavy-chain constant region]]**：之後製造的抗體由 IgM 改為 IgG、IgA 或 IgE，作用與分布隨之改變。Cytokines 如何影響 Ig 類別，見 [[抗體五類]]。
   - **CD40L 缺陷**使 class switching 受阻 → IgM 正常或升高，IgG／IgA／IgE 下降，形成 [[Congenital Immunodeficiency|Hyper-IgM]]。

2. **進入 germinal center（GC）**，進行 **somatic hypermutation（SHM）與篩選**

   在同一早期階段，部分活化的 B cells 在濾泡內增殖，形成 GC。
   1. 增殖時，**variable region DNA 突變**，使新 BCR 的結合力變強或變弱。
   2. B cell 用新 BCR 抓取、內吞抗原，再以 peptide–MHC II 呈現給 Tfh。\*\*BCR 結合力較強，通常能抓到、呈現更多抗原，因此較容易得到 Tfh 幫助而存活、增殖。\*\*幫助不足的 B cell 則可凋亡。
   3. 部分存活細胞重複上述過程，使群體的 **affinity（單一位點結合強度）** 逐漸提高，稱 **affinity maturation**。

3. **分化成 plasma cell／memory B cell**

   反應進行期間，Tfh 幫助與其他分化訊號，使部分細胞離開 GC 中的突變 - 篩選循環：
   - **Plasma cell**：大量分泌抗體，在血液、組織中作用。
   - **Memory B cell**：長期保留對該抗原的反應能力，平時不大量分泌抗體。
     - Memory B cell 再次遇到同一抗原時，活化、增殖，部分分化為分泌抗體的細胞；反應更快、更強，以 **IgG** 為主。

   **Tfh 的 IL-21** 配合其他活化訊號，可促進 B cell 分化為 plasma cell。B cell 無法正常分化為分泌抗體的細胞 → plasma cells、Ig 減少，例如 [[Congenital Immunodeficiency|CVID（common variable immunodeficiency）]]。

   分泌出的抗體結合目標後，可引發 [[抗體結合目標後的作用|中和、調理、補體活化與 ADCC]]。除了自己產生抗體，也能直接取得現成抗體；兩者起效與持續時間的差別，見 [[主動／被動免疫與疫苗應用|主動／被動免疫]]。

**註：沒有 class switching、沒有進 GC，也可以形成 plasma cell 或 memory B cell。**

發育與抗體反應可對照 [[B cell 的發育與抗體反應|原有流程示意]]；書頁與補充文獻列於 [[B cell 與抗體參考來源|參考來源]]。
