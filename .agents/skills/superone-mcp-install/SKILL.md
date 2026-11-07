---
name: superone-mcp-install
description: 为用户扫码登录并在 Codex 中配置 Superone 远程 MCP；用于首次接入、重新授权或排查连接。不会自动创建、更新或发布远端 Skill。
---

# Superone MCP 接入

帮助用户把 Superone 远程 MCP 配置到本机 Codex，并确认工具可用。优先读取用户给出的安装说明页，按页面提供的服务地址和环境参数操作；不要把测试地址、生产地址或小程序版本参数写死。

## 登录与凭证

1. 从安装说明页确定 HTTPS 服务地址。创建扫码会话时生成新的 `unique_id` 与高熵 `secret`，请求 `/api/so/user/code` 并设置 `scene=mcp`。只有测试页明确要求时才传 `env_version=trial`。
2. 在对话中展示返回的二维码，让用户用微信扫码确认。轮询 `/api/so/user/get_jwt` 时使用同一 `code` 和 `secret`；遵守接口的一次性领取约束。用户没有确认前等待，不代替用户扫码或确认。
3. 不在对话、日志、命令回显或 Skill 内容中输出二维码会话密钥和 JWT。领取后保存到本机权限受限的凭证文件（macOS 使用目录 `700`、文件 `600`），不得提交到 Git。
4. 凭证只用于请求 `Authorization: Bearer <jwt>`。遇到过期、无效或领取失败时，说明错误阶段并重新发起扫码；不要复用或公开旧令牌。

## 配置 Codex

为 Streamable HTTP 服务配置 `/api/so/mcp/transport`。优先使用 Codex 支持的 `http_headers_helper`，让本机 helper 从权限受限的凭证文件读取 JWT 并输出 JSON 字符串对象，例如 `{"Authorization":"Bearer …"}`。验证 helper 输出是合法 JSON，且不打印令牌到终端。不要把 JWT 直接写进 `config.toml`、项目文件或命令参数。

可使用 Codex CLI 添加服务，再在对应 `[mcp_servers.<名称>]` 表中设置 helper：

```sh
codex mcp add superone --url 'https://服务地址/api/so/mcp/transport'
```

helper 必须是本机命令；只有本地 Codex 客户端支持 `http_headers_helper` 的连接方式才使用它。保存配置后启动新的 Codex CLI 会话或按客户端能力刷新连接。

## 验证与失败处理

1. 先确认配置中的服务地址、helper 路径和凭证文件权限，不打印凭证内容。
2. 使用 Codex 客户端验证 MCP 初始化和工具发现。应看到 `list_skills`、`get_skill`、`save_skill`、`delete_skill` 和组织工具。
3. 用 `list_skills` 指定 `category=personal` 做只读验证并报告数量。不要为了验收创建测试 Skill、覆盖现有 Skill 或调用写入工具，除非用户明确要求。
4. 如果 Codex 报 `invalid Host header` 或握手失败，保留错误摘要，检查客户端与服务端实际返回；不要未经授权改代理、Host 校验或服务端部署配置。
5. Windows、其他 Agent 客户端及不同安装环境按安装页和对应客户端文档适配；未实际验证的平台要明确标为未验证，不照搬 macOS 路径。

## 同步 Skill

只有用户明确要求保存或同步时，才调用 Superone MCP 的 `save_skill`。写入前用 `list_skills` 按目标分类确认名称；存在同名 Skill 时按 `skill_id` 调用 `get_skill` 比较内容，只有用户授权更新时才传 `skill_id`、当前 `revision`、目标分类及完整文件包。组织分类还需传 `organization_id`。上传只包含用户选定的 Skill 文件，不包含凭证、机器配置或临时登录文件。保存后核对服务返回的名称、摘要和版本。
