# Correct Knockin Barcode Frequency 預測

1. 引用自哪篇 paper: pooled-knockin-cellular-immunotherapy
2. Outline (任務主線): Correct Knockin Barcode Frequency 預測
3. Method: 
   推算分四步，從 1000 顆已成功 knockin 的細胞開始：第一，假設 25% 是雙等位整合 (biallelic) — 細胞的兩條染色體都接到 knockin，這類有 250 顆，貢獻 500 條 allele；第二，剩下 75% 是單等位整合 (monoallelic) — 只有一條染色體被整合，這類有 750 顆，貢獻 750 條 allele；第三，加總起來總共 1250 條帶 knockin 的 allele；第四，FACS 是根據細胞表現 sort，所以這 1250 條 allele 全都會被讀進去。biallelic 那 250 顆細胞為什麼會貢獻錯誤條碼？因為它們兩條染色體獨立從同一池 36 種模板中抽，抽到同一個裝備兩次的機率極低，幾乎都是抽到兩個不同裝備。當 FACS 根據其中一個裝備的表現把這顆細胞 sort 進來時，雖然這條 allele 對的，但另一條 allele 帶的是另一個隨機裝備的條碼——PCR 不挑哪一條 allele 都讀，所以這 250 顆細胞會貢獻 250 條錯誤條碼。
   兩個 confounder 怎麼串成 72%？精神是「一個個扣」：1250 條 allele 中有 250 條因 biallelic 一定錯，剩 1000 條暫時是對的；這 1000 條再被 10% template switching 污染掉 100 條，剩下 900 條才是真正對的。最終正確比例 = 900 / 1250 ≈ 72%。這個串接的線性假設是兩個事件獨立——biallelic 發生與否不影響 switching 機率。為什麼要做這個解析預測？它是 sanity check：如果實驗測出的 sorted 群體條碼純度剛好 ≈ 72%，代表 protocol 確實只受這兩個雜訊源影響、沒有其他未知污染，可以放心進下游 log2 fold change 計算；如果偏離太多（例如只有 40%），代表還有其他雜訊（off-target 整合、未整合模板殘留等）沒處理乾淨，必須排查。等於用一道紙上推算為實驗品質定一條基準線。
   72% 不是萬用常數。如果換了一套電穿孔條件或 RNP 比例，biallelic 比例可能變成 30%、switching 變成 5%，就要用同樣邏輯重新代入算新預測值。把 72% 當固定值套到不同實驗會誤判結果。更進一步，線性串接假設了 biallelic 與 switching 兩個事件互不影響——如果其實 biallelic 細胞因模板濃度高更容易發生 switching，那 switching 在 biallelic 子群裡會比平均 10% 更頻繁，直接套平均值會系統性低估雜訊，預測值與觀察值會持續偏離。這時得改用條件機率分群重算。
4. 工具與材料: 
   - **Biallelic integration**: 兩條染色體都被整合 knockin 構築，貢獻一條正確一條錯誤條碼。
   - **Monoallelic integration**: 只有一條染色體被整合，貢獻單一正確條碼。
   - **Allele 加總公式**: 1000 細胞 → 750 mono (750 allele) + 250 bi (500 allele) = 1250 allele 進入 PCR 計數。
   - **72% sanity-check 基準**: 扣掉 biallelic 與 switching 後預期正確條碼比例，作為實驗 vs. 預測的對照線。
   - **獨立性假設**: biallelic 與 template switching 兩事件互不影響，是線性串接 25% + 10% 的前提。
5. 與此篇文章的關係: 
   在《Pooled Knockin Targeting for Genome Engineering of Cellular Immunotherapies》這篇文章中，作者為了在進入下游 log2 fold change 計算前先檢驗 protocol 雜訊是否在預期範圍內，採用了結合 biallelic integration 與 template switching 兩個 confounder 的解析預測。這個方法解決了實驗數字缺乏「該長什麼樣」的對照基準的瓶頸，吃進 25% biallelic 比例與 10% switching 比例兩個輸入參數，產出 sorted 群體預期 ~72% 正確條碼的理論值，作為實驗 vs. 預測的 sanity check。
