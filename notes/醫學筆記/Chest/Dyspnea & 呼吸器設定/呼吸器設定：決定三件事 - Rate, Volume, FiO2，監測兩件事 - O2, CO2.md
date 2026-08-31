# 呼吸器設定：決定三件事 - Rate, Volume, FiO2，監測兩件事 - O2, CO2

## 內文
- 注意：畫線 + 粗體

  代表重要、常用、需要會調的參數

### 決定三件事：Rate, Volume, FiO2

**Rate:**

1. Control mode: 按照要求規律給，一分鐘xxx次。適用於完全paralysis的病人
2. Assisted mode: 設定 Flow trigger，病人有呼吸再給
3. IMV mode(Intermittent Mandatory Ventilation): 最棒，病人有呼吸就給(設定**<u>Flow/Pressure trigger</u>**)，如果沒呼吸至少一分鐘給xxx次(**<u>Rate</u>**)當Back-up。適用於有一點自主呼吸能力的病人
4. **<u>I-time</u>**: 給予 inspiratory volume OR pressure 的時間，即為吸氣時間，通常設定 0.9s
   1. 如果呼吸太快，此時就有可能 E-time 比 I-time 快(E-time + I-time 即為一次呼吸所需時間，與Rate成反比)，稱為 I/E reverse，會肺氣腫
   2. 調整 I/E ratio: I-time 調高可以增加 O2, E-time 調高可以增加 CO2 wash out，通常ratio 1:2，COPD/Asthma 病患會調成 1:3~1:4

**Volume: 希望維持 Tidal volume(ml) = Predicted Body Weight(kg) \* 6**

1. Volume control: 直接決定給予的 <u>tidal volume(不常用)</u>(不常用的原因：1)因為有些 lung complicance 差的病人打固定體積肺泡會破；2)病人有時候會有翻身、咳嗽等行為，這時還給固定體積會造成麻煩)
2. Pressure control: 安全、常用。設定 **<u>peak inspiratory pressure(IP，吸氣正壓</u>**，即為 = IPAP-EPAP（EPAP即為PEEP）**<u>)</u>**，再監測實際tidal volume情形做調整。IP 與 tidal volume 完全正相關 (tidal volume = IP \* lung compliance)
3. Pressure protection: 若病人lung compliance差，使用 Volume Control Mode 可能因 Pressure 過大而導致lung受傷，因此使用Pressure control。通常設定 IP+PEEP < 30。其實也可以設定 Volume protection 只是不常用。
4. **<u>PEEP</u>**: 給予穩定正壓，促進氧氣交換 & 降低初始吸氣阻力

**<u>FiO2</u>:** 氧佔給氣的比例，空氣為21%，超過 60% 怕Toxic

### 監測兩件事：O2, CO2

O2: 監測 **<u>SpO2</u>**。**與 PEEP、FiO2、I-time 相關**。

- 由於氧氣交換仰賴的是平均呼吸道壓力(Paw, airway)與微血管中氧分壓的差，而IP只有吸氣時才會發揮作用 vs PEEP一直都在( <u>Paw = IP\*(I-time)/(E-time+I-time) + PEEP</u> )，因此O2與PEEP 相關而不是 IP
- PEEP & FiO2 兩個都影響氧氣，因此不能只調一個但不動另一個，要同步往上調 (Google 搜尋：PEEP FiO2 table)

CO2: 監測 EtCO2、ABG/**<u>VBG</u>**。**與VE**(每分鐘通氣量，minute ventilation，正比於 **IP** = IPAP-EPAP )、**E-time 有關**。**VE = Rate \* Tidal Volume**。

1. VE高通常代表病人本身的 CO2 washout demand 高，可能 underlying 有sepsis / ischemia 在產酸
2. EtCO2(End tidal CO2): 插管才準

**詳細可以看這裡 ⇒**

[兒童呼吸器使用的基本原則.pdf](../兒童呼吸器使用的基本原則.pdf)
