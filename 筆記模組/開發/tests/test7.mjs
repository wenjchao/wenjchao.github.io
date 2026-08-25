// 測試七：KaTeX 數學式（行內、區塊、標題、程式碼裡不渲染、美元符號不誤判）、唯讀說明、快取狀態下「重新連接後編輯」
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
const ROOT = process.env.ROOT, HERE = process.env.HERE, TMP = process.env.TMP || '/tmp';

const D = path.join(TMP, 'math'); fs.rmSync(D, { recursive: true, force: true }); fs.mkdirSync(D);
fs.copyFileSync(path.join(ROOT, 'index.html'), path.join(D, 'index.html'));
const md = (name, text) => ({ name, mimeType: 'text/markdown', buffer: Buffer.from(text) });
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1200, height: 800 }, locale: 'zh-TW' });
const page = await ctx.newPage();
const errors = []; page.on('pageerror', e => errors.push('pageerror: ' + e.message));

await page.goto('file://' + D + '/index.html'); await page.waitForSelector('.welcome');
await page.setInputFiles('#pickFiles', [
  md('數學.md', '# 數學 $E=mc^2$\n\n## 摘要\n行內 $\\frac{a}{b}$ 與區塊。\n\n## 內文\n$$\\int_0^1 x^2\\,dx = \\tfrac{1}{3}$$\n\n也可以 \\(\\alpha+\\beta\\) 和\n\n\\[ \\sum_{i=1}^n i = \\frac{n(n+1)}{2} \\]\n\n價格 $5 和 $10 不是數學；NT$100 也不是。\n\n回歸 $10 之後接著一個 `$` 程式碼，再一個 `$x$`。\n\n`$x$` 在程式碼裡不渲染。\n\n```\n$$ 區塊程式碼裡也不渲染 $$\n```\n\n[[數學]]\n'),
]);
await page.waitForSelector('.root');
assert.ok((await page.$eval('.root-title', e => e.innerHTML)).includes('katex'), '根標題的 $E=mc^2$ 要渲染');
assert.ok((await page.$eval('#list .item[data-id="數學"]', e => e.innerHTML)).includes('katex'), '側欄標題也要渲染');
assert.ok((await page.$eval('.root-summary', e => e.innerHTML)).includes('katex'), '摘要裡的行內數學');
const body = await page.$eval('.root-body', e => e.innerHTML);
assert.equal((body.match(/class="katex-display"/g) || []).length, 2, '兩個區塊數學');
assert.ok(body.includes('α') || body.includes('alpha'), '\\(…\\) 行內');
assert.ok(body.includes('價格 $5 和 $10 不是數學；NT$100 也不是。'), '美元符號不應被當成數學：' + body.slice(body.indexOf('價格'), body.indexOf('價格') + 60));
assert.deepEqual(await page.$$eval('.root-body p code', cs => cs.map(c => c.textContent)), ['$', '$x$', '$x$'], '程式碼裡保持原樣');
// 孤零零的 $ 不可以跨過後面的行內程式碼去配對（回歸：寫作規範裡的走法段落曾被吃掉）
assert.ok(body.includes('回歸 $10 之後') && !body.includes('katex">回歸'), '孤立的 $ 不能跨過反引號配對：' + body.slice(body.indexOf('回歸'), body.indexOf('回歸') + 80));
assert.ok(body.includes('$$ 區塊程式碼裡也不渲染 $$'));
assert.ok(await page.$('.root-body .card[data-id="數學"] .card-title .katex'), '卡片標題也渲染');
const fontOk = await page.evaluate(async () => { await document.fonts.ready; return [...document.fonts].some(f => f.family === 'KaTeX_Main' && f.status === 'loaded'); });
assert.ok(fontOk, 'KaTeX 字型應已內嵌載入');

// 唯讀？（檔案匯入、Chromium 有 FSA）→ 提示改用匯入資料夾
await page.click('.toolbar >> text=唯讀？');
assert.equal(await page.$eval('#notice', n => n.hidden), false);
assert.ok((await page.textContent('#notice')).includes('匯入資料夾'));
await ctx.close();

// 快取 + 重新連接後編輯（假 FSA）
const files = fs.readdirSync(ROOT, { recursive: true }).filter(f => f.endsWith('.md') && (!f.includes('/') || f.startsWith('範例/'))).map(f => ({ name: f, text: fs.readFileSync(path.join(ROOT, f), 'utf8') }));   // 根目錄的模組＋範例/
const ctx2 = await browser.newContext({ viewport: { width: 1200, height: 800 }, locale: 'zh-TW' });
await ctx2.addInitScript(({ files }) => {
  class FH { constructor(dir, name) { this.kind = 'file'; this.dir = dir; this.name = name; }
    async getFile() { const r = this.dir.files.get(this.name); return new File([r.text], this.name, { lastModified: r.mtime }); }
    async createWritable() { let buf = ''; const dir = this.dir, name = this.name; return { async write(t) { buf += t; }, async close() { dir.files.set(name, { text: buf, mtime: Date.now() }); } }; } }
  class DH { constructor(name) { this.kind = 'directory'; this.name = name; this.files = new Map(); this.dirs = new Map(); this.perm = 'prompt'; }
    async *entries() { for (const n of this.files.keys()) yield [n, new FH(this, n)]; for (const [n, d] of this.dirs) yield [n, d]; }
    async getDirectoryHandle(n, o) { if (!this.dirs.has(n)) { if (!o?.create) throw new Error('NotFound'); this.dirs.set(n, new DH(n)); } return this.dirs.get(n); }
    async getFileHandle(n, o) { if (!this.files.has(n)) { if (!o?.create) throw new Error('NotFound'); this.files.set(n, { text: '', mtime: Date.now() }); } return new FH(this, n); }
    async queryPermission() { return this.perm; } async requestPermission() { this.perm = 'granted'; return 'granted'; } }
  const root = new DH('我的筆記');
  const putFile = (dir, name, rec) => { const i = name.indexOf('/'); if (i < 0) dir.files.set(name, rec); else { const d = name.slice(0, i); if (!dir.dirs.has(d)) dir.dirs.set(d, new DH(d)); putFile(dir.dirs.get(d), name.slice(i + 1), rec); } };   // 路徑含資料夾 → 巢狀 DH（範例模組在 範例/）
  const at = n => { let d = root; const ps = n.split('/'); const last = ps.pop(); for (const p of ps) d = d && d.dirs.get(p); return [d ? d.files : null, last]; };
  window.__get = n => { const [m, k] = at(n); return m && m.get(k); }; window.__set = (n, rec) => { const [m, k] = at(n); m.set(k, rec); }; window.__fileText = n => window.__get(n)?.text;
  for (const f of files) putFile(root, f.name, { text: f.text, mtime: Date.now() - 10000 });
  window.__root = root; window.showDirectoryPicker = async () => { root.perm = 'granted'; return root; };
  const put = IDBObjectStore.prototype.put; IDBObjectStore.prototype.put = function (v, k) { if (v === root) v = { __fakeHandle: true }; return put.call(this, v, k); };
  const d = Object.getOwnPropertyDescriptor(IDBRequest.prototype, 'result');
  Object.defineProperty(IDBRequest.prototype, 'result', { get() { const r = d.get.call(this); return (r && r.__fakeHandle) ? root : r; } });
}, { files });
const pc = await ctx2.newPage(); pc.on('pageerror', e => errors.push('pageerror C: ' + e.message));
await pc.goto('file://' + D + '/index.html'); await pc.waitForSelector('.welcome');
await pc.click('.welcome button:has-text("匯入資料夾")'); await pc.waitForSelector('.root');
await pc.waitForTimeout(900); await pc.reload(); await pc.waitForSelector('.root');
assert.ok((await pc.textContent('#status .txt')).includes('快取'));
await pc.click('#list .item.folder[data-node="範例"] .chev');   // 樹狀側欄：先展開 範例
await pc.click('#list .item[data-id="範例/第一小點"]');
await pc.waitForFunction(() => document.querySelector('.root-title')?.textContent === '第一小點');
await pc.click('.toolbar >> text=重新連接後編輯');
await pc.waitForSelector('.editor.wysiwyg', { timeout: 8000 });   // 可寫 → 預設直觀編輯
assert.equal(await pc.inputValue('.wy-title'), '第一小點');
assert.ok((await pc.textContent('#status .txt')).includes('可編輯'));
await ctx2.close();

console.log('errors:', errors);
assert.equal(errors.length, 0, errors.join('\n'));
console.log('TEST7 OK');
await browser.close();
