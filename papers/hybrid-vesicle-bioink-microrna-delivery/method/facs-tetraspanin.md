# 利用磁珠/乳膠珠捕捉的 FACS Tetraspanin Profiling

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): 利用磁珠/乳膠珠捕捉的 FACS Tetraspanin Profiling
3. Method: 
   為什麼不能直接拿 EV 跑 FACS？FACS (Fluorescence-Activated Cell Sorting，螢光細胞分選) 是為 µm 級細胞設計的流式分析儀，當顆粒 < ~ 200 nm 時散射訊號弱到跟背景雜訊分不開，~ 30–100 nm 的 EV 直接消失在偵測極限以下。作者的解法是「載體放大法」：把好幾顆 EV / hEL 共價釘在一顆 4 µm latex bead 表面，等於把奈米級顆粒集中黏在一顆夠大的彈珠上。這時 FACS 的散射通道量到的是「bead 本體」(4 µm 散射夠強)，但這個訊號只是用來告訴儀器「有東西通過了」；真正關鍵的螢光通道則量到 bead 表面 EV 蛋白被抗體標亮後的密度——所以 bead 是「載體 + 放大器」，最後讀的是 EV 表面 marker 的密度而不是 bead 本身。

   怎麼把 EV / hEL 釘到 bead 上？作者用 30 µg EV/hEL 配 10 µl 4% (w/v) aldehyde/sulfate-latex beads (Invitrogen A37304)，室溫 15 min 後以 PBS 稀釋到 1 ml、4 °C overnight 震盪。bead 表面的 aldehyde 基 (-CHO) 會跟 EV 表面蛋白上的一級胺基 (NH₂) 反應形成 Schiff base 共價鍵——比物理吸附穩固很多，下游清洗時 EV 不會掉下來。Overnight 後 bead 表面還會剩沒反應的游離 aldehyde，所以下一步是 quench：100 mM glycine (小胺基酸把所有剩下的 aldehyde 全部封掉) + 2% BSA (再用大塊蛋白蓋住整個表面)，室溫 30 min。如果跳過 quench，後續加抗體時殘留 aldehyde 會把抗體無差別釘到所有 bead 上，連 control 組都會被染亮、FACS 訊號分不出組別——「hELs 是否保留 EV marker」這個核心問題就根本問不出來。

   選哪些抗體染？作者挑了 CD9、CD63、CD81 三個 marker——它們是「tetraspanin (四次跨膜蛋白)」家族成員，普遍存在細胞與 EV 的膜上，但細胞分泌 EV 時這三個蛋白會在 EV 膜上「過度富集」，所以全球 EV 研究社群把它們當作「這顆東西是不是 EV」的金標準身分證 (MISEV guideline)。為什麼三個一起測？因為不同 EV sub-population 表現 marker 不一樣，三個一起檢比較不會漏掉某個亞群造成假陰性。操作流程：把 bead-EV / bead-hEL 樣品分別跟 anti-CD9 (Biolegend 312105)、anti-CD63 (Biolegend 353005)、anti-CD81 (Biolegend 349509) 三種抗體 (全部 1:400 稀釋) 共培育，抗體只綁有對應 marker 的 bead；再加 5 µl 帶螢光的二抗放大訊號；最後用 Attune NxT Flow Cytometer (Thermo Fisher) 跑流式，每顆 bead 過雷射時量螢光強度——「亮 bead 的比例」就是該 marker 的陽性百分比。

   實測讀數：EVs 上 CD9 / CD63 / CD81 分別是 87% / 73.9% / 84.86%，hELs 是 32% / 16.93% / 34.23%。乍看像「hELs 訊號變弱 = 變差」，其實正好相反——膜融合的本質就是「把 EV 的膜分子稀釋進 Lip 的膜面積」，融合後同一張膜上有一半是 EV 來的 (帶 CD9/63/81)、一半是 Lip 來的 (不帶這些 marker)，所以平均下來表面 marker 密度本來就會降。如果 hELs 的訊號跟 EV 一樣高，反而代表「Lip 沒有真的融進來、只是物理黏在旁邊」。三個 marker 同步降到約一半的觀察結果，跟「EV:Lip = 1:1 融合」的預期吻合，是融合成功的證據，也跟 Module 4 FRET 訊號變化互相印證。
4. 工具與材料: 
   - **FACS (Fluorescence-Activated Cell Sorting)**: 流式細胞儀的標準分析模式，以散射 + 螢光雙通道每秒分析數萬顆 µm 級顆粒。
   - **Scatter signal (FSC/SSC)**: 前向 / 側向散射訊號；< 200 nm 顆粒散射弱於背景，這就是 EV 無法直接跑 FACS 的根因。
   - **4 µm aldehyde/sulfate-latex beads (Invitrogen A37304)**: 表面帶 aldehyde 基的 4 µm latex bead；aldehyde 共價綁 EV、sulfate 群提供水分散性。
   - **Schiff base covalent coupling**: aldehyde (-CHO) 與蛋白上的一級胺 (NH₂) 反應形成的共價鍵，比物理吸附穩固。
   - **Glycine + BSA quench**: 100 mM glycine 封掉殘留 aldehyde、2% BSA 蓋住整個表面，避免抗體被無差別釘上去產生假陽性。
   - **Tetraspanin (CD9 / CD63 / CD81)**: 四次跨膜蛋白家族，在 EV 膜上過度富集，是 EV 身分認證的金標準 marker (MISEV guideline)。
   - **anti-CD9 / CD63 / CD81 antibodies (Biolegend, 1:400)**: 三種抗體分別標 CD9 (312105)、CD63 (353005)、CD81 (349509)，1:400 稀釋使用。
   - **Attune NxT Flow Cytometer (Thermo Fisher)**: 本研究使用的流式細胞儀型號。
   - **Bead-based flow cytometry for nanoparticle analysis**: 把奈米顆粒釘在 µm 級 bead 上以躍過 FACS 散射偵測極限的技術通稱。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了證明融合過後的 hELs 仍保留 EV 的「身分」(即還帶有 CD9/CD63/CD81 招牌標誌)，採用了「4 µm latex bead 共價捕捉 + FACS tetraspanin 染色」的 bead-based flow cytometry。它解決的瓶頸是『次微米 EV 散射訊號太小、無法直接跑 FACS』，提供了與 Module 4 FRET 互補的「表面標誌驗證」證據，輸出 hELs 上 CD9/63/81 = 32% / 16.93% / 34.23% 的定量讀數，跟 EV 的 87% / 73.9% / 84.86% 對比，支持「~ 一半膜被 Lip 稀釋」的融合模型。
