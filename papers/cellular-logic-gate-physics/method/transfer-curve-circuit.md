# 反相器 Transfer Curve 量測電路的構築

1. 引用自哪篇 paper: cellular-logic-gate-physics
2. Outline (任務主線): 反相器 Transfer Curve 量測電路的構築
3. Method:
   有了 A 節的可調訊號源，作者把「待測 inverter」直接接在後面，就形成「constitutive 啟動子 → IMPLIES gate → 待測 inverter」三段式串聯電路。第一段用一直開著的啟動子讓某個 repressor 恆高，第二段把這個 repressor 送進 IMPLIES gate 當永遠開著的第一輸入，剩下唯一可扭的變因就是外加誘導物 (第二輸入)——旋鈕轉多少、就漏出多少要餵給第三段 inverter 的輸入 repressor。研究者只要掃單一誘導物濃度、同步讀輸入 (ECFP) 與輸出 (EYFP) 兩色螢光，就能還原待測 inverter 的完整 transfer curve。

   量 lacI/p(lac) inverter 時 (質體 pINV-203 + pINV-206)，作者第一段選 λP(R-O12) 當 constitutive 啟動子——但它不是天生就一直開，而是刻意讓整個系統不放 cI 這個 repressor、λP(R-O12) 沒東西鎖就等於強制一直開——讓它恆常做出 tetR 蛋白。tetR 再送進 tetR/P(LtetO-1) IMPLIES gate 當恆高輸入，於是唯一變因就是外加 aTc (anhydrotetracycline，能穿膜結合 tetR 並讓 tetR 從 DNA 掉下來的小分子)；aTc 加越多、tetR 越放開、下游 lacI 產量越大。這顆 lacI 才是要送進待測 lacI/p(lac) inverter 的輸入 repressor；lacI 與 ECFP 由同一段 mRNA 表現，ECFP 亮度直接代表當下 lacI 輸入量、EYFP 代表當下 inverter 輸出量。作者刻意把 aTc 掃描區間取在 3 ng/ml 到 30 ng/ml，剛好分別落在陡峭轉折的前後兩端，用來直接量出高低平台之間有沒有足夠明顯的分離度 (noise margin)。

   量 cI/λP(R-O12) inverter 時 (質體 pINV-110 + pINV-107)，作者換了驅動 repressor 對：直接把 A 節的「p(lacIq) constitutive → lacI/p(lac) IMPLIES」搬過來當前兩段，只是這次 IMPLIES gate 下游做出來的不是螢光蛋白，而是要送進待測 cI/λP(R-O12) inverter 的 cI；ECFP 標輸入、EYFP 標輸出的雙色慣例也一模一樣。兩顆 inverter 的量測電路因此構成完美對稱：拓撲同構、只是「誰恆高、誰做旋鈕、誰是輸入 repressor」對調而已。這種「模板不動、只換 repressor 對」讓兩顆 inverter 的 transfer curve 能放在同一組座標系比較 gain 與閾值位置；未來想量新元件也只要換 driver 對，無需重新設計整條電路。

   為什麼不用野生型 λ 啟動子而要自己合成 λP(R-O12)？因為野生型有三個 cI 結合位 ($O_{R1}$, $O_{R2}$, $O_{R3}$)，但 cI 對 $O_{R3}$ 親和力弱、幾乎不貢獻抑制；砍掉 $O_{R3}$ 可以簡化下游 BioSPICE 建模與後續定點突變設計，行為變化很小。而「ECFP 標輸入、EYFP 標輸出」的雙色慣例則是為了讓 FACS 在單細胞內同時讀到一對訊號、直接配成 (輸入, 輸出) 資料點——若同色標兩位置就分不開、若跨批次比對則會被細胞數與培養狀態的批次差異污染 curve 形狀。如果 aTc 只掃一個中央點，會看不到高低平台的存在也算不出轉折陡度；如果每顆 inverter 各自搭不同拓撲，量到的差異可能只是平台差異、不能歸因於元件本身，可攜性也差——作者堅持「拓撲同構、只換 driver repressor」就是要把量測環境當受控背景剝離掉。

4. 工具與材料:
   - **三段式串聯電路**: constitutive 啟動子 → IMPLIES gate → 待測 inverter；前兩段做出可調輸入 repressor、第三段量它的 transfer curve。
   - **IMPLIES gate (此處用法)**: 邏輯 (NOT x) OR y；作者把抑制蛋白 x 鎖成恆高，剩下誘導物 y 當唯一旋鈕，把 gate 化簡成單參數可調的 repressor 源。
   - **tetR/P(LtetO-1) IMPLIES gate**: 以 tetR 為抑制蛋白、P(LtetO-1) 為啟動子的 IMPLIES 閘；配合 aTc 誘導物扭動下游 lacI 產量。
   - **aTc (anhydrotetracycline)**: 四環黴素的穩定衍生物，能穿膜結合 tetR、讓 tetR 從 DNA 掉下來，作為量 lacI/p(lac) inverter 時的旋鈕分子。
   - **λP(R-O12) 作 constitutive**: 自訂合成啟動子，只保留 $O_{R1}$、$O_{R2}$ 兩個 cI 結合位；因系統中不放 cI 而等效於恆常表現。
   - **aTc 掃描區間 3–30 ng/ml**: 刻意跨陡峭轉折前後兩端的濃度範圍，用來量出高低平台之間的雜訊容忍度 (noise margin)。
   - **拓撲同構 (topology isomorphism)**: 兩顆待測 inverter 共用同一組三段式量測電路模板，只對調 driver repressor 對；讓 transfer curve 可放同座標系比較、量測平台差異被當受控背景剝離。
   - **ECFP-in / EYFP-out 雙色慣例**: 所有量測電路一律以 ECFP 標輸入 repressor、EYFP 標輸出；讓 FACS 在同一顆細胞內配對讀出 (輸入, 輸出) 資料點，避免跨批次比對污染。
   - **pINV-203 / pINV-206 / pINV-110 / pINV-107**: 分別為量 lacI/p(lac) 與 cI/λP(R-O12) inverter 的兩對量測質體對，遵循「模板不動、對調 driver repressor」設計。

5. 與此篇文章的關係:
   在《The Device Physics of Cellular Logic Gates》這篇文章中，作者要為 lacI/p(lac) 與 cI/λP(R-O12) 兩顆反相器各自量出可跨元件比較的 transfer curve。他們把待測 inverter 直接接到 A 節訊號源後面，構成「constitutive → IMPLIES → 待測 inverter」三段式量測電路 (pINV-203/206、pINV-110/107)，解決了「用不同批次、不同載體評估元件會參數不可比」的瓶頸。這套電路吃單一誘導物 (aTc 或 IPTG) 的濃度掃描，輸出每顆 inverter 完整的 (input, output) 曲線，交給下游做 gain、noise margin 判定與 gate 修理。
