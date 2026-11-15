# Superone MCP 操作 Skill

## 目标

为 Superone MCP 的个人日常操作提供明确入口，用户可用「so」唤起。

## 完成内容

- 新增 `.agents/skills/tools-superone/SKILL.md`，覆盖 Skill 列表、读取与上传/更新，近期任务查询，以及清单创建、编辑、执行和历史读取。
- 明确本地 Skill 编辑与远端上传是不同操作；远端同名 Skill 未经明确授权不得覆盖，删除 Skill 只接受明确指向的删除要求。
- 明确清单本身当前没有删除工具；只有清单执行记录支持删除。
- 根据后端常量和 DTO 定义记录执行模式与状态：模式 1/2 分别为正常/分步执行，状态 1/2 分别为进行中/已完成。时间使用 Unix 秒。
- 在 `AGENTS.md`、`task/registry.md`、`.agents/README.md` 增加清单和路由；在 `script/check-workbench.py` 登记必需文件并允许 `tools-superone` 命名。

## 验收记录

已对照当前可用 Superone MCP 工具定义确认工具名称和能力范围，并对照 `business-repo/backend-superone/constant/checklist.go`、清单执行 DTO 确认执行值。清单删除能力不存在，技能据实说明。未调用远端写工具；本次仅新增本地 Skill 与索引。
