# iCasp9 轉基因構築與 SFG 反轉錄病毒載體包裝

1. 引用自哪篇 paper: inducible-apoptosis-cell-therapy-safety
2. Outline (任務主線): iCasp9 轉基因構築與 SFG 反轉錄病毒載體包裝
3. Method:
      iCasp9 這顆自殺分子是兩塊人自己身上有的蛋白縫成一條。前段是 FKBP12——一顆本來會幫助折疊、能被特定小分子藥抓住的「藥物專用分子插座」。作者在關鍵位置換了一個胺基酸 (F36V mutation)：口袋裡的第 36 號從苯丙胺酸換成纈胺酸，讓腔隙變大剛好對應合成小分子 AP1903（Clackson et al., PNAS 1998），同時對天然 FK506 幾乎不再有親和力，等於替 iCasp9 打造一把只認「工廠訂做鑰匙」的專屬鎖。後段是 caspase 9 的酵素部分，作者刻意把它上游被組裝訊號扣住的接口 (CARD domain) 整段切掉。野生型 caspase 9 平常要靠 CARD 對接「粒線體釋放 cytochrome c 才組得起來的大平台」(apoptosome)、兩顆才能被拉近活化；CARD 拿掉之後這條上游訊號整條斷開，唯一還能讓兩顆酵素貼在一起的機制，就只剩「一顆 AP1903 兩頭各扣住一顆 FKBP12」這件事。兩段之間再放一小段 Ser-Gly-Gly-Gly-Ser 5-aa linker 當彈性鉸鏈，確保兩顆酵素被拉近時有足夠角度自由度互相剪切、變成活化型並下傳到 caspase 3/7。
   作者把 iCasp9 與 ΔCD19 串在同一條 mRNA 上（雙順反子, bicistronic），中間放一段從口蹄疫病毒抄來的短序列 (FMDV 2A peptide)：核糖體翻譯到 2A 尾巴的 Gly-Pro 鍵時會「跳過一個鍵不接」(ribosomal skipping)，前段 iCasp9 從核糖體掉出來、後段 ΔCD19 繼續被翻譯，結果同一條 mRNA 就出兩個獨立、近等莫耳的蛋白共存於同一顆細胞內。ΔCD19 這一段是把完整 CD19 的細胞質尾端整段砍掉——完整 CD19 是 B 細胞的訊號傳遞蛋白，作者只想借它的胞外段當表面標籤（供下游 CliniMACS 磁選與流式 FACS 抓 CD3⁺CD19⁺），不想多長一條不該有的訊號通道。這個等莫耳共表現是後續「用 ΔCD19 當 iCasp9 的替身指標」的分子基礎；若 2A 跳鍵效率不夠、ΔCD19 表現遠高於 iCasp9，磁選會混進一批「有 CD19 標籤但 iCasp9 蛋白量不足」的假陽性 T 細胞，AP1903 觸發時清不掉，這正是選 FMDV-2A（跳鍵效率相對高）並要求磁選純度 90–93% 的理由。
   整段 iCasp9-2A-ΔCD19 被裝進 SFG 反轉錄病毒載體（Moloney 鼠白血病病毒衍生），完整轉基因命名為 SFG.iCasp9.2A.ΔCD19，兩端夾帶 LTR (long terminal repeat)——這段重複序列既是病毒基因體的邊界，也是把整段基因永久釘進 T 細胞染色體的整合把手。作者選 SFG 而不是慢病毒或質體轉染，因為 Moloney MLV 骨架只能感染正在分裂的細胞，配合上游 OKT3 + IL-2 活化拿到的高轉導效率剛好對得上；一旦整合，T 細胞往後每次分裂都會把整套 iCasp9-2A-ΔCD19 一起複製下去。SFG 骨架在 Bonini 1997 Science 的 HSV-TK 試驗就有臨床安全紀錄，是這類 haploidentical 情境下最成熟、也最容易 GMP 放大的選擇。
4. 工具與材料:
   - **FKBP12 (F36V)**: 人源的藥物專用分子插座；F36V 突變把 36 號胺基酸從 F 換成 V 讓口袋腔隙變大，只認合成藥 AP1903，不理天然 FK506。
   - **Ser-Gly-Gly-Gly-Ser linker**: 一段 5 個胺基酸的彈性鉸鏈，讓 FKBP12 與 caspase 9 兩段之間有角度自由度。
   - **CARD-truncated caspase 9**: 去除 CARD domain 的人源 caspase 9 酵素段；斷掉 apoptosome 上游訊號，只剩「兩顆貼在一起」這條啟動路徑。
   - **FMDV 2A peptide**: 從口蹄疫病毒抄來的短序列，讓核糖體翻譯到 Gly-Pro 鍵時跳過一個鍵不接，一條 mRNA 因此翻譯出兩個獨立蛋白。
   - **ΔCD19**: 把完整 CD19 的細胞質尾端砍掉的截短型 CD19，保留胞外段供磁選/流式抓，不會傳訊號。
   - **SFG retroviral vector**: Moloney 鼠白血病病毒衍生的 gammaretroviral 載體，能把整段轉基因永久整合進分裂中 T 細胞的染色體。
   - **LTR**: 病毒基因體兩端的長重複片段，兼作邊界與染色體整合把手。
   - **SFG.iCasp9.2A.ΔCD19**: 完整轉基因命名，串接 iCasp9-FMDV2A-ΔCD19 於 SFG 骨架內。
5. 與此篇文章的關係:
   在《Inducible Apoptosis as a Safety Switch for Adoptive Cell Therapy》這篇文章中，作者為了讓一顆 T 細胞既能被 AP1903 觸發自殺、又能被磁選純化與流式追蹤，把 iCasp9 與 ΔCD19 綁在同一段 mRNA、透過 FMDV 2A ribosomal skip 近等莫耳共表現，並裝進臨床成熟的 SFG 反轉錄病毒骨架。它解決了「iCasp9 在細胞內、沒法直接染色」的追蹤瓶頸，讓一個標記同時當磁選鑰匙與 in vivo 替身指標，直接餵給下游的 T 細胞活化、轉導與 CliniMACS 純化步驟。
