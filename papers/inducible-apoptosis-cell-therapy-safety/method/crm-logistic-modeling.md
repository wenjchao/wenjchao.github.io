# 連續再評估（Continual Reassessment Method, CRM）之 Logistic 劑量–反應建模

1. 引用自哪篇 paper: inducible-apoptosis-cell-therapy-safety
2. Outline (任務主線): 連續再評估（Continual Reassessment Method, CRM）之 Logistic 劑量–反應建模
3. Method:
      作者事先在紙上畫一條 S 型曲線——橫軸是 T 細胞劑量、縱軸是「打了這個劑量會出現嚴重毒性 (dose-limiting toxicity, DLT) 的機率」，這叫 logistic 劑量–反應曲線 $p(x) = \frac{1}{1+e^{-(a+bx)}}$，兩個參數 $a$、$b$ 就能同時決定曲線位置與陡度。開始時這條曲線只是猜的 (先驗)。每收完一位病人的結果 (有沒有 DLT)，就把「新的相信 = 舊的相信 × 新資料的貼合度」的貝葉斯公式套上：先驗乘上「假設曲線就長這樣，這位病人在此劑量下沒出/出了 DLT 的機率」，重新正規化得到後驗，S 型曲線隨之微調。然後看哪個劑量水準的機率最接近事先設定的目標毒性率 (例如 20-30%)，下一位病人就打那個劑量。走完幾位病人後，曲線會逐漸鎖定在真正的最大耐受劑量 (MTD) 附近。作者用的是 Piantadosi 等人 1998 年 Cancer Chemother Pharmacol 的 modified CRM 版本。
   為什麼不用比較熟悉的 3+3 設計？因為 3+3 每一級要 3 或 6 位病人才能決定往上或往下，過去劑量的資訊只能用在「這一級要不要退」，不會傳遞到還沒試的下一級——5 位小孩的樣本規模在 3+3 邏輯下根本走不到最後幾個劑量水準。CRM 用一條連續曲線把所有病人的資料整合在一起，即使每級只有 2 人也能反覆更新曲線並預測沒試過劑量的毒性機率。作者同時架了兩道安全護欄：其一，相鄰兩位受試者強制間隔 >42 天，讓 GVHD 這類遲發毒性有完整觀察窗，否則模型會用「假陰性」資料誤估 MTD；其二，modified CRM 加上「相鄰劑量限制」，每次只能推進一格 (1×10⁶ → 3×10⁶ → 1×10⁷)，即使數學上算出更高的劑量最貼近目標毒性率也不准跳，把數學建議與兒科臨床安全綁在一起。
4. 工具與材料:
   - **Logistic 劑量–反應曲線**: $p(x) = \frac{1}{1+e^{-(a+bx)}}$，兩個參數決定「打某劑量出現 DLT 的機率」，天然被夾在 0-1 之間且單調上升。
   - **Dose-limiting toxicity (DLT)**: 臨床上定義的「嚴重毒性事件」，本試驗中對應到 GVHD 等 grade≥3 事件；作為 CRM 更新的觀測值。
   - **最大耐受劑量 (MTD)**: 使 DLT 機率貼近目標毒性率的劑量，是 CRM 想搜尋的目標。
   - **Bayesian prior/posterior 更新**: 先驗 × 新資料的貼合度 → 後驗；每收一位病人就用其 DLT 結果調整曲線位置與陡度。
   - **Piantadosi modified CRM (Cancer Chemother Pharmacol 1998)**: 本試驗採用的具體 CRM 版本，加入「相鄰劑量限制」等臨床護欄。
   - **Inter-patient interval >42 天**: 強制觀察窗，讓遲發 DLT (如 GVHD) 有時間顯現後再進入模型更新。
5. 與此篇文章的關係:
   在《Inducible Apoptosis as a Safety Switch for Adoptive Cell Therapy》這篇文章中，作者要在只招募 5 位兒童的嚴格倫理限制下找出 iCasp9-T 細胞的最大耐受劑量，因此改用 Piantadosi 修正版連續再評估法 (modified CRM)：吃進去的是每位病人的劑量與是否出現 DLT，吐出來的是持續更新的 logistic 劑量–反應曲線與下一位病人的建議劑量。它解決了傳統 3+3 在極小樣本下走不到後段劑量的瓶頸，讓 5 位受試者的資料仍能撐起「1×10⁶ → 3×10⁶ → 1×10⁷/kg」三級搜尋。
