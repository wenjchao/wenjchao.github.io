# Cell state control

## 內文
1. Cell state control 的目標，就是造出 specific tissue / cell。更具體的說，就是把細胞現在的 state 轉換到 specific cell 的 state，維持所需的特徵與功能
   1. 目標細胞要從三方面定義：種類、位置、成熟度。要做到什麼程度，由實驗問題決定
   2. 這三方面由不同步驟決定，最後也要分別檢查：

      | 目標細胞的哪一面 | 由哪一步決定 | 怎麼檢查 |
      |---|---|---|
      | 種類：哪一種神經元 | Differentiation：neural induction → regional patterning → neurogenesis | 種類 markers，例如 V2a 看 VSX2 |
      | 位置：在神經管的哪一區 | Differentiation 裡的 regional patterning | 區域 markers，例如 HOX genes |
      | 成熟度：走到哪一步 | Maturation | 階段 markers、patch clamp、calcium imaging |

2. 注意：某個培養條件讓 neuron 比 glia 更容易存活，最後 neuron 的比例增加。這是細胞組成改變，並不能說明任何細胞改變了 state
   1. 只看比例分不出這兩種情況，要看各種細胞的絕對數量（見 6. Cell characterization）
3. Tools to control cell state
   1. 分子大小決定它能不能穿過細胞膜，也就決定它能作用在哪裡

      | | Recombinant growth factor（蛋白質） | Small molecule |
      |---|---|---|
      | 能不能進細胞 | 太大，進不去 | 小，進得去 |
      | 作用在哪裡 | 只能接細胞表面的受體 | 細胞表面和細胞內的目標都可以，例如 DAPT → γ-secretase |
      | 好處 | 就是發育或組織環境中原本的訊號 | 便宜，好製造，易於品質管理（課外） |
      | 壞處 | Expensive；通常很脆弱，半衰期短又不耐熱（課外） | 進得去細胞、到處碰得到，所以容易有 off-target effect |

   2. Recombinant：把基因放進細菌或細胞，讓它們生產這個蛋白，因為從組織萃取的量不夠用（課外）。有些產品另外改造過，比較耐熱（課外）
   3. Agonist 活化路徑，antagonist 抑制路徑
      1. 同一條路徑可以在不同位置活化或抑制，不同分子的強度也不同，所以可以用來微調訊號強弱
      2. 例：SHH 路徑的 agonist 中，SAG 比 purmorphamine 強。SHH 越強，細胞越偏腹側，所以換分子或調劑量，就能調整細胞落在背腹軸的哪個位置
   4. Off-target effect 的例子：DAPT 是 γ-secretase inhibitor，用來擋 Notch；但 γ-secretase 也參與 amyloid-β 的產生、synapse 的形態與功能、hair follicle conversion
   5. Genome/Transcriptome/Proteome programming：直接改寫 cell state
      1. 具體操作技術另外單開一章
4. Routes of cell-state conversion
   1. Development-guided differentiation：逐步提供發育線索，引導細胞建立目標身分
      1. PSC → progenitors → target cell
      2. Follow and mimic the developmental process
      3. 以 neuron 為例
         1. Neural induction：PSC 進入 neural lineage，形成 neuroectoderm/neural progenitors
            1. dual SMAD inhibition：同時擋 TGFβ/Activin/Nodal（用 SB431542）和 BMP（用 LDN193189）。SMAD 是這兩條路徑在細胞內的傳訊蛋白
            2. 為什麼這樣會變成 neuroectoderm？人類 PSC 要靠 TGFβ/Activin 訊號才能留在幹細胞狀態（所以培養時要加 TGFβ1，見 [[Cell culture conditions]]），擋掉它，細胞就開始分化；BMP 會把細胞推向表皮或滋養層；兩條都擋，細胞就走預設的路線：neuroectoderm（課外）
            3. 要推向中內胚層，需要高劑量的 Activin/Nodal（課外）
         2. Regional patterning：建立區域身分。神經管裡，前驅細胞在哪一區，大致決定它會變成哪一種神經元
            1. 背腹軸 D–V：腹側 SHH；背側 BMP/WNT
            2. 前後軸 A–P：WNT、FGF、RA，越多越靠尾端
         3. Neurogenesis：neural progenitors → postmitotic neuron
            1. DAPT 擋 Notch，讓前驅細胞停止分裂、變成神經元
         4. 這些過程共同影響最後產生的 neuronal subtype，實際上可能重疊
      4. 三個例子：同一套規則，換訊號就換目標

         | 目標神經元 | 關鍵訊號 | 道理 |
         |---|---|---|
         | Striatal neurons（前腦） | IWR1 擋 WNT | WNT 越少越靠前，所以留在前腦 |
         | Midbrain dopaminergic neurons | CHIR（活化 WNT）、SHH、purmorphamine、FGF8b | 中腦比前腦後面，要一些 WNT；這種神經元在腹側，要 SHH |
         | V2a interneurons（脊髓） | RA、中等劑量 purmorphamine、DAPT | RA 推到脊髓；中等的 SHH 落在 V2 那一區；Notch 決定 V2a 或 V2b，DAPT 擋掉 Notch 就變成 V2a |

   2. Cell-fate programming/reprogramming：以關鍵命運調控因子，驅動目標 gene program
      1. 共同策略
         1. 強化目標細胞的 gene program，促使細胞重新建立或改變身分
         2. 例如透過 TF overexpression 或 CRISPRa
         3. 依照起始與目標 state，分成以下路徑（PSC → PSC 就是維持 pluripotency，見 [[Cell culture conditions]]）
         4. 投影片把 iPSC 也算成 direct conversion 的一個例子；這裡依起點和終點分開
      2. Pluripotency reprogramming：somatic cell → iPSC
         1. 目標：建立 pluripotent state
         2. The “Yamanaka Factors (OSKM)”: OCT3/4, SOX2, KLF4, c-MYC
      3. Forward programming/direct induction：PSC → target cell
         1. 目標：直接驅動專化細胞的 gene program，繞過或壓縮 developmental 階段
         2. 例如 iPSC → neuron：NGN2 overexpression
            1. 用 doxycycline（Dox）開關：有 Dox 時，rtTA 結合 TetO，打開 NGN2
            2. 缺點：做出來的大多是 excitatory cortical neurons。因為 NGN2 會抑制 MASH1，而 inhibitory（GABAergic）neuron 需要 MASH1
      4. Lineage reprogramming/direct conversion / transdifferentiation：somatic cell A → somatic cell B
         1. 目標：改變已建立的 lineage identity，不經過 pluripotent state
         2. 例如 fibroblast → neuron：BAM (Brn2、Ascl1、Myt1l) factor 或 Ngn2 and Ascl1 overexpression
         3. 例如 astrocyte → neuron：用 CRISPRa 在 astrocyte 打開 Ngn2 and Isl1
            1. 在活體內做，改善了 spinal cord injury 的恢復。這是研究再生的人對 direct conversion 有興趣的原因
         4. Preserve age-related signature
            1. iPSC reprogramming 會把細胞的年齡痕跡洗掉；direct conversion 不經過 pluripotent state，所以年齡痕跡留下來，適合研究老化相關的疾病
            2. 例：fibroblast 用 Ngn2 and Ascl1 轉成的 neuron（iN）保留了年齡痕跡；Alzheimer's disease 病人的 iN 比較不成熟
5. Maturation：immature neuron → functionally mature neuron
   1. 已經形成 neuronal identity 後，不代表其電生理和突觸功能已經成熟，因此還需要進一步建立成熟的細胞功能：停止分裂（postmitotic）、完善 neuronal processes、表現 neurotransmitters、建立 ion-channel properties 和 synaptic machinery，並建立細胞間的功能性連接
   2. 身分已經決定，所以這個階段加錯東西，細胞只是死得比較多或長得比較不成熟，身分不會改變；differentiation 階段身分還沒決定，加錯了，細胞會變成別種細胞
   3. 下面幾種方法都是送成熟訊號給細胞，差在訊號從哪裡來
   4. 添加生化調控分子，促進 maturation。作用在哪裡，看分子能不能進細胞（見 3. Tools）
      1. 透過細胞表面的 receptors/ion channels啟動或調整訊號，再由細胞內的 signaling pathways 影響成熟
         1. Growth factors, neurotrophic factors：BDNF、GDNF、CNTF、NT-3
         2. 每種因子接不同的受體，負責不同的過程，所以神經元有哪種受體，就加和該受體配對的因子
            1. DRG 的痛覺神經元表現 TrkA 和 RET，所以加 NGF 和 GDNF（課外）
            2. 本體感覺神經元表現 TrkC，就要加 NT-3（課外）
         3. Small molecules：NMDA（glutamate receptor agonist）、Bay K 8644（L-type Ca²⁺ channel agonist）
            1. 兩者都讓 Ca²⁺ 流進細胞，就像神經元真的在放電一樣，等於用藥物模擬電活動（課外）
      2. 調控細胞內的 signaling/epigenetic regulators
         1. 分子進入細胞後，作用於細胞內的調控蛋白
         2. 例如透過 LSD1、DOT1L inhibitors 調整 epigenetic regulation，促進 neuronal maturation
      3. 新的分子可以用高通量篩選找：一次測很多分子，前提是要有可靠的成熟度 readout（見 6. Cell characterization）。上面的 NMDA、Bay K 8644、LSD1 inhibitor、DOT1L inhibitor 就是這樣找到的組合（GENtoniK cocktail）
   5. support cells co-culture
      1. 與 glial cells 等支持細胞 co-culture
      2. 由支持細胞直接分泌 neurotrophic factors，也提供細胞互動，例如 astrocytes 能分泌促進 synapse formation 的蛋白（課外）
   6. 透過 electrical stimulation 改變細胞活動與訊號
      1. 藉由電刺激介入電活動及其下游反應，促進成熟相關過程
      2. 效果可能包含細胞內訊號改變，也可能涉及分泌因子，例如 Oh 等人的系統中，電刺激讓細胞多分泌 CNTF
      3. 有研究發現電刺激促進成熟的效果比 BDNF 好，但實驗是在 SH-SY5Y 神經母細胞瘤細胞上做的，要打折看
6. Cell characterization：量測細胞的形態、分子表現與功能。是否得到目標細胞？比例是多少？還有哪些其他細胞？
   1. Morphological characterization：細胞長什麼樣子？
      1. Shape of the soma
      2. Neurite formation
      3. Branching of the neurons
      4. Neurite bundles
   2. Molecular characterization：細胞表現哪些分子？
      1. Protein expression
         1. Immunostaining
         2. Western blot（課外）
         3. FACS (Fluorescence-Activated Cell Sorting) through flow cytometry：能算出各種細胞的比例
      2. RNA expression
         1. RT-qPCR：一次只測幾個基因，但結果很快
         2. Bulk RNA-seq、single-cell RNA-seq：測全部基因，但貴、慢，很難同時測很多條件
      3. 根據問題選擇需要的分子：看「有什麼」，也看「沒有什麼」
         1. 一個 marker 常常不夠。例如 SOX2 在 PSC 和 NPC 都有，要看到 OCT4 消失、PAX6 出現，才知道已經變成 NPC
         2. 還是幹細胞嗎？Pluripotency-associated markers
            1. 細胞核裡的轉錄因子：OCT3/4、NANOG、SOX2
            2. 細胞表面的分子：SSEA-4、TRA-1-60
               1. 因為長在細胞表面，不用固定、打破細胞就能染，所以可以用 FACS 分選活細胞（課外）
         3. 是哪一種、在哪個位置？Lineage / subtype / regional markers
            1. V2a interneuron：VSX2（= CHX10）；要排除的鄰居 V2b：GATA3
            2. Motor neuron：MNX1（= HB9）+ ISL1（課外）
            3. Midbrain dopaminergic neuron：TH + FOXA2 + LMX1A（課外）
            4. Medium spiny neurons in striatum：DARPP-32 + CTIP2（課外）
            5. 在身體前後的哪個位置：HOX genes（編號越大越靠尾端，課外）
         4. 走到哪一步？Stage markers
            1. 神經前驅細胞 NPC：SOX2、PAX6、Nestin (NES)，同時 OCT4 消失
            2. 剛變成神經元：TUBB3（βIII-tubulin，用 TUJ1 抗體偵測）、DCX（課外）
            3. 成熟神經元
               1. 細胞本身：Tau（軸突）、NeuN（細胞核）、MAP2（樹突，課外）
               2. 突觸：synaptophysin（突觸前）、PSD-95（突觸後，課外）
         5. 還混了什麼？Astrocyte：GFAP
            1. 人類的 radial glia 也有 GFAP，要確定是 astrocyte，通常再加 S100β 或 AQP4（課外）
   3. Functional characterization：細胞實際能做什麼？
      1. Electrophysiology：直接量測電性質
         1. Patch clamp
         2. Membrane potential、ionic currents、action potentials、synaptic currents
         3. 越成熟，action potentials 越多
      2. Calcium imaging：action potential 之後細胞內 Ca²⁺ 會上升，量測 Ca²⁺ 變化，作為活動的間接 readout
         1. Fluo-4：calcium-sensitive dye (small molecule)，加到細胞上就能用
         2. GCaMP：genetically encoded calcium indicator，要把基因放進細胞
   4. Basic culture quality control：培養物的基本品質是否合格？
      1. Cell health/viability
         1. 細胞是否存活、是否處於適合實驗的健康狀態
      2. Genomic integrity
         1. Karyotyping：檢查染色體數目與較大的結構異常
         2. 為什麼要定期查：染色體異常的細胞常常長得比較快，會慢慢佔滿培養皿。這也是一種細胞組成改變（課外）
      3. Contamination
         1. 細菌、真菌
         2. Mycoplasma
            1. Hard to see：很小，培養液也不會變混濁，要用專門的檢測（課外）
            2. Will cause the cells to grow slowly
            3. Should be tested for quarterly!
