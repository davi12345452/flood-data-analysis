"""Testes do dataset supervisionado: rótulos, subconjuntos e amostragem."""

import numpy as np
import pandas as pd

from src.dataset.build import colunas_do_subconjunto, montar_alvo

H = pd.date_range("2024-05-01", periods=100, freq="h", tz="UTC")


def frame_sintetico():
    return pd.DataFrame({
        "chuva_antas_24h": np.ones(100),
        "api_antas_k90": np.ones(100),
        "chuva_baixo_24h": np.ones(100),
        "nivel_mu": np.arange(100, dtype=float),
        "dnivel_1h_mu": np.ones(100),
        "nivel_jj": np.arange(100, dtype=float) * 2,
        "defluente_qj": np.ones(100) * 500,
    }, index=H)


JANELAS = [{"nome": "ev20240501", "inicio": str(H[10]), "fim": str(H[40])}]
SUB = {"chuva": ["antas"], "estacoes": ["jj", "mu"], "uhes": True}


class TestSubconjunto:
    def test_seleciona_so_montante(self):
        cols = colunas_do_subconjunto(frame_sintetico(), SUB)
        assert "chuva_antas_24h" in cols and "api_antas_k90" in cols
        assert "nivel_mu" in cols and "nivel_jj" in cols
        assert "defluente_qj" in cols
        assert "chuva_baixo_24h" not in cols  # jusante não entra


class TestRotulos:
    def test_rotulo_e_o_nivel_em_t_mais_h(self):
        ds = montar_alvo(frame_sintetico(), 86510000, [3, 6], JANELAS, SUB)
        t = H[20]
        assert ds.loc[t, "y_3h"] == 23.0  # nivel_mu é a rampa 0..99
        assert ds.loc[t, "y_6h"] == 26.0

    def test_rotulo_nan_quando_sensor_cai_no_futuro(self):
        f = frame_sintetico()
        f.loc[H[25], "nivel_mu"] = np.nan
        ds = montar_alvo(f, 86510000, [3, 6], JANELAS, SUB)
        # t=22h: y_3h cai na lacuna (NaN), mas a linha fica (y_6h existe)
        assert np.isnan(ds.loc[H[22], "y_3h"])
        assert ds.loc[H[22], "y_6h"] == 28.0
        assert ds.loc[H[23], "y_3h"] == 26.0
        # com UM só horizonte, a linha sem rótulo sai por inteiro
        ds1 = montar_alvo(f, 86510000, [3], JANELAS, SUB)
        assert H[22] not in ds1.index

    def test_linha_sem_nenhum_rotulo_sai(self):
        f = frame_sintetico()
        f.loc[H[30]:, "nivel_mu"] = np.nan  # sensor morre de vez
        ds = montar_alvo(f, 86510000, [3, 6], JANELAS, SUB)
        # a partir de H[27] nem y_3h nem y_6h existem
        assert ds.index.max() == H[26]

    def test_janelas_sobrepostas_nao_duplicam_linhas(self):
        janelas = JANELAS + [{"nome": "ev20240502", "inicio": str(H[35]), "fim": str(H[60])}]
        ds = montar_alvo(frame_sintetico(), 86510000, [3], janelas, SUB)
        assert not ds.index.duplicated().any()

    def test_metadados_de_amostragem(self):
        janelas = JANELAS + [{"nome": "nm20240503", "inicio": str(H[60]), "fim": str(H[80])}]
        ds = montar_alvo(frame_sintetico(), 86510000, [3], janelas, SUB)
        assert set(ds["tipo"].unique()) == {"evento", "normal"}
        assert (ds[ds["janela_id"] == "ev20240501"]["tipo"] == "evento").all()
