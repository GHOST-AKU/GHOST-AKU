#!/usr/bin/env python3
"""Render a self-contained, pixel-lettered SVG status card from public GitHub data.

Usage:
  python scripts/update_status.py           # query public GitHub REST API
  python scripts/update_status.py --offline # create placeholder, no network

GITHUB_TOKEN is optional for public data, but recommended for scheduled runs.
"""
import argparse
import datetime as dt
import html
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'live-status.svg'
USER = 'GHOST-AKU'

# Original 5x7 bitmap glyphs. Every glyph becomes SVG rects (no remote fonts).
GLYPHS = {
' ':['00000']*7,
'A':['01110','10001','10001','11111','10001','10001','10001'],
'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],
'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'F':['11111','10000','10000','11110','10000','10000','10000'],
'G':['01111','10000','10000','10111','10001','10001','01111'],
'H':['10001','10001','10001','11111','10001','10001','10001'],
'I':['11111','00100','00100','00100','00100','00100','11111'],
'J':['00111','00010','00010','00010','10010','10010','01100'],
'K':['10001','10010','10100','11000','10100','10010','10001'],
'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],
'N':['10001','11001','10101','10011','10001','10001','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],
'P':['11110','10001','10001','11110','10000','10000','10000'],
'Q':['01110','10001','10001','10001','10101','10010','01101'],
'R':['11110','10001','10001','11110','10100','10010','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'T':['11111','00100','00100','00100','00100','00100','00100'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'V':['10001','10001','10001','10001','10001','01010','00100'],
'W':['10001','10001','10001','10101','10101','10101','01010'],
'X':['10001','10001','01010','00100','01010','10001','10001'],
'Y':['10001','10001','01010','00100','00100','00100','00100'],
'Z':['11111','00001','00010','00100','01000','10000','11111'],
'0':['01110','10011','10101','10101','10101','11001','01110'],
'1':['00100','01100','00100','00100','00100','00100','01110'],
'2':['01110','10001','00001','00110','01000','10000','11111'],
'3':['11110','00001','00001','01110','00001','00001','11110'],
'4':['10010','10010','10010','11111','00010','00010','00010'],
'5':['11111','10000','10000','11110','00001','00001','11110'],
'6':['01110','10000','10000','11110','10001','10001','01110'],
'7':['11111','00001','00010','00100','00100','01000','01000'],
'8':['01110','10001','10001','01110','10001','10001','01110'],
'9':['01110','10001','10001','01111','00001','00001','01110'],
':':['00000','00100','00100','00000','00100','00100','00000'],
'.':['00000','00000','00000','00000','00000','01100','01100'],
'-':['00000','00000','00000','11111','00000','00000','00000'],
'_':['00000','00000','00000','00000','00000','00000','11111'],
'/':['00001','00001','00010','00100','01000','10000','10000'],
'+':['00000','00100','00100','11111','00100','00100','00000'],
'?':['01110','10001','00001','00010','00100','00000','00100'],
'!':['00100','00100','00100','00100','00100','00000','00100'],
'>':['10000','01000','00100','00010','00100','01000','10000'],
'[':['01110','01000','01000','01000','01000','01000','01110'],
']':['01110','00010','00010','00010','00010','00010','01110'],
}

def pixel(text, x, y, scale=3, color='#e8f5ff'):
    result = []
    for n,ch in enumerate(str(text).upper()):
        rows=GLYPHS.get(ch,GLYPHS['?'])
        for gy,row in enumerate(rows):
            run_start=None
            for gx in range(6):
                active = gx<5 and row[gx]=='1'
                if active and run_start is None: run_start=gx
                if run_start is not None and not active:
                    # A horizontal run of pixels drawn as one rect.
                    result.append(f'<rect x="{x+(n*6+run_start)*scale}" y="{y+gy*scale}" width="{(gx-run_start)*scale}" height="{scale}" fill="{color}"/>')
                    run_start=None
    return '\n'.join(result)

def api(path, token):
    req=urllib.request.Request('https://api.github.com'+path,headers={
        'Accept':'application/vnd.github+json',
        'User-Agent':'GHOST-AKU-pixel-profile',
        'X-GitHub-Api-Version':'2022-11-28',
        **({'Authorization':'Bearer '+token} if token else {})
    })
    with urllib.request.urlopen(req,timeout=20) as r:
        return json.load(r)

def get_live():
    token=os.getenv('GITHUB_TOKEN','')
    repos=[]
    for page in range(1,12):
        chunk=api(f'/users/{USER}/repos?per_page=100&page={page}&type=owner',token)
        if not isinstance(chunk,list):raise RuntimeError('Unexpected GitHub API response')
        repos.extend(chunk)
        if len(chunk)<100:break
    if not repos: raise RuntimeError('No public repos found; refusing to replace card with zeros')
    # Public GitHub API does not include private repositories, by design.
    latest=max(repos,key=lambda r:(r.get('pushed_at') or ''))
    pushed=latest.get('pushed_at') or ''
    return {
        'repos':str(len(repos)),
        'stars':str(sum(int(r.get('stargazers_count') or 0) for r in repos)),
        'latest':str(latest.get('name','UNKNOWN')).upper()[:30],
        'pushed':pushed[:10] if pushed else 'UNKNOWN',
        'sync':dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
    }

def build(data):
    repos=data['repos'];stars=data['stars'];latest=data['latest'];pushed=data['pushed'];sync=data['sync']
    # Avoid embedding arbitrary content without escaping: all variables are rendered as pixels.
    pieces=['''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="240" viewBox="0 0 960 240" role="img" aria-labelledby="title desc">
<title id="title">GHOST-AKU live GitHub status</title>
<desc id="desc">Public repos: '''+html.escape(repos)+'''; total repository stars: '''+html.escape(stars)+'''; latest public repository push: '''+html.escape(latest)+''' '''+html.escape(pushed)+'''; refreshed '''+html.escape(sync)+'''.</desc>
<rect width="960" height="240" fill="#090f22"/>
<defs><pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#131b35" stroke-width="1"/></pattern></defs>
<rect width="960" height="240" fill="url(#grid)"/>
<rect x="13" y="12" width="934" height="216" fill="none" stroke="#31456c" stroke-width="4"/>
<rect x="28" y="27" width="904" height="48" fill="#111a37"/>
<rect x="28" y="83" width="440" height="99" fill="#14213f" stroke="#5deaf8" stroke-width="2"/>
<rect x="480" y="83" width="452" height="99" fill="#14213f" stroke="#ff569b" stroke-width="2"/>
<rect x="28" y="189" width="904" height="29" fill="#111a37"/>
''']
    pieces.append(pixel('LIVE TELEMETRY',47,36,4,'#65e4b7'))
    pieces.append(pixel('AUTO SYNC',734,43,3,'#ffe186'))
    pieces.append(pixel('PUBLIC REPOS',49,95,3,'#94a6d4'))
    pieces.append(pixel(repos,53,122,7,'#5deaf8'))
    pieces.append(pixel('TOTAL STARS',501,95,3,'#94a6d4'))
    pieces.append(pixel(stars,504,122,7,'#ff569b'))
    bottom=f'LATEST PUSH: {latest} / {pushed}'
    if len(bottom)>63: bottom=bottom[:60]+'...'
    pieces.append(pixel(bottom,44,196,2,'#e8f5ff'))
    pieces.append('<rect x="902" y="40" width="12" height="12" fill="#65e4b7"/>')
    pieces.append('</svg>\n')
    return '\n'.join(pieces)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--offline',action='store_true',help='Generate a first-run placeholder without API access')
    args=parser.parse_args()
    if args.offline:
        data={'repos':'--','stars':'--','latest':'AWAITING FIRST SYNC','pushed':'--','sync':'NOT YET'}
    else:
        try: data=get_live()
        except (urllib.error.URLError,ValueError,RuntimeError) as e:
            print('GitHub data sync failed; existing card preserved: '+str(e),file=sys.stderr)
            return 1
    OUT.parent.mkdir(exist_ok=True)
    output=build(data)
    # Don't commit merely because the timestamp changed when stats haven't changed.
    # A successful run still refreshes the UTC timestamp so visitors know data age.
    OUT.write_text(output,encoding='utf-8')
    print('Wrote',OUT, 'with data',data)
    return 0

if __name__=='__main__':raise SystemExit(main())
