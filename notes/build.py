#!/usr/bin/env python3
"""
筆記模組 — 打包工具（只用 Python 標準函式庫）

單一檔案（丟到 iPad、寄給別人、離線看）：
    python3 build.py                       # 把這個資料夾的 .md 全部包進 筆記模組-單檔.html
    python3 build.py ~/我的筆記 -o 我的筆記.html
    python3 build.py --no-images           # 不內嵌圖片（檔案比較小）

GitHub Pages／任何靜態網站（檢視器靠 modules.json 知道有哪些檔案）：
    python3 build.py --manifest            # 產生 modules.json；在 git 倉庫裡會自動填入 GitHub 資訊，
                                           # 頁面上就會出現「在 GitHub 編輯」
    python3 build.py --manifest --inline   # 把每個模組的內容也放進 modules.json（只需一次請求，網站載入快很多）
    python3 build.py --manifest --github 帳號/倉庫 --branch main
"""
import argparse, base64, html, json, mimetypes, os, pathlib, re, subprocess, sys, time

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


def git(root, *args):
    try:
        return subprocess.run(['git', *args], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return ''


def detect_github(root: pathlib.Path):
    url = git(root, 'config', '--get', 'remote.origin.url')
    m = re.search(r'github\.com[:/]([^/]+)/([^/\s]+?)(?:\.git)?$', url)
    if not m:
        return None
    branch = git(root, 'rev-parse', '--abbrev-ref', 'HEAD') or 'main'
    top = git(root, 'rev-parse', '--show-toplevel')
    sub = ''
    if top:
        try:
            sub = root.resolve().relative_to(pathlib.Path(top).resolve()).as_posix()
        except ValueError:
            sub = ''
    return {'owner': m.group(1), 'repo': m.group(2), 'branch': branch, 'dir': '' if sub in ('', '.') else sub}


def build_manifest(root, a):
    modules = []
    for p, rel in iter_files(root, MD_EXTS):
        st = p.stat()
        item = {'path': rel, 'mtime': int(st.st_mtime * 1000), 'size': st.st_size}
        if a.inline:
            item['text'] = p.read_text(encoding='utf-8')
        modules.append(item)
    gh = None
    if a.github:
        owner, _, repo = a.github.partition('/')
        gh = {'owner': owner, 'repo': repo, 'branch': a.branch or 'main', 'dir': a.dir or ''}
    else:
        gh = detect_github(root)
        if gh and a.branch:
            gh['branch'] = a.branch
    out = {'generated': int(time.time() * 1000), 'modules': modules}
    if gh:
        out['github'] = gh
    dest = root / 'modules.json'
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'已寫入 {dest}（{len(modules)} 個模組' + (f'，GitHub：{gh["owner"]}/{gh["repo"]}@{gh["branch"]}' if gh else '') + '）')


def build_single(root, a):
    template = pathlib.Path(a.template) if a.template else (root / 'index.html' if (root / 'index.html').exists() else HERE / 'index.html')
    if not template.exists():
        sys.exit('找不到 index.html（檢視器樣板），請用 --template 指定')
    page = template.read_text(encoding='utf-8')
    if '<!-- @modules -->' not in page:
        sys.exit('這個 index.html 沒有 <!-- @modules --> 標記，無法打包')
    blocks, n_img, skipped = [], 0, []
    label = html.escape(root.name)
    for p, rel in iter_files(root, MD_EXTS):
        if p.resolve() == template.resolve():
            continue
        data = base64.b64encode(p.read_bytes()).decode('ascii')
        blocks.append(f'<script type="text/x-module" data-path="{html.escape(rel)}" data-mtime="{int(p.stat().st_mtime * 1000)}" data-set="{label}" data-enc="base64">{data}</script>')
    if not a.no_images:
        limit = int(a.max_image_mb * 1024 * 1024)
        for p, rel in iter_files(root, IMG_EXTS):
            if p.stat().st_size > limit:
                skipped.append(rel)
                continue
            mime = mimetypes.guess_type(p.name)[0] or 'application/octet-stream'
            data = base64.b64encode(p.read_bytes()).decode('ascii')
            blocks.append(f'<script type="text/x-asset" data-path="{html.escape(rel)}" data-type="{mime}">{data}</script>')
            n_img += 1
    out = page.replace('<!-- @modules -->', '<!-- @modules -->\n' + '\n'.join(blocks) + '\n')
    title = html.escape(a.title or root.name)
    out = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', out, count=1)
    dest = pathlib.Path(a.output) if a.output else root / '筆記模組-單檔.html'
    dest.write_text(out, encoding='utf-8')
    print(f'已寫入 {dest}（{len(blocks) - n_img} 個模組、{n_img} 張圖片、{dest.stat().st_size / 1024:.0f} KB）')
    if skipped:
        print('太大而略過的圖片：' + '、'.join(skipped) + f'（可用 --max-image-mb 調高上限）')


def main():
    ap = argparse.ArgumentParser(description='筆記模組打包工具')
    ap.add_argument('folder', nargs='?', default=str(HERE), help='筆記資料夾（預設：build.py 所在資料夾）')
    ap.add_argument('-o', '--output', help='輸出檔名（單檔模式）')
    ap.add_argument('--title', help='單檔的頁面標題（預設：資料夾名）')
    ap.add_argument('--template', help='檢視器 index.html 的位置')
    ap.add_argument('--no-images', action='store_true', help='不內嵌圖片')
    ap.add_argument('--max-image-mb', type=float, default=5, help='單張圖片內嵌上限（MB）')
    ap.add_argument('--manifest', action='store_true', help='只產生 modules.json（靜態網站用）')
    ap.add_argument('--inline', action='store_true', help='modules.json 內含每個模組的內容（配合 --manifest）')
    ap.add_argument('--github', help='GitHub 倉庫，例如 wenj/notes（產生「在 GitHub 編輯」連結）')
    ap.add_argument('--branch', help='GitHub 分支（預設 main 或自動偵測）')
    ap.add_argument('--dir', help='筆記在倉庫中的子資料夾（預設自動偵測）')
    a = ap.parse_args()
    root = pathlib.Path(a.folder).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f'找不到資料夾：{root}')
    if a.manifest:
        build_manifest(root, a)
    else:
        build_single(root, a)


if __name__ == '__main__':
    main()
