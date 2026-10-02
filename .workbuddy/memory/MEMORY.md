# 项目长期记忆（bean-workbench）

## 工程结构
- 多子模块工程。业务仓：`backend-superone`（Go+Gin+GORM）、`uni-superone`（微信绿"豆流便签"前端）、`frontend-contracts`（契约源：openapi yaml + types + apis，以 git submodule 挂 `uni-superone/src/contracts`）。
- 测试库硬编码共享远程库，DDL/写操作须用户"继续"逐项授权；迁移 `go run ./scripts/migration -action=exec-sql -sql-file=<path> -env=test`。
- 分支：dev 开发、就绪合 release；**开发阶段不擅自 commit，保持未提交工作区**，等"提交/合 release"再动。子仓改动须 push 远端后才可 bump 父仓子模块指针。

## 环境
- macOS arm64。助手 Bash PATH 不完整：`go` 用 `~/sdk/go/bin/go`，`brew` 用 `/opt/homebrew/bin/brew`；判"没装"前先排除 PATH。
- `make check` 跑 `script/check-workbench.py`（必需文件 + skill 命名一致 + md 相对链接失效）。backend-superone 仍是 Windows 脚本，非明确需求不动。

## skill
- 实体在 `.agents/skills/`，`~/.agents` 是指向它的外链；改动全局生效，台内试用先 `git stash push -- .agents`。
- 编号 `{前缀}-{阶段号}{序号}-{后缀}`；`dev-flow-*` 四阶段 00→01→02→03（必过 00 与 03）；`wb-*` 是唯一不跑流水线的例外（wb-router/skill-refactor/handoff）；`bn-*` 已归档。
- 写法：正面表述、只给框架与步骤、不把单次顺手行为固化成 skill 规则。

## 代码复杂度（豆哥定）
- 一套设计只解决一个问题，不叠加第二套解法；"要不要留缝"默认不留（直接调用 > 端口+接线）；提新抽象前先确认删掉老方案仍成立；顺手清未使用字段/单调用者中间方法。

## 目录与文档约定
- `task/YYMMDD_{主题}/README.md` 落方案文档（不往业务仓 docs/ 新增）。活跃文档改名须同步 `AGENTS.md`/SKILL.md/引用并跑 `make check`。
- `handoff/` 是一屏快照（最新一份）；`process/` 是 topic 维度思考过程（做了什么/结论/被推翻判断/待核），纵向只增不改。

## carbon / 边界
- 暖色品牌（米白 #f5f0ea + 琥珀 #f0a050），无红绿独立色；两人留痕空间，禁已读未读/强提醒/催回复/任务式推进。

## uni-superone 前端（豆流便签）
- 微信绿主色 #07C160；令牌 `--so-*`，主题类 `.theme-light`/`.theme-dark`。视觉/布局以 carbon 首页为样板（rail+swiper+底部操作栏+主按钮遥控+反受控弹层+高度链），不自创。
- **关键真机坑**：① 令牌只能挂 `page` 与主题类，**禁用 `:root`**；② `page` 不设主题背景，背景交给页面根容器；③ 用 `background: var(...)`，不要为想象中的兼容性写硬编码兜底；④ 不支持动态组件 `<component :is>`；⑤ 弃用 `uni.getSystemInfoSync()`，改用 getWindowInfo/getAppBaseInfo/getDeviceInfo。
- 页面包 `<so-page>` 门禁（profile 除外）；原生全局对象声明在 `src/types/platform.d.ts`（用到裸 `wx` 在此补，别另建 d.ts）。详细设计见 `task/261002_superone-modules/` 与 process 文件。

## beannote（豆小匠）
- 行为规范只在 skill，文档只描述项目本身。`topics/` 一篇一目录 + `manifest.yaml` 状态源；槽位 `01_选题卡`…`06_复盘`。投资认知：反口号说教，讲测量方法+背后道理，给阈值不堆公式。
