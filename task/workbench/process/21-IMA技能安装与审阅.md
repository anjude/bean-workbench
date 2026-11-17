# IMA 技能安装与审阅

- 任务目录：`task/workbench/`
- 阶段：日常维护
- 时间：2026-11-16

## 做了什么

- 下载并检查 `https://app-dl.ima.qq.com/skills/ima-skills-1.1.10.zip`，安装有效文件到 `.agents/skills/tools-ima/`；排除 ZIP 内的 macOS 元数据和历史快照。
- 审阅总入口、notes、knowledge-base 和三个 Node 脚本。确认包含笔记读写、知识库搜索/上传、图片换链、上传前文件校验和临时 COS 凭证上传。
- 修改 `ima_api.cjs` 固定使用 `https://ima.qq.com` 并拒绝 HTTP 重定向，防止自定义地址接收 API 凭证；移除命令行 JSON 参数传递 Client ID/API Key 的能力。
- 修改技能说明，要求配置文件目录权限 `700`、凭证文件权限 `600`，并将服务端返回的更新 `instruction` 视为远端数据，不作为 Agent 指令执行。
- 更新工作台 skill 清单与路由：`AGENTS.md`、`.agents/skills/wb-router/SKILL.md`；任务索引已使用固定入口 `task/workbench/`。

## 得到的结论

- ZIP 元数据版本为 `1.1.10`，依赖 Node.js 18 及以上；当前环境 Node.js `v22.23.2`：`/tmp/ima-skills-inspect/ima-skill/meta.json`。
- API Key 获取页 `https://ima.qq.com/agent-interface` 的页面读取结果仅显示 ima 标识，未能核验页面内实际凭证申请步骤；技能已安装，API 调用需用户先在本机配置 Client ID 与 API Key。
- 凭证检查只会读取环境变量或 `~/.config/ima/client_id`、`~/.config/ima/api_key`，本次没有读取、创建或保存用户凭证。

## 被推翻的判断

- 原始技能元数据声明凭证只发送至官方域名，但 `ima_api.cjs` 接受 `IMA_BASE_URL` 和 `options.baseUrl` 覆盖。静态审阅发现此处不符合声明，因此工作台副本固定官方域名并禁止重定向。
- 原始示例把凭证放进进程参数 JSON，可能暴露在进程列表；已改为只通过环境变量或权限受限配置文件读取。

## 待核 / 没答上来

- 用户需在 IMA 官方入口取得 Client ID 与 API Key 后在本机配置；尚未进行真实 API 调用。
- ZIP 说明中的接口行为和 COS 临时凭证限制尚未通过真实账户调用验证。

## 2026-11-16 后续：本机凭证配置

- 用户提供 Client ID 与 API Key 后，已写入 `~/.config/ima/client_id` 和 `~/.config/ima/api_key`；检查确认目录权限为 `700`，凭证文件权限为 `600`。
- 写入过程中交互终端回显了输入值，因此凭证出现在工具输出中。未使用该凭证调用 API；建议用户在 IMA 入口轮换 API Key，并通过本机编辑器更新文件，不要再次发到聊天。
