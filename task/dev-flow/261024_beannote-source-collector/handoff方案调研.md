# 本地信息源工具方案调研

- 日期：2026-10-24
- 任务：`task/dev-flow/261024_beannote-source-collector/`
- 范围：审视 `handoff/261024-2215_本地信息源工具方案确认.md` 的本地工具方向，与公开开源实现比较。此文是技术调研，不代表开始实现或已完成性能验证。
- 插件状态：已交付 Chrome 插件继续保留，可作为已有工作流与页面辅助入口；本调研不删除、不改造插件。

## 判断

本地工具方向更贴合“批量收集、长期保存、后续整理和重新处理”的目标。插件已满足直接从 Chrome 批量获取和导出的场景，保留它可以覆盖轻量、临时使用；两者可以并存。暂时不必把浏览器扩展重新设计成本地工具的唯一入口。

原方案的主要方向合理，但几个边界应收紧：先把首版定义为 B 站视频的可追溯采集与转录；不先承诺公众号、小红书、评论等泛平台能力。平台能力接口应从两个真实适配器或明确的用例中长出来，不必提前做可热插拔插件框架。SQLite + 文件素材目录适合本地资料库；任务应以可恢复的持久化状态机组织，进程重启后重用已下载音频和已保存字幕。

## 开源实现对照

| 项目 / 资料 | 可借鉴做法 | 对本项目的限制 |
| --- | --- | --- |
| [yt-dlp B 站提取器](https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/bilibili.py) | 已维护视频元数据、音视频流、字幕接口与请求头；可以作为媒体传输层候选，避免维护播放地址签名等低层细节。 | 返回结构里包含 `danmaku`，不能把 extractor 的所有 `subtitles` 都当成对白字幕。代码也显式提示部分字幕需登录。要标记作者/AI/未知、登录态可见和权限状态。yt-dlp 主要面向命令行下载，调用方式和许可证要在实现前评估。 |
| [VideoToNo](https://github.com/like-attract/video-to-note) | 与需求最接近：平台字幕优先、无字幕时本地转写、可单独导出带时间轴转录、任务持久化、本地服务及 MCP/Agent 出口。可参考它的状态、取消、长任务恢复和转录导出体验。 | 它是完整视频笔记产品，包含账号凭证、多个平台、LLM 等更大范围；不应整体照搬。其 README 描述的转写引擎和硬件并不等于 M1 Pro 本机最佳答案，仍要实测。 |
| [MLX Whisper 示例](https://github.com/ml-explore/mlx-examples/tree/main/whisper) 与 [mlx-community large-v3-turbo](https://huggingface.co/mlx-community/whisper-large-v3-turbo) | Python 调用直接，模型可通过 Hugging Face 下载；支持分段时间轴与词级时间戳。适合作为 Apple Silicon 原生候选，符合本机 M1 Pro 的方向。 | 项目没有给出本机这条视频的真实耗时、内存或中文专名准确率；不是已有性能结论。应把音频预处理、模型和推理参数固定后，以本机样本测量。 |
| [whisper.cpp](https://github.com/ggml-org/whisper.cpp) | Apple Silicon 支持 Metal；还可选 Core ML/ANE encoder；C/C++ CLI 适合作为部署轻、可控的替代引擎。 | 模型格式、构建和 Core ML 资源管理增加集成成本；官方“可加速”说明不能替代本机实测。可作为备选基准，不必在第一版同时维护两个引擎。 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Python 接口成熟，分段结果和 VAD 方便；适合 NVIDIA/CUDA 或通用 CPU 环境。 | 上游性能对比主要是 CUDA 硬件，不能据此推断 Apple Silicon 最优；本机应以 MLX/whisper.cpp 对比它之后再定。 |
| [SenseVoice](https://github.com/QwenAudio/SenseVoice) | 可作为中文识别及语言/情绪等任务的后续候选。 | 当前需求重视长音频稳定切段与可靠时间轴；其集成和时间戳路径要单独核实，不把模型特性宣传当作替代指标。 |

## 建议的实施边界

1. 先实现一个本地 Python 核心、一套 SQLite 数据和素材目录；首版只有 B 站采集器与一种默认转写引擎。CLI 和本地网页都调用同一服务层。
2. B 站链路优先提取可用平台字幕；没有字幕时才下载音频并转写。每份结果记录原始 URL、BV/分 P、作者、标题、采集时间、字幕语言、字幕类型、方法/模型版本和处理状态。
3. 明确区分“平台未提供字幕”“未登录而不可见”“请求受限”“提取器不支持”和“字幕确实为空”；拒绝访问时停止，不猜测或绕过权限。
4. 原始数据和派生数据分开存储。对重复 URL 归一化到平台 ID + 分 P；字幕源材料和转写结果分别保留，换模型可从已下载音频重新处理。
5. 任务状态落 SQLite，并记录可复用的阶段产物：元信息、平台字幕、媒体下载、转写、导出。重启后把过期的运行中状态变成可重试状态，不宣称能续接模型内部推理。
6. 音频保留策略做成配置：为大批量采集节省磁盘，可在成功转录后清理；要可复核和换模型时可选择保留。删除与保留状态写入记录。
7. 默认只本地运行，云端转写必须是明确的单次选择，显示即将发送的数据类型；云引擎不进入默认自动回退链。
8. 后续只有出现真实需求再增加 YouTube、公众号、小红书等适配器。评论单列为独立采集能力，范围与完整性单独说明。

## ASR 选型实验

不能仅凭芯片代际或项目 README 决定。用同一段中文音频（优先使用已经取得的公开视频音频）比较 MLX Whisper large-v3-turbo 与 whisper.cpp Metal；若轻量方案也重要，再加入 faster-whisper CPU。至少记录：模型下载大小、冷启动、热推理时长、峰值内存、时间轴连续性、数字/人名/专名表现、取消耗时、重跑能否复用缓存。原第三方 SRT 可作参考文本，但不是无错标注。

实验完成前，MLX large-v3-turbo 只算首选候选。其余引擎通过统一转写接口预留替换空间，不先同时实现和维护。

## 结论

- 本地工具与保留插件并行，是当前最合适的产品形态：插件负责快速浏览器采集，本地工具逐步承接批量资料库、任务恢复和多格式导出。
- 方案中“Python + SQLite + 文件素材 + 本地网页/CLI 共用核心”可以保留。
- 收窄首版平台与框架承诺；ASR 先做同机对比后冻结默认模型。
- 下一步若进入开发，应先把本调研的边界同步进主 README/方案，再做单条 B 站字幕采集闭环和 ASR 对照实验；不需要重开总体方向确认。

## 参考

- yt-dlp B 站实现：[extractor/bilibili.py](https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/bilibili.py)
- VideoToNo：[GitHub README](https://github.com/like-attract/video-to-note)
- MLX Whisper：[mlx-examples/whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper)
- whisper.cpp：[GitHub](https://github.com/ggml-org/whisper.cpp)
- faster-whisper：[GitHub](https://github.com/SYSTRAN/faster-whisper)
- SenseVoice：[GitHub](https://github.com/QwenAudio/SenseVoice)
