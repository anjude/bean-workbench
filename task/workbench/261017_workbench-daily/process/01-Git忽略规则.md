# Git 忽略规则 · 过程记录

- 任务目录：`task/workbench/261017_workbench-daily/`
- 阶段：01 日常维护
- 时间：2026-10-17

## 做了什么

- 盘点工作台未提交文件及大小，对照 `.gitignore` → 发现宣传样片的 MP4、WAV 已被忽略，但可再生成的预览帧仍是 Git 候选文件。
- 更新 `.gitignore` → 补充常见视频、音频格式、样片预览帧和 Python 临时产物的忽略规则；保留视频工具所需的内置短音效。
- 运行 `git check-ignore -v`、`git diff --check` 和 `make check` → 规则命中预期，结构检查通过。

## 得到的结论

- 样片视频、音频和预览帧属于可再生成产物：`task/dev-flow/261015_gknow-product-video/promo-sample/render.py`。
- 视频工具的 11 个内置 WAV 是运行所需素材，应允许随源码提交：`.agents/vendor/product-video/assets/audio/manifest.json`。

## 被推翻的判断

- 无。

## 待核 / 没答上来

- 无。
