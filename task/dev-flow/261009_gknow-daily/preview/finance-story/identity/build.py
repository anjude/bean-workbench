from pathlib import Path
import re, shutil
base=Path(__file__).resolve().parents[6]
out=base/'task/dev-flow/261009_gknow-daily/preview/finance-story/identity'
assets=out/'assets'
source=base/'business-repo/uni-gknow/src/static/illustrations/finance-story'
shutil.copy(source/'cover-sofa.svg',assets/'cover-sofa.svg')
ink='#294e50'; gold='#efbd6d'; teal='#9dc6bf'; paper='#fffaf0'
def svg(body,view='0 0 320 280'):
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}"><g stroke="{ink}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>'
def p(d,fill='none'): return f'<path d="{d}" fill="{fill}"/>'
def rect(x,y,w,h,fill,rx=8):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"/>'
def circ(x,y,r,fill):return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>'
goose=p('M91 213Q59 194 76 166Q86 154 105 163L110 94Q113 58 139 59Q173 59 169 91L164 166Q209 163 220 197Q230 232 187 246L112 244Q87 237 91 213Z',paper)+p('M169 82L197 93 168 105Z',gold)+circ(151,80,3,ink)+p('M112 201Q139 178 161 208M116 245L108 255H132M171 246L178 255H196')
arts=[
('rush','抢先上车鹅','别催，我已经在车上了',rect(204,146,88,77,teal)+p('M221 164H274M221 179H259')+circ(220,233,12,gold)+circ(279,233,12,gold)+p('M37 145H68M28 165H57M42 185H64')),
('reserve','留个后手鹅','别急，我还有另一半',rect(207,169,78,65,teal)+p('M246 169V234')+circ(226,145,17,gold)+circ(268,145,17,paper)+p('M218 145H233M261 145H275')),
('promise','按约办事鹅','我先跟昨天的自己对一下账',rect(205,111,84,124,paper)+rect(224,103,45,19,gold)+p('M217 150L225 158 239 141M248 151H275M217 184L225 192 239 175M248 185H275M217 217H269')),
('reason','认理由鹅','先别报涨跌，告诉我为什么',rect(202,139,74,96,paper)+p('M214 160H260M214 177H249M214 194H259')+circ(258,122,28,teal)+p('M277 143L299 171M245 121L255 130 272 111')),
('price','心里有个价鹅','道理我懂，先等它回到那个价',rect(210,154,76,81,paper)+p('M217 178H279M221 218L237 201 252 211 273 189')+p('M210 123L262 108 286 140 233 155Z',gold)+circ(225,127,3,ink)),
('wind','借个风向鹅','等等，我问个人',p('M246 92V246M227 246H267')+p('M247 99L292 116 247 137Z',teal)+p('M194 73H229M211 55H248')+rect(207,162,65,46,paper)+p('M222 208L217 222 242 208',paper)+circ(221,184,2,ink)+circ(239,184,2,ink)+circ(257,184,2,ink)),
('close','收工落袋鹅','这局先到这，下一局再说',p('M218 154L208 126H274L264 154Q301 191 278 227Q246 246 216 226Q194 197 218 154Z',teal)+p('M218 154H264')+rect(228,185,36,23,gold)+p('M34 101L48 115 74 87'))]
for key,name,line,prop in arts:
 (assets/f'{key}.svg').write_text(svg('<ellipse cx="169" cy="258" rx="124" ry="10" fill="#e8ddc7" stroke="none"/>'+prop+goose))
logo=rect(6,6,116,116,'#e2e9da',34)+p('M32 92Q23 75 40 66L44 38Q47 19 64 23Q82 26 78 42L75 66Q102 63 104 84Q105 105 78 106H51Q34 105 32 92Z',paper)+p('M79 36L98 45 78 52Z',gold)+circ(67,35,2,ink)+p('M49 85Q63 70 76 88')
(assets/'mark.svg').write_text(svg(logo,'0 0 128 128'))
print(assets)
