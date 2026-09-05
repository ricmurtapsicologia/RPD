from pathlib import Path
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2.3.1"
DATE_BR = "5 de setembro de 2026"
DATE_ISO = "2026-09-05"
PRO = "Richelmy Murta Pinto · Psicólogo clínico · CRP 04/54.383"


def p(rel):
    return ROOT / rel


def read(rel):
    return p(rel).read_text(encoding="utf-8")


def write(rel, content):
    path = p(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def apply_v230_if_needed():
    js = read("assets/js/app.js")
    if 'const VERSION="2.2.0"' in js:
        subprocess.run(["git", "apply", "scripts/js_v230.patch"], cwd=ROOT, check=True)


def harden_index():
    s = read("index.html").replace("2.2.0", VERSION).replace("2.3.0", VERSION)
    s = s.replace('<meta name="author" content="Richelmy Murta">', '<meta name="author" content="Richelmy Murta Pinto">')
    s = s.replace('"name":"Richelmy Murta","jobTitle":"Psicólogo clínico"', '"name":"Richelmy Murta Pinto","jobTitle":"Psicólogo clínico","identifier":"CRP 04/54.383"')
    s = s.replace("Richelmy Murta · Psicólogo clínico", PRO)
    s = s.replace('href="tel:+55188"', 'href="tel:188"')
    s = s.replace('<a class="btn btn-danger" href="tel:188">Ligar para o CVV — 188</a>', '<a class="btn btn-danger" href="tel:188" aria-label="Ligar para o CVV no número 188">Ligar para o CVV — 188</a>')
    s = s.replace(f'<link rel="stylesheet" href="assets/css/v230.css?v={VERSION}">\n', "")
    if '<meta name="referrer"' not in s:
        s = s.replace('<meta name="theme-color" content="#0b5d57">', '<meta name="theme-color" content="#0b5d57">\n<meta name="referrer" content="strict-origin-when-cross-origin">')
    write("index.html", s)


def harden_js():
    s = read("assets/js/app.js").replace("2.3.0", VERSION)
    s = s.replace('const LEGACY_DRAFT_KEYS=["rpd_draft_v2_2_0"];', 'const LEGACY_DRAFT_KEYS=["rpd_draft_v2_2_0","rpd_draft_v2_3_0"];')
    write("assets/js/app.js", s)


def merge_css():
    app = read("assets/css/app.css")
    override = p("assets/css/v230.css")
    if override.exists() and "RPD hardening merged" not in app:
        app += "\n\n/* RPD hardening merged: accessibility, editing and small-screen safeguards */\n" + override.read_text(encoding="utf-8").strip() + "\n"
    if "prefers-reduced-motion:reduce" not in app or "scroll-behavior:auto!important" not in app:
        app += "\n@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*::before,*::after{scroll-behavior:auto!important;transition:none!important;animation:none!important}}\n"
    write("assets/css/app.css", app)
    if override.exists():
        override.unlink()


def harden_privacy():
    s = read("privacidade.html").replace("2.3.0", VERSION)
    s = re.sub(r"Atualizado em [^<]+\.", f"Atualizado em {DATE_BR}.", s, count=1)
    s = s.replace("<code>RPD1.mp3</code>", "<code>audio/rpd1-n3.mp3</code>")
    if "Responsável profissional" not in s:
        marker = '<p><a href="./">Voltar ao RPD</a></p>'
        insert = f'<h2>11. Responsável profissional</h2>\n<p>{PRO}.</p>\n<p>Esta identificação se refere à responsabilidade profissional pela ferramenta psicoeducativa e não transforma o RPD em prontuário, teste psicológico ou serviço de urgência.</p>\n'
        s = s.replace(marker, insert + marker)
    write("privacidade.html", s)


def harden_readme():
    s = read("README.md")
    s = re.sub(r"\*\*Versão atual: v[^*]+\*\*", f"**Versão atual: v{VERSION} — 05/09/2026**", s, count=1)
    s = s.replace("RPD1.mp3", "audio/rpd1-n3.mp3")
    if "## v2.3.1 — hardening" not in s:
        marker = "## v2.3.0 — hardening técnico, acessibilidade e consistência entre modos"
        changelog = f'''## v2.3.1 — hardening, conformidade e consolidação\n\nRelease canônica de saneamento. Consolida a v2.3.x como uma única implementação executável e elimina o drift entre documentação, assets e runtime.\n\n- identificação profissional pública padronizada como `{PRO}`;\n- versão sincronizada entre HTML, JavaScript, package, README, privacidade, JSON-LD e assets;\n- botão do CVV corrigido para o tridígito nacional `188`;\n- política de privacidade sincronizada ao comportamento real do `sessionStorage`;\n- chave de rascunho estável `rpd_draft`, com versão de esquema e migração do legado;\n- melhorias de acessibilidade da v2.3 incorporadas ao runtime: progressbar semântica, erros ARIA, contraste, foco e reduced motion;\n- comportamento em telas muito pequenas corrigido;\n- modo essencial e modo completo novamente testados como fluxos independentes;\n- suíte Playwright ampliada para segurança, privacidade, acessibilidade, responsividade, PDF/print e mídia;\n- validação estrutural passa a derivar a versão do `package.json`, impedindo novo drift;\n- CI obrigatório em `main` e branches de release;\n- arquivos legados e patches transitórios removidos da árvore de produção, preservados na branch de rollback.\n\n'''
        s = s.replace(marker, changelog + marker)
    s = re.sub(r"\*\*Richelmy Murta · Psicólogo clínico\*\*", f"**{PRO}**", s)
    s = s.replace("**Richelmy Murta · Psicólogo clínico**", f"**{PRO}**")
    write("README.md", s)


def harden_package():
    data = json.loads(read("package.json"))
    data["version"] = VERSION
    data.setdefault("scripts", {})["validate"] = "python3 scripts/validate.py"
    data["scripts"]["test:e2e"] = "playwright test"
    write("package.json", json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def harden_sitemap():
    s = read("sitemap.xml")
    s = re.sub(r"<lastmod>[^<]+</lastmod>", f"<lastmod>{DATE_ISO}</lastmod>", s)
    write("sitemap.xml", s)


def write_validator():
    validator = r'''from pathlib import Path
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

if f'Transparência · v{version}' not in privacy:
    raise SystemExit('Política de privacidade com versão divergente')
if 'CRP 04/54.383' not in privacy:
    raise SystemExit('Identificação profissional ausente na política de privacidade')
if f'Versão atual: v{version}' not in readme:
    raise SystemExit('README com versão divergente')
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
    '.github/workflows/remaster-audio-n2.yml'
]
for rel in obsolete:
    if (ROOT / rel).exists():
        raise SystemExit(f'Legado ainda presente na árvore canônica: {rel}')

print(f'RPD v{version}: validação estrutural OK')
'''
    write("scripts/validate.py", validator)


def write_tests():
    tests = r'''const { test, expect } = require('@playwright/test');

async function reachStep3(page){
  await page.locator('#situation').fill('Recebi uma mensagem curta e fiquei em dúvida sobre o significado.');
  await page.locator('.step[data-step="1"] .next').click();
  await page.locator('#emotion_0').check({ force: true });
  await page.locator('.step[data-step="2"] .next').click();
  await page.locator('#thought').fill('A pessoa deve estar chateada comigo.');
}

async function reachEssentialSummary(page){
  await page.locator('#modeEssential').check({ force: true });
  await page.locator('#situation').fill('Recebi uma mensagem curta.');
  await page.locator('.step[data-step="1"] .next').click();
  await page.locator('#emotion_0').check({ force: true });
  await page.locator('.step[data-step="2"] .next').click();
  await page.locator('#thought').fill('Fiz algo errado.');
  await page.locator('.step[data-step="3"] .next').click();
  await page.locator('#action').fill('Esperar alguns minutos e pedir esclarecimento de forma direta.');
  await page.locator('.step[data-step="5"] .next').click();
}

async function reachFullStep6(page){
  await reachStep3(page);
  await page.locator('.step[data-step="3"] .next').click();
  await page.locator('.step[data-step="4"] .next').click();
  await page.locator('#skipValues').click();
}

test.beforeEach(async ({ page }) => {
  await page.goto('/');
});

test('release, identificação profissional e links críticos estão coerentes', async ({ page }) => {
  await expect(page.locator('meta[name="application-version"]')).toHaveAttribute('content', '2.3.1');
  await expect(page.locator('body')).toContainText('Richelmy Murta Pinto · Psicólogo clínico · CRP 04/54.383');
  await expect(page.locator('a[href="tel:188"]')).toHaveCount(1);
  await expect(page.locator('a[href="tel:+55188"]')).toHaveCount(0);
});

test('áudio N3 e carregador de vídeo permanecem disponíveis e vídeo é opt-in', async ({ page }) => {
  await expect(page.locator('audio source[src^="./audio/rpd1-n3.mp3"]')).toHaveCount(1);
  await expect(page.locator('#videoSlot iframe')).toHaveCount(0);
  await page.locator('#loadVideo').click();
  await expect(page.locator('#videoSlot iframe')).toHaveAttribute('src', /youtube-nocookie\.com/);
});

test('sliders começam como não avaliados e só mudam após interação deliberada', async ({ page }) => {
  await page.locator('#situation').fill('Situação breve.');
  await page.locator('.step[data-step="1"] .next').click();
  await expect(page.locator('#beforeOut')).toHaveText('Não avaliado');
  await page.locator('#before').focus();
  await page.keyboard.press('ArrowRight');
  await expect(page.locator('#beforeOut')).not.toHaveText('Não avaliado');
});

test('erros obrigatórios expõem estado ARIA e descrição associada', async ({ page }) => {
  await page.locator('.step[data-step="1"] .next').click();
  await expect(page.locator('#situation')).toHaveAttribute('aria-invalid', 'true');
  await expect(page.locator('#situation')).toHaveAttribute('aria-describedby', 'situation-error');
  await expect(page.locator('#situation-error')).not.toBeEmpty();
});

test('barra de progresso tem semântica e acompanha modo essencial', async ({ page }) => {
  await expect(page.locator('#progressCard')).toHaveAttribute('role', 'progressbar');
  await expect(page.locator('#progressCard')).toHaveAttribute('aria-valuemax', '7');
  await page.locator('#modeEssential').check({ force: true });
  await expect(page.locator('#progressCard')).toHaveAttribute('aria-valuemax', '5');
  await expect(page.locator('#progressLabel')).toContainText('Passo 1 de 5');
});

test('troca do modo completo para essencial não volta ao início', async ({ page }) => {
  await reachStep3(page);
  await page.locator('.step[data-step="3"] .next').click();
  await expect(page.locator('.step[data-step="4"]')).toHaveClass(/is-active/);
  await page.locator('#modeEssential').check({ force: true });
  await expect(page.locator('.step[data-step="5"]')).toHaveClass(/is-active/);
  await expect(page.locator('#progressLabel')).toContainText('Passo 4 de 5');
});

test('opções de não classificação são exclusivas com distorções específicas', async ({ page }) => {
  await reachStep3(page);
  await page.locator('#distortion_special_0').check({ force: true });
  await page.locator('#distortion_0').check({ force: true });
  await expect(page.locator('#distortion_0')).toBeChecked();
  await expect(page.locator('#distortion_special_0')).not.toBeChecked();
});

test('modo essencial mostra apenas próximo passo na etapa de ação', async ({ page }) => {
  await page.locator('#modeEssential').check({ force: true });
  await page.locator('#situation').fill('Situação breve.');
  await page.locator('.step[data-step="1"] .next').click();
  await page.locator('#emotion_0').check({ force: true });
  await page.locator('.step[data-step="2"] .next').click();
  await page.locator('#thought').fill('Algo vai dar errado.');
  await page.locator('.step[data-step="3"] .next').click();
  await expect(page.locator('#step5Title')).toHaveText('Próximo passo');
  await expect(page.locator('#value').locator('xpath=ancestor::div[contains(@class,"full-mode-only")]')).toBeHidden();
  await expect(page.locator('#actionLabel')).toContainText('Qual pequeno próximo passo é possível agora?');
});

test('resposta alternativa pode ser explicitamente adiada sem bloquear conclusão', async ({ page }) => {
  await reachFullStep6(page);
  await expect(page.locator('.step[data-step="6"]')).toHaveClass(/is-active/);
  await page.locator('.step[data-step="6"] .next').click();
  await expect(page.locator('#response')).toHaveAttribute('aria-invalid', 'true');
  await page.locator('#responsePending').check();
  await expect(page.locator('#response')).toBeDisabled();
  await page.locator('.step[data-step="6"] .next').click();
  await expect(page.locator('.step[data-step="7"]')).toHaveClass(/is-active/);
});

test('edição pela síntese volta diretamente à síntese', async ({ page }) => {
  await reachEssentialSummary(page);
  await page.locator('#summary .edit-step').first().click();
  await expect(page.locator('#editReturnBar')).toBeVisible();
  await page.locator('#situation').fill('Situação atualizada.');
  await page.locator('#returnSummary').click();
  await expect(page.locator('.step[data-step="7"]')).toHaveClass(/is-active/);
  await expect(page.locator('#summary')).toContainText('Situação atualizada.');
});

test('rascunho é opt-in, usa chave estável e permanece restrito ao sessionStorage', async ({ page }) => {
  await expect.poll(() => page.evaluate(() => sessionStorage.getItem('rpd_draft'))).toBeNull();
  await page.locator('#draftToggle').check();
  await page.locator('#situation').fill('Rascunho deliberado.');
  await expect.poll(() => page.evaluate(() => sessionStorage.getItem('rpd_draft'))).not.toBeNull();
  await expect.poll(() => page.evaluate(() => localStorage.length)).toBe(0);
});

test('PDF/print essencial oculta seções do modo completo', async ({ page }) => {
  await page.addInitScript(() => { window.print = () => {}; });
  await reachEssentialSummary(page);
  await page.locator('#printPdf').click();
  await page.locator('#actionConfirm').click();
  await expect(page.locator('.print-essential-only')).not.toHaveAttribute('hidden', '');
  for (const el of await page.locator('.print-full-only').all()) {
    await expect(el).toHaveAttribute('hidden', '');
  }
});

test('política de privacidade corresponde à release e identifica o responsável', async ({ page }) => {
  await page.goto('/privacidade.html');
  await expect(page.locator('body')).toContainText('Transparência · v2.3.1');
  await expect(page.locator('body')).toContainText('sessionStorage');
  await expect(page.locator('body')).toContainText('CRP 04/54.383');
});

for (const width of [320, 360, 390, 430, 768, 1024, 1366, 1440, 1920]) {
  test(`sem overflow horizontal em ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto('/');
    const metrics = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: window.innerWidth }));
    expect(metrics.sw).toBeLessThanOrEqual(metrics.iw + 1);
  });
}

test('em 390px a barra de progresso deixa de ser sticky', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await expect.poll(() => page.locator('#progressCard').evaluate(el => getComputedStyle(el).position)).toBe('static');
});

test('primeiro Tab expõe o link de salto para navegação por teclado', async ({ page }) => {
  await page.keyboard.press('Tab');
  await expect(page.locator('.skip')).toBeFocused();
});
'''
    write("tests/rpd.spec.js", tests)


def write_release_note():
    note = f'''# RPD v{VERSION} — Hardening, conformidade e consolidação\n\nData: 05/09/2026\n\nEsta release consolida a implementação executável da série v2.3, elimina o drift v2.2/v2.3 e fecha os bloqueadores das auditorias 30/30 e 90/90 aplicáveis à página web.\n\n## Gates da release\n\n- versão única em HTML, JS, package, README, privacidade e JSON-LD;\n- identificação profissional: {PRO};\n- CVV 188 sem URI internacional incorreta;\n- privacidade por desenho com rascunho opt-in em sessionStorage;\n- acessibilidade ARIA, contraste, foco, reduced motion e mobile estreito;\n- modo essencial e completo cobertos por regressão E2E;\n- mídia externa carregada apenas por ação do usuário;\n- PDF/print coerente com o modo utilizado;\n- validação estrutural derivada do package.json;\n- CI com validação + Playwright em main e release;\n- baseline anterior preservada em branch de rollback.\n\nA promoção a canônica só ocorre após CI verde, deployment do GitHub Pages e smoke test da URL pública.\n'''
    write(f"RELEASE_v{VERSION}.md", note)


def cleanup_legacy():
    files = [
        "manifest.json", "service-worker.js", "RPD1.mp3", "audio/rpd1-n2.mp3",
        "assets/js/audio-n2.js", "audio-freeze-20260825.json", "css/variables.css",
        "scripts/index_v230.patch", "scripts/js_v230.patch", "scripts/validate_v230.patch",
        "scripts/validate.sh", ".github/workflows/apply-v230.yml", ".github/workflows/issue-trigger-v230.yml",
        ".github/workflows/remaster-audio-n2.yml"
    ]
    dirs = ["_includes", "css"]
    for rel in files:
        path = p(rel)
        if path.exists():
            path.unlink()
    for rel in dirs:
        path = p(rel)
        if path.exists():
            shutil.rmtree(path)


def main():
    apply_v230_if_needed()
    harden_index()
    harden_js()
    merge_css()
    harden_privacy()
    harden_readme()
    harden_package()
    harden_sitemap()
    write_validator()
    write_tests()
    write_release_note()
    cleanup_legacy()
    print(f"Prepared RPD v{VERSION}")


if __name__ == "__main__":
    main()
