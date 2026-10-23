const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict')
const {chromium}=require('playwright')
const project=path.resolve(__dirname,'../../../../../business-repo/uni-gknow')
const ts=require(path.join(project,'node_modules/typescript'))
const source=fs.readFileSync(path.join(project,'src/components/gk-result-poster.vue'),'utf8')
const wrapped=source.slice(source.indexOf('function drawWrappedText('),source.indexOf('\nfunction drawPoster('))
const paper=source.slice(source.indexOf('function drawPaperPoster('),source.indexOf('\nfunction closePoster('))
const functions=ts.transpileModule(wrapped+'\n'+paper,{compilerOptions:{target:ts.ScriptTarget.ES2020}}).outputText
;(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'})
 try{
  const page=await browser.newPage({viewport:{width:630,height:1000}})
  await page.goto('http://127.0.0.1:5198/?screen=result&still=1')
  const variants=[['single','抢先上车鹅','先上车，别又看着它涨','别催，我已经在车上了','rush'],['mixed','两种反应，都挺像你','抢先上车鹅 × 心里有个价鹅','我的理财反应，还不止一面','mark']]
  for(const [name,title,subtitle,description,art]of variants){
   const checks=await page.evaluate(async({functions,title,subtitle,description,art})=>{
    document.body.innerHTML='<canvas width="630" height="1000"></canvas>';document.body.style.margin='0'
    const canvas=document.querySelector('canvas');const context=canvas.getContext('2d');const failures=[]
    const image=new Image();image.src=`/static/illustrations/finance-story/identity/${art}.png`;await image.decode()
    const logo=new Image();logo.src='/static/illustrations/finance-story/identity/mark.png';await logo.decode()
    const qr=new Image();qr.src='/static/illustrations/finance-story/identity/mark.png';await qr.decode()
    let draws=0
    const bridge={setFillStyle:value=>context.fillStyle=value,setStrokeStyle:value=>context.strokeStyle=value,setLineWidth:value=>context.lineWidth=value,setTextAlign:value=>context.textAlign=value,setFontSize:value=>context.font=`${value}px "PingFang SC",sans-serif`,draw:(_,callback)=>callback(),drawImage:(src,x,y,w,h)=>{draws++;context.drawImage(src==='image'?image:src==='logo'?logo:qr,x,y,w,h)},fillText:(text,x,y)=>{const width=context.measureText(text).width;if(x-width/2<30||x+width/2>600||y>960)failures.push(text);context.fillText(text,x,y)}}
    const ctx=new Proxy(bridge,{get:(target,key)=>key in target?target[key]:context[key].bind(context)})
    const render=new Function('props',functions+'; return drawPaperPoster;')({title,subtitle,description})
    await render(ctx,{path:'image',width:image.naturalWidth,height:image.naturalHeight},'qr',{path:'logo'})
    return {failures,draws}
   },{functions,title,subtitle,description,art})
   assert.deepEqual(checks,{failures:[],draws:3})
   await page.screenshot({path:path.join(__dirname,'ui/stock-full',`poster-${name}.png`)})
  }
  console.log('PASS: 复用真实纸面海报绘制函数，单型/双型文字边界与PNG插画绘制')
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)})
