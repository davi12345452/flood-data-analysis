"""Testes de métricas e baselines."""

import numpy as np
import pandas as pd
import pytest

from src.eval import metrics
from src.models import baselines

H = pd.date_range("2024-05-01", periods=60, freq="h", tz="UTC")


class TestMetricas:
    def test_previsao_perfeita(self):
        o = pd.Series([1.0, 2.0, 3.0, 4.0])
        assert metrics.nse(o, o) == pytest.approx(1.0)
        assert metrics.kge(o, o) == pytest.approx(1.0)
        assert metrics.rmse(o, o) == 0.0

    def test_nse_da_media_e_zero(self):
        o = pd.Series([1.0, 2.0, 3.0, 4.0])
        p = pd.Series([2.5] * 4)
        assert metrics.nse(o, p) == pytest.approx(0.0)

    def test_nan_excluido_e_cobertura_reportada(self):
        o = pd.Series([1.0, np.nan, 3.0, 4.0])
        p = pd.Series([1.0, 2.0, np.nan, 4.0])
        r = metrics.resumo(o, p)
        assert r["n"] == 2
        assert r["cobertura"] == pytest.approx(0.5)
        assert r["RMSE_cm"] == 0.0

    def test_kge_penaliza_vies(self):
        o = pd.Series(np.arange(50, dtype=float) + 10)
        assert metrics.kge(o, o * 2) < metrics.kge(o, o)


def dataset_sintetico():
    """Montante (jj) leva 2h para virar nível em Muçum (mu), com ganho 1."""
    up = pd.Series(np.sin(np.arange(60) / 5) * 100 + 500, index=H)
    own = up.shift(2)
    ds = pd.DataFrame({
        "nivel_mu": own, "dnivel_1h_mu": own.diff(), "dnivel_3h_mu": own.diff(3) / 3,
        "nivel_jj": up, "dnivel_1h_jj": up.diff(), "dnivel_3h_jj": up.diff(3) / 3,
        "janela_id": "ev1", "tipo": "evento",
    }, index=H)
    for h in (3,):
        ds[f"y_{h}h"] = own.shift(-h)
    return ds.dropna(subset=["nivel_mu"])


class TestBaselines:
    def test_persistencia_e_o_nivel_atual(self):
        ds = dataset_sintetico()
        pred = baselines.persistencia(ds, 86510000, 3)
        pd.testing.assert_series_equal(pred, ds["nivel_mu"], check_names=False)

    def test_tempo_viagem_recupera_o_lag(self):
        ds = dataset_sintetico()
        assert baselines.estimar_tempo_viagem(ds, 86510000, max_lag_h=6) == 2

    def test_regressao_aprende_relacao_linear(self):
        ds = dataset_sintetico()
        train, test = ds.iloc[:40], ds.iloc[40:]
        pred = baselines.regressao_lags(train, test, 86510000, 3)
        obs = test["y_3h"]
        ok = pred.notna() & obs.notna()
        assert metrics.rmse(obs[ok], pred[ok]) < 20  # sinal suave e linear
