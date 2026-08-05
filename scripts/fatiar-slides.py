#!/usr/bin/env python3
"""Fatia um deck em 1 arquivo HTML por slide, repetindo o <head> inteiro em cada fatia.

Por que fatiar: um print do documento inteiro sai errado. O Chrome fotografa a
viewport, não o documento — vem só o primeiro slide. E forçar uma janela altíssima
para "caber tudo" produz uma tira única, sem corte entre slides e com os halos do
`.slide::before` esticados. Um arquivo por slide resolve: cada fatia é um documento
de uma tela só, e o print sai exato.

O `scripts/shots.py` já fatia internamente — use ele para gerar a pasta de PNGs.
Este script existe para o caso avulso: inspecionar um slide isolado, mandar uma
fatia para alguém, ou gerar um PDF de um slide só.

uso:
    python3 fatiar-slides.py deck.html pasta-saida [classe]

    classe: 'slide' (modo relatorio, padrão) ou 'page' (modo narrativa)

exemplo:
    python3 fatiar-slides.py deck.html /tmp/fatias slide
    python3 fatiar-slides.py deck-narrativa.html /tmp/fatias page
"""
import re
import sys
import pathlib


def fatiar(caminho_deck, pasta_saida, classe="slide"):
    src = pathlib.Path(caminho_deck).read_text(encoding="utf-8")
    out = pathlib.Path(pasta_saida)
    out.mkdir(parents=True, exist_ok=True)

    if "<body" not in src:
        sys.exit(f"erro: {caminho_deck} não tem <body> — não parece um deck")
    head = src[: src.index("<body")]

    # Tudo que está no <body> ANTES do primeiro <section> — o sprite de ícones e o
    # HUD. Sem repetir isso em cada fatia, todo <use href="#i-*"> aponta para um
    # símbolo inexistente e o ícone some. O HUD vem junto mas o CSS abaixo o esconde.
    corpo_inicio = src.index(">", src.index("<body")) + 1
    m_primeira = re.search(r"<section\b", src[corpo_inicio:])
    preambulo = src[corpo_inicio : corpo_inicio + m_primeira.start()] if m_primeira else ""

    # \b nas bordas casa class="slide" E class="slide cover" — a capa não pode ficar de fora
    padrao = re.compile(
        r'<section\b[^>]*class="[^"]*\b' + re.escape(classe) + r'\b[^"]*"[\s\S]*?</section>'
    )
    secoes = padrao.findall(src)
    if not secoes:
        sys.exit(
            f'erro: nenhuma <section class="...{classe}..."> em {caminho_deck}.\n'
            f"       modo relatorio usa 'slide'; modo narrativa usa 'page'."
        )

    # Na fatia o HUD não faz sentido (o contador erraria) e o snap atrapalha o print.
    # 'estatico' desliga a animação de entrada do modo narrativa — sem isso a fatia
    # sai em branco, porque o print acontece antes de a animação terminar.
    ajuste = (
        "<style>"
        ".hud-logo,.hud-counter,.hud-controls{display:none!important}"
        "html{scroll-snap-type:none!important}"
        ".reveal{animation:none!important;opacity:1!important;transform:none!important}"
        "</style>"
    )

    for i, secao in enumerate(secoes, 1):
        doc = head.replace("</head>", ajuste + "\n</head>") if "</head>" in head else head + ajuste
        (out / f"slide-{i:02d}.html").write_text(
            f"{doc}<body>\n{preambulo}\n{secao}\n</body>\n</html>\n", encoding="utf-8"
        )

    print(f"{len(secoes)} fatias de .{classe} -> {out}")
    return len(secoes)


def main():
    args = [a for a in sys.argv[1:] if a not in ("-h", "--help")]
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    if len(args) < 2:
        print(__doc__)
        return 2
    classe = args[2] if len(args) > 2 else "slide"
    if classe not in ("slide", "page"):
        sys.exit(f"erro: classe '{classe}' inválida — use 'slide' ou 'page'")
    fatiar(args[0], args[1], classe)
    return 0


if __name__ == "__main__":
    sys.exit(main())
