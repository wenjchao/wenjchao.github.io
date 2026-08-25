#!/bin/sh
# 跑全部測試（需要 Node 18+ 與 Playwright：npm i playwright && npx playwright install chromium）
set -e
cd "$(dirname "$0")"
export ROOT="$(cd ../.. && pwd)" HERE="$(pwd)" TMP="${TMPDIR:-/tmp}"
python3 "$ROOT/build.py" "$ROOT" -o "$TMP/single.html" > /dev/null
for t in test1 test2 test3 test4 test5 test6 test7 test9 test10 test11; do node "$t.mjs"; done
python3 test8_notion.py   # 純 Python：notion2modules.py 的轉換規則（需要 beautifulsoup4、lxml）
