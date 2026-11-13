#!/usr/bin/env python3
"""Check static routes, local assets, language switching, and no-data behavior."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin, unquote
import json
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist'
class Page(HTMLParser):
 def __init__(self):super().__init__();self.tags=[]
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
results=[]
for f in sorted(DIST.rglob('index.html')):
 text=f.read_text();p=Page();p.feed(text)
 assert sum(t=='h1' for t,a in p.tags)==1,f'Missing or repeated h1: {f}'
 assert any(t=='html' and a.get('lang') for t,a in p.tags)
 assert not any(t in ['script','form','iframe'] for t,a in p.tags),f'Unexpected external code/input: {f}'
 assert 'mailto:funvalvar@proton.me' in text or f.parent.name not in ['support','privacy']
 assert 'Coming to the App Store' in text or '即将登陆' in text or '即將登陸' in text or f.parent.name in ['support','privacy']
 switches=[a for t,a in p.tags if t=='a' and 'hreflang' in a];assert len(switches)==3
 for t,a in p.tags:
  for attr in ['href','src']:
   val=a.get(attr,'');u=urlparse(val)
   if u.scheme or u.netloc or not u.path:continue
   assert not u.path.startswith('/'),f'Root-relative URL breaks file preview: {val} in {f}'
   assert not u.path.endswith('/'),f'Directory link breaks file preview: {val} in {f}'
   target=(f.parent/u.path).resolve()
   assert target.is_relative_to(DIST.resolve()),f'URL escapes dist: {val} in {f}' 
   assert target.is_file(),f'Broken {val} in {f}'
   # Regression: browser file URLs resolve from the current HTML directory.
   file_url=urlparse(urljoin(f.as_uri(),val))
   assert Path(unquote(file_url.path)).resolve()==target,f'file:// resolves differently: {val} in {f}'
 for token in ['fetch(', 'sendBeacon', 'localStorage', 'document.cookie', 'XMLHttpRequest']:
  assert token not in text, f'Unexpected collection/persistence: {token}'
 canonical=[a['href'] for t,a in p.tags if t=='link' and a.get('rel')=='canonical'];assert len(canonical)==1
 results.append(dict(page=str(f.relative_to(DIST)),language=next(a['lang'] for t,a in p.tags if t=='html'),canonical=canonical[0],status='PASS'))
assert len(results)==9
print(json.dumps(dict(status='PASS',pages=results,limitations='Checks resolve each local href/src relative to its actual page directory, matching file:// and HTTP. Browser and public HTTPS are separate checks.'),ensure_ascii=False,indent=2))
