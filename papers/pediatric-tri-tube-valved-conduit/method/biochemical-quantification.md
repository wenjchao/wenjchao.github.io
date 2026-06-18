# 組織生化定量（膠原、總蛋白、DNA、鈣）

1. 引用自哪篇 paper: pediatric-tri-tube-valved-conduit
2. Outline (任務主線): 把 histology 的「眼睛印象」量化成 collagen / protein / cell / Ca²⁺ 密度，以判斷 root 與 leaflet 在不同時間點是否真的有生長、重細胞化與鈣化。
3. Method:

膠原蛋白沒辦法直接秤，因為它和其他蛋白混在組織裡分不開。但膠原蛋白有一個獨家胺基酸叫羥脯胺酸 (hydroxyproline)，幾乎不出現在其他蛋白中——它是 proline 翻譯出來後再被 prolyl hydroxylase 在膠原蛋白特有的 Gly-X-Y 序列上加 -OH 修飾而來，所以只有膠原蛋白才會帶這個胺基酸。Hydroxyproline 固定佔膠原蛋白約 13.4% 的重量。作者把組織水解成胺基酸後，用化學顯色法量出 hydroxyproline 量，再乘以換算係數 7.46 (= 1/0.134) 得到膠原蛋白重量（Stegemann & Stalder 1967）。

總蛋白量則用 ninhydrin assay：茚三酮 (ninhydrin) 遇到一級胺基會反應產生鮮豔的紫藍色 (Ruhemann's purple)，紫色深淺與胺基酸總量成正比，水解後總胺基酸量就近似於總蛋白量；這個指標讓作者能算「膠原佔總蛋白的比例」。細胞密度則靠 DNA 定量：Hoechst 33258 染料鑽進 DNA 雙螺旋後在 460 nm 發強螢光，亮度與 DNA 質量成正比；因為每顆哺乳動物細胞約含 7.6 pg 雙股 DNA (Kim & Mooney 1998)，把測到的 DNA 總量除以 7.6 pg，就推出組織裡有幾顆細胞 (cellularity)，回答宿主細胞有沒有真的進駐 valve 內部。

鈣含量的測法比較迂迴。組織裡的鈣不是游離的 Ca²⁺，而是和磷酸根結合成磷酸鈣晶體（羥基磷灰石），緊緊嵌在蛋白基質裡，直接用顯色試劑根本碰不到。所以要先把組織冷凍乾燥 (lyophilized) 秤乾重，再用 6 M HCl 在 110 °C 連續水解 20 小時——這個時間是經驗值，能確保所有磷酸鈣晶體都被分解、Ca²⁺ 全部釋放，水解只做 6 小時會留下未拆解的晶體、鈣含量被低估；加 0.8 體積 6 M NaOH 中和強酸，最後用商品化的顯色試劑盒 (Calcium Detection Assay Kit, abcam ab102505) 與 Ca²⁺ 反應產生有色化合物、量吸光值。

為什麼要同時測這四種指標？因為它們各自回答一個關鍵問題——膠原蛋白量回答「支架材料夠不夠」、總蛋白量讓你算「膠原佔總蛋白的比例」可區分『全是膠原但細胞死光』還是『細胞活的新蛋白還在增加』、DNA 推得 cellularity 回答「宿主細胞有沒有真的住進去」、鈣含量回答「有沒有走上鈣化失效的老路」。膠原與 DNA 同時增加、鈣低，才能宣稱真生長；單看一個指標都會誤判。所有結果都除以 mg dry weight，因為活組織重量大部分是水分 (40-90%)，wet weight 易受擠水與孵育時間影響，乾重才能跨樣本、跨時間點直接比較。

4. 工具與材料:

   - **Hydroxyproline assay**: 量膠原蛋白特有的胺基酸 hydroxyproline，再乘 7.46 換算回膠原蛋白質量。
   - **7.46 mg collagen / mg hydroxyproline**: Stegemann & Stalder 1967 確立的換算係數，因 hydroxyproline 約佔膠原蛋白 13.4% 重量。
   - **Ninhydrin assay**: 茚三酮與一級胺基反應產生紫藍色 (Ruhemann's purple)，量總胺基酸 ≈ 總蛋白量。
   - **Hoechst 33258 fluorometric assay**: 染 DNA 的螢光定量法，460 nm 螢光強度與 DNA 質量成正比。
   - **7.6 pg DNA / cell**: Kim & Mooney 1998 的標準換算，把 DNA 質量轉成細胞數 (cellularity)。
   - **6 M HCl, 110 °C, 20 hr 水解**: 強酸高溫水解溶解羥基磷灰石晶體，把鈣鹽全部釋放成自由 Ca²⁺。
   - **Calcium Detection Assay Kit (abcam ab102505)**: 商品化的鈣顯色試劑盒，與 Ca²⁺ 反應產生有色化合物供吸光度定量。
   - **Per mg dry weight**: 結果除以乾重歸一化，排除含水量差異，可跨樣本與時間點比較。
   - **Lyophilized tissue**: 冷凍乾燥後的組織，提供穩定的乾重基準與後續強酸水解材料。

5. 與此篇文章的關係:

這篇 paper 在生長羊模型中追蹤工程肺動脈瓣 52 週，必須回答一個關鍵問題：valve 直徑變大究竟是「真正跟著小孩長大的 somatic growth」，還是「動脈瘤式擴張」、「鈣化失效」或「單純細胞遷入」？histology 染色只能給定性印象，無法區分這些情境，所以作者用四種生化定量——Hydroxyproline assay 算膠原蛋白、Ninhydrin assay 算總蛋白、Hoechst 33258 螢光定量換算細胞數、強酸水解後比色法量鈣——把組織組成轉成絕對密度數字。四個指標各自獨立回答一個問題（支架夠不夠、蛋白組成是否健康、宿主細胞有沒有住進去、有沒有鈣化），組合起來才能鎖定「膠原蛋白上升＋細胞密度上升＋鈣含量低」這個唯一符合真生長的特徵。這組生化數據與 echocardiography 看到的尺寸／功能變化、histology 看到的結構型態、單軸拉伸看到的力學 anisotropy 互相對照，構成 wet/dry 雙向驗證生長的核心一環；鈣含量改以 µg/mg dry weight 報告，也讓作者能用 one-sample t test 直接和 Flameng 2011 商用牛瓣的歷史鈣化數據對打，強化臨床轉譯論述。
