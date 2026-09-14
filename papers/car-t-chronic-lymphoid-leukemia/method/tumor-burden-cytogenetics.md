# 腫瘤負荷與細胞遺傳學評估（Cytogenetics、FISH、Flow、CT）

1. 引用自哪篇 paper: car-t-chronic-lymphoid-leukemia
2. Outline (任務主線): 腫瘤負荷與細胞遺傳學評估（Cytogenetics、FISH、Flow、CT）
3. Method:
      作者要證明病人達到完全緩解，一種工具做不到——他從四個不同尺度同時拍同一個腫瘤：染色體核型分析 (karyotype) 把分裂中期的染色體一條條染色看形狀，能看到大段異常，例如 baseline 20 個細胞裡有 10 個帶 17p 相關異常 (46,XY,del(17)(p12)[5]/46,XY,der(17)t(17;21)(q10;q10)[5]/46,XY[14])，治療後 15/15 顆全部回復正常。螢光原位雜交 (fluorescence in situ hybridization, FISH) 用一支專門黏到 TP53 基因的螢光探針，在 200 顆細胞裡直接數幾顆有兩份訊號、幾顆缺失——baseline 170/200 顆陽性、治療後只剩 2/200 (落在陰性對照的背景範圍)。多參數流式細胞儀 (multi-parameter flow cytometry) 從細胞層次量 CD19⁺CD5⁺ 亞群、以及這群細胞的 κ/λ 免疫球蛋白光鏈分布。對比增強電腦斷層 (contrast-enhanced CT) 則從解剖層次量 axillary 等淋巴結體積——在入組前、Day 31、Day 104 各拍一次，看到原本 1–3 cm 的淋巴結在一個月內完全退散。
   flow 判 clonality 的邏輯建立在 B 細胞成熟時的「等位排除 (allelic exclusion)」上——每顆 B 細胞隨機挑 κ 或 λ 其中一種輕鏈用，正常 B 細胞群體 κ:λ 大約 2:1。癌細胞是從同一顆祖細胞複製出來的億萬個複本，全都繼承同一種光鏈；因此看到 CD19⁺CD5⁺ 亞群裡 κ 佔壓倒性 (例如 >95%) 就代表單株增殖 (clonal expansion)。本案 baseline 骨髓 CD19⁺CD5⁺ 幾乎全表達 κ，Day 31 flow 顯示 CD5⁺CD10⁻CD19⁺CD23⁺ 淋巴球 gate 已 <1%，連正常 B 細胞都測不到。dot-plot x/y 兩軸都用 log₁₀ scale 是因為細胞表面 marker 螢光橫跨好幾個數量級，用線性尺度會讓弱陽性擠在原點、強陽性拉到圖外；log 尺度讓 dim 與 bright 都能同時看到，方便 gating。
   為什麼一定要四種都做、只做一種不行？每個工具各自有盲點：karyotype 只看 15–20 顆分裂中期細胞、殘餘 clone 若低於 5% 會直接漏掉；FISH 靈敏但只點單一位點；flow 有細胞層次卻看不到染色體；CT 只看解剖不看細胞。作者要下「完全緩解」的診斷，就必須讓四個工具彼此對得上：karyotype 15/15 顆回復正常、FISH 只剩 2/200 落回背景、flow CD5⁺CD10⁻CD19⁺CD23⁺ <1%、CT 淋巴結完全退散——四張獨立證據互相 cross-check，才能排除單一模態誤判。若只做 karyotype，殘餘低比例 CLL 可能被誤為 CR；若只看 flow 的 CD19⁺CD5⁺ 比例、不看 κ/λ 光鏈，反應性 B 細胞浸潤與真正單株 CLL 難以區分。這種多正交結構是本篇說服 FDA 與 review board 「n=1 case 真的達到 CR」的關鍵。
4. 工具與材料:
   - **Karyotype**: 分裂中期染色體 G-band 染色觀察，能看到大段結構異常，例如 baseline del(17p) 的兩支 clone。
   - **FISH**: 用序列特異螢光探針對 200 顆 interphase 細胞的 TP53 位點雜交，直接數陽性百分比 (baseline 170/200 → 治療後 2/200)。
   - **Multi-parameter flow cytometry**: 用多支螢光抗體 (CD19、CD5、CD10、CD23、κ、λ) 同時掃每顆細胞，先 gate CD19⁺CD5⁺ 再看 κ/λ 分布。
   - **κ / λ light chain clonality**: 基於 B 細胞 allelic exclusion 的判讀邏輯——單一光鏈壓倒性表達代表單株增殖。
   - **Log₁₀ dot-plot**: flow dot-plot 兩軸用 log₁₀ 尺度，讓 dim 與 bright positive 都能同時呈現。
   - **Contrast-enhanced CT**: 從解剖層次量 axillary 等淋巴結體積變化；入組前、Day 31、Day 104 各拍一次。
5. 與此篇文章的關係:
   在《Chimeric Antigen Receptor–Modified T Cells in Chronic Lymphoid Leukemia》這篇文章中，作者為了在 n=1 case 上客觀宣告完全緩解，採用了 karyotype + FISH + multi-parameter flow + contrast-enhanced CT 四種正交診斷工具。這個方法解決了「單一模態各有盲點、殘餘低比例 CLL clone 或反應性 B 細胞浸潤可能被誤判」的瓶頸，把染色體、單一基因位點、細胞單株性、解剖淋巴結四張獨立證據疊在一起交叉驗證，把 tumor burden 降至可測極限的結論寫進論文。
