# 微信防撤回 skill 内化

## 变更

- 将 `~/.workbuddy/skills/wechat-anti-revoke/SKILL.md` 的本机流程整理到 `.agents/skills/wb-wechat-anti-revoke/SKILL.md`，统一目录名与 frontmatter 名称。
- 补充安装前按版本和 build 备份、跳过会整包删除重打包的 provenance 步骤、区分核心 hook 与高开销消息监听、按同 build 回滚等约束。
- 更新 `AGENTS.md`、`task/registry.md` 和 `wb-router` 路由，确保提到微信防撤回时能找到该 skill。

## 本机验证记录

当前安装日志识别到微信核心版本 `4.2.0 (build 270350)`，特征码搜索命中并报告 `arm64 trampoline 安装成功`、`就绪，等待撤回消息`。应用包版本字段显示 `4.1.15 (build 270135)`；skill 已记录两者差异，后续以运行时 hook 日志核实实际适配状态。

本次核心 hook 安装前的原始主程序备份为 `/Users/bean/WeChatBackup/WeChat-4.1.15-270135-original`；`restore.sh` 已指向该备份，旧回滚脚本另存为 `restore-legacy-4.1.11.sh`。
