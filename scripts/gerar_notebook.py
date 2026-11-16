"""Monta o notebook da Fase II. Depois: jupyter nbconvert --execute --inplace."""
from pathlib import Path
import nbformat as nbf

md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
C = []

C.append(md("""# Programação para Dados — Fase II
**Fun Corp. · Análise do catálogo de jogos da Steam** (pandas, numpy e matplotlib)

Organização do projeto:
- `preprocessamento.py` — carga e limpeza dos dados (funções documentadas e com doctests)
- `estilo.py` + `estilo_fun_corp.mplstyle` — estilo visual padronizado de todas as figuras
- este notebook — consultas e gráficos; as figuras também são salvas em `figuras/`"""))

C.append(code("""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import estilo
from estilo import AZUL, LARANJA, VERDE, CINZA, pt_br
from preprocessamento import carregar_jogos

estilo.aplicar_estilo()
pd.set_option("display.width", 140)
pd.set_option("display.max_colwidth", 60)"""))

# ---------------- carga
C.append(md("## 1. Carga e pré-processamento"))
C.append(code("""df = carregar_jogos("data/steam_games.csv")
print(f"{len(df)} jogos · datas de {df.data_lancamento.min():%d/%m/%Y} a {df.data_lancamento.max():%d/%m/%Y}")
print("AppIDs duplicados:", df.app_id.duplicated().sum())
print("\\nValores ausentes por coluna (apenas colunas com ausência):")
print(df.isna().sum()[lambda s: s > 0])
df.head(3)"""))
C.append(md("""**Decisões de pré-processamento** (detalhadas em `preprocessamento.py`):
- *Datas*: formatos `"Oct 21, 2008"` e `"Oct 2008"` (dia 1) convertidos para `datetime`.
- *Metacritic*: nota `0` significa "sem nota" no arquivo; foi convertida para `NaN` (só 310 dos 5.199 jogos têm nota).
- *Gêneros, categorias e empresas*: campos de texto separados por vírgula viram listas. Nas empresas, vírgulas antes de sufixos como `Inc.`/`Ltd.` não separam empresas (ex.: `KOEI TECMO GAMES CO., LTD.` é uma só).
- *Mídias de demonstração*: contagem de links em `Screenshots` e `Movies` (vazio = 0).
- *Jogo pago*: preço > 0 (mesmo critério da Fase I)."""))

# ---------------- Q1
C.append(md("## 2. Pergunta 1 — Dez jogos mais bem avaliados no Metacritic"))
C.append(code("""com_nota = df.dropna(subset=["nota_metacritic"])
top10 = (com_nota
         .sort_values(["nota_metacritic", "data_lancamento"], ascending=[False, True])
         .head(10)[["nome", "nota_metacritic", "data_lancamento"]]
         .reset_index(drop=True))
top10.index += 1
top10["nota_metacritic"] = top10["nota_metacritic"].astype(int)
top10["data_lancamento"] = top10["data_lancamento"].dt.strftime("%d/%m/%Y")
display(top10)

# Desempate na fronteira do top 10: quantos jogos têm a nota do 10º colocado?
nota_corte = top10["nota_metacritic"].iloc[-1]
empatados = com_nota[com_nota.nota_metacritic == nota_corte].sort_values("data_lancamento")
print(f"\\nJogos com nota {nota_corte} (nota do 10º colocado): {len(empatados)}")
display(empatados[["nome", "data_lancamento"]].assign(
    data_lancamento=lambda d: d.data_lancamento.dt.strftime("%d/%m/%Y")).reset_index(drop=True))"""))

# ---------------- Q2
C.append(md("## 3. Pergunta 2 — Jogos de role-playing (gênero `RPG`)"))
C.append(code("""rpg = df[df.generos.map(lambda g: "RPG" in g)]
metricas = {"dlcs": "DLCs", "positivas": "Avaliações positivas",
            "negativas": "Avaliações negativas", "n_midias": "Materiais de demonstração"}
q2 = rpg[list(metricas)].agg(["mean", "max"]).T.rename(columns={"mean": "média", "max": "máximo"})
q2.index = [metricas[i] for i in q2.index]
print(f"{len(rpg)} jogos RPG")
display(q2.round(2))

# Quem são os jogos que têm os valores máximos?
for col, nome in metricas.items():
    linha = rpg.loc[rpg[col].idxmax()]
    print(f"Máximo de {nome}: {int(linha[col])} -> {linha['nome']}")"""))

# ---------------- Q3
C.append(md("## 4. Pergunta 3 — Empresas que mais publicam jogos pagos"))
C.append(code("""# Um jogo com várias publicadoras conta uma vez para cada uma; jogos sem publicadora ficam de fora.
pagos = df[df.pago].explode("publicadoras").dropna(subset=["publicadoras"])
contagem = pagos.groupby("publicadoras").size().sort_values(ascending=False)
print("Maiores contagens de jogos pagos:")
display(contagem.head(8).to_frame("jogos pagos"))

corte = contagem.iloc[4]                     # valor do 5º colocado
top = contagem[contagem >= corte].index      # inclui empatados no 5º lugar
q3 = (pagos[pagos.publicadoras.isin(top)]
      .groupby("publicadoras")["positivas"]
      .agg(jogos_pagos="count", media_positivas="mean", mediana_positivas="median")
      .sort_values(["jogos_pagos", "media_positivas"], ascending=[False, False]))
display(q3.round(1))
print(f"Empate no 5º lugar ({corte} jogos): {', '.join(contagem[contagem == corte].index)}")"""))

# ---------------- Q4
C.append(md("## 5. Pergunta 4 — O número de jogos com suporte a Linux cresceu entre 2018 e 2022?"))
C.append(code("""anos = range(2018, 2023)
por_ano = (df[df.ano.isin(anos)]
           .groupby("ano")
           .agg(lancamentos=("linux", "size"), com_linux=("linux", "sum")))
por_ano["% com Linux"] = 100 * por_ano.com_linux / por_ano.lancamentos
display(por_ano.round(1))

# O arquivo termina em 23/07/2022, então 2022 está incompleto.
# Comparação justa: apenas lançamentos de 1º de janeiro a 23 de julho de cada ano.
ate_23_jul = df[df.ano.isin(anos) & (df.data_lancamento.dt.strftime("%m-%d") <= "07-23")]
mesmo_periodo = (ate_23_jul.groupby("ano")
                 .agg(lancamentos=("linux", "size"), com_linux=("linux", "sum")))
mesmo_periodo["% com Linux"] = 100 * mesmo_periodo.com_linux / mesmo_periodo.lancamentos
print("\\nMesmo período (1º jan a 23 jul) em cada ano:")
display(mesmo_periodo.round(1))

ini, fim = mesmo_periodo.com_linux.loc[2018], mesmo_periodo.com_linux.loc[2022]
print(f"Mesmo período: {ini} (2018) -> {fim} (2022): variação de {100*(fim-ini)/ini:+.1f}%")"""))

# ---------------- Q5
C.append(md("""## 6. Pergunta 5 (própria) — Quais gêneros geram mais receita estimada e quão concentrada ela é?
**Receita estimada** de um jogo pago = preço × ponto médio da faixa de *Estimated owners*. É uma aproximação:
usa o preço atual, ignora DLCs e microtransações e depende de faixas largas de donos.
Um jogo com vários gêneros conta em cada um deles, então os totais por gênero não se somam.
Consideram-se apenas gêneros de jogo (excluídos `Early Access`, que é status de desenvolvimento, `Free to Play` e softwares como `Utilities`)."""))
C.append(code("""GENEROS_DE_JOGO = ["Action", "Adventure", "Indie", "Simulation", "RPG", "Strategy",
                   "Casual", "Massively Multiplayer", "Racing", "Sports"]

pagos_jogos = df[df.pago].copy()
pagos_jogos["receita"] = pagos_jogos.preco * pagos_jogos.donos_estimados

por_genero = (pagos_jogos.explode("generos")
              .query("generos in @GENEROS_DE_JOGO")
              .groupby("generos")["receita"]
              .agg(jogos="size", total="sum", media="mean", mediana="median")
              .sort_values("total", ascending=False))
tabela = por_genero.assign(total=lambda d: d.total / 1e6,
                           media=lambda d: d.media / 1e3,
                           mediana=lambda d: d.mediana / 1e3)
tabela.columns = ["jogos pagos", "total (US$ mi)", "média por jogo (US$ mil)", "mediana por jogo (US$ mil)"]
display(tabela.round(1))

# Concentração: quanto da receita total vem dos jogos mais lucrativos?
ordenada = pagos_jogos.receita.sort_values(ascending=False)
total = ordenada.sum()
n1 = int(np.ceil(0.01 * len(ordenada)))
print(f"Receita total estimada (jogos pagos): US$ {total/1e9:.2f} bi em {len(ordenada)} jogos")
print(f"Top 1% dos jogos ({n1}) concentram {100*ordenada.head(n1).sum()/total:.1f}% da receita")
print(f"Top 10% dos jogos ({int(0.1*len(ordenada))}) concentram {100*ordenada.head(int(0.1*len(ordenada))).sum()/total:.1f}% da receita")
print(f"Metade 'de baixo' dos jogos concentra {100*ordenada.tail(len(ordenada)//2).sum()/total:.2f}% da receita")
print("Jogos com receita estimada zero (0 donos estimados):", int((ordenada == 0).sum()))"""))

# ---------------- Graficos
C.append(md("## 7. Gráficos"))
C.append(md("### Gráfico 1 — Suporte por sistema operacional"))
C.append(code("""votos = df[["windows", "mac", "linux"]].sum()
votos.index = ["Windows", "macOS", "Linux"]
percentual = 100 * votos / votos.sum()
print(votos.to_dict(), "| total de votos:", int(votos.sum()))

fig, ax = plt.subplots(figsize=(7.5, 4.6))
barras = ax.bar(percentual.index, percentual.values, color=[AZUL, LARANJA, VERDE], width=0.55)
for barra, v, n in zip(barras, percentual.values, votos.values):
    ax.annotate(f"{pt_br(v)}%\\n({pt_br(n, 0)} jogos)", (barra.get_x() + barra.get_width() / 2, v),
                xytext=(0, 5), textcoords="offset points", ha="center", fontsize=10.5, fontweight="bold")
ax.set_ylim(0, 85)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax.set_ylabel("% do total de suportes declarados")
ax.grid(axis="x", visible=False)
estilo.titulo(ax, "Windows concentra quase três quartos do suporte",
              "Cada sistema operacional suportado por um jogo conta como 1 voto")
estilo.fonte(fig)
fig.savefig("figuras/grafico1_sistemas_operacionais.png")
plt.show()"""))

C.append(md("### Gráfico 2 — Jogos single-player Indie e Strategy lançados por ano (2010–2020)"))
C.append(code("""single = df[df.categorias.map(lambda c: "Single-player" in c) & df.ano.between(2010, 2020)]
anos2 = np.arange(2010, 2021)
series = {}
for genero in ["Indie", "Strategy"]:
    sel = single[single.generos.map(lambda g, gen=genero: gen in g)]
    series[genero] = sel.groupby("ano").size().reindex(anos2, fill_value=0)
tabela2 = pd.DataFrame(series)
display(tabela2.T)

fig, ax = plt.subplots(figsize=(8.5, 4.8))
for (genero, serie), cor in zip(series.items(), [AZUL, LARANJA]):
    ax.plot(anos2, serie.values, marker="o", color=cor, label=genero)
    coef = np.polyfit(anos2, serie.values, 1)          # tendência linear
    ax.plot(anos2, np.polyval(coef, anos2), ls="--", lw=1.6, color=cor, alpha=0.8,
            label=f"Tendência {genero} ({coef[0]:+.0f} jogos/ano)")
ax.set_xticks(anos2)
ax.set_ylim(bottom=0)                       # tendência linear não deve "afundar" abaixo de zero
ax.set_xlabel("Ano de lançamento")
ax.set_ylabel("Jogos single-player lançados")
ax.legend(loc="upper left")
estilo.titulo(ax, "Lançamentos single-player crescem, mas Indie cresce bem mais rápido",
              "Jogos single-player por gênero, 2010–2020 (um jogo Indie e Strategy conta nos dois)")
estilo.fonte(fig)
fig.savefig("figuras/grafico2_indie_estrategia.png")
plt.show()"""))

C.append(md("### Gráfico 3 — Receita estimada por gênero (pergunta 5)"))
C.append(code("""ordem = por_genero.index[::-1]                       # maior no topo
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), sharey=True,
                               gridspec_kw={"width_ratios": [1.1, 1], "wspace": 0.08})

# Painel esquerdo: receita total
ax1.barh(ordem, por_genero.total[ordem] / 1e9, color=AZUL, height=0.62)
for i, g in enumerate(ordem):
    ax1.annotate(f"{pt_br(por_genero.total[g] / 1e9, 2)} bi", (por_genero.total[g] / 1e9, i),
                 xytext=(4, 0), textcoords="offset points", va="center", fontsize=9.5)
ax1.set_xlim(0, 5.3)
ax1.set_xlabel("Receita total estimada (US$ bilhões)")
ax1.grid(axis="y", visible=False)
ax1.set_title("Receita total", loc="left", fontsize=11.5, pad=34)

# Painel direito: média x mediana por jogo (escala logarítmica)
ax2.scatter(por_genero.media[ordem] / 1e3, ordem, color=LARANJA, s=70, zorder=3, label="Média por jogo")
ax2.scatter(por_genero.mediana[ordem] / 1e3, ordem, color=VERDE, s=70, zorder=3, label="Mediana por jogo")
for g in ordem:
    ax2.plot([por_genero.mediana[g] / 1e3, por_genero.media[g] / 1e3], [g, g], color=CINZA, lw=1.5, zorder=2)
ax2.set_xscale("log")
ax2.set_xlim(40, 12000)
ax2.set_xticks([100, 500, 1000, 5000])
ax2.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{pt_br(v, 0)} mil" if v < 1000 else f"{pt_br(v/1000, 0)} mi"))
ax2.minorticks_off()
ax2.set_xlabel("Receita estimada por jogo (US$, escala log)")
ax2.grid(axis="y", visible=False)
ax2.legend(loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=2, borderaxespad=0.2)
ax2.set_title("Receita por jogo", loc="left", fontsize=11.5, pad=34)

fig.suptitle("Ação e Aventura lideram a receita, mas o jogo típico fatura muito menos que a média",
             x=0.01, y=1.08, ha="left", fontsize=14, fontweight="bold")
estilo.fonte(fig, "Receita estimada = preço × ponto médio das faixas de donos estimados (apenas jogos pagos). Fonte: Steam (steam_games.csv) · Fun Corp.")
fig.savefig("figuras/grafico3_receita_por_genero.png")
plt.show()"""))

nb = nbf.v4.new_notebook()
nb.cells = C
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, Path(__file__).resolve().parent.parent / "Fase2_Programacao_para_Dados.ipynb")
