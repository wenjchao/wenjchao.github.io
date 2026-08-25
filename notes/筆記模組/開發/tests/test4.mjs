// 測試四：合成拖放（dt.files 後備路徑）、沒有摘要的 [[x|摘要]] 卡片行為、全部展開的終止
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
const ROOT = process.env.ROOT, HERE = process.env.HERE, TMP = process.env.TMP || '/tmp';
const browser = await chromium.launch();
const page = await (await browser.newContext({ viewport: { width: 1100, height: 800 } })).newPage();
const errs = []; page.on('pageerror', e => errs.push(e.message));
await page.goto('file://' + ROOT + '/index.html');
await page.waitForSelector('.welcome');
await page.evaluate(() => {
  const dt = new DataTransfer();
  dt.items.add(new File(['# 甲\n\n## 內文\n內文甲\n\n[[乙|摘要]]\n\n[[甲|全文]]\n'], '甲.md'));
  dt.items.add(new File(['# 乙\n\n## 內文\n內文乙（沒有摘要）'], '乙.md'));
  document.body.dispatchEvent(new DragEvent('drop', { dataTransfer: dt, bubbles: true, cancelable: true }));
});
await page.waitForSelector('.root');
assert.equal(await page.textContent('#count'), '2 個模組');
await page.goto('file://' + ROOT + '/index.html#/' + encodeURIComponent('甲'));
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '甲');
// [[乙|摘要]] 但乙沒有摘要 → 一開始只顯示標題；按 ▸ 後直接到全文
const yi = '.root-body > .card[data-id="乙"]';
assert.equal(await page.$eval(yi, c => c.dataset.mode), '1');
await page.click(yi + ' .tri');
assert.equal(await page.$eval(yi, c => c.dataset.mode), '3');
assert.ok((await page.textContent(yi + ' .card-body')).includes('內文乙'));
// 自我引用 [[甲|全文]] → 循環，停在 2 以下；這裡甲沒有摘要 → 1
const jia = '.root-body > .card[data-id="甲"]';
assert.equal(await page.$eval(jia, c => c.dataset.mode), '1');
assert.equal(await page.$eval(jia + ' .seg button[data-m="3"]', b => b.disabled), true);
// 全部展開 必須在短時間內結束
const t0 = Date.now(); await page.click('text=全部展開'); assert.ok(Date.now() - t0 < 3000);
assert.equal(await page.$eval(yi, c => c.dataset.mode), '3');
console.log('errs', errs); assert.equal(errs.length, 0);
console.log('TEST4 OK'); await browser.close();
