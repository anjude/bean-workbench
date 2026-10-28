const fs = require('node:fs')
const path = require('node:path')
const assert = require('node:assert/strict')
const { createRequire } = require('node:module')
const root = path.resolve(__dirname, '../../../../..')
const project = path.join(root, 'business-repo/uni-gknow')
const appRequire = createRequire(path.join(project, 'package.json'))
const ts = appRequire('typescript')
function load(file, overrides = {}) {
  const mod = { exports: {} }
  const source = fs.readFileSync(path.join(project, file), 'utf8')
  const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText
  new Function('require', 'exports', 'module', js)(name => overrides[name] || appRequire(name), mod.exports, mod)
  return mod.exports
}
const catalog = load('src/data/projectCatalog.ts')
const atlasData = load('src/data/gooseAtlas.ts', { '@/data/projectCatalog': catalog })
const memory = new Map()
let failWrite = false
global.uni = { getStorageSync: key => memory.get(key), setStorageSync: (key, value) => { if (failWrite) throw new Error('storage full'); memory.set(key, value) } }
const atlas = load('src/composables/useGooseAtlas.ts', { '@/data/gooseAtlas': atlasData })
assert.equal(atlasData.gooseAtlasProjects.find(p => p.id === 'goose-grid').rule, 'highest-score')
assert.equal(atlas.useGooseAtlas().projects.value.find(p => p.id === 'goose-grid').record, null)
assert(atlas.recordGooseGameResult('goose-grid', 1))
assert(atlas.recordGooseGameResult('goose-grid', 3))
assert(atlas.recordGooseGameResult('goose-grid', 2))
let record = atlas.useGooseAtlas().projects.value.find(p => p.id === 'goose-grid').record
assert.equal(record.bestScore, 3)
assert.equal(record.plays, 3)
assert(atlas.recordGooseGameResult('goose-grid', 5))
record = atlas.useGooseAtlas().projects.value.find(p => p.id === 'goose-grid').record
assert.equal(record.bestScore, 5)
assert.equal(record.plays, 4)
failWrite = true
assert.equal(atlas.recordGooseGameResult('goose-grid', 4), false)
record = atlas.useGooseAtlas().projects.value.find(p => p.id === 'goose-grid').record
assert.equal(record.bestScore, 5)
assert.equal(record.plays, 4)
console.log('图鉴：首关解锁、最高关卡、重复关次、存储失败保护通过')
