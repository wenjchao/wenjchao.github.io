---
title: "心臟組織之 hydrogel 包埋與接種"
subitem_id: "2-D"
---

# 主線
以最小體積 (15 µL / 550,000 cells) 將心肌細胞與纖維母細胞包埋於 fibrin 或 collagen hydrogel，於 pillar 間原位 gel 化並在 7 天內自發 compaction，形成貼附於 pillar 頭部的緊密 3D 組織。

# 技術解析
讀者拿到純化好的 iPSC-CM 與纖維母細胞後，按 心肌細胞 : 纖維母細胞 = 75% : 25% 混合，總細胞數 550,000 顆，重懸於 RPMI-B27 培養基。每個井最終放 15 µL，分兩步加：先在 pillar 之間滴入 3 µL thrombin (2.5 U/mL)，再立刻把 12 µL 含 33 mg/mL fibrinogen 的細胞懸液加上去 (最終 fibrinogen 濃度 5 mg/mL)。Thrombin 一碰到 fibrinogen 就把它切成 fibrin monomer、自發聚合交聯成網狀 fibrin gel 把細胞包住；放回 37 °C 培養箱 15–20 分鐘讓 gel 完全固化。換 collagen 配方則依 Advanced Biomatrix (cat. 5279) 廠商 protocol 配製到終濃度 4 mg/mL，同樣每井 15 µL。Gel 剛凝固時會貼在 PDMS 井壁上，但作者要的是「組織自己收縮、只勾住兩根 pillar」，所以在 gel 化 1 小時與 24 小時後分別用一支 26G 細針沿井壁繞一圈，把細胞-gel 體跟井壁切開，只留下兩根 pillar 兩個錨點。接下來 7 天裡細胞會把胞外基質一邊降解、一邊用自己肌動蛋白-肌凝蛋白 (actomyosin) 的收縮力把整塊 gel 拉小，這就是自發收縮 (compaction)。因為兩根 pillar 是唯一的固定錨點，gel 被拉的方向會沿著兩根柱頭之間的軸線重排，最終體積大幅縮小、形狀變成一條啞鈴形貼住兩個柱頭。細胞也在過程中沿主應力方向重新排齊，逐漸形成有方向性的 3D 心肌組織，可培養達 100 天並保有 α-actinin 橫紋與 MLC-2v 心室型表型 (Supplementary Figure S4)。

為什麼 thrombin 一碰到 fibrinogen 就能形成 gel？Fibrinogen 是血漿裡負責止血的前驅蛋白，平常在水裡呈可溶狀態，因為兩端各有一段「保護蓋」(fibrinopeptide A 與 B) 把聚合位點蓋住。Thrombin 是一種絲氨酸蛋白酶 (serine protease)，作用就是把這兩段保護蓋剪掉，暴露出可以彼此辨識的接合位點；裸露的 fibrin monomer 隨即頭尾相接形成纖維 (fibrin fibrils)，再交織成 3D 網狀凝膠把細胞包住。這跟人體血液凝固時的反應一模一樣，只是作者搬到培養皿裡重現，並把 fibrinogen 濃度降到 5 mg/mL 以維持柔軟度與細胞貼附性。

為什麼 fibrin 培養必須額外加 5 mg/mL 6-aminocaproic acid (6-ACA)？心肌細胞與纖維母細胞會分泌 plasminogen activator，把 plasminogen 切活成 plasmin，再回過頭把 fibrin 網切碎——這就是身體溶解血塊的纖維蛋白溶解 (fibrinolysis) 機制。6-aminocaproic acid 是 lysine 的類似物，會競爭性卡住 plasmin/plasminogen 上的 lysine 結合位點，把 fibrinolysis 路徑擋下；collagen gel 主要由 collagen fibers 構成、不會被 plasmin 切，所以 collagen 配方不需要加。第 7 天進入電刺激階段時，作者把 6-ACA 移除，這時組織已足夠緊密。為何挑 75% CM : 25% fibroblast？讀者直覺以為 100% 純 CM 更好，但 fibroblast 在真心臟裡負責分泌膠原蛋白與細胞外基質、維持機械結構並透過 paracrine 訊號支援 CM 存活；若 hydrogel 裡只有 CM 缺少這層 ECM 支撐，組織會在 compaction 中崩散。75:25 是 CM 足夠強、fibroblast 足夠撐住結構的折衷比例。

兩個高頻失敗很容易讓肌條報廢。忘記在 1 h 與 24 h 用 26G 針頭剝離井壁，組織會在自發收縮時被井壁拉住一邊，最後變成不對稱的拉鋸狀、甚至卡死在井底某一角，根本繞不上 pillar 頭，量到的力是「壁的拉扯 + 殘缺肌條」沒辦法跟其他孔比較。Fibrin 配方若忘加 6-ACA，細胞會持續分泌 plasminogen activator 把 fibrin 切碎；前 2–3 天還看得到組織輪廓，第 5–7 天就會見到 gel 崩散、細胞團掉到井底，整個培養孔報廢。

# 工具/方法/材料
- **Fibrin hydrogel (fibrinogen + thrombin)**：33 mg/mL fibrinogen 與 2.5 U/mL thrombin 反應；thrombin 切除 fibrinopeptide A/B 後 fibrin monomer 聚合成 3D 網狀膠，終濃度 5 mg/mL。
- **Collagen hydrogel (Advanced Biomatrix, 4 mg/mL)**：備選凝膠材料，依廠商 protocol 配製、不需 fibrinolysis 抑制劑。
- **75% CM : 25% fibroblast**：細胞配方比例；CM 提供收縮力、fibroblast 提供 ECM 支撐與 paracrine 訊號，比例已先前最佳化。
- **15 µL / 550,000 cells**：每井接種體積與細胞數，最小體積策略確保 compaction 後緊密貼住兩個 pillar 頭。
- **6-aminocaproic acid (6-ACA, 5 mg/mL)**：lysine 類似物競爭性抑制 plasmin/plasminogen，阻擋 fibrin 被 fibrinolysis 降解；僅 fibrin 配方需要，第 7 天電刺激起移除。
- **Compaction (自發收縮)**：細胞透過 actomyosin 收縮把 hydrogel 拉小、沿主應力方向重排，7 天內形成貼附於 pillar 頭的緊密啞鈴形組織。
- **26G 針頭 release**：在 gel 化 1 h 與 24 h 後沿井壁繞一圈把組織從 PDMS 井壁切開，留下兩根 pillar 兩個錨點。
- **ROCK inhibitor 10 µM in media**：媒介中常駐保護劑，協助 CM 在接種早期度過解離與貼附壓力。
- **α-actinin / MLC-2v**：心肌肌節主成分與心室型 myosin light chain，定性驗證組織在 100 天培養後仍保有心室型表型。

# 與此篇文章的關係
在《milliPillar: A Platform for the Generation and Real-Time Assessment of Human Engineered Cardiac Tissues》這篇文章中，作者為了快速形成緊密的 3D 心肌組織並節省珍貴的 iPSC-CM，採用了 15 µL / 550,000 cells 微體積 fibrin/collagen hydrogel 接種法。這個方法解決了傳統大體積 EHT 培養耗細胞且 compaction 不均的瓶頸，吃進 2-C 純化好的 iPSC-CM 與纖維母細胞、產出貼附於 pillar 頭的啞鈴形肌條，直接交給 2-E 的長期電刺激訓練。
