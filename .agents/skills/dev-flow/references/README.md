# dev-flow 参考资料索引

本目录存放开发流程的阶段细则、技术规范和执行清单。`SKILL.md` 是唯一流程入口；先按当前任务阶段和改动范围从本索引选读，避免一次加载整套资料。

## 按阶段查找

| 阶段 | 主题 | 入口文件 | 需要时继续读取 |
| --- | --- | --- | --- |
| 00 任务初始化与需求沟通 | 需求梳理、影响面定位、与用户澄清 | [`00-plan/requirements.md`](00-plan/requirements.md) | [`../SKILL.md`](../SKILL.md) 的任务初始化规则 |
| 02 功能与系统设计 | 产品、数据、系统边界、接口和验收设计 | [`00-plan/design.md`](00-plan/design.md) | 后端或前端对应章节 |
| 03 后端开发 | 领域、数据库、API、依赖注入、契约 | [`01-backend/development.md`](01-backend/development.md) | [`01-backend/field-design-norms.md`](01-backend/field-design-norms.md) |
| 03 前端开发 | 原型、状态矩阵、数据、页面、Carbon 规范 | [`02-frontend/development.md`](02-frontend/development.md) | [`02-frontend/ui-ux-handbook.md`](02-frontend/ui-ux-handbook.md)、CSS 参考 |
| 03 开发验证与交付 | 整体验收、方案回填、部署与交接 | [`03-delivery/verification-and-delivery.md`](03-delivery/verification-and-delivery.md) | 仓库命令和分支信息见 `dev-flow-tools-repo` |

SVG 图标和空状态资产走 `dev-flow-tools-svg-assets`；数据库只读排查走 `dev-flow-tools-db-query`；产品视频制作走 `dev-flow-tools-product-video`。仓库路径、命令、分支与部署信息走 `dev-flow-tools-repo`。

## 目录约定

- `00-plan/`：任务初始化、需求沟通和方案设计。
- `01-backend/`：后端开发细则。
- `02-frontend/`：前端开发细则及其 UX、品牌和样式材料。
- `03-delivery/`：整体验证、部署与交付。
- 文件名表达具体能力；同一阶段的连续约束优先放在同一份文档中，只有独立按需加载的规范才单独成文。
- 新增文件后同步本索引、`dev-flow/SKILL.md` 的路由表及 `script/check-workbench.py` 必需文件清单；移动或改名时全仓搜索旧路径并更新活跃引用。
