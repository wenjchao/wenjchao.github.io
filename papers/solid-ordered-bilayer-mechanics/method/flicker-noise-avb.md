# Flicker noise 平均法 AVB

1. 引用自哪篇 paper: solid-ordered-bilayer-mechanics
2. Outline (任務主線): Flicker noise 平均法 AVB
3. Method:
   Flicker noise 平均法 (AVB) 跟 SA 拆解同一條 ξ(γ, t)，差別只在拆解的「基底」與「處理振幅的方法」。AVB 用 Legendre 多項式 P_n(cos γ) 當基底（方程式 7），把 ξ(γ, t) = ⟨B_0⟩ P_0(cos γ) + Σ_{n=2}^{n_max} B_n(t) P_n(cos γ)；之所以挑 Legendre 是因為它是球面上的自然基底——球面上的起伏標準展開就是球面諧波 Y_{l,m}，只考慮對軸對稱的模態時球面諧波退化成 Legendre 多項式 P_n(cos θ)。每個 P_n 對應一個 n 階球面起伏模式（n = 2 是橢圓化、n = 3 是梨形、n 越大越細碎）。每個模態 n 拿到一個隨時間變化的振幅 B_n(t)，AVB 對 |B_n|² 在時間軸上「直接平均」拿到 ⟨B_n⟩，再用方程式 8 解出 κ；同一條原始資料 SA 用直方圖、AVB 用平均，兩者互為獨立估計。protocol 來自 Pécréaux et al. 2004 (Eur. Phys. J. E, ref 22)。

   方程式 8 ⟨B_n⟩ = (2n+1)/(4π) · k_B T / {κ(n+2)(n−1)[σ̄ + n(n+1)]} 把 GUV 當成一顆充滿熱漲落能量的彈簧球：每個球面 n 階模態都從熱浴領一份能量 k_B T/2（等分能定理），這份能量被存進「彎曲」與「張力」兩個位能槽——κ 越大彎這個模態要花越多能量、振幅就越小；σ̄ 越大膜被拉得越緊、同樣抑制振幅。前置的 (2n+1)/(4π) 純粹是 Legendre 基底的歸一化常數。實作上把多個 n 的 ⟨B_n⟩ 對 n 畫圖，再用方程式 8 同時對 κ 與 σ̄ 做最小平方擬合就直接得到 κ。對 |B_n|² 做時間平均的好處是計算快、把雜訊壓低，高頻模態的擬合穩定；代價是丟失分佈尾部資訊。所以 AVB 給穩定的整體平均強度、SA 給分佈形狀是否真的單指數，兩條路徑同時跑互為背書：κ 一致即排除統計假設造成的偏差，不一致就提示 GUV 已超出 Helfrich 模型射程。

   方程式 8 同時擬合 κ 與 σ̄ 兩個未知數，至少需要好幾個模態的 ⟨B_n⟩ 才能解出；如果 n_max 取太低，例如只擬合到 n = 4，擬合自由度不足、兩個未知數會強耦合彼此抵銷、數值容易跑掉。GUV 樣本數太少同樣慘——每顆 GUV 形狀本就有個別差異，特別在固相連方塊都會出現，單顆 κ 不能代表這顆磷脂的真實彎曲剛性。作者 Table 1 列的 AVB 與 SA 數值都是至少 10 顆 GUV 平均，個別測值放在 Supporting Information 第 5 節 Figures S15–S18。
4. 工具與材料:
   - **Legendre 多項式 P_n(cos γ)**: 球面上對軸對稱起伏的自然展開基底，是球面諧波 Y_{l,m} 在 m = 0 退化後的單變數版本；n = 2 對應橢圓化、n = 3 對應梨形。
   - **模態振幅 B_n(t)**: ξ(γ, t) 展開到第 n 個 Legendre 模態的時間序列振幅。
   - **時間平均 ⟨B_n⟩**: 把 |B_n|² 在 5000+ 幀上平均，作為 AVB 的主要觀測量，計算成本低、高頻模態擬合穩定。
   - **Helfrich 連續介質模型 (方程式 8)**: 把每個 n 階模態的 ⟨B_n⟩ 寫成 κ 與 σ̄ 的封閉解，依等分能定理直接擬合彎曲剛性。
   - **κ 與 σ̄ 同時擬合**: 多個 n 的 ⟨B_n⟩ 對 n 畫圖後做最小平方擬合，同時解出彎曲剛性與約化張力兩個未知數。
   - **≥10 顆 GUV 平均**: Table 1 每個 AVB / SA 數值都是至少 10 顆 GUV 平均，個別測值見 Supporting Information 第 5 節 Figures S15–S18。
   - **Pécréaux et al. 2004 AVB protocol**: Eur. Phys. J. E (ref 22) 的平均法 protocol，本論文與 Méléard SA protocol 並用作為互校驗。
5. 與此篇文章的關係:
   在《Mechanical Properties Determination of DMPC, DPPC, DSPC, and HSPC Solid-Ordered Bilayers》這篇文章中，作者為了在 So 相 GUV 形狀已非完美球面的情境下仍能可靠擬合彎曲剛性 κ，採用了 Pécréaux 等人 2004 的 flicker noise 平均法 (AVB)。它把 ξ(γ, t) 用 Legendre 多項式展開、取 ⟨B_n⟩ 直接套 Helfrich 模型，與 SA 直方圖法併用——兩者一致即排除單一統計假設造成的偏差，給 Table 1 的 κ 數值一條獨立校驗路徑。
