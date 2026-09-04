# 核糖體結合位 (RBS) 序列工程

1. 引用自哪篇 paper: cellular-logic-gate-physics
2. Outline (任務主線): 核糖體結合位 (RBS) 序列工程
3. Method:
   作者把 cI/λP(R-O12) inverter 接上 B 節的量測電路後，量出來的是一條死板的平線 (Fig. 2)——就算把 IPTG 從最低撐到最高，輸出 EYFP 幾乎不動。診斷發現：即使前一段 p(lac) 被 lacI 完全鎖死，仍會漏出微量 cI mRNA；這微量 mRNA 又剛好碰上一個「特別會抓核糖體」的強效 RBS (Ribosome Binding Site，位於 mRNA 上、ATG 起始密碼子上游約 20 個鹼基以內的短序列，負責被核糖體較小的那一半 30S 亞基認出並卡上)，導致極少量的 mRNA 也能翻出足以完全壓死下游 λP(R-O12) 啟動子的 cI 蛋白，整條 transfer curve 因此被壓在零附近永遠不動。

   30S 亞基上有一段短小的 16S rRNA 尾端，會跟 mRNA 上的 RBS 進行鹼基配對；配對越「合」——例如典型的 Shine-Dalgarno 序列 `AGGAGG` 與 16S rRNA 尾端幾乎完全互補——30S 就越容易停在 RBS 上、越快組裝完整核糖體、每分子 mRNA 單位時間翻出的蛋白就越多。作者在下實驗手之前先用 BioSPICE (一種把 promoter 抑制、二聚化、轉錄、轉譯等生化反應寫成微分方程的細胞電路模擬平台) 掃過參數空間，模擬預測「單獨降低 RBS 決定的 translation rate」會把整條 transfer curve 沿右上方向平移：同樣的 IPTG 濃度下 cI 少了、下游被抑制得沒那麼死，YFP 被推高 (縱軸向上)；要把輸出壓到相同低水準得餵入更多 IPTG，臨界點右移 (橫軸向右)。這個方向指引作者接下來只要「換弱一點的 RBS」就有機會把原本壓在零的死線推回可判別的反 S 型，避免大範圍隨機突變的成本。

   作者從 Gardner, Cantor & Collins 2000 Nature 的 toggle switch 論文借來三條較弱的 RBS 序列。原本強效 RBS 是 `ATTAAAGAGGAGAAATTAAGCATG`，逐步替換為 RBS-1 (`TCACACAGGAAACCGGTTCGATG`)、RBS-2 (`TCACACAGGAAAGGCCTCGATG`)、RBS-3 (`TCACACAGGACGGCCGGATG`)——底線那三個字母 ATG 是起始密碼子，前面那段才是被替換的 RBS；每一條序列都變得更不像典型的 Shine-Dalgarno 共識，30S 越來越抓不牢、翻譯速率越壓越低。作者從 pINV-110 出發，僅置換 cI 上游那一段 RBS，得到 pINV-112-R1 (最強弱化)、pINV-112-R2、pINV-112-R3 (最弱) 三個衍生質體；cI 蛋白本體與 λP(R-O12) 啟動子一個字都不動。這樣的克制有兩個關鍵理由：一是把 transfer curve 的變化獨立歸因於「輸入蛋白產量」單一變因，不會與 cI 蛋白抓 DNA 的強度混淆 (那部分留給 D 節的 operator 定點突變處理)；二是 RBS 是可攜的通用改造菜單——同一組序列可以直接搬到未來任何一顆 inverter 上作曲線平移，改 cI 或啟動子則是特化改造。

   結果 (Fig. 11) 完全對上 BioSPICE 的模擬預測：三條較弱 RBS 都成功把死線推回明顯的反 S 型；其中 pINV-107/pINV-112-R1 (弱化最少) 對 IPTG 只有中等敏感度，另兩條較弱的則產出更陡的翻轉。為什麼要一次做三檔而不只挑一條？因為模擬只能給方向、算不出「弱化多少剛好」的絕對數值；三檔漸弱一次做出來，就能同時看到「弱化不足還是壓在零」「弱化剛好呈漂亮反 S 型」「若再繼續弱化下去會走向另一極端」的邊界在哪。這裡的另一端死線是：若 RBS 弱化過頭，即使 IPTG 加到最滿也做不出足以鎖死 λP(R-O12) 的 cI 濃度，輸出 YFP 會永遠停在高原、跟輸入無關，transfer curve 又變成一條「恆高」死線 (與原本的「恆低」死線相對)。三檔選擇正是覆蓋「太強」到「還沒太弱」的區間，才能同時避開兩端。

4. 工具與材料:
   - **RBS (Ribosome Binding Site)**: mRNA 上位於 ATG 起始密碼子上游、約 20 個鹼基以內的短序列，被核糖體 30S 亞基認出並卡上，決定該 mRNA 的翻譯速率。
   - **核糖體 30S 亞基**: 核糖體較小的那一半，其上的 16S rRNA 尾端會跟 RBS 做 Shine-Dalgarno 配對；配對越合，翻譯速率越高。
   - **Shine-Dalgarno-like 共識**: 典型 RBS 序列 (如 `AGGAGG`) 與 16S rRNA 尾端互補；序列越偏離此共識、30S 抓 RBS 越弱。
   - **四條 RBS 序列 (orig → RBS-1/2/3)**: 原始最強 `ATTAAAGAGGAGAAATTAAGCATG`；三條較弱版本取自 Gardner et al. 2000 Nature toggle switch，漸弱程度為 RBS-1 > RBS-2 > RBS-3。
   - **pINV-112-R1 / R2 / R3 質體**: 從 pINV-110 出發，僅置換 cI 上游 RBS 而構成的三個衍生質體，對應三檔漸弱的 RBS；cI 蛋白與 λP(R-O12) 啟動子維持不變。
   - **BioSPICE 生化電路動力學模擬**: 把 promoter 抑制、二聚化、轉錄、轉譯寫成微分方程的細胞電路模擬平台 (Weiss, Homsy & Knight 1999)；用來預測「調哪個參數會把 transfer curve 推到哪」，此處指出降低 translation rate 會讓曲線右上平移。
   - **Gardner et al. 2000 Nature toggle switch**: 三條較弱 RBS 序列的來源文獻；作者直接借用其序列作為現成的漸弱菜單。

5. 與此篇文章的關係:
   在《The Device Physics of Cellular Logic Gates》這篇文章中，作者要把死板不動的 cI/λP(R-O12) 反相器救成有反 S 型響應的合格邏輯閘。為此他們採用 RBS 序列工程，從 Gardner 2000 toggle switch 借三檔漸弱的 RBS 替換 cI 上游強效 RBS，構出 pINV-112-R1/R2/R3，解決了「強效 RBS 讓漏出的微量 mRNA 也翻出足以壓死下游啟動子的 cI」瓶頸。這一步吃 B 節量測電路對死線的診斷輸出，產出三條可用的 transfer curve，交給下游 O_R1 定點突變 (D 節) 做精修。
