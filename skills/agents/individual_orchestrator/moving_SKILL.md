# Moving Pipeline

## 目標

把已 finalize 的 paper（`<paper_dir>/final/` 內全部產物）複製到本人 GitHub Pages 倉庫 `wenjchao.github.io/workspace/<paper_slug>/`，使其成為網站可訪問的論文頁。

這是 mapping pipeline 之後、發佈前的最後一步（mechanical）。

## 參數

| 變數 | 預設 | 說明 |
|---|---|---|
| `paper_dir` | （必填） | 來源 paper 目錄，例：`workspace/pediatric-tri-tube-valved-conduit`。其 `final/` 子目錄是要複製的內容 |
| `paper_slug` | basename(`paper_dir`) | 用作目的端資料夾名稱 |
| `github_io_root` | `/Users/wenj/Courses/wenjchao.github.io` | GitHub Pages repo 本地路徑 |

## 路徑慣例

- 來源：`<paper_dir>/final/`（mapping_merger 已寫好的 finalize 產物，含 HTML、figures/、summary.md 等）
- 目的：`<github_io_root>/workspace/<paper_slug>/`（如不存在會建立）
- 對應關係：`final/` 內所有檔案 / 子目錄複製進 `<paper_slug>/`（**等同於把 `final/` 改名為 `<paper_slug>/`**）

例：
```
workspace/pediatric-tri-tube-valved-conduit/final/
  ├── pediatric-tri-tube-valved-conduit.html
  ├── pediatric-tri-tube-valved-conduit.md
  ├── pediatric-tri-tube-valved-conduit_summary.md
  ├── figures/
  └── method/
```

複製後：
```
wenjchao.github.io/workspace/pediatric-tri-tube-valved-conduit/
  ├── pediatric-tri-tube-valved-conduit.html
  ├── pediatric-tri-tube-valved-conduit.md
  ├── pediatric-tri-tube-valved-conduit_summary.md
  ├── figures/
  └── method/
```

## 流程

### Step 1：前置驗證

確認來源齊全：
1. `<paper_dir>/final/` 存在
2. `<paper_dir>/final/<paper_slug>.html` 存在（mapping_merger 應已寫入；若無代表 mapping pipeline 未完成）

確認目的端 root 存在：
3. `<github_io_root>/workspace/` 存在（如不存在則 abort 並要求 user 確認 github.io 路徑）

### Step 2：同步

**[mechanical]** 對每個 paper 跑一次 rsync：

```bash
mkdir -p <github_io_root>/workspace/<paper_slug>
rsync -a <paper_dir>/final/ <github_io_root>/workspace/<paper_slug>/
```

注意：
- 末尾 `/` 在 `rsync` 是必要的——`final/`（有斜線）代表「複製內容」而非「複製 final 這個目錄本身」
- `-a` = archive：保留 mtime、permission、recursive、symlinks
- **不加 `--delete`**：目的端可能有 user 自行加的檔案（如 `_old.html` 備份），不該被刪
- 同名檔會被覆蓋（這是預期行為——`final/` 是 source of truth）

### Step 3：批次處理

要一次處理多篇 paper 時，list 所有 `paper_slug` 跑 loop：

```bash
DEST_ROOT=/Users/wenj/Courses/wenjchao.github.io/papers
for slug in <slug1> <slug2> ...; do
  src=workspace/$slug/final
  dst=$DEST_ROOT/$slug
  mkdir -p "$dst"
  rsync -a "$src/" "$dst/"
done
```

### Step 4：交還給 user

複製完成後**不要**自動 `git add` / `git commit` / `git push` 到 `wenjchao.github.io`——那是 user 自己的 deploy decision。回報：

- 每篇 paper 在目的端的 item count 與 total size
- 哪些 paper 是新增、哪些是覆蓋既有
- 任何 rsync warning / error

## 注意事項

- `wenjchao.github.io` 是 user 個人的 GitHub Pages 倉庫，這支 SKILL 只負責「把 final/ 內容塞進去」這個 mechanical 步驟，**不負責** site-level 結構（`index.html`、navigation、CSS theme）——那些由 site 自身的 build 流程處理
- 若 user 要把 paper 從 site 上下架，請 user 自行刪除 `<github_io_root>/workspace/<paper_slug>/`，這支 SKILL 沒有 reverse 操作
- 若 source 端的 `final/<paper_slug>.html` 經過 `mapping_merger_script.py` 之後 self-check 沒有 11/11 PASS，請先回去修 mapping 而不是搬到網站
