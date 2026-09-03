# SBGN 相容策略（用「替代 glyph」保住既有社群）

1. 引用自哪篇 paper: sbol-visual-2-diagrams
2. Outline (任務主線): SBGN 相容策略（用「替代 glyph」保住既有社群）
3. Method:
SBOL Visual 2 對 SBGN 的相容策略是「有選擇性借」，不是全借也不是全棄。分子畫法方面，SBGN 對非 DNA 分子的畫法基本上是各種變形長方框——核酸畫成上下邊被削成半圓的長方形 (half-round rectangle)、一般大分子 (macromolecule) 畫成圓角長方形、複合物 (complex) 畫成把四個角切掉的長方形、沒指明類型的通用分子畫成橢圓形——彼此差別小、密集出現時難辨。作者為了在合成生物學社群常畫的密集電路裡讓分子一眼可辨，選了視覺鮮明得多的 double helix、single helix、pill/stadium 蛋白當首選 glyph，把 SBGN 上面那幾種形狀降到 MAY 級替代。MAY 級來自 RFC 2119 分級語彙——MUST 表「一定要」、SHOULD 表「強烈建議」、MAY 表「可以這樣做但沒有義務」，跟 §2B 的家族分級同一套語彙。至於三種 interaction node（Association 圓、Dissociation 圓中圓、Process 方），SBGN 早已把它們畫得辨識度夠、社群也熟——作者直接沿用不重造，是「找到既有標準畫得夠好的部分就直接借」的務實取捨。
SBOL 首選 glyph 與 SBGN 替代 glyph 長得不一樣，卻能保證語意等價——關鍵在 §3B 的 SBO 綁定：兩種畫法都綁到 SBO 樹上同一個 term，繪圖軟體讀到任何一個 glyph 都會查到同一個 URI、同一個定義；對機器來說兩者完全等價、只是視覺樣式不同。名稱也統一以 SBO term 為準（§3B 已定調「命名唯一來源」原則），連命名都不分歧。至於為什麼不乾脆全採 SBGN 圖個乾淨？因為 SBGN 對合成生物學社群過於嚴格，箭頭與節點的組合規則常跟合成生物學家日常畫法衝突、硬套會引起反彈；分子的形狀家族又彼此差別小、密集圖表視覺可辨性不夠。所以作者不做「一次性對齊」，而是分頭處理：視覺劣勢的分子自訂新首選、SBGN 畫得好的 interaction node 直接沿用。這比「全借」或「全不借」都精緻。
兩個假設情境凸顯這個相容策略的必要性。第一，如果作者反過來完全拋開 SBGN、只認自訂 glyph、不留 MAY 級替代——原本用 SBGN 畫了幾十張圖的實驗室瞬間變成「不合規」，SBGN 相關的既有工具也無法接進 SBOL 生態。留一個 MAY 級替代其實成本很低（就是明文承認 SBGN glyph 合法），但一舉守住兩邊社群，是典型「以最小讓步換最大採用率」的規範設計。第二，如果 SBOL 首選 glyph 跟 SBGN 替代 glyph 沒都綁到同一個 SBO term——機器讀到 double helix 檔案會判成「型別 A」、讀到 half-round rectangle 檔案會判成「型別 B」，兩張明明畫同一個 dsDNA 的圖資料層卻互不相認，使用者以為只是換畫法、實際上資料互通性被切斷。所以 SBO 綁定不是旁枝，它是這個「首選 + MAY 替代」雙軌能真正共存的技術地基——沒它，這個相容策略只是視覺妥協而非結構相容。
4. 工具與材料:
- **MAY 級替代 (RFC 2119)**: 「可以這樣做但沒有義務」等級；SBOL Visual 2 用來把 SBGN glyph 標為合法替代品，非官方首選。
- **SBGN 分子形狀家族**: half-round rectangle (核酸)、rounded rectangle (macromolecule)、corner-cut rectangle (complex)、ellipse (generic species) — 形狀彼此差別小，被列為 MAY 級替代。
- **SBOL 自訂首選 glyph**: double helix (dsDNA)、single helix (ssDNA)、pill/stadium (蛋白) 等視覺鮮明的畫法，作為官方推薦。
- **Interaction Node 直接沿用 SBGN**: Association 圓、Dissociation 圓中圓、Process 方；SBGN 這三種節點畫法辨識度夠，作者不重造。
- **SBO 名稱橋樑**: 首選與 MAY 替代都綁到同一個 SBO term，讓兩種畫法在機器眼中語意等價、名稱也統一。
5. 與此篇文章的關係:
在《Communicating Structure and Function in Synthetic Biology Diagrams》這篇文章中，作者為了在採用比 SBGN 更醒目的自訂分子畫法時，仍不撕裂既有 SBGN 使用者，採用「首選自訂 + SBGN 為 MAY 級替代 + SBO 當名稱橋樑」的三層相容策略。它接在 §3B SBO 綁定之後，讓兩套標準的畫法能同時合規，並讓 interaction node 這類 SBGN 畫得夠好的部分直接沿用，替 SBOL Visual 2 打開跨標準社群的採用空間。
