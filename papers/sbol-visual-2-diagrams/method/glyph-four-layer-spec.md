# Glyph 規範化剖析法（Stroke / Fill / Bounding Box / Backbone Alignment 四層界定）

1. 引用自哪篇 paper: sbol-visual-2-diagrams
2. Outline (任務主線): Glyph 規範化剖析法（Stroke / Fill / Bounding Box / Backbone Alignment 四層界定）
3. Method:
SBOL Visual 1 有個惱人老問題：每個 glyph 只給一張示意圖，哪塊算內部可以塗色、旁邊要留多少空白、要貼齊 DNA 骨幹哪個位置，全靠讀者自行推測。SBOL Visual 2 的第一招是把每個 glyph 拆成四個各自可寫死的層次：實線的形狀輪廓 (stroke outline) 決定它長什麼樣；標明「哪一塊算內部」的填色區 (interior for fill) 告訴實作者上色只能塗在這；旁邊要留白的保留區虛線外框 (bounding box) 明訂 glyph 周圍不建議被別的 glyph 侵入的緩衝空間；相對 DNA 骨幹的位置基準線 (backbone alignment line) 則指定它該貼齊、跨越、還是懸吊於骨幹上下。四層並非任意拆分——每一層剛好對應 SBOL Visual 1 時代一種實際發生過的實作困擾，例如絕緣子 (insulator) glyph 過去因為沒明訂內部，實作者常常塗到不該塗的地方；例如 promoter 箭頭底下的區塊若被別的 glyph 侵占，箭頭意義就糊了。
除了幾何四層，規範還把所有 glyph 都放到一個共用坐標系 (standard canvas) 上以向量圖定義，這樣「promoter 該畫多大、CDS 該畫多大」就有一個共同尺——也就是相對縮放比例 (recommended relative scale)。反過來，作者也主動點名一組「保留給實作者自由變化」的樣式屬性 (reserved visual properties)：線條顏色與填色、線寬粗細、輕微的圓角陰影、以及沿 DNA 長度縮放，全都禁止被 glyph 定義綁死。這組明文放行乍看多此一舉，實則配合四層硬規定共同啟動了「未明訂即允許」的邏輯——實作者只要守住輪廓、填色範圍、保留區、對齊四層，其餘怎麼玩都是合法的 SBOL Visual 2 圖。這反而比 SBOL Visual 1 時期給實作者更大的裝飾自由。
四層 + reserved 名單的必要性，其實從反例最清楚。SBOL Visual 1 時代，insulator 填色範圍、promoter 箭頭底下的保留區、glyph 該貼齊 backbone 哪一條線，全靠讀者猜，結果同一設計被畫成不同模樣，光看圖也無法判斷是否合規。SBOL Visual 2 於是把每一個模糊點釘死；而 Figure 1(c) 那一排「同一個 glyph 換不同顏色、線寬、陰影、縮放」的示範，就是為了讓實作者看見——只要輪廓、填色範圍、保留區、對齊都對，其他細節怎麼玩都不會破壞語意。
4. 工具與材料:
- **Stroke outline**: glyph 的實線形狀輪廓，四層裡的硬規範，決定 glyph 的視覺形狀。
- **Interior for fill**: glyph 輪廓內被明訂為「內部」的區塊，色彩填充只能落在這裡，用以消解如 insulator 等舊版填色曖昧的案例。
- **Bounding box**: 虛線標示的保留區，界定 glyph 周圍不建議被其他 glyph 侵入的緩衝空間（例如 promoter 箭頭底下）。
- **Backbone alignment line**: 序列元件 glyph 相對 DNA 骨幹的位置基準線，指定該 glyph 該貼齊、跨越、還是懸吊於骨幹上下。
- **Standard canvas**: 所有 glyph 共用的向量坐標系，供實作者比對「相對縮放比例」以決定不同 glyph 的相對大小。
- **Reserved visual properties**: 規範主動點名保留給實作者自由變化的樣式屬性——線條顏色、填色、線寬、圓角陰影、沿 DNA 長度的縮放——glyph 定義禁止約束這些屬性。
- **Insulator glyph**: SBOL Visual 1 時代填色範圍長期含糊不清的代表案例，作者以此說明為何需要明訂 interior for fill。
5. 與此篇文章的關係:
在《Communicating Structure and Function in Synthetic Biology Diagrams》(SBOL Visual 2) 這篇文章中，作者為了讓合成生物學家在 SBOL Visual 1 時代面對每個 glyph「哪些幾何是硬規範、哪些能自由裝飾」都得靠猜的困境徹底消失，採用了「Glyph 四層界定」規範法——把每個 glyph 拆成 stroke outline、interior for fill、bounding box、backbone alignment 四層各自寫死。這一層設計吃進 SBOL Visual 1 遺留的模糊 glyph 定義，產出可實作、可比對的幾何規範，供下游 §2B 的 RECOMMENDED / MAY / SHOULD NOT 分級與 §3A/§3B 的本體 URI 綁定接手。
