# Gas Vesicle 與 GV-Ca²⁺ Sensor 製備（影像對比劑）

1. 引用自哪篇 paper: deep-tissue-sound-printing
2. Outline (任務主線): Gas Vesicle 與 GV-Ca²⁺ Sensor 製備（影像對比劑）
3. Method: 
   GV 是某些光合細菌（例如藍綠藻 Anabaena flos-aquae）內天然製造的「奈米氣球」——殼是 GvpA 蛋白拼成的圓柱加錐形外殼，內部充滿氣體，整顆只有約 100 nm 寬。它能被超音波看見的關鍵是「裡面是氣體、外面是水」：氣與水的聲阻抗 (acoustic impedance) 差異極大，超音波打到時被強烈散射回探頭、亮如螢火蟲；周圍只有組織液的地方則暗。AM-mode 利用「GV 在不同聲壓下的回響是非線性的」這個特性，把線性的組織背景訊號相減掉、只留 GV 訊號。當 FUS 用更高聲壓打過去，殼體會像被踩癟的乒乓球一樣崩解，那一格的亮點消失——這就是「焦點打到了」的訊號。
   
   野生 GV 製備依 Lakshmanan et al. 2017 Nat. Protoc.（ref 40）。先培養藍綠藻 Anabaena flos-aquae、把細胞打破釋放出 GV；再加 6 M urea 配 100 mM Tris-HCl (pH 8–8.5) 把原本貼在 GV 外層的保護蛋白 GvpC 洗掉，得到「裸體 GV (stripped GV)」——為什麼要剝？因為作者要重新換上一件工程化 GvpC 當 Ca²⁺ 開關。剝完後的 GV 因為內部充氣比水輕，所以用 4 °C 300 g × 4 h 的低速浮選離心讓 GV 浮上去、雜質沉下去；丟掉下方沉澱液 (subnatant) 留上層 GV，重複兩輪純化。
   
   至於 GV-Ca²⁺ sensor 用的工程化 GvpC（URoC1-EF4KO，依 Jin et al. 2023 bioRxiv ref 39），是大腸桿菌大量表現的重組蛋白。流程像標準 His-tag 蛋白純化：先把質體轉殖到 BL21(DE3) 大腸桿菌，挑單一菌落在 2×YT + 50 μg/ml kanamycin 培養基 37 °C 養 14–16 小時當起頭菌；再以 1:100 稀釋到 Novagen 自動誘導培養基 (auto-induction Terrific Broth)，30 °C × 20–24 h——這種培養基放了 glucose + lactose + glycerol，菌先用 glucose 大量增殖、glucose 耗盡後 lactose 自動誘導 T7 promoter 表現 GvpC，不必手動加 IPTG。收菌後用 SoluLyse 配 lysozyme + DNase I 裂解；這個 GvpC 變體會堆在 inclusion body（不溶性蛋白團塊）裡，所以再用高速 15,000 g 收這團塊、用 6 M urea + 500 mM NaCl 溶成單體；最後用 Ni-NTA 親和管柱抓 His-tag GvpC，wash buffer 含 20 mM imidazole 沖雜蛋白、elution buffer 含 250 mM imidazole 把目標蛋白競爭下來。inclusion body 不是壞事——下游本來就要把 GvpC 解開成展開鏈狀才能裝回 GV，剛好接得上。
   
   工程化 GvpC 純好後怎麼裝回剝光的 GV？分兩步：先在 6 M urea 中把 GvpC（依公式 2 × OD500 × 480 nM × volume 算出兩倍莫耳量）跟剝光 GV 混在一起，此時 urea 把 GvpC 撐成展開鏈、不會亂折；接著裝進 Spectra/Por 132675T 透析袋（MWCO 6–8 kDa）對 PBS 在 4 °C 透析 ≥ 12 小時，透析袋只放小分子 urea 出去、留住 GvpC 和 GV，urea 濃度緩慢降低，GvpC 一邊重新摺疊一邊找到 GV 表面結合位點貼回殼體。緩慢是關鍵——若快速洗掉 urea，GvpC 會在自己鏈內亂折成 misfolded aggregates、整顆 GV 上裝載量低、Ca²⁺ 響應靈敏度差，影像偽陰性增加。最後用 NanoDrop OD500 量崩解前後吸光度變化、間接算出 GV 數量與 GvpC 裝載量。
   
   DISP 同時用兩種對比劑回報不同階段的成功訊號。野生 GV 是「物理打到了沒」的指示燈——FUS 高聲壓對準時殼體崩解、亮點消失，告訴操作者 focal point 確實打進這塊 ink。GV-Ca²⁺ sensor (URoC1-EF4KO) 則是「化學真的反應了沒」的指示燈：它在工程化 GvpC 上接了類似 calmodulin 的 Ca²⁺ 抓手 (EF-hand)，沒 Ca²⁺ 時 GvpC 緊貼 GV 像穿厚盔甲、殼很硬不易在聲壓下塌陷 (buckle)、影像暗；當 LTSL 釋放 Ca²⁺，抓手抓住 Ca²⁺ 後 GvpC 構象改變、部分脫離 GV、盔甲變鬆，殼體在聲壓下容易塌陷反彈、非線性回響大增、影像對應位置亮起來，等於把化學事件直接寫入影像對比。若只用野生 GV 只能看到「打到」但不知道是否真的觸發化學；若只用 sensor 又沒辦法在 FUS 前先確認墨水位置——兩者一前一後構成完整的物理 + 化學雙保險。
   
   影像端用 Verasonics Vantage 平台配 L22-14vX 線陣探頭，跑兩種模式。第一種叫 pB-mode (parabolic B-mode)：焦點設在 10 mm 深、開口 4 mm，提供寬視野的解剖定位影像，讓醫生先確認 catheter 是否真的把墨水送進膀胱。第二種叫 xAM (cross-propagating amplitude modulation，依 Maresca et al. 2018 Phys. Rev. X ref 27)：從探頭兩側各送一束 19.5° 斜向的波交叉在影像區中心，組織的線性訊號可以兩兩相消、GV 的非線性回響不會被消，影像上只剩 GV 訊號發亮。中心頻率 15.625 MHz、每條掃描線 64 條（ray lines）、同一張影像疊加 50 次提升訊雜比；最終影像每個像素 50 μm 寬 × 1 μm 深，足以看出 ~150 μm 的列印線寬。
   
   野生 GV 純化時為什麼要用 300 g 4 h 而不是高 g 離心？因為 GV 是充氣奈米氣球、浮力大；高 g 力（例如 > 10,000 g）會壓垮殼體讓 GV buckle、氣體外洩、GV 失活，純化反而把對比劑做死了。所以用低速、長時間的浮選離心，讓 GV 在輕柔壓力下慢慢浮上來、雜質沉下去；抽掉下層沉澱液 (subnatant)、保留上層 GV，重複兩輪以提高純度。
4. 工具與材料: 
   - **Gas vesicle (GV)**：藍綠藻 Anabaena flos-aquae 內天然奈米氣球，殼為 GvpA、內充氣，可被超音波強散射；FUS 高聲壓下崩解。
   - **Anabaena flos-aquae**：野生 GV 來源的藍綠藻，protocol 依 Lakshmanan et al. 2017 Nat. Protoc. (ref 40) 培養純化。
   - **GvpC**：GV 外層的保護蛋白，可被 urea 剝除後換上工程化版本當 Ca²⁺ 開關。
   - **URoC1-EF4KO (工程化 GvpC)**：接了類似 calmodulin EF-hand 的 Ca²⁺ 抓手的 GvpC 變體 (Jin et al. 2023 bioRxiv ref 39)；Ca²⁺ 結合後鬆開殼體、xAM 訊號亮起。
   - **Urea stripping (6 M urea / Tris-HCl pH 8–8.5)**：把原生 GvpC 從 GV 表面洗掉，得到 stripped GV，準備接工程化 GvpC。
   - **BL21(DE3) + auto-induction Terrific Broth**：大腸桿菌表現宿主搭配自誘導培養基 (glucose + lactose + glycerol)，30 °C × 20–24 h，免手動 IPTG。
   - **Inclusion body + 6 M urea 溶解**：重組 GvpC 沉於不溶團塊，用尿素解離成展開鏈，剛好接續下游裝回 GV 的需求。
   - **Ni-NTA 親和管柱**：Qiagen Ni-NTA 抓 His-tag，wash 20 mM imidazole、elute 250 mM imidazole 純化工程化 GvpC。
   - **Dialysis refolding (Spectra/Por 132675T MWCO 6–8 kDa, PBS, 4 °C ≥ 12 h)**：緩慢去 urea 讓 GvpC 邊摺疊邊裝回 GV；過快會 misfold 造成偽陰性。
   - **Verasonics Vantage + L22-14vX 線陣探頭**：影像平台，128 元線陣探頭跑 pB-mode 與 xAM 雙模式。
   - **pB-mode (parabolic B-mode)**：焦點 10 mm 深、開口 4 mm 的寬視野解剖定位影像，用來看 catheter 與墨水位置。
   - **xAM (cross-propagating amplitude modulation)**：兩束 19.5° 斜向波交叉，組織線性訊號相消、GV 非線性訊號保留 (Maresca et al. 2018 ref 27)；像素 50 μm × 1 μm。
   - **NanoDrop OD500**：利用 GV 崩解前後吸光差量化 GV 濃度，用於 GvpC 重組劑量公式。
5. 與此篇文章的關係: 
   在《Imaging-guided deep tissue in vivo sound printing》這篇文章中，作者要解決「FUS 在體內看不見焦點打到哪、ink 也不知道有沒有真的膠化」這個盲打問題。為此他們把兩種對比劑做進 US-ink：野生 GV 用 Anabaena flos-aquae 培養 + urea 剝衣 + 低速浮選離心得到；GV-Ca²⁺ sensor 則用大腸桿菌表現工程化 GvpC 後 dialysis 重組裝回 stripped GV。下游 in vivo 列印時，xAM 影像同時告訴操作者「焦點是否打中（亮→暗）」與「Ca²⁺ 是否釋放、膠形是否成型（暗→亮）」，讓 DISP 從盲打變成可即時導引。
