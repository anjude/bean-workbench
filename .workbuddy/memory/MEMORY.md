# 项目长期记忆

## 工作台 skill 编号体系（2026-08-29 定稿：be 族四阶段重构 → 前后端合为 dev-flow 单族 → 合并精简，27 个降到 18 个）
- 两种格式：`{族群前缀}-{阶段号}{阶段内序号}-{能力后缀}`（阶段 skill）、`{族群前缀}-tools-{能力后缀}`（**工具 skill，不占阶段号**）。四位编号拆两段：前两位=阶段号，后两位=阶段内序号（`xx00` 留给该阶段入口，具体 skill 从 `xx01` 起）。
- 族群：`dev-flow-*` 跨端开发（13 阶段 skill + 2 工具，前后端合一，含 carbon 品牌特化层）、`bn-*` beannote 内容生产（3，**前缀是 bn 不是 cn**）、`wb-*` 工作台基建（2）。合计 18 个。
- **dev-flow 四阶段**（一次需求的推进顺序）：`00` 方案设计 / `01` 后端开发 / `02` 前端开发 / `03` 整体验证。纯前端需求跳过 01，纯后端需求跳过 02；00 和 03 是必过节点。`bn` 为 `00` 素材 / `01` 创作 / `02` 复盘；`wb` 为 `00` 入口 / `01` 路由与维护。
- dev-flow 现编号：`0000-plan-flow`（唯一入口，方案设计+阶段派发）；后端 `0101-domain-flow`（领域层+字段与 SQL 设计，只设计不连库）/ `0102-db-change-flow`（唯一写操作入口）/ `0103-api-flow`（接口+Wire 装配）/ `0104-contract-flow`（OpenAPI+前端契约）；前端 `0201-archetype-flow`（原型+状态矩阵，硬门槛）/ `0202-data-flow`（API 类型+Repo+store/composable）/ `0203-page-flow`（页面+组件样式）/ `0204-asset-flow`（SVG+carbon 图标）/ `0205-space-ui`（carbon 品牌叠层，全程生效）；验证 `0301-verify-flow`（后端+前端统一收口与回填）；工具层 `tools-repo`（多仓上下文+分支部署）/ `tools-db-query`（严格只读）。
- **合并粒度原则（2026-08-29 定）**：同阶段内「总是一起走」且各自只有几十行的小 skill 合并成一个，用章节区分职责；单个 skill 超过 300 行才考虑拆。不合并的是三类：读写边界（db-change 写 vs db-query 只读）、品牌特化资产（space-ui 带 references CSS）、跨端验证的不同命令集已合并进一节。
- **方案产出规范**：开发需求的方案文档**落工作台 `task/YYMMDD_{主题}/README.md`**，不再往业务仓 `docs/feature/` 新增（历史文件保留）。模板见 `dev-flow-0000-plan-flow`，含需求理解/目标与边界/改动范围/实施方案/验收标准/实施顺序/测试方案三表/风险与回滚/落地记录。回填统一由 `dev-flow-0301-verify-flow` 负责，不再分前后端两个 skill。
- **职责边界**：`0101` 只设计不连库，`0102` 才执行写操作；`tools-db-query` 严格只读；`0104` 只生成契约，消费从 `0202` 开始；`0201` 原型与状态矩阵没过不进 `0203` 页面。
- 编号表维护在 `AGENTS.md`「当前 skill 编号表」，命名规则在 `docs/workspace.md`。目录名 / `SKILL.md` 的 `name` / 文档引用三者必须一致；改编号要同步 `script/check-workbench.ps1` 路径清单（目前只校验 wb-* 两个）。
- 新增 skill 先定阶段再定阶段内序号，追加到该阶段末尾；插队须重排并同步全部引用。横切能力建 `*-tools-*`，不要塞进阶段编号。两端同名能力（如 api-flow）靠阶段号区分，不改后缀。
- 旧名对照链（查历史文档用）：`backend-superone-dev-flow`→`be-0000-dev-flow`→`be-0000-plan-flow`→`dev-flow-0000-plan-flow`；`*-domain-flow`→`be-0001`→`be-0101`→`dev-flow-0101`；`*-field-sql-flow`→`be-0002`→`be-0102`→`dev-flow-0102`；`*-db-change-flow`→`be-0101`→`be-0103`→`dev-flow-0103`；后端 `*-api-flow`→`be-0102`→`be-0104`→`dev-flow-0104`；`*-wire-flow`→`be-0103`→`be-0105`→`dev-flow-0105`；`backend-frontend-contract-flow`→`be-0201-contract-flow`→`be-0106-contract-flow`→`dev-flow-0106-contract-flow`；`*-test-review-flow`→`be-0202`→`be-0301`→`dev-flow-0301-backend-verify-flow`；`uni-dev-flow`→`fe-0000-dev-flow`（2026-08-29 拆掉，内容散进 plan-flow/工具层/各前端 skill）；`uni-product-archetype-flow`→`fe-0001`→`dev-flow-0201`；`uni-state-matrix-flow`→`fe-0002`→`dev-flow-0202`；`carbon-space-ui`→`fe-0003-space-ui`→`dev-flow-0203-space-ui`；前端 `uni-api-flow`→`fe-0101`→`dev-flow-0204-api-flow`；`uni-state-flow`→`fe-0102`→`dev-flow-0205`；`uni-page-flow`→`fe-0103`→`dev-flow-0206`；`uni-component-style-flow`→`fe-0104`→`dev-flow-0207`；`uni-svg-flow`→`fe-0105`→`dev-flow-0208`；`carbon-icon-flow`→`fe-0106-icon-flow`→`dev-flow-0209-icon-flow`；`uni-test-build-flow`→`fe-0201`→`dev-flow-0302-frontend-verify-flow`；`content-beannote-knowledge-base`→`bn-0001`、`content-beannote-creation-flow`→`bn-0101`、`content-beannote-article-review`→`bn-0201`；`hair`→`wb-0000-hair`、`workbench-router`→`wb-0101-router`。
- 2026-08-29 合并精简对照（27→18，查旧文档用）：后端 `0102-field-sql` 并入 `0101-domain-flow`、`0105-wire` 并入新 `0103-api-flow`（原 `0104-api`）、原 `0103-db-change`→`0102-db-change-flow`、原 `0106-contract`→`0104-contract-flow`；前端 `0202-state-matrix` 并入 `0201-archetype-flow`、`0205-state` 并入 `0202-data-flow`（原 `0204-api`）、`0207-component-style` 并入 `0203-page-flow`（原 `0206-page`）、`0209-icon` 并入 `0204-asset-flow`（原 `0208-svg`）、原 `0203-space-ui`→`0205-space-ui`（改全程叠层）；`0301-backend-verify` + `0302-frontend-verify`→`0301-verify-flow`；`tools-project-context` + `tools-branch-release`→`tools-repo`；`wb-0000-hair` + `wb-0101-router`→`wb-0001-router`、`wb-0102-skill-refactor`→`wb-0101-skill-refactor`。

## 公众号内容生产
- 用户运营一个微信公众号，内容方向偏**商业/科技/战略思考**（如"护城河"主题）。
- 上上一篇《科技不是护城河》阅读仅 4，用户怀疑标题差或被限流。结论：限流概率低（无敏感词），更可能是标题太抽象/书面化或送达问题。
- 用户偏好**高点击标题**，方向：痛点实操 / 案例拆解 / 反常识观点 / 数据清单四类原型。
- 已沉淀可复用 skill：`content-wechat-article-flow`（用户级 ~/.workbuddy/skills/），覆盖选题→写作→发布清单。
- 文章成稿存工作区根目录，命名如 `技术不是护城河续篇-痛点实操版.md`，文末固定附"发布防低阅读清单"。

## carbon 项目（uni-carbon-space，情侣空间小程序）
- 原"留白"模块显示名改为**"一隅"**（用户拍板），内部 key `play` 不变，英文眉标 "Quiet Corner" 保留。一隅是轻入口+认真内容的聚合容器（含 QQ农场/默契问答/小游戏/边界）。
- "边界"模块（个人使用说明书）采用**两份模型**：每人写自己的底线/喜欢/不喜欢，对方只读且可表态（懂了 / 还需磨合）。**已于 2026-07-11 落地前后端代码**（前端页 `pages/boundaries/index.vue` + `useBoundary` composable + `biz-play-tab.vue` 入口卡片；后端 5 接口 list/create/update/react/delete 走 `/api/so/carbon/boundary/*`，权限：作者可改删、对方可表态、不可对自己表态、非成员拒绝）。设计文档 `docs/feature/2026-07-11_边界功能方案.md`、功能设计 `docs/功能设计文档.md「7. 边界」`。
- **carbon 品牌调性硬约束（做所有模块都要守）**：定位=两人留痕/回看/确认关系形状的空间，**不是效率工具、不是冲突解决工具**；明确避免：已读未读、强提醒、催回复、任务式推进、过重积分。配色 token 仅暖色（米白 #f5f0ea + 琥珀 glow #f0a050），**无红/绿独立色**，关系状态用"点亮 vs 未点亮"而非红绿对比。文案克制、口语化、不审问；"边界"=空间的深水区，概念锚定"个人使用说明书"（"我是台需要说明书的设备"比"底线"更软、更不审问）；须柔软地做成交换卡片/慢问题。**文案红线：避免普世口号式**（如"每个人都需要一份说明书"把抽象概念当标语），用第一人称、具体的、克制的口语；自嘲可，喊口号不可。

## carbon 文档与 dev-flow 规范（易踩错，已踩过）
- **需求/设计文档必须放 `business-repo/uni-carbon-space/docs/feature/`**，命名 `YYYY-MM-DD_功能名方案.md`（如 `2026-05-24_约定功能方案.md`）。**不要放 `docs/` 根目录**，也**不要拆成「前端设计文档」「后端设计文档」两份**——现有范式是**一篇合并文档**同时含「前端改动点」和「后端改动点」，末尾带「测试方案」（功能/回归/兼容性三张表）。
- **需求只走 `dev-flow-0000-plan-flow` 一个入口**（原前端 `fe-0000-dev-flow` + 后端 `be-0000-dev-flow` 两个总控，2026-08-29 合并）。方案确认模式的前后端产出要求都在这个 skill 里：前端要产品原型判断/状态矩阵/文件级方案/资产主权/品牌一致性/验证命令，后端要业务理解+验收/受影响接口表字段/DDL/OpenAPI YAML/末尾强制「测试方案」三表。跨端需求出同一篇方案文档。
- 兄弟模块设计文档是最好模板：`docs/feature/2026-05-24_约定功能方案.md`（关系模块）、`docs/feature/2026-05-30_刻度功能MVP方案.md`。后端分层按 `backend-superone`：表模型 `internal/model/carbon_*_tab.go`、DTO `internal/domain/carbon/carbon_dto`、UseCase `carbon_use_case.go`、Router `app/api_service/api_service.go`、API 契约 `frontend-contracts/openapi/carbon_api.yaml`（与 uni-carbon-space 同级，此前不存在，2026-07-11 首次创建该目录并补 boundary 契约）。
- **carbon_api.yaml 维护约定（用户拍板 2026-07-12）**：该文件是边界模块契约的空白起点（git 无历史、非覆盖原有），**只增量 append 新接口**——`paths:` 加 path、`components.schemas:` 加 schema，**不整份重写**。以后任何 carbon 新接口都在此文件上增量维护，使其作为碳基空间契约基线。
- **carbon_api.yaml 缩进坑（2026-07-12 踩过）**：`components:` 必须是**第 0 列**的顶层键（与 `paths:`/`info:` 同级），其下 `securitySchemes:`/`schemas:` 在 2 列、schema 名在 4 列。在 `paths:` 末尾追加新接口时，若以「上一条 path 的 `description: success` + `  components:`」做锚点插入，容易把 `components:` 误留在 **2 列**，使其被解析为 `paths` 的子节点、顶层丢失 `components` 键、所有 `$ref` 仍只是字符串不报错但结构非法。插入后务必确认 `components:` 在第 0 列；用 `yaml.safe_load` 跑一遍 `list(d.keys())` 含 `components` 即为合法。

## carbon 后端表迁移约定（已踩坑）
- carbon 业务表**不走** `scripts/migration/config.go` 的 `tablesToCreate`（那是 user/spot/trip 等非 carbon 表），而是**单独的 DDL 文件** `scripts/migration/sql/YYYYMMDD_*.sql` + 命令：`go run ./scripts/migration -action=exec-sql -sql-file=<path> -env=test`（bash 下不要用 README 里的 `--%`，那是 PowerShell 语法）。
- `verify-carbon` 校验的表清单是 `scripts/migration/exec_sql.go` 里的 `carbonTables` 切片——**新增 carbon 表后须手动把表名加进去**，否则 verify 不覆盖、连表是否建成功都看不到。2026-07-11 已为 `carbon_boundary_tab` 加上。
- test 库是共享远程库（脚本里写死 `8.155.38.83/weiyi_superone_db_test`），建表真实生效，属外部写操作；执行前须向用户确认（用户授权"继续"后才执行）。
- **后端 DTO 校验坑（已踩）**：gin 的 validator 对数值类型，把 `0` 当零值，`binding:"required"` 会拒绝 `0`。任何**含合法 0 值**的整数字段（如 reaction 取消态=0、status 默认态=0）不要用 `binding:"required"`；改用 `binding:"gte=0"` 或去掉 required，让业务层 `isValidXxx` 兜底校验。2026-07-12 边界 `ReactBoundaryReq.Reaction` 因此导致"取消表态"报 param error，已改为 `gte=0`。

## beannote 内容（豆小匠）
- 选题池在 `business-repo/beannote/02_topic_pool/`，每篇按「选题卡」格式（模板与阶段调性见用户级记忆 + cn-0001-creation-flow skill）。
- 投资认知内容方向（2026-07-22 用户强调整）：反对口号/说教式，要科学、平实、可操作。重点讲清"测量方法 + 背后的道理"，必要处给阈值但**不要公式堆砌**；老实交代指标局限（能证伪不能证明），不夸大。不要泛泛而谈的"劝人"文。
- 进行中主题「什么情况下我们认为一个人在股市能稳定挣钱」：已收敛出可操作科学版（备净值数据 → 基础四数 → 夏普/索提诺/卡玛+阈值 → 统计显著性 t≈夏普×√年数 → α/β 回归 → 尾部风险一票否决 → 分段持续性）。待用户确认是否落选题卡。
