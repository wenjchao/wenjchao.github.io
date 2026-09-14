# CD19 免疫磁珠選殖與品質放行（CliniMACS）

1. 引用自哪篇 paper: inducible-apoptosis-cell-therapy-safety
2. Outline (任務主線): CD19 免疫磁珠選殖與品質放行（CliniMACS）
3. Method:
      反轉錄病毒轉導效率沒辦法做到 100%——只有一部分 T 細胞被 SFG 病毒成功感染並整合 iCasp9-2A-ΔCD19，其餘轉導失敗的 T 細胞沒裝上開關。若把整批細胞直接輸給病人，AP1903 觸發時只能清掉裝上開關的那群，未轉導的攻擊性 T 細胞會殘留下來——這批細胞正是最可能引發 GVHD 的族群，卻沒有安全開關。所以作者必須用磁選把「有 ΔCD19 表面標籤」的 T 細胞富集出來。時機選在轉導後第 4 天：反轉錄病毒感染後還要經過反轉錄、染色體整合、mRNA 轉錄、蛋白翻譯、把 ΔCD19 送上細胞膜這一連串步驟，第 4 天是「表面 ΔCD19 已累積到磁珠抓得到 + 細胞在 IL-2 下還沒過度終末分化」的折衷點。
   磁選用的順磁性微珠 (paramagnetic microbeads, Miltenyi Biotec) 是把小顆氧化鐵包在 dextran 外殼裡的奈米級鐵珠，只在外加磁場存在時被磁化、磁場撤走就恢復無磁性，這是能「先抓後放」的關鍵。磁珠外殼共軛認 CD19 的鼠源抗體，跟細胞混一起孵育後，帶 ΔCD19 的 T 細胞表面掛上一堆磁珠；接著整批細胞流過放在強磁場中的柱子：帶珠的 CD19⁺ T 細胞被磁場拉住卡在柱子裡，未轉導的 CD19⁻ T 細胞沒磁珠、直接被緩衝液沖走；最後把柱子從磁場中拿開，磁性消失，被卡住的 T 細胞就被沖出來收集。作者用的機器是 Miltenyi 的 CliniMACS Plus 自動化封閉系統——整條路徑放在一次性封閉管路組裡，機器自動完成加珠、磁選、洗滌、收集，操作者不接觸細胞，把輸注品的無菌風險壓到 GMP 放行等級。CD19 磁選後再擴增最多 4 天然後冷凍保存。
   每批留樣送檢四項：帶開關的細胞比例 (transduction efficiency, %CD3⁺CD19⁺，須達 90–93%)、identity (是這位受試者對應的供者細胞)、phenotype (T 細胞亞群分佈仍健康)、sterility (無細菌黴菌污染)，全數符合 FDA 標準才可解凍輸注。純度定在 90–93% 是「臨床可行的最高純度 vs. AP1903 rescue 有效性」的折衷點——90% 對應約 10% 逃逸族群，臨床上仍能被 allodepletion 的第一道保險加上 AP1903 的第二道保險合力壓住；放寬到 80%，逃逸就翻倍，每次觸發都留下 1/5「無開關 T 細胞」足以維持 GVHD 不退。三項放行任一不合格必須銷毀：identity 錯誤代表混入非目標批次，phenotype 不符代表 rescue 覆蓋率或 in vivo 存活不足，sterility 失敗會直接把感染源靜脈打進骨髓移植後白血球極不全的孩子身上、引發致命敗血症。
4. 工具與材料:
   - **paramagnetic anti-CD19 microbeads**: 順磁性氧化鐵奈米珠外殼共軛認 CD19 的鼠源單株抗體 (Miltenyi Biotec)，用來抓帶 ΔCD19 表面標籤的 T 細胞。
   - **CliniMACS Plus**: Miltenyi Biotec 的臨床級全自動封閉磁選裝置，符合 GMP，用於把轉導後 CD19⁺ T 細胞富集至 90–93% 純度。
   - **transduction efficiency (%CD3⁺CD19⁺)**: 帶開關的細胞比例；本研究放行標準為 90–93%。
   - **identity/phenotype/sterility release**: 每批留樣送檢的三項 FDA 放行指標，任一不合格即銷毀整批。
   - **轉導後第 4 天**: 磁選時機；此時 ΔCD19 已表現到磁珠可辨識，同時 T 細胞尚未過度終末分化。
5. 與此篇文章的關係:
   在《Inducible Apoptosis as a Safety Switch for Adoptive Cell Therapy》這篇文章中，作者為了讓最終輸注給孩子的 T 細胞產品「幾乎每一顆都帶開關」，用 Miltenyi CliniMACS Plus 順磁性磁選把 iCasp9⁺ΔCD19⁺ T 細胞從轉導後的混合細胞群中富集到 90–93%。它解決了反轉錄病毒轉導效率無法做到 100%、未轉導細胞無法被 AP1903 清掉的瓶頸，把中間產品變成臨床級劑型，供下游劑量遞增試驗與 AP1903 觸發驗證使用。
