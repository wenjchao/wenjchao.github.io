# 化合物急性處置與 RCM 表型救援

1. 引用自哪篇 paper: engineered-cardiac-tissue-rcm
2. Outline (任務主線): 化合物急性處置與 RCM 表型救援
3. Method: 

養滿 4 週、表型已經穩定的病人版小肉條，作者直接在培養液裡加入終濃度 10 µM 的 trequinsin-HCl (Tocris #23371)，靜置 1–3 小時讓藥物滲進組織。給藥前先拍一次柱頭位移影片、給藥後再拍一次，同一條組織就充當自己的對照 (repeated-measures)。從位移影片用前一節的 displacement→force 標定曲線換算，分別讀出主動拉力 (active force)、最放鬆時殘留的拖力 (passive tension)、放鬆速度，以及「鬆到一半要花多久」(time to 50% relaxation)。除了 trequinsin，作者把篩選交集前段的另外兩個備選 hit——17α-hydroxyprogesterone (Sigma H-085-1ML) 與 denbuphylline (Santa Cruz sc-203915，非選擇性 PDE3/4 抑制劑)——也放上同一條救援流程跑一次，從另一個機制角度檢驗「抑制 PDE3 救援 RCM」的因果鏈。

為什麼擋住 PDE3 就能讓心肌鬆得開？心肌每跳一下都靠細胞內鈣離子先飆高再被收回儲存槽，收回的快慢直接決定鬆得開不開。細胞裡有一個叫 cAMP 的訊號傳遞分子，一升高就會啟動下游激酶 PKA，PKA 再把鈣回收幫浦 (SERCA)、肌絲鈣感受器 (troponin I) 等開關通通磷酸化打開，鈣回收變快、肌肉鬆得快。但細胞同時養著一群叫 PDE3 (phosphodiesterase 3) 的清道夫酵素，平常忙著把 cAMP 拆掉維持 baseline。trequinsin 就是專門擋住 PDE3 的小分子——PDE3 被綁住、cAMP 拆不掉就會堆積，下游 PKA 一路打開，把 RCM 細胞「鈣回收太慢」的源頭問題拉回正常。

致心律不整測試要回答兩件事：trequinsin 本身會不會誘發心律不整，以及如果不會，是真的安全還是測試系統根本沒鑑別力。所以作者放兩個對照。E-4031 (50 µM) 是「該失敗的對照」：它已知會阻斷 hERG 鉀離子通道、延長 QT，是心律不整研究的標準陽性對照 (依 Harris et al. Toxicol. Sci. 2013)——如果系統連 E-4031 都看不出亂跳，那測試方法本身不可信。Forskolin (10 µM) 則是另一個方向的對照：它直接活化腺苷酸環化酶、暴力拉高 cAMP，跟 trequinsin 同樣會推高 cAMP 但機制不同；用它確認「單獨拉高 cAMP」這條路在這個系統是否會引發亂跳。三組各處理 1 h，把細胞放進 Tyrode buffer 給 0.5 Hz 電刺激 1 分鐘，用 Nikon Fluor 10× + Prime BSI-Express sCMOS (Teledyne Photometrics) 在 510 nm 收 GCAMP6 鈣螢光訊號 (protocol 依 Papa et al. Nat. Cardiovasc. Res. 2022)，計算 beat-to-beat 變異度。

少了 LDH 細胞毒性測試的話，你看到的「passive tension 下降」可能不是因為藥讓肌肉鬆開，而是因為細胞死掉、拉不動柱子了——讀數一樣會下降，但意義完全相反。LDH (lactate dehydrogenase) 平常被關在細胞膜內，一旦膜破裂就漏到上清液中，所以 LDH-Glo Cytotoxicity Assay 量上清液 LDH 等於量「有多少細胞破了」。trequinsin 處理 3 h 後上清液 LDH 沒升高，代表救援效果不是死細胞造成的假象。另一個漏洞是 PDE3 → cAMP → PKA 機制若沒被直接量到，就只是合理推測。作者用 Pierce IP Lysis Buffer + 蛋白酶／磷酸酶抑制劑 (ThermoFisher 78442) 萃取細胞蛋白，BCA 定量後取 5 µg 進 PKA colorimetric kit (Invitrogen EIAPKA) 直接量酵素活性，看到 trequinsin 處理後 PKA 活性實際上升，整條因果鏈才算釘死。

4. 工具與材料: 
- **trequinsin-HCl**: PDE3 抑制劑 (Tocris #23371)，本研究以 10 µM 急性處理 ECT，作為救援 RCM 表型的候選藥物。
- **PDE3 (phosphodiesterase 3)**: 細胞內水解 cAMP 的清道夫酵素，被抑制後 cAMP 累積、PKA 路徑活化。
- **cAMP**: 細胞內訊號傳遞分子，升高後驅動 PKA 活化下游鈣回收幫浦與肌絲感受器。
- **PKA**: cAMP 下游激酶，磷酸化 SERCA、troponin I 等靶點以加速鈣回收與肌肉放鬆。
- **E-4031**: 已知 hERG 鉀通道阻斷劑 (50 µM)，作為致心律不整測試的陽性對照 (Harris et al. 2013)。
- **Forskolin**: 腺苷酸環化酶活化劑 (10 µM)，直接拉高 cAMP，作為「單獨提升 cAMP」的對照組。
- **Tyrode buffer**: 細胞外電刺激實驗用的生理緩衝液，提供穩定離子環境以維持心肌跳動。
- **Prime BSI-Express sCMOS**: Teledyne Photometrics 高速 sCMOS 相機，用於 510 nm 收 GCAMP6 鈣螢光跡。
- **LDH-Glo Cytotoxicity Assay**: 量測上清液中漏出的 lactate dehydrogenase 以評估細胞膜破裂程度，急性細胞毒性指標。
- **PKA colorimetric kit (Invitrogen EIAPKA)**: 比色法直接量測細胞溶解物中 PKA 酵素活性，驗證 PDE3 抑制是否實際提升下游激酶活性。
- **Pierce IP Lysis Buffer**: ThermoFisher 87787，溫和細胞溶解液，搭配蛋白酶/磷酸酶抑制劑 (78442) 保留 PKA 活性。
- **repeated-measures 配對設計**: 同一條 ECT 在給藥前後各拍一次柱頭位移影片，組織自己當對照以壓低個別差異。

5. 與此篇文章的關係: 
在《Engineered cardiac tissue model of restrictive cardiomyopathy for drug discovery》這篇文章中，作者為了直接驗證 2D 鈣螢光篩出的 hit trequinsin 是否真能在 3D 高保真模型上修復 RCM 的核心力學缺陷，採用了 milliPillar ECT 上的急性藥物救援與安全性測試。它解決了「2D τ 縮短不等於真實心肌力學恢復」的瓶頸，把單孔篩選來的候選藥物送回成熟 ECT 量 passive tension 與 relaxation velocity，並同步以 E-4031／forskolin 對照測致心律不整、以 LDH 與 PKA 活性分別排除細胞死亡假象並釘死分子機制，產出可送下一步動物驗證的安全有效候選藥。
