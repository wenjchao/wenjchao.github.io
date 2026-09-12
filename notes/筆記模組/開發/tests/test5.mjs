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

| ==大類 | 子分類 | 內容 |
|---|---|---|
| 周邊 | 破壞 | AIHA |
| ^^ | 流掉 | 出血 |
| ^^ | \`^^\` | 字面 |
| 甲 | << | 乙 |
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

  // R80：表格合併——^^ 併上（跨三列）、<< 併左、行內程式碼跳脫照字面
  const mg = await page.$eval('.root-body table:nth-of-type(2)', tb => ({
    rs: tb.querySelector('td[rowspan]')?.rowSpan, rsTxt: tb.querySelector('td[rowspan]')?.textContent.trim(),
    cs: tb.querySelector('td[colspan]')?.colSpan, csTxt: tb.querySelector('td[colspan]')?.textContent.trim(),
    lit: [...tb.querySelectorAll('td code')].map(c => c.textContent).join(','),
  }));
  assert.deepEqual(mg, { rs: 3, rsTxt: '周邊', cs: 2, csTxt: '甲', lit: '^^' }, 'R80 合併格：' + JSON.stringify(mg));
  // R82：表頭 == 欄——記號不顯示、整欄（含 rowspan 錯位列）不換行
  const nw = await page.$eval('.root-body table:nth-of-type(2)', tb => ({
    th: tb.querySelector('th').textContent.trim(),
    thNw: getComputedStyle(tb.querySelector('th')).whiteSpace,
    tdNw: getComputedStyle(tb.querySelector('td[rowspan]')).whiteSpace,
  }));
  assert.deepEqual(nw, { th: '大類', thNw: 'nowrap', tdNw: 'nowrap' }, 'R82 欄不換行：' + JSON.stringify(nw));

  // R87：儲存格裡句中帶模式字 → 載入即自動展開；R86：不重複卡頭（膠囊就是卡頭）
  await page.waitForSelector('.root-body td .card[data-mode="2"]');
  assert.equal(await page.$eval('.root-body td .card > .card-head', h => getComputedStyle(h).display), 'none', 'R86 就地展開不帶卡頭');
  assert.ok(await page.$('.root-body td .card > .card-summary'), 'R86 內容出現在格子裡');
  assert.ok(await page.$eval('.root-body td .chip', c => c.classList.contains('open')), 'R87 晶片狀態同步為展開');

  // --- 壞連結報告 ---（數量用相對斷言：筆記模組的說明可連到庫裡其他資料夾的檔，單獨拷出來測時基準數會浮動）
  const lb = page.locator('#linksBtn');
  assert.match(await lb.textContent(), /\d+ 個壞連結/);
  const lbCount = "n => { const el = document.querySelector('#linksBtn'); return (!el || el.hidden) ? 0 : +((el.textContent.match(/\\d+/) || [0])[0]); }";
  const n0 = await page.evaluate(`(${lbCount})()`);
  assert.ok(n0 >= 1, '至少有測試種的那個壞連結');
  await lb.click();
  await page.waitForSelector('.report');
  assert.ok((await page.textContent('.report')).includes('[[還沒寫的模組]]'));
  assert.ok((await page.textContent('.report')).includes('補充說明'));
  await page.click('.report >> text=建立 還沒寫的模組.md');
  await page.waitForSelector('.editor');
  await page.click('.toolbar >> text=取消');
  await page.waitForFunction(`(${lbCount})() === ${n0 - 1}`, null, { timeout: 8000 });   // 建立後：壞連結少一個
  fs.rmSync(path.join(DIR, '還沒寫的模組.md'));
  await page.waitForFunction(`(${lbCount})() === ${n0}`, null, { timeout: 8000 });   // 刪掉後：回到基準

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
