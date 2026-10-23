const { chromium } = require('playwright')
const fs = require('node:fs')
const path = require('node:path')
const assert = require('node:assert/strict')
const root = __dirname; const base = 'http://127.0.0.1:5198/'
;(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' })
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 })
  const errors = []; page.on('pageerror', error => errors.push(error.message))
  const routes = []
  for (let route = 0; route < 3; route++) {
    await page.goto(base + '?still=1')
    assert.match(await page.locator('.finance__fine').first().innerText(), /13/)
    await page.locator('.finance__intro-card .finance__primary').click()
    await page.locator('.finance__option').first().waitFor()
    const seen = []
    for (let index = 0; index < 13; index++) {
      const item = await page.evaluate(() => ({ id: window.__financePreview.item.value.id, progress: window.__financePreview.progress.value }))
      assert.equal(item.progress, index + 1); seen.push(item.id)
      assert.equal(await page.getByText('下一题', { exact: true }).count(), 0)
      assert.equal(await page.locator('.finance__response').count(), 0)
      await page.locator('.finance__option').nth(index === 0 ? route : 0).click()
      await page.waitForFunction(id => window.__financePreview.phase.value === 'result' || window.__financePreview.item.value.id !== id, item.id)
    }
    assert.equal(await page.locator('.finance__result-title').count(), 1)
    assert.equal(await page.evaluate(() => window.__financePreview.answers.value.length), 13)
    assert.equal(await page.evaluate(() => window.__financePreview.result.value.answeredCount), 12)
    assert(seen.every(id => !id.startsWith('B')))
    if (route === 0) assert(seen.slice(1).every(id => id.startsWith('N')))
    await page.getByText('查看答案', { exact: true }).click()
    assert.equal(await page.locator('.finance__transcript > view').count(), 12)
    await page.getByText('再测一次', { exact: true }).click()
    assert.equal(await page.evaluate(() => window.__financePreview.item.value.id), 'EXPERIENCE')
    assert.equal(await page.evaluate(() => window.__financePreview.answers.value.length), 0)
    routes.push(seen)
  }
  await page.goto(base + '?screen=S03&route=stock&still=1')
  const before = await page.evaluate(() => window.__financePreview.progress.value)
  await page.getByText('不熟，换成日常题', { exact: true }).click()
  assert.equal(await page.evaluate(() => window.__financePreview.item.value.id), 'N03')
  assert.equal(await page.evaluate(() => window.__financePreview.progress.value), before)
  await page.getByText('跳过', { exact: true }).click()
  await page.waitForFunction(() => window.__financePreview.item.value.id === 'F04')
  await page.goto(base + '?screen=N01&typing=1')
  await page.locator('.finance__typing-hint').waitFor(); await page.locator('.finance__setup').click()
  assert.equal(await page.locator('.finance__option').count(), 4)
  assert.equal(await page.evaluate(() => window.__financePreview.answers.value.length), 1)
  await page.evaluate(() => { const quiz = window.__financePreview; quiz.choose(quiz.item.value.options[0].id); quiz.pause() })
  await page.waitForTimeout(350)
  assert.equal(await page.evaluate(() => window.__financePreview.item.value.id), 'N01')
  await page.evaluate(() => window.__financePreview.resume())
  await page.waitForFunction(() => window.__financePreview.item.value.id === 'N02')
  const screens = [
    ['01-cover.png','开场 · 共13题','cover'],
    ['02-experience.png','第1题 · 投资经验','experience'],
    ['03-daily.png','日常 · 多了一笔钱','N01'],
    ['04-terms.png','日常 · 条款没看懂','N03'],
    ['05-budget.png','日常 · 下周要用的钱','N07'],
    ['06-fund.png','基金 · 第一次选基金','F02'],
    ['07-holdings.png','基金 · 同方向三只','F06'],
    ['08-dividend.png','基金 · 分红怎么收','F08'],
    ['09-notice.png','股票 · 公司公告','S03'],
    ['10-twelve.png','股票 · 十二只持仓','S06'],
    ['11-order.png','股票 · 挂单差一点','S09&theme=dark'],
    ['12-result.png','结果 · 展开可看依据','result&route=fund'],
  ]
  fs.mkdirSync(path.join(root, 'ui'), { recursive: true })
  for (const [file, title, screen] of screens) {
    await page.goto(base + `?screen=${screen}&still=1`); await page.locator('.finance').waitFor()
    await page.screenshot({ path: path.join(root, 'ui', file) })
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, title)
  }
  fs.writeFileSync(path.join(root, 'ui/screens.json'), JSON.stringify(screens.map(([file,title,screen]) => ({file,title,screen})),null,2))
  for (const width of [320, 430]) {
    await page.setViewportSize({ width, height: width === 320 ? 640 : 932 })
    await page.goto(base + '?screen=S03&still=1'); await page.locator('.finance__option').first().waitFor()
    const nav = await page.locator('.finance-preview-nav').boundingBox(); const scroll = await page.locator('.finance__scroll').boundingBox()
    assert(scroll.y >= nav.y + nav.height)
    const bounds = await page.locator('.finance__question-card').boundingBox()
    assert(bounds.x >= 0 && bounds.x + bounds.width <= width + 1)
    await page.screenshot({ path: path.join(root, `ui/check-${width}.png`) })
  }
  await page.goto(base + '?screen=empty&still=1')
  assert.equal(await page.locator('.finance__result-title').innerText(), '这次先留白')
  assert.equal(await page.locator('.finance__evidence').count(), 0)
  await page.route('**/scene-sofa.svg', route => route.abort())
  await page.goto(base + '?screen=N01&still=1'); await page.locator('.finance__retry').waitFor()
  assert.equal(await page.locator('.finance__option').count(), 4)
  assert.deepEqual(errors, [])
  console.log(JSON.stringify({ routes, screenshots: screens.length, passed: ['三路线真实点选各13题','选完自动切题','没有确认或后续页','经验不算画像','换题不增加进度','后台不连跳','补全不穿透','导航安全区','浅深色与窄屏'] },null,2))
  await browser.close()
})().catch(error => { console.error(error); process.exit(1) })
