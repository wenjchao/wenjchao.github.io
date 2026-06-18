# 微結構觀察 (SEM)

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): 微結構觀察 (SEM)
3. Method: 
   GelMA 固化後內部會留下一個三維孔網——孔多大、密不密，取決於 GelMA 鏈彼此的交聯有多緊。當作者把 NV 嵌進去，NV 表面跟 GelMA 鏈會形成非共價鍵：Lip 表面密集排列著磷脂頭基 (phosphate head)，跟 GelMA 鏈側上的胺基 (-NH₂，來自 lysine) 形成氫鍵 (hydrogen bond)；EVs 表面則富含蛋白質、磷脂頭基暴露密度較低，氫鍵就少；hELs 是兩者融合的中間版。鍵越多、越強，NV 等於把鄰近 GelMA 鏈捏在一起 (pseudo-crosslinker)，網被綁得更緊、孔徑變小。所以「孔變小多少」可以反推 NV 跟 GelMA 的鍵強。直接量鍵強實驗上極難，SEM 孔徑是「間接但好量」的代理指標；後面再配 AFM 局部模數與累積釋放曲線，三個證據排序一致才能下結論。

   SEM 必須在高真空下運作，濕水膠會立刻塌、釋出水蒸氣污染儀器，所以樣本必須先脫水。但不能用 air-dry——水蒸發時液-氣界面的表面張力會把孔網拉塌、所有組長得一樣，鍵強排序就看不出來。作者用冷凍乾燥 (freeze-dry)：樣本先 −80°C 凍住一晚、再真空把冰直接昇華成水蒸氣（不經過液態），沒有表面張力、孔網被原樣保留。乾樣切片後還要做 sputter coating（用電漿把幾奈米厚的金鍍在表面）——GelMA 是絕緣體，沒鍍金的話電子束累積的電荷會造成「閃亮條紋」(charging artifacts) 讓孔邊界看不清；鍍金讓電子流走，金也提高二次電子訊號、對比變好。最後用 JSM-IT100 (JEOL) 在 15 kV 加速電壓下拍剖面。每組做 3 塊獨立水膠、人工量 50 個孔的直徑算平均與分布 (n = 50)：3 塊樣本覆蓋批次間變異，50 個孔才有足夠樣本量做統計顯著性比較。
4. 工具與材料: 
   - **scanning electron microscopy (SEM)**: 用聚焦電子束掃描樣本表面、收集二次電子或反射電子成像的顯微鏡，奈米級解析度；本研究儀器為 JEOL JSM-IT100、15 kV 加速電壓。
   - **freeze-dry (lyophilization)**: 把樣本 −80°C 凍住後真空昇華冰，避免水蒸發時的表面張力把孔網拉塌，保留水膠原始多孔結構。
   - **sputter coating**: 用電漿把幾奈米厚的金鍍在絕緣樣本表面，導走電荷避免 charging artifacts，並提高二次電子訊號對比。
   - **charging artifacts**: 絕緣樣本未鍍金時電子束累積電荷造成的閃亮條紋、影像扭曲。
   - **pseudo-crosslinker**: 嵌進水膠的 NV 透過表面與 GelMA 鏈形成非共價鍵，在原有共價交聯網內製造額外的「縫合點」、提升交聯密度。
   - **氫鍵 (hydrogen bond)**: NV 表面磷脂頭基的 P=O 與 GelMA 鏈側胺基 N-H 之間的非共價吸引力，鍵強隨密度增加。
   - **n = 50 孔徑量測**: 每組做 3 塊獨立水膠樣本、人工量總共 50 個孔的直徑，得到具統計力的孔徑分布與平均。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了推斷三種 NV 與 GelMA 基質之間非共價鍵的強弱排序，採用了 SEM 剖面孔徑量測。這個方法解決了「鍵強無法直接量」的瓶頸，把化學鍵差異轉成可以人工數的孔徑差異——Gel-Lip 孔最小（鍵最強）、Gel-EV 孔最大（鍵最弱）、Gel-hEL 居中，為下游 AFM 模數與 NV 釋放曲線提供獨立的結構性對照。
