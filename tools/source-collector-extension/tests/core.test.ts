import test from 'node:test';
import assert from 'node:assert/strict';
import { parseInput, normalizeCues, srt, csvCell, safeName, recover, coverageWarning } from '../src/core.ts';
import { getAudio, getVideo, getSubtitles } from '../src/content/bilibili.ts';
import { DEFAULT_STATE, type State, type Video } from '../src/types.ts';
import { softwareAdapter } from '../src/transcription/device.ts';

test('自动设备模式排除模拟 GPU，避免把本地 CPU 经软件图形层绕远路', () => {
  assert(softwareAdapter({info:{description:'SwiftShader Device (Subzero)'}}));
  assert(softwareAdapter({isFallbackAdapter:true}));
  assert(!softwareAdapter({info:{description:'Apple M-series GPU',architecture:'metal'}}));
});

test('混合输入保留分P、去重，并拒绝第三方/伪装域名与无效页码', () => {
  const parsed = parseInput('BV1yUHP6rEYD\nhttps://www.bilibili.com/video/BV1yUHP6rEYD/?p=2\nhttps://www.bilibili.com/video/BV1yUHP6rEYD/?p=2\nhttps://bilibili.com.evil.test/video/BV1yUHP6rEYD/\nhttps://www.bilibili.com/video/BV1yUHP6rEYD/?p=-1');
  assert.equal(parsed.videos.length,2); assert.equal(parsed.duplicates,1); assert.equal(parsed.invalid.length,2); assert.equal(parsed.videos[1].page,2);
});
test('SRT 毫秒进位、无效时间过滤与顺序一致', () => {
  const cues = normalizeCues([{ from:59.9996,to:61,content:'这是第二句' },{from:0,to:1,content:'第一句'},{from:-1,to:0,content:'无效'},{from:2,to:1,content:'无效'}]);
  assert.equal(cues.length,2); assert.match(srt(cues),/2\n00:01:00,000 --> 00:01:01,000/);
  assert.equal(coverageWarning(cues,61),undefined); assert.match(coverageWarning(cues,600)!,/提前结束/);
});
test('导出标题不能构成路径穿越或 CSV 公式', () => {
  assert.equal(safeName('../../:a?b\\c'), '.._..__a_b_c');
  assert.equal(csvCell('=HYPERLINK("x")'), '"\'=HYPERLINK(""x"")"');
  assert.equal(csvCell('正常,标题'), '"正常,标题"');
});
test('后台中断仅重置活动任务，保留成功记录，并在恢复时暂停', () => {
  const state: State = { ...structuredClone(DEFAULT_STATE), running:true, jobs:[{id:'a',bvid:'BV1yUHP6rEYD',page:1,status:'transcribing',progress:.6,detail:'转写',createdAt:''},{id:'b',bvid:'BV1yUHP6rEYD',page:2,status:'success',progress:1,detail:'完成',createdAt:''}] };
  const interrupted = recover(state,false); assert.equal(interrupted.running,false); assert.equal(interrupted.jobs[0].status,'queued'); assert.equal(interrupted.jobs[1].status,'success');
  assert.equal(recover(state,true),state);
});
const video: Video = { bvid:'BV1yUHP6rEYD',cid:1,aid:1,page:1,pages:1,title:'样本',author:'作者',duration:721,url:'https://www.bilibili.com/video/BV1yUHP6rEYD/' };
test('不把接口通用预览提示误判为付费；未返回字幕时走转写路径', async () => {
  const realFetch = globalThis.fetch;
  globalThis.fetch = async () => new Response(JSON.stringify({code:0,data:{preview_toast:'为创作付费，购买观看完整视频',subtitle:{subtitles:[]}}}));
  try { assert.equal(await getSubtitles(video,new AbortController().signal),null); } finally { globalThis.fetch = realFetch; }
});
test('实际受限视频停止采集，短片段音频不被当作完整视频', async () => {
  const realFetch = globalThis.fetch;
  try {
    globalThis.fetch = async () => new Response(JSON.stringify({code:0,data:{rights:{ugc_pay:1}}}));
    await assert.rejects(getVideo(video.bvid,1,new AbortController().signal),/付费或专属/);
    globalThis.fetch = async () => new Response(JSON.stringify({code:0,data:{timelength:30000,dash:{audio:[]}}}));
    await assert.rejects(getAudio(video,new AbortController().signal),/片段/);
  } finally { globalThis.fetch = realFetch; }
});
test('平台字幕中文优先，并保留机器字幕来源标记', async () => {
  const realFetch = globalThis.fetch; let credentials: RequestCredentials | undefined;
  globalThis.fetch = async (url,init) => {
    credentials = init?.credentials;
    return new Response(JSON.stringify(String(url).includes('/x/player/v2') ? { code:0,data:{ subtitle:{subtitles:[{lan:'en',lan_doc:'English',subtitle_url:'https://aisubtitle.hdslb.com/en'},{lan:'ai-zh',lan_doc:'中文',ai_type:1,subtitle_url:'https://aisubtitle.hdslb.com/zh'}]}}} : {body:[{from:0,to:2,content:String(url).endsWith('zh') ? '中文样本':'English'}]}));
  };
  try { const result = await getSubtitles(video,new AbortController().signal); assert.equal(result?.cues[0].text,'中文样本'); assert.match(result!.track,/机器字幕/); assert.equal(credentials,'omit'); }
  finally { globalThis.fetch = realFetch; }
});
