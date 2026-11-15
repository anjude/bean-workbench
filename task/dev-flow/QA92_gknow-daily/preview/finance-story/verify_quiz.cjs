const fs = require('node:fs')
const path = require('node:path')
const vm = require('node:vm')
const assert = require('node:assert/strict')
const { createRequire } = require('node:module')
const project = path.resolve(__dirname, '../../../../../business-repo/uni-gknow')
const projectRequire = createRequire(path.join(project, 'package.json'))
const ts = projectRequire('typescript'); const cache = new Map()
function load(name) {
  if (!name.startsWith('@/')) return projectRequire(name)
  const file = path.join(project, 'src', name.slice(2)) + '.ts'
  if (cache.has(file)) return cache.get(file).exports
  const module = { exports: {} }; cache.set(file, module)
  const code = ts.transpileModule(fs.readFileSync(file, 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText
  vm.runInThisContext(`(function(require,module,exports){${code}\n})`, { filename: file })(load, module, module.exports)
  return module.exports
}
const data = load('@/data/financePersonalityStory')
const engine = load('@/utils/finance-personality')
const { useFinancePersonalityStory } = load('@/composables/useFinancePersonalityStory')
assert.equal(data.financeItems.length, 31)
assert.equal(data.financeExperience.options.length, 3)
for (const item of data.financeItems) assert.equal(item.options.length, 4)
const idSet = new Set(data.financeItems.map(item => item.id)); assert.equal(idSet.size, 31)
let runs = 0
for (const [routeIndex, route] of ['daily', 'fund', 'stock'].entries()) {
  assert.equal(data.financeRoutes[route].length, 12)
  assert.equal(new Set(data.financeRoutes[route]).size, 12)
  if (route === 'daily') assert(data.financeRoutes[route].every(id => id.startsWith('N')))
  for (const mode of ['A', 'B', 'C', 'D', 'skip', 'replace']) {
    const quiz = useFinancePersonalityStory(); quiz.start(77)
    assert.equal(quiz.item.value.id, 'EXPERIENCE'); assert.equal(quiz.progress.value, 1)
    assert.equal(quiz.record(null), false)
    quiz.record(data.financeExperience.options[routeIndex].id); quiz.advance()
    for (let slot = 1; slot <= 12; slot++) {
      assert.equal(quiz.progress.value, slot + 1)
      assert.equal(quiz.item.value.id, data.financeRoutes[route][slot - 1])
      if (mode === 'replace') {
        const before = quiz.item.value.id
        const swapped = quiz.replace()
        assert.equal(swapped, !before.startsWith('N'))
        assert.equal(quiz.item.value.id, engine.dailyReplacement(slot))
        assert.equal(quiz.replace(), false)
      }
      const option = mode === 'skip' ? null : quiz.item.value.options[Math.max(0, 'ABCD'.indexOf(mode))].id
      assert.equal(quiz.record(option), true)
      assert.equal(quiz.record(option), false)
      quiz.advance()
    }
    assert.equal(quiz.phase.value, 'result')
    assert.equal(quiz.answers.value.length, 13)
    assert.equal(quiz.result.value.transcript.length, 12)
    assert(quiz.result.value.transcript.every(row => row.kind === 'main'))
    assert.equal(quiz.result.value.answeredCount, mode === 'skip' ? 0 : 12)
    if (mode === 'skip') assert.equal(quiz.result.value.cards.length, 0)
    quiz.replay(); assert.equal(quiz.answers.value.length, 0); assert.equal(quiz.experience.value, null)
    assert.equal(quiz.item.value.id, 'EXPERIENCE')
    runs++
  }
}
// 同样的实际场景答案，不因经验项不同而变标签或分数。
const sceneAnswers = data.financeRoutes.daily.map((id, index) => ({ slot: index + 1, itemId: id, optionId: engine.getFinanceItem(id).options[0].id, kind: 'main', answerKind: 'choice', exposedItemIds: [id] }))
for (const gate of data.financeExperience.options) {
  const result = engine.evaluateFinance([{ slot: 0, itemId: 'EXPERIENCE', optionId: gate.id, kind: 'experience', answerKind: 'choice', exposedItemIds: ['EXPERIENCE'] }, ...sceneAnswers])
  assert.equal(result.title, engine.evaluateFinance(sceneAnswers).title)
  assert.deepEqual(result.ranked.map(row => [row.signal, row.count, row.strength]), engine.evaluateFinance(sceneAnswers).ranked.map(row => [row.signal, row.count, row.strength]))
}
const navigation = load('@/utils/adapt/navigation')
for (const status of [20, 24, 44, 59]) {
  global.uni = { getWindowInfo: () => ({ statusBarHeight: status, windowWidth: 390 }), getMenuButtonBoundingClientRect: () => ({ top: status + 6, height: 32, left: 294 }) }
  assert.equal(navigation.readNavigationGeometry().height, status + 44)
}
delete global.uni
assert.equal(navigation.readNavigationGeometry().height, 64)
console.log(JSON.stringify({ uniqueScenes: 31, experienceQuestions: 1, routeRuns: runs, passed: ['三路线严格13题', '经验不计人格', '日常无基金股票题', '专业题原位换日常', '跳过不加题', '重复点击', '重玩清空经验', '导航几何'] }, null, 2))
