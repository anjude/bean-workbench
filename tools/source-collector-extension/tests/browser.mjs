import { chromium } from 'playwright';
import { mkdtemp, mkdir, readFile, writeFile, rm, cp } from 'node:fs/promises';
import { build } from 'esbuild';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { unzipSync, strFromU8 } from 'fflate';

const root = path.resolve('artifacts/fixture-extension'); await mkdir('artifacts',{ recursive:true });
await rm(root,{recursive:true,force:true}); await cp('dist',root,{recursive:true});
// offscreen 不在 Playwright 的 Page 路由范围内，在测试构建中替换网络边界；生产包保持原样。
const mock = `const realFetch=globalThis.fetch;globalThis.fetch=async(url,init)=>{const u=new URL(String(url));let data;if(u.hostname==='api.bilibili.com'){if(u.pathname.endsWith('/view')){await new Promise(r=>setTimeout(r,250));data={bvid:u.searchParams.get('bvid'),aid:1,title:'字幕采集验收样本',duration:6,owner:{name:'测试作者'},pages:[{page:1,cid:1,part:'第一部分',duration:6}],rights:{}};}else if(u.pathname.endsWith('/v2'))data={subtitle:{subtitles:[{lan:'zh-CN',lan_doc:'中文',subtitle_url:'https://aisubtitle.hdslb.com/test.json'}]}};else throw new Error('不应请求音频');return new Response(JSON.stringify({code:0,data}));}if(u.hostname==='aisubtitle.hdslb.com')return new Response(JSON.stringify({body:[{from:0,to:2,content:'源信息采集样本'},{from:2.2,to:5.8,content:'原文与来源一起保留'}]}));return realFetch(url,init);};`;
await build({entryPoints:['src/transcription/offscreen.ts'],outfile:path.join(root,'offscreen.js'),bundle:true,format:'esm',platform:'browser',target:'chrome116',banner:{js:mock}});
const profile = await mkdtemp(path.join(os.tmpdir(),'beannote-extension-'));
const context = await chromium.launchPersistentContext(profile,{ channel:'chromium', headless:true, args:[`--disable-extensions-except=${root}`,`--load-extension=${root}`], acceptDownloads:true, viewport:{width:1100,height:900} });
const errors=[]; context.on('weberror', e => errors.push(e.error().message));
context.on('console', m => { if (m.type()==='error') console.error(m.text()); });
try {
  const sw = context.serviceWorkers()[0] ?? await context.waitForEvent('serviceworker');
  const id = new URL(sw.url()).host;
  let page = await context.newPage(); await page.goto(`chrome-extension://${id}/index.html`);
  await page.waitForSelector('#start:disabled');
  await page.screenshot({path:'artifacts/empty.png',fullPage:true});
  let control=page;
  const send = command => control.evaluate(command => chrome.runtime.sendMessage({target:'background',...command}),command);
  await page.locator('#input').fill('BV1yUHP6rEYD\nBV1yUHP6rEYD\nhttps://www.bilibili.com/video/BV1Ay4y1s7fG/\n不是视频'); await page.locator('#add').click();
  await page.waitForFunction(() => document.getElementById('count-all').textContent==='2');
  assert.match(await page.locator('#notice').innerText(),/1 条重复/); assert.match(await page.locator('#notice').innerText(),/1 条格式无效/);
  await page.locator('#start').click();
  await page.close(); page=await context.newPage(); control=page; await page.goto(`chrome-extension://${id}/index.html`);
  try { await page.waitForFunction(() => document.getElementById('count-success').textContent==='2',undefined,{timeout:30000}); }
  catch(e) { console.error(JSON.stringify(await send({action:'get'}))); await page.screenshot({path:'artifacts/failure.png',fullPage:true}); throw e; }
  await page.waitForFunction(()=>document.getElementById('run-state').textContent==='本批采集完成');
  await page.screenshot({path:'artifacts/success.png',fullPage:true});
  const downloadPromise=page.waitForEvent('download'); await page.locator('#export').click(); const download=await downloadPromise;
  const bytes=await readFile(await download.path()); const zip=unzipSync(bytes); const srtName=Object.keys(zip).find(n=>n.endsWith('字幕.srt'));
  assert(srtName); assert.match(strFromU8(zip[srtName]),/00:00:00,000 --> 00:00:02,000/); assert.match(strFromU8(zip['manifest.csv']),/测试作者/); assert.equal(Object.keys(zip).filter(n=>n.endsWith('字幕.srt')).length,2);
  await writeFile('artifacts/export-test.zip',bytes);
  // 取消读取中的条目后，不接受异步请求的迟到成功结果。
  const first='BV1yUHP6rEYD:1'; await send({action:'retry',id:first}); await send({action:'start'});
  await page.waitForFunction(()=>document.querySelector('[data-status=fetching]'));
  await send({action:'cancel',id:first}); await new Promise(r=>setTimeout(r,700));
  assert.equal((await send({action:'get'})).state.jobs.find(j=>j.id===first).status,'cancelled');
  await send({action:'retry',id:first}); await send({action:'start'});
  await page.waitForFunction(()=>document.getElementById('count-success').textContent==='2');
  // 弹窗/工作台重开时不丢失成功数据。
  await page.close(); const reopened=await context.newPage(); control=reopened; await reopened.goto(`chrome-extension://${id}/index.html`); await reopened.waitForFunction(()=>document.getElementById('count-success').textContent==='2');
  // 浏览器崩溃后，活动状态重置为待处理，不伪装成已完成。
  await sw.evaluate(async()=>{ await chrome.offscreen.closeDocument(); const {state}=await chrome.storage.local.get('state'); state.jobs[0].status='transcribing'; state.running=true; await chrome.storage.local.set({state}); });
  await reopened.reload(); await reopened.waitForFunction(()=>document.getElementById('count-pending').textContent==='1');
  assert.equal((await send({action:'get'})).state.running,false);
  await reopened.setViewportSize({width:420,height:900}); await reopened.emulateMedia({colorScheme:'dark'});
  assert(await reopened.evaluate(()=>document.documentElement.scrollWidth <= innerWidth));
  await reopened.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  await reopened.screenshot({path:'artifacts/narrow-dark.png'});
  await send({action:'add',input:Array.from({length:55},(_,i)=>`BV1234567${String(i+11).padStart(3,'1')}`).join('\n')});
  assert.equal(await reopened.locator('.job').count(),50);await reopened.locator('#next').click();assert.equal(await reopened.locator('.job').count(),7);
  assert.deepEqual(errors,[]);
  console.log('PASS: MV3 load, offscreen queue, metadata + SRT, IndexedDB, ZIP, reopening, crash recovery, narrow dark layout');
} finally { await context.close(); await rm(profile,{recursive:true,force:true}); }
