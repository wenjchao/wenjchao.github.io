# γH2AX 免疫螢光焦點影像比較 photon vs α-particle 之 DSB 痕跡

1. 引用自哪篇 paper: alpha-particle-rpt-dosimetry
2. Outline (任務主線): 直接視覺化 α-particle 與低 LET photon 在細胞核內造成 DSB 的空間分布差異，佐證 αRPT 引發局部高密度、難修復的 DSB 群集。
3. Method:
為了把 α 跟 γ 的 DSB 分布差異「直接拍出來」，作者跟合作者 Hong Song 在 MCF7 乳癌細胞上做了一組 γH2AX 免疫螢光焦點影像對照（Figure 3C；方法學細節呼應 Schipler & Iliakis, Nucleic Acids Res 2013）。原理是：DNA 雙股斷裂發生後幾分鐘內，細胞會把斷裂點附近的組蛋白 H2AX（DNA 平常纏繞在它上面）第 139 號絲胺酸磷酸化，形成 γH2AX 這個「正在搶修」的旗標。一個 DSB 大約會在周邊幾百 kb 範圍內貼上一片 γH2AX、吸引修補蛋白聚集。作者用一支會專門認 γH2AX 的抗體加上螢光分子染色，每個亮點 (focus) 就對應一個 DSB 周邊正在被修補的位置。挑「照射後 20 min」這個時間點固定染色不是隨意的：再早一點訊號還沒成形、再晚一點低 LET 損傷已經修掉、γH2AX 被去磷酸化、剩下的是「修補機篩選過的子集」。20 min 剛好讓訊號清楚浮現、又還沒被修補進度污染，最能反映「兩種射線剛打完留下的 DSB 空間分布」原貌。

實驗分兩條 arm 同時做。低 LET arm 用 ¹³⁷Cs irradiator 給 8 Gy 光子；high LET arm 把細胞泡在 8 μCi/ml ²¹³Bi-labeled antibody 裡讓 α 粒子原地衰變。為什麼劑量不嚴格配對？因為這個實驗的目的是「定性視覺化」——讓讀者一眼看出兩種射線的 DSB 空間分布長相不同，而不是量化哪邊的 DSB 比較多。兩 arm 的劑量只要各自落在「20 min 能看到足量焦點、亮點不太擠也不太稀疏」的範圍即可。Figure 3C 左圖（γ）顯示 MCF7 細胞核內 γH2AX 亮點細小、均勻散布在整個細胞核裡——這對應 Figure 3B 畫的低 LET 離子化軌跡：能量稀稀疏疏沿路徑沉積，DSB 隨機落在 DNA 上各處。右圖（α）的亮點則顯著聚成一條條線狀群——對應 4 MeV α 的高 LET 軌跡：能量在極短距離內密集沉積，沿粒子穿過 DNA 的軌跡製造一連串相鄰 DSB，γH2AX 標記也跟著串成「會發光的麥克筆痕跡」。

這個「軌跡狀 vs 灑胡椒粉」的視覺差異不只是好看而已——它是 §2-A、§2-B 那些 RBE 行為的分子根源。稀疏分布的 DSB 周邊還是完整 DNA，修補機不管走 NHEJ 還是 HR 都有完整模板可用、有對的斷端可以配對，修起來又快又正確。但軌跡狀的密集 DSB 不一樣：同一小段 DNA 上有好幾個斷裂同時發生，斷成幾段碎片漂在原地。NHEJ 要把斷頭接回去時，根本分不清哪兩個斷頭原本是一起的，硬接很容易接錯；HR 要找姊妹染色體當模板時，模板那邊對應位置可能也被 α 打傷，找不到乾淨的範本。結果就是修補機要嘛接錯（留下永久突變）、要嘛根本接不起來、要嘛直接放棄讓細胞死。這直接解釋了 §2-A 為什麼 α 沒有 sublethal damage repair（給時間休息也修不好），以及 §2-B 為什麼把修復組長敲掉之後 RBE 會跳到 8.6 / 15.6（原本就難修，再把工人撤掉就完全沒救）。

「20 min 立刻固定」是這個對照能成立的關鍵時序。如果不及時固定、放 2–4 小時再染色，細胞繼續活著就會啟動修補機：低 LET γ 打出來的簡單 DSB 在 2–4 小時內已經修掉一大半、γH2AX 標記消失；α 打出來的軌跡狀焦點雖然修得慢，邊緣相對單純的 DSB 也會被陸續清掉。結果是兩 arm 的差異被同時壓低，「α 帶來高密度難修 DSB 群集」這個主結論的視覺證據就被洗掉。所以這個時間點與固定動作不是流程細節，而是讓 DSB 被凍結在「剛打完、還沒被修補機修動」狀態的必要條件。
4. 工具與材料:
- **γH2AX**: DSB 發生後 H2AX 第 139 號絲胺酸被磷酸化的標記，吸引修補蛋白聚集，是 DSB 的可視旗標。
- **immunofluorescence**: 用抗體加螢光分子染特定蛋白、再用螢光顯微鏡照細胞的標準染色法。
- **MCF7**: 本實驗用的乳癌細胞系；γH2AX 焦點染色的常見細胞背景。
- **¹³⁷Cs-irradiator, 8 Gy**: 低 LET arm 的光子照射條件，γH2AX 染色教科書級常用劑量。
- **²¹³Bi-labeled antibody, 8 μCi/ml**: high LET arm 的 α 照射條件，孵育 20 min 後染色。
- **post-irradiation 20 min fixation**: 照射後 20 min 立刻固定細胞、染色，把 DSB 凍結在「剛打完、修補機尚未動」的狀態。
- **track-like foci**: 高 LET α 沿粒子軌跡產生的密集 γH2AX 焦點串，呈線狀分布。
- **clustered DSB (complex lesion)**: 同一小段 DNA 上多個 DSB 同時發生的結構，修補機難以找到正確配對的斷端與乾淨模板。
5. 與此篇文章的關係:
在《Dosimetry, Radiobiology and Synthetic Lethality: Radiopharmaceutical Therapy (RPT) with Alpha-Particle-Emitters》這篇文章中，作者為了把 §2-A、§2-B 觀察到的「α 沒 sublethal repair、且修復路徑缺損時 RBE 暴漲」的現象視覺化成可驗證的分子證據，採用了「γH2AX 免疫螢光焦點影像」在 MCF7 細胞核裡直接拍下兩種射線的 DSB 空間分布（Figure 3C，Hong Song unpublished；方法呼應 Schipler & Iliakis, Nucleic Acids Res 2013）。它解決了「RBE 數字無法說明 DSB 為何難修」的瓶頸，產出 α 訊號的軌跡狀焦點影像，作為下游 αRPT 為何能克服腫瘤抗藥機制的機制圖證據。
