# 從色散掃描重建脈衝相位 (Algorithm 2)

1. 引用自哪篇 paper: high-pulse-energy-mamyshev-laser
2. Outline (任務主線): 從色散掃描重建脈衝相位 (Algorithm 2)
3. Method: 
強度自相關 (intensity autocorrelation, IAC) 是「脈衝強度跟它自己位移版本的重疊」 $\mathrm{IAC}(t) = \int I(t')I(t'+t)\,dt'$，天生對稱 IAC(t) = IAC(−t)、且不同 chirp 與相位的脈衝可給出幾乎一樣的 IAC，所以單看 IAC 還原不了脈衝相位——這也是 FROG、SPIDER 等設備存在的理由。作者的解法是在 Waveshaper 上掃描二階色散 β_2，等於給脈衝加上不同度數的二次相位眼鏡 $e^{i\beta_2\omega^2/2}$。每換一個 β_2，時域強度 I(t) 重塑成不同形狀、IAC(t, β_2) 也跟著變；把整條 β_2 軸的 IAC 串成二維地圖一起擬合，就把單一 β_2 下的歧義通通鎖死。前向模型就是 Eq. 11 與 Eq. 12：把候選 φ(ω) 配上量到的 |E(ω)| 形成電場、乘 $e^{i\beta_2\omega^2/2}$、反傅立葉到時域取平方得到 I(t, β_2)；再用 Wiener–Khinchin 定理 IAC = $\mathcal{F}^{-1}\{|\mathcal{F}\{I\}|^2\}$ 一步算到自相關，省去位移積分。整個鏈條都是 FFT、乘法、平方，可微。

因為前向模型可微，作者用 PyTorch 的 stochastic gradient descent + automatic differentiation 直接把 loss 對相位向量 φ(ω) 的梯度算出來、做 backprop 更新相位；每次只挑一部分 β_2 切片就算夠，10 000 次迭代後 loss 收斂。loss 用 cosine similarity $L = 1 - (a\cdot b)/(\|a\|\|b\|)$ 而非 L2：量測 IAC 跟模型 IAC 之間有一個不固定的整體幅度比例（自相關儀響應、訊號功率、平均次數都會線性放縮 IAC），L2 會逼相位去湊振幅、走向 spurious 解；cosine similarity 對 amplitude 不匹配 robust，只看形狀相似度。資料預處理三步缺一不可：(1) normalize 把各 β_2 切片整體幅度拉一致；(2) 對每個切片用 min_t 當背景 subtract 掉；(3) 用以零時延為中心的權重 w(t) 把主峰加重、wings 加輕，逼 fitter 把錯誤分配給主峰結構。

演算法找到的最短脈衝點落在 β_2 = 0.0189 ps²，代表重建出的 φ(ω) 帶有一個對應這個 β_2 量的內建二次相位——也就是 Mamyshev 輸出有顯著線性 chirp，剛好被這個外加色散抵消掉。主峰中心的相位幾乎是線性的，意味著絕大多數能量真的可以被線性壓縮搬到 sub-200 fs，這也跟實驗上用 ~10 m SMF 壓到 147 fs 的觀察一致。Fig. S22 把 retrieved pulse 反算出的 IAC(t, β_2) 跟原始量到的二維地圖直接疊比，作為一致性檢查。

若只用一個 β_2 的 IAC 加上 |E(ω)| 去 fit 相位，候選 φ(ω) 仍是一整族——Algorithm 2 能挑出唯一解，是因為這群候選在另一個 β_2 下會給出不同 IAC，只有跟全套 IAC(t, β_2) 都一致的那組存活，少了色散掃描就還原不了。若把 cosine similarity 換成 L2 損失，整體幅度的不匹配會主宰 loss，梯度把相位推向能湊近幅度的 spurious 解，重建主峰位置可能整個跑掉——這也是這套 phase retrieval 設定下 scale-invariant metric 不可省的理由。

4. 工具與材料: 
   - **強度自相關 (IAC)**: 脈衝強度與其位移版本的重疊；對稱、且不同相位脈衝可給出相同 IAC，本身無相位資訊。
   - **色散掃描 (dispersion sweep)**: 在 Waveshaper 掃 β_2，把脈衝套上不同度數的二次相位眼鏡，蒐集 IAC(t, β_2) 二維地圖。
   - **Wiener–Khinchin 定理**: IAC = $\mathcal{F}^{-1}\{|\mathcal{F}\{I\}|^2\}$，把時域自相關等價於頻域功率譜的反傅立葉。
   - **PyTorch SGD + autodiff**: 把可微分前向模型直接 backprop 更新相位向量 φ(ω)；10 000 次迭代後 loss 收斂。
   - **Cosine similarity 損失**: $L = 1 - (a\cdot b)/(\|a\|\|b\|)$，scale-invariant，對 IAC 整體幅度不匹配 robust。
   - **Zero-delay 加權窗 w(t)**: 把主峰附近權重加重、wings 加輕，逼 fitter 專注脈衝主結構。
   - **β_2 = 0.0189 ps²**: Algorithm 2 找到的最短脈衝色散補償量，等同 Mamyshev 輸出脈衝攜帶的內建線性 chirp 量。
5. 與此篇文章的關係: 
在《High-pulse-energy integrated mode-locked laser using a Mamyshev oscillator》這篇文章中，作者要驗證 Mamyshev 輸出脈衝的線性 chirp 可被線性壓縮到 sub-200 fs，卻只用得到強度自相關與光譜兩種便宜量測。為此他們把 Sec. 2-F 的色散掃描 IAC(t, β_2) 與量測頻譜餵進 Algorithm 2 的 PyTorch SGD + autodiff 流程，重建出脈衝振幅與相位、供 Fig. S21/S22 確認壓縮極限，繞過 FROG/SPIDER 設備成本。
