import { ACTIVE, type Command, type Job, type Response, type State } from '../types';
const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
const statusNames = { queued:'待采集', fetching:'读取中', model:'准备模型', transcribing:'本地转写', success:'已完成', error:'失败', cancelled:'已取消' };
let state: State, filter = 'all', exporting = false, pageIndex = 0;
const pageSize = 50;
function notice(text: string, error = false) { const node = $('notice'); node.textContent = text; node.className = error ? 'notice error' : 'notice'; node.hidden = !text; }
async function call(c: Command) {
  const r = await chrome.runtime.sendMessage({ target: 'background', ...c }) as Response;
  if (!r?.ok) throw new Error(r?.error ?? '扩展后台未响应，请重新加载扩展');
  if (r.state) { state = r.state; render(); }
  if (r.message) notice(r.message); return r;
}
function button(text: string, fn: () => Promise<unknown>, cls = '') {
  const b = document.createElement('button'); b.type = 'button'; b.textContent = text; b.className = cls;
  b.onclick = () => void act(b, fn); return b;
}
async function act(button: HTMLButtonElement, fn: () => Promise<unknown>) {
  button.disabled = true;
  try { await fn(); } catch (e) { notice(e instanceof Error ? e.message : '操作失败', true); }
  finally { button.disabled = false; render(); }
}
function duration(seconds: number) { return `${Math.floor(seconds / 60)}:${String(Math.round(seconds % 60)).padStart(2,'0')}`; }
function renderJob(j: Job) {
  const row = document.createElement('article'); row.className = 'job'; row.dataset.status = j.status;
  const heading = document.createElement('div'); heading.className = 'job-heading';
  const link = document.createElement('a'); link.textContent = j.video?.title ?? `${j.bvid}${j.page > 1 ? ` · P${j.page}` : ''}`;
  link.href = j.video?.url ?? `https://www.bilibili.com/video/${j.bvid}/?p=${j.page}`; link.target = '_blank'; link.rel = 'noopener noreferrer';
  const badge = document.createElement('span'); badge.className = `badge ${j.status}`; badge.textContent = statusNames[j.status]; heading.append(link, badge);
  const meta = document.createElement('p'); meta.className = 'meta';
  meta.textContent = [j.video?.author,j.video ? duration(j.video.duration) : '',j.source === 'platform' ? j.track : j.source === 'local-asr' ? '本地机器转写 · 请核对数字' : '',j.cueCount ? `${j.cueCount} 条字幕` : ''].filter(Boolean).join(' · ');
  const detail = document.createElement('p'); detail.className = j.status === 'error' ? 'detail error-text' : 'detail'; detail.textContent = j.error ?? j.detail;
  row.append(heading,meta,detail);
  if (ACTIVE.includes(j.status)) { const bar = document.createElement('progress'); bar.max = 1; bar.value = j.progress; bar.setAttribute('aria-label','采集进度'); row.append(bar); }
  if (j.warning) { const warning = document.createElement('p'); warning.className = 'warning'; warning.textContent = j.warning; row.append(warning); }
  const actions = document.createElement('div'); actions.className = 'job-actions';
  if (ACTIVE.includes(j.status) || j.status === 'queued') actions.append(button('取消', () => call({ action:'cancel', id:j.id }), 'quiet'));
  if (['error','cancelled'].includes(j.status)) actions.append(button('重试', () => call({ action:'retry', id:j.id }), 'quiet'));
  if (!ACTIVE.includes(j.status)) actions.append(button('移除', () => call({ action:'remove', id:j.id }), 'quiet muted'));
  row.append(actions); return row;
}
function render() {
  if (!state) return;
  const success = state.jobs.filter(j => j.status === 'success').length;
  const active = state.jobs.some(j => ACTIVE.includes(j.status));
  $('count-all').textContent = String(state.jobs.length); $('count-success').textContent = String(success);
  $('count-pending').textContent = String(state.jobs.filter(j => j.status === 'queued' || ACTIVE.includes(j.status)).length);
  $('count-error').textContent = String(state.jobs.filter(j => ['error','cancelled'].includes(j.status)).length);
  const start = $<HTMLButtonElement>('start'); start.disabled = state.running || !state.jobs.some(j => j.status === 'queued'); start.textContent = state.running ? '正在采集' : '开始采集';
  $<HTMLButtonElement>('pause').disabled = !state.running;
  const exp = $<HTMLButtonElement>('export'); exp.disabled = !success || exporting; exp.textContent = exporting ? '正在生成 ZIP…' : `导出已完成（${success}）`;
  $('run-state').textContent = state.running ? '队列顺序处理 · 可关闭本页' : active ? '暂停中，当前条目完成后停止' : !state.jobs.length ? '导入视频后开始采集' : state.jobs.some(j => j.status === 'queued') ? '已暂停 · 等待开始' : state.jobs.every(j => j.status === 'success') ? '本批采集完成' : '本批处理结束 · 失败项可重试';
  $<HTMLSelectElement>('model').disabled = state.running || active; $<HTMLSelectElement>('device').disabled = state.running || active;
  $<HTMLSelectElement>('model').value = state.settings.model; $<HTMLSelectElement>('device').value = state.settings.device;
  $<HTMLButtonElement>('cache').disabled = state.running || active;
  const items = state.jobs.filter(j => filter === 'all' || filter === 'success' && j.status === 'success' || filter === 'pending' && (j.status === 'queued' || ACTIVE.includes(j.status)) || filter === 'error' && ['error','cancelled'].includes(j.status));
  const pages = Math.max(1, Math.ceil(items.length / pageSize)); pageIndex = Math.min(pageIndex, pages - 1);
  $('queue').replaceChildren(...items.slice(pageIndex * pageSize, (pageIndex + 1) * pageSize).map(renderJob));
  $('pagination').hidden = pages <= 1; $('page-label').textContent = `${pageIndex + 1} / ${pages} 页 · 共 ${items.length} 条`;
  $<HTMLButtonElement>('previous').disabled = pageIndex === 0; $<HTMLButtonElement>('next').disabled = pageIndex >= pages - 1;
  $('empty').hidden = !!items.length;
  $('empty-title').textContent = state.jobs.length ? '这个分组暂时没有条目' : '把想看的视频，留成可查的资料';
  $('empty-copy').textContent = state.jobs.length ? '切换上方分组查看其他采集任务。' : '粘贴 B 站视频链接或 BV 号，再点击“加入队列”。有字幕直接采集，无字幕在本机转写。';
  document.querySelectorAll<HTMLButtonElement>('[data-filter]').forEach(b => { b.setAttribute('aria-pressed',String(b.dataset.filter === filter)); });
}
async function add(input: string) {
  const r = await call({ action:'add', input });
  if (r.ok) notice(`已加入 ${r.added ?? 0} 条${r.duplicates ? `，跳过 ${r.duplicates} 条重复链接` : ''}${r.invalid?.length ? `；${r.invalid.length} 条格式无效：${r.invalid.slice(0,3).join('、')}` : ''}`, !!r.invalid?.length);
}
async function exportZip() {
  exporting = true; render();
  const worker = new Worker(chrome.runtime.getURL('export-worker.js'), { type:'module' });
  try {
    const data = await new Promise<Uint8Array>((resolve,reject) => {
      worker.onmessage = ({ data }) => { if (data.type === 'done') resolve(data.zip); if (data.type === 'error') reject(new Error(data.error)); };
      worker.onerror = e => reject(new Error(e.message)); worker.postMessage({ jobs:state.jobs });
    });
    const blob = new Blob([data as BlobPart], { type:'application/zip' }); const url = URL.createObjectURL(blob);
    try { await chrome.downloads.download({ url, filename:`beannote-sources_${new Date().toISOString().replace(/[:.]/g,'-')}.zip`, saveAs:true }); notice('ZIP 已交给 Chrome 下载，包含字幕、纯文本和来源索引。'); }
    finally { setTimeout(() => URL.revokeObjectURL(url), 60000); }
  } finally { worker.terminate(); exporting = false; render(); }
}
async function init() {
  await call({ action:'get' });
  $('add').onclick = () => void act($('add'), () => add($<HTMLTextAreaElement>('input').value));
  $('current').onclick = () => void act($('current'), () => call({ action:'current' }));
  $('start').onclick = () => void act($('start'), () => call({ action:'start' }));
  $('pause').onclick = () => void act($('pause'), () => call({ action:'pause' }));
  $('retry-all').onclick = () => void act($('retry-all'), () => call({ action:'retry-all' }));
  $('cache').onclick = () => void act($('cache'), () => call({ action:'clear-cache' }));
  $('clear').onclick = () => { if (confirm('清理已完成、失败与取消的条目及其本地字幕？请先导出需要保留的资料。')) void act($('clear'), () => call({ action:'clear-finished' })); };
  $('export').onclick = () => void act($('export'), exportZip);
  $<HTMLInputElement>('file').onchange = async e => { const file = (e.target as HTMLInputElement).files?.[0]; if (file) { try { await add(await file.text()); } catch (e) { notice(String(e),true); } } (e.target as HTMLInputElement).value = ''; };
  document.querySelectorAll<HTMLButtonElement>('[data-filter]').forEach(b => { b.onclick = () => { filter = b.dataset.filter!; pageIndex = 0; render(); }; });
  $('previous').onclick = () => { pageIndex = Math.max(0, pageIndex - 1); render(); };
  $('next').onclick = () => { pageIndex++; render(); };
  for (const id of ['model','device']) $<HTMLSelectElement>(id).onchange = () => void call({ action:'settings', settings:{ model:$<HTMLSelectElement>('model').value as State['settings']['model'], device:$<HTMLSelectElement>('device').value as State['settings']['device'] } }).catch(e => { notice(e.message,true); render(); });
  chrome.storage.onChanged.addListener((changes, area) => { if (area === 'local' && changes.state?.newValue) { state = changes.state.newValue as State; render(); } });
}
void init().catch(e => notice(e.message, true));
