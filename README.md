# Programação para Dados — Fase II

Análise exploratória do catálogo de jogos da Steam (5.199 jogos, lançamentos de 2003 a 23/07/2022) com **pandas, numpy e matplotlib**, para a empresa fictícia Fun Corp.

## Resultados principais

| # | Pergunta | Resposta resumida |
|---|----------|-------------------|
| 1 | 10 jogos mais bem avaliados no Metacritic | Call of Duty 4: Modern Warfare lidera (92). Só 310 jogos têm nota; no 10º lugar há 9 jogos com nota 88, desempatados pela data de lançamento |
| 2 | RPGs: média e máximo de DLCs, avaliações e mídias | 862 jogos. Média de 0,52 DLC, 1.444 avaliações positivas, 358 negativas e 11,4 mídias; os máximos são muito maiores (poucos grandes sucessos) |
| 3 | 5 empresas que mais publicam jogos pagos | Big Fish Games (35), 8floor (18), SEGA (16), Laush Studio (14); Ubisoft e Choice of Games empatam em 5º (13) |
| 4 | Jogos com Linux cresceram entre 2018 e 2022? | Sim em número (80 → 105 de 2018 a 2021; 47 → 60 no mesmo período jan–jul), mas a participação caiu de 12,1% para ~10% |
| 5 | Pergunta própria: receita estimada por gênero e sua concentração | Ação lidera (US$ 4,36 bi estimados); o top 1% dos jogos concentra 59,6% da receita |

Gráficos (em `figuras/`): suporte por sistema operacional, lançamentos single-player Indie × Strategy (2010–2020) e receita estimada por gênero.

## Estrutura

- `Fase2_Programacao_para_Dados.ipynb` — perguntas e gráficos (notebook já executado)
- `preprocessamento.py` — carga e limpeza dos dados, com doctests
- `estilo.py` e `estilo_fun_corp.mplstyle` — estilo padronizado das figuras
- `tests/` — testes do pré-processamento
- `data/steam_games.csv` — dados · `figuras/` — gráficos em PNG
- `Fase2_Relatorio.pdf` — relatório entregue · `scripts/` — gerador do notebook

## Decisões de análise

- Nota Metacritic `0` = sem nota (tratada como ausente).
- Jogo pago = preço maior que zero; jogo de role-playing = gênero `RPG`.
- Empresas: vírgulas antes de sufixos (`Inc.`, `Ltd.`...) não separam empresas.
- Receita estimada = preço × ponto médio da faixa de donos estimados (aproximação, sem DLCs e microtransações).

## Como executar

Python 3.10+, na raiz do projeto:

    pip install pandas numpy matplotlib jupyter
    python -m unittest discover -s tests -v
    jupyter nbconvert --to notebook --execute --inplace Fase2_Programacao_para_Dados.ipynb
