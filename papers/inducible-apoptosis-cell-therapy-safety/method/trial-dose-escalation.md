# 臨床試驗設計與 T 細胞回輸（劑量遞增）

1. 引用自哪篇 paper: inducible-apoptosis-cell-therapy-safety
2. Outline (任務主線): 臨床試驗設計與 T 細胞回輸（劑量遞增）
3. Method:
      作者挑的病人有兩個共同背景：白血病復發、接受了 CD34⁺ 選殖的 haploidentical 造血幹細胞移植 (haploidentical HSCT)。haploidentical 意思是捐贈者與病人 HLA 只對到一半，這種移植 GVHD 風險最高；臨床上先做 CD34⁺ 選殖——只把捐贈者的造血幹細胞挑出來、把成熟 T 細胞剃掉再輸給病人——目的是壓 GVHD，代價是免疫重建拖很長、抗病毒與抗白血病能力薄弱。作者選這個情境有兩個理由：一是這類病人「最需要」補充供者 T 細胞防病毒感染與白血病復發，二是 HLA 錯配大，一旦補充的 T 細胞裡殘留任何 alloreactivity，就是最敏感的 GVHD 測試場，能檢驗 iCasp9 開關真的能在人身上被觸發。回輸時機定在 HSCT 後 30–90 天：這時嗜中性球植入 (neutrophil engraftment) 已完成、沒有嚴重器官毒性或感染，供者 T 細胞回輸的效益還來得及；太早骨髓還沒長回嗜中性球、任何併發症可能致命，太晚免疫已部分重建、供者 T 的必要性下降。試驗於 ClinicalTrials.gov 註冊編號 NCT00710892，由 U54HL08100 (NHLBI) 與 P01CA094237 (NCI) 資助，輸注地點為 Center for Cell and Gene Therapy at the Methodist Hospital 或 Texas Children's Hospital。
   傳統 3+3 一級要用 3 人、看到毒性才擴展 3 人才決定升降級，樣本用量大、對兒科罕見病太奢侈。作者用的是 Piantadosi 改良過的連續再評估法 (modified CRM, ref 22, Cancer Chemother Pharmacol 1998)——三個劑量水準 1×10⁶、3×10⁶、1×10⁷ T cells/kg 每級只需 2 名受試者：每收一名後用貝氏公式更新一條 logistic dose–response 曲線的兩個參數（斜率與位置），若這位在低劑量就出現劑量限制毒性 (DLT)，曲線往左移、毒性估計更嚴；若在高劑量沒出 DLT，曲線往右移。更新後的曲線中位數估計出 MTD，決定下一位打哪個劑量。半個 log（~3 倍）的劑量間距是臨床能真的區分「有效 vs. 顯毒」的可辨解析度——再細會被人與人間的變異淹沒。
   受試者之間強制間隔 >42 天，這是 GVHD 事件的觀察窗——GVHD 通常在輸注後幾天到 4-6 週內出現，若太快收下一位，上一位還沒發完 GVHD 資料就先決策，CRM 模型會用不完整資料算後驗，可能把下一位放進實際上不安全的劑量。若同時取消 30–90 天的 HSCT 後回輸窗（例如 HSCT <30 天就回輸），會撞到嗜中性球植入期——這時病人白血球極度不全，任何 GVHD 引起的皮膚破損或腸黏膜損傷都可能引發致命感染，連 iCasp9 rescue 也救不了已經敗血症的孩子。42 天間隔與 30–90 天窗口是這套 5 人劑量遞增試驗「不能省」的安全欄杆。
4. 工具與材料:
   - **CD34⁺ selection**: 只把捐贈者的造血幹細胞挑出來、剃掉成熟 T 細胞的正選純化，是 haploidentical HSCT 抑制原生 GVHD 的前置步驟。
   - **neutrophil engraftment**: HSCT 後嗜中性球長回可測水平的指標，用來判斷免疫系統已初步重建、可以承受下一步 T 細胞回輸。
   - **modified CRM (Piantadosi)**: 貝氏連續再評估法；每收一名受試者就更新 logistic dose-response 曲線後驗，用最少樣本逼近 MTD。ref 22 Piantadosi 1998。
   - **劑量水準 1×10⁶ / 3×10⁶ / 1×10⁷ T cells/kg**: 三個 T 細胞回輸劑量，以半個 log 為間距覆蓋文獻中 haploidentical 有效劑量窗。
   - **NCT00710892**: 本試驗於 ClinicalTrials.gov 註冊編號。
   - **staggered enrollment >42 days**: 兩位受試者之間強制間隔，以確保上位的 GVHD 事件被納入下一位的劑量決策。
   - **HSCT 後 30–90 天窗口**: T 細胞回輸的臨床時機；平衡「嗜中性球植入完成」與「供者 T 細胞仍有效益」。
5. 與此篇文章的關係:
   在《Inducible Apoptosis as a Safety Switch for Adoptive Cell Therapy》這篇文章中，作者為了在 5 名 3–17 歲兒童身上找出 iCasp9-T 細胞能夠 in vivo 擴增並誘發 GVHD 的可耐受劑量，把 Piantadosi modified CRM 貝氏設計與 haploidentical HSCT + CD34⁺ 選殖後的臨床時間窗結合成整個試驗骨架。它解決了兒科罕見病樣本量嚴格受限、無法用傳統 3+3 撐起劑量遞增的瓶頸，把每位孩子的資訊密度榨到最高，直接餵給下游 AP1903 觸發驗證與 rescue kinetics 量化。
