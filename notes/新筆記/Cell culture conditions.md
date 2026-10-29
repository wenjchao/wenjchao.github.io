# Cell culture conditions

## 內文
1. Media composition of general cell culture 
   1. Carbon source: ENERGY! Often glucose
   2. Buffering system: Cells need a pH of 7.2 – 7.4 to live
      1. Bicarbonate 需要 5% CO₂，離開培養箱後培養基會偏鹼（長時間在箱外操作時，改用 HEPES 或不依賴 CO₂ 的培養基）（課外）
   3. pH indicator: Phenol red
      1. 如果要做螢光顯微鏡、螢光或比色檢測（MTT、盤式讀值）：會增加背景訊號（課外）
      2. 雌激素敏感的細胞（如 MCF-7）：phenol red 有微弱的類雌激素作用，會干擾荷爾蒙相關實驗（課外）
   4. Serum: mixture of sugar, salts, lipids, and growth factors
      1. Batch variation（課外）
      2. Not GMP（課外）
   5. Metabolites and vitamins: amino acids, etc
   6. Antibiotics (OPTIONAL!)
      1. 會掩蓋低度汙染，汙染可能悄悄擴散（課外）
2. Pluripotent stem cell culture
   1. 之前人們會在 fibroblasts（mouse embryonic fibroblasts）上養 pluripotent stem cells，因為 fibroblasts 會分泌 FGF2（bFGF）和 TGFβ，讓幹細胞維持 pluripotent
   2. Feeder(fibroblasts)-free culture 使用適當的 medium 和 matrix
      1. 人類和小鼠靠不同的訊號維持 pluripotency：人類 PSC 的狀態比較像「著床後」的細胞，小鼠 ESC 比較像「著床前」

         | | Human ESC / iPSC | Mouse ESC |
         |---|---|---|
         | 維持 pluripotency 的關鍵 | FGF2、TGFβ1 | LIF：活化 STAT3，促進 self-renewal |
         | Medium | mTeSR 等 pluripotency maintenance medium | 含 FBS 的 medium |
         | 養在什麼上面 | Matrigel 或 Geltrex：比較完整的 basement membrane，含 laminin、collagen IV、heparan sulfate proteoglycans、growth factors | Gelatin：用 collagen 做的簡單塗層 |
         | 傳代時 | 加 ROCK inhibitor：調節 actin cytoskeleton，降低解離造成的 apoptosis | |

      2. 小鼠 ESC 收到 FGF 反而會開始分化，所以小鼠的關鍵是 LIF，不是 FGF2（課外）
   3. Essential 8 medium（課外）：DMEM/F12、L-ascorbic acid、selenium、transferrin、NaHCO₃、insulin、FGF2、TGFβ1
   4. 維持得好不好要定期檢查：長出已分化的 colony 就不好；另外檢查 pluripotency markers、karyotype、mycoplasma（見 [[Cell state control]] 的 6. Cell characterization）
