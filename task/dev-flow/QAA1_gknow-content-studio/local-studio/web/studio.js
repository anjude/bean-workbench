const W = 1080, H = 1440;
const labels = {cover:'封面', qa:'问答', chat:'微信对话', knowledge:'知识普及'};
const samples = {
  cover: {type:'cover', title:'输入一个能抓住人的标题', subtitle:'补一句具体情境', kicker:'封面模板 · 主标题 + 情境', footer:'在右侧编辑内容，画布会同步更新'},
  qa: {type:'qa', title:'问答模板', question:'在这里输入具体问题内容', note:'补充说明或作答提示', options:['选项一','选项二','选项三']},
  chat: {type:'chat', title:'微信对话模板', left:'输入第一段对话内容', right:'输入第二段对话内容', footer:'气泡内容、顺序和语气都可以编辑'},
  knowledge: {type:'knowledge', title:'知识普及模板', body:'输入需要说明的知识内容', keyline:'提炼一句重点', source:'填写出处或品牌署名'},
};
let pages = structuredClone([samples.cover, samples.qa, samples.chat, samples.knowledge]);
let active = 0, zoom = 80, saveTimer, toastTimer;
const canvas = document.querySelector('#artboard'), ctx = canvas.getContext('2d');
const fields = document.querySelector('#editorFields');

function escapeHtml(value){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function pageName(p){return labels[p.type]||'页面'}
function idb(){return new Promise((resolve,reject)=>{const req=indexedDB.open('gknow-image-studio-v2',1);req.onupgradeneeded=()=>req.result.createObjectStore('drafts');req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error)})}
async function getDraft(){try{const db=await idb();return await new Promise((resolve,reject)=>{const req=db.transaction('drafts').objectStore('drafts').get('current');req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error)})}catch{return null}}
async function putDraft(value){try{const db=await idb();await new Promise((resolve,reject)=>{const req=db.transaction('drafts','readwrite').objectStore('drafts').put(value,'current');req.onsuccess=resolve;req.onerror=()=>reject(req.error)})}catch{localStorage.setItem('gknow-image-studio-text',JSON.stringify(value.pages.map(p=>({...p,image:''}))))}}
function toast(message){const el=document.querySelector('#toast');el.textContent=message;el.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.remove('show'),2600)}
function scheduleSave(){document.querySelector('#saveState').textContent='保存中…';clearTimeout(saveTimer);saveTimer=setTimeout(async()=>{await putDraft({pages,active});document.querySelector('#saveState').textContent='已保存在本地';},450)}
function loadSaved(){getDraft().then(saved=>{if(saved&&Array.isArray(saved.pages)&&saved.pages.length){pages=saved.pages;active=Math.min(saved.active||0,pages.length-1);refresh()}})}
function updatePageList(){document.querySelector('#pageCount').textContent=String(pages.length).padStart(2,'0');const list=document.querySelector('#pageList');list.innerHTML=pages.map((p,i)=>`<button class="page-item ${i===active?'selected':''}" data-index="${i}"><span class="page-thumb ${p.type}"></span><span class="page-info"><span class="page-title">${escapeHtml(p.title||pageName(p))}</span><span class="page-sub">${String(i+1).padStart(2,'0')} · ${pageName(p)}</span></span><span class="page-grab">··</span></button>`).join('');list.querySelectorAll('.page-item').forEach(el=>el.onclick=()=>{active=Number(el.dataset.index);refresh()})}
function field(label,key,value,{area=false,large=false,help='',placeholder=''}={}){return `<div class="field-group"><label class="field-label" for="field-${key}">${label}<span class="field-count" data-count="${key}"></span></label>${area?`<textarea class="text-area ${large?'large':''}" id="field-${key}" data-key="${key}" placeholder="${escapeHtml(placeholder)}">${escapeHtml(value)}</textarea>`:`<input class="text-input" id="field-${key}" data-key="${key}" value="${escapeHtml(value)}" placeholder="${escapeHtml(placeholder)}">`}${help?`<div class="field-help">${help}</div>`:''}</div>`}
function aiPanel(p){return `<div class="ai-card"><div class="ai-card-head"><span class="ai-spark">✳</span> AI 生成画面素材</div><div class="field-help">先生成插画/场景，再由 Canvas 叠加文字、题卡和品牌信息。</div><textarea class="text-area ai-prompt" id="aiPrompt" placeholder="描述你想要的画面，例如：温暖轻松的朋友聚会场景，桌上有橙色饮料，留出左侧浅色留白放标题；不要文字、字母或水印。">${escapeHtml(p.prompt||'')}</textarea><div class="ai-actions"><button class="button-ai" id="generateImage">✳ 生成背景</button><label class="upload-image">或上传图片<input type="file" id="uploadImage" accept="image/png,image/jpeg,image/webp"></label></div><div class="generation-state" id="generationState">${p.image?'已载入一张画面素材':'未配置生图服务时，可先上传本地图片。'}</div></div>`}
function renderFields(){const p=pages[active];const controls={
  cover:[field('主标题','title',p.title,{area:true,large:true,help:'建议一页表达一个问题，标题尽量控制在 3 行内。'}),field('副标题','subtitle',p.subtitle),field('眉题','kicker',p.kicker)],
  qa:[field('页面标题','title',p.title),field('问题内容','question',p.question,{area:true,large:true}),field('补充提示','note',p.note,{area:true}),field('选项文案','options',p.options?.join(' / ')||'',{help:'用 / 分隔；评分题可保留区间选项。'})],
  chat:[field('页面标题','title',p.title),field('左侧气泡','left',p.left,{area:true}),field('右侧气泡','right',p.right,{area:true}),field('页脚说明','footer',p.footer)],
  knowledge:[field('主标题','title',p.title,{area:true,large:true}),field('正文','body',p.body,{area:true,large:true}),field('重点句','keyline',p.keyline),field('来源/页脚','source',p.source)],
};
  document.querySelector('#editorTitle').textContent=pageName(p);document.querySelector('#activePageLabel').textContent=`${pageName(p)} · 第 ${active+1} 页`;
  fields.innerHTML=(controls[p.type]||[]).join('')+aiPanel(p)+`<div class="field-group"><div class="field-label">品牌底色</div><div class="color-row">${['#f6f2e9','#f1eee6','#f3e9df','#e9f0e9','#e9eef0'].map((c,i)=>`<button class="color-swatch ${i===0?'active':''}" data-color="${c}" style="background:${c}" aria-label="选择背景色"></button>`).join('')}</div></div>`;
  fields.querySelectorAll('[data-key]').forEach(el=>el.addEventListener('input',()=>{const key=el.dataset.key;let value=el.value;if(key==='options')value=value.split('/').map(s=>s.trim()).filter(Boolean);p[key]=value;const count=fields.querySelector(`[data-count="${key}"]`);if(count&&el.tagName==='TEXTAREA')count.textContent=`${el.value.length} 字`;updatePageList();draw();scheduleSave()}));
  fields.querySelectorAll('[data-color]').forEach(el=>el.onclick=()=>{fields.querySelectorAll('[data-color]').forEach(s=>s.classList.remove('active'));el.classList.add('active');p.bg=el.dataset.color;draw();scheduleSave()});
  const gen=fields.querySelector('#generateImage');gen.onclick=generateImage;
  fields.querySelector('#aiPrompt').oninput=e=>{p.prompt=e.target.value;scheduleSave()};
  fields.querySelector('#uploadImage').onchange=e=>{const file=e.target.files?.[0];if(!file)return;const reader=new FileReader();reader.onload=()=>{p.image=reader.result;draw();fields.querySelector('#generationState').textContent='已载入一张画面素材';scheduleSave()};reader.readAsDataURL(file)};
}
function roundedRect(c,x,y,w,h,r,fill){c.beginPath();c.roundRect(x,y,w,h,r);c.fillStyle=fill;c.fill()}
function wrapText(c,text,x,y,maxWidth,lineHeight,maxLines=8){const paragraphs=String(text||'').split('\n');let cy=y,lines=0;for(const paragraph of paragraphs){let line='';for(const ch of paragraph){const test=line+ch;if(c.measureText(test).width>maxWidth&&line){c.fillText(line,x,cy);cy+=lineHeight;line=ch;lines++;if(lines>=maxLines)return cy} else line=test}c.fillText(line,x,cy);cy+=lineHeight;lines++;if(lines>=maxLines)return cy}return cy}
function imageLoad(src){return new Promise(resolve=>{if(!src)return resolve(null);const img=new Image();img.onload=()=>resolve(img);img.onerror=()=>resolve(null);img.src=src})}
async function drawTo(c,p,index,total){c.clearRect(0,0,W,H);const bg=p.bg||'#f6f2e9';c.fillStyle=bg;c.fillRect(0,0,W,H);const img=await imageLoad(p.image);if(img){const scale=Math.max(W/img.width,H/img.height),iw=img.width*scale,ih=img.height*scale;c.drawImage(img,(W-iw)/2,(H-ih)/2,iw,ih);c.fillStyle='rgba(250,247,239,.60)';c.fillRect(0,0,W,H);const grad=c.createLinearGradient(0,0,W,H);grad.addColorStop(0,'rgba(252,249,242,.08)');grad.addColorStop(1,'rgba(238,231,216,.44)');c.fillStyle=grad;c.fillRect(0,0,W,H)}else{c.fillStyle='#f0e4d8';c.beginPath();c.arc(930,180,230,0,Math.PI*2);c.fill();c.fillStyle='#e0ebe1';c.beginPath();c.arc(100,1180,260,0,Math.PI*2);c.fill();c.fillStyle='#fff9ef';c.beginPath();c.arc(885,1150,160,0,Math.PI*2);c.fill()}
  c.fillStyle='#34372f';c.font='600 25px "Noto Sans SC", sans-serif';c.fillText('鹅懂个啥',80,90);c.fillStyle='#a29c8e';c.font='400 17px "Noto Sans SC", sans-serif';c.fillText('G KNOWS',228,90);roundedRect(c,80,125,10,10,5,'#e27450');c.fillStyle='#756f64';c.font='500 19px "Noto Sans SC", sans-serif';c.fillText(p.kicker||`${pageName(p)}模板`,104,143);
  if(p.type==='cover'){
    c.fillStyle='#4a453c';c.font='700 67px "Noto Sans SC", sans-serif';wrapText(c,p.title,80,390,870,102,5);
    roundedRect(c,80,770,920,275,30,'rgba(255,255,255,.83)');c.fillStyle='#2d302c';c.font='700 47px "Noto Sans SC", sans-serif';wrapText(c,p.subtitle,125,875,820,70,2);
    c.fillStyle='#898476';c.font='400 24px "Noto Sans SC", sans-serif';c.fillText(p.footer||'',84,1190);
    c.fillStyle='#d77451';c.beginPath();c.arc(905,1190,33,0,Math.PI*2);c.fill();c.fillStyle='#fff';c.font='500 21px "Noto Sans SC", sans-serif';c.fillText('答',893,1198);
  }else if(p.type==='qa'){
    c.fillStyle='#777368';c.font='500 23px "Noto Sans SC", sans-serif';c.fillText('今天这题，你怎么选？',80,270);
    roundedRect(c,70,330,940,430,30,'rgba(255,255,255,.88)');c.fillStyle='#363831';c.font='700 44px "Noto Sans SC", sans-serif';wrapText(c,p.question,125,440,830,66,5);
    const opts=p.options?.length?p.options:['先说说你的想法'];opts.slice(0,4).forEach((o,i)=>{const y=830+i*96;roundedRect(c,90,y,900,70,16,i===0?'#e9efe8':'rgba(255,255,255,.83)');c.fillStyle=i===0?'#6d8c72':'#4e514a';c.font='600 23px "Noto Sans SC", sans-serif';c.fillText(String.fromCharCode(65+i),120,y+44);c.font='500 23px "Noto Sans SC", sans-serif';c.fillText(o,175,y+44)});
    c.fillStyle='#8b867a';c.font='400 21px "Noto Sans SC", sans-serif';wrapText(c,p.note,90,1300,880,32,2);
  }else if(p.type==='chat'){
    c.fillStyle='#393b35';c.font='700 43px "Noto Sans SC", sans-serif';wrapText(c,p.title,80,320,900,62,3);
    roundedRect(c,90,500,720,210,28,'#fff');c.fillStyle='#3b3b36';c.font='400 27px "Noto Sans SC", sans-serif';wrapText(c,p.left,130,585,630,44,4);
    roundedRect(c,300,775,690,220,28,'#dcebd9');c.fillStyle='#3b3b36';c.font='400 27px "Noto Sans SC", sans-serif';wrapText(c,p.right,345,860,600,44,4);
    roundedRect(c,80,1105,520,52,15,'rgba(255,255,255,.68)');c.fillStyle='#827c70';c.font='500 17px "Noto Sans SC", sans-serif';c.fillText('对话情景演绎 · 非真实聊天记录',105,1138);
    c.fillStyle='#999386';c.font='400 20px "Noto Sans SC", sans-serif';wrapText(c,p.footer,80,1240,890,30,2);
  }else{
    c.fillStyle='#393b35';c.font='700 58px "Noto Sans SC", sans-serif';wrapText(c,p.title,80,340,900,82,4);
    roundedRect(c,70,690,940,330,28,'rgba(255,255,255,.84)');c.fillStyle='#57564f';c.font='400 27px "Noto Sans SC", sans-serif';wrapText(c,p.body,125,770,825,46,6);
    roundedRect(c,80,1090,920,115,22,'#e7eee5');c.fillStyle='#59775e';c.font='700 29px "Noto Sans SC", sans-serif';wrapText(c,p.keyline,125,1160,820,42,2);
    c.fillStyle='#8e887c';c.font='400 19px "Noto Sans SC", sans-serif';c.fillText(p.source||'',80,1290);
  }
  c.strokeStyle='rgba(71,67,58,.11)';c.lineWidth=2;c.strokeRect(36,36,W-72,H-72);c.fillStyle='#8a8579';c.font='500 17px "Noto Sans SC", sans-serif';c.fillText(`${String(index+1).padStart(2,'0')} / ${String(total).padStart(2,'0')}`,890,1350);
}
async function draw(){await drawTo(ctx,pages[active],active,pages.length);document.querySelector('#renderStatus').textContent='所有改动实时预览'}
async function exportPage(p,index){const off=document.createElement('canvas');off.width=W;off.height=H;await drawTo(off.getContext('2d'),p,index,pages.length);return off.toDataURL('image/png')}
function refresh(){updatePageList();renderFields();draw()}
function addPage(type='qa'){pages.push(structuredClone(samples[type]||samples.qa));active=pages.length-1;refresh();scheduleSave();toast(`已添加${labels[type]}模板`)}
async function generateImage(){const promptEl=fields.querySelector('#aiPrompt'),state=fields.querySelector('#generationState'),button=fields.querySelector('#generateImage');const prompt=promptEl.value.trim();if(!prompt){toast('先写下画面描述');promptEl.focus();return}button.disabled=true;button.textContent='正在生成…';state.textContent='正在请求生图服务，通常需要几十秒…';try{const response=await fetch('/api/generate-image',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt})});const data=await response.json();if(!response.ok)throw new Error(data.error||'生成失败');pages[active].image=data.image;state.textContent='画面已生成，Canvas 正在融合文字版式';await draw();scheduleSave();toast('背景素材已生成并应用')}catch(error){state.textContent=error.message;toast(error.message)}finally{button.disabled=false;button.textContent='✳ 生成背景'}}
async function downloadCurrent(){const data=await exportPage(pages[active],active);const a=document.createElement('a');a.href=data;a.download=`${String(active+1).padStart(2,'0')}_${pageName(pages[active])}.png`;a.click()}
async function exportAll(){const button=document.querySelector('#exportAll');button.disabled=true;button.textContent='正在打包…';try{const imageData=[];for(let i=0;i<pages.length;i++)imageData.push({name:pageName(pages[i]),data:await exportPage(pages[i],i)});const res=await fetch('/api/export',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pages:imageData})});if(!res.ok){const error=await res.json();throw new Error(error.error||'导出失败')}const blob=await res.blob(),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='鹅懂个啥_小红书图片.zip';a.click();URL.revokeObjectURL(url);toast('整组图片已导出')}catch(e){toast(e.message)}finally{button.disabled=false;button.innerHTML='<span class="button-icon">↓</span> 导出整组图片'}}
document.querySelectorAll('[data-add-template]').forEach(el=>el.onclick=()=>addPage(el.dataset.addTemplate));document.querySelector('#addPage').onclick=()=>addPage('qa');document.querySelector('#exportAll').onclick=exportAll;document.querySelector('#downloadCurrent').onclick=downloadCurrent;
document.querySelector('#deletePage').onclick=()=>{if(pages.length===1)return toast('至少保留一页');pages.splice(active,1);active=Math.max(0,active-1);refresh();scheduleSave();toast('已删除这一页')};
document.querySelector('#zoomIn').onclick=()=>{zoom=Math.min(100,zoom+5);document.querySelector('#canvasFrame').style.width=`${zoom/80*49}vh`;document.querySelector('#zoomLabel').textContent=`${zoom}%`};document.querySelector('#zoomOut').onclick=()=>{zoom=Math.max(50,zoom-5);document.querySelector('#canvasFrame').style.width=`${zoom/80*49}vh`;document.querySelector('#zoomLabel').textContent=`${zoom}%`};
fetch('/api/config').then(r=>r.json()).then(c=>{if(!c.imageGenerationReady){document.querySelector('#renderStatus').textContent='Canvas 可用 · 配置生图服务以启用 AI 生成'}}).catch(()=>{});
refresh();loadSaved();
