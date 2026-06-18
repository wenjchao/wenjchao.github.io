# 維度標準化與設計準則

1. 引用自哪篇 paper: high-pulse-energy-mamyshev-laser
2. Outline (任務主線): 維度標準化與設計準則
3. Method: 
Eq. 1 的 GNLSE 含 β_2、γ、g、α 四個有量綱係數，比較兩個系統得逐項對比，很難一眼看出「兩個平台是不是處在同一個工作區」。作者定義一個典型脈衝寬度 T_0 與峰值功率 P_0 作為自然單位，引出色散長度 $L_D = T_0^2/|\beta_2|$ (光走多遠脈衝被 GVD 拉開到比自身更寬) 與非線性長度 $L_\mathrm{NL} = 1/(\gamma P_0)$ (走多遠累積 1 rad 非線性相位)。重新縮放 $\xi = z/L_D$、$\tau = t/T_0$、$U = A/\sqrt{P_0}$ 代回去除以 L_D，整支方程式變成 Eq. 8 $\partial_\xi U = -i/2\,\mathrm{sgn}(\beta_2)\partial_\tau^2 U + \hat{g}/2\cdot U + iN^2|U|^2 U$。原本四個係數只剩兩個自由參數：孤子數 $N = \sqrt{L_D/L_\mathrm{NL}}$ 跟標準化淨增益 $\hat{g} = (g-\alpha)L_D$。N 比較非線性主宰長度與色散主宰長度的尺度差 (N≈1 是基本孤子、N≫1 表 SPM 強烈塑形)；ĝ 衡量一個色散長度內淨累積的增益，反映腔的能量放大強度。

因為 Eq. 8 僅依賴 N²、ĝ 與 sgn(β_2) 三個無量綱量，兩個系統的這三個數相同、U(ξ, τ) 演化軌跡就完全一樣。Table S3 把 Yb-doped fiber Mamyshev oscillator (γ ~ 0.005 W⁻¹m⁻¹、β_2 ~ 0.025 ps²/m)、350 nm Si₃N₄ (γ = 1.145, β_2 = 0.715)、600 nm Si₃N₄ 放在一起：γ 跨平台差到 200 倍、β_2 差 30 倍，但孤子數 N 都鎖在 ~10、ĝ 是 $\mathcal{O}$(40) 級 (600 nm 因 L_D 變長飆到 O(315))。代表這幾個系統在無量綱座標處於同一個「Mamyshev 工作區」、脈衝塑形機制不變，可由 N ~ O(10) 設計準則直接搬移。

作者把核心設計準則濃縮成「維持 N ~ O(10)、配 normal GVD (sgn(β_2) > 0)」。理由是 normal GVD 在波長變紅一端走得慢、藍一端走得快，會把因 SPM 拉寬的頻譜往時間軸兩側分開，自動把脈衝拉長、峰值強度降下來，這個「自動降強度」抑制 wave-breaking。N ~ O(10) 讓 SPM 強到把脈衝拉到夠寬的頻譜給 grating 濾波篩選，又不至於強到 SPM 比 GVD 抑制機制還快。B-integral $B = \int_0^{2l}\gamma I_\mathrm{s,prop}(z)\,dz$ 是整個 round-trip 累積的非線性相位 (rad)；本工作 B 達 ~20π (Fig. S7) 仍能穩定，遠超孤子鎖模 ~π 容忍上限，靠的就是 Mamyshev 的 SPM + filter 把過強脈衝能量「砍頭」加上 normal GVD 持續拉長脈衝。

無量綱準則只是「該往哪個方向走」的羅盤，實際選 Δλ_f、l、P_p 還受到 grating bandwidth、R_parasitic、製程 ±5 nm 變異等真實邊界影響。作者用 Algorithm 1 在 (Δλ_f, l) 與 (Δλ_f, P_p) 二維 map 上掃 (Fig. S9, S10)，標出每個落點是穩定鎖模、trivial CW 還是不收斂的混沌邊界。最後版本選在裕度大的中心點，避免製程波動推到邊界。失敗模式有二：(1) 如果換成 anomalous GVD (β_2 < 0) + N ~ O(10)，會跟 SPM 聯手形成 N 階孤子並週期性 soliton fission，整合平台 γ 又比 fiber 大三個數量級，會撐爆 wave-breaking 區、脈衝每 round trip 換一張臉、不可能穩定鎖模；這也是作者堅持選 350 nm 厚 normal-GVD 截面而非更薄 anomalous 區的原因。(2) 把 P_p 推到 > 100 mW、grating 間距 < 10 nm 時 N 飆到 > 20，SPM 把頻譜推得比 filter 能容納還寬、filter 反而把主峰也削掉，腔陷入混沌；Algorithm 1 在這區不收斂、Fig. S10 標為應避開區。N ~ O(10) 不是只給下限，上限也由 filter 寬度 + B-integral 容忍度設定。

4. 工具與材料: 
   - **色散長度 L_D = T_0²/|β_2|**: 脈衝因 GVD 被拉開到比自身更寬所需的距離；自然空間單位。
   - **非線性長度 L_NL = 1/(γ P_0)**: 累積 1 rad SPM 相位所需的距離；自然非線性單位。
   - **孤子數 N = √(L_D/L_NL)**: 非線性 vs 色散的尺度比；本工作鎖在 ~10。
   - **標準化淨增益 ĝ = (g − α)L_D**: 一個色散長度內淨累積的增益；本工作 $\mathcal{O}$(40)。
   - **B-integral**: $B = \int_0^{2l}\gamma I_\mathrm{s,prop}(z)\,dz$，整個 round-trip 累積非線性相位；本工作達 ~20π。
   - **Normal GVD (β_2 > 0)**: 紅端走慢藍端走快的色散，自動拉長 SPM 拉寬的脈衝、抑制 wave-breaking。
   - **Table S3 跨平台對齊**: Yb-fiber、350 nm Si₃N₄、600 nm Si₃N₄ 三平台無量綱數對照表，驗證 N ~ 10 + normal GVD 設計準則可移植。
5. 與此篇文章的關係: 
在《High-pulse-energy integrated mode-locked laser using a Mamyshev oscillator》這篇文章中，作者要把 fiber 上累積多年的 Mamyshev oscillator 經驗搬到 Si₃N₄ 整合平台，卻面臨 γ、β_2、l 三個量都跨數量級的問題。他們把 GNLSE 重新縮放成 Eq. 8、僅留 N 與 ĝ 兩個無量綱數，做出 Table S3 對齊三平台、確認 N ~ O(10) + normal GVD 是共用設計準則，再交給 Algorithm 1 在 (Δλ_f, l, P_p) 三維空間掃出實際穩定地圖供晶片版圖選擇。
