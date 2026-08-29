# dev-flow skill 合并精简

## 背景

2026-08-29 完成跨端合族后，`.agents/skills/` 有 27 个 skill。路由成本开始盖过收益：一次普通需求要连着读 6-9 个文件，其中不少只有 30-60 行，且执行顺序永远相邻（设计完字段就出 SQL、写完接口就补 Wire、原型判断完就补状态矩阵）。

用户反馈：skill 太多，适当合并和精简。

## 目标

- 数量从 27 降到 18，降幅 33%。
- 合并「总是一起走」的相邻小 skill，不丢约束内容。
- 保留三类边界：**读写边界**、**品牌特化资产**、**超长正文**。
- 阶段语义不变，仍然是 00 方案设计 / 01 后端开发 / 02 前端开发 / 03 整体验证。

## 合并映射（27 → 18）

### 阶段 01 后端开发：6 → 4

| 合并前 | 合并后 |
| --- | --- |
| `dev-flow-0101-domain-flow`（44 行） | `dev-flow-0101-domain-flow`（领域层 + 字段与 SQL 设计，含 `references/field-design-norms.md`） |
| `dev-flow-0102-field-sql-flow`（29 行） | ↑ |
| `dev-flow-0103-db-change-flow`（110 行） | `dev-flow-0102-db-change-flow` |
| `dev-flow-0104-api-flow`（30 行） | `dev-flow-0103-api-flow`（接口层 + Wire 装配） |
| `dev-flow-0105-wire-flow`（30 行） | ↑ |
| `dev-flow-0106-contract-flow`（139 行） | `dev-flow-0104-contract-flow` |

### 阶段 02 前端开发：9 → 5

| 合并前 | 合并后 |
| --- | --- |
| `dev-flow-0201-product-archetype-flow` | `dev-flow-0201-archetype-flow`（原型判断 + 状态矩阵，硬门槛合一） |
| `dev-flow-0202-state-matrix-flow` | ↑ |
| `dev-flow-0204-api-flow` | `dev-flow-0202-data-flow`（API 类型/请求 + 可选 Repo + store/composable） |
| `dev-flow-0205-state-flow` | ↑ |
| `dev-flow-0206-page-flow` | `dev-flow-0203-page-flow`（页面/路由/生命周期 + 组件与样式） |
| `dev-flow-0207-component-style-flow` | ↑ |
| `dev-flow-0208-svg-flow` | `dev-flow-0204-asset-flow`（SVG 资产主权 + carbon 品牌图标） |
| `dev-flow-0209-icon-flow` | ↑ |
| `dev-flow-0203-space-ui`（带 `references/` CSS） | `dev-flow-0205-space-ui`（改为全程叠层，不再占一个执行步） |

### 阶段 03 整体验证：2 → 1

| 合并前 | 合并后 |
| --- | --- |
| `dev-flow-0301-backend-verify-flow`、`dev-flow-0302-frontend-verify-flow` | `dev-flow-0301-verify-flow`（按端分节，方案回填统一负责） |

### 工具层：3 → 2

| 合并前 | 合并后 |
| --- | --- |
| `dev-flow-tools-project-context`、`dev-flow-tools-branch-release` | `dev-flow-tools-repo`（仓库上下文 + 分支部署） |
| `dev-flow-tools-db-query` | 不变（严格只读，与写操作隔离） |

### wb 族：3 → 2

| 合并前 | 合并后 |
| --- | --- |
| `wb-0000-hair`、`wb-0101-router` | `wb-0001-router`（入口 + 路由） |
| `wb-0102-skill-refactor` | `wb-0101-skill-refactor` |

## 刻意不合并的三类

1. **读写边界**：`dev-flow-0102-db-change-flow`（写）与 `dev-flow-tools-db-query`（只读）分开。合并后文档里会出现「本节只做读、禁止写」这类自相矛盾的约束，安全边界就失效了。
2. **带独立资产的特化层**：`dev-flow-0205-space-ui` 带 `references/css-variables.css`、`animations.css`，并入通用 skill 会让资产目录和职责混在一起。改为叠层调用。
3. **超长正文**：`bn-0101-creation-flow` 已 511 行，不再往里并 `bn-0201-article-review`。bn 族三个阶段（素材 / 创作 / 复盘）保持独立。

## 执行清单

1. 全部待调整目录先 `mv` 到 `tmp-*` 前缀，避免编号循环占用。
2. `mv` 到终态编号，被合并目录删除，资产目录（`references/`）随主体迁移。
3. 重写合并后的 `SKILL.md`：以执行靠前的为主体，被合并内容作为编号章节（一、二、三）并入。
4. 更新交叉引用：所有 `SKILL.md` 正文、`dev-flow-0000-plan-flow` 派发表与执行顺序、工具层引用。
5. 同步外部文档：`AGENTS.md` 编号表与命名原则、`docs/workspace.md` 示例与原则、`docs/workflows/business-generation-checklist.md`、`docs/goals/README.md`、`task/registry.md`、`script/check-workbench.ps1`。
6. 更新长期记忆：`MEMORY.md` 编号体系段 + 追加合并对照链。
7. 补 `wb-0101-skill-refactor`：新增「5. 合并精简」步骤、合并判定原则、两条踩坑。

## 校验结果

- skill 数量：18（13 个 dev-flow 阶段 skill + 2 个工具 + 2 个 wb + 3 个 bn）。
- 目录名与 `SKILL.md` 的 `name` 字段：18/18 一致。
- 悬空引用：`.agents/skills/` 内 0 处；活跃文档（AGENTS.md、docs/、task/registry.md、script/、长期记忆正文）0 处。
- 残留旧名仅出现在历史任务文档（`task/260614_*`、`260628_*`、`260829_be-skill-refactor`、`260829_dev-flow-merge`）与 `MEMORY.md` 的旧名对照链，属刻意保留。
- `dev-flow-0000-plan-flow` 派发表覆盖全部 13 个阶段 skill，阶段内执行顺序与编号一致。
- 资产完整：`dev-flow-0101-domain-flow/references/field-design-norms.md`、`dev-flow-0205-space-ui/references/{css-variables,animations}.css` 均已随目录迁移。

## 当前状态

已完成。后续新增需求按 `dev-flow-0000-plan-flow` 派发，不再引用旧的 0102-field-sql / 0105-wire / 0202-state-matrix 等编号。
