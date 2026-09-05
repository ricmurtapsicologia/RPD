# RPD v2.3.1 — Hardening, conformidade e consolidação

Data: 05/09/2026

Esta release consolida a implementação executável da série v2.3, elimina o drift v2.2/v2.3 e fecha os bloqueadores técnicos, de conformidade e editoriais aplicáveis à página web.

## Gates da release

- versão única em HTML, JS, package, README, privacidade e JSON-LD;
- identificação profissional: Richelmy Murta Pinto · Psicólogo clínico · CRP 04/54.383;
- CVV 188 sem URI internacional incorreta;
- privacidade por desenho com rascunho opt-in em `sessionStorage`;
- transparência explícita sobre o `localStorage` técnico do player de áudio, sem conteúdo clínico;
- fundamentação clínica e atribuições documentadas com referências públicas;
- acessibilidade ARIA, contraste, foco, reduced motion e mobile estreito;
- modo essencial e completo cobertos por regressão E2E;
- mídia externa carregada apenas por ação do usuário;
- PDF/print coerente com o modo utilizado;
- validação estrutural derivada do `package.json`;
- CI permanente em Node 24 com validação + Playwright em `main`, release e pull request;
- regressão de navegador: 25/25 testes aprovados na candidata antes da limpeza final;
- nova validação integral exigida após a limpeza e antes do merge;
- artefatos temporários de diagnóstico e workflows transitórios removidos;
- baseline anterior preservada em `backup/rpd-v2.2-baseline-2026-09-05`.

A promoção a canônica só ocorre após CI verde na árvore final, CI verde no pull request, deployment do GitHub Pages e smoke test da URL pública. Após a publicação, as auditorias 30/30 e 90/90 aplicáveis são reexecutadas sobre produção.
