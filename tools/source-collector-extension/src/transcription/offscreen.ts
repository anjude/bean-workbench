import { getAudio, getSubtitles, getVideo } from '../content/bilibili';
import { coverageWarning } from '../core';
import { saveCues } from '../storage';
import type { Cue, Job, Settings } from '../types';
let busy = false, active: string | undefined, controller: AbortController | undefined, worker: Worker | undefined;
let rejectWorker: ((error: Error) => void) | undefined;
const send = async (message: object) => {
  const res = await chrome.runtime.sendMessage({ target: 'background', ...message });
  if (!res.ok) throw new Error(res.error); return res;
};
const update = (id: string, patch: Partial<Job>) => send({ action: 'update', id, patch });
async function decode(bytes: ArrayBuffer): Promise<Float32Array> {
  const ctx = new AudioContext({ sampleRate: 16000 });
  try {
    const buffer = await ctx.decodeAudioData(bytes);
    if (buffer.sampleRate !== 16000) throw new Error('浏览器音频解码采样率不支持 16 kHz');
    const mono = new Float32Array(buffer.length);
    for (let c = 0; c < buffer.numberOfChannels; c++) {
      const channel = buffer.getChannelData(c); for (let i = 0; i < mono.length; i++) mono[i] += channel[i] / buffer.numberOfChannels;
    }
    return mono;
  } finally { await ctx.close(); }
}
async function transcribe(id: string, audio: Float32Array, settings: Settings, signal: AbortSignal): Promise<{ cues: Cue[]; device: string }> {
  worker ??= new Worker(chrome.runtime.getURL('asr-worker.js'), { type: 'module' });
  return new Promise((resolve, reject) => {
    rejectWorker = reject;
    worker!.onerror = event => { worker?.terminate(); worker = undefined; rejectWorker = undefined; reject(new Error(`本地转写引擎错误：${event.message}`)); };
    let progressError: unknown;
    worker!.onmessage = ({ data }) => {
      if (signal.aborted) { reject(new Error('任务已取消')); return; }
      if (data.type === 'progress') void update(id, data.patch).catch(e => { progressError = e; });
      if (data.type === 'done') { rejectWorker = undefined; if (progressError) reject(progressError); else resolve({ cues: data.cues, device: data.device }); }
      if (data.type === 'error') { rejectWorker = undefined; worker?.terminate(); worker = undefined; reject(new Error(data.error)); }
    };
    worker!.postMessage({ audio, settings, runtimeBase: chrome.runtime.getURL('') }, [audio.buffer as ArrayBuffer]);
  });
}
async function collect(job: Job, settings: Settings, signal: AbortSignal) {
  const video = await getVideo(job.bvid, job.page, signal); await update(job.id, { video, detail: '检查现有字幕', progress: .04 });
  const subtitles = await getSubtitles(video, signal);
  let cues: Cue[], extra: Partial<Job>;
  if (subtitles) { cues = subtitles.cues; extra = { source: 'platform', track: subtitles.track }; }
  else {
    await update(job.id, { detail: '未发现可用字幕，下载音频用于本地转写', progress: .08 });
    const bytes = await getAudio(video, signal); signal.throwIfAborted();
    await update(job.id, { detail: '在本机解码音频', progress: .12 });
    const audio = await decode(bytes); signal.throwIfAborted();
    if (Math.abs(audio.length / 16000 - video.duration) > Math.max(4, video.duration * .02)) throw new Error('音频解码时长与视频不符，已停止以避免导出不完整字幕');
    await update(job.id, { status: 'model', detail: '准备本地模型（首次使用需下载）', progress: .15 });
    const result = await transcribe(job.id, audio, settings, signal); cues = result.cues;
    extra = { source: 'local-asr', model: settings.model, device: result.device };
  }
  signal.throwIfAborted();
  if (!cues.length) throw new Error('没有识别到可用语音，字幕未生成');
  await saveCues(job.id, cues);
  await update(job.id, { ...extra, status: 'success', progress: 1, detail: '已完成，可导出', collectedAt: new Date().toISOString(), cueCount: cues.length, subtitleStart: cues[0].start, subtitleEnd: cues.at(-1)!.end, warning: coverageWarning(cues, video.duration) });
}
async function run() {
  if (busy) return; busy = true;
  try {
    while (true) {
      const next = await send({ action: 'claim' });
      if (!next.job) break;
      active = next.job.id; controller = new AbortController();
      try { await collect(next.job, next.settings, controller.signal); }
      catch (e) { await update(next.job.id, { status: controller.signal.aborted ? 'cancelled' : 'error', detail: '采集未完成', error: e instanceof Error ? e.message : String(e) }); }
      finally { active = undefined; controller = undefined; rejectWorker = undefined; }
      // 音频和模型均在本机顺序处理，避免多个转写任务争抢内存。
      await new Promise(r => setTimeout(r, 1200));
    }
  } catch (e) { console.error('队列停止', e); await send({ action: 'pause' }).catch(() => {}); }
  finally { worker?.terminate(); worker = undefined; busy = false; }
}
chrome.runtime.onMessage.addListener((message, sender, reply) => {
  if (sender.id !== chrome.runtime.id || message?.target !== 'engine') return;
  if (message.action === 'run') { reply({ ok: true }); void run(); }
  if (message.action === 'cancel' && message.id === active) {
    controller?.abort(); worker?.terminate(); worker = undefined; rejectWorker?.(new Error('已取消')); reply({ ok: true });
  } else if (message.action === 'cancel') reply({ ok: true });
});
