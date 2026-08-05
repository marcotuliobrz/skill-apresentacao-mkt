---
name: apresentacao-mkt
description: >-
  Gera apresentações corporativas como um único HTML autocontido, em dois modos do mesmo sistema
  visual: "relatorio" (tema escuro, slide fixo 1920x1080, para dados, números e board reporting) e
  "narrativa" (tema claro, página rolável com scroll-snap, para contar história, mostrar produto e
  fazer tour de telas). Entrega PNG por slide, PDF 16:9 e publicação na Vercel. Use quando pedirem
  relatório mensal, apresentação, deck, slides, board report, review de resultados, prestação de
  contas, showcase de entregas ou tour de produto. Não use para site responsivo, landing page,
  dashboard vivo, componente de app, nem para edição de PSD, imagem ou vídeo.
---

# apresentacao-mkt

Sai um arquivo HTML único e autocontido — que vira PNG por slide, PDF 16:9 e URL publicada — em que todo número na tela tem fonte, recorte e data de apuração declarados.

## Os dois modos

Um sistema visual, duas páginas possíveis. Escolha pelo trabalho que o deck precisa fazer.

| | `relatorio` | `narrativa` |
|---|---|---|
| Para quê | Dados, números, diretoria, prestação de contas | História, produto, entrega, tour de telas |
| Tema | Escuro (`--bg #050507`) | Claro (`--bg #FFFFFF`, acento `--accent #DB824E`) |
| Página | `.slide` fixo 1920x1080, um por `<section>` | `.page` rolável, `min-height:100dvh`, scroll-snap |
| Navegação | Nenhuma — é slide | HUD fixo + setas, PageUp/Down, espaço, Home, End |
| Saída | PNG 3840x2160 por slide + PDF 1920x1080 | PDF 338mm x 190mm via `@media print` |
| Componente-âncora | `.stats`, `.funil`, `.lista`, `.feat` | `.sys`, `.shift`, `.spec-list`, `.shot > .frame` |

**Misture quando fizer sentido.** Uma narrativa que precisa provar resultado ganha uma `.page--dark` com `.stat-row` no meio. Um relatório que precisa mostrar a tela do produto usa `.frame` dentro do slide escuro. `.nota` e `.metod` existem nos dois modos — são os componentes de honestidade e não são opcionais em slide com número. O que nunca acontece: misturar as duas paletas na mesma página.

Não invente classe. O contrato de componentes está em `references/componentes.md` e é fechado: se o layout não existe lá, componha com o que existe.

## O procedimento

1. **Enquadre a pergunta.** Uma frase: quem lê, que decisão toma, em que unidade de tempo decide. Se a diretoria decide por mês fechado, o deck é por mês fechado — nunca janela móvel de 30/60 dias, que não é auditável.

2. **Escolha o modo e trave o escopo.** Marca, tenant, período, sistema-fonte de cada bloco. Deck declarado de uma marca só roda com filtro de tenant em toda consulta — tabela multi-tenant sem filtro mistura quatro marcas e ninguém percebe olhando o slide.

3. **APURE ANTES DE ESCREVER.** Nenhuma linha de HTML antes desta etapa fechar. Produza uma folha de apuração: uma linha por número, com valor, query/fonte, recorte e data de apuração. Regras que valem sempre:
   - Receita vem do sistema de receita (PMS). CRM mede esforço comercial. Nunca some os dois, nunca divida um pelo outro.
   - "Ganho" no CRM desconta reversão posterior e pares duplicados (mesmo contato, mesmo valor, dois lançamentos).
   - Tráfego só depois de filtrar `user_agent` de bot e referrer de rede interna. Tracker que escreve parâmetro na URL faz crawler contar cada URL como página nova.
   - Contador bruto não é fato. Antes de afirmar "N sem resposta", abra a amostra e classifique: sem mensagem, autoresponder de terceiros, menção de story, ruído. Reporte só o que sobrou.
   - Antes de concluir que um dado "não existe", confirme QUAL coluna carrega o dado. Campo vazio na tabela errada não é ausência de informação.
   - Superlativo ("melhor mês", "recorde", "mais barato") exige consulta ao histórico completo e, em comparativo, os dois lados na mesma tela.
   - Base imatura (censura à direita): ou compara só a parte madura, ou não projeta. Se não dá para projetar, o slide diz por que não dá.
   - Correção prometida roda dry-run antes. "X sessões serão reclassificadas" só entra no slide depois do dry-run confirmar X.

4. **Escreva o roteiro em títulos.** Um slide, uma afirmação. Se o título não é uma frase que você defende sozinho, o slide não existe. Título aponta problema e caminho, nunca culpado — vai para diretoria e vira ata.

5. **Monte o HTML.** Um arquivo, um `<style>`, sprite SVG inline de ícones no topo do `<body>`, um `<section>` por slide/página, comentário numerado antes de cada um. Use só as classes do contrato. Largura de `.fill` é a proporção real do valor, nunca decorativa. Rótulo que não cabe na barra vai em `.fill.sm > span`. Funil de 6+ linhas usa `.funil.compacto`.

6. **Escreva `.nota` e `.metod` em cada slide de número.** `.nota` dá o contexto que impede leitura errada; `.metod` diz o que o número NÃO é, o que ficou de fora e onde a base é frágil. Rótulo ambíguo vira cobrança: escreva o que o número É ("total projetado, 82% já realizado"), não o que ele parece.

7. **Reconcilie o deck inteiro.** Todo número que aparece em mais de um slide vem da mesma apuração — reconfira a cada edição, principalmente capa contra slide interno. Referência cruzada por título ("ver *A mídia paga*"), nunca por número de slide. Se inseriu ou removeu slide, reconfira todos os `.pageno` e todas as referências.

8. **RENDERIZE E OLHE ANTES DE PUBLICAR.** Não julgue o deck lendo o HTML. Fatie o arquivo em N arquivos de um slide (`<head>` + uma `<section>`), tire um print de cada e abra os PNGs:

   ```bash
   CH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
   "$CH" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
     --window-size=1920,1080 --screenshot=saida.png "file:///caminho/um-slide.html"
   ```

   Print do documento inteiro sai errado — sempre um por slide. Confira: conteúdo que passa por baixo do `.sfoot` (`position:absolute; bottom:56px`) fica escondido pelo `overflow:hidden` do `.slide` — é a causa nº 1 de slide quebrado. Confira também o contador: `grep -c '<section' arquivo.html`. Nunca conte por `class="slide"` exato, que não pega a capa (`class="slide cover"`).

9. **Gere o PDF.** Abra no Chrome, imprimir, Salvar como PDF, margens nulas, gráficos de fundo ligados. O `@page` do modo A já define 1920x1080; o do modo B define 338mm x 190mm e desliga o snap.

10. **Publique e confira o que está no ar.**

    ```bash
    cp deck.html deploy/index.html && cd deploy && vercel deploy --prod --yes
    ```

    Depois compare `shasum -a 256` do arquivo local com o do `curl` da URL publicada. Publicar sem conferir não conta como publicado.

## Inegociáveis

- Apure antes de escrever. Slide sem folha de apuração não vai para o arquivo.
- Receita é do PMS. CRM é esforço comercial. Nunca somados.
- Número repetido em dois slides vem da mesma apuração. Capa inclusive.
- Superlativo só com histórico completo consultado. Comparativo só com os dois lados na tela.
- Tráfego só com filtro de bot aplicado. Contagem bruta de conversa só com amostra aberta.
- Base imatura não projeta — e o slide explica por quê.
- Barra de `.fill` é proporcional ao valor. Sempre.
- Todo slide de número carrega `.nota`; todo slide com recorte discutível carrega `.metod`.
- Título aponta o problema e o caminho, nunca o culpado.
- Referência cruzada por título, nunca por número de slide.
- Filtro de tenant em toda consulta de deck de marca única.
- Renderize e olhe cada PNG antes de publicar. Confira o hash depois de publicar.
- Nenhuma classe fora do contrato. Nenhum renomear.

## O que cada referência responde

Leia sob demanda; não carregue tudo de uma vez.

| Arquivo | Pergunta que responde |
|---|---|
| `references/componentes.md` | Qual é o contrato fechado de classes dos dois modos, com a anatomia, o exemplo e a armadilha de cada componente? E quantos cabem por slide? |
| `references/sistema-visual.md` | Quais são os tokens, a escala tipográfica, o significado de cada cor, a grade e o contraste? Como troco a marca sem quebrar nada? |
| `references/integridade-dados.md` | Como confiro que o número está certo antes de escrever — fonte, coluna, recorte, dedup, maturidade de safra, bot, tenant, reversão? |
| `references/build-e-publicacao.md` | Como gero PNG por slide, PDF 16:9, publico na Vercel e provo que o que está no ar é o meu arquivo? |
| `assets/deck-relatorio.html` | O esqueleto do modo relatório, com um slide de exemplo por componente. Comece copiando este arquivo. |
| `assets/deck-narrativa.html` | O esqueleto do modo narrativa, com o sprite de ícones completo e uma página de exemplo por bloco. |
| `scripts/check-deck.py` | O que rodo **antes** de publicar: número repetido, superlativo sem lastro, projeção sem ressalva, referência cruzada frágil. |
| `scripts/shots.py` | O que gera a pasta de PNGs, um por slide, em 2x. |

## Como instalar

```bash
git clone https://github.com/marcotuliobrz/skill-apresentacao-mkt.git \
  ~/.claude/skills/apresentacao-mkt
```

Requisitos: Google Chrome (para PNG e PDF) e Python 3 — os scripts usam só a biblioteca padrão.

A skill fica disponível em qualquer projeto. Invoque com `/apresentacao-mkt`, ou peça direto: "monta o relatório mensal de julho", "faz um deck de entregas para o cliente". Diga o modo se já souber (`relatorio` ou `narrativa`); se não disser, a skill escolhe pelo passo 2 e confirma antes de montar.
