# US-ink 配方化（alginate、PEGDA、conductive、GelCA 四種 US-ink）

1. 引用自哪篇 paper: deep-tissue-sound-printing
2. Outline (任務主線): US-ink 配方化（alginate、PEGDA、conductive、GelCA 四種 US-ink）
3. Method: 
   作者的關鍵洞察是：FUS 觸發 LTSL 開孔跟「交聯劑是哪種化學」無關，所以只要把不同交聯劑塞進同一款 LTSL、再配上能被該交聯劑黏起來的 prepolymer，就能用同一台 FUS 硬體做出三種完全不同化學機制的水膠。第一種 Alginate US-ink (2.5 wt% sodium alginate + 50 wt% Ca²⁺-LTSL) 走離子交聯：海藻酸鈉長糖鏈上很多 −COO⁻ 群，Ca²⁺ 一靠近會被兩條鏈上的 −COO⁻ 同時夾住，像雞蛋被左右紙盒扣住的「egg-box」結構，把鏈點點扣成 3D 網路。第二種 PEGDA US-ink (35 wt% PEGDA + 12% TEMED-LTSL + 0.5 wt% APS) 走自由基聚合：APS 是自由基啟動劑、TEMED 是還原催化劑，兩者一見面就釋出自由基、把 PEGDA 末端雙鍵 (acrylate) 連鎖打開串成長鏈。第三種 GelCA US-ink (20 wt% GelCA + 20% NaIO₄-LTSL) 走氧化偶聯：GelCA 是把咖啡酸的鄰苯二酚 (catechol) 接到明膠主鏈做出的蛋白 (protocol 採自 Montazerian et al. 2023 Cell Rep. Phys. Sci.：caffeic acid 經 EDC/NHS 活化後與 gelatin 反應 24 小時、再透析三天冷凍乾燥)，NaIO₄ 從 LTSL 釋出後把 catechol 氧化成 quinone，鏈與鏈互相縫起來，同時跟組織表面胺基反應產生黏附力。
   
   第四種 Conductive US-ink (alginate 2.5 wt% + 5 wt% 碳奈米管 CNT + 50 wt% Ca²⁺-LTSL) 是在 alginate US-ink 基礎上塞進導電添加物。CNT 是奈米尺度的中空黑色細管，混進 alginate 後一方面增加超音波被吸收成熱的比例 (acoustic absorption)，同樣功率下焦點處比較熱、達 41.7 °C 範圍稍微擴大，線寬比沒加 CNT 稍寬一點；另一方面 CNT 之間互相搭成連通電路 (percolation network)，電子順著管子跳，導電度比純離子導電的 alginate 高近 10 倍；再加 0.5 wt% 銀奈米線 (AgNW) 把 CNT 之間還沒接上的空隙橋起來，導電度可再多 10 倍 (MXene 製備引用 Song et al. 2023 Sci. Adv.)。可注射性靠的是「剪切變稀 (shear-thinning)」流體特性：alginate 是長鏈高分子，靜止時鏈與鏈彼此纏繞黏度高，LTSL 不會沉到底；推進針頭時鏈被高剪切拉直、鏈間滑動阻力驟降，黏度突然變小輕鬆擠出；一出針頭剪切消失，鏈又自動纏回去恢復原黏度，墨水乖乖停在注射點不流走。
   
   為什麼 alginate 用 50 wt% LTSL、PEGDA 用 12%、GelCA 用 20%？三個數字都是「夠用」與「不過量」的折衷，靠流變儀 (Anton Paar MCR 302, 8 mm 平行板、0.5 mm gap, strain 10%、1 Hz) 量儲存模量 G′ 與損耗模量 G′′ 的交點 (gelation time) 來定。Alginate 需要的 Ca²⁺ 量大、50 wt% 是上限——再高，囊泡彼此擠太緊、膜邊界互相干擾微微滲漏，37 °C 放 1 小時 G′ 就會自相黏結提前膠化，打進身體還沒到 FUS 焦點就堵在注射道。PEGDA 的自由基鏈式反應只需要「火苗」TEMED，12% 就足夠在 43 °C 啟動。GelCA 走 catechol 對一氧化交聯，20% NaIO₄-LTSL 剛好夠用、37 °C 又不會自燒。整罐 alginate US-ink 放在 4 °C 能保存 ≥ 450 天，因為 4 °C 遠低於 LTSL 相變溫度，膜處於最緊密的固態幾乎不漏，alginate 與 CNT/AgNW 在低溫水中又不會自己降解。LTSL 對 PEGDA ink 來說更是「化學上不可缺」：TEMED 一遇上 APS 就立刻生成自由基、PEGDA 整罐當場膠化，若不把 TEMED 鎖在 LTSL 與 APS 物理隔離，根本無法注射；同樣邏輯也適用於 alginate 與 GelCA，把 Ca²⁺ 或 NaIO₄ 鎖進 LTSL 才能避開「預混合就膠化」與「游離交聯劑沿路毒到組織」這兩個老問題。
4. 工具與材料: 
   - **Sodium alginate**：海藻酸鈉，長糖鏈上多 −COO⁻ 群；遇 Ca²⁺ 形成 egg-box 離子交聯水膠。
   - **PEGDA**：聚乙二醇雙丙烯酸酯，兩端 acrylate 雙鍵，可被自由基鏈式打開連成 3D 網路。
   - **APS (ammonium persulfate)**：自由基啟動劑，分子內 S–O 鍵在 TEMED 還原下產生自由基，引發 PEGDA 聚合。
   - **TEMED**：還原催化劑，與 APS 配對快速釋出自由基；被鎖進 LTSL 以避免 PEGDA 預膠化。
   - **GelCA (gelatin-catechol conjugate)**：把咖啡酸的鄰苯二酚共價接到明膠主鏈的蛋白，遇 NaIO₄ 氧化後鏈間互相偶聯並黏住組織。
   - **CNT (carbon nanotube)**：奈米中空細管，5 wt% 加入 alginate 提供電子導電與額外的超音波吸收。
   - **AgNW (silver nanowire)**：銀奈米線，0.5 wt% 加入做為 CNT 連通電路的補橋，導電度再提升 10 倍。
   - **MXene**：二維過渡金屬碳氮化物薄片，可作為替代 conductive additive (製備引用 Song et al. 2023)。
   - **Egg-box structure**：Ca²⁺ 把兩條 alginate 鏈上的 −COO⁻ 同時夾住形成的二維離子交聯點。
   - **Shear-thinning**：黏度隨剪切上升而下降的流體特性，使高黏 US-ink 仍能順利被擠出針頭。
   - **G′ / G′′ (storage / loss modulus)**：流變儀量到的彈性與黏性模量，兩者交點定義 gelation time。
   - **Gelation time**：G′ 跨過 G′′ 的時間點，作為膠化是否真正發生的客觀指標。
5. 與此篇文章的關係: 
   在《Imaging-guided deep tissue in vivo sound printing》這篇文章中，作者為了打造一個「可注射、長保存、FUS 觸發即膠化」的通用 ink 平台，採用 US-ink 配方化策略把 LTSL 與 alginate / PEGDA / GelCA / 導電添加物分別組合成四種墨水。它解決了「不同交聯化學需要不同硬體」與「TEMED、Ca²⁺ 等試劑無法在 prepolymer 裡共存」兩大限制，把流變學優化過的配方產出 alginate、PEGDA、conductive、GelCA 四種 ink，直接交給下游的 FUS 列印硬體。
