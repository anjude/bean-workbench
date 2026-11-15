---
name: tools-backend-auth
description: 使用 backend-superone 的环境配置为已授权操作生成短时 JWT，并安全调用 test 或 live API。
---

# backend-superone 环境鉴权

当用户明确授权调用 backend-superone 的 test/live API，或已授权的专项 skill 明确需要接口操作时使用。环境配置位于 `business-repo/backend-superone/configs/`；只有本 skill 的 helper 读取其中的 JWT key 和 Gknow AppID。

## 授权与边界

- 每次确认目标环境。调用 live 写接口必须有覆盖该 live 操作的明确授权；test 与 live 凭证不能互换。
- 只向 `https://api.beanflow.top:8080`（test）或 `https://api.beanflow.top`（live）发送请求；helper 只接受 `/api/so/` 相对路径，禁止重定向。
- JWT 默认 15 分钟，仅在内存中签发和使用；禁止打印、落盘、写入命令参数、日志、过程记录或 Git。响应输出会对 token、secret、password 等字段脱敏。
- 管理员 claim 默认关闭。创建、更新、发布等管理员操作须经用户授权，并显式使用 `-admin`；JWT 只使用配置中的 `app.gknow_app_id`，不可为其他 App 生成。
- OpenID 从权限受限的本地文件读取，不放在命令参数或内容仓。确有需要时生成临时文件，用完立即删除。
- 不用配置里的 AppSecret 生成 JWT。微信 AppSecret 只用于对应微信登录或服务流程，不是后端 JWT 签名密钥。

## 调用

从 `business-repo/backend-superone/` 运行 helper。live 合并读取 `configs/config.yaml`；test 先读同一基础文件，再合并 `configs/config.test.yaml`，遵循后端当前加载规则。配置文件必须在本机，不得在终端输出配置值。

```bash
go run /Users/bean/workspace/bean-workbench/.agents/skills/tools-backend-auth/scripts/with_auth.go \
  -env live -admin -openid-file /secure/path/openid.txt \
  -method POST -path /api/so/gknow/assessment/list \
  -body-file /secure/path/request.json
```

- `-env` 必须显式指定 `test` 或 `live`。
- `-admin` 默认关闭；仅用户授权的管理员 API 操作才启用。
- `-method` 只接受 GET 或 POST；需要 JSON 请求体时用 `-body-file`。
- 图片上传可将 `-upload-file` 与 `POST /api/so/common/wx_upload` 配合使用，文件作为 multipart `file` 字段发送；不与 `-body-file` 同时使用，单文件上限 4 MiB。
- helper 返回 HTTP 状态和脱敏后的 JSON 响应，不返回 JWT。
- 写入后用详情或列表接口回读核对 key、版本、状态和内容；不因 HTTP 200 单独判定成功，需检查业务 `err_code`。

此工具只负责环境鉴权与 API 传输；内容编写、配置格式和发布验收由对应业务 skill 负责。
