# 小红书工具资料

本页记录 2026-10-31 核对到的 GitHub 项目情况。上游会更新，启用前重新核对 README、LICENSE、发行包与安全说明。

## MediaCrawler

- 仓库：[NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler)
- 能力：关键词搜索、指定笔记采集、评论/二级评论、创作者主页等；支持多种存储格式，包括 CSV、JSON、JSONL、Excel、SQLite 和 MySQL。
- 最近可见提交：2026-10-27 更新 README。
- 工作台子模块：`tools/xhs-research/MediaCrawler/`，当前固定提交 `68d9ef1`。
- 许可证：仓库自带「非商业学习使用许可证 1.1」，仅限非商业学习研究，禁止大规模采集或扰乱平台运营；商业用途须取得版权方书面同意。
- 如果研究结果会直接用于商业营销活动，先向版权方确认该用途是否需要书面许可。
- 运行方式：基于 Playwright 浏览器自动化并使用登录态；只在用户明确要求采集且核对当前规则后运行。不要保存登录态、Cookie 或账号凭证到工作台仓库。

## XHS-Downloader

- 仓库：[JoeanAmier/XHS-Downloader](https://github.com/JoeanAmier/XHS-Downloader)
- 能力：从作品链接提取作品信息、下载图文/视频文件，支持命令行、API 和 MCP；作品数据可保存到本地文件/SQLite。
- 最近可见提交：2026-10-18。
- 工作台子模块：`tools/xhs-research/XHS-Downloader/`，当前固定提交 `2ab2620`。
- 许可证：GPL-3.0。
- 适用方式：运营者先人工选链接，再单条保存作为版式/视觉研究样本。项目的代理配置只用于用户有权配置的网络环境，不作为绕过平台限制的手段。

## xiaohongshu-cli

- 仓库：[Apageoflove/xhs-cli-xiaohongshu](https://github.com/Apageoflove/xhs-cli-xiaohongshu)
- README 宣称：笔记/评论读取、搜索和数据分析，以及点赞、收藏、评论、回复、发帖、删除等账号操作；还宣称使用反检测策略。
- 最近可见提交：2026-05-19。
- 许可证：当前仓库未找到 LICENSE 文件；README 的源码构建示例还指向另一个仓库名。
- 结论：暂不把源码复制到工作台，也不通过它操作账号。其 README 未说明可写入官方草稿箱的专用流程；“发布”命令不能等同于“预发布草稿”。如果希望采用，先取得仓库作者的使用/分发许可并验证是否支持官方草稿箱。
