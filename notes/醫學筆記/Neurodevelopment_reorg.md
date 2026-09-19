# Neurodevelopment reorg

## 內文

神經發育中，細胞持續改變**位置、身分與彼此的連接**。下面沿著這些變化追蹤：組織如何形成、局部訊號如何指定命運、細胞如何增殖與遷移，以及突起如何找到目標。區域指定、神經生成、遷移與導引可以交錯進行，章節順序是理解順序。

沿神經管長軸的 **anterior–posterior（AP）** 區分頭尾；同一橫切面的 **dorsal–ventral（DV）** 區分背腹。讀圖需要的細胞基本構造、座標與基因調控原理，可展開下方背景。

[[神經發育背景：細胞、座標與基因調控]]

### 一、細胞重新排列，表面的 neural plate 折成 neural tube

1. **Gastrulation 讓細胞內移，建立 neural tissue 與周圍組織的位置**

   受精卵經 cleavage 增加細胞數。接下來的 **gastrulation** 改變細胞所在的位置：有些留在表面，有些移入內部，形成 ectoderm、mesoderm、endoderm。

   | 胚胎 | 細胞從哪裡進入 | 如何建立後續的組織關係 |
   |---|---|---|
   | **Amphibian** | Mesoderm、endoderm 經 blastopore 內移。 | Axial mesoderm 移到 neural plate 下方，形成 **notochord**；外側 ectoderm 的背側區域走向 neural ectoderm，其他區域形成 epidermal ectoderm。Dorsal blastopore lip 的訊號參與 neural induction。 |
   | **Mouse** | Epiblast 細胞經 primitive streak 內移，前端有 node。 | 新的 mesoderm、endoderm 在內部形成；原有 extraembryonic visceral endoderm 逐漸被新進入的細胞取代。前方的 **anterior visceral endoderm（AVE）** 另參與前腦指定。 |

   （待補 by codex：neural induction 的訊號如何使 ectoderm 取得 neural tissue 身分。）來源：L3，4–14。

   [[神經發育對照：早期胚胎、腦泡與區段|早期胚胎的形狀、胚層與後續區域對照]]

2. **Neural plate 中央凹陷，兩側抬高並在背側接合**

   Ectoderm 中的 **neural plate** 中央形成 neural groove，兩側形成 neural folds。Folds 向中線靠攏、接合成 **neural tube**，表面的 epidermal ectoderm 隨之在管外連續起來。

   Neural plate 與 epidermal ectoderm 的交界包含未來的 **neural crest**；閉合後，它位於 neural tube 背側。此時 **notochord 在管的腹側，成對 somites 在兩旁**，這些位置使後續訊號能從不同方向作用於管壁。

   ![Neural plate 凹陷、neural folds 接合，形成位於表皮下的 neural tube](Neuro%20development/圖片/neural-folding.png)

   （待補 by codex：哪些細胞形狀、附著或力學變化，促成 neural plate 彎曲及兩側接合。）來源：L3，16–19；L4，6。

3. **閉合沿長軸延伸，局部異常會留下不同缺陷**

   哺乳類示意圖先在中段偏前的位置接合，再朝 anterior、posterior 延伸。圖中時間分別是 mouse E7.5–E10.5、human「gestation days 18–28」、chick 23–33 hours post-fertilization；各物種的標示須分別判讀。（待補 by codex：human gestation days 的起算方式及與臨床產科週數的對應。）來源：L3，17。

   **Neural tube defects（NTDs）** 有不同部位與外觀。Folate（vitamin B9）參與 DNA methylation，與正常細胞生長及 NTDs 風險有關；遺傳、染色體與其他環境因素也參與其中。（待補 by codex：DNA methylation 如何影響神經管閉合。）來源：L4，5。

   [[神經管缺陷的形態對照]]

### 二、不同位置接收不同訊號，神經管沿頭尾取得區域身分

神經管前端形成 brain vesicles，後方延續成 spinal cord。前端先分 forebrain、midbrain、hindbrain，再形成較小的腦泡與暫時分節。**局部的 organizer／signaling center 釋出訊號，改變相鄰細胞的基因表現，讓不同位置取得不同身分。** 來源：L3，20–23；L4，20、23–25。

1. **前腦一面接受局部誘導，一面限制 Wnt 向前作用**

   前腦下方的 **AVE** 釋出 fibroblast growth factors（FGFs）等訊號，影響前腦及 **anterior neural ridge（ANR）** 的指定。ANR 位於神經管最前緣，繼續提供局部訊號。

   Wnt 可參與較後方的 midbrain 指定。如果這類訊號過度向前延伸，前方組織會朝較後方身分改變。因此，前方的 **Cerberus、secreted Frizzled-related proteins（sFRPs）、Dickkopf（Dkk）** 限制 Wnt：前兩者阻擋 Wnt 與 receptor complex 的作用，Dkk 則作用於 LRP。

   **Xenopus 過量 Dkk 實驗**中，內源 Wnt 被阻擋後，頭與腦區域變大，向原本的 midbrain 區延伸。這把「限制後方化訊號」接到「前方組織範圍擴大」。來源：L4，23–24、27–30。

   Wnt 結合膜上的 Frizzled／LRP 後，經 Dishevelled 抑制 β-catenin 降解，使 **β-catenin 累積、進核，參與目標基因轉錄**。細胞外阻擋 Wnt，便會影響這個細胞內反應。來源：L4，26。

   [[神經發育的共用訊號路徑|Wnt、Notch、TGF-β 與 RA 的細胞內步驟]]

2. **互相抑制的 transcription factors，使區域邊界維持在不同位置**

   **Transcription factor** 是結合 DNA、調節轉錄的蛋白。前腦圖中，Otx2 的範圍由 forebrain 延至 midbrain，Pax6 在 prosomeres p1–p6 表現；Six3 偏前方 p3–p6，Irx3 偏 p1、p2 與更後方。

   **Six3 與 Irx3 互相抑制**，限制彼此的表現範圍。Midbrain–anterior hindbrain border（**MHB**）的 Wnt 增強 Irx3，限制前腦向後擴張；前方 Wnt inhibitors 則限制後方訊號向前延伸。區域大小由兩側的作用共同限制。來源：L4，25、29–30。

   Diencephalon 中的 **zona limitans intrathalamica（ZLI）** 位於 prethalamus 與 thalamus 之間；前腦下方另有 prechordal plate。（待補 by codex：ZLI 與 prechordal plate 分別釋出哪些訊號、作用於哪些組織，以及如何改變區域身分。）來源：L4，23–25。

3. **MHB 的局部訊號能在新位置誘導 midbrain 與 cerebellar tissue**

   Isthmus 的窄縮區表現 **FGF8**；Wnt 初期分布於較大範圍的 midbrain，之後限制在 FGF8 前方。FGF8 促進 Wnt、抑制 r1 的 Hox expression；Wnt 抑制 Otx2 的作用、促進後方 Gbx2，影響交界兩側的區域身分。

   | 改變的條件 | 發育結果 | 支持的關係 |
   |---|---|---|
   | 相近階段的 quail mesencephalon 轉向 180°，移入 chick telencephalon。 | 出現額外且方向相反的 midbrain 與 cerebellar tissue。 | 移入組織能改變局部區域發育。 |
   | 在 posterior forebrain、靠 mesencephalon／p1 邊界處放入 **FGF8-coated bead**。 | 出現異位 midbrain 與 cerebellar-like tissue。 | FGF8 參與這些區域的誘導。 |

   來源：L4，21–22、31–32。

4. **後腦分節後，細胞間排斥限制不同 rhombomeres 混合**

   正常相鄰的奇數、偶數 rhombomeres 保持分界。Chick grafting experiments 把兩個偶數節移到相鄰位置時，細胞可以混合；兩個奇數節也相同。奇偶相鄰時仍分開，顯示混合與否取決於節的性質。

   r3、r5 的 transcription factor **Krox20** 調節 **EphA receptor**。相鄰細胞表面的 ephrin A 與 EphA 結合，受體側產生 forward signaling，ligand 側產生 reverse signaling；雙向訊號限制細胞跨界。

   | 缺少的調控蛋白 | 受影響區域 | 分節結果 |
   |---|---|---|
   | **Krox20** | r3、r5 | r3、r5 未能維持，r2、r4、r6 接在一起，hindbrain 變短。 |
   | **Kreisler** | r5、r6 | r5、r6 融合，後方也未正常繼續分節。 |

   **區域內的基因表現，透過細胞表面的相互作用，影響組織能否保持邊界。** 來源：L4，35–38。

5. **Somites 的 RA 與 FGF／Cdx，使前後區段表現不同 Hox 組合**

   一個 rhombomere 可同時表現多個 Hox genes，組合及表現量構成 **Hox code**。沿 posterior 方向，表現組合逐漸累積；spinal cord 也有相應的前後排列。

   Somites 釋出 **retinoic acid（RA）**，圖中在 hindbrain／spinal cord 交界較高、往前後降低。RA 進入細胞後結合 **retinoic acid receptor（RAR）**，受體作用於 Hox promoter 的 **RA-response element（RARE）**，改變 transcription。

   | 區域 | 局部條件如何改變 | Hox 表現的結果 |
   |---|---|---|
   | **Hindbrain** | r6／r7 的 Cyp26 較低、RA 較高；RA 也抑制 Cdx expression。 | 較高 RA 可誘導 3′ Hox genes，如 Hoxb4。 |
   | **Spinal cord** | FGF 經 Cdx transcription factors 傳遞影響，也影響 RA synthesis；RA 與 Cyp26 的量互相調整。 | Cdx 介導 5′ Hox genes，如 Hoxb9 的表現。 |

   ![不同 rhombomeres 的 Hox 組合與表現量](Neuro%20development/圖片/hox-rhombomeres.png)

   圖中重疊色帶表示同一節的組合；這是 mouse E9.5 的例子。Hox expression 也與 spinal motor columns 的位置對應，其中 **lateral motor column（LMC）** 產生走向 limb bud 的 motor axons。（待補 by codex：Hox 組合如何指定各群 motor neurons。）來源：L4，39–46；L6，38–39。

   [[神經發育對照：早期胚胎、腦泡與區段|腦泡、rhombomeres、Hox 排列與 motor columns 對照]]

### 三、同一段神經管讀取背腹訊號，產生不同前驅區

以下以 caudal central nervous system（**CNS**）／spinal cord 為主。前驅細胞靠 neural canal 排成 **ventricular zone（VZ）**，新神經元由此往外產生。背側的 alar plate 主要產生 sensory interneurons，腹側 basal plate 主要產生 motor neurons 與相關 interneurons。來源：L5／L5V2，5–7。

1. **Notochord 先誘導 floor plate，floor plate 再成為管內的訊號來源**

   | Notochord 的條件 | Floor plate 的變化 | Motor neurons 的變化 |
   |---|---|---|
   | 正常位於 neural tube 腹側。 | 正常形成。 | 在附近形成。 |
   | 移除 notochord。 | 不形成。 | 不形成。 |
   | 移植到 neural tube 側方。 | 側方出現異位 floor plate。 | 在異位 floor plate 兩旁形成。 |

   **Sonic hedgehog（Shh）** 是這段腹側指定的重要訊號。Notochord 提供起始訊號；被誘導的 floor plate 本身再成為誘導 motor neurons 的主要來源。來源：L5／L5V2，8–9。

   在另一組實驗中，表現 Shh 的 **COS cells** 與 neural tube explant 共培養；COS 是來自猴腎組織的 fibroblast-like cell line。直接接觸可誘導 floor plate 與 motor neurons，隔濾膜或分開培養仍可誘導 motor neurons，卻未誘導 floor plate；加入抗 Shh 抗體後，兩種誘導都消失。

   ![Shh-producing COS cells 與 explant 的接觸、隔膜、分離及抗體比較](Neuro%20development/圖片/shh-cos-experiment.png)

   **Shh 可以跨細胞間隙作用，接觸與分離條件卻會得到不同產物。** 訊號可擴散，仍須連同接收條件判斷細胞命運。來源：L5／L5V2，10–12。

2. **Shh 梯度改變 transcription factors，再由互相抑制建立邊界**

   **Patched（PTC）** 是接收 Hedgehog ligand 的膜上受體，原本抑制膜上的 **Smoothened（SMO）**。Ligand 作用於 PTC 後，解除對 SMO 的抑制，使下游 **Gli transcription factors** 偏向活化型 GliA，促進 PTCH1、Gli1 等目標轉錄；沒有 ligand 時，圖中偏向抑制型 GliR，抑制目標轉錄。來源：L5／L5V2，13。

   Shh 靠腹側來源較高，往背側降低。接收細胞依濃度改變兩類因子的表現：

   | 類別 | Shh 的作用 | 例子 |
   |---|---|---|
   | **Class I** | 抑制表現。 | Dbx1、Dbx2、Irx3、Pax6。 |
   | **Class II** | 活化表現。 | Nkx6.2、Nkx6.1、Olig2、Nkx2.2。 |

   相鄰表現區的 **Dbx1／Nkx6.2、Dbx2／Nkx6.1、Irx3／Olig2、Pax6／Nkx2.2** 互相抑制。比如 Irx3 與 Olig2 互相限制，使邊界兩側偏向不同的基因組合，將漸變的訊號轉成較清楚的 progenitor domains。

   由較背側往腹側，**p0、p1、p2、pMN、p3** 分別產生 V0、V1、V2 interneurons、motor neurons、V3 interneurons。p 代表仍在前驅階段的 domain，後一組名稱則是其神經元產物。來源：L5／L5V2，14–15。

   ![背腹前驅區與離開分裂後的神經元 marker 組合](Neuro%20development/圖片/spinal-domain-markers.png)

   p2 還產生 V2a／V2b，dIL 也分 a／b；marker 組合幫助辨認各分支。（待補 by codex：各組 progenitor markers 如何接到相應的神經元分化，尤其 V2a／V2b 與 dIL a／b 的分支。）來源：L1，31；L5／L5V2，23–24。

3. **改變 Shh pathway 刺激強度，能改變分化產物的比例**

   **Induced pluripotent stem cells（iPSCs）** 可在合適條件下分化成 neurons。Human iPSC 實驗用刺激 SMO 的 **purmorphamine（Pur）** 比較 Shh pathway 強度：由 100 nM 提高到 1 μM 時，代表 V2a 的 CHX10-positive 細胞增加，課頁用來辨認 V0 的 LHX5-positive 細胞減少。

   ![Purmorphamine 劑量增加時，兩類 marker-positive 細胞比例往不同方向改變](Neuro%20development/圖片/purmorphamine-dose.png)

   這項比較把**同類起始細胞、不同刺激強度、不同命運比例**接在一起。來源：L2，32–33；L5／L5V2，16。

4. **背側由 epidermal BMP 誘導 roof plate，再區分不同的依賴條件**

   Epidermal ectoderm 的 **BMP4、BMP7** 誘導 roof plate 成為次級訊號來源。Roof plate 再提供 dorsalin-1、BMPs、activin、GDF7，這些屬於 TGF-β superfamily。

   在小鼠中，用 diphtheria toxin gene 取代 roof-plate-specific GDF7，使 roof plate 細胞退化。**Epidermal BMP 仍存在，dI1–dI3 卻不形成；dI4 仍能形成，並向背側擴張。**

   | 背側產物 | 對訊號來源的依賴 |
   |---|---|
   | **Class A：dI1–dI3** | 需要 roof plate 訊號。 |
   | **Class B：dI4–dI6** | 不依賴 roof plate；paraxial mesoderm 的 RA 看來參與其發育，也與 V0／V1 有關。 |

   ![移除 roof plate 而保留外側 BMP 後，背側 interneuron 的產生與分布改變](Neuro%20development/圖片/roof-plate-deletion.png)

   **外側最初的誘導訊號，與被誘導後的管內訊號來源，作用不能完全互換。** 來源：L5／L5V2，17–24。

   這些訊號接到細胞內的 SMAD 分支，再影響轉錄；BMP 的結果也與作用時機有關。背側 BMP／TGF-β 與腹側 Shh 所影響的基因彼此拮抗，細胞身分因而取決於位置、強度與發育階段。[[神經發育的共用訊號路徑|全文|SMAD 與非 SMAD 支路]]可另外展開。來源：L5／L5V2，19–24。

### 四、前驅細胞一面保留來源，一面產生開始分化的後代

1. **分裂後代的去向改變，組織從擴增轉向神經生成**

   **Neural progenitor cells（NPCs）** 是持續供應新細胞的來源。分裂後兩個後代是否仍維持前驅身分，會改變前驅池與新神經元的比例。

   | 階段 | 分裂後的去向 | 組織的變化 |
   |---|---|---|
   | **Expansion phase** | Neuroepithelial cell 對稱分裂，產生兩個 NPC。 | 擴大 progenitor pool，圖中對應 lateral expansion。 |
   | **Neurogenic phase** | Radial glia 不對稱分裂，保留一個 progenitor，另一個後代開始分化。 | 一面保留來源，一面增加 neurons，圖中對應 radial expansion。 |
   | **後續 astrogenic／gliogenic phase** | Radial glia 的產物也包括 astrocytes。 | 神經組織逐漸增加 glial cells。 |

   **Direct neurogenesis** 直接產生 neuron；**indirect neurogenesis** 先產生可繼續增殖的 neuronal progenitor，再由它產生 neurons。

   ![分裂後代由保留前驅轉向產生 neurons 與 glia](Neuro%20development/圖片/neurogenesis-phases.png)

   （待補 by codex：哪些條件促使前驅細胞切換上述分裂與產物策略。）來源：L5／L5V2，28–29。

2. **Delta／Notch 讓相鄰細胞的分化傾向逐漸分開**

   起初相近的 neural progenitors 中，proneural activity 較高的一側增加膜上的 **Delta ligand**。Delta 接觸鄰細胞的 **Notch receptor**，使它被切割並釋出 **Notch intracellular domain（NICD）**；NICD 進入接收細胞的核，改變 Hes／Hey 等目標轉錄，壓低其 proneural program。

   | 同一對相鄰細胞 | Proneural activity 較高的一側 | 收到較多 Notch 訊號的一側 |
   |---|---|---|
   | **送出的 Delta** | 較多，刺激鄰細胞。 | 因 proneural activity 被壓低，Delta 較少。 |
   | **對彼此的影響** | 使鄰細胞較不容易在本輪分化。 | 對另一側的 Notch 刺激較弱，使另一側更能維持 proneural activity。 |
   | **細胞去向** | 較容易形成 neuron。 | 保留為後續神經生成的 progenitor。 |

   ![相鄰細胞透過 Delta／Notch 放大差異，一側分化、一側保留前驅狀態](Neuro%20development/圖片/lateral-inhibition.png)

   這個 **lateral inhibition** 過程將小差異放大，使群體分出本輪 neurons 與保留的 progenitors。[[神經發育的共用訊號路徑|標題|Notch 的膜上切割與核內複合體]]可另外展開。來源：L5／L5V2，30–33。

3. **同一條 Notch pathway，在不同細胞階段接到不同結果**

   Mouse mutant 研究整理的路線圖中，Notch 可維持 multipotent CNS progenitor、neuroblast 或 adult neural stem cell 狀態；進入 neuroblast、early neuronal differentiation 或 adult neurogenesis 的某些轉變則標示 Notch 下調。之後的 neuronal maturation and function 又可需要 Notch。

   **解釋一次命運轉變時，要同時指出起始細胞與發育階段。** Glioblast 的 astrocyte／oligodendrocyte 分支也有不同 Notch 狀態，接在第九節。來源：L5／L5V2，34–35。

### 五、大腦皮質的新神經元往外移，在不同時間加入不同層

1. **從 VZ 移出的細胞，先形成暫時層，再建立 cortical plate**

   皮質發育圖中，靠腦室的 **ventricular／apical surface 在內**，靠表面的 **pial／basal surface 在外**。增殖細胞起初沿腦室排成 VZ。

   - 最早移出的細胞形成 **preplate（PP）**。
   - 後續細胞形成 **cortical plate（CP）**，把 PP 分成外側的 **marginal zone（MZ）** 與 CP 下方的 **subplate（SP）**。
   - 部分 VZ 細胞在旁邊建立第二個增殖區 **subventricular zone（SVZ）**。新 neurons 穿過 SVZ、**intermediate zone（IZ）**、SP，繼續加入 CP。

   ![新細胞移入，使 preplate 分成 marginal zone 與 subplate，並擴大 cortical plate](Neuro%20development/圖片/cortical-temporary-layers.png)

   CP 後來對應 layers II–VI，MZ 對應 layer I，IZ 參與 white matter。**原本的 PP，在新生細胞形成 CP 後被分隔到它的兩側。** 來源：L5／L5V2，37–39；L6，2–3。

2. **遷移需要附著的路徑，終點還需要脫離的訊號**

   | 移動方式 | 細胞先建立什麼連接 | 胞體如何移動 |
   |---|---|---|
   | **較早的 somal translocation** | VZ 細胞伸出達到 pial surface 的長突起，再失去 ventricular attachment。 | 沿自己仍接表面的突起向外移。 |
   | **較後的 glia-guided migration** | Radial glia 胞體留在 VZ，突起跨到 pial；neuron 附在它的支架上。 | Neuron 用 leading process 沿 glia 往外移。 |

   MZ 的 **Cajal–Retzius cells 釋放 Reelin**，使遷移的 neurons 脫離 radial glia、停在 CP，避免進入 MZ。（待補 by codex：neuron 與 radial glia 之間的附著如何被調節，以及 Reelin 如何接到末段脫離。）來源：L5／L5V2，40–45。

3. **後到的 CP 神經元越過先到者，形成 inside-out 層序**

   最早進入 CP 的 neurons 形成 future layer VI；接著的細胞越過 VI 形成 V，再逐漸加入 IV、III、II。新細胞在既有細胞的外側落定，使 CP 往外增加。**Inside-out 描述 CP 的 VI 到 II；layer I 來自先前的 MZ。**

   ![後出生的神經元越過較早生成者，逐步在 cortical plate 外側加入](Neuro%20development/圖片/cortex-inside-out.png)

   | 條件 | 遷移與排列的結果 |
   |---|---|
   | **正常 Reelin** | Neurons 在進入 MZ 前脫離支架，後到者可在先到者外側落定。 |
   | **Reeler mouse 缺少 Reelin** | SP 與 MZ／Cajal–Retzius cells 混成 superplate；早生 future VI 細胞位於最外側能到的位置，後來細胞堆在下方，出現倒置層序。 |

   ![正常與 Reeler 的層序比較：細胞能否在適當位置落定，會改變出生先後與內外位置的關係](Neuro%20development/圖片/reelin-layering.png)

   **出生先後、能否越過既有細胞、何時脫離支架，共同影響最後的層序。** 來源：L5／L5V2，42–45。

4. **人類皮質可在外側前驅區繼續增加細胞來源**

   Human **outer subventricular zone（OSVZ）** 有大量 **outer radial glia（oRG）** 與 intermediate progenitor cells。oRG 有長 basal process，卻不接 ventricular surface。

   Live imaging 與 clonal analysis 顯示，oRG 能做增殖性分裂、自我更新的不對稱分裂，並產生仍可增殖的 neuronal progenitors；抑制 OSVZ progenitors 的 Notch，會誘導 neuronal differentiation。這把「外側區域仍能供應細胞」接到實際分裂與後代去向。

   ![Human OSVZ 與 oRG 提供位於外側的增殖來源](Neuro%20development/圖片/human-org.png)

   GW15 時間序列追蹤 oRG 及後代。（待補 by codex：圖上 0:00–47:34 的時間單位。）來源：L7，10–11。

### 六、小腦細胞從不同來源移出，granule cells 先到表面再往內移

1. **Rhombic lips 向中線接合，形成 cerebellar primordium**

   Caudal metencephalon 的 alar plate 向 dorsomedial 擴張，越過薄的 roof plate 形成 **rhombic lips**；兩側向中線延伸、接合成小腦原基。Upper／rostral rhombic lip 產生 granule cells，lower／caudal rhombic lip 則產生 pons 的不同 nuclei。

   小腦原基中，**VZ 來源細胞先移出，形成 Purkinje cell layer（PCL）**，由初期不規則多列逐漸變成單層。另一群細胞由 rostral rhombic lip 沿表面遷移，在 pial 下形成暫時的 **external granule cell layer（EGL）**。

   ![小腦原基形成後，VZ 與 rhombic lip 的細胞沿不同路徑遷移](Neuro%20development/圖片/cerebellar-primordium.png)

   （待補 by codex：促使 rhombic lips 擴張接合，以及 Purkinje cells 由多列整理為單層的作用。）來源：L5V2，49–50。

2. **EGL 的細胞先增殖，再改變分化與移動狀態**

   | Granule cell 階段 | 所在位置與變化 | 分子特徵 |
   |---|---|---|
   | **Proliferating** | EGL 外排持續增殖；rodents 與 humans 可延續到出生後。 | 較高 Notch receptor expression，有利維持增殖。 |
   | **Premigratory** | EGL 內排開始準備向內遷移。 | **Math1（又名 Atoh1）** 是 transcription factor，表示 granule fate 承諾，並誘導 Zic1／Zic2。 |
   | **Mature** | 越過 PCL，形成 **internal granule cell layer（IGL）**。 | 出現 GABAα6r 等成熟 receptor markers。 |

   FGF、Wnt、BMP、BDNF、Shh 等外來訊號參與這個成熟過程。（待補 by codex：各訊號在何時作用於哪群細胞，如何影響增殖、分化與遷移。）來源：L5V2，51–54；Atoh1／Math1 對應見 L6，17。

3. **Granule cell 改變突起方向，沿 Bergmann glia 穿過既有的 PCL**

   Premigratory granule cell 先伸出與 pial surface 平行的 bipolar processes，再形成朝內的第三個 leading process。胞體與 **Bergmann radial glia** 接觸後，沿支架穿過 **molecular layer（ML）**、PCL，到 IGL 後繼續分化。

   ![Granule cell 在表面伸突起後，沿 Bergmann glia 朝內遷移](Neuro%20development/圖片/bergmann-migration.png)

   **這條 granule cell 路線由 EGL 向內到 IGL；大腦 CP 則由後生細胞加入更外側。** 小腦的 Purkinje cells 有自己的 VZ 來源路線。來源：L5V2，55。

   [[神經組織與感覺器官的成熟構造|小腦完成分層後的細胞位置與其他成熟構造]]

### 七、不同胚胎組織分別形成眼、內耳與周邊感覺結構

**Placode 是 surface ectoderm 的增厚區。** Lens、otic、nasal placodes 及顱感覺 ganglia 相關區域位於頭部表面；neural retina 則從 neural tube 的 diencephalon 延伸出來。來源：L6，13–16、21–24。

1. **Optic vesicle 外凸再內陷，同時誘導表面形成 lens**

   | 發育次序 | 神經來源的部分 | 表面 ectoderm 的反應 |
   |---|---|---|
   | **約 day 24** | Diencephalon 向外突出形成左右 optic vesicles，接近表面。 | 與 optic vesicle 接近的表面區域受到後續誘導。 |
   | **約 day 31** | Optic vesicle 內陷成 optic cup。 | 增厚為 lens placode。 |
   | **約 day 33** | Optic stalk 維持 eye 與 forebrain 的連接。 | Lens placode 內陷，最後分離成 lens vesicle。 |
   | **約 day 35** | Optic cup 內層成 neural retina、外層成 pigment epithelium；optic stalk 後來形成 optic nerve。 | Lens vesicle 形成 lens。 |

   ![神經來源的 optic cup 與表面來源的 lens 在相鄰位置共同發育](Neuro%20development/圖片/optic-cup-development.png)

   **Neural tube 延伸出的 optic vesicle，誘導表面 ectoderm 形成 lens placode；兩者最後形成不同的眼部構造。**（待補 by codex：optic vesicle 誘導 lens placode 的訊號，以及哪些作用造成 optic cup 與 lens 的內陷。）圖中是 human embryo 的 approximately gestation days 24–35。（待補 by codex：日齡的起算方式與臨床產科週數的對應。）來源：L6，21–24。

2. **Retinal progenitors 隨時間改變產物，transcription factors 影響命運分配**

   共同的 **retinal progenitor cell（RPC）population** 產生各種 retinal cells。較早的生成高峰偏向 ganglion、horizontal、cone、amacrine cells；較晚偏向 rod、bipolar、Müller cells，部分物種如 rat 可延續到 early postnatal life。**生成期彼此重疊，先後表示高峰不同。**

   | Mouse genotype | Retinal ganglion cells（RGCs） | Amacrine cells |
   |---|---|---|
   | **Wild type** | 可見 Math5-expressing RGCs。 | 可見 NeuroD／Math3-expressing cells。 |
   | **Math5−/−** | 減少。 | 增加。 |
   | **NeuroD−/−、Math3−/−** | 增加。 | 減少。 |

   缺少不同 transcription factors，會使這兩類細胞的比例往相反方向改變；減少的一類仍有生成。（待補 by codex：RPC 如何隨時間改變可產生的細胞身分，以及這些 transcription factors 如何接到各自的分化程式。）來源：L6，28–31。

3. **眼部也有背腹指定，訊號異常會牽連形態形成**

   Dorsal 的 **BMP4** 促進 Tbx5，再促進 ephrin B1／B2；ventral 的 **Shh** 促進 Vax，再促進 Pax2、EphB2／B3，並抑制 Pax6／Rx。兩側的 Tbx5／Vax 與 ephrin／Eph 模式互相限制。

   ![眼部背腹訊號作用於不同 transcription factors，再影響區域表現](Neuro%20development/圖片/eye-dv-signals.png)

   **Cyclopamine 抑制 SMO**，干擾 Shh pathway。（待補 by codex：Shh／SMO 受抑制如何影響眼原基分隔而導致單眼；形成圖中 DV boundary 的訊號接續。）**Holoprosencephaly（HPE）** 也與 Shh pathway disruption 有關。（待補 by codex：HPE 的結構異常及訊號擾動如何造成這些異常。）來源：L7，3–7。

4. **內耳的相鄰細胞，透過 Atoh1／Notch 分成 hair cell 與 supporting cell**

   Inner ear 來自 **otic placode**。發育中的 cochlear epithelium 有 Sox2-positive 的 **prosensory region**，能產生 hair cells 與 supporting cells。（待補 by codex：otic placode 如何轉變為內耳各部分，以及 cochlear prosensory region 如何建立。）來源：L6，14–18。

   **Atoh1（Math1）** 在這裡促進 hair cell development。沿用前面 lateral inhibition 的細胞間關係，這次被鄰細胞 Notch 訊號壓低的是 Atoh1：

   | 同一對鄰細胞 | 偏向 hair cell | 偏向 supporting cell |
   |---|---|---|
   | **送出的訊號** | Atoh1 增加 Dll1／Jag2，刺激鄰細胞 Notch。 | Atoh1 較低，Dll1／Jag2 較少，對另一側 Notch 刺激較弱。 |
   | **收到訊號後的反應** | 圖中 Notch 未活化，較能維持 Atoh1。 | Notch 釋出 NICD，入核活化 Hes；**Hes 抑制 Atoh1**。 |
   | **其他影響** | Id 較低，允許 Atoh1 持續作用。 | Id 較高，也抑制 Atoh1，減少 Dll1／Jag2。 |
   | **最後的命運傾向** | Hair cell。 | Supporting cell。 |

   ![Atoh1、Dll1／Jag2 與 Notch／Hes 的鄰細胞回饋，使兩側取得不同身分](Neuro%20development/圖片/hair-cell-notch.png)

   **小腦的 Atoh1／Math1 與此處是同一因子，細胞所處的組織與分化過程不同。** 來源：L6，17–18。

5. **Placodes 與 neural crest 參與周邊結構，但各群細胞須分別追蹤**

   顱部 placode-derived 區域包括 trigeminal 的 ophthalmic／maxillo-mandibular 部分、geniculate、vestibulocochlear、petrosal、nodose 等；一個 ganglion 的所有部分未必來自同一個 placode。

   ![顱部 placodes 與部分 placode-derived sensory ganglion 區域](Neuro%20development/圖片/cranial-placodes.png)

   **Neural crest** 位於 neural tube 背側及周圍，也形成部分 **peripheral nervous system（PNS）** 結構。（待補 by codex：neural crest 如何離開 neural tube、沿哪些路徑遷移，以及各群細胞與 PNS 產物的對應。）來源：L3，18–19；L6，13。

   [[神經組織與感覺器官的成熟構造|感覺輸入、內耳與 retina 的成熟排列及功能]]

### 八、Axon 的生長端持續改變形狀，沿路接收導引訊號

1. **Growth cone 更新細胞骨架，將接觸到的環境接到突起生長**

   **Growth cone** 位於神經突起的生長末端。Microtubules 從 axon shaft 伸入中央區，部分繼續伸向遠端；網狀 F-actin 形成 **lamellipodium**，actin bundles 再向外形成 **filopodia**，接觸周圍 substrate。

   Filopodium 的 actin subunits 在 leading edge 加入、在 proximal end 脫離，形成 **treadmilling**。細胞骨架持續更新，使生長端能改變形狀；substrate receptors、linking proteins、myosin II 把接觸面與骨架相連。

   ![Growth cone 以 filopodia 接觸環境，內部骨架持續更新](Neuro%20development/圖片/growth-cone.png)

   （待補 by codex：不同吸引或排斥訊號如何改變局部骨架活動，使 growth cone 轉向。）來源：L6，34–37。

2. **Limb bud 路線依序經歷聚束、背腹選路與肌肉表面分枝**

   LMC 的 motor axons 起初合成一束，接近 limb bud 後才在 choice point 分開。**NCAM 參與黏附，polysialic acid（PSA）修飾改變 axons 彼此黏附的程度。**

   | 路段 | 當地條件與作用 | Axon 的變化 |
   |---|---|---|
   | **接近 limb bud 的近端** | L1、低 PSA 的 NCAM 促進 axons 彼此黏附。 | 維持同一束，稱 **fasciculation**。 |
   | **Limb bud 的分岔處** | Ventral limb bud 的 ephrin A（圖標 ephrin A5）排斥具有 EphA receptor 的 axons。 | EphA-positive axons 避開 ventral、走向 dorsal；圖中 lateral LMC 走 dorsal，medial LMC 走 ventral。 |
   | **接近 extensor muscle／myotubes** | NCAM 參與 axon 與肌肉接觸；較高 PSA 干擾相鄰 axons 的 NCAM homophilic binding。 | 聚束減少，在肌肉表面分枝。 |

   ![Axons 由近端聚束，到 limb bud 選路，再於肌肉表面解束分枝](Neuro%20development/圖片/lmc-axon-guidance.png)

   **同一黏附分子，在不同修飾條件下，可配合不同路段的需要。** 前面的 rhombomeres 用 Eph／ephrin 排斥限制細胞跨界；此處接收排斥的是延伸中的 axon，結果表現在選路。來源：L4，37–38；L6，38–39。

3. **跨過中線後的排斥，限制 axons 反覆跨越**

   Drosophila 的例子中，中線 **Slit** 作用於 axon 的 **Robo（roundabout）receptors**。Contralateral projection 走向對側，圖中表現 Robo1；ipsilateral projection 留在同側，圖中表現 Robo1、Robo2。

   | 條件 | 路線如何改變 |
   |---|---|
   | **Wild type** | Contralateral axon 跨一次後走向對側，ipsilateral axon 留在同側。 |
   | **robo mutant** | Commissural axons 反覆穿越 transverse commissure，與 slit mutant 類似。 |
   | **robo1、robo2 都缺少** | 同側投射靠向中線並 collapse。 |

   ![正常與 robo mutant 的 axon 路線比較](Neuro%20development/圖片/slit-robo.png)

   **Slit／Robo 排斥參與維持不同投射路線。**（待補 by codex：commissural axon 在第一次跨越前後，如何調整對 Slit 的反應，才能先跨越、之後再受排斥。）來源：L6，40–41。

   （待補 by codex：axon 接近目標後，如何建立與成熟 synapses，以及連接如何在後續發育中調整。）

### 九、神經組織繼續增加 glia，外圍血管也向內長入

1. **前驅細胞的後代逐漸包括 glia，產物與階段及局部譜系有關**

   第四節的 radial glia 到後期可產生 astrocytes。Notch 路線圖中，multipotent CNS progenitor 可進入 glioblast 分支；glioblast 走向 astrocytes 的路線標示 Notch，走向 oligodendrocytes 的路線標示 Off。這些關係須連同當時的細胞狀態判讀。來源：L5／L5V2，28、34–35。

   Human late second trimester 的 neocortex 圖中，**tripotential intermediate progenitor cells（Tri-IPCs）** 可局部產生不同後代：

   | 分支 | 中間細胞與後代 |
   |---|---|
   | **GABAergic neurons** | 經 IPC-IN 產生局部 interneurons。 |
   | **Oligodendrocytes** | 經 **oligodendrocyte precursor cell（OPC）**，再到 oligodendrocyte。 |
   | **Astrocytes** | 產生 protoplasmic 與 fibrous astrocytes。 |

   ![Human late second trimester 的局部 Tri-IPC 譜系與其他前驅路線](Neuro%20development/圖片/human-tri-ipc.png)

   同圖另有 IPC-EN 到 EN，以及 radial glia 到 ependymal cell 的路線；Tri-IPC 是其中一群局部來源。（待補 by codex：IPC-EN／EN 的全名與細胞身分；圖中 radial glia 到 fibrous astrocyte 的虛線所代表的關係與證據程度。）來源：L7，12。

   **Oligodendrocyte 與 Schwann cell 分別在 CNS、PNS 包裹 axons；satellite cell 環繞 PNS neuron cell bodies。**（待補 by codex：microglia、Schwann cell、satellite cell 的發育來源，以及 oligodendrocyte／Schwann cell 如何形成與成熟髓鞘。）來源：L2，47–48。

2. **Mesodermal angioblasts 先在管外聚集，再由外圍血管叢向內萌芽**

   **Mesodermal angioblasts** 被招募到鄰近 NPCs 的區域，在 neural tube 外圍形成 **perineural vascular plexus（PNVP）**。Vascular sprouts 再由 PNVP 長入 neural tube，逐漸增加分枝。

   ![Angioblasts 在 neural tube 外形成 PNVP，再萌芽長入管壁](Neuro%20development/圖片/neural-vascularization.png)

   圖中分別以 E8.5–E12.5、E9.5–E18.5 標示時序；另一組較長序列延續到 postnatal，呈現神經元、glia 與血管逐漸多樣化。（待補 by codex：兩組胚胎時序圖的物種；招募 angioblasts 的 ligand／receptor，以及 NPCs 與血管萌芽之間的訊號。）來源：L7，13–14。

### 研究方法與模型

上面的擾動、移植與細胞追蹤，用來判斷特定發育關係。染色、qPCR、電生理、動物模型、行為試驗與體外模型的原理和用途，可另外展開。

[[神經發育的研究方法]]

## 來源

本地 `3_Lecture Slides` 八份投影片；頁碼包含隱藏頁。背景模組沿用相同代號，必要但尚缺的連接以「待補 by codex」留在所屬位置。

| 代號 | 投影片 | 總頁數 |
|---|---|---:|
| L1 | 1. Course Overview.pptx | 46 |
| L2 | 2. Neural Development Overview.pptx | 60 |
| L3 | 3. Embryogenesis and Hands on Activity.pptx | 29 |
| L4 | 4. AP and DV Patterning.pptx | 49 |
| L5 | 5. DV Patterning and Cell Fate.pptx | 50 |
| L5V2 | 5. DV Patterning and Cell Fate_V2.pptx | 60 |
| L6 | 6. Neurodevelopment_PNS and Axon Guidance.pptx | 45 |
| L7 | 7. Rapid Fire.pptx | 15 |

L5 的 1–45 與 L5V2 的 1–45 相同，L5 的 46–50 對應 L5V2 的 56–60；L5V2 的 46–55 另有小腦內容。
