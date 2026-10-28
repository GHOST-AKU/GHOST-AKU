#!/usr/bin/env python3
"""Generate original looping 8-bit GIFs for the GHOST-AKU profile README.
Requires Pillow: pip install pillow. No network or external assets.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, random

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)
S = 2
P = {'bg': '#090f22','dark':'#101832','indigo':'#19264a', 'mid':'#26365f',
     'light':'#344972','pink':'#ff569b','cyan':'#5deaf8','yellow':'#ffe186',
     'white':'#e8f5ff','green':'#65e4b7','muted':'#94a6d4','purple':'#986df0',
     'skin':'#f3c7ae','black':'#090e19'}

FONTS=[
  '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
  '/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf',
  '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
]
def font(sz):
    for path in FONTS:
        try: return ImageFont.truetype(path, sz)
        except OSError: pass
    return ImageFont.load_default()

def text(draw, pos, val, size=9, fill=None, shadow=None, spacing=0):
    x,y=pos
    if shadow:
        draw.text((x+2,y+2), val, font=font(size), fill=shadow, spacing=spacing)
    draw.text((x,y), val, font=font(size), fill=fill or P['white'], spacing=spacing)

def rect(d, xy, c): d.rectangle(xy, fill=c)
def border(d, box, c, thickness=1):
    for k in range(thickness): d.rectangle((box[0]+k,box[1]+k,box[2]-k,box[3]-k),outline=c)

def stars(d,t,maxy=170):
    rng=random.Random(60217)
    for i in range(54):
        x=rng.randrange(17,460); y=rng.randrange(18,maxy)
        if x<306 and 31<y<143: continue
        if x>376 and 38<y<96: continue
        tw=(i*7+t//2)%11
        col=P['cyan'] if tw == 0 else (P['muted'] if tw in (3,6) else P['mid'])
        d.point((x,y),fill=col)
        if tw==0:
            d.line((x-2,y,x+2,y),fill=col);d.line((x,y-2,x,y+2),fill=col)

def city(d,t):
    rng=random.Random(2807)
    # distant city silhouette
    distant=[(260,137,20,70),(280,112,33,95),(311,145,26,65),(339,121,34,85),
             (369,108,23,96),(389,130,36,78),(420,112,32,91),(454,144,20,63)]
    for x,y,w,h in distant:
        rect(d,(x,y,x+w,203),P['dark'])
        rect(d,(x,y,x+w,y+2),P['mid'])
        for wy in range(y+9,199,10):
            for wx in range(x+5,x+w-3,8):
                if rng.random()>.43:
                    c=P['pink'] if (wx+wy+t//3)%19==0 else ('#314c77' if (wx+wy)%4 else '#47648d')
                    rect(d,(wx,wy,wx+2,wy+3),c)
    # near foreground stacked buildings
    rect(d,(305,163,360,210), '#141b37')
    rect(d,(305,163,360,164),P['purple'])
    for yy in range(173,201,8):
        for xx in range(314,356,9):
            if (xx+yy+t//5)%6:
                rect(d,(xx,yy,xx+3,yy+3),'#435887')
    rect(d,(433,152,475,211),'#121c37')
    for yy in range(162,203,10):
        for xx in range(439,470,10):
            rect(d,(xx,yy,xx+3,yy+3),P['yellow'] if (xx+yy+t)%23<3 else '#314b6e')
    # neon shop
    rect(d,(322,140,367,158),P['pink'])
    rect(d,(324,142,365,156),P['bg'])
    text(d,(330,144),'NIM4',9,P['cyan'] if t%12<9 else P['pink'])

def sprite(d,x,y,t):
    # Ground shadow, boots
    rect(d,(x-12,y+35,x+15,y+37),'#070c19')
    rect(d,(x-8,y+27,x-2,y+34),P['black'])
    rect(d,(x+4,y+27,x+10,y+34),P['black'])
    rect(d,(x-9,y+32,x-1,y+35),P['light'])
    rect(d,(x+3,y+32,x+12,y+35),P['light'])
    # Hoodie and sleeves
    rect(d,(x-11,y+6,x+13,y+29),'#050912')
    rect(d,(x-13,y+11,x-9,y+25),'#0a1225')
    rect(d,(x+11,y+10,x+15,y+23),'#0a1225')
    rect(d,(x-8,y+14,x-7,y+25),P['indigo'])
    rect(d,(x+8,y+15,x+9,y+26),P['indigo'])
    rect(d,(x-10,y-6,x+10,y+12),'#090d18') # hood
    rect(d,(x-7,y-4,x+7,y+9),'#f0c3ae') # face
    # hair/fringe with side split
    rect(d,(x-8,y-6,x+8,y-1),'#080c19')
    rect(d,(x-6,y-2,x+2,y+1),'#080c19')
    rect(d,(x+5,y-2,x+8,y+4),'#080c19')
    if t%18 != 12:
        d.point((x-3,y+4),fill=P['black']);d.point((x+4,y+4),fill=P['black'])
    else:
        d.line((x-4,y+5,x-2,y+5), fill=P['black']);d.line((x+3,y+5,x+5,y+5),fill=P['black'])
    d.point((x+5,y+8),fill='#ac6677') # tiny mole
    # phone glowing in hand
    rect(d,(x+13,y+15,x+18,y+24),P['cyan'])
    rect(d,(x+14,y+16,x+17,y+22),'#0c5d75')
    if t%4<2:
        d.line((x+19,y+13,x+23,y+10),fill=P['cyan'])

def draw_hero(t):
    im=Image.new('RGB',(480,248),P['bg']); d=ImageDraw.Draw(im)
    # full-screen HUD grid and outer chrome
    for x in range(8,480,20):
        d.line((x,0,x,247),fill='#10172c')
    for y in range(8,248,20):
        d.line((0,y,479,y),fill='#10172c')
    border(d,(7,7,472,240),P['indigo'],2)
    rect(d,(12,12,467,27),P['dark'])
    text(d,(22,15),'[  PLAYER PROFILE  ]',9,P['green'])
    text(d,(345,15),'LEVEL 99',9,P['yellow'])
    rect(d,(459,17,462,21),P['green'] if t%10 < 7 else P['dark'])
    stars(d,t,160)
    # moon + orbiting star
    d.ellipse((401,43,444,86), fill='#2a3557')
    d.ellipse((406,42,444,82), fill=P['yellow'])
    d.ellipse((419,38,450,72), fill=P['bg'])
    if t%10<5:
        d.line((390,59,399,59),fill=P['cyan']);d.line((394,55,394,63),fill=P['cyan'])
    city(d,t)
    # subtle scrolling pixel rain, especially over the city skyline
    rainy=random.Random(1914)
    for k in range(18):
        rx=rainy.randrange(270,466)
        ry=30+(rainy.randrange(170)+t*9+k*3)%170
        d.line((rx,ry,rx-1,ry+5),fill='#29466b')
    # foreground rooftop
    rect(d,(274,204,474,226),'#151d39')
    rect(d,(272,202,475,205),P['cyan'])
    for x in range(285,468,16): rect(d,(x,210,x+6,212),P['mid'])
    # standing character + pet drone
    sprite(d,401,165+ (1 if t%12 in (4,5) else 0),t)
    drone_x=371+int(4*math.sin(t*.32));drone_y=164+int(5*math.sin(t*.35))
    rect(d,(drone_x-5,drone_y-3,drone_x+5,drone_y+3),P['purple'])
    rect(d,(drone_x-3,drone_y-2,drone_x+3,drone_y+1),P['bg'])
    d.point((drone_x+1,drone_y),fill=P['pink'])
    d.line((drone_x-3,drone_y-5,drone_x+3,drone_y-5),fill=P['cyan'])
    # hero title and shadows
    text(d,(24,45),'GHOST_AKU',36,P['white'],P['pink'])
    rect(d,(26,92,169,94),P['cyan'])
    rect(d,(172,92,205,94),P['pink'])
    text(d,(27,104),'AI DEVELOPER / WRITER',12,P['cyan'])
    text(d,(27,122),'REALITY IS AN',12,P['white'])
    text(d,(27,138),'OPEN SOURCE PROJECT.',11,P['yellow'])
    # scanline on name, tiny glitch, sparingly
    if t in (7,8,17):
        rect(d,(27,66,178,67),P['pink'])
        rect(d,(61,70,170,70),P['cyan'])
    # quest dialogue box, slightly above bottom border
    rect(d,(20,172,270,224), '#060d1f')
    border(d,(20,172,270,224),P['cyan'],1)
    rect(d,(25,177,265,190),P['indigo'])
    text(d,(31,179),'> ACTIVE QUEST',9,P['yellow'])
    text(d,(31,196),'BUILDING NEARBYIM',11,P['green'])
    d.rectangle((211,197,216,203),fill=P['cyan'] if t%6<3 else P['pink'])
    for j in range(18):
        c=P['cyan'] if j<6+(t//3)%11 else P['mid']
        rect(d,(31+j*12,212,40+j*12,216),c)
    # bottom status line
    text(d,(22,229),'PRESS START',8,P['muted'])
    text(d,(329,229),'[ 2026 // AKU ]',8,P['muted'])
    return im.resize((960,496),Image.Resampling.NEAREST)

def draw_projects(t):
    im=Image.new('RGB',(480,116),P['bg']); d=ImageDraw.Draw(im)
    border(d,(6,5,473,110),P['indigo'],2)
    text(d,(19,12),'SELECT A WORLD',14,P['yellow'])
    text(d,(361,18),'1P   0003',8,P['muted'])
    projects=[('01','WOZAI / NEARBYIM','LOCAL-FIRST MESSAGING',P['cyan']),
              ('02','OGOP / OPEN GAMING','OWNERSHIP PROTOCOL',P['pink']),
              ('03','AI TRAINING ARCADE','LEARNING, PLAYFULLY',P['green'])]
    active=(t//10)%3
    for i,(idx,name,tag,col) in enumerate(projects):
        y=35+i*23
        if i==active:
            rect(d,(17,y-3,460,y+19),P['indigo']);border(d,(17,y-3,460,y+19),col)
            text(d,(22,y+1),'►',11,col)
            text(d,(48,y),idx,11,P['yellow'])
            text(d,(78,y),name,11,P['white'])
            text(d,(313,y+3),tag,6,col)
        else:
            text(d,(48,y),idx,11,P['muted'])
            text(d,(78,y),name,11,P['muted'])
            text(d,(313,y+3),tag,6,P['muted'])
    return im.resize((960,232),Image.Resampling.NEAREST)

def draw_footer(t):
    im=Image.new('RGB',(480,70),P['bg']);d=ImageDraw.Draw(im)
    border(d,(6,5,473,64),P['indigo'],2)
    for i in range(12):
        x=23+i*37
        if (i+t)%5==0:
            d.line((x,16,x+3,16),fill=P['pink'])
            d.line((x+1,14,x+1,18),fill=P['pink'])
    text(d,(32,19),'CONTINUE?',17,P['white'])
    text(d,(198,23),'[ YES ]',12,P['green'] if t%10<7 else P['indigo'])
    text(d,(302,23),'[ STAR ]',12,P['yellow'] if t%10<7 else P['muted'])
    text(d,(32,49),'INSERT CURIOSITY TO PLAY',8,P['muted'])
    return im.resize((960,140),Image.Resampling.NEAREST)

def save_gif(name,frames,duration):
    # Adaptive global palette gives crisp rendering and efficient full-frame GIFs.
    frames=[f.quantize(colors=96,method=Image.Quantize.MEDIANCUT) for f in frames]
    file=OUT/name
    frames[0].save(file,save_all=True,append_images=frames[1:],duration=duration,loop=0,optimize=True,disposal=2)
    print(file,round(file.stat().st_size/1024),'KiB')

if __name__=='__main__':
    save_gif('hero.gif',[draw_hero(i) for i in range(30)],95)
    save_gif('worlds.gif',[draw_projects(i) for i in range(30)],170)
    save_gif('continue.gif',[draw_footer(i) for i in range(20)],125)
    draw_hero(3).save(ROOT/'preview.png')
