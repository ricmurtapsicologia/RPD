# RPD — Registro de Pensamentos

**Versão atual: v2.3.0 — 02/08/2026**

Ferramenta web psicoeducativa para organizar situações, emoções ou estados, pensamentos automáticos, evidências, convicção cognitiva, valores, respostas alternativas e próximos passos.

Aplicação: https://ricmurtapsicologia.github.io/RPD/

> O RPD é um recurso psicoeducativo inspirado na Terapia Cognitivo-Comportamental. Não é teste psicológico, diagnóstico, prontuário profissional ou substituto de atendimento individualizado.

## v2.3.0 — hardening técnico, acessibilidade e consistência entre modos

A v2.3.0 consolida a arquitetura da v2.2.0 e corrige pontos de robustez identificados em auditoria técnica e de UX:

- troca entre modo completo e essencial passa a levar o usuário para a próxima etapa compatível, sem devolvê-lo ao início;
- modo essencial simplifica a etapa de ação: o foco passa a ser apenas um **próximo passo pequeno e possível**;
- edição a partir da síntese ganhou **Salvar alteração e voltar à síntese**;
- resposta alternativa pode ser explicitamente marcada como **ainda não consigo formular neste momento**, sem bloquear a conclusão;
- rascunho passa a usar chave estável `rpd_draft`, com `schemaVersion` e migração do rascunho legado da v2.2.0;
- escalas só passam a ser consideradas avaliadas após mudança real por `input` ou teclado;
- erros de formulário agora recebem `aria-invalid` e `aria-describedby`;
- barra de progresso ganhou semântica `role=progressbar` com valores ARIA atualizados;
- dourado de texto foi escurecido para melhorar contraste sem alterar a identidade visual;
- em telas muito pequenas a barra de progresso deixa de ser sticky, preservando área útil;
- PDF do modo essencial passou a esconder investigação, reavaliação e campos não percorridos;
- PDF essencial não mostra mais status/utilidade que o paciente não respondeu;
- política de privacidade foi sincronizada com a versão atual e com o comportamento real do `sessionStorage`;
- validação estrutural foi ampliada e há configuração de CI para executá-la automaticamente;
- foi adicionada suíte comportamental Playwright para fluxos críticos.

## v2.2.0 — ergonomia cognitiva para diferentes níveis de ativação

A v2.2.0 transforma o RPD em dois percursos compatíveis entre si:

- **modo essencial**: 5 passos, para momentos de maior sobrecarga ou quando o objetivo é apenas organizar o básico;
- **modo completo**: 7 etapas, mantendo investigação, valores, nova leitura e reavaliação.

Outras mudanças desta versão:

- paridade de versão entre HTML, CSS/JS, JSON-LD, rodapé e README;
- cache-busting atualizado para `?v=2.2.0`;
- preenchimento automático da data usando a data local do dispositivo, não UTC;
- posição sticky da barra de progresso calculada pela altura real da navegação;
- escalas começam como **Não avaliado** e só geram número depois de interação deliberada;
- `Não sei ainda` e `Não identifiquei um padrão` aparecem antes da lista de distorções;
- nome e significado da distorção ficam sempre visíveis; pergunta de reconhecimento e exemplo ficam sob expansão opcional;
- retirada da redundância de ajuda dentro da etapa 3; o guia modal permanece apenas na área psicoeducativa inicial;
- investigação cognitiva ficou integralmente opcional e com linguagem menos judicial;
- etapa de valores ganhou botão explícito **Pular por agora**;
- microcopy foi reduzida para evitar excesso de instruções simultâneas;
- resumo, PDF e compartilhamento se adaptam ao modo essencial ou completo;
- rascunho em `sessionStorage` preserva também modo escolhido e estado real das escalas.

## v2.1.2 — correção de UX clínica e área de impressão

A v2.1.2 corrige dois pontos observados em uso real:

- a área técnica usada para gerar o PDF passou a ficar totalmente oculta na tela e só é exibida em modo de impressão;
- as distorções cognitivas passaram a ser explicadas **no próprio ponto de escolha**, sem exigir que o paciente abra outro guia para compreender o significado;
- cada cartão mostra nome, significado curto, pergunta de reconhecimento e exemplo cotidiano;
- `Não identifiquei um padrão` e `Não sei ainda` permanecem disponíveis como escolhas legítimas;
- os cartões foram reorganizados para leitura em uma coluna em telas menores, reduzindo carga visual durante ativação emocional;
- a microcopy reforça que o paciente não precisa saber nomes técnicos nem “acertar” uma classificação.

## v2.1.1 — correção de estabilidade e renderização

A v2.1.1 é uma versão de depuração da v2.1.0. O foco foi remover regressões de mídia e layout sem perder os avanços clínicos e de UX.

Principais correções:

- `index.html` voltou a ser um documento HTML estático completo;
- removida a dependência de composição da página por Jekyll `_includes`;
- adicionado `.nojekyll` para servir os arquivos exatamente como estão no repositório;
- áudio explicativo restaurado e mantido sempre visível, servido por `./RPD1.mp3`;
- vídeo explicativo restaurado como recurso sempre visível e carregado sob demanda via `youtube-nocookie.com`;
- guia de distorções permanece acessível por diálogo contextual;
- CSS refeito com foco em consistência desktop/mobile, grids resilientes e prevenção de overflow;
- navegação, cards multimídia, formulários, diálogos e síntese revisados responsivamente;
- removida a Content Security Policy em `<meta>` da v2.1.0, que poderia interferir em estilos dinâmicos usados pela própria interface;
- `app.js` reescrito e validado sintaticamente;
- parâmetros de versão em CSS/JS (`?v=2.1.1`) ajudam a evitar cache de assets antigos;
- preservadas as sete etapas, convicção cognitiva antes/depois, desconforto global, rascunho opcional por aba, síntese editável, PDF e compartilhamento seletivo.

## Arquitetura clínica

A trilha permanece em 7 etapas:

1. **Contexto** — episódio específico e observável.
2. **Emoções ou estados** — seleção múltipla + desconforto global.
3. **Pensamento automático** — frase mental + convicção + padrões cognitivos opcionais.
4. **Investigação** — evidências que sustentam, possíveis lacunas, explicações alternativas e perspectiva.
5. **Valores e ação possível** — módulo ampliado e opcional.
6. **Nova leitura e reavaliação** — resposta alternativa + convicção + desconforto.
7. **Síntese** — percurso organizado, edição direta, PDF e compartilhamento deliberado.

## Ergonomia cognitiva e UX

A interface foi desenhada para reduzir carga mental durante o autorregistro:

- conteúdo principal dividido em sete etapas;
- áudio e vídeo disponíveis sem obrigar o paciente a consumi-los;
- guia de distorções sem sair do registro;
- exemplos e perguntas de reconhecimento para paciente leigo;
- progressive disclosure na investigação;
- campos claramente marcados como necessários ou opcionais;
- erros apresentados junto ao campo;
- escalas com âncoras semânticas;
- síntese agrupada por raciocínio clínico com edição direta;
- mobile com navegação compacta e responsiva.

## Convicção x desconforto

A aplicação separa:

- **convicção cognitiva** — quanto o pensamento parece verdadeiro (0–100);
- **desconforto global** — intensidade geral do episódio (0–100).

A mudança em qualquer medida é apresentada de forma descritiva, sem usar redução como sinônimo automático de sucesso.

## Distorções cognitivas

A classificação é opcional. Cada padrão inclui:

- definição em linguagem simples;
- exemplo cotidiano;
- pergunta de reconhecimento.

Também existem `Não identifiquei um padrão` e `Não sei ainda`.

## Privacidade por desenho

- sem banco de dados próprio;
- sem analytics próprio;
- sem `localStorage` para conteúdo clínico;
- rascunho opcional em `sessionStorage`, restrito à aba e desligado por padrão;
- nome ou iniciais opcionais;
- PDF gerado pela impressão nativa do navegador;
- compartilhamento somente após ação do usuário;
- vídeo externo carregado somente quando solicitado.

## Arquitetura técnica

Aplicação estática sem framework e sem dependências JavaScript de terceiros em tempo de execução.

```text
/
├── index.html
├── privacidade.html
├── README.md
├── robots.txt
├── sitemap.xml
├── RPD1.mp3
├── .nojekyll
├── assets/
│   ├── favicon.svg
│   ├── og-card.svg
│   ├── css/
│   │   ├── app.css
│   │   └── print.css
│   └── js/
│       └── app.js
└── scripts/
    └── validate.sh
```

## Validação

A validação de regressão deve verificar, no mínimo:

- sintaxe JavaScript;
- sete etapas presentes;
- IDs HTML sem duplicação;
- áudio `RPD1.mp3` presente;
- botão de vídeo e carregamento do iframe presentes;
- campos de convicção antes/depois;
- emoção `Outra` com campo de especificação;
- diálogo de distorções;
- síntese e compartilhamento em resumo/completo.

## Autoria

**Richelmy Murta · Psicólogo clínico**

A identificação profissional completa deve seguir as regras aplicáveis à divulgação profissional. Não inserir número de registro sem verificação da informação.
