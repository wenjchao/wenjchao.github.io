# 影像、訊號與資料分析軟體棧

1. 引用自哪篇 paper: de-novo-design-of-luciferases
2. Outline (任務主線): 影像、訊號與資料分析軟體棧
3. Method: 
   整篇論文同時用了蛋白純化、質譜、CD、顯微影像、酵素動力學、SSM 熱圖等多種讀數，每種儀器吐出的資料格式天差地遠，必須各自搭配領域標準軟體來處理。質譜端，作者用 Bioconfirm 軟體 v10.0 把電灑游離 (ESI) 質譜原始圖反摺積 (deconvolution)——同一個蛋白在 ESI 下會打出一排間隔規律的帶電態峰，必須用 Bioconfirm 內建的「總熵演算法 (total entropy algorithm)」把這些峰重組回單一分子量 (X. Li 協助)，輸出乾淨的單峰，峰位數字就是真實分子量。顯微影像端，作者用 Nikon 的 NIS Elements 5.30 軟體做 ROI 圈選、背景扣除、曝光歸一化、螢光與發光通道對齊、光子訊號時間積分等動作 (Fig. 3c、Extended Data Fig. 9)，輸出可比較的定量數值而不是肉眼灰階。
酵素動力學端，作者用 GraphPad Prism 8 對變動受質濃度的實驗數據做非線性回歸擬合：Michaelis–Menten 方程 $v = V_{\max} [S] / (K_m + [S])$ 描述受質濃度 $[S]$ 越高、反應速率 $v$ 越快但會逼近上限 $V_{\max}$，$K_m$ 是 $v$ 達到 $V_{\max}$ 一半時的受質濃度。Prism 8 提供一鍵 Michaelis–Menten 擬合、自動處理重複實驗 (n = 3) 與 95% 信賴區間，輸出可發表等級的曲線 (Fig. 3a)。但碰到高維、需要重複跑、版面要客製化的圖——例如 SSM 飽和突變掃描的 heatmap（位置 × 19 種胺基酸 × 活性）、500 ns MD 軌跡的時間序列、ddG_bind 散點矩陣——就改用 Python 3.8 加 seaborn 0.12.1（統計繪圖庫）與 matplotlib 3.6.2（一般繪圖庫）寫腳本，能版本控管、能批次重跑。
整條 wet-lab 起點還有一個常被忽略的軟體 DNAWorks 2.0：把電腦設計的胺基酸序列反譯成 DNA 時，每個胺基酸有多種對應密碼子、不同宿主細胞偏好不同密碼子（大腸桿菌的 Leu 偏好 CTG、人類細胞偏好 CTC）。DNAWorks 2.0 做兩件事：把胺基酸序列轉成對大腸桿菌表達最有效率的密碼子組合（密碼子最佳化, codon optimization），並把整段基因切成可訂購的 oligo 片段、預先設計好重疊區以便後續 PCR 拼接。沒有這套軟體，7,648 個設計要手工湊密碼子幾乎不可能。
Multiplex 發光資料的單位寫成「RLU / CyOFP fluorescence (Ex/Em = 480/580 nm)」，這個除法不是裝飾。原始 plate reader 量到的相對發光單位 (Relative Light Unit, RLU) 同時受每孔細胞數、轉染效率、酵素本身活性三個因素影響——如果只看 RLU，分不清「這孔比較亮」是因為細胞多、轉染好，還是酵素真的厲害。作者在每個構築裡共轉染一個外加的螢光蛋白 CyOFP（激發 480 nm、發射 580 nm），它的螢光強度大致正比於「細胞數 × 轉染效率」。把 RLU 除以 CyOFP 螢光值，等於把這兩項干擾抵消掉，剩下純粹的酵素活性訊號；所有 multiplex 資料還再歸一化到 non-stimulated control，NF-κB 與 cAMP–PKA 兩條訊號通路的折扣才能放在同一張圖上比。如果直接拿原始 RLU 比較，觀察到的差異可能只是「這孔細胞多」或「這孔轉染好」的雜訊，整張結論圖就會被報導為失敗實驗。
為什麼要拿這麼多種軟體拼成一條管線？因為每種儀器的資料結構天差地遠：質譜是 m/z × 強度的二維光譜、顯微鏡是多通道像素陣列、酶動力學是時間序列、SSM 是位置 × 胺基酸 × 活性的矩陣。Excel 不會做 MS 反摺積、不會跑非線性 Michaelis–Menten 回歸、不會做多通道影像對齊、也畫不出 heatmap，所以每個領域都選了「事實上的標準軟體」。為了讓五年後想重現論文圖表的研究者拿得到一個可驗證的環境，方法描述把 seaborn 0.12.1、matplotlib 3.6.2 這種小數點兩位的版本號都寫死——Python 生態系的繪圖套件常常在小版本之間改預設行為（顏色、字型、subplot 邊界），不寫精確版本，其他人重跑同樣腳本會得到視覺差異不小的圖。失敗模式有兩個典型：跳過 MS 反摺積，無法確認 LuxSit 真實分子量是 13.9 kDa，可能把 +5 電荷的正確分子誤判成更小片段、看不出 TEV 是否確實切掉 His-tag 的 1 kDa 差異；省略 CyOFP 校正，multiplex 結論會被細胞數與轉染效率的雜訊淹沒，看不出 NF-κB 與 cAMP–PKA 的真實 fold-change。
4. 工具與材料: 
   - **Bioconfirm v10.0**: Agilent 出的質譜反摺積軟體；用總熵演算法把 ESI 的多帶電態峰重組回單一分子量。
   - **total entropy algorithm**: Bioconfirm 採用的反摺積演算法；從 m/z 光譜重建單一分子量分佈。
   - **NIS Elements 5.30**: Nikon 的顯微影像分析軟體；負責 ROI 圈選、背景扣除、通道對齊、光子訊號時間積分。
   - **GraphPad Prism 8**: 酵素動力學非線性擬合與長條圖工具；提供一鍵 Michaelis–Menten 擬合與 95% 信賴區間。
   - **Python 3.8 / seaborn 0.12.1 / matplotlib 3.6.2**: 腳本式繪圖棧；負責 SSM heatmap、MD 軌跡、ddG_bind 散點矩陣等高維可重現圖表。
   - **DNAWorks 2.0**: 胺基酸序列反譯 DNA 的工具；做密碼子最佳化與 oligo 切段（含重疊區設計）。
   - **CyOFP normalization**: 在每個構築共轉染的螢光校正蛋白 (Ex/Em = 480/580 nm)；用 RLU/CyOFP 校正細胞數與轉染效率差異。
   - **Michaelis–Menten equation**: $v = V_{\max}[S]/(K_m+[S])$；描述受質濃度與反應速率的非線性關係，需以非線性回歸擬合。
5. 與此篇文章的關係: 
   在《De novo design of luciferases using deep learning》這篇文章中，作者為了把蛋白純化、質譜、CD、顯微影像、酵素動力學、SSM 熱圖等差異極大的讀數整合到統一管線，採用了 Bioconfirm + NIS Elements + Prism + Python 棧 + DNAWorks 這套領域標準軟體組合。它解決了「不同儀器原始檔語言不通、Excel 又處理不了 MS 反摺積或矩陣熱圖」的瓶頸：每個工具吃對應的原始檔、輸出可比較的定量與圖表。產出的數字直接餵給論文 Fig. 1–4 與所有 Extended Data Figs。
