# Pooled Knockin Barcode 量化分析

1. 引用自哪篇 paper: pooled-knockin-cellular-immunotherapy
2. Outline (任務主線): Pooled Knockin Barcode 量化分析
3. Method: 
   整套量化從定序機吐出的 fastq 開始——這是一份純文字檔，每四行記錄一條 read：編號、鹼基序列、+、每個鹼基的可信度分數 (Phred score)。一個 pooled screen 樣本通常有上千萬條 read，量化就是把這些 read 一條條對到「裝備條碼字典」上計數。流程拆三步：第一，把 36 個裝備的 6-bp barcode 序列做成一本字典 (R 語言 Biostrings 套件的 PDict 函數的 input)，每個條目對應一個裝備；第二，把 fastq 裡的每條 read 拿去字典裡找——只有「一字不差」的 read 才被算進對應裝備的計數 (exact match)；第三，加總後得到每個裝備的 read count，再除以總 read 數變成 barcode frequency。為什麼堅持 exact match 而不允許 mismatch？因為 6-bp barcode 太短，允許一個 mismatch 會把鄰近條碼混在一起。
   計數本身只是中間結果，真正用來排名的指標是 log2 fold change (LFC)：LFC = $\log_2(\text{condition frequency} / \text{input frequency})$。例如某裝備在 input 時佔 1%、被 TGF-β 篩過後佔 4%，倍數是 4，LFC = $\log_2(4) = 2$；如果被壓制到 0.25%，LFC = $\log_2(0.25) = -2$。為什麼用 log2 而不用直接倍數？因為對數讓「漲 2 倍」與「縮 0.5 倍」變成 +1 與 -1 這種對稱數字，後續平均與統計檢定才不會被極端正向值偏倚。PDict 之所以能高效對成千上萬條 read 做精確比對，是因為它先把所有 barcode 預先打成一棵字首樹 (Aho-Corasick trie)；對每條 read 從頭掃到尾，每跨一個字元就能同時判斷是否命中任何字典條目，計算量是 O(讀長 + 條目數) 而非 O(讀長 × 條目數)，所以即使再多條碼也飛快。
   兩個設計選擇決定了結論的穩健度。第一，所有 donor (捐血者) replicate 分組合併進 LFC 計算——每個 donor 的 T 細胞背景不一樣，合併等於把「跨個體一致富集」的裝備拉出來，過濾掉只在單一 donor 有效的偶發 hit；這對未來真要做臨床治療的裝備來說是必要的篩選嚴度。第二，in vitro 用 two-way ANOVA + Holm-Sidak 多重比較校正，因為樣本數高、條件重複多，要嚴格控制偽陽性；in vivo 改用 Fisher's LSD 這種寬鬆版本，因為一隻老鼠只能回收 10–20k 顆 TIL、動物個體差異又大，重複次數少；如果還用 Holm-Sidak 那麼嚴的校正，真實 hit 會被當雜訊濾掉。寬鬆檢定承擔較高偽陽性風險，但在低統計力情境下能把候選 hit 提名出來，再交給後續個別驗證。
   兩個容易壞掉的邊界要注意。第一，比對若改用「允許 1 mismatch」的容錯方式，6-bp barcode 太短，36 個條碼間鹼基差異可能只有 1–2 個——某條 A 條碼的 read 讀錯一個鹼基，可能就被算進 B 條碼計數，真實 frequency 互相滲透，強裝備被分掉訊號、弱裝備被灌入假計數，排名就會錯。寧可丟掉少數讀錯的 read 也不要污染計數，所以堅持 exact match。第二，LFC 在 input frequency 接近零時會炸開——分母為零時 LFC = -∞、分母非常小時 LFC 是極大正值，會把整張圖被離群點主導。實務上要加 pseudocount (例如 +1) 或預先濾掉 input 太低的 member，否則 pooled screen 排名可能被低品質 outlier 主導。
4. 工具與材料: 
   - **Fastq**: 定序儀輸出的純文字檔，每四行一條 read，含序列與 Phred 品質分數。
   - **PDict (Biostrings)**: R 語言 Biostrings 套件的字典化精確比對函數，用 Aho-Corasick trie 高效掃描 fastq。
   - **Exact match**: 一字不差的比對策略，6-bp barcode 不能容錯避免條碼互相滲透。
   - **Log2 Fold Change (LFC)**: $\log_2(\text{condition frequency} / \text{input frequency})$，把倍數變化對稱化便於統計。
   - **Two-way ANOVA + Holm-Sidak**: in vitro 高樣本量情境下嚴格控制多重比較偽陽性的檢定組合。
   - **Fisher's LSD**: in vivo 低統計力情境下用的寬鬆事後檢定，承擔偽陽性以換取偵測力。
   - **Donor replicate 合併**: 把多位捐血者的重複跨組合併進 LFC，過濾掉只在單一 donor 有效的偶發 hit。
5. 與此篇文章的關係: 
   在《Pooled Knockin Targeting for Genome Engineering of Cellular Immunotherapies》這篇文章中，作者為了把定序機輸出的上千萬條 read 轉換成每個構築在不同選擇壓力下的成長排名，採用了 PDict 精確比對配 log2 fold change 的量化分析。這個方法解決了 raw fastq 缺乏可比指標的瓶頸，吃進 PCR 擴增完的 barcode amplicon 定序 fastq，產出每個 library member 的 LFC 與顯著性檢定結果，作為提名 TGF-βR2-41BB 等命中構築進入下游個別驗證的決定性依據。
