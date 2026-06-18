# siRNA 同步抑制 NHEJ／HR 修復路徑以建立合成致死細胞模型

1. 引用自哪篇 paper: alpha-particle-rpt-dosimetry
2. Outline (任務主線): 在 MDA-MB-231 細胞中以 RNAi 敲低 DNA-PKcs 或 BRCA1 來測試「DSB 修復缺損 + αRPT」的合成致死強化效應，量化 RBE 由基線升至 8.6（DNA-PKcs⁻/⁻）與 15.6（BRCA1⁻/⁻）。
3. Method:
為了測「修復路徑被斷掉時 α 會不會更狠」，作者沿用 §2-A 同一條 MDA-MB-231 細胞，但這次在照射前先把細胞自己的雙股斷裂修補機關掉。修補 DSB 的細胞有兩條獨立生產線：一條是「硬接生產線」非同源末端接合 (non-homologous end-joining, NHEJ)，抓住斷頭兩端、不管原本序列直接焊回去，DNA-PKcs 是這條生產線的總組長；另一條是「對著姊妹染色體抄」的同源重組 (homologous recombination, HR)，把姊妹染色體拉過來當模板小心重建，BRCA1 是 HR 必要的招集者。作者用 small interfering RNA (siRNA)——一段約 20 鹼基對、與 DNA-PKcs 或 BRCA1 mRNA 完全互補的小型雙股 RNA——加上脂質載體送進細胞，靠細胞內建的 RISC 系統把目標 mRNA 切碎，48–72 小時內把對應蛋白敲到幾乎偵測不到（標記為 DNA-PKcs⁻/⁻ 或 BRCA1⁻/⁻；注意這裡是功能上的蛋白消失，不是真的基因敲除）。為什麼不用 CRISPR 永久敲掉？因為 siRNA 是「臨時停工通知」，剛好對應 clonogenic survival 兩三週的窗口，避免細胞長期適應改變表型，也更貼近未來臨床用 PARP inhibitor 之類藥物臨時關掉修復酵素的情境。蛋白掉光後再照 ²¹³Bi-Cetuximab α 與 ¹³⁷Cs γ，各跑一條 clonogenic survival 曲線、抓 D₀ 與 RBE。

對照組的設計則比 §2-A 多一層。作者加了一條 scrambled siRNA——序列被刻意打亂、跟細胞任何 mRNA 都對不上、但脂質載體和 RISC 系統照樣被啟動。如果省掉這組、只比「沒處理 vs siRNA-BRCA1」，就分不清 RBE 跳升是 BRCA1 真的消失造成的、還是脂質轉染本身把細胞搞虛弱了。Table 1 顯示 scrambled siRNA 對照組 D₀ = 0.69 Gy、RBE = 4.7，跟不加 siRNA 的 ²¹³Bi-Cetuximab（D₀ = 0.87、RBE = 3.7）確實已有差異，說明轉染本身就有副作用，這條基線必須留。另外實驗要成功還必須踩穩兩個時序：照射要落在「siRNA 轉染後 48–72 小時、蛋白掉到最低點」的窗口，太早蛋白還沒降、太晚已經長回來，兩種錯位都會讓 RBE 跳升被壓平；同時必須用 Western blot 確認蛋白幾乎掉到偵測極限，否則殘餘 20–30% 蛋白還能撐起一定比例的修復活性，整個合成致死強化訊號就被稀釋。

Table 1 的結果顯示：scrambled 對照 D₀ = 0.69 Gy / RBE = 4.7、DNA-PKcs⁻/⁻ D₀ = 0.37 Gy / RBE = 8.6、BRCA1⁻/⁻ D₀ = 0.21 Gy / RBE = 15.6。關鍵在於 γ 那邊的 D₀ 幾乎不變——修復路徑被敲掉對低 LET γ 殺傷的影響有限，因為 γ 製造的多半是簡單斷裂，連備援機制都很容易修；但 α 那邊的 D₀ 卻從 0.69 Gy 降到 0.37 甚至 0.21 Gy，相當於同樣的存活率只需要原本三分之一甚至七分之一的 α 劑量。Figure 2 的三條存活曲線直接畫出 BRCA1⁻/⁻ 那條最陡、DNA-PKcs⁻/⁻ 次之、scrambled 對照最緩，視覺上一眼就能看出 8 倍敏感度差異。物理含意是：α 把細胞推到「不修不行」的狀態，這時把修復組長踢掉，殺傷力立刻倍增；正常細胞兩條修復生產線都還在，所以同樣的 α 劑量比較撐得住。這就是合成致死在 αRPT 上的定量表現。

為什麼這組實驗仍釘在 MDA-MB-231？因為如果換另一條細胞系，RBE 跳升可能來自兩個來源混在一起——修復路徑被敲掉本身、和新細胞系對 α 本來就比較敏感。釘住細胞系等於把「細胞背景」當作常數，只剩「修復路徑有沒有被敲掉」一個變數在動，這時 RBE 從 4.7 跳到 8.6 / 15.6 才能乾淨地歸因到合成致死強化效應；§2-A 的 ²¹³Bi-Cetuximab 基線也可以直接當這組的「沒被強化」對照。這個對照鏈條延續到 §2-F——只是把「實驗室用 siRNA 敲低」換成「找天生帶 HRD 突變的病人」，再看臨床反應有沒有同樣的強化方向。
4. 工具與材料:
- **siRNA (small interfering RNA)**: 約 20 鹼基對的小型雙股 RNA，序列與目標 mRNA 完全互補，靠細胞內建 RISC 系統把 mRNA 切碎，48–72 小時內把對應蛋白敲到偵測極限。
- **scrambled siRNA**: 序列被打亂、跟細胞內任何 mRNA 都對不上的對照 siRNA，控制脂質轉染與 RISC 系統啟動本身對細胞的副作用。
- **DNA-PKcs**: NHEJ 路徑的總組長 kinase，敲掉後硬接生產線整條停擺。
- **BRCA1**: HR 路徑必要的招集者與調控者，敲掉後對著姊妹染色體抄的生產線整條停擺。
- **NHEJ (non-homologous end-joining)**: DSB 修補的「硬接生產線」，抓住斷頭兩端直接焊回去，不管原本序列。
- **HR (homologous recombination)**: DSB 修補的「對著姊妹染色體抄」生產線，照模板小心重建斷裂處。
- **²¹³Bi-Cetuximab**: 與 §2-A 相同的 α-emitter–抗體複合物，本實驗的 α 照射來源。
- **¹³⁷Cs gamma rays**: 與 §2-A 相同的低 LET 參考輻射，用來算 RBE 的 1.0 基準。
- **Western blot**: 在照射前用來確認 DNA-PKcs 或 BRCA1 蛋白幾乎掉到偵測極限的標準驗證方法。
5. 與此篇文章的關係:
在《Dosimetry, Radiobiology and Synthetic Lethality: Radiopharmaceutical Therapy (RPT) with Alpha-Particle-Emitters》這篇文章中，作者為了直接證明「DSB 修復路徑缺損會放大 αRPT 殺傷」，採用了「在 MDA-MB-231 細胞中用 siRNA 暫時敲低 DNA-PKcs 或 BRCA1」這套合成致死細胞模型（protocol 取自 Song et al., Mol Cancer Ther 2013）。它解決了「光靠 ²¹³Bi-Cetuximab 基線 RBE = 3.7（§2-A）說不出合成致死強化幅度」的瓶頸，產出 RBE = 8.6（NHEJ 缺損）與 15.6（HR 缺損）這兩個關鍵跳升值，作為臨床上 §2-F 用 HRD 突變挑病人策略的細胞層級證據。
