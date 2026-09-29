# dev-flow 跨端 skill 族合族

## 背景

工作台此前按端分成两条 skill 流水线：

- `be-*` 后端 8 个（2026-08-29 上午已重构为四阶段 + 工具层）。
- `fe-*` 前端 11 个，仍是旧三阶段，`fe-0000-dev-flow` 是 176 行总控。

问题不在命名，在语义：

1. **一次需求要跨两个族群**。跨端需求得先走 `be-*` 拿契约、再跳到 `fe-*` 消费，`be-0000-plan-flow` 的派发表里前端那一行只能写「当前走 `fe-*` 系列」，链路是断的。
2. **阶段语义对不上**。be 的 `00/01/02/03` 是「方案 / 后端 / 前端 / 验证」，fe 的 `00/01/02` 是「设计 / 开发 / 交付」。同一个编号在两端含义不同。
3. **前端总控和后端总控的处置不一致**。be 的总控已经拆掉（方案进 plan-flow、上下文进工具层），fe 的总控还同时承担项目上下文、开发原则、阶段编排、执行模式、输出格式五件事。
4. **族名带端**。`be`/`fe` 这两个前缀把「一次需求」切成了「两次任务」，命名本身就在强化分裂。

## 目标

1. 合并为单一跨端族群 `dev-flow-*`，一次需求走一条流水线。
2. 四阶段语义统一，前后端各有固定阶段位。
3. 拆掉 `fe-0000-dev-flow`，原则落到该管的 skill 里，项目上下文收进工具层。
4. 工具层扩展到多仓，不再只服务后端仓。

## 四阶段定义

| 阶段号 | 含义 | 进入条件 | 产物 | 退出条件 |
| --- | --- | --- | --- | --- |
| `00` | 方案设计 | 任意开发需求进入 | 方案文档 `task/YYMMDD_{主题}/README.md` | 用户确认，门禁四项通过 |
| `01` | 后端开发 | 方案已确认且涉及后端改动 | 领域层、DDL、接口、注入、契约 | 契约已生成，可交付前端消费 |
| `02` | 前端开发 | 方案已确认且涉及前端改动 | 类型、API、状态、页面、样式、资产 | 页面与状态齐备，可跑前端验证 |
| `03` | 整体验证 | 01 / 02 已产出 | 验证结论、方案回填 | 验证命令通过，落地记录已写回 |

阶段可跳过：纯前端需求跳过 01，纯后端需求跳过 02。只有 00 和 03 是必过节点。

## 新旧编号映射

### 阶段 00 方案设计

| 旧编号 | 新编号 | 变化 |
| --- | --- | --- |
| `be-0000-plan-flow` | `dev-flow-0000-plan-flow` | 改前缀；扩展前端需求解析、前端影响面落点、阶段 02 派发表、阶段 02 执行顺序、前端门禁项 |
| `fe-0000-dev-flow` | — | **删除**。内容拆到下方各处 |

### 阶段 01 后端开发

| 旧编号 | 新编号 | 变化 |
| --- | --- | --- |
| `be-0101-domain-flow` | `dev-flow-0101-domain-flow` | 仅改前缀 |
| `be-0102-field-sql-flow` | `dev-flow-0102-field-sql-flow` | 仅改前缀 |
| `be-0103-db-change-flow` | `dev-flow-0103-db-change-flow` | 仅改前缀 |
| `be-0104-api-flow` | `dev-flow-0104-api-flow` | 仅改前缀 |
| `be-0105-wire-flow` | `dev-flow-0105-wire-flow` | 仅改前缀 |
| `be-0106-contract-flow` | `dev-flow-0106-contract-flow` | 改前缀；阶段 02 交接点从「`fe-*` 系列」改为「`dev-flow-0204-api-flow`」 |

### 阶段 02 前端开发

| 旧编号 | 新编号 | 变化 |
| --- | --- | --- |
| `fe-0001-product-archetype-flow` | `dev-flow-0201-product-archetype-flow` | 加阶段定位；加「先出产品再出页面」硬门槛 |
| `fe-0002-state-matrix-flow` | `dev-flow-0202-state-matrix-flow` | 加阶段定位；加「先补齐状态再写 happy path」硬门槛 |
| `fe-0003-space-ui` | `dev-flow-0203-space-ui` | 加阶段定位；调度方从已删总控改为 plan-flow |
| `fe-0101-api-flow` | `dev-flow-0204-api-flow` | 加阶段定位 |
| `fe-0102-state-flow` | `dev-flow-0205-state-flow` | 加阶段定位；新增「约束」段（不引入新状态库、逻辑不塞页面、不机械加 Repo、不做无关重构） |
| `fe-0103-page-flow` | `dev-flow-0206-page-flow` | 加阶段定位；新增「用户已给规格时不额外加入口」约束 |
| `fe-0104-component-style-flow` | `dev-flow-0207-component-style-flow` | 加阶段定位；反拼凑检查加「整体匹配」原则 |
| `fe-0105-svg-flow` | `dev-flow-0208-svg-flow` | 加阶段定位；新增「资产主权检查」清单 |
| `fe-0106-icon-flow` | `dev-flow-0209-icon-flow` | 加阶段定位 |

### 阶段 03 整体验证

| 旧编号 | 新编号 | 变化 |
| --- | --- | --- |
| `be-0301-test-review-flow` | `dev-flow-0301-backend-verify-flow` | 改前缀与后缀，定位为后端侧收口；明确跨端需求的方案回填由本 skill 统一负责 |
| `fe-0201-test-build-flow` | `dev-flow-0302-frontend-verify-flow` | 整体重写：加阶段门禁复核、审查重点、回填分工；与 0301 结构对齐 |

### 工具层

| 旧编号 | 新编号 | 变化 |
| --- | --- | --- |
| `be-tools-project-context` | `dev-flow-tools-project-context` | 从后端单仓扩为四仓速查：工作台根 / 后端仓 / 前端仓 / 协议仓，含各自目录约定、技术栈、构建命令、分支语义 |
| `be-tools-db-query` | `dev-flow-tools-db-query` | 仅改前缀 |
| `be-tools-branch-release` | `dev-flow-tools-branch-release` | 仅改前缀 |

## fe-0000-dev-flow 拆解去向

| 原内容 | 去向 |
| --- | --- |
| 项目上下文（技术栈、目录） | `dev-flow-tools-project-context`，核实前端仓真实结构后重写 |
| 子 skill 选择清单 | `dev-flow-0000-plan-flow` 阶段派发表 |
| 核心原则：先出产品再出页面 | `dev-flow-0201-product-archetype-flow` 硬门槛 |
| 核心原则：先补齐状态再写 happy path | `dev-flow-0202-state-matrix-flow` 硬门槛 |
| 核心原则：资产主权 | `dev-flow-0208-svg-flow` 资产主权检查 |
| 核心原则：整体匹配不拼凑 | `dev-flow-0207-component-style-flow` 反拼凑检查 |
| 品牌一致性检查 | `dev-flow-0203-space-ui`（原有结构治理段已覆盖） |
| 标准阶段 10 步 | `dev-flow-0000-plan-flow` 阶段 02 执行顺序 |
| 自动开发约束（不引新框架、逻辑不塞页面、不走 uni.request、不机械加 Repo、不做无关重构） | `dev-flow-0205-state-flow` 新「约束」段；`0204` 原有约束保留 |
| 自动开发约束（不额外加入口、首屏依赖外部资源、主题回令牌） | `0206` / `0208` / `0207` |
| 两种执行模式、最终输出格式 | `dev-flow-0000-plan-flow` 工作模式段 |

## 职责边界

- **0102 只设计，0103 才执行**。字段与 SQL 产出不连库，DDL/DML 执行归 0103。
- **tools-db-query 严格只读**。出现 INSERT/UPDATE/CREATE 立即转 `dev-flow-0103-db-change-flow`。
- **0106 只生成契约，消费属阶段 02**。前端从 `dev-flow-0204-api-flow` 开始消费 0106 的复制清单。
- **0201、0202 是硬门槛**，不是可选项。原型和状态矩阵没过，不进页面实现。
- **方案回填分端**：纯前端需求由 0302 回填；跨端需求由 0301 统一回填，0302 提供前端结论。

## 执行清单

1. 22 个目录重命名（无循环占用，前缀整体替换）。
2. 全仓文本替换：28 个文件，一次性正则扫描。
3. 删除 `fe-0000-dev-flow`。
4. 重写 `dev-flow-tools-project-context` 为多仓速查。
5. 扩展 `dev-flow-0000-plan-flow`：前端需求解析、前端落点、阶段 02 派发与执行顺序、门禁加前端项。
6. 前端 9 个 skill 加阶段定位，修正对已删总控的引用，吸收原则与约束。
7. 重写 `dev-flow-0302-frontend-verify-flow`，调整 `dev-flow-0301-backend-verify-flow` 定位。
8. 同步 `AGENTS.md`、`docs/workspace.md`、`docs/workflows/business-generation-checklist.md`、`task/registry.md`、长期记忆。

## 校验清单

1. 每个 skill 目录名与 `SKILL.md` 的 `name` 一致。
2. 悬空引用扫描：全仓提取技能名，逐个确认目录存在；历史映射文档的旧名属刻意保留。
3. 阶段链路闭合：plan-flow 派发表覆盖全部 18 个阶段 skill；每个 skill 能指到上下游。
4. 旧编号残留：工作台范围内 `be-*` / `fe-*` 仅出现在历史映射记录中。
5. 工作台结构校验：按 `script/check-workbench.ps1` 路径清单逐项确认。

## 校验结果

| 项 | 结果 |
| --- | --- |
| 目录名与 `name` 一致 | 27 个 skill 全部一致 |
| 悬空引用扫描 | 无；历史映射文档的旧名属刻意保留 |
| 旧族名残留 | 仅存于 `wb-0102-skill-refactor` 与 `task/registry.md` 的历史叙述 |
| plan-flow 派发表覆盖 | 18 个阶段 skill 全覆盖 |
| 前端品牌 skill 资产 | `dev-flow-0203-space-ui/references/` 两个 CSS 文件随目录迁移完好 |
| 工作台结构校验 | 17 项必需路径全在 |

## 当前状态

已完成。21 个 skill 归入 `dev-flow-*` 单族（18 个阶段 skill + 3 个工具 skill），加上 `bn-*`（3）与 `wb-*`（3），工作台共 27 个 skill。
