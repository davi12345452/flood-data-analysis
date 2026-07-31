"""Testes de detecção de ultrapassagem e métricas de pico."""

import numpy as np
import pandas as pd
import pytest

from src.eval.detection import deteccao, pico_por_evento

H = pd.date_range("2024-05-01", periods=48, freq="h", tz="UTC")


class TestDeteccao:
    def test_previsao_perfeita(self):
        obs = pd.Series([100, 200, 300, 400], dtype=float)
        r = deteccao(obs, obs, limiar=250)
        assert r["POD"] == 1.0 and r["FAR"] == 0.0 and r["CSI"] == 1.0
        assert r["vies_freq"] == 1.0

    def test_contagens_conhecidas(self):
        obs = pd.Series([300, 300, 100, 100], dtype=float)   # 2 acima
        pred = pd.Series([300, 100, 300, 100], dtype=float)  # 1 hit, 1 miss, 1 falso
        r = deteccao(obs, pred, limiar=250)
        assert r["POD"] == pytest.approx(0.5)
        assert r["FAR"] == pytest.approx(0.5)
        assert r["CSI"] == pytest.approx(1 / 3)
        assert r["vies_freq"] == pytest.approx(1.0)

    def test_nan_fica_fora(self):
        obs = pd.Series([300, np.nan, 100], dtype=float)
        pred = pd.Series([300, 300, np.nan], dtype=float)
        r = deteccao(obs, pred, limiar=250)
        assert r["n"] == 1 and r["POD"] == 1.0


class TestPico:
    def _grupo(self, obs, pred):
        return pd.DataFrame({"ts_utc": H[:len(obs)], "obs": obs, "pred": pred})

    def test_erros_de_valor_e_tempo(self):
        obs = np.concatenate([np.linspace(0, 100, 24), np.linspace(100, 0, 24)])
        pred = np.roll(obs, 3) * 0.9  # pico 3h depois, 10% menor
        r = pico_por_evento(self._grupo(obs, pred))
        assert r["pico_obs_cm"] == pytest.approx(100.0)
        assert r["erro_valor_pico_cm"] == pytest.approx(-10.0, abs=1.5)
        assert r["erro_tempo_pico_h"] == pytest.approx(3.0)

    def test_cobertura_reflete_lacuna_no_pico(self):
        obs = np.concatenate([np.linspace(0, 100, 24), np.linspace(100, 0, 24)])
        obs_lacuna = obs.copy()
        obs_lacuna[20:28] = np.nan  # sensor cai em torno do pico
        r = pico_por_evento(self._grupo(obs_lacuna, obs))
        assert r["cobertura_pico"] < 1.0

    def test_sem_observacao_retorna_none(self):
        r = pico_por_evento(self._grupo([np.nan] * 10, [1.0] * 10))
        assert r is None
