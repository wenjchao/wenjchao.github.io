# CRISPR-All 模組化迭代克隆 (Iterative Internal/External Stuffer cloning of CRISPR-All architecture)

1. 引用自哪篇 paper: crispr-all-genetic-perturbation-language
2. Outline (任務主線): CRISPR-All 模組化迭代克隆 (Iterative Internal/External Stuffer cloning of CRISPR-All architecture)
3. Method:
   起點是一條空的 backbone DNA，裡面預留兩個「占位區」：內部填充料 (internal stuffer) 與外部填充料 (external stuffer)，分別由 BsaI 與 BbsI 兩種限制酶切出來。每要塞進一個擾動 element，就把這條 backbone + 一條攜帶 element 的 insert vector 放進同一管反應液，加入對應的主切酶（例如 BsaI）把 backbone 的 internal stuffer 切掉、同時把 insert vector 兩端切開；同時加入副切酶 SrfI 把沒被切的母質體剪碎避免背景污染。接著加 T7 DNA ligase 把 backbone 缺口跟 insert 兩端接起來，element 就被縫進 backbone；同時 insert 兩端設計的 GTAA / AGCG 黏端會跟下游同步攜帶的 11 字母條碼接起來，等於每串一個 element 就同步累積一段條碼。下一輪換另一把酶 (BbsI + PmeI) 處理外部填充料，繼續接下一個 element。為什麼用 BsaI / BbsI 這兩把 Type IIS 限制酶？一般限制酶（例如 EcoRI）切的位置就在自己的識別序列上，4 bp 黏端被識別序列綁死；Type IIS 不一樣，它的識別序列像「指向標」、真正切割發生在識別序列「旁邊」幾個鹼基外的指定位置，4 bp 黏端因此可以自由設計。BsaI 認 GGTCTC、BbsI 認 GAAGAC，識別序列不同但都切出 4 bp 黏端，可以「同一條 backbone 內」用兩把酶處理不同位置而互不打架——這套設計叫 Golden Gate cloning。

   串接 element 時，每個接點都會留下一個 4 bp 的「結合疤痕」——這 4 個字母本來會變成最終 DNA 序列的一部分，干擾下游表達。作者讓所有接點都用同樣兩個固定字串：5′ 端 GTAA、3′ 端 AGCG。為什麼是這兩個？因為 GTAA 是人類細胞 splicing machinery 辨識為「5′ exon-intron 邊界」(consensus splice donor) 的標準起點——細胞會把 GTAA 之後的 DNA 當成 intron 區段剪掉。作者把所有 element 之間的接點都設計成「藏在 intron 裡」：element 結尾接 GTAA、接著一段 intron、再接 AGCG 開始下一個 element；mRNA 轉錄出來後細胞的 splicing 機器會自動把這段 intron 連同 GTAA / AGCG 黏端剪掉，最終蛋白質序列完全沒有疤痕。作者測了 24 條 52–310 bp 的 intron，最後挑出 11 條 ≥90 bp 的人類自然 intron 確認能保留 reporter gene 表達。如果不藏進 intron 而直接讓黏端留在 coding region，每個接點多出 4 字母就會造成 frameshift，下游蛋白序列全部跑掉；多串幾個 element 累積多份疤痕，蛋白表達直接崩盤——這也是這套設計能串 ≥10 個 element 仍維持 95% 正確表達的關鍵。

   每個擾動 element 出廠時就已經跟一個 11 字母的條碼綁在一起，cloning 反應把 element 接進 backbone 的中間部位，同時把 barcode 接到 backbone 的 3′ 端。每串一個 element 就同步累積一段條碼，最後一條完整構築的尾端就有「條碼 1 + 條碼 2 + 條碼 3 + ...」這樣的條碼陣列 (barcode array)。為什麼是 11 個鹼基？4 種鹼基的 11 個位置可以組合出 $4^{11} \approx 4.2 \times 10^6$ 種條碼，足夠區分每一個元件；但作者額外要求所有條碼兩兩之間至少差 3 個字母（漢明距離 Hamming distance ≥3）才能進入白名單，這樣即使定序時某個字母讀錯一兩個位置，仍可以「最接近的合法條碼」反推回原條碼，避免 sequencing error 造成誤判。所以雖然 11 bp 不是最大空間，但搭配漢明距離 ≥3 的白名單已經夠用且容錯。

   整套迭代克隆最怕的雜訊是「條碼跟 element 失聯」——條碼被串到不該對應的 element 上 (barcode template switching)，下游 pooled screen 就完全對不上實際擾動。作者用四道防線同時夾殺：(1) 副切酶 SrfI / PmeI 的切位設計在 backbone 的 stuffer 中段，主切酶沒切到的母質體會被副切酶切斷、轉化後無法形成 colony，等於把沒反應的母質體就地處決。(2) 抗藥性切換——目的 backbone 帶 ampicillin、insert vector 帶 kanamycin；最終 ligation 產物只帶 amp 抗性，用 ampicillin 板就能篩掉所有沒接好的旁路。(3) T7 DNA ligase（噬菌體連接酶）只連接完美互補的 4 bp 黏端、幾乎不連 blunt end；作者進一步把 DNA 量降到廠商建議的 1/10，反應中同時碰撞的 element 數變少、每個 backbone 周圍只有一個 insert 候選，concatemer 與 template switching 都壓下去。(4) 轉化後不用一般大腸桿菌 (DH5α) 與 37 °C 培養——一般株體內 RecA 重組會把共用序列的 plasmid 互相交換、把 A 的條碼串到 B 上；改用 recA-/recBC- 改造、電轉效率 >10^10 cfu/µg 的 Endura electrocompetent cells，並在 30 °C 培養 20–28 小時讓重組活性降到最低。即使有這四道防線，10,240-member 組合 library 的「正確四元素對應」也只有 60%——可見 template switching 是這套技術最核心的雜訊源，作者再用 PacBio HiFi 長讀定序量化每個 barcode 的真實對應，下游 pool screen 才有可信的雜訊上限。

4. 工具與材料:
   - **Type IIS 限制酶**: 識別序列與切割位點分離的限制酶，能在識別序列旁邊的指定位置切出自由設計的 4 bp 黏端。
   - **BsaI**: Type IIS 限制酶，識別 GGTCTC，本實驗用來切 Internal Stuffer。
   - **BbsI**: Type IIS 限制酶，識別 GAAGAC，本實驗用來切 External Stuffer。
   - **SrfI / PmeI**: 副切酶，切位設計在 backbone 的 stuffer 中段，把沒被主切酶切到的母質體就地處決避免背景 colony。
   - **Internal Stuffer / External Stuffer**: Backbone 中預留的兩個占位 DNA 區段，分別由 BsaI 與 BbsI 切出，每輪以對應酶切掉換上新的 element。
   - **GTAA / AGCG 共用黏端**: 所有 element 接點固定使用的 4 bp 黏端；GTAA 是人類 consensus splice donor，會把後面的 DNA 連同黏端當作 intron 剪掉，達到 scarless cloning。
   - **11 bp barcode + Hamming distance ≥3 白名單**: 每個 element 自帶 11 字母條碼，白名單要求兩兩之間至少差 3 字母，可容忍 sequencing error 自動糾錯。
   - **T7 DNA ligase**: 噬菌體連接酶，對完美互補 4 bp 黏端選擇性高、幾乎不連 blunt end；本實驗將 DNA 量降到廠商建議 1/10 以減少 concatemer。
   - **抗藥性切換 (amp vs kan)**: 目的 backbone 帶 ampicillin、insert vector 帶 kanamycin，雙抗篩選排除沒接好的旁路 colony。
   - **Endura electrocompetent cells**: recA-/recBC- 改造的大腸桿菌電轉接受株，電轉效率 >10^10 cfu/µg，避免 plasmid 在菌體內重組造成 barcode swapping。
   - **30 °C 培養 20–28 hr**: 降低大腸桿菌 RecA 重組活性的培養條件，進一步壓制 barcode template switching。
   - **barcode template switching**: ligation 或菌體重組導致條碼貼到非對應 element 的雜訊，是這套迭代克隆最核心的失敗模式，本實驗用四道防線同時夾殺。

5. 與此篇文章的關係:
   在《A unified genetic perturbation language for human cellular programming (CRISPR-All)》這篇文章中，作者為了把 Gene/Domain/Knockout/Knockdown 四類擾動 element 與專屬條碼一次性編譯成一條 DNA 序列，採用了 Type IIS Internal/External Stuffer 模組化迭代克隆配 GTAA/AGCG splice-donor 無疤痕設計。這個方法解決了多 element 串接會在蛋白序列累積疤痕、以及池化克隆容易發生 barcode 與 element 失聯的瓶頸。它為下游 TRAC 非病毒 knockin、CACTUS 篩選與 10,240-member 組合 library 提供無疤痕、有條碼陣列、且可定序回溯的構築。
