const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const { createRequire } = require('node:module')
const project = path.resolve(__dirname, '../../../../../business-repo/uni-gknow')
const appRequire = createRequire(path.join(project, 'package.json'))
const ts = appRequire('typescript')
const redis = new Map()
let failDelete = false
let failRead = false
const expirations = []
function client(id) {
  const storage = new Map(); const modules = new Map()
  const faults = { save: false, index: false }
  const store = { ready: true, userInfo: { openid: id, nickName: id } }
  const uni = {
    getStorageSync: k => storage.has(k) ? structuredClone(storage.get(k)) : '',
    setStorageSync: (k, v) => { if (faults.save && k === 'gk.goose-atlas.v1') throw Error('disk full'); storage.set(k, structuredClone(v)) },
    removeStorageSync: k => storage.delete(k), showModal: async () => ({ confirm: true }),
  }
  const commonApi = {
    getFeRedis: async ({ redisKey }) => { if (failRead) throw Error('offline'); return { errCode: 0, data: { redisValue: redis.get(redisKey) || '' } } },
    setFeRedis: async ({ redisKey, redisValue, expireSeconds }) => { assert(expireSeconds > 0 && expireSeconds <= 604800); if (faults.index && JSON.parse(redisValue).respondents?.length) throw Error('index offline'); expirations.push(expireSeconds); redis.set(redisKey, redisValue); return { errCode: 0 } },
    delFeRedis: async ({ redisKey }) => { if (failDelete) throw Error('offline'); redis.delete(redisKey); return { errCode: 0 } },
  }
  function load(name) {
    if (name.endsWith('.jpg')) return { default: '/mock-cover.jpg' }
    if (name === '@/stores/app') return { useAppStore: () => store }
    if (name === '@/contract') return { commonApi }
    if (!name.startsWith('@/')) return appRequire(name)
    const file = path.join(project, 'src', name.slice(2) + '.ts')
    if (modules.has(file)) return modules.get(file).exports
    const mod = { exports: {} }; modules.set(file, mod)
    let source = fs.readFileSync(file, 'utf8')
    if (file.endsWith('/data/gooseMirror.ts')) source = source.replace('{ 1: questionsV1 }', "{ 1: questionsV1, 2: questionsV1.map((q, i) => i === 0 ? { ...q, title: '测试题库二', options: ['新版选项', ...q.options.slice(1)] } : q) }")
    const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText
    new Function('require', 'module', 'exports', 'uni', js)(load, mod, mod.exports, uni)
    return mod.exports
  }
  const api = load('@/composables/useGooseMirror')
  return { storage, faults, load, quiz: () => api.useGooseMirror() }
}
async function fill(q, offset = 0) { for (let i = 0; i < 6; i++) { q.choose((i + offset) % 4); if (i < 5) q.next() } }
async function invite(a) {
  const q = a.quiz(); await q.refresh(); await q.start(); await fill(q); await q.submit()
  assert.equal(q.phase.value, 'waiting'); const url = new URL('https://example.test' + q.sharePath.value)
  return { q, key: url.searchParams.get('key'), taskId: q.task.value.taskId }
}
async function respond(client, invitation, offset = 0) {
  const q = client.quiz(); q.open(invitation.key, invitation.taskId); await q.refresh(); await q.start(); await fill(q, offset); return q
}
;(async () => {
  const a = client('A'); const b = client('B'); const c = client('C')
  const first = await invite(a)
  const qb = await respond(b, first); const qc = await respond(c, first, 1)
  await qb.submit(); await qc.submit()
  assert.equal(qb.phase.value, 'result'); assert.equal(qb.summary.value.same, 6)
  assert.equal(qc.phase.value, 'result'); assert.equal(qc.summary.value.same, 0)
  assert.deepEqual([...redis.keys()], [first.key])
  assert.deepEqual(JSON.parse(redis.get(first.key)).responses.map(r => r.respondentId), ['B', 'C'])
  assert(!b.storage.has('gk.goose-atlas.v1'))
  await qb.refresh(); assert.equal(qb.phase.value, 'result')
  await first.q.refresh(); assert.equal(first.q.participantCount.value, 2); assert.equal(first.q.records.value.length, 2)
  await first.q.refresh(); assert.equal(first.q.records.value.length, 2)
  first.q.openRecords(); while (first.q.busy.value) await new Promise(resolve => setImmediate(resolve))
  first.q.viewRecord(first.q.records.value[0]); assert.equal(first.q.task.value.friendAnswers.length, 6)
  console.log('PASS A单key保存B/C快照；B只看匹配数；图鉴领取两人且重复同步去重')
  const again = await respond(b, first, 2); await again.submit(); await first.q.refresh()
  assert.equal(first.q.participantCount.value, 2); assert.equal(first.q.records.value.length, 2)
  assert.deepEqual(first.q.records.value.find(r => r.respondentId === 'B').friendAnswers, [2,3,0,1,2,3])
  const inProgress = await respond(c, first, 3)
  const secondQuiz = a.quiz(); await secondQuiz.refresh(); await secondQuiz.start(); await fill(secondQuiz, 1); await secondQuiz.submit()
  const second = { q: secondQuiz, key: first.key, taskId: secondQuiz.task.value.taskId }
  await inProgress.submit(); assert.equal(inProgress.phase.value, 'result')
  assert.deepEqual(inProgress.task.value.selfAnswers, [1,2,3,0,1,2])
  const old = c.quiz(); old.open(first.key, first.taskId); await old.refresh(); assert.equal(old.phase.value, 'intro')
  await old.start(); await fill(old, 1); await old.submit(); assert.equal(old.phase.value, 'result')
  assert.deepEqual(old.task.value.selfAnswers, JSON.parse(redis.get(first.key)).selfAnswers)
  const b2 = await respond(b, second, 3); await b2.submit()
  a.faults.save = true; await second.q.refresh(); assert(second.q.warning.value); assert(redis.has(first.key))
  a.faults.save = false; await second.q.refresh()
  assert.equal(second.q.participantCount.value, 2); assert.equal(second.q.records.value.length, 4)
  assert.equal(JSON.parse(redis.get(first.key)).responses.length, 4)
  assert.deepEqual(second.q.records.value.find(r => r.taskId === first.taskId && r.respondentId === 'B').selfAnswers, [0,1,2,3,0,1])
  console.log('PASS 重复填写更新、历史快照、旧邀请仍可填写、本机保存失败重试')
  const third = await invite(a); const c3 = await respond(c, third)
  failRead = true; await c3.submit(); assert.equal(c3.phase.value, 'question')
  failRead = false; const resumed = c.quiz(); resumed.open(third.key, third.taskId); await resumed.refresh(); await resumed.start()
  assert.deepEqual(resumed.answers.value, c3.answers.value)
  const short = JSON.parse(redis.get(third.key)); short.expiresAt = Date.now() + 8000; redis.set(third.key, JSON.stringify(short))
  await resumed.submit(); assert(expirations.at(-1) <= 8); await third.q.refresh()
  assert.equal(third.q.records.value.length, 5)
  // 新答卷尚未同步时，先归档再删除；失败不能丢远端。
  const fresh = await respond(b, third, 2); await fresh.submit()
  a.faults.save = true; await third.q.resetOwn(); assert(redis.has(third.key)); assert(third.q.error.value)
  a.faults.save = false; failDelete = true; await third.q.resetOwn(); assert(redis.has(third.key)); assert(third.q.error.value)
  failDelete = false; await third.q.resetOwn(); assert(!redis.has(third.key)); assert.equal(third.q.phase.value, 'intro')
  assert.equal(third.q.records.value.length, 6)
  assert.equal(a.load('@/utils/local-tasks').getLocalTasks('A').filter(t => t.redisKey === third.key).length, 0)
  const expired = c.quiz(); expired.open(third.key); await expired.refresh(); assert.equal(expired.phase.value, 'expired')
  console.log('PASS 重置前归档、保存/删除失败保留远端、删除成功保留图鉴并令旧邀请失效')
  const reopened = a.quiz(); await reopened.refresh(); assert.equal(reopened.records.value.length, 6)
  const data = a.load('@/data/gooseMirror')
  assert.equal(first.q.task.value.questionVersion, 1)
  assert.equal(qb.task.value.questionVersion, 1)
  const legacy = { ...first.q.task.value }; delete legacy.questionVersion
  assert(data.isMirrorTask(legacy)); assert.equal(data.questionVersionOf(legacy), 1)
  const versionOwner = client('versionOwner'); const versionFriend = client('versionFriend')
  const versionInvite = await invite(versionOwner)
  const firstResponse = await respond(versionFriend, versionInvite); await firstResponse.submit()
  const pending = await respond(versionFriend, versionInvite)
  const changed = JSON.parse(redis.get(versionInvite.key)); changed.questionVersion = 2; changed.taskId = 'second-question-bank'
  redis.set(versionInvite.key, JSON.stringify(changed))
  await pending.submit(); assert.equal(pending.phase.value, 'intro'); assert.match(pending.warning.value, /题目/)
  assert.equal(JSON.parse(redis.get(versionInvite.key)).responses.length, 1)
  await pending.start(); assert.equal(pending.question.value.title, '测试题库二')
  await fill(pending); await pending.submit(); assert.equal(pending.task.value.questionVersion, 2)
  await versionInvite.q.refresh(); assert.deepEqual(versionInvite.q.records.value.map(r => r.questionVersion).sort(), [1, 2])
  assert.equal(data.mirrorAnswerText(0, 0, false, 2), '新版选项')
  assert.notEqual(data.mirrorAnswerText(0, 0, false, 1), data.mirrorAnswerText(0, 0, false, 2))
  const unknown = { ...changed, questionVersion: 999 }; redis.set(versionInvite.key, JSON.stringify(unknown))
  const unsupported = versionOwner.quiz(); await unsupported.refresh(); assert(unsupported.error.value); assert(redis.has(versionInvite.key))
  const bad = client('broken'); redis.set('broken:goose-mirror', '{bad json'); await bad.quiz().refresh(); assert(redis.has('broken:goose-mirror'))
  console.log('PASS 题目版本标记、缺字段归类、跨版本重新作答、历史题库与未知版本保留')
  console.log('PASS 断网保留草稿、七天剩余期限、过期后本机历史')
})().catch(e => { console.error(e); process.exitCode = 1 })
