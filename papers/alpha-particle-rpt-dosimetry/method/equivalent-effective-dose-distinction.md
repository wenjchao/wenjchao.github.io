# RBE-加權劑量、Equivalent Dose 與 Effective Dose 的區分

1. 引用自哪篇 paper: alpha-particle-rpt-dosimetry
2. Outline (任務主線): 釐清 αRPT 報告劑量時，應使用 Gy 表示的 D_RBE，避免誤用 ICRP 的 w_R=20 與 effective dose（Sv），因為後者僅適用於輻射防護的 stochastic risk 而非治療性 deterministic 效應。
3. Method:
ICRP 系統把「身體吃了多少能量」翻譯成「未來整體得癌風險」要兩步。第一步 (Eq. 6)：每個器官 $r_T$ 接到的各類輻射劑量 $D_R$ 分別乘上輻射加權因子 $w_R$ 加總，得到該器官的 equivalent dose $H$ (Sv)；$w_R$ 是 ICRP 為長期低劑量曝露選的「致癌風險保守換算係數」，α 為 20、低 LET 輻射為 1。第二步 (Eq. 7)：全身各器官 $H$ 各乘以組織加權因子 $w_T$ (該器官對致癌的相對敏感度) 加總，得到 effective dose $E$ (Sv)——不是任何單一器官的劑量，而是「全身整體 stochastic 致癌風險」的單一數字。RBE 看起來像 $w_R$ 但完全是另一套東西：它是針對 cell killing、骨髓抑制這類具體 deterministic 終點從實驗量出來的能量效應比，反映「現在馬上會造成多少 deterministic 傷害」。簡單說：$w_R$ 估「未來罹癌」、RBE 估「現在會不會被燒爛」。

兩種生物效應的物理本質不同：stochastic 效應指 DNA 殘留突變、累積數十年後變癌——「會不會發生」是機率問題、沒有閾值；deterministic 效應指當下大量細胞死亡導致組織直接失能（骨髓抑制、腎衰竭）——「多嚴重」是劑量量級問題，要超過閾值才會出現、超過後越打越壞。前者只需要一個保守的群體風險係數 ($w_R$)；後者需要特定終點實測的 RBE 才能精準預測。ICRP 自己在 Publication 92 [29] 也明文劃清：「effective dose 是給輻射防護用的，不是給流行病學研究或具體人體曝露研究用的；那些情境應該直接報告器官 absorbed dose 並使用該輻射類型在目標終點的 RBE 資料」。MIRD commentary [30] 接著建議：deterministic 效應沒有像 Sv 這種既定命名量，建議直接用「absorbed dose × endpoint-specific RBE」，這正是 §3-A 的 $D_{RBE}$。

ICRP 設 $w_R = 20$ 的場景是核電廠或工人意外曝露的「保護情境」：曝露對個人沒任何治療好處，預估幾十年後罹癌風險寧可估高一點。但 αRPT 病人是「為治癌主動接受曝露」，損益要算的是當下的腫瘤殺傷對上器官急性毒性，根本不是幾十年後罹癌；連退一步只談長期風險，$w_R = 20$ 預設的「無治療收益」前提也對不上。所以本綜述明確主張：αRPT 應放棄 effective/equivalent dose 報告法，回到 Gy 為單位、按粒子別分項、再乘上實驗量出的 RBE_α 的 $D_{RBE}$ 框架（§3-A）。MIRD commentary 還提案把這種 deterministic 加權後的單位另外命名為 barendsen (Bd) [30]，以與 Sv 區隔。

用 Sv 報告 αRPT 劑量會出什麼問題？假設病人腎臟接到 $D_\alpha = 2$ Gy：若按 ICRP 系統，$w_R = 20$ 算出 equivalent dose $H = 40$ Sv——這個數字遠高於任何臨床劑量上限，會被解讀為「腎臟劑量太高、應停藥」；但若按本綜述推薦用 $RBE_\alpha = 5$ 算 $D_{RBE} = 10$ Gy（等效 γ），仍在腎臟可承受範圍。報告單位混用，臨床決策會被 Sv 的虛胖數字嚇退、錯失有效藥；不同核種就算同樣 Sv 但實際生物效應落差也很大，多中心試驗無法合併比較。這就是本綜述把「單位選擇」當成 αRPT 標準化核心議題的原因。
4. 工具與材料:
- **輻射加權因子 $w_R$**: ICRP 為輻射防護指定的固定權重，反映該類輻射引發 stochastic 致癌的相對風險；α = 20、低 LET 輻射 = 1。
- **組織加權因子 $w_T$**: ICRP 對各器官致癌敏感度給的權重，用於把 equivalent dose 加總成 effective dose。
- **Equivalent dose $H(r_T)$ (Eq. 6)**: $\sum_R w_R D_R(r_T)$；單一器官按輻射類別加權後的 Sv 級劑量。
- **Effective dose $E$ (Eq. 7)**: $\sum_T w_T H_T(r_T)$；全身 stochastic 致癌風險的單一指標，不對應任何單一器官。
- **Stochastic effect**: 低劑量輻射隨機誘發 DNA 殘餘突變、長期可能變癌的效應，無閾值。
- **Deterministic effect**: 大量細胞同時死亡導致組織失能 (骨髓抑制、腎衰竭) 的急性效應，有閾值，超過後越打越壞。
- **ICRP Publication 60 [28] / Publication 92 [29]**: ICRP 對輻射防護加權系統的官方文件；Publication 92 自承 effective dose 不適用於具體人體曝露研究。
- **MIRD commentary on the barendsen unit [30]**: Sgouros et al. 2009 提案，建議為 αRPT 的 deterministic 加權劑量另立 barendsen (Bd) 單位以與 Sv 區隔。
5. 與此篇文章的關係:
在《Dosimetry, Radiobiology and Synthetic Lethality: Radiopharmaceutical Therapy (RPT) with Alpha-Particle-Emitters》這篇綜述中，作者要建議一套 αRPT 臨床通用的劑量報告語言，必須先排除單位誤用。為此援引了 ICRP Publication 60/92 與 MIRD commentary on the barendsen unit，解決「用 stochastic 防護用的 $w_R = 20$ 估治療毒性會把 Gy 虛胖成假 Sv」的瓶頸。它接收 §3-A 算出的按粒子分項 $D_\alpha$、$D_e$、$D_{ph}$，產出明確「αRPT 應以 Gy + 實測 RBE_α 報告」的單位選擇，作為下游 macro-to-micro 翻譯 (§3-D) 與臨床試驗報告的共同基準。
