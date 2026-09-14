# 第二代 anti-CD19 CAR 慢病毒載體 (pELPs 19-BB-z) 建構

1. 引用自哪篇 paper: car-t-chronic-lymphoid-leukemia
2. Outline (任務主線): 第二代 anti-CD19 CAR 慢病毒載體 (pELPs 19-BB-z) 建構
3. Method:
      作者要設計一支能給人用的「複合式對講機」——把辨識 CD19 的抗體、開火按鈕、持續作戰按鈕全部裝在 T 細胞的膜外與膜內。運送這台對講機圖紙的是慢病毒 (lentivirus)，只是它兩端原本的長重複片段 (LTR) 自帶啟動子會亂吵醒附近基因，作者把 3' LTR 的啟動子區整段拆掉，讓病毒「送貨完就自己關機」，即自失活載體 (self-inactivating, SIN)；正式編號為 GeMCRIS 0607-793。病毒外套也不用原本 HIV 的殼，而是換成水泡口炎病毒外套 (VSV-G) 把它包起來 (pseudotyped)——VSV-G 認的是幾乎所有細胞都有的受體，能感染 T 細胞範圍廣、離心也不會碎，方便臨床規模生產。載體要表達的 CAR19 本身是一條由四段功能組成的融合蛋白：最外側是從小鼠 FMC63 抗體剪下來的單鏈變異片段 (single-chain variable fragment, scFv)——一個能像原抗體一樣抓住 CD19 的辨識夾；中間接上 T 細胞常用的 CD8α hinge 與跨膜段 (transmembrane)，讓 scFv 像天線一樣立在膜外、有彈性搆到抗原，同時把整條 CAR 錨在膜上；胞內側則把 4-1BB (CD137) 的訊號域串在 CD3ζ 前面，讓一顆 CAR 同時內建開火扳機 (CD3ζ) 與「不要停」按鈕 (4-1BB)——CD3ζ 提供訊號一，4-1BB 透過 TRAF 打開 NF-κB 與抗凋亡路徑補上訊號二。這四段全寫在同一條連續讀框 (open reading frame, ORF) 裡，翻譯出來就是一條完整融合蛋白，一路折疊送上膜；啟動子挑 EF-1α 而不是 CMV，因為活化中的人類 T 細胞會把 CMV 關掉 (silencing)，EF-1α 屬於管家基因啟動子，能持續表達。
   為什麼挑 4-1BB 而不是同期被試過的 CD28？兩者都能提供訊號二，但驅動的 T 細胞後果差很多：CD28 傾向把 T 細胞推成短命執行者，一波殺敵後就耗盡；4-1BB 則透過 NF-κB 與抗凋亡路徑讓細胞轉往記憶型，殺敵後仍能長期存留。作者自己的動物實驗 (Milone 2009 Mol Ther；Carpenito 2009 PNAS) 就是拿兩者對比、看到 4-1BB CAR 持續期顯著較長；同時期 Brentjens 團隊用 CD28-CAR 治 CLL，改造 T 細胞很快就從循環中消失，正好成為本篇的反例。這支載體因為要進病人身上，還必須登錄美國 NIH 的人體基因治療監管識別碼 (GeMCRIS 0607-793)、通過 preclinical safety testing (包括驗證不會拼回可複製病毒、不偏好插進致癌基因等)，並委由 Lentigen 公司做臨床級生產。若跳過 SIN 或跳過 4-1BB 各自會壞掉什麼？沒有 SIN，LTR 啟動子會亂吵醒插入位置附近的基因——過去 X-SCID γ-retrovirus 試驗就因為載體剛好插進 LMO2 致癌基因旁邊，讓病人得到 T 細胞白血病；沒有 4-1BB、回到只剩 CD3ζ 的第一代 CAR，T 細胞只被扣訊號一、沒有訊號二支撐，很快進入耗竭或自殺，輸進病人幾天內就從血液中消失、幾乎不擴增。
4. 工具與材料:
   - **self-inactivating (SIN) lentiviral vector**: 拆掉 3' LTR 啟動子區的慢病毒載體，整合後兩端 LTR 都變啞巴，避免亂吵醒鄰近基因。
   - **VSV-G pseudotype**: 以水泡口炎病毒 G 外套取代原 HIV envelope，能感染的細胞範圍變廣，且離心耐操便於量產。
   - **FMC63 scFv**: 從小鼠單株抗體 FMC63 剪出 VH+VL 用 linker 串成的單鏈變異片段，能像原抗體一樣抓住 CD19。
   - **CD8α hinge / transmembrane**: T 細胞 CD8α 蛋白的兩段結構，hinge 提供彈性讓 scFv 立在膜外、TM 把 CAR 錨在膜上並輔助二聚化。
   - **CD3ζ 訊號域**: CAR 的『訊號一』開火扳機；帶 ITAM 序列，被磷酸化後啟動下游 T 細胞活化訊號。
   - **4-1BB (CD137) 共刺激域**: CAR 的『訊號二』持續作戰按鈕；透過 TRAF 招募 NF-κB 與抗凋亡路徑，讓 T 細胞轉往記憶型並長期存留。
   - **EF-1α promoter**: 管家基因啟動子，取代易被 T 細胞 silencing 的 CMV，讓 CAR 表現量在活化狀態下仍穩定。
   - **GeMCRIS 0607-793**: 美國 NIH 對人體基因治療載體的監管識別碼，此載體已完成 preclinical safety testing。
5. 與此篇文章的關係:
   在《Chimeric Antigen Receptor–Modified T Cells in Chronic Lymphoid Leukemia》這篇文章中，作者為了在 TP53 缺失、化療無效的 CLL 病人身上重新啟動免疫殺癌路徑，設計了自失活型 pELPs 19-BB-z 慢病毒載體。這支載體解決了第一代 CAR 只有 CD3ζ 導致 T 細胞在體內無法擴增與存留的瓶頸，把 anti-CD19 scFv 與 4-1BB + CD3ζ 雙訊號寫進單一 ORF，做出可直接感染自體 T 細胞的臨床級病毒，供下游 ex vivo 轉導製造 CART19 產品。
