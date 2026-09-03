# Systems Biology Ontology (SBO) URI 綁定（Molecular Species + Interaction）

1. 引用自哪篇 paper: sbol-visual-2-diagrams
2. Outline (任務主線): Systems Biology Ontology (SBO) URI 綁定（Molecular Species + Interaction）
3. Method:
SBOL Visual 2 為所有 §3A 覆蓋不到的元件——也就是不長在 DNA 上的分子與跨分子的箭頭——都改綁另一本受控詞彙：Systems Biology Ontology (SBO, Courtot et al. 2011, Mol. Syst. Biol.)。SBO 的結構跟 SO 一樣是階層樹、每個 term 都有唯一 URI，只是管轄範圍不同：SO 只認識「DNA/RNA 序列上的片段」，游離的蛋白質、活化/抑制這類交互作用它樹上根本找不到節點；SBO 剛好補上這塊。因此作者把 molecular species glyph 各自綁到對應的 SBO term——蛋白質 (protein)、小分子 (simple chemical)、通用大分子 (macromolecule)、單股核酸、雙股核酸、複合物 (complex)——這些 term 在 SBO 樹上有明確的父子關係，繪圖軟體讀到 URI 沿樹往上查就能判斷它屬於哪個大類。
interaction glyph 也一併綁到 SBO term，且刻意透過「父 term / 等價 term」把 SBGN 慣用詞當作 SBO 樹的子節點對齊——例如 SBO 的 `Process` 是 SBGN `Production` 的父 term（Process 在上、Production 在下），SBO 的 `Control` 是 SBGN `Modulation` 的等價 term（同一概念、不同名字）；Stimulation / Inhibition / Degradation 各自對應到 SBO 樹的相應分支。這樣做以後，作者訂了一條硬性規則——「SBOL Visual 一律採用對應 SBO term 的名稱」——即使該名稱跟 SBGN 慣用名不同也不遷就。理由是命名唯一來源 (single source of truth)：既然 glyph 已經綁到 SBO term，就直接用 SBO term 的名字當官方名字，不同工具讀 SBOL 圖只要順著 URI 往下解就拿到官方名稱，SBGN 使用者要對照透過 SBO 這個中間點也能無歧義換算。這是「以本體為錨、名字讓路給 URI」的典型設計。
兩個假設情境凸顯 SBO 綁定策略的設計品質。第一，如果沒有「命名唯一來源」原則，SBOL 為了對 SBGN 使用者友好而沿用 SBGN 的 `Modulation` 這個名字，SBOL 檔案就會出現「名字寫 Modulation、SBO URI 卻指 Control」的情況——任何軟體要在兩者間翻譯都要多維護一份同義詞表，SBGN 一改名就要手動同步、漏一次就出資料錯配。第二，如果 glyph 綁 SBO term 的層級沒挑好，例如 protein glyph 綁到很泛的 `entity`，下游軟體就分不出這個 glyph 是蛋白質還是核酸；綁到很細的「E. coli LacI」則圖鑑失去泛用性。作者對每個 glyph 都挑在「不失型別精度、又涵蓋足夠廣」的層級（例如 protein glyph 對應 `macromolecule` 或 `protein` 這種類別型 term），這個層級選擇本身就是規範設計品質的體現。
4. 工具與材料:
- **Systems Biology Ontology (SBO)**: 系統生物學受控詞彙 (Courtot et al. 2011, Mol. Syst. Biol.)，涵蓋分子種類與 interaction/reaction 類型，補上 SO 不涵蓋的範圍。
- **molecular species glyph → SBO term**: 蛋白質、小分子、macromolecule、單/雙股核酸、complex 等都綁到 SBO 對應 term，讀到 URI 沿樹往上就能判斷大類。
- **interaction glyph → SBO term**: Process、Control、Stimulation、Inhibition、Degradation 等箭頭型 term 綁到 SBO 對應分支。
- **父 term (parent term) / 等價 term (equivalent term)**: SBO 樹的階層關係：Process 是 SBGN Production 的父 term；Control 與 SBGN Modulation 為等價 term。
- **命名唯一來源 (single source of truth)**: SBOL Visual 一律採用對應 SBO term 的名稱作為官方名字，即使與 SBGN 慣用名不同，避免同義詞維護與同步漂移。
5. 與此篇文章的關係:
在《Communicating Structure and Function in Synthetic Biology Diagrams》這篇文章中，作者為了讓 SBOL Visual 2 新增的分子與箭頭 glyph 也具備機器可讀語意，採用 SBO URI 綁定。它接在 §3A 的 SO 綁定之後，吃 §2 已定義好的 glyph 圖形，產出「非序列元件 glyph ↔ SBO term」對應表，讓分子語意能被下游 SBOL 資料模型無歧義解析，也讓箭頭的語意不再依賴繪圖者主觀解釋。
