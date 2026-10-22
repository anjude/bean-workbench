---
name: bn-tools-publish-flow
description: 公众号素材上传、草稿箱、发布提交与结果查询工具。用于把已确认排版稿入草稿箱、按用户授权公开发布、记录回执或排查接口错误；全部执行代码随 skill 纳入工作台。
---

# 公众号发布

输入为主题内已确认的稿件与排版 HTML；排版见 `bn-tools-format-flow`，辅助编辑见 `bn-tools-edit-flow`。执行入口 `scripts/publish.py` 仅依赖 Python 标准库。命令在工作台根目录执行，`TOPIC` 指当前选题目录。

## 凭证

优先环境变量 `WECHAT_APPID` / `WECHAT_APPSECRET`，否则读工作台 `.agents/local-config/wechat/credentials`（两行，AppID、AppSecret，权限 600）。可用 `WECHAT_KEY_FILE` 指定受限文件。不要从业务配置整份复制凭证，不把密钥、token 写入文档或 Git。

```bash
python3 .agents/skills/bn-tools-publish-flow/scripts/publish.py token
```

验证命令只报告成功。token 按账号隔离缓存到 `.agents/local-config/wechat/token-cache/`，文件权限 600；本地配置目录由 Git 忽略，不依赖 home 密钥或 /tmp 缓存。当前凭证对应的公众号尚须后台确认，实际写入前核对目标账号。

## 上传与草稿

```bash
python3 .agents/skills/bn-tools-publish-flow/scripts/publish.py upload "$TOPIC/publish/cover.jpg" --kind cover
python3 .agents/skills/bn-tools-publish-flow/scripts/publish.py upload "$TOPIC/publish/body-image.jpg" --kind body
python3 .agents/skills/bn-tools-publish-flow/scripts/publish.py draft \
  --title "标题" --content-file "$TOPIC/publish/article_wechat.html" \
  --digest "有吸引力的导读文案" --thumb-media-id "封面素材ID" \
  --receipt "$TOPIC/publish/draft-receipt.json" --dry-run
```

已存在草稿时，先用 `draft-get --media-id "草稿ID"` 查询；需要替换其中一篇时用 `draft-update --media-id "草稿ID" --index 0`。更新操作也先 dry-run 核对 payload，再使用新的回执路径执行。不要因更新后的回执或封面素材 ID 变化而新增重复草稿。

草稿字段：`title`、`content`、`thumb_media_id` 必填；`author` 默认「豆小匠」；`digest` 必须提供有吸引力的导读文案，不要求复述全文；`need_open_comment` 默认 `1`（开启评论），`only_fans_can_comment` 默认 `0`（不限粉丝），均可用 CLI 显式覆盖。接口开关字段按数字 `0/1` 传入。`--receipt` 与 `--dry-run` 是本地执行控制，不属于文章字段。

封面返回 `media_id`，正文图返回 URL；正文 URL 回填后重排版。核对 dry-run payload 后，已有用户入草稿箱授权即可去掉 `--dry-run` 执行。没有授权时先交付本地预览。`draft/add` 的官方字段表没有原创声明字段，不向请求中添加未公开字段；需要声明原创时在公众号后台处理并核验。

脚本在写请求前独占创建回执；同一路径已有回执就拒绝重复提交。请求超时、失败或进程中断留下 pending 时，先核对后台，不自动重试；新回执文件名也不能代替后台核对。素材上传也不会自动重试，手工再次执行前先查是否已成功。

`draft/add` 与 `draft/update` 会把当时提交的标题、正文 HTML 和封面保存为平台端稿件快照。之后修改 `发布稿.md` 或重新生成本地 HTML 不会自动更新已有草稿，也不会更新其定时发布安排。先用 `draft-get` 核对指定 media_id；存在差异时用 `draft-update` 更新并再次读取复核，再排期。只有确认目标草稿不存在或无法继续使用时，才新增草稿；遇到无效 media_id 时先检查后台状态，避免重复草稿。

## 公开发布与状态

```bash
python3 .agents/skills/bn-tools-publish-flow/scripts/publish.py publish \
  --media-id "草稿ID" --receipt "$TOPIC/publish/publish-receipt.json" --dry-run
python3 .agents/skills/bn-tools-publish-flow/scripts/publish.py status --publish-id "发布任务ID"
```

公开发布须有用户对该稿件的明确发布授权；已有授权继续执行，无须逐步重复确认。接口权限以账号实际开通能力和响应为准，不按订阅号/服务号名称直接推断。`freepublish/submit` 是发布提交接口，不等同于向全部粉丝发送消息；返回 `publish_id` 只表示已受理。查询成功后再记录实际文章链接、时间和最终状态。无接口权限时交付草稿，由后台完成。

通过公众号后台设置的定时发布属于平台端操作，不是当前脚本能力。记录已设置状态及可获得的计划时间、任务标识，并区分“已排期”和“已发布”；计划时间到达后再核对平台执行结果，成功后补文章链接和实际发布时间。

## 记录与排障

主题 `发布记录.md` 写明目标平台/账号（不写密钥）、标题、所用发布稿、HTML 和封面路径、素材 ID、草稿 ID、发布任务 ID、最终链接及结果。状态区分本地预览、已入草稿、已提交发布、已发布、失败或结果未知。回执 JSON 作为平台返回依据。

排障见 [接口排障](references/troubleshooting.md)。每个稳定的新问题更新本 skill 或 reference；不要只留在单篇文章记录里。

完整模式、生产步骤、状态与二次开发边界见 [生产发布流程](references/production-flow.md)。需要理解或开发整条链路时读取。
