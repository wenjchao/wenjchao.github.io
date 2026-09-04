# Consensus 序列驅動的突變位點挑選

1. 引用自哪篇 paper: cellular-logic-gate-physics
2. Outline (任務主線): Consensus 序列驅動的突變位點挑選
3. Method:
   λ operator 是 17 bp、作者要改的 O_R1 序列共 20 bp。單點突變就有 60 種（每位可換成其他 3 種鹼基）、雙點突變會爆到上千種、三點更是幾萬種。若採「大規模隨機突變」路線，每一個候選都要做一次 site-directed mutagenesis、每一條都要 FACS 量一次 transfer curve——成本爆表，且大部分候選最後都會落在「沒差」或「壞死」的無效區。作者的目標，就是繞開這種盲目掃描。

   作者的做法是先讀「別的野生型 λ operator 怎麼寫」。野生型 Bacteriophage λ 基因組裡總共有 12 個 operator half-site，把這 12 條對齊、逐位置統計各鹼基出現的次數，就得到一張叫「位置權重矩陣 (position weight matrix)」的表 (論文 Equation 3)。這張表告訴你：第 2 位在 12 條裡有 12 條都是 A、第 4 位有 12 條都是 C、第 6 位有 11 條是 C，這幾個位置幾乎絕對保守；其他位置的鹼基分布則較分散。作者的關鍵推論建立在這個保守分布上：cI 蛋白靠一段叫 α-helix 3 的短區段插進 DNA 大溝 (major groove)、用蛋白側鏈與 DNA 特定鹼基「握手」形成 hydrogen bond 與 van der Waals 接觸——某個位置若換掉會直接斷手，演化壓力就會把它緊緊保留下來，變成 12 條都一樣的高頻位置；反之能自由變動的位置代表握手貢獻小、換掉沒差。所以「高頻＝結合能量貢獻最大」是很可靠的先驗，把這幾個位置從高頻鹼基改成低頻鹼基，等於直接打在結合最痛的地方。

   根據這張表，作者只做了三個候選版本，形成 1/2/3 bp 的削弱階梯：mut4 只改第 4 位 C→A（1 bp），mut5 額外加改第 6 位 C→A（2 bp），mut6 再加改第 5 位 T→G（3 bp）——都打在保守度最高的三個位置。這樣一次就跨完「1、2、3 bp 削弱」的階梯，可以直接掃出「削弱剛好」與「削弱過頭」的分界，而不必逐一測所有排列組合。

   實驗結果，mut5 和 mut6 削得過頭——即使把 IPTG 開到最大、把 cI 濃度衝到最滿也壓不下 λP(R-O12) 的輸出，變成「永遠開著」的死開關，失去 inverter 功能。只有 mut4 落在剛好的甜蜜點，配上最弱的 RBS 得到一個對輸入夠敏感的 inverter。若作者只挑 mut6 一個版本，量到平線就會誤以為「削弱這條路完全走不通」；正因為同時準備了 mut4/mut5/mut6 三檔階梯，才看到「mut6 壞、mut5 壞、mut4 剛好」的模式，明白甜蜜點就落在最輕的削弱。整套流程用 3 條質體就完成了原本要幾十條質體才能篩到的答案。

4. 工具與材料:
   - **12 個野生型 λ operator half-site**: Bacteriophage λ 基因組中總共 12 個 cI operator half-site，是位置權重矩陣的原始輸入資料。
   - **位置權重矩陣 (position weight matrix)**: 把 12 條 operator half-site 對齊後、逐位置統計各鹼基出現次數的表 (Equation 3)；指出第 2、4、6 位分別為 A₁₂、C₁₂、C₁₁ 幾乎絕對保守。
   - **共識序列 (consensus sequence)**: 位置權重矩陣每個位置最高頻鹼基串起來的序列，代表「野生型 λ 最偏好的 operator 形狀」。
   - **高頻→低頻鹼基突變策略**: 把保守位置的高頻鹼基改成低頻鹼基，作為「打在 cI-dimer 結合能量最痛位置」的先驗策略。
   - **1/2/3 bp 三檔階梯 (mut4 / mut5 / mut6)**: 分別是 1、2、3 bp 突變的三個 O_R1 版本，一次跨完「削弱剛好」到「削弱過頭」的邊界，只用 3 條質體。
   - **cI-dimer α-helix 3 對 major groove 對稱結合**: cI 兩個單體的 α-helix 3 motif 對稱插入 DNA 大溝與 operator 兩個 half-site 握手，是「保守位置＝結合能量最大」推論的物理基礎。

5. 與此篇文章的關係:
   在《The Device Physics of Cellular Logic Gates》這篇文章中，作者為了在 20 bp 的 O_R1 突變空間中挑出最省的削弱結合位點，採用了 consensus 序列驅動的位點挑選。這個方法把野生型 λ 12 個 operator half-site 對齊做成位置權重矩陣，直接鎖定 12/12 保守的第 4、6 位與 11/12 保守的第 5 位當作 cI-dimer 結合能量最貴的位置。只用 mut4／mut5／mut6 三條質體就掃出「1／2／3 bp 削弱」的階梯，交給下游 site-directed mutagenesis 執行，避開了大規模隨機文庫篩選。
