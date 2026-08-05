#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Confere um deck HTML ANTES de publicar. Python 3, só stdlib.

Este script não julga estética: ele procura os erros que já foram para a
diretoria e voltaram como cobrança em ata. Rode sempre antes de gerar PNG,
PDF ou de subir para a Vercel.

USO
    python3 scripts/check-deck.py deck.html
    python3 scripts/check-deck.py deck.html --max-repetidos 80
    python3 scripts/check-deck.py deck.html --sem-cor > conferencia.txt
    python3 scripts/check-deck.py --help

O QUE ELE CONFERE
    1. Estrutura       — conta <section> e exige .sfoot com fonte em cada slide.
    2. Numeração       — lista "ver slide 09" e .pageno fora de ordem (quebram
                         quando você insere um slide no meio).
    3. Repetidos       — valores em R$, % e multiplicadores (5,4×) que aparecem
                         em mais de um slide, para você checar divergência.
    4. Superlativos    — "melhor", "maior", "recorde": exigem lastro no histórico.
                         Comparativos exigem os dois lados na mesma tela.
    5. Projeção        — "projetado", "deve chegar" sem .metod no mesmo slide.
    6. Densidade       — slide com mais de 3 números e sem .nota nem .metod.

SAÍDA E CÓDIGO DE RETORNO
    Relatório agrupado por severidade. ERRO bloqueia (exit 1), AVISO é leitura
    obrigatória mas não bloqueia (exit 0).

O QUE ELE NÃO FAZ
    Não abre navegador: não mede se o conteúdo passou por baixo do .sfoot
    (overflow:hidden come o excesso em silêncio). Para isso, tire o PNG e olhe.
    Não valida o dado na fonte: ele aponta onde você precisa reconferir.
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser

# ---------------------------------------------------------------------------
# Vocabulário: escreva os termos SEM acento — o texto é normalizado antes.
# ---------------------------------------------------------------------------

# Superlativos: exigem consulta ao histórico completo antes de ir para o slide.
SUPERLATIVOS = [
    "melhor", "melhores", "pior", "piores", "maior", "maiores", "menor",
    "menores", "recorde", "recordes", "primeiro", "primeira", "unico", "unica",
    "inedito", "inedita", "nunca visto", "nunca vista", "jamais", "lider",
    "lideranca", "maximo", "maxima", "minimo", "minima", "historico",
    "sem precedentes", "de todos os tempos", "disparou", "explodiu",
    "o mais", "a mais alta", "o mais alto",
]

# Comparativos: só valem com os dois lados na mesma tela.
COMPARATIVOS = [
    "mais barato", "mais caro", "mais eficiente", "mais rentavel",
    "mais rapido", "melhor que", "pior que", "superior a", "inferior a",
    "acima de", "abaixo de", "supera", "ultrapassa",
]

# Projeção: número que ainda não aconteceu. Sem .metod no slide, não sai.
PROJECAO = [
    "projetado", "projetada", "projetados", "projetadas", "projecao",
    "projetamos", "projetar", "estimado", "estimada", "estimados",
    "estimativa", "previsto", "prevista", "previsao", "esperado", "esperada",
    "expectativa", "deve chegar", "deve fechar", "deve atingir", "vai chegar",
    "vai fechar", "vai atingir", "tendencia de", "no ritmo atual",
    "se mantiver", "anualizado", "run rate", "forecast", "extrapolando",
    "potencial de receita",
]

# Referência cruzada por número: quebra assim que você insere um slide.
# Exige a palavra "slide", ou um verbo de remissão antes de "página" — senão
# "Navegaram mais de uma página 11.825" viraria referência cruzada.
RE_REF_CRUZADA = re.compile(
    r"(?:(?:ver|vide|veja|conforme|vd\.?)\s+)?slides?\s*(?:n[.o]?\s*)?\d{1,3}(?![\d.,])"
    r"|(?:ver|vide|veja|conforme)\s+(?:a\s+)?(?:paginas?|pags?\.?)\s*\d{1,3}(?![\d.,])",
    re.I,
)

# Negação: "Fato, não estimativa" não é projeção. A negação tem que estar COLADA
# no termo — o texto do slide é a junção de vários elementos, e uma janela larga
# pegaria o "não" do título anterior e engoliria uma projeção de verdade.
RE_NEGACAO = re.compile(r"(?:\bnao\b|\bsem\b|\bnada de\b|\bnenhuma?\b)[\s,]{0,3}$")

# Dinheiro, percentual e multiplicador. Rodam sobre o texto já normalizado.
RE_DINHEIRO = re.compile(
    r"R\$\s*(\d[\d.,]*)\s*"
    r"(milhoes|milhao|milhar|mil|mi|bilhoes|bilhao|bi|k)?(?![\w])",
    re.I,
)
RE_PERCENTUAL = re.compile(r"(?<![\d.,])(\d+(?:[.,]\d+)?)\s*%")
RE_MULTIPLICADOR = re.compile(r"(?<![\d.,\w])(\d+(?:[.,]\d+)?)\s*[x×](?![\w])")
RE_QUALQUER_NUMERO = re.compile(r"(?<![\w.,])\d[\d.,]*")
RE_ANO = re.compile(r"^(?:19|20)\d{2}$")

SUFIXO_ESCALA = {
    "mil": 1_000, "milhar": 1_000, "k": 1_000,
    "mi": 1_000_000, "milhao": 1_000_000, "milhoes": 1_000_000,
    "bi": 1_000_000_000, "bilhao": 1_000_000_000, "bilhoes": 1_000_000_000,
}

# Tradução 1 para 1: preserva o tamanho da string, então os índices das buscas
# continuam valendo no texto original (é o que permite mostrar o trecho certo).
TABELA_ACENTOS = str.maketrans(
    "áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ",
    "aaaaaeeeeiiiiooooouuuucnAAAAAEEEEIIIIOOOOOUUUUCN",
)

# Tags que nunca fecham: se entrarem na pilha, desalinham todo o resto.
TAGS_VAZIAS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
    "param", "source", "track", "wbr", "path", "circle", "rect", "line",
    "polygon", "polyline", "ellipse", "stop", "use", "image",
}


def sem_acento(texto):
    """Devolve o texto minúsculo e sem acento, do mesmo tamanho do original."""
    convertido = texto.translate(TABELA_ACENTOS).lower()
    # .lower() muda o tamanho em casos exóticos; se mudar, o mapa de índices
    # deixa de valer e é melhor abrir mão do trecho original.
    return convertido if len(convertido) == len(texto) else texto.translate(TABELA_ACENTOS)


def compacta(texto):
    """Colapsa quebras de linha e espaços repetidos numa linha só."""
    return re.sub(r"\s+", " ", texto).strip()


def numero_br(bruto):
    """Converte '2.583.242' ou '2,58' no float correspondente."""
    limpo = bruto.strip().replace(" ", "").replace("\xa0", "")
    if "," in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    else:
        partes = limpo.split(".")
        # 362.884 é milhar; 2.58 (raro em pt-BR) é decimal.
        if len(partes) > 1 and all(len(p) == 3 for p in partes[1:]):
            limpo = "".join(partes)
    try:
        return float(limpo)
    except ValueError:
        return None


def negado(texto_normalizado, inicio):
    """Diz se o termo encontrado vem logo depois de uma negação."""
    return bool(RE_NEGACAO.search(texto_normalizado[max(0, inicio - 40):inicio]))


def casas_decimais(bruto):
    """Quantas casas depois da vírgula o número traz escrito."""
    if "," in bruto:
        return len(bruto.split(",")[-1])
    return 0


def e_arredondamento(a, bruto_a, b, bruto_b):
    """Diz se um número é só a versão arredondada do outro (5,43 vs 5,4)."""
    ca, cb = casas_decimais(bruto_a), casas_decimais(bruto_b)
    if ca == cb:
        return False
    preciso, casas_curtas = (a, cb) if ca > cb else (b, ca)
    curto = b if ca > cb else a
    return abs(round(preciso, casas_curtas) - curto) < 1e-9


def trecho(texto, inicio, fim, folga=46):
    """Recorta o entorno do achado para o relatório."""
    ini = max(0, inicio - folga)
    fim2 = min(len(texto), fim + folga)
    corte = compacta(texto[ini:fim2])
    return ("…" if ini > 0 else "") + corte + ("…" if fim2 < len(texto) else "")


# ---------------------------------------------------------------------------
# Leitura do HTML
# ---------------------------------------------------------------------------

class Slide:
    """Um <section> do deck, com o texto separado por região."""

    def __init__(self, ordem, linha, classes):
        self.ordem = ordem
        self.linha = linha
        self.classes = classes           # classes do próprio <section>
        self.classes_internas = set()    # todas as classes vistas dentro dele
        self.partes_texto = []           # tudo, inclusive shead e sfoot
        self.partes_corpo = []           # sem shead e sem sfoot
        self.partes_pageno = []
        self.partes_sfoot = []
        self.partes_titulo = []

    @property
    def texto(self):
        return compacta(" ".join(self.partes_texto))

    @property
    def corpo(self):
        return compacta(" ".join(self.partes_corpo))

    @property
    def pageno(self):
        return compacta(" ".join(self.partes_pageno))

    @property
    def sfoot(self):
        return compacta(" ".join(self.partes_sfoot))

    @property
    def titulo(self):
        bruto = compacta(" ".join(self.partes_titulo))
        if not bruto:
            bruto = compacta(self.corpo)[:60]
        return (bruto[:58] + "…") if len(bruto) > 58 else bruto or "(sem título)"

    @property
    def rotulo(self):
        return f'#{self.ordem:02d} "{self.titulo}"'


class LeitorDeck(HTMLParser):
    """Percorre o HTML e devolve os slides com o texto já separado.

    Ignora <style> e <script> — senão width:60% viraria percentual de negócio.
    Atributos style="" não entram: HTMLParser só entrega texto, não atributo.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides = []
        self.slide = None
        self.profundidade_section = 0
        self.pilha = []          # [(tag, [contadores que este elemento abriu])]
        self.ignorar = 0         # dentro de style/script
        self.fora_do_corpo = 0   # dentro de shead ou sfoot
        self.cap_pageno = 0
        self.cap_sfoot = 0
        self.cap_titulo = 0

    # -- utilidades internas ------------------------------------------------
    @staticmethod
    def _classes(attrs):
        for nome, valor in attrs:
            if nome == "class" and valor:
                return set(valor.split())
        return set()

    def _registra_classes(self, classes):
        if self.slide is not None:
            self.slide.classes_internas |= classes

    def _abre_capturas(self, tag, classes):
        """Liga os contadores conforme a classe do elemento que está abrindo."""
        abertos = []
        if "shead" in classes or "sfoot" in classes:
            self.fora_do_corpo += 1
            abertos.append("fora_do_corpo")
        if "pageno" in classes:
            self.cap_pageno += 1
            abertos.append("cap_pageno")
        if "sfoot" in classes:
            self.cap_sfoot += 1
            abertos.append("cap_sfoot")
        # .title do modo A; h1 da capa; h2 do modo B.
        if "title" in classes or "capa__title" in classes or tag in ("h1", "h2"):
            self.cap_titulo += 1
            abertos.append("cap_titulo")
        return abertos

    def _fecha_capturas(self, abertos):
        for nome in abertos:
            setattr(self, nome, max(0, getattr(self, nome) - 1))

    # -- eventos do parser --------------------------------------------------
    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self.ignorar += 1
            return
        classes = self._classes(attrs)

        if tag == "section":
            if self.profundidade_section == 0:
                self.slide = Slide(len(self.slides) + 1, self.getpos()[0], classes)
                self.slides.append(self.slide)
            self.profundidade_section += 1

        self._registra_classes(classes)
        if tag in TAGS_VAZIAS:
            return
        self.pilha.append((tag, self._abre_capturas(tag, classes)))

    def handle_startendtag(self, tag, attrs):
        # Auto-fechada (<use/>, <br/>): só anota a classe, não mexe na pilha.
        if tag not in ("style", "script"):
            self._registra_classes(self._classes(attrs))

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.ignorar = max(0, self.ignorar - 1)
            return

        # Desempilha até achar a tag; HTML mal fechado não pode travar a leitura.
        for i in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[i][0] == tag:
                for _, abertos in self.pilha[i:]:
                    self._fecha_capturas(abertos)
                del self.pilha[i:]
                break

        if tag == "section" and self.profundidade_section > 0:
            self.profundidade_section -= 1
            if self.profundidade_section == 0:
                self.slide = None

    def handle_data(self, data):
        if self.ignorar or self.slide is None or not data.strip():
            return
        self.slide.partes_texto.append(data)
        if not self.fora_do_corpo:
            self.slide.partes_corpo.append(data)
        if self.cap_pageno:
            self.slide.partes_pageno.append(data)
        if self.cap_sfoot:
            self.slide.partes_sfoot.append(data)
        if self.cap_titulo and not self.fora_do_corpo:
            self.slide.partes_titulo.append(data)


# ---------------------------------------------------------------------------
# Achados
# ---------------------------------------------------------------------------

class Achado:
    def __init__(self, severidade, codigo, alvo, mensagem, linhas=None):
        self.severidade = severidade      # "ERRO" ou "AVISO"
        self.codigo = codigo
        self.alvo = alvo                  # rótulo do slide ou "deck"
        self.mensagem = mensagem
        self.linhas = linhas or []        # detalhes indentados


# ---------------------------------------------------------------------------
# 1. Estrutura: contagem de <section> e fonte no rodapé
# ---------------------------------------------------------------------------

def tem_numero(texto):
    """True se o slide mostra número que alguém pode cobrar depois.

    Dinheiro, percentual e multiplicador contam sempre. Número solto só conta se
    tiver 3+ dígitos ou separador — assim "01" de numeração de item e ano solto
    (2026) não obrigam o slide a declarar fonte.
    """
    if RE_DINHEIRO.search(texto) or RE_PERCENTUAL.search(texto) or RE_MULTIPLICADOR.search(texto):
        return True
    for m in RE_QUALQUER_NUMERO.finditer(texto):
        bruto = m.group(0)
        if RE_ANO.match(bruto):
            continue
        if len(re.sub(r"\D", "", bruto)) >= 3 or "." in bruto or "," in bruto:
            return True
    return False


def check_estrutura(slides, achados):
    for s in slides:
        e_capa = "cover" in s.classes or "page--capa" in s.classes
        e_fim = "page--fim" in s.classes
        tem_sfoot = "sfoot" in s.classes_internas

        # A regra é "todo slide QUE MOSTRA NÚMERO carrega a fonte". Capa, sumário e
        # fechamento não mostram número — cobrar fonte deles é ruído.
        if not tem_numero(s.corpo):
            continue

        # O .sfoot é a convenção do modo relatorio. O modo narrativa não tem rodapé
        # fixo: declara a fonte numa .nota ou no .frame__note. Qualquer um dos três vale.
        texto_todo = sem_acento(s.texto)
        declara_fonte = "fonte" in texto_todo or "apurado em" in texto_todo

        if not tem_sfoot and not declara_fonte:
            achados.append(Achado(
                "ERRO", "sem-fonte", s.rotulo,
                "Slide com número e sem fonte declarada.",
                ["Todo slide que mostra número carrega a fonte: sistema, tabela e data "
                 "de apuração. No modo relatorio, no .sfoot; no modo narrativa, numa "
                 ".nota ou no .frame__note. Slide sem fonte não vai para a diretoria.",
                 f"linha {s.linha}"],
            ))
            continue

        if not tem_sfoot:
            continue

        texto_rodape = sem_acento(s.sfoot)
        if "fonte" not in texto_rodape and not (e_capa or e_fim):
            achados.append(Achado(
                "AVISO", "fonte-vaga", s.rotulo,
                "O .sfoot existe mas não nomeia a fonte.",
                [f'rodapé atual: "{s.sfoot}"',
                 "Escreva de onde veio: sistema · tabela · data de apuração."],
            ))


def check_dispersao_apuracao(slides, achados):
    """Datas de apuração diferentes no mesmo deck = números de dias diferentes."""
    datas = defaultdict(list)
    for s in slides:
        for achado in re.findall(r"apurado em\s*(\d{2}/\d{2}/\d{4})", sem_acento(s.sfoot)):
            datas[achado].append(s.rotulo)
    if len(datas) > 1:
        achados.append(Achado(
            "AVISO", "apuracao-mista", "deck",
            f"Há {len(datas)} datas de apuração diferentes no mesmo deck.",
            [f"{data} → {', '.join(alvos)}" for data, alvos in sorted(datas.items())]
            + ["Base viva muda de valor a cada dia. Ou apura tudo no mesmo dia, "
               "ou escreve no slide por que as datas diferem."],
        ))


# ---------------------------------------------------------------------------
# 2. Referência cruzada por número e numeração do .pageno
# ---------------------------------------------------------------------------

def check_referencias(slides, achados):
    for s in slides:
        alvo = sem_acento(s.texto)
        encontrados = []
        for m in RE_REF_CRUZADA.finditer(alvo):
            encontrados.append(trecho(s.texto, m.start(), m.end()))
        if encontrados:
            achados.append(Achado(
                "AVISO", "ref-por-numero", s.rotulo,
                f"{len(encontrados)} referência(s) cruzada(s) por número.",
                encontrados[:4]
                + ["Referencie pelo TÍTULO do slide. Referência por número aponta "
                   "para o slide errado assim que alguém insere um slide antes."],
            ))

    # .pageno fora de ordem é o sintoma clássico de slide inserido no meio.
    for s in slides:
        rotulo_pagina = s.pageno
        if not rotulo_pagina or not re.fullmatch(r"0*\d{1,3}", rotulo_pagina):
            continue  # capa costuma trazer texto, não número
        if int(rotulo_pagina) != s.ordem:
            achados.append(Achado(
                "AVISO", "pageno-fora-de-ordem", s.rotulo,
                f'.pageno diz "{rotulo_pagina}" mas o slide é o {s.ordem}º do arquivo.',
                ["Renumere e reconfira toda referência cruzada do deck."],
            ))


# ---------------------------------------------------------------------------
# 3. Números repetidos em mais de um slide
# ---------------------------------------------------------------------------

def coleta_numeros(slide):
    """Extrai (tipo, valor_canônico, texto_como_escrito) do corpo do slide.

    A busca roda no texto normalizado, mas o rótulo sai do texto ORIGINAL:
    sem_acento() preserva o tamanho, então os índices valem nos dois.
    """
    original = slide.corpo
    texto = sem_acento(original)
    achados = []

    def bruto(m):
        return compacta(original[m.start():m.end()])

    for m in RE_DINHEIRO.finditer(texto):
        valor = numero_br(m.group(1))
        if valor is None:
            continue
        escala = SUFIXO_ESCALA.get((m.group(2) or "").lower(), 1)
        achados.append(("R$", valor * escala, bruto(m)))

    for m in RE_PERCENTUAL.finditer(texto):
        valor = numero_br(m.group(1))
        if valor is not None:
            achados.append(("%", valor, bruto(m)))

    for m in RE_MULTIPLICADOR.finditer(texto):
        valor = numero_br(m.group(1))
        if valor is not None:
            achados.append(("×", valor, bruto(m)))

    return achados


def check_numeros_repetidos(slides, achados, limite):
    grupos = defaultdict(lambda: {"slides": [], "brutos": []})
    multiplicadores = defaultdict(lambda: {"slides": set(), "brutos": set()})

    for s in slides:
        vistos_no_slide = set()
        for tipo, valor, bruto in coleta_numeros(s):
            chave = (tipo, round(valor, 4))
            grupo = grupos[chave]
            grupo["brutos"].append(bruto)
            if chave not in vistos_no_slide:
                grupo["slides"].append(s.rotulo)
                vistos_no_slide.add(chave)
            if tipo == "×":
                multiplicadores[round(valor, 4)]["slides"].add(s.rotulo)
                multiplicadores[round(valor, 4)]["brutos"].add(bruto)

    repetidos = [(k, v) for k, v in grupos.items() if len(v["slides"]) > 1]
    repetidos.sort(key=lambda kv: (-len(kv[1]["slides"]), kv[0][0], -kv[0][1]))

    if repetidos:
        detalhes = []
        for (tipo, valor), dados in repetidos[:limite]:
            formas = sorted(set(dados["brutos"]))
            rotulo = formas[0] if len(formas) == 1 else " / ".join(formas)
            marca = "  ⟵ formas diferentes do mesmo valor" if len(formas) > 1 else ""
            detalhes.append(f"{rotulo}{marca}")
            detalhes.append(f"    em: {', '.join(dados['slides'])}")
        if len(repetidos) > limite:
            detalhes.append(f"(+{len(repetidos) - limite} não listados — use --max-repetidos)")
        achados.append(Achado(
            "AVISO", "numero-repetido", "deck",
            f"{len(repetidos)} valor(es) aparecem em mais de um slide.",
            detalhes + ["Todo número repetido tem que vir da MESMA apuração. "
                        "Reconfira a cada edição — a capa é a que mais envelhece."],
        ))

    # Multiplicadores quase iguais: o caso ROAS 5,9× na capa e 5,7× por dentro.
    valores = sorted(multiplicadores)
    for i, a in enumerate(valores):
        for b in valores[i + 1:]:
            if a <= 0 or abs(b - a) / max(a, b) > 0.10:
                continue
            bruto_a = sorted(multiplicadores[a]["brutos"])[0]
            bruto_b = sorted(multiplicadores[b]["brutos"])[0]
            if e_arredondamento(a, bruto_a, b, bruto_b):
                continue
            # Se os dois valores dividem algum slide, a comparação está explícita
            # na tela — é a prática certa. Vira conferência, não bloqueio.
            juntos = multiplicadores[a]["slides"] & multiplicadores[b]["slides"]
            achados.append(Achado(
                "AVISO" if juntos else "ERRO", "multiplicador-divergente", "deck",
                f"Multiplicadores próximos e diferentes: {bruto_a} e {bruto_b}.",
                [f"{bruto_a} em: {', '.join(sorted(multiplicadores[a]['slides']))}",
                 f"{bruto_b} em: {', '.join(sorted(multiplicadores[b]['slides']))}"]
                + ([f"Aparecem juntos em {', '.join(sorted(juntos))} — confirme que a "
                    f"distinção entre os dois está escrita ali."] if juntos else
                   ["Nunca aparecem no mesmo slide. Se for a mesma métrica, um dos dois "
                    "está velho — a capa é a que mais envelhece. Se forem métricas "
                    "diferentes, ponha os dois lados na mesma tela e diga qual é qual."]),
            ))


# ---------------------------------------------------------------------------
# 4. Superlativos e comparativos
# ---------------------------------------------------------------------------

def padrao_termos(termos):
    partes = [r"\s+".join(re.escape(p) for p in t.split()) for t in termos]
    partes.sort(key=len, reverse=True)
    return re.compile(r"(?<![\w])(" + "|".join(partes) + r")(?![\w])")


RE_SUPERLATIVOS = padrao_termos(SUPERLATIVOS)
RE_COMPARATIVOS = padrao_termos(COMPARATIVOS)
RE_PROJECAO = padrao_termos(PROJECAO)


def check_superlativos(slides, achados):
    for s in slides:
        alvo = sem_acento(s.texto)

        supers, trechos = [], []
        for m in RE_SUPERLATIVOS.finditer(alvo):
            supers.append(m.group(1))
            trechos.append(trecho(s.texto, m.start(), m.end()))
        if supers:
            achados.append(Achado(
                "AVISO", "superlativo", s.rotulo,
                "Superlativo sem lastro visível: " + ", ".join(sorted(set(supers))) + ".",
                trechos[:3]
                + ["Consulte o histórico COMPLETO antes de afirmar. Se o superlativo "
                   "se sustenta, ponha o 2º colocado no mesmo slide."],
            ))

        comps, trechos_c = [], []
        for m in RE_COMPARATIVOS.finditer(alvo):
            comps.append(m.group(1))
            trechos_c.append(trecho(s.texto, m.start(), m.end()))
        if comps:
            achados.append(Achado(
                "AVISO", "comparativo", s.rotulo,
                "Comparativo: " + ", ".join(sorted(set(comps))) + ".",
                trechos_c[:3]
                + ["Comparação exige os DOIS lados na mesma tela, com o mesmo recorte "
                   "e a mesma unidade."],
            ))


# ---------------------------------------------------------------------------
# 5. Projeção sem .metod no mesmo slide
# ---------------------------------------------------------------------------

def check_projecao(slides, achados):
    for s in slides:
        alvo = sem_acento(s.texto)
        termos, trechos = [], []
        for m in RE_PROJECAO.finditer(alvo):
            if negado(alvo, m.start()):
                continue  # "Fato, não estimativa" está afirmando o contrário
            termos.append(m.group(1))
            trechos.append(trecho(s.texto, m.start(), m.end()))
        if not termos:
            continue
        if "metod" in s.classes_internas:
            continue
        achados.append(Achado(
            "ERRO", "projecao-sem-metodo", s.rotulo,
            "Projeta (" + ", ".join(sorted(set(termos))) + ") e não traz .metod.",
            trechos[:3]
            + ["Base imatura infla ou desinfla conforme o dia da apuração (censura "
               "à direita). Ou compara só a parte madura, ou não projeta — e escreve "
               "no .metod POR QUE não dá para projetar.",
               "Diga também qual % da safra já completou a janela."],
        ))


# ---------------------------------------------------------------------------
# 6. Densidade de números sem componente de honestidade
# ---------------------------------------------------------------------------

def conta_numeros(slide):
    """Conta números do corpo, descartando anos (2025, 2026) e o .pageno."""
    total = 0
    for bruto in RE_QUALQUER_NUMERO.findall(sem_acento(slide.corpo)):
        if RE_ANO.fullmatch(bruto.strip(".,")):
            continue
        total += 1
    return total


def check_densidade(slides, achados):
    for s in slides:
        if "nota" in s.classes_internas or "metod" in s.classes_internas:
            continue
        quantos = conta_numeros(s)
        if quantos <= 3:
            continue
        if "cover" in s.classes or "page--capa" in s.classes:
            # A capa quase nunca leva .nota — mas é onde o número velho sobrevive.
            achados.append(Achado(
                "AVISO", "numeros-na-capa", s.rotulo,
                f"{quantos} números na capa.",
                ["Todo número da capa é cópia de outro slide. Reconfira um por um "
                 "contra a apuração final — a capa é editada primeiro e revisada por último."],
            ))
            continue
        achados.append(Achado(
            "AVISO", "numero-sem-leitura", s.rotulo,
            f"{quantos} números no corpo e nenhum .nota nem .metod.",
            ["Contador bruto não é fato. Diga o que o número É, o que ele não é, "
             "e o que foi excluído da contagem.",
             "Rótulo ambíguo vira cobrança em ata."],
        ))


# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------

class Cores:
    def __init__(self, ligado):
        self.erro = "\033[1;31m" if ligado else ""
        self.aviso = "\033[1;33m" if ligado else ""
        self.ok = "\033[1;32m" if ligado else ""
        self.fraco = "\033[2m" if ligado else ""
        self.forte = "\033[1m" if ligado else ""
        self.zero = "\033[0m" if ligado else ""


def imprime_relatorio(caminho, slides, achados, cores, texto_bruto):
    erros = [a for a in achados if a.severidade == "ERRO"]
    avisos = [a for a in achados if a.severidade == "AVISO"]

    print(f"{cores.forte}CONFERÊNCIA DO DECK{cores.zero}  {caminho}")
    print("=" * 78)

    # Contagem: cover usa class="slide cover", então grep por class="slide"
    # exato NÃO pega a capa. Mostre os dois números para ninguém se enganar.
    total_section = texto_bruto.count("<section")
    exatos = len(re.findall(r'class="slide"', texto_bruto))
    print(f"  <section> no arquivo ......... {total_section}")
    print(f"  slides lidos pelo parser ..... {len(slides)}")
    print(f'  class="slide" exato .......... {exatos}'
          f'{cores.fraco}  (grep exato não pega a capa: class="slide cover"){cores.zero}')
    com_sfoot = sum(1 for s in slides if "sfoot" in s.classes_internas)
    com_nota = sum(1 for s in slides
                   if {"nota", "metod"} & s.classes_internas)
    print(f"  com .sfoot ................... {com_sfoot}/{len(slides)}")
    print(f"  com .nota ou .metod .......... {com_nota}/{len(slides)}")
    print()

    for titulo, grupo, cor in (("ERRO", erros, cores.erro), ("AVISO", avisos, cores.aviso)):
        if not grupo:
            continue
        print(f"{cor}{titulo} ({len(grupo)}){cores.zero}")
        print("-" * 78)
        for a in grupo:
            print(f"  {cor}{titulo}{cores.zero} [{a.codigo}] {cores.forte}{a.alvo}{cores.zero}")
            print(f"    {a.mensagem}")
            for linha in a.linhas:
                print(f"      {cores.fraco}{linha}{cores.zero}")
            print()

    if not achados:
        print(f"{cores.ok}Nada a corrigir. Ainda assim: tire o PNG e olhe cada slide "
              f"antes de publicar.{cores.zero}")
        print()

    print("=" * 78)
    if erros:
        print(f"{cores.erro}{len(erros)} ERRO(S){cores.zero} e {len(avisos)} aviso(s). "
              f"Não publique antes de resolver os erros.")
    else:
        print(f"{cores.ok}Sem erros{cores.zero} e {len(avisos)} aviso(s). "
              f"Leia os avisos: eles são conferência manual, não ruído.")
    print(f"{cores.fraco}Depois de publicar, compare o hash: "
          f"shasum -a 256 do arquivo local x do curl da URL no ar.{cores.zero}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check-deck.py",
        description="Confere um deck HTML antes de publicar: fonte no rodapé, "
                    "referência cruzada, número repetido, superlativo, projeção "
                    "sem metodologia e slide de número sem leitura.",
        epilog="Exemplos:\n"
               "  python3 scripts/check-deck.py deck.html\n"
               "  python3 scripts/check-deck.py deck.html --max-repetidos 80\n"
               "  python3 scripts/check-deck.py deck.html --sem-cor > conferencia.txt\n"
               "\nExit code: 1 se houver ERRO, 0 se só houver AVISO.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("arquivo", help="caminho do deck HTML")
    parser.add_argument("--max-repetidos", type=int, default=40, metavar="N",
                        help="quantos valores repetidos listar (padrão: 40)")
    parser.add_argument("--sem-cor", action="store_true",
                        help="desliga o ANSI (para redirecionar para arquivo)")
    args = parser.parse_args(argv)

    caminho = os.path.abspath(os.path.expanduser(args.arquivo))
    if not os.path.isfile(caminho):
        print(f"ERRO: arquivo não encontrado: {caminho}", file=sys.stderr)
        return 2

    with open(caminho, "r", encoding="utf-8", errors="replace") as fh:
        bruto = fh.read()

    leitor = LeitorDeck()
    leitor.feed(bruto)
    leitor.close()
    slides = leitor.slides

    cores = Cores(not args.sem_cor and sys.stdout.isatty())

    if not slides:
        print(f"{cores.erro}ERRO{cores.zero} [sem-slides] {caminho}")
        print("    Nenhum <section> encontrado. O deck usa <section> por slide "
              "nos dois modos (relatorio e narrativa).")
        return 1

    achados = []
    check_estrutura(slides, achados)
    check_dispersao_apuracao(slides, achados)
    check_referencias(slides, achados)
    check_numeros_repetidos(slides, achados, max(1, args.max_repetidos))
    check_superlativos(slides, achados)
    check_projecao(slides, achados)
    check_densidade(slides, achados)

    imprime_relatorio(caminho, slides, achados, cores, bruto)
    return 1 if any(a.severidade == "ERRO" for a in achados) else 0


if __name__ == "__main__":
    sys.exit(main())
