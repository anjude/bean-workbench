# skill 沉淀与归档清理 · 过程记录

- 任务目录：`task/dev-flow/261017_beannote-daily/`
- 阶段：02 skill 沉淀与归档清理
- 时间：2026-10-17

## 做了什么

- 新建 `.agents/skills/bn-tools-publish-flow/`，只总结编写-排版-发布的机械链路，不含内容与风格规则
- 同步引用：AGENTS.md bn 节、docs/workspace.md、wb-router beannote 路由行、task/registry.md、.workbuddy/memory/MEMORY.md；`make check` 通过
- 用户删除 `.agents/archive/`（bn 两代归档 skill + trash 旧内容）后，清理残留引用：AGENTS.md（归档表与指针）、.agents/README.md（归档段，目录树补 bn-tools-*）、wb-router references 表、task/beannote/README.md、本任务 README（回迁议题作废）

## 得到的结论

- 命名走 `bn-tools-*` 工具层：发布链路在任何选题内容定稿后被调用，不专属 bn 00/01/02 内容阶段，符合「横切能力建工具 skill」规则
- bn 族复活只复活机械层：两代归档的教训是 skill 一写细就变成流程、agent 替用户做内容取舍；`bn-tools-publish-flow` 明确只写工具命令与排障，边界写进 skill 第六节
- 归档删除后的引用清理分三类：活跃指针（删）、历史任务文档与历史日志（按约定留旧名）、今日日志（只增不改，追加更正条目）

## 被推翻的判断

- 初判新 skill 应占 bn 阶段编号（如 `bn-02xx`）→ 阶段号语义是内容决策回合，与机械链路错位，改用工具层
- 初判 archive 删除后「旧内容回迁范围」议题继续有效 → 目录已删，议题作废，旧内容仅存 git 历史（commit `b15dfd7`）

## 待核 / 没答上来

- 无
