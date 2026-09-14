# Flow-cytometric 定量分析與 log 尺度腫瘤 clonality 判讀

1. 引用自哪篇 paper: car-t-chronic-lymphoid-leukemia
2. Outline (任務主線): Flow-cytometric 定量分析與 log 尺度腫瘤 clonality 判讀
3. Method:
      作者從骨髓吸取物做出單細胞懸液，加入一組各帶不同螢光顏色的抗體 (anti-CD19、anti-CD5、anti-CD10、anti-CD23、anti-κ、anti-λ)，每支只認一種表面蛋白，像貼色卡一樣掛到細胞表面。多餘抗體洗掉之後，細胞被送進多參數流式細胞儀 (multi-parameter flow cytometry)。儀器用一種叫流體聚焦 (hydrodynamic focusing) 的技術把細胞懸液擠成極細的一條線通過雷射點——就像把一鍋湯灌進吸管，細胞被迫排單縱隊、一顆一顆穿過光束。每顆細胞經過時同時做兩件事：散射光被前後兩支偵測器讀走 (前散射 → 細胞大小；側散射 → 內部顆粒度)；掛在表面的螢光抗體被雷射激發，各自的螢光被幾支光電倍增管 (photomultiplier tubes, PMT) 分色接收。因為每種螢光染料的激發峰與發射峰彼此錯開，多顏色在同一顆細胞上互不打架——最後每顆細胞都拿到「它是 CD19⁺ 嗎？CD5⁺ 嗎？κ 或 λ？」的完整多維座標。
   分層 gating 的作用是把訊噪比從「幾千比一」拉到「幾比一」。骨髓混著 T 細胞、B 細胞、漿細胞、B 前驅細胞、紅血球前身，直接把整鍋細胞的 κ/λ 分佈畫出來訊號會被非 B 細胞背景稀釋。作者先在第一張 dot-plot 上框出「同時 CD19⁺ 又 CD5⁺」的象限——這個組合是 CLL 幾乎專屬的表現型 (正常成熟 B 細胞的 CD5 通常是負的)——只把落在這個框內的細胞往下傳。第二張 dot-plot 只畫這批細胞的 κ 對 λ；為什麼看 κ/λ 就能判 clonality？因為 B 細胞在發育時隨機挑一條免疫球蛋白輕鏈基因當抗體零件——不是 κ 就是 λ——這個選擇一旦拍板，該細胞及其所有後代終身用同一種。正常人骨髓 B 細胞是幾千個獨立 clone 的混合，κ:λ 約 2:1；癌細胞若全部只帶 κ 或全部只帶 λ，就是「同一祖先繼承同一選擇」的分子指紋 (clonal restriction)。本研究病人 baseline 呈現 clonal κ 表現，Day 31 這一 clone 消失，就是「腫瘤 clone 被清除」的直接證據。
   作者為什麼把 dot-plot 的 x/y 軸都設成 log₁₀ 尺度？因為免疫染色訊號的動態範圍通常橫跨 3–4 個數量級——同一顆細胞可能綁 100 支抗體 (中度陽性)、也可能綁 10000 支 (強陽性)，兩者相差 100 倍。如果用線性刻度，10000 那顆被拉到最右上、其他細胞全擠成左下角一團黑點，dim 陽性與真正陰性根本分不開。改成 log 尺度後，每個「decade (十倍)」佔一格視覺空間，陰性、弱陽性、中度、強陽性都能清楚分開。這對本研究更關鍵：baseline 骨髓 40% 是 CLL clone，Day 31 已降到 <1%，log 軸才容納得下「一個 clone 從 40% 掉到 0.01%」這種跨四個量級的殞落。
   流式判讀有兩個常被漏掉的失敗模式。第一是 gating 邊界畫錯——太寬會把非 CLL 的 T 細胞或漿細胞納入 CD5⁺CD19⁺ 象限、稀釋掉真正 clone 的 κ 偏好；太窄則直接把弱陽性 CLL 排除、把 clone 消失量高估。第二是「螢光光譜補償 (spectral compensation) 沒做好」——每種螢光染料的發射光譜有 tail 會漏進鄰近偵測通道 (例如 FITC 訊號會在 PE 通道多讀出一點)，若沒把這部分數學扣掉，CD19 強陽性的細胞會被誤讀成 κ 弱陽性，clone 分佈整個歪掉；標準做法是先用單染樣本算出 spillover 矩陣、再自動扣除。而作者用 <1% 當「undetectable」的門檻，也和這些雜訊直接相關——流式即使沒有目標細胞仍會因背景螢光、細胞碎片、rare event 誤判讀出 0.1–0.5% 的假陽性，血液學界一律用 <1% 當「臨床上偵測不到」的閾值。Day 31 讀到 <1% 因此可宣稱為 CLL 已無殘留，但意義是「若還有也已低到儀器分辨力之下」，不是絕對零。
4. 工具與材料:
   - **多參數流式細胞儀 (multi-parameter flow cytometry)**: 讓細胞單縱隊通過雷射、同時讀多個螢光通道的儀器，每顆細胞可以同時得到多個表面標記的定量結果。
   - **流體聚焦 (hydrodynamic focusing)**: 用外層 sheath fluid 把細胞懸液擠成極細單縱隊的流體技術，讓細胞一顆一顆通過雷射點。
   - **螢光標記抗體 panel**: anti-CD19、anti-CD5、anti-CD10、anti-CD23、anti-κ、anti-λ 各帶不同螢光染料的抗體組合。
   - **分層 gating**: 先在第一張 dot-plot 框出 CD19⁺CD5⁺ (CLL 表現型)，再在第二張 dot-plot 只看這批細胞的 κ/λ 分佈，以拉開訊噪比。
   - **immunoglobulin κ / λ light chain**: B 細胞在發育時隨機二擇一的輕鏈基因；一群細胞是否全用同一種，是判定是否來自單一 clone 的分子指紋。
   - **log₁₀ 雙軸 dot-plot**: 把 x/y 軸都設為 log₁₀ 尺度，讓橫跨 3–4 個 decade 的螢光訊號在視覺上分得開。
   - **螢光光譜補償 (spectral compensation)**: 先用單染樣本算出各螢光染料漏進鄰近通道的 spillover，再從樣本讀值中數學扣除，避免顏色互相干擾。
   - **<1% undetectable 門檻**: 血液學流式界的傳統閾值——低於 1% 視為儀器分辨力之下，臨床上判為 undetectable 而非絕對零。
5. 與此篇文章的關係:
   在《Chimeric Antigen Receptor–Modified T Cells in Chronic Lymphoid Leukemia》這篇文章中，作者為了在細胞層次證明 CART19 已把 CD19⁺CD5⁺ CLL clone 從骨髓中清除，採用了多參數流式細胞儀 + log₁₀ 雙軸 dot-plot 判讀。此方法解決了「跨四個量級的 clone 消長無法在線性圖上呈現」的視覺瓶頸；它吃入骨髓吸取物的多色染色樣本，產出 clone 是否 <1% 的客觀判讀，直接支撐 karyotype/FISH 的細胞遺傳學結論並與 qPCR/Luminex 時間軸疊圖。
