# Multiplexed luciferase reporter assay

1. 引用自哪篇 paper: de-novo-design-of-luciferases
2. Outline (任務主線): Multiplexed luciferase reporter assay
3. Method: 
   作者把三段 DNA 構築一次塞進同一批 HEK293T 細胞，目標是在「同一管細胞」裡同時量兩條訊號通路。第一段是「發炎開關 (NF-κB binding site) → LuxSit-i」，只有當 NF-κB 通路被打開時下游的 LuxSit-i 才會被表達；第二段是「荷爾蒙開關 (cAMP response element, CRE) → RLuc」，只有 cAMP–PKA 通路被打開時 RLuc 才被表達；第三段是「常開的 CMV 啟動子 → CyOFP」，CyOFP 是一個 cyan-orange 螢光蛋白、與訊號通路無關，永遠都在表達，當作這顆細胞「我在這、我活著」的內參。為什麼要這支內參？因為同樣是 HEK293T，不同孔位真正轉染成功的細胞數可能差 4–8 倍——加 plasmid 手抖、孔位邊緣細胞長得少之類的技術雜訊，跟訊號通路無關。作者把每孔的發光量 (RLU) 除以同一孔的 CyOFP 螢光，得到「每顆轉染成功的細胞貢獻多少光」(RLU / a.u.)，再歸一化到沒加刺激物的對照組，技術雜訊除掉後剩下的差異才真的反映訊號通路本身。要測試兩條通路是否真的能各自被讀到，作者用兩種化學刺激物分別啟動：人類腫瘤壞死因子 (TNF) 是經典發炎訊號，加進去打開 NF-κB；福斯科林 (Forskolin, FSK) 會直接活化把 ATP 轉成 cAMP 的酵素 adenylyl cyclase，等於把 cAMP–PKA 通路強制打開。NF-κB 與 cAMP–PKA 是兩條最常被研究、彼此獨立的細胞訊號開關，是測試多工讀取最經典的搭配；作者特意把 LuxSit-i 接到 NF-κB，靠它對 DTZ 的高專一性即使有 cAMP 燃料污染也不會誤判。LuxSit-i 高度認 DTZ 卻幾乎不認 PP-CTZ，這個 substrate specificity 打開了兩種多工讀取模式。第一種是「時序分離」(substrate-resolved)：先只加 RLuc 的燃料 PP-CTZ 讀一輪，RLuc 把 PP-CTZ 燒成 ~390 nm 紫光、LuxSit-i 完全不反應；等 PP-CTZ 燒光、紫光衰減後，作者再加 DTZ 讀第二輪，換 LuxSit-i 燒 DTZ 發 528 nm 綠光。兩輪在時間與燃料上都互不重疊。第二種是「波長分離」(spectrally-resolved)：兩種燃料同時倒進去，用 Neo2 plate reader 上 528/20 nm 與 390/35 nm 兩個窄頻濾片同時讀，綠光對應 LuxSit-i、紫光對應 RLuc。前者操作簡單但比較慢、後者比較快但需要好的光學系統；兩種都示範代表 LuxSit-i 適用於不同實驗室的設備。為什麼 multiplexed luciferase reporter 在 LuxSit-i 出現前一直做不起來？因為一般天然發光酵素口袋大又開放，遇到 DTZ 跟 PP-CTZ 這類結構只差一兩顆原子的近親燃料都會反應、亂發光：第一輪加 PP-CTZ 時兩顆酵素都發光、第二輪加 DTZ 時也都發光，根本分不清哪一輪的訊號屬於哪一條通路。LuxSit-i 對近親燃料專一性達 28–50 倍，等於把這條路徹底打通。
4. 工具與材料: 
   - **NF-κB binding site → LuxSit-i**: NF-κB 通路打開時下游 LuxSit-i 才被表達的 reporter 構築，用來讀發炎訊號。
   - **CRE → RLuc**: cAMP response element 接 RLuc 的 reporter；cAMP–PKA 通路打開時 RLuc 才被表達。
   - **CMV → CyOFP**: 常開的 CMV 啟動子帶 cyan-orange 螢光蛋白，做每孔細胞數和轉染效率的內參。
   - **TNF**: 人類腫瘤壞死因子，經典發炎訊號刺激物，用來打開 NF-κB。
   - **Forskolin (FSK)**: 活化 adenylyl cyclase 把 ATP 轉成 cAMP，強制打開 cAMP–PKA 通路。
   - **substrate-resolved multiplex**: 先加 PP-CTZ 讀 RLuc、再加 DTZ 讀 LuxSit-i 的時序分離模式，靠 LuxSit-i 的高專一性確保兩輪訊號互不污染。
   - **spectrally-resolved multiplex**: 兩種燃料同時加入，用 528/20 與 390/35 nm 雙窄頻濾片同時讀兩種波長的多工模式。
   - **Neo2 plate reader**: 可同時讀兩個 bandpass filter 的盤式偵測儀，用來執行 spectrally-resolved 讀取。
   - **RLU / CyOFP normalisation**: 每孔的發光量除以同一孔的 CyOFP 螢光 (Ex/Em = 480/580 nm)，校正細胞數與轉染效率。
5. 與此篇文章的關係: 
   在《De novo design of luciferases using deep learning》這篇文章中，作者為了把 LuxSit-i 的高專一性實際變成「能在同一管細胞同時讀兩條訊號通路」的工具，採用了三 plasmid 共轉染加 substrate-resolved 與 spectrally-resolved 雙讀取的 multiplexed reporter assay。這個方法解決了傳統天然發光酵素對近親燃料 cross-reactivity 所造成的訊號互相污染瓶頸，把前一步驗證的 LuxSit-i 表達細胞與 CRE-RLuc 配對，產出 NF-κB 與 cAMP–PKA 兩條通路的獨立量化讀數，直接證明這套人工 luciferase 在 reporter assay 應用層級確實可用。
