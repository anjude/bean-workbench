---
name: tools-image-upload
description: 通过工作台接入的后端上传本地图片并取得 HTTPS URL；用于测试、页面或其他内容的图片素材，不负责生成图片、发布内容或承诺图床长期可用。
---

# 图片上传

把已准备好的本地图片上传到后端，返回可写入配置的 HTTPS URL。当前适配器调用 `POST /api/so/common/wx_upload`，由后端上传到微信图床；本能力可跨任务使用，但存储提供方目前只有这一种，不把 URL 当成任何平台均可长期访问的保证。

## 使用

1. 确认图片的用途、目标环境和目标账号。图片生成使用 `imagegen`，裁剪和压缩按目标项目的尺寸、比例、透明度及清晰度要求处理；保留原图，使用处理后的副本上传。本 skill 不自动生成、裁剪或压缩图片。
2. 凭证从 `.agents/local-config/image-upload/admin.jwt` 读取，或通过 `--token-file` 指向权限受限的文件。目录权限 700、凭证文件权限 600；不在日志、文档、命令参数或 Git 中记录 token。凭证对应的 AppID 和环境须符合目标用途，不从是否返回成功推断账号一致。
3. 用户已经授权上传或上传属于当前授权任务的必要步骤时，明确选择 `test` 或 `live` 后执行：

```bash
python3 .agents/skills/tools-image-upload/scripts/upload.py /absolute/path/image.png --env test
```

输出 JSON 包含 `environment` 和 `url`；接口按 multipart `file` 上传，脚本检查 HTTP、业务返回码及 HTTPS URL。支持 PNG、JPEG、GIF、WebP，工具本地上限 10 MiB，实际服务器和微信端支持范围以验证结果为准。脚本使用随机安全文件名、不自动重试、不跟随重定向。遇到超时等结果不明时，先核对已有回执或服务状态再决定是否重传。

4. 将 URL 用于配置或内容前，按实际用途验证读取、目标客户端及域名许可；需要 Canvas、分享卡、公众号正文或长期引用时分别验证。HTTP 能下载不代表这些场景或长期访问均已通过。失败时保留本地素材，说明失败步骤，不编造 URL。

## 账号与环境

`test` 为 `https://api.beanflow.top:8080`，`live` 为 `https://api.beanflow.top`。当前 test 已验证接口上传成功且普通 HTTP 下载的内容与原图一致；所用凭证 AppID 与鹅懂个啥不同，目标小程序、海报、分享与长期可用性未验证。公众号封面或正文的微信专属上传、发布及素材回执仍由 `bn-tools-publish-flow` 负责。
