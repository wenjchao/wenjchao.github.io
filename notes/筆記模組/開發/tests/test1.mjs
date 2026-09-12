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

// 入口模組（筆記模組.md）在 notes 根層、不在這一包裡（R94）；以「如何編輯內容」為起點
await page.evaluate(() => location.hash = '#/' + encodeURIComponent('如何編輯內容'));
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '如何編輯內容');
const N = (await import('node:fs')).default.readdirSync(ROOT, { recursive: true }).filter(f => /\.md$/.test(f) && !f.startsWith('開發')).length;
assert.equal(await page.textContent('#count'), `${N} 個模組`);
// R94：如何編輯內容＝目錄——子模組卡片都在 如何編輯內容/ 底下；模式合法即可、不釘死每張
const modes = await page.$$eval('.root .card', cs => cs.map(c => [c.dataset.id, c.dataset.mode]));
assert.ok(modes.length >= 6 && modes.every(([id, m]) => id.startsWith('如何編輯內容/') && ['1','2','3'].includes(m)), JSON.stringify(modes));
assert.equal(await page.$('#list .item[data-id="使用說明"]'), null, '使用說明 已併入首頁');

// 進入筆記一（樞紐不在包內，直接導向）；摘要模式：有摘要、無內文
await page.evaluate(() => location.hash = '#/' + encodeURIComponent('範例/筆記一'));
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

// R26、R85：清單裡的扁平卡片——標題列＝晶片膠囊（強調色粗體＋小箭頭同一顆）、卡片本身無框、號碼照舊；R27：有「卡片」切換鈕
const flat = await page.$eval('.root-body ol > li > .card.flat[data-id="範例/第二小點"]', c => ({ style: c.dataset.style, weight: getComputedStyle(c.querySelector('.card-title')).fontWeight, border: getComputedStyle(c).borderTopWidth, mode: c.dataset.mode, triAfterTitle: getComputedStyle(c.querySelector('.tri')).order === '2' && getComputedStyle(c.querySelector('.card-title')).order === '1', bold: c.querySelector('.tri svg path').getAttribute('fill') === 'currentColor', seg: [...c.querySelectorAll('.style-seg button')].map(b => b.dataset.st + (b.classList.contains('on') ? '*' : '')).join(','), marker: getComputedStyle(c.parentElement).listStyleType, n: c.parentElement.dataset.n, before: getComputedStyle(c.parentElement, '::before').content, tnum: getComputedStyle(c.parentElement, '::before').fontVariantNumeric }));
// D28、R66：卡片項的號碼掛在 li（不是卡片標題列——Safari 對 flex 容器的絕對定位 ::before 會算錯位置疊到標題）
assert.deepEqual(flat, { style: 'flat', weight: '700', border: '0px', mode: '1', triAfterTitle: true, bold: false, seg: 'card,flat*,group', marker: 'none', n: '2', before: '"2. "', tnum: 'tabular-nums' });
assert.equal(await page.$eval('.root-body ol > li > .card.flat[data-id="範例/第二小點"] .card-title', t => getComputedStyle(t).borderBottomStyle), 'solid', 'R85：扁平標題＝晶片膠囊（有外框）');
const pillDiff = await page.$eval('.root-body ol > li > .card.flat[data-id="範例/第二小點"]', c => Math.abs(c.querySelector('.card-title').getBoundingClientRect().height - c.querySelector('.tri').getBoundingClientRect().height));
assert.ok(pillDiff < 1, '1.3.38：膠囊兩半要一樣高，差 ' + pillDiff + 'px');
// R62：純文字項的記號也由檢視器畫（Safari 的原生記號度量與自畫的不同，永遠對不齊——所以全部自畫）
const plainLi = await page.$eval('.root-body ol > li:first-child', li => ({ n: li.dataset.n, ls: getComputedStyle(li).listStyleType, mk: getComputedStyle(li, '::before').content }));
assert.deepEqual(plainLi, { n: '1', ls: 'none', mk: '"1.\u00a0"' }, JSON.stringify(plainLi));
assert.equal(await page.$eval('.root > .root-body > .card[data-id="範例/第一小點"] .style-seg button.on', b => b.dataset.st), 'card');
// 切成一般卡片：號碼還在框外、和扁平時同一個位置規則（使用者回報 Safari 切回卡片後號碼跑進框裡）
await page.click('.root-body ol > li > .card[data-id="範例/第二小點"] .style-seg button[data-st="card"]');
const asCard = await page.$eval('.root-body ol > li > .card[data-id="範例/第二小點"]', c => ({ style: c.dataset.style, lst: getComputedStyle(c.parentElement).listStyleType, before: getComputedStyle(c.parentElement, '::before').content, pos: getComputedStyle(c.querySelector(':scope > .card-head')).position, border: getComputedStyle(c).borderTopWidth !== '0px' }));
assert.deepEqual(asCard, { style: 'card', lst: 'none', before: '"2. "', pos: 'relative', border: true });
await page.click('.root-body ol > li > .card[data-id="範例/第二小點"] .style-seg button[data-st="group"]');   // R50、1.3.3：群組縮排＝頁面的一節——標題放大＋rail 色底線；展開時首尾細線標出範圍
const grp = await page.$eval('.root-body ol > li > .card.group[data-id="範例/第二小點"]', c => ({ style: c.dataset.style, weight: getComputedStyle(c.querySelector('.card-title')).fontWeight, border: getComputedStyle(c).borderTopWidth }));
assert.deepEqual(grp, { style: 'group', weight: '700', border: '0px' }, JSON.stringify(grp));   // 收合＝只剩標題＋底線，沒有首尾線
await page.click('.root-body ol > li > .card.group[data-id="範例/第二小點"] .seg button[data-m="3"]');   // 展開
const grp2 = await page.$eval('.root-body ol > li > .card.group[data-id="範例/第二小點"]', c => { const cs = getComputedStyle(c), head = getComputedStyle(c.querySelector(':scope > .card-head')), body = c.querySelector(':scope > .card-body'); return { fs: parseFloat(getComputedStyle(c.querySelector('.card-title')).fontSize), head: head.borderBottomWidth, top: cs.borderTopWidth, bottom: cs.borderBottomWidth, indent: body ? getComputedStyle(body).borderLeftWidth : null }; });
const cardFs = await page.$eval('.root > .root-body > .card[data-id="範例/第一小點"] .card-title', t => parseFloat(getComputedStyle(t).fontSize));
assert.equal(grp2.fs, cardFs, '1.3.4：群組縮排標題大小＝卡片標題 ' + JSON.stringify({ grp: grp2.fs, card: cardFs }));
assert.deepEqual({ head: grp2.head, top: grp2.top, bottom: grp2.bottom, indent: grp2.indent }, { head: '2px', top: '1px', bottom: '1px', indent: '0px' }, '1.3.3 方案二＋五：標題底線 2px、首尾細線 1px、內容不掛左線 ' + JSON.stringify(grp2));
await page.click('.root-body ol > li > .card[data-id="範例/第二小點"] .style-seg button[data-st="flat"]');
assert.equal(await page.$eval('.root-body ol > li > .card[data-id="範例/第二小點"]', c => c.dataset.style), 'flat');
// 展開 補充說明 到全文 → 內含 筆記一（循環） 卡片，最多到摘要
await page.click('.card[data-id="範例/補充說明"] .seg button[data-m="3"]');
const cyc = await page.$eval('.card[data-id="範例/補充說明"] .card[data-id="範例/筆記一"]', c => ({ mode: c.dataset.mode, badge: c.querySelector('.card-badge')?.textContent, disabled: c.querySelector('.seg button[data-m="3"]').disabled }));
assert.deepEqual(cyc, { mode: '2', badge: '循環引用', disabled: true });

// R84：三角形＝循環切換（第二小點沒有摘要：全文→標題→全文，跳過摘要）
await page.click('.root > .root-body > .card[data-id="範例/第二小點"] > .card-head .tri');
assert.equal(await page.$eval('.root > .root-body > .card[data-id="範例/第二小點"]', c => c.dataset.mode), '1');
await page.click('.root > .root-body > .card[data-id="範例/第二小點"] > .card-head .tri');
assert.equal(await page.$eval('.root > .root-body > .card[data-id="範例/第二小點"]', c => c.dataset.mode), '3');
// R84：有摘要的卡片循環 全文→標題→摘要→全文；箭頭＝範圍指示（全文＝兩個箭頭、其餘一個）
const c1 = '.root > .root-body > .card[data-id="範例/第一小點"][data-key$="#0"]';
const triPaths = () => page.$eval(c1 + ' > .card-head .tri svg', s => s.querySelectorAll('path').length);
assert.equal(await page.$eval(c1, c => c.dataset.mode), '3');
assert.equal(await triPaths(), 2, 'R84：全文＝雙箭頭');
await page.click(c1 + ' > .card-head .tri');
assert.equal(await page.$eval(c1, c => c.dataset.mode), '1');
assert.equal(await triPaths(), 1, 'R84：標題＝單箭頭');
await page.click(c1 + ' > .card-head .tri');
assert.equal(await page.$eval(c1, c => c.dataset.mode), '2', 'R84：有摘要 → 循環經過摘要');
await page.click(c1 + ' > .card-head .tri');
assert.equal(await page.$eval(c1, c => c.dataset.mode), '3');

// 晶片就地展開
await page.click('.root-body .chip[data-id="範例/第一小點"] .chip-x');
assert.ok(await page.$('.card.inline-expand.flat[data-id="範例/第一小點"][data-mode="2"]'), 'R85：就地展開＝扁平無框');
assert.equal(await page.$eval('.card.inline-expand > .card-head', h => getComputedStyle(h).display), 'none', 'R86：不重複卡頭（膠囊就是卡頭）');
await page.click('.root-body .chip[data-id="範例/第一小點"] .chip-x');
assert.ok(await page.$('.card.inline-expand[data-mode="3"]'), 'R86：循環到全文');
assert.equal(await page.$eval('.root-body .chip[data-id="範例/第一小點"] .chip-x svg', s => s.querySelectorAll('path').length), 2, 'R86：全文＝雙箭頭');
await page.click('.root-body .chip[data-id="範例/第一小點"] .chip-x');
assert.equal(await page.$('.card.inline-expand'), null, 'R86：全文再按＝收合');
// R88：滑過晶片浮出段控，直接指定層級
await page.hover('.root-body .chip[data-id="範例/第一小點"]');
assert.equal(await page.$eval('.root-body .chip[data-id="範例/第一小點"] .chip-seg', s => getComputedStyle(s).display), 'block', 'R88：滑過浮出段控');
assert.ok(await page.$eval('.root-body .chip[data-id="範例/第一小點"] .chip-seg button[data-m="1"]', b => b.classList.contains('on')), 'R88：目前層級反白');
await page.click('.root-body .chip[data-id="範例/第一小點"] .chip-seg button[data-m="3"]');
assert.ok(await page.$('.card.inline-expand[data-mode="3"]'), 'R88：段控直接跳全文');
await page.hover('.root-body .chip[data-id="範例/第一小點"]');
await page.click('.root-body .chip[data-id="範例/第一小點"] .chip-seg button[data-m="1"]');
assert.equal(await page.$('.card.inline-expand'), null, 'R88：段控收合');
await page.waitForTimeout(400);   // 讓記憶寫完，避免和下面的暫時動作打架

// 全部展開／收合
await page.click('.toolbar >> text=全部展開');   // R93 起側欄也有同名鈕，鎖定工具列
const allModes = await page.$$eval('.root .card', cs => cs.map(c => c.dataset.mode));
assert.ok(allModes.every(m => m === '3' || m === '2'), allModes.join(','));
await page.click('.toolbar >> text=全部收合');
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
const bl = await page.$$eval('.crumbs .parents a.crumb', as => as.map(a => a.textContent));   // R76：被引用於 在頂端麵包屑列
assert.deepEqual(bl.sort(), ['筆記一']);   // 首頁／說明 裡提到第一小點的都在程式碼裡，不算
await page.click('#list .item[data-id="範例/第二小點"]');
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '第二小點');
const bl2 = await page.$$eval('.crumbs .parents a.crumb', as => as.map(a => a.textContent));
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
// 說明文件：程式碼區塊內的 [[...]] 不應變成卡片（R94 後文件在根層；子模組收在節點裡）
assert.equal(await page.$('#list .item[data-id="如何編輯內容/檔案格式"]'), null, '收起的節點裡的模組不該顯示');
await page.click('#list .item[data-id="如何編輯內容"]');
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '如何編輯內容');
const codeChips = await page.$$eval('.root-body code', cs => cs.filter(c => c.querySelector('.chip')).length);
assert.equal(codeChips, 0);
// R92：重整後嚴格跟隨——目前頁可見且標記
await page.reload(); await page.waitForSelector('.root');
assert.ok(await page.$('#list .item.on[data-id="如何編輯內容"]'), '目前模組要標記');
// 程式碼區塊內的 [[...]] 與 ## 摘要 不應被解析（1.3.2 起「檔案格式」＝純內文、無摘要——R52：內容少就整份放內文）
await page.evaluate(() => location.hash = '#/' + encodeURIComponent('如何編輯內容/檔案格式'));
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '檔案格式');
assert.ok((await page.textContent('.root-body pre')).includes('## 摘要'));
assert.equal(await page.$('.root-summary'), null, 'R52：檔案格式 不該有摘要段');
assert.equal(await page.$$eval('.root-body pre .mod-ph, .root-body pre .card', xs => xs.length), 0);
await page.evaluate(() => location.hash = '#/' + encodeURIComponent('如何編輯內容'));
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '如何編輯內容');
assert.ok((await page.$$eval('.root-body > .card', cs => cs.length)) >= 6, '目錄應有六張子模組卡片');
// 檢視原始檔（唯讀來源）
await page.click('text=檢視原始檔');
await page.waitForSelector('.editor textarea');
assert.ok((await page.inputValue('.editor textarea')).startsWith('# 如何編輯內容'));
assert.ok(await page.$('text=複製全文'));
await page.click('text=關閉');
await page.waitForSelector('.root');

// 深色模式切換
await page.click('#themeBtn');
assert.equal(await page.evaluate(() => document.documentElement.dataset.theme), 'dark');
await page.screenshot({ path: TMP + '/shot-dark.png' });
await page.click('#themeBtn');

// 回入口
await page.evaluate(() => location.hash = '#/' + encodeURIComponent('如何編輯內容'));
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '如何編輯內容');

// 截圖：筆記一（含展開）——R94 後入口頁沒有 筆記一 卡片，直接導向
await page.evaluate(() => location.hash = '#/' + encodeURIComponent('範例/筆記一'));
await page.waitForFunction(() => document.querySelector('.root-title')?.textContent === '筆記一');
await page.screenshot({ path: TMP + '/shot-desktop.png', fullPage: false });
await page.setViewportSize({ width: 820, height: 1180 });
await page.screenshot({ path: TMP + '/shot-ipad.png' });
await page.click('#railToggle');
await page.waitForTimeout(300);
await page.screenshot({ path: TMP + '/shot-ipad-rail.png' });

// R75：≤600px 卡頭換成兩列——標題整列、控制鈕第二列；扁平的控制鈕預設隱藏
await page.setViewportSize({ width: 390, height: 800 });
await page.waitForTimeout(250);
const m600 = await page.$eval('.root-body .card[data-id="範例/第一小點"] > .card-head', h => h.querySelector('.card-tools').getBoundingClientRect().top > h.querySelector('.card-title').getBoundingClientRect().top + 5);
assert.ok(m600, 'R75 手機卡頭兩列：控制鈕要在標題下面一列');
await page.evaluate(() => document.activeElement && document.activeElement.blur());   // 前面點過段控鈕，focus-within 會讓控制鈕現身（行為正確）
assert.equal(await page.$eval('.root-body .card.flat > .card-head > .card-tools', t => getComputedStyle(t).display), 'none', 'R75 扁平控制鈕在手機預設隱藏');

console.log('console errors:', errors);
assert.equal(errors.filter(e => !/fonts\.g|net::ERR|Failed to load resource/.test(e)).length, 0, errors.join('\n'));
console.log('TEST1 OK');
await browser.close();

function location_hash(url) { const i = url.indexOf('#'); return i < 0 ? '' : url.slice(i); }
