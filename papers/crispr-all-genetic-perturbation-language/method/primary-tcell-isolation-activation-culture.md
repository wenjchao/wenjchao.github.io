# 原代人類 T 細胞分離、活化與培養 (Primary human T cell isolation, activation, and culture)

1. 引用自哪篇 paper: crispr-all-genetic-perturbation-language
2. Outline (任務主線): 原代人類 T 細胞分離、活化與培養 (Primary human T cell isolation, activation, and culture)
3. Method:
   整個 T 細胞底盤製備可以拆成三段。第一段是「拿到血」。作者跟 Stanford Blood Center 拿經 IRB 核可的血液原料，但不是直接靜脈抽一管血，而是要白血球濃縮袋 (leukoreduction chamber, LRS)——這是血小板捐贈流程裡本來要丟掉的副產物，裡面攔下來的白血球量是直接抽血的數十倍，是 T 細胞研究的標準起始材料。第二段是「從白血球中分離出 PBMC」。白血球袋裡其實還是各種細胞混在一起 (淋巴細胞、單核球、顆粒球、紅血球)，作者用一種叫 Ficoll (商品名 Lymphoprep) 的分層液，密度剛好設計成介於兩群細胞之間，離心後紅血球與顆粒球甩到管底，淋巴細胞與單核球浮在分層液上方形成一層白環，這層就是周邊血單核細胞 (PBMC)。配合的 SepMate 離心管中間有一片擋板把血液與分層液物理隔開、倒血時不會混層，離心後一口氣把 PBMC 倒出來，省去精細吸取的麻煩。第三段是「從 PBMC 中只挑 T 細胞並把它叫醒」。PBMC 裡 T 細胞只佔六到七成，作者用負向篩選 (negative selection) 策略：用一組抗體把所有非 T 細胞 (B 細胞、單核球、NK 細胞) 貼上磁性標籤，磁鐵吸走標籤、留在溶液裡的就是 CD3+ T 細胞。為什麼不直接用 anti-CD3 抗體把 T 細胞吸出來？因為一旦抗體黏上 CD3，等於提前送出一個刺激訊號，會干擾後續活化時序的精準控制。純化完的 T 細胞還處於休眠，作者再用 anti-CD3/CD28 Dynabeads 把細胞叫醒——這是直徑 3-4 微米的小磁珠，表面同時塗了 anti-CD3 與 anti-CD28 兩種抗體，等於合成的「假抗原呈現細胞 (APC)」。活體裡 T 細胞要同時收到兩個訊號才會啟動分裂：第一是抗原訊號 (透過 CD3 受體)、第二是共刺激訊號 (透過 CD28 受體)，缺一不可。Dynabeads 一顆磁珠就同時提供兩個訊號，T 細胞與磁珠以 1:1 比例混合，每顆細胞剛好分到一顆磁珠戳——比例太高會引發過度交聯與提早耗竭，比例太低則活化不夠均勻。然而活化只開啟了「進入分裂狀態」的開關，T 細胞要持續一輪一輪分裂下去，靠的是另一個生長因子迴路：被活化後表面長出 IL-2 受體並自己分泌一點 IL-2 餵自己 (autocrine loop)。但在培養皿這種大體積環境裡，自體分泌物會被稀釋過頭根本喝不到，所以作者額外加 50 U/mL 的人類 IL-2 把這個迴路餵飽，讓 T 細胞能持續擴增兩週以上、累積到電穿孔與下游篩選需要的細胞量。培養基本身用 XVivo 15，這是專為臨床等級 T 細胞療法設計、成分明確、批次穩定的配方，未來要轉譯到臨床流程不必換配方；但它是低蛋白配方，原代 T 細胞 (剛從人體撈出來的細胞，不像細胞株耐操) 在純化學定義基底中存活率有限，所以再加 5% 胎牛血清 (FBS) 補上一些未定義的生長因子與貼附蛋白撐住細胞健康度，整個培養維持在 ~1×10⁶ cells/mL 密度、每 2–3 天計數重接種。為什麼這一步要做得這麼仔細？因為整條 CRISPR-All 流程的成敗都壓在「T 細胞處於活躍分裂狀態」這個前提上。如果 T 細胞沒被叫醒就直接電穿孔，休眠細胞不會啟動 DNA 修復、外來 DNA 根本整合不上去；如果 PBMC 純化沒做乾淨，殘留的單核球會把電穿孔送進去的 DNA 當外來物吞掉，還順便分泌發炎因子把旁邊的 T 細胞毒死；如果 IL-2 忘了加，剛電穿孔過的 T 細胞會在 48 小時內大量凋亡。任何一個環節失守，10,240 個構築的 pooled screen 結論就此報廢。也正因如此，後續電穿孔嚴格選在「活化第 2 天」——細胞剛醒過來、HDR 機器就位、但還沒進入第一次猛烈分裂的甜蜜點。

4. 工具與材料:
   - **Leukoreduction chamber (LRS)**: 血小板捐贈流程的副產物白血球濃縮袋，內含大量 PBMC，是 T 細胞研究的標準起始材料來源。
   - **PBMC (peripheral blood mononuclear cells)**: 周邊血單核細胞，包含淋巴細胞與單核球，是 T 細胞純化的起始混合群。
   - **SepMate + Ficoll (Lymphoprep)**: Ficoll 是密度約 1.077 g/mL 的分層液，介於紅血球/顆粒球與淋巴細胞/單核球之間；SepMate 是中間有擋板的離心管，讓血液與 Ficoll 不混層、離心後可直接傾倒分離 PBMC。
   - **Negative selection (Human CD3 T Cell Enrichment kit, StemCell)**: 負向篩選策略，用抗體 + 磁珠把所有非 T 細胞拉走，避免直接戳到 CD3 引發 T 細胞提前活化。
   - **anti-CD3/CD28 Dynabeads**: 直徑 3-4 µm 的磁珠，表面共價接 anti-CD3 與 anti-CD28，模擬 APC 同時提供 TCR signal 1 (CD3) 與共刺激 signal 2 (CD28)；本實驗 T 細胞:磁珠 = 1:1。
   - **Human IL-2 (50 U/mL, Peprotech)**: 外加 T 細胞生長因子，飽和 IL-2 自體分泌迴路，維持活化後 T 細胞長期擴增。
   - **XVivo 15 (Lonza) + 5% FBS**: GMP 等級、化學成分明確的 T 細胞培養基，加 5% 胎牛血清補未定義生長因子撐住原代細胞健康度。
   - **活化第 2 天**: 後續電穿孔的時序窗口——細胞醒過來、HDR 機器就位、但尚未進入第一次猛烈分裂的甜蜜點。

5. 與此篇文章的關係:
   在《A unified genetic perturbation language for human cellular programming》這篇文章中，作者要在原代人類 T 細胞中跑完整套 CRISPR-All 編輯、CACTUS meta-library 篩選與 CAR-T 重複刺激實驗。原代 T 細胞分離、活化與培養 (PBMC 經 SepMate/Ficoll 離心、negative selection 純化 CD3+、Dynabeads 1:1 活化、XVivo 15 + IL-2 培養) 提供整條流程的細胞底盤，解決了「原代細胞剛取出處於休眠、無法被基因編輯」的瓶頸，產出活躍分裂中的 T 細胞，交給下一步電穿孔做 TRAC knockin。
