# Superone 前端模块设计 · 交接

- 任务目录：`task/dev-flow/261002_superone-modules/`
- 时间：2026-10-06 02:46（更新）
- 状态：进行中
- 上一份：无

## 这次到哪了

一句话：P5「扩展」入口占位已接入首页，系统与签到导航按钮也已实现，签到沿用 backup 的订阅流程。

## 已完成

- 首页 rail 将独立订阅、问答面板合并为扩展 —— `business-repo/uni-superone/src/pages/index/index.vue`
- 新增订阅与问答入口卡片，点击只提示暂未开放 —— `business-repo/uni-superone/src/components/business/biz-extension-panel.vue`
- 首页设置按钮改为 Carbon 风格「齿轮 + 系统」胶囊，并增加签到胶囊 —— `business-repo/uni-superone/src/pages/index/index.vue`、`business-repo/uni-superone/src/styles/06-pages/_p-index.scss`
- 新增签到授权、订阅 API 和当日缓存处理 —— `business-repo/uni-superone/src/composables/useDailyCheckin.ts`、`business-repo/uni-superone/src/utils/storage.ts`
- 更新方案和任务登记 —— `task/dev-flow/261002_superone-modules/README.md`、`task/registry.md`

## 过程记录

- 阶段 02：见 `process/02-前端开发.md`（完成扩展入口占位，以及系统与签到按钮；签到使用现有契约）。

## 未完成 / 下一步

1. 如需完整验证，运行前端类型检查和微信小程序构建并回填结果；本轮未运行验证命令。

## 关键决策与原因

- 订阅、问答收纳在一个扩展面板中：遵循已确认的第五模块定义；本期入口只提示暂未开放。
- 底部主按钮显示「敬请期待」：避免继续承诺创建订阅或提问功能。
- 签到授权必须确认模板状态为 `accept` 才记录当天状态：避免把仅成功弹出授权框误判为用户已授权。

## 卡点与待确认

- 无。

## 环境与坑

- `uni-superone` 当前工作区已有其他未提交改动；不要重置或覆盖其他文件。
- 微信小程序不支持 `<component :is>`，扩展面板已使用首页显式分支。

## 关联产物

| 产物 | 路径 |
| --- | --- |
| 方案文档 | `task/dev-flow/261002_superone-modules/README.md` |
| 改动 | 当前工作区 diff，未提交 |

## 下次建议调用的 skill

- `dev-flow-0301-verify-flow`：进入整体验证时检查 type-check 和微信小程序 build，并回填结果。
