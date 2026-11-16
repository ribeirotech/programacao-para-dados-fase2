"""Estilo visual padronizado das figuras (identidade "Fun Corp.")."""

from pathlib import Path

import matplotlib.pyplot as plt

PASTA = Path(__file__).resolve().parent
ARQUIVO_ESTILO = PASTA / "estilo_fun_corp.mplstyle"

# Paleta única usada em todos os gráficos
AZUL = "#1F3A5F"
LARANJA = "#E07A2F"
VERDE = "#2A9D8F"
CINZA = "#B8B8B8"
CINZA_TEXTO = "#6B7280"


def aplicar_estilo() -> None:
    """Ativa o estilo customizado em toda a sessão do matplotlib."""
    plt.style.use(ARQUIVO_ESTILO)


def titulo(ax, texto: str, subtitulo: str = "") -> None:
    """Título em negrito alinhado à esquerda, com subtítulo cinza opcional."""
    ax.set_title(texto, loc="left", pad=30 if subtitulo else 14)
    if subtitulo:
        ax.annotate(subtitulo, xy=(0, 1), xycoords="axes fraction",
                    xytext=(0, 7), textcoords="offset points",
                    fontsize=9.5, color=CINZA_TEXTO, va="bottom")


def fonte(fig, texto: str = "Fonte: Steam (steam_games.csv) · Fun Corp.") -> None:
    """Rodapé padrão com a fonte dos dados."""
    fig.text(0.01, -0.02, texto, fontsize=8.5, color=CINZA_TEXTO, ha="left")


def pt_br(valor: float, casas: int = 1) -> str:
    """Formata número com vírgula decimal e ponto de milhar (padrão brasileiro).

    >>> pt_br(1234.5)
    '1.234,5'
    >>> pt_br(73.04, 2)
    '73,04'
    """
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")
