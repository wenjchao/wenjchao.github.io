# Hybrid EV-Liposome (hELs) 的 Membrane Fusion 製備

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): Hybrid EV-Liposome (hELs) 的 Membrane Fusion 製備
3. Method: 
   作者用「先 co-incubation、再 probe-sonication」的兩段式策略製作 hELs。第一段是 37 °C × 12 h 的共同培育 (co-incubation)：等濃度的 EVs 與 Liposome 泡在一起，靠三股力量讓兩種膜慢慢貼合——結構性 (磷脂的疏水尾巴會避開水、想跟另一片膜的疏水部分湊在一起)、靜電性 (兩種囊泡表面都帶負電，但局部仍有不均勻的電荷點吸引彼此)、化學性 (EV 表面的醣鏈、蛋白與 Lip 的磷脂頭基之間形成氫鍵或瞬時離子配對)。12 h 給夠時間讓它們把接觸面「黏起來」，但還不足以真的融成一張膜。第二段超音波 (probe-sonication) 才是把「黏在一起」變成「編織在一起」的關鍵：高頻能量在水裡形成瞬間崩潰的微小氣泡 (acoustic cavitation)，氣泡塌縮的剪切力把已貼合的雙膜局部撕開；EV 與 Lip 的碎片在 5 秒 off-pulse 的安靜期內各自捲回完整囊泡時，會「順手拿到對方的拼塊」(localized reorganization, interweaving)，組成同時帶兩家成分的單一張膜——這就是 hybrid EV-Liposome (hELs)。

   Sonication 階段沿用 Module 1 做純 Liposome 時完全相同的參數：Q500 Sonicator、3.2 mm microtip、30% 振幅、脈衝模式 (on 5 s / off 5 s)、總共 4 分鐘。這個一致性是有意為之——只有「破壞膜的能量」固定，後續三種囊泡 (Lip、EVs、hELs) 的大小與多分散度才能放在同一條尺上比較。實際讀數：hELs 直徑 37.31 ± 0.65 nm、PdI ~0.25，與 EVs 的 37.45 ± 0.49 nm 幾乎一樣，但比純 Lip 的 52.13 nm 小——這個尺寸線索後續會在 DLS 分析中被解讀為「hELs 物理特性更接近 EV」。

   為了確認融合真的發生，作者掃了 Lip:EVs = 1:0、2:1、1:1、1:2 四個比例 (這些比例會丟進下游 FRET assay)。1:0 是「只有 Lip、沒加 EV」的對照組、提供 FRET 基準線；其他三組逐步增加 EV 比例。這樣可以建立「EV 加得越多、FRET 訊號掉得越多」的劑量-反應曲線，把「FRET 變化是 EV 進到 Lip 膜造成的」這個因果鏈鎖死，排除濃度漂移或染料漂白等 artifact 的可能性。

   兩段式裡的 12 h incubation 不是可選項。如果跳過直接 sonicate，EV 跟 Lip 的膜還沒貼上、彼此距離仍大；sonication 把它們各自的膜打碎後，碎片只會在自己周圍找回同類重新捲起來，最後得到的是「Lip + EV 的物理混合」而不是真的融合膜——FRET 不會看到 530 nm 訊號升高、Lip 上也不會出現 CD9/CD63/CD81 標誌。整個雜化策略就會失敗。
4. 工具與材料: 
   - **Co-incubation (37 °C × 12 h)**: 兩段式融合的第一段，讓 EVs 與 Lip 在熱運動下慢慢靠近、靠結構/靜電/化學交互作用貼合。
   - **Structural / electrostatic / chemical interactions**: 驅動 incubation 階段膜貼合的三股力量：疏水尾巴互湊、表面局部電荷吸引、頭基之間氫鍵/離子配對。
   - **Probe-sonication-induced membrane breakage**: 兩段式的第二段；用 acoustic cavitation 的剪切力把已貼合的雙膜局部撕開。
   - **Localized reorganization / interweaving**: Sonication off-pulse 期間，EV 與 Lip 的碎片在同一微區重新捲合、互換成分，形成單一張混合膜。
   - **Membrane fusion protocol (refs [21–23])**: 本研究的 EV-Lip 融合流程整合自 Sato 2016、Piffoux 2018、Lin 2018 等 exosome-liposome hybrid 文獻。
   - **Lip:EVs ratio scan (1:0, 2:1, 1:1, 1:2)**: 用比例梯度建立 EV-劑量 vs FRET-反應曲線，鎖死『FRET 變化來自 EV 融入』這個因果鏈。
   - **Hybrid EV-Liposome (hELs)**: 本步驟最終產物：直徑 37.31 ± 0.65 nm，PdI ~0.25，膜上同時帶 Lip 磷脂與 EV 標誌的混血奈米囊泡。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者的目標是把「EV 會挑細胞、但跟 GelMA 黏不牢」與「Lip 跟 GelMA 黏得牢、但不會挑細胞」兩種互補性質縫到同一顆奈米囊泡上。為此採用了「co-incubation + probe-sonication」兩段式膜融合 (整合自 Sato 2016、Piffoux 2018、Lin 2018 等 ref [21–23])，解決了「兩種預先做好的脂質囊泡直接混合只會物理疊加、不會真正交換膜成分」的瓶頸，產出膜上同時帶兩家成分的 hELs，作為下游 FRET、FACS、miRNA 裝載與 GelMA 嵌入的核心材料。
