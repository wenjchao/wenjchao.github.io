# 1H NMR、EPR、XPS 對聚合與配位的化學驗證

1. 引用自哪篇 paper: nanocrystal-confinement-blue-peleds
2. Outline (任務主線): 1H NMR、EPR、XPS 對聚合與配位的化學驗證
3. Method:
   三套化學探針分別逼近三個機制問題。質子核磁共振 (1H NMR, Bruker 400 MHz) 的原理是：氫原子核在強磁場下會以特定頻率共振，每種化學鍵環境裡的氫都有自己的『化學位移』（chemical shift），就像身分證號碼。乙烯基末端的氫（H 接在 C=C 雙鍵上）位移在 5.9–6.4 ppm 這個獨特區間；OEGA 一聚合，C=C 變飽和 C–C，這些氫就跑到 1–3 ppm 區，原本的乙烯峰會消失。樣品準備是把鈣鈦礦薄膜旋塗退火後刮下、重溶於氘代溶劑（DMSO-d6 或 CDCl3，氫被換成氘避免溶劑訊號蓋掉樣品），且 OEGA 濃度刻意放大提升訊噪比。電子順磁共振 (EPR) 是 NMR 的姐妹——只偵測『單一未成對電子』也就是自由基。為了量 AIBN 點火後產生的丙烯酸酯自由基中間態（壽命微秒級），作者用『自旋捕獲劑』DMPO (5,5-dimethyl-1-pyrroline N-oxide) 把短壽命自由基轉成壽命較長的氮氧加合物。實驗條件是 OEGA + DMPO 溶於 DMSO，加熱到 335 K，做 5/10/20 min 時間序列。

   EPR 結果有點反直覺：三個時間點都沒量到 DMPO 加合物訊號。乍看可能是『反應沒發生』，但這跟 NMR 結果（乙烯訊號消失）矛盾。正確解釋是丙烯酸酯自由基反應太快——根據 Barth et al. (Macromol. Rapid Commun. 2009) 文獻，這類自由基壽命落在微秒級，AIBN 一吐出自由基就立刻撞上下一個 OEGA、繼續鏈成長，根本沒時間跟 DMPO 反應。335 K (62 °C) 比 60 °C 退火稍高，確保 AIBN 完全進入熱分解區；做 5/10/20 min 三個時間點覆蓋反應不同階段，如果自由基壽命有秒到分鐘級應該至少被捕獲一次。三個時間點都無訊號反過來坐實『微秒級壽命』假設，也排除『AIBN 沒分解』或『DMPO 失效』兩個其他可能。對元件而言，『最終無殘留自由基』是好消息：殘留自由基會繼續攻擊鄰近分子、引發長期降解。

   XPS (X-ray Photoelectron Spectroscopy) 用 Kratos Axis Ultra (Al Kα, 150 W) 進行：X 射線打到樣品表面，把內層電子整顆打出來（光電效應），量這些電子的動能反推它們的『束縛能 (binding energy, BE)』。把 Pb2+ 想成『缺電子』的空盒子，OEGA 的氧把孤對電子塞給它後，Pb 周圍的電子密度增加；XPS 量的內層電子相對被原子核的拉力減弱，BE 向低能方向偏移。實驗結果：Pb 4f5/2 由 pristine 138.1 eV、Pb 4f7/2 143.0 eV 在 OEGA 處理後都往低 BE 偏移；Br 3d 也同樣偏移，反映晶格整體電子密度提升、Pb–Br 鍵離子性減弱。位移幅度雖小（0.1–0.3 eV）但可重現、且與 DFT 算出的 O–Pb 配位能定性吻合。鈣鈦礦表面不導電容易累積正電（charging effect）把整個譜往高 BE 偏移幾百 meV，所以作者把表面吸附碳氫殘留物的 C 1s 峰（真實 BE 已知為 284.8 eV）當『內標』校正——否則帶電造成的整體位移會被誤判成配位偽訊號。

   為什麼一個聚合反應要做三個技術？三者各自有盲區，必須拼起來才能涵蓋『機制完整鏈條』。NMR 只看終點：乙烯訊號消失等於 OEGA 已聚合，但不知過程中有沒有奇怪中間產物。EPR 看自由基中間態：但結果是『沒訊號』本身不足以證明反應發生——必須搭配 NMR 證明聚合確實發生，才能把『EPR 無訊號』反過來解讀為『反應太快、最終無殘留』。XPS 在完全另一條軸上——它證明 OEGA 跟 Pb2+ 之間有電子轉移、有配位鍵，但無法告訴你聚合有沒有完成。三者拼起來，才能同時回答：(a) 聚合完成 (NMR)；(b) 無殘留自由基 (EPR)；(c) 配位機制成立 (XPS)，剛好對應主線 (a)(b)(c) 三個機制宣稱。

4. 工具與材料:
   - **1H NMR (Bruker 400 MHz)**: 質子核磁共振，看乙烯質子峰 (5.9–6.4 ppm) 退火後消失，驗證 POEGA 形成。
   - **化學位移 (chemical shift)**: 氫原子在不同鍵環境下共振頻率不同，等於氫的『身分證號碼』。
   - **氘代溶劑 (DMSO-d6 / CDCl3)**: 把溶劑的 H 換成 D，避免溶劑訊號蓋住樣品訊號。
   - **EPR (Electron Paramagnetic Resonance)**: 偵測單一未成對電子，量自由基中間態。
   - **DMPO (5,5-dimethyl-1-pyrroline N-oxide)**: 自旋捕獲劑，把微秒級自由基轉為壽命較長的氮氧加合物。
   - **in-situ EPR / quasi-in-situ EPR**: 邊加熱邊量 (in-situ) 與不同加熱時間後取樣 (quasi-in-situ)，5/10/20 min 皆無訊號。
   - **XPS (X-ray Photoelectron Spectroscopy)**: Kratos Axis Ultra (Al Kα, 150 W)，量內層電子結合能反推配位電子轉移。
   - **C 1s 內標 (284.8 eV)**: 校正樣品表面帶電與儀器漂移的標準動作。
   - **Pb 4f5/2 (138.1 eV) / Pb 4f7/2 (143.0 eV)**: 鉛內層電子峰，OEGA 處理後向低 BE 偏移代表配位電子轉移。
   - **UPS (Ultraviolet Photoelectron Spectroscopy, He I)**: 同儀器以紫外光激發，分析 OEGA 處理前後功函數與能帶對齊。

5. 與此篇文章的關係:
   在《In situ nanocrystal confinement for efficient blue perovskite LEDs》這篇文章中，作者對 OEGA 的機制提出三項化學鍵級宣稱：聚合完成、無殘留自由基、O–Pb 配位。NMR + EPR + DMPO + XPS 這套組合解決了單一表徵不足以同時驗證『反應動態』與『電子層交互』的瓶頸，把上游 OEGA 配方的化學行為連到下游薄膜的光學與穩定性。
