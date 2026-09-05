from pathlib import Path
from html.parser import HTMLParser
import json
import re

ROOT = Path(__file__).resolve().parents[1]
version = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]
html = (ROOT / "index.html").read_text(encoding="utf-8")
js = (ROOT / "assets/js/app.js").read_text(encoding="utf-8")
css = (ROOT / "assets/css/app.css").read_text(encoding="utf-8")
privacy = (ROOT / "privacidade.html").read_text(encoding="utf-8")
readme = (ROOT / "README.md").read_text(encoding="utf-8")
sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
audio_js = (ROOT / "assets/js/audio-n3.js").read_text(encoding="utf-8")

required_html = [
    f'content="{version}"', f'app.css?v={version}', f'print.css?v={version}', f'app.js?v={version}',
    f'"softwareVersion":"{version}"', f'RPD <span class="version">v{version}</span>',
    'Richelmy Murta Pinto · Psicólogo clínico · CRP 04/54.383',
    'href="tel:188"', 'aria-label="Ligar para o CVV no número 188"',
    'id="loadVideo"', 'id="videoSlot"', 'id="modeEssential"', 'id="modeFull"',
    'id="distortionQuick"', 'class="distortion-explore"', 'id="skipValues"', 'Não avaliado',
    './audio/rpd1-n3.mp3?v=n3-20260831'
]
for token in required_html:
    if token not in html:
        raise SystemExit(f"HTML crítico ausente/inconsistente: {token}")

if 'tel:+55188' in html:
    raise SystemExit('URI telefônica antiga do CVV ainda presente')
if 'assets/css/v230.css' in html:
    raise SystemExit('CSS transitório v230 ainda referenciado')

required_js = [
    f'const VERSION="{version}"', 'const DRAFT_KEY="rpd_draft"', 'const DRAFT_SCHEMA=1',
    'LEGACY_DRAFT_KEYS', 'mappedStepForMode', 'syncModeUi', 'syncResponsePending', 'enhanceMarkup',
    'progressCard.setAttribute("role","progressbar")', 'id="returnSummary"', 'id="responsePending"',
    'print-essential-only', 'print-full-only', 'pInitialMeasures', 'aria-valuemax', 'aria-invalid',
    'aria-describedby', 'rangeTouched', 'youtube-nocookie.com/embed/qp8VUlVqooI', 'sessionStorage',
    'renderSummary', 'buildPrint'
]
for token in required_js:
    if token not in js:
        raise SystemExit(f"JS crítico ausente/inconsistente: {token}")

required_css = [
    '#pdf-area,.print-sheet{display:none!important}', '.distortion-quick', '.mode-selector',
    '.edit-return-bar', '.response-pending', '@media(max-width:430px){.progress-card{position:static}',
    'prefers-reduced-motion:reduce', 'scroll-behavior:auto!important'
]
for token in required_css:
    if token not in css:
        raise SystemExit(f"CSS crítico ausente/inconsistente: {token}")

required_privacy = [
    f'Transparência · v{version}', 'CRP 04/54.383', 'sessionStorage', 'rpd.audioProgress.n3',
    'identificador do áudio e o segundo de reprodução',
    'https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/self-help-cbt-techniques/thought-record/',
    'https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/self-help-cbt-techniques/reframing-unhelpful-thoughts/',
    'https://transparencia.cfp.org.br/crp10/pergunta-frequente/publicidade-profissional/'
]
for token in required_privacy:
    if token not in privacy:
        raise SystemExit(f'Política/fundamentação incompleta: {token}')

if 'rpd.audioProgress.n3' not in audio_js:
    raise SystemExit('Chave de progresso do áudio divergente da política de privacidade')
if f'Versão canônica: v{version}' not in readme:
    raise SystemExit('README com versão divergente')
if 'scripts/validate.py' not in readme or 'scripts/validate.sh' in readme:
    raise SystemExit('README com arquitetura de validação desatualizada')
if 'rpd.audioProgress.n3' not in readme:
    raise SystemExit('README não documenta persistência técnica do player de áudio')
if '<lastmod>2026-09-05</lastmod>' not in sitemap:
    raise SystemExit('Sitemap sem lastmod da release')

class Checker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k == 'id' and v:
                self.ids.append(v)

c = Checker(); c.feed(html)
dup = sorted({x for x in c.ids if c.ids.count(x) > 1})
if dup:
    raise SystemExit('IDs duplicados: ' + ', '.join(dup))
steps = re.findall(r'data-step="([1-7])"', html)
if steps != list('1234567'):
    raise SystemExit(f'Etapas inválidas: {steps}')
if '{% include' in html:
    raise SystemExit('index.html ainda depende de Jekyll')

obsolete = [
    '_includes', 'assets/css/v230.css', 'manifest.json', 'service-worker.js', 'RPD1.mp3',
    'audio/rpd1-n2.mp3', 'assets/js/audio-n2.js', 'css/variables.css',
    'scripts/index_v230.patch', 'scripts/js_v230.patch', 'scripts/validate_v230.patch',
    'scripts/validate.sh', '.github/workflows/apply-v230.yml', '.github/workflows/issue-trigger-v230.yml',
    '.github/workflows/remaster-audio-n2.yml', '.github/workflows/diagnose-v230-patches.yml',
    '.github/workflows/harden-v231.yml', 'scripts/harden_v231.py',
    'E2E_DIAGNOSTIC.txt', 'E2E_EXIT.txt', 'FINAL_E2E_DIAGNOSTIC.txt', 'FINAL_E2E_EXIT.txt',
    'PATCH_DIAGNOSTIC.txt', 'RUNTIME_DIAGNOSTIC.txt', 'RUNTIME_EXIT.txt'
]
for rel in obsolete:
    if (ROOT / rel).exists():
        raise SystemExit(f'Legado/diagnóstico ainda presente na árvore canônica: {rel}')

print(f'RPD v{version}: validação estrutural OK')
