# MPAS/snMPAS AF 定量與二項式信賴區間過濾

1. 引用自哪篇 paper: developmental-organization-sensory-sympathetic-ganglia
2. Outline (任務主線): MPAS/snMPAS AF 定量與二項式信賴區間過濾
3. Method:

上一步 WGS pipeline 呼出每人 2,000–3,000 個候選 mosaic 後，接下來就要驗證是不是真的。作者拿這些候選 + 一批「已知是 het (AF 應該 ~50%)」和「已知是 hom (AF 應該 ~100%)」的參考位點設計一組專屬 amplicon panel——原理是「用一組事先設計好的引子把想看的幾千個 DNA 位點一次同時擴增出來 (multiplex PCR)」再定序，這樣能用同樣的定序容量把每個目標位點看到 ~10,000×，遠比 WGS 300× 深，這對「AF 只有 1% 的 mosaic」特別重要。定序完後對每個位點算 exact binomial 95% CI——把「多少 read 讀到 alt / 總 read」當成丟硬幣的樣本比例，用二項式分布公式直接解出「真正 AF 有 95% 機率落在這個下界到上界之間」。這裡選 exact (Clopper-Pearson) 而不是常用的 Wald 近似，是因為作者的 AF 常常很接近 0 (mosaic 1% 級) 或很接近 1 (hom 位點)，Wald 法在這種邊界會給出「下界是負的」這種不合理答案，exact 法則永遠在 [0, 1] 之間。

接著關鍵的一步是切門檻。理論上 het 位點 AF = 0.5、hom = 1.0，但實際定序資料裡完全不是這樣——PCR 對兩條 allele 可能不平衡 (amplification bias)、引子可能有 strand bias、有些位點特別容易 dropout。結果 het 位點的 AF 在 ID06 上分布 0.408–0.580、ID07 是 0.417–0.571、ID08 是 0.464–0.538，每位 donor 都不一樣。如果直接套「AF < 0.5 就算 mosaic」，ID06 那些其實是 het 但 AF 被壓到 0.42 的位點會被誤判成 mosaic；同樣 ID08 的 hom lower cutoff 只有 0.0035，如果套 default lower 0.02，很多真 low-AF mosaic 會被誤判成背景雜訊丟掉。作者的解法是把 het / hom 位點跟 mosaic candidate 一起放進同一個 panel、同一個 PCR、同一個 lane 上機——同批次的雜訊分布才能就地校準。從實測分布切出「95% 的 het 都會落在 AF ≤ 這個上界」當 mosaic upper cutoff、hom 位點切出 lower cutoff，這樣三位 donor 切出來的判定都對應同樣的 5% FDR。

最終一個 candidate 要當「真 mosaic」，必須同時通過六條門檻：(1) lower CI > donor 專屬的 mosaic cutoff，擋「其實是雜訊、AF 貼近 0」；(2) 每個 pool 都跑一個 unrelated control DNA，若對照上此位點的 upper CI 也很高，代表 index hopping 或跨樣本污染要排除；(3) upper CI < het threshold，擋 germline het (它們 AF ~0.5)；(4) 定序深度 > 30 才算樣本量足夠；(5) 至少 3 條 read 支持 alt，擋 sequencing 的單一 read 錯誤；(6) 這位點曾在原始 WGS 組織或相鄰 DRG/SG 被呼出來——確認 mosaic 有時空一致性，不是憑空冒出來的 amplicon artifact。六條全過才算 pass；少一條就會有一種假陽性漏進 clone 分析，例如少 (2) 會把樣本間污染當跨器官 shared clone、少 (6) 會把 amplicon-specific hotspot 當真 mosaic。經過這道六條篩選後，ID06 有 827 個 candidate 通過 (32.5%)、ID07 有 252 (9.7%)、ID08 有 511 (27.0%)——就是最終送去畫 clone tree 的骨幹清單。

當作者把 MPAS 拉到單顆核細胞 (snMPAS) 時，還要多做一層 QC。snMPAS 從一顆核抓 DNA、擴增再定序——單顆核只有兩份 allele，任一份沒被擴增到 (allele dropout) 都會嚴重扭曲 AF 判定。作者用「已被 bulk 驗證是 het 或 hom」的參考位點在這 224 顆核上重新讀：理論上 het 位點應該永遠讀到雙 allele，實測 ~19% 只讀到單一 allele——這就是 dropout rate；hom 位點應該只讀到單一 allele，但 ~5% 意外讀到 alt——這就是 false positive rate。這兩個數字很重要因為會直接扭曲下游 clone 分析：dropout 意味每 5 顆真正帶 mosaic 的核有 1 顆被誤判「沒帶」，若不校正，原本應聚同一群的兄弟細胞會被錯分到不同支、畫出來的 phylogenetic tree branch 不合理變長、共同祖先 pop size 也會被高估。事先量出 19% 與 5% 就是為了讓下游模型能校正這種系統偏差。

4. 工具與材料:

- **MPAS**: Massively Parallel Amplicon Sequencing，一組引子 multiplex PCR 擴增指定位點後定序到 ~10,000× 超深度。
- **snMPAS**: MPAS 用在單顆核細胞 (single nucleus) 的版本，用來把 mosaic barcode 對到具體 neuron/glia。
- **exact binomial 95% CI (Clopper-Pearson)**: 從二項式分布累積機率函數直接解出的信賴區間，永遠落在 [0, 1] 且對小樣本、邊界值都穩定。
- **donor-specific het/hom thresholds**: 以該 donor 自身 het (AF~50%) 與 hom (AF~100%) 位點的實測分布切出的 5% FDR upper/lower cutoff。
- **unrelated control DNA**: 每個 pool 都跑一份無關對照，用來偵測 index hopping 或跨樣本污染。
- **mosaic call 六條件**: lower CI > donor cutoff + control 無訊號 + upper CI < het threshold + depth > 30 + ≥3 alt reads + 相鄰 tissue 一致性，六條全過才算 pass。
- **dropout rate (~19%)**: snMPAS 從 het 位點被誤判成 hom 的比例，代表單顆核 allele 沒被擴增到的機率。
- **false positive rate (~5%)**: snMPAS 從 hom 位點被誤判有 alt read 的比例，用來校正下游 genotype call。

5. 與此篇文章的關係:

在《Developmental organization of sensory and sympathetic ganglia》這篇文章中，作者的目標是把 WGS pipeline 呼出的 mosaic 候選變成可信的 clonal barcode 用來畫神經節家族樹。為此他們用 AmpliSeq MPAS 做 ~10,000× 超深度定序、以 exact binomial CI 加上 donor-specific het/hom 門檻切出 5% FDR，把每位 donor 幾千個候選壓到幾百個 gold-standard mosaic (ID06 827、ID07 252、ID08 511)。這解決了「WGS 300× 對 1% AF mosaic 敏感度不足」與「default cutoff 對不同 donor 給出不同 FDR」的雙重瓶頸；同時 snMPAS 的 dropout / false positive rate 也校正了單核 phylogenetic tree 的系統偏差。
