import fs from 'node:fs/promises'
import path from 'node:path'
import sharp from 'sharp'

const here = path.dirname(new URL(import.meta.url).pathname)
const repo = path.resolve(here, '../../../../../business-repo/uni-gknow')
const output = path.join(here, 'output')

const jobs = [
  ['src/static/illustrations/goose-magic-performer.png', 540, undefined, 'hero'],
  ['src/static/illustrations/goose-mind-card.png', 180, 195, 'card'],
  ['src/static/illustrations/goose-smoke-screen-card.png', 180, 195, 'card'],
  ['src/static/illustrations/goose-lights-out-card.png', 180, 195, 'card'],
  ['src/static/illustrations/goose-bti-mascot.png', 180, 195, 'card'],
  ['src/static/illustrations/wheel-goose.png', 180, 195, 'card'],
  ['src/static/illustrations/goose-lights-stage.png', 465, undefined, 'inside'],
  ['src/assets/goose-mirror-cover.jpg', 525, 525, 'cover'],
]

await fs.mkdir(output, { recursive: true })
const report = []

for (const [relative, width, height, mode] of jobs) {
  const input = path.join(repo, relative)
  const target = path.join(output, path.basename(relative))
  const source = sharp(input)
  const before = await source.metadata()
  let resized

  if (mode === 'card') {
    resized = source.resize(width, height, {
      fit: 'contain',
      position: 'centre',
      background: { r: 0, g: 0, b: 0, alpha: 0 },
      withoutEnlargement: true,
    }).png({ palette: true, quality: 50, effort: 10, dither: 0.5 })
  } else if (mode === 'cover') {
    resized = source.resize(width, height, { fit: 'inside', withoutEnlargement: true })
      .jpeg({ quality: 78, mozjpeg: true, progressive: true })
  } else if (mode === 'hero') {
    resized = source.resize(width, undefined, { fit: 'inside', withoutEnlargement: true })
      .png({ palette: true, quality: 40, effort: 10, dither: 0.5 })
  } else {
    resized = source.resize(width, undefined, { fit: 'inside', withoutEnlargement: true })
      .png({ palette: true, quality: 50, effort: 10, dither: 0.5 })
  }

  await resized.toFile(target)
  const after = await sharp(target).metadata()
  const [beforeStat, afterStat] = await Promise.all([fs.stat(input), fs.stat(target)])
  report.push({
    file: relative,
    before: { width: before.width, height: before.height, bytes: beforeStat.size },
    after: { width: after.width, height: after.height, bytes: afterStat.size },
    savedBytes: beforeStat.size - afterStat.size,
    alpha: Boolean(after.hasAlpha),
    output: path.relative(here, target),
  })
}

await fs.writeFile(path.join(here, 'report.json'), `${JSON.stringify(report, null, 2)}\n`)
console.log(JSON.stringify(report, null, 2))

const tileWidth = 340
const tileHeight = 250
const sheetWidth = tileWidth * 2
const sheetHeight = tileHeight * jobs.length
const tiles = []

for (let index = 0; index < jobs.length; index += 1) {
  const [relative] = jobs[index]
  const beforePath = path.join(repo, relative)
  const afterPath = path.join(output, path.basename(relative))
  const rowTop = index * tileHeight
  const beforeMeta = report[index].before
  const afterMeta = report[index].after
  const name = path.basename(relative)
  const overlay = (heading, dimensions, left) => Buffer.from(
    `<svg width="${tileWidth}" height="${tileHeight}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#f3f1ed"/><text x="16" y="22" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#29251f">${name}</text><text x="16" y="244" font-family="Arial,sans-serif" font-size="12" fill="#59534a">${heading} · ${dimensions.width}×${dimensions.height} · ${(dimensions.bytes / 1024).toFixed(1)} KB</text></svg>`,
  )
  const beforeImage = await sharp(beforePath).resize(300, 205, { fit: 'contain', background: '#f3f1ed' }).png().toBuffer()
  const afterImage = await sharp(afterPath).resize(300, 205, { fit: 'contain', background: '#f3f1ed' }).png().toBuffer()
  const beforeTile = await sharp(overlay('BEFORE', beforeMeta, 0)).composite([{ input: beforeImage, left: 20, top: 28 }]).png().toBuffer()
  const afterTile = await sharp(overlay('AFTER', afterMeta, 0)).composite([{ input: afterImage, left: 20, top: 28 }]).png().toBuffer()
  tiles.push({ input: beforeTile, left: 0, top: rowTop }, { input: afterTile, left: tileWidth, top: rowTop })
}

await sharp({ create: { width: sheetWidth, height: sheetHeight, channels: 3, background: '#ddd8d1' } })
  .composite(tiles)
  .png()
  .toFile(path.join(here, 'comparison.png'))
