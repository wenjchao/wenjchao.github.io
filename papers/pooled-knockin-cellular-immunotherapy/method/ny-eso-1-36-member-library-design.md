# NY-ESO-1 TCR + 36-member 構築 Library 設計

1. 引用自哪篇 paper: pooled-knockin-cellular-immunotherapy
2. Outline (任務主線): NY-ESO-1 TCR + 36-member 構築 Library 設計
3. Method: 
   整個 library 為什麼共用同一支 TCR？因為不同 TCR 對抗原的抓握強度差很多——強的一抓住抗原 T 細胞就猛攻、弱的可能根本沒反應。如果每個構築用不同的 TCR，最後勝出的可能是「天線本來就強」而不是「外掛功能基因有用」。作者選的天線是辨識 NY-ESO-1 的 1G4 clone TCR（NY-ESO-1 是很多黑色素瘤細胞會在表面亮出來的腫瘤抗原，已被臨床測過），把它當成所有構築的共用骨架後，每個構築對 A375 黑色素瘤的「抓握強度」就一樣，剩下唯一的差異就是 Insert X 與條碼。最後讀到的勝負才能歸因到外掛本身。
   36 個構築涵蓋三大改造策略，分別瞄準 T 細胞在腫瘤環境裡被壓制的三條互補路徑。第一是「誘餌 receptor」(dominant negative)：把原本傳遞抑制訊號的天線（例如 Fas、TGF-βR2）砍掉胞內訊號段、只留辨識端後大量過表現，這種沒下游的天線會跟正常 receptor 競爭 ligand，把抑制訊號截胡耗掉；正向控制取自文獻已知有效的 truncated Fas (Yamamoto et al., 2019) 與 truncated TGF-βR2 / dnTGFβR2 (Gorelik & Flavell, 2000; Kim et al., 2017; Kloss et al., 2018)。第二是「拼裝 receptor」(switch receptor)：胞外仍抓抑制訊號、胞內換成 41BB 或 CD28 這類活化開關，新穎構築包括 Fas-41BB、TGF-βR2-41BB、CTLA4-CD28、TIM3-CD28、PD1-41BB 等。第三是直接整顆過表現內部元件：例如讓 T 細胞停留在年輕未耗竭狀態的轉錄因子 TCF7、讓細胞更抓得到 IL-2 鼓勵訊號的細胞因子受體 IL2RA。三類並列才能避免「在錯的範圍內找最強」的偏見——後續結果證明 in vivo 勝者 TCF7 是純粹的轉錄因子，如果只放 switch receptor 就會漏掉。所有構築都存放於 Addgene (編號詳列於 Table S1)。
   以 TGF-βR2-41BB 示範 switch receptor 怎麼拼。作者把兩個天然 receptor 從中間切一半再拼起來：胞外用 TGF-βR2 的天線部分（負責抓住 TGF-β），胞內換成 41BB 的訊號段（負責喊「衝啊」）。原本 TGF-βR2 抓到 TGF-β 後會啟動 SMAD 路徑把 T 細胞踩煞車；胞內換成 41BB 後，同一個 TGF-β 訊號被傳進細胞時走的是 NF-κB 與 TRAF 這條「我要打仗」的路徑。等於把腫瘤的煞車訊號改寫成油門訊號。值得注意的是 switch receptor 能不能起作用，關鍵在「胞外的 ligand 在腫瘤微環境裡是不是常常存在」——作者挑的 TGF-β、Fas、PD-1、CTLA-4 這些胞外端，配體在腫瘤微環境裡都確實大量存在，receptor 才有機會被觸發。如果胞外換成腫瘤不分泌的訊號（例如 IL-2），整合進細胞後永遠沒機會啟動，等於插了一張不會發亮的擴充卡。
4. 工具與材料: 
   - **NY-ESO-1 TCR (1G4 clone)**: 辨識黑色素瘤抗原 NY-ESO-1 的高親和力臨床等級 TCR 骨架，36 個構築共用。
   - **dominant negative receptor**: 保留胞外辨識端、刪除胞內訊號段的誘餌 receptor，過表現後競爭性吸走 ligand。
   - **switch receptor**: 胞外抓抑制訊號、胞內換成活化開關（41BB、CD28）的拼裝 receptor。
   - **TGF-βR2-41BB**: 新穎 switch receptor：胞外 TGF-βR2 抓 TGF-β、胞內 41BB 啟動 NF-κB/TRAF 活化路徑。
   - **TCF7**: 讓 T 細胞停留在年輕未耗竭狀態的轉錄因子，過表現策略代表。
   - **IL2RA**: 讓細胞更抓得到 IL-2 鼓勵訊號的細胞因子受體 α 鏈，過表現策略代表。
   - **truncated Fas / TGF-βR2**: 已知的 dominant negative 正向控制，分別參考 Yamamoto et al., 2019 與 Gorelik/Flavell, 2000、Kim et al., 2017、Kloss et al., 2018。
   - **Addgene**: 公開質體庫，所有構築存放於此，編號詳列於 Table S1。
5. 與此篇文章的關係: 
   在《Pooled Knockin Targeting for Genome Engineering of Cellular Immunotherapies》這篇文章中，作者為了系統比較三類抗腫瘤改造策略，採用了共用 1G4 NY-ESO-1 TCR 骨架的 36-member library 設計。它解決了過去單一策略測試無法跨機制比較的瓶頸，把唯一變數壓在 Insert X。產出的 36 個質體構築直接作為 HDR template PCR 擴增的原料，供下游 pooled knockin screen 使用。
