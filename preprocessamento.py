"""Carga e pré-processamento do catálogo de jogos da Steam (Fase II).

Todas as funções são puras e documentadas; o notebook apenas as chama,
de modo que cada decisão de limpeza fica registrada em um único lugar.
"""

import re
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd

# Sufixos societários que vêm depois de vírgula dentro do nome de UMA empresa
# (ex.: "KOEI TECMO GAMES CO., LTD."). Sem isso, a divisão por vírgula
# quebraria o nome em dois.
_SUFIXO_SOCIETARIO = re.compile(
    r"^(inc\.?|llc\.?|l\.l\.c\.?|ltd\.?|ltda\.?|limited|co\.?|corp\.?|corporation|"
    r"gmbh|s\.?a\.?|s\.?l\.?|b\.?v\.?|pty|oy|ab|ag|kg|ou)$",
    re.IGNORECASE,
)

_URL = re.compile(r"https?://")


def separar_empresas(texto: Optional[str]) -> List[str]:
    """Divide o campo ``Publishers``/``Developers`` em uma lista de empresas.

    Empresas são separadas por vírgula, mas vírgulas antes de sufixos
    societários (Inc., Ltd., LLC...) pertencem ao nome da empresa.

    >>> separar_empresas("Pixelated Milk,gaming company")
    ['Pixelated Milk', 'gaming company']
    >>> separar_empresas("KOEI TECMO GAMES CO., LTD.")
    ['KOEI TECMO GAMES CO., LTD.']
    >>> separar_empresas("Gemdrops, Inc.,Clouded Leopard Entertainment Inc.")
    ['Gemdrops, Inc.', 'Clouded Leopard Entertainment Inc.']
    >>> separar_empresas(None)
    []
    """
    if texto is None or (isinstance(texto, float) and np.isnan(texto)):
        return []
    empresas: List[str] = []
    for pedaco in (p.strip() for p in str(texto).split(",")):
        if not pedaco:
            continue
        if empresas and _SUFIXO_SOCIETARIO.match(pedaco):
            empresas[-1] += f", {pedaco}"
        else:
            empresas.append(pedaco)
    return empresas


def separar_lista(texto: Optional[str]) -> List[str]:
    """Divide campos simples separados por vírgula (gêneros, categorias).

    >>> separar_lista("Action,Indie")
    ['Action', 'Indie']
    >>> separar_lista(None)
    []
    """
    if texto is None or (isinstance(texto, float) and np.isnan(texto)):
        return []
    return [p.strip() for p in str(texto).split(",") if p.strip()]


def contar_urls(texto: Optional[str]) -> int:
    """Conta quantos links (capturas de tela ou filmes) há no campo.

    >>> contar_urls("https://a.com/1.jpg,https://a.com/2.jpg")
    2
    >>> contar_urls(None)
    0
    """
    if texto is None or (isinstance(texto, float) and np.isnan(texto)):
        return 0
    return len(_URL.findall(str(texto)))


def converter_datas(serie: pd.Series) -> pd.Series:
    """Converte datas "Oct 21, 2008" e "Oct 2008" (dia 1) para datetime."""
    completa = pd.to_datetime(serie, format="%b %d, %Y", errors="coerce")
    parcial = pd.to_datetime(serie, format="%b %Y", errors="coerce")
    return completa.fillna(parcial)


def ponto_medio_donos(faixa: str) -> float:
    """Ponto médio da faixa de donos estimados.

    >>> ponto_medio_donos("20000 - 50000")
    35000.0
    """
    inferior, superior = (float(x) for x in faixa.split("-"))
    return (inferior + superior) / 2


def carregar_jogos(caminho) -> pd.DataFrame:
    """Lê o CSV e devolve um DataFrame limpo, com colunas derivadas.

    Tratamentos aplicados:
      * ``data_lancamento`` e ``ano`` a partir de "Release date";
      * ``nota_metacritic``: a nota 0 significa "sem nota" e vira NaN;
      * ``generos``, ``categorias`` e ``publicadoras``: campos de texto
        transformados em listas;
      * ``n_capturas``, ``n_filmes`` e ``n_midias``: contagem de links
        (campos vazios contam como 0);
      * ``pago`` (preço > 0) e ``donos_estimados`` (ponto médio da faixa).
    """
    bruto = pd.read_csv(Path(caminho))
    df = pd.DataFrame({
        "app_id": bruto["AppID"],
        "nome": bruto["Name"],
        "data_lancamento": converter_datas(bruto["Release date"]),
        "preco": bruto["Price"],
        "windows": bruto["Windows"],
        "mac": bruto["Mac"],
        "linux": bruto["Linux"],
        "nota_metacritic": bruto["Metacritic score"].replace(0, np.nan),
        "dlcs": bruto["DLC count"],
        "positivas": bruto["Positive"],
        "negativas": bruto["Negative"],
        "generos": bruto["Genres"].map(separar_lista),
        "categorias": bruto["Categories"].map(separar_lista),
        "publicadoras": bruto["Publishers"].map(separar_empresas),
        "n_capturas": bruto["Screenshots"].map(contar_urls),
        "n_filmes": bruto["Movies"].map(contar_urls),
        "donos_estimados": bruto["Estimated owners"].map(ponto_medio_donos),
    })
    if df["data_lancamento"].isna().any():
        raise ValueError("Há datas de lançamento em formato não reconhecido.")
    df["ano"] = df["data_lancamento"].dt.year
    df["n_midias"] = df["n_capturas"] + df["n_filmes"]
    df["pago"] = df["preco"] > 0
    return df
