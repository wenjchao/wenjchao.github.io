# Substrate conformer generation + RIF/RifDock active-site grafting

1. 引用自哪篇 paper: de-novo-design-of-luciferases
2. Outline (任務主線): Substrate conformer generation + RIF/RifDock active-site grafting
3. Method: 
   DTZ 燃料能發光，是因為它在反應途中有一瞬間會變成「帶負電的活化狀態」(anionic DTZ)。酵素要做的事就是穩定這個瞬間。所以作者要設計的 active site 對的是「帶負電版本」的 DTZ 而不是中性版本。第一步：先用標準小分子 conformer generator 把帶負電 DTZ 所有可能的 3D 形狀列出來——單鍵能旋轉、分子能彎成不同姿勢，每種姿勢叫一個 conformer。為什麼要列舉全部、而不是只用真空最低能量那一個？因為 DTZ 在真空中能量最低的形狀跟它真的跑進蛋白口袋被擠出來的形狀通常不一樣；把整個 conformer ensemble 都丟給對接演算法試，等於同時測試「燃料每種可能姿勢都能找到形狀互補的 scaffold 嗎」，大幅提高匹配成功率。第二步：列出燃料喜歡的鄰居。蛋白胺基酸側鏈也不是僵硬的——它在 3D 空間能擺出有限的幾種「常見角度」(rotamer)。RifGen 在 DTZ 周圍的 3D 空間裡像撒網一樣，把所有 20 種胺基酸的所有可能 rotamer 全部撒一遍（大約百萬個），每撒一個就記下它跟 DTZ 形成的氫鍵能量、疏水接觸能量，最後得到一張「DTZ 周圍每個位置如果擺某種側鏈、會跟 DTZ 互動多好」的場 (Rotamer Interaction Field, RIF)。但作者額外加了一條硬性約束：在 DTZ 帶負電的關鍵位置 imidazopyrazinone N1 旁邊，必須放一個帶正電的 Arg 側鏈頂端 guanidinium。因為負電必須被正電扶住才能撐到下一步反應，等於用正電扳手把瞬間生出的負電鎖住、讓 anion 有時間遇到氧氣往發光那一步走；少了這個 Arg，演算法可能找到形狀貼合但 N1 旁無 Arg 的高分解，這種設計即使結合 DTZ 也不會發光，所以 Arg 在 N1 旁邊不能交給演算法自己挑、必須硬塞進 RifGen。第三步：把 RIF + DTZ 整塊塞進 scaffold。RifDock 把「DTZ 的某個 conformer + 包圍它的 RIF rotamer 集」當成一整塊「帶夾子的目標物」，整個拎起來塞進每個 hallucinated scaffold 的中央空腔。它會試遍 DTZ 各種平移位置、各種旋轉角度、各種 conformer，每試一個位置就看：DTZ 跟 scaffold 內壁的形狀互補度好不好、RIF 場裡的高分 rotamer 有沒有剛好落在 scaffold 上能放胺基酸的位置（特別是強制要求的 Arg）；每個 pocket 平均能放 8 個側鏈 rotamer。這個搜尋空間是「百萬種放置 × 1,615 個 scaffold」級的大計算，最後取總分最佳的前 50,000 個 dock 進入下一步序列設計。砍到 50,000 是因為下一步 RosettaDesign / ProteinMPNN 對每個 dock 做完整序列重新設計成本極高，必須先用便宜的能量分數做粗篩、把預算留給高分組精細設計。最後值得注意兩種一不小心就會發生的失敗。第一種是「黏住但不發光」：RifDock 只算形狀和能量、不懂催化機制，沒有 Arg 硬約束就會找出純 binder；下游 colony 噴霧篩選若混進一大半 false design，命中率會直接崩，所以 Arg 強制約束就是把這條失敗路線在計算階段直接砍掉。第二種是「scaffold 形狀根本不對」：RifDock 不會強行把 DTZ 塞進形狀不對的口袋，形狀互補度差的 scaffold 會直接拿到極低分或無解。最終 50,000 個高分 dock 集中在「口袋天生就適合 DTZ」的少數 scaffold 上，回頭驗證了上一步 family-wide hallucination 必須產出 pocket 形狀多樣的 scaffold pool。
4. 工具與材料: 
   - **Anionic DTZ**: DTZ 反應途中帶負電的瞬間活化狀態；酵素設計的對接目標。
   - **Conformer ensemble**: 同一分子在不同單鍵角度下的所有可能 3D 形狀集合；用標準 conformer generator 一次列出。
   - **Rotamer**: 蛋白胺基酸側鏈在 3D 空間能擺出的有限幾種常見角度。
   - **RIF (Rotamer Interaction Field)**: 在 DTZ 周圍 3D grid 上把百萬種 rotamer 都撒一遍並評分形成的場，記錄哪些 rotamer 跟 DTZ 互動好。
   - **RifGen**: 建構 RIF 的演算法 (Dou 2018, Cao 2022)；本論文加上「Arg 必須在 N1 旁邊」的硬性約束。
   - **RifDock**: 把 (DTZ conformer + RIF) 當整塊塞進 scaffold 中央空腔的對接演算法。
   - **Imidazopyrazinone N1**: DTZ 反應時負電會冒出來的關鍵原子位置；Arg guanidinium 必須擺在這旁邊。
   - **Arg guanidinium**: Arg 側鏈頂端的帶正電官能基，作為穩定 DTZ N1 負電的「正電扳手」。
   - **Top 50,000 dock**: 以 protein-DTZ 側鏈互動能量排序後取最佳前 5 萬個 dock，作為進入序列設計的篩選結果。
5. 與此篇文章的關係: 
   在《De novo design of luciferases using deep learning》這篇文章中，作者為了把 DFT 算出來的「Arg 扶住 anion」催化幾何實際植入 1,615 個 hallucinated scaffold，採用了 RifGen 加 RifDock 的活性中心對接流程。這個方法解決了傳統 theozyme grafting 因 scaffold 數量太少而沒地方放、或演算法找到 false binder 等催化幾何被破壞的瓶頸，將 anionic DTZ conformer 與強制 Arg-N1 約束的 rotamer 場結合，產出 50,000 個高分 dock 直接送進下一步 RosettaDesign / ProteinMPNN 序列設計。
