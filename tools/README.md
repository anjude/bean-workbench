# 工作台工具

| 工具 | 职责 | 入口 |
| --- | --- | --- |
| [来源采集器](source-collector/README.md) | 本地视频转写、B 站/YouTube/小红书及 yt-dlp 可访问公开视频的字幕、来源包和任务管理 | `hr collect` |
| [浏览器采集插件](source-collector-extension/README.md) | Chrome 内批量采集 B 站字幕并导出 ZIP | 加载该目录的 `dist/` |
| [投资分析 MVP](investment-analysis/README.md) | 当前仓位、价格与事件、开仓/roll/平仓情景及决定记录 | `python3 tools/investment-analysis/investment.py report` |
| [小红书研究工具](xhs-research/README.md) | MediaCrawler 小规模公开内容学习采样；XHS-Downloader 保存人工挑选的作品素材 | 按子目录 README 分别安装和运行 |

工作台自有工具源代码由工作台管理；第三方源码以独立 Git 子模块保留上游版本和 LICENSE。虚拟环境、媒体、数据库和构建产物不进入 Git。业务仓消费标准资料，保持各自的业务职责。
