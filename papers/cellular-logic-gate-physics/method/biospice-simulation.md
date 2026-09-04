# BioSPICE 生化電路動力學模擬

1. 引用自哪篇 paper: cellular-logic-gate-physics
2. Outline (任務主線): BioSPICE 生化電路動力學模擬
3. Method:
   面對「cI/λP(R-O12) 反相器整條 transfer curve 是死平線」這個壞消息，作者不是直接開始亂做突變，而是先用 BioSPICE (Weiss, Homsy & Knight 1999) 這套模擬工具排錯。BioSPICE 的名字借自電子工程界解電路方程式的 SPICE 模擬器，功能是把細胞內反應當一張電路圖來模擬：使用者把每個關鍵生化反應——repressor 結合 operator、cI 兩兩結合成 dimer、RNA 聚合酶轉錄基因、核糖體把 mRNA 翻譯成蛋白——都寫成一組帶速率係數的方程式，模擬器就會替你解出各種蛋白／mRNA 在穩態下的濃度，等於用電腦「重跑」一遍實驗會得到的 transfer curve。

   作者拿這套模型去問一個很具體的問題：「這條死線曲線，到底是哪個參數過強？」他們對兩個懷疑參數做敏感度掃描——一是 RBS 決定的 translation rate（同樣多 mRNA 能翻出多少蛋白），二是 cI 對 O_R1 的 binding affinity（cI 蛋白對 DNA 位點的抓握強度）。模擬結果一致指出：只要把任一項係數調小，整條 transfer curve 就會往「上」與「外」平移——「上」是同樣輸入濃度下輸出沒被壓那麼低，「外」是中段翻轉挪到更高的輸入濃度區間。從方程式的角度看，translation rate 出現在「mRNA × 係數 = 蛋白生成率」裡，係數調小等於同樣多 cI mRNA 只翻出更少 cI 蛋白；affinity 出現在「cI × 係數 = 結合機率」裡，係數調小等於同樣多 cI 只鎖住比例更小的 operator。兩個方向的效果加起來，就是把死線推回可分辨的 inverse sigmoid。

   如果沒有模擬先鎖方向，作者只能猜「該動 RBS、動 operator、動 promoter 強度、還是動降解速率」——每動一種都要做一批質體、跑一批 FACS，成本很高。模擬便宜、快，先讓電腦掃描所有懷疑參數看誰對曲線位移方向有效，實驗就只需覆蓋這幾個方向、且只做「單方向的階梯」(例如三個逐漸更弱的 RBS) 即可。順著模擬結果，作者在濕實驗上分別對這兩個參數各做一條改造路線：把 RBS 從最強版換成三個逐漸更弱的版本（Section 5.1）、對 O_R1 做定點突變降低 cI 抓握力（Section 5.2）。Figure 11 與 Figure 12 的結果都符合模擬預測的平移方向，證明「模擬鎖方向、實驗定數量」這個 loop 可行。

   另一方面，作者刻意不把 BioSPICE 當「絕對數值預測器」用。生化反應的速率係數在文獻中常有數量級的不確定 (同一 RBS 在不同 mRNA 環境下強度差 10 倍以上都常見)；若照模擬給的絕對 transfer curve 位置直接挑「該換哪個 RBS」，很可能挑到完全錯的版本。作者的自覺處理是只信「參數→曲線位移方向」這種相對關係，實驗端則準備一個階梯 (三檔 RBS 或 1/2/3 bp 突變) 掃過去，讓實驗自己找到甜蜜點——這讓 Genetic Process Engineering 從盲目試錯升級為模型指導的定向改造，同時不倚賴模型過度自信。

4. 工具與材料:
   - **BioSPICE**: 一套把細胞內生化反應當電路節點模擬的動力學工具 (Weiss, Homsy & Knight 1999)，名字借自電子工程界的 SPICE；本論文用來預測參數改造方向。
   - **生化反應方程組**: 包括 repressor 結合 operator、cI 二聚化、轉錄、翻譯的一組帶速率係數的方程式，是 BioSPICE 的輸入。
   - **translation rate**: RBS 決定的轉譯速率，出現在「mRNA × 速率係數 = 蛋白生成率」的方程式裡，是模擬掃描的第一個關鍵參數。
   - **repressor-operator binding affinity**: cI 蛋白對 O_R1 DNA 位點的抓握強度，出現在「cI × 係數 = 結合機率」的方程式裡，是模擬掃描的第二個關鍵參數。
   - **參數敏感度掃描**: 在模擬中只動單一參數看 transfer curve 如何平移的做法，用來鎖定濕實驗要動的方向，而不用來預測絕對數值。
   - **曲線「向上、向外」平移**: 模擬預測的方向指標：「上」= 同樣輸入下輸出沒被壓那麼低，「外」= 中段翻轉挪到更高輸入濃度區間。

5. 與此篇文章的關係:
   在《The Device Physics of Cellular Logic Gates》這篇文章中，作者為了決定改造 cI/λP(R-O12) 反相器時該動哪個參數，採用了 BioSPICE 生化電路動力學模擬。這個方法把細胞內反應寫成一組帶速率係數的方程式、模擬 transfer curve 對每個參數的敏感度，指出「降低 translation rate」與「降低 repressor-operator affinity」都能把死線推回 inverse sigmoid，直接為下游 Section 5.1 的 RBS 替換與 5.2 的 O_R1 定點突變兩條實驗路線提供方向，避免盲目大範圍突變。
