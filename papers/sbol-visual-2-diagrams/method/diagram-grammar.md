# 圖形語法（Diagram Language：Backbone × Species × Interaction × Node 的組合文法）

1. 引用自哪篇 paper: sbol-visual-2-diagrams
2. Outline (任務主線): 圖形語法（Diagram Language：Backbone × Species × Interaction × Node 的組合文法）
3. Method:
作者的「一套語法」規範四件事：怎麼畫 DNA 那條主線 (backbone)——單線還是雙線、水平還是環狀；序列元件 glyph 怎麼貼在 backbone 上以及正股反股怎麼區分——glyph 畫在 backbone 上方且方向朝右代表落在正股 (positive strand)、畫在下方且方向反過來代表落在反股 (reverse complement)，讀者光憑位置與方向就能直接看出來；分子之間的箭頭走向與頭形代表什麼；多分子在同一點碰撞的生化反應要用什麼形狀的節點圖示 (node glyph) 表達——Figure 2 是完整示範。這套語法最精巧的一段，是「箭頭桿子只講方向、意義全靠頭形」的分工：菱形頭是通用調控 (Control)、實心頭是「產出某個新分子」 (Process)、空心或異色頭是「使目標更活躍」 (Stimulation)、T 形頭是「壓抑目標」 (Inhibition)、指向一個空集合符號的箭頭是「把目標分解掉」 (Degradation)。這樣的分工能行得通，是因為頭形本身在視覺上差異明顯，而且每種頭形都唯一對應到一個既有本體 term——語意來源在別處，不會因人而異。第二段分工靠交叉跳線記號 (crossover)：兩條 interaction 箭頭如果不得不在版面上交叉，一律借用電子電路的跳線記號標明兩者無關，否則讀者會把交叉點誤讀成「一支箭頭從一個尾巴生出多個頭」。第三段分工靠節點：兩個蛋白結合成複合物這種真正的化學反應，箭頭要在匯合處落到一顆節點圖示上——圓形節點是結合 (Association)、雙圓節點是解離 (Dissociation)、方形節點是通用反應 (generic Process)。至於「多頭/多尾箭頭」的語意則被鎖定為 superposition——同一個介質作用於多個目標。
為什麼三條規則要一起上？只有 crossover 沒有多頭專屬語意，讀者仍會把「一顆蛋白抑制兩個 promoter」誤畫成兩條箭頭交叉；只有多頭語意沒有 crossover，多頭與無關交叉又混在一起；沒有節點形狀對應，讀者無法區分結合與解離。三條規則各自堵住一個歧義出口，缺一不可。至於 backbone 這一層，作者不想強迫大家把質體「拉直」畫——允許環狀走向後，環狀質體 (Circular Plasmid) 用 C 形彎曲就能傳達「這是一圈完整質體」的拓樸；染色體位點 (Chromosomal Locus) 用 S 形彎曲則明示「這段序列已整合進染色體某處」。兩個常見的畫錯情境把規則的必要性反過來說清楚：一顆 activator 從左邊指向 promoter A、一顆 repressor 從右邊指向 promoter B，兩條線交叉但沒畫 crossover 時，讀者會誤讀成 superposition，錯把兩個蛋白的調控關係全部串在一起；把「A + B → C」畫成 A、B 兩條實心頭箭頭直接指到 C，讀者只看到「A 生產 C、B 也生產 C」，完全看不出這其實是「A 和 B 綁在一起變成 C」的結合反應。這兩種失敗模式共同指出：圖形語法的三規則不是形式主義，而是圖表被正確解讀的必要條件。
4. 工具與材料:
- **backbone**: 貫穿 DNA 建構的主軸線，可用單線或雙線、水平或環狀走向表達不同拓樸。
- **positive strand / reverse complement**: 正股與反股；glyph 上下位置與方向直接編碼所在鏈。
- **arrowhead 意義對應**: 菱形 Control、實心 Process、空心 Stimulation、T 形 Inhibition、指向空集合符號 Degradation。
- **crossover**: 借自電子電路的交叉跳線記號，用來明示兩條 interaction 邊在版面上交叉但無關。
- **superposition**: 同一支箭頭分岔出多頭多尾的語意，表示同一介質同時作用於多個目標。
- **node glyph**: 生化反應在多條 interaction 匯合處的節點圖示，形狀決定反應類型：圓 Association、雙圓 Dissociation、方形 Process。
- **Circular Plasmid backbone**: C 形彎曲的 backbone 造型，明示這段序列位於環狀質體。
- **Chromosomal Locus backbone**: S 形彎曲的 backbone 造型，明示這段序列已整合進染色體某處。
5. 與此篇文章的關係:
在《Communicating Structure and Function in Synthetic Biology Diagrams》這篇文章中，作者為了讓 SBOL Visual 2 能承接 2-A 的 glyph 幾何與 2-B 的家族分級，讓 glyph 組合出去表達完整合成生物學設計，設計了 Diagram Language 圖形語法。它吃進逐顆有規格的 glyph，交給後面的 module 抽象化系統當作可以打包的原子——並透過箭頭頭形、crossover、節點形狀三條規則同時上，徹底消除 superposition 與生化反應在既有系統圖裡的混淆。
