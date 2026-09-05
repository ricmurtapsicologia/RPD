# RPD v2.3.1 — Hardening, conformidade e consolidação

Data: 05/09/2026

Esta release consolida a implementação executável da série v2.3, elimina o drift v2.2/v2.3 e fecha os bloqueadores das auditorias 30/30 e 90/90 aplicáveis à página web.

## Gates da release

- versão única em HTML, JS, package, README, privacidade e JSON-LD;
- identificação profissional: Richelmy Murta Pinto · Psicólogo clínico · CRP 04/54.383;
- CVV 188 sem URI internacional incorreta;
- privacidade por desenho com rascunho opt-in em sessionStorage;
- acessibilidade ARIA, contraste, foco, reduced motion e mobile estreito;
- modo essencial e completo cobertos por regressão E2E;
- mídia externa carregada apenas por ação do usuário;
- PDF/print coerente com o modo utilizado;
- validação estrutural derivada do package.json;
- CI com validação + Playwright em main e release;
- baseline anterior preservada em branch de rollback.

A promoção a canônica só ocorre após CI verde, deployment do GitHub Pages e smoke test da URL pública.
