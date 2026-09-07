from pathlib import Path
import base64
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2.3.2"
DATE_PT = "7 de setembro de 2026"
DATE_ISO = "2026-09-07"


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def write(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: esperado 1 match, encontrado {count}")
    return text.replace(old, new, 1)


def regex_once(text, pattern, repl, label, flags=0):
    out, count = re.subn(pattern, repl, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f"{label}: esperado 1 match, encontrado {count}")
    return out


# ---------------- index.html ----------------
index = read("index.html")
index = index.replace("2.3.1", VERSION)
index = index.replace(
    "https://ricmurtapsicologia.github.io/RPD/assets/og-card.svg",
    "https://ricmurtapsicologia.github.io/RPD/assets/og-card.png",
)

index = replace_once(
    index,
    '<p>Use o percurso essencial quando estiver mais sobrecarregado ou quiser apenas organizar o básico. O percurso completo mantém as sete etapas do RPD.</p>',
    '<p>Use o percurso essencial quando estiver mais sobrecarregado ou quiser organizar o básico. Ele organiza o episódio e um próximo passo, mas não substitui a investigação e a reavaliação do percurso completo.</p>',
    "descrição do modo essencial",
)
index = replace_once(
    index,
    '<small>5 passos · menos decisões de uma vez</small>',
    '<small>5 passos · organização breve, sem investigação completa</small>',
    "rótulo modo essencial",
)
index = replace_once(
    index,
    '<p class="stage-intent">Escreva o pensamento como surgiu. Não precisa corrigi-lo agora.</p>',
    '<p class="stage-intent">Registre o que surgiu automaticamente — frase, imagem mental, lembrança, impulso ou significado. Não precisa corrigir agora.</p>',
    "intenção pensamento automático",
)
index = replace_once(
    index,
    '<textarea id="thought" required placeholder="Escreva a frase como ela apareceu."></textarea><div class="field-error"></div>',
    '<textarea id="thought" required placeholder="Ex.: uma frase, imagem mental, lembrança, impulso ou significado que apareceu."></textarea><small>Não precisa transformar a experiência em uma frase perfeita; registre da forma mais próxima do que ocorreu.</small><div class="field-error"></div>',
    "campo pensamento automático",
)

old_crisis = '<div class="crisis"><h3>Se estiver difícil manter-se seguro(a)</h3><p>Não use esta página como único recurso. Procure companhia e apoio humano imediato.</p><div class="crisis-actions"><a class="btn btn-danger" href="tel:188" aria-label="Ligar para o CVV no número 188">Ligar para o CVV — 188</a><a class="btn btn-secondary" href="https://www.cvv.org.br/chat/" target="_blank" rel="noopener noreferrer">Abrir chat do CVV</a></div></div>'
new_crisis = '<div class="crisis" id="crise-imediata"><h3>Se estiver difícil manter-se seguro(a)</h3><p>Não use esta página como único recurso. Se houver risco imediato de se ferir, tentativa de suicídio, ameaça iminente à vida ou impossibilidade de permanecer em segurança, procure atendimento de urgência e não fique sozinho(a).</p><p><strong>Urgência:</strong> ligue para o SAMU 192 ou vá a uma UPA 24h, pronto-socorro ou hospital. Para apoio emocional e conversa sigilosa, o CVV atende gratuitamente pelo 188 e pelo chat.</p><div class="crisis-actions"><a class="btn btn-danger" href="tel:192" aria-label="Ligar para o SAMU no número 192">Ligar para o SAMU — 192</a><a class="btn btn-secondary" href="tel:188" aria-label="Ligar para o CVV no número 188">CVV — 188</a><a class="btn btn-secondary" href="https://www.cvv.org.br/chat/" target="_blank" rel="noopener noreferrer">Chat do CVV</a></div><small>Referência de segurança: <a href="https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/suicidio-prevencao/suicidio-prevencao" target="_blank" rel="noopener noreferrer">Ministério da Saúde — prevenção do suicídio</a>.</small></div>'
index = replace_once(index, old_crisis, new_crisis, "bloco de crise")

# Dialog semantics.
dialog_updates = [
    ('<dialog id="distortionDialog">', '<dialog id="distortionDialog" aria-labelledby="distortionDialogTitle">'),
    ('<h3>Distorções cognitivas: como reconhecer</h3>', '<h3 id="distortionDialogTitle">Distorções cognitivas: como reconhecer</h3>'),
    ('<dialog id="valueDialog">', '<dialog id="valueDialog" aria-labelledby="valueDialogTitle">'),
    ('<h3>O que é um valor?</h3>', '<h3 id="valueDialogTitle">O que é um valor?</h3>'),
    ('<dialog id="shareDialog">', '<dialog id="shareDialog" aria-labelledby="shareDialogTitle">'),
    ('<h3>Compartilhar registro</h3>', '<h3 id="shareDialogTitle">Compartilhar registro</h3>'),
    ('<dialog id="actionDialog">', '<dialog id="actionDialog" aria-labelledby="actionTitle">'),
]
for old, new in dialog_updates:
    index = replace_once(index, old, new, f"dialog {old}")

# CSP with a hash for the inline JSON-LD block.
match = re.search(r'<script type="application/ld\+json">(.*?)</script>', index, flags=re.S)
if not match:
    raise SystemExit("JSON-LD não encontrado para CSP")
jsonld_hash = base64.b64encode(hashlib.sha256(match.group(1).encode("utf-8")).digest()).decode("ascii")
csp = (
    "default-src 'self'; "
    f"script-src 'self' 'sha256-{jsonld_hash}'; "
    "style-src 'self'; img-src 'self' data:; media-src 'self'; "
    "frame-src https://www.youtube-nocookie.com; connect-src 'self'; "
    "font-src 'self' data:; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests"
)
index = replace_once(
    index,
    '<meta name="referrer" content="strict-origin-when-cross-origin">',
    '<meta name="referrer" content="strict-origin-when-cross-origin">\n<meta http-equiv="Content-Security-Policy" content="' + csp + '">',
    "meta CSP",
)
write("index.html", index)


# ---------------- app.js ----------------
js = read("assets/js/app.js")
js = js.replace('const VERSION="2.3.1";', f'const VERSION="{VERSION}";')
js = replace_once(
    js,
    'const EMOTIONS=["Ansiedade","Tristeza","Raiva","Culpa","Medo","Vergonha","Frustração","Insegurança","Desânimo","Solidão","Confusão","Alívio","Alegria","Outra"];',
    'const EMOTIONS=["Ansiedade","Tristeza","Raiva","Culpa","Medo","Vergonha","Frustração","Insegurança","Desânimo","Solidão","Confusão","Alívio","Alegria","Não sei/não consigo nomear agora","Outra"];',
    "lista de emoções",
)

js = regex_once(
    js,
    r'function openWhatsApp\(kind\)\{\s*window\.open\(\s*`https://wa\.me/\$\{WHATSAPP\}\?text=\$\{encodeURIComponent\(message\(kind\)\)\}`,\s*"_blank",\s*"noopener,noreferrer"\s*\);\s*\}',
    '''function openWhatsApp(kind){
  const opened=window.open(
    `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(message(kind))}`,
    "_blank",
    "noopener,noreferrer"
  );
  if(!opened)toast("O navegador bloqueou a abertura do WhatsApp. Permita pop-ups para esta página e tente novamente.");
}''',
    "fallback de popup WhatsApp",
    flags=re.S,
)

js = replace_once(
    js,
    'function openDialog(id){\n  const dialog=$("#"+id);\n  if(dialog && !dialog.open)dialog.showModal();\n}\n\nfunction closeDialog(dialog){\n  if(dialog?.open)dialog.close();\n}',
    '''let dialogInvoker=null;
function openDialog(id,invoker){
  const dialog=$("#"+id);
  if(!dialog || dialog.open)return;
  dialogInvoker=invoker||document.activeElement;
  dialog.showModal();
  requestAnimationFrame(()=>{
    const target=dialog.querySelector("[data-close-dialog],button,[href],input,select,textarea");
    target?.focus();
  });
}

function closeDialog(dialog){
  if(dialog?.open)dialog.close();
}''',
    "gestão de foco dos dialogs",
)
js = replace_once(
    js,
    'if(opener)openDialog(opener.dataset.openDialog);',
    'if(opener)openDialog(opener.dataset.openDialog,opener);',
    "invocador de dialog",
)

# Add close-event focus restoration once during initialization.
needle = 'document.addEventListener("click",event=>{'
focus_hook = '''$$('dialog').forEach(dialog=>dialog.addEventListener("close",()=>{
    if(dialogInvoker && dialogInvoker.isConnected)dialogInvoker.focus();
    dialogInvoker=null;
  }));

  document.addEventListener("click",event=>{'''
js = replace_once(js, needle, focus_hook, "retorno de foco dialog")

old_iframe = '<iframe loading="lazy" src="https://www.youtube-nocookie.com/embed/qp8VUlVqooI?rel=0" title="Como fazer um Registro de Pensamentos" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>'
new_iframe = '<iframe loading="lazy" src="https://www.youtube-nocookie.com/embed/qp8VUlVqooI?rel=0" title="Como fazer um Registro de Pensamentos" referrerpolicy="strict-origin-when-cross-origin" allow="encrypted-media; picture-in-picture" allowfullscreen></iframe>'
js = replace_once(js, old_iframe, new_iframe, "permissões iframe")
write("assets/js/app.js", js)


# ---------------- privacy ----------------
privacy = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Privacidade, dados e fundamentação | RPD</title>
<meta name="description" content="Aviso de privacidade, segurança, tratamento local de dados e fundamentação do RPD.">
<meta name="robots" content="index,follow">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; font-src 'self' data:; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<link rel="canonical" href="https://ricmurtapsicologia.github.io/RPD/privacidade.html">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/css/app.css?v={VERSION}">
<link rel="stylesheet" href="assets/css/privacy.css?v={VERSION}">
</head>
<body class="privacy-page">
<a class="skip" href="#privacy-main">Ir para o conteúdo principal</a>
<main id="privacy-main" class="privacy-main">
<a class="privacy-back" href="./">← Voltar ao RPD</a>
<article class="privacy-card">
<span class="kicker">Transparência · v{VERSION}</span>
<h1>Privacidade, dados e fundamentação do RPD</h1>
<p class="privacy-updated">Atualizado em {DATE_PT}.</p>
<div class="privacy-notice"><strong>Resumo:</strong> o conteúdo clínico do registro não é enviado ao responsável pelo RPD nem persistido por padrão. O preenchimento ocorre localmente no navegador. Recursos externos só são acionados por decisão do usuário.</div>

<h2>1. Quem é o responsável pela ferramenta</h2>
<p>O RPD é mantido por <strong>Richelmy Murta Pinto · Psicólogo clínico · CRP 04/54.383</strong>. Para questões sobre esta ferramenta ou para exercer direitos relativos a dados que tenham sido efetivamente recebidos em contato direto, utilize o canal profissional de WhatsApp disponível na seção <a href="./#apoio">Contato e segurança</a>.</p>

<h2>2. Quais informações podem aparecer no registro</h2>
<p>O usuário pode inserir, voluntariamente, nome ou iniciais, data, situação, emoções ou estados, pensamentos, padrões cognitivos percebidos, medidas opcionais de desconforto e convicção, investigação, valores, ações possíveis e resposta alternativa. Dependendo do que a pessoa escrever, o conteúdo pode revelar informações de saúde e outros dados pessoais sensíveis.</p>
<p>Nome, telefone, endereço, documentos ou identificação de terceiros não são necessários para concluir o RPD. Recomenda-se inserir somente o mínimo necessário para a reflexão.</p>

<h2>3. Finalidades</h2>
<p>O RPD foi desenhado para apoiar reflexão psicoeducativa, organizar um episódio e, quando o usuário desejar, produzir uma síntese para impressão ou compartilhamento deliberado. A ferramenta não realiza diagnóstico, teste psicológico, decisão automatizada, perfil comportamental para publicidade ou pontuação clínica automatizada.</p>

<h2>4. Onde o conteúdo fica e por quanto tempo</h2>
<p>Por padrão, as respostas existem apenas na memória da página durante o uso. A aplicação não possui banco de dados próprio nem analytics próprio para armazenar o conteúdo clínico.</p>
<p>Se o usuário ativar explicitamente <strong>“Manter rascunho somente nesta aba”</strong>, as respostas são gravadas em <code>sessionStorage</code> sob a chave <code>rpd_draft</code>. O rascunho permanece restrito à sessão daquela aba e é removido quando o usuário inicia um novo registro ou desativa o recurso. Alguns navegadores podem restaurar sessões/abas após fechamento inesperado; em equipamento compartilhado, recomenda-se desativar o rascunho e fechar a aba ao terminar.</p>
<p>O player de áudio pode guardar em <code>localStorage</code>, sob a chave <code>rpd.audioProgress.n3</code>, somente o identificador do áudio e o segundo aproximado de reprodução. Esse dado não contém respostas clínicas. Ele permanece até ser substituído ou removido pelo próprio navegador/usuário.</p>

<h2>5. PDF e impressão</h2>
<p>O PDF é produzido pela função de impressão do navegador. O conteúdo é montado localmente. Depois que o arquivo é salvo, sua proteção, retenção e eventual compartilhamento passam a depender do dispositivo e das escolhas do usuário.</p>

<h2>6. WhatsApp e compartilhamento</h2>
<p>Quando o usuário escolhe compartilhar um registro ou preparar uma mensagem de contato, o RPD monta o texto localmente e abre o WhatsApp com conteúdo pré-preenchido. Nada é enviado pelo RPD sem a confirmação do próprio usuário no serviço externo. A partir dessa ação, o tratamento também fica sujeito às práticas do WhatsApp e do destinatário escolhido.</p>

<h2>7. YouTube e áudio</h2>
<p>O áudio do RPD é servido pelo próprio site. O vídeo usa <code>youtube-nocookie.com</code> e somente cria a conexão com o YouTube depois que o usuário pressiona “Carregar vídeo”. O RPD aplica política de referência restrita e limita as permissões concedidas ao iframe.</p>

<h2>8. Hospedagem e dados técnicos</h2>
<p>O site é publicado por meio do GitHub Pages. A infraestrutura do provedor pode processar dados técnicos necessários à entrega, segurança e operação do serviço, conforme suas próprias políticas. O RPD não mantém um banco próprio desses registros técnicos.</p>

<h2>9. Segurança e minimização</h2>
<p>A aplicação adota minimização de dados, ausência de persistência clínica por padrão, rascunho opt-in restrito à sessão da aba, carregamento externo sob ação explícita, política de segurança de conteúdo (CSP), política de referência restrita e compartilhamento deliberado. Nenhum sistema elimina integralmente riscos; por isso, evite inserir dados desnecessários de terceiros e revise o conteúdo antes de imprimir ou compartilhar.</p>

<h2>10. Direitos do titular</h2>
<p>A LGPD prevê direitos como confirmação da existência de tratamento, acesso, correção, informação sobre compartilhamento e, conforme o caso, bloqueio, anonimização, eliminação e revogação de consentimento. Como o conteúdo clínico do RPD não é recebido pelo responsável por padrão, grande parte do controle permanece diretamente com o usuário no navegador. Se algum dado tiver sido efetivamente enviado em contato profissional, o pedido relativo a esse dado pode ser feito pelo canal indicado na seção 1.</p>

<h2>11. Crianças e adolescentes</h2>
<p>O RPD não foi concebido para solicitar identificação de crianças ou adolescentes nem para criar perfis desse público. Quando a ferramenta for utilizada por pessoa menor de idade, recomenda-se uso compatível com sua compreensão, com mediação responsável/profissional quando necessária e sempre considerando seu melhor interesse. Evite inserir nome completo, escola, endereço ou outros identificadores desnecessários.</p>

<h2>12. Limites clínicos e situações de urgência</h2>
<p>O RPD é uma ferramenta psicoeducativa inspirada na Terapia Cognitivo-Comportamental. Não é teste psicológico, prontuário profissional, diagnóstico nem substitui atendimento psicológico, médico ou de urgência.</p>
<p>Em risco imediato de autoagressão, tentativa de suicídio, ameaça iminente à vida ou impossibilidade de permanecer em segurança, a orientação é buscar serviço de urgência: <strong>SAMU 192, UPA 24h, pronto-socorro ou hospital</strong>. O <strong>CVV 188</strong> oferece apoio emocional e conversa sigilosa, mas não substitui atendimento de urgência.</p>

<h2>13. Fundamentação e referências públicas</h2>
<ul class="privacy-refs">
<li><a href="https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/self-help-cbt-techniques/thought-record/" target="_blank" rel="noopener noreferrer">NHS · Every Mind Matters — Thought record</a>.</li>
<li><a href="https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/self-help-cbt-techniques/reframing-unhelpful-thoughts/" target="_blank" rel="noopener noreferrer">NHS · Reframing unhelpful thoughts</a>.</li>
<li><a href="https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/suicidio-prevencao/suicidio-prevencao" target="_blank" rel="noopener noreferrer">Ministério da Saúde — Prevenção do suicídio</a>.</li>
<li><a href="https://www.gov.br/saude/pt-br/composicao/saes/samu-192" target="_blank" rel="noopener noreferrer">Ministério da Saúde — SAMU 192</a>.</li>
<li><a href="https://www.gov.br/anpd/pt-br/acesso-a-informacao/aviso-de-privacidade" target="_blank" rel="noopener noreferrer">ANPD — Aviso de Privacidade</a>.</li>
<li><a href="https://www.gov.br/anpd/pt-br/assuntos/titular-de-dados-1/direito-dos-titulares" target="_blank" rel="noopener noreferrer">ANPD — Direitos dos titulares</a>.</li>
<li><a href="https://www.gov.br/anpd/pt-br/assuntos/noticias/anpd-divulga-enunciado-sobre-o-tratamento-de-dados-pessoais-de-criancas-e-adolescentes" target="_blank" rel="noopener noreferrer">ANPD — tratamento de dados de crianças e adolescentes</a>.</li>
<li><a href="https://transparencia.cfp.org.br/crp10/pergunta-frequente/publicidade-profissional/" target="_blank" rel="noopener noreferrer">Sistema Conselhos de Psicologia — publicidade profissional</a>.</li>
</ul>
<p>As referências são apresentadas para transparência conceitual e normativa e não significam endosso institucional do RPD.</p>

<p class="privacy-return"><a class="btn btn-secondary" href="./">Voltar ao RPD</a></p>
</article>
</main>
</body>
</html>
'''
write("privacidade.html", privacy)

privacy_css = '''.privacy-page{min-height:100vh}.privacy-main{width:min(100% - 32px,860px);margin:34px auto;padding:0}.privacy-back{display:inline-flex;margin-bottom:18px;text-decoration:none;color:var(--primary);font-weight:850}.privacy-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow);padding:clamp(22px,5vw,40px)}.privacy-card h1{font-size:clamp(2rem,5vw,3rem);line-height:1.05;letter-spacing:-.035em;margin:8px 0 12px}.privacy-card h2{font-size:1.2rem;margin:30px 0 8px}.privacy-card p,.privacy-card li{color:var(--muted)}.privacy-card strong{color:var(--ink)}.privacy-card a{color:var(--primary);font-weight:800}.privacy-updated{margin-top:0}.privacy-notice{background:var(--surface2);border:1px solid var(--border);border-left:4px solid var(--primary);border-radius:14px;padding:14px 16px;color:var(--muted)}.privacy-refs{padding-left:1.25rem}.privacy-refs li{margin-bottom:10px}.privacy-return{margin-top:30px}.privacy-return .btn{color:var(--primary2)}code{overflow-wrap:anywhere}@media(max-width:480px){.privacy-main{width:min(100% - 20px,860px);margin:20px auto}.privacy-card{padding:20px 16px;border-radius:18px}}'''
write("assets/css/privacy.css", privacy_css + "\n")


# ---------------- Playwright config ----------------
playwright = '''const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30000,
  retries: 1,
  expect: { timeout: 7000 },
  use: {
    baseURL: 'http://127.0.0.1:4173',
    viewport: { width: 390, height: 844 },
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure'
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
    { name: 'firefox', use: { browserName: 'firefox' } },
    { name: 'webkit', use: { browserName: 'webkit' } }
  ],
  webServer: {
    command: 'python3 -m http.server 4173 --bind 127.0.0.1',
    url: 'http://127.0.0.1:4173',
    reuseExistingServer: true
  }
});
'''
write("playwright.config.js", playwright)


# ---------------- New tests ----------------
hardening_tests = r'''const { test, expect } = require('@playwright/test');

async function reachEssentialSummary(page){
  await page.locator('#modeEssential').check({ force: true });
  await page.locator('#situation').fill('Recebi uma mensagem curta.');
  await page.locator('.step[data-step="1"] .next').click();
  await page.locator('#emotion_0').check({ force: true });
  await page.locator('.step[data-step="2"] .next').click();
  await page.locator('#thought').fill('Fiz algo errado.');
  await page.locator('.step[data-step="3"] .next').click();
  await page.locator('#action').fill('Esperar e pedir esclarecimento.');
  await page.locator('.step[data-step="5"] .next').click();
}

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test('CSP, crise e versão de segurança estão presentes', async ({ page }) => {
  await expect(page.locator('meta[name="application-version"]')).toHaveAttribute('content', '2.3.2');
  const csp = await page.locator('meta[http-equiv="Content-Security-Policy"]').getAttribute('content');
  expect(csp).toContain("object-src 'none'");
  expect(csp).toContain('frame-src https://www.youtube-nocookie.com');
  await expect(page.locator('a[href="tel:192"]')).toContainText('SAMU');
  await expect(page.locator('#crise-imediata')).toContainText('UPA 24h');
  await expect(page.locator('#crise-imediata')).toContainText('pronto-socorro');
  await expect(page.locator('#crise-imediata')).toContainText('hospital');
  await expect(page.locator('#crise-imediata')).toContainText('apoio emocional');
});

test('usuário pode registrar que ainda não consegue nomear a emoção', async ({ page }) => {
  await page.locator('#situation').fill('Aconteceu algo difícil de nomear.');
  await page.locator('.step[data-step="1"] .next').click();
  const option = page.locator('input[name="emotion"][value="Não sei/não consigo nomear agora"]');
  await expect(option).toHaveCount(1);
  await option.check({ force: true });
  await page.locator('.step[data-step="2"] .next').click();
  await expect(page.locator('.step[data-step="3"]')).toHaveClass(/is-active/);
});

test('pensamento automático aceita formas não verbais', async ({ page }) => {
  await expect(page.locator('.step[data-step="3"]')).toContainText('imagem mental');
  await expect(page.locator('.step[data-step="3"]')).toContainText('lembrança');
  await expect(page.locator('.step[data-step="3"]')).toContainText('impulso');
});

test('rascunho restaura após reload na mesma aba', async ({ page }) => {
  await page.locator('#draftToggle').check();
  await page.locator('#situation').fill('Rascunho que deve voltar.');
  await expect.poll(() => page.evaluate(() => sessionStorage.getItem('rpd_draft'))).not.toBeNull();
  await page.reload();
  await expect(page.locator('#situation')).toHaveValue('Rascunho que deve voltar.');
  await expect(page.locator('#draftToggle')).toBeChecked();
});

test('novo registro elimina rascunho e respostas', async ({ page }) => {
  await page.locator('#draftToggle').check();
  await page.locator('#situation').fill('Conteúdo temporário.');
  await page.locator('#newRecord').click();
  await expect(page.locator('#actionDialog')).toHaveAttribute('open', '');
  await page.locator('#actionConfirm').click();
  await expect(page.locator('#situation')).toHaveValue('');
  await expect.poll(() => page.evaluate(() => sessionStorage.getItem('rpd_draft'))).toBeNull();
});

test('popup bloqueado produz orientação sem perder o registro', async ({ page }) => {
  await reachEssentialSummary(page);
  await page.evaluate(() => { window.open = () => null; });
  await page.locator('#shareRecord').click();
  await page.locator('#shareSummary').click();
  await expect(page.locator('#toast')).toContainText('bloqueou a abertura do WhatsApp');
  await expect(page.locator('#summary')).toContainText('Recebi uma mensagem curta.');
});

test('mensagem de WhatsApp leva apenas conteúdo deliberadamente compartilhado', async ({ page }) => {
  await reachEssentialSummary(page);
  await page.evaluate(() => {
    window.__openedUrl = '';
    window.open = (url) => { window.__openedUrl = String(url); return {}; };
  });
  await page.locator('#shareRecord').click();
  await page.locator('#shareSummary').click();
  const opened = await page.evaluate(() => window.__openedUrl);
  expect(opened).toContain('https://wa.me/');
  const decoded = decodeURIComponent(opened.split('?text=')[1] || '');
  expect(decoded).toContain('Recebi uma mensagem curta.');
  expect(decoded).toContain('Fiz algo errado.');
});

test('falha de rede do YouTube não quebra o fluxo principal', async ({ page }) => {
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route('https://www.youtube-nocookie.com/**', route => route.abort());
  await page.locator('#loadVideo').click();
  await expect(page.locator('#videoSlot iframe')).toHaveCount(1);
  await page.locator('a[href="#form-area"]').first().click();
  await expect(page.locator('#situation')).toBeVisible();
  expect(errors).toEqual([]);
});

test('dialogs expõem nome acessível e devolvem foco ao invocador', async ({ page }) => {
  const opener = page.locator('[data-open-dialog="distortionDialog"]');
  await opener.focus();
  await opener.click();
  await expect(page.locator('#distortionDialog')).toHaveAttribute('aria-labelledby', 'distortionDialogTitle');
  await expect(page.locator('#distortionDialog [data-close-dialog]').first()).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(opener).toBeFocused();
});

test('PDF real é gerável e contém a síntese montada', async ({ page, browserName }) => {
  test.skip(browserName !== 'chromium', 'page.pdf é específico do Chromium');
  await reachEssentialSummary(page);
  await page.evaluate(() => window.dispatchEvent(new Event('beforeprint')));
  await expect(page.locator('#pSituation')).toHaveText('Recebi uma mensagem curta.');
  const pdf = await page.pdf({ format: 'A4', printBackground: true });
  expect(pdf.subarray(0, 4).toString()).toBe('%PDF');
  expect(pdf.length).toBeGreaterThan(10000);
});
'''
write("tests/hardening.spec.js", hardening_tests)

a11y_tests = r'''const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

async function expectNoSeriousOrCritical(page){
  const results = await new AxeBuilder({ page }).analyze();
  const blocking = results.violations.filter(v => ['serious','critical'].includes(v.impact));
  expect(blocking, blocking.map(v => `${v.id}: ${v.help}`).join('\n')).toEqual([]);
}

test('home sem violações axe serious/critical', async ({ page }) => {
  await page.goto('/');
  await expectNoSeriousOrCritical(page);
});

test('privacidade sem violações axe serious/critical', async ({ page }) => {
  await page.goto('/privacidade.html');
  await expectNoSeriousOrCritical(page);
});

test('reflow continua funcional em zoom equivalente a 400%', async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 800 });
  await page.goto('/');
  await page.evaluate(() => { document.documentElement.style.zoom = '4'; });
  const metrics = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: window.innerWidth }));
  expect(metrics.sw).toBeLessThanOrEqual(metrics.iw + 2);
});
'''
write("tests/a11y.spec.js", a11y_tests)

visual_tests = r'''const { test, expect } = require('@playwright/test');

for (const width of [320, 390, 768, 1366]) {
  test(`baseline visual ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: width < 700 ? 844 : 900 });
    await page.goto('/');
    await page.evaluate(() => window.scrollTo(0, 0));
    await expect(page).toHaveScreenshot(`rpd-home-${width}.png`, {
      fullPage: true,
      animations: 'disabled',
      caret: 'hide',
      maxDiffPixelRatio: 0.015
    });
  });
}
'''
write("tests/visual.spec.js", visual_tests)

manual_checklist = '''# RPD — checklist manual de acessibilidade assistiva\n\nRelease-alvo: v2.3.2\n\nEste checklist existe porque NVDA/VoiceOver exigem validação humana em dispositivo real. O CI automatizado não substitui esta prova.\n\n## NVDA + Windows\n- [ ] Percorrer cabeçalhos e landmarks.\n- [ ] Confirmar link de salto.\n- [ ] Executar modo essencial só com teclado.\n- [ ] Executar modo completo só com teclado.\n- [ ] Validar anúncio de erros obrigatórios.\n- [ ] Validar sliders e seus valores.\n- [ ] Abrir/fechar todos os dialogs; conferir nome, foco e retorno ao invocador.\n- [ ] Revisar síntese e botões de edição.\n- [ ] Confirmar bloco de crise e números 192/188.\n\n## VoiceOver + iOS\n- [ ] Percorrer hero, orientação e formulário por swipe.\n- [ ] Confirmar rótulos dos campos e estados selecionados.\n- [ ] Verificar controles do áudio.\n- [ ] Validar dialogs e retorno de foco.\n- [ ] Validar modo essencial em tela estreita.\n- [ ] Revisar síntese e ações finais.\n\n## Critério de fechamento\nA release só recebe chancela de acessibilidade humana após todos os itens acima serem executados sem bloqueadores.\n'''
write("ACCESSIBILITY_MANUAL_CHECKLIST.md", manual_checklist)


# ---------------- clinical basis ----------------
clinical_basis = f'''# RPD — base clínica, segurança e rastreabilidade\n\nVersão: {VERSION}\nAtualizado em: {DATE_ISO}\n\n| Decisão/claim | Aplicação no RPD | Fonte pública principal | Revisão |\n|---|---|---|---|\n| Estrutura de registro de pensamentos | situação, emoções, pensamento, evidências, alternativa e reavaliação | NHS Every Mind Matters — Thought record | {DATE_ISO} |\n| Reenquadramento sem “pensamento positivo” | investigar evidências e formular leitura mais completa/flexível | NHS — Reframing unhelpful thoughts | {DATE_ISO} |\n| Distorções são opcionais | classificação não é requisito para concluir o registro | adaptação clínica própria; coerente com caráter psicoeducativo | {DATE_ISO} |\n| Modo essencial é organização breve | 1 → 2 → 3 → 5 → 7; não equivale ao percurso completo | adaptação de ergonomia/carga cognitiva própria | {DATE_ISO} |\n| Crise: urgência ≠ apoio emocional | SAMU 192/UPA/pronto-socorro/hospital para urgência; CVV 188 para apoio emocional | Ministério da Saúde — Prevenção do suicídio e SAMU 192 | {DATE_ISO} |\n| Minimização e transparência de dados | conteúdo local por padrão; rascunho opt-in; externos sob ação deliberada | ANPD — Aviso de Privacidade e Direitos dos Titulares | {DATE_ISO} |\n| Crianças/adolescentes | orientar mediação e prevalência do melhor interesse | ANPD — Enunciado sobre tratamento de dados de crianças e adolescentes | {DATE_ISO} |\n| Identificação profissional | nome + Psicólogo clínico + CRP | Sistema Conselhos de Psicologia — publicidade profissional | {DATE_ISO} |\n\n## URLs canônicas\n- https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/self-help-cbt-techniques/thought-record/\n- https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/self-help-cbt-techniques/reframing-unhelpful-thoughts/\n- https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/suicidio-prevencao/suicidio-prevencao\n- https://www.gov.br/saude/pt-br/composicao/saes/samu-192\n- https://www.gov.br/anpd/pt-br/acesso-a-informacao/aviso-de-privacidade\n- https://www.gov.br/anpd/pt-br/assuntos/titular-de-dados-1/direito-dos-titulares\n- https://www.gov.br/anpd/pt-br/assuntos/noticias/anpd-divulga-enunciado-sobre-o-tratamento-de-dados-pessoais-de-criancas-e-adolescentes\n- https://transparencia.cfp.org.br/crp10/pergunta-frequente/publicidade-profissional/\n\nAs referências sustentam transparência e rastreabilidade; não representam endosso institucional do produto.\n'''
write("CLINICAL_BASIS.md", clinical_basis)


# ---------------- recurring link checker ----------------
check_links = r'''from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

URLS = [
  'https://ricmurtapsicologia.github.io/RPD/',
  'https://ricmurtapsicologia.github.io/RPD/privacidade.html',
  'https://www.cvv.org.br/chat/',
  'https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/suicidio-prevencao/suicidio-prevencao',
  'https://www.gov.br/saude/pt-br/composicao/saes/samu-192',
  'https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/self-help-cbt-techniques/thought-record/',
  'https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/self-help-cbt-techniques/reframing-unhelpful-thoughts/',
  'https://www.gov.br/anpd/pt-br/acesso-a-informacao/aviso-de-privacidade',
  'https://www.gov.br/anpd/pt-br/assuntos/titular-de-dados-1/direito-dos-titulares',
  'https://transparencia.cfp.org.br/crp10/pergunta-frequente/publicidade-profissional/',
]

failed=[]
for url in URLS:
    try:
        req=Request(url, headers={'User-Agent':'RPD-link-check/2.3.2'})
        with urlopen(req, timeout=20) as response:
            code=getattr(response,'status',200)
            print(code, response.geturl())
            if code >= 400:
                failed.append((url, code))
    except (HTTPError, URLError, TimeoutError) as exc:
        failed.append((url, str(exc)))
if failed:
    raise SystemExit('Links com falha: ' + repr(failed))
print('Link integrity: OK')
'''
write("scripts/check_links.py", check_links)

link_workflow = '''name: RPD Link Integrity\n\non:\n  schedule:\n    - cron: '17 10 * * 1'\n  workflow_dispatch:\n\npermissions:\n  contents: read\n\njobs:\n  links:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n        with:\n          python-version: '3.13'\n      - name: Check critical public links\n        run: python3 scripts/check_links.py\n'''
write(".github/workflows/link-check.yml", link_workflow)


# ---------------- CI / live smoke ----------------
ci = read(".github/workflows/ci.yml")
ci = ci.replace(
    "      - name: Install Chromium\n        run: npx playwright install --with-deps chromium",
    "      - name: Install Playwright browsers\n        run: npx playwright install --with-deps chromium firefox webkit",
)
write(".github/workflows/ci.yml", ci)

live = read(".github/workflows/live-smoke.yml").replace("2.3.1", VERSION)
live = replace_once(
    live,
    "              && grep -Fq 'href=\"tel:188\"' <<<\"$HTML\" \\",
    "              && grep -Fq 'href=\"tel:192\"' <<<\"$HTML\" \\\n              && grep -Fq 'href=\"tel:188\"' <<<\"$HTML\" \\\n              && grep -Fq 'Content-Security-Policy' <<<\"$HTML\" \\",
    "live smoke segurança",
)
write(".github/workflows/live-smoke.yml", live)


# ---------------- validate.py ----------------
validate = read("scripts/validate.py")
validate = replace_once(
    validate,
    "    'href=\"tel:188\"', 'aria-label=\"Ligar para o CVV no número 188\"',",
    "    'href=\"tel:192\"', 'aria-label=\"Ligar para o SAMU no número 192\"',\n    'href=\"tel:188\"', 'aria-label=\"Ligar para o CVV no número 188\"',\n    'Content-Security-Policy', 'assets/og-card.png', 'Não sei/não consigo nomear agora',",
    "validate html segurança",
)
validate = replace_once(
    validate,
    "    'https://transparencia.cfp.org.br/crp10/pergunta-frequente/publicidade-profissional/'",
    "    'https://transparencia.cfp.org.br/crp10/pergunta-frequente/publicidade-profissional/',\n    'SAMU 192', 'Direitos do titular', 'Crianças e adolescentes', 'gov.br/anpd'",
    "validate privacidade",
)
validate += '''\n\nrequired_files = [\n    'assets/og-card.png', 'assets/css/privacy.css', 'CLINICAL_BASIS.md',\n    'ACCESSIBILITY_MANUAL_CHECKLIST.md', 'tests/hardening.spec.js', 'tests/a11y.spec.js',\n    'tests/visual.spec.js', 'scripts/check_links.py', '.github/workflows/link-check.yml'\n]\nfor rel in required_files:\n    if not (ROOT / rel).exists():\n        raise SystemExit(f'Arquivo de hardening ausente: {rel}')\n'''
write("scripts/validate.py", validate)


# ---------------- sitemap ----------------
sitemap = read("sitemap.xml")
sitemap = re.sub(r'<lastmod>\d{4}-\d{2}-\d{2}</lastmod>', f'<lastmod>{DATE_ISO}</lastmod>', sitemap)
write("sitemap.xml", sitemap)


# ---------------- package.json ----------------
package = json.loads(read("package.json"))
package["version"] = VERSION
package.setdefault("scripts", {})["test:e2e"] = "playwright test"
package["scripts"]["test:visual"] = "playwright test tests/visual.spec.js"
package["scripts"]["test:a11y"] = "playwright test tests/a11y.spec.js"
write("package.json", json.dumps(package, ensure_ascii=False, indent=2) + "\n")


# ---------------- README / release notes ----------------
readme = read("README.md")
readme = readme.replace("**Versão canônica: v2.3.1 — 05/09/2026**", f"**Versão candidata: v{VERSION} — {DATE_ISO}**")
readme = readme.replace("## v2.3.1 — hardening, conformidade e consolidação", "## v2.3.2 — safety, privacy & QA hardening")
readme = readme.replace(
    "Release de saneamento que elimina o drift entre documentação, assets e runtime e incorpora os reparos técnicos, clínicos e de acessibilidade da linha v2.3.x.",
    "Release de hardening que mantém a base v2.3.x e fecha os principais achados de segurança clínica, privacidade, acessibilidade e validação multiplataforma.",
)
insert_after = "- identificação profissional pública: `Richelmy Murta Pinto · Psicólogo clínico · CRP 04/54.383`;\n"
extra = (
    "- protocolo de crise distingue urgência (SAMU 192/UPA/pronto-socorro/hospital) de apoio emocional (CVV 188);\n"
    "- CSP em meta compatível com GitHub Pages e redução das permissões do iframe do YouTube;\n"
    "- aviso de privacidade ampliado com finalidade, duração, compartilhamentos, direitos e proteção de crianças/adolescentes;\n"
    "- matriz `CLINICAL_BASIS.md` para rastreabilidade de decisões e fontes;\n"
    "- Playwright em Chromium, Firefox e WebKit, axe-core, PDF real, visual regression e novos cenários E2E;\n"
    "- verificador recorrente de links críticos;\n"
)
readme = replace_once(readme, insert_after, insert_after + extra, "README hardening")
readme = readme.replace("softwareVersion":"2.3.1", "softwareVersion":"2.3.2") if 'softwareVersion":"2.3.1"' in readme else readme
write("README.md", readme)

release = f'''# RPD v{VERSION} — Safety, Privacy & QA Hardening\n\nData: {DATE_ISO}\n\n## Objetivo\nFechar os bloqueadores remanescentes da auditoria completa da v2.3.1 sem alterar a finalidade psicoeducativa do RPD.\n\n## Mudanças\n- protocolo de crise alinhado às portas de urgência informadas pelo Ministério da Saúde;\n- separação explícita entre SAMU 192/UPA/pronto-socorro/hospital e apoio emocional pelo CVV 188;\n- aviso de privacidade ampliado e CSS de privacidade desacoplado de estilos inline;\n- CSP, referrer policy e menor privilégio no iframe externo;\n- opção “Não sei/não consigo nomear agora” para emoções;\n- pensamento automático explicitamente admite frase, imagem mental, lembrança, impulso ou significado;\n- modo essencial descrito como organização breve, sem equivalência à investigação completa;\n- foco e retorno de foco reforçados em dialogs;\n- fallback para popup do WhatsApp bloqueado;\n- E2E ampliado, axe-core, Chromium/Firefox/WebKit, PDF real e regressão visual;\n- link checker semanal;\n- base de rastreabilidade clínica e checklist manual NVDA/VoiceOver.\n\n## Gate\nA promoção a `main` exige `npm run validate` e `npm run test:e2e` verdes. A prova humana NVDA/VoiceOver permanece um gate manual explícito e não é simulada pelo CI.\n'''
write(f"RELEASE_v{VERSION}.md", release)


# ---------------- OG PNG ----------------
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as exc:
    raise SystemExit(f"Pillow necessário para gerar OG PNG: {exc}")
img = Image.new("RGB", (1200, 630), "#0b5d57")
draw = ImageDraw.Draw(img)
draw.rounded_rectangle((70, 70, 1130, 560), radius=42, fill="#173b37", outline="#d6aa63", width=3)
font_paths = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]
font_path = next((p for p in font_paths if Path(p).exists()), None)
if font_path:
    title_font = ImageFont.truetype(font_path, 76)
    sub_font = ImageFont.truetype(font_path, 34)
    small_font = ImageFont.truetype(font_path, 25)
else:
    title_font = sub_font = small_font = ImageFont.load_default()
draw.text((120, 135), "RPD", fill="#efd09a", font=title_font)
draw.text((120, 245), "Registro de Pensamentos", fill="white", font=sub_font)
draw.text((120, 315), "Uma trilha guiada para organizar situação, emoções,", fill="#dcebea", font=small_font)
draw.text((120, 355), "pensamentos, evidências e próximos passos.", fill="#dcebea", font=small_font)
draw.text((120, 455), "Richelmy Murta Pinto · Psicólogo clínico · CRP 04/54.383", fill="#efd09a", font=small_font)
img.save(ROOT / "assets/og-card.png", "PNG", optimize=True)


# Remove helper automation from the resulting release commit.
for rel in ["scripts/apply_v232.py", ".github/workflows/apply-v232.yml"]:
    path = ROOT / rel
    if path.exists():
        path.unlink()

print(f"RPD v{VERSION}: patch aplicado")
