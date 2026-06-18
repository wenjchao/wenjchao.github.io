# 擠出式 3D Bioprinting

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): 擠出式 3D Bioprinting
3. Method: 
   擠出式 3D bioprinting 就像在做「會永久定型的果凍擠花」。作者先把墨水配方準備好：7.5% GelMA + 5% gelatin + 0.5% 光起始劑 (photoinitiator, PI)，三者在 80 °C 攪 30 分鐘徹底溶解，降到 37 °C × 60 分鐘讓溫度回到細胞能活的範圍再加入 CF 跟 NV，最後送進 4 °C 冰箱 10 分鐘讓墨水部分固化 (partially solidified) 變成像甜筒霜淇淋一樣半流半固的稠度。印表機 (SunP ALPHA-CPD1) 按照預寫的路徑指令 (G-code) 控制 27 號針頭移動，用氣壓把墨水擠出來——27-gauge 內徑約 200 µm，是「線條夠細＋細胞通過時的剪力還不會大量殺死它們」的折衷點。為了防止針頭內墨水被環境紫外光提前啟動 crosslink 堵住，整支噴頭包鋁箔擋光，只在最後一步擠完後取下。墨水裡那 5% 純 gelatin 是「犧牲性配角」——它跟 GelMA 在 4 °C 一起糾纏成更稠的物理凝膠，幫助列印當下維持線條粗細跟堆疊不塌，但因為它沒被甲基丙烯化、不會被 UV 抓住共價交聯，列印完升回 37 °C 它就會融化、隨水洗掉，最終結構裡只剩下 GelMA 共價網。這比常見的 alginate 或 pluronic 犧牲材料更乾淨，因為純 gelatin 是水溶性、不需要額外解膠處理。

   為什麼擠完還要照紫外光？因為 4 °C 凝的只是「物理凝膠」——GelMA 鏈上殘留的明膠序列在低溫下會自發捲成三股螺旋 (triple helix) 互相糾纏，形成可逆的果凍狀網，撐得住擠花當下的形狀，但升回 37 °C 就會融化。作者把擠好的結構放到 800 mW 的 UV 光源底下、距樣本 8 cm、照 20 秒，讓光起始劑 Irgacure D-2959 被 UV 打成自由基，攻擊 GelMA 鏈上掛著的甲基丙烯酸 (methacrylate) 雙鍵，誘發鏈式自由基聚合把不同鏈共價縫在一起，形成不可逆的 3D 網。物理網管「擠的時候不塌」、共價網管「之後不化」，兩張網接力。如果跳過 4 °C 部分固化、直接從 37 °C 擠出墨水，墨水會像水彩一樣攤平、線條散開、堆疊塌陷，即使最後照 UV 也只是把塌掉的形狀「永久定型」下來，列印失去意義。UV 時間另一頭的陷阱是「照太久」：自由基會直接攻擊細胞 DNA 跟膜脂，過度交聯也會讓網眼太細、營養跟廢物進出受阻。作者把 UV 時間壓在 20 秒、距離 8 cm，是「剛好讓 GelMA 撐住結構＋細胞還能活」的折衷，實測 3 天後細胞活性約 80%。
4. 工具與材料: 
   - **Extrusion bioprinting**: 用氣壓把含細胞墨水從 27 號針頭擠出來、按 G-code 路徑堆出 3D 結構。
   - **Bioink (7.5% GelMA + 5% gelatin + 0.5% PI)**: 本研究的細胞墨水配方，加 CFs 跟 NVs；5% gelatin 為犧牲性流變調節劑。
   - **Sacrificial gelatin (5%)**: 純明膠沒有甲基丙烯化、不參與 UV crosslink，列印完升溫即融化洗去，幫助列印當下提升 printability。
   - **Partially solidified bioink (4 °C × 10 min)**: 把墨水冷藏到半流半固狀態，形成 triple-helix 物理凝膠撐住擠出形狀。
   - **Triple-helix physical gel**: 明膠序列在低溫下捲成三股螺旋互相糾纏的可逆凝膠，是 4 °C 部分固化的分子機制。
   - **Photoinitiator (Irgacure D-2959, 0.5%)**: 被 UV 打成自由基的化學起爆劑，引發 GelMA 上的甲基丙烯酸鏈式聚合。
   - **UV crosslink (Omnicure S2000, 800 mW, 8 cm, 20 s)**: 用紫外光啟動自由基聚合把 GelMA 共價交聯成不可逆 3D 網，「永久定型」結構。
   - **27-gauge needle**: 內徑約 200 µm，兼顧線條解析度與細胞通過時的剪力傷害。
   - **G-code**: 印表機讀的路徑指令，定義針頭的移動軌跡。
   - **SunP ALPHA-CPD1**: 本研究使用的擠出式 3D 生物列印機型號。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了把驗證過的 hELs+miRNA 系統真正做成可植入的 3D 構造，採用了擠出式 3D bioprinting，配合 4 °C 部分固化與 UV crosslink 的兩段策略。這套方法解決了 GelMA 在生理溫度下太稀、擠出就塌的瓶頸，輸入是含 CFs 跟 hELs 的 bioink，輸出是形狀保真、細胞活性約 80% 的補片、螺旋與心形結構，作為「miRNA 在 3D 構造內仍能成功遞送」這個最終結論的物理載體。
