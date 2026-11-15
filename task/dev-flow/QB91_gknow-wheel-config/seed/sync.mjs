import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const seedDir = path.dirname(fileURLToPath(import.meta.url))
const workspaceRoot = path.resolve(seedDir, '../../../..')
const baseURL = process.env.WHEEL_API_BASE_URL?.replace(/\/$/, '')
const tokenFile = process.env.WHEEL_ADMIN_TOKEN_FILE
  || path.join(workspaceRoot, '.agents/local-config/image-upload/admin.jwt')

if (!baseURL) throw new Error('WHEEL_API_BASE_URL is required')

const token = fs.readFileSync(tokenFile, 'utf8').trim()
if (!token || /\r|\n/.test(token)) throw new Error('admin token file is empty or invalid')

const seed = JSON.parse(fs.readFileSync(path.join(seedDir, 'first-batch.json'), 'utf8'))
if (!Array.isArray(seed.wheels) || seed.wheels.length === 0) throw new Error('seed contains no wheels')

async function request(method, pathname, body) {
  const response = await fetch(baseURL + pathname, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      ...(body ? { 'Content-Type': 'application/json' } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  })
  const payload = await response.json().catch(() => null)
  if (!response.ok || !payload || payload.err_code !== 0) {
    throw new Error(`${method} ${pathname} failed: HTTP ${response.status}, err_code ${payload?.err_code ?? 'invalid'}`)
  }
  return payload.data
}

const existing = await request('POST', '/api/so/gknow/wheel/list', {
  offset: 0,
  size: 100,
  include_unpublished: true,
})
const existingKeys = new Set((existing.list || []).map((item) => item.wheel_key))
const conflicts = seed.wheels.filter((wheel) => existingKeys.has(wheel.wheel_key))
if (conflicts.length) {
  throw new Error(`refuse to overwrite existing wheels: ${conflicts.map((wheel) => wheel.wheel_key).join(', ')}`)
}

for (const wheel of seed.wheels) {
  await request('POST', '/api/so/gknow/wheel/create', wheel)
  await request('POST', '/api/so/gknow/wheel/update', {
    wheel_key: wheel.wheel_key,
    expected_version: 1,
    wheel_status: 1,
  })
  const detail = await request('GET', `/api/so/gknow/wheel/detail?wheel_key=${encodeURIComponent(wheel.wheel_key)}`)
  if (detail.content_version !== 2 || detail.options.length !== wheel.options.length) {
    throw new Error(`verify failed for ${wheel.wheel_key}`)
  }
  console.log(`${wheel.wheel_key}: ${detail.options.length} options, version ${detail.content_version}`)
}

const published = await request('POST', '/api/so/gknow/wheel/list', { offset: 0, size: 100 })
const publishedKeys = new Set((published.list || []).map((item) => item.wheel_key))
for (const wheel of seed.wheels) {
  if (!publishedKeys.has(wheel.wheel_key)) throw new Error(`published list missing ${wheel.wheel_key}`)
}
console.log(`published ${seed.wheels.length} wheels and ${seed.wheels.reduce((sum, wheel) => sum + wheel.options.length, 0)} options`)
