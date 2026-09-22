"""Conferência previsto × observado: pareamento exato, pendências e picos."""

import numpy as np
import pandas as pd

from src.live import evento


def _frame():
    idx = pd.date_range("2026-09-21 03:00", periods=30, freq="h", tz="UTC")
    return pd.DataFrame({"nivel_mu": np.linspace(400, 1800, 30),
                         "nivel_en": np.linspace(300, 1100, 30),
                         "nivel_es": np.linspace(1500, 2200, 30)}, index=idx)


def _publicadas():
    t0 = pd.Timestamp("2026-09-21 21:00", tz="UTC")
    return pd.DataFrame({
        "emissao": ["18h"] * 3, "tipo": ["emissao"] * 3,
        "alvo": ["Muçum", "Muçum", "Encantado"], "codigo": [86510000, 86510000, 86720000],
        "motor": ["linear"] * 3, "h": [3, 6, 3], "t_ref_utc": [t0] * 3,
        "emitido_em_utc": [t0 + pd.Timedelta(minutes=67)] * 3,
        "valido_para_utc": [t0 + pd.Timedelta(hours=h) for h in (3, 6, 3)],
        "antecedencia_real_h": [3 - 67 / 60, 6 - 67 / 60, 3 - 67 / 60],
        "previsto_cm": [1500.0, np.nan, 800.0], "corrigido_cm": [1600.0, np.nan, np.nan],
    })


def test_pareia_na_validade_exata_e_marca_pendente_alem_de_agora():
    frame = _frame()
    agora = pd.Timestamp("2026-09-22 01:00", tz="UTC")
    pares = evento.parear(_publicadas(), frame, agora)
    mu3 = pares[(pares.alvo == "Muçum") & (pares.h == 3)].iloc[0]
    assert mu3.status == "conferido"
    assert mu3.observado_cm == frame.loc[mu3.valido_para_utc, "nivel_mu"]
    assert mu3.erro_cm == 1500.0 - mu3.observado_cm
    assert mu3.erro_corrigido_cm == 1600.0 - mu3.observado_cm
    assert pares[(pares.alvo == "Muçum") & (pares.h == 6)].status.iloc[0] == "não emitida"
    en3 = pares[pares.alvo == "Encantado"].iloc[0]
    assert en3.status == "conferido" and en3.erro_cm < 0


def test_futuro_fica_pendente_mesmo_com_cota_no_frame():
    frame = _frame()
    agora = pd.Timestamp("2026-09-21 23:00", tz="UTC")
    pares = evento.parear(_publicadas(), frame, agora)
    assert (pares.status == "pendente").sum() == 2
    assert pares.loc[pares.status == "pendente", "observado_cm"].isna().all()


def test_lacuna_na_validade_nao_e_interpolada():
    frame = _frame().drop(pd.Timestamp("2026-09-22 00:00", tz="UTC"))
    pares = evento.parear(_publicadas(), frame, pd.Timestamp("2026-09-22 06:00", tz="UTC"))
    assert pares[(pares.alvo == "Muçum") & (pares.h == 3)].status.iloc[0] == "sem observação"


def test_picos_registra_hora_e_cruzamento_da_inundacao():
    frame = _frame()
    frame.loc[frame.index[20:], "nivel_mu"] = 1700  # platô abaixo da inundação (1800)
    frame.loc[frame.index[25], "nivel_mu"] = 1850
    agora = frame.index[-1]
    pico = evento.picos(frame, agora).set_index("alvo")
    assert pico.loc["Muçum", "pico_cm"] == 1850
    assert pico.loc["Muçum", "hora_pico_utc"] == frame.index[25]
    assert pico.loc["Muçum", "cruzou_inundacao_utc"] == frame.index[25]
    assert pico.loc["Muçum", "horas_acima_inundacao"] == 1
    assert pd.isna(pico.loc["Encantado", "cruzou_inundacao_utc"])
