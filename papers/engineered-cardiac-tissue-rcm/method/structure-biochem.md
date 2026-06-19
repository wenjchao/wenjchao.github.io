# 結構與蛋白生化檢驗

1. 引用自哪篇 paper: engineered-cardiac-tissue-rcm
2. Outline (任務主線): 結構與蛋白生化檢驗
3. Method: 

FLNC 蛋白若結構正常會均勻溶解在一般的溶解液裡，若聚集成不溶纖維塊則沉到管底分不開——作者就用這個性質做「可溶/不溶分離」。先把細胞泡進 Pierce IP Lysis Buffer 冰浴 30 min 把膜溶掉、16,000×g 離心 10 min，上清是「能被一般溶解液帶走」的可溶蛋白；沉澱再用更強力的方式重溶，西方點墨用 10 mM Tris-HCl + 4% SDS，分離分析用 DNase I (Roche) + 2% SDS + 超音波三件式——SDS 強迫蛋白解開、DNase I 把纏在裡面的細胞核 DNA 剪斷、超音波物理打散殘餘纏結。若省略這三件式，pellet 會卡在膠的 well 口進不去，不溶 FLNC 被低估、結論直接報廢。兩份各用 BCA 定量、每孔 20 µg 上 4–20% Tris-glycine 梯度膠 (Thermo XP04205BOX) 跑 SDS-PAGE，以 FLNC 抗體 (Sigma HPA006135) 點墨，並以 β-Actin (CST 5125S) 與 GAPDH (CST 3683) 內參校正上樣量；ΔGAA 病人版本若不溶 lane FLNC 比例升高，就直接拍到 ΔGAA 真的造成蛋白聚集。

為了看 FLNC 與肌節之間的空間關係，作者在兩個尺度各做一次免疫螢光 (immunofluorescence, IF)。2D 那一段把 iPSC-CM 鋪在 Matrigel 鍍過的 coverslip 上，4% PFA 固定 15 min → 0.1% Triton X-100 打洞讓抗體鑽進細胞 → 一抗過夜、二抗室溫 1 h：FLNC (Sigma HPA006135) 標蛋白本身、α-actinin/ACTN2 (MACS 130-119-766) 標肌節 Z 線、Cardiac Troponin/TNNT2 (ThermoFisher MA5-12960) 標肌絲鈣感受器、Vimentin (Abcam Ab24525) 標纖維母細胞，DAPI 染細胞核。讀數有兩個：其一，沿 α-actinin 平行線取 pixel intensity 用 ImageJ 算峰間距 = 肌節長度 (sarcomere length)，看 ΔGAA 細胞肌節是否縮短或失序；其二，把每張影像取 256 × 256 px ROI 用 ImageJ Coloc2 算 Pearson 相關係數——影像裡每個 pixel 在 FLNC (綠) 與 α-actinin (紅) 兩個通道各有亮度值，Pearson 把所有 pixel 的「綠亮度 vs 紅亮度」配對計算共變異程度，亮位一致接近 1、各走各的接近 0。若 ΔGAA 樣本 Pearson 顯著下降，就代表 FLNC 不再貼著 Z 線、跑去聚集成別處的不溶塊，正好與西方點墨上不溶份升高交叉印證。Whole-mount 那一段是把整條 ECT 直接拿去染：100% Methanol 室溫 15 min 一次完成固定加透化、5% BSA/PBS 阻斷 1 h、一抗 1 h (α-actinin 2 MACS 130-119-766、Vimentin Ab202504、Cardiac Troponin T BD 565744)，封在 ProLong Glass Antifade + NucBlue (Invitrogen P36981) 加 CoverWell chambers (Grace Bio-Labs 645501) 裡，用 Nikon A1 共軛焦顯微鏡逐層光學切片把 3D 組織內肌節走向看清楚；再對每條組織取 30 個量測，算肌節 fiber 與組織長軸的夾角分布，量化排列散亂程度。

為什麼流式量心肌細胞大小要用 SIRPA+/CD90− 雙標？ECT 經 200 U/mL Type II Collagenase (Worthington)/HBSS 37°C 1–2 h 解離後，鍋裡是心肌、纖維母細胞與少數殘留細胞的混合物；直接讀前向散射 (FSC，代表細胞大小) 會被纖維母細胞污染。作者用兩個表面抗體把心肌挑出來：anti-SIRPA (Biolegend 323806) 標的 SIRPA (signal regulatory protein α) 是 iPSC-CM 公認的陽性表面標記 (依 Dubois et al. Nat. Biotechnol. 2011)、CD90 (ThermoFisher 11-0909-42) 是纖維母細胞標記，只框 SIRPA+/CD90− 這群「真心肌」再讀 FSC 算大小。另外用 Sytox Blue (S34857) 排掉膜破的死細胞、Vibrant DyeCycle Ruby (V10309) 框有完整核的活細胞避免碎屑被誤計，最後用 Bio-Rad ZE5 cell analyzer 上機。這套門控才能公平比較 ΔGAA vs ψWT 心肌細胞是否有大小差異。

4. 工具與材料: 
- **Pierce IP Lysis Buffer**: ThermoFisher 87787，溫和細胞溶解液，先把膜溶掉拿到可溶蛋白。
- **可溶/不溶分離 (4% SDS / DNase I + 2% SDS + 超音波)**: 三件式強力重溶不溶 pellet，把聚集 FLNC 與纏繞 DNA 拆開，避免不溶份被低估。
- **FLNC 抗體 (Sigma HPA006135)**: 西方點墨與免疫螢光用以標 filamin C 本身。
- **α-actinin / ACTN2 (MACS 130-119-766)**: 肌節 Z 線標記，用以量化 sarcomere length 與 FLNC 共定位。
- **Cardiac Troponin / TNNT2 (MA5-12960 / BD 565744)**: 肌絲鈣感受器，標肌絲走向。
- **Vimentin (Abcam Ab24525 / Ab202504)**: 纖維母細胞中間絲標記，與心肌分離分析。
- **ImageJ Coloc2 (Pearson 相關係數)**: 在 256 × 256 px ROI 計算 FLNC 與 α-actinin 兩通道亮度共變異，量化共定位程度。
- **Sarcomere length (peak-to-peak)**: 沿 α-actinin 平行線取 pixel intensity 的峰間距，量化肌節長度。
- **Whole-mount IF (100% MeOH 一步固定/透化)**: 整塊組織染色，搭配 Nikon A1 共軛焦逐層切片觀察 3D 肌節走向。
- **Sarcomere 角度分布**: 每條 ECT 取 30 個量測，計算 actinin fiber 與組織長軸夾角，量化排列散亂程度。
- **SIRPA+/CD90− 流式門控 (Dubois 2011)**: anti-SIRPA (Biolegend 323806) + CD90 (ThermoFisher 11-0909-42) 雙標框出純 iPSC-CM。
- **活/死細胞框選 (Sytox Blue / Vibrant DyeCycle Ruby)**: Sytox Blue (S34857) 染膜破死細胞、DyeCycle Ruby (V10309) 染有核活細胞，去除碎屑。
- **Bio-Rad ZE5 cell analyzer**: 流式細胞儀，讀 FSC 估算心肌大小。
- **4–20% Tris-glycine gel (Thermo XP04205BOX)**: 梯度 SDS-PAGE 膠，分離大小範圍廣的 FLNC 與內參蛋白。
- **β-Actin (CST 5125S) / GAPDH (CST 3683)**: 西方點墨內參，校正上樣量。

5. 與此篇文章的關係: 
在《Engineered cardiac tissue model of restrictive cardiomyopathy for drug discovery》這篇文章中，作者為了把 ΔGAA 突變造成的臨床舒張缺陷與分子病理對位，採用了 FLNC 可溶/不溶蛋白分離、共定位免疫螢光與流式心肌大小門控等結構生化檢驗。它解決了「只有力學表型而沒有分子病理證據，無法說明 FLNC 突變是透過蛋白聚集致病」的瓶頸，把 iPSC-CM 與 ECT 切片轉成西方點墨不溶份比例、Pearson 共定位係數、sarcomere length 與角度分布等可計算讀數，為下游 RCM 致病機制與藥物救援結論補上分子層級的對應證據。
