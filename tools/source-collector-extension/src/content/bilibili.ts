import type { Cue, Video } from '../types';
import { normalizeCues } from '../core';
interface Page { cid: number; page: number; part: string; duration: number }
interface View { bvid: string; aid: number; title: string; duration: number; owner: { name: string }; pages: Page[]; rights?: { ugc_pay?: number; arc_pay?: number }; is_upower_exclusive?: boolean }
interface Track { lan: string; lan_doc: string; subtitle_url: string; is_lock?: boolean; ai_type?: number }
interface Audio { id: number; bandwidth: number; mimeType?: string; codecs?: string; baseUrl?: string; base_url?: string; backupUrl?: string[]; backup_url?: string[] }
const API = 'https://api.bilibili.com';
export async function fetchJSON<T>(url: string, signal: AbortSignal): Promise<T> {
  const res = await fetch(url, { credentials: 'omit', signal: AbortSignal.any([signal, AbortSignal.timeout(30000)]) });
  if (!res.ok) throw new Error(`B 站请求失败（HTTP ${res.status}），请稍后重试`);
  return res.json() as Promise<T>;
}
async function api<T>(path: string, signal: AbortSignal): Promise<T> {
  const result = await fetchJSON<{ code: number; message: string; data?: T }>(`${API}${path}`, signal);
  if (result.code !== 0 || !result.data) throw new Error(`B 站接口返回 ${result.code}：${result.message || '未取得数据'}`);
  return result.data;
}
export async function getVideo(bvid: string, page: number, signal: AbortSignal): Promise<Video> {
  const v = await api<View>(`/x/web-interface/view?bvid=${encodeURIComponent(bvid)}`, signal);
  if (v.is_upower_exclusive || v.rights?.ugc_pay || v.rights?.arc_pay) throw new Error('此视频存在付费或专属访问限制，暂不采集');
  const p = v.pages?.find(p => p.page === page);
  if (!p) throw new Error(`视频没有第 ${page} P，请检查链接的 p 参数`);
  return { bvid: v.bvid, aid: v.aid, cid: p.cid, page, pages: v.pages.length,
    title: v.pages.length > 1 ? `${v.title} · P${page} ${p.part}` : v.title,
    author: v.owner.name, duration: p.duration, url: `https://www.bilibili.com/video/${v.bvid}/${page > 1 ? `?p=${page}` : ''}` };
}
export async function getSubtitles(video: Video, signal: AbortSignal): Promise<{ cues: Cue[]; track: string } | null> {
  const data = await api<{ subtitle?: { subtitles?: Track[] } }>(`/x/player/v2?aid=${video.aid}&cid=${video.cid}`, signal);
  const tracks = (data.subtitle?.subtitles ?? []).filter(t => !t.is_lock && t.subtitle_url);
  const rank = (t: Track) => /^(ai-)?zh/.test(t.lan) ? 0 : 1;
  tracks.sort((a, b) => rank(a) - rank(b) || Number(!!a.ai_type) - Number(!!b.ai_type));
  if (!tracks.length) return null;
  const track = tracks[0]; const url = new URL(track.subtitle_url, 'https://www.bilibili.com');
  if (url.protocol !== 'https:' || !/(^|\.)(hdslb\.com|bilibili\.com)$/.test(url.hostname)) throw new Error('字幕地址不属于支持的 B 站域名');
  const raw = await fetchJSON<{ body: { from: number; to: number; content: string }[] }>(url.href, signal);
  const cues = normalizeCues(raw.body ?? []);
  if (!cues.length) return null;
  const machine = !!track.ai_type || track.lan.startsWith('ai-');
  return { cues, track: `${track.lan_doc || track.lan} · ${machine ? '平台机器字幕' : '平台字幕（未核实制作方式）'}` };
}
export async function getAudio(video: Video, signal: AbortSignal): Promise<ArrayBuffer> {
  if (video.duration > 7200) throw new Error('此分 P 超过 120 分钟，超出首版本地转写容量；有现成字幕的视频不受此限制');
  const p = await api<{ timelength: number; is_preview?: boolean; dash?: { audio: Audio[] } }>(`/x/player/playurl?bvid=${video.bvid}&cid=${video.cid}&fnval=16&qn=16&fourk=0`, signal);
  if (p.is_preview || p.timelength / 1000 < video.duration - Math.max(3, video.duration * .02)) throw new Error('播放数据仅包含片段，无法采集完整字幕');
  const audio = [...(p.dash?.audio ?? [])].filter(a => !a.codecs || a.codecs.startsWith('mp4a')).sort((a, b) => a.bandwidth - b.bandwidth)[0];
  if (!audio) throw new Error('没有取得可用音频流，请确认视频可公开播放');
  const urls = [audio.baseUrl ?? audio.base_url, ...(audio.backupUrl ?? audio.backup_url ?? [])].filter((u): u is string => !!u);
  let last = '';
  for (const link of urls) {
    const url = new URL(link);
    if (url.protocol !== 'https:' || !/(^|\.)(bilivideo\.(com|cn|net)|bilibili\.com|hdslb\.com)$/.test(url.hostname)) continue;
    try {
      const res = await fetch(url.href, { credentials: 'omit', signal: AbortSignal.any([signal, AbortSignal.timeout(180000)]) });
      if (!res.ok) throw new Error(`音频下载 HTTP ${res.status}`);
      const limit = 256 * 1024 * 1024;
      if (Number(res.headers.get('Content-Length')) > limit) { await res.body?.cancel(); throw new Error('音频超过 256 MB，超出首版浏览器转写容量'); }
      if (!res.body) throw new Error('音频数据为空');
      const reader = res.body.getReader(); const chunks: Uint8Array[] = []; let size = 0;
      while (true) {
        const { done, value } = await reader.read(); if (done) break;
        size += value.length;
        if (size > limit) { await reader.cancel(); throw new Error('音频超过 256 MB，超出首版浏览器转写容量'); }
        chunks.push(value);
      }
      const buffer = new Uint8Array(size); let offset = 0;
      for (const chunk of chunks) { buffer.set(chunk, offset); offset += chunk.length; }
      const bytes = buffer.buffer;
      if (bytes.byteLength < 1024) throw new Error('音频数据为空或不完整');
      return bytes;
    } catch (e) { if (signal.aborted) throw e; last = e instanceof Error ? e.message : '音频下载失败'; }
  }
  throw new Error(last || '未找到支持的 B 站音频地址');
}
