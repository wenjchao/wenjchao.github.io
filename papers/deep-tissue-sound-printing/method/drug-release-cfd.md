# 藥物釋放 CFD 模擬（Navier–Stokes + 對流擴散）

1. 引用自哪篇 paper: deep-tissue-sound-printing
2. Outline (任務主線): 藥物釋放 CFD 模擬（Navier–Stokes + 對流擴散）
3. Method: 
   為了論證「把載藥 hydrogel 精準印在腫瘤上比直接打針有效」，作者在電腦裡跑一種「用流體力學算藥物如何被沖走的數值模擬」(computational fluid dynamics, CFD)，工具是 COMSOL Multiphysics 的有限元素分析。模擬同時解兩條方程：(1) 不可壓縮 Navier–Stokes 方程 $\rho(\partial v/\partial t + (v\cdot\nabla)v) = -\nabla p + \mu\nabla^2 v$, $\nabla \cdot v = 0$（式 4），算出膀胱腔內每一點的流速 $v$ 與壓力 $p$；(2) 對流–擴散方程 $\partial c/\partial t + v\nabla c = D\nabla^2 c$（式 5），把流速塞進去，算藥物濃度 $c$ 隨時間怎麼分布。$v\nabla c$ 是水流帶著藥跑（像粉末被沖下游），$D\nabla^2 c$ 是藥分子自己擴散（從濃處往稀處跑），$D = 1 \times 10^{-10}$ m² s⁻¹ 是水溶性小分子典型值。三種幾何（直接注射、隨機表面 hydrogel、精準腫瘤上 hydrogel）的初始藥物濃度都標成 1，方便比較「過了多久還剩多少比例」；直接注射用的流速是 1 mm s⁻¹、2 分鐘灌完。
   
   為什麼把藥包進 hydrogel 印在腫瘤上能比直接打針撐更高的局部濃度？直接注射時，藥物分子像粉末撒進河裡，被膀胱內的尿液流動一沖就散開，腫瘤附近的濃度幾秒鐘就掉到很低。包進 hydrogel 後，藥物分子要先從凝膠網絡裡擴散出來才會進入膀胱液，等於多了一層緩釋屏障；同時 hydrogel 本身是固體一塊貼在腫瘤上，水流沖不走它。CFD 直接畫出來：hydrogel 版的局部濃度在 10 分鐘、30 分鐘後仍維持高位，注射液版很快被沖光（fig. S27）。
   
   為什麼要特別比「隨機表面」與「精準腫瘤上」兩種 hydrogel 幾何，不直接比「有 vs 沒有 hydrogel」？因為這樣的二分法雖然能看出 hydrogel 緩釋的價值，卻分不清贏在「有緩釋屏障」還是「有貼著腫瘤」。作者特地加一組「隨機在膀胱表面列印 hydrogel」當中間對照：同樣有 hydrogel 緩釋、但沒貼在腫瘤上。若它仍輸給「精準腫瘤上」那組，就直接證明 DISP 的「影像導引精準定位」本身在臨床上有額外價值，不是 hydrogel 屏障一個人的功勞。
   
   如果跳過 CFD 直接做動物實驗，每隻動物的膀胱容積、尿液流速、腫瘤位置都不一樣，量到的「腫瘤旁濃度」差異可能來自個體差而不是給藥策略本身。更糟的是，IVIS 之類的活體成像只看「亮在哪」，看不到流場——觀察到隨機表面組輸給精準靶向組時，無法區分是「藥被沖走」還是「藥根本沒貼到腫瘤」。CFD 在純物理條件下隔離流場與幾何兩個變數，先乾淨拆解出機制，再用最少動物驗證關鍵預測。
4. 工具與材料: 
   - **Computational fluid dynamics (CFD)**：用流體力學算藥物如何被流場帶走、擴散的數值模擬；這裡用 COMSOL 的 FEM 實作。
   - **Incompressible Navier–Stokes equation (式 4)**：$\rho(\partial v/\partial t + (v\cdot\nabla)v) = -\nabla p + \mu\nabla^2 v$, $\nabla \cdot v = 0$，描述膀胱內每一點的流速與壓力。
   - **Convection-diffusion equation (式 5)**：$\partial c/\partial t + v\nabla c = D\nabla^2 c$，把藥物如何被水流帶走（對流）與如何自己擴散（擴散）兩種機制疊在一起算。
   - **Diffusion coefficient (D)**：分子靠濃度差自己跑開的能力，本模擬取 $D = 1 \times 10^{-10}$ m² s⁻¹（水溶性小分子典型值）。
   - **Normalized concentration**：把三種給藥方式的初始藥物濃度都標成 1，公平比較「過了多久還剩多少比例」。
   - **Direct injection model**：對照組之一：以 1 mm s⁻¹ 流速、2 分鐘把藥液灌進膀胱腔；模擬中作為「無 hydrogel」基線。
5. 與此篇文章的關係: 
   在《Imaging-guided deep tissue in vivo sound printing》這篇文章中，作者為了論證「把載藥 hydrogel 精準印在腫瘤上」比「直接灌藥」或「隨機印一層」更能維持高局部濃度，採用了 COMSOL CFD 模擬。它解決了「光靠動物實驗難以拆解 hydrogel 緩釋與精準定位兩個機制」的瓶頸：吃進膀胱幾何與流速條件後，輸出三種給藥策略的時空濃度地圖，直接為下游的小鼠膀胱腫瘤 in vivo 列印實驗提供「為什麼這樣設計」的物理證據。
