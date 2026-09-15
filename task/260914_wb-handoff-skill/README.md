# 任务交接 handoff skill

## 背景

会话中断后，下一个 agent 只能靠 `README.md` 和 git 记录猜进展，上下文反复重建。参考 [mattpocock/skills 的 handoff](https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff)（把当前会话压成交接文档），改成工作台自己的版本：交接文档不只给下一个 agent，还要**落在任务目录里跟着任务走**。

## 结论

- 新建 skill `wb-handoff`（wb 族不编号，直接 `wb-{能力}`）。
- 每个 `task/YYMMDD_{主题}/` 带一个 `handoff/` 目录，交接文档命名 `YYMMDD-HHMM_{slug}.md`，按名排序最后一份即最新。
- 与参考版的三处差异：存任务目录而非系统临时目录；加「下次建议调用的 skill」段（工作台有编号族群，能直接点名）；不复制已有产物，只给路径。

## 改动清单

| 文件 | 改动 |
| --- | --- |
| `.agents/skills/wb-handoff/SKILL.md` | 新增：触发条件、定位任务目录、写文件时机、命名、硬规则、接手侧用法 |
| `.agents/skills/wb-handoff/references/handoff-template.md` | 新增：文档骨架 + 字段说明 + 红线 |
| `AGENTS.md` | wb 表加 `wb-handoff`；命名规则加 wb 族例外说明 |
| `.agents/skills/wb-router/SKILL.md` | 路由表加 handoff 关键词行 |
| `task/registry.md` | 热任务登记 + 路由提示加 handoff 一条 |
| `script/check-workbench.py` | `REQUIRED_FILES` 加新 skill 的两个文件 |

## 验收

- `make check` 通过（必需文件 + skill 命名 + md 链接）。
- 目录名 / `SKILL.md` 的 `name` / 文档引用三者一致。

## 后续

- 老任务目录按需补 `handoff/`（不强制回补）。
