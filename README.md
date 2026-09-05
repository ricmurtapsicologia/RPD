# RPD — Registro de Pensamentos

**Versão canônica: v2.3.1 — 05/09/2026**

Ferramenta web psicoeducativa para organizar situação, emoções ou estados, pensamentos automáticos, evidências, convicção cognitiva, valores, respostas alternativas e próximos passos.

Aplicação: https://ricmurtapsicologia.github.io/RPD/

> O RPD é um recurso psicoeducativo inspirado na Terapia Cognitivo-Comportamental. Não é teste psicológico, diagnóstico, prontuário profissional ou substituto de atendimento individualizado.

## v2.3.1 — hardening, conformidade e consolidação

Release de saneamento que elimina o drift entre documentação, assets e runtime e incorpora os reparos técnicos, clínicos e de acessibilidade da linha v2.3.x.

- identificação profissional pública: `Richelmy Murta Pinto · Psicólogo clínico · CRP 04/54.383`;
- versão sincronizada entre HTML, JavaScript, package, README, privacidade e JSON-LD;
- CVV com ligação pelo tridígito nacional `188`;
- política de privacidade sincronizada ao comportamento real do runtime;
- rascunho clínico opt-in em `sessionStorage`, chave estável `rpd_draft`, versão de esquema e migração do legado;
- progresso semântico, erros ARIA, foco, contraste, reduced motion e correções para telas pequenas;
- modos essencial (5 passos) e completo (7 etapas) testados independentemente;
- áudio N3 canônico e vídeo externo somente sob ação explícita;
- PDF/print adaptado ao percurso utilizado;
- validação estrutural derivada do `package.json`;
- suíte Playwright cobrindo fluxos clínicos, privacidade, mídia, acessibilidade, responsividade e impressão;
- CI em `main`, branches de release e pull requests;
- artefatos temporários de migração/diagnóstico removidos da árvore final;
- baseline anterior preservada em branch de rollback.

## Arquitetura clínica

Modo completo:

1. **Contexto** — episódio específico e observável.
2. **Emoções ou estados** — seleção múltipla e desconforto global opcional.
3. **Pensamento automático** — frase mental, convicção opcional e padrões cognitivos opcionais.
4. **Investigação** — evidências, lacunas, explicações alternativas e perspectiva.
5. **Valores e ação possível** — módulo opcional.
6. **Nova leitura e reavaliação** — resposta alternativa, convicção e desconforto.
7. **Síntese** — revisão, edição, PDF e compartilhamento deliberado.

O modo essencial percorre `1 → 2 → 3 → 5 → 7`, reduzindo decisões sem apagar o registro já realizado.

## Fundamentação

A arquitetura dialoga com o registro de pensamentos usado em Terapia Cognitivo-Comportamental. As referências públicas utilizadas para transparência conceitual são:

- NHS Every Mind Matters — Thought record: https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/self-help-cbt-techniques/thought-record/
- NHS Every Mind Matters — Reframing unhelpful thoughts: https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/self-help-cbt-techniques/reframing-unhelpful-thoughts/
- Sistema Conselhos de Psicologia — publicidade profissional: https://transparencia.cfp.org.br/crp10/pergunta-frequente/publicidade-profissional/

O RPD inclui adaptações próprias de linguagem, ergonomia, modo essencial, valores/ação, síntese, privacidade e compartilhamento. As instituições citadas não endossam o produto.

## Privacidade por desenho

- sem banco de dados próprio;
- sem analytics próprio;
- sem `localStorage` para conteúdo clínico;
- rascunho clínico somente por opt-in em `sessionStorage` e restrito à aba;
- o player de áudio pode guardar apenas o identificador do áudio e o segundo de reprodução em `localStorage` (`rpd.audioProgress.n3`), sem conteúdo clínico;
- nome ou iniciais opcionais;
- PDF montado localmente pela impressão nativa do navegador;
- compartilhamento somente após ação deliberada do usuário;
- vídeo via `youtube-nocookie.com` somente quando solicitado.

A política detalhada está em `privacidade.html`.

## Arquitetura técnica

Aplicação estática, sem framework e sem dependências JavaScript de terceiros em tempo de execução.

```text
/
├── index.html
├── privacidade.html
├── README.md
├── RELEASE_v2.3.1.md
├── robots.txt
├── sitemap.xml
├── package.json
├── package-lock.json
├── playwright.config.js
├── audio/
│   └── rpd1-n3.mp3
├── assets/
│   ├── favicon.svg
│   ├── og-card.svg
│   ├── css/
│   │   ├── app.css
│   │   └── print.css
│   └── js/
│       ├── app.js
│       └── audio-n3.js
├── scripts/
│   ├── validate.py
│   └── remaster_rpd_n3.py
├── tests/
│   ├── rpd.spec.js
│   └── runtime.spec.js
└── .github/workflows/
    ├── ci.yml
    └── remaster-audio-n3.yml
```

## Validação

```bash
npm ci
npm run validate
npx playwright install chromium
npm run test:e2e
```

O gate de release exige validação estrutural verde, runtime sem exceções JavaScript e regressão Playwright integralmente verde antes de promoção para `main`.

## Autoria e responsabilidade profissional

**Richelmy Murta Pinto · Psicólogo clínico · CRP 04/54.383**
