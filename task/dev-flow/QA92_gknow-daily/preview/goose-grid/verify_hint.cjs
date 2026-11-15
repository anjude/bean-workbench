const fs = require('node:fs')
const path = require('node:path')
const assert = require('node:assert/strict')
const { createRequire } = require('node:module')
const root = path.resolve(__dirname, '../../../../..')
const project = path.join(root, 'business-repo/uni-gknow')
const appRequire = createRequire(path.join(project, 'package.json'))
const ts = appRequire('typescript')
function load(relativePath, resolve = appRequire) {
  const module = { exports: {} }
  const source = fs.readFileSync(path.join(project, relativePath), 'utf8')
  const code = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText
  new Function('require', 'exports', 'module', code)(resolve, module.exports, module)
  return module.exports
}
const { gooseGridLevels } = load('src/data/gooseGridLevels.ts')
const { deriveGooseHint } = load('src/utils/goose-grid-hint.ts')
let checked = 0
for (const [levelIndex, level] of gooseGridLevels.entries()) {
  const n = level.solution.length
  for (let mask = 0; mask < (1 << n) - 1; mask++) {
    const state = Array(n * n).fill('empty')
    for (let row = 0; row < n; row++) if (mask & (1 << row)) state[row * n + level.solution[row]] = 'goose'
    for (let miss = -1; miss < n * n; miss++) {
      if (miss >= 0 && level.solution[Math.floor(miss / n)] === miss % n) continue
      const board = state.slice()
      if (miss >= 0) board[miss] = 'miss'
      const hint = deriveGooseHint(level.regions, board)
      assert(hint, `第 ${levelIndex + 1} 关 mask=${mask} miss=${miss} 无法推导`)
      assert.equal(level.solution[Math.floor(hint.index / n)], hint.index % n)
      assert(hint.steps.length)
      assert(!hint.steps.some(step => step.includes('已排除') && !step.includes('之前找错')), '存在缺少原因的排除')
      checked++
    }
    const marked = state.map(cell => cell === 'empty' ? 'mark' : cell)
    const hint = deriveGooseHint(level.regions, marked)
    assert(hint && level.solution[Math.floor(hint.index / n)] === hint.index % n, '普通误标不应阻止提示')
  }
}
const first = Array(16).fill('empty')
first[11] = 'goose'
const second = deriveGooseHint(gooseGridLevels[0].regions, first)
assert.equal(second.index, 2)
assert(second.steps.join('').includes('第2行第3列') && second.steps.join('').includes('相邻'))
console.log(`已检查 ${checked} 种已确认位置和一次失误组合，以及普通误标场景；第一关第二只鹅解释正确。`)
