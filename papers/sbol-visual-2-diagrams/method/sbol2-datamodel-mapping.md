# SBOL 2 資料模型自動映射（Component / FunctionalComponent / Interaction / Participation）

1. 引用自哪篇 paper: sbol-visual-2-diagrams
2. Outline (任務主線): SBOL 2 資料模型自動映射（Component / FunctionalComponent / Interaction / Participation）
3. Method:
SBOL 2 資料模型 (Madsen et al. 2019, J. Integr. Bioinf.) 是一份用機器可讀格式（RDF/XML）寫的「合成生物學設計檔案規格」，像是資料庫的 schema。SBOL Visual 圖就是這份資料的視覺投影：每一類 glyph 都明訂綁到唯一一個 SBOL 2 資料類別。Sequence feature glyph 對應 Component——描述某段 DNA 序列上第幾到第幾 bp 是什麼結構元件，屬於「結構視角」。Molecular species glyph 對應 FunctionalComponent——描述某個分子系統裡誰是誰（一顆 LacI 蛋白、一顆 IPTG 小分子），這些漂浮的分子沒有「位置在哪段 DNA 上」的概念，屬於「功能視角」。Interaction glyph 對應 SBOL Interaction，並且必須配一組 Participation roles 記錄箭頭頭尾各自的角色（例如 LacI 是 inhibitor、lac promoter 是 target），否則反向渲染時箭頭方向會消失。整張圖則依內容綁到兩類容器之一：只有 backbone + 序列元件的純結構圖對應 ComponentDefinition（一份序列規格），出現分子物種或箭頭的圖則對應 ModuleDefinition（一份系統規格）——判準就是「這張圖畫的是序列結構還是分子網路」。
這份對照表本身就是「圖 ↔ 資料」的翻譯字典。畫圖 → 資料：繪圖軟體掃過圖上每個 glyph，查字典寫出對應的 Component / FunctionalComponent / Interaction 記錄，補上位置、角色、Participation 就完成一份合規的 SBOL 2 檔案。資料 → 畫圖：吃一份 SBOL 2 檔案，把每個 Component 查字典換成對應 glyph 沿 backbone 排列、每個 FunctionalComponent 換成 molecular species glyph 放在旁邊、每個 Interaction + Participation 畫成箭頭串起頭尾實體，就渲染出一張圖。SBOLDesigner、VisBOL、DNAplotlib 三款專用工具（§3E）就是靠這張對照表運作。至於把整張圖分成 ComponentDefinition 與 ModuleDefinition 兩類容器的設計，是為了讓「畫一段簡單 DNA」跟「畫一個完整分子網路」兩種常見情境都用得順手——純結構圖用不到 module 級的欄位包袱，含分子與箭頭的圖則必需 module 級的表達力。ModuleDefinition 也正好是 §2D 那個 module 視覺概念的資料層對應物。
作者也刻意在規範裡寫下一句誠實的自制：「從資料模型到圖表的翻譯通常會省略或壓縮大量資訊」。理由是資料模型記的是「這份設計的完整檔案」（每段 DNA 的完整鹼基序列、版本號、標註、來源引用、修改歷史），什麼都不能漏；圖表則只挑重點呈現。兩者本質是有損投影 (lossy projection) 關係：圖是資料的一個角度視圖，反之從圖回推資料時只能填回圖上看得到的欄位、其他欄位維持空白。誤把兩邊當無損等價會逼圖表塞爆細節、或者逼資料模型只記能畫出來的東西——兩邊都會被拖垮。同樣的護欄精神也體現在 Participation：如果繪圖軟體把箭頭寫回 SBOL 2 檔案時只記 Interaction、漏了 Participation，反向渲染時就完全查不到誰是 inhibitor、誰是 target，只能亂猜或畫成無方向的線，箭頭方向資訊直接消失。所以 Participation 是 Interaction 記錄能不能反向重建箭頭的最低門檻，被作者明列為必要欄位。
4. 工具與材料:
- **SBOL 2 資料模型**: 以 RDF/XML 寫的合成生物學設計檔案 schema (Madsen et al. 2019)，規定 Component/FunctionalComponent/Interaction/Participation 等物件。
- **Component ↔ sequence feature glyph**: 「結構視角」的元件記錄——描述某段 DNA 序列上第幾到第幾 bp 是什麼片段。
- **FunctionalComponent ↔ molecular species glyph**: 「功能視角」的元件記錄——描述某個分子系統裡的一顆漂浮分子扮演什麼角色。
- **Interaction + Participation roles ↔ interaction glyph**: Interaction 記反應本身、Participation 記頭尾實體各自扮演什麼角色（inhibitor / target 等），Participation 缺席時箭頭方向會消失。
- **ComponentDefinition**: SBOL 2 中的一份序列規格 (sequence specification)——只有 backbone + 序列元件的純結構圖對應此容器。
- **ModuleDefinition**: SBOL 2 中的一份系統規格 (module specification)——出現分子物種或箭頭的圖對應此容器；也是 §2D module 視覺概念的資料層對應物。
- **有損投影 (lossy projection)**: 資料模型 → 圖表本來就會省略大量細節，兩邊不必也不應完全等價；這是作者明訂的規範自制。
5. 與此篇文章的關係:
在《Communicating Structure and Function in Synthetic Biology Diagrams》這篇文章中，作者為了讓 SBOL Visual 2 圖表能被機器讀寫，把每一類 glyph 對應到 SBOL 2 資料模型 (Madsen et al. 2019) 的一個資料類別。它接續 §3A/§3B 的本體綁定，把整套視覺語言接上 SBOL 資料生態，讓 SBOLDesigner、VisBOL、DNAplotlib 等下游工具能靠這份對照表把圖表與資料檔案雙向自動轉換。
