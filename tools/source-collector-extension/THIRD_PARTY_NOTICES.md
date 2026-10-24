# 第三方组件与模型

| 组件 | 许可证 | 来源 |
| --- | --- | --- |
| Transformers.js 3.8.1 | Apache-2.0 | https://github.com/huggingface/transformers.js |
| ONNX Runtime Web | MIT | https://github.com/microsoft/onnxruntime |
| fflate 0.8.3 | MIT | https://github.com/101arrowz/fflate |
| Hugging Face Jinja（间接依赖） | MIT | https://github.com/huggingface/huggingface.js |
| Whisper 上游代码 | MIT | https://github.com/openai/whisper |
| Xenova Whisper ONNX 转换模型 | Apache-2.0（模型卡声明） | https://huggingface.co/Xenova/whisper-small |

Whisper 模型经 Xenova 的 ONNX 转换版本按需下载：

- https://huggingface.co/Xenova/whisper-small
- https://huggingface.co/Xenova/whisper-base
- https://huggingface.co/Xenova/whisper-tiny

模型权重不放入本项目版本管理。第三方许可证原文保留为 `.txt` 文件，构建时随扩展打包。
