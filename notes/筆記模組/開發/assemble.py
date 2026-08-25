#!/usr/bin/env python3
"""把 開發/src 裡的零件組成上一層的 index.html（單一檔案）。

    python3 開發/assemble.py

改了 src/style.css、src/app.js、src/body.html 之後跑一次即可。
"""
import pathlib
W = pathlib.Path(__file__).resolve().parent
src = W / 'src'
tpl = (src / 'template.html').read_text(encoding='utf-8')
css = (src / 'style.css').read_text(encoding='utf-8')
body = (src / 'body.html').read_text(encoding='utf-8')
marked = (W / 'marked.min.js').read_text(encoding='utf-8').strip()
katex_js = (W / 'katex.min.js').read_text(encoding='utf-8').strip()
app = (src / 'app.js').read_text(encoding='utf-8')

# KaTeX 的 CSS：字型改成內嵌的 data URI（只留 woff2），離線也能正確排版
import base64, re
katex_css = (W / 'katex.min.css').read_text(encoding='utf-8')
def font_uri(m):
    name = m.group(1)
    data = base64.b64encode((W / 'katex-fonts' / f'{name}.woff2').read_bytes()).decode('ascii')
    return f'url(data:font/woff2;base64,{data}) format("woff2")'
katex_css = re.sub(r'url\(fonts/([\w-]+)\.woff2\) format\("woff2"\),url\(fonts/[\w-]+\.woff\) format\("woff"\),url\(fonts/[\w-]+\.ttf\) format\("truetype"\)', font_uri, katex_css)
assert 'url(fonts/' not in katex_css, 'KaTeX 字型沒有全部內嵌'

scripts = ('<script>/* marked v18 — MIT License, https://github.com/markedjs/marked */\n' + marked + '\n</script>\n'
           '<script>/* KaTeX — MIT License, https://katex.org */\n' + katex_js + '\n</script>\n'
           '<script>\n' + app + '\n</script>')
out = tpl.replace('/* @@CSS@@ */', css + '\n/* ===== KaTeX（MIT） ===== */\n' + katex_css).replace('<!-- @@BODY@@ -->', body + '\n' + scripts)
assert '@@' not in out
dest = W.parent / 'index.html'
dest.write_text(out, encoding='utf-8')
print('已寫入', dest, f'{len(out.encode("utf-8")) / 1024:.0f} KB')
