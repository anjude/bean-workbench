import type { Cue, Job, State } from './types';
import { ACTIVE } from './types';

export function parseInput(input: string): { videos: { bvid: string; page: number; id: string }[]; invalid: string[]; duplicates: number } {
  const videos: { bvid: string; page: number; id: string }[] = [], invalid: string[] = [];
  const seen = new Set<string>(); let duplicates = 0;
  for (const raw of input.split(/[\s,;，；]+/).map(s => s.trim()).filter(Boolean)) {
    let bvid = '', page = 1;
    if (/^BV[\da-z]{10}$/i.test(raw)) bvid = `BV${raw.slice(2)}`;
    else {
      try {
        const url = new URL(raw);
        if (url.protocol !== 'https:' || !(url.hostname === 'bilibili.com' || url.hostname.endsWith('.bilibili.com'))) throw new Error();
        bvid = url.pathname.match(/\/video\/(BV[\da-z]{10})(?:\/|$)/i)?.[1] ?? '';
        bvid = bvid ? `BV${bvid.slice(2)}` : '';
        const param = url.searchParams.get('p'); page = param === null ? 1 : Number(param);
        if (!bvid || !Number.isSafeInteger(page) || page < 1) throw new Error();
      } catch { invalid.push(raw); continue; }
    }
    const id = `${bvid}:${page}`;
    if (seen.has(id)) { duplicates++; continue; }
    seen.add(id); videos.push({ bvid, page, id });
  }
  return { videos, invalid, duplicates };
}
export function normalizeCues(body: { from: number; to: number; content: string }[]): Cue[] {
  return body.map(x => ({ start: Number(x.from), end: Number(x.to), text: String(x.content ?? '').trim() }))
    .filter(x => Number.isFinite(x.start) && Number.isFinite(x.end) && x.start >= 0 && x.end > x.start && x.text)
    .sort((a, b) => a.start - b.start);
}
export function srt(cues: Cue[]): string {
  const time = (n: number) => {
    const ms = Math.max(0, Math.round(n * 1000));
    return `${String(Math.floor(ms / 3600000)).padStart(2,'0')}:${String(Math.floor(ms / 60000) % 60).padStart(2,'0')}:${String(Math.floor(ms / 1000) % 60).padStart(2,'0')},${String(ms % 1000).padStart(3,'0')}`;
  };
  return cues.map((c, i) => `${i + 1}\n${time(c.start)} --> ${time(c.end)}\n${c.text.replace(/\r?\n\s*\r?\n/g, '\n')}`).join('\n\n') + '\n';
}
export function safeName(name: string): string {
  return name.replace(/[<>:"/\\|?*\u0000-\u001f]/g, '_').replace(/[. ]+$/g, '').slice(0, 70) || '未命名';
}
export function csvCell(value: unknown): string {
  let text = String(value ?? '');
  // 来源标题不能成为表格公式。
  if (/^[\s]*[=+@-]/.test(text)) text = `'${text}`;
  return `"${text.replace(/"/g, '""')}"`;
}
export function recover(state: State, engineAlive: boolean): State {
  if (engineAlive) return state;
  return { ...state, running: false, jobs: state.jobs.map(j => ACTIVE.includes(j.status) ? { ...j, status: 'queued', progress: 0, detail: '上次任务中断，点击开始采集可重试' } : j) };
}
export function coverageWarning(cues: Cue[], duration: number): string | undefined {
  if (!cues.length) return '未识别到可用语音';
  const end = cues[cues.length - 1].end;
  if (end < duration - Math.max(15, duration * .1)) return '字幕提前结束，请核对视频是否包含较长的无声片段或识别遗漏';
}
export function publicMetadata(job: Job) { return { ...job, subtitleGenerated: job.source === 'local-asr', requiresReview: job.source === 'local-asr' }; }
