# 跨项目 Agent skill 源

这里存放跨项目复用的 skill。实体在 bean-workbench 仓库里，由工作台 git 做版本管理；`~/.agents` 是指向这里的外链，其他 Agent 工具和其他项目通过它读到同一套 skill。

## 目录结构

```text
.agents/                  本目录，工作台仓库内的实体
├── README.md             本文件，接入说明
├── skills/               skill 实体，按族群编号（wb-* 例外，用语义名）
│   ├── dev-flow-*        跨端开发流水线（13 个阶段 skill + 3 个工具 skill）
│   ├── bn-tools-*        内容写作规范、辅助编辑、排版与发布工具（4 个，不占阶段号）
│   └── wb-*              工作台基建（3 个，不编号）
└── vendor/product-video/ 第三方视频制作能力的固定版本
```

vendor/product-video/ 保存第三方视频 skill 的固定版本，来源、许可与更新方式见 [vendor/README.md](vendor/README.md)；工作台入口为 `skills/dev-flow-tools-product-video/`。

## 其他项目怎么读到

多数 Agent 工具会直接读 home 目录下的 `.agents`，所以外链在，其他项目什么都不用做：

```bash
ln -s /Users/bean/workspace/bean-workbench/.agents ~/.agents
```

某个项目想在本仓目录里也能看到，再建一条项目内链接：

```bash
ln -s ~/.agents /path/to/your-project/.agents
```

摘除时用 `rm /path/to/your-project/.agents`，**不要带尾斜杠**，否则会顺着链接删到这里的实体。

换机器或移动工作台目录后，外链会失效，重建一条即可。

## 版本控制

skill 文件就是工作台仓库的普通文件，跟着工作台一起提交，不需要单独操作：

```bash
cd /Users/bean/workspace/bean-workbench && make commit 说明改了什么
```

改动全局生效：所有读 `~/.agents` 的项目和工具都会看到最新版。只想在工作台内试的改动，用 `git stash push -- .agents` 暂存。

## 编号体系

编号规则、阶段划分和完整编号表见 `~/workspace/bean-workbench/AGENTS.md`。新增 skill 前先读那份文档，不要凭感觉起名。

## 本地配置

`.agents/local-config/` 是工作台统一的本机配置入口，由 `.gitignore` 中的 `local-config/` 规则排除。按能力建子目录，存放不能提交的凭证、机器配置与私有缓存。目录权限 700，敏感文件权限 600；说明和脱敏模板应放在受版本管理的 skill references 或工作台文档中，不把实际值写入记录。

公众号使用 `local-config/wechat/credentials`（AppID、AppSecret 两行）与 `local-config/wechat/token-cache/`。脚本按自身位置定位工作台配置目录，不依赖执行时的当前目录。仍支持环境变量与显式凭证文件覆盖。换机器需要单独配置这些本地文件，Git 不负责分发凭证。
