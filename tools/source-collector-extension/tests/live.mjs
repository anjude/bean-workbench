// 可选联网验收：真实公开视频、真实音频、本地模型。使用独立测试 profile。
import { chromium } from 'playwright';
import path from 'node:path';
import { mkdir, writeFile, mkdtemp, rm } from 'node:fs/promises';
import os from 'node:os';
await mkdir('artifacts',{recursive:true});
const root=path.resolve('dist');
const profile=process.env.LIVE_PROFILE??await mkdtemp(path.join(os.tmpdir(),'beannote-live-'));
const context=await chromium.launchPersistentContext(profile,{channel:'chromium',headless:true,args:[`--disable-extensions-except=${root}`,`--load-extension=${root}`],acceptDownloads:true,viewport:{width:1100,height:900}});
try{
  const sw=context.serviceWorkers()[0]??await context.waitForEvent('serviceworker');
  const id=new URL(sw.url()).host;
  let page=await context.newPage();await page.goto(`chrome-extension://${id}/index.html`);await page.waitForSelector('#start:disabled');
  const send=async command=>{const r=await page.evaluate(command=>chrome.runtime.sendMessage({target:'background',...command}),command);if(!r?.ok)throw new Error(r?.error??'后台无应答');return r;};
  const get=await send({action:'get'}); if(get.state.jobs.some(j=>['fetching','model','transcribing'].includes(j.status))) throw new Error('旧测试仍在运行');
  for(const j of get.state.jobs) await send({action:'remove',id:j.id});
  await send({action:'settings',settings:{model:process.env.ASR_MODEL??'Xenova/whisper-small',device:process.env.ASR_DEVICE??'wasm'}});
  console.log('设置',JSON.stringify((await send({action:'get'})).state.settings));
  await send({action:'add',input:process.env.BVID??'BV1yUHP6rEYD'}); await send({action:'start'});
  let last='',finished=false,reopened=false;
  for(let i=0;i<120;i++){
    await new Promise(r=>setTimeout(r,10000));
    const state=(await send({action:'get'})).state;const j=state.jobs[0];const text=`${j.status} ${Math.round(j.progress*100)}% ${j.detail} ${j.error??''}`;
    if(text!==last){console.log(text);last=text;}
    if(j.status==='transcribing'&&!reopened){await page.close();page=await context.newPage();await page.goto(`chrome-extension://${id}/index.html`);reopened=true;console.log('工作台关闭并重开，后台转写继续');}
    if(j.status==='transcribing'&&process.env.ASR_CANCEL==='1'){
      await send({action:'cancel',id:j.id});await new Promise(r=>setTimeout(r,3000));
      const cancelled=(await send({action:'get'})).state.jobs[0];
      if(cancelled.status!=='cancelled')throw new Error('取消后出现迟到结果');
      console.log('PASS: live ASR Worker termination and cancelled state remains stable');finished=true;break;
    }
    if(['success','error','cancelled'].includes(j.status)){
      await page.screenshot({path:'artifacts/live-result.png',fullPage:true});
      await writeFile('artifacts/live-result.json',JSON.stringify(j,null,2));
      if(j.status!=='success')throw new Error(j.error??j.detail);
      const downloadPromise=page.waitForEvent('download');await page.locator('#export').click();const download=await downloadPromise;await download.saveAs('artifacts/live-sources.zip');
      console.log('PASS: live Bilibili audio -> local ASR -> SRT ZIP');finished=true;break;
    }
  }
  if(!finished)throw new Error('本地转写验收超过 20 分钟');
}finally{await context.close();if(!process.env.LIVE_PROFILE)await rm(profile,{recursive:true,force:true});}
