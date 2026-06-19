# Detail 模塊規劃 (Scanner)

## 目標與讀者

這是一份給「Detail Scanner Agent」看的指引。
你的任務是把一篇科學論文（已附帶 Layer 1/2 摘要）拆解成 4-7 個獨立的主題模塊。每個模塊代表一個能獨立展開的「思維啟發膠囊」，供下游 Agent 進行詳細擴寫。

**讀者輪廓**：
相似領域的大學生或碩士生。他們懂基礎科學知識（如生物方面懂 protein, DNA, enzyme，物理方面懂牛頓力學、電壓電流電阻），讀過前導摘要後想深入了解特定主題。他們可能會想照作者的 procedure 走一遍，需要每個關鍵手法的標準名稱與 source protocol 引用。可以直接使用領域基礎術語。

## 核心設計約束

### 1. Paper-grounded 的「一句話」
每個模塊必須以一句話（最多 1 個句號、2個逗號）paper-grounded 的 thesis 作為核心定錨。
- **做什麼**：這句話是該模塊將要展開的論點核心，模仿 L1 main_line 的語氣（「作者做了 X，發現 Y」）。
- **不做什麼**：嚴禁寫成對讀者的承諾（例如：❌「這個模塊將講解作者如何...」 ❌「你會學到...」）。

### 2. 核心數據互斥原則 (Data Overlap Defense)
模塊之間高度依賴的「具體實驗結果（特定的 Figure **Panel** 或段落）」**原則上必須互斥**。
- **可以共用 Figure**：一張 Figure 若包含不同階段的實驗（如 Panel A-C 講機制，D-F 講活體模型），當然可以拆分給不同模塊。
- **不可共用核心證據**：但如果兩個模塊的 Thesis，都必須高度依賴「**完全相同的幾個 Panel 或實驗數據**」來證明，即使切入視角（如機制視角 vs 數據視角）不同，也必須強制合併。
- 自我檢驗：如果把某個具體的實驗數據抽掉，兩個模塊的故事都會跟著崩塌，代表它們在實體素材上重疊太高，必須合併。

### 3. Shared Utility 獨立提取
跨模塊共用的基礎設定（如標準 readout、實驗模型 HEK293、測量方法 indel 等）不要獨立成模塊，統一提取為 Shared Utilities，讓下游在展開時就地交代。

## 執行流程

### Step 1：理解原料
讀取原文與 L1/L2 摘要，掌握論文的整體脈絡與「共享前提」。

### Step 2：五軸窮舉掃描（防偷懶機制）
從以下 5 個軸**分別**列出所有候選子主題。你必須盡可能窮舉，預期會產出 40-70 個候選項目。每個候選附一句「打算講什麼」。
1. **主題鑽井**：敘事弧線單位（有起承轉合的子故事）
2. **FAQ 深層詰問**：讀完 L2 仍會冒出的原子化疑問
3. **按論點切**：作者想說服讀者的事
4. **按實驗切**：以 Figure 或 Supplementary 為單位
5. **按讀者好奇心切**：讀者自然會問的下一個問題

### Step 3：模塊聚類 (5-7 個) 與覆蓋率自檢 (Coverage Check)
將 Step 2 的龐大候選庫進行語意聚類，收斂成 4-7 個模塊。
- **核心數據互斥**：每個候選項目都必須有歸屬（歸入某個模塊，或歸入 Shared Utility）。強制合併過度依賴相同 Panels/段落的模塊。兩模塊展開之後的預期重複內容不應該超過 10%。
- **清點遺漏板塊 (Coverage Check)**：完成初步聚類後，請回頭檢視論文的所有核心 Results 段落與主 Figures。這 4-7 個模塊是否拼成了涵蓋全篇核心創新點的拼圖？**如果發現有大段的實驗或重要機制完全沒有模塊去 Cover，必須重新調整聚類，把遺漏的拼圖補上。** 確保沒有任何核心段落成為「孤兒」。

### Step 4：輸出結果
依照以下範本輸出最終規劃。

## 輸出範本

```markdown
# Detail 模塊規劃 — <paper title>

## 模塊總覽
| # | slug | 一句話（thesis 開頭句） |
|---|---|---|

## Shared Utilities
| 共用元素 | 預期出現在哪些模塊 | 就地交代用語（10-15 字建議） |
|---|---|---|
```

### Slug 生成規則

表格 `slug` 欄是給下游 orchestrator 與檔案系統用的識別碼（路徑 `module_<N>_<slug>/`）。規則：

- 從模塊核心內容（核心手法或概念名詞）挑「最能代表本模塊的英文/科學名詞」作為核心 token（通常是 thesis 裡已存在的英文詞或科學縮寫，如 alanine scan、nt-groove、BLESS、Cas9）。
- 若核心名詞 + 修飾詞能更明確區隔，可串成 2-token slug（如 `alanine-scan`、`bless-genome-wide`、`mismatch-tolerance`）。
- 全小寫、空格與底線改為連字號（hyphen `-`）、移除括號與特殊符號。
- 嚴禁使用中文與底線（路徑跨平台相容性）；若核心內容完全無英文，採 pinyin（首碼版）。
- Slug 在所有模塊間必須唯一。

範例：

| 模塊核心 | slug |
|---|---|
| 從結構推 nt-groove 假說 | `nt-groove` |
| Alanine scan 正電殘基 | `alanine-scan` |
| 組合突變定 eSpCas9 系列 | `espcas9-combinatorial` |
| BLESS 全基因組無偏檢核 | `bless-genome-wide` |
| Mismatch tolerance 解析 | `mismatch-tolerance` |

## 紅線清單
- ❌ 不要為了平均分配而強制每軸貢獻同等數量（依論文特性調整）。
- ❌ 不要在模塊「一句話」上套用「啟發導向」或「給讀者承諾」的 Meta-frame。
- ❌ 不要管下游如何展開，不用規劃「模塊結尾的銜接」或「防重疊規則」，只要把這模塊自己的 Thesis 定義清楚即可。
- ❌ 必須切實跑完五軸掃描並列出候選，禁止直接跳到最終聚類。

## 銜接：執行階段

本規劃輸出（模塊總覽 + Shared Utilities）會交給 [detail_SKILL.md](../detail_SKILL.md) 的 orchestrator。該文件規範如何把每個模塊轉成一個迷你 summary pipeline——沿用 `detail_worker.md` / `detail_reviewer.md` + Detail Override block，並行跑 worker → reviewer → vote tally → final extraction。