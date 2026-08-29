# 工作台自进化工作流

## 目标

把使用过程中反复出现的问题转化为工作台能力。

## 流程

1. 将问题记录到 `task/pain-points.md`。
2. 判断问题类型：意图识别、路由、知识缺口、流程缺口、脚本缺口。
3. 临时问题更新 `task/registry.md`。
4. 稳定知识写入 `knowledge-base/`。
5. 稳定流程升级为 `~/.agents/skills/`；流程中用到的模板和清单，放进该 skill 的 `references/`。
6. 重复命令或机械操作升级为 `script/` 或 `Makefile`。

skill 实体在工作台仓库的 `.agents/skills/`，随工作台一起提交；`~/.agents` 是指向它的外链，供其他 Agent 工具和其他项目读取。工作台的 `make check` 会列出 `.agents/` 下未提交的改动，也会检查外链是否还在。
