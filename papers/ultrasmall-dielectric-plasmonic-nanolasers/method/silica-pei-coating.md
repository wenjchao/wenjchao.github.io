# Stöber TEOS 二氧化矽包覆與 PEI 表面官能化

1. 引用自哪篇 paper: ultrasmall-dielectric-plasmonic-nanolasers
2. Outline (任務主線): Stöber TEOS 二氧化矽包覆與 PEI 表面官能化
3. Method:
這個子項在做的事，是把剛從酸液脫落的裸粒子，一步步變成能被活細胞吞下且長期穩定的雷射條碼。整個流程從自由粒子懸浮液開始分三段。第一段「溶液交換」：粒子還泡在稀 piranha 裡（酸性強、對後續反應不利），作者用離心機讓粒子沉到管底、倒掉上清、加乙醇、超音波打散粒子，重複多輪把酸稀釋到可忽略；因為每輪只是把上層倒掉、無法完全乾淨，所以要靠「指數稀釋」——每輪 100 倍、做三輪就 100 萬倍下降。第二段「長 silica 殼」：把乙醇裡的粒子加入四乙氧基矽烷 (tetraethyl orthosilicate, TEOS) 與氨水 (ammonium hydroxide, NH₄OH)。TEOS 的分子結構是一顆矽原子中心接四條乙氧基 $\mathrm{Si(OC}_2\mathrm{H}_5)_4$，本身是透明液體。氨水提供鹼性讓 TEOS 先水解成矽醇 Si-OH，兩個 Si-OH 相遇脫水縮合 (condensation) 成 Si-O-Si 橋，多個橋交織成三維無定形 SiO₂ 網絡，這種在粒子表面均勻長 silica 的做法就叫 Stöber 反應，最終形成約 25 nm 厚的均勻二氧化矽殼。第三段「掛 PEI」：把包好 silica 的粒子跟聚乙烯亞胺 (polyethylenimine, PEI) 混合。PEI 骨架上密密麻麻掛著二級/三級胺基，生理 pH 7.4 下多數質子化成 $-\mathrm{NH}_2^+-$、整條分子帶大量正電；silica 殼表面天生帶負電，PEI 就自然吸附上去、變成一層帶正電塗層。細胞膜外側因磷脂質頭端有磷酸基本身帶負電，粒子一碰到細胞膜就被吸過去並觸發細胞的內吞 (endocytosis) 機制。這一整套 silica + PEI 策略沿用自 Kwok et al. (bioRxiv 2022, ref 11) 的 LP 官能化方案。從裸盤到成品，全流程 yield 優於 10%。

為什麼 TEOS + 氨水混一起，剛好只在粒子表面長一層均勻殼、而不是在乙醇裡到處長出散亂 silica 顆粒？因為 Stöber 反應有兩條路線在競爭：同質成核 (homogeneous nucleation) 是 Si-OH 在乙醇裡彼此碰上隨機聚成散亂膠體球；異質沉積 (heterogeneous deposition) 是 Si-OH 直接沉積到既有表面上長成殼。異質沉積能量門檻低很多，所以只要溶液裡有粒子當「種子」，Si-OH 一生成就衝到粒子表面沉積，慢慢長成均勻殼——InGaP 盤剛脫離基板時表面帶羥基與缺陷，是絕佳沉積位點，所以殼厚度可以控制在 25 nm 上下。至於為什麼選 25 nm 而不是更薄或更厚？太薄（例如 5 nm）——silica 殼有微孔，含氯離子與蛋白酶的細胞質仍會滲進去慢慢咬半導體，粒子放進細胞幾小時就發光下降、光譜漂移超過條碼可辨識的 ±0.5 nm；太厚（例如 50 nm）——粒子總直徑膨脹、細胞攝取變差，同時 WGM 的消散場 (evanescent field) 被殼吃掉太多、發光效率下降。25 nm 是「穩定性 + 攝取效率 + 敏感度」三者的當前折衷，論文 Study Limitations 也提到「若想再降低對介質折射率的敏感度可加厚到 >50 nm」。另一個容易忽略的問題是——InGaP cap 已經擋住 Al 氧化，為什麼還要再包 silica？答案是兩層保護分工不同：InGaP cap 是「材料內建防鏽」，silica 殼是「與生物環境的隔離牆 + PEI 掛載點」；InGaP 本身放在細胞質裡仍會被蛋白吸附與酸性慢慢咬，silica 則是化學上最惰性的表面之一，剛好也帶負電是 PEI 最容易掛的介面。

為什麼最外面選 PEI 而不是抗體、PEG 或 biotin？作者目標是「同一批粒子能被 HeLa、MCF-7、RAW 264.7、Jurkat T 四種細胞株都吞下」，這個「非特異性、廣譜」需求把候選幾乎只剩 PEI——抗體只綁特定 marker 的細胞（要換細胞株就要換塗層）、PEG 屬於隱形塗層設計不利內吞、biotin 需要細胞先表達 streptavidin 才綁得住。PEI 帶大量正電，靠靜電廣泛吸附到所有真核細胞膜並觸發 endocytosis，是「一種塗層通用多細胞」的最經濟解。這條 pipeline 有三個致命失敗模式：一，離心-再懸浮做太少輪、酸殘濃度太高就加 TEOS + 氨水，殘酸會中和氨水讓 Stöber 反應停擺，甚至溶掉剛長出來的 silica，粒子光禿禿沒殼直接作廢；二，silica 殼太薄 (5 nm) 幾乎必然有微孔，含氯離子與蛋白酶的細胞質穿孔咬半導體，粒子放進細胞幾小時發光下降、光譜失控漂移超過 ±0.5 nm，條碼壞掉；三，只包 silica 沒掛 PEI，silica 表面帶負電正好跟細胞膜負電互斥，共培養一夜多數粒子還漂在培養液裡沒進細胞，達不到「每顆細胞幾顆粒子」的條碼密度。三個「儀式」——洗乾淨酸、25 nm 剛好、PEI 掛好——一起決定粒子能不能安全長時間住在細胞裡。
4. 工具與材料:
- **TEOS (tetraethyl orthosilicate)**: $\mathrm{Si(OC}_2\mathrm{H}_5)_4$，一顆矽原子接四條乙氧基的透明液體，是 Stöber 反應的 silica 前驅物。
- **NH₄OH (ammonium hydroxide)**: 氨水，提供鹼性催化讓 TEOS 水解成矽醇 Si-OH 並凝聚成 SiO₂ 網絡。
- **Stöber-type 反應**: 在有種子粒子存在時，異質沉積勝過同質成核，讓 SiO₂ 均勻長在粒子表面成殼的經典化學。
- **~25 nm silica 殼**: 作者採用的殼厚，兼顧化學隔絕、細胞攝取效率與消散場保留，撐 72 小時且維持條碼 ±0.5 nm 穩定。
- **PEI (polyethylenimine)**: 分枝高分子，骨架掛滿二級/三級胺基，生理 pH 下大量質子化帶正電，透過靜電與細胞膜結合並觸發內吞。
- **離心-再懸浮循環 (centrifugation–resuspension)**: 把粒子從稀 piranha 逐輪換到乙醇，指數式稀釋殘酸避免下游 Stöber 反應停擺。
- **Kwok et al. (bioRxiv 2022, ref 11) LP 官能化策略**: 本論文 silica + PEI 表面官能化的原型 protocol 來源。
- **全流程 yield >10%**: 從基板脫落、silica 包覆到純化為溶液中 LP 的整體收率。
5. 與此篇文章的關係:
在《Ultrasmall InGa(As)P Dielectric and Plasmonic Nanolasers》這篇文章中，作者為了讓半導體奈米雷射真的能被塞進活細胞當光譜條碼，用 Stöber TEOS silica 包覆與 PEI 表面官能化把裸露的 III-V disk 密封並改成正電表面。這解決了兩個瓶頸：一是 InGaP 在細胞質裡會被慢慢咬掉的化學降解、二是負電裸粒子與負電細胞膜互斥導致內吞效率極低。它吃進的是溼蝕刻脫落的自由粒子，交出的是可以與 HeLa/MCF-7/RAW 264.7/Jurkat T 共培養 72 小時、發光穩定的雷射條碼粒子，直接餵給下游細胞條碼實驗。
