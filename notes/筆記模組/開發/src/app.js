'use strict';
/* =====================================================================
   筆記模組 viewer
   結構：CONFIG（設定）→ Util → Parse（切 .md）→ Refs（[[連結]]）→ Store（索引）
         → MD（Markdown 渲染）→ Cards（卡片／晶片）→ Sources（讀寫來源）
         → Editor → App
   想改行為，多半只要改 CONFIG。
   ===================================================================== */

const CONFIG = {
  appName: '筆記模組',
  // 切法：'headings' = 「# 標題 / ## 摘要 / ## 內文」；'separator' = 標題後第一條 --- 之前是摘要
  format: 'headings',
  summaryHeadings: ['摘要', 'summary', '簡介', 'abstract'],
  bodyHeadings: ['內文', '正文', '內容', 'body', 'content'],
  // [[模組|模式]] 可用的模式別名
  modeAliases: { '1': 1, '標題': 1, 'title': 1, 't': 1,
                 '2': 2, '摘要': 2, 'summary': 2, 's': 2,
                 '3': 3, '全文': 3, '內文': 3, 'full': 3, 'body': 3, 'f': 3, 'all': 3 },
  // [[模組|扁平]] 的外觀別名：card 卡片（預設，有框）、flat 扁平（和清單項目平行）、group 群組縮排（無框，內容縮排在標題底下）
  styleAliases: { '卡片': 'card', 'card': 'card', '扁平': 'flat', 'flat': 'flat', '平': 'flat', '群組縮排': 'group', '群組': 'group', '縮排': 'group', 'group': 'group' },
  defaultMode: 1,          // [[模組]] 沒寫模式時
  inlineExpandMode: 2,     // 段落中的晶片按 ▾ 展開時至少顯示到
  maxDepth: 10,            // 巢狀深度上限（防止無限展開）
  home: ['首頁', 'index', 'README', 'readme', '使用說明'],   // 沒有指定模組時優先顯示
  pollMs: 2000,            // 資料夾／本機伺服器：檢查檔案變動的間隔
  staticPollMs: 60000,     // 靜態網站（GitHub Pages）：檢查間隔
  markdown: { gfm: true, breaks: true },   // breaks: 單一換行就換行（筆記比較直覺）
  math: true,              // $…$、$$…$$、\(…\)、\[…\] 用 KaTeX 渲染（false 就維持純文字）
  newModuleTemplate: name => `# ${name}\n\n## 摘要\n\n\n\n## 內文\n\n`,
  mdExts: ['md', 'markdown', 'txt'],
  imageExts: ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'avif', 'bmp'],
  imageFolder: '圖片',     // 在編輯器貼上／拖入的圖片，存到模組旁邊的這個資料夾
  // 外觀樣式：ink 墨線、card 便條、outline 大綱、sketch 手帳、tab 標籤
  defaultStyle: 'ink',
  styles: { ink: '墨線', card: '便條', outline: '大綱', sketch: '手帳', tab: '標籤' },
  showStylePicker: true,   // false 可把右上角的樣式選單藏起來（鎖定 defaultStyle）
  editorDefault: 'wysiwyg',   // 第一次進編輯器用哪種模式：'wysiwyg' 直觀編輯、'source' 原始碼（之後記住上次用的）
  rememberCards: true,        // 記住每一頁卡片的展開／收合狀態（R22）；false 就每次都照連結的預設
};

/* ===================== Util ===================== */
const Util = {
  esc: s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])),
  norm: s => String(s).normalize('NFC'),
  ext: p => (p.split('.').pop() || '').toLowerCase(),
  isMd: p => CONFIG.mdExts.includes(Util.ext(p)),
  isImage: p => CONFIG.imageExts.includes(Util.ext(p)),
  pathToId: p => Util.norm(p).replace(/\\/g, '/').replace(/^\.?\//, '').replace(/\.(md|markdown|txt)$/i, ''),
  basename: p => p.split('/').pop(),
  dirname: p => p.includes('/') ? p.slice(0, p.lastIndexOf('/')) : '',
  join(dir, rel) {
    if (rel.startsWith('/')) return rel.slice(1);
    const parts = dir ? dir.split('/') : [];
    for (const seg of rel.split('/')) { if (seg === '..') parts.pop(); else if (seg && seg !== '.') parts.push(seg); }
    return parts.join('/');
  },
  /* 從 fromDir 走到 toPath 的相對路徑（搬移模組時改寫圖片與 .md 連結用）：'a/b' → 'a/c/x' 得 'c/x'；'a/b' → 'd/x' 得 '../../d/x' */
  relPath(fromDir, toPath) {
    const a = fromDir ? fromDir.split('/') : [], b = toPath.split('/');
    let i = 0; while (i < a.length && i < b.length - 1 && a[i] === b[i]) i++;
    return '../'.repeat(a.length - i) + b.slice(i).join('/');
  },
  encodePath: p => p.split('/').map(encodeURIComponent).join('/'),
  hashFor: id => '#/' + encodeURIComponent(id),
  idFromHash() { const h = location.hash; if (!h.startsWith('#/')) return null; try { return decodeURIComponent(h.slice(2)); } catch { return h.slice(2); } },
  debounce(fn, ms) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; },
  fmtTime: d => new Date(d).toLocaleString('zh-TW', { hour12: false, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }),
  isIOS: () => /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1),
  collator: new Intl.Collator('zh-Hant', { numeric: true, sensitivity: 'base' }),
  wordCount(t) { return ((t.match(/[㐀-鿿豈-﫿]/g) || []).length + (t.match(/[A-Za-z0-9_]+/g) || []).length); },
  stamp: f => f.lastModified + ':' + f.size,
  // 標題裡的 $…$ 也用 KaTeX 畫（側欄、卡片、根標題），其餘文字照常跳脫
  /* 卡片標題與晶片文字：行內格式照常渲染（R67——顯示文字可用粗體、底線、刪除線、行內碼、數學式）。
     連結與圖片在標題裡不合法（標題本身就是連結）→ 拆殼／移除；含 [[ 的照原樣顯示避免巢狀解析 */
  inlineHtml(seg) {
    if (seg.includes('[[')) return Util.esc(seg);
    try { return String(marked.parseInline(seg)).replace(/<img\b[^>]*>/gi, '').replace(/<\/?a\b[^>]*>/gi, ''); }
    catch { return Util.esc(seg); }
  },
  titleHtml(t) {
    t = String(t);
    if (!CONFIG.math || typeof katex === 'undefined' || !t.includes('$')) return Util.inlineHtml(t);
    return t.split(/(\$[^$\n]+?\$)/).map(seg => {
      if (seg.length > 2 && seg.startsWith('$') && seg.endsWith('$')) { try { return katex.renderToString(seg.slice(1, -1), { throwOnError: false, strict: 'ignore' }); } catch { return Util.esc(seg); } }
      return Util.inlineHtml(seg);
    }).join('');
  },
};

function h(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k === 'html') el.innerHTML = v;
    else if (k === 'dataset') Object.assign(el.dataset, v);
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else if (v === true) el.setAttribute(k, '');
    else el.setAttribute(k, v);
  }
  for (const c of children.flat(Infinity)) if (c != null && c !== false) el.append(c.nodeType ? c : document.createTextNode(String(c)));
  return el;
}

const ICON = {
  chev: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m9 6 6 6-6 6"/></svg>',
  down: '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>',
  pen: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>',
  triBold: '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3.5 19 12 7 20.5z" fill="currentColor"/></svg>',   // 扁平外觀用的實心粗箭頭
  merge: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 14-5-5 5-5"/><path d="M4 9h10a6 6 0 0 1 6 6v5"/></svg>',   // 併回（R47）
};

/* ===================== Parse：把一個 .md 切成 標題／摘要／內文 ===================== */
const Parse = {
  frontmatter(text) {
    const m = /^---[ \t]*\n([\s\S]*?)\n---[ \t]*(?:\n|$)/.exec(text);
    if (!m) return { meta: {}, rest: text, raw: '' };
    const meta = {}; let last = null;
    for (const line of m[1].split('\n')) {
      const mm = /^([\w\-㐀-鿿]+)\s*:\s*(.*)$/.exec(line);
      if (mm) { meta[mm[1]] = mm[2].trim().replace(/^(["'])(.*)\1$/, '$2'); last = mm[1]; continue; }
      const li = /^\s*-\s+(.+)$/.exec(line);   // YAML 清單：tags:\n  - a\n  - b
      if (li && last) { if (!Array.isArray(meta[last])) meta[last] = meta[last] ? [meta[last]] : []; meta[last].push(li[1].trim().replace(/^(["'])(.*)\1$/, '$2')); }
    }
    return { meta, rest: text.slice(m[0].length), raw: m[0] };   // raw：編輯器存檔時原樣保留
  },
  /* 標籤（R37）：frontmatter 的 tags／tag／標籤——接受 [a, b]、a, b、#a #b、YAML 清單；統一成去掉 # 的字串陣列 */
  tags(meta) {
    let v = meta.tags ?? meta.tag ?? meta['標籤'];
    if (v == null) return [];
    const arr = Array.isArray(v) ? v : String(v).replace(/^\[|\]$/g, '').split(/[,，、\s]+/);
    return [...new Set(arr.map(t => String(t).trim().replace(/^#/, '').replace(/^(["'])(.*)\1$/, '$2')).filter(Boolean))];
  },
  title(lines) {
    let i = 0;
    while (i < lines.length && !lines[i].trim()) i++;
    if (i < lines.length) {
      const m = /^#[ \t]+(.+?)[ \t]*#*[ \t]*$/.exec(lines[i]);
      if (m) return { title: m[1].trim(), rest: lines.slice(i + 1) };
      if (i + 1 < lines.length && /^=+\s*$/.test(lines[i + 1]) && lines[i].trim()) return { title: lines[i].trim(), rest: lines.slice(i + 2) };
    }
    return { title: null, rest: lines };
  },
  h2Name(line) {
    const m = /^##[ \t]+(.+?)[ \t]*#*[ \t]*$/.exec(line);
    return m ? m[1].trim().replace(/[:：]$/, '').toLowerCase() : null;
  },
  isFence: l => /^\s{0,3}(```|~~~)/.test(l),
  split(rest) {
    if (CONFIG.format === 'separator') {
      let inFence = false, sep = -1;
      for (let i = 0; i < rest.length; i++) {
        if (this.isFence(rest[i])) inFence = !inFence;
        else if (!inFence && /^\s*-{3,}\s*$/.test(rest[i])) { sep = i; break; }
      }
      return sep === -1 ? { summary: '', body: rest.join('\n'), pre: '' }
                        : { summary: rest.slice(0, sep).join('\n'), body: rest.slice(sep + 1).join('\n'), pre: '' };
    }
    const S = CONFIG.summaryHeadings.map(s => s.toLowerCase()), B = CONFIG.bodyHeadings.map(s => s.toLowerCase());
    const pre = [], sum = [], bod = [];
    let cur = pre, inFence = false, seenBody = false, seenSum = false;
    for (const l of rest) {
      if (this.isFence(l)) { inFence = !inFence; cur.push(l); continue; }
      if (!inFence && !seenBody) {
        const name = this.h2Name(l);
        if (name !== null) {
          if (B.includes(name)) { cur = bod; seenBody = true; continue; }
          if (!seenSum && S.includes(name)) { cur = sum; seenSum = true; continue; }
          if (cur === sum) cur = pre;   // 摘要之後出現別的 ## → 摘要結束，後面算內文
        }
      }
      cur.push(l);
    }
    return { summary: sum.join('\n'), body: pre.concat(bod).join('\n'), pre: pre.join('\n') };
  },
  module(text, path) {
    text = String(text).replace(/\r\n?/g, '\n').replace(/^﻿/, '');
    const { meta, rest: afterFm } = this.frontmatter(text);
    const { title: h1, rest } = this.title(afterFm.split('\n'));
    let { summary, body, pre } = this.split(rest);
    const id = Util.pathToId(path);
    const title = String(meta.title || h1 || Util.basename(id)).trim();
    if (meta.summary && !summary.trim()) summary = String(meta.summary);
    summary = summary.trim(); body = body.trim();
    // linkIndex：改寫連結模式（D26）時，把「摘要／內文裡第 k 個連結」換算成「整個檔案裡第 j 個連結」要用
    const linkIndex = { pre: pre.trim() ? Refs.cards(pre).length : 0, summary: summary ? Refs.cards(summary).length : 0 };
    const taskIndex = { pre: pre.trim() ? TaskWriter.scan(pre).length : 0, summary: summary ? TaskWriter.scan(summary).length : 0 };   // 同 linkIndex，核取方塊用（R38）
    const tags = this.tags(meta), date = meta.date != null ? String(meta.date) : (meta['日期'] != null ? String(meta['日期']) : '');
    return { id, path, title, summary, body, meta, tags, date, raw: text, mtime: 0, links: Refs.extract(summary + '\n' + body), linkIndex, taskIndex };
  },
};

/* ===================== Refs：解析 [[目標|模式|顯示文字]] ===================== */
const Refs = {
  parse(inner, bang) {
    const parts = inner.split('|').map(s => s.trim());
    let target = parts.shift() || '', anchor = null;
    const hi = target.indexOf('#');
    if (hi > 0) { anchor = target.slice(hi + 1); target = target.slice(0, hi); }
    let mode = bang ? 3 : null, style = null, label = null; const opts = [];
    for (const p of parts) {
      if (!p) continue;
      const m = CONFIG.modeAliases[p.toLowerCase()], s = CONFIG.styleAliases[p.toLowerCase()];
      if (m && mode === null) mode = m;
      else if (s && style === null) style = s;
      else if (label === null) label = p;
      else opts.push(p);
    }
    return { target, anchor, mode: mode ?? CONFIG.defaultMode, style: style || 'card', label, opts };
  },
  /* 把解析結果寫回 [[…]]（改寫模式用，D26）：模式 1 不寫字；外觀只在扁平時寫 */
  build(ref) {
    const parts = [ref.target + (ref.anchor ? '#' + ref.anchor : '')];
    if (ref.mode === 2) parts.push('摘要'); else if (ref.mode === 3) parts.push('全文');
    if (ref.style === 'flat') parts.push('扁平');
    else if (ref.style === 'group') parts.push('群組縮排');
    if (ref.label) parts.push(ref.label);
    for (const o of ref.opts || []) parts.push(o);
    return '[[' + parts.join('|') + ']]';
  },
  /* 從全文抽出所有連結（反向連結、壞連結用）。用 marked 本身的 lexer 走訪 token，
     所以和畫面上的解析結果一致：程式碼、數學式裡的 [[…]] 自然不算。 */
  extract(text) {
    const out = [];
    const walk = toks => {   // 文件順序（和畫面上卡片／晶片的順序一致；表格先表頭再列）
      for (const t of toks || []) {
        if (t.type === 'modBlock' || t.type === 'modInline') out.push({ ...t.ref, raw: (t.src || t.raw || '').trim() });
        else if (t.type === 'link' && /\.md$/i.test(t.href || '')) { let h = t.href; try { h = decodeURIComponent(h); } catch {} out.push({ target: h.replace(/\.md$/i, ''), mode: 1, style: 'card', label: null, opts: [], mdlink: true, raw: t.raw }); }
        if (t.tokens) walk(t.tokens);
        if (t.items) walk(t.items);
        if (t.header) for (const cell of t.header) walk(cell.tokens);
        if (t.rows) for (const row of t.rows) for (const cell of row) walk(cell.tokens);
      }
    };
    try { walk(marked.lexer(String(text || ''))); } catch (e) { console.warn('連結解析失敗', e); }
    return out;
  },
  /* 只要會變成卡片或晶片的連結（排除一般 Markdown 連結），文件順序 */
  cards(text) { return this.extract(text).filter(r => !r.mdlink); },
};

/* ===================== Store：所有模組與索引 ===================== */
const Store = {
  modules: new Map(), assets: new Map(),
  _lower: new Map(), _base: new Map(), _title: new Map(), _back: new Map(), _tags: new Map(),
  clear() { this.modules.clear(); for (const a of this.assets.values()) if (a.objUrl) URL.revokeObjectURL(a.objUrl); this.assets.clear(); this.reindex(); },
  upsert(mod) { this.modules.set(mod.id, mod); },
  remove(id) { this.modules.delete(id); },
  addAsset(a) { this.assets.set(Util.pathToId(a.path) + '.' + Util.ext(a.path), a); },
  list() { return [...this.modules.values()].sort((a, b) => Util.collator.compare(a.path, b.path)); },
  reindex() {
    this._lower.clear(); this._base.clear(); this._title.clear(); this._back.clear(); this._tags.clear();
    const push = (map, k, v) => { const arr = map.get(k) || []; arr.push(v); map.set(k, arr); };
    for (const m of this.list()) {
      this._lower.set(m.id.toLowerCase(), m);
      push(this._base, Util.basename(m.id).toLowerCase(), m);
      push(this._title, m.title.toLowerCase(), m);
      for (const t of m.tags || []) push(this._tags, t, m);
    }
    for (const m of this.modules.values()) {
      for (const ref of m.links) { const t = this.resolve(ref.target, Util.dirname(m.path)); if (t && t.id !== m.id) push(this._back, t.id, m.id); }
    }
    for (const [k, v] of this._back) this._back.set(k, [...new Set(v)]);
  },
  resolve(target, basePath = '') {
    if (!target) return null;
    const t = Util.pathToId(String(target).trim());
    if (!t) return null;
    if (this.modules.has(t)) return this.modules.get(t);
    const rel = Util.join(basePath, t);
    if (rel !== t && this.modules.has(rel)) return this.modules.get(rel);
    const lower = t.toLowerCase();
    if (this._lower.has(lower)) return this._lower.get(lower);
    const bl = Util.basename(t).toLowerCase();
    const byBase = this._base.get(bl); if (byBase && byBase.length) return byBase[0];
    const byTitle = this._title.get(lower); if (byTitle && byTitle.length) return byTitle[0];
    return null;
  },
  /* 只用前兩步（完整 id、相對於所在資料夾）找：搬移時判斷「搬過去還找得到嗎」用，不靠檔名或標題的寬鬆比對 */
  resolveStrict(target, basePath = '') {
    const t = Util.pathToId(String(target || '').trim()); if (!t) return null;
    if (this.modules.has(t)) return this.modules.get(t);
    const rel = Util.join(basePath, t); return (rel !== t && this.modules.has(rel)) ? this.modules.get(rel) : null;
  },
  backlinks(id) { return (this._back.get(id) || []).map(i => this.modules.get(i)).filter(Boolean).sort((a, b) => Util.collator.compare(a.title, b.title)); },
  /* 標籤 → 模組（R37）；tags() 回傳 [[標籤, 數量]] 依數量排序 */
  byTag(tag) { const k = [...this._tags.keys()].find(t => t.toLowerCase() === String(tag).toLowerCase()); return k ? this._tags.get(k) : []; },
  tags() { return [...this._tags.entries()].map(([t, arr]) => [t, arr.length]).sort((a, b) => b[1] - a[1] || Util.collator.compare(a[0], b[0])); },
  /* 在 fromDir 裡的模組要連到 id 時，最短又不會連錯的寫法：同一個資料夾只寫檔名（但最上層沒有同名模組才行，因為完整 id 會先被找到）；其餘寫完整路徑 */
  linkTarget(id, fromDir) {
    const base = Util.basename(id);
    if (Util.dirname(id) === fromDir && fromDir && !this.modules.has(base)) return base;
    if (fromDir && id.startsWith(fromDir + '/') && !this.modules.has(id.slice(fromDir.length + 1))) return id.slice(fromDir.length + 1);
    return id;
  },
  brokenLinks() {
    const map = new Map();   // target → Set(from id)
    for (const m of this.modules.values()) for (const ref of m.links) {
      if (!ref.target || this.resolve(ref.target, Util.dirname(m.path))) continue;
      if (!map.has(ref.target)) map.set(ref.target, new Set()); map.get(ref.target).add(m.id);
    }
    return [...map.entries()].map(([target, from]) => ({ target, from: [...from].map(i => this.modules.get(i)).filter(Boolean) })).sort((a, b) => Util.collator.compare(a.target, b.target));
  },
  async assetUrl(rel, basePath) {
    if (App.source && App.source.kind === 'http') return Util.encodePath(Util.join(basePath, rel));
    const key = Util.pathToId(Util.join(basePath, rel)) + '.' + Util.ext(rel), key2 = Util.pathToId(rel) + '.' + Util.ext(rel);
    const a = this.assets.get(key) || this.assets.get(key2);
    if (!a) return null;
    if (a.url) return a.url;
    if (!a.objUrl) { const file = a.file || (a.handle && await a.handle.getFile()); if (!file) return null; a.objUrl = URL.createObjectURL(file); }
    return a.objUrl;
  },
};

/* ===================== MD：marked + [[...]] 擴充 ===================== */
const MD = (() => {
  const attr = ref => Util.esc(JSON.stringify(ref));
  const block = {
    name: 'modBlock', level: 'block',
    start(src) { const m = /^[ \t]{0,3}!?\[\[/m.exec(src); return m ? m.index : undefined; },
    tokenizer(src) { const m = /^[ \t]{0,3}(!?)\[\[([^\[\]\n`]+?)\]\][ \t]*(?:\n|$)/.exec(src); if (m) return { type: 'modBlock', raw: m[0], src: m[0].trim(), ref: Refs.parse(m[2], !!m[1]) }; },
    renderer(tok) { return `<div class="mod-ph" data-ref="${attr(tok.ref)}" data-raw="${Util.esc(tok.src)}"></div>\n`; },   // data-raw：編輯器原樣寫回用
  };
  const inline = {
    name: 'modInline', level: 'inline',
    start(src) { const i = src.search(/!?\[\[/); return i >= 0 ? i : undefined; },
    tokenizer(src) { const m = /^(!?)\[\[([^\[\]\n`]+?)\]\]/.exec(src); if (m) return { type: 'modInline', raw: m[0], ref: Refs.parse(m[2], !!m[1]) }; },
    renderer(tok) { return `<span class="mod-ph-inline" data-ref="${attr(tok.ref)}" data-raw="${Util.esc(tok.raw)}"></span>`; },
  };
  // 數學式：區塊 $$…$$ / \[…\]，行內 $…$ / \(…\)（程式碼裡的不會被碰到，因為 marked 先處理 code）
  const renderMath = (tex, display) => {
    if (typeof katex === 'undefined') return display ? `<pre class="math-src">${Util.esc(tex)}</pre>` : `<code class="math-src">${Util.esc(tex)}</code>`;
    try { return katex.renderToString(tex, { displayMode: display, throwOnError: false, strict: 'ignore', output: 'htmlAndMathml' }); }
    catch (e) { return `<code class="math-src" title="${Util.esc(e.message)}">${Util.esc(tex)}</code>`; }
  };
  const mathBlock = {
    name: 'mathBlock', level: 'block',
    start(src) { const m = /^[ \t]{0,3}(\$\$|\\\[)/m.exec(src); return m ? m.index : undefined; },
    tokenizer(src) {
      const m = /^[ \t]{0,3}\$\$([\s\S]+?)\$\$[ \t]*(?:\n|$)/.exec(src) || /^[ \t]{0,3}\\\[([\s\S]+?)\\\][ \t]*(?:\n|$)/.exec(src);
      if (m) return { type: 'mathBlock', raw: m[0], tex: m[1].trim() };
    },
    renderer(tok) { return `<div class="math-block" data-raw="${Util.esc(tok.raw.trim())}">${renderMath(tok.tex, true)}</div>\n`; },
  };
  const mathInline = {
    name: 'mathInline', level: 'inline',
    start(src) { const i = src.search(/\$(?!\s)|\\\(/); return i >= 0 ? i : undefined; },
    tokenizer(src) {
      // 內容不可含反引號：否則一個孤零零的 $ 會跨過後面的行內程式碼去配對
      const m = /^\$(?!\s|\$)((?:\\.|[^\\$\n`])+?)(?<!\s)\$(?!\d|\$)/.exec(src) || /^\\\(((?:\\.|[^\\\n`])+?)\\\)/.exec(src);
      if (m) return { type: 'mathInline', raw: m[0], tex: m[1] };
    },
    renderer(tok) { return `<span class="math-inline" data-raw="${Util.esc(tok.raw)}">${renderMath(tok.tex, false)}</span>`; },
  };
  const exts = [block, inline];
  if (CONFIG.math) exts.push(mathBlock, mathInline);
  marked.use({ gfm: CONFIG.markdown.gfm, breaks: CONFIG.markdown.breaks, extensions: exts });
  return {
    render(text) {
      try { return marked.parse(text || ''); }
      catch (e) { console.error(e); return `<pre>${Util.esc(text)}</pre>`; }
    },
  };
})();

/* ===================== Cards：巢狀卡片、行內晶片、找不到的模組 ===================== */
const Cards = {
  // ctx = { ancestors: [id...], key: '路徑鍵', depth, basePath }
  card(mod, ref, ctx, occ = 0, extraClass = '') {
    const cyclic = ctx.ancestors.includes(mod.id);
    const tooDeep = ctx.depth >= CONFIG.maxDepth;
    const capped = cyclic || tooDeep;
    const hasSummary = !!mod.summary;
    const key = `${ctx.key}>${mod.id}#${occ}`;
    const el = h('section', { class: 'card' + (extraClass ? ' ' + extraClass : '') + (ref.style === 'flat' ? ' flat' : ref.style === 'group' ? ' group' : ''), dataset: { id: mod.id, key, depth: String(ctx.depth), rail: String(((ctx.depth - 1) % 4) + 1), style: ref.style || 'card' } });
    el._ref = ref; el._parent = ctx.ancestors[ctx.ancestors.length - 1];   // 改寫連結模式時要知道連結寫在哪個模組裡
    if (ref.index != null) el.dataset.link = String(ref.index);
    const tri = h('button', { class: 'tri icon-btn', type: 'button', title: '展開／收合', html: (ref.style === 'flat' || ref.style === 'group') ? ICON.triBold : ICON.chev });
    const title = h('a', { class: 'card-title', href: Util.hashFor(mod.id), title: mod.path, html: Util.titleHtml(ref.label || mod.title) });
    const segBtns = [1, 2, 3].map(m => h('button', { type: 'button', dataset: { m: String(m) } }, ['標題', '摘要', '全文'][m - 1]));
    if (!hasSummary) { segBtns[1].disabled = true; segBtns[1].title = '這個模組沒有摘要'; }
    if (capped) { segBtns[2].disabled = true; segBtns[2].title = cyclic ? '循環引用：這個模組已在上層展開' : '已達巢狀深度上限'; }
    // 外觀用和「標題／摘要／全文」一樣的段控鈕：兩個選項都看得到，目前的反白（R27）
    const styleBtns = [['card', '卡片', '卡片外觀：有框、標題粗體'], ['flat', '扁平', '扁平外觀：像清單項目，和其他項目平行'], ['group', '群組縮排', '群組縮排：無框，標題粗體，內容縮排在標題底下']].map(([st, label, title]) => h('button', { type: 'button', dataset: { st }, title }, label));
    const tools = h('div', { class: 'card-tools' }, h('div', { class: 'seg', role: 'group', 'aria-label': '顯示範圍' }, segBtns), h('div', { class: 'seg style-seg', role: 'group', 'aria-label': '外觀' }, styleBtns));
    if (App.canEdit()) tools.append(h('button', { class: 'icon-btn edit', type: 'button', title: '編輯這個模組', html: ICON.pen, onclick: () => App.edit(mod.id) }));
    if (App.canEdit() && typeof App.source.remove === 'function') tools.append(h('button', { class: 'icon-btn merge', type: 'button', title: '併回：把這個模組的內容搬回這裡、刪除模組檔（R47）', html: ICON.merge, onclick: () => App.inlineCard(el, mod, ref) }));
    el.append(h('header', { class: 'card-head' }, tri, title,
      cyclic ? h('span', { class: 'card-badge', title: '這個模組在上層已經展開過' }, '循環引用') : null,
      (!cyclic && tooDeep) ? h('span', { class: 'card-badge' }, '深度上限') : null,
      tools));

    el.dataset.initStyle = ref.style || 'card';
    // 外觀：卡片 ↔ 扁平（R27）。改了會和模式一樣寫回檔案（或唯讀時記在瀏覽器）
    const setStyle = (st, initial) => {
      st = (st === 'flat' || st === 'group') ? st : 'card';
      el.classList.toggle('flat', st === 'flat'); el.classList.toggle('group', st === 'group'); el.dataset.style = st; ref.style = st;
      tri.innerHTML = st !== 'card' ? ICON.triBold : ICON.chev;
      styleBtns.forEach(b => b.classList.toggle('on', b.dataset.st === st));
      if (!initial) App.onCardStyle(el);
    };
    el._setStyle = setStyle; styleBtns.forEach(b => b.addEventListener('click', () => { if (b.dataset.st !== el.dataset.style) setStyle(b.dataset.st); }));
    const childCtx = { ancestors: [...ctx.ancestors, mod.id], key, depth: ctx.depth + 1, basePath: Util.dirname(mod.path) };
    let summaryEl = null, bodyEl = null, mode = 0;
    let expanded = ref.mode > 1 ? ref.mode : 3;
    // 沒有摘要的模組：一開始若要求「摘要」就只顯示標題；之後手動展開則直接到全文
    const clamp = (m, initial) => { if (capped) m = Math.min(m, 2); if (m === 2 && !hasSummary) m = (initial || capped) ? 1 : 3; return m; };
    const ensure = m => {
      if (m >= 2 && hasSummary && !summaryEl) { summaryEl = h('div', { class: 'card-summary md', html: MD.render(mod.summary) }); Cards.hydrate(summaryEl, childCtx, mod, 'summary'); el.append(summaryEl); }
      if (m >= 3 && !bodyEl) {
        bodyEl = h('div', { class: 'card-body md', html: mod.body ? MD.render(mod.body) : '<p class="note">（沒有內文）</p>' });
        Cards.hydrate(bodyEl, childCtx, mod, 'body'); el.append(bodyEl);
      }
    };
    const setMode = (m, initial) => {
      m = clamp(m, initial); ensure(m); mode = m; el.dataset.mode = String(m);
      segBtns.forEach(b => b.classList.toggle('on', +b.dataset.m === m));
      tri.setAttribute('aria-expanded', String(m > 1));
      if (m > 1) expanded = m;
      if (!initial) App.onCardMode(el);   // 使用者改了 → 寫進檔案或記住（還原中會被 App._restoring 擋掉）
    };
    el._setMode = setMode; el._getMode = () => mode;
    tri.addEventListener('click', () => setMode(mode > 1 ? 1 : expanded));
    segBtns.forEach(b => b.addEventListener('click', () => { if (!b.disabled) setMode(+b.dataset.m); }));
    el.dataset.init = String(clamp(ref.mode || 1, true));   // 連結要求的預設模式；記憶只記和它不同的（D24）
    setStyle(ref.style, true);
    setMode(ref.mode || 1, true);
    return el;
  },

  chip(ref, mod, ctx, occ) {
    const key = `${ctx.key}>${mod.id}#i${occ}`;
    const chip = h('span', { class: 'chip' + (ref.style === 'flat' ? ' flat' : ''), dataset: { id: mod.id, key } });
    const go = h('a', { class: 'chip-go', href: Util.hashFor(mod.id), title: mod.path, html: Util.titleHtml(ref.label || mod.title) });
    const x = h('button', { class: 'chip-x', type: 'button', title: '在這裡展開', html: ICON.down });
    chip.append(go, x);
    chip._card = null;
    chip._expand = (m) => {
      if (chip._card) { chip._card.remove(); chip._card = null; chip.classList.remove('open'); return; }
      const want = Math.max(ref.mode || 1, m || CONFIG.inlineExpandMode);
      const card = Cards.card(mod, { ...ref, mode: want }, ctx, 'i' + occ, 'inline-expand');
      card.dataset.inline = '1';
      const host = chip.closest('li, td, th, p, h1, h2, h3, h4, h5, h6, blockquote, dd') || chip.parentElement;
      if (/^(P|H[1-6]|BLOCKQUOTE)$/.test(host.tagName)) host.after(card); else host.append(card);
      chip._card = card; chip.classList.add('open');
    };
    x.addEventListener('click', () => { chip._expand(); App.remember(); });
    return chip;
  },

  missing(ref, ctx, block) {
    const creatable = App.canEdit();
    const name = ref.target;
    if (block) {
      const el = h('div', { class: 'missing-block', dataset: { target: name } }, h('span', {}, '找不到模組 ', h('code', {}, name)));
      if (creatable) el.append(h('button', { class: 'btn', type: 'button', onclick: () => App.createModule(name) }, '建立這個模組'));
      else el.append(h('span', { class: 'note' }, '（檔案還不存在）'));
      return el;
    }
    const chip = h('span', { class: 'chip missing' + (creatable ? ' creatable' : ''), dataset: { target: name }, title: creatable ? '找不到模組，按一下建立' : '找不到模組：' + name + '.md' });
    const go = h('a', { class: 'chip-go', href: '#' }, ref.label || name);
    go.addEventListener('click', e => { e.preventDefault(); if (creatable && confirm(`找不到模組「${name}」，要建立 ${name}.md 嗎？`)) App.createModule(name); });
    chip.append(go);
    return chip;
  },

  /* 清單記號（D28、R62）：Safari 會把原生號碼畫進卡片裡，而且 WebKit 與 Chrome 的原生記號度量不同——
     卡片項（自畫）配原生項（瀏覽器畫）在 Safari 永遠對不齊。所以閱讀畫面的清單記號**全部**自己畫：
     編號算好放 data-n（純文字項放在 li、卡片項放在卡片頭），圓點項標 data-b 由 CSS 依層級畫；
     核取方塊項目不標。編輯器裡沒有這些標記，維持原生記號。 */
  numberListCards(container) {
    const alpha = n => { let s = ''; while (n > 0) { n--; s = String.fromCharCode(97 + (n % 26)) + s; n = Math.floor(n / 26); } return s; };
    const roman = n => { const T = [[1000, 'm'], [900, 'cm'], [500, 'd'], [400, 'cd'], [100, 'c'], [90, 'xc'], [50, 'l'], [40, 'xl'], [10, 'x'], [9, 'ix'], [5, 'v'], [4, 'iv'], [1, 'i']]; let s = ''; for (const [v, r] of T) while (n >= v) { s += r; n -= v; } return s; };
    const hasBox = li => !!li.querySelector(':scope > input[type="checkbox"], :scope > p:first-child > input[type="checkbox"]');
    for (const ol of container.querySelectorAll('ol')) {
      const items = [...ol.children].filter(el => el.tagName === 'LI');
      const rev = ol.hasAttribute('reversed');
      const start = ol.hasAttribute('start') ? (parseInt(ol.getAttribute('start'), 10) || 1) : (rev ? items.length : 1);
      const type = ol.getAttribute('type');
      items.forEach((li, idx) => {
        const n = rev ? start - idx : start + idx;
        let label = String(n);
        if (n > 0) {
          if (type === 'a') label = alpha(n); else if (type === 'A') label = alpha(n).toUpperCase();
          else if (type === 'i') label = roman(n); else if (type === 'I') label = roman(n).toUpperCase();
        }
        if (hasBox(li)) return;
        li.dataset.n = label;   // 記號一律掛在 li 上（Safari 對 flex 容器〔卡片標題列〕的絕對定位 ::before 會算錯位置）
      });
    }
    for (const ul of container.querySelectorAll('ul')) {
      for (const li of ul.children) {
        if (li.tagName !== 'LI' || hasBox(li)) continue;
        li.dataset.b = '1';
      }
    }
  },
  /* owner／part：這個容器是哪個模組的摘要或內文（算出每個連結在檔案裡的序號，改寫模式用） */
  hydrate(container, ctx, owner, part) {
    const occ = new Map();
    const next = k => { const n = occ.get(k) || 0; occ.set(k, n + 1); return n; };
    const li = owner && owner.linkIndex;
    const fileIndex = k => !li ? null : (part === 'summary' ? li.pre + k : (k < li.pre ? k : li.summary + k));
    let k = 0;
    for (const ph of [...container.querySelectorAll('.mod-ph, .mod-ph-inline')]) {   // 文件順序，和 Refs.cards() 一致
      let ref; try { ref = JSON.parse(ph.dataset.ref); } catch { continue; }
      ref.raw = ph.dataset.raw || ''; ref.index = fileIndex(k++);
      const block = ph.classList.contains('mod-ph');
      const mod = Store.resolve(ref.target, ctx.basePath);
      if (block) ph.replaceWith(mod ? this.card(mod, ref, ctx, next(mod.id)) : this.missing(ref, ctx, true));
      else ph.replaceWith(mod ? this.chip(ref, mod, ctx, next('i:' + mod.id)) : this.missing(ref, ctx, false));
    }
    this.numberListCards(container);
    TaskWriter.enable(container, owner, part);   // 核取方塊直接點、寫回檔案（R38）
    // 注意：巢狀卡片的摘要／內文在上面 replaceWith 時已用「它自己的資料夾」解析過相對路徑，
    // 這裡再抓到它們會用父頁面的資料夾重算而蓋錯（HTTP 來源必回字串、蓋掉才會 404；1.1.7 修正），
    // 所以處理過的一律標記 data-hyd，外層跳過。
    for (const a of container.querySelectorAll('a[href]')) {
      if (a.dataset.hyd) continue;
      if (a.closest('.chip, .card-head')) continue;
      const href = a.getAttribute('href') || '';
      if (/^(https?:|mailto:|tel:)/i.test(href)) { a.target = '_blank'; a.rel = 'noopener'; continue; }
      if (href.startsWith('#')) continue;
      let dec = href; try { dec = decodeURIComponent(href); } catch {}
      if (/\.md$/i.test(dec)) {
        a.dataset.hyd = '1';
        const mod = Store.resolve(dec.replace(/\.md$/i, ''), ctx.basePath);
        if (mod) { a.href = Util.hashFor(mod.id); a.classList.add('mod-link'); }
      }
    }
    for (const img of container.querySelectorAll('img[src]')) {
      if (img.dataset.hyd) continue;
      const src = img.getAttribute('src') || '';
      if (/^(https?:|data:|blob:)/i.test(src)) continue;
      img.dataset.hyd = '1';
      let dec = src; try { dec = decodeURIComponent(src); } catch {}
      Store.assetUrl(dec, ctx.basePath).then(url => { if (url) img.src = url; });
    }
    for (const img of container.querySelectorAll('img')) {   // R65：預設半寬，按一下放大／縮回（只在閱讀畫面；編輯器沒跑 hydrate）
      if (img.dataset.z || img.closest('a[href]')) continue;
      img.dataset.z = '1';
      img.addEventListener('click', () => img.classList.toggle('img-full'));
    }
  },
};

/* ===================== Persist：記住資料夾、快取、偏好（每個 html 檔各自一份） ===================== */
// 同一台電腦上所有 file:// 網頁共用同一個瀏覽器儲存空間，所以一律用「這個 html 的路徑」當前綴：
// 複製到 A、B 兩個資料夾裡的 index.html 才會各記各的，互不干擾。
const PROFILE = (() => { let p = location.pathname; try { p = decodeURIComponent(p); } catch {} return ((location.origin && location.origin !== 'null') ? location.origin : 'file') + p; })();
const LS = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch {} },
  del(k) { try { localStorage.removeItem(k); } catch {} },
};
const Persist = {
  _db: undefined,   // undefined = 還沒試；null = IndexedDB 不可用（例如 Safari 的 file://），改用 localStorage
  key: k => `nm::${PROFILE}::${k}`,
  pref: { get: k => LS.get(Persist.key(k)), set: (k, v) => LS.set(Persist.key(k), v), del: k => LS.del(Persist.key(k)) },
  async db() {
    if (this._db !== undefined) return this._db;
    try {
      this._db = await new Promise((res, rej) => {
        const r = indexedDB.open('notes-modules', 1);
        r.onupgradeneeded = () => r.result.createObjectStore('kv');
        r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); r.onblocked = () => rej(new Error('blocked'));
        setTimeout(() => rej(new Error('timeout')), 4000);
      });
    } catch { this._db = null; }
    return this._db;
  },
  async get(k) {
    const db = await this.db();
    if (db) { try { return await new Promise((res, rej) => { const t = db.transaction('kv', 'readonly').objectStore('kv').get(this.key(k)); t.onsuccess = () => res(t.result); t.onerror = () => rej(t.error); }); } catch {} }
    const raw = LS.get(this.key(k)); if (raw == null) return undefined;
    try { return JSON.parse(raw); } catch { return undefined; }
  },
  async set(k, v) {
    const db = await this.db();
    if (db) { try { await new Promise((res, rej) => { const t = db.transaction('kv', 'readwrite'); t.objectStore('kv').put(v, this.key(k)); t.oncomplete = res; t.onerror = () => rej(t.error); }); return true; } catch {} }
    try {   // localStorage 退路：只能存純文字（圖片與資料夾 handle 存不進去），上限約 4 MB
      if (k === 'dirHandle') return false;
      if (v && v.assets) v = { ...v, assets: [] };
      const str = JSON.stringify(v); if (str === undefined || str.length > 4000000) return false;
      localStorage.setItem(this.key(k), str); return true;
    } catch { return false; }
  },
  async del(k) {
    const db = await this.db();
    if (db) { try { await new Promise((res, rej) => { const t = db.transaction('kv', 'readwrite'); t.objectStore('kv').delete(this.key(k)); t.oncomplete = res; t.onerror = () => rej(t.error); }); } catch {} }
    LS.del(this.key(k));
  },
};

/* ===================== Memory：每頁的展開狀態（R22）與側欄樹的展開節點（R24） ===================== */
// 都是小小的 JSON，放 localStorage（同樣以 html 路徑為前綴）。cards 只記「和連結預設不同」的卡片（D24）。
const Memory = {
  _read(k) { try { return JSON.parse(Persist.pref.get(k) || '{}') || {}; } catch { return {}; } },
  _write(k, v) { Persist.pref.set(k, JSON.stringify(v)); },
  cards(id) { const all = this._read('cards'); return all[id] || null; },
  setCards(id, state) {
    if (!id) return;
    const all = this._read('cards');
    const empty = !Object.keys(state.modes || {}).length && !Object.keys(state.chips || {}).length && !Object.keys(state.styles || {}).length;
    if (empty) delete all[id]; else all[id] = { modes: state.modes, chips: state.chips, styles: state.styles || {}, t: Date.now() };
    const ids = Object.keys(all);
    if (ids.length > 400) ids.sort((a, b) => (all[a].t || 0) - (all[b].t || 0)).slice(0, ids.length - 400).forEach(k => delete all[k]);   // 最多記 400 頁
    this._write('cards', all);
  },
  clearCards(id) { const all = this._read('cards'); if (id in all) { delete all[id]; this._write('cards', all); } },
  treeOpen(path) { return !!this._read('tree')[path]; },
  setTreeOpen(path, open) { const t = this._read('tree'); if (open) t[path] = 1; else delete t[path]; this._write('tree', t); },
  forgetAll() { Persist.pref.del('cards'); Persist.pref.del('tree'); },
};

/* ===================== LinkWriter：把卡片的展開狀態寫進 .md（R22、D26） =====================
   改卡片模式 = 改寫父模組檔案裡那個 [[…]] 的模式字。位置靠「lexer 列出的連結（文件順序）」和
   「原文掃描到的 [[…]] 候選（跳過程式碼）」對齊；改完用 lexer 驗證才存檔。 */
const LinkWriter = {
  pending: new Map(), timer: null, busy: false,
  queue(parentId, index, raw, patch) {   // patch：{ mode } 或 { style } 或兩者
    if (!this.pending.has(parentId)) this.pending.set(parentId, new Map());
    const cur = this.pending.get(parentId).get(index) || { raw };
    this.pending.get(parentId).set(index, Object.assign(cur, patch, { raw }));
    clearTimeout(this.timer); this.timer = setTimeout(() => this.flush(), 600);
  },
  async flush() {
    if (this.busy) { clearTimeout(this.timer); this.timer = setTimeout(() => this.flush(), 300); return; }
    this.busy = true;
    try {
      const jobs = [...this.pending.entries()]; this.pending.clear();
      for (const [id, changes] of jobs) { try { await this.apply(id, changes); } catch (e) { console.warn(e); App.toast('無法寫回 ' + id + '：' + (e.message || e), true); } }
    } finally { this.busy = false; }
  },
  /* 原文裡所有 [[…]] 候選的位置（跳過圍欄程式碼與行內程式碼） */
  candidates(text) {
    const out = [];
    let i = 0, fence = null;
    const lines = text.split('\n'); let offset = 0;
    for (const line of lines) {
      const f = /^\s{0,3}(`{3,}|~{3,})/.exec(line);
      if (fence) { if (f && f[1][0] === fence[0] && f[1].length >= fence.length) fence = null; offset += line.length + 1; continue; }
      if (f) { fence = f[1]; offset += line.length + 1; continue; }
      let j = 0;
      while (j < line.length) {
        if (line[j] === '`') { const m = /^`+/.exec(line.slice(j)); const close = line.indexOf(m[0], j + m[0].length); if (close >= 0) { j = close + m[0].length; continue; } j += m[0].length; continue; }
        if (line[j] === '[' && line[j + 1] === '[') {
          const end = line.indexOf(']]', j + 2);
          if (end >= 0 && !/[\[\]`]/.test(line.slice(j + 2, end))) { const bang = j > 0 && line[j - 1] === '!'; const s = bang ? j - 1 : j; out.push({ start: offset + s, end: offset + end + 2, raw: line.slice(s, end + 2) }); j = end + 2; continue; }
        }
        j++;
      }
      offset += line.length + 1; i++;
    }
    return out;
  },
  rewrite(text, changes) {
    const links = Refs.cards(text), cands = this.candidates(text);
    const pos = []; let c = 0;
    for (const l of links) { while (c < cands.length && cands[c].raw !== l.raw) c++; if (c >= cands.length) throw new Error('在原文裡找不到連結的位置'); pos.push(cands[c++]); }
    const edits = [...changes.entries()].map(([j, ch]) => ({ j, ...ch })).sort((a, b) => b.j - a.j);
    let out = text;
    for (const e of edits) {
      const link = links[e.j], p = pos[e.j];
      if (!link || !p || link.raw !== e.raw) throw new Error('檔案內容已經改變，這個連結對不上');
      const nr = Refs.build({ ...link, ...(e.mode != null ? { mode: e.mode } : {}), ...(e.style ? { style: e.style } : {}) });
      out = out.slice(0, p.start) + nr + out.slice(p.end);
    }
    const after = Refs.cards(out);
    if (after.length !== links.length) throw new Error('改寫後連結數不同，已放棄');
    for (let i = 0; i < links.length; i++) {
      const ch = changes.get(i) || {};
      const wantMode = ch.mode != null ? ch.mode : links[i].mode, wantStyle = ch.style || links[i].style;
      if (after[i].target !== links[i].target || after[i].mode !== wantMode || after[i].style !== wantStyle) throw new Error('改寫後驗證不符，已放棄');
    }
    return out;
  },
  /* 把檔案裡第 j 個 [[…]] 連結整個換成任意文字（併回用，R47）。
     在清單項目裡時，後續行縮排到項目內容的位置，讓多段內容仍屬於同一個項目。 */
  replaceWith(text, j, raw, replacement) {
    const links = Refs.cards(text), cands = this.candidates(text);
    const pos = []; let c = 0;
    for (const l of links) { while (c < cands.length && cands[c].raw !== l.raw) c++; if (c >= cands.length) throw new Error('在原文裡找不到連結的位置'); pos.push(cands[c++]); }
    const link = links[j], p = pos[j];
    if (!link || !p || link.raw !== raw) throw new Error('檔案內容已經改變，這個連結對不上');
    const lineStart = text.lastIndexOf('\n', p.start - 1) + 1;
    const prefix = text.slice(lineStart, p.start);
    let rep = replacement;
    const m = /^(\s*)([-*+]|\d+[.)])\s+$/.exec(prefix);
    if (m) {
      const ind = m[1] + ' '.repeat(m[2].length + 1);
      rep = replacement.split('\n').map((l, i) => (i && l.trim()) ? ind + l : (i ? '' : l)).join('\n');
    }
    const out = text.slice(0, p.start) + rep + text.slice(p.end);
    const expect = links.length - 1 + Refs.cards(replacement).length;
    if (Refs.cards(out).length !== expect) throw new Error('併回後連結數不符，已放棄');
    return out;
  },
  async apply(parentId, changes) {
    const mod = Store.modules.get(parentId); if (!mod || !App.canWriteLinks()) return;
    const out = this.rewrite(mod.raw, changes);
    if (out === mod.raw) return;
    const r = await App.source.save(mod.path, out);
    const nm = Parse.module(out, mod.path); nm.mtime = (r && r.mtime) || Date.now();
    Store.upsert(nm); Store.reindex(); App.renderSidebar(); App.updateCache();
    if (!Editor.open) App.refresh();   // 重畫但保留每張卡片的狀態與捲動位置
  },
};

/* ===================== TaskWriter：閱讀畫面上直接勾核取方塊，寫回 .md（R38） =====================
   和 LinkWriter 同一個思路：畫面上第 k 個核取方塊 ↔ 原文裡第 j 行「- [ ] / - [x]」（跳過圍欄程式碼）。 */
const TaskWriter = {
  RE: /^(\s*(?:>\s*)*)([-*+]|\d+[.)])\s+\[([ xX])\](?=\s|$)/,
  /* 原文裡所有核取項目：{ at: 方括號裡那個字元的位置, checked } */
  scan(text) {
    const out = []; let offset = 0, fence = null;
    for (const line of String(text || '').split('\n')) {
      const f = /^\s{0,3}(`{3,}|~{3,})/.exec(line);
      if (fence) { if (f && f[1][0] === fence[0] && f[1].length >= fence.length) fence = null; }
      else if (f) fence = f[1];
      else { const m = this.RE.exec(line); if (m) out.push({ at: offset + m[0].length - 2, checked: m[3] !== ' ' }); }
      offset += line.length + 1;
    }
    return out;
  },
  /* 把容器裡的核取方塊變成可以點的（唯讀來源、編輯器預覽維持 disabled） */
  enable(container, owner, part) {
    if (!owner || Editor.open || !App.canEdit() || typeof App.source.save !== 'function') return;
    let k = 0;
    for (const cb of container.querySelectorAll('input[type="checkbox"]')) {
      if (cb.closest('.md') !== container) continue;   // 巢狀卡片裡的歸它自己的容器
      const idx = k++;
      cb.disabled = false; cb.title = '點一下會直接寫回檔案';
      cb.addEventListener('change', () => this.toggle(owner.id, part, idx, cb.checked).catch(e => { cb.checked = !cb.checked; App.toast('無法寫回：' + (e.message || e), true); }));
    }
  },
  async toggle(ownerId, part, k, checked) {
    const mod = Store.modules.get(ownerId); if (!mod) throw new Error('找不到模組');
    const ti = mod.taskIndex || { pre: 0, summary: 0 };
    const j = part === 'summary' ? ti.pre + k : (k < ti.pre ? k : ti.summary + k);   // 畫面序 → 檔案序（內文 = 前段＋內文段）
    const items = this.scan(mod.raw);
    const it = items[j]; if (!it) throw new Error('對不到檔案裡的核取項目');
    if (it.checked === checked) return;
    const out = mod.raw.slice(0, it.at) + (checked ? 'x' : ' ') + mod.raw.slice(it.at + 1);
    if (this.scan(out).length !== items.length) throw new Error('改寫後驗證不符，已放棄');
    const r = await App.source.save(mod.path, out);
    const nm = Parse.module(out, mod.path); nm.mtime = (r && r.mtime) || Date.now();
    Store.upsert(nm); Store.reindex(); App.updateCache();
    if (!Editor.open) App.refresh();
  },
};

/* ===================== Refactor：改名／搬移／刪除，連結一起更新（R34、R40） =====================
   改名＝先寫新檔、再刪舊檔；搬到別的資料夾時，自己內容裡的相對連結、圖片路徑也改寫；
   所有連到它的模組，用 LinkWriter 同一套「lexer 順序 ↔ 原文候選」對齊法改寫目標。 */
const Refactor = {
  normalizeId(name) {
    name = Util.norm(String(name || '')).trim().replace(/\.md$/i, '').replace(/\\/g, '/').replace(/^\/+|\/+$/g, '').replace(/\/{2,}/g, '/');
    if (!name || name.split('/').some(seg => !seg.trim() || seg === '..' || seg === '.' || seg.startsWith('.'))) return null;
    if (/[|\[\]#]/.test(name)) return null;
    return name;
  },
  /* 連到 mod 的其他模組：回傳 [{ m, text }]（text 為改寫後的內容；改不動的不列） */
  retargetAll(mod, newId) {
    const out = [];
    for (const m of Store.modules.values()) {
      if (m.id === mod.id) continue;
      const t = this.retarget(m, mod, newId);
      if (t != null && t !== m.raw) out.push({ m, text: t });
    }
    return out;
  },
  retarget(m, oldMod, newId) {
    const raw = m.raw, dir = Util.dirname(m.path);
    const links = Refs.extract(raw);
    if (!links.some(l => Store.resolve(l.target, dir) === oldMod)) return null;
    const wiki = links.filter(l => !l.mdlink), cands = LinkWriter.candidates(raw);
    const pos = []; let c = 0;
    for (const l of wiki) { while (c < cands.length && cands[c].raw !== l.raw) c++; if (c >= cands.length) throw new Error(`${m.path}：在原文裡找不到連結的位置`); pos.push(cands[c++]); }
    let out = raw;
    for (let i = wiki.length - 1; i >= 0; i--) {
      const l = wiki[i]; if (Store.resolve(l.target, dir) !== oldMod) continue;
      const nr = Refs.build({ ...l, target: Store.linkTarget(newId, dir) });
      out = out.slice(0, pos[i].start) + nr + out.slice(pos[i].end);
    }
    for (const l of links.filter(l => l.mdlink)) {   // 一般 Markdown 連結 [文字](x.md)：照原本相對與否改寫
      if (Store.resolve(l.target, dir) !== oldMod) continue;
      const wasRel = !Store.modules.has(Util.pathToId(l.target));
      const t = wasRel ? Util.relPath(dir, newId) : newId;
      const nr = l.raw.replace(/\]\([^)]*\)$/, `](${t}.md)`);
      const at = out.indexOf(l.raw); if (at >= 0) out = out.slice(0, at) + nr + out.slice(at + l.raw.length);
    }
    const after = Refs.extract(out);
    if (after.length !== links.length) throw new Error(`${m.path}：改寫後連結數不同，已放棄`);
    return out;
  },
  /* 搬到別的資料夾：自己內容裡「靠同資料夾找到」的 [[…]]、相對路徑的圖片與 .md 連結都要跟著改 */
  relocate(text, oldDir, newDir) {
    const links = Refs.extract(text), wiki = links.filter(l => !l.mdlink), cands = LinkWriter.candidates(text);
    const pos = []; let c = 0;
    for (const l of wiki) { while (c < cands.length && cands[c].raw !== l.raw) c++; if (c >= cands.length) throw new Error('在原文裡找不到連結的位置'); pos.push(cands[c++]); }
    let out = text;
    for (let i = wiki.length - 1; i >= 0; i--) {
      const l = wiki[i], target = Store.resolve(l.target, oldDir);
      if (!target || Store.modules.has(Util.pathToId(l.target))) continue;   // 寫完整路徑的不用動
      if (Store.resolveStrict(l.target, newDir) === target) continue;       // 搬過去之後（不靠檔名寬鬆比對）還是找得到
      out = out.slice(0, pos[i].start) + Refs.build({ ...l, target: Store.linkTarget(target.id, newDir) }) + out.slice(pos[i].end);
    }
    // 圖片與 .md 連結的相對路徑（逐行、跳過圍欄程式碼）
    const lines = out.split('\n'); let fence = null;
    const fix = rel => { if (/^(https?:|data:|blob:|\/|#|mailto:)/i.test(rel)) return rel; return Util.relPath(newDir, Util.join(oldDir, rel)); };
    for (let i = 0; i < lines.length; i++) {
      const f = /^\s{0,3}(`{3,}|~{3,})/.exec(lines[i]);
      if (fence) { if (f && f[1][0] === fence[0] && f[1].length >= fence.length) fence = null; continue; }
      if (f) { fence = f[1]; continue; }
      lines[i] = lines[i].replace(/(!\[[^\]]*\]\()([^)\s]+)((?:\s+"[^"]*")?\))/g, (m0, a, rel, b) => a + fix(rel) + b)
                         .replace(/(^|[^!])(\[[^\]]*\]\()([^)\s]+\.md)(\))/gi, (m0, pre, a, rel, b) => pre + a + fix(rel) + b);
    }
    return lines.join('\n');
  },
  /* 標題行一起改（# 舊檔名 → # 新檔名）；有 frontmatter title 的不動 */
  retitle(text, newTitle) {
    const fm = Parse.frontmatter(text); if (fm.meta.title) return text;
    const lines = fm.rest.split('\n'); let i = 0; while (i < lines.length && !lines[i].trim()) i++;
    if (i < lines.length && /^#[ \t]+/.test(lines[i])) lines[i] = '# ' + newTitle;
    return fm.raw + lines.join('\n');
  },
  /* 抽出成模組（R47、D42）：選取的內容搬進新模組，放在「目前模組的配對資料夾」底下（D22 的世界觀）。
     不自動產生摘要（R31）；相對路徑用 relocate 改寫。回傳 { id, link }，原位置的取代由呼叫端做（編輯器）。 */
  async extract(parentMod, md, name) {
    name = Util.norm(String(name || '')).trim().replace(/\.md$/i, '');
    if (!name || /[|\[\]#/\\]/.test(name) || name.startsWith('.')) throw new Error('名稱不合法（不能空白、不能含 / | [ ] #）');
    const childId = parentMod.id + '/' + name;
    if (Store.modules.has(childId)) throw new Error('已經有同名的模組：' + childId);
    const parentDir = Util.dirname(parentMod.path), childDir = parentMod.id;
    let content = String(md || '').trim();
    if (!content) throw new Error('選取的內容是空的');
    content = this.relocate(content, parentDir, childDir);
    const text = `# ${name}\n\n${content}\n`;
    const r = await App.source.save(childId + '.md', text);
    const nm = Parse.module(text, childId + '.md'); nm.mtime = (r && r.mtime) || Date.now();
    Store.upsert(nm); Store.reindex(); App.renderSidebar(); App.updateCache();
    return { id: childId, link: '[[' + Store.linkTarget(childId, parentDir) + ']]' };
  },
  /* 併回（R47、D42）：卡片的模組內容搬回上層檔案裡連結的位置，原檔刪除。
     格式：**標題**（＋一行摘要接在冒號後；多行摘要另起段）＋內文；相對路徑改寫到上層的資料夾。 */
  async inline(parentId, refIndex, mod) {
    if (LinkWriter.pending.size) { clearTimeout(LinkWriter.timer); await LinkWriter.flush(); }
    const parent = Store.modules.get(parentId);
    if (!parent) throw new Error('找不到上層模組');
    if (refIndex == null) throw new Error('對不到檔案裡的連結位置');
    const links = Refs.cards(parent.raw), link = links[refIndex];
    const parentDir = Util.dirname(parent.path), childDir = Util.dirname(mod.path);
    if (!link || Store.resolve(link.target, parentDir) !== mod) throw new Error('檔案內容已經改變，這個連結對不上，請重新整理再試');
    const s = (mod.summary || '').trim(), b = (mod.body || '').trim();
    const head = '**' + mod.title + '**' + (s && !s.includes('\n') ? '：' + s : '');
    const pieces = [head]; if (s && s.includes('\n')) pieces.push(s); if (b) pieces.push(b);
    let inlined = pieces.join('\n\n');
    if (childDir !== parentDir) inlined = this.relocate(inlined, childDir, parentDir);
    const out = LinkWriter.replaceWith(parent.raw, refIndex, link.raw, inlined);
    const r = await App.source.save(parent.path, out);
    const np = Parse.module(out, parent.path); np.mtime = (r && r.mtime) || Date.now(); Store.upsert(np);
    await this.remove(mod);
  },
  async rename(mod, newId, { retitle = false } = {}) {
    newId = this.normalizeId(newId); if (!newId) throw new Error('名稱不合法');
    if (newId === mod.id) return { id: mod.id, updated: 0 };
    if (Store.modules.has(newId)) throw new Error('已經有同名的模組');
    const oldDir = Util.dirname(mod.path), newDir = Util.dirname(newId), newPath = newId + '.md';
    let text = mod.raw;
    if (newDir !== oldDir) text = this.relocate(text, oldDir, newDir);
    if (retitle) text = this.retitle(text, Util.basename(newId));
    const edits = this.retargetAll(mod, newId);   // 先算好，任何一個對不上就整個不做
    const r = await App.source.save(newPath, text);
    await App.source.remove(mod.path);
    Store.remove(mod.id); Memory.clearCards(mod.id); Drafts.del(mod.id);
    const nm = Parse.module(text, newPath); nm.mtime = (r && r.mtime) || Date.now(); Store.upsert(nm);
    let n = 0;
    for (const e of edits) {
      try { const r2 = await App.source.save(e.m.path, e.text); const m2 = Parse.module(e.text, e.m.path); m2.mtime = (r2 && r2.mtime) || Date.now(); Store.upsert(m2); n++; }
      catch (err) { console.warn(err); App.toast(`${e.m.path} 的連結沒改到：` + (err.message || err), true); }
    }
    Store.reindex(); App.renderSidebar(); App.updateCache();
    return { id: newId, updated: n };
  },
  async remove(mod) {
    await App.source.remove(mod.path);
    Store.remove(mod.id); Memory.clearCards(mod.id); Drafts.del(mod.id);
    Store.reindex(); App.renderSidebar(); App.updateCache();
  },
  /* 整串搬（R63）：改名／搬移時，X 的同名資料夾底下的子模組全部跟著搬，
     每一個都走 rename（自己的相對路徑改寫＋所有引用連動）。
     順序＝深的子先搬、父最後搬：每搬一個，還沒搬的那些連到它的連結會被 retarget 指到新家，
     最後搬父時再把所有已搬子模組裡「指回舊父」的連結一次修正——收斂到全部正確。 */
  async renameTree(mod, newId, opts) {
    newId = this.normalizeId(newId); if (!newId) throw new Error('名稱不合法');
    if (newId === mod.id) return { id: mod.id, moved: 0, updated: 0 };
    if (newId.startsWith(mod.id + '/')) throw new Error('不能搬進自己底下');
    const oldPrefix = mod.id + '/';
    const kids = [...Store.modules.keys()].filter(id => id.startsWith(oldPrefix))
      .sort((a, b) => b.split('/').length - a.split('/').length);   // 深的先搬
    if (Store.modules.has(newId)) throw new Error('已經有同名的模組');
    for (const kid of kids) if (Store.modules.has(newId + '/' + kid.slice(oldPrefix.length))) throw new Error('目標底下已經有同名的子模組');
    let moved = 0, updated = 0;
    for (const kid of kids) {
      const m = Store.modules.get(kid); if (!m) continue;
      const rr = await this.rename(m, newId + '/' + kid.slice(oldPrefix.length));
      moved++; updated += rr.updated;
    }
    // 搬子模組時父的連結被改寫過、Store 裡已是新物件——要拿最新的，不能用面板開啟時抓的舊參照
    const fresh = Store.modules.get(mod.id) || mod;
    const r = await this.rename(fresh, newId, opts);
    moved++; updated += r.updated;
    return { id: newId, moved, updated };
  },
};

/* ===================== Drafts：編輯中自動存草稿（R41） =====================
   每次改動後 1 秒把編輯器內容存進 localStorage（以 html 路徑為前綴）；存檔或放棄時清掉；
   下次再開同一個模組的編輯器、草稿又和檔案不同時，問要不要還原。 */
const Drafts = {
  key: id => 'draft::' + id,
  get(id) { try { return JSON.parse(Persist.pref.get(this.key(id)) || 'null'); } catch { return null; } },
  set(id, text, base) { Persist.pref.set(this.key(id), JSON.stringify({ text, t: Date.now(), base: base || 0 })); },
  del(id) { Persist.pref.del(this.key(id)); },
  clearAll() { try { const pre = Persist.key('draft::'); for (const k of Object.keys(localStorage)) if (k.startsWith(pre)) localStorage.removeItem(k); } catch {} },
};

/* ===================== Autocomplete：打 [[ 跳出模組清單（R35） =====================
   原始碼文字框與直觀編輯都用：open(rect, query, onPick) 畫在游標下面；↑↓ 選、Enter／Tab 插入、Esc 關。 */
const Autocomplete = {
  pop: null, items: [], idx: 0, onPick: null, excludeId: null,
  get visible() { return !!this.pop; },
  matches(q) {
    q = (q || '').trim().toLowerCase();
    const all = Store.list().filter(m => m.id !== this.excludeId);
    const hit = q ? all.filter(m => (m.title + ' ' + m.path).toLowerCase().includes(q)) : all;
    return hit.sort((a, b) => { const ta = a.title.toLowerCase().startsWith(q) || Util.basename(a.id).toLowerCase().startsWith(q), tb = b.title.toLowerCase().startsWith(q) || Util.basename(b.id).toLowerCase().startsWith(q); return (tb - ta) || Util.collator.compare(a.path, b.path); }).slice(0, 8);
  },
  open(rect, query, excludeId, onPick) {
    this.excludeId = excludeId; this.onPick = onPick; this.items = this.matches(query); this.idx = 0;
    if (!this.items.length) { this.close(); return; }
    if (!this.pop) { this.pop = h('div', { class: 'ac-pop', role: 'listbox' }); document.body.append(this.pop); }
    this.render();
    const W = 320, H = this.pop.offsetHeight || 200;
    let left = Math.min(rect.left, window.innerWidth - W - 8), top = rect.bottom + 4;
    if (top + H > window.innerHeight - 8) top = Math.max(8, rect.top - H - 4);
    this.pop.style.left = Math.max(8, left) + 'px'; this.pop.style.top = top + 'px';
  },
  render() {
    this.pop.innerHTML = '';
    this.items.forEach((m, i) => this.pop.append(h('div', { class: 'ac-item' + (i === this.idx ? ' on' : ''), role: 'option', onmousedown: e => { e.preventDefault(); this.idx = i; this.pick(); } },
      h('span', { class: 'ac-title', html: Util.titleHtml(m.title) }), h('span', { class: 'ac-path' }, m.path))));
  },
  move(d) { if (!this.visible) return; this.idx = (this.idx + d + this.items.length) % this.items.length; this.render(); },
  pick() { if (!this.visible) return; const m = this.items[this.idx], fn = this.onPick; this.close(); if (m && fn) fn(m); },
  close() { if (this.pop) { this.pop.remove(); this.pop = null; } this.items = []; this.onPick = null; },
  /* 共用的鍵盤處理：清單開著時攔 ↑↓ Enter Tab Esc；回傳 true 表示已處理 */
  key(e) {
    if (!this.visible) return false;
    if (e.key === 'ArrowDown') { e.preventDefault(); this.move(1); return true; }
    if (e.key === 'ArrowUp') { e.preventDefault(); this.move(-1); return true; }
    if (e.key === 'Enter' || e.key === 'Tab') { e.preventDefault(); this.pick(); return true; }
    if (e.key === 'Escape') { e.preventDefault(); this.close(); return true; }
    return false;
  },
  /* 游標前面是不是打到一半的 [[…：回傳 query（可為空字串）或 null */
  query(before) { const m = /(?:^|[^\[])\[\[([^\[\]\n|]*)$/.exec(before); return m ? m[1] : null; },
  /* 文字框裡游標的螢幕位置：用一個看不見的鏡像 div 量 */
  caretRect(ta) {
    const cs = getComputedStyle(ta), d = document.createElement('div');
    for (const k of ['fontFamily', 'fontSize', 'fontWeight', 'lineHeight', 'letterSpacing', 'paddingTop', 'paddingLeft', 'paddingRight', 'borderTopWidth', 'borderLeftWidth', 'boxSizing', 'tabSize']) d.style[k] = cs[k];
    d.style.cssText += ';position:fixed;left:0;top:0;visibility:hidden;white-space:pre-wrap;overflow-wrap:break-word;width:' + ta.clientWidth + 'px;';
    d.textContent = ta.value.slice(0, ta.selectionStart);
    const sp = document.createElement('span'); sp.textContent = '\u200b'; d.append(sp); document.body.append(d);
    const r = ta.getBoundingClientRect(), lh = parseFloat(cs.lineHeight) || 20;
    const top = r.top + sp.offsetTop - ta.scrollTop, left = r.left + sp.offsetLeft - ta.scrollLeft;
    d.remove();
    return { left, top, bottom: top + lh };
  },
};

/* ===================== Sources：各種讀（寫）來源 ===================== */
function decodeDataBlock(s) {
  const t = s.textContent;
  if (s.dataset.enc === 'base64') { const bin = atob(t.replace(/\s+/g, '')); return new TextDecoder().decode(Uint8Array.from(bin, c => c.charCodeAt(0))); }
  return t.replace(/<\\\//g, '</');
}

class EmbeddedSource {
  constructor() { this.kind = 'embedded'; this.label = document.querySelector('script[type="text/x-module"]')?.dataset.set || '內嵌筆記'; this.writable = false; }
  async load() {
    const modules = [], assets = [];
    document.querySelectorAll('script[type="text/x-module"]').forEach(s => modules.push({ path: s.dataset.path, text: decodeDataBlock(s), mtime: +s.dataset.mtime || 0 }));
    document.querySelectorAll('script[type="text/x-asset"]').forEach(s => assets.push({ path: s.dataset.path, url: `data:${s.dataset.type || 'application/octet-stream'};base64,${s.textContent.replace(/\s+/g, '')}` }));
    return { modules, assets };
  }
}

class FolderSource {
  constructor(handle) { this.kind = 'folder'; this.handle = handle; this.label = handle.name; this.writable = false; this.stamps = new Map(); this.timer = null; this.busy = false; }
  static supported() { return typeof window.showDirectoryPicker === 'function'; }
  static async pick() {
    try { return await window.showDirectoryPicker({ mode: 'readwrite', id: 'notes-modules', startIn: 'documents' }); }
    catch (e) {
      if (e && e.name === 'AbortError') return null;
      try { return await window.showDirectoryPicker({ id: 'notes-modules' }); } catch (e2) { if (e2 && e2.name === 'AbortError') return null; throw e2; }
    }
  }
  async ensurePermission(interactive) {
    const q = async mode => { try { return await this.handle.queryPermission({ mode }); } catch { return 'denied'; } };
    const r = async mode => { try { return await this.handle.requestPermission({ mode }); } catch { return 'denied'; } };
    if (await q('readwrite') === 'granted') { this.writable = true; return true; }
    if (interactive && await r('readwrite') === 'granted') { this.writable = true; return true; }
    if (await q('read') === 'granted') return true;
    if (interactive) return (await r('read')) === 'granted';
    return false;
  }
  async *walk(dir, prefix) {
    if (prefix) { try { await dir.getFileHandle('.noteignore'); return; } catch {} }   // 放了 .noteignore 的資料夾整個略過
    for await (const [name, entry] of dir.entries()) {
      if (name.startsWith('.') || name === 'node_modules') continue;
      if (entry.kind === 'file') yield { path: prefix + name, handle: entry };
      else yield* this.walk(entry, prefix + name + '/');
    }
  }
  async scan() { const out = []; for await (const f of this.walk(this.handle, '')) out.push(f); return out; }
  async load() {
    const modules = [], assets = []; this.stamps = new Map();
    for (const f of await this.scan()) {
      if (Util.isMd(f.path)) { const file = await f.handle.getFile(); this.stamps.set(f.path, Util.stamp(file)); modules.push({ path: f.path, text: await file.text(), mtime: file.lastModified }); }
      else if (Util.isImage(f.path)) assets.push({ path: f.path, handle: f.handle });
    }
    return { modules, assets };
  }
  watch(onDelta) { this.stopWatch(); this.timer = setInterval(() => { if (document.visibilityState === 'visible' && !this.busy) this.check(onDelta); }, CONFIG.pollMs); }
  stopWatch() { if (this.timer) clearInterval(this.timer); this.timer = null; }
  async check(onDelta) {
    this.busy = true;
    try {
      const seen = new Set(), upserts = [];
      for (const f of await this.scan()) {
        if (!Util.isMd(f.path)) continue;
        seen.add(f.path);
        const file = await f.handle.getFile(); const st = Util.stamp(file);
        if (this.stamps.get(f.path) !== st) { this.stamps.set(f.path, st); upserts.push({ path: f.path, text: await file.text(), mtime: file.lastModified }); }
      }
      const removed = [...this.stamps.keys()].filter(p => !seen.has(p)); removed.forEach(p => this.stamps.delete(p));
      if (upserts.length || removed.length) onDelta({ upserts, removed });
    } catch (e) { console.warn('檢查檔案變動時發生問題', e); }
    finally { this.busy = false; }
  }
  async save(path, text) {
    if (!this.writable) throw new Error('沒有這個資料夾的寫入權限');
    const parts = path.split('/'); let dir = this.handle;
    for (const p of parts.slice(0, -1)) dir = await dir.getDirectoryHandle(p, { create: true });
    const fh = await dir.getFileHandle(parts[parts.length - 1], { create: true });
    const w = await fh.createWritable(); await w.write(text); await w.close();
    const file = await fh.getFile(); this.stamps.set(path, Util.stamp(file));
    return { mtime: file.lastModified, size: file.size };
  }
  async saveBinary(path, blob) {
    if (!this.writable) throw new Error('沒有這個資料夾的寫入權限');
    const parts = path.split('/'); let dir = this.handle;
    for (const p of parts.slice(0, -1)) dir = await dir.getDirectoryHandle(p, { create: true });
    const fh = await dir.getFileHandle(parts[parts.length - 1], { create: true });
    const w = await fh.createWritable(); await w.write(blob); await w.close();
    return { handle: fh };
  }
  /* 刪除一個檔案（改名／搬移＝先 save 新檔再 remove 舊檔；R34） */
  async remove(path) {
    if (!this.writable) throw new Error('沒有這個資料夾的寫入權限');
    const parts = path.split('/'); let dir = this.handle;
    for (const p of parts.slice(0, -1)) dir = await dir.getDirectoryHandle(p);
    await dir.removeEntry(parts[parts.length - 1]);
    this.stamps.delete(path);
  }
}

class FilesSource {
  constructor(entries, label) { this.kind = 'files'; this.entries = entries; this.label = label; this.writable = false; }
  async load() {
    const modules = [], assets = [];
    for (const e of this.entries) {
      if (Util.isMd(e.path)) modules.push({ path: e.path, text: await e.file.text(), mtime: e.file.lastModified });
      else if (Util.isImage(e.path)) assets.push({ path: e.path, file: e.file });
    }
    return { modules, assets };
  }
  static stripRoot(entries) {
    const firsts = new Set(entries.map(e => e.path.split('/')[0]));
    if (entries.length && firsts.size === 1 && entries.every(e => e.path.includes('/'))) {
      const root = [...firsts][0];
      return { root, entries: entries.map(e => ({ path: e.path.slice(root.length + 1), file: e.file })) };
    }
    return { root: null, entries };
  }
  static async fromDrop(dt) {
    const items = [...dt.items].map(i => i.webkitGetAsEntry && i.webkitGetAsEntry()).filter(Boolean);
    const out = [];
    const walk = async (entry, prefix) => {
      if (entry.isFile) { const file = await new Promise((res, rej) => entry.file(res, rej)); out.push({ path: prefix + entry.name, file }); }
      else if (entry.isDirectory) {
        if (entry.name.startsWith('.') || entry.name === 'node_modules') return;
        const reader = entry.createReader(); let batch; const all = [];
        do { batch = await new Promise((res, rej) => reader.readEntries(res, rej)); all.push(...batch); } while (batch.length);
        if (all.some(e => e.name === '.noteignore')) return;
        for (const e of all) await walk(e, prefix + entry.name + '/');
      }
    };
    if (items.length) for (const e of items) await walk(e, '');
    else for (const f of dt.files) out.push({ path: f.name, file: f });
    return this.stripRoot(out);
  }
  static fromInput(files) {
    let out = [...files].map(f => ({ path: (f.webkitRelativePath || f.name).replace(/\\/g, '/'), file: f }));
    const ignored = out.filter(e => Util.basename(e.path) === '.noteignore').map(e => Util.dirname(e.path) + '/');
    out = out.filter(e => !e.path.split('/').some(seg => seg.startsWith('.') || seg === 'node_modules') && !ignored.some(d => e.path.startsWith(d)));
    return this.stripRoot(out);
  }
}

class CacheSource {
  constructor(rec) { this.kind = 'cache'; this.rec = rec; this.label = `${rec.label || '上次匯入'}（快取）`; this.writable = false; this.when = rec.when; this.from = rec.kind || 'files'; }
  async load() { return { modules: this.rec.modules, assets: (this.rec.assets || []).map(a => ({ path: a.path, file: a.blob })) }; }
}

class HttpSource {
  constructor(url, man) {
    this.kind = 'http'; this.url = url; this.man = man; this.writable = !!man.writable; this.github = man.github || null;
    this.label = man.writable ? '本機伺服器' : (man.github ? 'GitHub Pages' : '網站');
    this.stamps = new Map(); this.timer = null; this.busy = false;
    this.token = null; this.shas = null; this.pending = new Map();   // GitHub 直接存檔（R43、D39）
    if (this.github && !this.writable) { const t = Persist.pref.get('ghToken'); if (t) this.enableToken(t); }
  }
  /* ---- GitHub 直接存檔（R43、D39）：存檔＝用 token 走 GitHub Contents API commit ---- */
  enableToken(token) { this.token = token; this.writable = true; this.writeThrough = false; this.label = 'GitHub（直接編輯）'; }
  disableToken() { this.token = null; this.writable = false; this.writeThrough = undefined; this.label = 'GitHub Pages'; Persist.pref.del('ghToken'); }
  ghPath(path) { const d = (this.github.dir || '').replace(/^\/|\/$/g, ''); return (d ? d + '/' : '') + path; }
  ghApi(path) { return `https://api.github.com/repos/${this.github.owner}/${this.github.repo}/contents/${Util.encodePath(this.ghPath(path))}`; }
  async gh(url, opt = {}) {
    const r = await fetch(url, { ...opt, headers: { Accept: 'application/vnd.github+json', Authorization: 'Bearer ' + this.token, ...(opt.headers || {}) } });
    if (r.status === 401) throw new Error('GitHub token 無效或過期（來源選單可更換）');
    const writing = opt.method === 'PUT' || opt.method === 'DELETE';
    if (writing && (r.status === 403 || r.status === 404)) throw new Error('GitHub 拒絕寫入（' + r.status + '）。最常見的原因：token 的 Contents 權限只有讀。到 github.com/settings/personal-access-tokens 點那把 token → Permissions → Contents 改成「Read and write」→ Update，然後直接再按一次儲存（token 那串不變、不用重貼）。');
    return r;
  }
  /* 驗證 token 能寫這個倉庫 */
  async verifyToken(token) {
    const r = await fetch(`https://api.github.com/repos/${this.github.owner}/${this.github.repo}`, { headers: { Accept: 'application/vnd.github+json', Authorization: 'Bearer ' + token } });
    if (r.status === 401) throw new Error('token 無效（貼錯或已過期）');
    if (!r.ok) throw new Error('讀不到倉庫（' + r.status + '）——fine-grained token 記得把 Repository access 選到這個倉庫');
    const j = await r.json();
    if (!j.permissions || !j.permissions.push) throw new Error('這個 token 沒有寫入權限——Permissions 要給 Contents: Read and write');
    return true;
  }
  /* 整棵樹的 sha 一次抓齊（改檔要帶舊 sha） */
  async ensureShas(force) {
    if (this.shas && !force) return;
    const r = await this.gh(`https://api.github.com/repos/${this.github.owner}/${this.github.repo}/git/trees/${encodeURIComponent(this.github.branch || 'main')}?recursive=1`);
    if (!r.ok) throw new Error('讀取檔案清單失敗（' + r.status + '）');
    const j = await r.json();
    this.shas = new Map();
    for (const it of j.tree || []) if (it.type === 'blob') this.shas.set(it.path, it.sha);
  }
  static b64(bytes) { let out = ''; for (let i = 0; i < bytes.length; i += 0x8000) out += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000)); return btoa(out); }
  async ghPut(path, bytes, msg) {
    await this.ensureShas();
    const full = this.ghPath(path);
    const body = { message: msg, content: HttpSource.b64(bytes), branch: this.github.branch || 'main' };
    if (this.shas.has(full)) body.sha = this.shas.get(full);
    let r = await this.gh(this.ghApi(path), { method: 'PUT', body: JSON.stringify(body) });
    if (r.status === 409 || r.status === 422) {   // sha 過期（別處剛改過）→ 重抓一次再試
      await this.ensureShas(true);
      if (this.shas.has(full)) body.sha = this.shas.get(full); else delete body.sha;
      r = await this.gh(this.ghApi(path), { method: 'PUT', body: JSON.stringify(body) });
    }
    if (!r.ok) throw new Error('GitHub 回應 ' + r.status);
    const j = await r.json();
    if (j.content && j.content.sha) this.shas.set(full, j.content.sha);
    this.pending.set(path, { t: Date.now() });   // 部署跟上之前，輪詢不要用舊資料蓋掉
    Persist.pref.set('ghSavedAt', String(Date.now()));   // 重新整理後若部署還沒跟上，要提示（D39）
    return j;
  }
  static normalize(d) { return Array.isArray(d) ? { modules: d } : { modules: d.modules || [], writable: !!d.writable, github: d.github || null, generated: d.generated || 0 }; }
  static async detect() {
    if (!/^https?:$/.test(location.protocol)) return null;
    for (const url of ['api/modules', 'modules.json']) {
      try { const r = await fetch(url, { cache: 'no-cache' }); if (!r.ok) continue; const ct = r.headers.get('content-type') || ''; if (!/json/.test(ct) && url === 'api/modules') continue; return new HttpSource(url, this.normalize(await r.json())); } catch {}
    }
    return null;
  }
  async text(path) { const r = await fetch(Util.encodePath(path), { cache: 'no-store' }); if (!r.ok) throw new Error(`${r.status} ${path}`); return await r.text(); }
  async load() {
    const modules = await Promise.all(this.man.modules.map(async m => { this.stamps.set(m.path, `${m.mtime || 0}:${m.size || 0}`); return { path: m.path, text: m.text != null ? m.text : await this.text(m.path), mtime: m.mtime || 0 }; }));
    return { modules, assets: [] };
  }
  watch(onDelta) {
    this.stopWatch();
    this.timer = setInterval(async () => {
      if (document.visibilityState !== 'visible' || this.busy) return;
      this.busy = true;
      try {
        const r = await fetch(this.url, { cache: 'no-cache' }); if (!r.ok) return;
        const man = HttpSource.normalize(await r.json()); const seen = new Set(), upserts = [];
        for (const [p, info] of this.pending) if (man.generated && man.generated >= info.t) this.pending.delete(p);   // 部署已包含這筆變更
        for (const m of man.modules) {
          if (this.pending.has(m.path)) { if (!this.pending.get(m.path).removed) seen.add(m.path); continue; }   // 剛存／剛刪的：等部署跟上
          seen.add(m.path); const st = `${m.mtime || 0}:${m.size || 0}`;
          if (this.stamps.get(m.path) !== st) { this.stamps.set(m.path, st); upserts.push({ path: m.path, text: m.text != null ? m.text : await this.text(m.path), mtime: m.mtime || 0 }); }
        }
        const removed = [...this.stamps.keys()].filter(p => !seen.has(p) && !this.pending.has(p)); removed.forEach(p => this.stamps.delete(p));
        this.man = man;
        if (upserts.length || removed.length) onDelta({ upserts, removed });
      } catch (e) { console.warn(e); } finally { this.busy = false; }
    }, this.writable ? CONFIG.pollMs : CONFIG.staticPollMs);
  }
  stopWatch() { if (this.timer) clearInterval(this.timer); this.timer = null; }
  async save(path, text) {
    if (this.token) {
      await this.ghPut(path, new TextEncoder().encode(text), '更新 ' + path);
      const mtime = Date.now(); this.stamps.set(path, `${mtime}:${text.length}`);
      return { mtime };
    }
    const r = await fetch('api/file?path=' + encodeURIComponent(path), { method: 'PUT', headers: { 'Content-Type': 'text/markdown; charset=utf-8' }, body: text });
    if (!r.ok) throw new Error('伺服器回應 ' + r.status);
    const j = await r.json().catch(() => ({}));
    if (j.mtime) this.stamps.set(path, `${j.mtime}:${j.size || 0}`);
    return j;
  }
  async saveBinary(path, blob) {
    if (this.token) { await this.ghPut(path, new Uint8Array(await blob.arrayBuffer()), '新增 ' + path); return {}; }
    const r = await fetch('api/file?path=' + encodeURIComponent(path), { method: 'PUT', headers: { 'Content-Type': blob.type || 'application/octet-stream' }, body: blob });
    if (!r.ok) throw new Error('伺服器回應 ' + r.status);
    return await r.json().catch(() => ({}));
  }
  async remove(path) {
    if (this.token) {
      await this.ensureShas();
      const full = this.ghPath(path); const sha = this.shas.get(full);
      if (sha) {
        const r = await this.gh(this.ghApi(path), { method: 'DELETE', body: JSON.stringify({ message: '刪除 ' + path, sha, branch: this.github.branch || 'main' }) });
        if (!r.ok) throw new Error('GitHub 回應 ' + r.status);
        this.shas.delete(full);
      }
      this.stamps.delete(path); this.pending.set(path, { t: Date.now(), removed: true });
      Persist.pref.set('ghSavedAt', String(Date.now()));
      return {};
    }
    const r = await fetch('api/file?path=' + encodeURIComponent(path), { method: 'DELETE' });
    if (!r.ok) throw new Error('伺服器回應 ' + r.status);
    this.stamps.delete(path);
    return await r.json().catch(() => ({}));
  }
  editUrl(path) {
    if (!this.github || !this.github.owner || !this.github.repo) return null;
    const g = this.github; const dir = g.dir ? g.dir.replace(/^\/|\/$/g, '') + '/' : '';
    return `https://github.com/${g.owner}/${g.repo}/edit/${g.branch || 'main'}/${dir}${Util.encodePath(path)}`;
  }
}

/* ===================== Theme ===================== */
const Theme = {
  init() { const t = Persist.pref.get('theme'); if (t === 'dark' || t === 'light') document.documentElement.dataset.theme = t; },
  toggle() {
    const root = document.documentElement;
    const dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    root.dataset.theme = dark ? 'light' : 'dark'; Persist.pref.set('theme', root.dataset.theme);
  },
};

const Style = {
  init() {
    const saved = Persist.pref.get('style'); const key = (saved && CONFIG.styles[saved]) ? saved : CONFIG.defaultStyle;
    this.set(key, false);
    const sel = document.getElementById('styleSel');
    if (sel) {
      sel.innerHTML = ''; for (const [k, name] of Object.entries(CONFIG.styles)) sel.append(h('option', { value: k }, name));
      sel.value = key; sel.hidden = !CONFIG.showStylePicker;
      sel.addEventListener('change', () => this.set(sel.value, true));
    }
  },
  set(key, persist) { document.documentElement.dataset.style = key; if (persist) Persist.pref.set('style', key); const sel = document.getElementById('styleSel'); if (sel && sel.value !== key) sel.value = key; },
};

/* ===================== Wysi：所見即所得編輯（R25、D23） =====================
   原理：把 Markdown 用同一套 marked 渲染成 HTML 放進 contenteditable；[[模組]]、數學式、圖片變成
   不可在裡面打字的「原子」（data-md 保存原文）；存檔時把 HTML 走訪一遍序列化回 Markdown。
   只用瀏覽器內建的 execCommand，不引入編輯器框架。 */
const Wysi = {
  BLOCK: /^(P|DIV|H[1-6]|UL|OL|LI|BLOCKQUOTE|PRE|HR|TABLE|THEAD|TBODY|TR|FIGURE|SECTION|ARTICLE|HEADER|FOOTER|DL|DT|DD)$/,
  isAtom: el => !!(el && el.classList && el.classList.contains('wy-atom')),
  isBlockAtom: el => Wysi.isAtom(el) && el.tagName === 'DIV',

  /* ---------- Markdown → 可編輯 HTML ---------- */
  field(md, basePath, placeholder) {
    const el = h('div', { class: 'wy-field md', contenteditable: 'true', spellcheck: 'false', 'data-placeholder': placeholder || '' });
    el.innerHTML = MD.render(md || '');
    this.hydrate(el, basePath);
    return el;
  },
  hydrate(root, basePath) {
    for (const ph of [...root.querySelectorAll('.mod-ph, .mod-ph-inline')]) ph.replaceWith(this.atomFromRaw(ph.dataset.raw || '', ph.classList.contains('mod-ph'), basePath));
    for (const m of root.querySelectorAll('.math-block, .math-inline')) { m.classList.add('wy-atom', 'wy-math'); m.contentEditable = 'false'; m.dataset.md = m.dataset.raw || ''; m.title = '點一下修改數學式'; }
    for (const img of root.querySelectorAll('img[src]')) {
      const src = img.getAttribute('src') || ''; if (/^(https?:|data:|blob:)/i.test(src)) continue;
      let dec = src; try { dec = decodeURIComponent(src); } catch {}
      img.dataset.md = dec; Store.assetUrl(dec, basePath).then(url => { if (url) img.src = url; });
    }
    for (const cb of root.querySelectorAll('input[type="checkbox"]')) { cb.disabled = false; cb.contentEditable = 'false'; }
    for (const a of root.querySelectorAll('a[href]')) a.title = a.getAttribute('href');
    this.tidy(root);
  },
  /* 區塊原子前後要有可以放游標的段落，否則游標進不去；序列化時空段落會被丟掉 */
  tidy(root) {
    const spacer = () => h('p', {}, h('br'));
    for (const a of [...root.querySelectorAll('.wy-atom')]) {
      if (!this.isBlockAtom(a)) continue;
      if (!a.nextSibling || this.isBlockAtom(a.nextSibling)) a.after(spacer());
    }
    if (!root.lastElementChild || this.isBlockAtom(root.lastElementChild)) root.append(spacer());
    if (!root.firstChild) root.append(spacer());
  },
  atomFromRaw(raw, block, basePath) {
    const m = /^(!?)\[\[([^\[\]\n`]+?)\]\]$/.exec(raw.trim());
    const ref = m ? Refs.parse(m[2], !!m[1]) : { target: raw, mode: 1, label: null };
    const mod = Store.resolve(ref.target, basePath);
    const name = ref.label || (mod ? mod.title : ref.target);
    const modeName = ['', '標題', '摘要', '全文'][ref.mode] || '標題';
    const el = h(block ? 'div' : 'span', { class: 'wy-atom ' + (block ? 'wy-card' : 'wy-chip') + (mod ? '' : ' missing'), contenteditable: 'false', dataset: { md: raw.trim() }, title: '模組連結：點一下修改' });
    el.append(h('span', { class: 'wy-atom-icon', html: ICON.chev }), h('span', { class: 'wy-atom-name', html: Util.titleHtml(name) }));
    if (block) el.append(h('span', { class: 'wy-atom-mode' }, modeName + (ref.style === 'flat' ? ' · 扁平' : ref.style === 'group' ? ' · 群組縮排' : '')));
    else if (ref.style === 'flat') el.classList.add('flat');
    return el;
  },
  mathAtom(tex, block) {
    const raw = block ? `$$\n${tex.trim()}\n$$` : `$${tex.trim()}$`;
    const html = MD.render(raw);
    const tmp = h('div', { html }); const el = tmp.querySelector('.math-block, .math-inline');
    if (!el) return null;
    el.classList.add('wy-atom', 'wy-math'); el.contentEditable = 'false'; el.dataset.md = raw; el.title = '點一下修改數學式';
    return el;
  },

  /* ---------- HTML → Markdown ---------- */
  toMarkdown(root) { return this.blocks(root).join('\n\n').replace(/\n{3,}/g, '\n\n').trim(); },
  blocks(container) {
    const out = []; let run = [];
    const flush = () => { if (!run.length) return; const t = this.inlineRun(run); if (t.trim()) out.push(this.protectLines(t)); run = []; };
    for (const node of container.childNodes) {
      if (node.nodeType === 3) { if (node.nodeValue.trim() || run.length) run.push(node); continue; }
      if (node.nodeType !== 1) continue;
      if (this.isBlockAtom(node) || node.tagName === 'IMG' && !run.length) { flush(); out.push(this.isBlockAtom(node) ? node.dataset.md : this.img(node)); continue; }
      if (!this.BLOCK.test(node.tagName) || (node.tagName === 'DIV' && !this.hasBlockChild(node) && !this.isBlockAtom(node))) {
        if (node.tagName === 'DIV') { flush(); const t = this.inline(node); if (t.trim()) out.push(this.protectLines(t)); continue; }   // contenteditable 的 <div> = 一段
        if (node.tagName === 'BR' && !run.length) continue;
        run.push(node); continue;
      }
      flush();
      const md = this.block(node); if (md != null && md !== '') out.push(md);
    }
    flush();
    return out;
  },
  hasBlockChild(el) { return [...el.children].some(c => this.BLOCK.test(c.tagName) || this.isBlockAtom(c)); },
  block(el) {
    const tag = el.tagName;
    if (/^H[1-6]$/.test(tag)) { const t = this.inline(el).replace(/\s*\n\s*/g, ' ').trim(); return t ? '#'.repeat(+tag[1]) + ' ' + t : null; }
    if (tag === 'P') { const t = this.inline(el); return t.trim() ? this.protectLines(t) : null; }
    if (tag === 'DIV' || tag === 'SECTION' || tag === 'ARTICLE' || tag === 'FIGURE' || tag === 'HEADER' || tag === 'FOOTER' || tag === 'DL' || tag === 'DD' || tag === 'DT') { const parts = this.blocks(el); return parts.length ? parts.join('\n\n') : null; }
    if (tag === 'UL' || tag === 'OL') return this.list(el);
    if (tag === 'BLOCKQUOTE') { const parts = this.blocks(el); return parts.length ? parts.join('\n\n').split('\n').map(l => ('> ' + l).replace(/\s+$/, '')).join('\n') : null; }
    if (tag === 'PRE') {
      const code = el.querySelector('code'); const lang = ((code && code.className.match(/language-([\w+-]+)/)) || [])[1] || '';
      const text = this.preText(code || el).replace(/\n+$/, '');
      const fence = '`'.repeat(Math.max(3, ((text.match(/`+/g) || []).reduce((m, s) => Math.max(m, s.length), 0)) + 1));
      return `${fence}${lang}\n${text}\n${fence}`;
    }
    if (tag === 'HR') return '---';
    if (tag === 'TABLE') return this.table(el);
    if (tag === 'LI') return this.list(h('ul', {}, el.cloneNode(true)));
    if (tag === 'THEAD' || tag === 'TBODY' || tag === 'TR') return this.table(h('table', {}, el.cloneNode(true)));
    return this.protectLines(this.inline(el));
  },
  preText(el) {
    let s = '';
    const walk = n => { for (const c of n.childNodes) { if (c.nodeType === 3) s += c.nodeValue; else if (c.nodeType === 1) { if (c.tagName === 'BR') s += '\n'; else { if (this.BLOCK.test(c.tagName) && s && !s.endsWith('\n')) s += '\n'; walk(c); if (this.BLOCK.test(c.tagName) && !s.endsWith('\n')) s += '\n'; } } } };
    walk(el); return s.replace(/\u00a0/g, ' ');
  },
  list(el, indent = '') {
    const ordered = el.tagName === 'OL'; let n = parseInt(el.getAttribute('start') || '1', 10) || 1;
    const loose = [...el.children].some(li => li.tagName === 'LI' && li.querySelector(':scope > p'));   // 原檔項目之間有空行（marked 的 loose list）→ 照樣留空行
    const lines = [];
    for (const li of el.children) {
      if (li.tagName === 'UL' || li.tagName === 'OL') { lines.push(this.list(li, indent + '  ')); continue; }   // 有些瀏覽器把巢狀清單直接放在 ul 底下
      if (li.tagName !== 'LI') continue;
      if (loose && lines.length) lines.push('');
      const marker = ordered ? `${n++}. ` : '- ', pad = ' '.repeat(marker.length);
      let check = '';
      const cb = li.querySelector(':scope > input[type="checkbox"], :scope > p > input[type="checkbox"]');
      if (cb && this.isFirstContent(cb, li)) check = cb.checked ? '[x] ' : '[ ] ';
      const parts = this.blocks(li).filter(p => p.trim());
      let first = parts.length && !this.isListMd(parts[0]) ? parts.shift() : '';   // 項目的第一塊（文字或原子卡片）直接接在記號後面：- [[x|扁平]]
      const head = indent + marker + check + first.split('\n').join('\n' + indent + pad);
      lines.push(head.replace(/\s+$/, ''));
      for (const p of parts) {
        if (this.isListMd(p)) lines.push(p.split('\n').map(l => indent + pad + l).join('\n'));
        else if (!loose && /^(>|```|~~~|#{1,6} |---$)/.test(p)) lines.push(p.split('\n').map(l => l ? indent + pad + l : l).join('\n'));   // 緊湊清單裡的引言、程式碼、標題可直接接在項目下
        else lines.push('', p.split('\n').map(l => l ? indent + pad + l : l).join('\n'));
      }
    }
    return lines.join('\n');
  },
  isFirstContent(node, li) { for (const c of li.childNodes) { if (c === node || (c.nodeType === 1 && c.contains(node))) return true; if (c.nodeType === 3 ? c.nodeValue.trim() : c.tagName !== 'BR') return false; } return false; },
  isListMd: s => /^\s*(?:[-*+] |\d+\. )/.test(s),
  isAtomMd: s => /^!?\[\[/.test(s) || /^\$\$/.test(s),
  table(el) {
    const rows = [...el.querySelectorAll('tr')].map(tr => [...tr.children].map(td => this.inline(td).replace(/\s*\n\s*/g, '<br>').replace(/\|/g, '\\|').trim()));
    if (!rows.length) return null;
    const w = Math.max(...rows.map(r => r.length));
    const norm = r => { while (r.length < w) r.push(''); return '| ' + r.join(' | ') + ' |'; };
    return [norm(rows[0]), '|' + '---|'.repeat(w), ...rows.slice(1).map(norm)].join('\n');
  },
  /* 行內：走訪子節點 */
  inlineRun(nodes) { const tmp = h('span'); for (const n of nodes) tmp.append(n.cloneNode(true)); return this.inline(tmp); },
  inline(el) {
    let s = '';
    for (const c of el.childNodes) {
      if (c.nodeType === 3) { s += this.text(c.nodeValue, c); continue; }
      if (c.nodeType !== 1) continue;
      const tag = c.tagName, st = c.style || {};
      if (this.isAtom(c)) { s += this.isBlockAtom(c) ? `\n\n${c.dataset.md}\n\n` : c.dataset.md; continue; }
      if (tag === 'BR') { s += '\n'; continue; }
      if (tag === 'IMG') { s += this.img(c); continue; }
      if (tag === 'INPUT') continue;
      if (tag === 'SCRIPT' || tag === 'STYLE') continue;
      const inner = () => this.inline(c);
      if (tag === 'STRONG' || tag === 'B' || (tag === 'SPAN' && /^(bold|[6-9]00)$/.test(st.fontWeight))) { s += this.wrap('**', inner()); continue; }
      if (tag === 'EM' || tag === 'I' || (tag === 'SPAN' && st.fontStyle === 'italic')) { s += this.wrap('*', inner()); continue; }
      if (tag === 'DEL' || tag === 'S' || tag === 'STRIKE' || (tag === 'SPAN' && /line-through/.test(st.textDecorationLine || st.textDecoration))) { s += this.wrap('~~', inner()); continue; }
      if (tag === 'U' || (tag === 'SPAN' && /underline/.test(st.textDecorationLine || st.textDecoration))) { s += this.tagWrap('u', inner()); continue; }
      if (tag === 'MARK') { s += this.tagWrap('mark', inner()); continue; }
      if (tag === 'SUP' || tag === 'SUB' || tag === 'KBD') { s += this.tagWrap(tag.toLowerCase(), inner()); continue; }
      if (tag === 'CODE') { const t = this.preText(c).replace(/\n/g, ' '); if (!t) continue; const run = Math.max(0, ...(t.match(/`+/g) || []).map(x => x.length)); const f = '`'.repeat(run + 1); s += `${f}${/^`|`$/.test(t) ? ' ' + t + ' ' : t}${f}`; continue; }
      if (tag === 'A') { const href = c.getAttribute('href') || ''; const t = inner().trim(); if (!href) { s += t; continue; } s += (!t || t === href) ? href : `[${t}](${href})`; continue; }
      if (this.BLOCK.test(tag)) { const md = this.block(c); if (md) s += (s && !s.endsWith('\n') ? '\n' : '') + md + '\n'; continue; }
      s += inner();   // span、font 與其他：透明
    }
    return s;
  },
  img(c) { const src = c.dataset.md || c.getAttribute('src') || ''; const alt = (c.getAttribute('alt') || '').replace(/[\[\]]/g, ''); return `![${alt}](${src})`; },
  wrap(mark, inner) {
    const lead = /^\s/.test(inner) ? ' ' : '', trail = /\s$/.test(inner) ? ' ' : '', core = inner.trim();
    if (!core) return inner ? ' ' : '';
    return `${lead}${mark}${core}${mark}${trail}`;
  },
  tagWrap(tag, inner) { const lead = /^\s/.test(inner) ? ' ' : '', trail = /\s$/.test(inner) ? ' ' : '', core = inner.trim(); return core ? `${lead}<${tag}>${core}</${tag}>${trail}` : (inner ? ' ' : ''); },
  /* 文字：壓掉多餘空白、把會被當成語法的字元加上反斜線 */
  text(t, node) {
    if (node && node.parentElement && node.parentElement.closest('pre, code')) return t;
    t = t.replace(/\u00a0/g, ' ').replace(/[ \t\r\n]+/g, ' ');
    return t.replace(/[\\`*\[\]$]/g, '\\$&').replace(/~~/g, '\\~\\~').replace(/(^|[^\w])_/g, '$1\\_').replace(/_(?=[^\w]|$)/g, '\\_').replace(/<(?=[a-zA-Z\/!])/g, '\\<');
  },
  /* 段落裡每一行的開頭若像標題、清單、引言、分隔線等區塊語法，補上反斜線（原子寫出的 [[…]]、$$ 行不碰） */
  protectLines(t) {
    return t.split('\n').map(l => {
      const s = l.replace(/^\s+/, '');
      if (/^!?\[\[.+\]\]$/.test(s) || /^\$\$/.test(s)) return s;
      return /^(#{1,6}\s|#{1,6}$|[-+*]\s|[-+*]$|\d+[.)]\s|>|---|\*\*\*|___|```|~~~|\|)/.test(s) ? '\\' + s : s;
    }).join('\n').trim();
  },

  /* ---------- 編輯動作 ---------- */
  exec(cmd, val) { document.execCommand(cmd, false, val == null ? undefined : val); },
  currentBlock(field) {
    const sel = window.getSelection(); if (!sel.rangeCount) return null;
    let n = sel.getRangeAt(0).startContainer; if (n.nodeType === 3) n = n.parentNode;
    while (n && n !== field && !(this.BLOCK.test(n.tagName) && n.tagName !== 'LI')) n = n.parentNode;
    return n && n !== field ? n : null;
  },
  inList(field) { const sel = window.getSelection(); if (!sel.rangeCount) return null; let n = sel.getRangeAt(0).startContainer; if (n.nodeType === 3) n = n.parentNode; const li = n.closest && n.closest('li'); return li && field.contains(li) ? li : null; },
  /* 用 <mark>／<code> 這類 execCommand 沒有的標籤包住選取範圍；已經在裡面就解除 */
  toggleTag(field, tag) {
    const sel = window.getSelection(); if (!sel.rangeCount) return;
    const range = sel.getRangeAt(0);
    let n = range.commonAncestorContainer; if (n.nodeType === 3) n = n.parentNode;
    const inside = n.closest && n.closest(tag);
    if (inside && field.contains(inside)) { const frag = document.createDocumentFragment(); while (inside.firstChild) frag.append(inside.firstChild); inside.replaceWith(frag); return; }
    if (range.collapsed) return;
    const wrapper = document.createElement(tag);
    try { range.surroundContents(wrapper); }
    catch { const frag = range.extractContents(); wrapper.append(frag); range.insertNode(wrapper); }
    sel.removeAllRanges(); const r = document.createRange(); r.selectNodeContents(wrapper); sel.addRange(r);
  },
  insertHtml(html) { this.exec('insertHTML', html); },
  insertNode(node) {
    const sel = window.getSelection(); if (!sel.rangeCount) return;
    const range = sel.getRangeAt(0); range.deleteContents(); range.insertNode(node);
    range.setStartAfter(node); range.collapse(true); sel.removeAllRanges(); sel.addRange(range);
  },
  insertBlockNode(field, node) {
    const blk = this.currentBlock(field);
    if (blk && blk.parentNode === field) {
      if (!blk.textContent.trim() && !blk.querySelector('img, .wy-atom')) blk.replaceWith(node); else blk.after(node);
    } else field.append(node);
    const p = h('p', {}, h('br')); node.after(p);
    const sel = window.getSelection(), r = document.createRange(); r.setStart(p, 0); r.collapse(true); sel.removeAllRanges(); sel.addRange(r);
  },
  /* 行首打 「- 」「1. 」「# 」「> 」「[] 」自動變格式 */
  autoformat(field) {
    const sel = window.getSelection(); if (!sel.rangeCount || !sel.isCollapsed) return false;
    const blk = this.currentBlock(field); if (!blk || !/^(P|DIV)$/.test(blk.tagName)) return false;
    const r = sel.getRangeAt(0); const pre = document.createRange(); pre.setStart(blk, 0); pre.setEnd(r.startContainer, r.startOffset);
    const before = pre.toString().replace(/\u00a0/g, ' ');
    const m = /^(-|\*|\+|1\.|#|##|###|>|\[\]|\[ \])\s$/.exec(before); if (!m) return false;
    sel.removeAllRanges(); sel.addRange(pre); this.exec('delete');
    const k = m[1];
    if (k === '-' || k === '*' || k === '+') this.exec('insertUnorderedList');
    else if (k === '1.') this.exec('insertOrderedList');
    else if (k === '>') this.exec('formatBlock', 'blockquote');
    else if (k[0] === '#') this.exec('formatBlock', 'h' + (k.length + 1));
    else if (k[0] === '[') { this.exec('insertUnorderedList'); const li = this.inList(field); if (li) li.prepend(h('input', { type: 'checkbox', contenteditable: 'false' }), ' '); }
    return true;
  },
  placeCaretAtEnd(el) { const sel = window.getSelection(), r = document.createRange(); r.selectNodeContents(el); r.collapse(false); sel.removeAllRanges(); sel.addRange(r); el.focus(); },
};

/* ===================== Editor ===================== */
const Editor = {
  MODES: ['wysiwyg', 'source', 'split'],   // 直觀編輯｜原始碼｜並排（R29）
  mod: null, dirty: false, ta: null, preview: null, mode: 'source', fields: null, savedRange: null,
  side: 'source',      // 並排模式：最近在哪一邊打字（'source'｜'wysi'），存檔與同步都以那一邊為準
  _toSource: null,     // 並排模式：直觀 → 原始碼的同步（renderSplit 設定）
  get open() { return !!this.mod; },
  start(mod) {
    if (this.mod && this.dirty && !confirm('目前的修改還沒儲存，要放棄嗎？')) return false;
    const pref = Persist.pref.get('editMode');
    this.mode = App.canEdit() ? (this.MODES.includes(pref) ? pref : CONFIG.editorDefault) : 'source';   // 唯讀只有原始碼（檢視）
    this.mod = mod; this.dirty = false; this.fields = null; this.ta = null; App.renderEditor();
    this.offerDraft(mod);
    return true;
  },
  /* 草稿（R41）：上次編輯到一半沒存（關掉分頁、當機）→ 問要不要還原 */
  offerDraft(mod) {
    if (!App.canEdit()) return;
    const d = Drafts.get(mod.id); if (!d || typeof d.text !== 'string' || d.text === mod.raw) { if (d) Drafts.del(mod.id); return; }
    const when = Util.fmtTime(d.t), newer = mod.mtime && d.base && mod.mtime > d.base;
    App.showBanner(`有 ${when} 自動儲存、還沒存進檔案的草稿${newer ? '（檔案在那之後也被改過）' : ''}。`, '還原草稿', () => { this.load(d.text); this.dirty = true; App.hideBanner(); }, ['丟棄草稿', () => { Drafts.del(mod.id); App.hideBanner(); }]);
  },
  autosave: Util.debounce(() => { const E = Editor; if (!E.open || !App.canEdit()) return; const t = E.text(); if (t === E.mod.raw) { Drafts.del(E.mod.id); return; } Drafts.set(E.mod.id, t, E.mod.mtime); }, 1000),
  cancel() { if (this.dirty && !confirm('放棄這次的修改？')) return; if (this.mod) Drafts.del(this.mod.id); this.mod = null; this.dirty = false; this.fields = null; App.show(App.currentId, true); },
  /* 直觀編輯那邊改了東西（打字、貼圖、插模組……）：標記未儲存；並排模式再把原始碼那邊同步過去 */
  touch() {
    this.dirty = true; this.autosave();
    if (this.mode === 'split') { this.side = 'wysi'; if (this._toSource) this._toSource(); }
  },
  /* 目前編輯器裡的內容（不論哪種模式）轉成 Markdown 全文 */
  text() {
    if (this.mode === 'wysiwyg' && this.fields) return this.compose();
    if (this.mode === 'split' && this.fields && this.ta) return this.side === 'wysi' ? this.compose() : this.ta.value;
    return this.ta ? this.ta.value : this.mod.raw;
  },
  compose() {
    const f = this.fields; const title = (f.title.value || '').trim() || Util.basename(this.mod.id);
    const fm = Parse.frontmatter(this.mod.raw).raw;
    const summary = Wysi.toMarkdown(f.summary), body = Wysi.toMarkdown(f.body);
    return `${fm}# ${title}\n\n## 摘要\n${summary}${summary ? '\n' : ''}\n## 內文\n${body}\n`;
  },
  switchMode(mode) {
    if (mode === this.mode || !this.mod) return;
    const text = this.text();
    this.mode = mode; Persist.pref.set('editMode', mode);
    App.renderEditor(text);
    this.dirty = text !== this.mod.raw;
  },
  /* 外部改了檔案、或切換模式時，用指定的文字重畫 */
  load(text) { App.renderEditor(text); this.dirty = text !== this.mod.raw; },
  /* 抽成模組（R47、D42）：選取的內容搬進新模組、原位置換成 [[連結]]。
     原始碼／並排（原始碼側）＝文字框選取範圍；直觀編輯＝選取範圍蓋到的整個段落。 */
  async extractSelection() {
    if (!this.mod || !App.canEdit()) return;
    const mod = this.mod, basePath = Util.dirname(mod.path);
    let md = '', replace = null;
    const useTa = this.mode === 'source' || (this.mode === 'split' && this.side === 'source');
    if (useTa && this.ta) {
      const ta = this.ta, a = ta.selectionStart, b = ta.selectionEnd;
      if (a === b) return App.toast('先在原始碼裡選取要抽出的內容', true);
      md = ta.value.slice(a, b);
      replace = link => {
        const before = ta.value.slice(0, a), after = ta.value.slice(b);
        const nl1 = before && !before.endsWith('\n') ? '\n' : '', nl2 = after && !after.startsWith('\n') ? '\n' : '';
        ta.value = before + nl1 + link + nl2 + after;
        ta.dispatchEvent(new Event('input', { bubbles: true }));
        ta.focus();
      };
    } else if (this.fields) {
      const sel = window.getSelection();
      if (!sel || !sel.rangeCount || sel.isCollapsed) return App.toast('先選取要抽出的內容（以整個段落為單位）', true);
      const range = sel.getRangeAt(0);
      const field = [this.fields.body, this.fields.summary].find(f => f && (f === range.commonAncestorContainer || f.contains(range.commonAncestorContainer)));
      if (!field) return App.toast('請在內文或摘要區域裡選取', true);
      const top = n => { while (n && n.parentNode !== field) n = n.parentNode; return n; };
      const s = top(range.startContainer), e = top(range.endContainer);
      if (!s || !e) return App.toast('選取範圍對不到段落', true);
      const blocks = []; for (let n = s; n; n = n.nextSibling) { blocks.push(n); if (n === e) break; }
      if (!blocks.includes(e)) return App.toast('選取範圍對不到段落', true);
      const tmp = h('div'); blocks.forEach(n => tmp.append(n.cloneNode(true)));
      md = Wysi.toMarkdown(tmp);
      replace = link => {
        const atom = Wysi.atomFromRaw(link, true, basePath);
        s.parentNode.insertBefore(atom, s);
        blocks.forEach(n => n.remove());
        Wysi.tidy(field);
        this.touch();
      };
    } else return;
    md = (md || '').trim();
    if (!md) return App.toast('選取的內容是空的', true);
    const firstLine = (md.split('\n').find(l => l.trim()) || '')
      .replace(/^[\s>]*(?:[-*+]|\d+[.)])?\s*(?:\[[ xX]\]\s*)?#{0,6}\s*/, '')
      .replace(/[*_`~\[\]!|]/g, '').trim().slice(0, 40) || '新模組';
    const name = prompt('新模組的名稱（會放在 ' + mod.id + '/ 底下）：', firstLine);
    if (name == null) return;
    try {
      const r = await Refactor.extract(mod, md, name.trim() || firstLine);
      replace(r.link);
      if (useTa) { this.dirty = this.ta.value !== mod.raw; this.autosave(); }
      App.toast('已建立 ' + r.id + '，記得儲存這一篇');
    } catch (e) { console.warn(e); App.toast('抽出失敗：' + (e.message || e), true); }
  },
  async save() {
    if (!this.mod || !App.canEdit()) return;
    const mod = this.mod, text = this.text();
    try {
      const r = await App.source.save(mod.path, text);
      const nm = Parse.module(text, mod.path); nm.mtime = (r && r.mtime) || Date.now();
      Store.upsert(nm); Store.reindex(); Drafts.del(mod.id);
      this.mod = null; this.dirty = false; this.fields = null;
      App.renderSidebar(); App.updateCache();
      App.toast(App.source && App.source.token ? '已 commit 到 GitHub：' + mod.path + '（公開頁面約 1–2 分鐘後更新）' : '已儲存 ' + mod.path);
      App.show(nm.id, true);
    } catch (e) { App.toast('儲存失敗：' + (e.message || e), true); }
  },
};

/* ===================== App ===================== */
const App = {
  source: null, currentId: null, pendingHandle: null, _toastT: null,
  $: id => document.getElementById(id),
  canEdit() { return !!(this.source && this.source.writable); },
  canSaveImages() { return this.canEdit() && typeof this.source.saveBinary === 'function'; },
  /* 把圖片存到模組旁邊的 圖片/ 資料夾，回傳可寫進 Markdown 的相對路徑 */
  async saveImage(file, mod) {
    if (!this.canSaveImages()) throw new Error('目前的來源無法儲存圖片');
    const ext = (file.name && file.name.includes('.') ? file.name.split('.').pop() : (file.type.split('/')[1] || 'png')).toLowerCase().replace('jpeg', 'jpg');
    if (!CONFIG.imageExts.includes(ext)) throw new Error('不支援的圖片格式：' + ext);
    const d = new Date(), pad = n => String(n).padStart(2, '0');
    const stamp = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
    const base = (file.name && !/^image\.(png|jpe?g|gif|webp)$/i.test(file.name)) ? file.name.replace(/\.[^.]+$/, '').replace(/[\\/:*?"<>|#\[\]]/g, '_').slice(0, 40) : 'img';
    const rel = `${CONFIG.imageFolder}/${stamp}-${base}.${ext}`;
    const full = Util.join(Util.dirname(mod.path), rel);
    const r = await this.source.saveBinary(full, file);
    Store.addAsset({ path: full, handle: r && r.handle, file: r && r.handle ? undefined : file });
    return rel;
  },
  insertAtCursor(ta, text) {
    const s = ta.selectionStart, e = ta.selectionEnd;
    ta.setRangeText(text, s, e, 'end'); ta.dispatchEvent(new Event('input')); ta.focus();
  },
  async handleEditorFiles(files, ta, mod) {
    const imgs = [...files].filter(f => f.type.startsWith('image/') || CONFIG.imageExts.includes(Util.ext(f.name || '')));
    if (!imgs.length) return false;
    if (!this.canSaveImages()) { this.toast('這個來源無法儲存圖片；請把圖片放進資料夾後用 ![](路徑) 引用', true); return true; }
    for (const f of imgs) {
      try {
        const rel = await this.saveImage(f, mod);
        const alt = (f.name && !/^(image|img|screenshot|擷取|截圖)[\w\- ]*\.\w+$/i.test(f.name)) ? f.name.replace(/\.[^.]+$/, '') : '';
        this.insertAtCursor(ta, `![${alt}](${rel})\n`); this.toast('已儲存圖片 ' + rel);
      }
      catch (e) { this.toast('圖片儲存失敗：' + (e.message || e), true); }
    }
    return true;
  },

  async init() {
    Theme.init(); Style.init();
    this.page = this.$('page'); this.main = this.$('main');
    this.bindUI();
    if (document.querySelector('script[type="text/x-module"]')) await this.useSource(new EmbeddedSource());
    else {
      const http = await HttpSource.detect();
      if (http) await this.useSource(http); else await this.tryRestore();
    }
    window.addEventListener('hashchange', () => this.onHash());
    if (!this.source) this.renderWelcome();
    this.updateChrome();
  },

  /* 打開頁面時：有記住的資料夾且權限還在 → 直接連；否則先顯示上次的快取，再請使用者按一下重新連接 */
  async tryRestore() {
    let handle = null;
    try { handle = await Persist.get('dirHandle'); } catch {}
    if (handle && typeof handle.queryPermission !== 'function') handle = null;   // 不是真的 handle（例如壞掉的快取）
    if (handle && FolderSource.supported()) {
      try {
        const src = new FolderSource(handle);
        if (await src.ensurePermission(false)) { await this.useSource(src); return; }
        this.pendingHandle = handle;
      } catch (e) { console.warn(e); }
    }
    let rec = null;
    try { rec = await Persist.get('cache'); } catch {}
    if (rec && rec.modules && rec.modules.length) {
      await this.useSource(new CacheSource(rec));
      if (this.pendingHandle) this.showNotice(`目前顯示的是上次的快取（唯讀）。重新連接資料夾「${this.pendingHandle.name}」就能編輯並自動更新。`, '重新連接資料夾', () => this.reopen());
    }
  },

  async useSource(src) {
    if (Editor.open && Editor.dirty && !confirm('目前的修改還沒儲存，要放棄嗎？')) return false;
    if (this.source && this.source.stopWatch) this.source.stopWatch();
    this.source = src; this.setStatus('載入中…', 'warn'); this.hideNotice();
    let loaded;
    try { loaded = await src.load(); }
    catch (e) { console.error(e); this.toast('載入失敗：' + (e.message || e), true); this.source = null; this.renderWelcome(); this.updateChrome(); return false; }
    Store.clear();
    for (const m of loaded.modules) { const mod = Parse.module(m.text, m.path); mod.mtime = m.mtime || 0; Store.upsert(mod); }
    for (const a of loaded.assets || []) Store.addAsset(a);
    Store.reindex();
    if (src.watch) src.watch(d => this.applyDelta(d));
    if (src.kind === 'http' && src.github && src.token) {   // 剛在別次重新整理前存過檔？部署（約 1–2 分鐘）沒跟上前先說清楚（D39）
      const t = +Persist.pref.get('ghSavedAt') || 0;
      const gen = (src.man && src.man.generated) || 0;
      if (t && gen && gen < t && Date.now() - t < 15 * 60 * 1000) { this._ghLagNotice = true; this.showNotice('剛存進 GitHub 的修改正在部署（通常 1–2 分鐘）。這頁目前顯示的是部署前的版本——修改都在，部署完會自動換上，不用重打。'); }
    }
    if (src.kind === 'folder') { this.pendingHandle = null; Persist.set('dirHandle', src.handle); }
    if (src.kind === 'files') { this.pendingHandle = null; Persist.del('dirHandle'); }   // 新的匯入取代舊的記憶
    if (src.kind === 'folder' || src.kind === 'files') this.writeCache();
    Editor.mod = null; Editor.dirty = false;
    this.updateChrome(); this.renderSidebar(); this.onHash();
    return true;
  },

  writeCache() {
    const src = App.source; if (!src || !(src.kind === 'folder' || src.kind === 'files')) return;
    const rec = { kind: src.kind, label: src.label, when: Date.now(), modules: [...Store.modules.values()].map(m => ({ path: m.path, text: m.raw, mtime: m.mtime })) };
    if (src.kind === 'files') {   // 檔案匯入：圖片也一起記住（上限 20 MB），下次打開才看得到
      let total = 0; rec.assets = [];
      for (const a of Store.assets.values()) { if (!a.file) continue; total += a.file.size; if (total > 20 * 1024 * 1024) break; rec.assets.push({ path: a.path, blob: a.file }); }
    }
    Persist.set('cache', rec);
  },
  /* 忘記這個頁面匯入的一切（不會動到任何 .md 檔），回到待匯入的起點 */
  async forget() {
    if (!confirm('忘記這個頁面匯入的內容，回到起點？\n只會清掉瀏覽器裡的記憶；你的 .md 檔案不會有任何變動。')) return;
    if (Editor.open && Editor.dirty && !confirm('目前的修改還沒儲存，確定放棄？')) return;
    if (this.source && this.source.stopWatch) this.source.stopWatch();
    await Promise.all(['dirHandle', 'cache'].map(k => Persist.del(k)));
    Persist.pref.del('last'); Memory.forgetAll(); Drafts.clearAll();
    this.source = null; this.pendingHandle = null; Editor.mod = null; Editor.dirty = false; this.currentId = null;
    Store.clear(); this.hideNotice();
    if (location.hash) history.replaceState(null, '', location.pathname + location.search);
    this.renderSidebar(); this.renderWelcome(); this.updateChrome(); this.toast('已忘記，回到起點');
  },
  showNotice(text, actionLabel, action) {
    const n = this.$('notice'); n.innerHTML = ''; n.hidden = false;
    n.append(h('span', {}, text));
    if (actionLabel) n.append(h('button', { class: 'btn primary', type: 'button', onclick: action }, actionLabel));
    n.append(h('button', { class: 'icon-btn', type: 'button', title: '關閉', 'aria-label': '關閉', onclick: () => this.hideNotice(), html: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>' }));
  },
  hideNotice() { const n = this.$('notice'); if (n) { n.hidden = true; n.innerHTML = ''; } },
  updateCache: Util.debounce(() => App.writeCache(), 800),

  applyDelta({ upserts, removed }) {
    if (this._ghLagNotice) { this._ghLagNotice = false; this.hideNotice(); this.toast('部署完成，內容已更新'); }   // 新的 manifest 到了
    const changed = new Set();
    for (const u of upserts) { const m = Parse.module(u.text, u.path); m.mtime = u.mtime || Date.now(); Store.upsert(m); changed.add(m.id); }
    for (const p of removed) { const id = Util.pathToId(p); Store.remove(id); changed.add(id); }
    Store.reindex(); this.renderSidebar(); this.updateCache(); this.setStatus();
    if (Editor.open) {
      if (!changed.has(Editor.mod.id)) return;
      const nm = Store.modules.get(Editor.mod.id);
      if (!nm) { this.toast('這個檔案已在外部被移除', true); return; }
      if (!Editor.dirty) { Editor.mod = nm; Editor.load(nm.raw); this.toast('已載入外部的修改'); }
      else this.showBanner('這個檔案剛在外部被修改，而你這裡也有未儲存的變更。', '改用外部版本', () => { Editor.mod = nm; Editor.load(nm.raw); Editor.dirty = false; this.hideBanner(); });
      return;
    }
    const cur = Util.idFromHash();
    if (cur && cur.startsWith('__')) { this.renderSpecial(cur); return; }
    if (this.currentId && !Store.modules.has(this.currentId)) { location.hash = ''; return; }
    this.refresh();
  },

  /* ---------- 導覽 ---------- */
  homeId() {
    for (const n of CONFIG.home) { const m = Store.resolve(n); if (m) return m.id; }
    const last = Persist.pref.get('last'); if (last && Store.modules.has(last)) return last;
    const first = Store.list()[0]; return first ? first.id : null;
  },
  onHash() {
    if (!this.source) return;
    const id = Util.idFromHash() || this.homeId();
    if (Editor.open) {
      if (Editor.mod.id === id) return;
      if (Editor.dirty && !confirm('目前的修改還沒儲存，要離開嗎？')) { location.hash = Util.hashFor(Editor.mod.id); return; }
      Editor.mod = null; Editor.dirty = false;
    }
    this.show(id);
  },
  trail: [], _navFrom: null,   // 麵包屑（R36）：從哪些模組一路點進來的
  show(id, force) {
    if (id && id.startsWith('__')) { this.renderSpecial(id); return; }
    if (!id) { this.renderNoModules(); return; }
    const mod = Store.modules.get(id) || Store.resolve(id);
    if (!mod) { this.renderMissingRoot(id); return; }
    // 軌跡：從頁面裡的卡片／晶片點進來 → 接在來源後面；其他方式（側欄、搜尋、網址）→ 回到軌跡裡的那一點或重新開始
    const from = this._navFrom; this._navFrom = null;
    if (from && from !== mod.id && Store.modules.has(from)) { const i = this.trail.indexOf(from); this.trail = (i >= 0 ? this.trail.slice(0, i + 1) : [from]).concat(mod.id); }
    else { const i = this.trail.indexOf(mod.id); this.trail = i >= 0 ? this.trail.slice(0, i + 1) : [mod.id]; }
    if (mod.id !== this.currentId || force || !this.page.querySelector('.root')) {
      this.currentId = mod.id; Persist.pref.set('last', mod.id);
      this.page.innerHTML = ''; this.page.append(...this.buildRoot(mod, {}));
      this.restoreMemory(mod.id);
      this.highlight();
      this.main.scrollTop = 0;
    }
    document.title = `${mod.title} · ${CONFIG.appName}`;
    this.markSidebar(); document.body.classList.remove('rail-open');
  },
  /* ---------- 展開狀態：可寫入時寫進檔案（D26），否則記在瀏覽器（D24） ---------- */
  _restoring: false,
  canWriteLinks() { return this.canEdit() && typeof this.source.save === 'function' && this.source.writeThrough !== false; },   // GitHub 直接編輯：翻卡片不 commit（D39），記在瀏覽器
  onCardMode(el) { this.onCardChange(el, { mode: +el.dataset.mode }); },
  onCardStyle(el) { this.onCardChange(el, { style: el.dataset.style }); },
  onCardChange(el, patch) {
    if (this._restoring || Editor.open) return;
    if (el.dataset.inline || el.dataset.link == null || !el._parent) { if (!this.canWriteLinks()) this.remember(); return; }   // 晶片就地展開的卡片：檔案沒有對應寫法
    if (this.canWriteLinks()) LinkWriter.queue(el._parent, +el.dataset.link, el._ref.raw, patch);
    else this.remember();
  },
  restoreMemory(id) {
    if (!CONFIG.rememberCards || this.canWriteLinks()) return;   // 可寫入時檔案就是真相，不用記憶
    const saved = Memory.cards(id); if (!saved) return;
    this._restoring = true;
    try { this.restoreState({ modes: saved.modes || {}, chips: saved.chips || {}, styles: saved.styles || {}, scroll: 0 }); } finally { this._restoring = false; }
  },
  remember() { if (!CONFIG.rememberCards || this._restoring || Editor.open || this.canWriteLinks()) return; clearTimeout(this._rememberTimer); this._rememberTimer = setTimeout(() => this._rememberNow(), 250); },
  _rememberNow() {
    const a = App; if (!CONFIG.rememberCards || a._restoring || !a.currentId || Editor.open) return;
    const s = { modes: {}, chips: {}, styles: {} };
    a.page.querySelectorAll('.card[data-key]:not([data-inline])').forEach(c => { if (c.dataset.mode !== c.dataset.init) s.modes[c.dataset.key] = +c.dataset.mode; if (c.dataset.style !== c.dataset.initStyle) s.styles[c.dataset.key] = c.dataset.style; });
    a.page.querySelectorAll('.chip.open[data-key]').forEach(c => { s.chips[c.dataset.key] = c._card ? +c._card.dataset.mode : CONFIG.inlineExpandMode; });
    Memory.setCards(a.currentId, s);
    const b = a.page.querySelector('.toolbar .reset-btn'); if (b) b.hidden = !Memory.cards(a.currentId);
  },
  resetMemory() { if (!this.currentId) return; Memory.clearCards(this.currentId); this.show(this.currentId, true); this.toast('已回到這一頁的預設展開狀態'); },
  refresh() {
    if (!this.currentId || Editor.open) return;
    const mod = Store.modules.get(this.currentId); if (!mod) return;
    const state = this.captureState();
    this.page.innerHTML = ''; this.page.append(...this.buildRoot(mod, {}));
    this.restoreState(state); this.highlight();
  },
  captureState() {
    const s = { modes: {}, chips: {}, styles: {}, scroll: this.main.scrollTop };
    this.page.querySelectorAll('.card[data-key]:not([data-inline])').forEach(c => { s.modes[c.dataset.key] = +c.dataset.mode; s.styles[c.dataset.key] = c.dataset.style; });
    this.page.querySelectorAll('.chip.open[data-key]').forEach(c => { s.chips[c.dataset.key] = c._card ? +c._card.dataset.mode : CONFIG.inlineExpandMode; });
    this.page.querySelectorAll('.card[data-inline][data-key]').forEach(c => { s.modes[c.dataset.key] = +c.dataset.mode; });
    return s;
  },
  restoreState(s) {
    const was = this._restoring; this._restoring = true;
    let guard = 0, progressed = true;
    while (progressed && guard++ < 60) {
      progressed = false;
      for (const ch of this.page.querySelectorAll('.chip[data-key]:not([data-restored])')) { ch.dataset.restored = '1'; const m = s.chips[ch.dataset.key]; if (m != null && !ch._card) ch._expand(m); progressed = true; }
      for (const c of this.page.querySelectorAll('.card[data-key]:not([data-restored])')) { c.dataset.restored = '1'; const st = s.styles && s.styles[c.dataset.key]; if (st && st !== c.dataset.style) c._setStyle(st); const m = s.modes[c.dataset.key]; if (m != null && m !== +c.dataset.mode) c._setMode(m); progressed = true; }
    }
    this._restoring = was;
    this.main.scrollTop = s.scroll;
  },
  expandAll(mode) {   // 閱讀用的暫時動作：不寫檔、不記憶（D26）
    clearTimeout(this._rememberTimer); this._restoring = true;
    let guard = 0, progressed = true;
    while (progressed && guard++ < 60) {
      progressed = false;
      for (const c of this.page.querySelectorAll('.card')) {
        if (+c.dataset.mode === mode) continue;
        const before = c.dataset.mode; c._setMode(mode);
        if (c.dataset.mode !== before) progressed = true;
      }
      if (mode === 1) for (const ch of this.page.querySelectorAll('.chip.open')) { ch._expand(); progressed = true; }
    }
    this._restoring = false;
  },

  /* ---------- 根模組 ---------- */
  buildRoot(mod, { preview = false } = {}) {
    const out = [];
    if (!preview) {
      const tb = h('div', { class: 'toolbar' },
        h('button', { class: 'btn quiet', type: 'button', onclick: () => history.back() }, '← 返回'),
        h('span', { class: 'path', title: mod.path }, mod.path),
        h('span', { class: 'spacer' }),
        h('button', { class: 'btn quiet', type: 'button', onclick: () => this.expandAll(3) }, '全部展開'),
        h('button', { class: 'btn quiet', type: 'button', onclick: () => this.expandAll(1) }, '全部收合'),
        h('button', { class: 'btn quiet reset-btn', type: 'button', title: '忘掉這一頁記住的展開狀態，回到連結寫的預設', hidden: !(CONFIG.rememberCards && !this.canWriteLinks() && Memory.cards(mod.id)), onclick: () => this.resetMemory() }, '回到預設'),
        h('button', { class: 'btn quiet', type: 'button', onclick: () => window.print() }, '列印'),
      );
      if (this.canEdit()) {
        tb.append(h('button', { class: 'btn', type: 'button', onclick: () => this.edit(mod.id) }, '編輯'));
        if (typeof this.source.remove === 'function') tb.append(
          h('button', { class: 'btn quiet', type: 'button', title: '改檔名或搬到別的資料夾，連到它的連結會一起更新', onclick: () => this.renamePanel(mod) }, '改名／搬移'),
          h('button', { class: 'btn quiet danger-hover', type: 'button', title: '刪除這個檔案', onclick: () => this.deleteModule(mod) }, '刪除'));
      }
      else if (this.source && this.source.editUrl && this.source.editUrl(mod.path)) {
        tb.append(h('button', { class: 'btn primary', type: 'button', title: '輸入一次 GitHub token，之後就能像在電腦上一樣直接編輯（R43）', onclick: () => this.githubTokenPanel() }, '啟用編輯'));
        tb.append(h('a', { class: 'btn', href: this.source.editUrl(mod.path), target: '_blank', rel: 'noopener' }, '在 GitHub 編輯'));
      }
      else if (this.pendingHandle) tb.append(h('button', { class: 'btn primary', type: 'button', title: '重新取得資料夾權限後直接進入編輯', onclick: async () => { if (await this.reopen()) this.edit(mod.id); } }, '重新連接後編輯'));
      else if (this.source) {
        tb.append(h('button', { class: 'btn', type: 'button', onclick: () => this.edit(mod.id) }, '檢視原始檔'));
        tb.append(h('button', { class: 'btn quiet', type: 'button', title: '為什麼不能編輯？', onclick: () => this.explainReadOnly() }, '唯讀？'));
      }
      out.push(tb);
    }
    if (!preview) { const c = this.buildCrumbs(mod); if (c) out.push(c); }
    const root = h('article', { class: 'root', dataset: { id: mod.id } });
    const children = new Set(mod.links.map(r => Store.resolve(r.target, Util.dirname(mod.path))).filter(m => m && m.id !== mod.id).map(m => m.id));
    const meta = h('div', { class: 'root-meta' });
    if (mod.date) meta.append(h('span', { class: 'date', title: 'frontmatter 的 date' }, mod.date));
    if (mod.mtime) meta.append(h('span', {}, '更新 ' + Util.fmtTime(mod.mtime)));
    meta.append(h('span', {}, `約 ${Util.wordCount(mod.summary + mod.body)} 字`));
    if (children.size) meta.append(h('span', {}, `${children.size} 個子模組`));
    if (mod.tags && mod.tags.length) meta.append(h('span', { class: 'tags' }, mod.tags.map(t => h('a', { class: 'tag', href: '#', title: '列出有這個標籤的模組', onclick: e => { e.preventDefault(); this.searchTag(t); } }, '#' + t))));
    root.append(h('header', { class: 'root-head' }, h('h1', { class: 'root-title', html: Util.titleHtml(mod.title) }), meta));
    const ctx = { ancestors: [mod.id], key: 'root', depth: 1, basePath: Util.dirname(mod.path) };
    if (mod.summary) { const s = h('div', { class: 'root-summary md', html: MD.render(mod.summary) }); Cards.hydrate(s, ctx, mod, 'summary'); root.append(s); }
    if (mod.body) { const b = h('div', { class: 'root-body md', html: MD.render(mod.body) }); Cards.hydrate(b, ctx, mod, 'body'); root.append(b); }
    if (!mod.summary && !mod.body) root.append(h('p', { class: 'note' }, '（這個模組還沒有內容）'));
    out.push(root);
    if (!preview) {
      const bl = Store.backlinks(mod.id);
      if (bl.length) out.push(h('footer', { class: 'backlinks' }, h('span', { class: 'lbl' }, '被引用於'),
        bl.map(b => h('span', { class: 'chip' }, h('a', { class: 'chip-go', href: Util.hashFor(b.id), title: b.path }, b.title)))));
    }
    return out;
  },
  /* 麵包屑（R36）：一路點進來的軌跡（可一鍵跳回），軌跡以外「誰把我裝進去」列為上層 */
  buildCrumbs(mod) {
    const trail = this.trail.slice(0, -1).filter(t => Store.modules.has(t));
    const parents = Store.backlinks(mod.id).filter(b => !trail.includes(b.id));
    if (!trail.length && !parents.length) return null;
    const nav = h('nav', { class: 'crumbs', 'aria-label': '位置' });
    if (trail.length) {
      for (const t of trail) { const m = Store.modules.get(t); nav.append(h('a', { class: 'crumb', href: Util.hashFor(t), title: m.path, html: Util.titleHtml(m.title) }), h('span', { class: 'crumb-sep' }, '›')); }
      nav.append(h('span', { class: 'crumb cur', html: Util.titleHtml(mod.title) }));
    }
    if (parents.length) nav.append(h('span', { class: 'parents' }, h('span', { class: 'lbl' }, trail.length ? '也在' : '上層'), parents.slice(0, 8).map(p => h('a', { class: 'crumb', href: Util.hashFor(p.id), title: p.path, html: Util.titleHtml(p.title) })), parents.length > 8 ? h('span', { class: 'lbl' }, `…共 ${parents.length} 個`) : null));
    return nav;
  },
  /* 標籤（R37）：點標題旁或側欄的標籤 → 側欄改列有這個標籤的模組 */
  searchTag(t) { const s = this.$('search'); s.value = '#' + t; this.renderSidebar(); if (window.innerWidth <= 900) document.body.classList.add('rail-open'); },
  /* 解析搜尋字：#標籤 要全中；其他字（空白分隔）要全部出現在標題／路徑／摘要／內文 */
  parseQuery(q) {
    const terms = (q || '').trim().split(/\s+/).filter(Boolean);
    return { tags: terms.filter(t => t.startsWith('#') && t.length > 1).map(t => t.slice(1).toLowerCase()), words: terms.filter(t => !t.startsWith('#')).map(t => t.toLowerCase()) };
  },
  matchQuery(m, pq) {
    if (pq.tags.length && !pq.tags.every(t => (m.tags || []).some(x => x.toLowerCase() === t))) return false;
    if (!pq.words.length) return true;
    const hay = (m.title + ' ' + m.path + ' ' + m.summary + ' ' + m.body).toLowerCase();
    return pq.words.every(w => hay.includes(w));
  },
  escRe(w) { return w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); },
  /* Markdown 去掉記號變成純文字（搜尋片段用）：連結留文字、圖片留說明、清單與核取記號拿掉 */
  plainText(md) {
    return String(md || '')
      .replace(/```[\s\S]*?```/g, s => s.replace(/```[^\n]*\n?/g, ''))
      .replace(/!\[([^\]]*)\]\([^)]*\)/g, '$1').replace(/!?\[\[([^\]|]+)[^\]]*\]\]/g, '$1').replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
      .replace(/^\s{0,3}#{1,6}\s+/gm, '').replace(/^\s*(?:[-*+]|\d+[.)])\s+(?:\[[ xX]\]\s*)?/gm, '').replace(/^\s*>\s?/gm, '')
      .replace(/[*_~`]+/g, '').replace(/<\/?[a-z][^>]*>/gi, '').replace(/\|/g, ' ').replace(/-{3,}/g, '')
      .replace(/\s+/g, ' ').trim();
  },
  /* 搜尋結果的摘要片段：第一個命中處前後各 30 字，命中的字 <mark> */
  snippet(m, words) {
    if (!words.length) return null;
    const text = this.plainText(m.summary + '\n' + m.body), low = text.toLowerCase();
    let at = -1, w0 = '';
    for (const w of words) { const i = low.indexOf(w); if (i >= 0 && (at < 0 || i < at)) { at = i; w0 = w; } }
    if (at < 0) return null;
    const start = Math.max(0, at - 30), end = Math.min(text.length, at + w0.length + 40);
    const piece = (start > 0 ? '…' : '') + text.slice(start, end) + (end < text.length ? '…' : '');
    const re = new RegExp(words.map(w => this.escRe(w)).join('|'), 'gi');
    return h('div', { class: 'snip', html: Util.esc(piece).replace(re, x => '<mark>' + x + '</mark>') });
  },
  /* 有搜尋字時，把目前頁面裡命中的字標起來（R39） */
  highlight() {
    const { words } = this.parseQuery(this.$('search').value);
    const root = this.page.querySelector('.root'); if (!root || !words.length) return;
    const re = new RegExp(words.map(w => this.escRe(w)).join('|'), 'gi'), test = new RegExp(re.source, 'i');
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: n => (test.test(n.nodeValue) && !n.parentElement.closest('.card-tools, .tri, .katex, script, style')) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT });
    const nodes = []; while (walker.nextNode()) nodes.push(walker.currentNode);
    for (const n of nodes) {
      const sv = n.nodeValue, frag = document.createDocumentFragment(); let last = 0, m; re.lastIndex = 0;
      while ((m = re.exec(sv))) { frag.append(sv.slice(last, m.index), h('mark', { class: 'hl' }, m[0])); last = m.index + m[0].length; if (!m[0]) re.lastIndex++; }
      frag.append(sv.slice(last)); n.replaceWith(frag);
    }
  },
  /* 改名／搬移（R34、R40）：面板放在工具列下面 */
  /* 卡片工具列的「併回」（R47）：確認後把模組內容搬回上層、刪掉模組檔 */
  async inlineCard(el, mod, ref) {
    if (!this.canEdit() || typeof this.source.remove !== 'function') return;
    const parentId = el._parent, parent = Store.modules.get(parentId);
    if (!parent) return this.toast('找不到上層模組', true);
    if (ref.index == null) return this.toast('對不到檔案裡的連結位置（晶片就地展開的卡片不能併回，請到上層模組的頁面操作）', true);
    const others = Store.backlinks(mod.id).filter(m => m.id !== parentId);
    const metaKeys = Object.keys(mod.meta || {}).filter(k => k !== 'title');
    const kids = [...Store.modules.keys()].some(id => id.startsWith(mod.id + '/'));
    let msg = `併回：「${mod.title}」的內容會搬進 ${parent.path}，原檔 ${mod.path} 會刪除。`;
    if (others.length) msg += `\n\n注意：另有 ${others.length} 個模組連到它，併回後那些連結會變成「找不到」。`;
    if (kids) msg += `\n它底下的子模組會留在原資料夾，內容裡連到它們的連結會改寫、仍然可用。`;
    if (metaKeys.length) msg += `\n它的 frontmatter（${metaKeys.join('、')}）不會保留。`;
    if (!confirm(msg)) return;
    try {
      await Refactor.inline(parentId, ref.index, mod);
      this.toast('已併回 ' + parent.path + '，並刪除 ' + mod.path);
      if (!Editor.open) this.refresh();
    } catch (e) { console.warn(e); this.toast('併回失敗：' + (e.message || e), true); }
  },
  renamePanel(mod) {
    this.closePanel();
    const input = h('input', { class: 'wy-q', type: 'text', value: mod.id, placeholder: '新的檔名，可含資料夾：專案/想法', spellcheck: 'false', autocomplete: 'off' });
    const sameTitle = mod.title === Util.basename(mod.id);
    const cb = h('input', { type: 'checkbox' }); cb.checked = sameTitle;
    const refs = Store.backlinks(mod.id);
    const kidCount = [...Store.modules.keys()].filter(id => id.startsWith(mod.id + '/')).length;
    // 搬進模組（R63）：輸入或選一個目標模組，路徑自動填成「目標/原名」（配對資料夾世界觀）
    const dl = h('datalist', { id: 'move-into-dl' });
    for (const m of Store.modules.values()) { if (m.id !== mod.id && !m.id.startsWith(mod.id + '/')) dl.append(h('option', { value: m.id })); }
    const lb1 = h('div', { style: 'font-size:12.5px;color:var(--ink-2);margin:2px 0 0' }, '新檔名（整段路徑；只想改名就改最後一段。檔名不能含 /，要斜線用全形 ／ 或寫進標題）');
    const lb2 = h('div', { style: 'font-size:12.5px;color:var(--ink-2);margin:6px 0 0' }, '或：搬進某個模組（自動放進它的同名資料夾）');
    const into = h('input', { class: 'wy-q', type: 'text', list: 'move-into-dl', placeholder: '輸入目標模組名稱', spellcheck: 'false', autocomplete: 'off' });
    into.addEventListener('input', () => {
      const t = Store.modules.get(into.value) || Store.resolve(into.value, Util.dirname(mod.path));
      if (t && t.id !== mod.id && !t.id.startsWith(mod.id + '/')) input.value = t.id + '/' + Util.basename(mod.id);
    });
    const info = h('div', { class: 'note' }, refs.length ? `有 ${refs.length} 個模組連到它（${refs.slice(0, 5).map(r => r.title).join('、')}${refs.length > 5 ? '…' : ''}），連結會一起改。` : '沒有其他模組連到它。', ' 搬到別的資料夾時，它自己的相對連結與圖片路徑也會跟著改。', kidCount ? ` 它底下有 ${kidCount} 個子模組，會整串一起搬。` : '');
    const doIt = async () => {
      const newId = Refactor.normalizeId(input.value);
      if (!newId) { this.toast('名稱不合法（不能含 | [ ] #，不能用 .. ）', true); return; }
      if (newId === mod.id) { this.toast('檔名沒有變，沒有做任何事'); return; }
      if (Store.modules.has(newId)) { this.toast('已經有同名的模組', true); return; }
      try {
        const r = await Refactor.renameTree(mod, newId, { retitle: cb.checked });
        this.closePanel(); this.toast(`已改成 ${newId}.md` + (r.moved > 1 ? `（含 ${r.moved - 1} 個子模組）` : '') + (r.updated ? `，更新了 ${r.updated} 個模組的連結` : ''));
        this.trail = []; this.currentId = null;
        if (Util.idFromHash() === r.id) this.show(r.id, true); else location.hash = Util.hashFor(r.id);
      } catch (e) { this.toast('改名失敗：' + (e.message || e), true); }
    };
    input.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); doIt(); } });
    into.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); doIt(); } });
    this.showPanel('改名／搬移 ' + mod.path, [lb1, input, lb2, into, dl, h('label', { class: 'wy-check' }, cb, ' 標題也改成新檔名'), info], [
      { label: '改名', primary: true, fn: doIt }, { label: '取消', fn: () => this.closePanel() }], { top: true });
    input.focus(); input.select();
  },
  async deleteModule(mod) {
    const refs = Store.backlinks(mod.id);
    const msg = `刪除 ${mod.path}？` + (refs.length ? `\n\n有 ${refs.length} 個模組連到它（${refs.slice(0, 5).map(r => r.title).join('、')}${refs.length > 5 ? '…' : ''}），刪除後那些連結會變成「找不到模組」。` : '') + '\n\n圖片資料夾不會被刪除。';
    if (!confirm(msg)) return;
    try { await Refactor.remove(mod); this.toast('已刪除 ' + mod.path); this.trail = []; this.currentId = null; if (location.hash) location.hash = ''; else this.onHash(); }
    catch (e) { this.toast('刪除失敗：' + (e.message || e), true); }
  },
  /* GitHub 直接編輯（R43、D39）：輸入 token 的面板；驗證通過才存起來 */
  githubTokenPanel() {
    const src = this.source; if (!src || src.kind !== 'http' || !src.github) return;
    this.closePanel();
    const g = src.github, repo = `${g.owner}/${g.repo}`;
    const input = h('input', { class: 'wy-q', type: 'password', placeholder: 'github_pat_… 或 ghp_…', autocomplete: 'off', spellcheck: 'false' });
    const steps = h('div', { class: 'note', style: 'line-height:1.7' },
      h('div', {}, '到 GitHub 申請一把只能動這個倉庫的鑰匙（一次就好）：'),
      h('div', {}, '1. 開 ', h('a', { href: 'https://github.com/settings/personal-access-tokens/new', target: '_blank', rel: 'noopener' }, 'github.com/settings/personal-access-tokens/new'), '（用同一個 GitHub 帳號登入）'),
      h('div', {}, `2. Repository access 選 Only select repositories → 勾 ${repo}`),
      h('div', {}, '3. Permissions → Repository permissions → Contents 選 Read and write'),
      h('div', {}, '4. 按 Generate token，把整串貼進上面的框裡'),
      h('div', {}, 'token 只會存在這台裝置的這個瀏覽器裡；存檔＝自動 commit 到倉庫，網站約 1–2 分鐘後跟著更新。'));
    const doIt = async () => {
      const v = input.value.trim(); if (!v) return;
      try {
        await src.verifyToken(v);
        Persist.pref.set('ghToken', v); src.enableToken(v);
        this.closePanel(); this.updateChrome(); this.renderSidebar();
        if (this.currentId) this.show(this.currentId, true);
        this.toast('可以直接編輯了：存檔會自動 commit 到 ' + repo);
      } catch (e) { this.toast(String(e.message || e), true); }
    };
    input.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); doIt(); } });
    this.showPanel('啟用直接編輯（' + repo + '）', [input, steps], [{ label: '啟用', primary: true, fn: doIt }, { label: '取消', fn: () => this.closePanel() }], { top: true });
    input.focus();
  },
  renderSpecial(id) {
    this.currentId = null; this.page.innerHTML = ''; document.body.classList.remove('rail-open');
    if (id === '__links') {
      const broken = Store.brokenLinks();
      const w = h('div', { class: 'welcome report' }, h('h1', {}, '連結檢查'), h('p', { class: 'lead' }, broken.length ? `有 ${broken.length} 個被引用但不存在的模組。建立檔案或修正連結後，這裡會自動更新。` : '所有連結都找得到對應的模組。'));
      for (const b of broken) {
        const row = h('div', { class: 'row' }, h('span', { class: 'target' }, '[[' + b.target + ']]'), h('span', { class: 'from' }, h('span', { class: 'note' }, '引用自'), b.from.map(m => h('a', { class: 'chip', href: Util.hashFor(m.id) }, h('span', { class: 'chip-go' }, m.title)))));
        if (this.canEdit()) row.append(h('button', { class: 'btn', type: 'button', onclick: () => this.createModule(b.target) }, '建立 ' + b.target + '.md'));
        w.append(row);
      }
      this.page.append(w); document.title = `連結檢查 · ${CONFIG.appName}`;
    } else this.renderMissingRoot(id);
    this.markSidebar();
  },
  renderMissingRoot(id) {
    this.currentId = null; this.page.innerHTML = '';
    const w = h('div', { class: 'welcome' }, h('h1', {}, '找不到模組'), h('p', { class: 'lead' }, h('code', {}, id + '.md'), ' 不在目前載入的來源裡。'));
    if (this.canEdit()) w.append(h('button', { class: 'btn primary', type: 'button', onclick: () => this.createModule(id) }, `建立 ${id}.md`));
    w.append(' ', h('a', { class: 'btn', href: '#' }, '回首頁'));
    this.page.append(w); this.markSidebar();
  },
  renderNoModules() {
    this.currentId = null; this.page.innerHTML = '';
    const w = h('div', { class: 'welcome' }, h('h1', {}, '這裡還沒有任何模組'), h('p', { class: 'lead' }, '來源裡沒有 .md 檔。'));
    if (this.canEdit()) w.append(h('button', { class: 'btn primary', type: 'button', onclick: () => this.newModule() }, '＋ 新增第一個模組'));
    this.page.append(w);
  },

  /* ---------- 編輯 ---------- */
  edit(id) {
    const mod = Store.modules.get(id); if (!mod) return;
    if (location.hash !== Util.hashFor(id)) { this.currentId = id; location.hash = Util.hashFor(id); }
    Editor.start(mod); this.markSidebar();
  },
  /* 編輯器外框：上方工具列（路徑、取消）＋ 釘在頂端的編輯列（模式切換、格式鈕、儲存；R28）＋ 依模式畫出內容 */
  renderEditor(text) {
    const mod = Editor.mod, writable = this.canEdit();
    if (text == null) text = mod.raw;
    this.page.innerHTML = ''; this.currentId = mod.id; Editor.ta = null; Editor.fields = null; Editor.preview = null; Editor.side = 'source'; Autocomplete.close();
    const tb = h('div', { class: 'toolbar' }, h('span', { class: 'path' }, (writable ? '編輯 ' : '原始檔 ') + mod.path), h('span', { class: 'spacer' }));
    if (!writable) {
      tb.append(h('button', { class: 'btn', type: 'button', onclick: async () => { try { await navigator.clipboard.writeText(Editor.text()); this.toast('已複製全文'); } catch { this.toast('無法複製', true); } } }, '複製全文'));
      if (window.self === window.top) tb.append(h('button', { class: 'btn', type: 'button', onclick: () => { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([Editor.text()], { type: 'text/markdown;charset=utf-8' })); a.download = Util.basename(mod.path); a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 5000); } }, '下載 .md'));
    }
    tb.append(h('button', { class: 'btn quiet', type: 'button', onclick: () => Editor.cancel() }, writable ? '取消' : '關閉'));
    const banner = h('div', { id: 'editBanner', class: 'banner warn', hidden: true });
    const mode = writable ? Editor.mode : 'source';
    const wrap = h('div', { class: 'editor ' + mode });
    if (writable) wrap.append(this.buildEditorBar(mod));
    this.page.append(tb, banner, wrap);
    if (mode === 'wysiwyg') this.renderWysiwyg(text, mod, wrap);
    else if (mode === 'split') this.renderSplit(text, mod, wrap);
    else this.renderSource(text, mod, writable, wrap);
    this.main.scrollTop = 0; document.title = `編輯 ${mod.title} · ${CONFIG.appName}`;
  },
  /* 編輯列（R28）：position: sticky 釘在捲動區頂端，捲到哪都看得到——模式切換｜格式鈕（原始碼模式藏起來）｜儲存 */
  buildEditorBar(mod) {
    const basePath = Util.dirname(mod.path);
    const modes = [['wysiwyg', '直觀編輯', '直接在畫面上打字、選字後按格式鈕'], ['source', '原始碼', 'Markdown 原始碼，下方有預覽'], ['split', '並排', '左邊直觀編輯、右邊原始碼，兩邊即時同步（R29）']];
    const seg = h('div', { class: 'seg mode-seg', role: 'group', 'aria-label': '編輯模式' },
      modes.map(([m, label, title]) => h('button', { type: 'button', class: Editor.mode === m ? 'on' : '', dataset: { mode: m }, title, onclick: () => Editor.switchMode(m) }, label)));
    const extractBtn = App.canEdit() ? h('button', { class: 'btn quiet ex-btn', type: 'button', title: '把選取的內容搬進一個新模組（放在這個模組底下），原位置換成連結；直觀編輯以整個段落為單位（R47）', onclick: () => Editor.extractSelection() }, '抽成模組') : null;
    const bar = h('div', { class: 'wy-tools ed-bar' + (Editor.mode === 'source' ? ' no-fmt' : '') },
      seg, extractBtn, h('span', { class: 'wy-sep' }), this.buildWysiTools(mod, basePath), h('span', { class: 'spacer' }),
      h('button', { class: 'btn primary', type: 'button', onclick: () => Editor.save() }, '儲存'));
    bar.addEventListener('mousedown', e => { if (e.target.tagName !== 'SELECT') e.preventDefault(); });   // 不搶焦點，直觀編輯的選取範圍才會留著
    return bar;
  },
  /* ----- 原始碼模式：文字框＋即時預覽 ----- */
  renderSource(text, mod, writable, wrap) {
    const ta = this.makeTextarea(text, mod, () => { Editor.dirty = ta.value !== mod.raw; this.renderPreview(); });
    const hint = h('div', { class: 'hint' },
      writable ? h('span', {}, h('span', { class: 'kbd' }, '⌘/Ctrl + S'), ' 儲存') : h('span', {}, '這個來源無法直接寫回檔案；可以複製或下載後自己存檔。'),
      h('span', {}, '連結寫法：', h('code', {}, '[[模組名]]'), '、', h('code', {}, '[[模組名|摘要]]'), '、', h('code', {}, '[[資料夾/模組名|全文]]')),
      this.canSaveImages() ? h('span', {}, '圖片直接貼上或拖進來，會存到 ', h('code', {}, Util.join(Util.dirname(mod.path), CONFIG.imageFolder) + '/')) : null);
    Editor.preview = h('div');
    wrap.append(ta, hint, h('div', { class: 'preview-lbl' }, '預覽'), Editor.preview);
    const grow = () => { ta.style.height = 'auto'; ta.style.height = Math.max(280, Math.min(ta.scrollHeight + 4, window.innerHeight * 0.72)) + 'px'; };
    ta.addEventListener('input', grow);
    this.renderPreview(); grow();
    if (writable) ta.focus();
  },
  /* 原始碼文字框（原始碼模式與並排模式共用）：Tab 縮排、貼圖、拖圖 */
  makeTextarea(text, mod, onInput) {
    const ta = h('textarea', { spellcheck: 'false', 'aria-label': '模組原始內容' }); ta.value = text;
    Editor.ta = ta;
    ta.addEventListener('input', Util.debounce(onInput, 180));
    ta.addEventListener('input', () => { Editor.autosave(); this.textareaAutocomplete(ta, mod); });
    ta.addEventListener('blur', () => setTimeout(() => { if (document.activeElement !== ta) Autocomplete.close(); }, 120));
    ta.addEventListener('keydown', e => {
      if (Autocomplete.key(e)) return;
      if (e.key === 'Tab') { e.preventDefault(); const s = ta.selectionStart, en = ta.selectionEnd; ta.setRangeText('  ', s, en, 'end'); ta.dispatchEvent(new Event('input')); }
    });
    ta.addEventListener('paste', e => { const files = e.clipboardData && e.clipboardData.files; if (files && files.length && [...files].some(f => f.type.startsWith('image/'))) { e.preventDefault(); this.handleEditorFiles(files, ta, mod); } });
    ta.addEventListener('drop', e => { const files = e.dataTransfer && e.dataTransfer.files; if (files && files.length) { e.preventDefault(); e.stopPropagation(); document.body.classList.remove('dragging'); this.handleEditorFiles(files, ta, mod); } });
    return ta;
  },
  /* 連結自動完成（R35）——文字框：游標前是 [[… 就列出模組，選了補成 [[目標]] */
  textareaAutocomplete(ta, mod) {
    const q = Autocomplete.query(ta.value.slice(0, ta.selectionStart));
    if (q == null) { Autocomplete.close(); return; }
    const basePath = Util.dirname(mod.path);
    Autocomplete.open(Autocomplete.caretRect(ta), q, mod.id, m => {
      const end = ta.selectionStart, start = end - q.length;
      ta.setRangeText(Store.linkTarget(m.id, basePath) + ']]', start, end, 'end');
      ta.focus(); ta.dispatchEvent(new Event('input'));
    });
  },
  /* 直觀編輯：游標所在文字節點的前面是 [[… 就列出模組，選了換成原子（該行沒別的字 → 卡片，否則晶片） */
  fieldAutocomplete(f, mod) {
    const sel = window.getSelection(); const n = sel && sel.rangeCount ? sel.anchorNode : null;
    if (!n || n.nodeType !== 3 || !f.contains(n)) { Autocomplete.close(); return; }
    const q = Autocomplete.query(n.nodeValue.slice(0, sel.anchorOffset));
    if (q == null) { Autocomplete.close(); return; }
    let rect = sel.getRangeAt(0).getBoundingClientRect(); if (!rect.width && !rect.height) rect = n.parentElement.getBoundingClientRect();
    const basePath = Util.dirname(mod.path), off = sel.anchorOffset;
    Autocomplete.open(rect, q, mod.id, m => {
      f.focus();
      const r = document.createRange(); r.setStart(n, off - q.length - 2); r.setEnd(n, off); r.deleteContents();
      const s2 = window.getSelection(); s2.removeAllRanges(); s2.addRange(r);
      const target = Store.linkTarget(m.id, basePath), blk = Wysi.currentBlock(f);
      if (blk && !blk.textContent.trim() && !blk.querySelector('img, .wy-atom')) Wysi.insertBlockNode(f, Wysi.atomFromRaw(`[[${target}|摘要]]`, true, basePath));
      else { Wysi.insertNode(Wysi.atomFromRaw(`[[${target}]]`, false, basePath)); Wysi.insertNode(document.createTextNode(' ')); }
      Wysi.tidy(f); Editor.touch();
    });
  },
  renderPreview() {
    if (!Editor.open || !Editor.preview || !Editor.ta) return;
    const m = Parse.module(Editor.ta.value, Editor.mod.path); m.mtime = Editor.mod.mtime;
    Editor.preview.innerHTML = ''; Editor.preview.append(...this.buildRoot(m, { preview: true }));
  },
  /* ----- 直觀編輯模式（R25）：標題、摘要、內文三個區域直接打字 ----- */
  renderWysiwyg(text, mod, wrap) {
    const basePath = Util.dirname(mod.path);
    wrap.append(this.buildWysiDoc(text, mod),
      h('div', { class: 'hint' }, h('span', {}, h('span', { class: 'kbd' }, '⌘/Ctrl + S'), ' 儲存'), h('span', {}, '選字後按工具列設粗體、標題、清單；連結、圖片、模組、數學式也在工具列。'), this.canSaveImages() ? h('span', {}, '貼上或拖入圖片會存到 ', h('code', {}, Util.join(basePath, CONFIG.imageFolder) + '/')) : null));
    Editor.fields.title.focus();
  },
  /* ----- 並排模式（R29）：左邊直觀編輯、右邊原始碼；哪邊在打字就以哪邊為準，停下來 0.3 秒後同步到另一邊 ----- */
  renderSplit(text, mod, wrap) {
    const basePath = Util.dirname(mod.path);
    const left = h('div', { class: 'ed-pane ed-left' }), right = h('div', { class: 'ed-pane ed-right' });
    const split = h('div', { class: 'ed-split' }, left, right);
    const ta = this.makeTextarea(text, mod, () => {});
    right.append(ta);
    left.append(this.buildWysiDoc(text, mod));
    wrap.append(split, h('div', { class: 'hint' }, h('span', {}, h('span', { class: 'kbd' }, '⌘/Ctrl + S'), ' 儲存'), h('span', {}, '兩邊都能改：右邊打字，左邊跟著變；左邊改了，右邊的原始碼也會更新。'), this.canSaveImages() ? h('span', {}, '貼上或拖入圖片會存到 ', h('code', {}, Util.join(basePath, CONFIG.imageFolder) + '/')) : null));
    // 原始碼 → 直觀：整份重畫（打字的那邊是原始碼，直觀那邊沒有游標要保留）
    let pendingWysi = false;
    const redrawWysi = () => {
      pendingWysi = false;
      if (!Editor.open || Editor.mode !== 'split' || Editor.side !== 'source') return;
      const st = left.scrollTop; left.innerHTML = ''; left.append(this.buildWysiDoc(ta.value, mod)); left.scrollTop = st;
    };
    const toWysi = Util.debounce(redrawWysi, 300);
    ta.addEventListener('input', () => { Editor.side = 'source'; Editor.dirty = ta.value !== mod.raw; pendingWysi = true; toWysi(); });
    // 直觀 → 原始碼：序列化後換掉文字框內容（保留捲動位置）
    const pushSource = () => {
      if (!Editor.open || Editor.mode !== 'split' || Editor.side !== 'wysi' || !Editor.fields) return;
      const st = ta.scrollTop; ta.value = Editor.compose(); ta.scrollTop = st;
    };
    Editor._toSource = Util.debounce(pushSource, 300);
    left.addEventListener('input', () => Editor.touch());
    left.addEventListener('change', () => Editor.touch());
    // 在 0.3 秒內就換邊：先把還沒同步的那邊推過去，才不會被另一邊蓋掉
    ta.addEventListener('focus', () => { if (Editor.side === 'wysi') pushSource(); });
    left.addEventListener('mousedown', () => { if (pendingWysi) redrawWysi(); });
    // 捲動大致同步（按比例；同步引起的捲動不再回傳）
    let lock = false;
    const follow = (from, to) => { if (lock) return; lock = true; const r = from.scrollTop / Math.max(1, from.scrollHeight - from.clientHeight); to.scrollTop = r * (to.scrollHeight - to.clientHeight); setTimeout(() => { lock = false; }, 60); };
    ta.addEventListener('scroll', () => follow(ta, left));
    left.addEventListener('scroll', () => follow(left, ta));
    // 高度：佔滿視窗剩下的空間，兩邊各自捲動；視窗改變大小時重算
    const fit = () => { if (!split.isConnected) { window.removeEventListener('resize', fit); return; } const top = split.getBoundingClientRect().top; split.style.height = Math.max(320, window.innerHeight - top - 16) + 'px'; };
    window.addEventListener('resize', fit); requestAnimationFrame(fit);
    ta.focus();
  },
  /* 直觀編輯的文件本體：標題輸入框＋摘要、內文兩個可編輯區（直觀模式與並排模式共用） */
  buildWysiDoc(text, mod) {
    const m = Parse.module(text, mod.path), basePath = Util.dirname(mod.path);
    const title = h('input', { class: 'wy-title', type: 'text', value: m.title, placeholder: '標題', 'aria-label': '標題', spellcheck: 'false' });
    const summary = Wysi.field(m.summary, basePath, '摘要：一兩句話說這篇在講什麼（可留白）');
    const body = Wysi.field(m.body, basePath, '內文：直接打字；行首打 - 、1. 、# 、> 會自動變成清單、標題、引言');
    Editor.fields = { title, summary, body };
    const doc = h('div', { class: 'wy-doc' }, title, h('div', { class: 'wy-lbl' }, '摘要'), summary, h('div', { class: 'wy-lbl' }, '內文'), body);
    const dirty = () => Editor.touch();
    title.addEventListener('input', dirty);
    for (const f of [summary, body]) {
      f.addEventListener('focusin', () => { Editor.activeField = f; });
      f.addEventListener('input', e => { dirty(); if (e.inputType === 'insertText' && e.data === ' ') Wysi.autoformat(f); this.fieldAutocomplete(f, mod); });
      f.addEventListener('change', dirty);   // 核取方塊
      f.addEventListener('blur', () => setTimeout(() => { if (!f.contains(document.activeElement)) Autocomplete.close(); }, 120));
      f.addEventListener('keydown', e => {
        if (Autocomplete.key(e)) return;
        if (e.key === 'Tab') { e.preventDefault(); if (Wysi.inList(f)) Wysi.exec(e.shiftKey ? 'outdent' : 'indent'); dirty(); }
      });
      f.addEventListener('paste', e => {
        const cd = e.clipboardData; if (!cd) return;
        const files = cd.files;
        if (files && files.length && [...files].some(x => x.type.startsWith('image/'))) { e.preventDefault(); this.handleWysiFiles(files, f, mod); return; }
        const t = cd.getData('text/plain'); if (t != null) { e.preventDefault(); Wysi.exec('insertText', t); dirty(); }
      });
      f.addEventListener('drop', e => { const files = e.dataTransfer && e.dataTransfer.files; if (files && files.length) { e.preventDefault(); e.stopPropagation(); document.body.classList.remove('dragging'); this.handleWysiFiles(files, f, mod); } });
      f.addEventListener('click', e => {
        const atom = e.target.closest('.wy-atom'); if (!atom || !f.contains(atom)) return;
        e.preventDefault();
        if (atom.classList.contains('wy-math')) this.editMathAtom(atom, f); else this.openLinkPanel(f, basePath, atom);
      });
    }
    Editor.activeField = body;
    return doc;
  },
  /* 格式鈕：都靠 execCommand 與幾個小幫手（放在編輯列裡；原始碼模式用 CSS 藏起來） */
  buildWysiTools(mod, basePath) {
    const field = () => { const f = Editor.activeField || Editor.fields.body; if (!f.contains(document.activeElement) && document.activeElement !== f) f.focus(); return f; };
    const mark = () => Editor.touch();
    const btn = (label, title, fn, cls = '') => h('button', { class: 'wy-btn ' + cls, type: 'button', title, 'aria-label': title, onmousedown: e => e.preventDefault(), onclick: () => { fn(field()); mark(); } }, label);
    const sep = () => h('span', { class: 'wy-sep' });
    const headingSel = h('select', { class: 'sel wy-heading', title: '段落格式', 'aria-label': '段落格式', onmousedown: e => e.stopPropagation(), onchange: e => { const f = field(); Wysi.exec('formatBlock', e.target.value); e.target.value = 'p'; mark(); } },
      h('option', { value: 'p' }, '一般文字'), h('option', { value: 'h2' }, '大標題'), h('option', { value: 'h3' }, '中標題'), h('option', { value: 'h4' }, '小標題'));
    const imgInput = h('input', { type: 'file', accept: 'image/*', multiple: true, hidden: true, onchange: e => { if (e.target.files.length) this.handleWysiFiles(e.target.files, field(), mod); e.target.value = ''; } });
    const tools = h('span', { class: 'wy-fmt' },
      btn('B', '粗體（⌘B）', () => Wysi.exec('bold'), 'b'),
      btn('I', '斜體（⌘I）', () => Wysi.exec('italic'), 'i'),
      btn('U', '底線（⌘U）', () => Wysi.exec('underline'), 'u'),
      btn('S', '刪除線', () => Wysi.exec('strikeThrough'), 's'),
      btn('螢光', '螢光標記', f => Wysi.toggleTag(f, 'mark')),
      sep(), headingSel, sep(),
      btn('• 清單', '項目清單', () => Wysi.exec('insertUnorderedList')),
      btn('1. 清單', '編號清單', () => Wysi.exec('insertOrderedList')),
      btn('☑ 核取', '核取清單', f => { let li = Wysi.inList(f); if (!li) { Wysi.exec('insertUnorderedList'); li = Wysi.inList(f); } if (!li) return; const cb = li.querySelector(':scope > input[type="checkbox"]'); if (cb) { cb.remove(); } else li.prepend(h('input', { type: 'checkbox', contenteditable: 'false' }), ' '); }),
      btn('❝ 引言', '引言', f => { const b = Wysi.currentBlock(f); Wysi.exec('formatBlock', b && b.closest('blockquote') ? 'p' : 'blockquote'); }),
      btn('‹›', '程式碼：選字變行內程式碼，沒選字變程式碼區塊', f => { const sel = window.getSelection(); if (sel && !sel.isCollapsed) Wysi.toggleTag(f, 'code'); else { const b = Wysi.currentBlock(f); Wysi.exec('formatBlock', b && b.tagName === 'PRE' ? 'p' : 'pre'); } }),
      sep(),
      btn('連結', '插入連結', f => { const sel = window.getSelection(); const has = sel && !sel.isCollapsed; const url = prompt('連結網址：', 'https://'); if (!url) return; if (has) Wysi.exec('createLink', url); else Wysi.insertHtml(`<a href="${Util.esc(url)}">${Util.esc(url)}</a>&nbsp;`); }),
      btn('圖片', '插入圖片（也可以直接貼上或拖進來）', () => { if (!this.canSaveImages()) { this.toast('這個來源無法儲存圖片', true); return; } imgInput.click(); }),
      btn('模組', '插入另一個模組（卡片或晶片）', f => this.openLinkPanel(f, basePath, null)),
      btn('∑ 數學', '插入數學式（TeX）', f => this.editMathAtom(null, f)),
      btn('表格', '插入表格', f => Wysi.insertBlockNode(f, h('table', {}, h('thead', {}, h('tr', {}, h('th', {}, '欄一'), h('th', {}, '欄二'))), h('tbody', {}, h('tr', {}, h('td', {}, h('br')), h('td', {}, h('br'))))))),
      btn('—', '分隔線', f => Wysi.insertBlockNode(f, h('hr'))),
      imgInput);
    return tools;
  },
  async handleWysiFiles(files, field, mod) {
    const imgs = [...files].filter(f => f.type.startsWith('image/') || CONFIG.imageExts.includes(Util.ext(f.name || '')));
    if (!imgs.length) return false;
    if (!this.canSaveImages()) { this.toast('這個來源無法儲存圖片', true); return true; }
    field.focus();
    for (const f of imgs) {
      try {
        const rel = await this.saveImage(f, mod);
        const url = await Store.assetUrl(rel, Util.dirname(mod.path));
        const img = h('img', { src: url || rel, alt: '', dataset: { md: rel } });
        const blk = Wysi.currentBlock(field);
        if (blk && blk.parentNode === field && !blk.textContent.trim()) Wysi.insertNode(img); else Wysi.insertBlockNode(field, h('p', {}, img));
        Editor.touch(); this.toast('已儲存圖片 ' + rel);
      } catch (e) { this.toast('圖片儲存失敗：' + (e.message || e), true); }
    }
    return true;
  },
  /* 數學式：用一個小面板輸入 TeX；atom 為 null 表示新增 */
  editMathAtom(atom, field) {
    const cur = atom ? atom.dataset.md : '';
    const isBlock = atom ? atom.tagName === 'DIV' : false;
    const tex = cur.replace(/^\$\$\n?|\n?\$\$$/g, '').replace(/^\$|\$$/g, '');
    const ta = h('textarea', { class: 'wy-tex', rows: '3', placeholder: '例如 \\frac{a}{b}、x^2、\\sum_{i=1}^n', spellcheck: 'false' }); ta.value = tex;
    const blockCb = h('input', { type: 'checkbox' }); blockCb.checked = isBlock;
    const preview = h('div', { class: 'wy-tex-preview md' });
    const upd = () => { preview.innerHTML = ta.value.trim() ? MD.render(blockCb.checked ? `$$\n${ta.value.trim()}\n$$` : `$${ta.value.trim()}$`) : ''; };
    ta.addEventListener('input', upd); blockCb.addEventListener('change', upd); upd();
    const savedRange = this.saveRange(field);
    this.showPanel('數學式', [ta, h('label', { class: 'wy-check' }, blockCb, ' 獨立一行（置中顯示）'), preview], [
      { label: atom ? '更新' : '插入', primary: true, fn: () => {
        const t = ta.value.trim(); if (!t) return;
        const node = Wysi.mathAtom(t, blockCb.checked); if (!node) return;
        if (atom) atom.replaceWith(node); else { this.restoreRange(field, savedRange); if (blockCb.checked) Wysi.insertBlockNode(field, node); else { Wysi.insertNode(node); Wysi.insertNode(document.createTextNode(' ')); } }
        Wysi.tidy(field); Editor.touch(); this.closePanel();
      } },
      atom ? { label: '刪除', fn: () => { atom.remove(); Wysi.tidy(field); Editor.touch(); this.closePanel(); } } : null,
      { label: '取消', fn: () => this.closePanel() }]);
    ta.focus();
  },
  /* 模組連結：搜尋模組、選模式、卡片或晶片；atom 不為 null 時是修改既有的 */
  openLinkPanel(field, basePath, atom) {
    let ref = { target: '', mode: 2, label: null }, block = true;
    if (atom) { const m = /^(!?)\[\[([^\[\]\n`]+?)\]\]$/.exec(atom.dataset.md || ''); if (m) ref = Refs.parse(m[2], !!m[1]); block = atom.tagName === 'DIV'; }
    const q = h('input', { class: 'wy-q', type: 'search', placeholder: '搜尋模組名稱或路徑…', autocomplete: 'off' }); q.value = ref.target;
    const list = h('div', { class: 'wy-results' });
    const modeSel = h('select', { class: 'sel' }, h('option', { value: '1' }, '只顯示標題'), h('option', { value: '2' }, '標題＋摘要'), h('option', { value: '3' }, '標題＋摘要＋內文')); modeSel.value = String(ref.mode || 1);
    const formSel = h('select', { class: 'sel' }, h('option', { value: 'card' }, '卡片（獨立一行）'), h('option', { value: 'chip' }, '晶片（句子中間）')); formSel.value = block ? 'card' : 'chip';
    const styleSel = h('select', { class: 'sel', title: '外觀' }, h('option', { value: 'card' }, '外觀：卡片'), h('option', { value: 'flat' }, '外觀：扁平（和清單項目平行）'), h('option', { value: 'group' }, '外觀：群組縮排（無框、內容縮排）')); styleSel.value = (ref.style === 'flat' || ref.style === 'group') ? ref.style : 'card';
    const label = h('input', { class: 'wy-q', type: 'text', placeholder: '顯示文字（留白＝模組標題）' }); label.value = ref.label || '';
    let picked = ref.target;
    const renderList = () => {
      const s = q.value.trim().toLowerCase(); list.innerHTML = '';
      const mods = Store.list().filter(m => m.id !== Editor.mod.id && (!s || (m.title + ' ' + m.path).toLowerCase().includes(s))).slice(0, 40);
      if (!mods.length) { list.append(h('div', { class: 'note', style: 'padding:6px 8px' }, s ? '沒有符合的模組；按「插入」會連到這個名稱（檔案還不存在時顯示為壞連結）' : '沒有模組')); }
      for (const m of mods) list.append(h('button', { type: 'button', class: 'wy-result' + (m.id === picked ? ' on' : ''), onclick: () => { picked = m.id; q.value = m.id; renderList(); } }, h('span', { class: 'wy-rt', html: Util.titleHtml(m.title) }), h('span', { class: 'wy-rp' }, m.path)));
    };
    q.addEventListener('input', () => { picked = q.value.trim(); renderList(); });
    renderList();
    const savedRange = this.saveRange(field);
    const build = () => {
      const target = (picked || q.value).trim(); if (!target) return null;
      // 連到同資料夾或子資料夾的模組時，寫成相對於目前模組資料夾的路徑，搬家也不會壞
      let t = target; if (basePath && target.startsWith(basePath + '/')) t = target.slice(basePath.length + 1);
      const mode = ['', '標題', '摘要', '全文'][+modeSel.value] || '標題';
      const parts = [t]; if (mode !== '標題') parts.push(mode); if (styleSel.value === 'flat') parts.push('扁平'); else if (styleSel.value === 'group') parts.push('群組縮排'); if (label.value.trim()) parts.push(label.value.trim());
      return `[[${parts.join('|')}]]`;
    };
    this.showPanel(atom ? '修改模組連結' : '插入模組', [q, list, h('div', { class: 'wy-row' }, modeSel, formSel, styleSel), label], [
      { label: atom ? '更新' : '插入', primary: true, fn: () => {
        const raw = build(); if (!raw) return;
        const node = Wysi.atomFromRaw(raw, formSel.value === 'card', basePath);
        if (atom) atom.replaceWith(node); else { this.restoreRange(field, savedRange); if (formSel.value === 'card') Wysi.insertBlockNode(field, node); else { Wysi.insertNode(node); Wysi.insertNode(document.createTextNode(' ')); } }
        Wysi.tidy(field); Editor.touch(); this.closePanel();
      } },
      atom ? { label: '刪除', fn: () => { atom.remove(); Wysi.tidy(field); Editor.touch(); this.closePanel(); } } : null,
      { label: '取消', fn: () => this.closePanel() }]);
    q.focus(); q.select();
  },
  saveRange(field) { const sel = window.getSelection(); if (sel && sel.rangeCount && field.contains(sel.getRangeAt(0).startContainer)) return sel.getRangeAt(0).cloneRange(); return null; },
  restoreRange(field, range) { field.focus(); const sel = window.getSelection(); sel.removeAllRanges(); if (range) sel.addRange(range); else Wysi.placeCaretAtEnd(field); },
  showPanel(title, bodyEls, actions, { top = false } = {}) {
    this.closePanel();
    const panel = h('div', { class: 'wy-panel', role: 'dialog', 'aria-label': title }, h('div', { class: 'wy-panel-title' }, title), ...bodyEls,
      h('div', { class: 'wy-row' }, actions.filter(Boolean).map(a => h('button', { type: 'button', class: 'btn' + (a.primary ? ' primary' : ''), onclick: a.fn }, a.label))));
    panel.addEventListener('keydown', e => { if (e.key === 'Escape') this.closePanel(); if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') { e.preventDefault(); const p = panel.querySelector('.btn.primary'); if (p) p.click(); } });
    const tb = top ? this.page.querySelector('.toolbar') : null, tools = this.page.querySelector('.wy-tools');
    if (tb) tb.after(panel); else if (tools) tools.after(panel); else this.page.append(panel);
    this._panel = panel;
  },
  closePanel() { if (this._panel) { this._panel.remove(); this._panel = null; } },
  showBanner(text, actionLabel, action, extra) {
    const b = this.$('editBanner'); if (!b) return;
    b.innerHTML = ''; b.hidden = false; b.append(h('span', {}, text));
    if (actionLabel) b.append(h('button', { class: 'btn primary', type: 'button', onclick: action }, actionLabel));
    if (extra) b.append(h('button', { class: 'btn', type: 'button', onclick: extra[1] }, extra[0]));
  },
  hideBanner() { const b = this.$('editBanner'); if (b) b.hidden = true; },
  newModule() {
    const name = prompt('新模組的名稱（可含資料夾，例如「專案/想法」）：');
    if (name) this.createModule(name);
  },
  async createModule(name) {
    if (!this.canEdit()) { this.toast('目前的來源不能建立檔案', true); return; }
    name = Util.norm(String(name || '')).trim().replace(/\.md$/i, '').replace(/\\/g, '/').replace(/^\/+|\/+$/g, '');
    if (!name || name.split('/').some(s => !s.trim() || s === '..' || s === '.')) { this.toast('名稱不合法', true); return; }
    const exist = Store.resolve(name);
    if (exist) { location.hash = Util.hashFor(exist.id); return; }
    const path = name + '.md', text = CONFIG.newModuleTemplate(Util.basename(name));
    try {
      const r = await this.source.save(path, text);
      const m = Parse.module(text, path); m.mtime = (r && r.mtime) || Date.now();
      Store.upsert(m); Store.reindex(); this.renderSidebar(); this.updateCache();
      this.toast('已建立 ' + path); this.edit(m.id);
    } catch (e) { this.toast('建立失敗：' + (e.message || e), true); }
  },

  /* ---------- 側欄：樹狀（R24、D22）；有搜尋字時改平面列表 ---------- */
  renderSidebar() {
    const list = this.$('list'); const q = (this.$('search').value || '').trim().toLowerCase();
    list.innerHTML = '';
    const pq = this.parseQuery(q);
    const mods = Store.list().filter(m => !q || this.matchQuery(m, pq));
    this.$('count').textContent = q ? `${mods.length} / ${Store.modules.size} 個模組` : `${Store.modules.size} 個模組`;
    const nb = Store.brokenLinks().length, lb = this.$('linksBtn');
    lb.hidden = !nb; lb.textContent = `${nb} 個壞連結`; lb.title = '有連結指向不存在的模組，按一下查看';
    if (!mods.length) { list.append(h('div', { class: 'empty-hint' }, Store.modules.size ? '沒有符合的模組' : '還沒有模組')); return; }
    const home = this.homeId();
    if (q) {   // 搜尋：平面列表，依資料夾分組
      const groups = new Map();
      for (const m of mods) { const d = Util.dirname(m.path); if (!groups.has(d)) groups.set(d, []); groups.get(d).push(m); }
      for (const [dir, arr] of [...groups.entries()].sort((a, b) => Util.collator.compare(a[0], b[0]))) {
        const g = h('div', { class: 'grp' });
        if (dir) g.append(h('div', { class: 'grp-name' }, dir));
        for (const m of arr.sort((a, b) => (b.id === home) - (a.id === home) || Util.collator.compare(a.title, b.title))) {
          const row = this.treeRow({ name: Util.basename(m.id), path: m.id, mod: m, children: new Map() }, 0, false, false);
          const snip = this.snippet(m, pq.words); if (snip) row.append(snip);   // 全文搜尋：命中片段（R39）
          g.append(row);
        }
        list.append(g);
      }
    } else {
      this.renderTree(this.buildTree(mods), 0, list, home);
      this.renderTagSection(list);
    }
    this.markSidebar();
  },
  /* 側欄底下的「標籤」節點（R37）：展開列出所有標籤與數量，點了就篩選 */
  renderTagSection(list) {
    const tags = Store.tags(); if (!tags.length) return;
    const open = Memory.treeOpen('__tags');
    const row = h('div', { class: 'item folder tags-row' + (open ? ' open' : ''), dataset: { node: '__tags' }, style: '--d:0', 'aria-expanded': String(open) });
    const chev = h('button', { class: 'chev', type: 'button', tabindex: '-1', html: ICON.chev });
    chev.addEventListener('click', e => { e.preventDefault(); e.stopPropagation(); this.toggleNode('__tags'); });
    row.append(chev, h('span', { class: 'name' }, '標籤'), h('span', { class: 'sub' }, `${tags.length} 個`));
    row.addEventListener('click', () => this.toggleNode('__tags'));
    list.append(row);
    if (open) list.append(h('div', { class: 'kids tag-list', dataset: { node: '__tags' } }, tags.map(([t, n]) => h('a', { class: 'item tag-item', href: '#', style: '--d:1', dataset: { tag: t }, onclick: e => { e.preventDefault(); this.searchTag(t); } }, h('span', { class: 'chev none' }), h('span', { class: 'name' }, '#' + t), h('span', { class: 'cnt' }, String(n))))));
  },
  /* 把模組路徑整理成樹：X.md 與 X/ 合併成一個節點；沒有同名模組的資料夾是純資料夾節點 */
  buildTree(mods) {
    const root = { name: '', path: '', mod: null, children: new Map() };
    const dirNode = path => {
      let node = root;
      if (!path) return node;
      for (const seg of path.split('/')) {
        const p = node.path ? node.path + '/' + seg : seg;
        if (!node.children.has(seg)) node.children.set(seg, { name: seg, path: p, mod: null, children: new Map() });
        node = node.children.get(seg);
      }
      return node;
    };
    for (const m of mods) {
      const parent = dirNode(Util.dirname(m.path)), name = Util.basename(m.id);
      if (parent.children.has(name)) parent.children.get(name).mod = m;
      else parent.children.set(name, { name, path: m.id, mod: m, children: new Map() });
    }
    return root;
  },
  renderTree(node, depth, container, home) {
    const entries = [...node.children.values()].sort((a, b) => (b.mod?.id === home) - (a.mod?.id === home) || Util.collator.compare(a.mod ? a.mod.title : a.name, b.mod ? b.mod.title : b.name));
    for (const n of entries) {
      const hasKids = n.children.size > 0, open = hasKids && Memory.treeOpen(n.path);
      container.append(this.treeRow(n, depth, hasKids, open));
      if (open) { const kids = h('div', { class: 'kids', dataset: { node: n.path } }); this.renderTree(n, depth + 1, kids, home); container.append(kids); }
    }
  },
  treeRow(n, depth, hasKids, open) {
    const row = h(n.mod ? 'a' : 'div', { class: 'item' + (n.mod ? '' : ' folder') + (open ? ' open' : ''), href: n.mod ? Util.hashFor(n.mod.id) : null, dataset: n.mod ? { id: n.mod.id, node: n.path } : { node: n.path }, style: `--d:${depth}`, title: n.mod ? n.mod.path : n.path + '/', 'aria-expanded': hasKids ? String(open) : null });
    const chev = h('button', { class: 'chev' + (hasKids ? '' : ' none'), type: 'button', tabindex: '-1', title: hasKids ? (open ? '收起' : '展開') : null, 'aria-label': hasKids ? '展開或收起' : null, html: ICON.chev });
    chev.addEventListener('click', e => { e.preventDefault(); e.stopPropagation(); this.toggleNode(n.path); });
    row.append(chev, h('span', { class: 'name', html: n.mod ? Util.titleHtml(n.mod.title) : Util.esc(n.name) }));
    if (n.mod && Util.basename(n.mod.id) !== n.mod.title) row.append(h('span', { class: 'sub' }, Util.basename(n.mod.path)));
    if (!n.mod) row.addEventListener('click', () => this.toggleNode(n.path));
    return row;
  },
  toggleNode(path) { Memory.setTreeOpen(path, !Memory.treeOpen(path)); this.renderSidebar(); },
  markSidebar() {
    const list = this.$('list'), id = this.currentId;
    // 目前模組被收在某個節點裡 → 先展開它的祖先（只在樹狀模式下）
    if (id && !(this.$('search').value || '').trim() && !list.querySelector(`.item[data-id="${CSS.escape(id)}"]`)) {
      const segs = id.split('/'); let changed = false;
      for (let i = 1; i < segs.length; i++) { const p = segs.slice(0, i).join('/'); if (!Memory.treeOpen(p)) { Memory.setTreeOpen(p, true); changed = true; } }
      if (changed) { this.renderSidebar(); return; }
    }
    list.querySelectorAll('.item').forEach(a => { const on = !!id && a.dataset.id === id; a.classList.toggle('on', on); if (on && typeof a.scrollIntoView === 'function') { const r = a.getBoundingClientRect(), l = list.getBoundingClientRect(); if (r.top < l.top || r.bottom > l.bottom) a.scrollIntoView({ block: 'nearest' }); } });
  },

  /* ---------- 歡迎畫面 ---------- */
  renderWelcome() {
    this.currentId = null; this.page.innerHTML = '';
    const fsa = FolderSource.supported(), ios = Util.isIOS();
    const way = (title, desc, ...btns) => h('div', { class: 'way' }, h('h3', {}, title), h('p', {}, desc), btns.length ? h('div', { style: 'display:flex;gap:6px;flex-wrap:wrap' }, btns) : null);
    const btn = (label, cls, fn) => h('button', { class: 'btn ' + cls, type: 'button', onclick: fn }, label);
    const ways = [];
    if (this.pendingHandle) ways.push(way(`繼續上次：${this.pendingHandle.name}`, '這個頁面記得上次匯入的資料夾，按一下重新取得權限就能繼續。', btn('重新連接', 'primary', () => this.reopen())));
    if (fsa) ways.push(way('匯入資料夾', '選擇放 .md 檔的資料夾。用任何編輯器改檔，頁面會自動更新；也能直接在這裡編輯、存回檔案。只要匯入一次，之後打開會記得。', btn('匯入資料夾', this.pendingHandle ? '' : 'primary', () => this.pickFolder())));
    ways.push(way(ios ? '從「檔案」匯入' : '匯入檔案或資料夾（唯讀）',
      ios ? '在「檔案」裡多選 .md 檔匯入。內容會留在這台裝置的瀏覽器裡，下次打開直接可讀。'
          : '任何瀏覽器都能用，但不能寫回檔案；匯入的內容會記住，下次打開直接可讀。也可以直接把資料夾拖進這個視窗。',
      btn('匯入檔案', fsa ? '' : 'primary', () => this.$('pickFiles').click()), !ios ? btn('匯入資料夾', '', () => this.$('pickDir').click()) : null));
    ways.push(way(fsa ? '本機小伺服器' : '本機小伺服器（Safari／Firefox 要編輯請用這個）',
      '在筆記資料夾裡雙擊「啟動筆記.command」（Windows：啟動筆記.bat），或在終端機執行 python3 serve.py，再打開 http://localhost:8765 。任何瀏覽器都能看、能編輯、能貼圖；同一個 Wi‑Fi 的 iPad 也連得上。'));
    const sample = '# 筆記一\n\n## 摘要\n一兩句話說這篇在講什麼。\n\n## 內文\n內文裡可以裝其他模組：\n\n[[第一小點|全文]]\n[[第二小點|摘要]]\n也可以在句子中間提到 [[第一小點]]。';
    const w = h('div', { class: 'welcome' },
      h('h1', {}, '筆記模組'),
      h('p', { class: 'lead' }, '每個 .md 檔就是一個模組：標題、摘要、內文。模組裡用 [[模組名|模式]] 裝進別的模組，點一下就能展開。先把筆記匯入進來：'),
      h('div', { class: 'ways' }, ways),
      h('div', { class: 'dropzone' }, '把資料夾或 .md 檔拖到這個視窗也可以'),
      h('div', { class: 'md', style: 'margin-top:18px' }, h('p', { class: 'note', style: 'margin-bottom:6px' }, '一個模組檔案長這樣：'), h('pre', {}, h('code', {}, sample))),
      h('p', { class: 'fine' }, '每一份 index.html 各自記住自己匯入的內容（記憶跟這個檔案的路徑綁在一起）。想同時管理好幾個資料夾，就把 index.html 複製一份到每個資料夾裡，各自匯入一次。右上角的選單隨時可以重新匯入或忘記。要放到 GitHub Pages：把資料夾推上去，附的 GitHub Actions 會自動產生 modules.json。要做成單一檔案（例如丟到 iPad）：python3 build.py。'),
    );
    this.page.append(w); document.title = CONFIG.appName;
  },
  async pickFolder() {
    try {
      const handle = await FolderSource.pick(); if (!handle) return;
      const src = new FolderSource(handle);
      if (!await src.ensurePermission(true)) { this.toast('沒有取得讀取權限', true); return; }
      await this.useSource(src);
      this.toast(`已匯入「${handle.name}」` + (src.writable ? '，已記住' : '（唯讀）'));
    } catch (e) { console.error(e); this.toast('無法開啟資料夾：' + (e.message || e), true); }
  },
  async reopen() {
    if (!this.pendingHandle) return false;
    const src = new FolderSource(this.pendingHandle);
    if (await src.ensurePermission(true)) { this.pendingHandle = null; await this.useSource(src); if (!src.writable) this.toast('只拿到「檢視」權限；要編輯請重新匯入並允許「編輯」', true); return src.writable; }
    this.toast('沒有取得權限', true); return false;
  },
  /* 說明目前為什麼是唯讀，以及怎麼變成可編輯 */
  explainReadOnly() {
    const src = this.source, fsa = FolderSource.supported();
    let text, label, fn;
    if (this.pendingHandle) { text = '目前顯示的是上次的快取。瀏覽器規定每次重開頁面都要再按一下，才允許網頁寫入資料夾。'; label = '重新連接資料夾'; fn = () => this.reopen(); }
    else if (src && src.kind === 'folder' && !src.writable) { text = '這個資料夾只拿到「檢視」權限。重新匯入一次，在瀏覽器詢問時選擇允許「編輯」。'; label = '重新匯入資料夾'; fn = () => this.pickFolder(); }
    else if (src && src.kind === 'embedded') { text = '這是用 build.py 打包成單一檔案的快照，不能編輯。請打開 index.html 匯入原始資料夾。'; }
    else if (src && src.kind === 'http' && src.github) { text = '這是 GitHub Pages 版本。輸入一次 GitHub token 就能在這裡直接編輯（和電腦上同一套編輯器），存檔會自動 commit 回倉庫。'; label = '啟用直接編輯'; fn = () => this.githubTokenPanel(); }
    else if (src && src.kind === 'http') { text = '這是靜態網站版本，改檔案要透過原始檔案的主人（或改用 serve.py 啟動的本機伺服器）。'; }
    else if (fsa) { text = '用拖放或選檔匯入的內容，瀏覽器不允許寫回原檔。改用「匯入資料夾…（可編輯）」重新匯入一次，之後就能直接編輯、貼圖，改檔也會自動更新。'; label = '匯入資料夾（可編輯）'; fn = () => this.pickFolder(); }
    else { text = 'Safari 與 Firefox 沒有讓網頁寫入資料夾的功能。最簡單的做法：在筆記資料夾裡雙擊「啟動筆記.command」（Windows 用「啟動筆記.bat」），再用瀏覽器打開 http://localhost:8765 ，就能編輯、貼圖、自動更新。或者改用 Chrome／Edge 開這個 index.html。'; label = '複製網址 http://localhost:8765'; fn = async () => { try { await navigator.clipboard.writeText('http://localhost:8765/'); this.toast('已複製'); } catch { this.toast('請手動輸入 http://localhost:8765', true); } }; }
    this.showNotice(text, label, fn);
    this.main.scrollTop = 0;
  },
  async loadEntries(result) {
    const { root, entries } = result;
    if (!entries.some(e => Util.isMd(e.path))) { this.toast('沒有找到 .md 檔', true); return; }
    if (await this.useSource(new FilesSource(entries, root || `${entries.length} 個檔案`)) !== false) this.toast(`已匯入 ${Store.modules.size} 個模組（唯讀，已記住）`);
  },
  async reload() {
    if (!this.source) return;
    if (this.source.kind === 'folder' || this.source.kind === 'http' || this.source.kind === 'embedded') { await this.useSource(this.source); this.toast('已重新讀取'); }
    else this.toast('這是匯入時的快照，要更新請再匯入一次', true);
  },

  /* ---------- 介面雜項 ---------- */
  bindUI() {
    this.$('railToggle').addEventListener('click', () => document.body.classList.toggle('rail-open'));
    this.$('scrim').addEventListener('click', () => document.body.classList.remove('rail-open'));
    this.$('themeBtn').addEventListener('click', () => Theme.toggle());
    document.addEventListener('click', e => { const m = this.$('srcMenu'); if (m && m.open && !m.contains(e.target)) m.open = false; });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') { const m = this.$('srcMenu'); if (m) m.open = false; } });
    this.$('newBtn').addEventListener('click', () => this.newModule());
    this.$('brand').addEventListener('click', e => { e.preventDefault(); if (!this.source) return; const id = this.homeId(); if (id) { if (location.hash === Util.hashFor(id)) this.onHash(); else location.hash = Util.hashFor(id); } });
    this.$('search').addEventListener('input', Util.debounce(() => { this.renderSidebar(); if (this.currentId && !Editor.open) this.refresh(); }, 120));
    this.page.addEventListener('click', e => { const a = e.target.closest('a.card-title, a.chip-go, a.mod-link'); if (a && !a.closest('.backlinks, .crumbs')) this._navFrom = this.currentId; });   // 麵包屑：記住從哪一頁點進去
    this.$('search').addEventListener('keydown', e => { if (e.key === 'Escape') { e.target.value = ''; this.renderSidebar(); e.target.blur(); } });
    this.$('pickFiles').addEventListener('change', e => { if (e.target.files.length) this.loadEntries(FilesSource.fromInput(e.target.files)); e.target.value = ''; });
    this.$('pickDir').addEventListener('change', e => { if (e.target.files.length) this.loadEntries(FilesSource.fromInput(e.target.files)); e.target.value = ''; });
    let dragDepth = 0;
    document.addEventListener('dragenter', e => { if ([...e.dataTransfer.types].includes('Files')) { dragDepth++; document.body.classList.add('dragging'); } });
    document.addEventListener('dragleave', () => { if (--dragDepth <= 0) { dragDepth = 0; document.body.classList.remove('dragging'); } });
    document.addEventListener('dragover', e => { if ([...e.dataTransfer.types].includes('Files')) e.preventDefault(); });
    document.addEventListener('drop', async e => {
      dragDepth = 0; document.body.classList.remove('dragging');
      if (![...e.dataTransfer.types].includes('Files')) return;
      if (e.target && e.target.closest && e.target.closest('.editor textarea')) return;   // 編輯器自己處理（圖片）
      e.preventDefault();
      try { this.loadEntries(await FilesSource.fromDrop(e.dataTransfer)); } catch (err) { this.toast('讀取失敗：' + (err.message || err), true); }
    });
    document.addEventListener('keydown', e => {
      const tag = (e.target.tagName || '').toLowerCase();
      const typing = tag === 'input' || tag === 'textarea' || e.target.isContentEditable;
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 's') { if (Editor.open && this.canEdit()) { e.preventDefault(); Editor.save(); } return; }
      if (e.key === '/' && !typing) { e.preventDefault(); this.$('search').focus(); }
    });
    window.addEventListener('beforeunload', e => { if (Editor.open && Editor.dirty) { e.preventDefault(); e.returnValue = ''; } });
    document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') this.writeCache(); });
  },
  updateChrome() {
    this.$('newBtn').hidden = !this.canEdit();
    this.setStatus(); this.buildSourceMenu();
  },
  /* 頂列「匯入／來源」選單：任何時候都能換來源、重新載入或忘記 */
  buildSourceMenu() {
    const pop = this.$('srcPop'), btn = this.$('srcBtn'); if (!pop) return;
    pop.innerHTML = '';
    const src = this.source, ios = Util.isIOS();
    btn.textContent = src ? '來源 ▾' : '匯入 ▾';
    const mi = (label, fn, cls = '') => h('button', { class: 'mi ' + cls, type: 'button', onclick: () => { this.$('srcMenu').open = false; fn(); } }, label);
    const where = PROFILE.split('/').slice(-2).join('/');
    pop.append(h('div', { class: 'menu-head' }, src ? this.$('status').querySelector('.txt').textContent : '尚未匯入任何筆記', h('br'), h('span', { class: 'note' }, '記憶綁定在：…/' + where)));
    if (this.pendingHandle) pop.append(mi(`重新連接資料夾「${this.pendingHandle.name}」`, () => this.reopen(), 'strong'));
    if (FolderSource.supported()) pop.append(mi('匯入資料夾…（可編輯、自動更新）', () => this.pickFolder()));
    pop.append(mi(ios ? '從「檔案」匯入…' : '匯入檔案…（唯讀）', () => this.$('pickFiles').click()));
    if (!ios) pop.append(mi('匯入資料夾…（唯讀，任何瀏覽器）', () => this.$('pickDir').click()));
    if (src && src.kind === 'http' && src.github) {
      if (!src.token) pop.append(mi('啟用直接編輯（輸入 GitHub token）…', () => this.githubTokenPanel(), 'strong'));
      else { pop.append(mi('更換 GitHub token…', () => this.githubTokenPanel())); pop.append(mi('停用直接編輯（清除這台裝置的 token）', () => { src.disableToken(); this.updateChrome(); this.show(this.currentId, true); this.toast('已清除 token，回到唯讀'); })); }
    }
    if (src && (src.kind === 'folder' || src.kind === 'http')) pop.append(mi('重新載入', () => this.reload()));
    if (src && !src.writable && !(src.editUrl && src.kind === 'http')) pop.append(mi('為什麼是唯讀？', () => this.explainReadOnly()));
    if ((src && src.kind !== 'embedded' && src.kind !== 'http') || this.pendingHandle) pop.append(h('div', { class: 'menu-sep' }), mi('忘記匯入的內容，回到起點', () => this.forget(), 'danger'));
  },
  setStatus(text, cls) {
    const s = this.$('status'), dot = s.querySelector('.dot'), txt = s.querySelector('.txt');
    dot.className = 'dot' + (cls ? ' ' + cls : '');
    if (text) { txt.textContent = text; this.$('railStatus').textContent = text; return; }
    if (!this.source) { txt.textContent = '尚未載入'; this.$('railStatus').textContent = '尚未載入'; return; }
    const src = this.source, n = Store.modules.size;
    const bits = [src.label, `${n} 個模組`];
    if (src.kind === 'cache') bits.push('上次匯入 ' + Util.fmtTime(src.when));
    if (src.watch) bits.push('自動更新');
    bits.push(src.writable ? '可編輯' : '唯讀');
    txt.textContent = bits.join(' · '); txt.title = txt.textContent; this.$('railStatus').textContent = txt.textContent;
    dot.className = 'dot' + (src.watch ? ' live' : (src.kind === 'cache' ? ' warn' : ''));
  },
  toast(msg, isErr) {
    const t = this.$('toast'); t.textContent = msg; t.className = 'show' + (isErr ? ' err' : '');
    clearTimeout(this._toastT); this._toastT = setTimeout(() => { t.className = ''; }, isErr ? 4200 : 2200);
  },
};

let _booted = false;
function boot() { if (_booted) return; _booted = true; App.init().catch(e => { console.error(e); App.toast('啟動時發生錯誤：' + (e.message || e), true); }); }
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
