import { readdir, readFile, mkdir, writeFile } from 'node:fs/promises';
import { zipSync } from 'fflate';
import path from 'node:path';
const files={};
async function walk(dir,prefix='') { for(const entry of await readdir(dir,{withFileTypes:true})) { const p=path.join(dir,entry.name),name=prefix+entry.name; if(entry.isDirectory())await walk(p,name+'/');else if(!name.endsWith('.map'))files[name]=new Uint8Array(await readFile(p)); } }
await walk('dist');await mkdir('artifacts',{recursive:true});
await writeFile('artifacts/beannote-source-collector-0.1.0.zip',zipSync(files,{level:6}));
console.log('已生成 artifacts/beannote-source-collector-0.1.0.zip（解压后加载）');
