#!/bin/bash
# 雙擊這個檔案：啟動本機小伺服器並打開瀏覽器（http://localhost:8765）。關掉這個終端機視窗就會停止。
# 第一次打開若 macOS 說「無法打開」，對檔案按右鍵 → 打開 → 打開 即可。
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  python3 serve.py "$@"
else
  echo "找不到 python3。macOS 請先執行：xcode-select --install（或到 python.org 安裝）。"
  read -r -p "按 Enter 關閉…" _
fi
