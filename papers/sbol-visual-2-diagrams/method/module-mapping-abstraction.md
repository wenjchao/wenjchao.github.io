# Module 與 Mapping 抽象化系統（White-box / Black-box × Port × Identity Mapping）

1. 引用自哪篇 paper: sbol-visual-2-diagrams
2. Outline (任務主線): Module 與 Mapping 抽象化系統（White-box / Black-box × Port × Identity Mapping）
3. Method:
動作很簡單：在一組 glyph（例如一個 CRISPR NOR 邏輯閘裡的 promoter、CDS、gRNA、Cas9）外面畫一個封閉的虛線邊框，這個邊框就是 module。作者提供兩種樣式：白盒模組 (white-box module) 就是虛線框裡照樣畫出所有 glyph，只是明白告訴讀者「這一整塊是一個功能單元」；黑盒模組 (black-box module) 則把內部細節全部收起來、變成一塊灰色的方塊，只在邊界上留矩形凸點作為對外介面接口 (port)，告訴讀者「這裡有進有出，但你現在不用看內部」。port 是 module 邊框上的一顆小矩形凸點，任何從外界進來或往外界出去的 interaction 箭頭都必須通過某個 port——port 於是變成整個 module 對外語意的唯一介面，讀者不用打開黑盒也能知道這個 module 接收哪幾種輸入、輸出哪幾種產物。身份等同映射 (identity mapping) 則處理另一種情境：同一顆蛋白 X 如果在 module A 與 module B 裡各出現一次，讀者預設會以為那是兩份獨立實體；作者的做法是用一條沒有方向的無向邊把兩個 X 直接連起來，明說「這兩顆是同一個」。這條線沒有方向，也不會被誤讀成「A 生產 X 給 B」這類有方向的 interaction。
為什麼直接類比電子電路 IC 封裝而不另闢一套？作者刻意不重造輪子——讀者裡有大量工程背景的人，他們對「IC 外殼、腳位、跨 chip 同一條線」的直覺是既成資產，把 module = IC 外殼、port = 腳位、identity mapping = 跨 chip 同一條線比重新發明生物專屬名詞更省學習成本。作者也讓白盒黑盒兩種樣式並存——同一張圖裡實作者往往需要「這一塊細節攤開、另一塊收起來」的混合狀態，只留其中一種都不夠用。從兩種失敗模式可以看到抽象層的價值。第一種：不畫 identity mapping 時，兩個 module 裡的蛋白 X 會被讀成兩份獨立實體，動力學分析時濃度被錯當成獨立變數。第二種：把 CRISPR NOR 邏輯閘收成黑盒卻沒標任何 port，讀者只看到一塊灰方塊懸在圖上，黑盒等於徹底黑箱。Figure 5 的 Rule 30 迴路之所以能被壓縮成幾個黑盒 + 連線仍然清楚，關鍵就是每個黑盒的 port 都畫全了；Figure 4 用 module 邊界標示 CRISPR NOR gate 的輸入輸出介面同樣是這套抽象在起作用。
4. 工具與材料:
- **white-box module**: 以虛線框框住一組 glyph 但保留內部細節可見的模組樣式，用於強調「這一塊是一個功能單元」但仍要看細節。
- **black-box module**: 隱藏內部細節、只留矩形邊界的模組樣式，用來壓縮視覺複雜度、只顯示對外連線。
- **port**: module 邊界上的矩形凸點，是 module 對外互動的唯一介面；任何跨模組 interaction 箭頭都須通過 port。
- **identity mapping**: 無向邊，用來明示「不同 module 裡出現的兩顆同名 glyph 其實是同一個實體」，避免被誤讀為兩份獨立實體。
- **hierarchical abstraction**: 分層抽象；module 可再被包在更大的 module 裡，讓大型設計得以分層溝通。
5. 與此篇文章的關係:
在《Communicating Structure and Function in Synthetic Biology Diagrams》這篇文章中，作者為了讓 SBOL Visual 2 能處理如 Figure 5 那種上百顆 glyph 的 Rule 30 大型迴路，設計了 Module 與 Mapping 抽象化系統。這一步吃進由 2-C 圖形語法組合出的 glyph 群，把它們打包成白盒或黑盒 module，並用 port 與 identity mapping 把跨模組連線鎖成固定介面，交給後面的實作驗證與資料模型映射當作壓縮視覺複雜度的骨架。
