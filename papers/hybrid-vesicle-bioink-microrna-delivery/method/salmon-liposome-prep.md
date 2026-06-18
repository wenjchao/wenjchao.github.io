# Salmon-derived Liposome 的酵素萃取與超音波製備

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): Salmon-derived Liposome 的酵素萃取與超音波製備
3. Method: 
   作者要做出後續和 EV 融合的脂質袋子原料——「鮭魚卵磷脂 (lecithin)」。為什麼是鮭魚而不是大豆？大豆卵磷脂便宜量產但脂肪酸尾巴幾乎都是飽和的，鮭魚卵磷脂天然富含 ω-3 (例如 DHA、EPA)、ω-6 多元不飽和脂肪酸 (polyunsaturated fatty acids)，這些脂肪酸對心臟與神經組織本身就有抗發炎與促修復的作用，等於 Liposome 殼本身就帶藥效。從大西洋鮭 (Salmo salar) 魚頭萃取時，作者改用「酵素萃取法 (enzymatic extraction，protocol 沿用 Linder et al. ref [38])」——丟入蛋白酶把組織消化成糊狀、磷脂自動從膜上跑進水相，避開傳統氯仿/甲醇有機溶劑萃取會破壞 ω-3 / ω-6 雙鍵的問題。

   拿到 lecithin 後到下一步之間還有兩個關鍵保護動作。第一，配 2% (w/v) 母液時要在氮氣保護 (nitrogen flow) 下操作、4 °C 避光存放——因為 ω-3 / ω-6 的多個雙鍵碰到氧氣會自己加成成過氧化物，整段脂肪酸壞掉、生物活性消失，那選鮭魚而不選大豆的理由就沒了。第二，實際做 Liposome 之前先把 lecithin 在 37 °C 培育 12 h 進行水合熟化 (hydration)，讓乾燥磷脂吸飽水、自行排成整齊的雙層結構，下一步超音波才打得開、打得均勻。如果跳過水合直接超音波，做出來的 Liposome 大小不一、還會混進多層膜套膜的囊泡 (multilamellar vesicles)，後續和 EV 融合的比例完全控不住。

   成球這一步的物理原理是：磷脂分子一頭親水、一頭怕水，在水裡會自己排成雙層。作者把熟化好的 lecithin 溶液放在冰浴裡，伸進一根 3.2 mm 細頭的超音波探針 (probe-sonication，型號 Q500 Sonicator)，以 30% 振幅 (amplitude) 採脈衝模式 (pulse mode, on 5 s / off 5 s) 敲打 4 分鐘。聲波在水裡製造瞬間崩潰的微小氣泡 (acoustic cavitation)，氣泡塌縮的剪切力把雙層膜撕成奈米級碎片；碎片邊緣裸露著怕水的脂質尾巴，能量一停就會自己「圍成一圈」捲成一顆顆中空小球——這就是 fresh Liposome (Lip)。挑這兩個參數有原因：脈衝模式留 5 秒散熱，避免連續波把樣品煮熟、讓多元不飽和脂肪酸氧化；30% 振幅是「能打出小顆單分散 Liposome、又不打斷磷脂分子」的甜蜜點。最後用 DLS 量出直徑為 52.13 ± 0.57 nm。
4. 工具與材料: 
   - **Salmon-derived lecithin**: 從大西洋鮭 (Salmo salar) 魚頭取得的卵磷脂，富含 ω-3 / ω-6 多元不飽和磷脂，作為 Liposome 的脂質原料。
   - **ω-3 / ω-6 polyunsaturated fatty acids**: 碳鏈中帶多個雙鍵的脂肪酸，對心臟與神經組織有抗發炎與促修復活性；怕氧化也怕有機溶劑。
   - **Enzymatic extraction (Linder et al. ref [38])**: 用蛋白酶消化魚頭組織把磷脂釋出進水相的萃取法，避開有機溶劑對 PUFA 的破壞。
   - **Nitrogen flow**: 配 lecithin 母液時通氮氣把瓶內氧氣趕走，防止 ω-3 / ω-6 雙鍵被氧化。
   - **Hydration (37 °C × 12 h)**: 把乾燥磷脂泡在水裡讓它吸飽水、自行排成雙層結構，是超音波成球前的必要前處理。
   - **Probe-sonication (Q500 Sonicator, 3.2 mm microtip)**: 把超音波探針伸進溶液中釋放高頻能量、把脂質雙層撕成奈米級碎片的設備。
   - **Acoustic cavitation**: 超音波在水中產生瞬間崩潰的微小氣泡，崩潰時的剪切力是撕開雙層膜的物理機制。
   - **Pulse mode (on 5 s / off 5 s)**: 超音波打 5 秒停 5 秒的脈衝模式，避免樣品過熱導致 PUFA 氧化。
   - **30% amplitude**: 超音波振幅設定；能打出 ~50 nm 單分散 Liposome 又不打斷磷脂分子的甜蜜點。
   - **Multilamellar vesicles**: 膜套膜的多層囊泡；若跳過水合熟化會出現這種大小不一的副產物，是失敗指標。
   - **fresh Liposome (Lip)**: 本步驟最終產物：直徑 52.13 ± 0.57 nm 的奈米級中空磷脂小球。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了做出能跟 GelMA 形成強鍵結、又自帶 ω-3 / ω-6 生物活性的脂質袋子，採用了「鮭魚 lecithin 酵素萃取 + probe-sonication 自組裝」這個製備流程。它解決的是「市售大豆或合成 Liposome 雖然量產容易，但只是被動容器、缺乏對心臟組織的促修復活性」這個瓶頸，產出純度足夠的 fresh Liposome (Lip)，作為下游 Module 3 與 CF-derived EVs 進行膜融合的脂質基底。
