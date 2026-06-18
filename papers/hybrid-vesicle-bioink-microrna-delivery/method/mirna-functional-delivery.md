# miRNA 對多種細胞的功能性遞送與選擇性測試

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): miRNA 對多種細胞的功能性遞送與選擇性測試
3. Method: 
   為了證明 hELs 真的能完成「進細胞 → 找到目標 → 關掉它」整條功能性遞送，作者用一段人工小 RNA (miRNA mimic) 當示範訊號——它的序列剛好能貼上管家基因 GAPDH 的 mRNA 尾巴調控區 (3′-UTR)，把這條 mRNA 鎖住或催它分解。GAPDH 不是治療目標，是因為它在幾乎每種細胞都大量穩定表現，可以當乾淨的訊號讀數。流程是：把 miRNA-GAPDH (100 nM) 包進 NVs (100 µg ml⁻¹)、與細胞共培育、抽 RNA、做反向轉錄定量 PCR (RT-qPCR)——TRIzol 抽 total RNA、QuantiTect Kit 逆轉錄成 cDNA、Rotor-Gene SYBR Green 跑 qPCR，量每個樣本訊號超過閾值需要幾個循環 (Ct 值)。最後用 2^(−ΔΔCt) 換算成「相對於對照組是幾倍」的相對表現量；同時用另一個管家基因 β-actin 當內參，校正「這次抽 RNA 抽得多寡」的技術差異。

   光測 CFs 只能證明 hELs 進得了 CFs，分不出「它只認 CFs」還是「它什麼細胞都認」。作者把同一批 NVs 同時餵給四種細胞做特異性比較：CFs（EVs 的母細胞）、CMs（心肌細胞）、HUVECs（人臍靜脈內皮細胞）、C2C12（小鼠肌母細胞）。背後的分子機制是這樣的——CF 自己分泌 EVs 時會把膜上的「身份蛋白」(纖維母細胞特有的辨識分子) 一起帶走，這些分子像鑰匙，只認 CF 自己膜上對應的鎖。hELs 因為融合保留了這些 EV 表面辨識分子，所以也只認 CF；CMs、HUVECs 細胞膜上沒有配對的鎖，hELs 就進不去。實驗結果完全符合預期：CFs 中 miRNA GAPDH-EVs 下調 GAPDH 至 ~0.3、hELs ~0.4、Lip ~0.5；但在 CMs 中只有 Lip (~0.7) 顯著下調，EVs 和 hELs 沒效；HUVECs 也是只有 Lip 有效；只有 C2C12 是四組都有效（推測膜本身就比較容易讓 RNA 滲透）。

   這套實驗有兩個容易被忽略但很關鍵的設計。第一是轉染期分兩段培養基：前 4 h 用「無抗生素培養基」讓細胞用力吞 NVs，因為 penicillin-streptomycin 會干擾內吞 (endocytosis) 路徑、降低攝取效率；4 h 後 NVs 該進的都進去了，再換回含抗生素 + 血清的完整培養基培養 24 h，給細胞時間執行 knockdown，同時抗生素回來保護培養液。第二是內參基因換成 β-actin 而不用 GAPDH：GAPDH 自己就是被打的目標，如果拿它當內參等於「自打自的」，比值永遠是 1，再強的 knockdown 也看不出來；β-actin 是另一個不受 miRNA GAPDH 影響的管家基因，可以乾淨地校正每個樣本的 RNA 投入量差異。

   Lip 作為「沒有 EV 表面辨識分子但其他物理性質類似」的對照組不能省。如果只測 EVs 和 hELs，就算它們只在 CFs 把 GAPDH 打下來，仍會被質疑「會不會只是 CFs 比較容易吞 NV，跟 EV 表面分子無關」。Lip 跟 EVs/hELs 大小、電位類似但缺乏辨識分子；實驗證實 Lip 對四種細胞都一律有效，正好說明「同樣物理性質下，差別來自有沒有 EV 元件」，把 EVs/hELs 的特異性歸因穩穩釘在分子辨識而不是物理偏好。影像端用共軛焦顯微鏡 (ZEISS LSM 880 Airyscan) 看 DY547-miRNA（紅色）疊在 DAPI（藍色）細胞核周圍——紅色訊號圍著細胞核分布，代表 miRNA 真的到了細胞質，不是黏在膜外。
4. 工具與材料: 
   - **miRNA mimic**: 化學合成的人工小 RNA，模擬細胞內生 miRNA 的雙股結構與序列，能進入細胞質後執行相同的基因壓抑功能。
   - **3′-UTR**: mRNA 尾巴上不被翻譯成蛋白、但帶有 miRNA 結合位點的調控區，是 miRNA 鎖定目標的「停車位」。
   - **GAPDH**: 幾乎所有細胞都大量穩定表現的管家基因，本研究借它當乾淨的 knockdown 讀數，不是治療標的。
   - **RT-qPCR**: 反向轉錄定量 PCR：把 mRNA 逆轉錄成 cDNA 後做即時 qPCR，量化 mRNA 表現量。
   - **TRIzol**: Thermo Fisher 的單相試劑，把細胞溶解後用相分離抽出 total RNA。
   - **QuantiTect Reverse Transcription Kit**: Qiagen 出的逆轉錄試劑套組，把 RNA 變成穩定的 cDNA。
   - **Rotor-Gene SYBR Green PCR Kit**: Qiagen 出的 qPCR 試劑，用 SYBR Green 螢光染料隨擴增量增加而發光、量 Ct 值。
   - **Ct 值**: qPCR 訊號超過閾值所需的循環數；mRNA 越多 Ct 越小。
   - **2^(−ΔΔCt) 法**: 以內參與對照組為基準的相對量化公式，輸出「目標 mRNA 相對於對照組是幾倍」的數字。
   - **β-actin**: 另一個管家基因，本實驗當內參用，校正每個樣本 RNA 投入量的技術差異，避免用 GAPDH 自己當內參導致比值恆為 1。
   - **DY547-miRNA**: 把紅色螢光染料 DY547 接在 miRNA mimic 上的版本，用來直接看到 miRNA 在細胞裡的位置。
   - **F-actin / Alexa Fluor 594**: 綠色/紅色細胞骨架染色，標出細胞外形供影像疊圖。
   - **anti-cTnI**: 抗心肌肌鈣蛋白 I 抗體 (Abcam ab19615)，染心肌細胞 (CMs) 用以與 CFs 區分。
   - **ZEISS LSM 880 Airyscan**: 共軛焦螢光顯微鏡，加 Airyscan 偵測器後解析度與訊噪比更好，用來看 miRNA 與細胞核的相對位置。
   - **endocytosis**: 細胞用膜把外部東西包起來吞進細胞質的攝取路徑；本實驗轉染前 4 h 拿掉抗生素是怕 penicillin 干擾這條路徑。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了證明融合做出來的 hELs 真的繼承了 CF-EVs 對心臟纖維母細胞的天然親和力，採用了 miRNA-GAPDH knockdown + RT-qPCR 的功能性遞送測試。這套方法解決了單靠膜染料、無法分辨「真的影響細胞行為」與「只是進去過」的瓶頸，把上游做好的三種 NVs 變成可比較的「對四種細胞各有多少 knockdown 效力」數字，作為下游 GelMA-hELs bioink 是否能在 3D 構造中精準調控細胞基因的關鍵前提。
