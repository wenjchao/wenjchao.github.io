# RosettaDesign / ProteinMPNN 序列設計與 PSSM bias

1. 引用自哪篇 paper: de-novo-design-of-luciferases
2. Outline (任務主線): RosettaDesign / ProteinMPNN 序列設計與 PSSM bias
3. Method: 
   上一步 RifDock 已經決定每個 dock 裡哪些是「動不得」的催化殘基——特別是 N1 旁邊那支 Arg、跟 Arg 配對的 Asp、以及內部 HBNet 氫鍵網路鉚釘。但 scaffold 有 100 個以上殘基，這些動不得的核心只佔個位數，其他位置仍然空白。序列設計的工作就是「把這些空白位置填上適當的胺基酸」，讓蛋白整體能折好、能繞著 DTZ 把催化殘基穩穩地擺住——像廚房中央的爐子已經架好，現在要把四周牆壁、家具、燈具一次決定好。作者把這個過程拆兩階段做：第一階段，所有 RIF 殘基（含 Arg）和 HBNet 殘基的胺基酸身分都鎖死，只優化周邊填空位置，把側鏈與 DTZ 之間的接觸面鎖在位、確保催化幾何不被序列改動拉跑。第二階段，除了必備的 Arg 還鎖著之外，其他 RIF 殘基的身分也允許變動——因為 RIF 是用離散 grid 列舉 rotamer，可能漏掉介於兩個方格之間的好擺法，Rosetta 重新探索能找出 RIF 沒列到的芳香族堆疊或疏水堆疊，把整體 packing 再優化一輪。但填空時還有一個陷阱：純物理能量設計常會挑出「能量很低但天然版沒出現過」的胺基酸組合——例如把太多表面位置堆滿疏水殘基（物理上 OK 但實際上蛋白會聚集成沉澱）。為了避開這些坑，作者用 PSSM (Position-Specific Score Matrix) 拉一下 RosettaDesign 的選擇：PSSM 是一張「位置 × 胺基酸」的分數表，把 NTF2 家族 2,000 條真實序列在每個位置上各種胺基酸的出現頻率算出來，當「天然版會在這個位置擺哪些胺基酸」的標準答案。Rosetta 在能量分數差不多時會優先挑天然版常出現的胺基酸；等於把演化的知識當作 prior 加進設計，提升表達量與可溶性。作者第一輪 DTZ 設計用 RosettaDesign——基於物理能量函數的組合優化工具，把每個位置 20 種胺基酸跟 rotamer 全部列出來搜整體能量最低的組合。2022 年 ProteinMPNN 出來後，第二輪 h-CTZ 設計就換成它。MPNN 是深度學習工具：給它一個蛋白 backbone，它直接吐出最可能折成這個 backbone 的胺基酸序列；在實驗驗證上表達率、可溶性、結構準確度都比 RosettaDesign 高。換 MPNN 之後 wet-lab 成功率從 3/7,648 (0.04%) 跳到 2/46 (4.3%)，提升大約 100 倍——這個量級的提升直接決定整套 de novo 設計流程要訂多少 oligo 才撈得到 hit。整套序列設計的最終目標是 preorganization：催化殘基在 ligand 還沒到之前就已經擺在正確的催化幾何上，DTZ 一進口袋就立刻被 Arg 扶住，不需要先誘導蛋白擺動到正確姿勢（這會耗能、且常常擺不到對的位置就讓 DTZ 跑掉）。實作上靠 HBNet（內部氫鍵鉚釘鎖住核心結構）+ 蛋白整體高穩定性（Tm > 95°C）+ 序列設計刻意把催化殘基放在剛性最高的內部位置。設計過程中 backbone、side chain 與 DTZ ligand 都允許在 Cartesian space 鬆弛，最後用 ligand-binding energy、protein-ligand H-bond 數、shape complementarity (sc) 等多個 metrics 一起篩。
4. 工具與材料: 
   - **RosettaDesign**: 基於物理能量函數的組合式序列設計工具；第一輪 DTZ luciferase 全程使用。
   - **ProteinMPNN**: 深度學習序列設計工具 (Dauparas 2022)：給 backbone 直接吐出最可能折成它的序列；第二輪 h-CTZ 用，成功率提升約 100 倍。
   - **PSSM (Position-Specific Score Matrix)**: NTF2 家族 2,000 條真實序列在每個位置上各胺基酸的出現頻率表，當作 RosettaDesign 的演化 prior。
   - **Two-stage sequence design**: Stage 1 全鎖 RIF + HBNet 只動周邊；Stage 2 除 Arg 外 RIF 也放開，讓 Rosetta 找出網格漏掉的更好 packing。
   - **Preorganization**: 催化殘基在 ligand 還沒到之前就已擺在正確催化幾何上，避免 ligand-induced conformational change 的 entropy 損失。
   - **Shape complementarity (sc)**: ligand 與蛋白口袋形狀貼合度的量化分數，與 ligand-binding energy、H-bond 數一起當設計篩選 metric。
   - **Backbone / side chain / ligand Cartesian relaxation**: 設計過程允許骨架、側鏈與 DTZ 在三維空間都鬆弛，找全局最佳的協同擺法。
5. 與此篇文章的關係: 
   在《De novo design of luciferases using deep learning》這篇文章中，作者為了把 RifDock 撈出的 50,000 個高分 dock 轉成大腸桿菌能實際表達的完整蛋白序列，採用了 RosettaDesign 搭配 PSSM bias 的兩階段序列設計（第二輪換成 ProteinMPNN）。這個方法解決了「催化幾何與蛋白可折疊性難兼顧」的瓶頸，把演化過的胺基酸頻率與物理能量函數整合，產出 7,648 條（第一輪）與 46 條（第二輪）可直接送進 AlphaFold2 filter 與 colony screening 的設計序列。
