# 流式細胞驗證、競爭性 / 絕對增殖、殺傷 assay

1. 引用自哪篇 paper: crispr-all-genetic-perturbation-language
2. Outline (任務主線): 流式細胞驗證、競爭性 / 絕對增殖、殺傷 assay
3. Method:
   流式驗證每顆細胞表面有沒有正確亮起該亮的「燈」（受體有沒有表達正常），操作上是「染色 → 洗一次 → 上機讀」三步：把每孔 ~100,000 顆細胞放進 96 孔圓底盤、300 G 5 min 甩到孔底、倒掉上清；加 20 µL FACS Buffer（PBS 加 2% FBS，用來防止抗體非特異性黏細胞表面），同時把目標抗體稀釋進去，這些抗體屁股上接著螢光分子，會專一去黏細胞表面的某個受體（例如 NGFR、CD19、CD47）；4 °C 暗處靜置 20 分鐘讓抗體找到目標——低溫減慢非特異結合、避光保護螢光；用 FACS Buffer 洗一次把沒結合的抗體沖掉；上 Bio-Rad ZE5 流式細胞儀 (flow cytometer)，把細胞一顆顆送過雷射光束，量每顆細胞身上不同顏色的螢光強度，等於對每顆細胞做一張「哪些燈有亮、有多亮」的記錄；資料用 FlowJo v10 分析。為什麼這套染色能只染到表面受體？兩個層次保證：抗體本身只能黏到目標蛋白上一小段特定形狀的胺基酸序列 (epitope)，跟其他蛋白形狀對不上根本黏不住；而流式用沒打洞的活細胞，細胞膜完整、抗體進不去細胞質，只有露在表面的受體會被染到。如果跳過洗滌，溶液裡的游離抗體會拉高全細胞背景螢光；如果在室溫做染色，表面抗原會被細胞主動吞進去 (internalization) 造成讀出低於真實值，加上抗體非特異結合加快——兩個錯誤疊在一起，陰性陽性混在一起根本無法判定。

   增殖讀出分兩種：競爭性與絕對。競爭性增殖 (competitive proliferation) 把改造款細胞與同骨架對照款細胞 1:1 混進同一孔跑重複刺激；對照款帶 GFP、改造款不帶，流式上分 GFP± 兩群、都鎖在 NGFR+（成功整合）這個母群裡，比較相對比例怎麼變。為什麼要用「GFP 取代 OE gene / scrambled gRNA / NT shRNA」這種同骨架對照而不是直接拿沒改造的 T 細胞？因為同骨架對照在「電穿孔 + 整合 + 表面 NGFR + 一份 TRAC 位點被替換」這幾項全部與改造款一致，唯一差別只剩「擾動元件本身」——相對比例變化才能單純歸因到擾動功能。絕對增殖 (absolute proliferation) 則不混 control、單一構築重複刺激後，在每個樣本管裡加入固定體積的 CountBright Plus Absolute Counting Beads (Thermo)——一管「螢光強、廠商已標好每 mL 多少顆」的塑膠小球，在流式上被視為與細胞不同的事件分別計數；用「真實小球數 ÷ 機器讀到小球數 = 真實細胞數 ÷ 機器讀到細胞數」這個比例，把流式從「只能看比例」升級成「能讀絕對細胞數」，直接得出每 mL 的絕對 CAR-T 數與絕對 Nalm6 數。兩種 assay 互補：競爭性靈敏到能讀 1.2 倍相對優勢，但不一定等於「絕對細胞數變多」；絕對增殖能確認改造款真的養出更多細胞，但敏感度低、容易被孔間死亡浮動稀釋掉小幅差異。兩種一起跑才能既看出相對勝率又確認絕對戰力。

   殺傷 assay 是實戰打靶分數。編輯後第 8 天，每孔放 40,000 顆 Nalm6 白血病細胞 (target)，再加進不同數量的 CAR-T (effector) 形成不同 effector:target ratio (E:T)；同時設一組「不加任何 T 細胞、只有 Nalm6 獨自長」的對照組 (NoT)。48 小時後流式量化還活著的 Nalm6 細胞數，計算 % killing = 1 − [實驗孔存活 Nalm6 / NoT 孔存活 Nalm6]——物理意義是在這個 E:T 下，CAR-T 把多少比例的 Nalm6 從原本獨自長的軌跡上拉下來。為什麼要設多個 E:T 跑稀釋曲線而不是固定一個比例？因為 E:T 拉太高（例如 10:1），CAR-T 多到不管哪個構築都把 Nalm6 全殺光，所有實驗組讀數都飽和在 ~100% killing；E:T 拉太低（例如 0.05:1），CAR-T 少到全部構築都殺不動，所有讀數都黏在 ~0% killing。要看出構築之間的差異就得卡在「中等殺傷區間」（例如 30–70% killing），這時不同構築的相對強弱才會清楚展現。

4. 工具與材料:
   - **Bio-Rad ZE5 flow cytometer**: 把細胞一顆顆送過雷射光束的流式細胞儀，量每顆細胞表面螢光強度。
   - **FACS Buffer**: PBS 加 2% FBS，用來稀釋抗體並阻擋非特異性黏附。
   - **antibody staining (4°C, 20 min, dark)**: 螢光抗體染表面受體；低溫減慢非特異結合與 internalization、暗處保護螢光。
   - **FlowJo v10**: 流式資料分析軟體，做 gating 與細胞群分群。
   - **competitive proliferation**: 改造款 vs 同骨架對照 1:1 混孔競賽，以 GFP± 在 NGFR+ 母群裡追相對比例；靈敏度高。
   - **absolute proliferation**: 單一構築獨跑，用 CountBright 小球反推每 mL 絕對細胞數；驗證相對優勢有沒有轉成真正細胞數變多。
   - **CountBright Plus Absolute Counting Beads**: 螢光小球（廠商已標好每 mL 顆數），在流式上分開計數，反推絕對細胞濃度。
   - **same-backbone control**: 把擾動元件換成 GFP / scrambled gRNA / NT shRNA 的對照構築；控住電穿孔、整合、NGFR、CAR 一致，唯一差別是擾動元件。
   - **killing assay (E:T)**: 用不同 effector:target 比例混 CAR-T 與 Nalm6，48 hr 後測 % killing = 1 − Exp/NoT。
   - **E:T (effector:target ratio)**: CAR-T 與靶細胞數量比；要設稀釋曲線把讀數拉到 30–70% killing 的中等區間才能分辨構築強弱。

5. 與此篇文章的關係:
   在《A unified genetic perturbation language for human cellular programming》這篇文章中，作者為了驗證 CRISPR-All 構築的功能表現並把池化篩選命中的擾動逐一坐實，採用了流式染色 + 競爭性 / 絕對增殖 + 殺傷 assay 三套標準 wet-lab 讀出。這套組合解決了「單看條碼計數變化無法確認生物效應」的瓶頸，吃進編輯後的 CAR-T 細胞與 Nalm6 靶細胞，產出受體表達確認、相對與絕對增殖優勢、以及實戰殺癌能力，為 CACTUS 與 10,240-組合篩選的 hit 提供 individual validation。
