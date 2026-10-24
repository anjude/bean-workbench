# 工作台工具

| 工具 | 职责 | 入口 |
| --- | --- | --- |
| [来源采集器](source-collector/README.md) | B 站与 YouTube 字幕、音频转写、来源包和任务管理 | `hr collect` |
| [浏览器采集插件](source-collector-extension/README.md) | Chrome 内批量采集 B 站字幕并导出 ZIP | 加载该目录的 `dist/` |

工具源代码由工作台管理；虚拟环境、媒体、数据库和构建产物不进入 Git。业务仓消费标准资料，保持各自的业务职责。
