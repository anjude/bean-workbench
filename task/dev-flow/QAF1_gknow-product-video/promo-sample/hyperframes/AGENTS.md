# HyperFrames 样片工程

这是「鹅懂个啥·今天吃什么」的 HyperFrames 对照工程。用 HTML/CSS 与 GSAP 编排画面，HyperFrames 按帧渲染；原 Python 工程与成片保持独立。

## 常用命令

```sh
npm ci
npm run dev
npm run check
npx hyperframes snapshot --at 0,4,8,10 --output preview
npm run render
```

## 修改约定

- 对照上级 `DIRECTION.md` 与产品源码，画面仍是按源码还原的展示层，不是小程序录屏。
- 动效必须可按时间 seek；不使用时钟、随机数或运行时网络请求。
- 每个时间元素要有 `id`、`class="clip"`、`data-start` 和 `data-duration`；时间线注册在 `window.__timelines.main`。
- 修改 HTML 后运行 `npm run check`，修正错误并审看关键帧；成片输出用 `npm run render`。
- 不提交 `node_modules/`、`.hyperframes/` 或本机缓存。安装包版本以 `package.json` 与 lockfile 为准。

## 来源与素材

- HyperFrames CLI：Apache-2.0，版本固定在 `package.json`。
- GSAP：标准商业许可；本工程只用其动画运行库。
- 大鹅表情与音乐复用上级工程素材；来源见上级 `README.md` 与 `DIRECTION.md`。
