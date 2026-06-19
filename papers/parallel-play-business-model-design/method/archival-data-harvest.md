# 檔案資料與第三方量化指標蒐集 (Archival + third-party quantitative indicator harvesting)

1. 引用自哪篇 paper: parallel-play-business-model-design
2. Outline (任務主線): 檔案資料與第三方量化指標蒐集 (Archival + third-party quantitative indicator harvesting)
3. Method:
   作者把所有「事件當下就被外部記下來」的東西通通收進來：每家公司 23–102 篇媒體文章 (共 248 篇、517 頁，來源涵蓋 Wall Street Journal、New York Times、Financial Times、Barron's、TechCrunch、Investment News、VentureBeat、Washington Post)，再加每家 19–150 則公司部落格與新聞稿、創辦團隊交出來的內部文件、分析師報告、會議簡報、第三方網站快照。這套檔案的關鍵性質是「時間戳釘死的」——某篇 2009 年 Q1 的新聞稿寫了什麼就是寫了什麼，受訪者三年後不能回頭改。所以它能當訪談的對照組：逐字稿說「我們 Q2 就決定走代操」，新聞稿如果到 Q4 還在講廣告模式，就會撞出一個值得追問的矛盾。檔案能對抗主觀敘事，靠的是兩條機制：(1)「時間鎖」——同期紀錄無法被事後修改；(2)「來源獨立」——新聞、政府申報、第三方統計的產生機制互不相干，污染源不會共通。
   績效不能用一個指標套全部，因為 5 家公司在過程中自然分流成兩種商業模式模板。3 家走「幫人代操股票收手續費」(financial intermediary) 的，成功定義是「客戶把錢交給你」——量化方法是 (1) 客戶帳戶數，從產業分析師報告抓；(2) 管理資產 (assets under management, AUM)，從美國證券主管機關公開揭露網站 (SEC Investment Advisor Public Disclosure) 抓——這個數字是政府強制註冊投顧定期申報的，是最可信的第三方數字。2 家走「靠廣告賺錢的網站」(advertising destination) 的，成功定義是「有多少人來我的網站」——量化方法是每月獨立訪客數，從第三方流量量測公司 Compete.com 抓，這做法沿用 Kerr, Lerner & Schoar (2014) 在創投研究中的先例。為什麼非要分模板？假設偷懶用同一指標——例如都用 AUM——廣告路線的公司永遠是 0，不是因為失敗，是因為指標跟它們的商業模式不對齊。Per-template 指標的設計理由就是先承認 5 家在追求不同的價值定義，再為每個模板量身設計反映成功的指標。
   除了「賺多少」之外還要量「過程多有效率」。發展時間是「從公司創立日到第一個能真正運作的商業模式長出來」中間經過幾個月。資金消耗則用兩層：第一層是粗略指標——募資總額（沿用 Pahnke et al. 2015 的慣例）；第二層是更尖銳的二元指標——「是否在做出商業模式之前就把錢燒光」。為什麼要加第二層？如果只看募資總額，Icarus 募了 1100 萬美元、Phaethon 募了 150 萬美元，第一眼會覺得 Icarus 是「資源充裕的明星」。但事實是 Icarus 把 1100 萬全燒光卻沒做出能運作的商業模式——這個關鍵狀態如果不加二元指標，會被「資源充足」這層表象完全蓋掉。二元指標把「過程有沒有走到終點」這件事釘死在資料裡，不依賴額度大小。
   除了媒體與績效數字之外，作者還抓了兩組輔助指標。第一組是「市場排名」：對行業分析師與專家做投票式排名 (poll of industry analysts)，加上內外部受訪者的質性評價，這層能反映業界共識下「誰被認為做得好」。第二組是「VC 中心性」：在 Crunchbase 早期投資人網路裡用 eigenvector centrality 排序判定「Top-50 VC」——白話說就是看每個 VC 跟其他重要 VC 連得有多近、有多廣，越靠近網路中心代表越重要。為什麼這層需要？因為 5 家公司的可比性控制裡有一條是「皆獲得 Top-50 VC 挹注」，這條只有量化中心性才能客觀界定。如果作者只靠訪談、跳過所有檔案蒐集，結果是：績效退化為受訪者自陳、事件時序失去外部錨點、triangulation 結構塌掉、後面案例史「事件須在多種來源出現」的納入門檻根本進不去。
4. 工具與材料:
   - **Archival data (檔案資料)**: 事件當下就被外部記下來的證物——媒體文章 248 篇、公司部落格、新聞稿、分析師報告、會議簡報——靠「時間鎖 + 來源獨立」對抗訪談的事後重構偏誤。
   - **Template-specific performance measures**: 為 financial intermediary 與 advertising destination 兩種商業模式模板分別量身設計專屬指標，避免硬塞同一指標扭曲跨模板比較。
   - **SEC Investment Advisor Public Disclosure**: 美國證券主管機關要求註冊投顧定期申報的公開揭露網站，用於抓 financial intermediary 模板的管理資產 (AUM) 與帳戶數，是最可信的第三方數字。
   - **Compete.com (月獨立訪客)**: 第三方網站流量量測公司，用於抓 advertising destination 模板的每月獨立訪客數，做法沿用 Kerr, Lerner & Schoar (2014) 創投研究先例。
   - **燒光錢二元指標 (Pahnke et al. 2015)**: 「是否在做出能運作的商業模式之前就把錢燒光」的 0/1 指標，補上單看募資總額會錯失的『過程是否走到終點』訊號。
   - **Crunchbase eigenvector centrality (Top-50 VC 判定)**: 在 Crunchbase 早期投資人網路裡用特徵向量中心性排序——看每個 VC 跟其他重要 VC 連得多近、多廣——客觀判定哪些算 Top-50 VC，用於可比性控制。
   - **Poll of industry analysts**: 對行業分析師與專家做投票式排名，加上質性評價，反映業界共識下『誰被認為做得好』。
5. 與此篇文章的關係:
   在《Parallel Play: Startups, Nascent Markets, and Effective Business-model Design》(McDonald & Eisenhardt, 2020) 這篇文章中，作者要把「過程效能」的判定立在客觀的量化基底上、不依賴受訪者自說自話。他們採用了檔案資料與第三方量化指標蒐集：吃前一步圈出的 5 家公司樣本，產出 248 篇媒體文章、SEC 申報的 AUM、Compete.com 流量、Crunchbase VC 中心性等多軌資料。這套做法解決了質性研究最常被挑戰的「績效衡量主觀」與「事件時序被事後重構」瓶頸，為下游 borrowing 編碼、focus 量化、案例史合成提供可三角驗證、有時間戳、模板對齊的客觀錨點。
