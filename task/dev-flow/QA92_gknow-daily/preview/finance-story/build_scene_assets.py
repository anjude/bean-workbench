"""生成理财人格自有场景 SVG：统一纸色、墨线与色块，文本由页面绘制。"""
from pathlib import Path
root=Path(__file__).resolve().parents[5]/'business-repo/uni-gknow/src/static/illustrations/finance-story'
root.mkdir(parents=True,exist_ok=True)
ink='#294e50'; paper='#fff2d7'; gold='#efbd6d'; teal='#9dc6bf'; terracotta='#cf8f6d'
def rect(x,y,w,h,fill,rx=0):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"/>'
def path(d,fill='none'):return f'<path d="{d}" fill="{fill}"/>'
def circle(x,y,r,fill):return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>'
window=rect(395,180,265,360,'#b6d1cb',90)+path('M527 180V540M395 395H660')+circle(579,268,34,gold)+path('M408 455L463 405 510 451 554 414 642 475V527H408Z','#83aaa2')
plant=path('M81 613Q57 491 92 424Q119 486 87 523Q48 517 40 470Q93 465 88 556Q142 507 148 458Q102 462 87 580',teal)+rect(46,584,88,98,terracotta,12)
goose=path('M244 621Q193 596 212 550Q222 528 249 535L256 456Q259 412 294 413Q337 414 331 451L323 557Q377 554 391 601Q404 654 343 673L266 670Q231 662 244 621Z','#fffaf0')+path('M330 442L366 455 329 467Z',gold)+circle(308,438,4,ink)+path('M261 598Q298 569 325 610M277 672L268 685H297M330 674L336 685H357')
phone=rect(331,489,51,86,ink,9)+rect(337,499,39,62,paper,3)+path('M342 542L350 533 357 537 369 516',terracotta)
sofa=rect(125,541,500,155,teal,39)+rect(99,614,555,112,'#81aca3',30)+path('M141 724L135 757M607 724L615 757M396 568V623')
table=path('M66 781L682 781 735 883H18Z','#d9ae82')+path('M59 883L43 1019M681 883L706 1019')
cup=path('M485 739H540L533 788H492Z',paper)+path('M540 748Q570 747 563 766Q557 779 536 770M498 725Q488 711 503 697M522 725Q512 711 527 697')
scenes={}
scenes['sofa']=window+plant+sofa+goose+phone+table+cup
scenes['night']=window.replace('#b6d1cb','#87a7a4')+plant+rect(120,564,527,145,'#d6b299',27)+rect(92,657,560,112,terracotta,27)+goose+phone+path('M579 437V692M534 693H622M549 340H608L640 441H519Z',gold)+table+cup
lunch=rect(89,162,564,355,'#c7dbca',30)+path('M370 164V515M89 335H653')+path('M107 483L182 407 254 464 309 395 364 465 445 415 511 470 594 419 640 476V515H107Z',teal)+rect(75,586,598,53,'#d8b080',12)+path('M109 639V758M635 639V758')+goose+phone+table+cup+circle(213,830,58,paper)+circle(213,830,37,gold)+path('M120 784L159 860M286 785L263 860')
scenes['lunch']=lunch
monitor=rect(194,300,382,259,teal,20)+rect(214,320,342,212,paper,8)+path('M365 560V614M326 615H436')+path('M243 478L277 451 314 462 349 407 383 430 431 379 469 395 526 355',terracotta)+path('M241 498H527M241 339V498')
book=path('M453 697L600 677 649 763 493 794 362 759 398 680Z',paper)+path('M493 794L453 697M471 716L583 701M481 739L603 720M416 705L443 712M400 724L451 739')
scenes['study']=window+plant+path('M62 632H683L730 820H14Z','#d6b38a')+path('M50 820L37 1040M697 820L713 1040')+monitor+book+cup.replace('485','110').replace('540','165').replace('533','158').replace('492','117')
calendar=rect(90,236,310,300,paper,20)+rect(90,236,310,61,gold,20)+path('M160 217V262M330 217V262')
for row in range(3):
    for col in range(4):calendar+=rect(121+col*67,329+row*62,35,32,teal if (row+col)%3 else '#e4cfaa',5)
calendar+=circle(273,407,29,'none')+path('M535 200V509M466 329H604M482 510H587')
scenes['calendar']=calendar+plant+rect(75,630,598,50,'#d6b38a',15)+goose+phone+table+book
train=rect(0,152,750,498,'#c4d6c5',0)+rect(65,201,620,334,'#a9cbc7',55)+path('M282 201V535M502 201V535')
for x,y,h in [(89,328,153),(150,275,205),(331,316,165),(396,258,223),(541,302,179),(598,340,141)]:train+=rect(x,y,48,h,'#8faaa1',4)
train+=path('M0 151H750M0 584H750M39 152V616M711 152V616')+path('M180 153V248M571 153V248')+rect(152,243,56,48,paper,16)+rect(543,243,56,48,paper,16)+rect(30,637,690,106,teal,25)+path('M58 744V818M691 744V818')+goose+phone+path('M35 850H715M100 924H650')
scenes['train']=train
for name,art in scenes.items():
    ground='#e6d6b9' if name!='night' else '#d9c8ae'
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 1500"><rect width="750" height="1500" fill="{paper}"/><g stroke="{ink}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">{rect(0,877,750,623,ground)}{path("M0 1016H750M0 1217H750M0 1418H750M145 877L75 1500M601 877L684 1500")} {art}</g></svg>'
    (root/f'scene-{name}.svg').write_text(svg)
print(f'生成 {len(scenes)} 张场景 SVG，总大小 {sum((root/f"scene-{n}.svg").stat().st_size for n in scenes)} 字节')

# 封面复用客厅元素，透明底构图，避免裁切桌子和杯子。
cover = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 140 750 650"><g stroke="{ink}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">{window}{plant}{sofa}{goose}{phone}</g></svg>'
(root/'cover-sofa.svg').write_text(cover)

# 回看页复用同一只阿白，移除室内家具，保持封面角色一致。
recap = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="190 395 215 305"><g stroke="{ink}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">{goose}{phone}</g></svg>'
(root/'goose-reflection.svg').write_text(recap)
