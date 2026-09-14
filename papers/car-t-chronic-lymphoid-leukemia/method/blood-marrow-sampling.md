# 骨髓與血液取樣、Q-PCR/Luminex/Flow 樣本前處理

1. 引用自哪篇 paper: car-t-chronic-lymphoid-leukemia
2. Outline (任務主線): 骨髓與血液取樣、Q-PCR/Luminex/Flow 樣本前處理
3. Method:
      作者的取樣時間軸釘在幾個關鍵事件上：化療前、化療後 Day −1 (回輸前一天)、Day 23 (急性反應期)、Day 31 (完全緩解評估點)、Day 90 (3 個月) 與 Day 180 (6 個月)。每個時間點都同時抽 whole blood 與做一次骨髓穿刺 (aspirate) 加切片 (biopsy)。骨髓要兩種一起做，是因為兩者互補：穿刺抽出液態骨髓細胞懸浮液，可直接跑 flow cytometry (量 CD5/CD19/κ/λ)、抽 genomic DNA 做 qPCR、離心取上清液做 Luminex 測骨髓 cytokine；切片則取一小塊完整組織做 H&E 染色，看細胞在骨髓結構裡的空間分佈 (baseline 60% cellularity、CLL 佔 40%；Day 23 剩 10% CD5-negative 淋巴 aggregates；6 個月完全空掉)。
   血液這邊，作者分離出血清後把每份切成「一次用完的小管」(single-use aliquot)、−80°C 冷凍保存——血清裡的細胞激素每經一次凍融就會失活一部分，這樣跨批次跑 Luminex 時讀值才有橫向可比性。取樣時間點的選擇同樣不是隨機：Day 23 剛好落在 CART19 峰值期與 cytokine 峰 (Day 17-23)，若漏抽這一天，就無法把「CAR-T 峰值」與「TLS + cytokine + 骨髓清空」在時間軸上綁在一起、臨床反應也就無法歸因給 CART19；Day 90 與 Day 180 則負責證明 4-1BB 版 CAR-T 不會像 CD28 版那樣早早消失。取樣管線的紀律，決定了下游 qPCR/Luminex/Flow 的整套解讀能不能站得住。
4. 工具與材料:
   - **whole blood 取樣**: 每個時間點抽全血分離血清與 gDNA，供 qPCR、Luminex、flow。
   - **bone marrow aspirate**: 液態骨髓細胞懸浮液，用於 flow、qPCR、Luminex cytokine 測定。
   - **bone marrow biopsy + H&E**: 取一小塊完整骨髓組織做染色，看細胞在骨髓結構的空間分佈。
   - **single-use aliquot**: 每份血清分裝到一次用完的小管，避免反覆凍融失活。
   - **−80°C 冷凍保存**: 血清標準保存溫度，維持 cytokine 蛋白活性以便跨批次可比。
   - **取樣節點 (Day −1/23/31/90/180)**: 分別對應 baseline、峰值/TLS、完全緩解、長期存活等關鍵臨床/科學問題。
5. 與此篇文章的關係:
   在《Chimeric Antigen Receptor–Modified T Cells in Chronic Lymphoid Leukemia》這篇文章中，作者為了把「CAR-T 動力學」「宿主 cytokine 反應」「腫瘤負荷」三條時間序列疊在同一張時間軸上，建立了一條 whole blood + bone marrow 縱向取樣管線。它解決了單靠臨床觀察無法歸因延遲性 TLS 的瓶頸。它接收病人回輸後的樣本，並產出經 single-use aliquot 分裝的血清、gDNA 與骨髓組織，直接餵給下游 §3-A qPCR、§3-B Luminex 與 §3-C 流式分析。
