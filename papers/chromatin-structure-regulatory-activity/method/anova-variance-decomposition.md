# 變異數分解 (ANOVA) 與重複再現性

1. 引用自哪篇 paper: chromatin-structure-regulatory-activity
2. Outline (任務主線): 變異數分解 (ANOVA) 與重複再現性
3. Method: 
   拿到擬合好的線性模型後，作者用變異數分解 (ANOVA, analysis of variance) 把整批 $E_{ij}$ 觀察值的散開程度切片：每個因子分到多少百分比的解釋力。直觀說：CRS 解釋 16% 表示「整批資料的散開有 16% 單純由『CRS 是哪個』就能預測」。第一代資料 (8 LP × 310 CRS) 的拆分結果：基因組位置 ($L_j$) 一人就佔 64%——最大的單一因子；CRS 序列 ($C_i$) 16%；biological replicate 之間的隨機抖動約佔 20%。三者加起來剛好 100%，加性模型已經把訊號吸乾，剩下能歸給「CRS × LP 特異交互」的空間幾乎沒有。第二代資料 (14 LP + Hsp68/MinP swap) 加入 promoter 因子後拆出：local CRS 9.0%、regional chromosome 26%、promoter identity 26%——三者各自顯著但互不吃對方份額，代表 CRS、位置、promoter 三件元件都是獨立可加的模塊。

   為什麼「殘差中能歸給特異交互的部分」會被 replicate noise 框死？關鍵是：真實的生物訊號應該在重複實驗中重現。如果 CRS-A 在 LP-B 真的有某種特異性放大效果，獨立做兩次實驗都應該看到「CRS-A 在 LP-B 異常高」這個訊號穩定出現。可是 biological replicate 之間的 Pearson 相關只有 R = 0.66——超出這個相關度的部分本來就無法在 replicate 間穩定出現。換句話說，replicate noise (重複間的隨機抖動) 設下了「能歸給真實生物訊號」的上限：任何規模比 replicate noise 還小的訊號，根本沒辦法和實驗隨機雜訊區分。所以即使殘差裡藏著一點點 CRS × LP 特異交互，它的規模也必須小於 replicate noise——這就是作者主張「特異交互貢獻必小」的數學根據。

   作者再做兩道再現性對照來強化結論。第一道是 landing pad 兩兩之間的相關：最高達 R = 0.71 (LP1 vs. LP4)、R = 0.65 (LP1 vs. LP6)。Replicate 上限 R = 0.66 是「同個 LP 重複量同一批 CRS」的天花板；跨 LP 相關竟逼近這個上限，代表「換完全不同的染色體環境」造成的差異和「重複跑一次實驗」的差異是同一量級——位置在改變整體音量，CRS 之間的相對排序卻幾乎沒被打亂，這就是「同倍率縮放」最直觀的指紋。第二道對照是把 patchMPRA 算出的 $C_i$ 拿去和傳統 episomal MPRA (CRS 放在游離 DNA 環上、沒有染色體環境的對照實驗) 的活性比較：平均 R ≈ 0.35 乍看不高，但作者把 CRS 依 episomal 活性分成 low/medium/high 三群後，這個分群順序在每個 landing pad 都保留 (Supplementary Fig. 7)。意思是：episomal 量到的「裸活性」雖然在絕對數字上和染色體環境有落差，但「強弱排序」這個 CRS 內在屬性可以橫跨 episome → genome 一致——強的 CRS 不管放在質體還是染色體都是強。這支持把 $C_i$ 解讀為「CRS 固有強度」。

   這套變異分解最容易失靈的兩個地方都跟 replicate 設計有關。第一，replicate 不能省：只跑一次實驗時，所有殘差都可能被當成真實的特異交互——你沒有 baseline 知道實驗本身的隨機雜訊有多大，殘差裡再小的訊號都能被宣稱「這就是 CRS × LP 交互」。Replicate 提供「不變動任何實驗條件，光是重做一次會有多大差異」的下限，殘差若不顯著超過這個下限，就沒有理由歸給真實生物訊號。第二，replicate 必須是真正獨立：必須整個流程從頭跑一次。如果兩個 replicate 共用同一管轉染後細胞、只是分兩管做後續定序，兩管之間的相關會被共同來源人為抬高，replicate noise 被嚴重低估——「殘差只比 replicate noise 大一點」的論證會失靈，因為 replicate noise 本身被縮水了。作者跑 2 個獨立的 biological replicate (第二代 3 個) 並從電穿孔層次就分開做，就是為了確保 replicate 雜訊真實反映實驗整體變異。
4. 工具與材料: 
   - **ANOVA**: 變異數分解；把總變異依模型切給每個因子，未分到的部分稱殘差。
   - **% variance explained**: 每個因子分到的變異百分比；本研究第一代 LP 64%、CRS 16%、replicate noise ~20%。
   - **biological replicate Pearson R**: 獨立重複實驗之間 CRS 表現量的相關 (R = 0.66)；構成「真實訊號可被檢出」的上限。
   - **replicate noise ceiling**: 重複實驗本身的隨機抖動規模；殘差若小於此上限，無法區別於隨機雜訊。
   - **LP1 vs. LP4 / LP1 vs. LP6**: 跨 landing pad 相關 R = 0.71 / R = 0.65；逼近 replicate 上限，說明跨環境 CRS 排序高度保留。
   - **extended ANOVA with promoter**: 第二代資料含 promoter 因子：CRS 9.0%、LP 26%、promoter 26%。
   - **episomal MPRA control (R ≈ 0.35)**: 把 CRS 放在游離 DNA 環的對照實驗；low/medium/high 排序在跨 landing pad 中保留，支持 $C_i$ 的「固有強度」解讀。
5. 與此篇文章的關係: 
   在《A massively parallel reporter assay dissects the influence of chromatin structure on cis-regulatory activity》中，作者主張「染色質與 CRS 序列獨立、特異交互貢獻很小」。ANOVA 拿前一步擬好的線性模型來把 $E_{ij}$ 的總變異分給 CRS、位置、promoter 等主因子，剩下的殘差再用 replicate 之間的隨機抖動框出上限，把「特異交互必小」這個結論從定性推論變成可量化的百分比論證。
