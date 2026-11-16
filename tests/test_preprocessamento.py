"""Testes do pré-processamento (executar na raiz: python -m unittest discover -s tests -v)."""
import doctest
import unittest
from datetime import datetime
from pathlib import Path

import pandas as pd

import estilo
import preprocessamento as pp

DADOS = Path(__file__).resolve().parent.parent / "data" / "steam_games.csv"


def load_tests(loader, tests, ignore):
    for modulo in (pp, estilo):
        tests.addTests(doctest.DocTestSuite(modulo))
    return tests


class TestFuncoes(unittest.TestCase):
    def test_empresa_com_sufixo_nao_e_dividida(self):
        self.assertEqual(pp.separar_empresas("KOEI TECMO GAMES CO., LTD."), ["KOEI TECMO GAMES CO., LTD."])

    def test_varias_empresas(self):
        self.assertEqual(pp.separar_empresas("XSEED Games,Marvelous USA, Inc."), ["XSEED Games", "Marvelous USA, Inc."])

    def test_datas_com_e_sem_dia(self):
        s = pp.converter_datas(pd.Series(["Oct 21, 2008", "Oct 2008"]))
        self.assertEqual(list(s), [pd.Timestamp(2008, 10, 21), pd.Timestamp(2008, 10, 1)])

    def test_contar_urls(self):
        self.assertEqual(pp.contar_urls("http://a/1.mp4?t=1,http://a/2.mp4"), 2)
        self.assertEqual(pp.contar_urls(float("nan")), 0)


class TestCarga(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pp.carregar_jogos(DADOS)

    def test_tamanho_e_ids_unicos(self):
        self.assertEqual(len(self.df), 5199)
        self.assertTrue(self.df.app_id.is_unique)

    def test_nota_zero_vira_ausente(self):
        self.assertEqual(self.df.nota_metacritic.notna().sum(), 310)
        self.assertGreater(self.df.nota_metacritic.min(), 0)

    def test_periodo_dos_dados(self):
        self.assertEqual(self.df.data_lancamento.max(), pd.Timestamp(2022, 7, 23))

    def test_midias_nao_negativas(self):
        self.assertTrue((self.df.n_midias >= 0).all())


if __name__ == "__main__":
    unittest.main()
