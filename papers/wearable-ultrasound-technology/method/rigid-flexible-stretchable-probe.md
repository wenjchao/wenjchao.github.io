# Rigid / Flexible / Stretchable Probe 的機械工程

1. 引用自哪篇 paper: wearable-ultrasound-technology
2. Outline (任務主線): Rigid / Flexible / Stretchable Probe 的機械工程
3. Method: 
   論文把 wearable 探頭按「能不能跟著皮膚變形」分成三代。硬式探頭 (rigid probe) 把整片陣列做在剛性基板上，結構與醫院手持探頭一致，影像品質最高、與既有後端電路最相容；它不再靠技師握著，而是底面黏一層 silicone elastomer 或 bioadhesive hydrogel 作為軟夾心耦合皮膚（Wang et al. *Science* 2022, ref. 73）。Zhang et al. *Nat. Electron.* 2023 (ref. 24) 還把多片 phased array 嵌進 silicone 中組成更大聲學窗口。但 rigid 只能貼相對平的部位（胸口、太陽穴、腹部），碰到手腕膝蓋就要墊厚緩衝層、貼片變笨重。可彎式探頭 (flexible probe) 改把陣列做在聚醯亞胺基板 (polyimide substrate) 上，整片像便條紙一樣可彎曲（Fig. 2c）。便條紙能繞鉛筆、繞不過皮球——這就是可發展曲面 (developable surface) 與非可發展曲面 (non-developable surface) 的差別：前者指「圓柱圓錐這類能從平面捲起、不必拉伸」的形狀（脖子、手臂），後者指「球面、馬鞍面這種不拉伸捲不平」的幾何（肩膀、運動中的胸口）。可彎式只能搞定前者。三代的選擇邏輯不是「越能伸縮越好」，而是「依貼合部位的曲率類型選最便宜可行的一代」：rigid 影像最好且最相容，flexible 製程最成熟，stretchable 只留給曲率高又會動的部位。
   可拉伸探頭 (stretchable probe) 用「硬島 + 軟橋」架構解決 non-developable 曲面問題。每顆 transducer 仍是硬的小島 (rigid island)，但島與島之間的連線改用會拉的材料：蛇形銅電極 (serpentine copper electrode)（Hu et al. *Nat. Biomed. Eng.* 2023, ref. 75; Fig. 2d）或液態金屬電極 (liquid metal electrode)（Hu et al. *Nature* 2023, ref. 63; Fig. 2e）。蛇形 Cu 的關鍵是幾何把伸縮化為彎曲——銅本身只能拉 ~1% 就斷，繞成 S 形後當 patch 被拉長 30%，並不是讓 Cu 軸向被拉長，而是讓 U 形彎曲段「展開」，銅僅承受小幅彎曲應變 (bending strain) 仍在 elastic 範圍。液態金屬則乾脆把連線材料換成室溫下流動的金屬（例如 EGaIn），自然能跟著任意變形不破壞導電。元件之間原本剝開的縫隙叫元件間隙 (kerf)，必須填入矽橡膠填縫 (silicone elastomer kerf filling) 作為電氣絕緣兼機械保護（Wang et al. *Sci. Adv.* 2021, ref. 104; Fig. 2f）；不填的話相鄰島會互相撞裂、震動互相耦合 (cross-talk) 造成重影。封裝層必須用疏水彈性體 (hydrophobic elastomer) 把汗水擋在外面 (ref. 75)，否則親水彈性體會讓汗液滲入腐蝕電極。製程上 stretchable 仰賴轉印 (transfer printing) 把元件手工挑到彈性基板上，scalability 受限；作者建議改成滾印 (roll-to-roll printing on elastomer substrate) 量產（Ota et al. *Adv. Mater. Technol.* 2024, ref. 77）才打得開市場。
4. 工具與材料: 
   - **Rigid probe**: 陣列做在剛性基板，影像最佳，須靠 silicone/hydrogel 軟夾心耦合皮膚，僅貼相對平的部位。
   - **Flexible probe**: polyimide 基板可彎，貼脖子手臂這類 developable 曲面。
   - **Stretchable probe**: 硬島 + 軟橋架構貼 non-developable 曲面，serpentine Cu / 液態金屬作連線。
   - **Developable surface**: 圓柱圓錐這類可由平面不拉伸捲成的曲面，可彎式即可貼。
   - **Non-developable surface**: 球面、馬鞍面這種不拉伸無法服貼的曲面，需要 stretchable probe。
   - **Serpentine copper electrode**: 繞成 S 形的銅走線，拉伸時 U 段展開，銅只承受彎曲應變不被拉斷。
   - **Liquid metal electrode**: 室溫流動金屬（如 EGaIn）做連線，可任意變形保持導電。
   - **Kerf filling**: 元件間隙填入 silicone elastomer 作絕緣與機械保護，避免相鄰元件撞裂與 cross-talk。
   - **Hydrophobic elastomer**: 疏水彈性體封裝，把汗水擋在外面、避免腐蝕電極。
   - **Roll-to-roll printing**: 在彈性基板上的滾印量產製程，作者建議用以取代手工 transfer printing 解 scalability 問題。
5. 與此篇文章的關係: 
   在《Wearable ultrasound technology》這篇 Review 中，作者要把超音波探頭按身體不同部位的曲率與動態變形需求做出可貼合的形態，因此提出 rigid / flexible / stretchable 三代探頭架構。這套機械工程方案接續材料選擇與 stack 設計，往下決定後端 channel 數量與 phase aberration 補償演算法的需求；它把「哪些部位能貼、能貼多久、量產可行性」這三道工程瓶頸攤開分配給三種剛度的探頭。