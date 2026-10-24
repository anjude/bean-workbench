# HyperFrames 对照工程 · 过程记录

- 任务目录：`task/dev-flow/261015_gknow-product-video/`
- 阶段：03 HyperFrames 对照工程
- 时间：2026-10-22

## 做了什么

- 核对 HyperFrames 上游能力、CLI 0.8.185、Apache-2.0 许可与本机运行条件；新建隔离工程并锁定 HyperFrames 与 GSAP 版本：`promo-sample/hyperframes/package.json`、`package-lock.json`。
- 按现有方向和产品素材制作 HTML/GSAP 转盘对照画面，沿用演示候选、煲仔饭结果、鹅表情及既有合成音轨：`promo-sample/hyperframes/index.html`、`assets/`。
- 为视频工具补充 HyperFrames 路由，标明 HTML 展示层与需挂载 React 真实组件时的框架选择：`.agents/skills/dev-flow-tools-product-video/SKILL.md`。
- `check_environment.py --engine hyperframes --force` 报告 ready；HyperFrames check 无错误，留有一条单镜头嵌套结构提示。审看 0.1、4.8、7.8、10.2 秒预览帧，修正开场初始透明状态与转盘停点：`promo-sample/hyperframes/preview/contact-sheet.jpg`。
- 启动本地 HyperFrames 预览服务供用户审看：`http://localhost:3002/#project/hyperframes`。

## 得到的结论

- HyperFrames 可在现有 macOS 工作站正常检查与生成预览帧，已具备产品视频工具的可用入口：`.agents/skills/dev-flow-tools-product-video/SKILL.md`、`promo-sample/hyperframes/README.md`。
- 对此 12 秒吉祥物与 HTML 展示层短片，保留单一根组合和内部 HTML 图层即可；唯一 lint 提示是嵌套图层建议拆子组合，不影响检查通过：`promo-sample/hyperframes/preview/contact-sheet.jpg`。
- 新工程仅到 Studio 预览阶段；没有 HyperFrames MP4，也没有主观试听或端上实拍核对：`promo-sample/hyperframes/README.md`。

## 被推翻的判断

- 初始版本的扇区渐变起点和候选文字位置错开，转盘停点未能与「煲仔饭」结果匹配；关键帧检查后调整颜色角度、标签角度和最终旋转角：`promo-sample/hyperframes/index.html`。
- 开场标题在首帧被 GSAP 未来动画的初始值隐藏；加入 `immediateRender: false` 后 0.1 秒预览已显示完整开场：同上。

## 待核 / 没答上来

- 用户是否认可 HyperFrames 预览的视觉、节奏和声音；确认后才渲染完整 MP4。
- HyperFrames 导出文件是否与原 Python 成片在听感和整体表现上更合适：待用户审片。
