# Ultrafast Imaging + Singular Value Decomposition Clutter Filter

1. 引用自哪篇 paper: wearable-ultrasound-technology
2. Outline (任務主線): Ultrafast Imaging + Singular Value Decomposition Clutter Filter
3. Method: 
   傳統超音波像逐線掃描：發一道聚焦聲波打進去、聽回波、再掃下一條線、最後把所有線拼成一張切面，每秒只有幾十張。高速整片掃描 (ultrafast imaging) 改成一次發射就把整個切面照亮，每秒因此能拍到上千張影像 (kHz 級 frame rate)。一次照亮整片靠的是不聚焦的整片聲波：平面前進、像一面波前推過去的 plane wave 覆蓋寬而平的視野，適合表淺結構；從一點散開成扇形的 diverging wave 覆蓋更廣，能深入或穿過彎曲表面，後續做 3D 顱內影像時特別有用 (Zhou et al. Nature 2024, ref. 72)。單次不聚焦發射很糊，作者改成「換不同角度連發好幾次」——例如從 -10°、0°、+10° 各打一次 plane wave、把回波都收下來，再把多角度影像對齊、像疊圖層般加總 (coherently summed)；糊掉的部分被多角度資訊互補回來、清晰部分被反覆增強。一秒內就累積出 compounded data，畫質追上聚焦掃描甚至更高。
   把幾百張連拍影像疊在一起，每個像素就有一條「亮度隨時間變化」的訊號。肌肉、血管壁、皮下脂肪是整片軟組織，呼吸與心跳推它們時整片一起平移、相鄰像素同進同退、時序曲線幾乎一模一樣 (高 spatiotemporal coherence)；血流則是紅血球以細胞為單位流過自己的血管，相鄰像素看的是不同紅血球、時序曲線完全對不上 (低 spatiotemporal coherence)。把整堆資料攤成大矩陣丟進大型矩陣拆解為主成分 (singular value decomposition, SVD)，「整批像素同步擺動」只需要少數幾個主成分就能描述、能量集中在前面；「各像素獨立快閃」很分散、能量散在後面。把前幾個主成分丟掉、留下後面的，就剩下乾淨的 blood flow 訊號——這就是 spatiotemporal clutter filter 的本質。
   為什麼非要 kHz frame rate？因為 SVD 拆主成分需要每個像素有夠長的時序樣本——時序太短、慢速與快速訊號還沒展開差異就被一起丟掉。一次心跳約 1 秒，要在這 1 秒裡蒐到幾百個時間點才能分出主成分，所以 frame rate 必須拉到 kHz 級。普通 30–60 Hz 一個心跳只取到幾十張，撐不起 SVD。為什麼特別搭配 power Doppler 做 3D 顱內影像？因為顱骨會把聲波削弱很多 (skull attenuation)、血流回波本來就很弱；power Doppler 把多次回波的訊號功率加總、等同把弱訊號累積放大，對微小血流特別靈敏。再搭上 ultrafast imaging 的高樣本量與 SVD 把組織擾動切掉，整個顱內血管網就能被重建成立體血流影像 (3D power Doppler)，而傳統 spectral Doppler 只能鎖一個深度、做不到這件事。
   這套流程有兩個容易出錯的關鍵。第一，如果只發射一次 plane wave、跳過多角度 compounded data，畫面像嚴重失焦的照片——邊邊細節被光暈糊掉、對比不夠。在這種畫質上即使疊上 SVD，分離出的血流訊號還是糊在噪聲裡，看不到細小血管，所以多角度疊加是把訊噪比 (SNR) 拉回來的必要步驟。第二，SVD 的閾值如果切得太兇、砍掉太多前面主成分，慢速血流——尤其是小血管或微血管——會跟組織擾動一起被丟掉，重建出的影像「乾淨」卻少了一大塊真實血管，所以閾值要根據組織與貼片位置調整。
4. 工具與材料: 
   - **Ultrafast imaging**: 用不聚焦的整片聲波把 frame rate 推到 kHz 級的高速掃描方式，每秒上千張影像。
   - **Plane wave**: 整排元件同時發聲，波前像平面一樣推過去，一次照亮寬而平的視野。
   - **Diverging wave**: 從一點散開成扇形的不聚焦聲波，覆蓋更廣、能深入或穿過顱骨等彎曲表面。
   - **Compounded data**: 多角度發射的回波對齊後同調加總 (coherently summed)，補回單次不聚焦發射的畫質損失。
   - **Spatiotemporal clutter filter**: 用「時間 + 空間相干性」差異把 tissue motion 與 blood flow 訊號分離的後處理。
   - **Singular value decomposition (SVD)**: 把時序矩陣拆成主成分；組織擾動集中在前幾個高相干主成分，血流分散在後面。
   - **Tissue motion**: 肌肉、血管壁、皮下脂肪受呼吸心跳整片同步擺動的低速訊號。
   - **3D power Doppler**: 搭配 ultrafast imaging 與 SVD 重建出的立體血流影像，對微小血流靈敏但無方向資訊。
   - **Skull attenuation**: 顱骨對聲波的強烈削弱，是經顱影像必須克服的最大訊號損失。
5. 與此篇文章的關係: 
   在《Wearable ultrasound technology》這篇 Review 中，作者要解決穿戴貼片在彎曲、有顱骨遮蔽的部位仍能看到血流的問題。ultrafast imaging 配合 singular value decomposition clutter filter 吃進貼片連拍的高頻率 radiofrequency signal，輸出乾淨的 blood flow 影像給下游 power Doppler 與 3D 血管重建，補上傳統 spectral Doppler 只能鎖單一深度、訊號累積不足的缺口。代表案例是 Zhou et al. *Nature* 2024 用 conformal patch 做出 3D transcranial power Doppler。