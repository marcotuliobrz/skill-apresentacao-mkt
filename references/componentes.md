# Catálogo de componentes

Um sistema visual, dois modos de página.

- **Modo A — `relatorio`**: tema escuro, slide fixo de 1920x1080, um `<section class="slide">` por slide. Para dados, números e board reporting. Sai em PNG por slide e PDF 16:9. Referência viva: `assets/deck-relatorio.html`.
- **Modo B — `narrativa`**: tema claro, página rolável com scroll-snap, um `<section class="page">` por tela. Para contar história, mostrar produto, fazer tour de telas.

Não invente classes fora deste catálogo. Não renomeie nada. Se um layout não existe aqui, componha com o que existe ou quebre em dois slides.

**Componentes que atravessam os dois modos:** `.nota` e `.metod` (honestidade) e `.frame` (prova de tela). Relatório também mostra print; narrativa também precisa dizer de onde veio o número.

**Regra que vale para todo componente que carrega número:** o mesmo número, repetido em mais de uma tela, tem que vir da mesma apuração. Numa edição já publicada, ROAS saiu 5,9x na capa e 5,7x no slide interno porque a capa ficou velha. Ao editar qualquer valor, procure o valor antigo no arquivo inteiro antes de salvar.

---

## Estrutura de página

### .slide

Modo A. A unidade do relatório: 1920x1080, `overflow:hidden`, padding `96px 130px`, `display:flex; flex-direction:column`.

Use para todo slide de dado. Não use para conteúdo que role — não existe rolagem no modo A; o que passa da altura é cortado sem aviso.

```html
<section class="slide">
  <div class="shead"><div class="brand"><b>GR</b>·<i>GROWTH</i></div><div class="pageno">02</div></div>
  <div class="title">As vendas de julho</div>
  <div class="subtitle">Reservas criadas de 1º a 31 de julho, direto do PMS — <b>excluídas canceladas, no-show e pré-reservas</b>.</div>

  <!-- bloco central: leva margin-top:auto e margin-bottom:auto (já embutidos em .stats, .feat, .funil, .lista) -->

  <div class="nota">…</div>
  <div class="sfoot"><span class="u">Fonte: PMS · reservas</span><span>Mês/Ano · mês fechado</span></div>
</section>
```

Armadilhas:
- O bloco central precisa de `margin-top:auto; margin-bottom:auto` para centralizar entre cabeçalho e rodapé. `.stats`, `.feat`, `.funil` e `.lista` já trazem isso no CSS. Se criar um agrupamento com `div` cru, ele encosta no cabeçalho.
- `overflow:hidden` + `.sfoot` absoluto = conteúdo que estoura **desaparece em silêncio**. Não confie no navegador para avisar. Confira cada slide no PNG exportado, não no scroll do navegador.
- Não reduza fonte para caber. Se não coube, quebre em dois slides.
- Contagem de slides: `grep -c '<section' arquivo.html`. Um `grep` por `class="slide"` exato **não pega a capa**, que usa `class="slide cover"`.

### .slide.cover

Modo A. Capa do relatório. `justify-content:center`, sem `.title`/`.subtitle`.

Use uma vez por deck, sempre como primeiro `<section>`. Não use como divisória de capítulo — no modo A a divisória é um slide comum com `.title` grande e `.nota` curta.

```html
<section class="slide cover">
  <div class="shead"><div class="brand"><b>GR</b>·<i>GROWTH</i></div><div class="pageno">RELATÓRIO MENSAL</div></div>
  <span class="eyebrow"><span class="dot"></span>Marca Exemplo · Mês/Ano · mês fechado</span>
  <h1>O mês de <span class="grad">julho</span><br><span class="dim">em números</span></h1>
  <p class="lede">O maior mês de vendas desde março — <b>+60% de receita sobre junho</b> —
    sustentado por mídia paga.</p>
  <div class="mini">
    <div><div class="n" style="color:var(--inbox)">934</div><div class="l">reservas no mês</div></div>
    <div><div class="n" style="color:#fff">R$ 1,40 mi</div><div class="l">em vendas · +60,0%</div></div>
  </div>
  <div class="sfoot"><span class="u">Time de Growth Marketing</span><span>Marco Túlio</span></div>
</section>
```

Armadilhas:
- `.grad` e `.dim` usam `background-clip:text`. **Isso não sobrevive ao PDF**: o leitor pinta a caixa inteira e o título vira um retângulo colorido. O bloco `@media print` do modo A já força cor sólida nesses dois — não apague esse bloco e não crie novas classes com `background-clip:text` sem o par no `@media print`.
- Título de capa é o lugar onde superlativo escapa. "Melhor mês do ano" já foi publicado sendo falso (março e janeiro tinham sido maiores). Superlativo na capa exige consulta ao histórico completo, não à comparação com o mês anterior.
- Os números do `.mini` são os mesmos que aparecem nos slides internos. Reconfira os quatro a cada edição.

### .page e modificadores

Modo B. A unidade da narrativa: `min-height:100dvh`, `scroll-snap-align:start`.

```html
<section class="page">          <!-- fundo branco, padrão -->
<section class="page page--alt"> <!-- fundo --bg-subtle, para alternar ritmo -->
<section class="page page--dark"><!-- fundo --ink, inverte o HUD via body.on-dark -->
<section class="page page--capa"><!-- abertura -->
<section class="page page--fim"> <!-- fechamento -->
```

Use `--alt` para separar capítulos sem trocar de tema. Use `--dark` para o momento de virada da história (o "antes/agora", o número que dói). Não use `--dark` em duas páginas seguidas: o HUD pisca na transição e a leitura perde o contraste do gesto.

```html
<section class="page page--alt" id="cap-02">
  <div class="page__inner">
    <div class="page-head">
      <span class="eyebrow">Capítulo 02</span>
      <h2>O atendimento deixou de depender de um número de celular</h2>
      <p class="lede">Uma caixa só, com histórico, dono e prazo.</p>
    </div>
    <!-- conteúdo -->
  </div>
</section>
```

Armadilhas:
- `min-height:100dvh` com `scroll-snap-type: y mandatory` significa: **o que passa de 100dvh só é alcançável se a página inteira crescer**, e aí o snap encaixa no topo e o rodapé nunca é lido. Conteúdo que não cabe em uma tela vira duas páginas.
- Teste em 1366x768, não só no monitor grande. É a altura onde o `.sys` estoura primeiro.
- `.page--dark` só inverte o HUD se estiver na lista observada pelo IntersectionObserver. Se você adicionar uma página escura depois, confira o HUD rolando até ela — o sintoma é botão preto sobre fundo preto.

### .page__inner

Modo B. Caixa de largura máxima e respiro interno de cada `.page`. Um por página, envolvendo todo o conteúdo.

```html
<div class="page__inner">…</div>
```

Não empilhe dois `.page__inner` na mesma página nem coloque conteúdo direto no `.page` — sem ele, o texto vai de borda a borda no monitor largo.

### .grid, .grid--2, .grid--3

Modo B. Grade genérica para cartões de mesma altura. Hospeda `.persona-card` e blocos curtos.

```html
<div class="grid grid--3">
  <div class="persona-card">…</div>
  <div class="persona-card">…</div>
  <div class="persona-card">…</div>
</div>
```

Sem modificador é coluna única. Não use `.grid` para dado comparado — para isso existem `.lista`, `.funil` e `.compare-grid`, que carregam proporção.

---

## Cabeçalho e rodapé

### .shead, .brand, .pageno

Modo A. Faixa superior de todo slide: marca à esquerda, número à direita.

```html
<div class="shead">
  <div class="brand"><b>GR</b>·<i>GROWTH</i></div>
  <div class="pageno">02</div>
</div>
```

`.brand b` fica branco, `.brand i` fica na cor `--inbox`. Na capa, `.pageno` recebe o tipo do documento ("RELATÓRIO MENSAL") em vez do número.

Armadilhas:
- `.pageno` é preenchido à mão. Ao inserir um slide no meio, **todos os seguintes ficam errados**. Renumere de ponta a ponta depois de qualquer inserção.
- Nunca escreva "ver slide 09" no corpo do texto. Referência cruzada é por título ("ver *A safra do lead paga depois*"). Isso já quebrou um deck: slides entraram no meio e todas as remissões passaram a apontar para o slide errado.

### .eyebrow e .dot

Modo A e modo B, com desenhos diferentes.

Modo A: pílula com contorno e um ponto luminoso. Carrega o **recorte** — marca, período e regime de apuração.

```html
<span class="eyebrow"><span class="dot"></span>Marca Exemplo · Mês/Ano · mês fechado</span>
```

Modo B: mesma classe, sem `.dot`; a régua vem do `::before`. Carrega o capítulo.

```html
<span class="eyebrow">Capítulo 02 · Atendimento</span>
```

Armadilhas:
- No modo A, `.eyebrow` é filho direto de um flex-column e **estica na largura inteira** se perder o `align-self:flex-start`. Não sobrescreva.
- É aqui que se declara "mês fechado" ou "janela móvel de 30 dias". Escolha a unidade que a diretoria usa para decidir: mês fechado é auditável, janela móvel não. Já foi publicada janela de 30/60 dias respondendo a uma pergunta que era "por mês".
- Deck multi-tenant: se o recorte é de uma marca só, o `.eyebrow` diz o nome da marca — e a consulta que gerou o número tem que ter filtro de tenant. Quatro marcas já se misturaram num deck declarado de uma.

### .title e .subtitle

Modo A. Título do slide e a linha que define o recorte do dado.

```html
<div class="title">De onde vêm as vendas</div>
<div class="subtitle">Receita por canal de reserva no PMS. <b>Barra proporcional ao valor.</b></div>
```

O `.subtitle` é obrigatório em slide de dado: ele diz qual sistema, qual período e o que foi excluído. `<b>` dentro dele destaca a exclusão ("excluídas canceladas, no-show e pré-reservas").

Armadilhas:
- `.title` cabe em uma linha. Duas linhas empurram o bloco central para baixo do `.sfoot`.
- Título não acusa. Já foi para diretoria um título chamando um canal de "buraco de rastreio". O slide aponta o problema e o caminho, não o culpado: "Google Ads: o canal a destravar" diz a mesma coisa e sobrevive à reunião.
- Rótulo ambíguo vira cobrança em ata. "R$ 319 mil ainda não realizado" era o total projetado, com 82% já realizado. Escreva o que o número **é**.

### .sfoot e .u

Modo A. Rodapé: fonte à esquerda, período à direita.

```html
<div class="sfoot">
  <span class="u">Fonte: GR Station · pipeline Hospedagem · apurado em 04/08/2026</span>
  <span>Mês/Ano</span>
</div>
```

Obrigatório em todo slide de dado. A fonte nomeia tabela ou sistema, não "nosso banco". A data de apuração entra sempre que o número ainda se mexe (conversa de julho recebe resposta em agosto).

Armadilhas:
- **`.sfoot` é `position:absolute; bottom:56px`.** Ele não empurra nada e não é empurrado. Conteúdo que cresce passa por baixo dele e some no `overflow:hidden`. Esta é a causa número um de slide quebrado no modo A.
- Como diagnosticar: abra o PNG exportado. Se a última linha da `.nota` ou do `.metod` está cortada ou colada no rodapé, tire conteúdo — não diminua a fonte.

### .page-head

Modo B. Cabeçalho de página: `.eyebrow` + título + `.lede`.

```html
<div class="page-head">
  <span class="eyebrow">Entrega · Ciclo 2</span>
  <h2>O que passou a existir</h2>
  <p class="lede">Quatro sistemas que antes eram planilha, grupo de WhatsApp e memória.</p>
</div>
```

Uma por página. Não repita `.eyebrow` no corpo.

### Tipografia do modo B: h1 h2 h3 h4, p, .lede, em.acc

- `h1` só na capa (`.capa__title`).
- `h2` é o título da página.
- `h3` é título de bloco dentro da página.
- `h4` é título de item dentro de `.spec-row`, `.compare-card`, `.persona-card`, `.ledger`.
- `.lede` é o parágrafo grande logo abaixo do título; um por página.
- `em.acc` marca a palavra que carrega a frase, na cor `--accent`.

```html
<p class="lede">O time deixou de perguntar <em class="acc">quem está falando com esse cliente</em>.</p>
```

Não use `em.acc` mais de duas vezes por página: ele deixa de acentuar e vira ruído.

---

## Números

### .mini, .n, .l

Modo A, capa. Quatro números de abertura, em linha.

```html
<div class="mini">
  <div><div class="n" style="color:var(--inbox)">934</div><div class="l">reservas no mês</div></div>
  <div><div class="n" style="color:#fff">R$ 1,40 mi</div><div class="l">em vendas · +60,0%</div></div>
  <div><div class="n" style="color:var(--pipeline)">10.386</div><div class="l">leads de mídia paga</div></div>
  <div><div class="n" style="color:var(--ia)">5,4×</div><div class="l">retorno sobre mídia paga</div></div>
</div>
```

Só na capa. Para número dentro do deck, use `.stats`.

Armadilhas:
- A cor vai inline no `.n`. Use os tokens semânticos, não hex avulso — exceto branco puro (`#fff`) para o número neutro principal.
- Todo `.n` da capa se repete lá dentro. Reconfira os quatro a cada edição: é exatamente aqui que a capa envelhece.

### .stats, .stats.dois, .stats.tres, .stat, .big, .lb, .sb

Modo A. Cartões de indicador. Padrão é 4 colunas; `.tres` e `.dois` reduzem.

```html
<div class="stats">
  <div class="stat" style="--ac:var(--inbox)">
    <div class="big" style="color:var(--inbox)">934</div>
    <div class="lb">Reservas</div>
    <div class="sb">junho: 618 · <b style="color:#6ee7b7">+51,1%</b></div>
  </div>
  <div class="stat" style="--ac:#fff">
    <div class="big" style="color:#fff">R$ 1,40 mi</div>
    <div class="lb">Valor total</div>
    <div class="sb">R$ 2.583.242 · <b style="color:#6ee7b7">+60,0%</b> vs. junho</div>
  </div>
  <div class="stat" style="--ac:var(--gestor)">
    <div class="big" style="color:var(--gestor)">R$ 2.766</div>
    <div class="lb">Ticket médio</div>
    <div class="sb">junho: R$ 2.613</div>
  </div>
  <div class="stat" style="--ac:var(--pipeline)">
    <div class="big" style="color:var(--pipeline)">R$ 372 mil</div>
    <div class="lb">Veio de mídia paga</div>
    <div class="sb">117 clientes · R$ 68,6 mil investidos</div>
  </div>
</div>
```

`--ac` pinta a régua de 4px no topo do cartão. `.big` é o número, `.lb` o rótulo, `.sb` a linha de contexto — que deve trazer o valor de comparação, não um adjetivo.

Armadilhas:
- **`--ac` não colore o número.** A régua e o `.big` são pintados separadamente: se você trocar só o `--ac`, o número fica na cor antiga. Troque os dois.
- `.sb` sem base de comparação é indicador solto. "+329%" precisa de "junho: R$ 1.113" ao lado. Comparativo exige os dois lados na mesma tela: já foi publicado "o clique mais barato do mês" sobre um canal cujo CPC era maior que o do outro — os dois CPCs não estavam no mesmo slide.
- Verde (`#6ee7b7`) e vermelho (`#fca5a5`) dentro do `.sb` significam bom e ruim para o negócio, não subida e descida. Queda de custo por lead é verde.
- Nunca some CRM com PMS num mesmo `.stats`. Receita vem do sistema de receita; o CRM mede esforço comercial. Numa apuração real o CRM registrou 31% a mais que o PMS e tinha 20 pares duplicados (mesmo contato, mesmo valor, dois lançamentos).

### .chip, .chip.up, .chip.down, .chips

Modo A. Pílula de variação, colada ao lado de um número no `.subtitle` ou solta em `.chips`.

```html
<div class="subtitle"><b>30.102 sessões humanas</b> em julho — contra 9.662 em junho.
  <span class="chip up">↗ +211,6%</span></div>

<div class="chips">
  <span class="chip up">↗ leads +153,7%</span>
  <span class="chip down">↘ disparos −7,3%</span>
</div>
```

`.chip` sozinho não tem fundo nem borda — use sempre com `.up` ou `.down`. `.up` é o que é bom para o negócio, `.down` o que é ruim.

Não use chip sem o valor de origem visível na mesma tela: "+211,6%" só significa alguma coisa ao lado de "9.662 em junho".

### .stat-row, .stat-box, .stat-box__value, .stat-box__label

Modo B. Faixa de números dentro de uma página de narrativa. Equivalente claro do `.stats`, mas sem cartão e sem régua colorida.

```html
<div class="stat-row">
  <div class="stat-box">
    <span class="stat-box__value">6</span>
    <span class="stat-box__label">atendentes na mesma caixa</span>
  </div>
  <div class="stat-box">
    <span class="stat-box__value">38 min</span>
    <span class="stat-box__label">mediana de primeira resposta, horário comercial</span>
  </div>
  <div class="stat-box">
    <span class="stat-box__value">100%</span>
    <span class="stat-box__label">das conversas com origem classificada</span>
  </div>
</div>
```

Use para sustentar a afirmação da página. Não use como painel — se são mais de quatro indicadores, o assunto é relatório, não narrativa: mude para o modo A.

`.stat-box__label` é frase, não sigla. É o lugar de dizer "mediana em horário comercial" em vez de "TMR".

### .ledger, .ledger__row, .ledger__row--wide, .ledger__ico, .ledger__body, .ledger__name, .ledger__sub, .ledger__price

Modo B. Lista de itens com preço à direita — escopo, plano, entregáveis.

```html
<div class="ledger">
  <div class="ledger__row">
    <span class="ledger__ico"><svg><use href="#i-inbox"/></svg></span>
    <div class="ledger__body">
      <span class="ledger__name">Caixa única de atendimento</span>
      <span class="ledger__sub">WhatsApp, Instagram e chat do site no mesmo lugar</span>
    </div>
    <div class="ledger__price"><b>R$ 1.480</b><span>/mês</span></div>
  </div>
  <div class="ledger__row ledger__row--wide">
    <span class="ledger__ico"><svg><use href="#i-bot"/></svg></span>
    <div class="ledger__body">
      <span class="ledger__name">Automação de régua</span>
      <span class="ledger__sub">10 réguas ativas, e-mail, SMS e WhatsApp</span>
    </div>
    <div class="ledger__price"><b>incluso</b><span>no plano</span></div>
  </div>
</div>
```

`--wide` alarga a linha para itens que precisam de mais texto no `.ledger__sub`.

Armadilhas:
- `.ledger__price b` é o valor, `span` é a unidade. Nunca escreva "R$ 1.480/mês" tudo dentro do `<b>`: a unidade fica do tamanho do preço e a coluna desalinha.
- Se um item ainda não existe, marque com `.badge-soon` no `.ledger__name`. Escopo futuro apresentado como entregue vira cobrança.

### .total, .total__block, .total__num, .total__num--sm, .total__unit, .total__sep, .total__text

Modo B. O fechamento numérico embaixo do `.ledger`.

```html
<div class="total">
  <div class="total__block">
    <span class="total__num">R$ 4.900</span><span class="total__unit">/mês</span>
  </div>
  <span class="total__sep"></span>
  <div class="total__block">
    <span class="total__num total__num--sm">12 meses</span><span class="total__unit">de contrato</span>
  </div>
  <p class="total__text">Sem taxa de implantação. Os quatro sistemas entram juntos.</p>
</div>
```

`--sm` reduz o segundo número para ele não competir com o principal. `.total__sep` é o traço vertical entre blocos — elemento vazio, sem texto dentro.

Armadilhas:
- Um `.total` por página. Dois totais na mesma tela é a forma mais rápida de alguém somar errado.
- `.total__text` diz o que **não** está incluso. Omissão aqui é o que gera discussão depois.

---

## Dados comparados

### .funil, .funil.compacto, .fstep, .fl, .track, .fill, .fill.sm, .fv

Modo A. Barras horizontais com rótulo à esquerda e valor à direita. É o componente mais usado do relatório: funil comercial, receita por canal, origem de atendimento, tráfego.

```html
<div class="funil">
  <div class="fstep">
    <div class="fl">Central de Reservas<small>time comercial próprio</small></div>
    <div class="track"><div class="fill" style="width:100%;background:var(--inbox)">520 reservas</div></div>
    <div class="fv">R$ 1,61 mi<small>62,4% da receita</small></div>
  </div>
  <div class="fstep">
    <div class="fl">Operadora<small>parceiros de turismo</small></div>
    <div class="track"><div class="fill" style="width:24.2%;background:var(--gestor)">131</div></div>
    <div class="fv">R$ 389 mil<small>15,1%</small></div>
  </div>
  <div class="fstep">
    <div class="fl">Site + demais OTAs<small>site resort, Expedia, Omnibees</small></div>
    <div class="track"><div class="fill sm" style="width:5.6%;background:var(--dist)"><span>26</span></div></div>
    <div class="fv">R$ 90 mil<small>3,5%</small></div>
  </div>
  <div class="fstep">
    <div class="fl">Outros<small>pós-venda, clube de férias, balcão</small></div>
    <div class="track"><div class="fill sm" style="width:1.2%;min-width:5px;background:var(--ia)"><span>121</span></div></div>
    <div class="fv">R$ 19 mil<small>0,7%</small></div>
  </div>
</div>
```

Versão compacta, para 6 ou 7 linhas:

```html
<div class="funil compacto">
  <div class="fstep">
    <div class="fl">Meta Ads<small>mídia paga</small></div>
    <div class="track"><div class="fill" style="width:100%;background:var(--gestor)">16.064 contatos</div></div>
    <div class="fv">R$ 335 mil<small>105 vendas · converte 0,65%</small></div>
  </div>
  <!-- … até 7 .fstep -->
</div>
```

Armadilhas:
- **A largura de `.fill` é a proporção real do valor.** Nunca decorativa, nunca arredondada para ficar bonita. A maior linha é `width:100%` e todas as outras se calculam sobre ela — e sobre a **mesma grandeza**: se a barra é volume, o `.fv` pode ser dinheiro, mas as barras entre si comparam volume.
- Diga no `.subtitle` qual é a grandeza da barra: "Barra proporcional ao valor" ou "proporcional ao número de leads". Sem isso o leitor assume que a barra é o número da direita.
- **`.fill.sm` existe porque barra estreita não comporta rótulo dentro.** Abaixo de ~8% de largura o texto vaza ou some. Com `.sm`, o rótulo vai num `<span>` posicionado à direita da barra. Regra prática: até 8%, use `.sm`; acima, texto dentro.
- Barra abaixo de ~1,5% desaparece. Acrescente `min-width:5px` inline junto do `width`.
- **`.funil.compacto` existe porque 7 linhas não cabem na altura padrão.** Ele reduz `gap` de 22 para 13, `track` de 56 para 46 e as fontes. Não crie uma terceira variação: se nem o compacto cabe, o slide tem assunto demais.
- `.fl small` e `.fv small` são a segunda linha em cinza. Use `.fl small` para explicar o rótulo em português de gente ("cotação enviada ou negociando") e `.fv small` para a base do percentual ("de 12.815 entrantes").
- Percentual sem base declarada é o erro clássico. Escreva "15,8% de 12.815 entrantes", não "15,8%".
- Antes de montar funil de tráfego, filtre robô: user_agent de crawler e referrer de rede interna. Já foram publicados "111,8 mil visitantes" quando 74% eram bingbot, inflados porque o rastreador escreve um parâmetro na URL e o crawler trata cada URL como página nova.
- Contador bruto não é fato. "30.565 conversas sem resposta" virou 1.578 pessoas reais depois de abrir a amostra: 850 sem mensagem nenhuma, 293 autoresponders de outras empresas, 152 menções de story, 146 ruído. Abra a amostra antes de transformar um `COUNT(*)` em `.fill`.

### .lista, .lista.um, .li, .bar, .nome, .val, .pct

Modo A. Ranking em duas colunas com valor à direita. Para motivos de perda, drivers de ganho, origem de sessão, resumo do mês.

```html
<div class="lista">
  <div class="li" style="--ac:var(--alerta)">
    <div class="bar"></div>
    <div class="nome">Parou de responder depois de receber o preço<small>1.569 oportunidades</small></div>
    <div class="val">R$ 3,80 mi<span class="pct">58,1%</span></div>
  </div>
  <div class="li" style="--ac:var(--pipeline)">
    <div class="bar"></div>
    <div class="nome">Preço — achou caro<small>336 oportunidades</small></div>
    <div class="val">R$ 835 mil<span class="pct">12,8%</span></div>
  </div>
</div>
```

Uma coluna, quando o rótulo é longo:

```html
<div class="lista um">
  <div class="li" style="--ac:var(--inbox)">
    <div class="bar"></div>
    <div class="nome">Retorno sobre mídia paga<small>R$ 372,0 mil sobre R$ 68,6 mil</small></div>
    <div class="val" style="color:var(--inbox)">5,4×</div>
  </div>
</div>
```

Armadilhas:
- Ordene sempre pelo valor de `.val`, decrescente. Lista fora de ordem faz o leitor procurar o critério e desconfiar do resto.
- `--ac` pinta a barrinha lateral. Para colorir o `.val` (no slide de resumo, verde para ganho e vermelho para perda), ponha `style="color:…"` no `.val` — o `--ac` não chega nele.
- `.pct` é o share, e o `.subtitle` tem que dizer share de quê ("o % é share do dinheiro perdido"). Sem isso, alguém lê como taxa de conversão.
- `.nome small` carrega o volume quando o `.val` carrega o dinheiro. Os dois juntos evitam a leitura de que o motivo mais frequente é o mais caro.
- Percentuais que somam mais de 100% são legítimos quando cada item pode aparecer junto com outro — mas **diga isso no `.metod`**, com o número: "cada conversa pode ter mais de um motivo, e 77% têm".

### .feat, .card, .ic, .tag, .sw

Modo A. Três cartões de destaque, para o slide de "o que precisa de atenção" ou de recomendações.

```html
<div class="feat">
  <div class="card" style="--ac:var(--alerta)">
    <div class="ic"><svg><use href="#i-coin"/></svg></div>
    <h3>R$ 4,64 milhões param depois da proposta</h3>
    <p>71% de tudo que se perdeu é preço ou silêncio após o orçamento — e <b>99,8% desse valor
      estava em negócio que a gente atendeu</b>.</p>
    <span class="tag"><span class="sw"></span>Comercial</span>
  </div>
  <div class="card" style="--ac:var(--alerta)">
    <div class="ic"><svg><use href="#i-hand"/></svg></div>
    <h3>1.037 pedidos ficaram sem resposta</h3>
    <p>O CRM marcou 3.122 conversas como "sem resposta". Tirando autoresposta, menção de story e
      contador vazio, sobram <b>1.578 pessoas que escreveram de verdade</b>.</p>
    <span class="tag"><span class="sw"></span>Atendimento</span>
  </div>
  <div class="card" style="--ac:var(--pipeline)">
    <div class="ic"><svg><use href="#i-phone"/></svg></div>
    <h3>19 disseram que não conseguem falar com a gente</h3>
    <p>Dezenove escreveram que tentaram e não foram atendidos. Poucos em volume, mas são os que
      já viraram reclamação.</p>
    <span class="tag"><span class="sw"></span>Demanda entrante</span>
  </div>
</div>
```

Armadilhas:
- **A grade é de 3 colunas fixas.** Um quarto cartão cai numa segunda linha e some sob o `.sfoot`. Três, sempre.
- `.tag` tem `margin-top:auto`: ele cola no rodapé do cartão e alinha as três tags entre si mesmo com textos de tamanhos diferentes. Não tire.
- `.tag` nomeia o **time dono da ação**, não o culpado. "Comercial", "Atendimento", "Ingestão de dados".
- `.ic` aceita emoji (é o que o deck de referência usa), mas prefira o sprite: emoji muda de desenho entre máquinas e não obedece à cor do token no PDF.
- Ordene os cartões por dinheiro envolvido e diga isso no `.subtitle`.

### .shift, .shift__side, --before, --after, .shift__tag, .shift__arrow

Modo B. O "Antes / Agora" — dois lados e uma seta no meio.

```html
<div class="shift">
  <div class="shift__side shift__side--before">
    <span class="shift__tag">Antes</span>
    <p>Três celulares, um grupo de WhatsApp e a memória de quem atendeu. Ninguém sabia
      quantos pedidos ficaram sem resposta.</p>
  </div>
  <div class="shift__arrow"><svg><use href="#i-arrow-right"/></svg></div>
  <div class="shift__side shift__side--after">
    <span class="shift__tag">Agora</span>
    <p>Uma caixa, com dono, histórico e prazo. O que fica sem resposta aparece numa lista.</p>
  </div>
</div>
```

Use uma vez por capítulo, no máximo. Não use para comparar números — para isso existe `.compare-grid` ou `.stat-row`. O `.shift` compara **situações**.

Armadilhas:
- O lado `--before` descreve a rotina antiga sem ironia e sem nomear pessoa. Vai para diretoria.
- Em telas estreitas a seta gira para baixo. Se você trocar o ícone, use `#i-arrow-right`; a rotação é do CSS.

### .compare-grid, .compare-card, --a, --b, .compare-card__ico, --coin, .compare-card__tag

Modo B. Duas opções lado a lado — cenário A contra cenário B, custo de fazer contra custo de não fazer.

```html
<div class="compare-grid">
  <div class="compare-card compare-card--a">
    <span class="compare-card__ico"><svg><use href="#i-clock"/></svg></span>
    <span class="compare-card__tag">Sem o sistema</span>
    <h4>Cada pedido depende de alguém lembrar</h4>
    <p>O tempo de resposta varia com quem está de plantão, e não existe registro de quem
      não foi atendido.</p>
  </div>
  <div class="compare-card compare-card--b">
    <span class="compare-card__ico compare-card__ico--coin"><svg><use href="#i-coin"/></svg></span>
    <span class="compare-card__tag">Com o sistema</span>
    <h4>O que fica sem resposta vira fila</h4>
    <p>Mediana de 38 minutos em horário comercial, e a fila do que não foi atendido é visível
      para o gestor.</p>
  </div>
</div>
```

`--a` e `--b` dão os dois tratamentos visuais; `--coin` marca o cartão que fala de dinheiro. Sempre dois cartões — comparativo exige os dois lados na mesma tela.

---

## Narrativa

### Capa do modo B: .capa-grid, .capa__title, .capa__sub, .capa__cta, .capa-stats, .capa-stat, .capa__meta

Abertura da narrativa, dentro de `.page--capa`.

```html
<section class="page page--capa">
  <div class="page__inner">
    <div class="capa-grid">
      <div>
        <span class="eyebrow">GR Group · Entrega</span>
        <h1 class="capa__title">O que a gente construiu para o seu atendimento</h1>
        <p class="capa__sub">Quatro sistemas que substituíram planilha, grupo de WhatsApp
          e memória — todos no ar, todos em uso.</p>
        <div class="capa__cta"><svg><use href="#i-arrow-down"/></svg> Role para começar</div>
        <div class="capa-stats">
          <div class="capa-stat"><b>4</b><span>sistemas no ar</span></div>
          <div class="capa-stat"><b>6</b><span>atendentes na mesma caixa</span></div>
          <div class="capa-stat"><b>10</b><span>réguas ativas</span></div>
        </div>
        <p class="capa__meta">Marco Túlio · Growth Marketing · agosto de 2026</p>
      </div>
      <div class="hero-stack">…</div>
    </div>
  </div>
</section>
```

`.capa-grid` é o par texto + `.hero-stack`. `.capa-stat` leva `<b>` para o número e `<span>` para o rótulo. `.capa__meta` é a assinatura: autor, time e data.

Armadilhas:
- `.capa__cta` é indicação de rolagem, não botão de ação. Não coloque link externo aí — o leitor sai do deck.
- Três `.capa-stat`. Quatro comprime o número e apaga a hierarquia com o `.capa__title`.

### .agenda-grid, .agenda-item, .agenda-item__top, .agenda-item__ico, --brand, .agenda-item__num, .agenda-item__label

Modo B. O sumário navegável, logo depois da capa.

```html
<nav class="agenda-grid">
  <a class="agenda-item" href="#cap-01">
    <div class="agenda-item__top">
      <span class="agenda-item__ico agenda-item__ico--brand"><svg><use href="#i-compass"/></svg></span>
      <span class="agenda-item__num">01</span>
    </div>
    <div class="agenda-item__label">Onde estávamos<span>diagnóstico e baseline</span></div>
  </a>
  <a class="agenda-item" href="#cap-02">
    <div class="agenda-item__top">
      <span class="agenda-item__ico"><svg><use href="#i-inbox"/></svg></span>
      <span class="agenda-item__num">02</span>
    </div>
    <div class="agenda-item__label">O atendimento<span>caixa única e fila do que não respondeu</span></div>
  </a>
</nav>
```

`--brand` marca o item de destaque (o capítulo principal). Um só por agenda.

Armadilhas:
- O `href` aponta para o `id` da `.page` correspondente. Numeração e ordem das páginas têm que bater — confira depois de inserir capítulo.
- `.agenda-item__label span` é a segunda linha, em cinza. Sem ela, a agenda vira lista de substantivos sem informação.

### .sys, .sys--flip, .sys__media, .sys__body

Modo B. O layout de duas colunas que carrega cada capítulo: mídia de um lado, texto do outro.

```html
<div class="sys">
  <div class="sys__media">
    <figure class="shot">
      <div class="frame">
        <div class="frame__bar">
          <span class="frame__dots"><i></i><i></i><i></i></span>
          <span class="frame__url">crm.grgroup.app/atendimento</span>
          <span class="frame__spacer"></span>
        </div>
        <img src="assets/atendimento.png" alt="Caixa de atendimento com as conversas do dia">
      </div>
    </figure>
  </div>
  <div class="sys__body">
    <span class="eyebrow">Sistema 01</span>
    <h3>Caixa única de atendimento</h3>
    <p>WhatsApp, Instagram e chat do site chegam na mesma fila, com dono e histórico.</p>
    <div class="spec-list">…</div>
  </div>
</div>
```

`--flip` inverte os lados. Alterne de capítulo em capítulo — dois `.sys` seguidos com a mídia do mesmo lado fazem a página parecer repetida.

Armadilhas:
- É o componente que mais estoura os 100dvh, porque o `.sys__body` costuma receber `.spec-list` inteira. Em 1366x768, `.sys` + 5 `.spec-row` já não cabe. Ou corta uma linha, ou vira duas páginas.
- `.sys__media` recebe um `.shot` ou uma imagem, nunca texto.

### .spec-list, .spec-row, .spec-row__icon, --glyph, .spec-row__body, .spec-row__role

Modo B. Lista de capacidades dentro do `.sys__body`.

```html
<div class="spec-list">
  <div class="spec-row">
    <span class="spec-row__icon"><svg><use href="#i-inbox"/></svg></span>
    <div class="spec-row__body">
      <span class="spec-row__role">Atendente</span>
      <h4>Responde sem trocar de aplicativo</h4>
      <p>Todos os canais na mesma tela, com o histórico do contato ao lado.</p>
    </div>
  </div>
  <div class="spec-row">
    <span class="spec-row__icon spec-row__icon--glyph">SLA</span>
    <div class="spec-row__body">
      <span class="spec-row__role">Gestor</span>
      <h4>Vê a fila do que não foi respondido</h4>
      <p>Mediana de primeira resposta por atendente e por canal, em horário comercial.</p>
    </div>
  </div>
</div>
```

`--glyph` troca o ícone por uma sigla ou número curto — use quando não existe ícone que diga a coisa. `.spec-row__role` diz **para quem** aquilo serve; sem isso a lista vira catálogo de funcionalidade.

### .flow-chain, .flow-step, --last, .flow-arrow

Modo B. Cadeia horizontal de etapas — o caminho que o lead percorre, o fluxo do dado.

```html
<div class="flow-chain">
  <div class="flow-step">Anúncio no Meta</div>
  <span class="flow-arrow"><svg><use href="#i-arrow-right"/></svg></span>
  <div class="flow-step">Conversa no WhatsApp</div>
  <span class="flow-arrow"><svg><use href="#i-arrow-right"/></svg></span>
  <div class="flow-step">Oportunidade no CRM</div>
  <span class="flow-arrow"><svg><use href="#i-arrow-right"/></svg></span>
  <div class="flow-step flow-step--last">Reserva no PMS</div>
</div>
```

`--last` destaca o passo final. Cinco passos no máximo — a partir daí ninguém lê a cadeia inteira.

Use para explicar caminho. Não use para mostrar perda entre etapas: quem carrega proporção é o `.funil`, no modo A.

### .persona-card, .persona-card__glyph, .persona-card__role

Modo B. Cartão de papel/pessoa, dentro de `.grid--2` ou `.grid--3`.

```html
<div class="grid grid--3">
  <div class="persona-card">
    <span class="persona-card__glyph"><svg><use href="#i-user-check"/></svg></span>
    <h4>Atendente</h4>
    <span class="persona-card__role">opera a caixa</span>
    <p>Recebe, responde e passa adiante sem perder histórico.</p>
  </div>
  <div class="persona-card">
    <span class="persona-card__glyph"><svg><use href="#i-gauge"/></svg></span>
    <h4>Gestor</h4>
    <span class="persona-card__role">acompanha a fila</span>
    <p>Vê o que não foi respondido e o tempo de resposta por canal.</p>
  </div>
  <div class="persona-card">
    <span class="persona-card__glyph"><svg><use href="#i-key"/></svg></span>
    <h4>Diretoria</h4>
    <span class="persona-card__role">lê o resultado</span>
    <p>Recebe o relatório mensal com receita do PMS e esforço comercial do CRM, separados.</p>
  </div>
</div>
```

`.persona-card__role` é a função em minúscula, uma linha. Não coloque nome de pessoa real no cartão.

### .callout

Modo B. Bloco de destaque no meio do texto: a frase que resume o capítulo.

```html
<p class="callout">O ganho não foi responder mais rápido. Foi passar a saber quem não foi respondido.</p>
```

Um por página. Não use para dado — dado com destaque é `.stat-row`. Não use para ressalva — ressalva é `.nota`.

Antes de escrever num `.callout` o efeito prometido de uma correção, rode o dry-run. Já foi afirmado que "2.030 sessões seriam reclassificadas" quando o dry-run mostrou cerca de 30 contatos.

### .closing

Modo A e modo B. A frase de fechamento.

Modo A, com `<b>`:

```html
<div class="closing">Julho provou que <b>a demanda responde</b>: R$ 63,9 mil em mídia viraram
  10.386 leads e o maior faturamento do ano. O limite de agosto não é gerar procura —
  é <b>o que a gente faz depois que o orçamento sai</b>.</div>
```

Modo B, com `<em>`:

```html
<div class="closing"><em>O sistema não vende sozinho.</em> Ele mostra, todo dia, onde a venda
  está parando.</div>
```

Armadilhas:
- No modo A o `.closing` costuma dividir o slide final com `.lista` e `.metod`. Nessa combinação, o `.closing` cabe em três linhas — a quarta passa por baixo do `.sfoot`.
- Fechamento não introduz número novo. Todo valor citado aqui já apareceu antes, com a mesma apuração.

---

## Interface e prova

### .shot, .frame, .frame__bar, .frame__dots, .frame__url, .frame__spacer, .frame__note

Modo B **e modo A**. Moldura de navegador em volta de um print. É como o deck mostra que a coisa existe.

```html
<figure class="shot">
  <div class="frame">
    <div class="frame__bar">
      <span class="frame__dots"><i></i><i></i><i></i></span>
      <span class="frame__url">mkt.grgroup.app/emails</span>
      <span class="frame__spacer"></span>
    </div>
    <img src="assets/emails.png" alt="Tela de disparo de e-mail com o segmento selecionado">
  </div>
  <figcaption class="frame__note">Print de 03/08/2026. Telefones e e-mails borrados.</figcaption>
</figure>
```

No modo A, entre no lugar do bloco central, com o mesmo `margin-top:auto; margin-bottom:auto` do restante:

```html
<div class="shot" style="margin-top:auto;margin-bottom:auto">…</div>
```

Armadilhas:
- `.frame__url` mostra a URL real da tela. URL inventada quebra a confiança do print inteiro.
- `.frame__spacer` é o contrapeso vazio dos `.frame__dots`, para a URL ficar centralizada. Não coloque conteúdo dentro.
- `.frame__note` é obrigatória quando o print tem dado de cliente: diga a data e diga o que foi borrado.
- Print de tela com dado de teste tem que ser declarado como tal na `.frame__note`. Print de mockup apresentado como sistema no ar é o erro mais caro deste catálogo.
- Imagem sempre com `alt` descrevendo o que se vê, não "print da tela".

### .hero-stack, .hero-shot, --a, --b, --c

Modo B. Colagem de três prints levemente rotacionados, na capa.

```html
<div class="hero-stack">
  <img class="hero-shot hero-shot--a" src="assets/hero-atendimento.png" alt="Caixa de atendimento">
  <img class="hero-shot hero-shot--b" src="assets/hero-crm.png" alt="Funil do CRM">
  <img class="hero-shot hero-shot--c" src="assets/hero-relatorio.png" alt="Relatório mensal">
</div>
```

Exatamente três, com `--a`, `--b` e `--c` — cada modificador tem sua rotação e seu deslocamento. Quatro imagens não têm modificador e empilham sem offset.

Armadilhas:
- As rotações vazam da caixa. O `.capa-grid` reserva o espaço; não coloque `overflow:hidden` em volta.
- Use prints de proporção parecida. Um print muito mais alto que os outros desalinha a colagem inteira.

### Sprite de ícones

Um único `<svg>` oculto no começo do `<body>`, com um `<symbol>` por ícone. Vale nos dois modos.

```html
<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <symbol id="i-target" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/>
  </symbol>
  <!-- … demais símbolos -->
</svg>
```

Uso:

```html
<svg><use href="#i-target"/></svg>
```

Nomes disponíveis — não invente outros:

`i-compass` `i-target` `i-check` `i-chart` `i-repeat` `i-bell` `i-clipboard` `i-bot` `i-zap`
`i-kanban` `i-layers` `i-message` `i-broadcast` `i-prism` `i-heart` `i-trophy` `i-star` `i-coin`
`i-inbox` `i-search` `i-gauge` `i-user-check` `i-key` `i-users` `i-play` `i-link` `i-grid`
`i-code` `i-arrow-right` `i-arrow-down` `i-chev-up` `i-chev-down` `i-sparkle` `i-clock` `i-hand`
`i-phone` `i-globe` `i-building`

Armadilhas:
- Traço em `currentColor`: o ícone herda a cor do contexto. Não fixe `stroke` no `<symbol>` — em `.page--dark` ele some.
- `viewBox` fica no `<symbol>`; o tamanho vem do CSS do container (`.spec-row__icon`, `.ledger__ico`, `.ic`).
- O sprite tem que estar no mesmo arquivo HTML. Referência a arquivo externo quebra no print do Chrome e na abertura por `file://`.
- Ao separar o deck em N arquivos de um slide para exportar PNG, **copie o sprite para cada arquivo**. Sem ele, todos os ícones somem do PNG e o erro só aparece na imagem final.

---

## Honestidade

Estes dois componentes existem nos dois modos. Eles são o que separa um deck de dado de um deck de slogan.

### .nota

Rodapé analítico do slide: contexto, base de cálculo, o que o número não diz.

```html
<div class="nota">O canal próprio responde por <b style="color:var(--ink)">62% da receita</b> —
  é onde o Growth mexe o ponteiro. Mas o <b style="color:var(--ink)">site vende R$ 55 mil</b>
  num mês de R$ 1,40 milhões — <b style="color:var(--ink)">2,1% da receita</b>.</div>
```

Use em todo slide que tem número. O `<b style="color:var(--ink)">` destaca o valor dentro do texto corrido; `<span style="opacity:.75">` rebaixa a parte que é ressalva técnica.

Armadilhas:
- Cinco linhas é o teto no modo A quando há `.metod` no mesmo slide. Acima disso, o texto passa por baixo do `.sfoot`.
- É na `.nota` que se resolve a ambiguidade de rótulo. Não escreva "R$ 319 mil ainda não realizado" se 82% já foi realizado — escreva o que o número é.
- Quando o mesmo conceito tem mais de uma contagem possível, liste as contagens e diga qual está em uso: "87 é a safra de julho, 113 é lead de qualquer safra, 105 é primeiro toque. Diga sempre qual."
- Referência a outro slide vai por título, nunca por número.

### .metod e .metod .h

Bloco azul de metodologia e ressalva. É onde se avisa que o número tem limite.

```html
<div class="metod"><span class="h">Leia antes de usar estes números</span>
  <b>1.</b> Só o pipeline de <b>Hospedagem</b>. O CRM inteiro somaria 13.593 entradas, mas inclui
  Recepção, Day Use e Ingressos — que não são oportunidade comercial e distorcem a conversão.
  <b>2.</b> Só <b>28,9% dos cards perdidos têm valor</b> (1.567 de 5.428): os R$ 6,52 mi são a soma
  desses, não o total real.
  <b>3.</b> A venda oficial é a do PMS — o CRM mede esforço comercial.</div>
```

O `.metod .h` é o título em caixa alta: uma frase que já entrega o aviso ("Os 87 não são o resultado da safra — são o que coube em 31 dias"), não a palavra "Metodologia" sozinha.

Use `.metod` obrigatoriamente quando:

- **A base ainda não maturou.** Censura à direita: já foi projetada receita sobre uma safra em que só 13% dos leads tinham completado 30 dias, e o número mudava conforme o dia da apuração. Ou compara só a parte madura, ou não projeta — e se não dá para projetar, o `.metod` diz **por que** não dá.
- **O número vem de sistema diferente do slide vizinho.** CRM e PMS não se somam nem se dividem um pelo outro.
- **Existe duplicidade conhecida.** Vinte pares de mesmo contato e mesmo valor lançados duas vezes já inflaram um total.
- **"Ganho" pode reverter.** Ganho no CRM precisa descontar reversão posterior, senão conta venda que caiu.
- **A amostra foi lida por IA ou por amostragem.** Diga o tamanho e diga que foi auditada por amostra.
- **Você mediu uma coluna e concluiu que o dado não existe.** Já foi publicado "99,96% das conversas chegam sem UTM" medindo o campo errado: a atribuição vivia em outra tabela, com 100% de cobertura. Confirme qual coluna carrega o dado antes de afirmar ausência.
- **A correção proposta tem efeito menor que o volume citado.** Rode o dry-run e escreva o resultado dele, não a expectativa.

Armadilhas:
- Sete linhas é o teto no modo A. `.metod` longo é o que mais empurra conteúdo para baixo do `.sfoot`.
- Um `.metod` por slide. Dois viram parede de texto e ninguém lê nenhum dos dois.
- `.metod` não é desculpa: é instrução de uso. Escreva no imperativo — "use R$ 154 mil para um número conservador".

### .badge-soon

Modo B. Etiqueta para o que ainda não existe.

```html
<h4>Painel de metas por atendente <span class="badge-soon">em breve</span></h4>
```

Use em todo item de `.ledger`, `.spec-list` ou `.agenda-grid` que ainda não está no ar. Sem ela, roadmap vira entrega na cabeça de quem lê — e vira cobrança na ata.

Não use como enfeite em coisa entregue. A etiqueta só tem valor enquanto for verdadeira.

---

## Navegação

### HUD: .hud-logo, .hud-counter, .hud-controls, .hud-btn, body.on-dark

Modo B. Barra fixa de navegação, fora das `.page`, filha direta do `<body>`.

```html
<div class="hud-logo"><svg><use href="#i-prism"/></svg> GR Group</div>
<div class="hud-counter"><b>03</b> / 14</div>
<div class="hud-controls">
  <button class="hud-btn" id="nav-prev" type="button" aria-label="Seção anterior"><svg><use href="#i-chev-up"/></svg></button>
  <button class="hud-btn" id="nav-next" type="button" aria-label="Próxima seção"><svg><use href="#i-chev-down"/></svg></button>
</div>
```

O HUD troca de cor sozinho sobre `.page--dark`: um IntersectionObserver põe e tira `body.on-dark`, e o CSS inverte `.hud-logo`, `.hud-counter` e `.hud-btn`.

Armadilhas:
- O total do `.hud-counter` é escrito pelo script na carga, contando as `.page`. Não deixe número fixo no HTML — ele desatualiza a cada capítulo inserido.
- `.hud-btn` precisa de `aria-label`: o conteúdo é só um ícone.
- O HUD é `position:fixed`. Ele aparece por cima do conteúdo em telas baixas — deixe respiro no canto inferior direito das páginas cheias.
- No `@media print` o HUD sai. Confira: HUD impresso em cima do slide é erro que só aparece no PDF.

### Teclado

Modo B. O script escuta: setas para cima/baixo e esquerda/direita, PageUp/PageDown, barra de espaço, Home e End.

Espaço avança e `Shift`+espaço volta. `Home` vai para a capa, `End` para a `.page--fim`. Não capture `Tab` — a navegação por foco tem que continuar funcionando.

### .reveal e data-delay

Modo B. Entrada animada do bloco quando ele chega na tela.

```html
<div class="reveal" data-delay="1">…</div>
<div class="reveal" data-delay="2">…</div>
<div class="reveal" data-delay="3">…</div>
<div class="reveal" data-delay="4">…</div>
```

`data-delay` vai de 1 a 4. Não invente 5 — não existe regra de CSS para ele e o bloco entra sem atraso, fora de cadência.

Armadilhas:
- Não ponha `.reveal` na `.page__inner` inteira: se o observer falhar, a página fica em branco. Anime os blocos internos.
- `@media (prefers-reduced-motion: reduce)` desliga a animação. Não anule.
- Bloco animado com `opacity:0` inicial **some no PDF** se o observer não disparou antes da impressão. Antes de imprimir, role o documento inteiro até o fim para acionar todos os reveals.

### Impressão e export

Modo A: o `@page` já é `1920px 1080px`, margem zero, e cada `.slide:not(:last-child)` força quebra de página. Para PNG, separe o HTML em N arquivos de um slide cada (head completo + sprite + um `<section>`) e tire um print de cada. Print do documento inteiro sai errado.

```
CH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
"$CH" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=1920,1080 --screenshot=saida.png "file:///caminho/um-slide.html"
```

Modo B: o `@media print` força `338mm x 190mm` (16:9) e desliga o scroll-snap, para virar PDF de slides.

Nos dois: imprimir pelo Chrome com "Salvar como PDF", margens nulas e gráficos de fundo ligados.

Depois de publicar, confira. Compare o `shasum -a 256` do arquivo local com o do `curl` da URL publicada — já foi publicada uma versão antiga sem ninguém perceber.

---

## Quantos cabem

Limites reais, testados em 1920x1080 (modo A) e em 1366x768 (modo B). Passou disso, o conteúdo some sob o `.sfoot` no modo A, ou fica fora dos 100dvh no modo B. Quando não couber: quebre em duas telas. Nunca reduza a fonte abaixo dos tokens.

| Componente | Modo | Cabe | Observação |
|---|---|---|---|
| `.mini` | A · capa | 4 blocos | 5 só com rótulos de até 3 palavras |
| `.stats` | A | 4 cartões | com `.nota` **e** `.metod` no mesmo slide, ainda cabe |
| `.stats.tres` | A | 3 cartões | número maior, sobra espaço para `.metod` longo |
| `.stats.dois` | A | 2 cartões | combina com `.funil.compacto` de até 4 linhas abaixo |
| `.funil` | A | 4 linhas com `.nota` + `.metod` · 5 com só `.nota` · 6 sem nenhum dos dois | acima disso, use `.compacto` |
| `.funil.compacto` | A | 7 linhas com `.nota` de até 4 linhas | 7 linhas + `.nota` + `.metod` só se ambos forem curtos; 8 linhas não cabem |
| `.lista` | A | 6 itens (2 colunas x 3 linhas) com `.nota` + `.metod` | 8 itens só sem `.metod` |
| `.lista.um` | A | 4 itens com `.closing` + `.metod` · 6 itens sem `.metod` | usar quando o `.nome` passa de 40 caracteres |
| `.feat` | A | 3 cartões | grade fixa de 3 colunas: o 4º cai na 2ª linha e desaparece |
| `.chips` | A | 5 chips | quebra em 2 linhas a partir de 6 |
| `.nota` | A e B | 5 linhas de texto | 3 linhas quando dividir o slide com `.metod` e `.closing` |
| `.metod` | A e B | 7 linhas de texto | 1 por slide |
| `.closing` | A e B | 3 linhas | 2 quando houver `.metod` no mesmo slide |
| `.title` | A | 1 linha (até ~46 caracteres) | 2 linhas empurram o bloco central |
| `.shot` no modo A | A | 1 print | 2 prints lado a lado só sem `.metod` |
| `.capa-stats` | B | 3 `.capa-stat` | 4 comprimem o número |
| `.hero-stack` | B | 3 `.hero-shot` | exatamente 3: só existem `--a`, `--b` e `--c` |
| `.agenda-grid` | B | 8 itens em 4 colunas | 6 itens é o número confortável; 10 exige rolagem e quebra o snap |
| `.sys` | B | 1 por página | com `.spec-list` no `.sys__body`, no máximo 4 linhas |
| `.spec-list` | B | 5 linhas soltas na página · 4 dentro de `.sys__body` | acima disso, divida em duas páginas |
| `.compare-grid` | B | 2 cartões | sempre dois — é comparativo |
| `.shift` | B | 2 lados + 1 seta | 1 por página |
| `.stat-row` | B | 4 boxes · 3 quando houver `.lede` longa acima | mais que isso é relatório, use o modo A |
| `.flow-chain` | B | 5 passos | 6 passos quebram a linha e a seta gira sozinha |
| `.ledger` | B | 6 linhas com `.total` abaixo · 8 sem `.total` | `--wide` conta como 1,5 linha |
| `.total` | B | 2 `.total__block` + `.total__text` | 1 por página |
| `.grid--3` | B | 3 cartões | 6 (duas fileiras) só em página sem `.page-head` |
| `.grid--2` | B | 2 cartões · 4 em duas fileiras | |
| `.callout` | B | 2 linhas | 1 por página |
| `.reveal` | B | `data-delay` de 1 a 4 | 4 blocos animados por página |
