# Glyph 家族與變體系統（RECOMMENDED / MAY / SHOULD NOT 三級分級）

1. 引用自哪篇 paper: sbol-visual-2-diagrams
2. Outline (任務主線): Glyph 家族與變體系統（RECOMMENDED / MAY / SHOULD NOT 三級分級）
3. Method:
同一個生物概念在合成生物學社群裡本來就有多種畫法習慣：例如編碼蛋白質的序列 (CDS)，有人畫五角箭頭、有人畫塊狀箭頭。硬性強制一種會逼掉大量既有作品，全放任又會失去互通。作者的解法是把每個概念的多種畫法歸類成一個「glyph 家族 (glyph family)」，並對家族內成員給予三種語意等級：官方指定唯一一個首選畫法 (RECOMMENDED)——CDS 選五角箭頭；社群既有的塊狀箭頭列為允許的替代 (MAY)，有理由就能用；而若拿一個「什麼都能代表」的通用 glyph——Unspecified glyph——去畫一個明明是 CDS 的段落，則被標為 SHOULD NOT——強烈不建議，因為那等於故意用更模糊的圖示覆蓋更具體的案例。這種分級讓標準得以在不撕裂社群既有畫法的前提下推出。
為什麼大寫的 RECOMMENDED / MAY / SHOULD NOT 能真的達成語意精準、而不是隨意口語？作者直接借用了網路標準組織 IETF 發布的關鍵字約定 (RFC 2119)——這份文件為每個大寫關鍵字綁定了明確定義的要求強度：MUST 是硬性、SHOULD 是強烈建議、MAY 是允許選項、SHOULD NOT 是強烈不建議。讀者只要熟悉這套規範關鍵字，就能一眼判斷不同 glyph 之間的優先順位，不必再猜「作者是不是只是個人偏好」。這種「借既有標準語彙」的做法在工程領域早有前例——電子電路符號的 IEEE Std 91a-1991 與 IEEE Std 315-1975 也是同一路子——因此 SBOL Visual 2 不必自己重新定義優先度語彙，直接接軌一個已被廣泛認可的規範傳統。
光有三級分級還不夠。若缺少「使用最具體 glyph 原則 (most-specific glyph rule)」，實作者遇到不確定的情況就會偷懶挑最泛用的 Unspecified glyph 應付，一整份設計圖看下來讀者只看得到一堆「這是某個東西」，卻看不出來到底是 promoter、CDS 還是 terminator——標準表面被遵守，訊息量卻已流失。作者因此把「一個特徵能被多個 glyph 表達時，務必選最具體那個」寫死為規範，並在濫用時直接標成 SHOULD NOT。這條原則就是三級分級的守門員，防止圖示庫在使用時退化成一堆通用方塊。
4. 工具與材料:
- **RFC 2119**: IETF 發布的關鍵字約定文件，為 MUST / SHOULD / MAY / SHOULD NOT 等大寫關鍵字綁定明確的要求強度層級。
- **RECOMMENDED glyph**: glyph 家族中的首選畫法，每個概念只能有一個，例如 CDS 的五角箭頭。
- **MAY variant**: glyph 家族中允許的替代畫法，可保留社群既有習慣，例如 CDS 的塊狀箭頭。
- **SHOULD NOT (use of a less specific glyph)**: 強烈不建議使用「較不精確的通用 glyph」覆蓋更具體的 glyph，例如拿 Unspecified glyph 畫 CDS。
- **Glyph family**: 同一個概念的多種畫法所歸屬的家族群，家族內成員以三級分級標定優先順序。
- **Most-specific glyph rule**: 當一個特徵能被多個 glyph 表達時，規範要求選擇最具體的那個，避免圖示庫在使用時退化。
- **Unspecified glyph**: 涵蓋範圍最廣的通用 glyph，作為「濫用會被標為 SHOULD NOT」的代表案例。
- **IEEE Std 91a-1991 / IEEE Std 315-1975**: 電子電路符號的既有標準，SBOL Visual 2 借鑑其「借用規範關鍵字定義優先度」的做法。
5. 與此篇文章的關係:
在《Communicating Structure and Function in Synthetic Biology Diagrams》(SBOL Visual 2) 這篇文章中，作者為了讓標準能同時保有語意權威與社群包容，採用了「RFC 2119 式三級分級」方法把 §2A 界定好的每個 glyph 歸為 RECOMMENDED / MAY / SHOULD NOT 家族。此法吃進 SBOL Visual 1 時代社群已流通的多種畫法習慣（例如 CDS 的五角箭頭與塊狀箭頭），產出可讓不同社群共存的優先度標籤，並在 §3D SBGN 相容策略裡直接被沿用——把 SBGN 版 glyph 也降為 MAY 級替代。
