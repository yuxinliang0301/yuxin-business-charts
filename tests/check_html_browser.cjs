/* 可选浏览器回归：需安装 playwright；TC_BROWSER_PATH 可指定本机 Chrome。
 * node tests/check_html_browser.cjs [现成 HTML 路径]
 * 不传路径时自动在临时目录生成样例；所有临时产物结束后清理。
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const {pathToFileURL} = require('node:url');
const {chromium} = require('playwright');

(async () => {
  const root = path.resolve(__dirname, '..');
  const work = fs.mkdtempSync(path.join(os.tmpdir(), 'tc-html-browser-'));
  let browser;
  try {
    const python = process.env.TC_PYTHON || path.join(root, '.venv/bin/python');
    let source = process.argv[2] && path.resolve(process.argv[2]);
    if (!source) {
      source = path.join(work, 'charts.html');
      execFileSync(python, [path.join(root, 'scripts/tc_render.py'),
        path.join(root, 'examples/waterfall.json'), path.join(root, 'examples/doughnut.json'),
        '--html', source], {stdio: 'pipe'});
    }
    browser = await chromium.launch({headless: true,
      ...(process.env.TC_BROWSER_PATH ? {executablePath: process.env.TC_BROWSER_PATH} : {})});
    const context = await browser.newContext({viewport: {width: 1440, height: 1000}, acceptDownloads: true});
    await context.setOffline(true);
    const page = await context.newPage();
    const failures = [];
    const external = [];
    page.on('pageerror', error => failures.push(error.message));
    page.on('request', request => {
      if (/^https?:/i.test(request.url())) external.push(request.url());
    });
    page.on('dialog', dialog => dialog.accept());
    await page.goto(pathToFileURL(source).href);
    assert.ok(await page.locator('svg .tc-editable').count() > 10);
    assert.equal(await page.locator('svg image, canvas, img').count(), 0);
    assert.equal(await page.locator('.tc-editable[contenteditable="true"]').count(), 0);
    const vectorGeometry = () => page.locator('svg').evaluateAll(svgs => svgs.map(svg =>
      [...svg.querySelectorAll('path,rect,line,polygon,ellipse')].map(shape => shape.outerHTML)));
    const geometry = await vectorGeometry();
    await page.locator('#tc-edit').click();
    const box = page.locator('.tc-editable').first();
    const note = page.locator('.tc-editable').nth(1);
    const originalNote = await note.innerText();
    const title = '增长来自新增客户';
    await box.fill(title);
    await box.press('End');
    await box.press('Enter');
    await page.keyboard.insertText('说明可直接在页面修改');
    assert.match(await box.innerText(), /增长来自新增客户\n+说明可直接在页面修改/);
    const editedTitle = await box.innerText();
    const payload = '<img src=x onerror="window.injected=1"> & 中文备注';
    // 点击可见文字；整行文本框中部可能与其他批注重合。
    await note.locator('span').first().click();
    await note.press('ControlOrMeta+A');
    await note.evaluate((element, text) => {
      const clipboardData = new DataTransfer();
      clipboardData.setData('text/plain', text);
      clipboardData.setData('text/html', '<img src=x onerror="window.injected=1"><b>富文本</b>');
      element.dispatchEvent(new ClipboardEvent('paste', {clipboardData, bubbles: true, cancelable: true}));
    }, payload);
    assert.equal(await note.innerText(), payload);
    assert.equal(await page.locator('svg img, svg script').count(), 0);
    assert.equal(await page.evaluate(() => window.injected), undefined);
    await page.locator('#tc-fit').click();
    assert.deepEqual(await vectorGeometry(), geometry);

    const downloadPromise = page.waitForEvent('download');
    await page.locator('#tc-save').click();
    const download = await downloadPromise;
    const saved = path.join(work, 'saved.html');
    await download.saveAs(saved);
    await page.goto(pathToFileURL(saved).href);
    assert.equal(await page.locator('.tc-editable').first().innerText(), editedTitle);
    assert.equal(await page.locator('.tc-editable').nth(1).innerText(), payload);
    assert.equal(await page.locator('.tc-editable[contenteditable="true"]').count(), 0);
    assert.deepEqual(await vectorGeometry(), geometry);

    await page.locator('#tc-edit').click();
    await page.locator('.tc-editable').nth(1).fill('第二次编辑');
    await page.locator('#tc-reset').click();
    assert.equal(await page.locator('.tc-editable').nth(1).innerText(), payload);
    assert.notEqual(payload, originalNote);
    await page.setViewportSize({width: 390, height: 844});
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    assert.ok(await page.locator('.tc-slide-scroll').first().evaluate(el => el.scrollWidth > el.clientWidth));
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#tc-edit').getAttribute('aria-pressed'), 'false');
    assert.deepEqual(failures, []);
    assert.deepEqual(external, []);
    console.log('PASS: 离线矢量显示、中文换行、纯文本粘贴、图形保持、下载重开、再次编辑、还原、小屏滚动、零外部请求');
  } finally {
    if (browser) await browser.close();
    fs.rmSync(work, {recursive: true, force: true});
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
