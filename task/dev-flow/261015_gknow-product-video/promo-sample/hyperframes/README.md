# 鹅懂个啥转盘样片 · HyperFrames 对照工程

用 HyperFrames 的 HTML/CSS 与 GSAP 时间轴复现同一支 12 秒竖版转盘样片，方便比较编排效率、运动表现和修改体验。原 Python 工程与成片仍是独立基线。

## 内容与素材

- 沿用上级 [`DIRECTION.md`](../DIRECTION.md) 中的镜头、文案、演示候选和结果。
- 画面参考 `business-repo/uni-gknow` 的真实页面、颜色与鹅表情；小程序界面仍为还原展示层，不是端上录屏。
- 大鹅表情与已合成的音乐音效来自上级 `../` 样片工程，复制到 `assets/` 供本工程复现。

## 运行

要求 Node.js 22+、FFmpeg/FFprobe 和可启动的 Chrome。CLI 与 GSAP 版本已锁定；克隆工程后从本目录执行：

```sh
npm ci
npm run check
npm run dev
npx hyperframes snapshot --at 0.1,4.8,7.8,10.2 --no-end --output preview
npm run render
```

`npm run render` 输出 `output.mp4`。环境诊断可以从工作台根目录运行：

```sh
python3 .agents/vendor/product-video/scripts/check_environment.py \
  --project task/dev-flow/261015_gknow-product-video/promo-sample/hyperframes \
  --engine hyperframes --force
```

当前预览帧见 `preview/contact-sheet.jpg`；尚未输出 HyperFrames 成片，待用户审看预览后继续。

## 检查记录

- HyperFrames 0.8.185 检查通过：无错误；唯一提示是单镜头 HTML 中使用嵌套图层，复杂视觉按扁平 HTML 绘制，符合这个短片的结构，不需要拆成多个子组合。
- 已审看 0.1 秒开场、4.8 秒转动中、7.8 秒结果揭晓、10.2 秒结尾四帧；停点为「煲仔饭」。
- 完整时间线、节奏与声音尚待用户审片确认。
