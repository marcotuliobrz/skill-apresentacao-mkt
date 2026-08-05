#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shots.py — um PNG por slide de um deck HTML, via Chrome headless.

POR QUE FATIAR
    Um print do documento inteiro sai errado: no modo "relatorio" o Chrome captura
    só a primeira dobra da página, e no modo "narrativa" o scroll-snap embaralha o
    que aparece. A técnica que funciona é outra: quebrar o HTML em N arquivos de
    um <section> cada (mantendo <head>, sprite de ícones e CSS intactos) e tirar
    um print de cada arquivo.

USO
    python3 scripts/shots.py deck.html shots/
    python3 scripts/shots.py deck.html shots/ --escala 2
    python3 scripts/shots.py deck.html shots/ --largura 1920 --altura 1080
    python3 scripts/shots.py deck.html shots/ --apenas 1,3-5 --paralelo 1
    python3 scripts/shots.py --help

SAÍDA
    Arquivos numerados e com slug do título do slide, na ordem do documento:
        01-o-mes-de-julho-em-numeros.png
        03-de-onde-vem-as-vendas.png
    O título sai de .title, senão de <h2>, senão de <h1>. Sem título: slide-NN.
    Acentos viram ASCII no slug (relatório -> relatorio).

O QUE O SCRIPT INJETA EM CADA FATIA
    - CSS que esconde o HUD do modo narrativa (.hud-logo/.hud-counter/.hud-controls),
      porque HUD é navegação de tela, não conteúdo de slide. Use --com-hud pra manter.
    - CSS que força .reveal visível: fatia isolada não rola, e slide em branco por
      animação parada é falha silenciosa. Use --respeitar-reveal pra manter a animação.
    - scroll-snap desligado no html: irrelevante numa página de um slide só.
    Os scripts do fim do <body> ficam de fora por padrão (--com-scripts liga).

DETALHES QUE IMPORTAM
    - As fatias temporárias nascem NA MESMA PASTA do deck (prefixo .shots-tmp-) pra
      que caminho relativo de imagem e de asset continue resolvendo. São apagadas no
      fim; --manter-temp preserva pra depuração.
    - Se o deck busca fonte em fonts.googleapis.com, o print precisa de rede. Sem
      rede, sai com fonte de sistema e o layout muda. O script avisa.
    - Cada print é conferido: arquivo existe, tem bytes e bate com a resolução
      esperada (largura x escala). Qualquer falha derruba o código de saída pra 1.

REQUISITOS
    Python 3.8+ (só stdlib) e Google Chrome / Chromium instalado.
"""

import argparse
import concurrent.futures
import html as _html
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# Localizar o Chrome
# ---------------------------------------------------------------------------

# Ordem de preferência por sistema. Chromium serve; Brave e Edge são o último recurso.
CANDIDATOS_MACOS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]

CANDIDATOS_LINUX = [
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/snap/bin/chromium",
    "microsoft-edge",
    "brave-browser",
]


def detectar_so(escolha):
    """Resolve o valor de --so. 'auto' olha para sys.platform."""
    if escolha != "auto":
        return escolha
    if sys.platform == "darwin":
        return "macos"
    if sys.platform.startswith("linux"):
        return "linux"
    # Windows e outros não estão homologados aqui: exige --chrome explícito.
    return "outro"


def achar_chrome(so, explicito):
    """Devolve o caminho do executável do Chrome ou None."""
    if explicito:
        caminho = Path(explicito).expanduser()
        if caminho.is_file() and os.access(caminho, os.X_OK):
            return str(caminho)
        achado = shutil.which(explicito)
        return achado  # None se nem no PATH existir

    candidatos = CANDIDATOS_MACOS if so == "macos" else CANDIDATOS_LINUX
    for cand in candidatos:
        if cand.startswith("/"):
            if os.path.isfile(cand) and os.access(cand, os.X_OK):
                return cand
        else:
            achado = shutil.which(cand)
            if achado:
                return achado
    return None


# ---------------------------------------------------------------------------
# Fatiar o HTML
# ---------------------------------------------------------------------------

RE_BODY_ABRE = re.compile(r"<body\b[^>]*>", re.IGNORECASE)
RE_BODY_FECHA = re.compile(r"</body\s*>", re.IGNORECASE)
RE_TOKEN_SECTION = re.compile(r"<section\b|</section\s*>", re.IGNORECASE)


def limites_das_secoes(corpo):
    """Lista de (inicio, fim) de cada <section> de primeiro nível.

    Conta profundidade em vez de usar regex guloso: se um dia um <section>
    aninhar dentro de outro, a fatia continua saindo inteira.
    """
    limites = []
    nivel = 0
    inicio = 0
    for m in RE_TOKEN_SECTION.finditer(corpo):
        if m.group(0).lower().startswith("<section"):
            if nivel == 0:
                inicio = m.start()
            nivel += 1
        elif nivel > 0:
            nivel -= 1
            if nivel == 0:
                limites.append((inicio, m.end()))
    return limites


def separar_deck(texto):
    """Quebra o deck em (cabeca, preambulo, secoes, rodape, fecho).

    cabeca    -> doctype + <head> + a tag <body> aberta (CSS, fontes, @page)
    preambulo -> o que vem no body ANTES do primeiro <section>: sprite de ícones
                 (<symbol id="i-*">) e HUD. Vai em toda fatia, senão <use> quebra.
    secoes    -> lista com o HTML de cada slide
    rodape    -> o que vem depois do último </section> (scripts de navegação)
    fecho     -> </body></html>
    """
    m_body = RE_BODY_ABRE.search(texto)
    if m_body:
        corte = m_body.end()
    else:
        # Deck sem <body> explícito: tudo antes da primeira seção vira cabeça.
        primeira = re.search(r"<section\b", texto, re.IGNORECASE)
        corte = primeira.start() if primeira else len(texto)

    cabeca = texto[:corte]
    corpo = texto[corte:]

    limites = limites_das_secoes(corpo)
    if not limites:
        return cabeca, "", [], "", "\n</body>\n</html>\n"

    preambulo = corpo[: limites[0][0]]
    secoes = [corpo[a:b] for a, b in limites]
    cauda = corpo[limites[-1][1]:]

    m_fecha = RE_BODY_FECHA.search(cauda)
    if m_fecha:
        rodape = cauda[: m_fecha.start()]
        fecho = cauda[m_fecha.start():]
    else:
        rodape = cauda
        fecho = "\n</body>\n</html>\n"

    return cabeca, preambulo, secoes, rodape, fecho


# ---------------------------------------------------------------------------
# Título e slug
# ---------------------------------------------------------------------------

# class="title" — o \b evita casar com capa__title (o _ é caractere de palavra).
RE_CLASSE_TITLE = re.compile(
    r"<(\w+)[^>]*\bclass=[\"'][^\"']*\btitle\b[^\"']*[\"'][^>]*>(.*?)</\1\s*>",
    re.IGNORECASE | re.DOTALL,
)
RE_H2 = re.compile(r"<h2\b[^>]*>(.*?)</h2\s*>", re.IGNORECASE | re.DOTALL)
RE_H1 = re.compile(r"<h1\b[^>]*>(.*?)</h1\s*>", re.IGNORECASE | re.DOTALL)


def texto_puro(fragmento):
    """Tira tags, resolve entidades e colapsa espaço. <br> vira espaço."""
    t = re.sub(r"<br\s*/?>", " ", fragmento, flags=re.IGNORECASE)
    t = re.sub(r"<[^>]+>", " ", t)
    t = _html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def titulo_do_slide(secao):
    """Título do slide: .title, senão <h2>, senão <h1>. None se não achar."""
    for regex, grupo in ((RE_CLASSE_TITLE, 2), (RE_H2, 1), (RE_H1, 1)):
        m = regex.search(secao)
        if m:
            titulo = texto_puro(m.group(grupo))
            if titulo:
                return titulo
    return None


def gerar_slug(texto, limite=58):
    """Slug ASCII: sem diacrítico, minúsculo, hífen entre palavras."""
    if not texto:
        return ""
    # Casos que o NFKD não decompõe sozinho.
    trocas = {"ß": "ss", "æ": "ae", "œ": "oe", "ø": "o", "đ": "d", "ł": "l", "ª": "a", "º": "o", "&": " e "}
    for de, para in trocas.items():
        texto = texto.replace(de, para).replace(de.upper(), para)

    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))

    s = re.sub(r"[^a-zA-Z0-9]+", "-", sem_acento).lower()
    s = re.sub(r"-{2,}", "-", s).strip("-")

    if len(s) > limite:
        corte = s[:limite]
        # Não parte palavra ao meio se der pra evitar.
        if "-" in corte and s[limite: limite + 1] != "-":
            corte = corte.rsplit("-", 1)[0]
        s = corte.strip("-")
    return s


# ---------------------------------------------------------------------------
# Montagem da fatia
# ---------------------------------------------------------------------------

def css_do_fatiador(com_hud, respeitar_reveal):
    """CSS injetado no topo do body de cada fatia. Só mexe em classes do contrato."""
    regras = [
        "html{scroll-snap-type:none !important;scroll-behavior:auto !important}",
        "html,body{margin:0 !important;padding:0 !important;overflow:hidden !important}",
    ]
    if not com_hud:
        # HUD é navegação de tela; não entra em PNG de slide.
        regras.append(".hud-logo,.hud-counter,.hud-controls{display:none !important}")
    if not respeitar_reveal:
        # Fatia isolada não rola: sem isto o .reveal pode ficar invisível no print.
        regras.append(
            ".reveal{opacity:1 !important;transform:none !important;"
            "animation:none !important;visibility:visible !important}"
        )
    return "<style id=\"shots-fatiador\">" + "".join(regras) + "</style>\n"


def montar_fatia(cabeca, preambulo, secao, rodape, fecho, css, com_scripts):
    """Documento HTML completo com um único slide."""
    partes = [cabeca, "\n", css, preambulo, secao, "\n"]
    if com_scripts and rodape.strip():
        partes.append(rodape)
    partes.append(fecho)
    return "".join(partes)


# ---------------------------------------------------------------------------
# Print
# ---------------------------------------------------------------------------

def dimensoes_png(caminho):
    """Lê largura/altura do IHDR. None se não for PNG válido."""
    try:
        with open(caminho, "rb") as f:
            cabecalho = f.read(24)
    except OSError:
        return None
    if len(cabecalho) < 24 or cabecalho[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return (
        int.from_bytes(cabecalho[16:20], "big"),
        int.from_bytes(cabecalho[20:24], "big"),
    )


def montar_comando(chrome, modo_headless, args, destino, url):
    """Linha de comando do Chrome headless para um print.

    NÃO passe --user-data-dir aqui. Medido no Chrome 150 (macOS): com perfil
    próprio o processo tira o print e não termina — trava até o timeout (45s+);
    sem ele, o mesmo print sai em ~2,5s. O headless moderno já cria perfil
    descartável sozinho, então convivem várias instâncias em paralelo.
    """
    cmd = [
        chrome,
        modo_headless,
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--mute-audio",
        "--allow-file-access-from-files",
        f"--force-device-scale-factor={args.escala}",
        f"--window-size={args.largura},{args.altura}",
        # Segura o desenho até o compositor terminar e dá tempo de fonte/CSS carregar.
        "--run-all-compositor-stages-before-draw",
        f"--virtual-time-budget={args.espera}",
        f"--screenshot={destino}",
    ]
    if args.sem_sandbox:
        cmd.insert(2, "--no-sandbox")
    cmd.append(url)
    return cmd


def tirar_print(chrome, args, arquivo_fatia, destino):
    """Roda o Chrome. Devolve (ok, detalhe, segundos, dimensoes)."""
    url = Path(arquivo_fatia).resolve().as_uri()  # percent-encode resolve pasta com espaço
    esperado = (args.largura * args.escala, args.altura * args.escala)

    # --headless é o que está homologado nesta máquina; --headless=new é o plano B
    # para builds recentes que removeram o headless antigo.
    tentativas = ["--headless", "--headless=new"]
    ultimo_erro = "falha desconhecida"
    inicio = time.time()

    for indice, modo in enumerate(tentativas):
        if os.path.exists(destino):
            os.remove(destino)
        cmd = montar_comando(chrome, modo, args, destino, url)
        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=args.timeout,
            )
        except subprocess.TimeoutExpired:
            ultimo_erro = f"chrome estourou o timeout de {args.timeout}s"
            continue
        except OSError as e:
            return False, f"não deu para executar o chrome: {e}", time.time() - inicio, None

        if proc.returncode != 0:
            erro = (proc.stderr or b"").decode("utf-8", "replace").strip().splitlines()
            detalhe = erro[-1][:160] if erro else ""
            ultimo_erro = f"chrome saiu com código {proc.returncode}" + (f" — {detalhe}" if detalhe else "")
            continue

        if not os.path.exists(destino) or os.path.getsize(destino) < 512:
            ultimo_erro = "chrome terminou sem gravar PNG utilizável"
            continue

        dims = dimensoes_png(destino)
        if dims is None:
            ultimo_erro = "arquivo gerado não é um PNG válido"
            continue
        if dims != esperado:
            # Não é fatal: avisa e segue, porque pode ser display scaling do sistema.
            return (
                True,
                f"atenção: saiu {dims[0]}x{dims[1]}, esperado {esperado[0]}x{esperado[1]}",
                time.time() - inicio,
                dims,
            )

        aviso = "" if indice == 0 else "usou --headless=new"
        return True, aviso, time.time() - inicio, dims

    return False, ultimo_erro, time.time() - inicio, None


# ---------------------------------------------------------------------------
# Seleção de slides e formatação
# ---------------------------------------------------------------------------

def parse_selecao(spec, total):
    """'1,3-5' -> [1,3,4,5]. Vazio -> todos."""
    if not spec:
        return list(range(1, total + 1))
    escolhidos = set()
    for parte in spec.split(","):
        parte = parte.strip()
        if not parte:
            continue
        try:
            if "-" in parte:
                a_txt, b_txt = parte.split("-", 1)
                a, b = int(a_txt), int(b_txt)
                if a > b:
                    a, b = b, a
                escolhidos.update(range(a, b + 1))
            else:
                escolhidos.add(int(parte))
        except ValueError:
            raise ValueError(f"trecho inválido em --apenas: {parte!r}")
    fora = sorted(n for n in escolhidos if n < 1 or n > total)
    if fora:
        amostra = ", ".join(str(n) for n in fora[:6])
        if len(fora) > 6:
            amostra += f" ... (+{len(fora) - 6})"
        raise ValueError(f"--apenas cita slide fora da faixa 1..{total}: {amostra}")
    return sorted(escolhidos)


def formatar_tamanho(bytes_):
    if bytes_ >= 1024 * 1024:
        return f"{bytes_ / (1024 * 1024):.1f} MB"
    return f"{bytes_ / 1024:.0f} KB"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def construir_parser():
    p = argparse.ArgumentParser(
        prog="shots.py",
        description="Gera um PNG por slide de um deck HTML usando Chrome headless.",
        epilog=(
            "exemplos:\n"
            "  python3 scripts/shots.py deck.html shots/\n"
            "  python3 scripts/shots.py deck.html shots/ --escala 2 --espera 4000\n"
            "  python3 scripts/shots.py deck.html shots/ --apenas 1,3-5\n"
            "  python3 scripts/shots.py deck.html shots/ --so linux --sem-sandbox\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("deck", help="caminho do deck HTML")
    p.add_argument("saida", help="pasta onde gravar os PNG (criada se faltar)")
    p.add_argument("--escala", type=int, default=2,
                   help="fator de densidade do print; 2 = 3840x2160 num slide 1920x1080 (padrão: 2)")
    p.add_argument("--largura", type=int, default=1920, help="largura da janela em px (padrão: 1920)")
    p.add_argument("--altura", type=int, default=1080, help="altura da janela em px (padrão: 1080)")
    p.add_argument("--so", choices=["auto", "macos", "linux"], default="auto",
                   help="onde procurar o Chrome (padrão: auto)")
    p.add_argument("--chrome", default=None,
                   help="caminho explícito do executável do Chrome; ignora a detecção")
    p.add_argument("--apenas", default=None,
                   help="recorte de slides, ex.: 1,3-5 (padrão: todos)")
    p.add_argument("--prefixo", default="",
                   help="prefixo do nome do arquivo, ex.: julho- (padrão: nenhum)")
    p.add_argument("--espera", type=int, default=3000,
                   help="orçamento de tempo virtual em ms para fonte e CSS carregarem (padrão: 3000)")
    p.add_argument("--timeout", type=int, default=60,
                   help="tempo máximo por print, em segundos (padrão: 60)")
    p.add_argument("--paralelo", type=int, default=3,
                   help="quantos prints ao mesmo tempo (padrão: 3)")
    p.add_argument("--com-hud", action="store_true",
                   help="mantém .hud-logo/.hud-counter/.hud-controls visíveis no print")
    p.add_argument("--respeitar-reveal", action="store_true",
                   help="não força .reveal visível; use se quiser o estado animado original")
    p.add_argument("--com-scripts", action="store_true",
                   help="mantém os scripts do fim do body em cada fatia")
    p.add_argument("--manter-temp", action="store_true",
                   help="não apaga os arquivos .shots-tmp-*.html gerados ao lado do deck")
    p.add_argument("--sem-sandbox", action="store_true",
                   help="passa --no-sandbox ao Chrome (necessário em container/root no Linux)")
    return p


def main():
    args = construir_parser().parse_args()

    # --- validação de entrada -------------------------------------------------
    deck = Path(args.deck).expanduser().resolve()
    if not deck.is_file():
        print(f"erro: deck não encontrado: {deck}", file=sys.stderr)
        return 2
    if args.escala < 1:
        print("erro: --escala precisa ser >= 1", file=sys.stderr)
        return 2
    if args.largura < 1 or args.altura < 1:
        print("erro: --largura e --altura precisam ser > 0", file=sys.stderr)
        return 2
    if args.paralelo < 1:
        print("erro: --paralelo precisa ser >= 1", file=sys.stderr)
        return 2

    saida = Path(args.saida).expanduser().resolve()
    saida.mkdir(parents=True, exist_ok=True)

    so = detectar_so(args.so)
    chrome = achar_chrome(so, args.chrome)
    if not chrome:
        print(
            "erro: Chrome não encontrado.\n"
            "  macOS: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome\n"
            "  Linux: google-chrome, google-chrome-stable ou chromium\n"
            "  Ou passe --chrome /caminho/do/executavel",
            file=sys.stderr,
        )
        return 2

    # --- fatiar ---------------------------------------------------------------
    texto = deck.read_text(encoding="utf-8", errors="replace")
    cabeca, preambulo, secoes, rodape, fecho = separar_deck(texto)
    total = len(secoes)
    if total == 0:
        print(f"erro: nenhum <section> encontrado em {deck}", file=sys.stderr)
        return 2

    try:
        selecionados = parse_selecao(args.apenas, total)
    except ValueError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 2
    if not selecionados:
        print("erro: --apenas não selecionou nenhum slide", file=sys.stderr)
        return 2

    largura_num = max(2, len(str(total)))
    css = css_do_fatiador(args.com_hud, args.respeitar_reveal)

    # --- cabeçalho de execução -----------------------------------------------
    print(f"deck ....... {deck}  ({total} seções)")
    print(f"saída ...... {saida}")
    print(f"chrome ..... {chrome}")
    print(
        f"print ...... janela {args.largura}x{args.altura} · escala {args.escala}"
        f" → {args.largura * args.escala}x{args.altura * args.escala} px"
    )
    if len(selecionados) != total:
        print(f"recorte .... {len(selecionados)} de {total} slides ({args.apenas})")
    if "fonts.googleapis.com" in texto:
        print("aviso ...... o deck busca fonte em fonts.googleapis.com; sem rede o print sai com fonte de sistema")
    print("")

    # --- montar as fatias ao lado do deck (mantém caminho relativo de asset) ---
    pasta_deck = deck.parent
    fatias = []          # (numero, arquivo_fatia, destino_png)
    temporarios = []

    try:
        for numero in selecionados:
            secao = secoes[numero - 1]
            titulo = titulo_do_slide(secao)
            slug = gerar_slug(titulo) if titulo else ""
            if not slug:
                slug = "slide-" + str(numero).zfill(largura_num)
            nome = f"{args.prefixo}{str(numero).zfill(largura_num)}-{slug}.png"

            arquivo_fatia = pasta_deck / f".shots-tmp-{str(numero).zfill(largura_num)}.html"
            arquivo_fatia.write_text(
                montar_fatia(cabeca, preambulo, secao, rodape, fecho, css, args.com_scripts),
                encoding="utf-8",
            )
            temporarios.append(arquivo_fatia)
            fatias.append((numero, arquivo_fatia, saida / nome))

        # --- rodar os prints --------------------------------------------------
        falhas = []
        feitos = 0
        contador = 0

        def trabalho(item):
            numero, arquivo_fatia, destino = item
            ok, detalhe, segundos, dims = tirar_print(chrome, args, arquivo_fatia, destino)
            return numero, destino, ok, detalhe, segundos, dims

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.paralelo) as pool:
            futuros = [pool.submit(trabalho, item) for item in fatias]
            for futuro in concurrent.futures.as_completed(futuros):
                numero, destino, ok, detalhe, segundos, dims = futuro.result()
                contador += 1
                marca = f"[{str(contador).rjust(len(str(len(fatias))))}/{len(fatias)}]"
                if ok:
                    feitos += 1
                    tamanho = formatar_tamanho(os.path.getsize(destino))
                    dim_txt = f"{dims[0]}x{dims[1]}" if dims else "?"
                    extra = f"  ({detalhe})" if detalhe else ""
                    print(f"{marca} ok    {destino.name}  {dim_txt}  {tamanho}  {segundos:.1f}s{extra}")
                else:
                    falhas.append((numero, destino.name, detalhe))
                    print(f"{marca} FALHA {destino.name} — {detalhe}", file=sys.stderr)

        # --- resumo -----------------------------------------------------------
        print("")
        if falhas:
            print(f"{feitos} prints ok, {len(falhas)} falha(s) em {saida}", file=sys.stderr)
            for numero, nome, detalhe in sorted(falhas):
                print(f"  slide {numero}: {nome} — {detalhe}", file=sys.stderr)
            return 1

        print(f"{feitos} prints ok em {saida}")
        return 0

    finally:
        # Limpa as fatias temporárias, dê certo ou não.
        if args.manter_temp:
            print(f"temp ....... {len(temporarios)} arquivo(s) .shots-tmp-*.html mantidos em {pasta_deck}")
        else:
            for arquivo in temporarios:
                try:
                    arquivo.unlink()
                except OSError:
                    pass


if __name__ == "__main__":
    sys.exit(main())
