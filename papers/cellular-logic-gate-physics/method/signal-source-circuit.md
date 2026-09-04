# 外部誘導型訊號設定電路的構築

1. 引用自哪篇 paper: cellular-logic-gate-physics
2. Outline (任務主線): 外部誘導型訊號設定電路的構築
3. Method:
   量任何 inverter 的 transfer curve 之前，作者第一件事是造一顆能從細胞外用手扭的訊號源。他們設計一組雙質體 pINV-102 與 pINV-112-R1，兩片邏輯完全相同——都以「常開的 IMPLIES 邏輯閘」把培養液加的 IPTG 濃度換成細胞內螢光蛋白的量——差別只在輸出端 pINV-102 掛 EYFP、pINV-112-R1 掛 ECFP。IMPLIES gate 邏輯上等於「NOT x OR y」，只有當抑制蛋白 x 高、誘導物 y 低時才輸出 LOW；作者刻意把 x 寫死成永遠高，剩下唯一可扭的旋鈕就變成 IPTG。

   怎麼把 x 寫死？作者用一段一直開著的啟動子 (constitutive，此處為 p(lacIq)) 驅動 lacI，讓 lacI 濃度永遠處於高檔；於是下游 p(lac) IMPLIES gate 的第一輸入被鎖成高，唯一能扭的變因只剩加進培養液的 IPTG (isopropylthio-β-galactoside)——它模仿乳糖但不會被細胞代謝、能自由穿膜進細胞、形狀剛好卡進 lacI 側面口袋、讓 lacI 彎折後抓不牢 p(lac) 那段 DNA。IPTG 加越多、鎖被撬得越徹底、輸出螢光蛋白越多，構成一條乾淨的濃度→訊號單調映射。

   兩片姊妹質體的骨架也刻意做得一致：p15A 複製起點決定質體在細胞裡的拷貝數 (p15A 屬於中低拷貝，避免每顆細胞塞太多質體、蛋白負擔過大而扭曲量測)、kanamycin 抗性基因讓「培養液加 kanamycin 只留下帶質體的細胞」形成選擇壓力 (否則細胞會逐代丟質體、族群裡混進大量空背景細胞把螢光讀值稀釋掉)、T1 Term 這個轉錄終止子則讓 RNA polymerase 讀到此段停下、避免讀穿到旁邊基因造成串訊。整套電路送進 Escherichia coli 表現，液態培養約 5 小時、族群 mRNA 與蛋白進到合成-降解平衡的穩態後才 FACS 量測；穩態下的螢光才與蛋白產量一對一，否則讀到的是瞬時累積值，同一 IPTG 濃度、不同採樣時間會給出不同答案。

   為什麼要做「同拓撲、不同顏色」的姊妹質體？因為後續量測要「同一顆細胞同時看到輸入與輸出」——輸入位置搭 ECFP、輸出位置搭 EYFP，FACS 才能一次讀出成對訊號。但兩種螢光蛋白的量子產率 (每個分子能放出幾顆光子)、成熟時間 (從翻譯完到會發光要等多久) 與激發-發射光譜都不同，直接比較會把顏色差異誤讀成訊號差異。作者利用這對姊妹質體，在同一組 IPTG 濃度下各自量出 ECFP 與 EYFP 響應曲線 (Fig. 5)，建成「CFP↔YFP 換算查表」；之後任何電路量到的 ECFP 讀值都先透過此表換成 EYFP 等效強度再作圖，把跨顏色的非線性偏差從量測結果剝離。完整質體構築與培養條件見 Weiss MIT 博士論文 [2001]；ECFP 與 EYFP 取自 Clontech (Green, Kain & Angres, Meth. Enzymol. vol.327, 2000)。

4. 工具與材料:
   - **IMPLIES gate**: 兩輸入邏輯閘，真值表等於「NOT x OR y」；當抑制蛋白 x 恆為高時，輸出僅由誘導物 y 決定，可當單旋鈕訊號源。
   - **constitutive promoter p(lacIq)**: 一段一直開著的啟動子，細胞內沒有它的抑制蛋白，用來把 lacI 蛋白鎖在恆高狀態。
   - **IPTG (isopropylthio-β-galactoside)**: 模仿乳糖但不被代謝、可自由穿膜的小分子誘導物；卡進 lacI 口袋讓 lacI 彎折後放開 p(lac) DNA。
   - **pINV-102 / pINV-112-R1**: 邏輯結構完全相同、僅輸出端 fluorophore 不同 (EYFP vs. ECFP) 的姊妹質體對，用於建立 CFP↔YFP 換算查表。
   - **p15A origin**: 質體的複製起點，決定質體在細胞裡的拷貝數 (中低拷貝)，避免蛋白負擔過大扭曲量測。
   - **kanamycin 抗性基因**: 選擇性標記；加 kanamycin 培養時只有帶質體的細胞能活，防止族群中混入丟失質體的背景細胞。
   - **T1 Term**: 轉錄終止子；RNA polymerase 讀到此段就停下，防止讀穿到旁邊基因造成串訊。
   - **FACS 5 小時穩態採樣**: 液態培養約 5 小時待 mRNA/蛋白進到合成-降解平衡的穩態後再流式細胞儀 (FACS) 量測，才能得到 IPTG 濃度到蛋白產量的一對一映射。
   - **CFP↔YFP 換算查表**: 利用 pINV-102 與 pINV-112-R1 在同一 IPTG 掃描下的雙色響應曲線 (Fig. 5) 建成的跨螢光通道對應表，用來剝離量子產率、成熟時間、光譜差異造成的非線性偏差。

5. 與此篇文章的關係:
   在《The Device Physics of Cellular Logic Gates》這篇文章中，作者為了幫 lacI/p(lac) 與 cI/λP(R-O12) 兩顆反相器量出可跨元件比較的 transfer curve，先做了一組 pINV-102 / pINV-112-R1 雙質體訊號源電路。這套「常開 IMPLIES gate + IPTG 誘導」的平台解決了「沒有一個可調的細胞內輸入源，transfer curve 根本無從量起」的瓶頸，向下輸出兩片以 IPTG 為單一旋鈕、以 ECFP/EYFP 為讀值的姊妹質體，並提供一組 CFP↔YFP 校正曲線，供 B 節串上待測 inverter 後做跨通道歸一化。
