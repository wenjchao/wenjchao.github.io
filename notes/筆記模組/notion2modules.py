#!/usr/bin/env python3
"""Notion HTML 匯出 → 筆記模組（# 標題 / ## 摘要 / ## 內文，[[子模組|摘要]]）。

    python3 notion2modules.py "CV new.html" ~/我的筆記
    python3 notion2modules.py "CV new.html" ~/我的筆記 --overrides cv.json

需要：python3 -m pip install beautifulsoup4 lxml

轉換規則（規格書 D21：每個 toggle 一個模組）：
  頁面本身        → <頁名>.md（總覽模組），內文是一排 [[<頁名>/<主題>|摘要]] 卡片
  每個 toggle     → 一個模組，不論深度、不論大小：<頁名>/<主題>.md、<頁名>/<主題>/<子題>.md、…
                    父模組在 toggle 原本的位置放 [[相對路徑|摘要]] 卡片（在清單項目或引言裡也一樣）
  h3 標題後的散落段落 → 以該標題為名的模組
  摘要一律留給你寫（或用 overrides.json 的 summaries 填）；程式不自己猜。加 --split-title 才會把「主題：重點」拆成標題＋摘要
  blockquote 開頭是粗體字 → 小節標題；callout → 💡 引言；表格 → Markdown 表格；KaTeX → $…$
  圖片 → 複製到 <頁名>/圖片/（乾淨檔名），Markdown 用相對路徑引用（../ 依模組深度）

overrides.json（選用）：
  {"summaries": {"<頁名>/<主題>/<子題>": "手寫摘要", ...},            ← key 是輸出的相對路徑（不含 .md）
   "names":     {"原標題開頭": "想要的檔名", "<資料夾>/原標題開頭": "只對這個資料夾生效", ...},
   "titles":    {"原標題開頭": "想要的模組標題", ...},                 ← 同 names 的 key 規則
   "fixes":     [["錯字", "正確"], ...]}                              ← 直接取代 HTML 裡的文字
"""
import sys, re, json, pathlib, urllib.parse, html as htmlmod
from bs4 import BeautifulSoup, NavigableString, Tag

FORBIDDEN = dict.fromkeys('/\\:*?"<>|[]#', '')
FORBIDDEN['/'] = '／'
SPLIT_RE = re.compile(r'^(.{3,60}?)\s*(?:：|:\s|⇒|→)\s*(.+)$')   # 「主題：重點」→ 標題 + 摘要
TRAILING_PUNCT = '：:，,、;；'                                       # 標題尾端的冒號等不進檔名與標題


# 行內層級標籤：blocks() 遇到時和相鄰文字併成同一段（callout 內文常是「文字＋<style>＋數學 token」直接混排）
INLINE_TAGS = {'span', 'a', 'strong', 'b', 'em', 'i', 'del', 's', 'code', 'mark', 'u',
               'sup', 'sub', 'kbd', 'br', 'img', 'style', 'script', 'math', 'annotation', 'svg'}


def clean_filename(title, limit=50):
    t = re.sub(r'\$([^$]*)\$', lambda m: re.sub(r'[\\{}^_]', '', m.group(1)), title)   # 數學式只留字母
    t = t.replace('\ufeff', '')
    t = ''.join(FORBIDDEN.get(c, c) for c in t)
    t = re.sub(r'[{}$^~`]', '', t)
    t = re.sub(r'\s+', ' ', t).strip(' .').rstrip(TRAILING_PUNCT).strip()
    t = t.replace('’', "'")
    if len(t) > limit:
        cut = t[:limit]
        m = re.search(r'^(.+)[\s,;，；、:：(（]', cut)
        t = (m.group(1) if m and len(m.group(1)) >= limit * 0.6 else cut).rstrip(' ,;，；、(（的之與和及')
        t = re.sub(r'\s*[(（][^)）]*$', '', t).rstrip(' ,;，；、')   # 截斷後留下沒關上的括號就整段去掉
    return t or '未命名'


def find_override(table, folder, title):
    """names／titles 的 key：「原標題開頭」；也可以寫「資料夾/原標題開頭」只對某個資料夾生效。"""
    for k, v in table.items():
        if ('/' in k and f'{folder}/{title}'.startswith(k)) or ('/' not in k and title.startswith(k)):
            return v
    return None


def split_title(title, split=False):
    """預設不拆：標題整個保留、摘要空白（使用者要求：不要自己補摘要，0.9）。
    split=True（--split-title）才把 'Aortic stenosis：V2 max, …' 拆成 ('Aortic stenosis', 'V2 max, …')；太短的左半邊不拆。"""
    t = re.sub(r'\s+', ' ', title).strip()
    m = SPLIT_RE.match(t) if split else None
    if m:
        left, right = m.group(1).strip(), m.group(2).strip()
        if len(left) >= 3 and not left.endswith(('問', '答')) and len(right) >= 2:
            return left, right
    return t.rstrip(TRAILING_PUNCT).strip(), ''


class Converter:
    def __init__(self, html_path, out_dir, overrides=None, page_name=None, split_title=False):
        raw = open(html_path, encoding='utf-8').read()
        ov = overrides or {}
        for a, b in ov.get('fixes', []):
            raw = raw.replace(a, b)
        self.soup = BeautifulSoup(raw, 'lxml')
        for s in self.soup.find_all(['style', 'script']):
            s.decompose()                            # 樣式表／腳本永遠不是內容（曾把 @import 倒進 callout 文字）
        self.page_title = page_name or self.soup.select_one('.page-title').get_text(' ', strip=True)
        self.out = pathlib.Path(out_dir)
        self.split = split_title                     # --split-title：「主題：重點」→ 標題＋摘要（預設關閉）
        self.summaries = ov.get('summaries', {})
        self.names = ov.get('names', {})
        self.titles = ov.get('titles', {})
        used = sorted({h.name for h in self.soup.select('.page-body h1, .page-body h2, .page-body h3')})
        self.hmap = {h: 3 + i for i, h in enumerate(used)}     # 頁面裡用到的最大標題 → ###，依序往下
        self.images = {}        # on-disk relative (decoded once) → clean name
        self.modules = {}       # rel path → text
        self.used_names = {}    # folder → set(names)
        self.warnings = []

    # ---------------- 檔名 ----------------
    def unique(self, folder, name):
        used = self.used_names.setdefault(folder, set())
        base, n = name, 2
        while name.lower() in used:
            name = f'{base} {n}'; n += 1
        used.add(name.lower())
        return name

    # ---------------- 圖片 ----------------
    def image_ref(self, src, from_folder_depth):
        """src 是匯出的相對路徑；回傳 markdown 用的相對路徑，並記錄要複製的檔案。"""
        if src.startswith('http'):
            return src
        ondisk = urllib.parse.unquote(src)             # 解一次 = 磁碟上的實際路徑（檔名可能仍含 %XX）
        folder, base = (ondisk.rsplit('/', 1) + [''])[:2] if '/' in ondisk else ('', ondisk)
        clean = re.sub(r'\s+', '-', urllib.parse.unquote(base))   # 再解一次 → 人看得懂的名字
        if folder and folder != self.page_title:       # 引用到別頁資料夾的圖：放進子資料夾避免撞名
            clean = re.sub(r'\s+', '-', urllib.parse.unquote(folder)) + '/' + clean
        self.images[ondisk] = clean
        # 圖片都放在 <頁名>/圖片/；總覽在頁名資料夾外面，第 1 層模組在裡面，更深一層就多一個 ../
        prefix = f'{self.page_title}/圖片/' if from_folder_depth == 0 else '../' * (from_folder_depth - 1) + '圖片/'
        return prefix + clean

    # ---------------- 行內 ----------------
    def inline(self, node, ctx):
        if isinstance(node, NavigableString):
            if node.parent and node.parent.name in ('pre', 'code'):
                return str(node)
            return re.sub(r'[ \t\r\n]+', ' ', str(node)).replace('*', '\\*')
        if not isinstance(node, Tag):
            return ''
        name = node.name
        cls = ' '.join(node.get('class', []))
        style = node.get('style') or ''
        if name in ('style', 'script', 'math', 'annotation'):
            return ''
        if name == 'br':
            return '\n'
        if name == 'span' and 'katex' in cls:
            ann = node.find('annotation')
            tex = ' '.join(ann.get_text().split()) if ann else node.get_text(' ', strip=True)   # 摺成單行：行內 $…$ 不得含換行（檢視器規格 §5）
            return f'${tex}$'
        if name == 'annotation' or (name == 'span' and 'katex' in ' '.join(node.parent.get('class', []))):
            return ''
        inner = ''.join(self.inline(c, ctx) for c in node.children)
        s = inner.strip()
        lead = ' ' if inner[:1].isspace() else ''
        trail = ' ' if inner[-1:].isspace() else ''
        def wrap(a, b=None):
            return f'{lead}{a}{s}{b if b is not None else a}{trail}' if s else (' ' if (lead or trail) else '')
        if name in ('strong', 'b'):
            return wrap('**')
        if name in ('em', 'i'):
            return wrap('*')
        if name in ('del', 's'):
            return wrap('~~')
        if name == 'code':
            return wrap('`')
        if name == 'mark':
            if cls.startswith('highlight-default') or not cls:
                return inner
            return wrap('<mark>', '</mark>')
        if name == 'a':
            href = node.get('href', '')
            if node.find('img'):
                return inner
            text = inner.strip() or href
            if href.endswith('.html') and not href.startswith('http'):
                return text                       # Notion 內部頁面連結：匯出裡沒有那一頁，只留文字
            return f'[{text}]({href})' if href else text
        if name == 'img':
            return f'![]({self.image_ref(node.get("src", ""), ctx["depth"])})'
        if name == 'span':
            if 'border-bottom' in style:
                return wrap('<u>', '</u>')
            return inner
        if name in ('sup', 'sub', 'u', 'kbd'):
            return f'<{name}>{inner}</{name}>'
        if name in ('figure', 'div', 'ul', 'ol', 'li', 'p', 'blockquote', 'details', 'table', 'h1', 'h2', 'h3'):
            return ''                             # 區塊由 blocks() 處理
        return inner

    def li_text_and_blocks(self, li, ctx):
        """li 的直接文字／行內 → 文字；巢狀區塊（div/ul/ol/…）→ 之後縮排輸出。"""
        text_parts, blocks = [], []
        for c in li.children:
            if isinstance(c, Tag) and (c.name in ('div', 'ul', 'ol', 'figure', 'blockquote', 'details', 'table', 'p') or 'display:contents' in (c.get('style') or '')):
                blocks.append(c)
            else:
                text_parts.append(self.inline(c, ctx))
        text = re.sub(r'[ \t]+', ' ', ''.join(text_parts)).strip()
        return text, blocks

    # ---------------- 區塊 ----------------
    def blocks(self, container, ctx, indent=''):
        """回傳 markdown 行的 list。ctx: depth(模組層級 0/1/2), folder, section_level, allow_modules"""
        out = []
        last = None
        fam = lambda k: 'ul' if k in ('ul', 'todo') else k   # 項目清單與核取清單同一家，可以接在一起
        def push(lines, kind):
            nonlocal last
            if out and fam(kind) != fam(last):
                if out[-1] != '':
                    out.append('')
            elif out and kind == last and kind not in ('ol', 'ul', 'todo') and out[-1] != '':
                out.append('')
            out.extend(lines); last = kind
        flat = self.flat_children(container)   # 先拆掉 Notion 的透明包裝 div，才看得到誰和誰相鄰
        skip_until, shift = 0, 0   # shift：toggle 串變成編號清單前幾項之後，接下來的編號要往後挪
        for i, el in enumerate(flat):
            if i < skip_until:
                continue
            if shift and self.list_kind(el) != 'ol':
                shift = 0
            if isinstance(el, NavigableString) or el.name in INLINE_TAGS:
                j = i                                 # 行內節點聚成同一段：文字與數學 token 不再被拆成各自的區塊
                while j < len(flat) and (isinstance(flat[j], NavigableString) or (isinstance(flat[j], Tag) and flat[j].name in INLINE_TAGS)):
                    j += 1
                t = re.sub(r'[ \t]+', ' ', ''.join(self.inline(c, ctx) for c in flat[i:j])).strip()
                if t:
                    push([indent + t], 'p')
                skip_until = j
                continue
            if not isinstance(el, Tag):
                continue
            name, cls, style = el.name, ' '.join(el.get('class', [])), el.get('style') or ''
            if name == 'div' and ('display:contents' in style or 'indented' in cls or 'column' in cls or not cls):
                sub = self.blocks(el, ctx, indent)
                if sub:
                    push(sub, 'group'); last = None
                continue
            if name == 'p':
                t = self.inline_block(el, ctx)
                if t.strip():
                    push([indent + line for line in t.split('\n')], 'p')
                continue
            if name in ('h1', 'h2', 'h3'):
                level = ctx['section_level'] - 3 + self.hmap.get(name, 3)
                level = max(3, min(level, 6))
                t = self.inline_block(el, ctx).strip().lstrip('—– ').strip()
                push([indent + '#' * level + ' ' + t], 'h')
                continue
            if self.is_toggle(el):
                e = i   # 連續幾個 toggle 當成一串一起看：前後鄰居是清單項目 → 整串變成同一個清單裡的扁平項目（D27）
                while e + 1 < len(flat) and self.is_toggle(flat[e + 1]):
                    e += 1
                dets = [d for k in range(i, e + 1) for d in self.toggle_details(flat[k])]
                nb = self.list_neighbor(flat, i, e, len(dets))
                if nb and nb[0] == 'ol' and self.list_kind(flat[i - 1] if i else None) != 'ol':
                    nb = ('ol', 1 + shift); shift += len(dets)   # 前面沒有編號清單：從 1 起算，後面的清單往後挪
                elif nb and nb[0] == 'ol':
                    nb = ('ol', nb[1] + shift); shift += len(dets)
                for det in dets:
                    if nb:
                        kind, num = nb
                        line = self.toggle(det, ctx, indent, flat=True)[0].strip()
                        push([indent + (f'{num}. ' if kind == 'ol' else '- ') + line], kind)
                        if kind == 'ol':
                            nb = (kind, num + 1)
                    else:
                        push(self.toggle(det, ctx, indent), 'toggle')
                skip_until = e + 1
                continue
            if name == 'ul' and 'to-do-list' in cls:
                for li in el.find_all('li', recursive=False):
                    checked = bool(li.select_one('.checkbox-on'))
                    text, subs = self.li_text_and_blocks(li, ctx)
                    lines = [indent + ('- [x] ' if checked else '- [ ] ') + text]
                    for s in subs:
                        lines += self.blocks(s, ctx, indent + '  ')
                    push(lines, 'todo')
                continue
            if name in ('ul', 'ol'):
                ordered = name == 'ol'
                start = int(el.get('start', 1) or 1) + (shift if ordered else 0)
                lines = []
                for i, li in enumerate(el.find_all('li', recursive=False)):
                    text, subs = self.li_text_and_blocks(li, ctx)
                    marker = f'{start + i}. ' if ordered else '- '
                    pad = ' ' * len(marker)
                    text_lines = text.split('\n') if text else ['']
                    lines.append(indent + marker + text_lines[0])
                    for extra in text_lines[1:]:
                        lines.append(indent + pad + extra)
                    for s in subs:
                        sub_lines = self.blocks(s, dict(ctx, inline_sections=True), indent + pad)
                        if sub_lines:
                            if sub_lines[0].strip().startswith('[[') and lines and lines[-1] != '':
                                lines.append('')                 # 項目裡的 toggle 卡片要自成一段，否則會黏進上一行變成晶片
                            lines += sub_lines
                    if not text and not subs:
                        lines.pop()                      # 空的項目不輸出
                push(lines, 'ol' if ordered else 'ul')
                continue
            if name == 'blockquote':
                push(self.blockquote(el, ctx, indent), 'bq')
                continue
            if name == 'figure' and 'image' in cls:
                img = el.find('img')
                cap = el.find('figcaption')
                captxt = self.inline_block(cap, ctx).strip() if cap else ''
                if img:
                    push([indent + f'![{captxt}]({self.image_ref(img.get("src", ""), ctx["depth"])})'], 'img')
                continue
            if name == 'figure' and 'callout' in cls:
                icon = el.select_one('.icon')
                icon_t = icon.get_text(strip=True) if icon else '💡'
                body = el.find_all('div', recursive=False)[-1] if el.find_all('div', recursive=False) else el
                inner = self.blocks(body, ctx, '')
                if not inner:
                    inner = [self.inline_block(body, ctx)]
                first = True
                lines = []
                for ln in inner:
                    if first:
                        lines.append(indent + f'> {icon_t} ' + ln.lstrip()); first = False
                    else:
                        lines.append(indent + '> ' + ln)
                push(lines, 'callout')
                continue
            if name == 'figure' and ('bookmark' in cls or el.find('a', class_='bookmark')):
                a = el.find('a')
                title = el.select_one('.bookmark-title')
                t = title.get_text(' ', strip=True) if title else (a.get('href') if a else '')
                if a:
                    push([indent + f'[{t}]({a.get("href")})'], 'p')
                continue
            if name == 'figure' and 'equation' in cls:
                ann = el.find('annotation')
                push([indent + '$$', indent + (ann.get_text().strip() if ann else el.get_text(' ', strip=True)), indent + '$$'], 'eq')
                continue
            if name == 'figure':
                sub = self.blocks(el, ctx, indent)
                if sub:
                    push(sub, 'group'); last = None
                continue
            if name == 'table':
                push(self.table(el, ctx, indent), 'table')
                continue
            if name == 'hr':
                push([indent + '---'], 'hr')
                continue
            if name == 'pre':
                code = el.get_text()
                push([indent + '```'] + [indent + l for l in code.rstrip('\n').split('\n')] + [indent + '```'], 'code')
                continue
            if name == 'a':
                push([indent + self.inline(el, ctx)], 'p')
                continue
            # 其他：當作透明容器
            sub = self.blocks(el, ctx, indent)
            if sub:
                push(sub, 'group'); last = None
            elif el.get_text(strip=True):
                push([indent + self.inline_block(el, ctx)], 'p')
        # 去掉開頭結尾空行
        while out and out[0] == '': out.pop(0)
        while out and out[-1] == '': out.pop()
        return out

    def inline_block(self, el, ctx):
        return ''.join(self.inline(c, ctx) for c in el.children).strip()

    def flat_children(self, container):
        """Notion 把每個區塊包在 display:contents 的 div 裡；拆掉它們，回傳真正的區塊序列。"""
        out = []
        for el in container.children:
            if isinstance(el, NavigableString):
                if str(el).strip():
                    out.append(el)
                continue
            if not isinstance(el, Tag):
                continue
            cls = ' '.join(el.get('class', [])); style = el.get('style') or ''
            if el.name == 'div' and ('display:contents' in style or 'indented' in cls or 'column' in cls or not cls):
                out.extend(self.flat_children(el))
            else:
                out.append(el)
        return out

    @staticmethod
    def list_kind(el):
        if not isinstance(el, Tag):
            return None
        cls = ' '.join(el.get('class', []))
        if el.name == 'ol' and 'numbered-list' in cls:
            return 'ol'
        if el.name == 'ul' and ('bulleted-list' in cls or 'to-do-list' in cls):
            return 'ul'
        return None

    @staticmethod
    def is_toggle(el):
        return isinstance(el, Tag) and ((el.name == 'ul' and 'toggle' in ' '.join(el.get('class', []))) or el.name == 'details')

    @staticmethod
    def toggle_details(el):
        if el.name == 'details':
            return [el]
        return [d for d in (li.find('details', recursive=False) for li in el.find_all('li', recursive=False)) if d is not None]

    def list_neighbor(self, flat, i, e, n):
        """flat[i..e] 是一串 toggle（共 n 個）：前一個或後一個區塊是清單時回傳 ('ul'|'ol', 第一個的編號)，否則 None。"""
        prev = flat[i - 1] if i > 0 else None
        nxt = flat[e + 1] if e + 1 < len(flat) else None
        kp, kn = self.list_kind(prev), self.list_kind(nxt)
        if kp == 'ol':
            return ('ol', int(prev.get('start') or 1) + len(prev.find_all('li', recursive=False)))
        if kp == 'ul':
            return ('ul', None)
        if kn == 'ol':
            return ('ol', max(1, int(nxt.get('start') or 1) - n))
        if kn == 'ul':
            return ('ul', None)
        return None

    def blockquote(self, el, ctx, indent):
        """Notion 裡常把 blockquote 當「小節容器」：第一個是粗體/底線標題 → 轉成 ### 小標；否則當引言。"""
        kids = [k for k in el.children if not (isinstance(k, NavigableString) and not str(k).strip())]
        title = None
        if kids and isinstance(kids[0], Tag) and kids[0].name in ('strong', 'b', 'span', 'mark', 'u'):
            t = self.inline(kids[0], ctx).strip().strip('*').strip()
            t = re.sub(r'</?u>', '', t)
            rest_inline = ''.join(self.inline(k, ctx) for k in kids[1:] if not (isinstance(k, Tag) and k.name in ('div', 'ul', 'ol', 'figure', 'blockquote', 'details', 'table', 'p'))).strip()
            if t and len(t) <= 40 and len(rest_inline) <= 120:
                title = t
        if title:
            level = max(3, min(ctx['section_level'], 6))
            lines = [indent + '#' * level + ' ' + title, '']
            lead = rest_inline.lstrip('：: ').strip()
            if lead:
                lines += [indent + lead, '']
            rest = Tag(name='div')
            for k in kids[1:]:
                if isinstance(k, Tag) and k.name in ('div', 'ul', 'ol', 'figure', 'blockquote', 'details', 'table', 'p'):
                    rest.append(k.__copy__())
            lines += self.blocks(rest, dict(ctx, section_level=level + 1), indent)
            return lines
        # 引言二用法（R72、D46）：單行＝小節標題 → ###；多行＝完整內容 → 獨立子模組（原位 [[…|全文]]）
        isblock = lambda k: isinstance(k, Tag) and (k.name in ('div', 'ul', 'ol', 'figure', 'blockquote', 'details', 'table', 'p') or 'display:contents' in (k.get('style') or ''))
        plain = lambda s: re.sub(r'\*\*|</?u>|</?mark>', '', s).replace('﻿', '').strip()
        mlen = lambda s: len(re.sub(r'\$[^$\n]*\$', '□□', plain(s)))   # 標題長度：數學式折算兩字
        lead_kids = []
        for k in kids:
            if isblock(k):
                break
            lead_kids.append(k)
        lead = ''.join(self.inline(k, ctx) for k in lead_kids).strip()
        if not any(isblock(k) for k in kids):
            if not indent and lead:                       # 頂層單行 → 小節標題；清單內單行＝說明句，保留原樣
                level = max(3, min(ctx['section_level'], 6))
                return [indent + '#' * level + ' ' + lead, '']
        else:
            title_raw, consumed = None, 0
            if kids and isinstance(kids[0], Tag) and kids[0].name in ('strong', 'b', 'u', 'mark'):
                t = plain(self.inline(kids[0], ctx))
                if t and mlen(t) <= 40:
                    title_raw, consumed = t, 1
            if title_raw is None and lead and mlen(lead) <= 40:
                title_raw, consumed = lead, len(lead_kids)
            if title_raw:
                title_plain = plain(title_raw)
                folder = ctx['folder']
                norm = title_plain.replace('\\*', '*')
                override = find_override(self.names, folder, norm)
                title_override = find_override(self.titles, folder, norm)
                fname = self.unique(folder, override or clean_filename(title_plain))
                rest_kids = list(kids[consumed:])
                if consumed == 1 and rest_kids and isinstance(rest_kids[0], NavigableString):
                    rest_kids[0] = NavigableString(str(rest_kids[0]).lstrip('：: '))   # 粗體標題後的冒號不進內文
                content = Tag(name='div')
                for k in rest_kids:
                    content.append(k.__copy__() if isinstance(k, Tag) else NavigableString(str(k)))
                sub_folder = f'{folder}/{fname}'
                sub_ctx = dict(depth=ctx['depth'] + 1, folder=sub_folder, section_level=3, path=f'{sub_folder}.md')
                body_lines = self.blocks(content, sub_ctx, '')
                title = (title_override or re.sub(r'[：:]\s*$', '', title_raw)).replace('\\*', '*').replace('﻿', '')
                self.modules[f'{sub_folder}.md'] = self.module_text(title, self.summaries.get(sub_folder, ''), body_lines)
                link = f'{pathlib.Path(folder).name}/{fname}'
                return [indent + f'[[{link}|全文]]']
            self.warnings.append(f'引言未拆（取不出標題）：{ctx.get("path", "?")} ← 「{(plain(lead)[:24] or "（以區塊開頭）")}…」')
        inner = self.blocks(el, dict(ctx, inline_sections=True), '')
        if not inner:
            inner = [self.inline_block(el, ctx)]
        return [indent + '> ' + ln for ln in inner]

    def table(self, el, ctx, indent):
        rows = []
        for tr in el.find_all('tr'):
            cells = [re.sub(r'\s*\n\s*', '<br>', self.inline_block(td, ctx)).replace('|', '\\|') for td in tr.find_all(['td', 'th'])]
            rows.append(cells)
        if not rows:
            return []
        width = max(len(r) for r in rows)
        rows = [r + [''] * (width - len(r)) for r in rows]
        lines = [indent + '| ' + ' | '.join(rows[0]) + ' |', indent + '|' + '---|' * width]
        for r in rows[1:]:
            lines.append(indent + '| ' + ' | '.join(r) + ' |')
        return lines

    # ---------------- toggle → 模組（D21：每個 toggle 一個模組，不論深度與大小） ----------------
    def toggle(self, det, ctx, indent, flat=False):
        summ = det.find('summary', recursive=False) or det.find('summary')
        title_raw = self.inline_block(summ, ctx) if summ else '（無標題）'
        title_plain = re.sub(r'\*\*|</?u>|<mark>|</mark>', '', title_raw).strip()
        content = Tag(name='div')                     # toggle 的內容 = summary 以外的所有子節點
        for k in list(det.children):
            if isinstance(k, Tag) and k.name == 'summary': continue
            content.append(k.__copy__() if isinstance(k, Tag) else NavigableString(str(k)))
        short, rest = split_title(title_plain, self.split)
        folder = ctx['folder']                        # 目前模組自己的資料夾（子模組都放這裡面）
        norm = title_plain.replace('\\*', '*')
        override = find_override(self.names, folder, norm)
        title_override = find_override(self.titles, folder, norm)
        fname = self.unique(folder, override or clean_filename(short))
        sub_folder = f'{folder}/{fname}'
        sub_ctx = dict(depth=ctx['depth'] + 1, folder=sub_folder, section_level=3, path=f'{sub_folder}.md')
        body_lines = self.blocks(content, sub_ctx, '')
        summary = self.summaries.get(sub_folder) or rest
        title = (title_override or short).replace('\\*', '*')
        self.modules[f'{sub_folder}.md'] = self.module_text(title, summary, body_lines)
        # 連結相對於「目前模組所在的資料夾」：總覽在 <頁名>/ 外面 → 頁名/子題；<頁名>/A.md → A/子題；<頁名>/A/B.md → B/子題
        link = f'{pathlib.Path(folder).name}/{fname}'
        return [indent + (f'[[{link}|扁平]]' if flat else f'[[{link}|摘要]]')]   # 扁平：和清單項目平行、預設收合（像 Notion toggle）

    def module_text(self, title, summary, body_lines):
        body = '\n'.join(body_lines).strip('\n')
        body = body.replace('\ufeff', '').replace('****', '')
        body = re.sub(r'[ \t]+\n', '\n', body)
        body = re.sub(r'\n{3,}', '\n\n', body)
        parts = [f'# {title.strip()}', '']
        if summary:
            parts += ['## 摘要', summary.strip(), '']
        parts += ['## 內文', body, '']
        return '\n'.join(parts)

    # ---------------- 整頁 ----------------
    def run(self):
        body = self.soup.select_one('.page-body')
        page = self.page_title
        hub_ctx = dict(depth=0, folder=page, section_level=3, path=f'{page}.md')
        # 把最上層拆成：toggle（→模組卡片）／h3 區段（→模組，收納其後的散落內容）／其他散落內容（留在 hub）
        top = self.flatten_top(body)
        hub_lines, section = [], None   # section = (title, [elements])
        def flush_section():
            nonlocal section
            if not section: return
            title, els = section
            holder = Tag(name='div')
            for e in els: holder.append(e)
            short, rest = split_title(title, self.split)
            override = find_override(self.names, page, title)
            title_override = find_override(self.titles, page, title)
            fname = self.unique(page, override or clean_filename(short))
            sub_ctx = dict(depth=1, folder=f'{page}/{fname}', section_level=3, path=f'{page}/{fname}.md')
            lines = self.blocks(holder, sub_ctx, '')
            key = f'{page}/{fname}'
            self.modules[f'{page}/{fname}.md'] = self.module_text(title_override or short, self.summaries.get(key) or rest, lines)
            hub_lines.append(f'[[{page}/{fname}|摘要]]'); hub_lines.append('')
            section = None
        for el in top:
            if el.name in ('h1', 'h2', 'h3'):
                flush_section()
                t = self.inline_block(el, hub_ctx).strip().lstrip('—– ').strip()
                section = (t, [])
            elif el.name == 'details':
                if section and not section[1]:
                    # 標題後面直接接 toggle：標題只當分組，不成模組
                    hub_lines.append('### ' + section[0]); hub_lines.append(''); section = None
                if section:
                    section[1].append(el)
                else:
                    hub_lines += self.toggle(el, hub_ctx, ''); hub_lines.append('')
            else:
                if section:
                    section[1].append(el)
                else:
                    lines = self.blocks(Tag(name='div'), hub_ctx) if False else self.blocks(self.wrap(el), hub_ctx, '')
                    if lines:
                        hub_lines += lines; hub_lines.append('')
        flush_section()
        self.modules[f'{page}.md'] = self.module_text(page, self.summaries.get(page, ''), hub_lines)
        return self

    def wrap(self, el):
        holder = Tag(name='div'); holder.append(el); return holder

    def flatten_top(self, body):
        """展開最上層的透明 div，得到真正的區塊清單（details、h3、p、ul…）。"""
        out = []
        def walk(c):
            for el in c.children:
                if not isinstance(el, Tag): continue
                cls = ' '.join(el.get('class', [])); style = el.get('style') or ''
                if el.name == 'div' and ('display:contents' in style or not cls or 'column' in cls):
                    walk(el)
                elif el.name == 'ul' and 'toggle' in cls:
                    for li in el.find_all('li', recursive=False):
                        det = li.find('details', recursive=False)
                        if det: out.append(det)
                else:
                    out.append(el)
        walk(body)
        return out

    def write(self):
        for rel, text in self.modules.items():
            p = self.out / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding='utf-8')
        return self


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('html', help='Notion 匯出的 .html')
    ap.add_argument('out', help='輸出到哪個資料夾（通常是你的筆記資料夾）')
    ap.add_argument('--overrides', help='摘要／檔名／標題的覆寫 JSON')
    ap.add_argument('--name', help='頁名（預設用 HTML 裡的標題）')
    ap.add_argument('--no-images', action='store_true', help='不複製圖片')
    ap.add_argument('--split-title', action='store_true', help='把「主題：重點」形式的標題拆成 標題＋摘要（預設不拆、不自動補摘要）')
    a = ap.parse_args()
    ov = json.load(open(a.overrides, encoding='utf-8')) if a.overrides else {}
    c = Converter(a.html, a.out, ov, a.name, split_title=a.split_title).run().write()
    print(f'{c.page_title}：{len(c.modules)} 個模組')
    for rel in c.modules: print('   ', rel)
    # 圖片：從 HTML 旁邊的匯出資料夾複製到 <頁名>/圖片/
    if not a.no_images and c.images:
        import shutil
        src_root = pathlib.Path(a.html).resolve().parent
        dest_root = pathlib.Path(a.out) / c.page_title / '圖片'
        copied, missing = 0, []
        for ondisk, clean in c.images.items():
            src = src_root / ondisk
            dst = dest_root / clean
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                if not dst.exists(): shutil.copy2(src, dst)
                copied += 1
            else:
                missing.append(ondisk)
        print(f'圖片：複製 {copied} 張到 {dest_root}' + (f'；找不到 {len(missing)} 張：' if missing else ''))
        for m in missing: print('    ', m, '（匯出時沒有一起帶出來，或在別的頁面資料夾；補進 圖片/ 對應位置即可）')
    nosum = [rel for rel, text in c.modules.items() if '## 摘要' not in text]
    if nosum:
        print(f'沒有摘要的模組（{len(nosum)}）——原樣搬運，不必補。')
    for w in c.warnings:
        print('警告：' + w)
