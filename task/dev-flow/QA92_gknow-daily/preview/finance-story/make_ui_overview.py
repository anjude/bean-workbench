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
print(json.dumps({'screens':len(screens),'size':[width,height]},ensure_ascii=False))
