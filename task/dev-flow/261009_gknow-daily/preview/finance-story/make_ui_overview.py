"""从真实页面截图生成理财人格总览；旧鹅湾夜航总览保留在 archive/goose-voyage。"""
from pathlib import Path
import json,html,math
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parent
screens=json.loads((root/'ui/screens.json').read_text())
columns=4;tile_w=230;gap=24;margin=40;header=145;caption=37;row_gap=46
first=Image.open(root/'ui'/screens[0]['file'])
tile_h=round(tile_w*first.height/first.width)
rows=math.ceil(len(screens)/columns)
width=margin*2+tile_w*columns+gap*(columns-1)
height=header+rows*(tile_h+caption+row_gap)+35
canvas=Image.new('RGB',(width,height),'#f2eee6');draw=ImageDraw.Draw(canvas)
font=lambda size:ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',size)
draw.text((margin,32),'理财人格 / 投资小现场',font=font(35),fill='#294e50')
draw.text((margin,88),'共13题 · 先选投资经验 · 三条路线 · 选完直接切题',font=font(19),fill='#657d73')
for index,item in enumerate(screens):
    x=margin+(index%columns)*(tile_w+gap);y=header+(index//columns)*(tile_h+caption+row_gap)
    draw.text((x,y),f'{index+1:02d}  {item["title"]}',font=font(16),fill='#294e50')
    picture=Image.open(root/'ui'/item['file']).convert('RGB').resize((tile_w,tile_h),Image.Resampling.LANCZOS)
    canvas.paste(picture,(x,y+caption))
draw.text((margin,height-33),'真实 Vue 页面截图；浏览器预览与小程序共用题库、分支和结果逻辑。',font=font(17),fill='#657d73')
canvas.save(root/'ui-overview.png')
items=''.join(f'<a class="screen" href="/?screen={html.escape(item["screen"],quote=True)}&still=1"><span>{index+1:02d}　{html.escape(item["title"])}</span><img src="ui/{html.escape(item["file"])}" alt="{html.escape(item["title"])}" loading="lazy"></a>' for index,item in enumerate(screens))
page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>理财人格 · UI 总览</title><style>*{box-sizing:border-box}body{margin:0;padding:32px;background:#f2eee6;color:#294e50;font-family:-apple-system,'PingFang SC',sans-serif}main{max-width:1300px;margin:auto}h1{font-size:32px;margin:0 0 12px}p{color:#657d73;line-height:1.8}nav{display:flex;gap:22px;flex-wrap:wrap;margin:24px 0 30px}a{color:#9b603e}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:32px 22px}.screen{color:inherit;text-decoration:none;min-width:0}.screen span{display:block;font-size:14px;line-height:1.6;margin-bottom:10px}img{display:block;width:100%;border:1px solid #bdbdae;border-radius:10px;box-shadow:0 4px 12px #294e5018}@media(max-width:800px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:450px){body{padding:24px 16px}h1{font-size:26px}.grid{gap:24px 12px}.screen span{font-size:12px}}</style></head><body><main><h1>理财人格 / 投资小现场</h1><p>共13题，包含1题投资经验和12题场景。按熟悉程度出题，选完直接进入下一题。<br>点击缩略图打开对应的真实可玩状态；回到开场可体验完整一轮。</p><nav><a href="/">从头玩一轮 →</a><a href="ui-overview.png" target="_blank">打开完整总览图</a><a href="archive/goose-voyage/ui-overview.html">原鹅湾夜航视觉参考</a></nav><div class="grid">'''+items+'</div></main></body></html>'
(root/'ui-overview.html').write_text(page)
print(json.dumps({'screens':len(screens),'size':[width,height]},ensure_ascii=False))
