const { chromium } = require('playwright')
const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const root = path.join(__dirname,'ui','stock-full');fs.mkdirSync(root,{recursive:true})
;(async()=>{
 const browser = await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'})
 try {
  const page = await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1})
  const errors=[];page.on('pageerror',e=>errors.push(e.message))
  const goto = async(query='')=>{await page.goto(`http://127.0.0.1:5198/?still=1&${query}`);await page.locator('.finance__scroll').waitFor()}
  const shot = async(name)=>page.screenshot({path:path.join(root,`${name}.png`)})
  const noOverflow = async()=>{
   assert.equal(await page.locator('.finance__scroll').evaluate(el=>el.scrollWidth>el.clientWidth+1),false)
   assert(await page.locator('.finance__option').evaluateAll(els=>els.every(el=>el.scrollWidth<=el.clientWidth+1)))
  }
  await goto();await page.locator('.finance__cover-start').waitFor()
  assert((await page.locator('.finance__cover-note').innerText()).includes('跳过'))
  assert.equal(await page.locator('.finance__cover-mark').evaluate(el=>el.complete&&el.naturalWidth>0),true)
  await shot('cover');await page.locator('.finance__cover-start').click()
  const seq='ACACACAABDAC'
  for(let i=0;i<12;i++){
   const id=`Q${String(i+1).padStart(2,'0')}`
   await page.waitForFunction(id=>window.__financePreview.item.value.id===id,id)
   assert.equal(await page.locator('.finance__option').count(),4)
   assert((await page.locator('.finance__progress-head').innerText()).includes(`${i+1} / 12`))
   await noOverflow();await shot(`question-${i+1}`)
   await page.locator('.finance__option').nth('ABCD'.indexOf(seq[i])).click()
  }
  await page.locator('.finance__result-title').waitFor()
  assert.equal(await page.locator('.finance__result-title').innerText(),'抢先上车鹅')
  assert.equal(await page.locator('.finance__transcript,.finance__evidence,.finance__recap').count(),0)
  assert.equal(await page.locator('.finance__type-art').evaluate(el=>el.complete&&el.naturalWidth>0),true)
  await shot('result');await page.locator('.finance__scroll').evaluate(el=>el.scrollTop=el.scrollHeight);await shot('result-bottom')
  await page.getByText('再测一次',{exact:true}).click()
  assert.equal(await page.evaluate(()=>window.__financePreview.answers.value.length),0)
  await page.evaluate(()=>{const q=window.__financePreview;q.choose(q.item.value.options[0].id);q.choose(q.item.value.options[1].id);q.pause()})
  await page.waitForTimeout(300)
  assert.equal(await page.evaluate(()=>window.__financePreview.answers.value.length),1)
  assert.equal(await page.evaluate(()=>window.__financePreview.item.value.id),'Q01')
  await page.evaluate(()=>window.__financePreview.resume())
  await page.waitForFunction(()=>window.__financePreview.item.value.id==='Q02')
  // 跳过全部12题，真实点击，最后无分享入口。
  await goto();await page.locator('.finance__cover-start').click()
  for(let i=0;i<12;i++){
   await page.waitForFunction(i=>window.__financePreview.cursor.value===i,i)
   await page.getByText('跳过此题',{exact:true}).click()
  }
  await page.getByText('这次先不贴名字',{exact:true}).waitFor()
  assert.equal(await page.locator('[open-type="share"]').count(),0)
  await shot('empty')
  const results={M:seq,H:'CCBCCCBBDBBC',P:'ACDABCCAACCB',E:'BDCDDBDCCCCB',L:'BBBBBDBABACC',S:'ADDDDDADCBBA',C:'DDDABADBCADD',mixed:'CBABABCABADC',scattered:'BDBDBCAADCDD'}
  for(const [width,height,theme] of [[320,640,'light'],[390,844,'dark']]){
   await page.setViewportSize({width,height})
   await goto(`theme=${theme}`);await noOverflow();await shot(`cover-${theme}-${width}`)
   for(let i=1;i<=12;i++){
    await goto(`screen=Q${String(i).padStart(2,'0')}&theme=${theme}`)
    await page.locator('.finance__option').first().waitFor();await noOverflow()
    if([1,8,12].includes(i)) await shot(`question-${i}-${theme}-${width}`)
   }
   for(const [kind,choices] of Object.entries(results)){
    await goto(`screen=result&choices=${choices}&theme=${theme}`)
    await page.locator('.finance__result-title').waitFor();await noOverflow()
    if(['M','mixed','scattered'].includes(kind))await shot(`result-${kind}-${theme}-${width}`)
    assert(!/你选过|查看答案|Q\d\d/.test(await page.locator('.finance__result').innerText()))
    assert.equal(await page.locator('.finance__type-art').evaluateAll(els=>els.every(el=>el.complete&&el.naturalWidth>0)),true)
   }
  }
  await page.route('**/rush.svg',route=>route.abort());await goto('screen=result')
  await page.locator('.finance__type-art').waitFor({state:'detached'})
  assert.equal(await page.locator('.finance__result-title').innerText(),'抢先上车鹅')
  await page.route('**/cover-sofa.svg',route=>route.abort());await goto()
  await page.locator('.finance__cover-placeholder').waitFor();await page.locator('.finance__cover-start').click()
  await page.locator('.finance__option').first().waitFor()
  await page.route('**/chart-sold-too-soon.svg',route=>route.abort());await goto('screen=Q01')
  await page.locator('.finance__chart-fallback').waitFor()
  assert.equal(await page.locator('.finance__option').count(),4)
  assert.deepEqual(errors,[])
  console.log('PASS: 真实12题/跳过/重测/连点/后台恢复，全部结果、无答案推导、320浅色/390深色、图片失败和截图')
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)})
