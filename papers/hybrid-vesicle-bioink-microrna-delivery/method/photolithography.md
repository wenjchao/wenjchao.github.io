# Photolithography 微圖案化

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): Photolithography 微圖案化
3. Method: 
   Photolithography 微圖案化的流程像「果凍版的雷射雕刻」。作者在 6 cm 培養皿底部用兩片手切的玻片當墊角，支撐出一個薄薄的夾層空間，把含有綠色螢光標記混血囊泡 (PKH67-hELs，200 µg ml⁻¹) 的 7.5% GelMA bioink 滴 50 µl 在中間；上方蓋一片玻片，玻片底下事先貼好一張黑色鏤空遮罩 (photomask)——遮罩有洞的地方光透得過去、沒洞的地方光被擋住。整個夾心結構送到 8 cm 下的紫外光燈 (Omnicure S2000, 800 mW) 照 25 秒：光只穿過遮罩鏤空處，把底下對應的 bioink UV 固化；沒被光照到的地方還是液態。解析度由三個因素決定：遮罩鏤空的最小尺寸、光的繞射讓邊緣略微外溢、以及 bioink 夾層的厚度——太厚則光斜射穿出來邊界會糊。兩片玻片夾住 50 µl bioink 等於把厚度壓得很薄，所以邊界相對銳利。

   幾個設計細節值得注意。首先，UV 時間拉長到 25 秒 (擠出式列印是 20 秒)，這是因為光要先穿過「上玻片 + 黑色遮罩」兩層介質，有效光劑量略低，多 5 秒剛好補償損失、確保鏤空對應區的 bioink 完全交聯。其次，作者特意用 PKH67-hELs (綠色脂膜染料標記過的 hELs) 而不是普通 hELs——標記後整個微圖案化結構在螢光顯微鏡下會自動發綠光，不用額外染色就能直接看出 hELs 是否均勻分布在 patterned 區域、邊界是否銳利。等於 PKH67-hELs 同時是「貨」也是「自帶座標的標籤」。

   最後的 DPBS 沖洗是關鍵的一步。沒接到光、還是液態的 bioink 會留在遮罩黑色區對應的地方；如果只洗 1~2 次沒沖乾淨，殘留的液態 GelMA 還會帶著綠色 PKH67-hELs 留在「應該無圖案」的區域，顯微鏡看起來就是邊界糊糊的、整片發綠，分不出鏤空形狀。作者刻意洗 5 次、每次 1000 µl，目的就是把所有未交聯區徹底沖乾淨、留下銳利邊界。
4. 工具與材料: 
   - **Photomask**: 黑色鏤空遮罩，有洞處光透過、沒洞處光擋住，決定 UV 光把哪些區域固化。
   - **Microfabrication / Photolithography**: 用 photomask + 短時 UV 在 bioink 上刻出微結構的圖案化技術。
   - **PKH67-hELs**: 綠色脂膜染料標記的混血奈米囊泡，本實驗中作為「貨 + 自帶螢光座標」雙重角色。
   - **Glass-spacer sandwich**: 兩片手切玻片夾住 50 µl bioink 形成薄夾層，控制 bioink 厚度以提升解析度。
   - **UV exposure (25 s, 800 mW, 8 cm)**: 比擠出式列印多 5 秒以補償穿過遮罩與上玻片的光劑量損失。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者要證明 Gel-hEL bioink 不只擠得出來，也能做高解析微結構。為此採用 photomask + 25 秒 UV 的 photolithography，解決了「擠出式列印解析度受針徑限制」的瓶頸。它吃 PKH67-hELs 標記的 Gel-hEL 配方進來，產出邊界銳利的微圖案，證明這款墨水可同時支援巨觀擠出與微觀刻畫兩種尺度的成形需求。
