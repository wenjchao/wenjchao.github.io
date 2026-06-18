# 3D LV geometry reconstruction (LV 三維幾何重建)

1. 引用自哪篇 paper: aortoseptal-angle-anomalies
2. Outline (任務主線): 3D LV geometry reconstruction (LV 三維幾何重建)
3. Method: 
第二步是把 cine-MRI 裡的「血液所在腔體」抓出來、堆成 3D 形狀。作者從 cine 序列挑出收縮中期 (mid-systole)——心臟用力擠到一半的那個瞬間——當作基準時相，再用 Segment v3.0 R7568 (Medviso AB；protocol 見 Heiberg et al. 2010 [29]) 做半自動影像分割 (semi-automatic segmentation)：軟體先自動估一條腔體輪廓，使用者再修掉乳突肌與心室壁交界、瓣膜環這些對比模糊的位置；比全自動可靠，又比逐片手描快很多。把所有薄片描出的 2D 輪廓沿垂直方向堆起來，就得到一顆 3D 的內腔血液體積。選 mid-systole 而非舒張或收縮末，是為了後面 FSI 模擬施加位移時，往兩個方向漲縮的幅度都不會過大、數值較穩。
分割完的腔體還不能直接餵給求解器。從 8 mm 厚薄片堆出來的表面會有一階一階的「階梯感」與局部鋸齒，後面的網格生成會在這些位置產生破碎元素，導致計算發散。所以作者再把這顆體積丟進 CAD 軟體 SolidWorks (Dassault Systèmes) 做空間平滑，把鋸齒磨成連續曲面、補上局部空洞，產出一個封閉、連續、可重網格的乾淨幾何。整套「Segment 分割 → SolidWorks 平滑 → 交給 ANSYS 做 FSI」的流程是作者群在 Shar et al. 2020 (Front. Bioeng. Biotechnol.) 與 Shar et al. 2021 (Cardiovasc. Eng. Technol.) 已驗證過的成熟管線，細節補充在本論文 Appendix A.1；沿用已發表 protocol 讓本篇可以把篇幅集中在新的 AoSA 變體比較。
重建出來的 3D LV 是否真的長對，要靠四個臨床心功能指標來檢驗。作者把模擬跑出的舒張末容積 (end-diastolic volume, EDV) 107.7 mL、收縮末容積 (end-systolic volume, ESV) 51.1 mL、心搏量 (stroke volume, SV) 56.6 mL、射出分率 (ejection fraction, EF) 52.6%，與同一位受試者的 cine-MRI 量測值逐一比對，四個數字差距全部 <2 %。這道驗證很關鍵：若跳過，即使後面四個 AoSA 變體之間出現顯著差異，reviewer 都可以合理懷疑那只是重建誤差的雜訊，而非角度真正的效應。
4. 工具與材料: 
- **Segment v3.0 R7568 (Medviso AB)**: 半自動心臟影像分割軟體；先自動估腔體輪廓再讓使用者手動修正。Protocol 見 Heiberg et al. 2010 [29]。
- **SolidWorks (Dassault Systèmes)**: CAD 軟體，用於把分割出的腔體做空間平滑，產出可重網格的封閉幾何。
- **mid-systole 基準時相**: 收縮中期；以這個時相幾何當基準，後續 FSI 再施加位移漲縮到其他時相。
- **EDV / ESV / SV / EF**: 舒張末容積、收縮末容積、心搏量、射出分率；四個臨床心功能指標，作者用來驗證重建模型與 MRI 量測差距 <2 %。
5. 與此篇文章的關係: 
在《Significance of aortoseptal angle anomalies to left ventricular hemodynamics and subaortic stenosis: A numerical study》中，作者要建立一個值得信賴的 3D LV 幾何當下游 FSI 模擬的底，所以從受試者的 cine-MRI 把 mid-systole 時相的內腔半自動分割出來，再用 SolidWorks 平滑成可重網格的封閉體積。這顆幾何接著餵給 AoSA 變體建構 (子項 C) 與壁面變形邊界 (子項 D)，並用 EDV/ESV/SV/EF 與 MRI 差距 <2 % 證明可信度。
