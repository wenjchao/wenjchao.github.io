# 反應離子蝕刻與 GaAs 犧牲層的選擇性溼蝕刻

1. 引用自哪篇 paper: ultrasmall-dielectric-plasmonic-nanolasers
2. Outline (任務主線): 反應離子蝕刻與 GaAs 犧牲層的選擇性溼蝕刻
3. Method:
這個子項在做的事，是把已縮到目標直徑的 SU8 圓柱陣列，用「電漿+液」兩把刀先垂直雕出 III-V mesa、再選擇性把下方 GaAs 溶掉，做出 disk-on-pillar 或自由粒子。第一步「垂直雕刻 (RIE)」：把晶圓送進 SAMCO 200iP 或 230iP 反應離子蝕刻機 (RIE)，通入 BCl₃ 與 Ar 混合氣體。一般泡在酸液的化學蝕刻是等向的，會把柱子邊緣咬圓；RIE 反過來走「兩手抓」——射頻電場把 BCl₃-Ar 電離成電漿，同時直流偏壓讓正離子垂直往下衝，於是同時提供「化學反應」（Cl 自由基跟 In、Ga、Al 反應形成揮發性 InCl₃、GaCl₃、AlCl₃ 逸散）與「物理轟擊」（Ar 離子動能敲斷表面鍵、把副產物拍走），最終「只往下咬、不往兩邊擴散」，能複製 SU8 圖案得到近乎垂直的側壁，直到底部 GaAs 犧牲層。第二步「去光阻」：先用 CF₄-O₂ 電漿把大部分 SU8 吹掉，再泡稀硫酸把殘餘碳化物徹底洗乾淨。第三步「選擇性溼蝕刻」：把晶圓浸入稀 piranha 溶液（$\mathrm{H}_2\mathrm{SO}_4 : \mathrm{H}_2\mathrm{O}_2 : \mathrm{H}_2\mathrm{O} = 1 : 1 : 100$）。這種配方會咬 GaAs 但幾乎不動 InGaP/InGaAlP/InGaAsP——機制是 H₂O₂ 把 GaAs 表面氧化成 Ga₂O₃ 與 As₂O₃，硫酸再把氧化物溶掉，露出新 GaAs 面再重複；InGaP 因 P 鍵能強、不易生成可溶氧化物，同樣的酸液幾乎不咬，這就是「選擇性 (selectivity)」的來源。第四步「時間控制」：短時間浸泡 → 只咬掉盤下方一段 GaAs，盤懸掛在細柱上形成「disk-on-pillar」（Fig. 1c-iv、Fig. S2）；長時間浸泡 → 整段 GaAs 咬穿，盤直接落進酸液成自由粒子。disk-on-pillar 用於基礎特性量測（Q、閾值、線寬），自由粒子用於後續 silica 包覆進細胞——控時就是切換這兩種形態的旋鈕。

為什麼作者放棄 Oxford 的 CH₄-H₂-Cl₂ 而選 SAMCO 的 BCl₃-Ar？兩者形貌對比在 Fig. S9 一目了然。CH₄-H₂-Cl₂ 裡的甲烷會在蝕刻過程中生成含碳氫聚合物副產物 (CxHy) 沉積在側壁，這些聚合物一方面鈍化保護，一方面若沉積不均就會在側壁留下起伏或黑條（Fig. S9a）；被複製到 disk 邊緣後，每一個突起就是 WGM 光路的散射點，Q 因子急速下降。BCl₃-Ar 裡沒有可以聚合的 C 或 H，Cl 自由基由 BCl₃ 解離提供化學反應性、Ar 離子提供純物理轟擊，側壁不會被聚合物覆蓋，直接得到 Fig. S9b 那種平滑垂直側壁。另一個底層設計是「為什麼 III-V 用氯基而不是矽晶製程常用的氟基」——因為 In、Ga、Al 的氟化物（InF₃、GaF₃、AlF₃）是高熔點固體會殘留堵住蝕刻，而氯化物揮發性都夠好可以直接被抽走。至於稀 piranha 為什麼是 1:1:100 而不是標準的 3:1？因為 3:1 對 GaAs 每秒可蝕刻幾百 nm，disk-on-pillar 幾秒就變自由粒子、根本沒時間切換形態，而且極強氧化性會開始咬 InGaP、把選擇性打破。稀釋到 1:1:100 讓蝕刻速率降到每分鐘幾十 nm 的可控範圍，同時保留高選擇性，靠時間就能自由切換 partial vs full etch。而 disk-on-pillar 的「盤大柱小」細腰幾何本身，是稀 piranha 從盤邊往內等向咬 GaAs 的必然結果：pillar 直徑 = disk 直徑 − 2 × 蝕刻進深，控時就完全對應到 pillar 細度。

這條 RIE + 溼蝕刻的信賴度都押在三個判斷上，錯一個就整批報廢。第一，若當初選了 Oxford 的 CH₄-H₂-Cl₂ 化學，Fig. S9a 那種粗糙側壁會直接被複製到 disk 邊緣，每個突起都是 WGM 的散射點，Q 因子急速下降、閾值飆高，甚至 460 nm 的最小盤根本無法起振。所以「選對 RIE 化學」不是機台品牌偏好，是雷射能不能起振的先決條件。第二，若不小心用了標準 piranha (3:1) 而不是稀釋版本，泡進去幾秒 GaAs 就會全部溶光，根本沒時間拿出 disk-on-pillar 樣品；同時強氧化性會開始咬 InGaP，盤直徑變小又凹凸不平，WGM Q 因子破壞、雷射閾值飆高，整批粒子報廢。第三，若 RIE 之後只用 CF₄-O₂ 沒有再泡硫酸，殘留的碳化物會擋住 piranha 接觸底下 GaAs——一部分盤下方 GaAs 已溶光、另一部分還沒動，脫落時間不同步、有的盤帶怪 pillar、有的黏碎屑，後續 silica 包覆也會不均勻。三個「儀式」——選對氯基化學、稀對 piranha、清乾淨光阻——缺一不可。
4. 工具與材料:
- **SAMCO 200iP / 230iP RIE**: 反應離子蝕刻機台，本論文採用其 BCl₃-Ar 氯基化學做垂直側壁的 III-V mesa 蝕刻。
- **BCl₃-Ar 氯基蝕刻化學**: BCl₃ 解離出 Cl 自由基與 In/Ga/Al 反應形成揮發性氯化物、Ar 離子提供物理轟擊；沒有碳氫聚合副產物，側壁平滑垂直 (Fig. S9b)。
- **Oxford CH₄-H₂-Cl₂ 對照化學**: 另一種氯基化學，會在側壁沉積 CxHy 聚合物造成粗糙 (Fig. S9a)，作者作為反面對照後棄用。
- **CF₄-O₂ 電漿 + 稀硫酸 兩步光阻剝除**: 先用氟氧電漿把大部分 SU8 吹掉，再用稀硫酸洗乾淨殘餘碳化物，確保後續 piranha 均勻接觸 GaAs。
- **稀 piranha (H₂SO₄:H₂O₂:H₂O = 1:1:100)**: 溫和的選擇性溼蝕刻液，H₂O₂ 氧化 GaAs 表面、H₂SO₄ 溶解氧化物；GaAs 蝕率每分鐘幾十 nm、InGaP/InGaAlP/InGaAsP 幾乎不動。
- **disk-on-pillar 結構 (partial etch)**: 短時間浸稀 piranha 得到的盤懸掛在細 GaAs 柱上的懸掛幾何，供晶片級光學量測與 SEM 對位。
- **自由粒子 (full etch → LP in piranha)**: 長時間浸稀 piranha 讓 GaAs 完全咬穿，盤脫離基板落入酸液，供離心收集與後續 silica 包覆。
5. 與此篇文章的關係:
在《Ultrasmall InGa(As)P Dielectric and Plasmonic Nanolasers》這篇文章中，作者的大目標是把 UV 微影+灰化縮出的 SU8 次波長圖案真正變成可以雷射的 III-V 奈米盤。這個模塊採用了 SAMCO BCl₃-Ar 反應離子蝕刻搭配稀 piranha 選擇性溼蝕刻，解決了兩個瓶頸：一是要拿到 WGM Q 夠高的平滑垂直側壁 (棄用會殘留聚合物的 Oxford CH₄-H₂-Cl₂)，二是要能用時間切換 disk-on-pillar 與自由粒子兩種形態。它吃進的是上游的 SU8 圓柱陣列與多層晶圓，交出的是可以直接做光學量測的 disk-on-pillar 或可以送去 silica 包覆的自由粒子懸浮液。
