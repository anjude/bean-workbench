# ASR 模型统一

## 目标

把 Qwen 与 Whisper 统一为来源采集器的模型能力：集中声明模型、固定权重来源和 revision、可验证下载、统一转写返回结构，并在 CLI、网页和来源包中记录实际使用信息。模型权重不进 Git，重建方法进项目 README。

## 实现

- 新增 `model-catalog.json`，集中登记 Qwen3-ASR 1.7B 8-bit、Whisper Large v3 Turbo、Whisper Tiny 的引擎、Hugging Face repo、40 位 revision、权重大小与 SHA-256。
- `transcribe.py` 按注册表解析模型别名、下载指定 revision、核验权重、选择 MLX Audio 或 MLX Whisper 适配器；统一返回 cues、引擎、repo、revision、语言、时间戳质量和推理参数。
- 本机模型统一缓存至 `.agents/local-config/models/asr/{model-id}/{revision}`，并添加明确 Git 忽略项；将已有 Qwen checkpoint 复制到该路径，复核 SHA-256 与注册表一致。
- Go CLI 增加 `hr models list` / `hr models download`，采集命令传递模型和语言；网页提供模型/语言选择；任务库保存 model id 与语言提示，来源包写入模型 revision 与时间戳精度。
- README 记录三份 Hugging Face 固定下载源、revision、文件大小、SHA-256、依赖安装和其他机器重建步骤。Qwen 的 30 秒分段明确标作粗时间戳。
- ASR 环境锁定 MLX、mlx-audio、mlx-whisper 与 huggingface-hub 版本。

## 验证

- Python 单测 22 项通过，含模型注册、别名、cache override、权重大小/SHA 校验、Qwen dict 段与语言列表归一化、来源包元数据与现存采集功能。
- `go test ./cmd/...` 通过；执行 `make install` 后 `hr models list` 正确报告 Qwen 已安装且校验通过、两种 Whisper 尚未下载。
- Qwen checkpoint SHA-256：`bf304b009cc7eca79283056f787b44c952d24ac22cec787b39732bba3c23c13c`，与实验目录及注册表一致。
- 使用 Qwen 对既有 704.45 秒中文样本做实际推理，得到 24 个分块，时间范围包含至样本结束。推理中发现 mlx-audio 的 `segments` 是字典而非带属性对象、语言是列表；适配器已兼容并归一化为语言字符串。
- ASR README 中提供基于相对仓库路径的环境重建步骤，模型下载后执行 `hr models list` 检查。

## 限制

- Qwen 时间戳为约 30 秒粗分块，不可用作逐句对齐字幕；ForcedAligner 尚未接入。
- 本轮仅有中文音频真实运行，英文/混合语言样本仍待测；Qwen 与 Whisper 的通用质量对比未完成。
- Whisper 权重本机尚未下载，下载/核验路径由注册表实现，尚未实测大文件下载。

## 文件

- 实现：`tools/source-collector/src/workbench_source_collector/transcribe.py`、`model-catalog.json`、`core.py`、`storage.py`、`cli.py`、`server.py`、`web/index.html`
- 入口与文档：`cmd/collect.go`、`cmd/source_collector.go`、`tools/source-collector/README.md`、`tools/source-collector/pyproject.toml`
- 回归：`tools/source-collector/tests/test_transcribe.py`、`test_core.py`、`test_youtube.py`
