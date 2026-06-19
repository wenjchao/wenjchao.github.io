# 病人特異 iPSC 重編程 (Sendai virus 自 PBMC)

1. 引用自哪篇 paper: engineered-cardiac-tissue-rcm
2. Outline (任務主線): 病人特異 iPSC 重編程 (Sendai virus 自 PBMC)
3. Method: 

作者從病童手臂抽一管血，取出白血球層的週邊血單核細胞 (PBMC) 共 2 × 10⁶ 個。剛抽出來的 PBMC 是一鍋很雜的細胞，能成功重編程的只有少數造血前體，所以先在無血清造血培養基裡擴增 9–12 天，讓紅血球前體 (erythroblast) 這群「年輕、好接收新指令」的細胞長到夠多。接著用 Cytotune iPS 2.0 Sendai Reprogramming Kit (Life Technologies) 同時把 Oct4 / Sox2 / KLF4 / c-Myc 四個重編程因子塞進去。Sendai virus 是一種只在細胞質裡複製、不進細胞核、不會把基因黏進染色體的 RNA 病毒——它把四因子當成 mRNA「短期廣播」，等細胞回到 iPSC 狀態後，病毒會隨細胞分裂被稀釋掉、自然消失，比起會永久插入染色體的 lentivirus 不留下人為痕跡。感染一週後移到 MEF feeder 上養 25–30 天，再從盤裡挑出長得像 iPSC 純系的細胞團——細胞核佔比大、核仁明顯——這就是後續一切實驗的種子細胞。

為什麼這四個因子塞進去就能把血球變回幹細胞？Oct4 / Sox2 / KLF4 / c-Myc 是控制「胚胎幹細胞身分」最上游的四個總開關轉錄因子（Yamanaka factors），一旦同時打開，會把細胞染色質重新洗牌、關掉血球身分基因、打開幹細胞身分基因。後培養為什麼要在 MEF feeder 上、配 20% Knock-Out Serum Replacement (KO-SR) + 4 ng/mL 鹼性纖維母細胞生長因子 (bFGF)？因為剛重編程出來的 iPSC 純系很脆弱，MEF feeder 是事先輻射過、不會再分裂但仍會分泌生長因子的胚胎纖維母細胞，等於墊一層奶媽細胞幫新生 iPSC 撐場面；KO-SR 取代血清避免批次差異，bFGF 維持多能性訊號。等純系穩定下來，後續才會搬到無 feeder 的系統繼續養。

重編程是隨機事件，挑出來的 colony 不一定真的是乾淨的 iPSC，所以要走完四道品管。流式偵測 Oct4 / Nanog（細胞內多能性標記）和 Tra-1-60 / SSEA4（細胞表面多能性標記），確認重編程已經完整、不是「半成品還留著血球痕跡」。G-band 核型分析在顯微鏡下檢查 ≥20 個分裂中期細胞的 450–500 條染色體帶，排除染色體斷裂或缺失——不然疾病表型會跟 FLNC 突變本身混雜分不清。三胚層分化測試 (Pluripotent Stem Cell Functional ID kit, R&D Systems) 確認這株 iPSC 真的能分化成三大類胚層，不然到後面才發現分化不出心肌就太晚了。最後用 e-Myco plus PCR kit (Bulldog Bio) 排查 mycoplasma 黴漿菌污染——這種無細胞壁細菌污染了培養基也看不出來，但會偷偷改變細胞代謝與基因表現，可能把疾病表型整段污染掉。

4. 工具與材料: 
- **PBMC**: 週邊血單核細胞，是抽血後白血球層的細胞群，本研究 2 × 10⁶ 個作為重編程起始材料。
- **erythroblast**: 紅血球前體細胞，在無血清造血培養基中擴增 9–12 天以提高重編程效率。
- **Sendai virus**: 只在細胞質裡複製、不進細胞核、不整合宿主基因組的 RNA 病毒，作為非整合性重編程載體。
- **Cytotune iPS 2.0 Sendai Reprogramming Kit**: Life Technologies 套組，含 Oct4 / Sox2 / KLF4 / c-Myc 四個重組 Sendai 病毒載體。
- **Yamanaka factors (OSKM)**: Oct4 / Sox2 / KLF4 / c-Myc 四個總開關轉錄因子，一起打開能把成熟細胞倒帶回多能狀態。
- **MEF feeder**: 事先輻射、不再分裂但仍會分泌生長因子的胚胎纖維母細胞層，幫新生 iPSC 純系撐場面。
- **KO-SR**: Knock-Out Serum Replacement，取代血清避免批次差異的 20% 培養基添加物。
- **bFGF**: 鹼性纖維母細胞生長因子，4 ng/mL 維持 iPSC 多能性訊號。
- **Tra-1-60 / SSEA4**: iPSC 表面多能性標記，與細胞內 Oct4 / Nanog 一起用流式驗證重編程完整。
- **G-band 核型分析**: 在顯微鏡下檢查 ≥20 個分裂中期細胞、看 450–500 條染色體帶有無斷裂或缺失。
- **Pluripotent Stem Cell Functional ID kit**: R&D Systems 套組，確認 iPSC 真的能分化成三大類胚層。
- **e-Myco plus PCR kit**: Bulldog Bio 套組，PCR 偵測無細胞壁的 mycoplasma 黴漿菌污染。

5. 與此篇文章的關係: 
在《Engineered cardiac tissue model of restrictive cardiomyopathy for drug discovery》這篇文章中，作者為了把一名帶 FLNC c.7416_7418delGAA 突變的三歲 RCM 病童做成可重複實驗的活體模型，採用了 Sendai virus 從病童 PBMC 重編程出 iPSC 的非整合性流程。它解決了「病人組織只能取一次、數量極有限」與「lentivirus 重編程會在染色體留下人為痕跡」這兩個瓶頸，產出一株可長期培養、可分化的患者特異 iPSC，作為後續 CRISPR 校正、心肌分化、ECT 製作、藥物篩選整條管線的起點細胞。
