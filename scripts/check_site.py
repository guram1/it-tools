#!/usr/bin/env python3
"""Static checks for ops-box.net (stdlib only). Run from the repo root: python3 scripts/check_site.py

Fails (exit 1) on:
- JSON-LD that does not parse
- FAQPage questions that do not match the visible .faq-question text
- internal links / assets that point to files that do not exist (redirect sources in _redirects count as valid)
- tool pages missing from sitemap.xml, or sitemap URLs without a page
- canonical / og:url not extensionless https://ops-box.net/... or not matching the file
- <title> longer than 60 chars, missing meta description, not exactly one <h1>
- unified header / nav.js / base.css missing
- external <script src> on a CDN without integrity=
"""
import glob
import html
import json
import os
import re
import sys

errors, warnings = [], []
pages = sorted(glob.glob('*.html') + glob.glob('tools/*.html'))
redirect_sources = set()
if os.path.exists('_redirects'):
    for line in open('_redirects', encoding='utf-8'):
        line = line.strip()
        if line and not line.startswith('#'):
            redirect_sources.add(line.split()[0])


def url_for(path):
    if path == 'index.html':
        return 'https://ops-box.net/'
    return 'https://ops-box.net/' + path[:-5]


def target_exists(href):
    href = href.split('#')[0].split('?')[0]
    if not href or href == '/':
        return True
    if href in redirect_sources:
        return True
    p = href.lstrip('/')
    return os.path.exists(p) or os.path.exists(p + '.html') or os.path.exists(os.path.join(p, 'index.html'))


def norm(t):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', t))).strip()


for f in pages:
    s = open(f, encoding='utf-8').read()
    is_404 = f == '404.html'
    # JSON-LD
    faq_ld = []
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            data = json.loads(block)
        except Exception as e:  # noqa: BLE001
            errors.append(f'{f}: invalid JSON-LD ({e})')
            continue
        if isinstance(data, dict) and data.get('@type') == 'FAQPage':
            faq_ld = [norm(q.get('name', '')) for q in data.get('mainEntity', [])]
    visible = [norm(q) for q in re.findall(r'<button class="faq-question"[^>]*>(.*?)</button>', s, re.S)]
    if faq_ld and visible and faq_ld != visible:
        errors.append(f'{f}: FAQPage JSON-LD questions differ from visible FAQ')
    # links and assets
    for href in re.findall(r'(?:href|src)="(/[^"]*|\.\./[^"]*)"', s):
        h = href.replace('../', '/', 1) if href.startswith('../') else href
        if h.startswith('//') or h.startswith('/cdn-cgi/'):
            continue
        if not target_exists(h):
            errors.append(f'{f}: broken internal link {href}')
    # head
    if not is_404:
        m = re.search(r'<link rel="canonical" href="([^"]+)"', s)
        if not m:
            errors.append(f'{f}: missing canonical')
        elif m.group(1) != url_for(f):
            errors.append(f'{f}: canonical {m.group(1)} != {url_for(f)}')
        og = re.search(r'<meta property="og:url" content="([^"]+)"', s)
        if og and og.group(1) != url_for(f):
            errors.append(f'{f}: og:url {og.group(1)} != {url_for(f)}')
    t = re.search(r'<title>(.*?)</title>', s, re.S)
    if not t:
        errors.append(f'{f}: missing <title>')
    elif len(html.unescape(t.group(1).strip())) > 60:
        errors.append(f'{f}: title {len(html.unescape(t.group(1).strip()))} chars > 60')
    if not re.search(r'<meta name="description" content="[^"]{50,}"', s):
        errors.append(f'{f}: missing/short meta description')
    if len(re.findall(r'<h1[\s>]', s)) != 1:
        errors.append(f'{f}: expected exactly one <h1>')
    for needle in ('class="nav-toggle"', '/js/nav.js', '/css/base.css'):
        if needle not in s:
            errors.append(f'{f}: missing {needle}')
    for tag in re.findall(r'<script[^>]+src="https://(?:cdn\.jsdelivr\.net|unpkg\.com|cdnjs\.cloudflare\.com)[^>]*>', s):
        if 'integrity=' not in tag:
            errors.append(f'{f}: CDN script without SRI: {tag[:90]}')
    if f.startswith('tools/') and 'dns-dumpster' in s.replace('ssl-api.ops-box.net/dns-dumpster', ''):
        warnings.append(f'{f}: still links to dns-dumpster')

# sitemap
sm = open('sitemap.xml', encoding='utf-8').read()
locs = set(re.findall(r'<loc>([^<]+)</loc>', sm))
expected = {url_for(p) for p in pages if p != '404.html'}
for u in sorted(expected - locs):
    errors.append(f'sitemap.xml: missing {u}')
for u in sorted(locs - expected):
    errors.append(f'sitemap.xml: {u} has no page')

for w in warnings:
    print('WARN ', w)
for e in errors:
    print('ERROR', e)
print(f'{len(pages)} pages checked, {len(errors)} errors, {len(warnings)} warnings')
sys.exit(1 if errors else 0)
