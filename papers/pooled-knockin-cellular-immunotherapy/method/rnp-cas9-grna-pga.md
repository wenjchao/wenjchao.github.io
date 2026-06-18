# RNP (Cas9 + gRNA + PGA) 製備

1. 引用自哪篇 paper: pooled-knockin-cellular-immunotherapy
2. Outline (任務主線): RNP (Cas9 + gRNA + PGA) 製備
3. Method: 
   作者要在 T 細胞染色體上精準剪一刀的工具叫 RNP——蛋白與 RNA 預先組好的剪刀組 (ribonucleoprotein)。剪刀本體是 Cas9 蛋白，帶它去找目標的是一段嚮導 RNA (gRNA)。作者用化學合成的兩段 RNA 拼出 gRNA：crRNA 提供前 20 個鹼基的「地址欄位」、tracrRNA 提供 Cas9 抓得住的支架結構；兩段各配到 160 μM 後 1:1 體積混勻、37 °C 加熱 30 分鐘退火，就得到 80 μM 的功能型 gRNA。Cas9 蛋白本身是 UC Berkeley 的 Cas9-NLS 版本，尾巴帶有「進核許可標籤」(Nuclear Localization Signal)：細胞核入口的搬運蛋白看到這段標籤就會把 Cas9 拖進核裡，沒有它 Cas9 會卡在細胞質碰不到染色體。組裝好之後，gRNA 開頭 20 個鹼基掃描染色體找「字串對得起來」的位置，對上且旁邊有 Cas9 認得的小密碼 (PAM) 時，Cas9 就啟動兩個刀片把雙股 DNA 一刀剪斷。這把剪刀的地址指向 TRAC 位點的第一個外顯子 (exon 1)。
   光把 Cas9 + gRNA 跟 HDR template 混在一起送進原代 T 細胞會出問題。Cas9 蛋白表面帶正電、HDR template DNA 帶負電，混合時容易像膠水一樣黏成大團聚集物。電穿孔靠細胞膜上瞬間打開的小孔讓分子通過，大團聚集物根本鑽不進去，就算進去了也很容易被細胞當廢物分解。作者在混合液裡加入一串重複的麩胺酸聚合成、整體帶負電的人工聚合物，叫 PGA (Poly(L-glutamic acid)，Sigma，分子量 15–50 kDa，配成 100 mg/mL 水溶液)。PGA 像一層「緩衝海綿」先蓋住 Cas9 表面的正電，讓 Cas9 跟 DNA 不會直接結成糊狀，順便保護 DNA 不被細胞質的核酸酶咬掉。結果就是電穿孔送進去的有效份量變多，原代 T 細胞的 HDR 效率明顯提升。
   為什麼 gRNA、PGA、Cas9 三者體積比是 1 : 0.8 : 1、gRNA-to-Cas9 莫耳比 2:1？想讓每一個 Cas9 蛋白都帶上 gRNA、不要有「空手」的剪刀，就得把 gRNA 莫耳數壓到 Cas9 的兩倍，這是飽和組裝又不浪費 gRNA 的折衷。PGA 的量則挑得剛好遮住 Cas9 表面正電、又不會把整管稀釋到 RNP 濃度太低；最後得到約 14.3 μM 的 RNP，37 °C 加熱 15 分鐘讓組裝完成，立刻拿去電穿孔。為什麼整套都選送預組裝 RNP、而不是把 Cas9 基因送進細胞讓它自己合成？因為基因遞送會在細胞裡持續產生新的 Cas9，剪刀效應被無限期延長，剪到不該剪位置的機會 (off-target) 就累積；RNP 進去剪一刀就被細胞自己分解掉，作用快、停留時間短，順便避免 Cas9 永遠留在基因組裡。Protocol 整體沿用 Nguyen et al., 2020 與 Roth et al., 2018。
4. 工具與材料: 
   - **RNP**: Cas9 蛋白與 gRNA 預先在試管裡組好的剪刀組 (ribonucleoprotein)。
   - **Cas9-NLS**: 尾巴帶有「進核許可標籤」(Nuclear Localization Signal) 的 Cas9 蛋白版本，能被主動運入細胞核。
   - **crRNA + tracrRNA**: 化學合成的兩段 RNA：crRNA 提供 20 鹼基地址欄位，tracrRNA 提供 Cas9 抓得住的支架，1:1 退火後等同 sgRNA。
   - **PAM**: Cas9 認得的小密碼，位於目標序列旁，缺它即使序列對上 Cas9 也不會切。
   - **PGA**: Poly(L-glutamic acid)，帶負電的人工聚合物，蓋住 Cas9 正電以防 Cas9 與 DNA 聚集，提升原代 T 細胞 HDR 效率。
   - **TRAC exon 1**: 本研究中 gRNA 指向的 T 細胞天線基因第一個外顯子。
   - **off-target**: Cas9 剪到非目標位置的副作用；遞送 RNP 而非 Cas9 基因可降低其累積。
5. 與此篇文章的關係: 
   在《Pooled Knockin Targeting for Genome Engineering of Cellular Immunotherapies》這篇文章中，作者為了把 36 種候選外掛基因都精準縫進 TRAC 位點，採用了非病毒 RNP + PGA 遞送策略。它解決了傳統 Cas9 基因遞送會持續產生 Cas9 並累積脫靶切割的瓶頸，並用 PGA 阻止 Cas9 與 HDR template 在電穿孔緩衝液裡聚成大團。產出的 14.3 μM RNP 直接交給下一步原代 T 細胞共電穿孔，作為精準在 TRAC 開口的剪刀。
