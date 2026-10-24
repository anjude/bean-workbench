import { build } from 'esbuild';
import { copyFile, mkdir, readdir, rm, writeFile } from 'node:fs/promises';
import { deflateSync } from 'node:zlib';
await rm('dist', { recursive:true, force:true }); await mkdir('dist/ort', { recursive:true }); await mkdir('dist/icons', { recursive:true }); await mkdir('dist/licenses', {recursive:true});
await build({ entryPoints: { background:'src/background/index.ts', offscreen:'src/transcription/offscreen.ts', 'asr-worker':'src/transcription/worker.ts', 'export-worker':'src/export/worker.ts', ui:'src/ui/index.ts' }, outdir:'dist', bundle:true, format:'esm', platform:'browser', target:'chrome116', sourcemap:true, minify:true, logLevel:'info' });
for (const file of ['manifest.json','index.html','offscreen.html','style.css','README.md','THIRD_PARTY_NOTICES.md']) await copyFile(file,`dist/${file}`);
for (const [source,name] of [['node_modules/@huggingface/transformers/LICENSE','transformers-LICENSE.txt'],['node_modules/@huggingface/jinja/LICENSE','jinja-LICENSE.txt'],['node_modules/fflate/LICENSE','fflate-LICENSE.txt']]) await copyFile(source,`dist/licenses/${name}`);
for (const file of await readdir('licenses')) await copyFile(`licenses/${file}`,`dist/licenses/${file}`);
for (const file of await readdir('node_modules/onnxruntime-web/dist')) if (/^ort-wasm-simd-threaded.*\.(mjs|wasm)$/.test(file)) await copyFile(`node_modules/onnxruntime-web/dist/${file}`,`dist/ort/${file}`);
// 代码生成原创工具图标，避免外部图片依赖。
function crc32(buf) { let c=0xffffffff; for(const b of buf){c^=b;for(let k=0;k<8;k++)c=(c>>>1)^((c&1)?0xedb88320:0);}return(c^0xffffffff)>>>0; }
function chunk(name,data){const n=Buffer.from(name),len=Buffer.alloc(4),crc=Buffer.alloc(4);len.writeUInt32BE(data.length);crc.writeUInt32BE(crc32(Buffer.concat([n,data])));return Buffer.concat([len,n,data,crc]);}
for(const size of [16,48,128]){const bytes=Buffer.alloc((size*4+1)*size);for(let y=0;y<size;y++)for(let x=0;x<size;x++){const i=y*(size*4+1)+1+x*4;const doc=x>size*.28&&x<size*.73&&y>size*.2&&y<size*.8;const line=doc&&x>size*.38&&x<size*.62&&[.38,.5,.62].some(v=>Math.abs(y/size-v)<.018);bytes.set(line?[17,107,104,255]:doc?[246,250,247,255]:[17,107,104,255],i);}const ih=Buffer.alloc(13);ih.writeUInt32BE(size);ih.writeUInt32BE(size,4);ih[8]=8;ih[9]=6;await writeFile(`dist/icons/${size}.png`,Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),chunk('IHDR',ih),chunk('IDAT',deflateSync(bytes)),chunk('IEND',Buffer.alloc(0))]));}
await writeFile('dist/构建说明.txt','开发版本 0.1.0。Chrome 扩展管理页开启开发者模式，加载此目录。使用与隐私说明见项目 README.md。\n');
