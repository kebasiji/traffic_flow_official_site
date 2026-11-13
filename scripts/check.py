#!/usr/bin/env python3
"""Check the root-published GitHub Pages site and portable local links."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin, unquote
import json

ROOT = Path(__file__).resolve().parents[1]
content = json.loads((ROOT / 'src/content.json').read_text())
config = json.loads((ROOT / 'src/config.json').read_text())
KINDS = ['home', 'support', 'privacy']

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
    def handle_starttag(self, tag, attributes):
        self.tags.append((tag, dict(attributes)))

def route(locale, kind):
    return '/' + content[locale]['prefix'] + ('' if kind == 'home' else kind + '/')

assert not (ROOT / 'dist').exists(), 'Do not keep a second site under dist/'
assert (ROOT / '.nojekyll').is_file(), 'GitHub Pages must serve the static site directly'
assert (ROOT / 'CNAME').read_text().strip() == urlparse(config['origin']).hostname
results = []
for locale, language in content.items():
    for kind in KINDS:
        path = route(locale, kind)
        file = ROOT / path.lstrip('/') / 'index.html'
        text = file.read_text()
        page = Page()
        page.feed(text)
        assert sum(tag == 'h1' for tag, attrs in page.tags) == 1, file
        policies = [attrs['content'] for tag, attrs in page.tags if tag == 'meta' and attrs.get('http-equiv') == 'Content-Security-Policy']
        assert len(policies) == 1 and "script-src 'none'" in policies[0] and "connect-src 'none'" in policies[0], file
        assert '<body><!--email_off-->' in text and '<!--/email_off--></body>' in text, file
        assert any(tag == 'html' and attrs.get('lang') == language['lang'] for tag, attrs in page.tags), file
        assert not any(tag in ['script', 'form', 'iframe'] for tag, attrs in page.tags), file
        if kind in ['support', 'privacy']:
            assert 'mailto:' + config['supportEmail'] in text, file
        if kind == 'home' and not config['released']:
            assert language['coming'] in text, file
        switches = [attrs for tag, attrs in page.tags if tag == 'a' and 'hreflang' in attrs]
        assert len(switches) == 3, file
        for target_locale, target_language in content.items():
            switch = next(attrs for attrs in switches if attrs['hreflang'] == target_language['lang'])
            target = (file.parent / switch['href']).resolve()
            expected = ROOT / route(target_locale, kind).lstrip('/') / 'index.html'
            assert target == expected.resolve(), (file, switch)
        for tag, attrs in page.tags:
            for attribute in ['href', 'src']:
                value = attrs.get(attribute, '')
                parsed = urlparse(value)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                assert not parsed.path.startswith('/'), (file, value, 'root-relative URL breaks file preview')
                assert not parsed.path.endswith('/'), (file, value, 'use explicit index.html')
                target = (file.parent / parsed.path).resolve()
                assert target.is_relative_to(ROOT), (file, value)
                assert target.is_file(), (file, value, 'missing local file')
                file_url = urlparse(urljoin(file.as_uri(), value))
                assert Path(unquote(file_url.path)).resolve() == target
        for token in ['fetch(', 'sendBeacon', 'localStorage', 'document.cookie', 'XMLHttpRequest']:
            assert token not in text, (file, token)
        canonical = [attrs['href'] for tag, attrs in page.tags if tag == 'link' and attrs.get('rel') == 'canonical']
        assert canonical == [config['origin'] + path], file
        results.append({'page': str(file.relative_to(ROOT)), 'language': language['lang'], 'status': 'PASS'})

not_found = Page()
not_found.feed((ROOT / '404.html').read_text())
assert any(tag == 'style' for tag, attrs in not_found.tags), '404 must not rely on relative styles'
assert any(tag == 'meta' and attrs.get('http-equiv') == 'Content-Security-Policy' and "script-src 'none'" in attrs.get('content', '') for tag, attrs in not_found.tags)
assert not any(tag in ['img', 'script'] or tag == 'link' and attrs.get('rel') == 'stylesheet' for tag, attrs in not_found.tags)
assert any(tag == 'a' and attrs.get('href') == config['origin'] + '/' for tag, attrs in not_found.tags)
assert len(results) == 9
print(json.dumps({'status': 'PASS', 'pages': results, 'deployment': {'root_entry': 'index.html', 'domain': config['origin'], 'nojekyll': True, 'legacy_dist_removed': True, '404_self_contained': True}, 'limitations': 'Static checks include file URL resolution. Live HTTPS and browser rendering are verified separately.'}, ensure_ascii=False, indent=2))
