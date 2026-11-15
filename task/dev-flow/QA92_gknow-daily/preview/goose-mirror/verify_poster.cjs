const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const project = path.resolve(__dirname, '../../../../../business-repo/uni-gknow')
const ts = require(path.join(project, 'node_modules/typescript'))
function load(file) {
  const source = fs.readFileSync(path.join(project, 'src', file), 'utf8')
  const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText
  const mod = { exports: {} }; new Function('module', 'exports', js)(mod, mod.exports); return mod.exports
}
const { measureComparisonPoster, drawComparisonPoster } = load('utils/comparison-poster.ts')
const { getQuestions, mirrorAnswerText } = load('data/gooseMirror.ts')
async function verify() {
  let font = 24; const text = []; const images = []
  const ctx = {
    setFillStyle() {}, fillRect() {}, setTextAlign() {}, setFontSize(value) { font = value },
    measureText(value) { return { width: [...value].length * font * 0.8 } },
    fillText(value, x, y) { text.push({ value, x, y, font }) }, drawImage(...args) { images.push(args) }, draw(_, done) { done() },
  }
  const questions = getQuestions(1)
  const comparisons = questions.map((q, i) => ({ title: q.title, prompt: q.self, label: i === 2 ? '留着聊聊' : '看到的不太一样', selfAnswer: mirrorAnswerText(i, i === 2 ? null : 0, false, 1), friendAnswer: mirrorAnswerText(i, i === 2 ? null : 1, true, 1) }))
  // 长答案用于验证自动换行不会截断或压住底部二维码。
  comparisons[5].friendAnswer += '这个情况我还想多聊几句，看看我们为什么理解得不一样。'
  const layout = measureComparisonPoster(ctx, comparisons)
  assert.equal(layout.cards.length, 6)
  for (let i = 0; i < comparisons.length; i++) {
    const card = layout.cards[i], input = comparisons[i]
    assert.equal(card.prompt.join(''), input.prompt); assert.equal(card.self.join(''), input.selfAnswer); assert.equal(card.friend.join(''), input.friendAnswer)
    assert.equal(card.title.join(''), `${i + 1} · ${input.title}`)
  }
  await drawComparisonPoster(ctx, layout, '有 1 题，你们想到一起了', '朋友小林眼中的我', 'qr')
  assert.equal(text.filter(x => x.value === '我选的').length, 6)
  assert.equal(text.filter(x => x.value === '朋友选的').length, 6)
  assert(text.some(x => x.value === '这题先跳过')); assert(text.some(x => x.value === '这个真没见过'))
  const qr = images.find(image => image[0] === 'qr'); assert(qr); assert(qr[2] + qr[4] <= layout.height)
  assert(text.every(item => item.y > 0 && item.y < layout.height))
  assert(text.filter(x => x.value === '看到的不太一样').length === 5)
  console.log(`PASS 六题的题目、双方完整答案和跳过状态；长文本换行、偏差提示、二维码均在画布内（630 × ${layout.height}）`)
}
verify().catch(error => { console.error(error); process.exitCode = 1 })
