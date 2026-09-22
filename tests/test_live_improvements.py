"""Bloqueios contra vazamento temporal e falsa precisão durante uma cheia."""

import json

import numpy as np
import pandas as pd
import pytest

from src.features.rain import acumulados_posto
from src.live import improve, operational, verification
from src.live.adaptation import corrigir
from src.live.uncertainty import cobertura_recente, faixa_empirica

H = pd.date_range("2024-01-01", periods=60, freq="h", tz="UTC")


def test_correcao_espera_o_alvo_ser_observado_e_expira_na_lacuna():
    pred = pd.Series(0., index=H)
    obs = pd.Series(100., index=H)
    obs.loc[H[10]:] = np.nan
    out = corrigir(pred, obs, 6, ganho=.5, janela_h=6, min_amostras=3)
    assert out.loc[H[7], "ajuste_cm"] == 0  # só dois erros conhecidos
    assert out.loc[H[8], "ajuste_cm"] == 50
    assert out.loc[H[15], "ajuste_cm"] == 0  # não carrega viés velho no apagão
    assert out.loc[H[15], "n_ajuste"] == 0


def test_correcao_e_cobertura_nao_mudam_quando_o_futuro_muda():
    pred = pd.Series(np.arange(60.), index=H)
    obs = pd.Series(np.arange(60.) + 10, index=H)
    a = corrigir(pred, obs, 12)
    cobertura = cobertura_recente(pred, pd.Series(5., index=H), obs, 12)
    futuro = obs.copy()
    futuro.loc[H[31]:] = 99999
    b = corrigir(pred, futuro, 12)
    cb = cobertura_recente(pred, pd.Series(5., index=H), futuro, 12)
    pd.testing.assert_frame_equal(a.loc[:H[30]], b.loc[:H[30]])
    pd.testing.assert_frame_equal(cobertura.loc[:H[30]], cb.loc[:H[30]])


def test_correcao_nao_encurta_horizonte_quando_faltam_horas():
    pred = pd.Series(0., index=H[[0, 20, 40]])
    obs = pd.Series(100., index=H)
    out = corrigir(pred, obs, 9, janela_h=6, min_amostras=1)
    assert out.ajuste_cm.eq(0).all()  # erro de t=0 venceu a janela antes de t=20


def test_chuva_posto_exclui_hora_atual_e_horas_incompletas():
    g = pd.DataFrame({"ts_utc": H, "chuva_mm": 1., "chuva_n": 4})
    g.loc[10, "chuva_mm"] = 99.
    g.loc[11, "chuva_n"] = 3
    out = acumulados_posto(g, "mu")
    assert out.loc[H[10], "posto_mu_1h"] == 1.
    assert out.loc[H[11], "posto_mu_1h"] == 99.
    assert pd.isna(out.loc[H[12], "posto_mu_1h"])
    assert pd.isna(out.loc[H[13], "posto_mu_3h"])
    assert out.loc[H[15], "posto_mu_3h"] == 3.
    futuro = g.copy()
    futuro.loc[30:, "chuva_mm"] = 9999
    pd.testing.assert_frame_equal(out.loc[:H[30]], acumulados_posto(futuro, "mu").loc[:H[30]])


def test_chuva_posto_nao_cruza_lacuna_e_nao_inclui_jusante():
    g = pd.DataFrame({"ts_utc": H.delete(10), "chuva_mm": 1., "chuva_n": 4})
    out = acumulados_posto(g, "mu")
    assert pd.isna(out.loc[H[11], "posto_mu_1h"])
    frame = pd.DataFrame({"nivel_mu": 500., "posto_mu_1h": 1., "posto_es_1h": 100.}, index=H)
    ds = pd.DataFrame({"nivel_mu": 500., "y_3h": 0., "janela_id": "ev1", "tipo": "evento"}, index=H)
    operacional = operational.dataset_operacional(frame, ds, 86510000)
    assert "posto_mu_1h" in operacional
    assert "posto_es_1h" not in operacional


def test_faixa_nao_e_exibida_sem_amostra_ou_fora_do_regime():
    cal = {"n": 50, "margem_cm": 100., "velocidade_min_cm_h": 10., "velocidade_max_cm_h": 80.}
    dentro = faixa_empirica(1000., 50., cal)
    assert dentro["inferior_cm"] == 900
    assert dentro["superior_cm"] == 1100
    fora = faixa_empirica(1000., 150., cal)
    assert pd.isna(fora["inferior_cm"])
    assert fora["faixa_status"] == "regime_fora_calibracao"
    assert faixa_empirica(1000., 50., cal | {"n": 29})["faixa_status"] == "amostra_insuficiente"


def test_aceitacao_veta_regressao_sem_escolher_outro_candidato(tmp_path, monkeypatch):
    monkeypatch.setattr(improve, "R", tmp_path)
    (tmp_path / "11_live_modelos.json").write_text(json.dumps({"modelos": [
        {"codigo": 86510000, "h": 9, "motor": "linear"}]}))
    linhas = []
    for particao in ("desenvolvimento", "calibracao", "teste"):
        for motor in ("linear", "ridge_montante", "gbm_postos"):
            # Ridge vence desenvolvimento e confirmação, mas falha na aceitação.
            erro = 100 if motor == "linear" else (70 if motor == "ridge_montante" else 80)
            if particao == "teste" and motor == "ridge_montante":
                erro = 150
            for regime in ("alto", "subida", "descida", "rapida"):
                linhas.append({"codigo": 86510000, "h": 9, "particao": particao,
                               "motor": motor, "ajuste": "original", "regime": regime,
                               "mae_cm": erro})
    escolha = improve.escolher(pd.DataFrame(linhas))[0]
    assert escolha["motor"] == "linear"
    assert escolha["motor_testado_2026"] == "ridge_montante"
    assert not escolha["aceito_2026"]


def test_verificacao_exclui_replay_alvo_futuro_emissao_atrasada_e_sensor_ausente(tmp_path):
    frame = pd.DataFrame({"nivel_mu": np.arange(60.)}, index=H)
    frame.loc[H[13]] = np.nan
    linhas = []
    for modo, emissao, valido in (("emissao", 0, 6), ("replay", 0, 9),
                                  ("emissao", 20, 10), ("emissao", 0, 50),
                                  ("emissao", 0, 13)):
        linhas.append({"modo": modo, "emitido_em_utc": H[emissao], "valido_para_utc": H[valido],
                       "codigo": 86510000, "alvo": "Muçum", "h": 6, "motor": "linear",
                       "previsto_cm": 10.})
    pasta = tmp_path / "emissao_1"
    pasta.mkdir()
    pd.DataFrame(linhas).to_parquet(pasta / "previsoes.parquet", index=False)
    out = verification.conferir(frame, tmp_path, H[30])
    assert len(out) == 1
    assert out.erro_cm.iloc[0] == pytest.approx(4.)


def test_regua_parada_nao_atrasa_as_outras_estacoes(monkeypatch):
    idx = pd.date_range("2024-01-01", periods=200, freq="h", tz="UTC")
    frame = pd.DataFrame(index=idx)
    for _, ap in operational.ALVOS.values():
        frame[f"nivel_{ap}"] = np.arange(200, dtype=float)
        frame[f"dnivel_1h_{ap}"] = 1.
    ds = frame.iloc[:50].assign(janela_id="ev1", tipo="evento")
    frame.loc[idx[-5]:, "nivel_mu"] = np.nan
    monkeypatch.setattr(pd, "read_parquet", lambda _: ds.reset_index(names="ts_utc"))
    monkeypatch.setattr(operational, "configuracao_validada", lambda: {"modelos": []})
    monkeypatch.setattr(operational, "escolhas_validadas", lambda: {
        (c, h): "linear" for c in operational.ALVOS for h in operational.HORIZONTES})
    monkeypatch.setattr(operational, "prever_modelo", lambda tr, te, c, h, m:
                        te[f"nivel_{operational.baselines.PROPRIA[c]}"] + h)
    prev, _ = operational.rodada(frame)
    assert prev[prev.alvo == "Muçum"].t_ref_utc.eq(idx[-6]).all()
    assert prev[prev.alvo == "Muçum"].idade_cota_h.eq(5).all()
    assert prev[prev.alvo == "Estrela"].t_ref_utc.eq(idx[-1]).all()
