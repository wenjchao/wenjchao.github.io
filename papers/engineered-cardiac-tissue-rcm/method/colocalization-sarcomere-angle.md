# 共定位 (Pearson) 與 sarcomere 排列角度量化

1. 引用自哪篇 paper: engineered-cardiac-tissue-rcm
2. Outline (任務主線): 共定位 (Pearson) 與 sarcomere 排列角度量化
3. Method: 

作者用兩種顏色螢光標籤同時染同一張切片：FLNC 用一種顏色 (例如紅)、α-actinin 用另一種顏色 (例如綠)。每個像素同時有紅亮度與綠亮度兩個值。如果「紅亮的地方綠也亮、紅暗的地方綠也暗」，代表這兩個蛋白共住一處 (共定位)；完全沒關係則各住各的。用 Pearson 相關係數 (r) 把這條關係壓縮成一個數字：r 接近 1 = 完美正相關 (共定位)、0 = 沒關係、−1 = 完全互斥。計算上是「對所有像素算紅亮度減平均乘以綠亮度減平均的平均 (共變異)，再除以兩通道各自標準差的乘積」，標準化後固定落在 −1 到 +1 之間，跨樣本可比、不受絕對亮度影響。實作直接用學界標準免費軟體 ImageJ 的 Coloc2 外掛，每張影像取 256 × 256 px ROI——一張整張照片大部分像素其實是細胞間空白區，紅綠都接近 0 會把 r 拉向 baseline、稀釋細胞內真正訊號；切到細胞內肌節區，r 才反映「FLNC 與 α-actinin 真的共住」的程度，且每張影像可重複取多個 ROI 提升統計力。

ECT 是一條長條狀組織，自然有一個「長軸」(tissue long axis)——從一根 PDMS 柱指向另一根那個方向。正常成熟心肌的肌節 (sarcomere) 應整齊順著長軸排，這樣收縮力才能沿長軸有效傳遞。作者用 ECT 整塊組織的共軛焦影像 (whole-mount confocal)，標記 α-actinin/ACTN2——它集中堆在 sarcomere 兩端的 Z-disk 上，染出來會在影像上呈一條一條銳利的平行條紋，每條線代表一個 Z-disk、一個 sarcomere 邊界。為什麼挑 α-actinin 而不是 troponin 或 myosin？因為後者分布在肌節全長，染出來是片狀條紋而非銳利的線，角度量化會被模糊；α-actinin 的「點狀規律」最適合電腦量角度。對每條 actinin 纖維量它與 long axis 的夾角，每塊組織取 30 條纖維形成一個角度分布——30 條是統計上估角度離散度的最小穩定樣本與半自動量測工時的折衷。角度集中在 0° 代表整齊、分布寬代表紊亂。值得一提的是，這個量化對主軸定義錯誤穩健：如果組織因脫柱或彎曲偏離柱間連線方向，所有 sarcomere 角度會被同向平移 (例如通通變成 15°)，但彼此相對關係不變，「離散度」量的是分布寬窄，不會被影響。

4. 工具與材料: 
- **ImageJ Coloc2 plugin**: ImageJ 官方共定位分析外掛，自動算 Pearson r 與其他共定位指標。
- **Pearson correlation coefficient (r)**: 兩通道亮度的線性相關係數，−1 到 +1，r 接近 1 = 共定位、0 = 無關、−1 = 互斥。
- **ROI 256 × 256 px**: 切到細胞內肌節區的感興趣區域，避免細胞外空白把 r 拉向 baseline 稀釋訊號。
- **α-actinin / ACTN2**: 集中在 sarcomere Z-disk 的 marker，染出來呈銳利平行條紋，是「sarcomere 走向」電腦可讀的最佳標記。
- **Whole-mount confocal imaging**: 把整塊 ECT 直接放上共軛焦顯微鏡 (Nikon A1) 成像，保留 3D 組織結構與主軸資訊。
- **Tissue long axis**: 兩根 PDMS 柱的連線方向，作為量 sarcomere 角度的參考基準。
- **Angular dispersion**: 30 條 actinin 纖維與長軸夾角分布的寬窄；越窄代表 sarcomere 排得越整齊。

5. 與此篇文章的關係: 
在《Engineered cardiac tissue model of restrictive cardiomyopathy for drug discovery》中，作者要把「病人型 ECT 看起來纖維歪七扭八」這個主觀印象變成可量化的證據，於是用 ImageJ Coloc2 算 FLNC 與 α-actinin 的 Pearson 相關係數做共定位量化，再從 whole-mount 共軛焦影像沿每條 α-actinin 纖維量它與組織長軸的夾角。輸出的兩個影像統計量讓「結構紊亂」可以對應到上游的力學表型 (passive tension 升、active force 降)，把 RCM 的分子病理與功能異常綁起來。
