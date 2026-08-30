// 測試十：1.0 的功能——標籤與日期（R37）、全文搜尋片段與高亮（R39）、核取方塊直接點（R38）、麵包屑（R36）、
//          連結自動完成（R35）、自動儲存草稿（R41）、改名／搬移／刪除連結連動（R34、R40）。假的 File System Access 資料夾。
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
const ROOT = process.env.ROOT, HERE = process.env.HERE, TMP = process.env.TMP || '/tmp';

const files = fs.readdirSync(ROOT, { recursive: true }).filter(f => f.endsWith('.md') && (!f.includes('/') || f.startsWith('範例/'))).map(f => ({ name: f, text: fs.readFileSync(path.join(ROOT, f), 'utf8') }));
files.unshift({ name: '首頁.md', text: '# 首頁\n\n## 內文\n[[範例/筆記一|摘要]]\n' });   // 測試用入口（使用者把工具首頁改名了，fixture 自備一個）
files.push({ name: '專案/待辦.md', text: '---\ntags: [工作, 重要]\ndate: 2026-08-22\n---\n# 待辦\n\n## 摘要\n有標籤和核取方塊的模組，連回 [[計畫]]。\n\n## 內文\n- [ ] 第一件事\n- [x] 第二件事\n- [ ] 第三件事\n\n![](圖片/a.png)\n\n```\n- [ ] 程式碼裡的不算\n```\n' });
files.push({ name: '專案/計畫.md', text: '---\ntags:\n  - 工作\n---\n# 計畫\n\n## 摘要\n專案的計畫。\n\n## 內文\n[[待辦|全文]]\n\n也連到 [[範例/第二小點]] 和 [待辦](待辦.md)。\n' });

const browser = await chromium.launch();
const errors = [];
const ctx = await browser.newContext({ viewport: { width: 1200, height: 900 }, locale: 'zh-TW' });
await ctx.addInitScript(({ files }) => {
  class FH { constructor(dir, name) { this.kind = 'file'; this.dir = dir; this.name = name; }
    async getFile() { const r = this.dir.files.get(this.name); if (!r) throw new Error('NotFound'); return new File([r.text], this.name, { lastModified: r.mtime }); }
    async createWritable() { let buf = ''; const dir = this.dir, name = this.name; return { async write(t) { buf += (typeof t === 'string') ? t : ''; }, async close() { dir.files.set(name, { text: buf, mtime: Date.now() }); } }; } }
  class DH { constructor(name) { this.kind = 'directory'; this.name = name; this.files = new Map(); this.dirs = new Map(); this.perm = 'granted'; }
    async *entries() { for (const n of this.files.keys()) yield [n, new FH(this, n)]; for (const [n, d] of this.dirs) yield [n, d]; }
    async getDirectoryHandle(n, o) { if (!this.dirs.has(n)) { if (!o?.create) throw new Error('NotFound'); this.dirs.set(n, new DH(n)); } return this.dirs.get(n); }
    async getFileHandle(n, o) { if (!this.files.has(n)) { if (!o?.create) throw new Error('NotFound'); this.files.set(n, { text: '', mtime: Date.now() }); } return new FH(this, n); }
    async removeEntry(n) { if (this.files.has(n)) this.files.delete(n); else if (this.dirs.has(n)) this.dirs.delete(n); else throw new Error('NotFound'); }
    async queryPermission() { return this.perm; } async requestPermission() { return this.perm; } }
  const root = new DH('測試資料夾');
  const putFile = (dir, name, rec) => { const i = name.indexOf('/'); if (i < 0) dir.files.set(name, rec); else { const d = name.slice(0, i); if (!dir.dirs.has(d)) dir.dirs.set(d, new DH(d)); putFile(dir.dirs.get(d), name.slice(i + 1), rec); } };
  const at = n => { let d = root; const ps = n.split('/'); const last = ps.pop(); for (const p of ps) d = d && d.dirs.get(p); return [d ? d.files : null, last]; };
  window.__get = n => { const [m, k] = at(n); return m && m.get(k); }; window.__set = (n, rec) => { const [m, k] = at(n); m.set(k, rec); }; window.__fileText = n => window.__get(n)?.text;
  window.__has = n => !!window.__get(n);
  for (const f of files) putFile(root, f.name, { text: f.text, mtime: Date.now() - 10000 });
  window.__root = root; window.showDirectoryPicker = async () => root;
  const put = IDBObjectStore.prototype.put; IDBObjectStore.prototype.put = function (v, k) { if (v === root) v = { __fakeHandle: true }; return put.call(this, v, k); };
  const d = Object.getOwnPropertyDescriptor(IDBRequest.prototype, 'result');
  Object.defineProperty(IDBRequest.prototype, 'result', { get() { const r = d.get.call(this); return (r && r.__fakeHandle) ? root : r; } });
}, { files });
const page = await ctx.newPage();
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error' && !/net::ERR|Failed to load resource/.test(m.text())) errors.push(m.text()); });
page.on('dialog', d => d.accept());
const go = async id => { await page.goto('file://' + ROOT + '/index.html#/' + encodeURIComponent(id)); await page.waitForSelector('.root'); };
const title = async t => page.waitForFunction(x => document.querySelector('.root-title')?.textContent === x, t);

await page.goto('file://' + ROOT + '/index.html'); await page.waitForSelector('.welcome');
await page.click('.welcome button:has-text("匯入資料夾")'); await page.waitForSelector('.root');

/* ---------- 標籤與日期（R37） ---------- */
await go('專案/待辦'); await title('待辦');
assert.deepEqual(await page.$$eval('.root-meta .tag', ts => ts.map(t => t.textContent)), ['#工作', '#重要']);
assert.equal(await page.textContent('.root-meta .date'), '2026-08-22');
await page.click('.root-meta .tag:has-text("#重要")');
assert.equal(await page.inputValue('#search'), '#重要');
await page.waitForFunction(() => document.querySelector('#count')?.textContent.startsWith('1 /'));
assert.deepEqual(await page.$$eval('#list .item', as => as.map(a => a.dataset.id)), ['專案/待辦']);
await page.fill('#search', '#工作'); await page.waitForFunction(() => document.querySelector('#count')?.textContent.startsWith('2 /'));
assert.deepEqual((await page.$$eval('#list .item', as => as.map(a => a.dataset.id))).sort(), ['專案/待辦', '專案/計畫'], 'YAML 清單寫法的 tags 也要算');
await page.fill('#search', ''); await page.waitForFunction(() => !document.querySelector('#count')?.textContent.includes('/'));
// 側欄底下的「標籤」節點
assert.ok(await page.$('#list .tags-row'), '側欄應有標籤節點');
await page.click('#list .tags-row .chev');
assert.deepEqual(await page.$$eval('#list .tag-item', as => as.map(a => a.dataset.tag + ':' + a.querySelector('.cnt').textContent)), ['工作:2', '重要:1']);
await page.click('#list .tag-item[data-tag="重要"]');
assert.equal(await page.inputValue('#search'), '#重要');
await page.fill('#search', '');

/* ---------- 全文搜尋：片段與高亮（R39） ---------- */
await page.fill('#search', '第三件');
await page.waitForFunction(() => document.querySelector('#count')?.textContent.startsWith('1 /'));
assert.ok((await page.innerHTML('#list .item .snip')).includes('<mark>第三件</mark>'), '結果要有命中片段');
assert.ok((await page.$$eval('.root-body mark.hl', ms => ms.length)) >= 1, '目前頁面命中的字要高亮');
await page.fill('#search', '第三件 第一件');   // 多個字都要有
await page.waitForFunction(() => document.querySelector('#count')?.textContent.startsWith('1 /'));
await page.fill('#search', '第三件 不存在的字');
await page.waitForFunction(() => document.querySelector('#count')?.textContent.startsWith('0 /'));
await page.fill('#search', '');
await page.waitForFunction(() => !document.querySelector('.root-body mark.hl'));

/* ---------- 核取方塊直接點（R38） ---------- */
await go('專案/待辦'); await title('待辦');
const cbs = page.locator('.root-body input[type="checkbox"]');
assert.equal(await cbs.count(), 3);
assert.equal(await cbs.nth(0).isDisabled(), false, '可寫入來源：核取方塊可以點');
await cbs.nth(0).click();
await page.waitForFunction(() => window.__fileText('專案/待辦.md').includes('- [x] 第一件事'), null, { timeout: 5000 });
await page.waitForFunction(() => document.querySelectorAll('.root-body input[type="checkbox"]')[0]?.checked);
await page.locator('.root-body input[type="checkbox"]').nth(1).click();
await page.waitForFunction(() => window.__fileText('專案/待辦.md').includes('- [ ] 第二件事'), null, { timeout: 5000 });
let t = await page.evaluate(() => window.__fileText('專案/待辦.md'));
assert.ok(t.includes('- [x] 第一件事\n- [ ] 第二件事\n- [ ] 第三件事') && t.includes('```\n- [ ] 程式碼裡的不算'), t);
// 巢狀卡片裡的核取方塊：改的是被裝進來的那個模組
await go('專案/計畫'); await title('計畫');
const nested = page.locator('.root-body .card[data-id="專案/待辦"] input[type="checkbox"]');
assert.equal(await nested.count(), 3);
await nested.nth(2).click();
await page.waitForFunction(() => window.__fileText('專案/待辦.md').includes('- [x] 第三件事'), null, { timeout: 5000 });

/* ---------- 麵包屑（R36） ---------- */
await page.click('#brand'); await title('首頁');
assert.equal(await page.$('.crumbs'), null, '首頁沒有上層也沒有軌跡');
await page.click('.root-body .card[data-id="範例/筆記一"] .card-title'); await title('筆記一');
await page.click('.root > .root-body > .card[data-id="範例/第一小點"] .card-title'); await title('第一小點');
assert.deepEqual(await page.$$eval('.crumbs a.crumb', as => as.map(a => a.textContent)), ['首頁', '筆記一'], '軌跡');
assert.equal(await page.textContent('.crumbs .crumb.cur'), '第一小點');
await page.click('.crumbs a.crumb:has-text("首頁")'); await title('首頁');
assert.equal(await page.$('.crumbs'), null);
// 從側欄直接進（沒有軌跡）→ 顯示「上層」＝誰把我裝進去
if (await page.$('#list .item.folder[data-node="範例"]:not(.open)')) await page.click('#list .item.folder[data-node="範例"] .chev');
await page.click('#list .item[data-id="範例/補充說明"]'); await title('補充說明');
assert.ok((await page.textContent('.crumbs .parents')).includes('上層') && (await page.textContent('.crumbs .parents')).includes('第一小點'));

/* ---------- 連結自動完成（R35） ---------- */
await go('專案/計畫'); await title('計畫');
await page.click('.toolbar >> text=編輯'); await page.waitForSelector('.editor');
await page.click('.ed-bar .mode-seg button[data-mode="source"]'); await page.waitForSelector('.editor textarea');
const ta = page.locator('.editor textarea');
await ta.focus(); await page.keyboard.press('Control+End'); await page.keyboard.type('\n[[待');
await page.waitForSelector('.ac-pop .ac-item');
assert.ok((await page.textContent('.ac-pop')).includes('待辦'));
await page.keyboard.press('Enter');
await page.waitForFunction(() => !document.querySelector('.ac-pop'));
assert.ok((await ta.inputValue()).endsWith('\n[[待辦]]'), '同資料夾：只寫檔名');
await page.keyboard.type('\n[[第二');
await page.waitForSelector('.ac-pop .ac-item');
await page.keyboard.press('ArrowDown'); await page.keyboard.press('ArrowUp'); await page.keyboard.press('Tab');
assert.ok((await ta.inputValue()).endsWith('[[範例/第二小點]]'), '別的資料夾：完整路徑');
// 直觀編輯裡也會：換成原子
await page.click('.ed-bar .mode-seg button[data-mode="wysiwyg"]'); await page.waitForSelector('.editor.wysiwyg');
const body = page.locator('.wy-field').nth(1);
await body.locator('p').last().click();   // 最後一個（空的）段落；內文結尾是卡片原子，Ctrl+End 會落在原子外面
await page.keyboard.type('提到 [[待');
await page.waitForSelector('.ac-pop .ac-item');
await page.keyboard.press('Enter');
await page.waitForFunction(() => [...document.querySelectorAll('.wy-field .wy-chip')].some(c => c.dataset.md === '[[待辦]]'), null, { timeout: 4000 });
await page.click('.toolbar >> text=取消');   // 放棄（dialog 自動接受）
await page.waitForSelector('.root');

/* ---------- 自動儲存草稿（R41） ---------- */
await go('專案/待辦'); await title('待辦');
await page.click('.toolbar >> text=編輯'); await page.waitForSelector('.editor');
await page.click('.ed-bar .mode-seg button[data-mode="source"]'); await page.waitForSelector('.editor textarea');
await page.locator('.editor textarea').focus(); await page.keyboard.press('Control+End'); await page.keyboard.type('\n草稿裡打的字\n');
await page.waitForTimeout(1500);   // autosave 1 秒
await page.reload(); await page.waitForSelector('.root');   // 沒存就離開（beforeunload 自動接受）
await page.click('.toolbar >> text=編輯'); await page.waitForSelector('.editor');
await page.waitForSelector('#editBanner:not([hidden])');
assert.ok((await page.textContent('#editBanner')).includes('草稿'));
await page.click('#editBanner >> text=還原草稿');
await page.waitForFunction(() => document.querySelector('.editor')?.textContent.includes('草稿裡打的字') || document.querySelector('.editor textarea')?.value.includes('草稿裡打的字'));
await page.click('.toolbar >> text=取消'); await page.waitForSelector('.root');   // 放棄＝草稿也丟掉
await page.click('.toolbar >> text=編輯'); await page.waitForSelector('.editor');
assert.equal(await page.$eval('#editBanner', b => b.hidden), true, '丟掉後不再提示');
await page.click('.toolbar >> text=取消'); await page.waitForSelector('.root');

/* ---------- 改名／搬移／刪除（R34、R40） ---------- */
await go('專案/待辦'); await title('待辦');
await page.click('.toolbar >> text=改名／搬移'); await page.waitForSelector('.wy-panel');
assert.ok((await page.textContent('.wy-panel .note')).includes('1 個模組連到它'));
assert.equal(await page.$eval('.wy-panel input[type="checkbox"]', c => c.checked), true, '標題＝檔名 → 預設一起改');
await page.fill('.wy-panel input[type="text"] >> nth=0', '專案/清單');
await page.click('.wy-panel .btn.primary');
await title('清單');
await page.waitForFunction(() => window.__has('專案/清單.md') && !window.__has('專案/待辦.md'));
t = await page.evaluate(() => window.__fileText('專案/清單.md'));
assert.ok(t.startsWith('---\ntags: [工作, 重要]\ndate: 2026-08-22\n---\n# 清單\n'), '標題跟著改、frontmatter 保留：' + t.slice(0, 80));
let plan = await page.evaluate(() => window.__fileText('專案/計畫.md'));
assert.ok(plan.includes('[[清單|全文]]') && plan.includes('[待辦](清單.md)') && plan.includes('[[範例/第二小點]]'), plan);
assert.equal(await page.$eval('#count', c => c.textContent), `${await page.evaluate(() => Store.modules.size)} 個模組`);
// 搬到別的資料夾：它自己的相對連結與圖片路徑也要改
await page.click('.toolbar >> text=改名／搬移'); await page.waitForSelector('.wy-panel');
await page.fill('.wy-panel input[type="text"] >> nth=0', '封存/清單');
await page.keyboard.press('Enter');
await page.waitForFunction(() => window.__has('封存/清單.md') && !window.__has('專案/清單.md'));
t = await page.evaluate(() => window.__fileText('封存/清單.md'));
assert.ok(t.includes('連回 [[專案/計畫]]') && t.includes('![](../專案/圖片/a.png)'), t);
plan = await page.evaluate(() => window.__fileText('專案/計畫.md'));
assert.ok(plan.includes('[[封存/清單|全文]]') && plan.includes('[待辦](../封存/清單.md)'), plan);
await page.waitForFunction(() => location.hash === '#/' + encodeURIComponent('封存/清單'));
await page.waitForSelector('#list .item[data-id="封存/清單"]');   // 側欄更新（祖先資料夾自動展開）
// 刪除：連到它的連結變成找不到
await page.click('.toolbar >> text=刪除');
await page.waitForFunction(() => !window.__has('封存/清單.md'));
await title('首頁');
await go('專案/計畫'); await title('計畫');
assert.ok(await page.$('.root-body .missing-block[data-target="封存/清單"]'), '刪除後連結變成找不到');
assert.equal(await page.$('#list .item[data-id="封存/清單"]'), null);

/* ---------- 抽出成模組／併回（R47、D42） ---------- */
// 抽出：原始碼模式選取兩段 → 抽成模組（prompt 用預設名，全域 dialog.accept()）
await go('專案/計畫'); await title('計畫');
await page.click('.toolbar >> text=編輯'); await page.waitForSelector('.editor');
await page.click('.ed-bar .mode-seg button[data-mode="source"]'); await page.waitForSelector('.editor textarea');
await page.evaluate(() => {
  const ta = document.querySelector('.editor textarea');
  ta.value = ta.value + '\n細節甲\n\n細節乙 ![](圖片/b.png)\n';
  const a = ta.value.indexOf('細節甲');
  ta.setSelectionRange(a, ta.value.length);
});
await page.click('.ed-bar .ex-btn');   // prompt 預設名＝第一行「細節甲」
await page.waitForFunction(() => window.__has('專案/計畫/細節甲.md'));
t = await page.evaluate(() => window.__fileText('專案/計畫/細節甲.md'));
assert.ok(t.startsWith('# 細節甲\n'), t);
assert.ok(t.includes('![](../圖片/b.png)'), '抽出後圖片路徑要改成相對於新位置：' + t);
assert.ok(!t.includes('## 摘要'), '不自動產生摘要');
let tav = await page.$eval('.editor textarea', el => el.value);
assert.ok(tav.includes('[[計畫/細節甲]]') && !tav.includes('細節乙'), tav);
await page.click('.ed-bar .btn.primary');   // 儲存
await page.waitForFunction(() => window.__fileText('專案/計畫.md').includes('[[計畫/細節甲]]'));
// 併回：卡片工具列的併回鈕 → 內容回到連結處、原檔刪除
await page.waitForSelector('.root-body .card[data-id="專案/計畫/細節甲"]');
await page.click('.root-body .card[data-id="專案/計畫/細節甲"] .icon-btn.merge');   // confirm 自動接受
await page.waitForFunction(() => !window.__has('專案/計畫/細節甲.md'));
plan = await page.evaluate(() => window.__fileText('專案/計畫.md'));
assert.ok(plan.includes('**細節甲**') && plan.includes('細節乙 ![](圖片/b.png)'), '內容併回、路徑改回上層的資料夾：' + plan);
assert.ok(!plan.includes('[[計畫/細節甲]]'), plan);
assert.equal(await page.$('.root-body .card[data-id="專案/計畫/細節甲"]'), null, '卡片消失');

/* ---------- 搬進模組＋整串搬（R63） ---------- */
// 造一個有子模組的樹：直接在假資料夾放 專案/計畫/附錄.md，並讓 計畫 連到它
await page.evaluate(() => { window.__set('專案/計畫/附錄.md', { text: '# 附錄\n\n## 內文\n回上層 [[../計畫]]。\n', mtime: Date.now() }); });
await page.waitForFunction(() => Store.modules.has('專案/計畫/附錄'), null, { timeout: 8000 });
await page.evaluate(() => { const r = window.__get('專案/計畫.md'); window.__set('專案/計畫.md', { text: r.text + '\n[[計畫/附錄|摘要]]\n', mtime: Date.now() }); });
await page.waitForFunction(() => Store.modules.get('專案/計畫').raw.includes('[[計畫/附錄|摘要]]'), null, { timeout: 8000 });
await go('專案/計畫'); await title('計畫');
await page.click('.toolbar >> text=改名／搬移'); await page.waitForSelector('.wy-panel');
assert.ok((await page.textContent('.wy-panel .note')).includes('1 個子模組'), '面板要提示整串搬');
await page.fill('.wy-panel input[list="move-into-dl"]', '範例/筆記一');   // 「搬進模組」欄位 → 路徑自動填成 目標/原名
assert.equal(await page.$eval('.wy-panel input[type="text"] >> nth=0', i => i.value), '範例/筆記一/計畫');
await page.click('.wy-panel .btn.primary');
await page.waitForFunction(() => window.__has('範例/筆記一/計畫.md') && window.__has('範例/筆記一/計畫/附錄.md') && !window.__has('專案/計畫.md') && !window.__has('專案/計畫/附錄.md'), null, { timeout: 8000 });
t = await page.evaluate(() => window.__fileText('範例/筆記一/計畫.md'));
assert.ok(t.includes('計畫/附錄'), '父連到子的連結搬完仍要成立：' + t.slice(-200));
await page.waitForFunction(() => !(window.__fileText('範例/筆記一/計畫/附錄.md') || '').includes('[[專案/計畫]]'), null, { timeout: 8000 });   // 父最後搬完才回頭修子的連結
t = await page.evaluate(() => window.__fileText('範例/筆記一/計畫/附錄.md'));
const resolved = await page.evaluate(() => { const l = Refs.extract(window.__fileText('範例/筆記一/計畫/附錄.md'))[0]; return l && Store.resolve(l.target, '範例/筆記一/計畫')?.id; });
assert.equal(resolved, '範例/筆記一/計畫', '子連回父要指到新家：' + t);
await title('計畫');
assert.ok(await page.$('.root-body .card[data-id="範例/筆記一/計畫/附錄"]'), '新家頁面上子模組卡片存在');

await ctx.close();
console.log('errors:', errors);
assert.equal(errors.length, 0, errors.join('\n'));
console.log('TEST10 OK');
await browser.close();
