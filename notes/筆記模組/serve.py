#!/usr/bin/env python3
"""
筆記模組 — 本機小伺服器（只用 Python 標準函式庫）

    python3 serve.py                  # 伺服「這個檔案所在的資料夾」，開 http://localhost:8765
    python3 serve.py ~/我的筆記        # 指定筆記資料夾
    python3 serve.py --port 9000
    python3 serve.py --host 0.0.0.0   # 讓同一個 Wi-Fi 的 iPad／手機也能連（只在信任的網路使用）

提供：
    GET  /                 → index.html（檢視器）
    GET  /api/modules      → 所有 .md 的清單（路徑、修改時間、大小）
    GET  /<路徑>.md        → 檔案本身
    PUT  /api/file?path=x  → 寫入（建立或覆蓋）x：.md 或圖片，給檢視器的「編輯」與貼圖功能用
    DELETE /api/file?path=x → 刪除 x（.md 或圖片）：檢視器的「刪除」與「改名／搬移」（先 PUT 新檔再 DELETE 舊檔）用
"""
import argparse, http.server, json, os, pathlib, sys, time, urllib.parse, webbrowser

HERE = pathlib.Path(__file__).resolve().parent
MD_EXTS = {'.md', '.markdown', '.txt'}
IMG_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.avif', '.bmp'}


def iter_files(root: pathlib.Path, exts):
    """走訪資料夾；略過隱藏項目、node_modules，以及放了 .noteignore 的資料夾。"""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith('.') and d != 'node_modules'
                             and not (pathlib.Path(dirpath) / d / '.noteignore').exists())
        for name in sorted(filenames):
            p = pathlib.Path(dirpath) / name
            if name.startswith('.') or p.suffix.lower() not in exts:
                continue
            yield p, p.relative_to(root).as_posix()


def list_modules(root: pathlib.Path):
    items = []
    for p, rel in iter_files(root, MD_EXTS):
        st = p.stat()
        items.append({'path': rel, 'mtime': int(st.st_mtime * 1000), 'size': st.st_size})
    return items


def make_handler(root: pathlib.Path, index: pathlib.Path):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(root), **kw)

        # --- 小工具 ---
        def _json(self, obj, status=200):
            data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _safe_path(self, rel: str):
            rel = urllib.parse.unquote(rel).replace('\\', '/').lstrip('/')
            target = (root / rel).resolve()
            if root != target and root not in target.parents:
                return None
            if any(part.startswith('.') for part in target.relative_to(root).parts):
                return None
            return target

        def end_headers(self):
            self.send_header('Cache-Control', 'no-store')
            super().end_headers()

        # --- 路由 ---
        def do_GET(self):
            u = urllib.parse.urlparse(self.path)
            if u.path == '/api/modules':
                return self._json({'writable': True, 'modules': list_modules(root)})
            if u.path in ('/', '/index.html') and index.parent != root:
                # index.html 不在筆記資料夾裡（例如 serve.py 指定了別的資料夾）時，仍然提供檢視器
                data = index.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                return self.wfile.write(data)
            return super().do_GET()

        def do_PUT(self):
            u = urllib.parse.urlparse(self.path)
            if u.path != '/api/file':
                return self._json({'error': 'not found'}, 404)
            rel = urllib.parse.parse_qs(u.query).get('path', [''])[0]
            target = self._safe_path(rel)
            if target is None or target.suffix.lower() not in (MD_EXTS | IMG_EXTS):
                return self._json({'error': '路徑不合法（只接受 .md 與圖片）'}, 400)
            n = int(self.headers.get('Content-Length') or 0)
            body = self.rfile.read(n)
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_suffix(target.suffix + '.tmp')
            tmp.write_bytes(body)
            os.replace(tmp, target)           # 先寫暫存檔再換名，避免寫到一半
            st = target.stat()
            return self._json({'ok': True, 'path': target.relative_to(root).as_posix(),
                               'mtime': int(st.st_mtime * 1000), 'size': st.st_size})

        def do_DELETE(self):
            u = urllib.parse.urlparse(self.path)
            if u.path != '/api/file':
                return self._json({'error': 'not found'}, 404)
            rel = urllib.parse.parse_qs(u.query).get('path', [''])[0]
            target = self._safe_path(rel)
            if target is None or target.suffix.lower() not in (MD_EXTS | IMG_EXTS):
                return self._json({'error': '路徑不合法（只接受 .md 與圖片）'}, 400)
            if not target.is_file():
                return self._json({'error': '檔案不存在'}, 404)
            target.unlink()
            return self._json({'ok': True, 'path': target.relative_to(root).as_posix()})

        def log_message(self, fmt, *args):
            first = args[0] if args else ''
            if isinstance(first, str) and '/api/modules' in first:
                return                        # 輪詢的請求不洗版
            # 注意：錯誤記錄（如 404）的第一個參數是 HTTPStatus 不是字串，不能拿來做子字串比對——
            # 0.x～1.1.5 這裡曾直接 `in args[0]`，404 時拋 TypeError，連回應都送不出去（1.1.6 修正）。
            sys.stderr.write('%s  %s\n' % (time.strftime('%H:%M:%S'), fmt % args))

    Handler.extensions_map.update({'.md': 'text/markdown; charset=utf-8', '.markdown': 'text/markdown; charset=utf-8',
                                   '.txt': 'text/plain; charset=utf-8', '.html': 'text/html; charset=utf-8',
                                   '.json': 'application/json; charset=utf-8'})
    return Handler


def main():
    ap = argparse.ArgumentParser(description='筆記模組本機伺服器')
    ap.add_argument('folder', nargs='?', default=str(HERE), help='筆記資料夾（預設：serve.py 所在資料夾）')
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--host', default='127.0.0.1', help='0.0.0.0 可讓區網裝置連線')
    ap.add_argument('--no-open', action='store_true', help='不要自動開瀏覽器')
    a = ap.parse_args()

    root = pathlib.Path(a.folder).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f'找不到資料夾：{root}')
    index = root / 'index.html'
    if not index.exists():
        index = HERE / 'index.html'
    if not index.exists():
        sys.exit('找不到 index.html（檢視器），請把它放在 serve.py 旁邊或筆記資料夾裡')

    srv = http.server.ThreadingHTTPServer((a.host, a.port), make_handler(root, index))
    url = f'http://{"localhost" if a.host in ("127.0.0.1", "0.0.0.0") else a.host}:{a.port}/'
    print(f'筆記資料夾：{root}\n檢視器：{url}   （Ctrl+C 結束）')
    if a.host == '0.0.0.0':
        print('提醒：區網內所有裝置都能讀寫這個資料夾，請只在信任的網路使用。')
    if not a.no_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\n已停止')


if __name__ == '__main__':
    main()
