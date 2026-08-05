# Integridade de dados

O arquivo mais importante desta skill. Layout bonito com número errado é pior que
tabela feia com número certo.

---

## 1. Deck de diretoria não é deck interno

Num deck interno, o número errado morre na reunião: alguém corrige, todo mundo ri, segue o jogo.

Num deck de diretoria, o número **vira ata**. Ele é copiado para a apresentação do trimestre,
citado numa meta, usado para aprovar ou cortar verba, e volta três meses depois como cobrança —
com o seu nome do lado. Ninguém vai lembrar da ressalva que você falou de boca; vão lembrar do
que estava escrito no slide.

Três consequências práticas:

- **O slide é o contrato.** O que não está escrito, não foi dito.
- **Errar para mais é pior que errar para menos.** Número inflado vira meta impossível no mês seguinte.
- **Ressalva não enfraquece o deck — sustenta ele.** Quem mostra o limite do próprio dado ganha
  o direito de ser acreditado no resto.

Por isso este sistema tem dois componentes de honestidade que existem nos **dois modos** (`relatorio` e `narrativa`):

- `.nota` — o contexto que impede a leitura errada. Vai sempre.
- `.metod` (com `.metod .h`) — a ressalva de método: o que o número **não** é, por que ele muda, o que ficou de fora.

Regra de ouro: **se você precisou explicar o número na reunião, ele precisava de `.metod` no slide.**

---

## 2. Antes de escrever qualquer slide

Checklist de apuração. Rode inteiro, na ordem, antes de abrir o HTML.

1. **Defina a pergunta que a diretoria vai fazer com esse número.** Se não dá para escrever a pergunta em uma linha, o slide não existe.
2. **Escolha o sistema-fonte de cada métrica e escreva no `.sfoot .u`.** Receita vem do sistema de receita. Esforço comercial vem do CRM. Mídia vem da API da plataforma.
3. **Confirme QUAL coluna carrega o dado.** Nome parecido não é a mesma coluna. Consulte o schema antes de concluir que o dado não existe.
4. **Aplique o recorte antes de contar.** Tenant/marca, período, status válido (fora: cancelado, no-show, pré-reserva, teste).
5. **Filtre o lixo na origem.** Bot por `user_agent`, tráfego de rede interna por IP/referrer, duplicados por chave de deduplicação declarada.
6. **Abra a amostra.** Todo contador acima de mil ganha uma leitura de 30 a 50 casos reais antes de virar afirmação.
7. **Fixe a unidade de tempo que a diretoria usa para decidir.** Mês fechado por padrão. Janela móvel só quando a pergunta é explicitamente sobre janela.
8. **Anote a data de apuração.** Todo número vivo muda. `apurado em DD/MM/AAAA` no `.sfoot`.
9. **Teste a maturidade da base.** Que % da safra já completou o ciclo de decisão? Abaixo de ~80%, não projete (seção 5).
10. **Verifique o histórico completo antes de qualquer superlativo.** "Maior", "melhor", "recorde", "mais barato" exigem consulta a todo o período, não aos últimos dois meses.
11. **Monte a tabela de números repetidos.** Todo número que aparece em mais de um slide entra numa lista com sua apuração de origem.
12. **Rode o dry-run de toda correção prometida.** O efeito real, não o efeito esperado.
13. **Escreva o rótulo de cada número dizendo o que ele É.** Se o rótulo aceita duas leituras, reescreva.
14. **Separe fato, estimativa e leitura de tendência** (seção 4) — e marque cada um no slide.
15. **Releia os títulos procurando culpado.** Troque acusação por problema + caminho.

---

## 3. Os 16 erros

Cada um aconteceu de verdade num relatório mensal para diretoria. Formato:
**afirmei → era → regra**.

### Família A — Fonte errada (a métrica veio do lugar errado)

**E03 · Coluna errada**
- **Afirmei:** "99,96% das conversas chegam sem UTM."
- **Era:** eu tinha medido o `utm_source` da *conversa*. A atribuição real vivia em outra tabela, com 100% de cobertura.
- **Regra:** confirme qual coluna carrega o dado antes de concluir que o dado não existe.
- **Regra:** ausência de dado é a acusação mais grave que você pode fazer a um sistema — prove em duas tabelas antes de escrever.

**E04 · Sistema errado**
- **Afirmei:** um total de receita somando CRM e PMS.
- **Era:** o CRM registrou 31% a mais que o PMS e tinha 20 pares duplicados (mesmo contato, mesmo valor, dois lançamentos).
- **Regra:** receita vem do sistema de receita; o CRM mede esforço comercial.
- **Regra:** nunca some dois sistemas na mesma barra, nem divida um pelo outro. Se aparecerem no mesmo slide, diga a origem de cada um na `.nota`.

**E14 · Recorte errado**
- **Afirmei:** números de um deck declarado de uma marca só.
- **Era:** as tabelas eram multi-tenant e sem filtro — quatro marcas misturadas.
- **Regra:** filtre o tenant na query, não na cabeça; declare o recorte no `.subtitle` ou no `.sfoot`.

**E15 · Definição errada da métrica**
- **Afirmei:** o total de "ganho" do CRM.
- **Era:** ganho bruto conta venda que depois caiu.
- **Regra:** ganho é sempre líquido de reversão posterior; escreva "líquido de reversões" junto do rótulo.

### Família B — Contador bruto (o número existia, o fato não)

**E01 · Tráfego com robô**
- **Afirmei:** "111,8 mil visitantes."
- **Era:** 74% era bingbot. O tracker escreve um parâmetro na URL e o crawler trata cada URL como página nova.
- **Regra:** filtre `user_agent` de bot e referrer de rede interna **antes** de reportar tráfego.
- **Regra:** quando o número cair pela metade depois do filtro, explique a queda no `.metod` — senão o slide parece contradizer o mês anterior.

**E02 · Contador de "sem resposta"**
- **Afirmei:** "30.565 conversas sem resposta."
- **Era:** eram disparos nossos, não demanda. Das 3.122 realmente entrantes sem retorno: 850 sem mensagem nenhuma, 293 autoresponders de outras empresas, 152 menções de story, 146 ruído — e o resto classificado a mão até sobrarem **1.578 pessoas reais**.
- **Regra:** contador bruto não é fato; abra a amostra antes de afirmar.
- **Regra:** separe o que **nós** iniciamos do que **o cliente** iniciou antes de calcular qualquer taxa de atendimento.
- **Regra:** publique o número depurado como principal e o bruto na `.metod`, com a conta da depuração.

### Família C — Comparação inválida (faltou o outro lado)

**E06 · Superlativo sem histórico**
- **Afirmei:** "melhor mês do ano."
- **Era:** março e janeiro foram maiores.
- **Regra:** superlativo exige consulta ao histórico completo, sempre.
- **Regra:** se não consultou, escreva o fato relativo ("maior desde março") com os dois valores de referência na `.nota`.

**E07 · Comparativo com um lado só**
- **Afirmei:** "o clique mais barato do mês", sobre um canal cujo CPC era **maior** que o do outro.
- **Era:** eu tinha olhado só a série daquele canal.
- **Regra:** comparativo exige os dois lados na mesma tela — no `.stat .sb`, na `.nota` ou em duas linhas do `.funil`.
- **Regra:** `.chip.up` / `.chip.down` só quando o valor de comparação está visível ao lado.

**E09 · Unidade de tempo errada**
- **Afirmei:** resultados em janela móvel de 30/60 dias.
- **Era:** a pergunta da diretoria era "por mês".
- **Regra:** escolha a unidade que a diretoria usa para decidir; mês fechado é auditável, janela móvel não.
- **Regra:** nunca misture janela móvel e mês fechado no mesmo slide sem dizer qual é qual.

### Família D — Projeção indevida (a base não estava madura)

**E08 · Censura à direita**
- **Afirmei:** receita futura projetada sobre uma safra.
- **Era:** só 13% dos leads tinham completado 30 dias. O número inflava ou desinflava conforme o dia da apuração.
- **Regra:** com base imatura, compare só a parte madura — ou não projete.
- **Regra:** se não dá para projetar, escreva no slide **por que** não dá (seção 5).
- **Regra:** toda safra citada leva a data de apuração e o % já maturado.

### Família E — Rótulo ambíguo (o número certo, lido errado)

**E10 · Rótulo que aceita duas leituras**
- **Afirmei:** "R$ 319 mil ainda não realizado."
- **Era:** os R$ 319 mil eram o **total projetado**, com 82% já realizado.
- **Regra:** escreva o que o número É, não o que ele sugere.
- **Regra:** rótulo ambíguo vira cobrança em ata — leia cada rótulo assumindo má-fé de quem lê.
- **Regra:** valor com parte já realizada sempre vem quebrado: total, realizado, em aberto.

### Família F — Tom (o slide certo, a frase errada)

**E11 · Título acusatório**
- **Afirmei:** um título chamando um canal de "buraco de rastreio".
- **Era:** o problema era real, mas o slide vai para diretoria e o dono do canal está na sala.
- **Regra:** o slide aponta o problema e o caminho, não o culpado.
- **Regra:** título nomeia a oportunidade ("o canal a destravar"), a `.nota` mede o tamanho do problema, o `.metod` diz qual é a correção e de quem é a alavanca.
- **Regra:** nenhum nome de pessoa em slide de problema.

### Família G — Processo (a apuração estava certa; o deck, não)

**E05 · Número repetido divergente**
- **Afirmei:** ROAS 5,9× na capa e 5,7× no slide interno.
- **Era:** a capa tinha ficado com a apuração antiga.
- **Regra:** todo número repetido em mais de um slide vem da mesma apuração e é reconferido a cada edição.
- **Regra:** a capa (`.cover .mini .n`) é o lugar que mais envelhece — reconfira por último, sempre.

**E12 · Prometer efeito sem dry-run**
- **Afirmei:** "2.030 sessões serão reclassificadas."
- **Era:** o dry-run mostrou ~30 contatos. As sessões só viram toque quando existe contato identificado.
- **Regra:** rode o dry-run antes de prometer o efeito de uma correção.
- **Regra:** separe no `.metod` o tamanho do sintoma e o tamanho do conserto — quase nunca são o mesmo número.

**E13 · Referência cruzada por número**
- **Afirmei:** "ver slide 09" — e depois inseri slides no meio.
- **Era:** todas as referências passaram a apontar para o slide errado.
- **Regra:** referencie por título, nunca por número; se usar número, reconfira todas após qualquer inserção.
- **Regra:** o `.pageno` também é referência — reconfira a numeração inteira depois de inserir ou remover `.slide`.

```bash
# listar títulos na ordem real do arquivo (para reconferir referências e .pageno)
grep -n '<div class="title">' deck.html
grep -n 'class="pageno"' deck.html
grep -c '<section' deck.html   # conta a capa também; 'class="slide"' exato NÃO pega .slide.cover
```

**E16 · Publicar e não conferir**
- **Afirmei:** que estava no ar.
- **Era:** eu não tinha comparado o que subiu com o que estava na minha máquina.
- **Regra:** compare o hash do arquivo local com o do que está no ar antes de mandar o link (seção 6).

---

## 4. Fato, estimativa e leitura de tendência

Três naturezas diferentes. O leitor não distingue sozinho — **você marca**.

### Fato

Número medido, de uma fonte declarada, num período fechado.

- Vai no `.stat .big`, no `.fill`, no `.li .val`, no `.mini .n`.
- Leva fonte no `.sfoot .u` e período no lado direito do `.sfoot`.
- Escreva sem advérbio. Fato não precisa de "aproximadamente".

```
RUIM: "Cerca de 2,5 milhões em vendas no mês, aproximadamente 60% acima de junho."
BOM:  "R$ 2.583.242 em vendas · +60,0% vs. junho (R$ 1,61 mi)."
      .sfoot: "Fonte: PMS · reservas" | "Mês/Ano · mês fechado"
```

### Estimativa

Número derivado de suposição, extrapolação ou classificação assistida.

- Diga que é estimativa **no mesmo bloco do número**, não no rodapé.
- O `.metod` carrega o método, a base e o intervalo.
- Se houver versão conservadora, ofereça ela como número de trabalho.

```
RUIM: "O Instagram trouxe R$ 222 mil."
BOM:  "Instagram: R$ 222 mil, dos quais R$ 152 mil com origem confirmada pelo link
       e R$ 52 mil declarados pelo cliente. Para número conservador, use R$ 154 mil."
       .metod: como cada pedaço foi classificado e o que fica de fora.
```

```
RUIM: "70% dos clientes compram por causa da estrutura para crianças."
BOM:  "Estrutura para crianças aparece em 243 das 438 conversas ganhas (55,5%).
       Uma conversa pode ter mais de um motivo — os percentuais somam mais de 100%.
       O número diz em quantas conversas o tema aparece, não que o motivo foi esse."
```

### Leitura de tendência

Interpretação sua sobre a direção do número. É a parte mais útil do deck e a mais fácil de errar.

- Sempre com os dois lados na tela e a base explícita.
- Nunca declare tendência com uma única observação.
- Use `.chip.up` / `.chip.down` só ao lado do valor comparado.

```
RUIM: "A safra de julho deve fechar em R$ 500 mil."
BOM:  "Junho fechou metade da receita da safra fora do próprio mês (R$ 51,0 mil dentro,
       R$ 50,3 mil no mês seguinte). É uma safra só — não faz padrão.
       Fato: R$ 20,2 mil de lead de julho já entraram nos 5 primeiros dias de agosto."
```

```
RUIM: "O canal está crescendo."
BOM:  "12,7% em julho, 17,6% nos 5 primeiros dias de agosto — dois pontos de medição,
       ainda não é série. Fechamos a leitura no fim de agosto."
```

Palavras que exigem prova antes de entrar no slide:
**maior, melhor, recorde, mais barato, dobrou, sempre, nunca, ninguém, todo mundo, vai fechar em.**

---

## 5. Quando NÃO dar o número

Não dar o número é uma resposta. Chutar não é.

Um slide que assume o limite do dado é **mais forte** que um que projeta, porque:

- ele sobrevive à próxima apuração — o chute não;
- ele mostra que existe um método por trás dos outros números do deck;
- ele transforma "não sei" em compromisso com data, que é o que a diretoria precisa para planejar.

**A estrutura de quatro partes.** Use nesta ordem, no `.nota` + `.metod` do slide:

1. **O que já é fato** — a parte madura, medida, com número.
2. **Por que não dá para projetar** — a razão técnica, em uma linha (base imatura, safra única, cobertura parcial, catálogo vazio).
3. **O fato parcial que já existe** — o pedaço que já entrou, marcado como fato e não como tendência.
4. **Quando vai dar** — a data em que a leitura fecha.

```
RUIM: "Projetamos que a safra de julho renda mais R$ 260 mil até setembro."

BOM:  "Para julho não cravamos número: só temos uma safra completa para comparar
       e uma safra não faz padrão. Fato, não estimativa: R$ 20,2 mil de lead de julho
       já entraram nos 5 primeiros dias de agosto. Fechamos a curva em setembro."
```

```
RUIM: "Os clientes ganham por preço." (quando o catálogo de motivo de ganho está vazio)

BOM:  "O CRM não sabe por que a gente ganha: o catálogo de motivos de ganho está vazio —
       zero motivos cadastrados em 19.979 oportunidades. Para não ficar sem resposta,
       lemos as 438 conversas dos negócios ganhos do mês."
```

Outras situações em que a resposta certa é não dar o número:

- **Base imatura** — menos de ~80% da safra completou o ciclo. Compare só a parte madura.
- **Uma observação só** — série de um ponto não é tendência; diga quantos pontos faltam.
- **Cobertura parcial do campo** — se só 28,9% dos registros perdidos têm valor, o total é a soma desses, não o total real. Escreva isso.
- **Métrica sem dono** — se nenhum sistema é a fonte oficial daquele número, o slide diz isso em vez de escolher o sistema mais generoso.
- **Correção ainda não rodada** — nunca publique o efeito esperado; publique o dry-run ou nada.

E o inverso: **não use `.badge-soon` para maquiar o que não foi medido.** Esse componente é para o que ainda não existe no produto, não para dado que você não apurou.

---

## 6. Checklist de publicação

Antes de mandar o link.

**Conteúdo**

1. Todo número repetido bate entre capa e miolo (E05) — confira a capa por último.
2. Toda referência cruzada aponta para o título certo e o `.pageno` está na ordem real (E13).
3. Todo slide com número tem fonte no `.sfoot .u` e período no lado direito.
4. Todo número vivo tem data de apuração escrita.
5. Todo superlativo tem o histórico consultado e os valores de comparação visíveis (E06, E07).
6. Todo slide de problema aponta caminho e não pessoa (E11).
7. Toda ressalva conhecida está em `.metod` — não na sua cabeça, não no e-mail.
8. Todo rótulo diz o que o número é, sem segunda leitura possível (E10).
9. As barras `.fill` são proporcionais ao valor real, nunca decorativas.

**Layout (ressalva escondida = ressalva inexistente)**

10. Abra cada slide e confira que `.nota` e `.metod` **não passam por baixo do `.sfoot`** — o `.slide` tem `overflow:hidden` e come o texto sem aviso. É a causa nº 1 de slide quebrado.
11. Funil com 7 linhas usa `.funil.compacto`; barra estreita usa `.fill.sm` para o rótulo sair de dentro da barra.
12. Confira a contagem de slides:

```bash
grep -c '<section' deck.html
```

**Exportação**

13. PNG por slide (2x, 3840×2160) — separe o HTML em N arquivos de 1 slide (head + section) e tire 1 print de cada; print do documento inteiro sai errado:

```bash
CH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
"$CH" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=1920,1080 --screenshot=saida.png "file:///caminho/um-slide.html"
```

14. PDF: abra no Chrome, "Salvar como PDF", margens nulas, gráficos de fundo ligados. O `@page` do modo `relatorio` já define 1920×1080; o do modo `narrativa`, 338mm × 190mm.
15. Abra o PDF e confira os títulos com gradiente — texto com `background-clip:text` vira retângulo colorido na impressão se o `@media print` não forçar cor sólida.

**Publicação**

16. Publique e **confira o que subiu** (E16):

```bash
cp deck.html deploy/index.html && cd deploy && vercel deploy --prod --yes
shasum -a 256 deck.html
curl -s https://URL-PUBLICADA | shasum -a 256   # os dois hashes têm que bater
```

17. Abra a URL publicada num navegador limpo, sem cache, e leia a capa inteira antes de mandar.

**A pergunta final, antes de enviar:** se a diretoria imprimir este slide e cobrar você por ele daqui a três meses, o slide se defende sozinho?
