# RPD — Registro de Pensamentos

**Versão atual: v2.1.1 — 02/08/2026**

Ferramenta web psicoeducativa para organizar situações, emoções ou estados, pensamentos automáticos, evidências, convicção cognitiva, valores, respostas alternativas e próximos passos.

Aplicação: https://ricmurtapsicologia.github.io/RPD/

> O RPD é um recurso psicoeducativo inspirado na Terapia Cognitivo-Comportamental. Não é teste psicológico, diagnóstico, prontuário profissional ou substituto de atendimento individualizado.

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

A validação de regressão verifica, no mínimo:

- sintaxe JavaScript;
- sete etapas presentes;
- IDs HTML sem duplicação;
- áudio `RPD1.mp3` referenciado;
- botão de vídeo e carregamento do iframe presentes;
- campos de convicção antes/depois;
- emoção `Outra` com campo de especificação;
- diálogo de distorções;
- síntese e compartilhamento em resumo/completo.

## Autoria

**Richelmy Murta · Psicólogo clínico**

A identificação profissional completa deve seguir as regras aplicáveis à divulgação profissional. Não inserir número de registro sem verificação da informação.
