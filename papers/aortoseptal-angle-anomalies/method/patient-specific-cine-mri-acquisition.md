# Patient-specific cine-MRI acquisition (受試者心臟動態 MRI 影像取得)

1. 引用自哪篇 paper: aortoseptal-angle-anomalies
2. Outline (任務主線): Patient-specific cine-MRI acquisition (受試者心臟動態 MRI 影像取得)
3. Method: 
作者要的不是一張心臟靜止照片，而是「心臟一邊跳、一邊被拍下來」的縮時影片——這種會跟著心跳連拍的磁振造影叫心臟動態磁振造影 (cine-MRI)。整段影片涵蓋一次完整心跳：心室先被血液撐到最飽 (end-diastole)，再用力擠出血液縮到最小 (end-systole)，然後再次鬆開。MRI 一次只能拍一個平面切片，所以要從不同方向各拍一疊：短軸切面 (short-axis) 把心臟橫切成一片片麵包；長軸的 2-、3-、4-chamber 切面則沿心臟長軸切，分別看到 2、3、4 個腔室；把這幾種切面疊在一起，3D 重建時內外輪廓才對得起來。每張切片的像素邊長 (in-plane resolution) 決定能看多細，相鄰切片間隔 8 mm (slice thickness)，也就是沿厚度方向每 8 mm 才有一張新照片。
作者選的不是 DSS 病人，而是一位 21 歲健康年輕女性，掃描儀是 3 特斯拉的 GE Medical Systems MR 750w。為什麼挑健康人？這個研究要追問「光是夾角變陡能不能解釋血流變亂」，如果一開始就拿病人，他的心臟可能已經被疾病改造過 (心肌肥大、瓣膜異常)，這些變化會跟夾角效應混在一起拆不開；所以反過來拿一顆健康的心臟當「乾淨底材」，再人工把夾角調陡，後面看到的差異就只能歸因於夾角。3 特斯拉而非常見的 1.5 特斯拉，是因為磁場愈強訊噪比愈高，同樣 8 mm 切片下能看到更清楚的心壁輪廓，重建出來的幾何才夠精準。
8 mm 厚切片有個代價：任何沿厚度方向小於 8 mm 的結構都會被「平均掉」、看不到。LV 內壁那些凹凸的小肌肉束 (trabeculae carneae) 與兩根突出的乳頭肌 (papillary muscles) 都在這個量級以下，所以根本進不了重建幾何，下游模擬等於把內壁當成平滑壁，近壁速度與 WSS 會略微比真實情況平滑。作者在 Limitations 也承認這點，但補充這個簡化在 LV CFD 文獻是常見作法，整體 LV 流場與相位對比 MRI 量測仍能對上。
4. 工具與材料: 
- **cine-MRI**: 會跟著心跳連拍的心臟磁振造影，把整顆心臟一個完整週期錄成 3D 縮時影片，用心電圖當節拍器把多次心跳的同相位訊號合成一段時間序列。
- **3T GE Medical Systems MR 750w**: 本研究用的磁振造影掃描儀，磁場強度 3 特斯拉（比常見 1.5 特斯拉更高訊噪比）。
- **short-axis view**: 短軸切面，垂直心臟長軸把心臟橫切成一片片麵包的影像方向。
- **2-/3-/4-chamber views**: 沿心臟長軸切的三種長軸切面，分別看到 2、3、4 個腔室，用於與短軸交叉校正 3D 輪廓。
- **in-plane resolution**: 單張切片內像素邊長，決定同一張片子裡能看多細的構造。
- **slice thickness**: 相鄰切片之間的厚度（本研究 8 mm），決定 3D 重建時沿厚度方向的解析能力。
- **end-diastole / end-systole**: 心動週期的兩個極端時相：心室被血撐到最大／被擠到最小。
- **trabeculae carneae / papillary muscles**: 心室內壁的小肌肉束與乳頭肌，因小於 8 mm 切片厚度而被本研究的重建幾何省略。
5. 與此篇文章的關係: 
在《Significance of aortoseptal angle anomalies to left ventricular hemodynamics and subaortic stenosis: A numerical study》這篇文章中，作者要在電腦裡單獨檢驗 AoSA 變陡對血流的純效應，於是先用心臟動態磁振造影 (cine-MRI) 把一位 21 歲健康女性的心臟動態錄下來。這套影像提供下游 3D LV 幾何重建與壁面變形邊界條件所需的真實素材，避免使用理想化解析變形函數而失真。
