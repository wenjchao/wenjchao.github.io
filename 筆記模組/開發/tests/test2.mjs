// 測試二：serve.py（HTTP 來源）— 載入、編輯存檔、建立模組、外部修改自動更新、狀態保留
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const ROOT = process.env.ROOT, HERE = process.env.HERE, TMP = process.env.TMP || '/tmp';

const DIR = '/tmp/notes-http';
fs.rmSync(DIR, { recursive: true, force: true });
fs.cpSync(ROOT + '', DIR, { recursive: true });
const srv = spawn('python3', [path.join(DIR, 'serve.py'), '--port', '8799', '--no-open'], { stdio: ['ignore', 'pipe', 'pipe'] });
srv.stderr.on('data', d => process.stdout.write('[serve] ' + d));
await new Promise(r => setTimeout(r, 800));

const browser = await chromium.launch();
const page = await (await browser.newContext({ viewport: { width: 1280, height: 860 }, locale: 'zh-TW' })).newPage();
const errors = [];
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
try {
  await page.goto('http://localhost:8799/');
  await page.waitForSelector('.root');
  assert.equal(await page.textContent('.root-title'), '首頁');
  assert.ok((await page.textContent('#status .txt')).includes('本機伺服器'));
  assert.ok((await page.textContent('#status .txt')).includes('可編輯'));
  assert.ok(!(await page.$eval('#newBtn', b => b.hidden)));

  // 編輯 第二小點：加一行並儲存
  await page.goto('http://localhost:8799/#/' + encodeURIComponent('範例/第二小點'));
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '第二小點');
  await page.click('.toolbar >> text=編輯');
  await page.waitForSelector('.editor');
  await page.click('.ed-bar .mode-seg button[data-mode="source"]');   // 這些測試驗的是原始碼模式
  await page.waitForSelector('.editor textarea');
  const ta = page.locator('.editor textarea');
  await ta.fill((await ta.inputValue()) + '\n3. 這一行是在瀏覽器裡加的。\n');
  await page.waitForFunction(() => document.querySelector('.editor .root-body')?.textContent.includes('瀏覽器裡加的'));   // 即時預覽
  await page.keyboard.press('Control+s');
  await page.waitForSelector('.page .root:not(.editor .root), .root');
  await page.waitForFunction(() => !document.querySelector('.editor') && document.querySelector('.root-body')?.textContent.includes('瀏覽器裡加的'));
  const onDisk = fs.readFileSync(path.join(DIR, '範例/第二小點.md'), 'utf8');
  assert.ok(onDisk.includes('3. 這一行是在瀏覽器裡加的。'), onDisk);

  // 從找不到的模組建立新檔：補充說明 裡的 [[還沒寫的模組]]
  await page.goto('http://localhost:8799/#/' + encodeURIComponent('範例/補充說明'));
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '補充說明');
  page.once('dialog', d => d.accept());
  await page.click('.chip.missing .chip-go');
  await page.waitForSelector('.editor');
  await page.click('.ed-bar .mode-seg button[data-mode="source"]');   // 這些測試驗的是原始碼模式
  await page.waitForSelector('.editor textarea');
  assert.ok(fs.existsSync(path.join(DIR, '還沒寫的模組.md')));
  assert.ok((await page.inputValue('.editor textarea')).startsWith('# 還沒寫的模組'));
  await page.click('.toolbar >> text=取消');
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '還沒寫的模組');
  assert.ok(true);

  // 改名（serve.py：PUT 新檔 + DELETE 舊檔）：補充說明 裡的 [[還沒寫的模組]] 要跟著改；再刪除（DELETE）
  await page.click('.toolbar >> text=改名／搬移'); await page.waitForSelector('.wy-panel');
  await page.fill('.wy-panel input[type="text"]', '寫好的模組');
  await page.click('.wy-panel .btn.primary');
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '寫好的模組', null, { timeout: 8000 });
  assert.ok(fs.existsSync(path.join(DIR, '寫好的模組.md')) && !fs.existsSync(path.join(DIR, '還沒寫的模組.md')), '改名後舊檔要消失');
  assert.ok(fs.readFileSync(path.join(DIR, '範例/補充說明.md'), 'utf8').includes('[[寫好的模組]]'), '連結連動');
  page.once('dialog', d => d.accept());
  await page.click('.toolbar >> text=刪除');
  await page.waitForFunction(() => !document.querySelector('.root-title') || document.querySelector('.root-title')?.textContent !== '寫好的模組', null, { timeout: 8000 });
  await new Promise(r => setTimeout(r, 300));
  assert.ok(!fs.existsSync(path.join(DIR, '寫好的模組.md')), '刪除後檔案要消失');
  fs.writeFileSync(path.join(DIR, '範例/補充說明.md'), fs.readFileSync(path.join(DIR, '範例/補充說明.md'), 'utf8').replace('[[寫好的模組]]', '[[還沒寫的模組]]'));   // 還原給後面的測試
  await new Promise(r => setTimeout(r, 2600));   // 等輪詢把還原讀回來

  // 外部修改 → 自動更新（輪詢 2 秒），且保留展開狀態與捲動
  await page.goto('http://localhost:8799/#/' + encodeURIComponent('範例/筆記一'));
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '筆記一');
  await page.click('.card[data-id="範例/補充說明"] .seg button[data-m="3"]');   // 手動展開到全文
  assert.equal(await page.$eval('.card[data-id="範例/補充說明"]', c => c.dataset.mode), '3');
  await new Promise(r => setTimeout(r, 1100));   // 確保 mtime 不同
  fs.writeFileSync(path.join(DIR, '範例/第一小點.md'), fs.readFileSync(path.join(DIR, '範例/第一小點.md'), 'utf8').replace('第一項……', '第一項（外部編輯器改的）'));
  await page.waitForFunction(() => document.querySelector('.root-body')?.textContent.includes('外部編輯器改的'), null, { timeout: 8000 });
  assert.equal(await page.$eval('.card[data-id="範例/補充說明"]', c => c.dataset.mode), '3', '重新渲染後應保留手動展開狀態');

  // 新增模組按鈕（prompt）
  page.once('dialog', d => d.accept('專案/新想法'));
  await page.click('#newBtn');
  await page.waitForSelector('.editor');
  await page.click('.ed-bar .mode-seg button[data-mode="source"]');   // 這些測試驗的是原始碼模式
  await page.waitForSelector('.editor textarea');
  assert.ok(fs.existsSync(path.join(DIR, '專案', '新想法.md')));
  await page.click('.toolbar >> text=取消');
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '新想法');
  assert.ok(await page.$('#list .item.folder[data-node="專案"]'), '側欄應出現「專案」資料夾節點');

  // 外部刪除檔案 → 側欄更新（專案/新想法 是剛用「新增模組」建的）
  assert.ok(await page.$('#list .item[data-id="專案/新想法"]'));
  fs.rmSync(path.join(DIR, '專案', '新想法.md'));
  await page.waitForFunction(() => !document.querySelector('#list .item[data-id="專案/新想法"]'), null, { timeout: 8000 });

  console.log('errors:', errors);
  assert.equal(errors.filter(e => !/fonts\.g|net::ERR|Failed to load resource/.test(e)).length, 0, errors.join('\n'));
  console.log('TEST2 OK');
} finally {
  await browser.close(); srv.kill();
}
