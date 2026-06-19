# Focus（競爭對手認知方向）的雙軌量化編碼 (Dual-track quantification of competitive focus)

1. 引用自哪篇 paper: parallel-play-business-model-design
2. Outline (任務主線): Focus（競爭對手認知方向）的雙軌量化編碼 (Dual-track quantification of competitive focus)
3. Method:
   主觀軌的資料來源是「受訪者親口或公司親自寫下來說了算」的內容：訪談逐字稿裡受訪者明白點名的「我們的主要對手是 X、Y、Z」、公司部落格裡寫「我們挑戰 X 公司」、新聞稿裡寫「我們不同於 X」。每家公司會得到一份「他們宣稱的主要對手清單」。接著每個名單裡的對手要被分類為 peer（同期同類新創）或 established substitute（相鄰產業老牌），用 §2D 已建立的 Porter (1996) + Adner & Kapoor (2016) + Lounsbury & Rao (2004) 雙重檢驗。例如 Icarus 宣稱「我們最在乎的對手是 Zeus、Hercules」，這份清單就全是 peer；Zeus 宣稱「我們最在乎的對手是 Morgan Stanley、UBS、Fidelity」，這份清單就全是 established substitute。
   客觀軌的計算很機械化：拿出每家公司過去幾年所有對外發布的新聞稿，把裡面每一次「我們跟另一家公司比較」的句子（例如「我們跟 Zeus 不同的是…」「我們的服務超越 Morgan Stanley 因為…」）一句一句數出來，每一句都標註比較對象是 peer 還是 established substitute。然後算比例——「peer 比較數 ÷ 總比較數」就是這家公司把注意力放在同類同儕的百分比。例如 Zeus 96% 比較指向 established substitutes、Icarus 66% 比較指向 peers（見表 4）。為什麼一定要除以總比較數而不是只看 raw 次數？因為公司發稿量規模差很大——Zeus 過去三年發 150 篇、Icarus 只發 25 篇，raw 次數其實反映的是 PR 強度而非認知焦點。比例化才能洗掉規模效應，得出真正可比的注意力百分比。
   雙軌的設計理由不是「兩個都拿來算給審稿人看比較嚴謹」，而是「兩條軌道對撞、抓認知與行為的錯位」。主觀軌抓的是受訪者「以為自己在跟誰比」這個認知層；客觀軌抓的是公司對外發稿時「實際上一直在對比誰」這個行為層。兩軌一致時結論強烈可信；不一致就是個值得追問的訊號——例如創辦人嘴上說「我們瞄準 Morgan Stanley」但新聞稿三年來都在跟同行 Hercules 比，那他真正盯著的是誰？這條對撞之所以有力，是因為新聞稿是「沉積性證據」(sedimented evidence)——過去幾年陸陸續續被寫下來，每一篇發稿時公司沒辦法預見幾年後會被研究者拿來計數，所以無法被事後策略性修改。受訪者可以選擇性地強調某幾家對手讓自己顯得有遠見，但他不可能回去改 2008、2009 年的新聞稿。
   整套方法是直接沿用 Navis & Glynn (2010) 在類似新興市場研究中的競爭定向 (competitive orientation) 量化做法。為什麼沿用而不自己發明？因為這帶來三個好處：(1) 方法可重複性——後續研究者拿到原始新聞稿可以照同規則重算；(2) 與既有文獻對接——別篇用同方法量出的數字可以直接跟本研究比較；(3) 避免質性管理研究最常見的「每篇都重新發明指標導致無法累積」的問題。如果作者只用主觀軌跳過客觀軌會怎樣？受訪者會把「我們有遠見地對標傳統老牌」當成正確答案說出來——5 家公司的 founders 可能都說「我們的對手是 Morgan Stanley」，雖然 Icarus 實際上整天盯著 Zeus 和 Hercules 在做什麼。只信主觀軌會看不出 Zeus 96% vs Icarus 66% 這條關鍵差距，parallel play 模型「贏家鎖定 substitute / 輸家盯著 peer」的核心對比就失去硬證據。
4. 工具與材料:
   - **主觀軌 (subjective track)**: 從訪談、部落格、新聞稿萃取受訪者明白宣稱的『主要對手』名單，標註每位對手是 peer 還是 established substitute。
   - **客觀軌 / 語料計數 (objective track)**: 把每家公司新聞稿裡每一句『與其他公司比較』的句子一句一句數出來，再算『peer 比較數 ÷ 總比較數』作為注意力百分比。
   - **比例化 (去規模效應)**: 除以總比較數能消除『公司發稿規模差異』污染，把比較量轉成可跨公司比較的注意力比例。
   - **Sedimented evidence (沉積性證據)**: 過去多年陸續被寫下來的新聞稿，當時不知會被後人計數，所以無法事後策略性修改——這是客觀軌不可作假的物理基礎。
   - **雙軌對撞 (認知 vs 行為錯位)**: 主觀軌抓認知層的『以為自己在跟誰比』，客觀軌抓行為層的『實際上在對比誰』；兩軌不一致就是值得追問的訊號。
   - **Navis & Glynn (2010) 沿用**: 直接採用既有競爭定向 (competitive orientation) 量化做法，帶來方法可重複性、與文獻可對接性、避免重新發明指標。
5. 與此篇文章的關係:
   在《Parallel Play: Startups, Nascent Markets, and Effective Business-model Design》(McDonald & Eisenhardt, 2020) 這篇文章中，作者要把「贏家把對手鎖定在 substitute、輸家盯著 peer」這條核心對比立在不可作假的數字上。他們採用了 Focus 的雙軌量化編碼：吃前述訪談與檔案資料，產出主觀軌（受訪者宣稱對手清單）與客觀軌（新聞稿比較句百分比）兩條獨立軌道。這套設計解決了「受訪者會把『有遠見對標老牌』當作正確答案說出來」的主觀偏誤瓶頸，產出 Zeus 96% vs Icarus 66% 這類可被獨立重算的數字，作為下游 parallel play 模型與表 4 跨案例對比的硬證據。
