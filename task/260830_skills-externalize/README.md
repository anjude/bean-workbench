# 260830 skill 跨项目共享

## 目标

让工作台里的 skill 能被其他项目和其他 Agent 工具读到，同时**保留工作台对 skill 的版本管理**。

## 背景

skill 原先只在 `bean-workbench/.agents/skills/` 下，只有工作台自己能用；其他项目要复用，要么复制一份（之后必然分叉），要么手工拷路径。

## 最终方案

skill 实体留在工作台仓库里，不做独立仓库。`~/.agents` 是指向工作台 `.agents` 的**外链**，多数 Agent 工具会直接读 home 目录下的 `.agents`，所以外链在就够，其他项目什么都不用做。

```bash
ln -s /Users/bean/workspace/bean-workbench/.agents ~/.agents
```

某个项目想在仓内目录也看到，再建 `ln -s ~/.agents <项目根>/.agents`。摘除用 `rm <项目根>/.agents`，不要带尾斜杠。

## 走过一次弯路：方向建反了

第一版做成了实体在 `~/.agents`、工作台 `.agents` 是指向它的链接，还给 `~/.agents` 单独 `git init`。这是错的：

1. **把 skill 从工作台版本管理里挖走了**。工作台 git 索引里 32 个文件条目变成 1 行 symlink（模式 `120000`），`make commit` 带不走 skill 改动，每次改完还得记得去另一个仓库单独提交。
2. **没解决任何实际问题**。用户要的只是「其他项目能读到」，一条外链就够了，不需要把实体搬出仓库。

已改回：实体在工作台，外链在 home。工作台索引恢复为 33 个普通文件条目（32 个 skill 文件 + `.agents/README.md`）。

教训：**「把目录链接到 ~」不等于「把实体搬到 ~」**。目标是让别人能读到，不是把文件挪走；挪走实体等于放弃版本管理。

## 范围

- 实体：`bean-workbench/.agents/`，由工作台 git 跟踪。
- 外链：`~/.agents -> bean-workbench/.agents`（home 目录不受版本控制，换机器重建一条即可）。
- 脚本：`script/check-workbench.py` 结尾提示区改为「skill 共享与版本状态」，检查外链是否缺失 / 指向别处 / 被换成真实目录，并列出 `.agents/` 下未提交的改动。
- 文档：`AGENTS.md` 的「跨项目共享」小节、`README.md`、`docs/workspace.md`、`docs/self-evolution.md`、`.agents/README.md` 全部按新方向改写。
- skill 正文：`wb-0001-router`、`wb-0101-skill-refactor` 及其 references 里「单独提交」的说法去掉，路径保留 `~/.agents/skills/`（穿透外链有效，跨项目读得到）。

## 边界

- 不改动 `business-repo/` 下任何业务仓；业务仓是否接入链接由用户决定。
- 不动 `~/.workbuddy/skills/`（WorkBuddy 用户级目录）。WorkBuddy 不读 `~/.agents`，需要它自动加载时再考虑挂 router 进去。

## 踩坑

- **`Path.rglob` 不进入符号链接目录**。只要 `.agents` 或其子目录是链接，链接检查就会空转——放进 `.agents` 里的坏链接一个都检不出来，还显示「通过」。必须自己写递归遍历跟随链接，用 real path 集合防循环。改完做负向测试确认能报出来。
- **外链异常要单独报**。链接断了以后，必需文件检查只会列出一串「文件缺失」，看不出根因。
- **遍历只覆盖工作台内部**。从工作台根开始遍历不会经 `~/.agents` 绕回来，脚本改完后要确认没有把 home 目录整个扫一遍。

## 当前状态

已完成。`make check` 三项通过；负向测试覆盖 skill 命名错、skill 文档坏链接、外链缺失、外链指向别处、外链被换成真实目录五种情况，均按预期报出。

## 后续

- 其他项目接入或业务仓接入待用户决定。
- 换机器后重建外链：`ln -s /Users/bean/workspace/bean-workbench/.agents ~/.agents`。
