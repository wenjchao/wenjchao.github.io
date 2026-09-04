# ECFP／EYFP 雙色讀值的跨通道歸一化

1. 引用自哪篇 paper: cellular-logic-gate-physics
2. Outline (任務主線): ECFP／EYFP 雙色讀值的跨通道歸一化
3. Method:
   作者要把「輸入蛋白量」和「輸出蛋白量」畫在同一張 transfer curve 上，但這兩個量分別由增強型青色螢光蛋白 (ECFP) 與增強型黃色螢光蛋白 (EYFP) 讀出。兩種螢光蛋白雖然都源自 GFP，但發光波段不同、需要不同的激發雷射與發射濾片，每產生一個光子的效率 (量子產率)、蛋白折疊到能發光的成熟時間也都不一樣。結果就是細胞裡實際有 100 份蛋白時，ECFP 通道可能讀出 300、EYFP 通道可能讀出 800，而且這條換算關係還帶彎，不是簡單的比例。

   作者的校正巧思是「同一個電路、只換輸出色」。他們準備兩個標定用質體 pINV-102 與 pINV-112-R1，上游完全相同——由 `p(lacIq)` 常開型啟動子把 lacI 表現量拉滿，再透過 `p(lac)` IMPLIES gate 讓外加 IPTG 濃度正相關於下游輸出蛋白量；差別只在下游輸出蛋白：pINV-102 是 EYFP、pINV-112-R1 是 ECFP。這樣一來，同濃度 IPTG 送進兩個質體理論上會產生等量的輸出蛋白，量到的差異就只剩「螢光通道換色」這一個變數。掃過同一組 IPTG 濃度後，Figure 5 就給出一張純粹反映通道偏差的對應表：同一份輸入蛋白量會分別對應多少 ECFP 亮度、多少 EYFP 亮度。作者刻意用「後續 inverter 實驗也會用的」常開 IMPLIES gate 拓撲來校正，是要讓對應表涵蓋下游會踩到的整個動態範圍，避免用外推法猜答案。

   有了這張對應表，量測 lacI/p(lac) inverter 時就有依據：ECFP 讀出的輸入蛋白量先透過查表換算成「同一份蛋白若改用 EYFP 標記會有多少亮度」，再與同一批細胞讀到的 EYFP 輸出放在同一個座標軸上比對，這樣畫出來的 Figure 9 才真的是「輸入蛋白量 vs 輸出蛋白量」而不是「ECFP 亮度 vs EYFP 亮度」。

   反過來說，如果跳過這一步歸一化，直接拿 ECFP raw 讀值當輸入軸、EYFP raw 讀值當輸出軸，兩色的非線性偏差就會被誤算成 inverter 的元件特性——看到 ECFP 300 對上 EYFP 800，你分不清是 inverter 真的把訊號放大了 2.7 倍，還是純粹兩色的量子產率不同造成的假象。跨 gate 比對時 (例如 lacI/p(lac) 與 cI/λP(R-O12)) 這層污染更致命：報出來的 gain 差異可能根本不是 repressor 本身的差異，而是通道偏差。

4. 工具與材料:
   - **ECFP / EYFP**: 增強型青色 / 黃色螢光蛋白 (Clontech 提供的 GFP 衍生物)，本論文分別用來標記 inverter 的輸入與輸出蛋白量。
   - **pINV-102**: 校正用雙質體之一，「p(lacIq) → p(lac) IMPLIES」下游輸出為 EYFP。
   - **pINV-112-R1**: 校正用雙質體之二，上游拓撲同 pINV-102，僅把下游輸出換成 ECFP。
   - **常開 IMPLIES gate 拓撲**: 作者選用的校正電路：`p(lacIq)` 常開型啟動子把 lacI 拉滿，再讓外加 IPTG 濃度透過 `p(lac)` IMPLIES gate 正相關於下游輸出蛋白量。
   - **CFP↔YFP 對應查表**: 掃描同一組 IPTG 濃度下兩個標定質體的螢光讀值，得到「同一份蛋白量分別對應多少 ECFP 與 EYFP 亮度」的查表 (Figure 5)。
   - **兩色螢光通道偏差**: ECFP 與 EYFP 因激發／發射光譜、量子產率、成熟時間不同而在同一份蛋白量上呈現非線性差異，是這套校正要剝離的干擾。

5. 與此篇文章的關係:
   在《The Device Physics of Cellular Logic Gates》這篇文章中，作者為了在同一張 transfer curve 上同時呈現 lacI/p(lac) inverter 的輸入與輸出，採用了 ECFP／EYFP 雙色跨通道歸一化。這個方法解決了兩種螢光蛋白因激發／發射光譜、量子產率、成熟時間不同造成的非線性偏差，把 pINV-102 與 pINV-112-R1 在同一組 IPTG 濃度下產生的螢光讀值做成查表，把後續 inverter 電路的 ECFP 讀值換算成 EYFP 等效強度，最終產出 Figure 9 那條可以直接讀出 gain = 4.72 的歸一化 transfer curve。
