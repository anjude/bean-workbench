import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'
const here = path.dirname(fileURLToPath(import.meta.url))
const project = path.resolve(here, '../../../../../business-repo/uni-gknow')
const require = createRequire(path.join(project, 'package.json'))
const { createServer } = require('vite')
const vue = require('@vitejs/plugin-vue')
const redis = new Map()
const server = await createServer({
  configFile: false, root: here, publicDir: false,
  plugins: [{ name: 'mirror-preview', enforce: 'pre', transform(source, id) {
    if ((id.endsWith('/goose-mirror/index.vue') || id.endsWith('/collection/index.vue'))) return source.replace(/<image\b/g, '<img').replace(/<\/image>/g, '</img>')
  }, configureServer(vite) { vite.middlewares.use(async (req, res, next) => {
    if (req.url?.startsWith('/__redis')) {
      let body = ''; for await (const chunk of req) body += chunk
      const { op, key, value, ttl } = JSON.parse(body)
      const record = redis.get(key)
      if (record && record.expiresAt <= Date.now()) redis.delete(key)
      if (op === 'set') redis.set(key, { value, expiresAt: Date.now() + ttl * 1000 })
      if (op === 'del') redis.delete(key)
      res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify({ value: redis.get(key)?.value || '' })); return
    }
    if (req.url?.startsWith('/static/')) {
      const file = path.resolve(project, 'src', new URL(req.url, 'http://localhost').pathname.slice(1))
      if (file.startsWith(path.join(project, 'src/static/')) && fs.existsSync(file)) { res.setHeader('Content-Type', file.endsWith('.svg') ? 'image/svg+xml' : 'image/png'); fs.createReadStream(file).pipe(res); return }
    }
    next()
  }) } }, vue()],
  resolve: { alias: [
    { find: '@/stores/app', replacement: path.join(here, 'store.js') },
    { find: '@/contract', replacement: path.join(here, 'contract.js') },
    { find: '@dcloudio/uni-app', replacement: path.join(here, 'uni.js') },
    { find: '@', replacement: path.join(project, 'src') },
    { find: 'vue', replacement: path.join(project, 'node_modules/vue/dist/vue.runtime.esm-bundler.js') },
  ] },
  server: { host: '127.0.0.1', port: 5209, strictPort: true, fs: { allow: [path.resolve(project, '../..')] } },
})
await server.listen(); console.log('Mirror preview with simulated Redis: http://127.0.0.1:5209')
