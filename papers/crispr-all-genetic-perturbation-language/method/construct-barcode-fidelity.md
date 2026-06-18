# 構築-Barcode 對應度 (Long-read PacBio fidelity assessment)

1. 引用自哪篇 paper: crispr-all-genetic-perturbation-language
2. Outline (任務主線): 構築-Barcode 對應度 (Long-read PacBio fidelity assessment)
3. Method:
   這個分析想驗證一件事：作者設計時每個構築都是「element 序列 + 一段 11 字母條碼」的固定配對，理論上條碼 X 一定接著 element X，但池化迭代克隆 (iterative pooled cloning) 過程中，池子裡上千種 element 跟條碼一起被切、一起被接，PCR 跟接合反應可能在中途把某條 DNA 的一半換成另一條的另一半 (template switching)。結果有些 plasmid 上條碼 X 後面接的卻是 element Y——條碼跟內容對不上。下游短讀篩選只讀條碼、察覺不到這件事，會把 element Y 的功能誤掛在條碼 X 上。要驗證對應率必須在同一條 DNA 分子上同時看到條碼跟 element，但兩者中間夾著約 700 bp 的 internal stuffer，短讀一次只能讀 ~150 字母、永遠跨不過去。所以作者改用 PacBio 長讀高保真定序 (PacBio HiFi)——把 DNA 折成圓圈讓定序機沿著圓圈反覆讀同一條，最後平均成又長 (常 >1 kb) 又精準的 read，整個分子從頭讀到尾，條碼與 element 同時在一條 read 上。每條 PacBio read 要回答兩個問題：『裡面的 element 序列是哪個設計？』交給 minimap2 v2.28-r1209 配上專為 HiFi 調過參數的 map-hifi 預設值；『裡面的 11 字母條碼是哪一條？』交給作者自己寫的 python 暴力搜尋腳本 (brute force barcode search)。兩個答案合起來統計，就能算出每個 library 的條碼-element 對應率。

   暴力搜尋一段 11 字母在長 read 裡其實「短得很容易撞名」——隨便挑一個 11 字母窗格，DNA 自然就有可能剛好長得跟某條條碼一樣。作者的訣竅是利用 cloning 留下的兩段 AGCG 疤痕：條碼前後一定接 AGCG。把搜尋目標從 11 字母擴成「AGCG + 11 字母 + AGCG」總共 19 字母 (19 bp anchor)，要求搜尋窗格兩端必須同時對上常數錨點，撞名機率瞬間趨近於零，brute force 才能在 1 kb read 上保持高精準度。對應地，minimap2 的 map-hifi 預設值針對 PacBio HiFi 這種「又長又準」的 read 調過內部參數——k-mer 種子長度跟比對缺口扣分權重都跟 default 不同。HiFi 因為錯誤少，可以用較長種子加速比對、用嚴格扣分減少假對齊；用預設值等於把 HiFi 當低品質 read 處理、會在常數區誤判分裂，換成 map-hifi 才把它的優勢用到底。

   計算對應率時還有兩個容易踩到的雷。第一個是 base library 的 PacBio amplicon 從 5′ 到 3′ 涵蓋整個 CAR，而 CAR 上本來就帶著 FMC63 這段 binder；同時 FMC63 又是 reference 裡的一個 element 條目。minimap2 在比對每一條 read 時都會「成功對上」backbone 裡的 FMC63、把 FMC63 element 當 primary alignment，結果每條 read 看起來都跟 FMC63 吻合、fidelity 假性 100%。作者把 FMC63 從統計剔除，其他條目的對應率才能反映真實情況。第二個是 combo library 同時藏著 Domain、Gene、Knockout、Knockdown 四個位置的 element，長度差很多 (Knockdown 才 97 字母、Gene 的 CDS 卻動輒上千字母)。把四段揉在同一份 reference 一次比對，會被最長最顯眼的 element 帶著走、較短的 Knockdown 對齊被忽略。作者改成把同一條 read 拆成四個位置，分別跟「只有 Domain」、「只有 Gene」、「只有 Knockout」、「只有 Knockdown」四份獨立的 reference 比對，逐位置算對應率——這就是為什麼最後可以分別報出 signaling domain 92.3%、gene 92.2%、knockout 76.2%、knockdown 74.5% 這四個獨立數字。

   這套量化的真正價值在於讓下游短讀篩選的雜訊可被建模。如果完全跳過 PacBio 量化，作者只能假設「條碼 X 一定對應 element X」，但 combo library 實測只有 60% 的構築條碼真的對得上設計，剩下 40% 是條碼跟 element 對不上。短讀篩選看到「條碼 X 在 Chronic Stimulation 變多」時，可能根本不是 element X 讓細胞長得壯，而是條碼 X 實際上裝著 element Y——排行榜會混入大量噪音、甚至把無效或有害的 element 誤判為命中。先量化對應率後，作者才能在每個 hit 旁邊標一個信心上限：對應率 92% 的 signaling domain hit 信心很高，對應率 74% 的 knockdown hit 就要打折看。另一個容易壞掉的環節是 brute force 搜尋時忘了串上 AGCG anchor：11 字母在長 read 裡常有「位置不對但序列剛好相同」的偶然撞名，沒加 anchor 等於放手讓假命中混進統計，barcode_A 會被一堆「序列剛好像它但其實是別處」的命中拉高指派率，fidelity 看似很高、其實是雜訊。anchor 不是裝飾，是 brute force 精準度的命脈。

4. 工具與材料:
   - **PacBio HiFi**: 把 DNA 折成圓圈反覆讀取再平均的長讀高保真定序，產生 >Q20、>1 kb reads，能在一條 read 上同時涵蓋 element 與 barcode。
   - **template switching**: 池化迭代克隆中 PCR/ligation 把不同分子的片段意外互換，導致 plasmid 上條碼 X 接到 element Y。
   - **minimap2 v2.28-r1209 + map-hifi preset**: 長讀比對工具，map-hifi 預設針對 HiFi 高準確度長讀調過 k-mer 與缺口扣分，用來判斷每條 read 的 element 身份 (參 reference 119)。
   - **brute force barcode search (python)**: 作者自製 python 腳本，在同一條 PacBio read 上暴力掃出 11 bp 條碼，輸出 (barcode, element) 配對。
   - **19 bp anchor (AGCG-barcode-AGCG)**: 把 11 bp 條碼前後串上兩段 cloning scar AGCG，搜尋目標變 19 字母，把長 read 內偶然撞名的假命中壓到趨近零。
   - **per-position fidelity (combo library 切四份 reference)**: combo 構築拆成 Domain / Gene / Knockout / Knockdown 四位置，各自跟對應的獨立 reference 比對，避免長 element 主導 alignment。
   - **FMC63 exclusion**: base library 的 amplicon backbone 包含 FMC63，與 element FMC63 重複會造成假性 100% fidelity，必須從統計剔除。

5. 與此篇文章的關係:
   在《A unified genetic perturbation language for human cellular programming》這篇文章中，作者要把 CACTUS meta-library 與 10,240 個四維組合構築一次性塞進 T 細胞做池化篩選，但池化迭代克隆會發生 template switching，使部分構築的條碼跟設計上的 element 對不上。這套 PacBio 長讀流程吃 HiFi reads，吐出每個 library 的條碼-element 對應率，給下游短讀篩選的命中清單標上信心上限。它解掉了「短讀無法跨越中間 700 bp 內含子」的瓶頸，是組合篩選結果能被科學社群採信的前提。
