// 測試五：圖片貼上存檔（serve.py）、壞連結報告、表格內的 \| 跳脫、樣式切換記憶、靜態 modules.json（--inline）模式
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { spawn, execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const ROOT = process.env.ROOT, HERE = process.env.HERE, TMP = process.env.TMP || '/tmp';

const SRC = ROOT + '';
const DIR = '/tmp/notes-t5';
fs.rmSync(DIR, { recursive: true, force: true });
fs.cpSync(SRC, DIR, { recursive: true });
// 一個有表格、表格內用 \| 的模組
fs.writeFileSync(path.join(DIR, '表格測試.md'), `# 表格測試

## 內文
| 寫法 | 效果 |
|---|---|
| \`[[第一小點\\|摘要]]\` | 程式碼 |
| [[第一小點\\|摘要]] | 晶片 |
`);
const srv = spawn('python3', [path.join(DIR, 'serve.py'), '--port', '8798', '--no-open'], { stdio: ['ignore', 'pipe', 'pipe'] });
await new Promise(r => setTimeout(r, 800));
const browser = await chromium.launch();
const page = await (await browser.newContext({ viewport: { width: 1280, height: 860 }, locale: 'zh-TW' })).newPage();
const errors = []; page.on('pageerror', e => errors.push('pageerror: ' + e.message));
let srv2 = null;
try {
  // --- 表格內 \| ---
  await page.goto('http://localhost:8798/#/' + encodeURIComponent('表格測試'));
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '表格測試');
  assert.equal(await page.$$eval('.root-body td .chip', cs => cs.length), 1);
  assert.ok((await page.$eval('.root-body td code', c => c.textContent)).includes('[[第一小點|摘要]]'));

  // --- 壞連結報告 ---
  const lb = page.locator('#linksBtn');
  assert.equal(await lb.textContent(), '1 個壞連結');
  await lb.click();
  await page.waitForSelector('.report');
  assert.ok((await page.textContent('.report')).includes('[[還沒寫的模組]]'));
  assert.ok((await page.textContent('.report .from')).includes('補充說明'));
  await page.click('.report >> text=建立 還沒寫的模組.md');
  await page.waitForSelector('.editor');
  await page.click('.toolbar >> text=取消');
  await page.waitForFunction(() => document.querySelector('#linksBtn')?.hidden === true);
  fs.rmSync(path.join(DIR, '還沒寫的模組.md'));
  await page.waitForFunction(() => document.querySelector('#linksBtn')?.hidden === false, null, { timeout: 8000 });

  // --- 圖片貼上 ---
  await page.goto('http://localhost:8798/#/' + encodeURIComponent('範例/第一小點'));
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '第一小點');
  await page.click('.toolbar >> text=編輯');
  await page.waitForSelector('.editor');
  await page.click('.ed-bar .mode-seg button[data-mode="source"]');   // 這些測試驗的是原始碼模式
  await page.waitForSelector('.editor textarea');
  const png = fs.readFileSync(HERE + '/sample.png');
  await page.evaluate(async (b64) => {
    const bin = atob(b64); const bytes = Uint8Array.from(bin, c => c.charCodeAt(0));
    const file = new File([bytes], 'image.png', { type: 'image/png' });
    const dt = new DataTransfer(); dt.items.add(file);
    const ta = document.querySelector('.editor textarea'); ta.focus(); ta.setSelectionRange(ta.value.length, ta.value.length);
    ta.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true }));
  }, png.toString('base64'));
  await page.waitForFunction(() => /!\[\]\(圖片\/\d{8}-\d{6}-img\.png\)/.test(document.querySelector('.editor textarea').value), null, { timeout: 8000 });
  const saved = fs.readdirSync(path.join(DIR, '範例/圖片'));
  assert.equal(saved.length, 1); assert.ok(saved[0].endsWith('-img.png'));
  assert.equal(fs.statSync(path.join(DIR, '範例/圖片', saved[0])).size, png.length);
  // 預覽中圖片可載入
  await page.waitForFunction(() => { const img = document.querySelector('.editor .root-body img'); return img && img.complete && img.naturalWidth > 0; }, null, { timeout: 8000 });
  await page.keyboard.press('Control+s');
  await page.waitForFunction(() => !document.querySelector('.editor'));
  assert.ok(fs.readFileSync(path.join(DIR, '範例/第一小點.md'), 'utf8').includes('](圖片/'));
  await page.waitForFunction(() => { const img = document.querySelector('.root-body img'); return img && img.complete && img.naturalWidth > 0; }, null, { timeout: 8000 });

  // --- 樣式切換記憶 ---
  await page.selectOption('#styleSel', 'sketch');
  assert.equal(await page.evaluate(() => document.documentElement.dataset.style), 'sketch');
  await page.reload(); await page.waitForSelector('.root');
  assert.equal(await page.evaluate(() => document.documentElement.dataset.style), 'sketch');
  assert.equal(await page.$eval('#styleSel', s => s.value), 'sketch');
  await page.selectOption('#styleSel', 'ink');
  await page.click('.root .card[data-id="範例/補充說明"] .seg button[data-m="3"]');
  const rails = await page.$$eval('.root .card', cs => cs.map(c => c.dataset.rail));
  assert.ok(rails.includes('1') && rails.includes('2'), rails.join(','));

  console.log('errors:', errors);
  assert.equal(errors.length, 0, errors.join('\n'));
  srv.kill();

  // --- 靜態網站模式：build.py --manifest --inline + 純 http.server ---
  execSync(`python3 ${path.join(DIR, 'build.py')} --manifest --inline --github wenj/notes --branch main`, { cwd: DIR });
  const man = JSON.parse(fs.readFileSync(path.join(DIR, 'modules.json'), 'utf8'));
  assert.ok(man.modules.every(m => typeof m.text === 'string'));
  assert.equal(man.github.owner, 'wenj');
  srv2 = spawn('python3', ['-m', 'http.server', '8797', '--bind', '127.0.0.1'], { cwd: DIR, stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 900));
  const reqs = [];
  page.on('request', r => reqs.push(r.url()));
  await page.goto('http://127.0.0.1:8797/#/' + encodeURIComponent('範例/筆記一'));
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '筆記一');
  assert.ok((await page.textContent('#status .txt')).includes('GitHub Pages'));
  assert.ok(!reqs.some(u => u.endsWith('.md')), '有 --inline 時不應逐檔抓 .md：' + reqs.filter(u => u.endsWith('.md')).join(','));
  const editHref = await page.$eval('.toolbar a.btn', a => a.getAttribute('href'));
  assert.equal(editHref, 'https://github.com/wenj/notes/edit/main/' + encodeURIComponent('範例') + '/' + encodeURIComponent('筆記一') + '.md');
  // 圖片（相對路徑）在 http 模式也能載入
  await page.goto('http://127.0.0.1:8797/#/' + encodeURIComponent('範例/第一小點'));
  await page.waitForFunction(() => { const img = document.querySelector('.root-body img'); return img && img.complete && img.naturalWidth > 0; }, null, { timeout: 8000 });
  console.log('TEST5 OK');
} finally {
  await browser.close(); srv.kill(); if (srv2) srv2.kill();
}
