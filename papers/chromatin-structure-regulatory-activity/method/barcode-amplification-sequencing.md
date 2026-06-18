# mRNA / gDNA 條碼放大與 Illumina 定序

1. 引用自哪篇 paper: chromatin-structure-regulatory-activity
2. Outline (任務主線): mRNA / gDNA 條碼放大與 Illumina 定序
3. Method: 
   整個放大-定序流程是「分流抽—逆轉錄—條碼擴增—加 adapter—定序」。(1) 每個 replicate 收 1.75 × 10⁷ 顆 FACS 過的細胞，同一批細胞分流兩份：一份用 Ambion ToTALLY RNA kit 抽 RNA，另一份依廠商 protocol 抽 gDNA。RNA 那份再用 Turbo DNase 跑兩輪嚴格 DNase 處理 (Rigorous DNase treatment)——RNA 跟 gDNA 上都有同樣的 cBC-gBC 條碼，任何殘留 gDNA 都會在後續 PCR 變成假 RNA 訊號，所以兩輪 DNase 是把殘留壓到偵測極限以下的核心保險。(2) RNA 用 SuperScript III First-Strand Synthesis 加 oligo(dT) primer 逆轉錄 (reverse transcription) 成 cDNA——oligo(dT) 只認 mRNA 3' 端的聚 A 尾巴，從那裡反向合成，剛好把 dsRed 3' UTR 裡的 cBC 區段優先涵蓋，而且不會把 rRNA / tRNA 收進來。(3) 用 LP32/LP33 引子 PCR 放大整段 cBC-gBC 條碼對（NEB HF Phusion MM，20 cycles）。(4) PCR 產物用 EcoRI + SphI 切出黏端、接上含 multiplex index 的 Illumina adapter，再用 LP30/LP31 引子做第二輪 PCR 放大；分兩輪是因為一輪沒辦法同時擴增又裝載 adapter。(5) 最後上 Illumina NextSeq 1 × 150 bp 定序，跑兩重複——DNA 平均拿到 4.004 × 10⁷ reads、RNA 平均 1.225 × 10⁷ reads；資料釋出於 NCBI SRA accession PRJNA394868。

   為什麼要用 log₂(RNA reads / DNA reads) 而不是直接看 RNA reads？因為光看 RNA reads 沒辦法分辨「訊號強」是因為這個位置 × CRS 組合的細胞多，還是因為單份模板的轉錄效率高。DNA reads 反映該組合在群體中佔多少細胞 (integration abundance)；RNA reads 同時受「細胞數」與「轉錄效率」影響。相除後細胞數因子被消掉，剩下純粹的「平均每份 DNA 模板被轉錄成多少 RNA」——這才是 CRS-位置組合真正的轉錄活性。這個標準化把 Cre 置換效率不均、FACS bias、細胞分裂差異一次抵銷，DNA reads 同時兼任內生 normalizer 與品質指標。

   PCR jackpot 是什麼？PCR 的指數擴增有個特性——頭幾個 cycle 哪條模板被先擴到，往後就會被持續放大。如果模板量少，最後出來的 reads 可能 90% 都來自最初幾條「中獎」模板，其他被嚴重低估，這就是 jackpot。對「條碼計數」這種需要精確定量的實驗是致命傷。作者用多次稀釋多重複設計：gDNA 跑 10 × 700 ng + 40 × 75 ng + 40 × 500 ng 共 90 個獨立 PCR——高 input (700 ng) jackpot 概率低；低 input (75 ng) jackpot 概率高但 40 管獨立抽樣分散風險；中 input 過渡。90 個獨立反應 pool 後任何單一管的 jackpot 都被攤平，這是用大數法則對抗指數放大隨機性的低成本策略。cDNA 只跑 2 replicates 是因為 RNA 模板數本身遠少於 gDNA，jackpot 風險已較低。

   兩個步驟若省掉，整個定量會壞在哪？(1) RNA 若沒做兩輪 Rigorous DNase 處理，混進來的 gDNA 條碼會跟著被 LP32/LP33 擴增、計入「RNA reads」——即使某個位置 × CRS 組合根本沒在轉錄，看起來也有訊號，log₂(RNA/DNA) 全部往 0 集中，整個 patchMPRA 的訊號維度坍塌。(2) gDNA 條碼擴增若只跑一管大反應而不是 90 個獨立稀釋 PCR，jackpot 概率最高——少數中獎條碼主導 library、多數條碼被嚴重低估甚至消失，精確計數的任務完全失效。兩件事各自管不同雜訊源，一個都不能省。
4. 工具與材料: 
   - **Ambion ToTALLY RNA kit**: 從 1.75 × 10⁷ 細胞抽 RNA 的試劑套組。
   - **Turbo DNase (兩輪 Rigorous treatment)**: 嚴格 DNase 處理，把 RNA 樣本中殘留的 gDNA 消化到偵測極限以下，防止 gDNA 條碼變成假 RNA 訊號。
   - **SuperScript III + oligo(dT)**: 逆轉錄酶與只認 mRNA 3' 端聚 A 尾巴的引子；從 3' 端優先合成 cDNA，剛好涵蓋 cBC，且排除 rRNA/tRNA。
   - **LP32 / LP33**: 條碼擴增的第一輪 PCR 引子，放大整段 cBC-gBC 條碼對；NEB HF Phusion MM，20 cycles。
   - **Multi-dilution multi-replicate PCR (90 反應)**: gDNA 跑 10 × 700 ng + 40 × 75 ng + 40 × 500 ng 共 90 個獨立 PCR；pool 後攤平 PCR jackpot 雜訊。
   - **EcoRI + SphI adapter ligation**: PCR 產物經兩種酶切出黏端，接上含 multiplex index 的 Illumina adapter，方向唯一。
   - **LP30 / LP31**: 第二輪 PCR 引子，把整段（條碼 + adapter）擴增到 Illumina library 所需濃度。
   - **Illumina NextSeq 1 × 150 bp**: 最終定序平台；DNA 平均 4.004 × 10⁷ reads / replicate，RNA 平均 1.225 × 10⁷ reads / replicate。
   - **log₂(RNA reads / DNA reads)**: 單一 barcode 的活性量化指標；DNA reads 兼任細胞數 normalizer 與品質指標，相除消去整合事件數雜訊。
   - **NCBI SRA PRJNA394868**: 本研究定序資料的公開釋出 accession。
5. 與此篇文章的關係: 
   在《A massively parallel reporter assay dissects the influence of chromatin structure on cis-regulatory activity》這篇文章中，作者要量化每個 CRS 在每個 landing pad 上的轉錄活性。本步驟同步抽 RNA 與 gDNA 並放大 cBC-gBC 條碼對，解決了「Cre 置換效率不均、FACS bias 會把訊號污染」的瓶頸——DNA reads 兼任內生 normalizer。產出 Illumina NextSeq 高深度條碼定序資料，作為下一步乾實驗 log₂(RNA/DNA) 量化與線性模型擬合的原始輸入。
