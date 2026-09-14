# 淋巴球耗竭化療 (Lymphodepleting Chemotherapy)

1. 引用自哪篇 paper: car-t-chronic-lymphoid-leukemia
2. Outline (任務主線): 淋巴球耗竭化療 (Lymphodepleting Chemotherapy)
3. Method:
      作者用的這輪化療目的不是殺癌，而是先把病人自己的淋巴球數量壓下去、把免疫系統的舞台空出來，讓等下要回輸的 CART19 有空位擴增。配方沿用 Lamanna 2006 J Clin Oncol 的 PCR (pentostatin/cyclophosphamide/rituximab) regimen，但因為病人先前對 rituximab 有嚴重過敏，作者直接拿掉 rituximab 只留下前兩味藥——反正 CART19 本身就會清掉 B 細胞，並不會失手。劑量是 pentostatin 4 mg/m² 體表面積一劑加 cyclophosphamide 600 mg/m² 一劑，於回輸前 4 天給藥。時序上 4 天剛好能等淋巴球被壓到最低、化療藥物本身的細胞毒性峰值也退掉，避免順便毒到剛打進去的 CART19；中間第 3 天還做了一次骨髓 biopsy，把 CLL 佔骨髓約 40%、TP53 缺失比例等基線量到。pentostatin 是一種嘌呤類似物，會卡住淋巴球內一個叫 adenosine deaminase (ADA) 的酵素——ADA 失效後 dATP 在細胞裡累積過量把淋巴球毒死，其他細胞影響小得多，等於「選擇性毒殺淋巴球」。cyclophosphamide 則是一種烷化劑，會在 DNA 兩股間拉出強力交叉鏈結，對正在增殖的淋巴球特別致命。分子層面上，體內原本的 T、B 細胞平時每天都在吃 IL-7、IL-15 這兩支支持性細胞因子，把它們維持在低濃度；化療把大部分淋巴球清掉後，這兩支 cytokine 沒人搶、血中濃度飆升，剛回輸進去的 CART19 一進來就吃到滿滿的支持訊號，擴增速度大幅加快，同時 Treg 被壓、APC 上的共刺激分子上升，都對新進 T 細胞有利。
   為什麼挑這種溫和化療、而不是清髓化療加異體骨髓移植？帶 TP53 缺失的 CLL 過去唯一能長期壓下癌症的辦法是把別人的骨髓整組換進來，但別人的免疫系統會反過來攻擊病人 (GvHD)，對年長 CLL 病人風險過高。作者的替代路線是只用溫和淋巴球耗竭清出空間、把殺癌工作交給病人自己 T 細胞改造的 CART19——既避開 GvHD、又保留骨髓不動。若走另外兩端各自會壞：跳過整輪淋巴球耗竭直接回輸 CART19，病人自己的淋巴球會繼續把 IL-7/IL-15 吃光、Treg 繼續壓 T 細胞、免疫系統還可能認出 murine scFv 把 CART19 清掉，1.46×10⁵ / kg 這種低劑量幾乎必然消失無蹤；反過來走清髓化療，等於把 APC 與骨髓間質細胞也一起殺掉，把 CART19 擴增賴以維生的支持環境也拆掉，同時老年病人治療相關死亡率飆升。溫和的 PCR-minus-R 是這條光譜上的甜蜜點。
4. 工具與材料:
   - **Pentostatin**: 嘌呤類似物、選擇性 adenosine deaminase (ADA) 抑制劑；造成淋巴球內 dATP 累積致死，本案用 4 mg/m² 一劑。
   - **Cyclophosphamide**: 烷化劑；DNA 交叉鏈結對增殖中淋巴球特別致命，本案用 600 mg/m² 一劑。
   - **PCR-minus-R regimen**: Lamanna 2006 J Clin Oncol PCR (pentostatin/cyclophosphamide/rituximab) 三合一化療拿掉 rituximab 的版本，因病人 rituximab 過敏而略去。
   - **Lymphodepletion**: 把宿主淋巴球數量壓下去為 CART19 騰出 niche，並讓血中 IL-7、IL-15 濃度飆升以支持擴增。
   - **Homeostatic cytokines (IL-7, IL-15)**: 平時被大量 T 細胞消耗、維持 T 細胞低度存活與分裂的支持因子；淋巴球被清空後濃度飆升，成為 CART19 的擴增燃料。
5. 與此篇文章的關係:
   在《Chimeric Antigen Receptor–Modified T Cells in Chronic Lymphoid Leukemia》這篇文章中，作者為了讓 1.46×10⁵ / kg 這種低於前人數個數量級的極低劑量 CART19 也能在體內擴增，採用了 pentostatin + cyclophosphamide 化療 (即 PCR regimen 拿掉 rituximab)。這個方法解決了自體 CART19 進到未經處理的 host 環境時被 IL-7/IL-15 競爭、Treg 抑制、murine scFv 免疫排斥的瓶頸，把宿主淋巴球區室清空，交給下一步的分次靜脈回輸做為擴增地基。
