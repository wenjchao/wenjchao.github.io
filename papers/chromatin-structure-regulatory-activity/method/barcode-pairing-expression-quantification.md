# 條碼配對篩選與 CRS-level 表現量化

1. 引用自哪篇 paper: chromatin-structure-regulatory-activity
2. Outline (任務主線): 條碼配對篩選與 CRS-level 表現量化
3. Method: 
   Illumina 定序機吐回大量 150 bp 的讀取序列 (read)，每條 read 內部在事先設計好的位置會同時出現兩段條碼——前段是「這條 mRNA 來自哪一個 CRS」的開關身分條碼 (cBC)，後段是「這段報導基因被插在哪個基因組位置」的位置條碼 (gBC)。處理流程的第一關，就是按位置把兩段條碼剪出來、湊成一對 `(cBC, gBC)`。湊完還要再做一道指紋檢查：條碼前後本來有一段不變的設計序列當夾鏈（spacer、酵素切位、adapter 尾巴），合稱條碼前後的固定序列指紋 (sequence context)；如果這段指紋對不上，代表這條 read 可能是 PCR 反應中兩段 DNA 黏錯邊的混血產物 (chimera)、或定序錯字、或異常重組事件，必須丟掉，否則會把「某個 CRS 在某個位置」的訊號污染掉。

   通過篩檢的配對接著進入三層彙整。第一層：對每個 cBC 分別計算 $\log_2(\text{RNA reads}/\text{DNA reads})$。為什麼要除以 DNA reads？因為 DNA reads 反映「FACS 後這批細胞裡有多少份基因組拷貝帶這個條碼」，等於這個條碼背後有多少細胞、整合進去多少份；RNA reads 才是「這些細胞最後做出多少 mRNA」。兩者相除，就把 Cre 置換效率不均、FACS 富集不均、各 landing pad 細胞數差異這些技術變因一次標準化掉。再取 $\log_2$ 則是為了後面 $E_{ij} = C_i \times L_j$ 的乘法模型——log 空間下乘法變加法，剛好可以丟給線性擬合。第二層：同一段 CRS 預掛了 25 個獨立條碼 (25 redundant cBC)，把這 25 個 ratio 在同一個 landing pad 取平均，平均掉單條碼的偶發雜訊。第三層：對兩個生物重複 (biological replicate) 再取一次平均，得到該 CRS 在該 landing pad 的單一表現值 $E_{ij}$。整個實驗最後看到 > 30,000 種獨立的 gBC-cBC 組合，平均每個 (CRS, LP) 格子由約 11 個獨立整合事件撐著。

   為什麼每段 CRS 要預掛 25 個不同的 cBC，而不是 1 個？單一條碼撐起的「這段 CRS 在這個 landing pad 的活性」只有一筆數字——萬一這個條碼剛好被 PCR 偏好性放大、剛好掉進難定序的 motif、或剛好整合到序列稍有破損的細胞，整個訊號就被偶發雜訊綁架。預掛 25 個 cBC 等於同一段 CRS 被 25 個獨立通道量了一次，平均完單條碼噪聲互相抵銷。對應到實際數字：平均每個 (CRS, LP) 格子有 ~11 個獨立整合事件支撐，replicate 間的 Pearson R 才得以推到 0.66。

   這套量化流程有兩個關卡偷不得。第一，sequence context 過濾不能省：PCR 在多輪循環中很容易把兩段不同來源的 DNA 接錯邊，產生「A 細胞的 cBC + B 細胞的 gBC」這種根本不存在於細胞裡的混血配對。不過濾，這些假配對會被當成真訊號灌進 $E_{ij}$，後續位置效應與 CRS 強度的二維拆解全部失準。第二，DNA reads 不能跳：若只測 RNA reads、不平行測 DNA reads，那「某個 landing pad RNA 訊號高」可能是因為這個位置環境真的會把基因吵醒，也可能只是因為 Cre 在這裡置換效率特別高、整合進去的細胞多 5 倍。沒有 DNA reads 當分母，「轉錄產出強」與「樣本量大」會被混在一起，整篇研究想回答的核心問題就答不出來。
4. 工具與材料: 
   - **read**: Illumina 定序機吐出的單條 150 bp 短 DNA 讀取序列，是 dry-lab 流程的基本輸入單位。
   - **cBC**: 開關身分條碼，告訴你這條 read 來自哪個 CRS。
   - **gBC**: 位置條碼，告訴你這條 read 來自哪個 landing pad 在基因組的位置。
   - **sequence context**: 條碼前後不變的設計序列指紋（spacer、酵素切位、adapter 尾巴等）；用來剔除 PCR chimera、定序錯字等異常 reads。
   - **$\log_2(\text{RNA reads}/\text{DNA reads})$**: 用 DNA reads 做分母把整合份數標準化掉，剩下的 RNA 訊號專門反映「每份模板被轉錄成多少 mRNA」；取 $\log_2$ 是為後續線性模型把乘法轉成加法。
   - **25 redundant cBC**: 每段 CRS 預掛 25 個獨立 cBC，藉冗餘平均壓低單條碼噪聲。
   - **biological replicate**: 獨立進行的兩次實驗，用來平均掉每次實驗特有的批次雜訊。
   - **$E_{ij}$**: 三層平均後得到的 CRS i 在 landing pad j 的單一表現值，用於後續線性模型擬合。
   - **gBC-cBC integration event**: 一個獨立成功的「某 CRS 被塞進某 landing pad」事件；全實驗共觀察到 > 30,000 個，平均每格 ~11 個。
5. 與此篇文章的關係: 
   在《A massively parallel reporter assay dissects the influence of chromatin structure on cis-regulatory activity》中，作者要回答「位置和 CRS 序列是獨立還是糾纏」，必須把濕式實驗產出的條碼定序資料化成乾淨的二維 $E_{ij}$ 矩陣。這套條碼配對與 $\log_2(\text{RNA/DNA})$ 量化流程吃 Illumina reads、吐出每個 CRS 在每個 landing pad 的單一表現值，把 Cre 置換、FACS 富集、PCR chimera 等技術雜訊一次清掉，直接供下游線性模型與 ANOVA 拆解使用。
