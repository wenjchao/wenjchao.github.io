// 測試三：本機 index.html（file://）— 歡迎畫面、假的 File System Access 資料夾、編輯存檔、外部變動、快取還原、檔案選取器
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const ROOT = process.env.ROOT, HERE = process.env.HERE, TMP = process.env.TMP || '/tmp';

const NOTES = ROOT + '';
const files = fs.readdirSync(NOTES, { recursive: true }).filter(f => f.endsWith('.md') && (!f.includes('/') || f.startsWith('範例/'))).map(f => ({ name: f, text: fs.readFileSync(`${NOTES}/${f}`, 'utf8') }));   // 根目錄的模組＋範例/

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 860 }, locale: 'zh-TW' });
await ctx.addInitScript(({ files }) => {
  // 假的 File System Access API（記憶體版）
  class FH { constructor(dir, name) { this.kind = 'file'; this.dir = dir; this.name = name; }
    async getFile() { const r = this.dir.files.get(this.name); return new File([r.text], this.name, { lastModified: r.mtime }); }
    async createWritable() { let buf = ''; const dir = this.dir, name = this.name; return { async write(t) { buf += t; }, async close() { dir.files.set(name, { text: buf, mtime: Date.now() }); } }; } }
  class DH { constructor(name) { this.kind = 'directory'; this.name = name; this.files = new Map(); this.dirs = new Map(); }
    async *entries() { for (const n of this.files.keys()) yield [n, new FH(this, n)]; for (const [n, d] of this.dirs) yield [n, d]; }
    async getDirectoryHandle(n, o) { if (!this.dirs.has(n)) { if (!o?.create) throw new Error('NotFound'); this.dirs.set(n, new DH(n)); } return this.dirs.get(n); }
    async getFileHandle(n, o) { if (!this.files.has(n)) { if (!o?.create) throw new Error('NotFound'); this.files.set(n, { text: '', mtime: Date.now() }); } return new FH(this, n); }
    async queryPermission() { return 'granted'; } async requestPermission() { return 'granted'; } }
  const root = new DH('我的筆記');
  const putFile = (dir, name, rec) => { const i = name.indexOf('/'); if (i < 0) dir.files.set(name, rec); else { const d = name.slice(0, i); if (!dir.dirs.has(d)) dir.dirs.set(d, new DH(d)); putFile(dir.dirs.get(d), name.slice(i + 1), rec); } };   // 路徑含資料夾 → 巢狀 DH（範例模組在 範例/）
  const at = n => { let d = root; const ps = n.split('/'); const last = ps.pop(); for (const p of ps) d = d && d.dirs.get(p); return [d ? d.files : null, last]; };
  window.__get = n => { const [m, k] = at(n); return m && m.get(k); }; window.__set = (n, rec) => { const [m, k] = at(n); m.set(k, rec); }; window.__fileText = n => window.__get(n)?.text;
  for (const f of files) putFile(root, f.name, { text: f.text, mtime: Date.now() - 10000 });
  window.__root = root;
  window.showDirectoryPicker = async () => root;
}, { files });
const page = await ctx.newPage();
const errors = [];
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });

await page.goto('file://' + NOTES + '/index.html');
await page.waitForSelector('.welcome');
await page.screenshot({ path: TMP + '/shot-welcome.png' });
assert.ok(await page.$(".welcome button:has-text(\"匯入資料夾\")"));

// 開啟（假的）資料夾
await page.click(".welcome button:has-text(\"匯入資料夾\")");
await page.waitForSelector('.root');
assert.ok((await page.textContent('#status .txt')).includes('我的筆記'));
assert.ok((await page.textContent('#status .txt')).includes('可編輯'));
assert.equal(await page.textContent('.root-title'), '首頁');

// R22／D26：改卡片模式會直接寫回父模組的 .md（只換那一個連結的模式字）
await page.goto('file://' + NOTES + '/index.html#/' + encodeURIComponent('範例/筆記一'));
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '筆記一');
const fileText = () => page.evaluate(() => window.__get('範例/筆記一.md').text);
assert.ok((await fileText()).includes('[[第一小點|摘要]]\n\n每張卡片'));
await page.click('.root > .root-body > .card[data-id="範例/第一小點"][data-key$="#1"] .seg button[data-m="3"]');   // 第二張 第一小點（原本 摘要）→ 全文
await page.waitForFunction(() => window.__get('範例/筆記一.md').text.includes('[[第一小點|全文]]\n\n每張卡片'), null, { timeout: 5000 });
let t1 = await fileText();
assert.equal((t1.match(/\[\[第一小點\|全文\]\]/g) || []).length, 2, '第一張卡片（本來就是全文）不該變');
assert.ok(t1.includes('提到 [[第一小點]]，'), '句中的晶片不該變');
assert.equal(await page.$eval('.root > .root-body > .card[data-id="範例/第一小點"][data-key$="#1"]', c => c.dataset.mode), '3', '重畫後狀態要保留');
// 扁平卡片（清單裡）：全文 → [[第二小點|全文|扁平]]；收合 → [[第二小點|扁平]]
assert.ok(await page.$('.root-body ol > li > .card.flat[data-id="範例/第二小點"]'), '清單裡的扁平卡片');
await page.click('.root-body ol > li > .card.flat[data-id="範例/第二小點"] .seg button[data-m="3"]');
await page.waitForFunction(() => window.__get('範例/筆記一.md').text.includes('2. [[第二小點|全文|扁平]]'), null, { timeout: 5000 });
await page.click('.root-body ol > li > .card.flat[data-id="範例/第二小點"] .tri');
await page.waitForFunction(() => window.__get('範例/筆記一.md').text.includes('2. [[第二小點|扁平]]'), null, { timeout: 5000 });
// R27：外觀切換鈕也寫檔：扁平 → 卡片 → 扁平
await page.click('.root-body ol > li > .card[data-id="範例/第二小點"] .style-seg button[data-st="card"]');
await page.waitForFunction(() => window.__get('範例/筆記一.md').text.includes('2. [[第二小點]]\n'), null, { timeout: 5000 });
assert.equal(await page.$eval('.root-body ol > li > .card[data-id="範例/第二小點"]', c => c.dataset.style), 'card');
await page.click('.root-body ol > li > .card[data-id="範例/第二小點"] .style-seg button[data-st="flat"]');
await page.waitForFunction(() => window.__get('範例/筆記一.md').text.includes('2. [[第二小點|扁平]]'), null, { timeout: 5000 });
assert.equal(await page.evaluate(() => Object.keys(JSON.parse(localStorage.getItem(Persist.key('cards')) || '{}')).length), 0, '可寫入時不該用瀏覽器記憶');
// 全部展開不寫檔
const before = await fileText();
await page.click('.toolbar >> text=全部展開'); await page.waitForTimeout(900);
assert.equal(await fileText(), before, '全部展開是暫時動作，不寫檔');
await page.click('.toolbar >> text=全部收合'); await page.waitForTimeout(300);

// 編輯並存回（假資料夾）
await page.click('#list .item[data-id="範例/第一小點"]');
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '第一小點');
await page.click('.toolbar >> text=編輯');
await page.waitForSelector('.editor');
await page.click('.ed-bar .mode-seg button[data-mode="source"]');   // 這些測試驗的是原始碼模式
await page.waitForSelector('.editor textarea');
const ta = page.locator('.editor textarea');
await ta.fill((await ta.inputValue()).replace('## 摘要\n', '## 摘要\n（已在瀏覽器修改）'));
await page.click('.ed-bar >> text=儲存');
await page.waitForFunction(() => !document.querySelector('.editor') && document.querySelector('.root-summary')?.textContent.includes('已在瀏覽器修改'));
assert.ok((await page.evaluate(() => window.__get('範例/第一小點.md').text)).includes('已在瀏覽器修改'));

// 外部變動（直接改假資料夾）→ 2 秒內自動更新
await page.evaluate(() => { const r = window.__get('範例/第二小點.md'); window.__set('範例/第二小點.md', { text: r.text + '\n3. 外部新增的一行\n', mtime: Date.now() }); });
await page.click('#list .item[data-id="範例/第二小點"]');
await page.waitForFunction(() => document.querySelector('.root-body')?.textContent.includes('外部新增的一行'), null, { timeout: 8000 });
// 新增檔案（外部）→ 側欄出現
await page.evaluate(() => { window.__set('新檔.md', { text: '# 新檔\n\n## 內文\n嗨', mtime: Date.now() }); });
await page.waitForFunction(() => !!document.querySelector('#list .item[data-id="新檔"]'), null, { timeout: 8000 });

// 重新整理頁面：假 handle 存不進 IndexedDB → 退回快取
await page.waitForTimeout(1200);
await page.reload();
await page.waitForSelector('.root');
assert.ok((await page.textContent('#status .txt')).includes('快取'), await page.textContent('#status .txt'));
assert.ok(await page.$('#list .item[data-id="新檔"]'), '快取應含外部新增的檔案');
assert.ok(await page.$('.toolbar >> text=檢視原始檔'));

// 檔案選取器（模擬 iPad 多選）
await page.click('#srcBtn'); await page.click('#srcPop .mi:has-text("匯入資料夾…（可編輯")');   // 透過選單切回假資料夾
await page.waitForFunction(() => document.querySelector('#status .txt')?.textContent.includes('我的筆記'));
await page.setInputFiles('#pickFiles', ['筆記一.md', '第一小點.md'].map(n => ({ name: n, mimeType: 'text/markdown', buffer: Buffer.from(fs.readFileSync(`${NOTES}/範例/${n}`)) })));   // 非 ASCII 路徑在此環境的 CDP 會失效，改用 buffer
await page.waitForFunction(() => document.querySelector('#count')?.textContent === '2 個模組');
assert.ok((await page.textContent('#status .txt')).includes('2 個檔案'));
await page.goto('file://' + NOTES + '/index.html#/' + encodeURIComponent('筆記一'));
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '筆記一');
// 沒載入的 第二小點 應顯示為找不到
assert.ok(await page.$('.missing-block[data-target="第二小點"]'));

console.log('errors:', errors);
assert.equal(errors.filter(e => !/fonts\.g|net::ERR|Failed to load resource/.test(e)).length, 0, errors.join('\n'));
console.log('TEST3 OK');
await browser.close();
