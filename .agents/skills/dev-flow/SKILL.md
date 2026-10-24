---
name: dev-flow
description: 当用户提出新功能、缺陷修复、技术改造或业务仓开发任务时使用；统一推进任务建档、需求沟通、功能与系统设计、实现反馈循环、部署验收与交接，并按改动范围读取对应 reference。
metadata:
  short-description: 开发需求全流程入口
---

# 开发流程

这是 dev-flow 唯一的流程入口 skill。开发需求由本 skill 负责阶段推进，后端、前端、设计、验证细则按需从 references 读取；不要把实现阶段再次拆成多个入口 skill 组合触发。

## 流程

| 阶段 | 目标 | 主要产物 | 退出条件 |
| --- | --- | --- | --- |
| 00 任务初始化 | 绑定或建立任务上下文，创建基础文件并登记 | `task/dev-flow/YYMMDD_{主题}/README.md`、`handoff/`、`process/`、任务登记 | 任务范围与目录明确 |
| 01 需求理解与沟通 | 理清目标、约束、边界、受影响对象；与用户对齐真实需求 | 已确认的需求理解与范围 | 关键歧义已解决，用户认可理解 |
| 02 功能与系统设计 | 形成可执行的产品、数据、接口、系统和验收设计 | 任务 README 中的方案 | 设计、影响范围和验收标准满足门禁；默认等待用户确认 |
| 03 开发与迭代 | 按方案实现；运行针对性检查或预览，收集反馈并继续修改 | 代码、契约、过程记录 | 反馈收敛，目标和验收标准达成 |
| 04 部署、总结与交接 | 按授权推进分支或部署，核验结果，回填总结并写 handoff | 部署/验收结论、过程记录、最新 handoff | 结果可追溯，后续动作明确或任务关闭 |

按需求裁剪阶段；需求理解、方案和实现后的验收构成基本闭环。纯前端或纯后端任务只做命中的部分；缺陷修复先明确复现条件与验收结果，设计可以保持轻量。

## 入口路由

1. 读取工作台 `AGENTS.md`、`task/registry.md`，再按 `wb-router` 建立业务仓和任务上下文。检查最近任务，优先复用同一需求链条的目录；确属独立目标时才新建。用户明确要求建目录时直接执行。
2. 新建任务时参考 `wb-router/references/task-readme.md` 初始化 `README.md`、`handoff/`、`process/` 并更新登记。进入既有任务时先读 README 和最新 handoff。
3. 按当前阶段和改动范围选择资料。完整目录、阶段索引和路径变更约定见 [`references/README.md`](references/README.md)。仓库路径、技术栈、命令、分支或部署信息需要时调用 `dev-flow-tools-repo`。
4. 每阶段结束时按任务目录的 `process/` 记录结论，遵循 `wb-handoff/references/process-template.md` 的格式与边界；只有需要跨会话续接、中断交接、任务收口，或用户明确要求时，才写或更新 handoff 并调用 `wb-handoff`。

| 本次工作 | 按需读取 |
| --- | --- |
| 需求拆解、澄清、影响面定位 | [`references/00-plan/requirements.md`](references/00-plan/requirements.md) |
| 产品功能、数据模型、系统边界、接口和验收设计 | [`references/00-plan/design.md`](references/00-plan/design.md)，需要时叠加后端或前端细则 |
| 后端领域、数据库迁移、API、依赖注入、契约 | [`references/01-backend/development.md`](references/01-backend/development.md)；字段设计补读 [`references/01-backend/field-design-norms.md`](references/01-backend/field-design-norms.md) |
| 前端原型、状态矩阵、数据、页面和 Carbon 规范 | [`references/02-frontend/development.md`](references/02-frontend/development.md)；页面 UX 补读 [`references/02-frontend/ui-ux-handbook.md`](references/02-frontend/ui-ux-handbook.md)，Carbon 样式按需读同目录 CSS |
| 整体验收、方案回填、部署与交付 | [`references/03-delivery/verification-and-delivery.md`](references/03-delivery/verification-and-delivery.md)；仓库命令和部署调用 `dev-flow-tools-repo` |
| 数据库只读排查 / SVG 资产 / 软件产品视频 | 分别调用 `dev-flow-tools-db-query` / `dev-flow-tools-svg-assets` / `dev-flow-tools-product-video` |

## 需求和设计门禁

先用一句话复述需求和当前理解，再针对会改变行为、数据、权限、兼容性或验收结果的缺口向用户沟通。可由现有实现安全确定的细节，说明依据并继续，不逐项询问无关偏好。需求变化时更新任务 README 和改动范围。

默认采用方案确认模式：方案达到门禁后停下等用户确认，再进入实现。用户明确要求直接做、自动完成或本轮完整交付时，可按全流程执行；live 数据库写入、生产部署或公开发布仍需符合对应工具与工作台授权规则。

不得在关键需求未明、方案范围不清、验收不可判定时开始业务代码或数据库写入。设计深度按风险和改动范围调整；涉及数据、接口、权限、页面状态和多端契约时，写清影响与验证方式。

## 开发反馈循环

实现按依赖和改动范围推进，不要求每个功能都走完整后端/前端清单。每次有可评审结果时运行必要的针对性检查、预览或演示，再结合用户反馈修改：

`实现 → 检查/预览 → 用户反馈 → 修改 → 再检查`

反馈改变需求目标或系统边界时，回到阶段 01 或 02 更新理解和方案后再继续；只是实现细节或视觉调整时留在阶段 03。保持每轮改动聚焦，过程结论追加到同阶段记录。不要因加载某个细则就自动扩大任务范围或做无关重构。

## 部署与收口

部署前核对验收标准、目标环境、变更分支、数据库操作、回滚办法和用户授权。按 `dev-flow-tools-repo` 的实际命令执行；命令成功后核对目标环境或发布状态，不能把退出码当成部署验收。

最后将实际改动、验证结果、部署状态、未解决项和回滚信息回填任务 README，并按 `wb-handoff` 写可执行的下一步。未部署时明确记录阻塞和原因。任务完成后更新 `task/registry.md` 状态。

## 最终回复

简要报告需求理解、任务文档、改动范围、实际验证和部署状态；列出还需用户决定或外部条件阻塞的事项。路径和结论以实际文件与命令结果为准。
