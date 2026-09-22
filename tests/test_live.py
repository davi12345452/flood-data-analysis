"""Causalidade operacional, referências exatas e separação temporal."""

import numpy as np
import pandas as pd
import pytest

from src.live import operational as op


def test_fontes_atrasadas_preservam_cota_atual_e_nao_preenchem_lacunas():
    idx = pd.date_range("2024-01-01", periods=40, freq="h", tz="UTC")
    frame = pd.DataFrame({c: np.arange(40, dtype=float) for c in
                          ["nivel_mu", "chuva_antas_6h", "defluente_qj",
                           "api_antas_k90", "disp_mu"]}, index=idx)
    frame.loc[idx[10], "chuva_antas_6h"] = np.nan
    out = op.features_disponiveis(frame)
    assert out.loc[idx[30], "nivel_mu"] == 30
    assert out.loc[idx[30], "chuva_antas_6h"] == 25
    assert out.loc[idx[30], "defluente_qj"] == 29
    assert out.loc[idx[30], "api_antas_k90"] == 6
    assert out.loc[idx[30], "disp_mu"] == 29
    assert pd.isna(out.loc[idx[15], "chuva_antas_6h"])


def test_deslocamento_e_por_tempo_e_futuro_nao_muda_passado():
    idx = pd.date_range("2024-01-01", periods=40, freq="h", tz="UTC").delete(10)
    frame = pd.DataFrame({"chuva_antas_1h": np.arange(39, dtype=float)}, index=idx)
    out = op.features_disponiveis(frame)
    assert pd.isna(out.loc[pd.Timestamp("2024-01-01 15:00", tz="UTC"), "chuva_antas_1h"])
    futuro = frame.copy()
    futuro.loc[idx[20]:] = 9999
    pd.testing.assert_frame_equal(out.loc[:idx[19]],
                                  op.features_disponiveis(futuro).loc[:idx[19]])


def test_rotulo_9h_nao_atravessa_buraco_por_posicao():
    idx = pd.date_range("2024-01-01", periods=40, freq="h", tz="UTC").delete(9)
    frame = pd.DataFrame({"nivel_mu": np.arange(39, dtype=float)}, index=idx)
    ds = frame.assign(janela_id="ev1", tipo="evento", y_3h=0)
    out = op.dataset_operacional(frame, ds, 86510000)
    assert pd.isna(out.loc[idx[0], "y_9h"])
    assert out.loc[idx[1], "y_9h"] == frame.loc[idx[1] + pd.Timedelta(hours=9), "nivel_mu"]


def test_treino_exclui_janelas_inteiras_e_rotulos_que_atravessam_corte():
    idx = pd.date_range("2024-01-01", periods=100, freq="h", tz="UTC")
    ds = pd.DataFrame({"janela_id": ["a"] * 30 + ["b"] * 30 + ["c"] * 40}, index=idx)
    train = op.treino_antes(ds, idx[65], 12)
    assert set(train.janela_id) == {"a"}
    assert (train.index + pd.Timedelta(hours=12) < idx[65]).all()


def test_gbm_delta_ancora_no_nivel_atual_mesmo_com_auxiliar_ausente(monkeypatch):
    monkeypatch.setattr(op, "load_config", lambda _: {
        "valid_frac_janelas": .15, "early_stopping_rounds": 5,
        "lgbm": {"n_estimators": 10, "min_child_samples": 5, "verbosity": -1},
    })
    idx = pd.date_range("2024-01-01", periods=100, freq="h", tz="UTC")
    train = pd.DataFrame({"nivel_mu": np.arange(100.) + 200,
                          "chuva_antas_6h": 1., "janela_id": "ev1", "tipo": "evento"},
                         index=idx)
    train["y_12h"] = train.nivel_mu + 50
    test = pd.DataFrame({"nivel_mu": [2000., np.nan], "chuva_antas_6h": [np.nan, 1.]},
                        index=idx[-2:])
    before = train.copy()
    pred = op.prever_modelo(train, test, 86510000, 12, "gbm_delta")
    assert pred.iloc[0] == pytest.approx(2050.)
    assert pd.isna(pred.iloc[1])
    pd.testing.assert_frame_equal(train, before)


def test_rodada_avalia_horizonte_longo_sem_recuar_referencia(monkeypatch):
    idx = pd.date_range("2024-01-01", periods=200, freq="h", tz="UTC")
    frame = pd.DataFrame({f"nivel_{ap}": np.arange(200, dtype=float)
                          for _, ap in op.ALVOS.values()}, index=idx)
    for _, ap in op.ALVOS.values():
        frame[f"dnivel_1h_{ap}"] = 1.0
    ds = frame.iloc[:50].assign(janela_id="ev1", tipo="evento")
    monkeypatch.setattr(pd, "read_parquet", lambda _: ds.reset_index(names="ts_utc"))
    monkeypatch.setattr(op, "escolhas_validadas", lambda: {
        (c, h): "gbm_delta" for c in op.ALVOS for h in op.HORIZONTES})
    monkeypatch.setattr(op, "configuracao_validada", lambda: {"modelos": []})
    monkeypatch.setattr(op, "prever_modelo", lambda tr, te, c, h, m:
                        te[f"nivel_{op.baselines.PROPRIA[c]}"] + h)
    prev, bt = op.rodada(frame, horas=24)
    assert len(prev) == 12
    assert prev.t_ref_utc.eq(idx[-1]).all()
    assert set(prev.h) == {3, 6, 9, 12}
    assert (bt.groupby(["alvo", "h"]).size() == 24).all()
    assert bt.erro_cm.eq(0).all()
    assert bt.valido_para.max() == idx[-1]


def test_registro_distingue_replay_de_emissao_e_preserva_execucoes(tmp_path, monkeypatch):
    from src.live import run

    processed = tmp_path / "data/processed"
    processed.mkdir(parents=True)
    for pasta in ("src", "config", "reports"):
        (tmp_path / pasta).mkdir()
    (tmp_path / "uv.lock").write_text("lock")
    (tmp_path / "reports/11_live_modelos.json").write_text("{}")
    (processed / "dataset_86510000.parquet").write_text("dataset fingerprint")
    monkeypatch.setattr(run, "ROOT", tmp_path)
    monkeypatch.setattr(run, "PROCESSED", processed)
    monkeypatch.setattr(run, "ALVOS", {86510000: ("Muçum", "mu")})
    referencia = pd.Timestamp("2000-01-01", tz="UTC")
    prev = pd.DataFrame({"t_ref_utc": [referencia], "valido_para_utc": [referencia],
                         "status": ["estimativa"]})
    replay, pasta_replay = run.registrar(pd.DataFrame(), prev, pd.DataFrame(), False)
    emitida, pasta_emissao = run.registrar(pd.DataFrame(), prev, pd.DataFrame(), True)
    assert replay.emitido_em_utc.isna().all()
    assert replay.antecedencia_real_h.isna().all()
    assert emitida.emitido_em_utc.notna().all()
    assert emitida.status.iloc[0] == "validade_expirada"
    assert emitida.antecedencia_real_h.iloc[0] < 0
    assert pasta_replay != pasta_emissao
    assert (pasta_replay / "previsoes.parquet").exists()
    pd.testing.assert_frame_equal(pd.read_parquet(pasta_replay / "previsoes.parquet"), replay)


def test_escolha_nao_depende_dos_erros_de_2026(tmp_path, monkeypatch):
    import json

    from src.live import evaluate

    monkeypatch.setattr(evaluate, "REPORTS", tmp_path)
    monkeypatch.setattr(evaluate, "PROCESSED", tmp_path)
    linhas = []
    for particao in ("selecao", "teste"):
        for motor, erro in (("linear", 20), ("gbm_delta", 10)):
            linhas.append({"codigo": 86510000, "alvo": "Muçum", "h": 12,
                           "evento": "ev2024" if particao == "selecao" else "ev2026",
                           "motor": motor, "regime": "alto", "particao": particao,
                           "mae_cm": erro, "vies_cm": -erro, "n": 10})
    metricas = pd.DataFrame(linhas)
    evaluate.publicar(metricas, pd.DataFrame())
    primeiro = json.loads((tmp_path / "11_live_modelos.json").read_text())
    metricas.loc[(metricas.particao == "teste") & (metricas.motor == "gbm_delta"),
                  "mae_cm"] = 99999
    evaluate.publicar(metricas, pd.DataFrame())
    segundo = json.loads((tmp_path / "11_live_modelos.json").read_text())
    assert primeiro["modelos"] == segundo["modelos"]
    assert primeiro["modelos"][0]["motor"] == "gbm_delta"
