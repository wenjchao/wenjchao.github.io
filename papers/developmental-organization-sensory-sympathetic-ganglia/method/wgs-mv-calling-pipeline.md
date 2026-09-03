# WGS 前處理與四工具聯合 MV 呼叫 pipeline

1. 引用自哪篇 paper: developmental-organization-sensory-sympathetic-ganglia
2. Outline (任務主線): WGS 前處理與四工具聯合 MV 呼叫 pipeline
3. Method:

作者的目的是從神經節與器官樣本裡撈出「只有一小部分細胞帶」的 DNA 突變當條碼。做法分四步。第一步把定序機讀到的短片段用 BWA-mem 貼回人類參考基因體、用 GATK 的 IndelRealigner 與 BaseRecalibrator 做重複讀取整理與品質校正。第二步把整理好的資料同時餵給四種各有偏好的 mosaic caller，就像四個角度不同的偵探同時查案：MosaicHunter 是傳統機率模型直接算「這樣的讀取分佈符不符合 mosaic 假設」；Mutect2 + DeepMosaic 是把讀取排成一張圖丟給深度學習判定；Mutect2 + MosaicForecast 是把讀取一堆特徵餵給隨機森林分類器；Mutect2 ∩ Strelka2 paired 則把「左右心壁合併」當「乾淨對照」，用 tumor-normal 差異直接呼叫。這四種偏好完全不同，一種漏的另一種可能會抓到，這也是「四工具聯合」而不是只信一種的原因。第三步把四份候選清單彙整。第四步用一份「已知的假貨名單」把明顯是雜訊的位點刷掉。

所謂「WGS 深度」是「平均每個位點被讀到幾次」——30× 代表 30 次、300× 代表 300 次。深度越高，越能穩定看出「10 次讀到 A、290 次讀到 T」這種只有極少數細胞帶的突變（AF 約 3%）。作者選擇雙軌設計：對少數器官樣本（每位 donor 8–17 個）做昂貴的 300× WGS 找 rare 候選 mosaic；對數十顆神經節（每位 donor 18–34 個）做便宜的 30× WGS 補共享 clone 資訊。雙軌讓「同一個 mosaic 就算在單一 300× 器官樣本被漏掉，只要橫跨數十顆 30× 神經節都反覆出現微弱讀取，還是能浮現出來」。這是「深度精 vs 廣度足」的預算折衷——全做 300× 會爆預算幾十倍，全做 30× 則會漏掉高 AF rare mosaic。

為什麼一定要靠一份「已知的假貨名單」把雜訊刷掉？因為 mosaic caller 的輸出裡混了三種假貨。第一種是常見的 germline polymorphism。作者用 gnomAD 這個彙整超過 15 萬人變異頻率的公開資料庫，把 AF > 0.001（每千人就有一個帶）的位點通通排除——這些一定是 germline 大家共有的，不是 mosaic。第二種是定序流程本身的系統性錯誤（alignment artifact、hotspot noise）。作者建了一份 Panel of Normals (PoN)：混合 15 個精子樣本（代表唯一 haplotype、任何被呼出的都不會是 mosaic）與 11 個血液樣本（代表典型 somatic 背景，含可能的 CHIP-like signal）；只要某位點在 PoN 也反覆出現就當假貨。第三種是重複序列造成的 alignment 假 het，作者用 UCSC SegDup 與 RepeatMasker 遮罩、以及「>3 unit homopolymer / dinucleotide repeat」規則排除。最後補一刀：把 lower CI of AF < 0.001 的位點視為「參考同源突變的雜訊」也濾掉。

少了任何一層守門員，整條 pipeline 都會崩。假如作者省略 PoN，很多「參考基因體 alignment 難處理才反覆出現」的假 mosaic 會混進候選；如果省略 gnomAD filter，很多族群常見的 germline polymorphism 會被誤當個人化 mosaic；這兩層破口一起發作，會把 germline / 系統性錯誤位點通通送去做動輒幾百美金的 AmpliSeq MPAS 深度驗證，最後驗證率會從 27–32% 崩到個位數。另一個大干擾是 Clonal Hematopoiesis of Indeterminate Potential (CHIP)——造血幹細胞在成年之後累積 mosaic 突變、被 clone 擴增到血液系統裡的現象，AF 可以達幾個 percent、非常像胚胎 mosaic 卻完全跟神經節祖先無關。如果 pipeline 沒把 CHIP 挑掉，可能會把「血液樣本混進神經節樣本的 CHIP mosaic」當成胚胎條碼，畫錯 NC 家族樹。作者的防守分兩層：PoN 內含 11 個血液樣本讓 CHIP-like hotspot 被自動排除；下一步 MPAS 驗證時還會加上「這個 clone 有沒有在相鄰 DRG/SG 出現」的一致性條件再刷一次。

4. 工具與材料:

- **BWA-mem**: 把定序機讀到的短片段貼回人類參考基因體的對齊工具。
- **GATK IndelRealigner + BaseRecalibrator**: 對齊後對插入缺失附近的讀取重新校正、對鹼基品質分數重新計算，讓後續變異呼叫更準。
- **MosaicHunter**: 第一種 mosaic caller，靠 Bayesian likelihood 模型判定 mosaic。
- **Mutect2 + DeepMosaic**: 第二種組合，先用 Mutect2 掃候選，再用深度學習從讀取排列圖片判定 mosaic。
- **Mutect2 + MosaicForecast**: 第三種組合，先 Mutect2 掃候選，再用隨機森林分類器判定 mosaic。
- **Mutect2 ∩ Strelka2 (paired)**: 第四種，把左右心壁合併當「乾淨對照」，用 tumor-normal 差異呼叫個人化 mosaic。
- **Panel of Normals (PoN)**: 15 個精子 + 11 個血液樣本組成的參考池，用來排除定序流程系統性錯誤與 CHIP-like recurrent hotspot。
- **gnomAD (v2.1.1)**: 彙整 15 萬人變異頻率的公開資料庫，AF > 0.001 的位點視為 germline polymorphism 排除。
- **UCSC SegDup / RepeatMasker**: 基因體重複序列與 segmental duplication 遮罩，排除 alignment 難處理的假陽性熱點。
- **CHIP**: 造血幹細胞成年後 clonal expansion 產生的 mosaic 突變，AF 幾個 percent 難與胚胎 mosaic 區分，需要 PoN + 相鄰組織一致性條件排除。
- **AF (allele frequency)**: 同一位點被讀到帶突變的比例，是 mosaic 呼叫與後續 clone size 推估的核心量。

5. 與此篇文章的關係:

在《Developmental organization of sensory and sympathetic ganglia》這篇文章中，作者的目標是把「天然發生的 somatic mosaic variant」當條碼追蹤人類胚胎 NC 的家族樹。為了讓下游的 MPAS 驗證與 hypergeometric 群體大小估算不被雜訊污染，作者建立這條四工具聯合 WGS 呼叫 pipeline：吃進 30× 神經節與 300× 器官定序資料，輸出一份「已排除 germline、CHIP 與 alignment artifact」的候選 mosaic variant 清單 (ID06 3,357、ID07 3,380、ID08 2,415 個)。這解決了單一 caller 系統性漏抓與族群 polymorphism 誤判的雙重瓶頸，是整個 MVBA 框架能不能拿到可信條碼的第一道總開關。
