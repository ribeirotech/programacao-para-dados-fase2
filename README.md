# Programação para Dados — Fase II (Steam)

Análise exploratória do catálogo de jogos da Steam com pandas, numpy e matplotlib.

- `Fase2_Programacao_para_Dados.ipynb` — respostas e gráficos (já executado)
- `preprocessamento.py` — carga e limpeza dos dados (com doctests)
- `estilo.py` e `estilo_fun_corp.mplstyle` — estilo padronizado das figuras
- `figuras/` — gráficos em PNG · `data/steam_games.csv` — dados · `tests/` — testes
- `Fase2_Relatorio.pdf` — relatório

Execução (Python 3.10+; `pip install pandas numpy matplotlib jupyter`), na raiz do projeto:

    python -m unittest discover -s tests -v
    jupyter nbconvert --to notebook --execute --inplace Fase2_Programacao_para_Dados.ipynb
