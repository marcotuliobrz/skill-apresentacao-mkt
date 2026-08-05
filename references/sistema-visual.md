# Sistema visual

Um sistema, dois modos de página. Não são dois design systems: são dois **modos** do mesmo sistema, com a mesma tipografia estrutural (Sora para display, Plus Jakarta Sans para texto), a mesma semântica de cor e as mesmas regras de honestidade (`.nota`, `.metod`).

| Modo | Nome | Tema | Formato | Para que serve | Saída |
|---|---|---|---|---|---|
| A | `relatorio` | escuro | slide fixo 1920×1080 | dados, números, board reporting | PNG por slide + PDF 16:9 |
| B | `narrativa` | claro | página rolável com snap | contar história, mostrar produto, tour de telas | HTML navegável + PDF 338×190 mm |

Referência viva do modo A em disco: `assets/deck-relatorio.html`. Leia antes de escrever qualquer slide novo — ele é a fonte da verdade sobre proporção, densidade e tom.

Regra que vale para os dois modos: **não invente classe fora do contrato e não renomeie nada.** Se um layout não existe no contrato, o layout está errado, não o contrato.

---

## 1. Tokens — modo A (relatorio, escuro)

### 1.1 Superfície e texto

| Token | Valor | Para que serve |
|---|---|---|
| `--bg` | `#050507` | fundo do slide e do `body`. Quase preto, não preto puro: dá profundidade aos halos radiais |
| `--ink` | `#f5f3ff` | texto principal, números grandes, `<b>` dentro de `.nota`/`.metod` |
| `--muted` | `#a7a7bd` | `.subtitle`, `.card p`, `.brand`, `.closing`, corpo do `.metod` |
| `--faint` | `#71718a` | rótulo de apoio: `.stat .sb`, `.fl small`, `.fv small`, `.li .pct`, `.mini .l`, `.sfoot`, `.pageno`, `.nota` |
| `--line` | `rgba(255,255,255,.09)` | borda padrão de `.stat`, `.card`, `.li`, `.eyebrow` |
| `--line2` | `rgba(255,255,255,.15)` | borda de ênfase — só quando um bloco precisa se destacar de outro bloco vizinho já com `--line` |
| `--card` | `rgba(255,255,255,.035)` | fundo de `.stat`, `.card`, `.li`. Translúcido, para o halo do `.slide::before` atravessar |
| `--card2` | `rgba(255,255,255,.06)` | fundo de segundo nível: `.frame`, bloco dentro de bloco |

### 1.2 Cores semânticas

| Token | Valor | Significado | Uso típico |
|---|---|---|---|
| `--inbox` | `#34d399` | **positivo / realizado** | receita realizada, crescimento, canal próprio, "ganhas" |
| `--gestor` | `#60a5fa` | **neutro / comparação** | base de comparação, total de entrada, mês anterior, benchmark |
| `--pipeline` | `#fbbf24` | **atenção / pendente** | pipeline em aberto, taxa que precisa subir, dado incompleto |
| `--alerta` | `#f87171` | **perda** | oportunidade perdida, queda, falha de entrega |
| `--ia` | `#a78bfa` | **IA / inferência** | leitura assistida por IA, classificação inferida, projeção |
| `--dist` | `#f472b6` | **distribuição** | cauda longa, "demais canais", fatia residual |
| `--dados` | `#2dd4bf` | **dado bruto / infraestrutura** | contagem de base, volume de registros, tabela de origem |
| `--cyan` | `#22d3ee` | **acento de composição** | terceiro halo do fundo e degradê da capa. Não carrega semântica sozinho |

Cores auxiliares fixas (usadas inline, não são tokens):

| Cor | Valor | Onde |
|---|---|---|
| verde claro | `#6ee7b7` | delta positivo dentro de `.stat .sb`, texto de `.chip.up` |
| vermelho claro | `#fca5a5` | delta negativo dentro de `.stat .sb`, texto de `.chip.down` |
| azul claro | `#93c5fd` | `.metod .h` (cabeçalho do bloco de metodologia) |
| branco | `#fff` | `.brand b`, `.stat` de valor total absoluto (dinheiro consolidado) |

### 1.3 Tipografia

| Token | Valor |
|---|---|
| `--display` | `"Sora", system-ui, sans-serif` |
| `--sans` | `"Plus Jakarta Sans", system-ui, sans-serif` |

Sora entra em título, número e rótulo curto. Plus Jakarta Sans entra em tudo que é frase corrida.

---

## 2. Tokens — modo B (narrativa, claro)

### 2.1 Superfície e texto

| Token | Valor | Para que serve |
|---|---|---|
| `--bg` | `#FFFFFF` | fundo da `.page` padrão |
| `--bg-subtle` | `#F7F7FA` | fundo da `.page--alt` — alterna com a branca para marcar capítulo |
| `--surface` | `#FFFFFF` | cartão sobre `--bg-subtle`: `.persona-card`, `.compare-card`, `.frame` |
| `--surface-2` | `#F2F1F6` | segundo nível: `.frame__bar`, `.ledger__ico`, `.agenda-item__ico`, `.shift__side` |
| `--border` | `#E7E7EE` | borda padrão de cartão, régua de `.ledger__row`, divisor |
| `--border-strong` | `#D6D5E2` | borda de item ativo, `.total__sep`, contorno do `.frame` |
| `--text` | `#201E33` | texto principal, `h1`–`h4`, número |
| `--text-soft` | `#4B495E` | `p`, `.lede`, corpo de `.spec-row`, `.callout` |
| `--text-muted` | `#7B7A8C` | rótulo, `.stat-box__label`, `.ledger__sub`, `.capa__meta` |
| `--text-dim` | `#A6A5B4` | decorativo: `.frame__url`, `.frame__dots`, numeração de apoio, ícone inativo |
| `--ink` | `#17162A` | fundo da `.page--dark` (e da `.page--capa`/`.page--fim` quando escuras) |

### 2.2 Marca e movimento

| Token | Valor | Para que serve |
|---|---|---|
| `--accent` | `#DB824E` | laranja de marca. **Superfície e traço**: preenchimento de ícone, barra, `.hud-btn` ativo, texto sobre `--ink` |
| `--accent-soft` | `#C96C35` | versão escurecida para **texto sobre fundo claro** (`em.acc`, `.spec-row__role`, `.metod .h` do modo B) |
| `--accent-dim` | `#FCEEE3` | tinta clara de fundo: `.callout`, `.badge-soon`, `.agenda-item__ico--brand`, `.flow-step--last` |
| `--eyebrow` | `#9F5697` | magenta do `.eyebrow` e da régua `::before` que o antecede |
| `--ease` | `cubic-bezier(0.16,1,0.3,1)` | curva única de toda animação e transição. Não use outra |

---

## 3. Escala tipográfica

### 3.1 Modo A — escala fixa (o slide tem 1920×1080; não use `clamp`)

| Elemento | Família | Peso | Tamanho | Line-height | Letter-spacing |
|---|---|---|---|---|---|
| `.cover h1` | display | 800 | `6.6rem` | `1.0` | `-.03em` |
| `.cover .lede` | sans | 400 (`b` = 600) | `1.7rem` | `1.5` | — |
| `.mini .n` | display | 800 | `2.9rem` | `1` | `-.02em` |
| `.mini .l` | sans | 400 | `1.05rem` | — | — |
| `.title` | display | 700 | `3.5rem` | padrão | `-.02em` |
| `.subtitle` | sans | 400 (`b` = 600) | `1.45rem` | padrão | — |
| `.eyebrow` | sans | 600 | `.92rem` | — | `.17em` + `uppercase` |
| `.brand` | display | 700 | `1.15rem` | — | `.02em` |
| `.pageno` | display | 600 | `1rem` | — | `.05em` |
| `.stat .big` | display | 800 | `4.9rem` | `.95` | `-.03em` |
| `.stat .lb` | sans | 600 | `1.5rem` | — | — |
| `.stat .sb` | sans | 400 | `1.1rem` | `1.4` | — |
| `.card .ic` | — | — | `3.1rem` | `1` | — |
| `.card h3` | display | 600 | `1.86rem` | `1.18` | `-.01em` |
| `.card p` | sans | 400 | `1.24rem` | `1.5` | — |
| `.card .tag` | display | 600 | `1rem` | — | `.03em` |
| `.fstep .fl` | display | 600 | `1.6rem` | — | — |
| `.fstep .fl small` | sans | 400 | `1.05rem` | — | — |
| `.fstep .fill` | display | 800 | `1.5rem` | — | — |
| `.fstep .fv` | display | 700 | `1.5rem` | — | — |
| `.fstep .fv small` | sans | 400 | `1rem` | — | — |
| `.li .nome` | sans | 400 | `1.3rem` | — | — |
| `.li .nome small` | sans | 400 | `1rem` | — | — |
| `.li .val` | display | 800 | `1.7rem` | — | — |
| `.li .pct` | sans | 400 | `1.05rem` | — | — |
| `.chip` | display | 700 | `1rem` | — | `.02em` |
| `.closing` | display | 600 | `1.9rem` | `1.4` | — |
| `.nota` | sans | 400 (`b` = 600) | `1.05rem` | `1.6` | — |
| `.metod` | sans | 400 (`b` = 600) | `1.06rem` | `1.6` | — |
| `.metod .h` | display | 700 | `1rem` | — | `.12em` + `uppercase` |

Reduções de `.funil.compacto`: `.fl` `1.45rem` · `.fl small` `.98rem` · `.fv` `1.38rem` · `.fv small` `.94rem` · `.fill` `1.35rem`.

### 3.2 Modo B — escala fluida (a página respira com o viewport)

| Elemento | Família | Peso | Tamanho | Line-height | Cor |
|---|---|---|---|---|---|
| `.capa__title`, `h1` | display | 800 | `clamp(3.2rem, 6.2vw, 6.4rem)` | `1.02` / `-.03em` | `--text` (ou `#fff` em `.page--dark`) |
| `h2` | display | 700 | `clamp(2.2rem, 3.6vw, 3.4rem)` | `1.08` / `-.02em` | `--text` |
| `h3` | display | 600 | `clamp(1.4rem, 1.9vw, 1.85rem)` | `1.2` | `--text` |
| `h4` | display | 600 | `1.16rem` | `1.3` | `--text` |
| `.lede`, `.capa__sub` | sans | 400 | `clamp(1.05rem, 1.35vw, 1.35rem)` | `1.55` | `--text-soft` |
| `p` | sans | 400 | `1.02rem` | `1.65` | `--text-soft` |
| `.eyebrow` | sans | 600 | `.78rem` | — / `.16em` / `uppercase` | `--eyebrow` |
| `.capa-stat`, `.stat-box__value` | display | 800 | `2.6rem` | `1` | `--text` |
| `.stat-box__label`, `.capa__meta` | sans | 500 | `.82rem` | `1.4` | `--text-muted` |
| `.total__num` | display | 800 | `clamp(3rem, 5vw, 4.8rem)` | `1` | `--text` |
| `.total__num--sm` | display | 800 | `2.4rem` | `1` | `--text` |
| `.total__unit`, `.total__text` | sans | 500 | `.95rem` | `1.5` | `--text-muted` |
| `.spec-row__role`, `.compare-card__tag`, `.badge-soon`, `.agenda-item__label span`, `.shift__tag` | display | 600 | `.8rem` | — / `.1em` / `uppercase` | `--accent-soft` ou `--text-muted` |
| `.agenda-item__num` | display | 700 | `1.05rem` | — | `--text-dim` |
| `.ledger__name` | display | 600 | `1.02rem` | — | `--text` |
| `.ledger__sub` | sans | 400 | `.86rem` | `1.45` | `--text-muted` |
| `.ledger__price b` | display | 700 | `1.25rem` | — | `--text` |
| `.ledger__price span` | sans | 400 | `.8rem` | — | `--text-muted` |
| `.frame__url` | sans | 500 | `.78rem` | — | `--text-dim` |
| `.frame__note`, `.callout` | sans | 400 | `.92rem` | `1.6` | `--text-soft` |
| `.flow-step` | display | 600 | `.95rem` | `1.3` | `--text` |
| `.closing em` | display | 600 | `clamp(1.5rem, 2.4vw, 2.2rem)` | `1.35` | `--text` |
| `.persona-card__role` | sans | 500 | `.86rem` | `1.45` | `--text-muted` |

### 3.3 Quando cada peso entra

| Peso | Entra em |
|---|---|
| **800** (só Sora) | número que é a resposta do slide: `.stat .big`, `.mini .n`, `.li .val`, `.fill`, `.capa-stat`, `.stat-box__value`, `.total__num`, `h1`. Um slide tem **um** nível de 800 |
| **700** (Sora) | `.title`, `h2`, `.fv`, `.chip`, `.brand`, `.metod .h`, `.ledger__price b` |
| **600** | subtítulo estrutural (`h3`, `h4`, `.card h3`, `.fl`, `.closing`), rótulo em caixa-alta (`.eyebrow`, `.spec-row__role`, `.tag`), e `<b>` dentro de texto corrido |
| **500** | rótulo de apoio do modo B (`.stat-box__label`, `.ledger__price span`, `.frame__url`) |
| **400** | todo texto corrido: `p`, `.lede`, `.nota`, `.metod`, `.sb`, `small` |

**Números sempre com `font-variant-numeric: tabular-nums`.** Sem isso, `1.967` e `5.428` empilhados desalinham e a coluna parece torta.

---

## 4. Grade e espaçamentos

### 4.1 Modo A — orçamento vertical do slide

O slide tem `1920×1080`, `padding: 96px 130px`, `overflow: hidden`. **A altura útil da coluna é 888px.** O `.sfoot` é `position:absolute; bottom:56px` e cabe dentro do padding inferior — mas o que passar dos 888px é cortado e **some sem aviso**. Essa é a causa nº 1 de slide quebrado.

| Bloco | Altura que consome |
|---|---|
| `.shead` | 36px (28 + 8 de margem) |
| `.eyebrow` (só capa) | ~40px |
| `.title` | ~103px (30 de margem + 67 de caixa + 6) |
| `.subtitle` | ~39px |
| `.stats` (1 linha) | ~300px |
| `.feat` (3 cards) | 340–420px conforme o texto |
| `.funil` — cada `.fstep` | 78px (56 de `.track` + 22 de `gap`) |
| `.funil.compacto` — cada `.fstep` | 59px (46 + 13) |
| `.lista` — cada par de linhas | ~106px (86 + 20 de `gap`) |
| `.nota` | 26px de margem + ~27px por linha |
| `.metod` | 26px de margem + 44 de padding + 34 do `.h` + ~27px por linha |
| `.closing` | 60px de margem + ~45px por linha |

Antes de fechar o slide, **some**. Se passar de 888, tire conteúdo — não encolha fonte fora dos valores da tabela 3.1.

### 4.2 Modo A — grades

| Componente | Grade | Gap |
|---|---|---|
| `.stats` | `repeat(4,1fr)` | `30px` |
| `.stats.tres` | `repeat(3,1fr)` | `30px` |
| `.stats.dois` | `repeat(2,1fr)` | `30px` |
| `.feat` | `repeat(3,1fr)` | `34px` |
| `.funil` | coluna | `22px` (`.compacto`: `13px`) |
| `.fstep` | `300px 1fr 300px` | `28px` |
| `.lista` | `1fr 1fr` | `20px 54px` |
| `.lista.um` | `1fr` | `20px` |
| `.chips` | flex, wrap | `14px` |
| `.mini` | flex | `64px` |

Paddings e raios do modo A:

| Componente | Padding | Raio |
|---|---|---|
| `.stat` | `52px 44px` | `28px` |
| `.card` | `48px 42px` | `30px` |
| `.li` | `20px 26px` | `18px` |
| `.metod` | `22px 28px` | `18px` |
| `.eyebrow` | `9px 19px` | `999px` |
| `.chip` | `6px 14px` | `999px` |
| `.track` / `.fill` | — | `12px` |
| `.li .bar` | largura `5px` | `5px` |

Larguras máximas de leitura: `.nota` e `.closing` `1400px`; `.metod` `1560px`; `.cover .lede` `1180px`. Não estoure — linha de 1660px é ilegível na projeção.

### 4.3 Modo B — grade e ritmo

| Item | Valor |
|---|---|
| `.page` | `min-height: 100dvh`, `scroll-snap-align: start` |
| `html` | `scroll-snap-type: y mandatory` |
| `.page__inner` | `max-width: 1180px`, `margin-inline: auto` |
| padding horizontal da `.page__inner` | `clamp(28px, 6vw, 96px)` |
| padding vertical da `.page__inner` | `clamp(56px, 7vh, 96px)` |
| `.page-head` → conteúdo | `margin-bottom: 48px` |
| `.grid--2` | `repeat(2, 1fr)`, gap `clamp(12px, 1.5vw, 18px)` |
| `.grid--3` | `repeat(3, 1fr)`, gap `clamp(12px, 1.5vw, 18px)` |
| `.sys` | `1.3fr 1fr`, gap `clamp(26px, 3.2vw, 54px)`; `.sys--flip` vira `1fr 1.3fr` e troca a ordem |
| `.agenda-grid` | `repeat(4, 1fr)`, gap `clamp(12px, 1.4vw, 18px)` — 2 colunas até 1080px, 1 até 680px |
| `.stat-row` | grid `auto-fit minmax(118px, 1fr)`, gap `10px` |
| `.spec-list` | coluna, gap `15px` |
| `.ledger` | grid `repeat(2, 1fr)`, gap `9px`; `.ledger__row--wide` ocupa a faixa e centra em 50% |
| `.flow-chain` | flex, gap `7px`, `align-items:center`, `flex-wrap:wrap` |
| HUD | `position: fixed`, `z-index: 60`. Logo `top:26px;left:30px` · contador `bottom:30px;left:30px` · controles `bottom:26px;right:28px` · `.hud-btn` `40×40px` |

Escala de espaçamento do modo B — use **só** estes valores: `4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96`. Raio de cartão: `16px` (`.frame`, `.compare-card`, `.persona-card`, `.callout`); pílula: `999px` (`.badge-soon`, `.hud-btn`, `.shift__tag`).

---

## 5. Regras de composição

### 5.1 O que a barra significa

- **A largura de `.fill` é a proporção real do valor.** Nunca decorativa, nunca "para ficar bonito". A maior linha é `100%`; as outras são o valor dividido pela maior.
- `min-width:5px` é o único ajuste permitido, e só para a barra não sumir. Quando usar `min-width`, aquela linha deixa de ser proporcional — então o número **tem** que estar legível no `.fv`.
- `.fill.sm` põe o rótulo fora da barra. Use sempre que a largura ficar abaixo de ~8%: texto dentro de barra estreita fica cortado.
- A cor da barra é semântica (tabela 1.2), **não** posição no ranking. "Ganhas" é verde mesmo sendo a terceira linha; "Perdidas" é vermelho mesmo sendo a maior.

### 5.2 Limites de densidade

Os limites por componente estão em `componentes.md`, seção **Quantos cabem**. Ela é a única
tabela de limites do sistema — não duplique aqui, porque quantos itens cabem depende do que
mais está no slide (um `.funil` cabe 6 linhas sozinho, 5 com `.nota`, 4 com `.nota` + `.metod`).

Duas regras que valem sempre, independentemente do componente:

| Regra | Motivo |
|---|---|
| 1 `.nota` **e** 1 `.metod` por slide, no máximo | dois de cada significa que o slide tem dois assuntos — quebre em dois |
| Corte texto, nunca reduza a fonte | a escala é a mesma em todos os slides; fonte menor num slide só denuncia que faltou edição |

Se estourou e não dá para cortar, o problema não é densidade: o slide está tentando responder
duas perguntas. Ver `build-e-publicacao.md`, seção **Quando o slide estoura**.

### 5.3 O que não pode

- **Não combine `.closing` com `.feat` ou `.stats`.** `.closing` fecha o deck; só convive com `.lista` e `.metod`.
- **Não use `.chip` solto.** `.chip` fica ao lado de um número que já está na tela, nunca como fato isolado.
- **Não coloque texto abaixo de y=984** no modo A. É onde o `.sfoot` mora e o `overflow:hidden` come.
- **Não pinte com `--cyan` um dado.** Cyan é composição (halo do fundo, degradê da capa).
- **Não crie classe de cor.** A cor entra inline pela variável local: `style="--ac:var(--inbox)"` no `.stat`, `.card` ou `.li`, e `style="background:var(--inbox)"` no `.fill`.
- **Não repita a semântica em dois sentidos no mesmo deck.** Se verde é realizado no slide 02, verde é realizado em todos.
- **Não use `.eyebrow` fora da capa e de abertura de capítulo.**
- **Não use `background-clip:text` sem o override de `@media print`.** No PDF o leitor pinta a caixa inteira e o título vira retângulo colorido. O override obrigatório já está no `assets/deck-relatorio.html`: `.grad` vira cor sólida, `.dim` vira `#dcdaee`.

### 5.4 Regras de conteúdo que o layout precisa respeitar

Estas nasceram de erro publicado. Elas mandam no layout, não o contrário.

| Regra | Consequência no layout |
|---|---|
| Comparativo exige os dois lados na mesma tela | "mais barato que X" pede `.stats.dois` ou duas `.fstep`, nunca um `.stat` sozinho |
| Superlativo exige o histórico | "melhor mês" só sai se os concorrentes aparecem na `.nota` do mesmo slide |
| Número repetido em dois slides vem da mesma apuração | reconfira a capa (`.mini .n`) contra o slide interno a cada edição |
| Contador bruto não é fato | se o número passou por triagem manual, o corte vai no `.metod`, não escondido |
| Receita vem do sistema de receita | `.sfoot .u` sempre nomeia a fonte; CRM e PMS nunca no mesmo `.stat` |
| Rótulo diz o que o número **é** | `.lb` e `.fl` são descritivos, não sugestivos: "Total projetado (82% realizado)", não "ainda não realizado" |
| O slide aponta o problema e o caminho, nunca o culpado | `.title` descreve o fato ("O canal a destravar"), nunca acusa |
| Base imatura não se projeta | se não dá para projetar, o `.metod` explica **por que** não dá — não se omite |
| Referência cruzada por título, não por número | escrever "ver slide 09" só depois de reconferir; ao inserir slide, reconfira todas |
| Recorte declarado é recorte aplicado | deck de uma marca leva o filtro no `.sfoot` de todo slide ("tenant da marca") |

---

## 6. Componentes compartilhados

Três componentes atravessam os dois modos. Eles existem **em ambos** — só mudam de pele.

### 6.1 `.nota` — o rodapé de contexto

O que qualifica o número: base, exceção, ordem de grandeza, ressalva. Vive logo abaixo do bloco central.

| Modo | Cor do texto | Ênfase (`b`) | Fundo |
|---|---|---|---|
| A | `--faint` | `--ink` | nenhum |
| B | `--text-muted` | `--text` | nenhum |

### 6.2 `.metod` — o bloco de honestidade

O que o número **não** é. Método, corte, limitação, o que foi lido à mão. Tem `.h` como cabeçalho em caixa-alta.

| Modo | Fundo | Borda | `.h` |
|---|---|---|---|
| A | `rgba(96,165,250,.07)` | `1px solid rgba(96,165,250,.28)` | `#93c5fd` |
| B | `--accent-dim` | `1px solid var(--border-strong)` | `--accent-soft` |

Um `.metod` por slide. Se você não tem o que escrever nele, ou o slide é trivial ou você não checou o suficiente.

### 6.3 `.frame` — a moldura de navegador

Print de tela com barra falsa: `.frame__bar > .frame__dots + .frame__url + .frame__spacer`, e `.frame__note` embaixo como legenda.

| Modo | Fundo do `.frame` | `.frame__bar` | Borda |
|---|---|---|---|
| A | `--card2` | `rgba(255,255,255,.05)` | `1px solid var(--line)` |
| B | `--surface` | `--surface-2` | `1px solid var(--border)` |

`.frame__url` é sempre a URL real. URL inventada em print é fabricação.

### 6.4 Ícones

Sprite SVG inline com `<symbol id="i-*">`, usado por `<svg><use href="#i-nome"/></svg>`. Sprite único no topo do `<body>`, `display:none`.

Nomes disponíveis — não invente outro, não renomeie:

`i-compass` `i-target` `i-check` `i-chart` `i-repeat` `i-bell` `i-clipboard` `i-bot` `i-zap` `i-kanban` `i-layers` `i-message` `i-broadcast` `i-prism` `i-heart` `i-trophy` `i-star` `i-coin` `i-inbox` `i-search` `i-gauge` `i-user-check` `i-key` `i-users` `i-play` `i-link` `i-grid` `i-code` `i-arrow-right` `i-arrow-down` `i-chev-up` `i-chev-down` `i-sparkle` `i-clock` `i-hand` `i-phone` `i-globe` `i-building`

Traço `1.6px`, `stroke: currentColor`, `fill: none`, `stroke-linecap: round`. O ícone herda a cor do contexto — nunca pinte o `<svg>` direto.

---

## 7. Como trocar a marca

Trocar de empresa mexe em **poucos tokens**. Tudo que não está nesta seção fica como está — mexer no resto quebra a semântica ou o contraste.

### 7.1 Modo A — os 5 pontos

| # | O que trocar | Onde | Restrição |
|---|---|---|---|
| 1 | `--inbox` | `:root` | é a cor primária da marca **e** o verde de "positivo". Escolha um tom que funcione nos dois papéis: claro o bastante para dar ≥7:1 sobre `#050507` e escuro o bastante para o texto `#050507` do `.fill` ficar legível dentro da barra |
| 2 | `.brand i { color }` e `.eyebrow .dot { background / box-shadow }` | CSS | apontam para `var(--inbox)`. Se você trocou o token, já seguem junto |
| 3 | Os 3 `radial-gradient` de `.slide::before` | CSS | o primeiro usa o RGB de `--inbox` a `.16`, o segundo o de `--gestor` a `.17`, o terceiro o de `--cyan` a `.10`. Troque os RGB, mantenha as opacidades e as posições (`8% -6%`, `104% 4%`, `96% 108%`) |
| 4 | `.cover h1 .grad` | CSS + `@media print` | `linear-gradient(100deg, A, B 34%, C 66%, D)`. Use 4 tons da marca. **Atualize também o `color`/`-webkit-text-fill-color` do override de print** — é ele que salva o PDF |
| 5 | Favicon SVG inline no `<head>` | HTML | o `fill` do `<rect>` externo é a cor primária; o das barras é `--bg` |

**Não troque:** `--alerta` (vermelho é perda em qualquer marca), `--pipeline` (âmbar é atenção), `--gestor` (azul é a comparação neutra e é a cor do `.metod`), `--bg`, `--ink`, `--muted`, `--faint`, `--line*`, `--card*`. Se a marca é vermelha, a marca aparece em `--inbox`? Não: nesse caso mantenha `--inbox` verde para a semântica e use a cor da marca só nos itens 3, 4 e 5 (halo, degradê da capa e favicon).

### 7.2 Modo B — os 4 pontos

| # | Token | Como derivar | Restrição |
|---|---|---|---|
| 1 | `--accent` | cor da marca | só **superfície e traço**: ícone, barra, botão, e texto sobre `--ink`. Não precisa passar contraste de texto sobre branco |
| 2 | `--accent-soft` | escureça `--accent` até dar **≥3:1 sobre `#FFFFFF`** | é o único que pode virar texto em fundo claro, e ainda assim só em ≥18.66px semibold ou ≥24px |
| 3 | `--accent-dim` | `--accent` a ~8% sobre branco | fundo de `.callout` e `.badge-soon`. Tem que continuar dando ≥7:1 com `--text` por cima. O `.metod` do modo B **não** usa este token: é magenta, `rgba(159,86,151,.055)` com borda `rgba(159,86,151,.22)` e `.h` em `--eyebrow` |
| 4 | `--eyebrow` | tom análogo ou complementar de `--accent` | precisa de **≥4.5:1 sobre `#FFFFFF`** porque o `.eyebrow` é texto pequeno (`.78rem`) |

**Não troque:** `--ink`, `--text`, `--text-soft`, `--text-muted`, `--text-dim`, `--border`, `--border-strong`, `--bg`, `--bg-subtle`, `--surface`, `--surface-2`, `--ease`. Eles carregam o contraste e o ritmo do sistema.

### 7.3 Trocar de fonte

Troque `--display` e `--sans` no `:root` e o `<link>` do Google Fonts. Exigências:

- A família de `--display` precisa de **peso 800** e de `font-variant-numeric: tabular-nums`. Sem 800, use 700 e reduza os tamanhos da tabela 3.1 em ~6% — senão o número perde peso visual e o slide fica sem hierarquia.
- A família de `--sans` precisa de 400 e 600.
- Depois de trocar, **reconfira a altura de todo slide do modo A** (seção 4.1): métrica diferente muda a altura de `.nota` e `.metod` e o texto some por baixo do `.sfoot`.

### 7.4 Checklist de troca de marca

1. Trocou os tokens das seções 7.1 e 7.2.
2. Rodou o contraste de cada cor nova sobre o fundo do seu modo (mínimo da seção 8).
3. Abriu **todo** slide do modo A e confirmou que nada foi cortado embaixo.
4. Gerou o PDF e conferiu que o `.cover h1` saiu em cor sólida, não em retângulo.
5. Conferiu o favicon.
6. Publicou e comparou o `shasum -a 256` do arquivo local com o do `curl` da URL no ar.

---

## 8. Acessibilidade

### 8.1 Contraste medido — modo A sobre `--bg #050507`

| Cor | Razão | Veredito |
|---|---|---|
| `--ink` `#f5f3ff` | 18,3:1 | livre |
| `--muted` `#a7a7bd` | 8,6:1 | livre |
| `--pipeline` `#fbbf24` | 12,1:1 | livre |
| `--cyan` `#22d3ee` | 11,2:1 | livre |
| `--dados` `#2dd4bf` | 10,9:1 | livre |
| `--inbox` `#34d399` | 10,6:1 | livre |
| `--gestor` `#60a5fa` | 8,0:1 | livre |
| `--dist` `#f472b6` | 7,7:1 | livre |
| `--ia` `#a78bfa` | 7,5:1 | livre |
| `--alerta` `#f87171` | 7,3:1 | livre |
| `--faint` `#71718a` | **4,3:1** | **restrito** |

`--faint` fica logo abaixo dos 4.5:1 de AA para texto normal. Regra: **use `--faint` só em rótulo de apoio cuja informação também aparece em outro lugar do slide** — `.stat .sb`, `.fl small`, `.fv small`, `.li .pct`, `.sfoot`, `.pageno`. Nunca em `.nota` que carrega um fato exclusivo (nesse caso o fato vai em `<b style="color:var(--ink)">`), nunca num número que só existe ali.

Texto dentro de `.fill` é `#050507` sobre a cor da barra: todas as combinações dão ≥7:1. `.chip.up` (`#6ee7b7` sobre verde a 14%) dá 11:1; `.chip.down` (`#fca5a5` sobre vermelho a 14%) dá 9,2:1.

### 8.2 Contraste medido — modo B sobre `#FFFFFF`

| Cor | Razão | Veredito |
|---|---|---|
| `--text` `#201E33` | 16,2:1 | livre |
| `--text-soft` `#4B495E` | 8,7:1 | livre |
| `--eyebrow` `#9F5697` | 4,9:1 | livre (passa AA em `.78rem`) |
| `--text-muted` `#7B7A8C` | **4,2:1** | **restrito**: rótulo de apoio ≥.82rem, nunca fato exclusivo |
| `--accent-soft` `#C96C35` | **3,7:1** | **restrito**: só ≥18.66px em peso 600+ ou ≥24px |
| `--accent` `#DB824E` | **2,9:1** | **nunca como texto sobre branco.** Só superfície, traço e ícone |
| `--text-dim` `#A6A5B4` | **2,4:1** | **decorativo apenas**: `.frame__url`, `.frame__dots`, `.agenda-item__num`. Nunca informação |

Sobre `--ink #17162A`: branco dá 17,7:1 e `--accent` dá 6,2:1 — em `.page--dark`, `--accent` **pode** ser texto.

Consequência prática: `em.acc` dentro de `p` (1.02rem = 16,3px) **não** passa. Dentro de `p`, ênfase é `<b>` com `--text`. `em.acc` só entra em `.lede`, `.capa__sub`, `h2`, `h3` e `.closing em`, sempre com peso 600+.

### 8.3 Cor nunca sozinha

Toda informação codificada por cor tem **um segundo carregador**:

| Informação | Cor | Segundo carregador |
|---|---|---|
| Positivo / negativo | verde / vermelho | seta `↗` `↘` no `.chip` e sinal `+` `−` no número |
| Categoria no funil | cor do `.fill` | o `.fl` escreve o nome da etapa |
| Categoria na lista | `.li .bar` colorida | o `.nome` escreve o rótulo |
| Categoria no card | faixa `::before` do `.stat`/`.card` | `.tag` do `.card` escreve a área |
| Grandeza | largura da barra | `.fv` escreve o valor |
| Antes / agora | `--before` / `--after` | `.shift__tag` escreve "Antes" e "Agora" |

Se você tirar toda a cor do slide e ele deixar de ser compreensível, o slide está errado.

### 8.4 Movimento

- `.reveal[data-delay="1..4"]` anima com `--ease`, `opacity` e `translateY`, com `backface-visibility` para não borrar no Safari. Atrasos: `1`=70ms, `2`=140ms, `3`=210ms, `4`=280ms. Não crie `data-delay="5"`.
- Bloco obrigatório no modo B:

```css
@media (prefers-reduced-motion: reduce){
  *,*::before,*::after{animation-duration:.01ms !important;animation-iteration-count:1 !important;
    transition-duration:.01ms !important;scroll-behavior:auto !important}
  html{scroll-snap-type:none}
  .reveal{opacity:1;transform:none}
}
```

Note que ele desliga o `scroll-snap` também: snap obrigatório é enjoativo para quem tem sensibilidade vestibular.

- O modo A não anima. Slide é imagem estática — qualquer animação some no PNG e no PDF.

### 8.5 Navegação e estrutura

- Modo B navega por teclado: `↑`/`↓`, `←`/`→`, `PageUp`/`PageDown`, espaço, `Home`, `End`. Os `.hud-btn` são `<button>` de verdade, com `aria-label`, e o foco tem contorno visível (`outline: 2px solid var(--accent-soft); outline-offset: 2px`).
- O `.hud-counter` anuncia a posição (`aria-live="polite"`).
- `body.on-dark`, ligado por IntersectionObserver quando uma `.page--dark` entra em cena, inverte a cor do HUD. É cosmético: se o JS falhar, o HUD continua legível.
- Ordem de heading real: uma `h1` por documento (`.capa__title`), `h2` por `.page`, `h3` dentro de `.sys__body`, `h4` em `.spec-row` e `.compare-card`. Não pule nível para conseguir um tamanho — o tamanho vem da classe.
- Todo `<svg>` decorativo leva `aria-hidden="true"`. Ícone que carrega significado sozinho leva `role="img"` e `<title>`.
- `<html lang="pt-BR">` sempre.

---

## 9. Fechamento

Antes de entregar qualquer deck:

1. `grep -c '<section' arquivo.html` bate com o número de slides que você diz ter. Cuidado: `grep 'class="slide"'` exato **não** pega a capa, que é `class="slide cover"`.
2. Nenhum slide passou dos 888px de altura útil (modo A).
3. Todo número que aparece duas vezes veio da mesma apuração.
4. Toda referência cruzada aponta para o título certo.
5. Todo slide de dado tem `.sfoot .u` com a fonte.
6. O PDF saiu com o título em cor sólida.
7. O `shasum -a 256` do local bate com o do publicado.
