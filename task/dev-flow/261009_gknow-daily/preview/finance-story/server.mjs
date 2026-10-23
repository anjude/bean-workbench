import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'
const here = path.dirname(fileURLToPath(import.meta.url))
const workspace = path.resolve(here, '../../../../..')
const project = path.join(workspace, 'business-repo/uni-gknow')
const require = createRequire(path.join(project, 'package.json'))
const { createServer } = require('vite')
const vue = require('@vitejs/plugin-vue')
const staticRoot = path.join(project, 'src/static')
const server = await createServer({
  configFile: false, root: here, publicDir: false,
  plugins: [{ name: 'story-preview-image-tag', enforce: 'pre', transform(code, id) {
    if (id.endsWith('/finance-personality/index.vue')) return code.replace(/<image\b/g, '<img').replace(/<\/image>/g, '</img>').replace("'@/composables/useFinanceStoryPresentation'", "'/fixtures.js'")
  } }, vue(), { name: 'story-local-assets', configureServer(vite) {
    vite.middlewares.use((req, res, next) => {
      if (!req.url?.startsWith('/static/')) return next()
      const name = decodeURIComponent(new URL(req.url, 'http://localhost').pathname).slice('/static/'.length)
      const target = path.resolve(staticRoot, name)
      if (!target.startsWith(staticRoot + path.sep) || !fs.existsSync(target)) return next()
      res.setHeader('Content-Type', target.endsWith('.svg') ? 'image/svg+xml' : target.endsWith('.jpg') ? 'image/jpeg' : 'image/png')
      fs.createReadStream(target).pipe(res)
    })
  } }],
  resolve: { alias: { '@': path.join(project, 'src'), vue: path.join(project, 'node_modules/vue/dist/vue.runtime.esm-bundler.js'), '@dcloudio/uni-app': path.join(here, 'uni-stub.js') } },
  server: { host: '127.0.0.1', port: 5198, strictPort: true, fs: { allow: [workspace] } },
})
await server.listen()
console.log('Story visual preview: http://127.0.0.1:5198')
