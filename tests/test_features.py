"""Testes de features: causalidade, janelas, API e tempo-desde-atenção."""

import numpy as np
import pandas as pd
import pytest

from src.features.level import derivadas, disponibilidade, tempo_desde_atencao
from src.features.rain import acumulados, api_diaria, juntar_api_em_horas

H = pd.date_range("2024-05-01", periods=200, freq="h", tz="UTC")


class TestAcumulados:
    def test_janela_causal_nao_inclui_hora_atual(self):
        chuva = pd.DataFrame({"antas": np.zeros(200)}, index=H)
        chuva.iloc[100] = 10.0  # chuva na hora t=100 (acumulação [100, 101))
        ac = acumulados(chuva, [1])
        # em t=100 a chuva da própria hora ainda não é conhecida
        assert ac.iloc[100]["chuva_antas_1h"] == 0.0
        # em t=101 ela entra
        assert ac.iloc[101]["chuva_antas_1h"] == 10.0

    def test_soma_da_janela(self):
        chuva = pd.DataFrame({"antas": np.ones(200)}, index=H)
        ac = acumulados(chuva, [24])
        assert ac.iloc[50]["chuva_antas_24h"] == pytest.approx(24.0)

    def test_lacuna_gera_nan_nao_valor_fabricado(self):
        vals = np.ones(200)
        vals[95:100] = np.nan
        ac = acumulados(pd.DataFrame({"antas": vals}, index=H), [6])
        assert np.isnan(ac.iloc[100]["chuva_antas_6h"])  # janela toca a lacuna
        assert ac.iloc[110]["chuva_antas_6h"] == pytest.approx(6.0)

    def test_futuro_nao_altera_passado(self):
        # causalidade forte: mudar o futuro não muda a feature em t
        a = pd.DataFrame({"antas": np.ones(200)}, index=H)
        b = a.copy()
        b.iloc[150:] = 99.0
        fa = acumulados(a, [24]).iloc[:150]
        fb = acumulados(b, [24]).iloc[:150]
        pd.testing.assert_frame_equal(fa, fb)


class TestApi:
    DIAS = pd.date_range("2024-01-01 12:00", periods=100, freq="24h", tz="UTC")

    def test_recursao(self):
        chuva = pd.DataFrame({"antas": np.zeros(100)}, index=self.DIAS)
        chuva.iloc[10] = 20.0
        api = api_diaria(chuva, [0.90])["api_antas_k90"]
        # depois do impulso: API_d = 0.9^n * 20
        assert api.iloc[10] == pytest.approx(20.0, rel=0.05)
        assert api.iloc[15] == pytest.approx(20.0 * 0.9**5, rel=0.05)

    def test_junta_em_horas_e_causal(self):
        chuva = pd.DataFrame({"antas": np.ones(100)}, index=self.DIAS)
        api = api_diaria(chuva, [0.90])
        # período do dia D (rótulo 12 UTC) encerra em D+1 12 UTC:
        # às 11 UTC de D+1 o valor de D ainda NÃO pode estar disponível
        horas = pd.DatetimeIndex([
            pd.Timestamp("2024-01-02 11:00", tz="UTC"),
            pd.Timestamp("2024-01-02 12:00", tz="UTC"),
        ])
        j = juntar_api_em_horas(api, horas)
        # às 11:00 do dia 2 nenhum período fechou ainda (o 1º fecha 12:00)
        assert np.isnan(j.iloc[0]["api_antas_k90"])
        # às 12:00 o período do dia 1 acabou de fechar
        assert j.iloc[1]["api_antas_k90"] == pytest.approx(
            float(api.iloc[0, 0]), rel=1e-9
        )


class TestNivel:
    def test_derivada_nao_atravessa_lacuna(self):
        nivel = pd.Series(np.arange(200, dtype=float), index=H)
        nivel.iloc[100] = np.nan
        d = derivadas(nivel)
        assert np.isnan(d.iloc[100]["dnivel_1h"])
        assert np.isnan(d.iloc[101]["dnivel_1h"])  # vizinho da lacuna também
        assert d.iloc[102]["dnivel_1h"] == pytest.approx(1.0)

    def test_tempo_desde_atencao(self):
        nivel = pd.Series(np.zeros(200), index=H)
        nivel.iloc[50] = 600.0  # ultrapassa atenção=500
        t = tempo_desde_atencao(nivel, 500.0, cap_h=100)
        assert t.iloc[49] == 100  # antes: nunca ultrapassou -> teto
        assert t.iloc[50] == 0
        assert t.iloc[80] == 30
        assert t.iloc[199] == 100  # teto

    def test_tempo_desde_nan_conta_como_nao_acima(self):
        nivel = pd.Series(np.zeros(100), index=H[:100])
        nivel.iloc[50] = 600.0
        nivel.iloc[60:70] = np.nan
        t = tempo_desde_atencao(nivel, 500.0, cap_h=1000)
        assert t.iloc[75] == 25  # lacuna não reseta o marcador

    def test_disponibilidade_hora_ausente_conta_zero(self):
        disp = pd.Series([1.0, np.nan, 1.0, 1.0], index=H[:4])
        d = disponibilidade(disp, 2)
        assert d.iloc[1] == pytest.approx(0.5)  # (1 + 0)/2
