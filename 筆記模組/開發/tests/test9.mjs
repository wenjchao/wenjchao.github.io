// 測試九：所見即所得編輯器（R25）——全部模組來回轉換畫面相同、打字與工具列操作後存檔正確、原子保留、兩種模式互切
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
const ROOT = process.env.ROOT, HERE = process.env.HERE, TMP = process.env.TMP || '/tmp';

const browser = await chromium.launch();
const errors = [];

/* ---------- 一、來回轉換：ROOT 裡所有 .md（範例＋說明文件）渲染→序列化→再渲染，畫面 HTML 要一樣 ---------- */
{
  const ctx = await browser.newContext({ viewport: { width: 1200, height: 800 }, locale: 'zh-TW' });
  const page = await ctx.newPage(); page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  await page.goto('file://' + TMP + '/single.html'); await page.waitForSelector('.root');
  const files = fs.readdirSync(ROOT, { recursive: true }).filter(f => f.endsWith('.md') && !f.startsWith('開發')).map(f => path.join(ROOT, f));
  const tricky = '# 刁鑽\n\n## 摘要\n一顆 $5 和 $10，a_b、*星號*、`code`、[方括號]、~~刪除~~、<u>底線</u>、<mark>螢光</mark>、H<sub>2</sub>O\n\n## 內文\n- 項目一\n- 項目二\n  - 巢狀\n\n1. 一\n2. 二\n\n- [ ] 待辦\n- [x] 完成\n\n> 引言\n> 第二行\n\n```js\nconst a = 1;\n```\n\n| a | b |\n|---|---|\n| 1 | 2\\|3 |\n\n$$\nE = mc^2\n$$\n\n行內 $x^2$ 數學。\n\n![](圖片/a.png)\n\n---\n\n[[第一小點|摘要]]\n\n句中 [[第一小點]] 晶片。\n\n1. 緊湊清單\n   > 項目下的引言\n2. 第二項\n';
  const norm = s => s.replace(/\s+/g, ' ').replace(/> </g, '><').replace(/ data-raw="[^"]*"/g, '').replace(/ data-ref="[^"]*"/g, '').trim();
  const cases = files.map(f => [path.relative(ROOT, f), fs.readFileSync(f, 'utf8')]).concat([['刁鑽.md', tricky]]);
  let n = 0;
  for (const [name, md] of cases) {
    const r = await page.evaluate(({ md, name }) => {
      const base = name.includes('/') ? name.slice(0, name.lastIndexOf('/')) : '';
      const m = Parse.module(md, name);
      const f = Wysi.field(m.body, base), s = Wysi.field(m.summary, base); document.body.append(f, s);
      const body2 = Wysi.toMarkdown(f), sum2 = Wysi.toMarkdown(s); f.remove(); s.remove();
      const m2 = Parse.module('# ' + m.title + '\n\n## 摘要\n' + sum2 + '\n\n## 內文\n' + body2 + '\n', name);
      return { a: MD.render(m.summary) + '|' + MD.render(m.body), b: MD.render(m2.summary) + '|' + MD.render(m2.body), md2: sum2 + '\n' + body2 };
    }, { md, name });
    assert.equal(norm(r.b), norm(r.a), `round-trip 不同：${name}\n${r.md2}`);
    n++;
  }
  console.log(`round-trip ok: ${n} 個檔案`);
  await ctx.close();
}

/* ---------- 二、互動：假的資料夾（可寫）→ 直觀編輯 → 存檔 ---------- */
const files = fs.readdirSync(ROOT, { recursive: true }).filter(f => f.endsWith('.md') && (!f.includes('/') || f.startsWith('範例/'))).map(f => ({ name: f, text: fs.readFileSync(path.join(ROOT, f), 'utf8') }));   // 根目錄的模組＋範例/
const ctx = await browser.newContext({ viewport: { width: 1200, height: 900 }, locale: 'zh-TW' });
await ctx.addInitScript(({ files }) => {
  class FH { constructor(dir, name) { this.kind = 'file'; this.dir = dir; this.name = name; }
    async getFile() { const r = this.dir.files.get(this.name); return new File([r.text], this.name, { lastModified: r.mtime }); }
    async createWritable() { let buf = ''; const dir = this.dir, name = this.name; return { async write(t) { buf += (typeof t === 'string') ? t : ''; }, async close() { dir.files.set(name, { text: buf, mtime: Date.now() }); } }; } }
  class DH { constructor(name) { this.kind = 'directory'; this.name = name; this.files = new Map(); this.dirs = new Map(); this.perm = 'granted'; }
    async *entries() { for (const n of this.files.keys()) yield [n, new FH(this, n)]; for (const [n, d] of this.dirs) yield [n, d]; }
    async getDirectoryHandle(n, o) { if (!this.dirs.has(n)) { if (!o?.create) throw new Error('NotFound'); this.dirs.set(n, new DH(n)); } return this.dirs.get(n); }
    async getFileHandle(n, o) { if (!this.files.has(n)) { if (!o?.create) throw new Error('NotFound'); this.files.set(n, { text: '', mtime: Date.now() }); } return new FH(this, n); }
    async queryPermission() { return this.perm; } async requestPermission() { return this.perm; } }
  const root = new DH('測試資料夾');
  const putFile = (dir, name, rec) => { const i = name.indexOf('/'); if (i < 0) dir.files.set(name, rec); else { const d = name.slice(0, i); if (!dir.dirs.has(d)) dir.dirs.set(d, new DH(d)); putFile(dir.dirs.get(d), name.slice(i + 1), rec); } };   // 路徑含資料夾 → 巢狀 DH（範例模組在 範例/）
  const at = n => { let d = root; const ps = n.split('/'); const last = ps.pop(); for (const p of ps) d = d && d.dirs.get(p); return [d ? d.files : null, last]; };
  window.__get = n => { const [m, k] = at(n); return m && m.get(k); }; window.__set = (n, rec) => { const [m, k] = at(n); m.set(k, rec); }; window.__fileText = n => window.__get(n)?.text;
  for (const f of files) putFile(root, f.name, { text: f.text, mtime: Date.now() - 10000 });
  window.__root = root;
  window.showDirectoryPicker = async () => root;
  const put = IDBObjectStore.prototype.put; IDBObjectStore.prototype.put = function (v, k) { if (v === root) v = { __fakeHandle: true }; return put.call(this, v, k); };
  const d = Object.getOwnPropertyDescriptor(IDBRequest.prototype, 'result');
  Object.defineProperty(IDBRequest.prototype, 'result', { get() { const r = d.get.call(this); return (r && r.__fakeHandle) ? root : r; } });
}, { files });
const page = await ctx.newPage(); page.on('pageerror', e => errors.push('pageerror: ' + e.message));
await page.goto('file://' + ROOT + '/index.html'); await page.waitForSelector('.welcome');
await page.click('.welcome button:has-text("匯入資料夾")');
await page.waitForSelector('.root');
await page.goto('file://' + ROOT + '/index.html#/' + encodeURIComponent('範例/第二小點')); await page.waitForSelector('.root-title');
await page.click('.toolbar >> text=編輯');
await page.waitForSelector('.editor.wysiwyg');
// 預設是直觀編輯：三個區域都在
assert.equal(await page.inputValue('.wy-title'), '第二小點');
assert.equal(await page.$$eval('.wy-field', fs => fs.length), 2);
assert.ok(await page.$('.ed-bar .mode-seg button.on[data-mode="wysiwyg"]'));

// 在內文最後面打字＋粗體＋自動清單
const body = page.locator('.wy-field').nth(1);
await body.click();
await page.keyboard.press('Control+End');
await page.keyboard.press('Enter'); await page.keyboard.press('Enter');   // 原本結尾是清單：Enter 兩次離開清單
await page.keyboard.type('瀏覽器裡加的一段');
// 選最後三個字設粗體，再把粗體關掉
for (let i = 0; i < 3; i++) await page.keyboard.press('Shift+ArrowLeft');
await page.click('.wy-btn.b');
await page.keyboard.press('End');
await page.click('.wy-btn.b');
await page.keyboard.press('Enter');
await page.keyboard.type('- 第一個項目');
await page.keyboard.press('Enter');
await page.keyboard.type('第二個項目');
assert.ok(await page.$('.wy-field li'), '行首打「- 」要變成清單');
// 插入模組卡片
await page.click('.wy-btn:has-text("模組")');
await page.waitForSelector('.wy-panel');
await page.fill('.wy-panel .wy-q', '第一小點');
await page.click('.wy-panel .wy-result:has-text("第一小點")');
await page.click('.wy-panel .btn.primary');
await page.waitForSelector('.wy-field .wy-card');
assert.equal(await page.$eval('.wy-field .wy-card', c => c.dataset.md), '[[第一小點|摘要]]');
// 插入數學式（晶片形式）
await page.click('.wy-btn:has-text("數學")');
await page.waitForSelector('.wy-panel .wy-tex');
await page.fill('.wy-panel .wy-tex', 'x^2');
await page.click('.wy-panel .btn.primary');
await page.waitForSelector('.wy-field .wy-math');
// 切到原始碼：要看到序列化結果
await page.click('.ed-bar .mode-seg button[data-mode="source"]');
await page.waitForSelector('.editor textarea');
let src = await page.inputValue('.editor textarea');
console.log('--- 序列化結果 ---\n' + src);
assert.ok(src.startsWith('# 第二小點\n'), src);
assert.ok(src.includes('瀏覽器裡加**的一段**'), '粗體：' + src);
assert.ok(/\n- 第一個項目\n- 第二個項目/.test(src), '清單');
assert.ok(src.includes('\n[[第一小點|摘要]]\n'), '卡片原子');
assert.ok(src.includes('$x^2$'), '數學式');
// 在原始碼模式加一行，再切回直觀，內容要跟著
await page.fill('.editor textarea', src + '\n原始碼加的一行\n');
await page.click('.ed-bar .mode-seg button[data-mode="wysiwyg"]');
await page.waitForSelector('.editor.wysiwyg');
assert.ok((await body.textContent()).includes('原始碼加的一行'));
// 存檔 → 假資料夾裡的檔案
await page.click('.ed-bar >> text=儲存');
await page.waitForFunction(() => !document.querySelector('.editor') && document.querySelector('.root-body'));
const saved = await page.evaluate(() => window.__fileText('範例/第二小點.md'));
console.log('--- 存檔內容 ---\n' + saved);
assert.ok(saved.includes('瀏覽器裡加**的一段**') && saved.includes('[[第一小點|摘要]]') && saved.includes('$x^2$') && saved.includes('原始碼加的一行'));
assert.ok(await page.$('.root-body .card[data-id="範例/第一小點"]'), '存檔後畫面上有卡片');
assert.ok(await page.$('.root-body .katex'), '存檔後數學式有渲染');
// 上次用的模式會記住（剛才最後是直觀）；再開編輯器應是直觀
await page.click('.toolbar >> text=編輯'); await page.waitForSelector('.editor.wysiwyg');
// 標題也能改：改標題後存檔
await page.fill('.wy-title', '第二小點（改名）');
await page.click('.ed-bar >> text=儲存');
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '第二小點（改名）');
assert.ok((await page.evaluate(() => window.__fileText('範例/第二小點.md'))).startsWith('# 第二小點（改名）\n'));
// 外部修改（沒有未存變更）→ 直觀編輯器自動載入
await page.click('.toolbar >> text=編輯'); await page.waitForSelector('.editor.wysiwyg');
await page.evaluate(() => { window.__set('範例/第二小點.md', { text: '# 第二小點\n\n## 摘要\n外部寫的摘要\n\n## 內文\n外部內文\n', mtime: Date.now() }); });
await page.waitForFunction(() => document.querySelector('.wy-field')?.textContent.includes('外部寫的摘要'), null, { timeout: 8000 });
await page.click('.toolbar >> text=取消');

// R28：編輯列釘在頂端——模式切換、格式鈕、儲存都在同一條 sticky 的列上
await page.click('.toolbar >> text=編輯'); await page.waitForSelector('.editor.wysiwyg');
const bar = await page.$eval('.ed-bar', b => ({ pos: getComputedStyle(b).position, seg: b.querySelector('.mode-seg') != null, fmt: b.querySelector('.wy-fmt .wy-btn') != null, save: [...b.querySelectorAll('button')].some(x => x.textContent === '儲存'), modes: [...b.querySelectorAll('.mode-seg button')].map(x => x.dataset.mode).join(',') }));
assert.deepEqual(bar, { pos: 'sticky', seg: true, fmt: true, save: true, modes: 'wysiwyg,source,split' });
await page.click('.ed-bar .mode-seg button[data-mode="source"]');
assert.equal(await page.$eval('.ed-bar .wy-fmt .wy-btn', b => b.getClientRects().length), 0, '原始碼模式不顯示格式鈕');
assert.ok(await page.$('.ed-bar .mode-seg button.on[data-mode="source"]'));

// R29：並排模式——左直觀、右原始碼，兩邊同步
await page.click('.ed-bar .mode-seg button[data-mode="split"]');
await page.waitForSelector('.editor.split .ed-split');
assert.ok(await page.$('.ed-left .wy-doc') && await page.$('.ed-right textarea'), '左邊直觀、右邊原始碼');
assert.ok(await page.$('.ed-bar .wy-fmt .wy-btn'), '並排模式有格式鈕');
// 右邊打字 → 左邊跟著變
const ta9 = page.locator('.ed-right textarea');
await ta9.focus();
await page.keyboard.press('Control+End');
await page.keyboard.type('\n右邊打的**新段落**\n');
await page.waitForFunction(() => document.querySelector('.ed-left .wy-field:last-of-type')?.innerHTML.includes('右邊打的<strong>新段落</strong>'), null, { timeout: 4000 });
// 左邊打字 → 右邊原始碼跟著更新
const body9 = page.locator('.ed-left .wy-field').nth(1);
await body9.click(); await page.keyboard.press('Control+End'); await page.keyboard.press('Enter'); await page.keyboard.type('左邊打的一行');
await page.waitForFunction(() => document.querySelector('.ed-right textarea')?.value.includes('左邊打的一行'), null, { timeout: 4000 });
assert.ok((await page.inputValue('.ed-right textarea')).includes('右邊打的**新段落**'), '右邊先打的要還在');
// 儲存：兩邊的修改都要進檔案；模式記住為並排
await page.click('.ed-bar >> text=儲存');
await page.waitForFunction(() => !document.querySelector('.editor') && document.querySelector('.root-body'));
const saved9 = await page.evaluate(() => window.__fileText('範例/第二小點.md'));
assert.ok(saved9.includes('右邊打的**新段落**') && saved9.includes('左邊打的一行'), saved9);
await page.click('.toolbar >> text=編輯'); await page.waitForSelector('.editor.split');
assert.ok(await page.$('.ed-bar .mode-seg button.on[data-mode="split"]'), '上次用並排，這次也是並排');
await page.click('.ed-bar .mode-seg button[data-mode="wysiwyg"]'); await page.waitForSelector('.editor.wysiwyg');
await page.click('.toolbar >> text=取消');
await ctx.close();

console.log('errors:', errors);
assert.equal(errors.length, 0, errors.join('\n'));
console.log('TEST9 OK');
await browser.close();
