# 自體 T 細胞收集、離體活化與慢病毒轉導

1. 引用自哪篇 paper: car-t-chronic-lymphoid-leukemia
2. Outline (任務主線): 自體 T 細胞收集、離體活化與慢病毒轉導
3. Method:
      整條產線的起點，是 2009 年 12 月做的一次白血球分離術 (leukapheresis)：病人靜脈接上離心分離機，血液邊抽邊分層，機器只留下白血球那一層、紅血球與血漿即時回輸；一次就可以拿到幾十億顆自體淋巴球，全部冷凍保存等待用。臨床方案啟動時，Clinical Cell and Vaccine Production Facility (CVPF) 在 GMP 條件下把細胞解凍，接著用 CD3/CD28 共刺激珠子活化擴增——兩種抗體 anti-CD3 與 anti-CD28 綁在同一顆磁珠上，一顆珠子等於一台可攜式抗原呈現細胞 (APC)，同時對 T 細胞按下扳機 (訊號 1) 與加油門 (訊號 2)。這兩顆按鈕必須一起按：T 細胞若只收到 CD3 訊號、沒有 CD28 共刺激，會進入「無反應化」(anergy)、不再增殖 (protocol 沿用 Porter et al. 2006 Blood)。T 細胞進入分裂期後，才加入 pELPs 19-BB-z 慢病毒液共培養——順序倒過來就白搭，因為靜止期 T 細胞對慢病毒感染效率極差，非得進入分裂期病毒才能有效把 CAR 基因整合進染色體。
   最終產品裡約 5% 的 T 細胞掛上 CAR，總共 3×10⁸ 顆 T 細胞中有 1.42×10⁷ 顆是 CART19。轉導率停在 5% 而不強行拉高，是刻意的權衡：慢病毒每顆整合份數由「病毒對細胞比例」(MOI) 決定，MOI 拉高會讓一顆 T 細胞染色體帶好幾份 CAR，插入性致癌風險升高、體內動力學也難以預測。5% 已足夠讓回輸的 CART19 在體內找到 CD19 並啟動擴增，除非壓到 <1% 才會出現細胞數量不足的疑慮。
4. 工具與材料:
   - **leukapheresis**: 白血球分離術，用離心分離機從病人血液中專取白血球那一層、其餘即時回輸。
   - **cryopreservation**: 液氮冷凍保存細胞，等待臨床方案啟動時再解凍。
   - **GMP / CVPF**: 臨床級細胞生產規範與大學設施 (Clinical Cell and Vaccine Production Facility)，負責 ex vivo 慢病毒轉導。
   - **CD3/CD28 共刺激珠子**: anti-CD3 與 anti-CD28 抗體綁同一顆磁珠，等於可攜式 APC 同時給訊號 1+2 讓 T 細胞增殖。
   - **ex vivo activation**: 把 T 細胞從休眠狀態衝進分裂期，才能被慢病毒有效整合。
   - **lentiviral transduction**: 慢病毒把 CAR 設計圖永久釘進 T 細胞染色體的過程。
   - **transduction efficiency (~5%)**: 本次臨床產品中約 5% 的 T 細胞成功表達 CAR，是安全與擴增能力的權衡。
5. 與此篇文章的關係:
   在《Chimeric Antigen Receptor–Modified T Cells in Chronic Lymphoid Leukemia》這篇文章中，作者為了得到能在病人體內擴增的自體 CAR-T 產品，採用了 leukapheresis 收集 T 細胞、CD3/CD28 珠子活化擴增、pELPs 19-BB-z 慢病毒轉導這條 GMP 產線。它解決了「T 細胞怎麼從病人身上拿出來、又長回幾十億顆、又同時掛上 CAR」的臨床瓶頸。這條產線接收 §A 的載體與病人 leukapheresis 產物，產出下游 §C 化療後可直接回輸的 CART19 細胞袋。
