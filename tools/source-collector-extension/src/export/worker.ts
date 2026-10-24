import { strToU8, zipSync } from 'fflate';
import { csvCell, publicMetadata, safeName, srt } from '../core';
import { loadCues } from '../storage';
import type { Job } from '../types';
self.onmessage = async ({ data }: MessageEvent<{ jobs: Job[] }>) => {
  try {
    const files: Record<string, Uint8Array> = {}; let count = 0;
    const rows = [['BV号','分P','标题','作者','视频链接','视频时长秒','采集时间','状态','字幕来源','模型','运行设备','字幕条数','字幕末尾秒','提示','错误','文件目录']];
    for (const j of data.jobs) {
      let folder = '';
      if (j.status === 'success') {
        const cues = await loadCues(j.id);
        if (!cues?.length) throw new Error(`${j.bvid} 的字幕记录缺失，请重试采集后导出`);
        folder = `${j.bvid}_P${j.page}_${safeName(j.video?.title ?? '')}`;
        files[`${folder}/字幕.srt`] = strToU8(srt(cues));
        files[`${folder}/正文.txt`] = strToU8(cues.map(c => c.text).join('\n'));
        files[`${folder}/来源.json`] = strToU8(JSON.stringify(publicMetadata(j), null, 2)); count++;
      }
      rows.push([j.bvid,String(j.page),j.video?.title ?? '',j.video?.author ?? '',j.video?.url ?? `https://www.bilibili.com/video/${j.bvid}/?p=${j.page}`,String(j.video?.duration ?? ''),j.collectedAt ?? '',j.status,j.track ?? j.source ?? '',j.model ?? '',j.device ?? '',String(j.cueCount ?? ''),String(j.subtitleEnd ?? ''),j.warning ?? '',j.error ?? '',folder]);
      self.postMessage({ type: 'progress', done: count });
    }
    if (!count) throw new Error('还没有可导出的字幕');
    files['manifest.csv'] = strToU8('\ufeff' + rows.map(r => r.map(csvCell).join(',')).join('\r\n'));
    files['使用说明.txt'] = strToU8('本包由 工作台源信息采集生成。来源.json 与 manifest.csv 保留原视频链接、时间与采集方式。local-asr 表示在本机生成的机器字幕，需人工核对人名、数字和断句。字幕覆盖时间不等于内容已逐字核实；请对照原视频引用。失败项保留在索引中，便于重试。\n');
    const zip = zipSync(files, { level: 6 }); self.postMessage({ type: 'done', zip }, [zip.buffer as ArrayBuffer]);
  } catch (e) { self.postMessage({ type: 'error', error: e instanceof Error ? e.message : '导出失败' }); }
};
