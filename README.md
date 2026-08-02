# RPD — Registro de Pensamentos

**Ferramenta web psicoeducativa para organizar situações, emoções, pensamentos automáticos, evidências, valores, respostas alternativas e próximos passos.**

Aplicação: https://ricmurtapsicologia.github.io/RPD/

> O RPD é um recurso psicoeducativo inspirado na Terapia Cognitivo-Comportamental. Não é teste psicológico, diagnóstico, prontuário profissional ou substituto de atendimento individualizado.

## Objetivo

O RPD transforma uma experiência difícil em uma sequência observável e revisável. Em vez de exigir que o usuário “pense positivo”, a ferramenta convida a:

1. separar fatos de interpretações;
2. nomear uma ou várias emoções;
3. registrar o pensamento automático;
4. identificar, de forma opcional, padrões cognitivos que talvez estejam presentes;
5. examinar evidências que sustentam e que não sustentam completamente a interpretação;
6. considerar explicações alternativas;
7. conectar valores a uma ação possível;
8. construir uma resposta alternativa mais equilibrada;
9. observar a mudança de intensidade sem tratá-la como nota de sucesso.

## Trilha em 7 etapas

1. **Contexto** — data, identificação opcional e descrição objetiva da situação.
2. **Emoções** — seleção múltipla e intensidade geral do desconforto antes da reflexão.
3. **Pensamento automático** — registro da frase mental e padrões cognitivos opcionais.
4. **Investigação bilateral** — evidências favoráveis, evidências contrárias/incompletas, outra explicação e perspectiva externa.
5. **Valores e ação** — valor relevante e pequena ação possível.
6. **Resposta alternativa** — formulação mais equilibrada e nova avaliação do desconforto.
7. **Síntese** — revisão, compartilhamento deliberado e versão para PDF.

## Emoções múltiplas

O usuário pode marcar várias emoções simultaneamente. A aplicação não pressupõe que apenas uma emoção esteja presente.

O slider não mede cada emoção separadamente. Ele representa a **intensidade geral do desconforto** no episódio, antes e depois da reflexão.

A mudança numérica é apresentada de forma descritiva, sem interpretar automaticamente redução como sucesso ou aumento como fracasso.

## Padrões cognitivos

A classificação de padrões de pensamento é opcional e admite múltiplas escolhas. A interface inclui um **guia para leigos** com definição e exemplo de cada padrão, além de um CTA na etapa 3 para consultar essas explicações antes de marcar qualquer opção.

Os padrões apresentados são: catastrofização, supergeneralização, leitura mental, personalização, tudo ou nada, desqualificação do positivo, raciocínio emocional, rotulação e filtro mental.

Também estão disponíveis:

- `Não identifiquei um padrão`
- `Não sei ainda`

Reconhecer um padrão não significa que o pensamento seja necessariamente falso. O objetivo é investigar se a leitura está completa, proporcional e suficientemente sustentada.

## Privacidade por desenho

- sem analytics próprio;
- sem banco de dados;
- sem armazenamento persistente do conteúdo preenchido;
- sem `localStorage` para registros clínicos;
- nome ou iniciais são opcionais;
- telefone não é solicitado;
- PDF é montado localmente e usa a impressão nativa do navegador;
- compartilhamento só ocorre após ação e confirmação do usuário;
- política de privacidade disponível em `privacidade.html`.

## Conteúdo multimídia

A página preserva dois recursos de apoio ao aprendizado:

- **áudio explicativo** (`RPD1.mp3`), hospedado no próprio repositório e carregado apenas quando o usuário decide reproduzi-lo;
- **vídeo explicativo**, incorporado com o modo de privacidade aprimorada do YouTube (`youtube-nocookie.com`) e carregamento adiado (`loading="lazy"`).

Ambos aparecem antes da trilha principal com CTAs para retornar diretamente ao registro após o conteúdo.

## PDF

A versão de impressão foi criada especificamente para A4 e organiza o conteúdo em blocos editoriais:

- identificação opcional, data e emoções;
- situação;
- pensamento automático e padrões percebidos;
- evidências que sustentam;
- evidências que não sustentam completamente;
- outra explicação possível;
- valores e ação;
- resposta alternativa;
- comparação descritiva do desconforto antes/depois;
- observações finais.

A aplicação não depende de jsPDF.

## Arquitetura

Aplicação estática, sem framework e sem dependências JavaScript externas de execução. O conteúdo principal funciona sem bibliotecas de terceiros; áudio e vídeo são recursos de mídia opcionais.

Principais arquivos:

```text
/
├── index.html
├── privacidade.html
├── README.md
├── robots.txt
├── sitemap.xml
├── RPD1.mp3
└── assets/
    ├── favicon.svg
    └── og-card.svg
```

## Acessibilidade

A interface utiliza:

- labels associados aos campos;
- navegação por teclado;
- `aria-live` para estados dinâmicos;
- feedback de progresso;
- foco em campos inválidos;
- botões com áreas de toque adequadas;
- `prefers-reduced-motion`;
- texto alinhado à esquerda;
- layout responsivo.

## Ecossistema

O RPD integra o mesmo ecossistema visual e funcional de:

- Guia de Apoio à Saúde Mental
- Emoção 360

## Segurança e apoio

A página inclui acesso a recursos externos de apoio para situações de sofrimento intenso. O RPD não deve ser usado como único recurso em uma emergência.

## Autoria

**Richelmy Murta · Psicólogo clínico**

A identificação profissional completa deve seguir as regras aplicáveis à divulgação profissional. Não inserir número de registro sem verificação da informação.

## Licença e uso

Antes de reutilizar conteúdo, identidade visual ou materiais clínicos, verifique autoria, finalidade e eventuais requisitos éticos ou profissionais aplicáveis.
