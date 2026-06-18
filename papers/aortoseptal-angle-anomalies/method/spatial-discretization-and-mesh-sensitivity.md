# Spatial discretization & mesh sensitivity (空間離散與網格收斂)

1. 引用自哪篇 paper: aortoseptal-angle-anomalies
2. Outline (任務主線): Spatial discretization & mesh sensitivity (空間離散與網格收斂)
3. Method: 
Navier-Stokes 是連續方程，電腦不能直接解，要先把 LV 血液體積切成有限個小體積單元 (cell)——這個切法叫空間離散 (spatial discretization)。本研究每個模型約切 1.2 × 10⁶ 個 cell，用的是非結構化網格：四面體 cell (tetrahedral) 擅長填滿 LV 主腔那種不規則形狀；六面體 cell (hexahedral) 在貼壁規則區域計算效率與精度更好。「非結構化」的意思是兩種形狀可自由銜接、不同大小可拼接。沿心室壁特別加 10 層 inflation layers (總厚度 2 mm)：這是貼著壁面排一疊由薄到厚的細網格層，因為貼壁血液速度從零陡升到主流速度，這個速度過渡層才是 WSS 的真正來源；網格不夠細，速度梯度就被低估、算出來的 WSS 全是假數據。
為什麼貼壁網格直接決定 WSS 算得準不準？因為 WSS 的定義是「血液黏度乘以靠近壁面的速度沿法向方向變化率」(τ_w = μ ∂u/∂n|wall)。要從離散網格算這個變化率，只能拿緊鄰壁面那層 cell 的速度與壁面的零速度做差，再除以那層 cell 的厚度。如果這層 cell 太厚 (大過真正的黏滯次層 viscous sublayer)，等於拿一條粗略的直線去近似一條陡升曲線，斜率被嚴重低估、WSS 就算小了。10 層 inflation、總厚 2 mm 就是設計來確保最內側那層厚度進得了黏滯次層、抓得到真實斜率。
為什麼是 1.2 × 10⁶ cells 而不是更多或更少？作者做了 mesh sensitivity analysis (Appendix A.3)：先跑粗網格看 WSS 多少，再加細到中等、再加細到很細，如果從中等加到很細時 WSS 幾乎不再變動，就代表中等密度已經「收斂」——再加細只是花更多計算成本、結果不會更準。1.2 × 10⁶ 就是這個轉折點。如果不做這個驗證、直接挑一個密度跑，最壞情況是這個密度其實還沒收斂，整套「AoSA 變陡讓下緣 TSM 上升 >45%」的結論會被 reviewer 質疑：到底是真實效應，還是模型剛好在還沒收斂的範圍裡漂移？所以對任何想說服 reviewer 的 patient-specific CFD 研究，mesh sensitivity 不是錦上添花，是必修課。
4. 工具與材料: 
- **spatial discretization**: 把連續的 LV 血液體積切成有限個小體積單元 (cell)，讓 Navier-Stokes 變成可解的代數方程組。
- **unstructured tetrahedral + hexahedral cells**: 非結構化混合網格：四面體填複雜主腔、六面體用於貼壁規則區，兩種可自由銜接。
- **~1.2 × 10⁶ cells**: 本研究每個模型的網格規模，由 mesh sensitivity 選出的最低足夠密度。
- **inflation layers (n = 10, 總厚 2 mm)**: 貼著心壁排的 10 層由薄到厚細網格層，用以解析近壁速度梯度、確保 WSS 算得準。
- **viscous sublayer**: 壁面附近速度從零陡升的薄黏滯次層；最內側 inflation cell 必須進得了這層才能算出真實 ∂u/∂n。
- **mesh sensitivity analysis (Appendix A.3)**: 逐步加細網格觀察 WSS 變動是否停止，找出收斂轉折點作為選定密度。
5. 與此篇文章的關係: 
在《Significance of aortoseptal angle anomalies to left ventricular hemodynamics and subaortic stenosis: A numerical study》這篇文章中，WSS 是本研究的核心指標，但 WSS 對貼壁網格精度極度敏感。作者採用空間離散與網格收斂分析 (1.2 × 10⁶ cells + 10 層 inflation layers + Appendix A.3 收斂測試)，解決「網格太粗會嚴重低估 WSS」的瓶頸，確保下游四個 AoSA 模型之間的 TSM、OSI、WSS divergence 比較不是網格殘留誤差造成。
