import { env, pipeline, type AutomaticSpeechRecognitionPipeline, type AutomaticSpeechRecognitionOutput } from '@huggingface/transformers';
import type { Cue, Settings } from '../types';
import { automaticDevice } from './device';
let transcriber: AutomaticSpeechRecognitionPipeline | undefined, key = '', device = '', lastDownloadUpdate = 0;
const progress = (patch: object) => self.postMessage({ type: 'progress', patch });
self.onmessage = async ({ data }: MessageEvent<{ audio: Float32Array; settings: Settings; runtimeBase: string }>) => {
  try {
    env.allowLocalModels = false;
    env.backends.onnx.wasm!.wasmPaths = `${data.runtimeBase}ort/`;
    env.backends.onnx.wasm!.numThreads = 1;
    const { settings, audio } = data;
    const load = (d: 'webgpu' | 'wasm') => pipeline('automatic-speech-recognition', settings.model, {
        device: d, dtype: 'q8', progress_callback: p => {
          if (p.status === 'progress' && Date.now() - lastDownloadUpdate > 700) { lastDownloadUpdate = Date.now(); progress({ status: 'model', detail: `下载模型 ${p.file} · ${Math.round(p.progress ?? 0)}%`, progress: .15 }); }
          else if (p.status === 'initiate') progress({ status: 'model', detail: `准备模型文件 ${p.file}`, progress: .15 });
        }
    });
    if (key !== `${settings.model}:${settings.device}`) {
      if (transcriber) await transcriber.dispose(); transcriber = undefined;
      device = settings.device === 'auto' ? await automaticDevice() : settings.device;
      try { transcriber = await load(device as 'webgpu' | 'wasm'); }
      catch (e) {
        if (device !== 'webgpu' || settings.device !== 'auto') throw e;
        device = 'wasm'; progress({ status: 'model', detail: 'WebGPU 不可用，切换本地 CPU 转写', progress: .15 }); transcriber = await load('wasm');
      }
      key = `${settings.model}:${settings.device}`;
    }
    const duration = audio.length / 16000, cues: Cue[] = [];
    // 每段核心 26 秒，左右各留 2 秒上下文；以时间中点归属去重，降低断句边界重复。
    const coreSeconds = 26, count = Math.ceil(duration / coreSeconds);
    for (let i = 0; i < count; i++) {
      const coreStart = i * coreSeconds, coreEnd = Math.min(duration, coreStart + coreSeconds);
      const start = Math.max(0, coreStart - 2), end = Math.min(duration, coreEnd + 2);
      progress({ status: 'transcribing', detail: `本地${device === 'webgpu' ? ' GPU' : ' CPU'} 转写 · 第 ${i + 1} / ${count} 段`, progress: .2 + .78 * i / count });
      const infer = () => transcriber!(audio.subarray(Math.floor(start * 16000), Math.floor(end * 16000)), { return_timestamps: true, language: 'chinese', task: 'transcribe', chunk_length_s: 30, stride_length_s: 5, no_repeat_ngram_size: 8 });
      let output: AutomaticSpeechRecognitionOutput | AutomaticSpeechRecognitionOutput[];
      try { output = await infer(); }
      catch (e) {
        if (device !== 'webgpu' || settings.device !== 'auto') throw e;
        progress({ status: 'model', detail: 'GPU 转写不可用，改用本机 CPU 继续此段', progress: .2 + .78 * i / count });
        await transcriber?.dispose(); transcriber = await load('wasm'); device = 'wasm'; output = await infer();
      }
      const item = Array.isArray(output) ? output[0] : output;
      for (const c of item.chunks ?? []) {
        const from = start + (c.timestamp[0] ?? 0), to = Math.min(duration, start + (c.timestamp[1] ?? end - start));
        const middle = (from + to) / 2;
        if (middle < coreStart || (i < count - 1 && middle >= coreEnd) || !c.text.trim() || to <= from) continue;
        cues.push({ start: Math.max(from, cues.at(-1)?.end ?? 0), end: to, text: c.text.trim() });
      }
    }
    self.postMessage({ type: 'done', cues: cues.filter(c => c.end > c.start), device });
  } catch (e) { self.postMessage({ type: 'error', error: `本地转写失败：${e instanceof Error ? e.message : String(e)}。可改用较小模型或 CPU 后重试。` }); }
};
