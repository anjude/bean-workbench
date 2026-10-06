# 开发任务列表（dev-flow）

本目录汇总当前走 dev-flow 流水线（`dev-flow-0000-plan-flow` → `0101/0102/0103/0104` 后端 → `0201~0205` 前端 → `0301` 验证）的开发任务。

完整任务登记与热/冷任务索引在 `task/registry.md`，本表只收「开发类、进行中」的任务，便于快速路由到最近上下文。

## 进行中

| 任务 | 目录 | 资源范围 | 状态 |
| --- | --- | --- | --- |
| Superone 后端重构（下线老功能） | `task/dev-flow/260927_superone-backend-refactor/` | `business-repo/backend-superone`、`release-260927` tag | 进行中 |
| Superone 多仓规则完善 | `task/dev-flow/260614_superone-workbench-migration/` | `business-repo/` 路由、Superone skills、协议仓路径、知识库索引 | 进行中 |
| uni-carbon-space 接入 | `task/dev-flow/260614_uni-carbon-space-onboarding/` | `business-repo/uni-carbon-space`、uni 路由、品牌特化 skill、知识库索引 | 进行中 |
| Superone 前端模块设计（topic/checklist/plan 等） | `task/dev-flow/261002_superone-modules/` | `business-repo/uni-superone`、`business-repo/frontend-contracts` | 进行中 |
| Topic 记录嵌套（log 的 log，parent_log_id） | `task/dev-flow/261002_topic-log-nesting/` | `business-repo/backend-superone`、`business-repo/frontend-contracts` | 已完成 |
| uTools Superone 重构 | `task/dev-flow/261007_utools-refactor/` | 一级辅助文件精简；`src/` 无用文件清理与契约类型收敛 | 清理与门禁完成，子仓已推送 |
| 前端引入子日志（跟进，记录详情页） | `task/dev-flow/261002_superone-sub-log/` | `business-repo/uni-superone`、`business-repo/frontend-contracts` | 进行中 |
| topic 模块 P0 闭环（增删改 + 级联删除） | `task/dev-flow/261003_topic-crud/` | `business-repo/backend-superone`、`business-repo/uni-superone` | 进行中 |

## 约定

- 新开发需求先走 `dev-flow-0000-plan-flow` 出方案，方案落 `task/dev-flow/YYMMDD_{主题}/README.md`。
- 确认后再按端派发后端（`dev-flow-0101` 起）或前端（`dev-flow-0201` 起），收口走 `dev-flow-0301-verify-flow`。
- 本目录不放方案文档本身，只做索引；方案与过程记录写在各 `task/dev-flow/YYMMDD_{主题}/` 下。
