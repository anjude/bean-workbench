# 工作台源信息采集

Chrome 扩展，批量收集 B 站视频字幕与来源。优先读取平台字幕，没有字幕时在本机运行 Whisper 转写，导出 SRT、纯文本和来源索引。

## 安装当前构建

1. 在 Chrome 地址栏打开 `chrome://extensions`，开启「开发者模式」。
2. 点击「加载已解压的扩展程序」，选择本项目的 `dist/` 目录。
3. 点击工具栏中的「工作台源信息采集」图标，打开采集工作台。

本机目录：`/Users/bean/workspace/bean-workbench/tools/source-collector-extension/dist`。

使用 ZIP 分发包时，先完整解压，再加载解压后的目录。Chrome 无法直接加载 ZIP。扩展尚未发布到商店。

## 采集与导出

1. 粘贴 BV 号或完整 `https://www.bilibili.com/video/BV…` 链接，每行一条；也可以导入 UTF-8 TXT。
2. 点击「加入队列」，无效链接会单独提示，重复的 BV 号与分 P 组合自动跳过。
3. 在「本地转写设置」选模型，然后「开始采集」。平台现有中文字幕优先；缺字幕则下载音频并在本机转写。平台机器字幕会保留其来源标记。
4. 采集页可以关闭，浏览器后台继续工作。暂停会等当前条目完成；条目上的「取消」立即中断当前音频/模型任务。
5. 点击「导出已完成」，保存 ZIP。每视频目录包含 `字幕.srt`、`正文.txt`、`来源.json`；根目录 `manifest.csv` 包含全部条目的来源与成功/失败状态。
6. 用 `hr collect import-zip <ZIP路径>` 转换到工作台标准来源库；需要用于 beannote 时，再由内容仓的 `script/import-source.py` 复制到选定主题。

多 P 视频默认只处理第 1 P；用 `?p=2` 指定分 P。首版队列最多 2000 条，列表每页显示 50 条。本地转写支持单分 P 最长 120 分钟、音频文件最多 256 MB；已有平台字幕的视频不受转写时长限制。

## 模型与设备

| 模型 | 使用建议 |
| --- | --- |
| Whisper Small（默认） | 优先保证中文可读性，下载与推理成本较高 |
| Whisper Base | 速度和准确度折中 |
| Whisper Tiny | 快速预览；实测中文同音字和数字误差较多，不建议直接用于正式资料 |

第一次使用会从 Hugging Face 下载配置和模型权重（几十至数百 MB），以后从浏览器缓存读取。运行代码和 ONNX/WASM 运行时随扩展打包。默认采用已验证的 CPU/WASM；本机试验中该量化模型的 Metal GPU 路径更慢，不能假设 GPU 一定更快。可手动选 GPU，或选自动模式优先尝试硬件 WebGPU，加载/推理失败则改用 CPU；软件模拟 GPU 不在自动模式优先范围内。实际耗时因 Chrome、驱动、模型和设备而异。

ASR 字幕不是已核实逐字稿，尤其应核对人名、金额、百分比、英文和音乐片段。每段带上下文进行识别后按时间位置拼接，分段边界仍可能漏词或重复。导出标记记录使用的模型和实际设备，不冒充作者字幕。长音频还受设备可用内存限制，120 分钟是保护阈值，不代表所有设备都能处理该长度。

## 数据与恢复

- 来源元数据、队列和模型选择存在扩展本地存储中；完整字幕存于 IndexedDB，模型文件存于本扩展的浏览器缓存。批次结束或暂停后释放推理 Worker 的内存，已下载模型仍留在缓存。
- 音视频与字幕不发送到云端转写服务；网络请求用于 B 站公开资料/音频与模型下载，不读取 Cookie 或登录凭证。
- 不支持登录后独享、付费、私有或仅可试看视频；会检查音频时长，拒绝把试看片段当完整字幕。公开接口可能不向未登录请求返回字幕，即使登录页面能看见字幕，首版仍可能改走本地转写。
- 浏览器退出或扩展重载后，未完成条目回到待处理并暂停，点击开始后从当前视频开头重试；已完成字幕保留。首版不恢复到当前视频的某个音频分段。
- 「清理模型缓存」会释放已载入模型、删除模型缓存，保留字幕。「清理记录」会删除已完成/失败/取消的条目及对应字幕，请先导出。
- 移除扩展或清除浏览器扩展数据会丢失本机记录，长期资料应通过 ZIP 归档。

## 开发与验证

需要 Node.js 22+：

```bash
npm ci
npm run type-check
npm test
npm run build
```

构建后重新加载 Chrome 中的扩展。版本锁定在 `package-lock.json`。

浏览器集成检查使用独立 Chrome for Testing profile，不读取用户 Chrome 数据：

```bash
npx playwright install chromium
npm run test:browser
```

该检查对网络边界使用固定字幕资料，实际加载 MV3、offscreen、Worker、IndexedDB 和下载链路；覆盖批量去重、失败输入、取消、防止迟到成功、分页、ZIP 内容、页面关闭重开、进程中断恢复与窄屏布局。

可选真实联网验收（下载公开音频与本地模型，会耗时数分钟或更久）：

```bash
node tests/live.mjs
```

默认用 `BV1yUHP6rEYD` 和 Whisper Small。可用 `BVID`、`ASR_MODEL`、`ASR_DEVICE` 指定样本与本地模型；输出在被忽略的 `artifacts/`，测试退出后删除独立 profile。`LIVE_PROFILE` 可指定可复用测试 profile，修改代码后应重新加载扩展或使用新 profile，避免 Chromium 复用旧扩展代码。

打包供加载的 ZIP：

```bash
npm run package
```

## 代码结构

- `src/background/`：任务命令、持久化和最小权限请求头设置。
- `src/content/bilibili.ts`：B 站元数据、平台字幕和音频访问适配，不抓取弹幕。
- `src/transcription/`：offscreen 音频解码、本地模型 Worker 和分段时间轴。
- `src/storage.ts`：IndexedDB 字幕持久化。
- `src/export/`：SRT、纯文本、元数据和 ZIP 生成 Worker。
- `src/ui/`：工作台展示与交互；原文标题通过文本节点渲染。
- `tests/`：业务边界测试、隔离浏览器集成检查和可选真实转写。

## 开源依赖

使用 Transformers.js、ONNX Runtime Web、fflate 与 Whisper 模型。来源和许可证链接见 `THIRD_PARTY_NOTICES.md`；运行时许可证原文随构建一起打包到 `dist/licenses/`。

迁移说明：插件代码和构建目录已归工作台管理。为保留导出兼容性与浏览器已有数据，内部数据库名及 ZIP 文件名前缀沿用旧标识。加载旧目录的 Chrome 需重新加载当前 `dist/`；浏览器可能将新路径视为新的扩展，应先在旧扩展导出已有资料，浏览器数据不会因目录移动自动迁移。
