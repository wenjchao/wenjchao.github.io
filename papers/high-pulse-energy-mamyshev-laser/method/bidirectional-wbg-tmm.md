# 雙向 WBG 反射譜 TMM 計算

1. 引用自哪篇 paper: high-pulse-energy-mamyshev-laser
2. Outline (任務主線): 雙向 WBG 反射譜 TMM 計算
3. Method: 
Algorithm 1 把 WBG 視為瞬時頻域乘法 A(ν, l) × R_2(ν)。脈衝是複數頻譜，反射過 grating 後不只是各 ν 分量「減弱多少」(振幅 |R|)，每個 ν 還要套上特定的相位延遲 (arg R)，否則重組回時域的脈衝形狀就錯了——所以必須給「複數」R(ν) 不是純粹反射率 |R|²。作者把 grating 反射譜用 transfer matrix method (TMM) 算出來：把整支 grating 切成很多薄片，每片用一個 2×2 轉移矩陣描述「左邊前向/後向場與右邊前向/後向場之間的關係」，同時包含這片內部的相位累積跟界面反射。950 片矩陣全部連乘得到整支 grating 總矩陣，再從邊界條件 (右邊只有透射、無入射) 反推得到複數反射係數 R(ν)；掃過頻率軸就得到 R_1(ν), R_2(ν) 譜，餵給 Algorithm 1 使用 (Björk & Nilsson 1987, ref. 55)。

TMM 要兩個關鍵輸入：有效折射率調變 Δn 跟寄生 chirp Δl/l。Δn (peak-to-peak) 決定每片高/低折射率的對比強度，950 週期搭配 Δn = 8.6 × 10⁻³ 給出 8.3% / 9.6% 的反射率。Δl/l (Table S2 為 1.2 × 10⁻³) 代表 grating 週期沿位置線性漂移的比例——這個 chirp 並非設計刻意加入，而是 Gaussian apodization (σ_apo = 0.15) 「順手」造成的：作者把 Δn 沿 grating 位置做平滑包絡以消除反射譜 sidelobe，但局部 Δn 平均跟著變，使 Bragg 條件 λ_B = 2 n_eff Λ 中的 n_eff 也沿位置漂移，等同 grating 不同段反射的中心波長不同 (Brückerhoff-Plückelmann et al. 2025, ref. 56)。Brückerhoff 給出 bandgap center 隨位置移動的修正公式，被內建進 TMM 計算，把「免費」chirp 跟設計上的 chirp 分開精確處理。Gaussian apodization 的存在本身是為了避免 (1) 帶外洩漏 1480 nm 泵浦被反射、(2) 出現副峰支撐 parasitic lasing。

雖然 cross-section effective-index 與 photonic-bandgap 兩種模擬都能給 Δn 的數值，但用校準批次的 WBG 反射譜擬合得到的實驗 Δn 系統性低於模擬值，即使補償了 lithography 解析度後仍如此。作者推測這是因為 effective-index 模擬本質是『微擾理論』(perturbative)，假設 Δn 對模場是小修正；但這篇 Δn 已達 8.6 × 10⁻³、不滿足微擾。為了不讓理論誤差污染 Algorithm 1，他們直接餵實驗 Δn 給 TMM，反射譜形狀就跟實驗對齊。週期數選 950 是另一個折衷：太多週期會讓 grating 帶內 group delay variation 變大、反射本身就先把脈衝拉開；同時 cladding-mode scattering 在 1480 nm 泵浦下加重 (Zhan et al. 2019, ref. 65)，泵浦穿透時被多扣損耗。950 週期同時兼顧反射率夠用 (~10%)、群延遲平坦、泵浦損夠小。形狀用凹凸 (corrugated) WBG 可在 DUV 微影 + 一道含氟蝕刻同步定義，不需額外材料層，是整支腔可量產的關鍵。

若硬套模擬 Δn (比實際偏高)、不用實驗校準值，TMM 算出的 R_1, R_2 會把反射率高估、out-coupling 低估，Algorithm 1 預測的 round-trip 增益就跟實際對不上，最終預測的 (Δλ_f, l, P_p) 穩定區地圖整個偏離晶片真正的 sweet spot、版圖會選錯落點。另一個常見直覺錯誤是「週期越多反射越強越好」：增加週期確實提高反射率、提高 finesse 看似有利，但 cladding-mode scattering 也同步加重、1480 nm 泵浦穿透 grating 時被多扣的損耗直接吃掉腔內增益，round-trip net gain 反而下降。作者用 Zhan 2019 (ref. 65) 的 cladding-mode loss 模型驗證 950 週期是反射率/泵浦損的最佳折衷。

4. 工具與材料: 
   - **Waveguide Bragg grating (WBG)**: 在波導側壁刻凹凸條紋形成的窄帶反射器；本工作 950 週期、Δn = 8.6 × 10⁻³，反射率 8.3% / 9.6%。
   - **Transfer matrix method (TMM)**: 把 grating 切成薄片各以 2×2 矩陣連乘，得到複數反射譜 R(ν)；依 Björk & Nilsson 1987 (ref. 55)。
   - **有效折射率調變 Δn**: grating 高/低折射率對比；本工作由 calibration 批次 WBG 反射譜擬合得到 8.6 × 10⁻³。
   - **寄生 chirp Δl/l**: grating 週期沿位置線性漂移比例，apodization 造成；本工作 1.2 × 10⁻³。
   - **Gaussian apodization σ_apo**: Δn 沿位置的平滑包絡，σ = 0.15，消除反射譜 sidelobe、避免泵浦帶外洩漏。
   - **Bandgap center shift**: apodization 順手造成的 Bragg 波長位置漂移；以 Brückerhoff-Plückelmann 2025 (ref. 56) 公式修正。
   - **Cladding-mode scattering loss**: 週期增加時 1480 nm 泵浦穿透 grating 的額外損耗；依 Zhan 2019 (ref. 65) 模型，決定 950 週期上限。
   - **微擾近似失效**: Δn = 8.6 × 10⁻³ 已超出 effective-index 模擬的 perturbative 範圍；作者改採實驗 Δn 校準避開該誤差。
5. 與此篇文章的關係: 
在《High-pulse-energy integrated mode-locked laser using a Mamyshev oscillator》這篇文章中，Algorithm 1 把 WBG 反射視為瞬時頻域乘法，需要事先準備好複數反射譜 R_1(ν), R_2(ν)。作者把 calibration 批次 WBG 量到的實驗 Δn 與 Δl/l 餵進 transfer matrix method (TMM)，輸出 GNLSE 模擬可直接使用的 R_1, R_2，繞過 effective-index 模擬在強調變區的 perturbative 失效，確保 Algorithm 1 的 round-trip 增益跟實際晶片一致。
