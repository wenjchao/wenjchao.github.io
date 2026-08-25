// 測試十一：GitHub 直接存檔（R43、D39）——GitHub Pages（靜態 modules.json）版輸入 token 後：
//   直接編輯存檔＝Contents API PUT（帶 sha、路徑含 dir 前綴）、建立模組、核取方塊 commit、
//   改名＝PUT＋DELETE、翻卡片不 commit（記在瀏覽器）、輪詢的舊 manifest 不會蓋掉剛存的內容。
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { spawn, execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const ROOT = process.env.ROOT, HERE = process.env.HERE, TMP = process.env.TMP || '/tmp';

const DIR = '/tmp/notes-t11';
fs.rmSync(DIR, { recursive: true, force: true });
fs.cpSync(ROOT + '', DIR, { recursive: true });
fs.rmSync(path.join(DIR, '開發'), { recursive: true, force: true });
execSync(`python3 ${path.join(DIR, 'build.py')} --manifest --inline --github wenjchao/wenjchao.github.io --branch master --dir notes`, { cwd: DIR });
const srv = spawn('python3', ['-m', 'http.server', '8796', '--bind', '127.0.0.1'], { cwd: DIR, stdio: 'ignore' });
await new Promise(r => setTimeout(r, 900));

const browser = await chromium.launch();
const errors = [];
try {
  const ctx = await browser.newContext({ viewport: { width: 1200, height: 900 }, locale: 'zh-TW' });
  // 假的 GitHub API：攔截 api.github.com，記錄呼叫、管理 sha
  await ctx.addInitScript(() => {
    const calls = []; const shas = new Map(); let n = 0;
    window.__gh = { calls, shas, setSha: (p, v) => shas.set(p, v) };
    shas.set('notes/範例/第二小點.md', 'sha-old-1');
    const orig = window.fetch.bind(window);
    window.fetch = async (url, opt = {}) => {
      const u = String(url);
      if (!u.startsWith('https://api.github.com/')) return orig(url, opt);
      const auth = (opt.headers || {}).Authorization || '';
      const rec = { url: u, method: (opt.method || 'GET').toUpperCase(), auth, body: opt.body ? JSON.parse(opt.body) : null };
      calls.push(rec);
      const ok = j => new Response(JSON.stringify(j), { status: 200, headers: { 'Content-Type': 'application/json' } });
      if (auth !== 'Bearer TOKEN-OK') return new Response('{}', { status: 401 });
      if (u.endsWith('/repos/wenjchao/wenjchao.github.io')) return ok({ permissions: { push: true } });
      if (u.includes('/git/trees/')) return ok({ tree: [...shas.entries()].map(([p, sha]) => ({ path: p, type: 'blob', sha })) });
      const m = /\/contents\/(.+)$/.exec(u);
      if (m) {
        const p = decodeURIComponent(m[1]);
        if (rec.method === 'PUT') { if (shas.has(p) && rec.body.sha !== shas.get(p)) return new Response('{"message":"sha mismatch"}', { status: 409 }); const sha = 'sha-' + (++n); shas.set(p, sha); return ok({ content: { sha } }); }
        if (rec.method === 'DELETE') { shas.delete(p); return ok({}); }
      }
      return new Response('{}', { status: 404 });
    };
  });
  const page = await ctx.newPage();
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/net::ERR|Failed to load resource/.test(m.text())) errors.push(m.text()); });
  page.on('dialog', d => d.accept());

  await page.goto('http://127.0.0.1:8796/#/' + encodeURIComponent('範例/筆記一'));
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '筆記一');
  assert.ok(await page.$('.toolbar button:has-text("啟用編輯")'), 'GitHub Pages 版要有「啟用編輯」');
  assert.ok(await page.$('.toolbar a:has-text("在 GitHub 編輯")'));

  // 輸入 token：先錯的（401）再對的
  await page.click('.toolbar button:has-text("啟用編輯")');
  await page.waitForSelector('.wy-panel input[type="password"]');
  await page.fill('.wy-panel input[type="password"]', 'TOKEN-BAD');
  await page.click('.wy-panel .btn.primary');
  await page.waitForFunction(() => document.querySelector('#toast')?.textContent.includes('token 無效'));
  await page.fill('.wy-panel input[type="password"]', 'TOKEN-OK');
  await page.click('.wy-panel .btn.primary');
  await page.waitForFunction(() => document.querySelector('.toolbar')?.textContent.includes('編輯') && !document.querySelector('.wy-panel'));
  assert.ok((await page.textContent('#status .txt')).includes('可編輯'));
  assert.ok(await page.$('.toolbar button:has-text("改名／搬移")'), 'token 之後改名鈕要出現');

  // 直接編輯存檔 → PUT，路徑帶 notes/ 前綴、帶舊 sha
  await page.goto('http://127.0.0.1:8796/#/' + encodeURIComponent('範例/第二小點'));
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '第二小點');
  await page.click('.toolbar >> text=編輯'); await page.waitForSelector('.editor');
  await page.click('.ed-bar .mode-seg button[data-mode="source"]'); await page.waitForSelector('.editor textarea');
  await page.locator('.editor textarea').focus(); await page.keyboard.press('Control+End'); await page.keyboard.type('\niPad 上加的一行\n');
  await page.click('.ed-bar >> text=儲存');
  await page.waitForFunction(() => !document.querySelector('.editor'));
  let put = await page.evaluate(() => window.__gh.calls.filter(c => c.method === 'PUT').pop());
  assert.ok(put && decodeURIComponent(put.url).endsWith('/contents/notes/範例/第二小點.md'), put && put.url);
  assert.equal(put.body.sha, 'sha-old-1', '要帶舊 sha');
  assert.equal(put.body.branch, 'master');
  assert.ok(decodeURIComponent(escape(atob(put.body.content))).includes('iPad 上加的一行'), '內容要進 commit');
  assert.ok((await page.textContent('.root-body')).includes('iPad 上加的一行'), '畫面立即更新');

  // 輪詢讀到「部署還沒跟上」的舊 manifest → 不可以把剛存的蓋掉
  await page.waitForTimeout(2600);
  assert.ok((await page.textContent('.root-body')).includes('iPad 上加的一行'), '舊 manifest 不能蓋掉剛存的');

  // 翻卡片（標題/摘要/全文）不 commit：GitHub 模式記在瀏覽器
  await page.goto('http://127.0.0.1:8796/#/' + encodeURIComponent('範例/筆記一'));
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '筆記一');
  const before = await page.evaluate(() => window.__gh.calls.length);
  await page.click('.root > .root-body > .card[data-id="範例/第一小點"] .seg button[data-m="1"]');
  await page.waitForTimeout(900);
  assert.equal(await page.evaluate(() => window.__gh.calls.length), before, '翻卡片不該打 API');
  assert.equal(await page.$eval('.root > .root-body > .card[data-id="範例/第一小點"]', c => c.dataset.mode), '1');

  // 核取方塊＝有意的修改 → commit。先建一個有核取清單的新模組（建立也走 PUT）
  await page.evaluate(() => App.createModule('待辦測試'));
  await page.waitForSelector('.editor');
  await page.click('.ed-bar .mode-seg button[data-mode="source"]'); await page.waitForSelector('.editor textarea');
  await page.fill('.editor textarea', '# 待辦測試\n\n## 內文\n- [ ] 第一件\n- [ ] 第二件\n');
  await page.click('.ed-bar >> text=儲存'); await page.waitForFunction(() => !document.querySelector('.editor'));
  await page.locator('.root-body input[type="checkbox"]').first().click();
  await page.waitForFunction(() => { const c = window.__gh.calls.filter(x => x.method === 'PUT').pop(); return c && c.url.includes(encodeURIComponent('待辦測試.md')) && decodeURIComponent(escape(atob(c.body.content))).includes('- [x] 第一件'); }, null, { timeout: 5000 });

  // 改名 → PUT 新檔＋DELETE 舊檔
  await page.click('.toolbar >> text=改名／搬移'); await page.waitForSelector('.wy-panel');
  await page.fill('.wy-panel input[type="text"]', '待辦改名');
  await page.click('.wy-panel .btn.primary');
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '待辦改名');
  const dels = await page.evaluate(() => window.__gh.calls.filter(c => c.method === 'DELETE').map(c => decodeURIComponent(c.url)));
  assert.ok(dels.some(u => u.endsWith('/contents/notes/待辦測試.md')), dels.join());
  assert.ok(await page.evaluate(() => window.__gh.shas.has('notes/待辦改名.md') && !window.__gh.shas.has('notes/待辦測試.md')));

  // 部署還沒跟上時的提示（D39）：重新整理後 manifest 比最後一次寫入舊 → 顯示「部署中」，新 manifest 到了自動收掉
  await page.goto('http://127.0.0.1:8796/#/' + encodeURIComponent('範例/筆記一'));   // 回到 manifest 裡存在的模組再重整
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '筆記一');
  await page.evaluate(() => Persist.pref.set('ghSavedAt', String(Date.now())));
  await page.reload(); await page.waitForSelector('.root');
  await page.waitForFunction(() => !document.querySelector('#notice').hidden && document.querySelector('#notice').textContent.includes('部署'));
  await page.evaluate(() => Persist.pref.del('ghSavedAt'));
  await page.reload(); await page.waitForSelector('.root');
  assert.equal(await page.$eval('#notice', n => n.hidden), true, '沒有待部署的寫入就不該提示');

  // 停用：清 token 回唯讀
  await page.click('#srcBtn');
  await page.click('#srcPop >> text=停用直接編輯');
  await page.waitForFunction(() => document.querySelector('#status .txt')?.textContent.includes('唯讀'));
  assert.ok(await page.$('.toolbar button:has-text("啟用編輯")'));

  await ctx.close();
} finally { srv.kill(); }
console.log('errors:', errors);
assert.equal(errors.length, 0, errors.join('\n'));
console.log('TEST11 OK');
await browser.close();
