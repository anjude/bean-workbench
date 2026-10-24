# 工作台来源采集器

通用来源获取能力，代码由工作台维护，供研究、学习、业务分析和内容创作复用。采集器负责获取资料、标记来源和生成标准包；具体业务决定如何使用资料。

## 使用

在工作台根目录执行 `make install` 安装 Go 入口后，可以从任意目录调用：

```sh
hr collect bilibili BV1yUHP6rEYD
hr collect youtube 'https://www.youtube.com/watch?v=qU3fmidNbJE'
hr collect youtube qU3fmidNbJE
hr collect bilibili BV1yUHP6rEYD --model whisper-large-v3-turbo --language Chinese
hr collect jobs
hr collect serve
hr collect import-zip '/绝对路径/插件导出.zip'
hr models list
hr models download qwen3-asr-1.7b-8bit
hr models download qwen3-forced-aligner-0.6b-8bit
```

中文 B 站推荐步骤：先运行一次 `hr models list`，确认 Qwen3-ASR 和 Qwen3-ForcedAligner 都显示 `installed: true`；再执行 `hr collect bilibili <BV号或链接>`。命令会同步运行至完成。有平台字幕时优先保存平台字幕；无可用字幕时，才运行本机 ASR 和强制对齐。再次执行同一视频会重新采集，并覆盖同一来源包中的 `source.json`、`字幕.srt` 和 `正文.txt`；如果该视频已有任务正在排队或执行，会返回“采集任务正在执行”，不会重复启动。机器字幕仍需人工复核。

查看采集结果与打开网页：

```sh
hr collect jobs
hr collect serve
```

`hr collect jobs` 会显示来源包绝对路径。需要将选定资料用于已有 beannote 主题时，手工执行：

```sh
python3 task/beannote/script/import-source.py '/来源包完整路径' --topic '已存在的主题目录名'
```

插件导出 ZIP 可用 `hr collect import-zip '/ZIP完整路径'` 转成同一格式。采集器不会替你选择主题或自动写入主题目录。

网页为 `http://127.0.0.1:8765`，支持混合批量输入 B 站和 YouTube 链接。平台字幕优先；没有可用字幕时下载音频并调用本机 ASR 模型。默认 Qwen3-ASR 转写后由 Qwen3-ForcedAligner 生成词/汉字级时间轴；字幕优先按句末标点断行，只有长句超过长度或时长阈值时才在逗号等自然分句处换行。对齐结果仍需人工复核。未安装对齐模型时保留 Qwen 粗分块并在来源元数据中标明降级原因。YouTube 上传字幕优先于自动字幕，自动翻译轨不作原文采集。

资料包含 `source.json`、`字幕.srt`、`正文.txt`，格式见 [来源包 v1](../../docs/source-package-v1.md)。插件 ZIP 导入兼容旧格式。`hr collect jobs` 返回任务状态及资料包绝对路径。历史状态 `ready_to_archive` 在网页显示为“已采集”；保留数据库状态值以兼容已有任务，工作台不关联业务主题。

## 安装

基础能力需要 Python 3.9+。YouTube 需要 Python 3.10+ 和 Node.js；MLX 需要 Apple Silicon、Python 3.10+ 和 FFmpeg。当前本机使用 Python 3.12，完整环境已安装：

```sh
cd tools/source-collector
python3.12 -m venv .venv-asr
.venv-asr/bin/python -m pip install -e '.[youtube,asr-macos]'
```

基础环境可使用 `.venv` 并 `pip install -e .`。底层 Python CLI 为 `hr-source`，模块名为 `workbench_source_collector`。Go 优先调用 `.venv-asr`，其次 `.venv`，最后 PATH 中的 `hr-source`。

## 数据位置与配置

| 内容 | 默认位置 | 可选环境变量 |
| --- | --- | --- |
| Python 工具 | `tools/source-collector/` | `HR_SOURCE_COLLECTOR_DIR` |
| 轻量来源包 | 工作台 `source/collected/` | `HR_SOURCE_DIR` |
| SQLite、音频、迁移临时数据 | 工作台 `.agents/local-config/source-collector/` | `HR_COLLECTOR_DATA_DIR` |
| ASR 模型权重 | 工作台 `.agents/local-config/models/asr/{模型 ID}/{revision}/` | `HR_MODEL_CACHE_DIR` |
| YouTube 登录 Cookie 文件 | 默认不读取 | `HR_YOUTUBE_COOKIES_FILE` |

来源包、运行数据、虚拟环境和模型权重均被 Git 忽略。模型目录按 ID 与精确修订号隔离。下载时从 Hugging Face Hub 的固定 revision 获取文件，并核对权重大小和 SHA-256；校验失败不会进入转写。`HR_MODEL_CACHE_DIR` 可把权重放到其他磁盘。设置 `HR_COLLECTOR_DATA_DIR` 时，未指定 `HR_SOURCE_DIR` 的来源包会进入该数据目录的 `inbox/`，便于隔离运行。旧的 `BEANNOTE_DATA_DIR` 和 `BEANNOTE_YOUTUBE_COOKIES_FILE` 暂作为兼容别名。

YouTube 要求登录验证时，使用自己导出的 Netscape Cookie 文件重试：

```sh
HR_YOUTUBE_COOKIES_FILE='/私有目录/youtube-cookies.txt' hr collect youtube qU3fmidNbJE --retry
```

## ASR 模型清单与重建

模型定义集中在 [`model-catalog.json`](src/workbench_source_collector/model-catalog.json)，包括推理引擎、模型仓库、不可变 revision、权重文件大小和 SHA-256。模型 ID 与 Hugging Face repo ID 都可用于 `--model`；默认 ID 为 `qwen3-asr-1.7b-8bit`。`HR_ASR_MODEL` 可覆盖默认值。`hr models list` 显示本机模型校验状态，`hr models download <模型 ID>` 下载并核验模型。无需把大模型文件复制进项目或提交 Git。

当前目录中的模型来源如下。新机器只要能访问 Hugging Face Hub，执行上面的安装和下载命令即可重建相同环境；如 Hub 不可达，可从可信镜像取得完全相同 revision 的文件放进对应目录，再执行 `hr models list` 让校验器检查。

| 模型 ID | Hugging Face 来源 | 固定 revision | 权重文件 | 权重 SHA-256 | 用途 / 时间戳 |
| --- | --- | --- | --- | --- | --- |
| `qwen3-asr-1.7b-8bit` | [mlx-community/Qwen3-ASR-1.7B-8bit](https://huggingface.co/mlx-community/Qwen3-ASR-1.7B-8bit/tree/a8379a2e2f9e313c9292cdf1af4055ab56d50d55) | `a8379a2e2f9e313c9292cdf1af4055ab56d50d55` | `model.safetensors`（2,463,307,541 bytes） | `bf304b009cc7eca79283056f787b44c952d24ac22cec787b39732bba3c23c13c` | 默认中文模型；约 30 秒粗分块 |
| `qwen3-forced-aligner-0.6b-8bit` | [mlx-community/Qwen3-ForcedAligner-0.6B-8bit](https://huggingface.co/mlx-community/Qwen3-ForcedAligner-0.6B-8bit/tree/0e1a68e91d815300c7c9754b2a7639378b23db15) | `0e1a68e91d815300c7c9754b2a7639378b23db15` | `model.safetensors`（1,271,924,386 bytes） | `be19ef8ac4326d032e7673342930b14c2df30bd68c1632493b0f563e30829f91` | Qwen 转写后的强制对齐；逐词/汉字时间，单次音频最长 5 分钟 |
| `whisper-large-v3-turbo` | [mlx-community/whisper-large-v3-turbo](https://huggingface.co/mlx-community/whisper-large-v3-turbo/tree/a4aaeec0636e6fef84abdcbe3544cb2bf7e9f6fb) | `a4aaeec0636e6fef84abdcbe3544cb2bf7e9f6fb` | `weights.safetensors`（1,613,977,612 bytes） | `951ed3fc1203e6a62467abb2144a96ce7eafca8fa77e3704fdb8635ff3e7f8a6` | Whisper 备选；模型分段时间 |
| `whisper-tiny` | [mlx-community/whisper-tiny](https://huggingface.co/mlx-community/whisper-tiny/tree/78c52ab98ca87f570bc57ad852e15ef7060f9f76) | `78c52ab98ca87f570bc57ad852e15ef7060f9f76` | `weights.npz`（74,418,182 bytes） | `d5a3b8671ac7aab11a2c9d0f16e7da94bad5500d785856f438c6bd44c3723944` | 小模型链路诊断；不建议作为正式正文 |

以上 revision 和摘要值是重建依据；更新模型时应先更新注册表与此表，再做一轮转写验证。ASR extras 固定 Python 依赖版本，要求 Apple Silicon macOS、Python 3.10+ 和 FFmpeg。从新克隆的工作台仓库根目录执行：

```sh
cd tools/source-collector
python3.12 -m venv .venv-asr
.venv-asr/bin/python -m pip install --upgrade pip
.venv-asr/bin/python -m pip install -e '.[youtube,asr-macos]'
cd ../..
make install
hr models download qwen3-asr-1.7b-8bit
hr models download qwen3-forced-aligner-0.6b-8bit
hr models list
```

按需把下载命令中的模型 ID 替换成 Whisper 模型。也可以在工作台根目录设置 `HR_MODEL_CACHE_DIR` 指向容量充足的本机磁盘。Qwen 的样本对比记录见任务 `task/dev-flow/261024_beannote-source-collector/process/03-本地模型对比.md`；目前优先依据中文样本抽查选择默认模型，不能据此宣称跨语言或所有场景的普遍准确性。

## 数据迁移

本机 4 条历史任务、音频和资料包已从旧 beannote 数据目录迁入上述工作台目录；任务 ID、状态不变，来源路径已重写。迁移完成并核对后，旧数据目录已清理。其他机器可在停止旧服务后执行：

```sh
.venv-asr/bin/hr-source migrate-legacy --from-dir '/旧数据目录'
```

已有新任务库、目标冲突或旧任务处理中会拒绝迁移，不覆盖新旧数据。当前代码和环境只维护在 `tools/source-collector/`；模型统一缓存位于 `.agents/local-config/models/asr/`，具体来源和重建步骤见上文。

## 业务消费

采集器不导入业务仓、不选择创作主题。beannote 使用自己的 [来源导入脚本](../../task/beannote/script/import-source.py) 将选定资料包复制为主题快照，见 [创作导入说明](../../task/beannote/docs/import-source.md)。其他业务可以直接读取来源包。

## 检查

```sh
.venv-asr/bin/python -m unittest discover -s tests -v
```
