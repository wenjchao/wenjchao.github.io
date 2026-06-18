# Kerr 非線性係數 γ 與 mode-area 全向量計算

1. 引用自哪篇 paper: high-pulse-energy-mamyshev-laser
2. Outline (任務主線): Kerr 非線性係數 γ 與 mode-area 全向量計算
3. Method: 
GNLSE 裡的 self-phase modulation 項 $i\gamma|A|^2 A$ 描述「光自己感覺到的折射率隨自己強度變化」的效應。γ 越大，同樣脈衝走相同距離就累積越多非線性相位、把頻譜推得越寬，最後甚至 wave-breaking。所以 γ 是 GNLSE、Algorithm 1 穩態解、SCG 模擬最關鍵的單一參數之一；算錯 γ，整支模擬的脈衝形狀、B-integral 跟 supercontinuum 跨度全跟著錯。Eq. 5 $\gamma = (2\pi/\lambda)(n_2/A_\mathrm{eff})$ 的推導是：Kerr effect 的材料定義是 Δn = n_2 I、n_2 是材料常數；波導裡每瓦光功率對應強度 P/A_eff，所以折射率擾動 ≈ n_2 P/A_eff，乘上波數 2π/λ 即得每瓦每公尺累積的非線性相位 (單位 rad/W/m)。

標準的「弱侷限」公式 $A_\mathrm{eff} = (\int|E|^2)^2/\int|E|^4$ 假設光場主要橫向、縱向分量可忽略——對 fiber 沒問題，但 Si₃N₄–SiO₂ 對比達 1.45-vs-1.98，光被擠得很緊，模場的縱向 E_z 分量已不能忽略，且非線性項是 $(E\cdot E)$ 這種張量乘積。Afshar et al. 2013 (ref. 54) 的全向量公式 (Eq. 6) 同時用上 $\mathbf{E}\times\mathbf{H}^*$ (Poynting 向量，給能流) 與 $2|\mathbf{E}|^4 + |\mathbf{E}^2|^2$ 兩種項，正確處理 high-index-contrast 下「能流面積」跟「非線性相互作用面積」的差別。模場 E、H 由 COMSOL Multiphysics 的有限元素法 (FEM) 解 Maxwell 本徵值問題得到：給定截面幾何 (Si₃N₄ 心 2.07 µm × 0.70 µm、SiO₂ 包覆) 與材料折射率 (n_Si₃N₄ = 1.98, n_SiO₂ ≈ 1.45)，求出每支可導模的有效折射率 n_eff 與完整的橫向 + 縱向 E、H 分佈。把 (E, H) 代回 Eq. 6 算 A_eff、再丟回 Eq. 5 即得 γ。Fig. S2 提供不同寬高的 γ map。

n_2 = 2.2 × 10⁻¹⁹ m²/W 直接採用 Gao et al. 2022 (ref. 53) 的 Si₃N₄ 文獻量測值；erbium 佈植對 bulk Kerr 響應的修正預期很小，作者明文設為可忽略。SiO₂ 包覆的 n_2 約是 Si₃N₄ 的 1/10、加上光模在 350 nm 厚 Si₃N₄ 中被緊緊侷限，跑到包層的能量本就極少，所以同樣忽略。模式上只算 TE 基模 (主電場平行襯底)：這是 350 nm 厚 Si₃N₄ 截面下侷限最緊、γ 最高的模式，整支整合 MLL 也設計成在 TE 基模下操作 (Sec. 3-I 的 M² = 1.08 量測驗證單模性)。Table S2 給出選定截面的 γ = 1.145 W⁻¹m⁻¹。

若硬套弱侷限的 A_eff 公式，high-index-contrast 波導裡 A_eff 通常會被高估 10–30%、γ 同步被低估。代回 GNLSE 後 SPM 強度被低估、預測脈衝頻譜寬度與 B-integral 都偏小，Algorithm 1 掃出的穩定地圖會把實際應該避開的高 SPM 區誤標為穩定，導致版圖落在實驗上鎖不住模的點；對 Sec. 3-H 的 SCG 模擬也同樣壞，predicted octave 跨度比實驗少。另一個誤差來源是製程公差：Fig. S2 顯示 γ 隨寬高平滑變化，±5 nm 厚度、±20 nm 寬度的常見變異會帶來約 5% 的 γ 不確定度跟約 6% 的 GVD 偏差，所以 γ 不是『算一次就釘死』的常數，作者用 SEM 量測截面反代回 COMSOL，並把這 ±5% 不確定度納入 Algorithm 1 掃描的安全裕度。

4. 工具與材料: 
   - **Kerr 非線性係數 γ**: 每瓦光功率在波導中每公尺累積的非線性相位 (rad/W/m)；本設計 γ = 1.145 W⁻¹m⁻¹。
   - **Kerr 非線性折射率 n_2**: 材料 Δn = n_2 I 的常數；本工作採 Si₃N₄ 文獻值 2.2 × 10⁻¹⁹ m²/W (Gao 2022, ref. 53)。
   - **有效模面積 A_eff**: 把光功率轉成「強度」的等效截面積；high-index-contrast 波導需用全向量定義 (Afshar 2013, ref. 54)。
   - **全向量 A_eff 公式 (Eq. 6)**: 同時用 Poynting 向量 $\mathbf{E}\times\mathbf{H}^*$ 與 $2|\mathbf{E}|^4 + |\mathbf{E}^2|^2$，處理縱向 E 分量與張量非線性。
   - **COMSOL Multiphysics FEM**: 在波導截面上解 Maxwell 本徵值問題，輸出 n_eff 與完整 E, H 模場供 γ 計算。
   - **TE 基模 (fundamental TE mode)**: 本截面下侷限最緊、γ 最高的傳播模式；整合 MLL 即設計於此模式操作。
   - **Fig. S2 γ map**: γ 對 Si₃N₄ 波導寬與高的二維 map；本工作從中選 350 nm 厚作為非線性與佈植可行性的折衷。
5. 與此篇文章的關係: 
在《High-pulse-energy integrated mode-locked laser using a Mamyshev oscillator》這篇文章中，作者需要在 GNLSE 與 SCG 模擬裡放進一個正確的 γ；fiber 用的弱侷限 A_eff 公式在 Si₃N₄ 這種 high-index-contrast 波導會把 γ 系統性低估。他們用 COMSOL FEM 解出 TE 基模的完整 E、H 場，代入 Afshar 2013 (ref. 54) 的全向量 Eq. 6 算 A_eff，再經 Eq. 5 算出 γ = 1.145 W⁻¹m⁻¹，供 Algorithm 1 穩態搜索與 Sec. 3-H SCG 模擬使用。
