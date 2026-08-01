"""Testes de QC: flags, regra zero-como-NaN e alinhamento temporal."""

import pandas as pd

from src.qc import flags
from src.qc.ana import para_grade_horaria, qc_15min

CFG = {"stuck_min_steps_nivel": 4, "spike_max_cm_15min": 200}


def serie_15min(valores, inicio="2024-05-01 00:00"):
    dts = pd.date_range(inicio, periods=len(valores), freq="15min")
    return pd.DataFrame({
        "CodEstacao": "86510000",
        "DataHora": dts.astype(str),
        "dt_local": dts,
        "Vazao": [v * 10 if v is not None else None for v in valores],
        "Nivel": valores,
        "Chuva": 0.0,
    })


class TestFlags:
    def test_zero(self):
        s = pd.Series([100.0, 0.0, None, 50.0])
        assert flags.flag_zero(s).tolist() == [False, True, False, False]

    def test_stuck_detecta_run_longa(self):
        s = pd.Series([1.0, 5.0, 5.0, 5.0, 5.0, 2.0])
        assert flags.flag_stuck(s, 4).tolist() == [False, True, True, True, True, False]

    def test_stuck_nan_nao_forma_run(self):
        s = pd.Series([None, None, None, None, 1.0])
        assert not flags.flag_stuck(s, 3).any()

    def test_spike_so_em_passo_regular(self):
        dts = pd.Series(pd.to_datetime([
            "2024-05-01 00:00", "2024-05-01 00:15",
            "2024-05-01 06:00", "2024-05-01 06:15",
        ]))
        s = pd.Series([100.0, 400.0, 900.0, 950.0])
        result = flags.flag_spike(s, dts, max_delta=200)
        # 100->400 em 15min: spike; 400->900 através de lacuna de 6h: não
        assert result.tolist() == [False, True, False, False]

    def test_fora_de_ordem_respeita_convencao_descendente(self):
        # SOAP da ANA devolve o mês em ordem descendente: isso NÃO é anomalia
        dts = pd.Series(pd.to_datetime([
            "2024-05-03 00:00", "2024-05-02 00:00",
            "2024-05-02 12:00",  # embaralhado de verdade
            "2024-05-01 00:00",
        ]))
        result = flags.flag_fora_de_ordem(dts)
        assert result.tolist() == [False, False, True, False]

    def test_dst_incerto_marca_verao_2018(self):
        ts = pd.DatetimeIndex([
            pd.Timestamp("2019-01-15 12:00", tz="UTC"),   # DST vigente
            pd.Timestamp("2019-07-15 12:00", tz="UTC"),   # inverno
            pd.Timestamp("2024-01-15 12:00", tz="UTC"),   # DST já abolido
        ])
        assert flags.flag_dst_incerto(ts).tolist() == [True, False, False]


class TestQc15min:
    def test_zero_vira_nan_com_flag(self):
        df = qc_15min(serie_15min([100.0, 0.0, 120.0]), CFG)
        assert df["flag_nivel_zero"].tolist() == [False, True, False]
        assert pd.isna(df.loc[1, "Nivel"])
        assert pd.isna(df.loc[1, "Vazao"])  # vazão derivada cai junto

    def test_duplicata_removida_mas_flagada(self):
        df = serie_15min([100.0, 110.0])
        df = pd.concat([df, df.iloc[[1]]], ignore_index=True)
        out = qc_15min(df, CFG)
        assert len(out) == 2  # duplicata exata não entra duas vezes

    def test_spike_marcado_mas_nao_apagado(self):
        df = qc_15min(serie_15min([100.0, 400.0, 410.0]), CFG)
        assert df["flag_spike"].tolist() == [False, True, False]
        assert df.loc[1, "Nivel"] == 400.0


class TestGradeHoraria:
    def test_conversao_utc_e_topo_de_hora(self):
        # 21:00 local UTC-3 == 00:00 UTC do dia seguinte
        df = qc_15min(serie_15min([100.0, 110.0, 120.0, 130.0, 140.0],
                                  inicio="2024-05-01 21:00"), CFG)
        out = para_grade_horaria(df, tz_horas=-3)
        primeira = out.iloc[0]
        assert primeira["ts_utc"] == pd.Timestamp("2024-05-02 00:00", tz="UTC")
        assert primeira["nivel_cm"] == 100.0  # instantâneo, não média

    def test_chuva_soma_e_conta(self):
        df = serie_15min([100.0] * 4)
        df["Chuva"] = [1.0, 2.0, None, 4.0]
        out = para_grade_horaria(qc_15min(df, CFG), tz_horas=-3)
        assert out.iloc[0]["chuva_mm"] == 7.0
        assert out.iloc[0]["chuva_n"] == 3

    def test_hora_sem_amostra_no_topo_fica_nan(self):
        df = serie_15min([100.0, 110.0], inicio="2024-05-01 00:15")
        out = para_grade_horaria(qc_15min(df, CFG), tz_horas=-3)
        assert pd.isna(out.iloc[0]["nivel_cm"])  # sem interpolação

    def test_disponibilidade_parcial(self):
        df = serie_15min([100.0, 0.0, None, 130.0])
        out = para_grade_horaria(qc_15min(df, CFG), tz_horas=-3)
        assert out.iloc[0]["disp_nivel"] == 0.5  # 2 de 4 válidas (zero e NaN não contam)
