# 目標

這是一份給 `figure_repair` agent 看的指引。

Repair 的工作很窄：讀取 assignment 指定的 canonical repair request，修復被指派的 crop / preview / allowlisted manifest 欄位，然後把 repair-local artifacts 和 machine-readable merge 指令寫進 `repair_report.json`。Repair 不直接寫 canonical，也不做最終接受判定。

此流程使用場景與目標：
- 輸入：一個 paper directory、repair round / repair assignment、`canonical_artifact_root`、`repair_artifact_root`，以及 assignment 指定的 canonical `request_file`。
- 讀取位置：
    - `lanes/figures/canonical/`：目前 canonical figure extraction artifacts、canonical review、canonical repair request。
    - `shared/pages/`：完整解析度頁面圖片，這是重新裁切的來源真相。
- 輸出位置：`<paper_dir>/lanes/figures/repairs/round_<N>/repair_<ID>/`
- 輸出：
    - `repair_report.json`：本次修復結果與 machine-readable merge 指令。
    - `crops/`：修復後完整解析度 crop PNG。
    - `boundaries/`：修復後完整解析度 boundary 圖片。
    - `previews/`：修復後 crop preview、boundary preview、bottom band segments、bottom microzoom patches。
    - `manifest_updates/`：只有需要整檔 replacement manifest 時才寫。

第一階段不使用 hash。Repair report 不寫 `crop_hash`，self-check 不做 SHA-256。

# 流程

## 輔助工具

Repair 需要重新裁切或建立 preview 時，只使用本 skill 內的 local helper：

- `agents/scripts/crop_and_preview.py`：一次完成裁切 + evidence preview（crop、crop preview、boundary preview、top/left/right edge strips、bottom band、bottom microzoom）。recrop action 使用此工具。
- `agents/scripts/make_image_preview.py`：建立單張 preview。用於 `regenerate_missing_preview` action。
- `agents/scripts/build_repair_report.py`：從 `decisions.json` 自動組裝完整 `repair_report.json`。
- `agents/scripts/validate_figure_repair.py`：檢查 `repair_report.json` contract、repair-local path、merge 指令、manifest patch 配對與 summary 一致性。不做 hash，也不判斷修復後圖片是否視覺接受。

不要直接呼叫 `skills/_shared/scripts/...`。Repair output 先寫在本輪 repair 目錄；不要直接更新 canonical。

## 工作流程

### 準備修復資料

1. 確認 repair assignment：`repair_round`、`repair_id`、`canonical_artifact_root`、`repair_artifact_root`、`request_file`。若未指定 repair id，使用輸出目錄名稱（例如 `repair_01`）。

2. 讀取 assignment 指定的 `request_file`。它是本輪 canonical repair request。

只處理 `assigned_repair_id` 等於本 repair id 的 requests。不要直接把 reviewer working directory 裡的 `visual_review.json` 當成主要輸入。

3. 讀取 canonical 中和被指派 figures 相關的 artifacts：
   - `figures.json`
   - canonical crop PNG、crop preview、boundary preview、edge strips、bottom band、bottom micro
   - request 中列出的 `source_review`，例如 `reviews/round_00/reviewer_01/visual_review.json`（以 `canonical_artifact_root` resolve）

4. 針對每個 request，確認它是否只影響被指派的 figure / crop unit：
   - 只影響被指派的 crop unit → 繼續修復。
   - 需要同步修改相鄰 figure，但相鄰 figure 不在本輪 assignment → 標 `blocked`。
   - request 指向的 figure 或 crop unit 不存在於 canonical manifest → 標 `unresolved`。

### 讀取目前 canonical evidence

5. 對每個要修復的 crop unit，直接讀取 canonical 中已有的 evidence 作為修復前狀態：
   - canonical crop preview
   - canonical boundary preview
   - canonical bottom band segments（`bottom_band`）
   - canonical bottom microzoom segments（`bottom_micro`）

   這些 evidence 和 reviewer 讀到的相同，不需要重新建立。

### 決定修復動作

6. 根據 repair request 的 `action`、`direction`、`constraint` 和 canonical / source evidence 決定修復：
   - `recrop`：更新 `crop_px`，重新裁切 crop、crop preview、boundary preview、bottom band、bottom micro。
   - `regenerate_missing_preview`：不改 `crop_px`，只重新建立缺失 preview、boundary preview、bottom band 或 bottom micro。
   - `manifest_correction`：只修正 allowlisted manifest 欄位，不一定重裁。
   - 其他 action：若無法確定如何修，標 `unresolved`，不要猜。

7. 若要重裁，新的 `crop_px` 必須使用完整解析度頁面圖片 pixel coordinate。用 `crop_and_preview.py` 從 `shared/pages/page_N.png` 一次完成裁切和全套 evidence preview。不要從舊 crop、source region、preview 或其他中間圖片再裁一次。

8. 修復同一 figure 的多個 crop units 時，只修改需要修復的 crop units。未改動的 crop unit 必須保留原本的 `crop_id`、`page`、`crop_px`、`image_file`、`preview`、`boundary_preview`、`bottom_band`、`bottom_micro` 與 `role`。

### 修復後視覺檢查

9. 使用 `crop_and_preview.py` 一次完成修復後的裁切和全套 evidence preview：

   ```bash
   python3 agents/scripts/crop_and_preview.py \
     --page-image shared/pages/page_N.png \
     --crop-px <new_x1> <new_y1> <new_x2> <new_y2> \
     --crop-id <crop_id> \
     --output-dir <repair_artifact_root>
   ```

   一次呼叫產生：crop、crop preview、boundary preview、bottom band segments、bottom microzoom segments。`_micro` suffix 自動處理。

10. 讀取修復後 evidence：crop preview、boundary preview、bottom band segments、bottom microzoom segments。和 step 5 讀到的 canonical evidence 對照，確認：
   - reviewer finding 指出的 defect 已被處理。
   - boundary preview 上沒有 figure 內容跨過 cyan 線，cyan 框內沒有外部 caption、正文、page chrome 或相鄰內容。
   - bottom band 和 bottom microzoom 上沒有 figure 內容跨過 cyan 線，且 cyan 線外側沒有貼著外部 caption、正文、page chrome 或相鄰內容。
   - crop preview 上 figure 內部細節完整。
   - crop 不是整頁、整欄或過大的 page strip。

11. 如果修復後仍不正確，回到 step 7 調整 `crop_px`，重裁、重建 preview、重新檢查。不要直接修改 PNG，也不要只手改 `figures.json`。

12. 如果 source layout 讓 figure 內容和非 figure 內容無法乾淨分離，優先保留 figure 的全部內容，在 `repair_report.json` 標為 `unresolved`。不要為了裁掉非 figure 內容而切掉 figure 內容。

### 寫出 repair report

13. 為每個處理過的 request 寫一筆 decision 到 `decisions.json`：

    ```json
    [
      {
        "request_id": "Extended_Data_Figure_1_f001",
        "figure_id": "Extended_Data_Figure_1",
        "figure_label": "Extended Data Fig. 1",
        "crop_id": "Extended_Data_Figure_1",
        "result": "repaired",
        "action_taken": "recrop",
        "new_crop_px": [72, 175, 2410, 1158],
        "notes": ["Excluded Article header and external caption"]
      }
    ]
    ```

    `new_crop_px` 可選：有 → recrop；沒有 → regenerate_missing_preview / manifest_correction。`result` 為 `"unresolved"` / `"blocked"` 時不需要 `new_crop_px`。同 figure 多個 request 各寫一筆，`new_crop_px` 用相同的最終值。不需要寫 `page`（工具從 canonical 查）。

14. 呼叫 `build_repair_report.py` 自動組裝完整 `repair_report.json`：

    ```bash
    python3 agents/scripts/build_repair_report.py \
      --repair-root <repair_artifact_root> \
      --canonical <canonical_artifact_root> \
      --request-file <repair_requests_assigned.json> \
      --decisions <repair_artifact_root>/decisions.json
    ```

    工具自動：掃 repair 目錄找 crops/previews/boundaries → 組 `file_copies[]` → 從 canonical 讀 `old_value` 產生 `manifest_patches[]` → 從 canonical 查 `old_crop_px`/`page`/`role` → 組 `updated_crop_units[]` 和 `evidence_read` → 算 `summary` → 寫 `repair_report.json`。

    不需要手寫 `file_copies[]`、`manifest_patches[]`、`updated_crop_units[]`、`evidence_read` 或 `summary`。

15. 寫出 `repair_report.json` 後、回報完成前，執行 mandatory JSON self-validation（見規則段「機械自檢」）。validator 失敗時，必須修正 decisions 或 artifacts 後重跑 `build_repair_report.py` 和 validator。

16. 回報本輪處理的 requests、成功修復 / 未解決的 figures，以及 `repair_report.json` 路徑。

# 格式

## JSON 格式

開始工作前，**必須** Read 以下 schema 檔案。Schema 包含完整欄位定義、enum 值及其描述、JSON example。

- `repair_requests_assigned.json`：`agents/schemas/repair_request.schema.md`
- `repair_report.json`：`agents/schemas/repair_report.schema.md`

`repair_report.json` 由 `build_repair_report.py` 自動組裝，agent 不手寫。

### repair_report 行為規則（build_repair_report.py 自動處理，但 agent 應知道）

- `repair_round` 和 `repair_id` 必須和所在目錄 `round_<N>` / `repair_<ID>` 一致。
- `status`：所有 assigned requests 都完成才是 `complete`；有 `unresolved` 或 `blocked` 就是 `incomplete`。
- `repairs[].requires_review`：任何修改 crop、preview 或 manifest 的 repair 都必須是 `true`。
- `merge.manifest_patches[].target_file` 只能是 `figures.json`（`figure_decisions.json` 不進 canonical）。
- `summary` counts 必須和 `repairs[]` 一致。

## Artifact root 相對路徑

- `canonical_artifact_root`：`<paper_dir>/lanes/figures/canonical/`
- `repair_artifact_root`：`<paper_dir>/lanes/figures/repairs/round_<N>/repair_<ID>/`
- `repair_output` 使用 repair artifact root 相對路徑
- `canonical_target` 使用 canonical artifact root 相對路徑
- 不要在路徑裡寫 `lanes/figures/canonical/`、`lanes/figures/repairs/...` 或絕對路徑

# 規則

## 權責

- `figure_repair` 只修復 assigned repair requests。
- 不重新執行 initial extraction，不重建完整 figure inventory，不做 final independent review。
- 不直接覆蓋 `lanes/figures/canonical/`；修復圖片、preview 和 merge 所需資訊先寫在本輪 repair 目錄。
- 不修改來源 PDF、canonical review、canonical repair request、`before_snapshot/`。
- 任何 canonical artifact 被修改後，對應 figure 先前的 review 都失效，必須重新跑 `figure_reviewer`。

## 修復範圍

- 只處理 assignment 指定的 `request_file` 中分派給本 `repair_id` 的 requests。
- 如果 request 需要改到相鄰 figure，但相鄰 figure 未被指派，標 `blocked`。
- 修復同一 figure 的多個 crop units 時，只修改需要修復的 crop units。未改動的 crop unit 必須保留原本的 `crop_id`、`page`、`crop_px`、`image_file`、`preview`、`boundary_preview`、`bottom_band`、`bottom_micro` 與 `role`。
- 如果需要新增或移除 crop unit，保留同一個 `figure_id`，在 `repair_report.json` 記錄 merge section 應如何同步更新。新增 crop unit 的 `crop_id` 必須 filename-safe 且不與既有 `crop_id` 衝突。

## 裁切與座標

- 所有 `crop_px` 都使用完整解析度頁面圖片的 pixel coordinate。
- Final crop 永遠從 `shared/pages/page_N.png` 裁出（`--padding 0`），不要從 source region、preview 或其他中間圖片再裁一次。
- 座標換算時，邊界應保守外擴：左上角向外取整，右下角向外取整，再用 boundary preview、bottom band 和 bottom micro 收緊。

## 圖說與圖片邊界

- 外部 caption 存在 `caption_text`，不放進 crop。
- Figure-internal title、legend、axis label、panel label、scale bar、color bar、annotation 應保留在 crop 中。
- 排除正文、外部 caption、頁碼、頁眉、頁腳、期刊固定元素、浮水印、相鄰 figure、table、equation 與其他非 figure 內容。
- 如果非 figure 內容碰邊就縮小 crop，figure 內容碰邊就放大 crop。如果兩者因版面交錯無法乾淨分離，優先保留 figure 的全部內容，標 `unresolved`。

## 視覺檢查

- 每個標為 `repaired` 的 figure，repair agent 都必須讀過 canonical evidence（boundary preview、bottom band、bottom micro）和修復後 evidence（crop preview、boundary preview、bottom band、bottom micro）。
- 每個標為 `preview_regenerated` 的 figure，repair agent 至少必須確認缺失的 preview / boundary preview / bottom band / bottom micro 已在 repair 目錄產生、可讀取，且列入 `merge.file_copies[]`。
- 不確定就是 `unresolved`。
- 圖表型圖片的底邊與側邊風險最高：必須確認 x 軸刻度與標題、y 軸標籤、legend、color bar 和 plot boundary 完整。
- 大幅寬圖可以接近整頁寬度，但垂直方向仍應緊貼 figure；不得用整頁、整欄或大頁面條帶假裝修復成功。

## Manifest 一致性

- `repair_report.json` 的 `merge.manifest_patches[]` 必須足以將 canonical `figures.json` 更新到正確狀態；`updated_crop_units[]` 只作為 trace，不能取代 machine-readable patches。
- 不要留下 stale `crop_px`、stale `image_file`、stale `preview`、stale `boundary_preview`、stale `bottom_band` 或 stale `bottom_micro`。
- `repair_report.json` 是修復 trace 和 merge input，不是 canonical truth；merge 後的 final truth 以 canonical `figures.json` 和實際 PNG 檔案為準。

## 機械自檢

寫出/更新 `repair_report.json` 後、回報完成前，必須執行：

```bash
python3 agents/scripts/validate_figure_repair.py \
  "<repair_artifact_root>/repair_report.json"
```

若 validator 回傳 `status: "fail"`，先修正 repair-local artifacts、merge 指令或 `repair_report.json`，然後重跑 validator。Validator 通過前不得把 repair 回報為完成；若無法修，`repair_report.json.status` 必須是 `incomplete`。

此 validator 只檢查機械 contract：schema、status、repair-local paths、修復後 crop / preview / boundary / edge strips / bottom band / bottom micro 是否存在、`merge.file_copies[]`、`merge.manifest_patches[]`、summary count，以及不使用 hash。Mechanical self-check 通過不代表 final visual acceptance；最終接受判定來自下一輪 `figure_reviewer`。
