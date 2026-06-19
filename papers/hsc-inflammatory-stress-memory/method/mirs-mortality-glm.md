---
subitem_id: "3-J"
title: "mIRS 計算與廣義線性模型預測死亡風險"
---

# mIRS 計算與廣義線性模型預測死亡風險

**Subitem:** 3-J · **Slug:** `mirs-mortality-glm`

## 主線
修改原版 Intermountain Risk Score (IRS) 去除年齡與代謝項，僅留 6 個 CBC 參數作為「血液衰老指標」，並以 GLM 檢驗 HSC-I / HSC-iM 程式在六大成熟細胞型中能否預測高/低 mIRS。

## 技術解析
原版 IRS (Intermountain Risk Score, Horne et al. 2009 *Am J Med*, ref. 58) 是一個臨床死亡風險分數：醫師把例行的 CBC + 代謝項 + 年齡套進性別專屬的係數，就能算出 5 年死亡風險。本研究只想看「HSC-iM 發炎記憶在血液裡的痕跡」對死亡風險的影響，因此把年齡與代謝兩塊整個拿掉，只留 6 個純血球指標：紅血球壓積比 (haematocrit)、白血球數 (WBC count)、血小板數 (platelet count)、紅血球平均體積 (MCV)、紅血球平均血色素濃度 (MCHC)、紅血球大小變異 (RDW)。沿用 Horne et al. 2009、Anderson et al. 2007 (ref. 109) 與 JUPITER 隨機試驗 (ref. 110) 的性別專一 5 年死亡風險係數，把 6 個 CBC 值代入男/女公式得到 mIRS。理由有兩層：把年齡挖掉，年輕組 (≤45 歲) 與老年組 (≥65 歲) 才能在同一張尺上比較，避免年齡自己吸走差異；把代謝項挖掉，糖尿病、高血壓的訊號才不會洗掉 HSC-iM 的訊號。為了再加一層保護，作者同時排除 22 種會干擾血液狀態的自我回報慢性病（高血壓、心肌梗塞、中風、氣喘、慢支、COPD、憂鬱、糖尿病、肝硬化、慢性肝炎、克隆氏症、潰瘍性結腸炎、IBS、濕疹、SLE、乾癬、MS、骨鬆、關節炎、癌症等），把『身體已經明顯病了所以血球也亂、mIRS 也高』這條第三變數混淆切掉。

CanPath 隊列大約有 330,000 位 OHS 參與者；全跑 scRNA-seq 不現實，中間風險者訊號又太弱。作者改採『極端取樣』(extreme sampling)：先用全人群的 CBC 算 mIRS，把樣本限縮在歐裔（避免族群結構雜訊）、年輕 (≤45 歲) 與老年 (≥65 歲) 兩端，再從每組依 mIRS 抓最高與最低各約 100 人，共 428 位受試者進到分子表型分析。這樣兩端差異被人為拉開，GLM 才有機會以可控樣本量看到顯著訊號。428 位受試者外周血先用 CD45 富集做 scRNA-seq，以 BoneMarrowMap 把細胞自動分到六大成熟細胞型：naive T 細胞、B 細胞、natural killer (NK) 細胞、dendritic cell (DC)、CD14 單核球、CD16 單核球。memory T 被特地排除，因為 T 細胞自己抗原驅動的記憶程式跟 HSC-iM 在許多 NF-κB / AP-1 基因上重疊，留著會讓 GLM 量到的訊號歸因錯位、變成在量 T 細胞自己的記憶。直接在每顆細胞上算 200 基因分數會被技術 dropout 噪音吃掉（單細胞在低表現基因常被測到 0 顆 UMI，這不是真的沒表現而是 droplet 沒抓到），所以作者改用 decoupler v2.0.2 的 `sum` 模式把同捐贈者同細胞型的細胞 UMI 加總成 pseudobulk，要求至少 10 顆細胞與 1,000 counts 才保留；接著用 scanpy 的 `normalize_total` + `log1p` + `scale` 標準化，再用 `score_genes` 對 HSC-I 與 HSC-iM 各 top 200 基因打成一個樣本級分數。每位受試者每個細胞型就剛好有一個分數，符合 GLM 的一人一觀測假設。

對六大細胞型 × 兩個程式 (HSC-I / HSC-iM) × 兩個年齡組分別跑廣義線性模型 (generalized linear model, GLM)，把『高 mIRS / 低 mIRS』當作 0 或 1 的結果，公式為 `高風險 = HSC 分數 + batch + 性別 + 年齡`。batch (不同 10X run 或收樣時段)、性別、年齡都已知會影響免疫細胞轉錄與 mIRS，必須一起放進模型才能扣掉混淆；即便極端取樣，年齡組內仍有 ±20 歲差距，因此 age 留在共變項。整套會跑出 24 次假設檢定 (6 × 2 × 2)，作者用 Benjamini–Hochberg (BH) 校正成 FDR，FDR < 0.05 才算顯著，把偽發現率壓在 5% 以下。沒做 BH，純靠機運就可能有 1–2 個假陽性混進結論。

## 工具與材料清單 (Toolchain)
- **IRS (Intermountain Risk Score)**：原版臨床 5 年死亡風險分數 (Horne et al. 2009)，由 CBC + 代謝項 + 年齡 + 性別專屬係數算出。
- **mIRS (modified IRS)**：本研究自訂版本，去除年齡與代謝項、只保留 6 個 CBC 參數作為純『血液衰老指標』。
- **6 個 CBC 參數**：紅血球壓積比 (haematocrit)、白血球數 (WBC count)、血小板數 (platelet count)、紅血球平均體積 (MCV)、紅血球平均血色素濃度 (MCHC)、紅血球大小變異 (RDW)。
- **extreme sampling**：從 33 萬人 CanPath 隊列中限縮到歐裔、年輕 (≤45 歲) 與老年 (≥65 歲) 兩端的 mIRS 極端者各約 100 人，共 428 位做 scRNA-seq。
- **六大成熟細胞型**：naive T、B、NK、DC、CD14 monocyte、CD16 monocyte；memory T 因與 HSC-iM 訊號重疊被排除。
- **decoupler v2.0.2 `sum` pseudobulk**：把同一受試者同細胞型所有單細胞 UMI 加總成樣本級表現量，要求至少 10 cells 與 1,000 counts。
- **scanpy score_genes**：把 HSC-I / HSC-iM top 200 基因清單算成每個 pseudobulk 樣本的一個分數。
- **GLM (generalized linear model)**：邏輯迴歸延伸；公式 `高風險 = HSC 分數 + batch + 性別 + 年齡`，在年輕與老年子群分別擬合。
- **Benjamini–Hochberg FDR**：對 6 × 2 × 2 = 24 次檢定做多重檢定校正，FDR < 0.05 才算顯著。
