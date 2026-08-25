// 測試一：單檔（內嵌）模式 — 解析、卡片模式、巢狀、循環、晶片、導覽、搜尋
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
const ROOT = process.env.ROOT, HERE = process.env.HERE, TMP = process.env.TMP || '/tmp';

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 860 }, locale: 'zh-TW' });
const page = await ctx.newPage();
const errors = [];
page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errors.push(`${m.type()}: ${m.text()}`); });
page.on('pageerror', e => errors.push('pageerror: ' + e.message));

await page.goto('file://' + TMP + '/single.html');
await page.waitForSelector('.root');

// 首頁為入口
assert.equal(await page.textContent('.root-title'), '首頁');
const N = (await import('node:fs')).default.readdirSync(ROOT, { recursive: true }).filter(f => /\.md$/.test(f) && !f.startsWith('開發')).length;
assert.equal(await page.textContent('#count'), `${N} 個模組`);
// 首頁＝入口＋說明總覽（R42）：第一張是 範例/筆記一（摘要），後面是 說明/ 的各篇（摘要）
const modes = await page.$$eval('.root .card', cs => cs.map(c => [c.dataset.id, c.dataset.mode]));
assert.deepEqual(modes[0], ['範例/筆記一', '2']);
assert.ok(modes.length >= 13 && modes.slice(1).every(([id, m]) => id.startsWith('說明/') && m === '2'), JSON.stringify(modes));
assert.equal(await page.$('#list .item[data-id="使用說明"]'), null, '使用說明 已併入首頁');
// 摘要模式下有摘要、無內文
assert.ok(await page.$('.root .card[data-id="範例/筆記一"] > .card-summary'));
assert.equal(await page.$('.root .card[data-id="範例/筆記一"] > .card-body'), null);

// 進入筆記一
await page.click('.card[data-id="範例/筆記一"] .card-title');
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '筆記一');
assert.equal(location_hash(await page.url()), '#/' + encodeURIComponent('範例/筆記一'));
const modes2 = await page.$$eval('.root > .root-body > .card', cs => cs.map(c => [c.dataset.id, c.dataset.mode]));
assert.deepEqual(modes2, [['範例/第一小點', '3'], ['範例/第二小點', '3'], ['範例/第一小點', '2']]);
// 第一小點(全文) 裡面有 補充說明(摘要)，補充說明裡（未展開）不渲染內文
const nested = await page.$$eval('.root .card[data-id="範例/第一小點"][data-mode="3"] .card', cs => cs.map(c => [c.dataset.id, c.dataset.mode]));
assert.deepEqual(nested, [['範例/補充說明', '2']]);
// 第二小點沒有摘要：摘要按鈕 disabled
assert.equal(await page.$eval('.card[data-id="範例/第二小點"] .seg button[data-m="2"]', b => b.disabled), true);
// 行內晶片存在
assert.ok(await page.$('.root-body .chip[data-id="範例/第一小點"]'));
// R20：被連結的模組標題（卡片標題、晶片）在五種樣式下都是粗體（700）
for (const st of ['ink', 'card', 'outline', 'sketch', 'tab']) {
  await page.evaluate(s => { document.documentElement.dataset.style = s; }, st);
  const w = await page.$$eval('.root-body .card:not(.flat) > .card-head > .card-title, .root-body .chip:not(.flat) .chip-go', es => es.map(e => getComputedStyle(e).fontWeight));
  assert.ok(w.length >= 2 && w.every(x => x === '700'), `${st}: ${w.join(',')}`);
}
await page.evaluate(() => { document.documentElement.dataset.style = 'ink'; });

// R26：清單裡的扁平卡片——沒有框、標題一般字重、粗箭頭在標題後面、號碼照舊；R27：有「卡片」切換鈕
const flat = await page.$eval('.root-body ol > li > .card.flat[data-id="範例/第二小點"]', c => ({ style: c.dataset.style, weight: getComputedStyle(c.querySelector('.card-title')).fontWeight, border: getComputedStyle(c).borderTopWidth, mode: c.dataset.mode, triAfterTitle: getComputedStyle(c.querySelector('.tri')).order === '2' && getComputedStyle(c.querySelector('.card-title')).order === '1', bold: c.querySelector('.tri svg path').getAttribute('fill') === 'currentColor', seg: [...c.querySelectorAll('.style-seg button')].map(b => b.dataset.st + (b.classList.contains('on') ? '*' : '')).join(','), marker: getComputedStyle(c.parentElement).listStyleType, n: c.querySelector(':scope > .card-head').dataset.n, before: getComputedStyle(c.querySelector(':scope > .card-head'), '::before').content }));
// D28：清單裡的卡片——原生號碼關掉（Safari 會把它畫進卡片裡），號碼由 CSS 照 data-n 畫在標題列左邊、框外
assert.deepEqual(flat, { style: 'flat', weight: '400', border: '0px', mode: '1', triAfterTitle: true, bold: true, seg: 'card,flat*', marker: 'none', n: '2', before: '"2."' });
assert.equal(await page.$eval('.root > .root-body > .card[data-id="範例/第一小點"] .style-seg button.on', b => b.dataset.st), 'card');
// 切成一般卡片：號碼還在框外、和扁平時同一個位置規則（使用者回報 Safari 切回卡片後號碼跑進框裡）
await page.click('.root-body ol > li > .card[data-id="範例/第二小點"] .style-seg button[data-st="card"]');
const asCard = await page.$eval('.root-body ol > li > .card[data-id="範例/第二小點"]', c => ({ style: c.dataset.style, lst: getComputedStyle(c.parentElement).listStyleType, before: getComputedStyle(c.querySelector(':scope > .card-head'), '::before').content, pos: getComputedStyle(c.querySelector(':scope > .card-head')).position, border: getComputedStyle(c).borderTopWidth !== '0px' }));
assert.deepEqual(asCard, { style: 'card', lst: 'none', before: '"2."', pos: 'relative', border: true });
await page.click('.root-body ol > li > .card[data-id="範例/第二小點"] .style-seg button[data-st="flat"]');
assert.equal(await page.$eval('.root-body ol > li > .card[data-id="範例/第二小點"]', c => c.dataset.style), 'flat');
// 展開 補充說明 到全文 → 內含 筆記一（循環） 卡片，最多到摘要
await page.click('.card[data-id="範例/補充說明"] .seg button[data-m="3"]');
const cyc = await page.$eval('.card[data-id="範例/補充說明"] .card[data-id="範例/筆記一"]', c => ({ mode: c.dataset.mode, badge: c.querySelector('.card-badge')?.textContent, disabled: c.querySelector('.seg button[data-m="3"]').disabled }));
assert.deepEqual(cyc, { mode: '2', badge: '循環引用', disabled: true });

// 三角形收合／展開
await page.click('.root > .root-body > .card[data-id="範例/第二小點"] > .card-head .tri');
assert.equal(await page.$eval('.root > .root-body > .card[data-id="範例/第二小點"]', c => c.dataset.mode), '1');
await page.click('.root > .root-body > .card[data-id="範例/第二小點"] > .card-head .tri');
assert.equal(await page.$eval('.root > .root-body > .card[data-id="範例/第二小點"]', c => c.dataset.mode), '3');

// 晶片就地展開
await page.click('.root-body .chip[data-id="範例/第一小點"] .chip-x');
assert.ok(await page.$('.card.inline-expand[data-id="範例/第一小點"][data-mode="2"]'));
await page.click('.root-body .chip[data-id="範例/第一小點"] .chip-x');
assert.equal(await page.$('.card.inline-expand'), null);
await page.waitForTimeout(400);   // 讓記憶寫完，避免和下面的暫時動作打架

// 全部展開／收合
await page.click('text=全部展開');
const allModes = await page.$$eval('.root .card', cs => cs.map(c => c.dataset.mode));
assert.ok(allModes.every(m => m === '3' || m === '2'), allModes.join(','));
await page.click('text=全部收合');
assert.ok((await page.$$eval('.root .card', cs => cs.map(c => c.dataset.mode))).every(m => m === '1'));
// R22（唯讀來源的退路，D24）：個別切換過的卡片會記住；「全部展開／收合」是暫時動作，不記
await page.waitForTimeout(400);
await page.reload(); await page.waitForSelector('.root');
assert.deepEqual(await page.$$eval('.root > .root-body > .card', cs => cs.map(c => c.dataset.mode)), ['3', '3', '2'], '全部收合不該被記住');
assert.equal(await page.$eval('.card[data-id="範例/補充說明"]', c => c.dataset.mode), '3', '個別切換過的要記住');
assert.equal(await page.$eval('.toolbar .reset-btn', b => b.hidden), false);
await page.click('.toolbar .reset-btn');
await page.waitForFunction(() => document.querySelector('.toolbar .reset-btn')?.hidden === true);
assert.equal(await page.$eval('.card[data-id="範例/補充說明"]', c => c.dataset.mode), '2', '回到預設');

// 被引用於
await page.click('#list .item[data-id="範例/第一小點"]');
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '第一小點');
const bl = await page.$$eval('.backlinks .chip-go', as => as.map(a => a.textContent));
assert.deepEqual(bl.sort(), ['筆記一']);   // 首頁／說明 裡提到第一小點的都在程式碼裡，不算
await page.click('#list .item[data-id="範例/第二小點"]');
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '第二小點');
const bl2 = await page.$$eval('.backlinks .chip-go', as => as.map(a => a.textContent));
assert.deepEqual(bl2.sort(), ['筆記一', '補充說明']);   // 補充說明 用一般 Markdown 連結 [..](第二小點.md)

// 搜尋
await page.fill('#search', '第三層的模組');
await page.waitForFunction(() => document.querySelector('#count')?.textContent.startsWith('1 /'));
const found = await page.$$eval('#list .item', as => as.map(a => a.dataset.id).sort());
assert.deepEqual(found, ['範例/補充說明']);
await page.fill('#search', '');

// 補充說明：找不到的模組為虛線晶片；.md 連結改為內部連結
await page.click('#list .item[data-id="範例/補充說明"]');
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '補充說明');
assert.ok(await page.$('.root-body .chip.missing[data-target="還沒寫的模組"]'));
assert.equal(await page.$eval('.root-body a.mod-link', a => a.getAttribute('href')), '#/' + encodeURIComponent('範例/第二小點'));
// 使用說明／說明文件：程式碼區塊內的 [[...]] 不應變成卡片（側欄是樹狀：先展開「說明」）
assert.equal(await page.$('#list .item[data-id="說明/寫作規範"]'), null, '收起的資料夾裡的模組不該顯示');
await page.click('#list .item.folder[data-node="說明"] .chev');
await page.click('#list .item[data-id="說明/寫作規範"]');
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '寫作規範');
assert.ok((await page.textContent('.root-body pre')).includes('## 摘要'));
const codeChips = await page.$$eval('.root-body code', cs => cs.filter(c => c.querySelector('.chip')).length);
assert.equal(codeChips, 0);
assert.equal(await page.$$eval('.root-body pre .mod-ph, .root-body pre .card', xs => xs.length), 0);
// R24：側欄樹的展開狀態也記住
await page.reload(); await page.waitForSelector('.root');
assert.ok(await page.$('#list .item[data-id="說明/寫作規範"]'), '樹的展開狀態要記住');
assert.ok(await page.$('#list .item.on[data-id="說明/寫作規範"]'), '目前模組要標記');
await page.click('#brand');
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '首頁');
assert.ok((await page.$$eval('.root-body > .card', cs => cs.length)) >= 13, '首頁應有範例＋12 篇說明的卡片');
// 檢視原始檔（唯讀來源）
await page.click('text=檢視原始檔');
await page.waitForSelector('.editor textarea');
assert.ok((await page.inputValue('.editor textarea')).startsWith('# 首頁'));
assert.ok(await page.$('text=複製全文'));
await page.click('text=關閉');
await page.waitForSelector('.root');

// 深色模式切換
await page.click('#themeBtn');
assert.equal(await page.evaluate(() => document.documentElement.dataset.theme), 'dark');
await page.screenshot({ path: TMP + '/shot-dark.png' });
await page.click('#themeBtn');

// 回首頁
await page.click('#brand');
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '首頁');

// 截圖：筆記一（含展開）
await page.click('.card[data-id="範例/筆記一"] .card-title');
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '筆記一');
await page.screenshot({ path: TMP + '/shot-desktop.png', fullPage: false });
await page.setViewportSize({ width: 820, height: 1180 });
await page.screenshot({ path: TMP + '/shot-ipad.png' });
await page.click('#railToggle');
await page.waitForTimeout(300);
await page.screenshot({ path: TMP + '/shot-ipad-rail.png' });

console.log('console errors:', errors);
assert.equal(errors.filter(e => !/fonts\.g|net::ERR|Failed to load resource/.test(e)).length, 0, errors.join('\n'));
console.log('TEST1 OK');
await browser.close();

function location_hash(url) { const i = url.indexOf('#'); return i < 0 ? '' : url.slice(i); }
