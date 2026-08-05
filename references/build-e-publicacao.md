# Build e publicação

Como sair do HTML e chegar em PNG, PDF e URL pública — e como provar que o que está no ar é o
arquivo que você editou. Comandos verificados em macOS com Google Chrome instalado.

Convenções usadas aqui:

```bash
DECK="$HOME/decks/relatorio-julho.html"   # o arquivo do deck
SAIDA="$HOME/decks/build"                 # tudo que for gerado cai aqui
CH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
mkdir -p "$SAIDA"
```

Se o caminho tiver espaço (iCloud Drive tem), sempre entre aspas. Sempre caminho absoluto.

---

## 1. Antes de qualquer build

Rode esta conferência. Ela custa 20 segundos e evita reimprimir tudo.

```bash
# quantos slides o deck tem
grep -oE '<section[^>]*class="[^"]*\bslide\b' "$DECK" | wc -l    # modo A
grep -oE '<section[^>]*class="[^"]*\bpage\b'  "$DECK" | wc -l    # modo B

# a numeração de .pageno bate com a ordem dos slides?
grep -oE '<div class="pageno">[^<]*' "$DECK" | sed 's/.*>//'
```

A segunda conferência existe porque inserir slide no meio desalinha `.pageno` e quebra qualquer
frase do tipo "ver slide 09". Referência cruzada se faz **por título**, nunca por número. Se
algum número aparecer no texto, reconfira todos depois de inserir ou remover slide.

---

## 2. Pré-visualizar local

Abrir o arquivo direto já resolve 90% dos casos:

```bash
open -a "Google Chrome" "$DECK"
```

Se o deck carregar imagem, fonte local ou qualquer `fetch`, `file://` esbarra em CORS. Nesse
caso suba um servidor:

```bash
cd "$(dirname "$DECK")" && python3 -m http.server 8899
# depois: open "http://localhost:8899/$(basename "$DECK")"
```

**Modo A** (`.slide`, 1920×1080): dê zoom para 50% no Chrome (`Cmd -`) e role. Cada slide precisa
ocupar exatamente uma tela; se aparecer faixa preta ou conteúdo cortado no rodapé, vá para a
seção "Quando o slide estoura".

**Modo B** (`.page`, rolável): confira com o teclado — setas, PageUp/PageDown, espaço, Home, End.
O snap tem que parar exatamente no topo de cada `.page`. Confira também se o HUD (`.hud-logo`,
`.hud-counter`, `.hud-controls`) inverte de cor ao entrar numa `.page--dark`; se não inverter, o
`IntersectionObserver` que liga `body.on-dark` não está pegando aquela seção.

---

## 3. PNG por slide

### Por que fatiar o HTML

O Chrome headless fotografa **a viewport**, não o documento. Screenshot do deck inteiro devolve
1920×1080 — só o primeiro slide. Os outros 17 simplesmente não existem no arquivo. Verificado:

```bash
"$CH" --headless --disable-gpu --hide-scrollbars \
  --window-size=1920,1080 --screenshot=/tmp/inteiro.png "file://$DECK"
sips -g pixelWidth -g pixelHeight /tmp/inteiro.png   # 1920 x 1080, com 18 slides no arquivo
```

E forçar `--window-size=1920,19440` para "caber tudo" também não serve: sai uma tira única,
sem corte entre slides, com o `.slide::before` (os halos radiais) esticado errado, e nada disso
vira apresentação.

A técnica correta é **um arquivo HTML por slide**: repetir o `<head>` inteiro (tokens, `@page`,
fontes, os dois blocos `<style>`) e colocar uma única `<section>` no `<body>`. Cada arquivo vira
um documento de 1080px de altura, que cabe na viewport, e o print sai exato.

### O fatiador

Já vem pronto na skill, em `scripts/fatiar-slides.py`. O `scripts/shots.py` fatia internamente
e é o que você usa no dia a dia; o fatiador avulso serve para inspecionar um slide isolado.

```bash
python3 scripts/fatiar-slides.py deck.html /tmp/fatias slide   # modo relatorio
python3 scripts/fatiar-slides.py deck.html /tmp/fatias page    # modo narrativa
```

O regex casa `class="slide"` **e** `class="slide cover"` — a capa não pode ficar de fora.

### Fatiar e fotografar

```bash
python3 scripts/fatiar-slides.py "$DECK" "$SAIDA/fatias" slide   # modo A
# python3 scripts/fatiar-slides.py "$DECK" "$SAIDA/fatias" page  # modo B

mkdir -p "$SAIDA/png"
for f in "$SAIDA"/fatias/slide-*.html; do
  n="$(basename "$f" .html)"
  "$CH" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
    --virtual-time-budget=3000 \
    --window-size=1920,1080 --screenshot="$SAIDA/png/$n.png" "file://$f" 2>/dev/null
done

ls "$SAIDA/png" | wc -l
sips -g pixelWidth -g pixelHeight "$SAIDA/png/slide-01.png"   # esperado: 3840 x 2160
```

`--force-device-scale-factor=2` é o que dá 3840×2160 (2x). Sem ele sai 1920×1080 e o texto fica
sujo em telão e em slide impresso.

O Chrome headless cospe `ERROR:` no stderr (allocator, task_policy, install webapp). É ruído do
macOS, não é falha — por isso o `2>/dev/null`. O que importa é o PNG existir com o tamanho certo.

Duas conferências obrigatórias:

1. `ls | wc -l` tem que bater com a contagem de slides da seção 1.
2. Abra a pasta em modo galeria (`open "$SAIDA/png"`, visualização em ícones grandes) e **olhe**.
   Slide truncado, número faltando e barra do `.funil` desproporcional aparecem em 5 segundos.

No modo B, cada `.page` tem `min-height:100dvh`, então 1920×1080 funciona igual. Se alguma `.page`
tiver conteúdo mais alto que a viewport (comum em `.spec-list` longa ou `.ledger` com muitas
linhas), o print corta o excesso — trate como estouro, seção 6.

---

## 4. PDF 16:9

### Rota manual (a que vale para entregar)

```bash
open -a "Google Chrome" "$DECK"
```

No Chrome: `Cmd P` → Destino **Salvar como PDF** → Mais definições → **Margens: Nenhuma** →
**Gráficos de fundo: ligado** → Salvar em `$SAIDA/`.

"Gráficos de fundo" desligado é o erro clássico: o `--bg #050507` some, o deck escuro sai em papel
branco com texto branco. Fica ilegível e ninguém percebe até a reunião.

O tamanho vem do `@page` do próprio deck — modo A define `1920px 1080px`; modo B define
`338mm 190mm` e desliga o snap.

### Rota automatizável

```bash
"$CH" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$SAIDA/deck.pdf" "file://$DECK" 2>/dev/null
```

Verificado: 18 slides → 18 páginas, MediaBox `0 0 1440 810` pt, que é exatamente 1920×1080 px.
`--no-pdf-header-footer` tira o cabeçalho com URL e data que o Chrome insere por padrão.

### Conferir o PDF

```bash
python3 - "$SAIDA/deck.pdf" <<'PY'
import re, sys
d = open(sys.argv[1], 'rb').read()
print("paginas :", len(re.findall(rb'/Type\s*/Page(?![s])', d)))
print("mediabox:", set(re.findall(rb'/MediaBox\s*\[([^\]]*)\]', d)))
PY
```

O `(?![s])` importa: contar `/Type /Page` sem ele conta junto os nós `/Type /Pages` da árvore e
devolve número inflado (num teste, 22 em vez de 18).

**Páginas > slides significa que algum slide vazou para a página seguinte.** Não conserte no PDF:
volte ao HTML, ache o slide e vá para a seção 6.

---

## 5. Publicar na Vercel

```bash
mkdir -p "$SAIDA/deploy"
cp "$DECK" "$SAIDA/deploy/index.html"
cd "$SAIDA/deploy" && vercel deploy --prod --yes
```

Copie para `index.html` — sem isso a URL raiz devolve 404 e você entrega um link quebrado.

Se o deck usa imagem local (print de tela dentro de `.frame`, logo em `.hud-logo`), copie os
assets junto mantendo os caminhos relativos, ou embuta tudo em `data:` URI antes de publicar. O
deck publicado tem que ser autossuficiente: quem abre está fora da sua máquina.

---

## 6. Conferir o publicado por hash

Publicar não é conferir. Deploy que subiu a versão anterior é indistinguível de deploy bem-sucedido
até alguém abrir o link.

```bash
URL="https://seu-deck.vercel.app"

LOCAL=$(shasum -a 256 "$DECK" | awk '{print $1}')
REMOTO=$(curl -s --compressed "$URL" | shasum -a 256 | awk '{print $1}')

echo "local : $LOCAL"
echo "remoto: $REMOTO"
[ "$LOCAL" = "$REMOTO" ] && echo "OK — no ar é o arquivo local" || echo "DIVERGENTE — republique"
```

Se divergir, nesta ordem: confirme que copiou para `index.html`; rode o deploy de novo; espere e
repita o `curl` (cache de borda); só então investigue o conteúdo com
`curl -s "$URL" | diff - "$DECK" | head -20`.

Depois disso, abra a URL no navegador e passe o olho. O hash prova que o byte é o mesmo — não
prova que a fonte carregou nem que o slide 11 está inteiro.

---

## 7. Entregar a pasta de PNGs

```bash
ditto -c -k --sequesterRsrc --keepParent "$SAIDA/png" "$SAIDA/deck-png.zip"
ls -lh "$SAIDA/deck-png.zip"
```

`ditto` é o compactador nativo do macOS e preserva os nomes com acento; o `zip` genérico costuma
sujar o pacote com `__MACOSX`. Para descompactar do outro lado, `ditto -x -k arquivo.zip pasta`.

Nomeie os arquivos na ordem de exibição (`slide-01.png`… `slide-18.png`, com zero à esquerda),
senão qualquer visualizador ordena 1, 10, 11, 2. O fatiador já faz isso.

Checklist de entrega:

- [ ] contagem de PNGs = contagem de slides
- [ ] `slide-01.png` é a capa (`.slide.cover` / `.page--capa`)
- [ ] PDF com o mesmo número de páginas
- [ ] URL publicada com hash conferido
- [ ] você abriu a galeria e olhou cada slide

---

## 8. Quando o slide estoura

Sintomas: rodapé sumido, texto cortado na base, PDF com mais páginas que slides, o `.sfoot`
sobrepondo o conteúdo.

A causa é quase sempre a mesma: `.slide` tem `overflow:hidden` e `.sfoot` é
`position:absolute; bottom:56px`. Conteúdo que passa da linha do `.sfoot` **não empurra nada** —
some. O slide continua com 1080px de altura e parece certo no HTML.

### Diagnosticar: renderizar, olhar, medir

**Renderizar e olhar** é o primeiro passo, sempre. Gere o PNG só daquela fatia:

```bash
"$CH" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=1920,1080 --screenshot="$SAIDA/debug.png" \
  "file://$SAIDA/fatias/slide-11.html" 2>/dev/null
open "$SAIDA/debug.png"
```

**Medir** dá o culpado com nome e número. Injete o medidor na fatia e leia o DOM:

```bash
cat > "$SAIDA/medir.js" <<'JS'
<script>
window.addEventListener('load',()=>{
  const s = document.querySelector('.slide') || document.querySelector('.page');
  const f = s.querySelector('.sfoot');
  const limite = f ? f.getBoundingClientRect().top : s.getBoundingClientRect().bottom;
  const estouros = [...s.children]
    .filter(el => !el.classList.contains('sfoot'))
    .map(el => ({ c: el.className || el.tagName, b: Math.round(el.getBoundingClientRect().bottom) }))
    .filter(o => o.b > limite - 8);
  const d = document.createElement('div'); d.id = 'MEDIDA';
  d.textContent = 'altura=' + s.scrollHeight + ' limite=' + Math.round(limite)
                + ' estouros=' + JSON.stringify(estouros);
  document.body.appendChild(d);
});
</script>
JS

python3 - "$SAIDA" <<'PY'
import pathlib, sys
S  = pathlib.Path(sys.argv[1])
js = (S / "medir.js").read_text(encoding="utf-8")
for f in sorted((S / "fatias").glob("slide-*.html")):
    h = f.read_text(encoding="utf-8")
    (S / "fatias" / ("medir-" + f.name)).write_text(h.replace("</body>", js + "</body>"), encoding="utf-8")
print("medidores gerados")
PY

for f in "$SAIDA"/fatias/medir-slide-*.html; do
  printf '%s  ' "$(basename "$f")"
  "$CH" --headless --disable-gpu --virtual-time-budget=3000 --window-size=1920,1080 \
    --dump-dom "file://$f" 2>/dev/null | grep -o 'id="MEDIDA">[^<]*' | sed 's/id="MEDIDA">//'
  echo
done
```

Leitura do resultado:

- `altura=1080 limite=1005 estouros=[]` → slide são.
- `altura=1106 limite=1005 estouros=[{"c":"nota","b":1010}]` → estourou 26px, e o culpado é a
  `.nota`. Você agora sabe **qual componente** encolher, sem chutar.

Apague os `medir-*.html` e o `medir.js` antes de gerar os PNGs finais — eles não podem virar slide.

### As três saídas

Escolha nesta ordem. A primeira preserva a informação; a última é a mais honesta quando não dá.

**1. Compactar o componente.** Existe variante pronta para isso — use, não invente CSS novo:

| Situação | Troca |
|---|---|
| 6–7 linhas no funil | `.funil` → `.funil.compacto` |
| barra estreita com rótulo espremido | `.fill` → `.fill.sm` (rótulo vai para fora da barra) |
| 4 cartões de número apertados | `.stats` → `.stats.tres` ou `.stats.dois` |
| lista de 2 colunas com item longo | `.lista` → `.lista.um` |
| linha de destaque muito longa | encurte o `small` dentro de `.fl` / `.fv`, não o rótulo principal |

No modo B o equivalente é mover metade dos `.spec-row` (ou dos `.ledger__row`) para uma segunda
`.page` do mesmo capítulo, mantendo o mesmo `.eyebrow`.

**2. Remover linha.** Se depois de compactar ainda estoura, o slide tem mais dados do que cabe.
Corte a linha que menos decide: a de menor valor no `.funil`, o item de menor `.val` na `.lista`,
o 4º `.stat` quando os três primeiros já contam a história. Só não corte silenciosamente — se a
linha removida muda o total, diga o total na `.nota`.

**3. Fundir `.nota` + `.metod`.** Quando os dois blocos de honestidade aparecem no mesmo slide,
eles competem por 200px de altura e são o estouro mais comum. Funda num único `.metod`, com o
`.h` como título e o texto da `.nota` incorporado. Você perde um bloco visual e não perde nenhuma
ressalva — que é exatamente o trade certo.

**O que não fazer:** reduzir `font-size` no `style=` inline do slide. Resolve aquele slide e quebra
a consistência tipográfica do deck inteiro — dois slides com o mesmo componente em tamanhos
diferentes, e ninguém lembra por quê três semanas depois.

---

## 9. Problemas conhecidos

### Gradiente em texto não sobrevive ao PDF

`.cover h1 .grad` e `.cover h1 .dim` usam `background-clip:text` com `color:transparent`. Na tela
funciona. No PDF, o leitor pinta a **caixa** inteira e o título vira um retângulo colorido sólido
por cima do texto — ou some.

Solução: fallback sólido em `@media print`, que já está no deck de referência:

```css
@media print{
  .cover h1 .dim{background:none !important;-webkit-background-clip:border-box !important;
    background-clip:border-box !important;color:#dcdaee !important;-webkit-text-fill-color:#dcdaee !important}
  .cover h1 .grad{background:none !important;-webkit-background-clip:border-box !important;
    background-clip:border-box !important;color:#34d399 !important;-webkit-text-fill-color:#34d399 !important}
}
```

`-webkit-text-fill-color` é obrigatório: sem ele o `color` não vence o `transparent` anterior.

Consequência esperada: **PNG e PDF ficam diferentes na capa** — PNG usa mídia `screen` (gradiente),
PDF usa `print` (sólido). É intencional. Escolha para o fallback a primeira parada do gradiente,
para a diferença ser mínima. Qualquer novo texto com `background-clip:text` precisa entrar nesse
bloco `@media print` no mesmo commit — senão a próxima capa sai quebrada.

### Contagem de slides erra com classe composta

`grep -c 'class="slide"'` devolve 17 num deck de 18 slides. A capa é `class="slide cover"` e não
casa com a string exata — some da contagem, e é justamente ela que você mais precisa conferir.

```bash
grep -c '<section' "$DECK"                                        # 18 — serve se só houver slides
grep -c 'class="slide"' "$DECK"                                   # 17 — ERRADO, perde a capa
grep -oE '<section[^>]*class="[^"]*\bslide\b' "$DECK" | wc -l     # 18 — correto
```

Use sempre a terceira forma. `\bslide\b` casa com `slide` e com `slide cover`. Mesma armadilha no
modo B: `.page--capa`, `.page--dark`, `.page--alt` e `.page--fim` são todas classes compostas.

### Fonte do Google não carrega offline

O deck carrega Sora e Plus Jakarta Sans de `fonts.googleapis.com`. Sem rede — avião, sala de
reunião com Wi-Fi ruim, máquina de outra pessoa — o navegador cai no próximo item da pilha.

Por isso a pilha nunca pode terminar na fonte remota:

```css
--sans: "Plus Jakarta Sans", system-ui, sans-serif;
--display: "Sora", system-ui, sans-serif;
```

Com `system-ui` o deck degrada para San Francisco: continua legível, mas as métricas mudam — o
`.title` ganha 1 a 2 linhas e slides que estavam no limite estouram. Ou seja: **teste de fonte
ausente é teste de estouro**. Para simular, gere os PNGs com a rede desligada e compare.

Se o deck for apresentado offline, embuta as fontes em `data:` URI base64 dentro de um `@font-face`
no próprio HTML. Fica mais pesado e fica independente. Vale sempre a pena quando o deck vai para
diretoria.

O mesmo raciocínio vale para o sprite de ícones: `<symbol id="i-*">` inline no HTML funciona
offline; ícone puxado de URL externa não. Nunca troque o sprite por link externo.
