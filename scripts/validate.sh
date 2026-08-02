#!/usr/bin/env bash
set -euo pipefail

node --check assets/js/app.js

python3 - <<'PY'
from html.parser import HTMLParser
from pathlib import Path
import re

VERSION='2.2.0'
html=Path('index.html').read_text(encoding='utf-8')
js=Path('assets/js/app.js').read_text(encoding='utf-8')
css=Path('assets/css/app.css').read_text(encoding='utf-8')
readme=Path('README.md').read_text(encoding='utf-8')

for token in [
    'RPD1.mp3', 'id="loadVideo"', 'id="videoSlot"', 'id="modeEssential"',
    'id="modeFull"', 'id="distortionQuick"', 'class="distortion-explore"',
    'id="skipValues"', 'Não avaliado'
]:
    if token not in html:
        raise SystemExit(f'Recurso crítico ausente no HTML: {token}')

for token in [
    f'const VERSION="{VERSION}"', 'localDate()',
    'SEQUENCES={\n  full:[1,2,3,4,5,6,7],\n  essential:[1,2,3,5,7]\n}',
    'rangeTouched', 'youtube-nocookie.com/embed/qp8VUlVqooI',
    'sessionStorage', 'renderSummary', 'buildPrint'
]:
    if token not in js:
        raise SystemExit(f'Recurso crítico ausente no JS: {token}')

for token in [
    '#pdf-area,.print-sheet{display:none!important}',
    '.distortion-quick', '.distortion-more', '.mode-selector',
    'top:calc(var(--nav-h) + 8px)'
]:
    if token not in css:
        raise SystemExit(f'Recurso crítico ausente no CSS: {token}')

for token in [
    f'content="{VERSION}"',
    f'app.css?v={VERSION}',
    f'print.css?v={VERSION}',
    f'app.js?v={VERSION}',
    f'"softwareVersion":"{VERSION}"',
    f'v{VERSION}'
]:
    if token not in html:
        raise SystemExit(f'Versão inconsistente no HTML: {token}')

if f'Versão atual: v{VERSION}' not in readme:
    raise SystemExit('README com versão inconsistente')

class Checker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k=='id' and v:
                self.ids.append(v)

c=Checker()
c.feed(html)
dup=sorted({x for x in c.ids if c.ids.count(x)>1})
if dup:
    raise SystemExit('IDs duplicados: '+', '.join(dup))

steps=re.findall(r'data-step="([1-7])"',html)
if steps!=list('1234567'):
    raise SystemExit(f'Etapas inválidas: {steps}')

if '{% include' in html or '---\n---' in html[:20]:
    raise SystemExit('index.html ainda depende de Jekyll')

if '>50/100</output>' in html:
    raise SystemExit('Slider ainda apresenta 50/100 como avaliação automática')

print('RPD v2.2.0: validação estrutural OK')
PY
