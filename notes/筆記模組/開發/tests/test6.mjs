// 測試六：每個 html 各自記憶、忘記並回到起點、快取優先＋重新連接資料夾、localStorage 退路、檔案匯入連圖片一起記住
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
const ROOT = process.env.ROOT, HERE = process.env.HERE, TMP = process.env.TMP || '/tmp';

const P = path.join(TMP, 'prof'); fs.rmSync(P, { recursive: true, force: true });
for (const d of ['A', 'B', 'C', 'D']) { fs.mkdirSync(path.join(P, d), { recursive: true }); fs.copyFileSync(path.join(ROOT, 'index.html'), path.join(P, d, 'index.html')); }
const md = n => ({ name: n, mimeType: 'text/markdown', buffer: fs.readFileSync(fs.existsSync(path.join(ROOT, n)) ? path.join(ROOT, n) : path.join(ROOT, '範例', n)) });   // 範例模組在 範例/ 裡；用檔案選取器匯入時只有檔名，id 就是檔名
const url = d => 'file://' + path.join(P, d, 'index.html');

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1200, height: 800 }, locale: 'zh-TW' });
const errors = [];
const page = await ctx.newPage();
page.on('pageerror', e => errors.push('pageerror: ' + e.message));

// ---------- A 與 B 各記各的 ----------
await page.goto(url('A')); await page.waitForSelector('.welcome');
assert.equal(await page.textContent('#srcBtn'), '匯入 ▾');
await page.setInputFiles('#pickFiles', [md('筆記一.md'), { name: '圖測.md', mimeType: 'text/markdown', buffer: Buffer.from('# 圖測\n\n## 內文\n![](sample.png)\n') }, { name: 'sample.png', mimeType: 'image/png', buffer: fs.readFileSync(HERE + '/sample.png') }]);
await page.waitForFunction(() => document.querySelector('#count')?.textContent === '2 個模組');
await page.selectOption('#styleSel', 'tab');
await page.goto(url('B')); await page.waitForSelector('.welcome', { timeout: 8000 });   // B 還是空的
assert.equal(await page.evaluate(() => document.documentElement.dataset.style), 'ink', 'B 不該繼承 A 的樣式');
await page.setInputFiles('#pickFiles', [md('第一小點.md'), md('第二小點.md')]);
await page.waitForFunction(() => document.querySelector('#count')?.textContent === '2 個模組');
await page.waitForTimeout(1000);
await page.goto(url('A')); await page.waitForSelector('.root');
assert.equal(await page.textContent('#count'), '2 個模組');
assert.ok((await page.textContent('#status .txt')).includes('快取'));
assert.equal(await page.evaluate(() => document.documentElement.dataset.style), 'tab');
assert.ok(await page.$('#list .item[data-id="圖測"]'));
// 快取裡的圖片也在
await page.goto(url('A') + '#/' + encodeURIComponent('圖測'));
await page.waitForFunction(() => { const i = document.querySelector('.root-body img'); return i && i.complete && i.naturalWidth > 0; }, null, { timeout: 8000 });
await page.goto(url('B')); await page.waitForSelector('.root');
assert.ok(await page.$('#list .item[data-id="第二小點"]') && !(await page.$('#list .item[data-id="筆記一"]')));

// ---------- 選單：再匯入一次（換內容）、忘記 ----------
assert.equal(await page.textContent('#srcBtn'), '來源 ▾');
await page.click('#srcBtn');
const items = await page.$$eval('#srcPop .mi', bs => bs.map(b => b.textContent));
assert.ok(items.some(t => t.startsWith('匯入檔案')) && items.some(t => t.startsWith('忘記匯入')), items.join(' | '));
await page.keyboard.press('Escape');
assert.equal(await page.$eval('#srcMenu', m => m.open), false);
await page.setInputFiles('#pickFiles', [md('首頁.md')]);   // 換成另一批
await page.waitForFunction(() => document.querySelector('#count')?.textContent === '1 個模組');
await page.click('#srcBtn');
page.once('dialog', d => d.accept());
await page.click('#srcPop .mi.danger');
await page.waitForSelector('.welcome');
assert.equal(await page.textContent('#status .txt'), '尚未載入');
await page.reload(); await page.waitForSelector('.welcome', { timeout: 8000 });   // 忘記後重開仍是起點
// A 不受 B 的忘記影響
await page.goto(url('A')); await page.waitForSelector('.root');
assert.equal(await page.textContent('#count'), '2 個模組');

// ---------- C：假的資料夾 handle → 重開先看快取，按一下重新連接 ----------
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
  window.__root = root;
  window.showDirectoryPicker = async () => { root.perm = 'granted'; return root; };
  // 讓假 handle 能「存進」IndexedDB：存的時候換成記號，讀出來時換回活的物件
  const put = IDBObjectStore.prototype.put; IDBObjectStore.prototype.put = function (v, k) { if (v === root) v = { __fakeHandle: true }; return put.call(this, v, k); };
  const d = Object.getOwnPropertyDescriptor(IDBRequest.prototype, 'result');
  Object.defineProperty(IDBRequest.prototype, 'result', { get() { const r = d.get.call(this); return (r && r.__fakeHandle) ? root : r; } });
}, { files });
const pc = await ctx2.newPage(); pc.on('pageerror', e => errors.push('pageerror C: ' + e.message));
await pc.goto(url('C')); await pc.waitForSelector('.welcome');
await pc.click('.welcome button:has-text("匯入資料夾")');
await pc.waitForSelector('.root');
assert.ok((await pc.textContent('#status .txt')).includes('可編輯'));
await pc.waitForTimeout(900);
await pc.reload(); await pc.waitForSelector('.root');   // 權限回到 prompt → 快取優先
assert.ok((await pc.textContent('#status .txt')).includes('快取'), await pc.textContent('#status .txt'));
assert.equal(await pc.$eval('#notice', n => n.hidden), false);
assert.ok((await pc.textContent('#notice')).includes('我的筆記'));
await pc.click('#notice button.primary');
await pc.waitForFunction(() => document.querySelector('#status .txt')?.textContent.includes('可編輯'));
assert.equal(await pc.$eval('#notice', n => n.hidden), true);
assert.equal(await pc.$eval('#newBtn', b => b.hidden), false);
await ctx2.close();

// ---------- D：沒有 IndexedDB（像 Safari 的 file://）→ localStorage 退路 ----------
const ctx3 = await browser.newContext({ viewport: { width: 1200, height: 800 }, locale: 'zh-TW' });
await ctx3.addInitScript(() => { Object.defineProperty(window, 'indexedDB', { get() { throw new Error('SecurityError'); } }); });
const pd = await ctx3.newPage(); pd.on('pageerror', e => errors.push('pageerror D: ' + e.message));
await pd.goto(url('D')); await pd.waitForSelector('.welcome');
await pd.setInputFiles('#pickFiles', [md('筆記一.md'), md('第一小點.md'), md('第二小點.md')]);
await pd.waitForFunction(() => document.querySelector('#count')?.textContent === '3 個模組');
await pd.waitForTimeout(300);
await pd.reload(); await pd.waitForSelector('.root');
assert.equal(await pd.textContent('#count'), '3 個模組');
assert.ok((await pd.textContent('#status .txt')).includes('快取'));
await ctx3.close();

console.log('errors:', errors);
assert.equal(errors.length, 0, errors.join('\n'));
console.log('TEST6 OK');
await browser.close();
