---
subitem_id: "2-F"
title: "Ontario Health Study 周邊血 scRNA-seq"
---

# Ontario Health Study 周邊血 scRNA-seq

**Subitem:** 2-F · **Slug:** `ontario-health-pbmc-scrna`

## 主線
從 ~330,000 人 CanPath 隊列中以 mIRS (modified Intermountain Risk Score) 與年齡為篩選變數，挑出 428 位極端 IRS 個體，量化 HSC-iM 程式在循環血細胞中的富集與全因死亡風險的關聯。

## 技術解析
作者要在活人血液中找 HSC-iM 程式的「迴音」。他們先在 CanPath 這個 33 萬人的加拿大全國健康世代裡，用 mIRS 給每個人算一個「血液衰老指數」分數；mIRS 只用六個常規驗血數值——血比容、白血球數、血小板數、紅血球平均體積（MCV）、平均紅血球血紅蛋白濃度（MCHC）、紅血球分布寬度（RDW）——並依性別查表轉成 5 年死亡風險係數。為了讓訊號最大化且控制成本，作者採極端取樣：歐裔人群中分別在 ≤45 歲與 ≥65 歲各挑 mIRS 最高 100 人與最低 100 人，共 428 位。冷凍 PBMC 用 TTM 解凍液（10% FBS + 25 mM HEPES + 55 μM 2-mercaptoethanol + 1 mM sodium pyruvate）滴入恢復，再跑 25 U/ml benzonase × 15 min 37 °C 把死細胞釋出的游離 DNA 切碎；接著用 CD45 microbeads (Miltenyi) 把白血球勾出來，TC20 Cell Counter + trypan blue 計數後取 4,000 顆送 10X Chromium 3' v2 文庫、NovaSeq 定序（R1 = 26、i7 = 8、R2 = 98）、CellRanger v3.0.0 對齊 hg38。最後把每個細胞型的細胞合併成 pseudobulk——把同一人同細胞型的所有單細胞加總，避掉 dropout 噪音；scanpy `score_genes` 對 HSC-I 與 HSC-iM 各 top 200 基因打分得到 HSC_score，再用 GLM `high_risk ~ HSC_score + batch + sex + age` 在年輕（≤45）與老年（≥65）子群內分別跑，看 HSC_score 高低能不能預測這個人屬於 high 還是 low mIRS。

mIRS 為什麼只用六個 CBC 參數就能反映死亡風險？原版 IRS (Horne et al. 2009) 從大型臨床資料庫挖出來這六項常規驗血對 5 年內全死因死亡有獨立預測力——例如 RDW 高代表紅血球大小分散（老化骨髓徵兆）、白血球異常可能反映慢性發炎。本研究改用 modified IRS 把年齡與代謝項拿掉，讓 mIRS 純粹反映血液狀態；再分年輕/老年子群跑 GLM 才不會 double-count 年齡。為什麼用極端取樣？33 萬人裡絕大多數 mIRS 屬於中段平均、HSC-iM 程式差異最小，隨機抽會被攤平；改採「最高 100 與最低 100」兩極端，差異最大、有限樣本量才能看出顯著——這是流行病學常見的 extreme phenotype sampling 策略。為什麼刻意排除 memory T？因為 HSC-iM 程式裡有大量 NF-κB 與 AP-1 motif 相關基因，跟成熟 memory T 細胞自己的免疫記憶程式高度重疊；若不排除，HSC_score 在 memory T 上會自動偏高，這個高值可能是 T 細胞自己的免疫記憶而不是從 HSC-iM 遺傳下來的，為避免兩種「記憶」混淆，作者把 memory T 拿掉。

如果省掉解凍時的 benzonase，凍存 PBMC 解凍時死細胞釋出的游離 DNA 會跟活細胞一起跑進 10X 油滴，把細胞條碼污染——UMAP 充滿 ambient 噪音、scanpy `score_genes` 訊號被稀釋；25 U/ml × 15 min 37 °C 的 benzonase 把游離 DNA/RNA 切成短碎片就不會干擾微流體，是 10X 標準前置步驟。同樣容易被忽略的是 CD45 富集：PBMC 還是會殘留少量紅血球、血小板與細胞碎片，這些雜質會佔掉 4,000 顆細胞配額裡的一部分等於浪費 droplet；CD45 microbeads 把白血球選擇性勾出來上機，能確保 4,000 顆 input 都是分析目標（B、T、NK、單核球、樹突細胞等），對「428 位 × 每位 4,000 細胞」的有限預算很關鍵。

## 工具與材料清單 (Toolchain)
- **CanPath / Ontario Health Study**：加拿大 33 萬人健康世代研究，提供 mIRS 篩選的人群池。
- **modified Intermountain Risk Score (mIRS)**：六項常規驗血 (Hct, WBC, Plt, MCV, MCHC, RDW) 加性別權重的血液衰老指標。
- **極端取樣 (extreme phenotype sampling)**：只挑 mIRS 最高與最低 100 人，最大化 between-group 訊號。
- **TTM 解凍液**：10% FBS + 25 mM HEPES + 55 μM 2-ME + 1 mM 丙酮酸鈉的 PBMC 恢復液。
- **Benzonase (25 U/ml × 15 min)**：廣譜核酸酶，降解死細胞釋出的游離 DNA/RNA，避免 10X 油滴污染。
- **CD45 microbeads (Miltenyi)**：磁珠選擇性勾出 CD45⁺ 白血球，確保 4,000 顆 input 都是分析目標。
- **10X Chromium 3' v2 + NovaSeq + CellRanger v3.0.0**：本世代周邊血 scRNA-seq 文庫建構、定序與比對工作流。
- **Pseudobulk (decoupler `sum`)**：同人同細胞型加總成假整批，避掉單細胞 dropout 與隨機波動。
- **scanpy `score_genes`**：對指定 200 基因平均表現減 random reference，得到該細胞群的程式分數。
- **GLM `high_risk ~ HSC_score + batch + sex + age`**：年輕/老年子群內分跑，控制 batch/性別/年齡後檢驗 HSC_score 解釋力。
- **排除 memory T**：因 HSC-iM 程式與 T cell memory 高度相似，刻意排除以避免假性關聯。
