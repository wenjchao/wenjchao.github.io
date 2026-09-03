# 人類遺體神經節連續解剖與 DNA/單核萃取

1. 引用自哪篇 paper: developmental-organization-sensory-sympathetic-ganglia
2. Outline (任務主線): 人類遺體神經節連續解剖與 DNA/單核萃取
3. Method:

作者鎖定三位生前神經功能正常的老年捐贈者 (neurotypical adult donor)：ID06 (70 歲男, PMI 13 h)、ID07 (85 歲男, PMI 11 h)、ID08 (74 歲女, PMI 6 h)。他們把脊椎兩側每一節的 DRG 和 SG 都當成獨立樣本取下——一人身上就有 24 對 DRG 加 24 對 SG，三人合計共 94 顆 DRG 加 93 顆 SG，覆蓋從頸段一路到腰段全脊椎軸。為什麼一定要挑神經典型？因為若 donor 生前有帕金森、失智這類疾病，某個 clone 可能因病理性增生而異常放大，會污染後面 MV 頻率的分佈。同時左右都取，是為了讓「感覺 vs 交感」和「左 vs 右」兩件分家事件有內建對照可比。

解剖流程本身像拆一棟大樓：由 anatomical pathologist 先做脊椎骨後緣切除 (laminectomy) 把整條脊髓連同兩側神經節整段取出，接著在乾冰上一節一節分成單顆 DRG 或 SG。為什麼要整段取出再拆？因為 DRG 與 SG 沿脊髓排成有序陣列，整段取出才能保證「編號 T3-DRG 真的是 T3-DRG」，不會混淆節段。每顆神經節取下後立刻放進乾冰盒瞬間降溫 (snap-freezing)、再轉 -80 °C 保存。急凍到 -78 °C 以下時，酵素分子運動幾乎凍結，反應速率降到室溫的百萬分之一；同時水直接固化成細小晶體、不會形成大冰晶把細胞膜和 DNA 分子刺破——酵素攻擊和機械破壞一次關掉。任何延誤 snap-freezing 的神經節，DNA 會被酵素咬成短片段、MV 呼叫器會把 sequencer artifact 當真變異、snRNA-seq 建庫抓到的基因數也不足以分型，整顆就等於廢掉。

只取神經節夠嗎？其實不夠。作者額外用 8 mm 打洞器 (skin punch biopsy) 取了前額葉、小腦、雙側腎、雙側心壁、肝的小塊組織作為對照。因為 DRG 和 SG 都來自神經脊，一個 MV 若只出現在神經節，就可能是「NC 分家後才產生」；但如果它同時出現在腦、腎、心、肝，就代表更早在受精卵初期就已散佈全身。少了這些非 NC 對照組織，同一個 MV 的兩種發育時間點無法區分，整套「用 MV 反推 NC 分家時間」的邏輯就會坍塌。

每顆神經節取下後先被對半切：一半留作單顆細胞核篩選 (FACS single-nucleus sorting) 給後續 snRNA-seq 與 ResolveOME 用；另一半用手持研磨杵 (Kimble Pellet Pestle Motor) 壓碎成漿，倒入保護核酸的裂解液 (Qiagen RLT buffer) 讓細胞完全破裂但 DNA 不會被酵素咬掉。最後把這鍋懸浮液倒進 Qiagen DNeasy Blood & Tissue kit——套組內含矽膠管柱，DNA 會黏在矽膠上、雜質被洗掉，最後用洗脫液把純化 DNA 收下來。這條 DNA 就是後續 300× WGS 與 AmpliSeq MPAS 的原料。

4. 工具與材料:

- **Neurotypical adult donor**: 生前沒有神經退化或增生性疾病診斷的老年捐贈者，避免病理性 clone 污染 MV 頻率分佈。
- **Post-mortem interval (PMI)**: 從死亡到組織冷凍的時間；DNA 較耐、RNA 較敏感，本研究 PMI 6–13 h。
- **Laminectomy**: 把脊椎後緣椎弓一節節鋸開，讓整段脊髓與兩側神經節能整體取出以保節段編號正確。
- **Snap-freezing**: 以乾冰或液氮在數秒內把組織降到零下數十度，同時關掉酵素活性與冰晶形成兩種破壞。
- **8 mm skin punch biopsy**: 用打洞器從腦、腎、心、肝等非-NC 組織取小塊做對照，區分 MV 屬於 NC 譜系或更早的 body-wide 事件。
- **Pellet Pestle Motor**: 手持研磨杵 (Kimble 749540-0000)，把冷凍的神經節組織壓碎成漿以便後續萃取。
- **RLT buffer**: Qiagen 提供的核酸保護裂解液 (40724)，讓細胞破裂但 DNA/RNA 不被酵素咬掉。
- **DNeasy Blood & Tissue kit**: Qiagen 矽膠管柱套組 (69506)，把 DNA 吸附在矽膠上、洗掉雜質後洗脫回收，供 WGS 與 MPAS 使用。
- **FACS single-nucleus sorting**: 以流式細胞儀把 DAPI 染色後的單顆細胞核逐個分揀，作為 snRNA-seq 與 ResolveOME 的輸入。

5. 與此篇文章的關係:

在《Developmental organization of sensory and sympathetic ganglia》這篇文章中，作者為了用天然體細胞 MV 當條碼反推人類 NC 命運分家時間，採用了「全脊椎軸連續解剖 + 極短 PMI 內 snap-freezing + 非-NC 組織對照」的樣本學設計。它解決了「無法直接觀察人類胚胎」與「跨數十顆神經節必須逐顆保留節段編號、且核酸品質不能崩解」兩個瓶頸，為下游 300× WGS、AmpliSeq MPAS、snRNA-seq 與 ResolveOME 提供了統一的 187 顆神經節 + 對照器官樣本庫。
