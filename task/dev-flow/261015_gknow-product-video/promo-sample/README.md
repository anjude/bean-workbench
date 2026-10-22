# 鹅懂个啥宣传样片

12 秒竖版视频，展示「今天吃什么」转盘。产物：`gknow-food-wheel-sample.mp4`；首帧和关键帧在 `preview/`。

## 复现

Python 3.9+，安装 `pillow` 和 `imageio-ffmpeg` 后运行：

```bash
python3 render.py
```

画面根据产品现有页面、数据、色值和鹅表情资产制作。由于微信小程序组件无法直接挂载到浏览器渲染管线，本样片在独立工程中还原展示状态，没有改动产品仓库。视频中的「煲仔饭」是产品候选项，8 项盘面是演示时筛选的候选集合。

参考工作流：[guizang-product-video-skill](https://github.com/op7418/guizang-product-video-skill)。本工程未复制其起步工程或默认样式。
