# Family-wide hallucination：trRosetta-driven NTF2 scaffold 生成

1. 引用自哪篇 paper: de-novo-design-of-luciferases
2. Outline (任務主線): Family-wide hallucination：trRosetta-driven NTF2 scaffold 生成
3. Method: 
   作者用一個 AI 模型叫 trRosetta，這個模型本來的工作是「給它一條胺基酸序列，它告訴你蛋白會折成什麼形狀」（精確說：每兩個殘基之間的距離與相對角度的機率分布）。作者反過來用它：先丟一條候選序列進去，AI 給「我對這個摺疊有多自信」的分數；接著對序列做小修改——隨機抽兩種之一：「點突變」（換一個胺基酸）或「loop 改長改短」（在連接兩個結構元件的彈性 loop 上插入或刪掉一個殘基）——再丟進 AI 看分數有沒有變高。用一種「猜猜看再修改、修改後再猜」的隨機抽樣方法 (Markov chain Monte Carlo, MCMC) 重複幾千次，把序列逐步推向 AI 高度自信的版本。AI 同時當生成器跟 oracle，不需要任何 PDB 結構當模板。起始序列來自 NTF2 家族 2,000 條天然序列——挑這家族是因為 NTF2 天生中央就有一個大的疏水口袋，是之前測試形狀貼合度時最適合裝 DTZ 的家族。AI 評分有三條同時要滿足。第一條：跟 NTF2 家族 85 條已知實驗結構的「距離/角度」分布要對得起來——定義「什麼叫 NTF2」，避免 AI 越畫越不像家族成員。第二條：在保守區以外，AI 預測出的幾何要遠離「隨便一條序列會得到的幾何」(background distribution)，用 KL divergence 衡量；意思是「在 NTF2 的框架內、但要有結構獨特性、不能糊」。第三條：在蛋白內部強制建立多重氫鍵網路 (HBNet)——這些氫鍵像鉚釘，只有原子方向都對才能形成，等於要求結構必須剛好折成一個特定樣子才能滿足氫鍵，把「序列 → 結構」的映射收緊到接近一對一。三條同時優化就能逼出「屬於 NTF2、形狀清晰、自我穩定」的 scaffold。比起傳統 energy-based 設計那種「先列舉骨架幾何、再分別套序列」、骨架與序列分開算的做法，family-wide hallucination 把形狀跟序列綁在同一個 AI 上算：每改一次序列、AI 立刻告訴你形狀變成什麼、有多自信。這個迴圈自然把序列推向「只折成這個形狀、且 AI 非常確定」的點，也就是 sequence 與 structure 一對一映射。加上 HBNet 把內部鉚釘鎖住，最後產出的 scaffold 在 AlphaFold2 評估下 pLDDT 比 energy-based 設計更高、骨架也更接近天然 NTF2 (Fig. 1f, 1g)。如果只盯著 KL divergence 推、不約束跟 NTF2 距離分布要對齊，AI 會把序列推到自己最熟悉的 fold（很可能是 helical bundle），1,615 個 scaffold 就全沒有 DTZ 要的大口袋、整套設計失敗。那為什麼不直接用 PDB 現有 NTF2 當 scaffold？因為 PDB 上能直接拿的 NTF2 只有 85 條實驗結構加少數變體，數量遠遠不夠後續對每個 scaffold 各塞百萬種 rotamer；天然版 loop 通常太長會干擾受質結合、序列被改幾個殘基後折疊也常崩掉。Family-wide hallucination 一次就畫出 loop 已縮短、HBNet 已預組裝、口袋形狀彼此不同的 1,615 個理想化版本，數量擴大近 20 倍、結構穩定性也更高。
4. 工具與材料: 
   - **trRosetta**: 從序列預測蛋白每對殘基間距離與角度分布的 deep learning 模型 (Yang et al., PNAS 2020)。
   - **MCMC (Markov chain Monte Carlo)**: 在序列空間隨機修改 + 評分的迭代採樣方法，把序列逐步推向 AI 高度自信的版本。
   - **Point mutation / loop insertion / deletion**: MCMC 每步允許的兩種改動：換一個胺基酸，或在 loop 上插入/刪掉一個殘基。
   - **NTF2 fold family**: 天生中央帶疏水口袋的小型 α/β 蛋白家族；已有 85 條實驗結構與 2,000 條真實序列可當起點。
   - **Distance/orientation consistency loss**: 強制設計序列的預測幾何要落在 NTF2 家族 85 條實驗結構分布內，把方案鎖在 NTF2 fold 框架中。
   - **KL divergence loss**: 衡量「AI 對此序列預測的幾何」與「隨機序列的背景幾何」差距；差距愈大代表結構愈不糊、AI 愈有把握。
   - **HBNet**: Rosetta 出身的演算法，強制在蛋白內部排出多組埋藏的氫鍵接力，鎖緊 sequence-structure 映射。
   - **AlphaFold2 pLDDT**: AF2 對自己預測有多自信的局部分數，用來事後驗證 hallucinated scaffold 是否真的會折成設計形狀。
   - **1,615 hallucinated NTF2 scaffolds**: 最終產出的全新 scaffold pool，loop 縮短、HBNet 預組裝、口袋形狀多樣，公開於 IPD 網站。
5. 與此篇文章的關係: 
   在《De novo design of luciferases using deep learning》這篇文章中，作者為了繞開 PDB 上沒有形狀貼合 DTZ 的天然 scaffold 這個瓶頸，採用了 trRosetta 驅動的 family-wide hallucination。這個方法解決了傳統「先 theozyme 後 PDB 找 scaffold」因 PDB scaffold 數量太少、loop 太長、sequence-structure 關係脆弱而導致的設計失敗，把 NTF2 家族 85 條實驗結構與 2,000 條真實序列當起點，產出 1,615 個 loop 已縮短、HBNet 預組裝的理想化 scaffold，直接交給下一步 RifDock 把活性中心強塞進去。
