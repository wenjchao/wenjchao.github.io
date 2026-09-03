# 多繪圖工具 Cross-implementation 驗證法（四個範例、四個工具）

1. 引用自哪篇 paper: sbol-visual-2-diagrams
2. Outline (任務主線): 多繪圖工具 Cross-implementation 驗證法（四個範例、四個工具）
3. Method:
規範類論文最容易被質疑的一點是：「你這套 glyph 定義是不是暗中假設某款特定繪圖軟體才畫得出來？」若真如此，社群要採用標準就得先掏錢或改工具。作者的解法是刻意找四位作者，分別用四款完全不同的通用繪圖軟體，各自獨立畫一張示範圖。四張範例還刻意選難度遞增的真實案例：Figure 4 是 Gander et al. 2017 的 CRISPR/dCas9 NOR 與 AND gate，用 Microsoft PowerPoint 畫；Figure 5 是 Nielsen et al. 2016 的 Wolfram Rule 30 大型基因迴路，用 Inkscape 畫；Figure 6 是 Goñi-Moreno et al. 2017 的 P. putida TOL 代謝＋調控網路（涵蓋兩個主調控子 XylR/XylS），用 Adobe Illustrator 畫；Figure 7 是 Li et al. 2018 的酵母菌 noscapine 代謝工程，用 OmniGraffle 畫，示範九處染色體位點整合並用顏色與條紋標示基因來源與是否經 codon optimization。
這種「刻意用多工具實作同一標準」的做法為什麼具有證明力？軟體工程有個標準做法叫一致性測試套件 (conformance test suite)：規範要被認為「真的可實作」，必須有多個獨立團隊各自寫出實作，輸入相同、輸出可互相理解。SBOL Visual 2 把這個思路搬到視覺標準：四個作者是四個獨立實作團隊、四款軟體是四種實作環境、四張範例是 conformance 測試案例。而選難度遞增而非同一範例畫四次，是因為每個案例還交叉驗證了不同規範面：Figure 4 驗證 §2C 的分岔箭頭與模組邊界，Figure 5 驗證 §2D 的黑盒抽象，Figure 6 驗證與非 SBOL 元件（小分子化學結構式）共存的能力，Figure 7 驗證顏色與紋路作為可選 metadata 的可行性。
作者還特意讓每位作者「獨立選擇」自己偏好的繪圖工具，事前完全不協調。這是為了封住兩類質疑：若都用同一款軟體（例如 Inkscape）完成，讀者可以懷疑「規範是不是只有在 Inkscape 的 SVG 能力下才畫得出來？」若事先協調同一模板，四張圖看起來一致也可能是模板功勞而不是規範功勞。刻意選擇差異極大的四款軟體——一款簡報軟體、一款開源 SVG 編輯器、一款商業向量繪圖、一款 macOS 圖表軟體——並讓作者自選，就是模擬真實社群不同實驗室各自用不同軟體的異質環境，讓四張圖的成功具有更強的證明力。
4. 工具與材料:
- **Four tools, four examples strategy**: 作者用四位作者、四款通用繪圖軟體、四張難度遞增的範例圖，實地驗證標準對繪圖工具沒有隱性依賴。
- **Conformance test suite (informal)**: 軟體工程用來檢驗規範可實作性的做法：多個獨立實作能互相理解才算通過；本文把它搬到視覺標準。
- **Figure 4 CRISPR NOR/AND gate (Gander et al. 2017)**: 用 Microsoft PowerPoint 畫，示範分岔箭頭 + 顏色編碼 + 模組邊界。
- **Figure 5 Wolfram Rule 30 迴路 (Nielsen et al. 2016)**: 用 Inkscape 畫，示範用 black-box module 收納數十個基因細節。
- **Figure 6 TOL network (Goñi-Moreno et al. 2017)**: 用 Adobe Illustrator 畫，示範 P. putida XylR/XylS 主調控子與非 SBOL 小分子化學結構式共存。
- **Figure 7 noscapine 代謝工程 (Li et al. 2018)**: 用 OmniGraffle 畫，示範九處染色體位點整合、用顏色標示基因來源生物、用條紋或圓點標示 codon optimization。
- **作者獨立選擇繪圖工具**: 作者事前不預先協調，各自挑慣用的工具，用以模擬真實社群的異質軟體環境。
5. 與此篇文章的關係:
在《Communicating Structure and Function in Synthetic Biology Diagrams》(SBOL Visual 2) 這篇文章中，作者為了封住「這套規範是不是暗中綁定某款繪圖軟體」的質疑，採用了「四作者、四通用工具、四難度遞增範例」的獨立實作驗證法。此法吃進 §2A–§2D 定義好的完整規範，產出四張分別用 PowerPoint、Inkscape、Illustrator、OmniGraffle 畫成、卻語意一致的示範圖，等同於視覺標準的一致性測試套件，供社群直接引用為「標準可實作性」的證據。
