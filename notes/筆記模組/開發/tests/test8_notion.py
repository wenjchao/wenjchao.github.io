#!/usr/bin/env python3
"""測試八：notion2modules.py 的轉換規則（規格書 D21：每個 toggle 一個模組，不論深度與大小）。

純 Python，不需要瀏覽器；需要 beautifulsoup4 與 lxml（轉換器本來就需要）。
用一個合成的 Notion 匯出頁面驗證：
  - 三層 toggle 都各自成為模組，資料夾照巢狀；父模組在原位置放 [[相對路徑|摘要]] 卡片
  - 清單項目裡、引言（粗體標題的 blockquote）裡的 toggle 也獨立成模組，卡片前有空行（不會黏成晶片）
  - 預設不自動補摘要（標題整個保留）；--split-title 才把「主題：重點」拆成 標題＝主題、摘要＝重點；標題尾端的冒號不進檔名與標題
  - 圖片路徑依模組深度加 ../；KaTeX → $…$；h3 後的散落段落 → 模組
  - overrides：names／titles 可用「資料夾/原標題開頭」只對某資料夾生效；summaries 以輸出路徑為 key
  - 所有 [[…]] 都能相對於所在檔案的資料夾找到目標檔案
"""
import json, os, pathlib, re, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SCRIPT = ROOT / 'notion2modules.py'

KATEX = ('<span class="katex"><span class="katex-mathml"><math><semantics><mrow><mi>E</mi></mrow>'
         '<annotation encoding="application/x-tex">E=mc^2</annotation></semantics></math></span>'
         '<span class="katex-html">E=mc2</span></span>')

def toggle(title, inner):
    return (f'<div style="display:contents"><ul class="toggle"><li><details open="">'
            f'<summary>{title}</summary>{inner}</details></li></ul></div>')

def img(src):
    return f'<div style="display:contents"><figure class="image"><a href="{src}"><img src="{src}"/></a></figure></div>'

def p(text):
    return f'<div style="display:contents"><p class="">{text}</p></div>'

HTML = f'''<html><body><article id="x" class="page sans"><header><h1 class="page-title">測試頁</h1></header>
<div class="page-body">
{p('頁面開頭的散落段落。')}
{img('%E6%B8%AC%E8%A9%A6%E9%A0%81/Untitled.png')}
{toggle('主題一：重點一', p('主題一的內文。') + img('%E6%B8%AC%E8%A9%A6%E9%A0%81/a%20b.png')
        + toggle('子題', p('子題內文。') + toggle('孫題目：重點三', p('孫題內文 ' + KATEX + '。') + img('%E6%B8%AC%E8%A9%A6%E9%A0%81/a%20b.png')))
        + p('子題後面的段落。')
        + '<div style="display:contents"><ol class="numbered-list" start="1"><li>第一項' + toggle('清單裡的', p('清單 toggle 內文。')) + '</li></ol></div>'
        + '<div style="display:contents"><ul class="bulleted-list"><li>甲</li></ul></div>'
        + toggle('清單中的', p('和清單項目平行。'))
        + '<div style="display:contents"><ul class="bulleted-list"><li>乙</li></ul></div>'
        + p('中間隔一段。')
        + toggle('編號前的', p('排在編號清單前面。'))
        + '<div style="display:contents"><ol class="numbered-list" start="1"><li>編號一</li></ol></div>'
        + '<div style="display:contents"><ol class="numbered-list" start="2"><li>編號二</li></ol></div>'
        + '<div style="display:contents"><blockquote class=""><strong>小節標題</strong>' + toggle('引言裡的', p('引言 toggle 內文。')) + '</blockquote></div>')}
{toggle('圖示：', img('%E6%B8%AC%E8%A9%A6%E9%A0%81/Untitled%201.png'))}
{toggle('圖示', p('另一個圖示。'))}
{toggle('備註：', p('標題尾端有冒號。'))}
<h3 class="">其他</h3>
{p('h3 後面的散落段落，會變成「其他」模組。')}
</div></article></body></html>'''

OVERRIDES = {
    'names': {'測試頁/圖示：': '第二個圖示'},
    'titles': {'測試頁/圖示：': '第二個圖示（標題）'},
    'summaries': {'測試頁/主題一/子題': '手寫的子題摘要'},
}


def read(out, rel):
    return (out / rel).read_text(encoding='utf-8')


def main():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        html = tmp / '測試頁.html'
        html.write_text(HTML, encoding='utf-8')
        ov = tmp / 'ov.json'
        ov.write_text(json.dumps(OVERRIDES, ensure_ascii=False), encoding='utf-8')
        out = tmp / 'out'
        # 預設：不自動補摘要——「主題一：重點一」整個當標題、沒有 ## 摘要（0.9，使用者要求）；overrides.summaries 照常生效
        out0 = tmp / 'out0'
        r = subprocess.run([sys.executable, str(SCRIPT), str(html), str(out0), '--overrides', str(ov), '--no-images'], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        whole = read(out0, '測試頁/主題一：重點一.md')
        assert whole.startswith('# 主題一：重點一\n\n## 內文\n'), whole
        assert '## 摘要' not in whole, whole
        assert '[[測試頁/主題一：重點一|摘要]]' in read(out0, '測試頁.md')
        assert read(out0, '測試頁/主題一：重點一/子題/孫題目：重點三.md').startswith('# 孫題目：重點三\n\n## 內文\n')
        assert read(out0, '測試頁/備註.md').startswith('# 備註\n\n## 內文\n'), '尾端冒號仍然不進檔名與標題'
        assert '沒有摘要的模組' in r.stdout

        # 下面用 --split-title（舊行為：「主題：重點」拆成標題＋摘要）驗其餘規則
        r = subprocess.run([sys.executable, str(SCRIPT), str(html), str(out), '--overrides', str(ov), '--no-images', '--split-title'],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        assert '--min-chars' not in r.stdout and '小節' not in r.stdout

        files = sorted(str(p.relative_to(out)) for p in out.rglob('*.md'))
        expect = ['測試頁.md', '測試頁/主題一.md', '測試頁/主題一/子題.md', '測試頁/主題一/子題/孫題目.md',
                  '測試頁/主題一/清單裡的.md', '測試頁/主題一/引言裡的.md', '測試頁/主題一/清單中的.md', '測試頁/主題一/編號前的.md',
                  '測試頁/第二個圖示.md', '測試頁/圖示.md', '測試頁/備註.md', '測試頁/其他.md']
        assert sorted(files) == sorted(expect), files

        hub = read(out, '測試頁.md')
        assert '[[測試頁/主題一|摘要]]' in hub and '[[測試頁/圖示|摘要]]' in hub and '[[測試頁/其他|摘要]]' in hub, hub
        assert '![](測試頁/圖片/Untitled.png)' in hub, hub                       # 總覽在頁名資料夾外面

        m1 = read(out, '測試頁/主題一.md')
        assert m1.startswith('# 主題一\n\n## 摘要\n重點一\n'), m1                   # 「主題：重點」拆成標題與摘要
        assert '![](圖片/a-b.png)' in m1, m1                                       # 第 1 層：圖片/
        assert '[[主題一/子題|摘要]]' in m1, m1
        assert re.search(r'1\. 第一項\n\n   \[\[主題一/清單裡的\|摘要\]\]', m1), m1   # 清單項目裡：空行＋縮排的卡片
        assert '- 甲\n- [[主題一/清單中的|扁平]]\n- 乙\n' in m1, m1                    # 和清單項目相鄰的 toggle → 同一個清單裡的扁平項目（D27）
        assert '1. [[主題一/編號前的|扁平]]\n2. 編號一\n3. 編號二' in m1, m1             # 排在編號清單前：從 1 起算，後面的號碼往後挪
        assert re.search(r'### 小節標題\n\n\[\[主題一/引言裡的\|摘要\]\]', m1), m1   # 粗體開頭的引言 → 小節，裡面的 toggle 成卡片

        sub = read(out, '測試頁/主題一/子題.md')
        assert '## 摘要\n手寫的子題摘要\n' in sub, sub                               # overrides.summaries
        assert '[[子題/孫題目|摘要]]' in sub, sub

        g = read(out, '測試頁/主題一/子題/孫題目.md')
        assert g.startswith('# 孫題目\n\n## 摘要\n重點三\n'), g
        assert '$E=mc^2$' in g, g                                                 # KaTeX → $…$
        assert '![](../../圖片/a-b.png)' in g, g                                   # 第 3 層：../../圖片/

        s2 = read(out, '測試頁/第二個圖示.md')
        assert s2.startswith('# 第二個圖示（標題）\n'), s2                           # 資料夾限定的 names／titles
        assert read(out, '測試頁/圖示.md').startswith('# 圖示\n'), '圖示 不該被「圖示：」的覆寫影響'
        assert read(out, '測試頁/備註.md').startswith('# 備註\n\n## 內文\n'), '尾端冒號不進檔名與標題'
        assert read(out, '測試頁/其他.md').startswith('# 其他\n'), 'h3 後的散落段落成為模組'

        # 每個 [[…]] 都找得到目標（相對於所在檔案的資料夾）
        n = 0
        for f in out.rglob('*.md'):
            for m in re.finditer(r'(?<!!)\[\[([^\[\]\n`]+?)\]\]', f.read_text(encoding='utf-8')):
                target = (f.parent / (m.group(1).split('|')[0] + '.md'))
                assert target.exists(), f'{f.relative_to(out)} → {m.group(1)}'
                n += 1
        assert n == 11, n
    print('TEST8 OK')


if __name__ == '__main__':
    main()
