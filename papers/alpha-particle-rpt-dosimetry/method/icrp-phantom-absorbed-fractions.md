# α-particle 吸收分數估算：簡化假設與 ICRP voxelized phantom

1. 引用自哪篇 paper: alpha-particle-rpt-dosimetry
2. Outline (任務主線): 在缺乏 α-particle 吸收分數的傳統 Cristy-Eckerman phantom [18] 環境下，提供吸收分數的近似公式並過渡到 ICRP 110/133 體素化模型，特別處理骨髓 trabecular bone surface 的 cross-dose。
3. Method:
要算「α 從源組織射出之後有多少能量落在靶組織」(absorbed fraction $\phi$)，研究者必須先有一個「標準人體電腦娃娃」(anthropomorphic phantom) 當坐標系，然後用蒙地卡羅模擬「放一萬顆 α 出來、逐顆追蹤路徑、看最後落在哪」。問題是早期 Cristy-Eckerman 那一代娃娃 [18] 只有 photon 跟 electron 的吸收分數表，沒有 α 的表可查。作者群當時就用了 Eq.5 的捷徑簡化假設：「α 射程只有 50–100 μm，就假設它全部留在源組織自己身上 (self-dose=1)、完全不跑到隔壁 (cross-dose=0)」。對大多數軟組織器官這個假設夠準，因為兩個器官之間距離遠大於 α 射程；但這條捷徑會在「源靶距離跟 α 射程同數量級」的器官完全失效。

骨小樑是一張立體網狀的骨頭，網眼塞滿造血用的「活性骨髓 (trabecular active marrow, TAM)」；網的表面那 10 μm 薄層叫「骨小樑內骨膜 (trabecular bone endosteum, TBE)」，正是 ²²³Ra 與 ²²⁷Th 等骨向 α 藥停靠的位置。骨網孔洞約 50–1000 μm、跟 α 射程同數量級，TBE 距離 TAM 中央可能只有 5–10 μm；所以從 TBE 射出的 α 會直接穿過去打到造血細胞 (cross-dose)。Watchman et al. 2005 [21] 用蒙地卡羅算出來的數字 (Figure 5)：²²⁷Th 衰變鏈的 α 能量為 5.5–7.5 MeV，平均會有 20–22% 的能量從 TBE 落到 TAM（cross-dose 吸收分數 $\phi(TAM\leftarrow TBE)\approx 0.20\text{–}0.22$，self-dose $\phi(TAM\leftarrow TAM)<1$）。若硬套 Eq.5 的「α 不跨組織」捷徑，骨髓毒性會被嚴重低估，臨床會以為還能加劑量、實際卻會發生骨髓抑制。

解法是過渡到新一代「體素化娃娃」(voxelized phantom)。ICRP Publication 110（Menzel 2009 [19]）改用真實成年男女的 CT 影像，把人體切成數百萬個 1 mm 體素，每格都有組織種類；接著 ICRP Publication 133（Bolch 2016 [20]）在這個娃娃上顯式用蒙地卡羅算 α 與 electron 在每對組織之間的吸收分數，列成查表。對 αRPT 來說，這套娃娃是目前唯一能涵蓋 α 在人體所有組織的標準工具，也是腎臟皮質、唾液腺、骨髓等小尺度位置劑量計算的基礎；繼續用 Cristy-Eckerman 等於把 αRPT 限縮成「整顆器官劑量」的粗略估算，無法支援 §3-D 的 macro-to-micro 流程。
4. 工具與材料:
- **Cristy-Eckerman phantom [18]**: 1987 年的幾何拼裝標準人體模型；只附 photon 與 electron 的吸收分數，沒有 α 表。
- **Eq.5 簡化假設**: $\phi=1$ 若 $r_T=r_S$，$\phi=0$ 若 $r_T\ne r_S$；早期 αRPT 因缺 α 吸收分數表而採用的捷徑。
- **Trabecular active marrow (TAM)**: 塞在骨小樑網眼裡的活性造血骨髓，是 α 骨髓毒性的關鍵靶。
- **Trabecular bone endosteum (TBE)**: 骨小樑表面 10 μm 薄層內骨膜；²²³Ra 與 ²²⁷Th 等骨向 α 藥的主要停靠位置。
- **Watchman et al. 2005 吸收分數表 [21]**: 用蒙地卡羅算出 ²²⁷Th 衰變鏈 α (5.5–7.5 MeV) 從 TBE 落到 TAM 的吸收分數 0.20–0.22。
- **ICRP Publication 110 體素化娃娃 [19]**: Menzel 等 2009 年發布；用真實 CT 影像切成數百萬個 1 mm 體素的標準成年男女模型。
- **ICRP Publication 133 吸收分數表 [20]**: Bolch 等 2016 年發布；在 ICRP 110 娃娃上顯式用蒙地卡羅算 α 與 electron 對所有組織的吸收分數。
5. 與此篇文章的關係:
在《Dosimetry, Radiobiology and Synthetic Lethality: Radiopharmaceutical Therapy (RPT) with Alpha-Particle-Emitters》這篇文章中，作者為了讓 §3-A 的 MIRD 公式能在真實人體上落地，採用了 ICRP 110/133 體素化娃娃取代舊的 Cristy-Eckerman 模型。它解決了「早期模型只有 photon/electron 的吸收分數、骨向 α 藥的骨髓 cross-dose 嚴重被低估」的瓶頸，吃進 §3-A 公式需要的源-靶幾何，產出涵蓋 α 與 electron 的吸收分數查表，供後續按器官計算 $D_\alpha$、再進入 macro-to-micro 流程使用。
