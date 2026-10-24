import { ACTIVE, DEFAULT_STATE, MODELS, type Command, type Job, type Response, type State } from '../types';
import { parseInput, recover } from '../core';
import { deleteCues } from '../storage';

let lock: Promise<unknown> = Promise.resolve();
function serial<T>(fn: () => Promise<T>): Promise<T> { const next = lock.then(fn, fn); lock = next.catch(() => {}); return next; }
const read = async (): Promise<State> => (await chrome.storage.local.get('state')).state as State | undefined ?? structuredClone(DEFAULT_STATE);
const write = async (s: State) => { await chrome.storage.local.set({ state: s }); };
async function engineAlive() {
  return (await chrome.runtime.getContexts({ contextTypes: [chrome.runtime.ContextType.OFFSCREEN_DOCUMENT] })).length > 0;
}
let creating: Promise<void> | undefined;
async function ensureEngine() {
  if (await engineAlive()) return;
  if (!creating) creating = chrome.offscreen.createDocument({ url: 'offscreen.html', reasons: [chrome.offscreen.Reason.WORKERS], justification: '在本机解码音频并使用 Worker 执行长时间语音转写' }).finally(() => { creating = undefined; });
  await creating;
}
async function headers() {
  await chrome.declarativeNetRequest.updateDynamicRules({ removeRuleIds: [1], addRules: [{
    id: 1, priority: 1, action: { type: chrome.declarativeNetRequest.RuleActionType.MODIFY_HEADERS,
      requestHeaders: [{ header: 'Referer', operation: chrome.declarativeNetRequest.HeaderOperation.SET, value: 'https://www.bilibili.com/' }] },
    condition: { initiatorDomains: [chrome.runtime.id], requestDomains: ['api.bilibili.com', 'bilivideo.com', 'bilivideo.cn', 'bilivideo.net', 'hdslb.com'], resourceTypes: [chrome.declarativeNetRequest.ResourceType.XMLHTTPREQUEST] }
  }] });
}
async function command(c: Command): Promise<Response> {
  let state = await read();
  if (c.action === 'get') { state = recover(state, await engineAlive()); await write(state); return { ok: true, state }; }
  if (c.action === 'current') {
    const tabs = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
    // 工作台标签位于前台时，从最近访问的 B 站页中选择。
    let url = tabs[0]?.url;
    if (!url || !parseInput(url).videos.length) {
      const matches = await chrome.tabs.query({ url: 'https://www.bilibili.com/video/*' });
      url = matches.sort((a, b) => (b.lastAccessed ?? 0) - (a.lastAccessed ?? 0))[0]?.url;
    }
    if (!url) throw new Error('请先在 Chrome 打开一个 B 站视频');
    return command({ action: 'add', input: url });
  }
  if (c.action === 'add') {
    const parsed = parseInput(c.input); let added = 0;
    const existing = new Set(state.jobs.map(j => j.id));
    for (const v of parsed.videos) {
      if (existing.has(v.id)) { parsed.duplicates++; continue; }
      if (state.jobs.length >= 2000) throw new Error('队列已达 2000 条，请先导出并清理已完成条目');
      state.jobs.push({ ...v, status: 'queued', progress: 0, detail: '等待采集', createdAt: new Date().toISOString() }); existing.add(v.id); added++;
    }
    await write(state); return { ok: true, state, added, invalid: parsed.invalid, duplicates: parsed.duplicates };
  }
  if (c.action === 'settings') {
    if (state.running || state.jobs.some(j => ACTIVE.includes(j.status))) throw new Error('请在当前采集结束后修改模型');
    if (!MODELS.includes(c.settings.model) || !['auto','webgpu','wasm'].includes(c.settings.device)) throw new Error('模型设置无效');
    state.settings = c.settings;
  }
  if (c.action === 'start') {
    state = recover(state, await engineAlive());
    if (!state.jobs.some(j => j.status === 'queued')) throw new Error('没有待采集条目，可导入链接或重试失败项');
    await headers(); await ensureEngine(); state.running = true;
  }
  if (c.action === 'pause') state.running = false;
  if (c.action === 'retry-all') state.jobs = state.jobs.map(j => ['error','cancelled'].includes(j.status) ? { ...j, status: 'queued', progress: 0, error: undefined, detail: '等待重试' } : j);
  if (c.action === 'retry' || c.action === 'cancel' || c.action === 'remove') {
    const j = state.jobs.find(j => j.id === c.id); if (!j) throw new Error('条目不存在');
    if (c.action === 'retry') {
      if (ACTIVE.includes(j.status)) throw new Error('请先取消当前条目');
      Object.assign(j, { status: 'queued', progress: 0, detail: '等待重试', error: undefined });
    }
    if (c.action === 'cancel') {
      if (ACTIVE.includes(j.status) && await engineAlive()) await chrome.runtime.sendMessage({ target: 'engine', action: 'cancel', id: j.id });
      Object.assign(j, { status: 'cancelled', detail: '已取消', error: undefined });
    }
    if (c.action === 'remove') {
      if (ACTIVE.includes(j.status)) throw new Error('请先取消当前条目');
      await deleteCues(j.id); state.jobs = state.jobs.filter(x => x.id !== j.id);
    }
  }
  if (c.action === 'clear-finished') {
    const done = state.jobs.filter(j => ['success','error','cancelled'].includes(j.status));
    for (const j of done) await deleteCues(j.id);
    state.jobs = state.jobs.filter(j => !['success','error','cancelled'].includes(j.status));
  }
  if (c.action === 'clear-cache') {
    if (state.running || state.jobs.some(j => ACTIVE.includes(j.status))) throw new Error('采集结束后才能清理模型缓存');
    if (await engineAlive()) await chrome.offscreen.closeDocument();
    for (const name of await caches.keys()) await caches.delete(name);
    return { ok: true, message: '已释放模型并清理本扩展的模型缓存，字幕资料保留' };
  }
  await write(state);
  if (c.action === 'start') void chrome.runtime.sendMessage({ target: 'engine', action: 'run' }).catch(async e => {
    await serial(async () => { const current = await read(); current.running = false; await write(current); }); console.error('采集引擎启动失败', e);
  });
  return { ok: true, state };
}
chrome.runtime.onMessage.addListener((message, sender, reply) => {
  if (sender.id !== chrome.runtime.id || message?.target !== 'background') return;
  void serial(async () => {
    if (message.action === 'claim') {
      const state = await read();
      if (!state.running) return { ok: true, job: null };
      const job = state.jobs.find(j => j.status === 'queued');
      if (!job) { state.running = false; await write(state); return { ok: true, job: null }; }
      Object.assign(job, { status: 'fetching', progress: 0, detail: '读取视频信息', error: undefined,
        collectedAt: undefined, source: undefined, track: undefined, model: undefined, device: undefined,
        cueCount: undefined, subtitleStart: undefined, subtitleEnd: undefined, warning: undefined }); await write(state);
      return { ok: true, job, settings: state.settings };
    }
    if (message.action === 'update') {
      const state = await read(); const j = state.jobs.find(j => j.id === message.id);
      // 已取消的任务不接受旧 Worker 的迟到结果。
      if (j && j.status !== 'cancelled') Object.assign(j, message.patch as Partial<Job>);
      await write(state); return { ok: true };
    }
    return command(message as Command);
  }).then(reply, e => reply({ ok: false, error: e instanceof Error ? e.message : '操作失败' }));
  return true;
});
chrome.action.onClicked.addListener(async () => {
  const url = chrome.runtime.getURL('index.html'); const tabs = await chrome.tabs.query({ url });
  if (tabs[0]?.id) await chrome.tabs.update(tabs[0].id, { active: true }); else await chrome.tabs.create({ url });
});
chrome.runtime.onInstalled.addListener(() => { void headers(); });
