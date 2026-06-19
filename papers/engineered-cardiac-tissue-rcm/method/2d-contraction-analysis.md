# 2D 收縮分析 (Pixel-intensity Subtraction)

1. 引用自哪篇 paper: engineered-cardiac-tissue-rcm
2. Outline (任務主線): 2D 收縮分析 (Pixel-intensity Subtraction)
3. Method: 

作者要在大樣本下比較兩個基因型 iPSC-CM 的跳動表現，但又不想為了一個粗篩入口去加螢光染料。他們把 iPSC-CM 攤在 24 孔盤裡 (200,000 cells/cm²)，用最普通的明場顯微鏡 (brightfield) 連拍自發跳動的影片，每秒 20 張影格 (20 fps)。每張影格就是一張灰階圖：細胞靜止時，前後兩張影格同一個 pixel 灰階值幾乎不變，相減接近 0；一旦細胞收縮把邊界往內拉，原本是細胞的 pixel 變成背景、原本是背景的變成細胞，灰階值明顯改變，差值瞬間飆高。把所有相鄰影格的「pixel 差值平方和」串起來，就得到一條起伏的跳動代理曲線 (motion proxy trace；pixel-intensity subtraction，演算法依 Hossain et al. 2010 Analyst 與 Huebsch et al. 2015 Tissue Eng C，實作為 GVN Lab 自寫 Python，https://github.com/GVNLab)：每個高峰對應一次完整跳動。

有了這條代理曲線，下一步是把它轉成三個臨床對應數字：振幅、收縮速度、舒張速度。和鈣訊號不一樣，pixel subtraction 量到的不是「鈣濃度」這種狀態量、而是直接的「畫面變化速度」——細胞收縮越快，相鄰影格 pixel 差值越大。所以對這條曲線再取一階差分 (相鄰時間點的斜率) 就直接拿到「速度的代理」：曲線高峰本身就是跳動振幅，上升段最大斜率對應收縮速度，下降段最大斜率對應舒張速度。完全不需要像鈣 τ 那樣去擬合單指數衰減模型。

為什麼挑這三項規格？明場無標記是為了把這套分析當「最便宜、最快」的兩基因型篩選入口——免染料、無毒性與漂白，可直接在培養箱旁邊跑。20 fps 對 1 Hz 左右的自發跳動已足夠把收縮 (約 200 ms) 與放鬆 (約 400 ms) 兩段解析開來；幀率拉太低 (例如 5 fps)，整個收縮過程只剩一個影格，斜率根本算不出。細胞密度拉到 200,000 cells/cm² 則是為了讓相鄰心肌細胞彼此電氣耦合 (syncytium) 同步跳動，整個視野的差值才會出現明顯高峰；若鋪太稀，每顆細胞各跳各的，整片差值被平均掉、訊號被噪音蓋過。

這個方法的軟肋是「它只認 pixel 在動，不認是誰在動」。漂浮的死細胞跟著培養液飄移會產生與跳動無關的差值；顯微鏡載物台被碰一下、或培養液面震動產生反光，整張影格 pixel 全部變色、差值瞬間衝出一個假高峰，被誤判成一次跳動。細胞鋪得不均勻時，密集區跳得整齊、零星區各自為政，整視野差值被「沒跳到的區域」平均稀釋，可能讓真有差異的兩個基因型看起來沒差。這也是作者只把這套方法當「2D 入口」、最終必須回到 3D ECT 量真正力學的根本原因——它無法分辨「pixel 動」與「真的收縮力」。

4. 工具與材料: 
- **brightfield 顯微鏡**: 不需螢光標記的普通光學顯微鏡，本研究用來連拍 iPSC-CM 自發跳動，避免染料毒性與漂白。
- **pixel-intensity subtraction**: 把相鄰影格逐 pixel 相減、平方、加總，得到「這一瞬間整體動了多少」的數字，是整套分析的核心代理量。
- **motion proxy trace**: 把所有相鄰影格的 pixel 差值串起來形成的起伏曲線，每個高峰對應一次完整跳動。
- **一階差分 (first derivative)**: 取相鄰時間點的斜率；對代理曲線取一階差分，上升段最大斜率即收縮速度、下降段即舒張速度。
- **20 fps 取像**: 每秒拍 20 張影格的速率；對 1 Hz 自發跳動足以解析收縮 (~200 ms) 與放鬆 (~400 ms) 兩段。
- **200,000 cells/cm² 鋪盤密度**: 讓相鄰心肌細胞彼此電氣耦合 (syncytium) 同步跳動，整視野差值才會出現明顯高峰。
- **GVN Lab Python 程式**: 作者實作 pixel subtraction 與一階差分的開源管線 (https://github.com/GVNLab)，演算法依 Hossain et al. 2010 Analyst 與 Huebsch et al. 2015 Tissue Eng C。

5. 與此篇文章的關係: 
在《Engineered cardiac tissue model of restrictive cardiomyopathy for drug discovery》這篇文章中，作者要比較病人版與校正版 iPSC-CM 的功能差異，但 RCM 的舒張缺陷無法直接在 2D 量到絕對力。為此他們先以 2D 收縮分析 (pixel-intensity subtraction) 從明場影片快速擠出振幅、收縮速度、舒張速度，作為兩基因型大樣本比較的最便宜入口；這套量化的不足之處正是後續 milliPillar ECT 力學量化模組要補上的——前者吃影片、產出三條跳動指標，把懷疑「真有差異」的兩株細胞篩出來，再交給 3D 模組量真正的 active force 與 passive tension。
