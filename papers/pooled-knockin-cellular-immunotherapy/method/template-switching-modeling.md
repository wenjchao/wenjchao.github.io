# Template Switching 數學建模

1. 引用自哪篇 paper: pooled-knockin-cellular-immunotherapy
2. Outline (任務主線): Template Switching 數學建模
3. Method: 
   template switching 是「條碼跑到別的裝備上」的雜訊：36 種 DNA 模板的兩端同源臂幾乎完全一樣（這樣它們才能都精準整合到 TRAC 同一位點），中間才是各自獨特的裝備加條碼。PCR 或細胞 HDR 修補時，酵素跑到一半可能跳到另一條模板上繼續複製——A 裝備的條碼就接到 B 裝備的本體上，後續定序以為 A 在富集，其實是 B。問題是在 36 種裝備的大池子裡，A 的條碼可能跑到任何一種其他裝備上，根本拆不清。作者用一個只有兩個成員 (GFP+條碼 1、RFP+條碼 2) 的迷你 library 來量這件事：用 FACS 把綠細胞與紅細胞分開後讀條碼，「綠細胞讀到條碼 2 的比例」就是純的錯換訊號。再用一道數學公式把這個觀察值換算成大 library 的真實單次錯換機率。
   公式的形狀為什麼長這樣？定義 X 是「真實的單次錯換機率」、Y 是「最終觀察到的錯換比例」。Y 不等於 X，因為一條模板被切換一次後還可能被再切換——切偶數次又會被搬回原本的裝備、看起來「沒錯」；切奇數次才會被觀察到「錯」。寫成級數就是錯 1 次 + 錯 3 次 + 錯 5 次 + …，每一項的機率都是 $X^n$，前面係數 2 來自兩個方向的對稱：$Y = 2X + 2X^3 + 2X^5 + \ldots$。整理成等比級數的閉合解就是 $Y = \dfrac{2}{1/X - 1}$。這套推導靠兩個簡化假設：第一，每條模板被切換的機率彼此一樣（所有同源臂結構相同，酵素無法分辨）；第二，模板的歷史不影響未來切換機率 (memoryless)。實測上 pooled assembly 的 Y ≈ 50%（嚴重）、pooled electroporation 的 Y ≈ 10%（可接受），這就是作者選擇 pooled electroporation 的依據。
   兩個地方容易壞掉。第一，如果直接用觀察到的 Y 當真實錯換率代入下游校正，因為 Y 包含被切換 1、3、5… 次的累積，會高估雜訊強度，後續 log2 fold change 過度校正——可能把真正富集的裝備校成沒富集，或把雜訊放大成富集。校正必須先用 $Y = \dfrac{2}{1/X - 1}$ 反推回 X 才能用。第二，如果某些裝備的同源臂稍有差異 (例如模板長度不同) 導致它被切換的機率高於其他人，「均一機率」假設就失效，推出來的數字對那些異常成員會嚴重失準——這是作者刻意把所有 36 個構築設計成「兩端同源臂完全相同、唯獨中間的 Insert X 與 6 bp barcode 不同」的原因，保證假設成立才能套這套公式。
4. 工具與材料: 
   - **Template switching**: 酵素複製/修補時跳到另一條同源模板上，使條碼與裝備本體錯配的雜訊。
   - **2-member calibration library**: 只含 GFP+條碼 1 與 RFP+條碼 2 兩個成員的校正組，用顏色 sort 後讀條碼純度即可量化錯換率。
   - **等比級數閉合解**: $Y = 2X + 2X^3 + \ldots = \dfrac{2}{1/X - 1}$，把觀察值 Y 反推回真實單次錯換機率 X。
   - **Memoryless 假設**: 已 switch 過的模板再 switch 機率與原本一樣，這是讓級數可解的核心假設。
   - **Pooled Assembly vs. Pooled Electroporation**: 兩種池化策略，前者 Y ≈ 50% 太雜，後者 Y ≈ 10% 可接受，被選為標準流程。
5. 與此篇文章的關係: 
   在《Pooled Knockin Targeting for Genome Engineering of Cellular Immunotherapies》這篇文章中，作者為了量化大型 36-member knockin library 的條碼錯換污染程度，採用了 2-member 校正配等比級數閉合解的反推策略。這個方法解決了大 library 中無法直接拆解條碼如何錯配的瓶頸，吃進 GFP/RFP 雙色校正組的 FACS 後條碼純度，產出真實單次錯換機率 X，作為判斷哪個池化階段 (assembly vs. electroporation) 雜訊最低的決定性依據。
