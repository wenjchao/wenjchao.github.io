# ECM Proteomics (Hydroxylamine + QconCAT + LC-SRM)

1. 引用自哪篇 paper: pediatric-tri-tube-valved-conduit
2. Outline (任務主線): 對四個 tube batch 量化約 250 種 ECM 與 ECM-affiliated 蛋白的絕對濃度 (nmol/g)，回答「不同 batch 間結果差異是否來自 starting matrix 蛋白組成」這個臨床轉譯關鍵問題。
3. Method:

作者要回答一個臨床轉譯級別的問題：四批 tube 做出來的瓣膜有的撐到 12 週就壞、有的撐到 62 週，是不是因為這四批起始的膠原蛋白管成分本來就不一樣？要排除「材料 batch 不穩定」這條退路，必須精確量化每一批裡 ~250 種 ECM 蛋白的絕對濃度。這在技術上比一般 proteomics 難很多——ECM 蛋白彼此大量交聯 (crosslinking)，整塊組織硬得像水泥湯，一般用的胰蛋白酶根本打不進去、只能切到表面。所以作者先用一個小分子化學試劑：取 ~3 mg tissue、加 1 M hydroxylamine（5 mg/mL、3 小時，protocol 採自 Barrett et al., J. Proteome Res. 2017）。Hydroxylamine 可以擴散進緻密的 ECM 網內、選擇性切斷「天門冬醯胺-甘胺酸 (Asn-Gly)」這種特定胺基酸組合的肽鍵，水泥湯一旦被切斷就會散開成可溶碎片，後續胰蛋白酶才有機會接著消化。這一步是 ECM proteomics 比一般 proteomics 多出來的關鍵化學前處理。

一般質譜只能給「相對強度」——能看出 A 蛋白多 B 蛋白少，但說不出「A 是 5 nmol/g、B 是 1 nmol/g」這種絕對數字。要拿絕對量，每個目標蛋白都需要「已知重量的參考砝碼」一起跑。作者用的砝碼叫 QconCAT (Quantification conCATamer)：把所有目標蛋白裡用來定量的代表性肽段串成一長條人造蛋白，放入大腸桿菌表達時用 ¹³C₆ 標記的胺基酸培養，所以每個肽段都比天然版重 6 Da。為什麼挑 ¹³C₆？因為 ¹³C 是穩定同位素、化學行為和 ¹²C 一樣，6 個原子讓肽段差距 6 Da——足夠和原生肽段在質譜上分出兩個獨立峰、但 UHPLC 滯留時間完全一樣；差 1 Da 會被天然 ¹³C 同位素峰污染、再重沒必要。樣本加入 500 fmol QconCAT 後一起跑質譜，會同時看到「樣本中的天然肽段」和「QconCAT 裡的 ¹³C₆ 重肽段」兩個並列峰；算「樣本峰強度 ÷ 重峰強度 × 500 fmol」就得到樣本裡那個肽段的絕對 moles，再除以樣本質量就得到 nmol/g。接著用 FASP（過濾式樣本前處理 filter-aided sample preparation，Hill et al., 2015）讓胰蛋白酶把樣本進一步消化成適合質譜分析的短肽。

肽段消化好後送進 Dionex Ultimate 3000 UHPLC 搭配 Acquity UPLC BEH C18 column 分離，再進 AB Sciex QTRAP 5500 三聯四極桿質譜儀，用 LC-SRM (Selected Reaction Monitoring) 模式量化。為什麼用 SRM 而不用一般 shotgun？因為 shotgun 像「廣撒網」，每次跑可能抓到不同的肽段，做絕對定量時重現性差；SRM 則是「狙擊」——作者事先給質譜一張清單，「請只看這 ~250 個目標蛋白的特定肽段、並只追蹤每個肽段被打碎後產生的特定碎片離子 (parent ion m/z → fragment ion m/z)」。三聯四極桿質譜為這個模式設計：第一個四極桿只放預設質量的母離子進來、碰撞室打碎、第三個四極桿只看預設質量的子離子。代價是「沒看到不在清單上的蛋白」，但對 ~250 個指定蛋白的封閉問題，靈敏度與重現性比 shotgun 高 10-100 倍。最後用 Skyline 軟體手動檢查每個峰的形狀是否乾淨、有沒有干擾，只有確認過的峰才用來算濃度——這個人工檢查不能省，因為軟體誤判一個峰、後續 ANOVA 就可能誤判某個蛋白 batch 間有差異。最終輸出每個 batch 的 ~250 個蛋白絕對濃度 (Table S1, nmol/g)。

四個 batch 不是隨便挑的數量，而是為了統計設計的最小要求：用 four independent tube batches 做 two-way ANOVA 看 ~250 個 ECM 蛋白是否在 batch 間有系統性差異。如果結果顯示「batch 間幾乎沒差、只有 fibrillar collagen 總量略有差」，就能堵住「材料 batch 不穩定」這條退路，把結果差異歸到「細胞反應」「機械力」這些下游機制。整套流程有兩個關鍵失敗模式：第一是 hydroxylamine 化學裂解不完整——水泥湯沒被敲碎到底，胰蛋白酶進不去緻密的膠原蛋白與彈性蛋白網，這些難消化的不溶蛋白被低估、容易消化的可溶蛋白被「相對放大」，整個 ECM 組成圖會系統性偏向容易測到的蛋白，掩蓋真實的 collagen 比例差異；所以濃度 (5 mg/mL) 與時間 (3 hr) 必須嚴格控制。第二是 QconCAT 內標量偏離線性響應區——絕對定量假設「兩個並列峰都在質譜的線性響應範圍內」，內標濃度比樣本高 1000 倍會飽和、低 100 倍會掉進雜訊，兩種情況下「樣本峰 / 內標峰」的比例都會失真，算出來的絕對濃度可能差好幾倍。所以 500 fmol 是基於作者對 ECM 蛋白濃度範圍的預估，換到不同樣本類型時內標量要重新摸索。

4. 工具與材料:

   - **hydroxylamine 化學裂解**: 小分子化學試劑，擴散進緻密 ECM 切斷 Asn-Gly 肽鍵，把交聯水泥湯打散成可溶碎片。
   - **FASP (filter-aided sample preparation)**: 過濾式樣本前處理。在過濾裝置內讓胰蛋白酶把蛋白進一步切成短肽，方便質譜分析。
   - **QconCAT (¹³C₆-labeled)**: 把目標肽段串成一長條人造蛋白，用 ¹³C₆ 標記讓肽段比天然版重 6 Da，當作絕對定量的「參考砝碼」。
   - **LC-SRM (Selected Reaction Monitoring)**: 三聯四極桿質譜的目標模式。只追蹤預設的肽段 → 碎片離子轉換，靈敏度與重現性比 shotgun 高 10-100 倍。
   - **AB Sciex QTRAP 5500**: 本實驗使用的三聯四極桿質譜儀，為 SRM 模式設計。
   - **Dionex Ultimate 3000 UHPLC**: 液相層析系統。搭配 C18 column 把肽段依疏水性分離後進質譜。
   - **Skyline**: SRM 數據分析軟體。提供視覺化界面讓人手動檢查每個目標肽段的峰形與整合。
   - **absolute quantification (nmol/g)**: 絕對定量。每克組織含多少 nmol 某蛋白，由樣本峰 ÷ 內標峰 × 已知內標量算出。
   - **two-way ANOVA**: 兩因子變異數分析。檢測 batch 與蛋白類別兩個因子對濃度的影響，判斷 batch 間是否有系統差異。

5. 與此篇文章的關係:

這個 ECM proteomics 模組在整篇論文裡扮演「替代假說的排除者」：作者在生長羊模型中觀察到四隻 Gen 1 tri-tube 瓣膜壽命差距極大（有的 12 週就退化、有的撐到 62 週），審稿人最直覺的質疑就是「會不會其實只是四批起始組織管的材料本身不穩定」，因此必須對四個 tube batch 中約 250 種 ECM 與 ECM-affiliated 蛋白做絕對濃度 (nmol/g) 的量測，而不是只比相對高低。它的好處有三：用 hydroxylamine 化學裂解先把高度交聯、胰蛋白酶打不進去的不溶 ECM 切散，補上一般 shotgun proteomics 在 ECM 上的盲點；用 ¹³C₆-QconCAT 內標讓每個蛋白都拿到可跨論文比較的絕對數字，能直接對齊原生肺動脈瓣文獻值；用 LC-SRM 把質譜變成「只認這 250 個蛋白」的客製化偵測器，靈敏度與重現性遠勝 shotgun，後續 two-way ANOVA 才有統計檢力宣稱 batch 間無系統差異。它與其他方法相互咬合：上游接 fibroblast-fibrin 組織管培養（提供四個 batch 的原料），下游餵給 PLS-DA + Ward clustering 熱圖視覺化、以及 two-way ANOVA 統計檢定，並與 echocardiography 觀察到的活體壽命差異、histology 的重細胞化證據、力學測試的 modulus 結果共同形成一條「材料 → 細胞 → 機械 → 功能」的因果鏈，把 Gen 1 失敗原因從「材料 batch 不穩」逼向「細胞反應與 cyclic stretching 機制」，並為 Gen 2 sleeve 改良提供 mechanistic 合理性。
