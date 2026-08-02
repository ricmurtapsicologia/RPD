#!/usr/bin/env bash
set -euo pipefail

node --check assets/js/app.js

python3 - <<'PY'
from html.parser import HTMLParser
from pathlib import Path
import re

html_path = Path('index.html')
if not html_path.exists():
    raise SystemExit('index.html ausente')
html = html_path.read_text(encoding='utf-8')
js = Path('assets/js/app.js').read_text(encoding='utf-8')

required_html = [
    'RPD1.mp3', 'id="loadVideo"', 'id="videoSlot"', 'id="beliefBefore"',
    'id="beliefAfter"', 'id="otherEmotion"', 'id="distortionDialog"',
    'id="shareSummary"', 'id="shareFull"', 'v2.1.1'
]
for token in required_html:
    if token not in html:
        raise SystemExit(f'Recurso crítico ausente no HTML: {token}')

required_js = ['youtube-nocookie.com/embed/qp8VUlVqooI', 'sessionStorage', 'renderSummary', 'buildPrint']
for token in required_js:
    if token not in js:
        raise SystemExit(f'Recurso crítico ausente no JS: {token}')

class Checker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
    def handle_starttag(self, tag, attrs):
        for k,v in attrs:
            if k=='id' and v:
                self.ids.append(v)

c=Checker(); c.feed(html)
dup=sorted({x for x in c.ids if c.ids.count(x)>1})
if dup:
    raise SystemExit('IDs duplicados: ' + ', '.join(dup))

steps=re.findall(r'data-step="([1-7])"', html)
if steps != list('1234567'):
    raise SystemExit(f'Etapas inválidas: {steps}')

if '{% include' in html or '---\n---' in html[:20]:
    raise SystemExit('index.html ainda depende de composição Jekyll')

print('RPD v2.1.1: validação estrutural OK')
PY
