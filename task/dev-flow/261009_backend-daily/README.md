# 261009 backend-superone 日常开发

## 目标

集中承接 `backend-superone` 的日常开发需求，保持需求方案、实现过程、验证结论与交接上下文连续可查。

## 范围

- 业务仓：`business-repo/backend-superone`
- 按具体需求涉及的后端领域、数据库、API 与协议改动扩展范围。
- 方案与过程记录：本任务目录下的 `README.md`、`process/`、`handoff/`。

## 边界

- 本目录用于日常开发需求；已有明确独立目标的专项任务继续使用各自任务目录。
- 具体开发需求仍按 `dev-flow-0000-plan-flow` 产出并确认方案，再按涉及阶段派发；不因任务目录为日常入口而跳过阶段门禁。
- 未经明确需求，不改动其他业务仓；数据库变更按对应流程执行。

## 当前状态

进行中，作为 `backend-superone` 日常开发上下文入口。

## 沉淀候选

- 可复用的后端开发约定与排错结论沉淀至相关知识库。
- 稳定重复的流程可评估升级为 skill 或脚本。

## 后端接入第三个微信小程序

### 背景与需求理解

- 后端已有两个小程序的 `AppID → AppSecret` 映射，登录按请求中的 `app_id` 查找凭证；本次将这两个凭证与鹅懂个啥凭证统一迁入 `configs/config.yaml`。
- 初始化逻辑将配置注入现有映射，登录与 JWT 流程保持不变。

### 目标与边界

#### 本期目标

- 在 `configs/config.yaml` 的 `wechat_mini_programs` 中配置全部三个小程序凭证。
- 初始化时将配置项注入 `AppIdSecret` 映射；Go 常量中不再硬编码小程序凭证。
- 复用现有按 `app_id` 查找凭证、换取 OpenID 与生成 JWT 的登录链路。

#### 本期不做

- 不改登录 API、JWT 格式、数据库、OpenAPI 或客户端协议。
- 保持三个小程序凭证值与公众号凭证逻辑不变，仅调整小程序凭证的配置位置。
- 不执行部署或数据库操作。

### 改动范围

#### 涉及仓库

- `business-repo/backend-superone`
- 工作台方案与过程记录：本任务目录。

#### 涉及库表、接口与契约

- 无数据库、接口或契约改动；复用现有小程序登录接口。

### 实施方案

1. 在 `internal/infrastructure/config/define.go` 声明 `wechat_mini_programs` 配置映射。
2. 在 `internal/bootstrap/initialize/init_config.go` 将非空配置注入 `constant.AppIdSecret`。
3. 将三个小程序的凭证统一登记在 `configs/config.yaml`，从 `constant/system.go` 移除硬编码项。
4. 不改微信登录、UseCase、API、JWT 与公众号凭证逻辑。

### 验收标准

- 三个 AppID 均可通过现有映射找到对应凭证，并复用微信 code 换 OpenID 流程。
- 公众号凭证注入与行为不变。
- 后端相关测试通过。

### 测试方案

| 场景 | 预期 |
| --- | --- |
| 三个小程序分别登录 | 后端按 AppID 使用对应凭证向微信换取 OpenID |
| 公众号凭证使用 | 原有公众号凭证注入与行为不变 |

### 风险与回滚

- 若某个小程序配置缺失或为空，该 AppID 无法完成登录；回滚时将凭证映射恢复到常量并移除配置注入即可，不涉及数据迁移。

### 落地记录

- 已将全部三个小程序凭证迁入 `configs/config.yaml`，并由初始化逻辑注册到现有映射；`constant/system.go` 中的小程序映射已清空。
- 已运行 `gofmt`；未运行测试或构建。
