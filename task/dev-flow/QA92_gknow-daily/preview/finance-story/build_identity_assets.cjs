const fs = require('node:fs')
const path = require('node:path')
const { chromium } = require('playwright')
const sharp = require('sharp')
const base = path.resolve(__dirname, '../../../../../business-repo/uni-gknow/src/static/illustrations/finance-story/identity')
const profiles = [
 ['rush','抢先上车鹅','别催，我已经在车上了'], ['reserve','留个后手鹅','别急，我还有另一半'],
 ['promise','按约办事鹅','我先跟昨天的自己对一下账'], ['reason','认理由鹅','先别报涨跌，告诉我为什么'],
 ['price','心里有个价鹅','道理我懂，先等它回到那个价'], ['wind','借个风向鹅','等等，我问个人'],
 ['close','收工落袋鹅','这局先到这，下一局再说'], ['default','理财人格','12个股票现场，你会怎么选？'],
]
;(async () => {
 for (const file of fs.readdirSync(base).filter(file => file.endsWith('.svg'))) {
  await sharp(path.join(base, file)).resize(640).png().toFile(path.join(base, file.replace('.svg','.png')))
 }
 const browser = await chromium.launch({ headless:true, executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' })
 try {
  const page = await browser.newPage({viewport:{width:500,height:400},deviceScaleFactor:1})
  for (const [key, title, line] of profiles) {
   const svg = fs.readFileSync(path.join(base, `${key === 'default' ? 'mark' : key}.svg`)).toString('base64')
   await page.setContent(`<style>*{box-sizing:border-box}body{margin:0;background:#fff2d7;color:#294e50;font-family:'PingFang SC',sans-serif;padding:22px}.card{height:356px;border:2px solid #294e50;border-radius:20px;background:#fff9ed;display:flex;flex-direction:column;align-items:center}small{font-size:14px;margin-top:17px}img{width:185px;height:163px;object-fit:contain}h1{font-size:28px;margin:5px 0 12px}p{font-size:17px;margin:0}</style><div class="card"><small>鹅懂个啥 · 理财人格</small><img src="data:image/svg+xml;base64,${svg}"><h1>${title}</h1><p>${line}</p></div>`)
   await page.locator('img').evaluate(img=>img.decode())
   await page.screenshot({path:path.join(base,`share-${key}.png`)})
  }
 } finally { await browser.close() }
 console.log('PASS: 8张500×400分享卡与8张Canvas插画已生成')
})().catch(e=>{console.error(e);process.exit(1)})
