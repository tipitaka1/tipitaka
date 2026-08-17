# -*- coding: utf-8 -*-
"""data.bin 을 읽어 경마다 미리보기용 작은 파일을 만든다.

카톡·페북·네이버는 링크를 받으면 그 주소를 직접 열어 og 표를 읽는다.
그런데 `#` 뒤는 서버로 가지 않으므로, `#자따까547` 이든 `#우다나1` 이든
그들 눈에는 모두 같은 첫 화면으로 보인다. 그래서 경마다 실제 주소를 하나씩 만들어 준다.

  s/M_JA_547_04.html  ← 이 파일이 og 표를 지니고, 열리면 곧바로 ../#M_JA_547_04 로 넘긴다

깃허브 액션이 이 스크립트를 돌려 s/ 를 만들고 저장소에 도로 넣는다.
사람이 손댈 일은 없다.
"""
import json, gzip, os, re, html, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, 's')
SITE = os.environ.get('SITE_URL', '').rstrip('/')      # 예: https:/⁠/아이디.github.io/tipitaka

D = json.loads(gzip.decompress(open(os.path.join(ROOT, 'data.bin'), 'rb').read()))

def h32(s):
    """앱(index.html)의 h32 와 똑같아야 한다 — djb2 xor, 36진법"""
    h = 5381
    for ch in s:
        h = ((h * 33) ^ ord(ch)) & 0xFFFFFFFF
    d = '0123456789abcdefghijklmnopqrstuvwxyz'
    if h == 0: return '0'
    o = ''
    while h: h, m = divmod(h, 36); o = d[m] + o
    return o

def ids(docs):
    cnt = {}
    for r, d in docs.items():
        n = d.get('n', ''); i = n.rfind('_')
        c = n[:i] if i > 0 else n
        cnt[c] = cnt.get(c, 0) + 1
    out = {}
    for r, d in docs.items():
        n = d.get('n', ''); i = n.rfind('_')
        c = n[:i] if i > 0 else n
        out[r] = c if (cnt[c] == 1 and c.isascii() and re.fullmatch(r'[!-~]+', c)) else ('x' + h32(r))
    return out

def title(r, d, i):
    n = d.get('n', ''); k = n.rfind('_')
    return (n[:k+1] + d.get('t', '')) if k > 0 else d.get('t', '')

def brief(d):
    """본문에서 앞머리 줄을 걷어 내고 한글 두어 문장을 뽑는다."""
    t = d.get('c', '')
    t = re.sub(r'^#.*$', '', t, flags=re.M)                 # 제목 줄
    t = re.sub(r'^목록 →.*$', '', t, flags=re.M)            # 길잡이 줄
    t = re.sub(r'^##.*$', '', t, flags=re.M)                # 절 이름
    t = re.sub(r'^§.*$', '', t, flags=re.M)                 # 게송 표시
    t = re.sub(r'\[\[([^\]|]+)\]\]', r'\1', t)
    out = []
    for line in t.split('\n'):
        line = line.strip()
        if not line: continue
        if not re.search(r'[가-힣]', line): continue        # 팔리 줄은 건너뛴다
        out.append(line)
        if sum(len(x) for x in out) > 130: break
    s = ' '.join(out)
    return (s[:150] + '…') if len(s) > 150 else s

ID = ids(D['docs'])
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.endswith('.html'): os.remove(os.path.join(OUT, f))

TPL = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t}</title>
<meta name="description" content="{b}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="경율논 3장">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{b}">
<meta property="og:url" content="{u}">
<meta property="og:image" content="{img}">
<meta name="twitter:card" content="summary">
<link rel="canonical" href="../#{i}">
<meta http-equiv="refresh" content="0; url=../#{i}">
<script>location.replace('../#{i}');</script>
<style>body{{font-family:system-ui,sans-serif;margin:3em auto;max-width:34em;padding:0 1em;
line-height:1.8;color:#2a2622;background:#faf7f2}}a{{color:#8a6a3a}}</style>
</head>
<body>
<h1>{t}</h1>
<p>{b}</p>
<p><a href="../#{i}">경율논 3장에서 열기</a></p>
</body>
</html>
"""

n = 0
for r, d in D['docs'].items():
    i = ID[r]
    t = html.escape(title(r, d, i), quote=True)
    b = html.escape(brief(d) or '빠알리 삼장 한글 대역', quote=True)
    u = f'{SITE}/s/{i}.html' if SITE else f's/{i}.html'
    img = f'{SITE}/icon-512.png' if SITE else '../icon-512.png'
    open(os.path.join(OUT, i + '.html'), 'w', encoding='utf-8').write(
        TPL.format(t=t, b=b, u=u, i=i, img=img))
    n += 1
print(f'미리보기 파일 {n:,}개 만듦 → s/')
