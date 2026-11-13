#!/usr/bin/env python3
"""Build all nine static pages. Python 3 standard library only; no network."""
from pathlib import Path
from html import escape as e
import json, shutil, posixpath, re
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'src';OUTPUT=ROOT
CSP="script-src 'none'; connect-src 'none'; object-src 'none'; base-uri 'none'"
content=json.loads((SRC/'content.json').read_text());cfg=json.loads((SRC/'config.json').read_text())
def route(locale,kind='home'):
 prefix=content[locale]['prefix'];return '/'+prefix+('' if kind=='home' else kind+'/')
def portable_links(html, page):
 # Explicit relative index files work with file://, HTTP, and subdirectory hosting.
 # Canonical/alternate/Open Graph URLs remain absolute public URLs.
 def replace(match):
  attribute, target = match.groups()
  filename = target.lstrip('/') + ('index.html' if target.endswith('/') else '')
  relative = posixpath.relpath(filename, start=page.strip('/') or '.')
  return f'{attribute}="{relative}"'
 return re.sub(r'\b(href|src)="(/[^"\s]*)"', replace, html)

def document(locale,kind):
 c=content[locale];base=route(locale);page=route(locale,kind);title=c['name'] if kind=='home' else c[kind]+' · '+c['name'];desc=c['intro'] if kind=='home' else c['support_intro'] if kind=='support' else c['policy_intro']
 alt=''.join(f'<link rel="alternate" hreflang="{d["lang"]}" href="{cfg["origin"]}{route(l,kind)}">' for l,d in content.items())
 languages=''.join(f'<a href="{route(l,kind)}" lang="{content[l]["lang"]}" hreflang="{content[l]["lang"]}"'+(' aria-current="page"' if l==locale else '')+f'>{label}</a>' for l,label in [('en-US','EN'),('zh-Hans','简'),('zh-Hant','繁')])
 nav=''.join(f'<a href="{route(locale,k)}"'+(' aria-current="page"' if kind==k else '')+f'>{c[k]}</a>' for k in ['support','privacy'])
 header=f'<a class="skip" href="#main">{c["skip"]}</a><header class="masthead wrap"><a class="brand" href="{base}"><img src="/assets/icon-192.png" alt="" width="48" height="48"><span>{c["name"]}</span></a><nav aria-label="{c["home"]}">{nav}</nav><div class="languages" aria-label="{c["languages"]}">{languages}</div></header>'
 email=f'<a class="email" href="mailto:{cfg["supportEmail"]}">{cfg["supportEmail"]} <span aria-hidden="true">↗</span></a>'
 if kind=='home':
  hero=''.join(x+'<br>' for x in c['headline'])[:-4]
  shot=f'/assets/{locale}-route-level10.png'
  cta=f'<a class="store" href="{cfg["appStoreURL"]}">App Store <span aria-hidden="true">↗</span></a>' if cfg['released'] else f'<span class="store coming"><span class="status-dot" aria-hidden="true"></span>{c["coming"]}</span>'
  steps=''.join(f'<article class="step"><span class="step-number">0{i+1}</span><h3>{e(s[0])}</h3><p>{e(s[1])}</p></article>' for i,s in enumerate(c['steps']))
  features=''.join(f'<li><span aria-hidden="true">✓</span> {x}</li>' for x in c['features'])
  body=f'''<main id="main"><section class="hero wrap"><div class="hero-copy"><p class="eyebrow">{c['eyebrow']}</p><h1>{hero}</h1><p class="intro">{c['intro']}</p>{cta}<p class="trial">{c['trial']}</p><a class="text-link" href="#how">{c['how_title']} <span aria-hidden="true">↓</span></a></div><figure class="game-figure"><div class="game-frame"><img fetchpriority="high" src="{shot}" width="1320" height="2868" alt="{c['screenshot_alt']}"></div><figcaption>{c['caption']}</figcaption></figure></section><section id="how" class="how wrap"><p class="eyebrow">{c['how_label']}</p><h2>{c['how_title']}</h2><div class="steps">{steps}</div></section><section class="journey wrap"><div class="journey-head"><div><p class="eyebrow">{c['level_label']}</p><h2>{c['level_title']}</h2></div><p>{c['level_body']}</p></div><div class="level-range"><div><strong>01—12</strong><span>{c['free']}</span></div><span class="range-plus" aria-hidden="true">+</span><div><strong>13—60</strong><span>{c['paid']}</span></div></div><p class="purchase">{c['purchase']}</p><ul class="features">{features}</ul><p class="offline">{c['offline']}</p></section><section class="help wrap"><div><h2>{c['help_title']}</h2><p>{c['help_body']}</p></div><a class="button" href="{route(locale,'support')}">{c['help_cta']} <span aria-hidden="true">↗</span></a></section></main>'''
 elif kind=='support':
  faq=''.join(f'<details'+(' open' if i==0 else '')+f'><summary>{e(q)}</summary><p>{e(a)}</p></details>' for i,(q,a) in enumerate(c['faq']))
  body=f'<main id="main" class="reading wrap"><p class="eyebrow">{c["name"]} / {c["support"]}</p><h1>{c["support"]}</h1><p class="lead">{c["support_intro"]}</p><div class="faq">{faq}</div><section class="contact"><h2>{c["contact_title"]}</h2><p>{c["contact_body"]}</p>{email}</section></main>'
 else:
  policy=''.join(f'<section><h2>{e(h)}</h2><p>{e(p)}</p></section>' for h,p in c['policy'])
  apple_label='Apple Privacy Policy' if locale=='en-US' else 'Apple 隐私政策' if locale=='zh-Hans' else 'Apple 隱私權政策'
  body=f'<main id="main" class="reading policy wrap"><p class="eyebrow">{c["policy_date"]}</p><h1>{c["privacy"]}</h1><p class="lead">{c["policy_intro"]}</p>{policy}<p><a href="https://www.apple.com/legal/privacy/">{apple_label} ↗</a></p>{email}</main>'
 footer=f'<footer class="footer wrap"><a class="wordmark" href="{base}">{c["name"]}</a><p>© {cfg["year"]} {cfg["developer"]}</p><div><a href="{route(locale,"support")}">{c["support"]}</a><a href="{route(locale,"privacy")}">{c["privacy"]}</a></div></footer>'
 return portable_links(f'''<!doctype html>
<html lang="{c['lang']}"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="{CSP}"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#FCF3E9"><title>{title}</title><meta name="description" content="{e(desc,quote=True)}"><link rel="canonical" href="{cfg['origin']}{page}">{alt}<link rel="alternate" hreflang="x-default" href="{cfg['origin']}{route('en-US',kind)}"><meta property="og:title" content="{title}"><meta property="og:description" content="{e(desc,quote=True)}"><meta property="og:type" content="website"><meta property="og:url" content="{cfg['origin']}{page}"><meta property="og:image" content="{cfg['origin']}/assets/icon-1024.png"><link rel="icon" type="image/png" href="/assets/favicon.png"><link rel="apple-touch-icon" href="/assets/icon-192.png"><link rel="stylesheet" href="/assets/style.css"></head><body><!--email_off-->{header}{body}{footer}<!--/email_off--></body></html>''', page)
OUTPUT.mkdir(exist_ok=True)
for locale in content:
 for kind in ['home','support','privacy']:
  p=OUTPUT/route(locale,kind).lstrip('/')/'index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(document(locale,kind))
shutil.copy2(SRC/'style.css',OUTPUT/'assets/style.css')
urls=[cfg['origin']+route(l,k) for l in content for k in ['home','support','privacy']]
(OUTPUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+u+'</loc></url>' for u in urls)+'</urlset>\n')
(OUTPUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+cfg['origin']+'/sitemap.xml\n')
# Inline styling and an absolute home link also work at deep missing URLs.
style=(SRC/'style.css').read_text()
(OUTPUT/'404.html').write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="{CSP}"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><meta name="theme-color" content="#FCF3E9"><title>Page not found · Carflow Puzzle</title><style>{style}</style></head><body><main class="reading wrap"><p class="eyebrow">404 / CARFLOW PUZZLE</p><h1>Page not found</h1><p class="lead">This page may have moved. Let’s get you back to the little cars.</p><a class="button" href="{cfg['origin']}/">Carflow Puzzle →</a></main></body></html>''')
print('Built 9 pages, inline-styled 404, sitemap and robots at the repository root.')
