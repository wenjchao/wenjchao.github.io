# NNK randomized library 組合突變篩選

1. 引用自哪篇 paper: de-novo-design-of-luciferases
2. Outline (任務主線): NNK randomized library 組合突變篩選
3. Method: 
   SSM 標出 LuxSit 上三個可動的熱點：位置 60、96、110。下一步作者要撈出三點同時改的協同效應 (epistasis)，所以做了一條 NNK randomized library。「NNK」是訂 oligo 時用的簡併密碼子 (degenerate codon)：第一、第二鹼基寫成 N (A/T/G/C 任意)、第三鹼基寫成 K (G/T 任意)，每個位置 32 種寫法卻仍涵蓋全部 20 種胺基酸。為什麼不直接用 NNN？因為 NNN 有 3 個終止子，每位置 4.7% 機率截短，三位置一起累積到 13% 失敗率；NNK 限制第三鹼基後只剩 TAG 一個終止子，失敗率壓到 9%。三位點 NNK 的組合數是 $32^3 \approx 33{,}000$ codon、涵蓋 $20^3 = 8{,}000$ 個胺基酸組合，剛好在幾片培養盤 colony 數可覆蓋的範圍內——擴到四位點就跳到 $10^6$、要上百片盤或改用 FACS，成本立刻翻倍。三個熱點對 LuxSit 來說已是 SSM 標出最強的三個位置，足夠。
NNK 三點同時隨機這個策略，目的就是抓 SSM 看不見的東西。協同效應指的是：一個位置單獨改沒效，但配合別位一起改才會跳。LuxSit-i (R60S/A96L/M110V) 正是經典例子——R60 在 loop 上突出、沒有 H-bond 夥伴，SSM 整條 profile 平平無奇，照單點規則絕對挑不到 Ser；但 NNK 跑完，最亮的菌落定序回來剛好是 R60S+A96L+M110V。後續 MD 模擬解釋了物理意義：A96L 和 M110V 把口袋幾何稍微擠緊後，R60 換成更小的 Ser、loop 才剛好讓出空間讓燃料的反應中間態貼進去，整體比 LuxSit 亮 100 倍以上，比天然 Renilla reniformis luciferase (RLuc) 還亮 38%。如果只做 SSM 然後憑單點最佳組合，永遠停在 16×19 = 304 倍的單點疊加，找不到真正的協同提升。NNK 篩到的另一條 LuxSit-f (A96M/M110V) 走的是 flash-type 閃光動力學，跟 LuxSit-i 互補。
luciferase 反應有兩種動力學型態：flash-type 像閃光燈，一加燃料訊號爆發但幾秒內衰減（LuxSit-f）；glow-type 像穩定燭火，訊號可在幾分鐘到幾十分鐘穩定發出（LuxSit-i）。Colony 噴霧階段曝光時間如果設不對，會偏掉某一型——曝光太短，glow 型訊號還沒累積足會被當沒活性；曝光太長，flash 型已經熄滅也會被低估。所以作者後續用 plate reader 統一紀錄 RLU 前 15 分鐘累積值來定量比較——這個積分視窗對兩種動力學都公平，才能把 flash 和 glow 候選同台比較，並挑出更適合穩定 reporter 應用的 LuxSit-i。
4. 工具與材料: 
   - **NNK degenerate codon**: N = A/T/G/C 任意、K = G/T 任意的簡併密碼子，每位置 32 種寫法卻仍涵蓋全部 20 AA。
   - **epistasis**: 多位置同時改才會出現的協同效應；單點掃描看不到。
   - **LuxSit-f (A96M/M110V)**: NNK 篩出的 flash-type 變異株：訊號爆發後快速衰減。
   - **LuxSit-i (R60S/A96L/M110V)**: NNK 篩出的 glow-type 主力變異株：穩定發光、光通量比 LuxSit 高 100 倍以上、比 RLuc 還亮 38%。
   - **RLU 前 15 分鐘累積值**: 對 flash 與 glow 兩種動力學都公平的積分定量視窗。
5. 與此篇文章的關係: 
   在《De novo design of luciferases using deep learning》這篇文章中，作者為了把 LuxSit 從會發光提升到追上天然酵素的水準，採用了 NNK 三位點組合突變庫，撈出協同變異 LuxSit-i。這個方法解決了「SSM 一次只看一個位置、看不見多位點協同效應」的瓶頸，吃 SSM 標出的 60/96/110 三個熱點當輸入，產出活性比 LuxSit 高 100 倍以上的 LuxSit-i，直接交給下游酶動力學定量比較。
