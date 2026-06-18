# 心臟纖維母細胞分離與 EV 取得 (Aqueous Two-Phase System, ATPS)

1. 引用自哪篇 paper: hybrid-vesicle-bioink-microrna-delivery
2. Outline (任務主線): 心臟纖維母細胞分離與 EV 取得 (Aqueous Two-Phase System, ATPS)
3. Method: 
   作者先要拿到「會分泌目標 EV」的源頭細胞——新生大鼠的心臟纖維母細胞 (CFs)。為什麼用新生大鼠？成體心臟組織太硬、CF 不易增殖；新生大鼠的心室組織還很軟、CF 還在快速分裂，是研究人員拿心臟細胞的標準來源。流程是兩步酵素消化加上差別貼壁：先在 4 °C 過夜泡 0.05% trypsin 把細胞間連結鬆開，再用 Collagenase Type II 在 37 °C、80 rpm shaking 下消化 4 次、每次 10 min，把細胞從膠原基質裡釋放出來。離心鋪盤後利用「CF 1 小時內就會貼壁、CMs 不貼壁」的差別貼壁分離 (differential adhesion)：1 h 後吸走上清液 (富集 CMs)，留下盤底的 CFs。CFs 最多只用 3 個 passage——再多就會自發轉化成肌纖維母細胞 (myofibroblast)、分泌的 EV 跑掉，下游驗證的特異性整條邏輯都會被污染。

   拿到 CFs 後，下一步是讓它們「分泌 EV 到培養液裡」再去收。這需要一個關鍵試劑替換：一般 FBS (胎牛血清) 本身就含有牛源 EV，會跟 CFs 自己分泌的 EV 混在一起無法區分，所以作者用市售已預先離掉自身 EV 的「EVs-depleted FBS」做培養基，餵 CFs 6 h；再以 300 × g × 10 min 低速離心把脫落的整顆細胞甩掉、留下 EV 浮在上清液——這個上清液就是「條件培養液 (conditioned medium)」，是丟進下一步 ATPS 的原料。

   怎麼從條件培養液裡把 EV 分出來？這篇用了「兩相水相分離系統 (Aqueous Two-Phase System, ATPS)」——把兩種高分子聚合物 (聚乙二醇 PEG 與葡聚醣 DEX) 溶在水裡，濃度夠高時它們會像油水分層一樣自動分成兩個互不相溶的水相，上相富 PEG、下相富 DEX。EV 表面有大量親水的醣鏈與磷脂頭、跟 DEX 那相比較合得來，會自動沉到下相；游離雜蛋白則跑進 PEG 上相。操作上把上清液加入等體積 DEX-PEG，於 −4 °C 用 1000 × g 慢慢離心 10 min (低加減速避免擾動相界面)，倒掉上相、留下相，再以 1:1 H₂O:DEX-PEG 洗液重複兩次把殘留雜蛋白繼續趕走，最後 0.22 µm 過濾擋住任何微米級碎屑、−80 °C 保存。為什麼放棄主流的超高速離心 (ultracentrifugation)？UC 要在 100 000 × g 下轉好幾個小時，相當於把 EV 用 10 萬倍重力按到管底，CD9/CD63/CD81 等表面標誌蛋白會被擠壞、EV 也會被壓成聚集團塊；ATPS 只用 1000 × g、剪切力是 UC 的 1/100，產量略低但能保住膜蛋白完整性——這對「EV 必須保留靶向能力」的核心命題是決定性的取捨。

   拿到分離好的 EV 之後，要量它多少濃度才能在下游融合時控制比例。EV 是奈米級顆粒、光學顯微鏡看不到也數不出來，作者改量「EV 上的膜蛋白總量」當作 EV 濃度的代理指標：用 Bradford assay (測蛋白質總量的標準方法，protocol refs [77,78])——5 µl 樣品混進 250 µl Bradford reagent、室溫 30 min，蛋白會把試劑從紅色變藍色、在 595 nm 吸光增強；配上 BSA 標準曲線 (0.25–1 mg ml⁻¹) 換算成 µg ml⁻¹，給下游使用。
4. 工具與材料: 
   - **Neonatal rat ventricle**: 新生大鼠心室組織，是研究人員拿心臟纖維母細胞與心肌細胞的標準源頭。
   - **Trypsin (0.05%, 4 °C overnight)**: 蛋白酶；過夜冷消化鬆開組織內的細胞間連結。
   - **Collagenase Type II**: 專門切膠原蛋白纖維的酵素；37 °C × 4 次 × 10 min 消化把細胞從膠原基質釋放。
   - **Differential adhesion (1 h)**: 利用 CF 1 小時內貼壁、CM 不貼壁的速度差，分離兩種細胞。
   - **Passage (≤ 3)**: CF 傳代上限；超過 3 代後會轉化成 myofibroblast、EV 組成跑掉。
   - **EVs-depleted FBS**: 已預先離掉自身 EV 的胎牛血清；避免牛源 EV 污染 CF 自分泌的 EV。
   - **Conditioned medium**: 餵過細胞的培養液，富含細胞分泌物 (本研究主要是 EV)。
   - **Aqueous Two-Phase System (ATPS, PEG/DEX)**: 兩種高分子在水裡自動分相，EV 優先進入 DEX 下相、雜蛋白進入 PEG 上相，是溫和的 EV 分離法 (ref [76])。
   - **Ultracentrifugation (UC)**: 傳統 EV 分離法；100 000 × g 數小時，會擠壞 CD9/CD63/CD81 與造成 EV 聚集，本研究刻意避開。
   - **0.22 µm filtration**: 最終過濾步驟，擋住所有 > 0.22 µm 的細胞碎屑與蛋白聚集團塊，奈米級 EV 順利通過。
   - **Bradford assay (refs [77,78])**: 用蛋白染料在 595 nm 吸光改變來定量蛋白；本研究以此估算 EV 濃度。
5. 與此篇文章的關係: 
   在《Hybrid extracellular vesicles-liposome incorporated advanced bioink to deliver microRNA》這篇文章中，作者為了拿到帶有「CF 專屬地址貼紙」的 EV 作為混血奈米袋子的靶向能力來源，採用了 ATPS (兩相水相分離) 取代傳統超高速離心。它解決了 UC 把 EV 表面 CD9/CD63/CD81 蛋白擠壞、無法保留靶向能力的瓶頸，為下游 Module 3 的 EV-Liposome 膜融合提供膜蛋白完整、可量化濃度的 EV 原料。
