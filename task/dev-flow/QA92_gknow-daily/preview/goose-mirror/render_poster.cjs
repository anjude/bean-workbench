const fs = require('node:fs'), path = require('node:path')
const { createCanvas, GlobalFonts } = require('@napi-rs/canvas')
GlobalFonts.registerFromPath('/System/Library/AssetsV2/com_apple_MobileAsset_Font8/86ba2c91f017a3749571a82f2c6d890ac7ffb2fb.asset/AssetData/PingFang.ttc', 'Poster Chinese')
const project = path.resolve(__dirname, '../../../../../business-repo/uni-gknow')
const ts = require(path.join(project, 'node_modules/typescript'))
function load(file) {
  const source = fs.readFileSync(path.join(project, 'src', file), 'utf8')
  const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText
  const mod = { exports: {} }; new Function('module', 'exports', js)(mod, mod.exports); return mod.exports
}
const { measureComparisonPoster, drawComparisonPoster } = load('utils/comparison-poster.ts')
const { getQuestions, mirrorAnswerText } = load('data/gooseMirror.ts')
function context(canvas) {
  const c = canvas.getContext('2d')
  return {
    setFillStyle(value) { c.fillStyle = value }, fillRect: (...args) => c.fillRect(...args), setTextAlign(value) { c.textAlign = value },
    setFontSize(size) { c.font = `${size}px "Poster Chinese", sans-serif` }, measureText: text => c.measureText(text), fillText: (...args) => c.fillText(...args),
    drawImage(_, x, y, w, h) { c.fillStyle = '#ebe6db'; c.fillRect(x, y, w, h); c.fillStyle = '#465a50'; c.font = '20px "Poster Chinese"'; c.fillText('示例码', x + 34, y + 70) },
    draw(_, done) { done() },
  }
}
;(async () => {
  const items = getQuestions(1).map((q, i) => ({ title: q.title, prompt: q.self, label: i === 2 ? '留着聊聊' : i === 1 ? '想到一起了' : '看到的不太一样', selfAnswer: mirrorAnswerText(i, i === 2 ? null : 0, false, 1), friendAnswer: mirrorAnswerText(i, i === 2 ? null : i === 1 ? 0 : 1, true, 1) }))
  const layout = measureComparisonPoster(context(createCanvas(630, 1)), items)
  const canvas = createCanvas(630, layout.height)
  await drawComparisonPoster(context(canvas), layout, '有 1 题，你们想到一起了', '朋友小林眼中的我', 'sample')
  const output = path.join(__dirname, 'ui/comparison-poster-sample.png')
  fs.writeFileSync(output, canvas.toBuffer('image/png')); console.log(`已生成海报样片：${output}（二维码为示意）`)
})().catch(error => { console.error(error); process.exitCode = 1 })
