# Sequence Ontology (SO) URI 綁定

1. 引用自哪篇 paper: sbol-visual-2-diagrams
2. Outline (任務主線): Sequence Ontology (SO) URI 綁定
3. Method:
SBOL Visual 2 為每一個序列元件 glyph（promoter、CDS、terminator……）都綁上一組來自 Sequence Ontology (SO, Eilbeck et al. 2005) 的網址 (URI)。Sequence Ontology 是一本由社群共同維護、專門定義「DNA 或 RNA 上的每一種功能片段」的字典——它是一種受控詞彙 (controlled vocabulary)：每個名詞都被官方寫死了一條定義、給了一個唯一的網址、還被安排在一棵大分類樹上（bacterial promoter 是 promoter 的子類）。URI 長得像 `http://purl.obolibrary.org/obo/SO_0000167` 這樣，這串字串在網路上永遠指向 SO 官方定義的某一條。所謂「機器可讀」的意思就是：兩支不同軟體只要都讀到這串 URI，就一定知道它們在講同一件事，不用靠人肉判斷。作者也允許「同一個 glyph 對應多個 SO term」——promoter glyph 直接對應「promoter 及其所有子亞型」這整個 SO 子樹，讓亞型精度外包給 metadata 欄位，避免圖鑑爆炸。
綁 SO URI 最直接的好處是「圖 ↔ 資料」雙向自動化。GFF (General Feature Format) 與 GenBank 這兩份被全世界基因體資料庫使用的檔案格式，本來就用 SO term 當作「這一段是什麼」的欄位——GFF 檔的第三欄可以直接寫 `SO:0000167`。既然 SBOL Visual 的 glyph 也綁了 SO URI，兩邊講同一種語言：繪圖軟體讀完一張圖，就能把每個 glyph 的位置 + SO term 直接寫成 GFF/GenBank 記錄；反過來從 GFF 讀進來，也能自動渲染成 SBOL Visual 圖。作者刻意借用既有的 SO 而不另發私有詞表，正是因為 SO 已經是基因體註解界的通用語（GenBank、Ensembl、UCSC、NCBI 都用它）——如果自立門戶，等於把 SBOL Visual 跟整個既有資料生態切開，每次交換都要多寫一層對照表。
從兩個假設情境可以看出 SO URI 綁定的必要性。第一，如果只規範畫法卻不綁 URI：繪圖軟體 A 把 promoter glyph 認成 `promoter`、軟體 B 認成 `regulatory element`、軟體 C 只當它是一支箭頭圖形——同一張圖被三套系統解讀出三個意思，跨工具互通承諾直接破功。第二，如果反過來規定「一 glyph 對一 term」：SO 樹上 promoter 底下的每一個亞型（bacterial、eukaryotic、σ-70、σ-32……）都得另發明一個新 glyph，圖鑑瞬間從幾十個爆到幾百個。所以作者選擇的中庸點——「每個 glyph 必須綁 SO URI、但可以對應多個 term」——正好在兩個極端之間，把跨工具語意鎖死、又把亞型細節留給 metadata。
4. 工具與材料:
- **Sequence Ontology (SO)**: 社群共同維護、專門定義 DNA/RNA 序列特徵的受控詞彙 (Eilbeck et al. 2005, Genome Biol.)；每個 term 都有唯一 URI 與階層式定義。
- **受控詞彙 (controlled vocabulary)**: 由官方寫死定義、給了唯一網址、還被安排在分類樹上的名詞表，兩份文件指向同一 URI 就一定在講同一件事。
- **唯一網址 (URI)**: Uniform Resource Identifier，全世界唯一的字串（如 `http://purl.obolibrary.org/obo/SO_0000167` 指到 promoter），讓機器能無歧義地認出概念。
- **序列元件 glyph 綁定規則**: SBOL Visual 2 規定每個序列元件 glyph 必須綁到一或多個 SO term；一 glyph 對多 term 保留亞型彈性、避免圖鑑爆炸。
- **GFF / GenBank 格式**: 基因體註解界通用的檔案格式，欄位直接使用 SO term；因此 SBOL Visual 圖表可與這些格式雙向自動轉換。
5. 與此篇文章的關係:
在《Communicating Structure and Function in Synthetic Biology Diagrams》這篇文章中，作者為了把 SBOL Visual 2 從「一組看得懂的圖示」升級為「機器可讀的資料」，為每一個序列元件 glyph 綁定 Sequence Ontology (SO) 的 URI。這一步吃 SBOL Visual 1 就已規範好的 glyph 圖形，產出「glyph ↔ SO term」對應表，讓下游能把 SBOL Visual 圖表自動輸出成 GFF/GenBank 註解，也是 §3B SBO 綁定與 §3C SBOL 2 資料模型映射的姊妹規範。
