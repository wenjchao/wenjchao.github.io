---
title: "組織學、免疫螢光與共軛焦影像"
subitem_id: "2-F"
---

# 主線
透過 H&E、α-sarcomeric actinin、cTnT、vimentin、MLC-2v 等染色，定性驗證 milliPillar 組織內部的細胞排列、肌節結構與心室型表型。

# 技術解析
milliPillar 組織學分兩條路線並行。整塊組織染色 (whole mount staining) 把整條 1–2 mm 厚的肌條用 100% 冰冷甲醇泡 10 分鐘——甲醇能溶細胞膜脂質讓抗體進去、同時瞬間沉澱固定蛋白，一步完成固定與通透。優點是保留 3D 立體結構看細胞在組織內的空間排列；缺點是抗體要穿透厚組織需時間。石蠟切片 (paraffin section) 則用 4% PFA 固定 30 分鐘、包埋於 Histogel、切 5 µm 薄片貼上玻片；薄片沒擴散困難可看局部細節，但失去 3D 資訊。PFA 透過甲烯橋把蛋白鎖在原位、形態保留最完整，但不通透細胞膜也會遮住抗原表位，所以切片後必須做兩件事：用 0.25% Triton X-100 戳出膜上小洞讓抗體進去；把切片泡在 pH 6 檸檬酸鈉緩衝液加熱到 95 °C 做熱誘導抗原回收 (HIER) 打斷甲烯橋。若跳過 HIER，cTnT 與 α-actinin 通道會一片黑、白做一場。兩種染色都需 2% (whole mount) 或 10% (切片) FBS/PBS 在室溫 block 1 小時，佔據組織內非特異吸附位點，避免抗體亂貼產生高背景。

作者用四個抗體當不同顏色標籤，一次回答「身份 + 結構 + 基質分布 + 心室型」四個維度。第一，α-sarcomeric actinin (1:750)：肌節 (sarcomere) 是心肌最小出力單元，α-actinin 站在每段肌節邊界的 Z 線上把肌絲固定住，螢光呈規律橫紋——條紋越清晰越密集代表肌節越成熟。第二，cTnT (1:100)：心肌肌節調節蛋白，告訴你組織內哪些細胞是心肌。第三，vimentin：纖維母細胞中間絲蛋白，標出 fibroblast 在組織裡的分布——光看 cTnT 看不出基質細胞架構合理性。第四，MLC-2v：成人心臟分心房與心室兩腔室，肌凝蛋白輕鏈也有心房型 (MLC-2a) 與心室型 (MLC-2v) 兩款；iPSC-CM 一開始混合多種，作者用 MLC-2v 抗體驗證 milliPillar 訓練後組織確實往心室型走，這是藥物測試最有臨床意義的標的（補充資料 Figure S4）。

免疫螢光像「兩段式郵件投遞」。一抗 (primary antibody) 是精準地址貼紙、只結合特定目標，本身不發光；二抗 (secondary antibody) 是會發光的郵差，認的是一抗的物種尾段並攜帶螢光分子，一抗插上目標後二抗來貼上就點亮目標位置；一個目標可被多個二抗環繞達訊號放大。NucBlue (DAPI 衍生物) 直接鑽進細胞核 DNA 雙股之間發藍光，當整張圖的細胞核底色。成像用 scanning laser confocal Eclipse Ti (Nikon) 或 inverted fluorescent DMi8 (Leica) 顯微鏡。共軛焦顯微鏡在物鏡與相機之間多放一個叫 pinhole 的小針孔——只准焦平面那一層發出的螢光通過、焦平面外的光被擋掉。一張影像只記錄一層 < 1 µm 厚的光學切片，再沿 z 軸逐層掃描堆疊出 3D 影像。對 1 mm 厚的 milliPillar 肌條，這是能同時看深層細胞排列的唯一辦法。

# 工具/方法/材料
- **H&E (Hematoxylin and Eosin)**：蘇木紫染酸性結構 (細胞核) 紫藍色、伊紅染鹼性結構 (細胞質、ECM) 粉紅色，看組織形態。
- **Whole mount staining**：整塊組織以 100% 冰冷甲醇 10 min 同步固定與通透，保留 3D 結構供整體排列觀察。
- **Paraffin section (4% PFA + Histogel, 5 µm)**：切薄片看局部高解析細節，需後續 Triton 通透與抗原回收。
- **熱誘導抗原回收 (HIER, pH 6 sodium citrate)**：高溫打斷 PFA 留下的甲烯橋，重新露出抗原表位供抗體辨識。
- **α-sarcomeric actinin (1:750)**：標肌節 Z 線，條紋規律密集代表肌節成熟。
- **cTnT (1:100)**：心肌肌節調節蛋白，看心肌細胞身份。
- **Vimentin**：纖維母細胞中間絲蛋白，看 fibroblast 在組織裡的分布。
- **MLC-2v**：心室型肌凝蛋白輕鏈，驗證組織往心室型走、非心房型。
- **NucBlue (DAPI 衍生物)**：鑽進細胞核 DNA 雙股發藍光，作細胞核底色。
- **Scanning laser confocal microscope**：用 pinhole 阻擋焦平面外螢光、逐 z 軸掃描重組 3D 影像，看 1 mm 厚肌條深層結構的唯一辦法。

# 與此篇文章的關係
在《milliPillar: A Platform for the Generation and Real-Time Assessment of Human Engineered Cardiac Tissues》中，作者要證明 milliPillar 訓練的組織內部真的長成「整齊排列、肌節成熟、心室型」的心肌結構。本步驟採用 H&E 形態描述加 α-actinin、cTnT、vimentin、MLC-2v 多重免疫螢光染色，並用 whole mount 與石蠟切片兩條路線互補，搭配共軛焦顯微鏡逐層 3D 掃描。它解決了「功能讀數好但結構未必對」的可能質疑，為下游 force/calcium 量測提供結構面的解釋基礎。
