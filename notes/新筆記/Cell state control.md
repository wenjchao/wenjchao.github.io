# Cell state control

## 內文
1. Cell conversion 的目標，就是造出 specific tissue / cell。更具體的說，就是把細胞現在的 state 轉換到 specific cell 的 state，維持所需的特徵與功能
2. 注意：某個培養條件讓 neuron 比 glia 更容易存活，最後 neuron 的比例增加。這是細胞組成改變，並不能說明任何細胞改變了 state
3. Tools to control cell state
   1. Recombinant Growth factor：從細胞外提供訊號，可以模擬發育或組織環境中的訊號
      1. Endogenous Growth factor 通常很脆弱，半衰期短又不耐熱，所以要魔改一下
      2. Expensive
   2. Small molecule：因為使用原版 Growth factor 很麻煩所以改用 Small molecule
      1. 便宜，好製造，易於品質管理
      2. Agonist vs partial agonist vs antagonist
      3. off target effect ex: DAPT for Notch & γ-secretase
   3. Genome/Transcriptome/Proteome programming：直接改寫 cell state
      1. 具體操作技術另外單開一章
4. Routes of cell-state conversion
   1. Development-guided differentiation：逐步提供發育線索，引導細胞建立目標身分
      1. PSC → progenitors → target cell
      2. Follow and mimic the developmental process
      3. 以 neuron 為例
         1. Neural induction：PSC 進入 neural lineage，形成 neuroectoderm/neural progenitors
            1. dual SMAD inhibition：SMAD 是 (1) TGFβ/Activin/Nodal 和 (2) BMP 這兩條路徑在細胞內的傳訊蛋白。hPSC 一旦收到這兩種訊號，就會被推向中內胚層、表皮或滋養層，而同時阻斷這兩個訊號就會變成 neuroectoderm
         2. Regional patterning：建立區域身分
            1. 背腹軸 D–V：SHH、BMP/WNT
            2. 前後軸 A–P：WNT、FGF、RA
         3. Neurogenesis：neural progenitors → postmitotic neuron
         4. 這些過程共同影響最後產生的 neuronal subtype，實際上可能重疊
   2. Cell-fate programming/reprogramming：以關鍵命運調控因子，驅動目標 gene program
      1. 共同策略
         1. 強化目標細胞的 gene program，促使細胞重新建立或改變身分
         2. 例如透過 TF overexpression 或 CRISPRa
         3. 依照起始與目標 state，分成以下路徑
      2. Pluripotency reprogramming：somatic cell → iPSC
         1. 目標：建立 pluripotent state
         2. The “Yamanaka Factors (OSKM)”: OCT3/4, SOX2, KLF4, c-MYC
      3. Forward programming/direct induction：PSC → target cell
         1. 目標：直接驅動專化細胞的 gene program，繞過或壓縮 developmental 階段
         2. 例如 iPSC → neuron：NGN2 overexpression
      4. Lineage reprogramming/direct conversion / transdifferentiation：somatic cell A → somatic cell B
         1. 目標：改變已建立的 lineage identity，不經過 pluripotent state
         2. 例如 fibroblast → neuron：BAM (Brn2、Ascl1、Myt1l) factor 或 Ngn2 and Ascl1 overexpression
         3. 例如 astrocyte → neuron：Ngn2 and Isl1 overexpression 
         4. Preserve age-related signature
5. Maturation：immature neuron → functionally mature neuron
   1. 已經形成 neuronal identity  後，不代表其電生理和突觸功能已經成熟，因此還需要進一步建立成熟的細胞功能：後續仍需要完善 neuronal processes、ion-channel properties 和 synaptic machinery，並建立細胞間的功能性連接
   2. 添加生化調控分子，促進 maturation
      1. 透過細胞表面的 receptors/ion channels啟動或調整訊號，再由細胞內的 signaling pathways 影響成熟
         1. 所有神經元在 Maturation 階段都大同小異：BDNF、GDNF、CNTF、NT-3 (Growth factors, Neurotrophic factors) 
         2. 差在針對該神經元特有的受體要額外補充和該受體配對的因子
            1. DRG 的痛覺神經元表現 TrkA 和 RET，所以加 NGF 和 GDNF
            2. 本體感覺神經元表現 TrkC，就要加 NT-3
         3. Small molecules：例如作用於 NMDA receptor 或 L-type calcium channel 的分子
      2. 調控細胞內的 signaling/epigenetic regulators
         1. 分子進入細胞後，作用於細胞內的調控蛋白
         2. 例如透過 LSD1、DOT1L inhibitors 調整 epigenetic regulation，促進 neuronal maturation
   3. support cells co-culture
      1. 與 glial cells 等支持細胞 co-culture
      2. 由支持細胞提供分泌因子和細胞互動，例如 astrocytes 能分泌促進 synapse formation 的蛋白。
   4. 透過 electrical stimulation 改變細胞活動與訊號
      1. 藉由電刺激介入電活動及其下游反應，促進成熟相關過程
      2. 效果可能包含細胞內訊號改變，也可能涉及分泌因子，例如 Oh 等人的系統中，電刺激的促進效果與 CNTF production 有關。
6. Cell characterization：量測細胞的形態、分子表現與功能。是否得到目標細胞？比例是多少？還有哪些其他細胞？
   1. Morphological characterization：細胞長什麼樣子？
      1. Shape of the soma
      2. Neurite formation
      3. Branching of the neurons
      4. Neurite bundles
   2. Molecular characterization：細胞表現哪些分子？
      1. Protein expression
         1. Immunostaining
         2. Western blot
         3. FACS (Fluorescence-Activated Cell Sorting) through flow cytometry
      2. RNA expression
         1. RT-qPCR
         2. Bulk RNA-seq
         3. Single-cell RNA-seq
      3. 根據問題選擇需要的分子
         1. Pluripotency-associated markers
            1. 細胞核裡的轉錄因子：OCT3/4、NANOG、SOX2
            2. 細胞表面的分子：SSEA-4、TRA-1-60。
               1. 因為長在細胞表面，不用固定、打破細胞就能染，所以可以用 FACS 分選活細胞
         2. Differentiation / Lineage / subtype-associated markers
            1. V2a interneuron：VSX2（= CHX10）；要排除的鄰居 V2b：GATA3
            2. Motor neuron：MNX1（= HB9）+ ISL1
            3. Midbrain dopaminergic neuron：TH + FOXA2 + LMX1A
            4. Medium spiny neurons in striatum：DARPP-32 + CTIP2
            5. 在身體前後的哪個位置：HOX genes（編號越大越靠尾端）
         3. Maturation / synapse-associated markers
            1. 神經前驅細胞 NPC：SOX2、PAX6、Nestin (NES)，同時 OCT4 消失
            2. 剛變成神經元：TUBB3（βIII-tubulin，用 TUJ1 抗體偵測）、DCX
            3. 成熟神經元
               1. 細胞本身：Tau（軸突）、NeuN（細胞核）、MAP2（樹突）
               2. 突觸：synaptophysin（突觸前）、PSD-95（突觸後）
   3. Functional characterization：細胞實際能做什麼？
      1. Electrophysiology：直接量測電性質
         1. Patch clamp
         2. Membrane potential、ionic currents、action potentials、synaptic currents
      2. Calcium imaging：量測細胞內 Ca²⁺ 變化，作為活動的間接 readout
         1. Fluo-4：calcium-sensitive dye (small molecule)
         2. GCaMP：genetically encoded calcium indicator
   4. Basic culture quality control：培養物的基本品質是否合格？
      1. Cell health/viability
         1. 細胞是否存活、是否處於適合實驗的健康狀態
      2. Genomic integrity
         1. Karyotyping：檢查染色體數目與較大的結構異常
      3. Contamination
         1. 細菌、真菌
         2. Mycoplasma
            1. Hard to see
            2. Will cause the cells to grow slowly
            3. Should be tested for quarterly!
