# 工作台来源资料

`source/local-source/` 用于存放本机保留的原始素材，不进入 Git。这里的文件保持获取时的原貌，不编辑、不覆盖，也不放筛选结果、改造版本或构建产物。

需要挑选或二次开发时，先从 `source/local-source/` 复制到对应任务或业务仓的工作目录，再修改副本。后续切换任务时，仍从工作台根目录的 `source/README.md` 找到素材位置。

## 当前素材

| 目录 | 内容 | 使用场景 |
| --- | --- | --- |
| `source/local-source/h5-game-library/` | 原始 H5 小游戏源码合集，约 1.0 GB | 为「鹅懂个啥」及后续任务挑选测试、游戏素材；具体取舍见相关任务文档 |

## 采集来源库

`source/collected/` 接收 `hr collect` 生成的标准来源包，包含来源 JSON、字幕和纯文本，已被 Git 忽略。代码与安装见 [采集器说明](../tools/source-collector/README.md)，数据格式见 [来源包 v1](../docs/source-package-v1.md)。

SQLite 和音频缓存位于 `.agents/local-config/source-collector/`，模型沿用本机缓存。来源包供学习、研究及内容创作复用；具体业务选定材料后复制到自己的工作目录。beannote 使用自身的来源导入脚本生成主题快照。
