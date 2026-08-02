#!/usr/bin/env bash
set -euo pipefail

node --check assets/js/app.js

python3 - <<'PY'
from html.parser import HTMLParser
from pathlib import Path
import re

parts = [
    '_includes/v210_head.html',
    '_includes/v210_intro.html',
    '_includes/v210_steps_2_4.html',
    '_includes/v210_steps_5_7.html',
    '_includes/v210_support_print.html',
    '_includes/v210_dialogs.html',
]
for p in parts:
    if not Path(p).exists():
        raise SystemExit(f'Arquivo ausente: {p}')
html = ''.join(Path(p).read_text(encoding='utf-8') for p in parts)

required = [
    'RPD1.mp3', 'loadVideo', 'beliefBefore', 'beliefAfter', 'otherEmotion',
    'distortionDialog', 'draftToggle', 'shareSummary', 'shareFull',
    'v2.1.0', 'Emoções ou estados'
]
for token in required:
    if token not in html and token not in Path('assets/js/app.js').read_text(encoding='utf-8'):
        raise SystemExit(f'Recurso crítico ausente: {token}')

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

print('RPD v2.1.0: validação estrutural OK')
PY
