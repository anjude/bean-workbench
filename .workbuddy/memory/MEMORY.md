# 项目长期记忆

## skill 实体位置
- 实体在 `bean-workbench/.agents/skills/`，工作台 git 管版本；`~/.agents` 是指向它的外链（`ln -s .../bean-workbench/.agents ~/.agents`），其他工具经它读同一套 skill。换机器重建外链即可。
- 坑：Python `Path.rglob` 与 Bash `grep -r` 都**不跟随符号链接目录**，校验/搜索脚本必须自写递归或单独 `cd ~/.agents` 再跑一遍。**改动目录结构后必须做负向测试**。
- 代价：skill 改动全局生效；只在台内试用先 `git stash push -- .agents`。

## skill 编号体系（2026-08-29 定稿，27→18）
- 格式：`{族群前缀}-{阶段号}{阶段内序号}-{能力后缀}`；工具 skill 用 `{前缀}-tools-{后缀}`，不占阶段号。`xx00` 是阶段入口，具体从 `xx01` 起。
- 族群：`dev-flow-*` 跨端开发 13+2、`bn-*` beannote 内容生产（**前缀 bn 不是 cn**）、`wb-*` 工作台基建 3。**bn 族群 2026-09-24 全部归档**，`.agents/skills/` 下已无 bn。两代归档：20260914（8 个，重规范）、20260924（2 个骨架）。
- **`wb-*` 是编号体系唯一例外（2026-09-14 豆哥定）**：不跑流水线、没有阶段可排，直接 `wb-{能力}`（`wb-router` / `wb-skill-refactor` / `wb-handoff`）。`check-workbench.py` 里 wb 走独立正则 `WB_NAME_RE`，带编号的 `wb-0102-handoff` 判不合规。旧名 `wb-0001-router` / `wb-0101-skill-refactor` 只在历史任务文档里残留。
- dev-flow 四阶段：`00` 方案设计（必过）/ `01` 后端 / `02` 前端 / `03` 整体验证（必过）。纯前端跳 01，纯后端跳 02。
  - `0000-plan-flow` 唯一入口；`0101-domain-flow`（只设计不连库）→ `0102-db-change-flow`（唯一写入口）→ `0103-api-flow`（+Wire）→ `0104-contract-flow`；`0201-archetype-flow`（原型+状态矩阵，硬门槛）→ `0202-data-flow` → `0203-page-flow` → `0204-asset-flow` → `0205-space-ui`（carbon 叠层全程生效）；`0301-verify-flow` 统一收口+回填；工具 `tools-repo` / `tools-db-query`（严格只读）。
  - `bn` 按**用户交互回合**划分（内容线不是流水线，质量判定权在用户，每步停下等确认）。**2026-09-13 彻底重构为「思考/梳理/表达」三层**：`bn-0000-think-flow`（追问到本质：拆层→追问→反常识点→排雷）/ `bn-0100-shape-flow`（读厚→读薄：主题句 + 3-5 小点逐点绑依据）/ `bn-0200-express-flow`（分享人视角：入口/顺序/落点/收尾，一次成稿）/ `bn-0301-review-flow`（反馈归层+逐轮收敛）/ `bn-0302-publish-flow` / `bn-0303-retro-flow`；工具 `bn-tools-knowledge-base` / `bn-tools-content-context`（目录与状态约定，所有阶段读）。`wb`：`wb-router` / `wb-skill-refactor` / `wb-handoff`。
  - **三层即能力边界（2026-09-13 重构）**：`00` 只答「这件事到底是什么」，`01` 只答「这次讲哪几个点」，`02` 只答「怎么讲给人听」。上一层替下一层做决策，下一层就只能翻译上一层的产物 = 念提纲 = AI 味。反馈归层：观点/事实/本质错→`00`；讲偏了/该说的没说→`01`；太 AI/像提纲/读不下去→`02`。
  - **重构原则（豆哥定）**：skill 只给框架和步骤，不写细；不搞机械写文规范。所有模板类 references（大纲/成稿/表达设计/质检清单/发布清单/复盘模板）已删，只留 `表达红线.md`（纠错清单，写完对照排查，不是写作模板）、`公众号草稿发布-本地配置.md`、`manifest模板.yaml`。细节在实践里迭代。
  - **风格锚点**：`business-repo/beannote/topics/2026-09-12_智谱融资条款拆解/03_正文.md` —— 从读者刚看到的数字开口、抽象条款落到具体价格、收尾克制不升华。
  - 槽位（2026-09-14 定，格式 `{阶段号}-{阶段内序号}-{槽位名}-{主题}`，阶段号固定两位不动）：`01-1-问答录-{主题}.md`（讨论阶段的问答原始记录）/ `01-2-素材-{主题}.md`（有意思的知识点、故事、数字，带出处和可用在哪）/ `01-3-大纲-{主题}.md`（事实模块：必须解释 / 有意思 / 待核 + 问题分类表）/ `02-1-公众号-{主题}.md` / `02-2-小红书-{主题}.md`。序号即流程顺序，中间插文件要重排。
  - **`source/` 目录（2026-09-14 豆哥加）**：每个 topic 下建一个，放原始素材——原文摘录、数据表格、网络内容快照。命名 `{序号}-{来源}-{内容}.md`，文件头写来源 URL、数据口径、抓取时间，表格照抄原文不加工。**原文进 source，结论进槽位文件**，槽位文件不膨胀、事实可追溯。
  - **目录骨架的唯一定义处**：原是 `bn-0000-init-flow`（豆哥 2026-09-14 定），增删槽位、改命名一律先改它，再同步已建 topic 的 `manifest.json` 的 `slots`。**该 skill 已随 bn 族群归档**，下一代开建时这条约定继续生效，定义处跟着新 skill 走。
- 合并粒度：同阶段总是一起走的小 skill 合并，超 300 行才拆；不合并的是读写边界、品牌特化资产。
- 方案文档落工作台 `task/YYMMDD_{主题}/README.md`，不再往业务仓 `docs/feature/` 新增。
- 编号表在 `AGENTS.md`；目录名 / `SKILL.md` 的 `name` / 文档引用三者必须一致，改完跑 `make check`。
- 旧名对照（查历史文档）：`be-*`/`fe-*` 前缀已废弃，统一为 `dev-flow-*`；`content-beannote-knowledge-base`→`bn-0001`、`content-beannote-creation-flow`→`bn-0101`、`content-beannote-article-review`→`bn-0201`；`hair`→`wb-0000-hair`、`workbench-router`→`wb-0101-router`→合并为 `wb-0001-router`→去编号为 `wb-router`。历史文档里的旧路径刻意保留，靠路由提示指路。

## skill 写法偏好
- **规则用正面表述**（豆哥 2026-09-19 定）：写"要做什么"，少写"不要做什么"。禁止式规则记不住也执行不了，改成"做完 X 就停""查到什么记什么""只做当前环节"这类动作指令。走偏信号写成对照表：左边"在做的事"，右边"回到哪"。
- **别把单次自然行为固化成 skill 规则**（豆哥 2026-09-23 吐槽"太机械了"）：一次顺手的动作（阶段总结汇总回槽位文件、补 source）不需要写成五条规范。写进 skill 的门槛是"不写就会反复做错"，不是"这次做对了值得记"。日常互动里的好做法留在 working memory，skill 保持骨架。写之前先问：不写这条，下次会不会出事？

## 工作台目录约定
- `docs/` 只放说明类，平铺：`workspace.md`、`self-evolution.md`、`task-system.md`、`goals.md`。
- 要照着填/做的材料进各 skill 的 `references/`，并在 `SKILL.md` 里列「配套 references」表（文件/用途/何时读）。
- `knowledge-base/README.md` 同时是规范+条目模板；`task/pain-points.md` 记痛点，`task/registry.md` 登记任务。
- **`handoff/` 与 `process/` 两层（2026-09-21 豆哥加）**：任务目录下分开。`handoff/` 是「我从哪接着干」——高层、一屏、时间戳快照、最后一份最新；`process/` 是「这件事怎么被想清楚的」——一个阶段一份 `{阶段号}-{环节名}.md`，记做了什么/结论/被推翻的判断/待核。handoff 只引用 process 路径不复制内容，process 不写下一步。写法定义处 `wb-handoff`。**2026-09-23 更正：process 是 topic 维度的**，工作台 task 目录和 beannote 选题目录两边都建，`process/{阶段号}-{环节名}.md`，命名写法一致；选题那边的骨架由选题初始化 skill 建（该 skill 现已归档）。选题内部分工：槽位文件（如 `01-1-问答录`）横向按题号、结论会被覆盖；`process/` 纵向按阶段时间、只增不改、留被推翻的判断路径；`source/` 放第三方原文。（曾误写成"选题目录不建 process/，槽位文件已经够了"，是替豆哥排除，错。）

## 环境：macOS（2026-08-29 起）
- darwin/arm64，无 pwsh/powershell；brew 在 `/opt/homebrew/bin/brew`，Go 1.27.0 在 `~/sdk/go`（PATH 与 GOPROXY 写在 `.zshrc` 末尾，曾被 oh-my-zsh 模板覆盖过）。
- **助手 Bash 的 PATH 不完整**：不读 `/etc/paths.d` 也不读 `.zshrc`，直接敲 `brew`/`go` 会 command not found。用绝对路径或先 `export PATH="/opt/homebrew/bin:$HOME/sdk/go/bin:$PATH"`。判断「没装」前先排除 PATH。
- `make check` 调 `script/check-workbench.py`（纯标准库，跨平台）：必需文件存在性 + skill 命名一致性 + md 相对链接失效。三项均已负向测试。
- 业务仓 `backend-superone` 仍是 Windows 脚本（`push.bat`、`powershell` 取日期、`cygpath` 会退化成 `HOME=""` 导致 SSH key 找不到），非明确需求不动业务仓。

## 引用同步排查坑
- Grep 工具默认跳过点开头目录，扫不到 `.agents/skills/`；全仓同步必须 `grep -rn --exclude-dir=business-repo --exclude-dir=.git --exclude-dir=node_modules`。
- 改完要区分：活跃文档（`AGENTS.md`、`SKILL.md`+`references/`、`docs/`、`task/registry.md`、脚本）必须改新名；历史任务文档保留旧名。

## carbon 项目（uni-carbon-space）
- 「留白」模块显示名改**「一隅」**（key `play` 不变）。「边界」= 个人使用说明书，两份模型，2026-07-11 已落地前后端（`/api/so/carbon/boundary/*` 5 接口）。
- 品牌硬约束：两人留痕/回看的空间，不是效率或冲突解决工具；避免已读未读、强提醒、催回复、任务式推进；配色仅暖色（米白 #f5f0ea + 琥珀 #f0a050），**无红绿独立色**；文案第一人称、具体、克制，禁口号。
- 文档放 `business-repo/uni-carbon-space/docs/feature/YYYY-MM-DD_功能名方案.md`，**一篇合并**含前后端改动点+测试三表，不要拆两份、不要放 docs 根目录。
- `frontend-contracts/openapi/carbon_api.yaml` 只**增量 append**，不整份重写；`components:` 必须在第 0 列（曾误缩进成 paths 子节点）。
- 迁移：carbon 表不走 `tablesToCreate`，用 `scripts/migration/sql/YYYYMMDD_*.sql` + `go run ./scripts/migration -action=exec-sql -sql-file=<path> -env=test`；新增表须手动加进 `exec_sql.go` 的 `carbonTables`。test 库是共享远程库，写操作须用户「继续」授权。
- gin validator 坑：含合法 0 值的整数字段别用 `binding:"required"`，改 `gte=0` + 业务层兜底。

## beannote 内容（豆小匠）
- **行为规范只在 skill 里，不写进业务仓文档**（2026-09-08 定）：beannote 的 `docs/` 只描述「项目是什么样」给接手的人看（`项目说明.md`/`账号定位.md`/`content-playbook.md`），目录、槽位、状态、交互节奏一律进 bn skill。曾把目录规范写成 `docs/目录规范.md`，已删。
- 目录（2026-09-08 重构，8→4）：`topics/`（唯一生产区，一篇一目录）/ `knowledge-base/` / `data/` / `docs/`。目录与状态约定原本在 `bn-tools-content-context` skill（已归档），状态看板 `topics/索引.md`（由各篇 `manifest.yaml` 派生）。
- **每篇一个 `manifest.yaml`（2026-09-08 加）**：单篇唯一状态源，记 `status`/`conclusion`/`decisions`(含被否切口)/`blockers`/`metrics`/`slots`/`next` 等。`status` 必须与目录名前缀一致。改完重跑 `business-repo/beannote/script/gen_index.py` 重建索引（自带无依赖 YAML 解析）。模板 `bn-tools-content-context/references/manifest模板.yaml`。
- 一篇一目录：`topics/{状态前缀}{日期}_{主题}/`，前缀无=在制、`done-`=已发布、`drop-`=已归档。路径建后不变，只在发布/废弃时同层改名，不跨目录搬家。
- **月份归档（2026-09-08 加）**：`topics/` 根只放当前月选题，跨月后按**选题记录日**搬进 `topics/YYYY-MM/`，只换所在目录不改目录名。触发时机：开题前扫一眼根，有非当前月的先搬再干活。
- 槽内文件固定数字前缀：`01_选题卡` `02_脚本` `03_正文` `04_发布稿` `05_检查清单` `06_复盘` ＋ `assets/`。缺哪号=卡在哪步。旧名对照：公众号文章→04、纯享正文→03、图文脚本→02、发布检查清单→05、复盘→06。
- 最小充分原则：公众号默认 01/04/05，小红书 01/02/03/05，06 有反馈才写。
- 历史复盘文件里的旧路径（`02_topic_pool/TODO_*` 等）按约定保留，不回改。
- `docs/content-playbook.md`（账号定位）优先级高于 skill 旧规则。
- 投资认知内容：反口号说教，讲清「测量方法+背后道理」，给阈值不堆公式，老实交代局限。
- 公众号标题偏好：痛点实操 / 案例拆解 / 反常识 / 数据清单四类原型。
