# RPD — Registro de Pensamentos

**Versão atual: v2.1.0 — 02/08/2026**

Ferramenta web psicoeducativa para organizar situações, emoções ou estados, pensamentos automáticos, evidências, convicção cognitiva, valores, respostas alternativas e próximos passos.

Aplicação: https://ricmurtapsicologia.github.io/RPD/

> O RPD é um recurso psicoeducativo inspirado na Terapia Cognitivo-Comportamental. Não é teste psicológico, diagnóstico, prontuário profissional ou substituto de atendimento individualizado.

## O que mudou na v2.1.0

A versão 2.1.0 concentra o refinamento de **ergonomia cognitiva, UX clínica e arquitetura técnica**:

- entrada adaptativa: `Já sei usar` x `Primeira vez ou quero revisar`;
- conteúdo psicoeducativo por progressive disclosure;
- áudio mantido e servido localmente (`RPD1.mp3`);
- vídeo mantido, em `youtube-nocookie.com`, com carregamento somente após clique;
- guia de distorções aberto em diálogo, sem retirar o paciente da etapa 3;
- cada distorção possui definição, exemplo e pergunta de reconhecimento;
- seleção múltipla de emoções ou estados;
- campo específico quando `Outra` é selecionada;
- medida de convicção no pensamento automático antes/depois (0–100);
- desconforto global antes/depois mantido como dimensão separada;
- etapa de investigação com revelação progressiva;
- evidências contrárias e explicação alternativa deixaram de ser obrigatórias;
- valores e ação passaram a ser explicitamente uma ampliação opcional do RPD;
- ajuda contextual para o conceito de valor;
- textareas com crescimento automático;
- navegação inferior sticky no mobile;
- remoção do percentual redundante da barra de progresso;
- campos marcados como necessários ou opcionais;
- mensagens de erro inline, menos disruptivas;
- rascunho opcional via `sessionStorage`, desativado por padrão e restrito à aba;
- aviso de saída quando há conteúdo não preservado;
- síntese agrupada por raciocínio clínico com botão `Editar` por bloco;
- hierarquia de CTA final: PDF → compartilhar → novo registro;
- compartilhamento em `Resumo essencial` ou `Registro completo`;
- substituição de `confirm()` por diálogos próprios;
- HTML, CSS e JavaScript separados por responsabilidade;
- Content Security Policy básica adicionada;
- versão exibida na interface e documentada no README.

## Arquitetura clínica

A trilha permanece em 7 etapas:

1. **Contexto** — episódio específico e observável.
2. **Emoções ou estados** — seleção múltipla + desconforto global.
3. **Pensamento automático** — frase mental + convicção + padrões cognitivos opcionais.
4. **Investigação** — evidências que sustentam, possíveis lacunas, explicações alternativas e perspectiva.
5. **Valores e ação possível** — módulo ampliado e opcional.
6. **Nova leitura e reavaliação** — resposta alternativa + convicção + desconforto.
7. **Síntese** — percurso organizado, edição direta, PDF e compartilhamento deliberado.

## Convicção x desconforto

A aplicação trata separadamente:

- **convicção cognitiva**: quanto o pensamento parece verdadeiro (0–100);
- **desconforto global**: intensidade geral do episódio (0–100).

A mudança em qualquer uma dessas medidas é apresentada de forma descritiva. Redução não é interpretada automaticamente como sucesso, nem aumento como fracasso.

## Distorções cognitivas

A classificação é opcional e admite múltiplas escolhas. O paciente não precisa conhecer os nomes previamente. Cada padrão contém:

- definição em linguagem simples;
- exemplo cotidiano;
- pergunta de reconhecimento.

Também existem `Não identifiquei um padrão` e `Não sei ainda`.

## Privacidade por desenho

- sem banco de dados próprio;
- sem analytics próprio;
- sem `localStorage` para conteúdo clínico;
- nome ou iniciais opcionais;
- rascunho opcional apenas em `sessionStorage` da própria aba;
- rascunho desativado por padrão;
- PDF montado localmente via impressão do navegador;
- compartilhamento somente após ação explícita;
- vídeo externo carregado apenas após clique.

## Arquitetura técnica

Na v2.1.0, CSS e JavaScript foram separados por responsabilidade. O HTML é composto por `_includes` Jekyll semânticos por seção, evitando os antigos fragmentos arbitrários que cortavam CSS, HTML e JavaScript no meio do documento:

```text
/
├── index.html
├── privacidade.html
├── README.md
├── robots.txt
├── sitemap.xml
├── RPD1.mp3
├── _includes/
│   ├── v210_head.html
│   ├── v210_intro.html
│   ├── v210_steps_2_4.html
│   ├── v210_steps_5_7.html
│   ├── v210_support_print.html
│   └── v210_dialogs.html
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

## Controle de qualidade

O script `scripts/validate.sh` executa uma verificação sem dependências de framework: valida a sintaxe do JavaScript, confirma os sete passos na ordem correta, procura recursos críticos da versão e detecta IDs HTML duplicados.

```bash
bash scripts/validate.sh
```

## Acessibilidade e ergonomia cognitiva

A interface utiliza labels associados, navegação por teclado, `aria-live`, barra de progresso, áreas de toque adequadas, `prefers-reduced-motion`, texto alinhado à esquerda, progressive disclosure, diálogos nativos, mensagens de erro inline, autoexpansão de texto e navegação sticky no mobile.

O princípio de UX da versão é: **menos esforço para operar a ferramenta e mais energia disponível para refletir sobre a experiência**.

## Histórico de versões

### v2.1.0 — 02/08/2026
Refinamento de ergonomia cognitiva, UX clínica, convicção cognitiva, progressive disclosure, rascunho de sessão, síntese editável e arquitetura modular.

### v2.0.0 — 02/08/2026
Grande refatoração de privacidade, precisão clínica, PDF editorial, identidade visual e conteúdo multimídia/psicoeducativo.

## Limites

O RPD não deve ser utilizado para automatizar diagnóstico ou substituir julgamento clínico. Padrões cognitivos são hipóteses psicoeducativas, não rótulos obrigatórios. Valores e ação possível representam uma ampliação contemporânea do registro cognitivo clássico.
