# 261017 beannote 日常维护

## 目标

集中承接 beannote 的日常开发维护需求，让每项改动的方案、过程、验证和交接有持续可查的入口。

## 范围

- 内容与工具仓：`task/beannote`，包括内容生产辅助工具、各平台发布能力及相关文档。
- 任务记录：本目录的 `README.md`、`process/` 和 `handoff/`。
- 具体需求涉及其他仓库时，再按实际依赖确定影响范围。

## 边界

- 本目录承接 beannote 的日常开发维护；明确独立目标的专项开发可另建任务目录。
- 文章、笔记等内容主题放在 `task/beannote/topics/`，按主题目录绑定会话，不在本目录记录创作过程。
- 具体开发需求仍先形成方案，再按适用阶段实施并验证。当前只建立维护任务上下文，尚无具体开发项或代码改动。

## 当前状态

进行中。已装公众号排版与发布两个 skill：`oa-wechat-formatter`（Markdown → 微信兼容 HTML 三件套，含敏感词扫描）、`wechat-oa-publisher`（自备 AppID/AppSecret 走官方 API，草稿箱 + 群发）。链路跑通并稳定后，按本仓 README 约定沉淀为 `task/beannote/script/` 下按平台隔离的发布代码。待具体维护需求。

发布链路当前阻塞在微信侧 IP 白名单：凭证已配到 `~/.wechat_pub_key`（来源 `business-repo/backend-superone/configs/config.yaml` 的 `wechat_mp_config`），token 验证返回 `40164`，需在公众平台基本配置里把出口 IP `58.251.160.140` 加进白名单。

**2026-10-17 21:30 更新**：IP 白名单已加并生效，`publish.py token` 验证通过，排版 → 草稿箱链路就绪。经验：本机代理按目标主机粘住出口 IP，微信 API 固定从 `58.251.160.140` 出（ipify 等站点显示的是另一个出口 `103.135.104.236`，查 IP 别用通用回显站，以微信报错里的 IP 为准）。

**2026-10-17 21:48 更新**：首篇完整跑通「改稿 → 排版 → 封面 → 草稿箱」全流程（选题「复利的临界点」，`task/beannote/topics/2026-10-17_复利的临界点/`）。两个排障结论：① draft/add **必须带 thumb_media_id**，缺封面报 `40007 invalid media_id`（与内容无关）；② 封面走 ImageGen 生成 → sips 裁 2.35:1（切 AI 水印）→ 上传素材库。

**2026-10-17 21:55 更新**：发布链路经验沉淀为 skill `bn-tools-publish-flow`（`.agents/skills/`，工具层，只管流程不碰内容取舍）；AGENTS.md、docs/workspace.md、wb-router、task/registry.md、长期记忆已同步，`make check` 通过。待办：素材上传仍靠一次性脚本，稳定后并入 `task/beannote/script/` 或给 `wechat-oa-publisher` 补能力。

另有一项待拍板：`task/beannote` 新目录骨架已建但未提交。原「`.agents/archive/trash/` 旧内容回迁范围」议题随归档目录于 2026-10-17 删除而作废，旧内容仅存于工作台 git 历史（commit `b15dfd7`），需要时可按需取回。

## 沉淀候选

- 稳定可复用的平台发布接入经验和内容工具约定，可整理到知识库或脚本。
