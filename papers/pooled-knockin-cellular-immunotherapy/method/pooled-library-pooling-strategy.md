# Pooled Knockin Library 池化策略選擇

1. 引用自哪篇 paper: pooled-knockin-cellular-immunotherapy
2. Outline (任務主線): Pooled Knockin Library 池化策略選擇
3. Method: 
   在「把 36 個成員混到同一條產線上」這件事上，每個工序都有可能讓 A 模板的 barcode 跑到 B 模板的 Insert X 上——這個現象叫 template switching。原因是模板們大部分序列相同（同樣的 TCRβ、同樣的同源臂），只差中段，DNA 聚合酶或細胞 HDR 抄寫到一半，正在抄的鏈可能會「跳」到旁邊一條長得很像的模板上接著抄，導致 barcode 與真實 Insert X 對不上。為了找到「在哪一站才把所有成員倒進同一桶」傷害最小，作者沿著 protocol 系統測試了四個池化點：(1) Pooled Assembly——36 條 gBlock 全部倒進同一管 Gibson Assembly 一次組裝；(2) Pooled PCR——36 個質體個別組好後混在一起 PCR 擴增 HDR template；(3) Pooled Electroporation——每個質體個別 PCR 出 HDR template，混在一起後與 RNP 共電穿孔；(4) Pooled Culture——每個 HDR template 與細胞個別電穿孔後再把細胞混在一起培養。測試方法用「2-member 校正庫」：只放兩個成員，一個帶 GFP、一個帶 RFP，但都各帶獨特 barcode。電穿孔後用螢光分選把 GFP+ 與 RFP+ 細胞分開讀 barcode——細胞發什麼顏色光就代表原本該裝什麼版本，混到對方那邊的比例就是 switching 的實測值。GFP/RFP 提供了獨立於 barcode 的 ground truth，這是 36 成員大庫做不到的事。
   結果非常清楚：越晚池化、switching 越少。Pooled Assembly 推算的真實 switching 約 50%——意思是讀到的 barcode 有一半與細胞真正裝的 Insert X 對不上，整套 fitness 排序失去意義。Pooled Electroporation 推算約 10%，已是可接受範圍。為什麼？switching 主要發生在「DNA 鏈被聚合酶延伸時有同源序列在旁邊」的時刻，早池化讓所有模板從 gBlock 拼成質體、再到 PCR 大量擴增全程泡在一起，跳模板的機會逐站累積；晚池化時每個模板已是純淨成品 dsDNA，唯一還可能 switching 的就是細胞內 HDR 抄寫的瞬間，機會大幅減少。理論上 Pooled Culture 還會更低，但這等於要為每個構築單獨做一次電穿孔——36 個成員就要 36 次平行操作，pooled screen「一次處理一大群」的吞吐量優勢就消失了，回到 arrayed 模式。所以作者最終選 Pooled Electroporation：switching 已壓到 ~10% 的可接受範圍，同時保留一次電穿孔處理整池模板的吞吐量。
4. 工具與材料: 
   - **Template switching**: 多個同源模板共存時，DNA 鏈延伸到一半跳到別條模板繼續延伸，造成 barcode 與真實 Insert X 對不上的現象。
   - **Pooled Assembly**: 在 Gibson 階段就把所有成員混在一起組裝；switching 最嚴重，推算真實值約 50%。
   - **Pooled PCR**: 質體個別組好後混在一起 PCR 擴增 HDR template。
   - **Pooled Electroporation**: 每個 HDR template 個別 PCR 純化後混在一起與 RNP 共電穿孔；作者最終選定，switching 推算約 10%。
   - **Pooled Culture**: 細胞個別電穿孔後再混在一起培養；switching 最低但失去 pooled 吞吐量。
   - **2-member GFP/RFP library**: 校正用迷你庫；以顏色為獨立 ground truth，FACS 分選後讀 barcode 量化 switching。
   - **FACS 分選**: 螢光細胞分選，把 GFP+ 與 RFP+ 細胞分開後個別讀 barcode 純度。
5. 與此篇文章的關係: 
   在《Pooled Knockin Targeting for Genome Engineering of Cellular Immunotherapies》這篇文章中，作者要把 36 條 barcoded HDR 模板在原代 T 細胞中一次比拼。本子項用 2-member GFP/RFP 校正庫沿著 protocol 各階段量化 template switching，解決了「池化階段越早 barcode 錯換越多、整套 fitness 排序失真」的瓶頸；產出「Pooled Electroporation 為最佳池化點 (switching ~10%)」這個結論，定下 2-C 電穿孔步驟與下游 2-H barcode 擴增的標準作業點。
