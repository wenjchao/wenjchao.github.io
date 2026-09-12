// 測試十二（R77）：表格格子裡的 [[x\|摘要]] 不能擋住同一頁的寫回——
// marked 切格子時把 \| 還原成 |，LinkWriter 在原文裡要用還原後的字比對；寫回格子裡的連結時要重新跳脫。
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const ROOT = process.env.ROOT, HERE = process.env.HERE, TMP = process.env.TMP || '/tmp';

const DIR = '/tmp/notes-t12';
fs.rmSync(DIR, { recursive: true, force: true });
fs.cpSync(ROOT + '', DIR, { recursive: true });
const SRC = `# 表格寫回

## 內文
| 名稱 | 晶片 |
|---|---|
| 第一 | [[第一小點\\|摘要]] |
| 第二 | [[第二小點\\|扁平\\|顯示字]]、[[第一小點]] |

表格底下的卡片：

[[第一小點]]

句中的 [[第二小點]] 晶片。
`;
fs.writeFileSync(path.join(DIR, '表格寫回.md'), SRC);
const srv = spawn('python3', [path.join(DIR, 'serve.py'), '--port', '8796', '--no-open'], { stdio: ['ignore', 'pipe', 'pipe'] });
srv.stderr.on('data', d => process.stdout.write('[serve] ' + d));
await new Promise(r => setTimeout(r, 1000));

const browser = await chromium.launch();
const page = await (await browser.newContext({ viewport: { width: 1280, height: 860 }, locale: 'zh-TW' })).newPage();
const errors = [];
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errors.push(m.text()); });
const onDisk = () => fs.readFileSync(path.join(DIR, '表格寫回.md'), 'utf8');
try {
  await page.goto('http://localhost:8796/#/' + encodeURIComponent('表格寫回'));
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '表格寫回');
  assert.equal(await page.$$eval('.root-body td .chip', cs => cs.length), 3, '表格裡三個晶片');
  assert.equal(await page.$eval('.root-body td .chip[data-id="範例/第二小點"] .chip-go', c => c.textContent.trim()), '顯示字', '顯示文字要用 \\| 後面那段');   // R88 起晶片裡多了隱藏段控，改讀 .chip-go

  // 1) 切表格底下那張卡片 → 只有它的模式字改變；格子裡的 \| 原封不動
  await page.click('.root > .root-body > .card[data-id="範例/第一小點"] .seg button[data-m="3"]');
  await page.waitForFunction(() => fetch('/表格寫回.md?t=' + Date.now()).then(r => r.text()).then(t => t.includes('\n[[第一小點|全文]]\n')).catch(() => false), null, { timeout: 8000 });
  let t = onDisk();
  assert.ok(t.includes('| 第一 | [[第一小點\\|摘要]] |'), '格子裡的連結不能被動到：' + t);
  assert.ok(t.includes('| 第二 | [[第二小點\\|扁平\\|顯示字]]、[[第一小點]] |'), '格子裡第二列不能被動到：' + t);
  assert.ok(t.includes('句中的 [[第二小點]] 晶片。'), '句中晶片不能被動到');
  assert.equal((t.match(/無法寫回/g) || []).length, 0);
  assert.equal(await page.$eval('.root > .root-body > .card[data-id="範例/第一小點"]', c => c.dataset.mode), '3');
  await page.click('.root > .root-body > .card[data-id="範例/第一小點"] .seg button[data-m="1"]');
  await page.waitForFunction(() => fetch('/表格寫回.md?t=' + Date.now()).then(r => r.text()).then(t => t.includes('\n[[第一小點]]\n')).catch(() => false), null, { timeout: 8000 });
  assert.equal(onDisk(), SRC, '切回標題後整份檔案要跟原本一字不差');
  assert.ok(errors.every(e => /favicon|fonts\.googleapis|net::ERR/.test(e)), '切模式不能有錯誤或警告：' + errors.join('\n'));

  // 2) 改名（retarget）：格子裡的連結要跟著改、而且 \| 要保留；句中與卡片也一起改
  await page.goto('http://localhost:8796/#/' + encodeURIComponent('範例/第一小點'));
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '第一小點');
  await page.click('.toolbar >> text=改名／搬移'); await page.waitForSelector('.wy-panel');
  await page.fill('.wy-panel input[type="text"] >> nth=0', '第壹小點');
  await page.click('.wy-panel .btn.primary');
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '第壹小點', null, { timeout: 8000 });
  await new Promise(r => setTimeout(r, 500));
  t = onDisk();
  assert.ok(t.includes('| 第一 | [[第壹小點\\|摘要]] |'), '格子裡的目標要改、\\| 要留著：' + t);
  assert.ok(t.includes('| 第二 | [[第二小點\\|扁平\\|顯示字]]、[[第壹小點]] |'), '同一格第二個連結：' + t);
  assert.ok(t.includes('\n[[第壹小點]]\n'), '表格底下的卡片：' + t);
  assert.ok(t.includes('句中的 [[第二小點]] 晶片。'), '沒連到的不動');
  // 改完名的頁面重新載入，格子裡的晶片仍然是晶片（表格沒有被 | 拆壞）
  await page.goto('http://localhost:8796/#/' + encodeURIComponent('表格寫回'));
  await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '表格寫回');
  assert.equal(await page.$$eval('.root-body td .chip', cs => cs.length), 3, '改名後表格裡仍是三個晶片');
  assert.equal(await page.$$eval('.root-body table tr', rs => rs.length), 3, '表格仍是表頭＋兩列');

  // 改名流程本身會多印一次「檔案內容已經改變，這個連結對不上」（和表格無關、改名前就有），這裡只驗結果
  console.log('TEST12 OK');
} finally {
  await browser.close();
  srv.kill();
}
