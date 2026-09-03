# 社群驅動的新 Glyph 提案與收錄流程（Best-practice checklist × GitHub 治理）

1. 引用自哪篇 paper: sbol-visual-2-diagrams
2. Outline (任務主線): 社群驅動的新 Glyph 提案與收錄流程（Best-practice checklist × GitHub 治理）
3. Method:
作者把整個過程切成兩階段。第一階段隨手用階段 (ad hoc stage)：任何實作者都可以在自己的圖表裡直接畫一顆新 glyph，只要自己標明「這不是官方 glyph」即可，不必經過任何審批。第二階段社群提報階段 (community submission stage)：如果那顆 glyph 用了一陣子被證明有用，實作者就把它以 GitHub pull request 的形式提交到 https://github.com/SynBioDex/SBOL-visual，由社群審議、經過 checklist 檢驗後正式納入標準。第一階段給實驗自由，第二階段給品質把關。checklist 有四條：前三條適用於所有新 glyph——(1) 易於手繪 (sketchable by hand)，(2) 不易混淆 (visually distinguishable)，(3) 不含文字 (no embedded text)；第四條專屬於序列元件 glyph——(4) 非對稱且水平可縮放 (asymmetric and horizontally scalable)，用以指示方向性與元件長度。「GitHub PR + checklist」怎麼保證品質？PR 流程本身是機制的一半——任何人送出的 PR 都是公開的，其他實作者、規範維護者、乃至潛在使用者都能來留言審議，比封閉委員會的黑箱審核透明得多。checklist 是機制的另一半——它給審議者一組可稽查的判準，避免審議退化成純主觀的美學口味之爭。至於兩階段流程的巧妙在中間留了一段「先自己用一陣子」的緩衝：不成熟的想法會在 ad hoc 階段被實作者自己丟掉，只有真正好用的 glyph 才會被送上 PR，PR 審議者只需要處理已在真實使用中證明價值的提案。
為什麼把「易於手繪」列為第一條？第一，科學家在會議白板、實驗手稿、期刊審稿邊註上都會臨時手繪基因迴路，如果 glyph 複雜到只能靠 Illustrator 才畫得出來，那它只能活在正式檔案裡、不會出現在真實的思考流。第二，能被手繪的 glyph 通常也代表它的核心特徵不倚賴細節裝飾——手繪要求同時是對「本質形狀夠簡潔」的間接檢驗。序列元件另加的兩條同樣有明確任務：非對稱是為了讓 glyph 用鏡像直接表達正股/反股，如果 glyph 是對稱的（例如圓形），那正反股就得靠額外文字標示，違反第三條「不含文字」；水平可縮放則讓 glyph 的寬度直接表達元件長度或複雜度。從兩個失敗模式可以反過來看出流程的必要。第一種：如果沒有 checklist、只靠 PR 審議，某位成員 PR 一個「用文字寫 CDS」的 glyph——審議者只能靠個人品味爭論，決策變成看哪派人多；checklist 給出「這個 glyph 含文字，違反第三條」這種可稽查的事實陳述，爭論就結束了。第二種：傳統封閉委員會治理審議週期長（半年才有回音）且通道不透明，實作者容易放棄參與；GitHub PR 治理直接把 issue、討論、review、merge 全部公開存檔，避免這兩種失敗模式。這套流程已實際跑出成果：Aptamer、Non-Coding RNA Gene、Origin of Transfer、PolyA Site、Specific Recombination Site、Circular Plasmid、Chromosomal Locus，以及一整套莖-頂端系統 (stem-top site glyph system)（用 DNA / RNA / protein 三種 stem 樣式對應直線 / 波浪線 / 環狀線）都是這樣被納入標準的。
4. 工具與材料:
- **ad hoc stage**: 隨手用階段；實作者可自由在自己圖表裡新增 glyph 並自標非標準身份，不必經過任何審批。
- **community submission stage**: 社群提報階段；使用者透過 GitHub pull request 把 glyph 送上 SynBioDex/SBOL-visual repo，由社群審議後納入標準。
- **best-practice checklist**: 四條的最佳實務檢查表：易於手繪、不易混淆、不含文字；序列元件另加非對稱且水平可縮放。
- **sketchable by hand**: checklist 第一條，要求 glyph 能被手繪，兼具現場使用便利與本質形狀簡潔兩重意義。
- **visually distinguishable**: checklist 第二條，要求 glyph 即使被縮小或潦草手繪也應可與其他 glyph 分辨。
- **no embedded text**: checklist 第三條，要求 glyph 本體不含文字，避免與旁邊的 label 混淆。
- **asymmetric and horizontally scalable**: checklist 第四條（僅限序列元件），要求非對稱以表達方向、水平可縮放以表達長度。
- **GitHub PR governance**: 把 issue、討論、review、merge 全部公開存檔的開源治理模式，取代傳統封閉委員會。
- **stem-top site glyph system**: 已由此流程納入的一整套站點 glyph 家族，用 DNA / RNA / protein 三種 stem 樣式對應直線 / 波浪線 / 環狀線。
5. 與此篇文章的關係:
在《Communicating Structure and Function in Synthetic Biology Diagrams》這篇文章中，作者為了讓 SBOL Visual 2 這套標準能持續吸收社群創新而不失控，設計了雙階段的新 glyph 提案流程。這一步吃進社群自造的 ad hoc glyph 提案，交由四條可稽查的最佳實務檢查表把關、經 GitHub pull request 公開審議，產出正式收錄的新 glyph（如 Aptamer、Non-Coding RNA Gene、莖-頂端系統），交給下游規範版本演進與工具更新持續擴大 SBOL Visual 2 的覆蓋範圍。
