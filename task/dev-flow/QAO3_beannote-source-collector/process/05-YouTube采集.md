# YouTube 采集支持

## 需求和方案

用户要求在 beannote 采集工具中增加 YouTube，并给定 `https://www.youtube.com/watch?v=qU3fmidNbJE` 实测。工作台新增 `hr collect youtube <链接或ID>`；Python 用 yt-dlp 适配平台信息、JSON3 字幕和音频，共用既有队列、MLX、来源包与主题归档。

参考：[yt-dlp 官方嵌入说明](https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp)。只处理单视频，链接附带播放列表也不扩展成整表采集；直播需等待完成后采集。

## 改动

- Go：统一生成 B 站和 YouTube 子命令，透传平台、模型及 `--retry`；实际运行失败不再打印整段 usage。
- Python：新增 YouTube 适配与平台路由，数据库已有 platform 字段作为去重维度，无需迁表。网页接受混合平台输入。
- 字幕：优先上传字幕，其次原语言自动字幕，跳过机器翻译轨；自动字幕标为 `platform_ai`、需复核。无字幕或字幕读取失败时进入音频和 MLX 分支。
- 来源包：YouTube 文件夹带平台前缀，元数据剔除内部 yt-dlp 信息；B 站已有资料包与音频缓存命名保留。
- 依赖：新增 `youtube` extra，本机 `.venv-asr` 已安装 yt-dlp 2026.10.21 和默认依赖；使用现有 Node 22 解析 YouTube 脚本。
- 登录：默认匿名；显式设置 `BEANNOTE_YOUTUBE_COOKIES_FILE` 时才读取该 Netscape Cookie 文件。没有浏览器凭据自动读取。受限任务可重试，不输出空资料包。

## 检查结果

- 17 项 Python 单测通过：原有 9 项 B 站/导入/归档回归，新增 8 项覆盖 YouTube 输入、字幕时间轴、去重、自动字幕标记、原语言过滤、ASR 回退、空转写、访问限制。
- `go test ./cmd/...` 通过，`make install` 成功。
- 从 `/tmp` 执行 `hr collect youtube`，确认安装后的命令可找到采集器。
- 真实样本读到标题《AI Agents Fundamentals In 21 Minutes》和作者 Tina Huang；YouTube 返回 “Sign in to confirm you’re not a bot”。首轮失败后用 `--retry` 复测，状态为 `login_required`、退出码 1、result_path 为空；没有重复任务或空资料包。
- 该样本任务 ID：`54c2dd59-6914-4c03-9bb6-a8c331ba8a0e`，保留在本机 SQLite。

## 当前边界与下一步

真实 YouTube 字幕或音频的成功采集尚未通过当前网络验证；自动化测试使用受控数据，不能替代真实链路成功。用户可提供自己的有效 Cookie 文件并用 `--retry` 重新采集，平台仍可能要求额外验证。默认 large-v3-turbo 模型权重下载问题沿用此前限制；本轮传 Tiny 仅作备用链路验证，实际未进入转写。

旧网页服务需要重启才加载新代码。本轮没有自动修改任何内容主题，也没有提交或推送代码。
