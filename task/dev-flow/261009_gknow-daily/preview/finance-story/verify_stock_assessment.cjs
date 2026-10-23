const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const os = require('node:os')
const project = path.resolve(__dirname, '../../../../../business-repo/uni-gknow')
const { buildSync } = require(path.join(project, 'node_modules/esbuild'))
const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'finance-assessment-'))
const outfile = path.join(temp, 'assessment.cjs')
buildSync({ stdin: { contents: `export * from './src/utils/finance-stock-assessment'; export * from './src/data/financeStockAssessment'`, resolveDir: project, loader: 'ts' }, bundle: true, platform: 'node', format: 'cjs', outfile, alias: { '@': path.join(project,'src') } })
const { evaluateStockAssessment: evaluate, stockQuestions: questions } = require(outfile)
const approvedSamples = [
 ['昨天刚卖掉一只股票，小赚了一笔\n今天它又涨了8%，你还是看好，但买回来就贵了','你会怎么做？',['买回来，后面的钱还得赚','等跌回来，现在这价下不去手','先买回一点，别又全错过了','不买了，赚过这笔就找下一只']],
 ['买这只股票，是因为看好它的一项新业务\n现在公司公告：这项业务不做了\n股价已经跌了15%，你还拿着','接下来怎么做？',['卖掉，当初买它的理由已经没了','等反弹一点再卖，现在割太疼','先卖一半，剩下的再看看','再找找它还有什么值得拿的，别急着卖']],
 ['一直买宽基基金的你，今年小赚\n做短线的朋友，一个月就赚过了你一年\n他把最近在买的几只股票发了过来','你会怎么做？',['跟一只试试，光看别人赚也没用','拿点闲钱跟，原来的基金不动','先问清他怎么买卖，不能只看赚了多少','继续买自己的，他这钱我未必赚得来']],
 ['买入前你给自己定了规矩：亏10%就卖\n现在已经跌了12%，公司也没出什么新消息\n你盯着卖出键，有点下不去手','这笔怎么处理？',['卖，说好亏到这就走','再等等，别刚卖就反弹','补一点，涨回来一点就能回本','重新看看还值不值得拿，不能只盯着亏了多少']],
]
const answers = choices => [...choices].map((choice, i) => ({ itemId: questions[i].id, optionId: 'ABCD'.includes(choice) ? `${questions[i].id}-${choice}` : null }))
assert.equal(questions.length, 12)
for (const [i,q] of questions.entries()) {
 assert.equal(q.options.length, 4)
 for(const o of q.options) assert(!/[。.!！]$/.test(o.text))
 if (i<4) { const [setup,prompt,options]=approvedSamples[i]; assert.equal(q.setup,setup); assert.equal(q.prompt,prompt); assert.deepEqual(q.options.map(o=>o.text),options) }
}
const cases = {M:'ACACACAABDAC',H:'CCBCCCBBDBBC',P:'ACDABCCAACCB',E:'BDCDDBDCCCCB',L:'BBBBBDBABACC',S:'ADDDDDADCBBA',C:'DDDABADBCADD'}
for (const [id, seq] of Object.entries(cases)) {
 const result=evaluate(answers(seq)); assert.equal(result.kind,'single',id); assert.equal(result.cards[0].id,id)
 assert(result.description.length>30); assert(result.caution)
 for (const asset of [result.image,result.posterImage,result.shareImage]) assert(fs.existsSync(path.join(project,'src',asset)))
}
assert.equal(evaluate(answers('CBABABCABADC')).kind,'mixed')
assert.equal(evaluate(answers('BDBDBCAADCDD')).kind,'scattered')
assert.equal(evaluate(answers('------------')).kind,'empty')
// 同类情境两次支持仍不足以成型（Q01、Q05都是机会）。
assert.equal(evaluate(answers('A---A-------')).kind,'scattered')
// 一个普通支持加半个弱支持不能满足“两普通支持”。
assert.equal(evaluate(answers('-D-------C--')).kind,'scattered')
const sparse=evaluate(answers('A------A----'))
assert.equal(sparse.cards[0].id,'M')
const score=sparse.ranked.find(r=>r.id==='M');assert.equal(score.n,2);assert.equal(score.b,.5);assert.equal(score.r,.375)
const weak=evaluate(answers('-D----------')).ranked.find(r=>r.id==='E')
assert.equal(weak.s,.5);assert.equal(weak.b,.375);assert.equal(weak.ordinary.length,0)
// 重复题、错误选项、未知题不能增加回答数量。
assert.equal(evaluate([...answers('ACACACAABDAC'), ...answers('ACACACAABDAC'), {itemId:'bad',optionId:'A'}]).answeredCount,12)
assert.equal(evaluate([{itemId:'Q01',optionId:'Q02-A'}]).answeredCount,0)
console.log('PASS: 12题/前四题逐字、七型、双型、分散、全跳过、弱支持、跨情境门槛、曝光分母、重复/非法记录')
